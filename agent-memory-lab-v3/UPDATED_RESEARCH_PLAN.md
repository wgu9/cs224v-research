# Adaptive Memory System for Coding Agents - Updated Research Plan
**整合版：保留Q1技术核心 + 采纳SWE-bench评估策略**

---

## 📋 Executive Summary

### What Changed
- **数据源**: 真实对话（补充）→ SWE-bench（核心）
- **评估重点**: 验证weights → 端到端效果（Resolve rate vs SOTA）
- **Q3定义**: User-based → Task/agent-based abstraction

### What Stayed
- ✅ Four-Guard System（已有34 tests）
- ✅ Chat-first架构（从agent trace提取events）
- ✅ Pattern learning框架
- ✅ 真实对话作为技术验证

---

## 🎯 Research Questions (Refined)

| Question | Focus | Key Metric | Target | Baseline |
|----------|-------|------------|--------|----------|
| **Q1: Goal Alignment** | 防止multi-step execution中的drift，实时阻断 | Drift rate | <15% | ~28% (GPT-4 unmonitored) |
| **Q2: Pattern Learning** | 从成功tasks提取可复用patterns | Pattern reuse rate | ≥30% | 0% (no memory) |
| **Q3: Dynamic Abstraction** | 根据task/agent context调整detail level | Efficiency gain | >1.1x | 1.0x (fixed level) |
| **Overall System** | 端到端任务解决能力 | **Resolve rate** | **≥30%** | **AutoCodeRover 20%** |

**核心贡献**: Dynamic abstraction based on context (Yucheng's "nobody is doing") + 实时drift blocking

---

## 🏗️ System Architecture (New + Old Combined)

### Component Overview

```
User Input: SWE-bench Issue
    ↓
[Goal Parser] ──────────────→ Structured Goal (LLM-based)
    ↓
[Pattern Retriever] ────────→ Relevant Patterns (Vector search)
    ↓
[Abstraction Selector] ─────→ Choose Level 1/2/3 (Context-aware)
    ↓
[Agent Execution Loop]
    ├─ Generate Action (GPT-4o + Pattern)
    ├─ [Four-Guard Checker] ──→ Real-time drift detection ✨ (YOUR TECH)
    │   ├─ Scope Guard (0.4)
    │   ├─ Plan Guard (0.3)
    │   ├─ Test Guard (0.2)
    │   └─ Evidence Guard (0.1)
    ├─ IF drift ≥ 0.8: ROLLBACK
    ├─ ELSE: Execute Action
    └─ Observe Results
    ↓
[Test Execution] ───────────→ Pass/Fail (SWE-bench harness)
    ↓
IF Success:
    [Pattern Extractor] ────→ Extract Pattern (LLM)
    [Pattern Library] ──────→ Store for future
```

---

## 📊 Data Strategy

### Primary Dataset: SWE-bench Lite (300 tasks)

```
Split Strategy:
├─ Training (0-50): Extract patterns, tune thresholds
├─ Validation (50-100): Week 3 checkpoint, adjust system
└─ Test (100-300): Final evaluation, NEVER peek during dev

Selection Criteria:
├─ Difficulty: 33% easy, 50% medium, 17% hard
├─ Repos: Diverse (Django, scikit-learn, matplotlib...)
└─ Task types: Bug fix, validation, refactoring
```

**Why SWE-bench**:
- ✅ Standard benchmark (reproducible)
- ✅ Ground truth (test suite)
- ✅ Compare with SOTA (AutoCodeRover, Devin)
- ✅ Large enough for statistical tests (200 test instances)

---

### Supplementary Data: Real Cursor Conversations (10-20 sessions)

```
Purpose:
├─ Validate chat2events.py accuracy (Precision/Recall)
├─ Qualitative case studies (show real-world drift)
└─ Paper Section 2.1: Motivation ("real developers face this")

NOT used for:
❌ Primary evaluation metrics
❌ Quantitative comparison
```

---

## 🔧 Technical Implementation

### Q1: Goal Alignment & Drift Detection (CORE TECH - Preserved)

**Components**:

```python
# 1. Goal Parser (LLM-based)
def parse_goal(problem_statement: str) -> Goal:
    """
    Input: SWE-bench problem_statement
    Output: Structured goal
    """
    prompt = f"""
    Extract structured goal from this GitHub issue:

    {problem_statement}

    Return JSON with:
    - objective: one sentence goal
    - allowed_files: list of files that should be modified
    - forbidden_actions: list of actions to avoid
    - required_tests: tests that must pass
    """
    return llm.generate(prompt)

# 2. Four-Guard System (YOUR EXISTING CODE - 34 tests ✅)
def check_guards(action: Action, goal: Goal) -> GuardResult:
    """
    Returns:
    - scope_guard: 0.0-1.0
    - plan_guard: 0.0-1.0
    - test_guard: 0.0-1.0
    - evidence_guard: 0.0-1.0
    - drift_score: weighted sum
    - action: ok | warn | rollback
    """
    # Use existing events2guards.py logic
    return calculate_drift(action, goal)

# 3. Real-time Blocking (NEW)
def execute_with_monitoring(agent, task, goal):
    actions = []

    for step in range(MAX_STEPS):
        action = agent.generate_next_action(task, actions)

        # Check drift BEFORE executing
        guard_result = check_guards(action, goal)

        if guard_result.drift_score >= 0.8:
            # ROLLBACK
            print(f"⚠️ Drift detected! Score: {guard_result.drift_score}")
            print(f"Reason: {guard_result.notes}")
            actions = rollback_to_checkpoint(actions)
            continue

        # Execute
        result = agent.execute(action)
        actions.append((action, result))

        if is_done(result):
            break

    return actions
```

**Metrics**:
- Drift rate: % actions with drift_score > 0.5
- Block rate: % actions blocked (drift ≥ 0.8)
- False positive rate: % blocks that were actually ok

---

### Q2: Pattern Learning (NEW + Framework from Old)

**Pattern Extraction**:

```python
# When task succeeds
def extract_pattern(session: Session) -> Pattern:
    """
    Input: Successful solving session
    Output: Reusable pattern
    """
    prompt = f"""
    Analyze this successful solution and extract a reusable pattern.

    Issue: {session.task.problem_statement}
    Solution approach: {session.actions}
    Final patch: {session.patch}

    Extract:
    1. Problem signature (what type of problem?)
    2. Solution approach (high-level how?)
    3. Key insights (what made it work?)
    4. Applicable domains (when to use?)

    Decontextualize: Make it general, not task-specific.
    """

    pattern_text = llm.generate(prompt)

    return Pattern(
        id=generate_id(),
        name=extract_name(pattern_text),
        problem_signature=...,
        solution_approach=...,

        # Multi-level abstractions
        level_1_hint="Check for null before accessing field",
        level_2_explanation="When working with optional fields...",
        level_3_code="if obj.field is not None: ...",

        # Metadata
        times_used=0,
        success_rate=0.0,
        embedding=embed(pattern_text)
    )
```

**Pattern Retrieval & Application**:

```python
def solve_with_patterns(task, pattern_library):
    # Retrieve relevant patterns
    relevant = pattern_library.search(
        query=task.problem_statement,
        top_k=3
    )

    # Select abstraction level (Q3)
    level = select_abstraction_level(
        task_complexity=estimate_complexity(task),
        pattern_confidence=relevant[0].confidence,
        agent_history=get_history()
    )

    # Apply pattern
    pattern_text = relevant[0].get_level(level)

    solution = agent.solve(
        task=task,
        guidance=pattern_text
    )

    return solution
```

**Metrics**:
- Pattern reuse rate: % tasks where pattern applied
- Time savings: (time_without - time_with) / time_without
- Success rate with pattern vs without

---

### Q3: Dynamic Abstraction (ADJUSTED - Task-based)

**Context Factors** (not user-based):

```python
def select_abstraction_level(
    task_complexity: str,      # simple | medium | hard
    pattern_confidence: float, # 0.0-1.0
    agent_history: dict        # first_try | retry | ...
) -> int:
    """
    Returns: 1 (hint) | 2 (explanation) | 3 (code)
    """

    # Rule-based (MVP)
    if task_complexity == "simple" and pattern_confidence > 0.8:
        return 1  # Hint is enough

    elif task_complexity == "hard" or pattern_confidence < 0.5:
        return 3  # Need full code

    else:
        return 2  # Explanation

    # Future: Learn from feedback
    # level = learned_policy(context)
```

**Abstraction Levels**:

```
Level 1 - Hint (10-15 words):
"Check object for null before accessing its field attribute"

Level 2 - Explanation (50-100 words):
"When working with objects that have optional fields, you need to
verify the object exists before accessing its attributes. Add a
null check using 'if obj is not None' before the field access.
This prevents AttributeError when the object is None."

Level 3 - Code (Full implementation):
```python
# Before (buggy)
result = obj.field.value

# After (fixed)
if obj is not None and hasattr(obj, 'field'):
    result = obj.field.value
else:
    result = default_value
```
```

**Metrics**:
- Efficiency: (success_rate / avg_time) for dynamic vs fixed
- Selection accuracy: % times optimal level chosen (vs ground truth)
- Convergence: # tasks until policy stabilizes

---

## 📈 Evaluation Framework

### Baselines

| Baseline | Type | Setup | Expected Performance |
|----------|------|-------|---------------------|
| **Vanilla GPT-4** | Weak | Zero-shot, no tools | ~8% resolve |
| **GPT-4 + Static RAG** | Medium | Fixed retrieval, no memory | ~15% resolve |
| **AutoCodeRover** | Strong | Published SOTA | ~20% resolve |
| **Ablations** | Variants | Q1 only, Q2 only, etc | Varies |

### Metrics

**Primary**:
- **Resolve Rate**: % tasks where all FAIL_TO_PASS tests pass
- **Target**: ≥30% (vs AutoCodeRover 20%)

**Secondary**:
- Drift rate (Q1): <15% vs ~28% unmonitored
- Pattern reuse rate (Q2): ≥30%
- Time savings (Q2): ≥30% when pattern used
- Dynamic efficiency (Q3): >1.1x vs fixed level

### Statistical Tests

```python
# For each metric
from scipy import stats

# T-test
t_stat, p_value = stats.ttest_ind(
    your_system_scores,
    baseline_scores
)
# Target: p < 0.05

# Effect size (Cohen's d)
effect_size = (mean_yours - mean_baseline) / pooled_std
# Target: d > 0.5 (medium effect)

# 95% Confidence Interval
ci_lower, ci_upper = bootstrap_ci(your_system_scores)
```

### Ablation Study

```
Systems to evaluate (on same 200 test tasks):
1. Full System (Q1 + Q2 + Q3)
2. Q1 + Q2 only (no dynamic abstraction)
3. Q1 + Q3 only (no pattern memory)
4. Q2 + Q3 only (no drift monitoring)
5. Q1 only
6. Q2 only
7. Q3 only
8. Baseline (none)

Analysis:
- Component contribution
- Interaction effects
- Diminishing returns?
```

---

## 📅 6-Week Implementation Plan

### Week 1: Foundation + Baseline

**Goal**: Get basic pipeline working, establish baseline

**Tasks**:
- [ ] Load SWE-bench Lite, explore 20 examples
- [ ] Implement Goal Parser (LLM-based)
- [ ] Test Four-Guard System on SWE-bench format
- [ ] Implement Vanilla GPT-4 baseline
- [ ] Run baseline on 10 easy tasks

**Deliverable**: Baseline results on 10 tasks

**Success Criteria**:
- Goal Parser works (manually verify 10 goals)
- Four-Guard System compiles without errors
- Baseline achieves ~5-10% resolve on easy tasks

---

### Week 2: Q1 Integration + Pattern Extraction

**Goal**: Four-Guard System working on SWE-bench, first patterns extracted

**Tasks**:
- [ ] Integrate real-time drift blocking
- [ ] Run full pipeline on 20 tasks
- [ ] Extract patterns from successful cases (≥5 patterns)
- [ ] Implement pattern storage (ChromaDB)
- [ ] Validate chat2events on 10 real Cursor conversations

**Deliverable**:
- 20 tasks solved with drift monitoring
- 5+ patterns extracted
- Chat2events validation report

**Success Criteria**:
- Drift detection working (can catch obvious violations)
- At least 5 high-quality patterns extracted
- Chat2events F1 > 0.85

---

### Week 3: CHECKPOINT - Pattern Reuse + Q3 MVP

**Goal**: Pattern reuse working, decide if Q3 is feasible

**Tasks**:
- [ ] Implement pattern retrieval (semantic search)
- [ ] Run on validation set (50 tasks)
- [ ] Measure pattern reuse rate
- [ ] Implement basic abstraction selector (rule-based)
- [ ] Compare dynamic vs fixed abstraction (if time)

**Deliverable**: Validation results

**Success Criteria** (CRITICAL):
- ✅ Pattern reuse rate ≥20% → Continue with Q3
- ✅ Resolve rate ≥15% → On track
- ⚠️ If < 20% reuse: Debug Q2, simplify Q3
- ❌ If < 15% resolve: Skip Q3, focus on Q1+Q2

**Decision Point**:
```
IF reuse ≥ 20% AND resolve ≥ 15%:
    Continue with full plan (Q1+Q2+Q3)
ELIF reuse ≥ 15% OR resolve ≥ 12%:
    Simplify Q3 (fixed rules instead of dynamic)
ELSE:
    Skip Q3, focus on making Q1+Q2 solid
```

---

### Week 4: Polish + Ablations

**Goal**: Refine system, run ablation studies

**Tasks**:
- [ ] Implement all ablation variants (Q1 only, Q2 only, etc)
- [ ] Run ablations on validation set
- [ ] Tune hyperparameters (thresholds, weights)
- [ ] Error analysis (categorize failures)
- [ ] Implement Q3 learning (if passed checkpoint)

**Deliverable**:
- Ablation results showing component contributions
- Error taxonomy
- Tuned system

**Success Criteria**:
- Each component shows positive contribution
- Clear error categories identified
- System tuned for test set

---

### Week 5: Full Evaluation

**Goal**: Run on full test set, compute all metrics

**Tasks**:
- [ ] Run full system on 200 test tasks
- [ ] Run all baselines on same 200 tasks
- [ ] Compute all metrics (resolve, drift, reuse, time)
- [ ] Statistical tests (t-test, effect size, CI)
- [ ] Generate learning curves
- [ ] Detailed error analysis

**Deliverable**: Complete results

**Success Criteria**:
- Resolve rate ≥25% (conservative) or ≥30% (target)
- Statistically significant vs baseline (p < 0.05)
- All metrics computed and documented

---

### Week 6: Paper + Demo

**Goal**: Finalize paper, create demo

**Tasks**:
- [ ] Write paper draft (4-6 pages)
- [ ] Create demo video (5 min)
- [ ] Clean up code for release
- [ ] Create publication-quality figures
- [ ] Prepare presentation

**Deliverable**:
- Paper draft
- Demo video
- GitHub repo

---

## 🎯 Success Criteria by Grade

### B Grade (Minimum Viable)

**Technical**:
- ✅ Q1 implemented, drift rate < 20%
- ✅ Q2 implemented, reuse ≥ 20%
- ⚠️ Q3 basic (multi-level storage, may be fixed rules)
- ✅ Evaluation on 100+ tasks
- ✅ Statistical significance vs weak baseline

**Paper**:
- Clear methods
- Basic ablation
- Some error analysis

---

### A Grade (Strong Paper)

**Technical**:
- ✅ Q1 excellent, drift rate < 15%, p < 0.01
- ✅ Q2 excellent, reuse ≥ 30%, time savings ≥ 30%
- ✅ Q3 dynamic selection working
- ✅ Evaluation on 200 tasks
- ✅ Comprehensive ablations
- ✅ Learning curves shown

**Paper**:
- Publication-ready figures
- Thorough error analysis
- Comparison with strong baseline
- Clear contribution

---

### A+ / Publication Quality

**Technical**:
- ✅ All metrics exceed targets
- ✅ Resolve rate ≥30% (approach/beat AutoCodeRover)
- ✅ Clear learning over time
- ✅ Novel insights from analysis

**Paper**:
- Workshop-ready submission
- Open-source release
- Reproducible results
- Community impact potential

---

## 💰 Budget & Resources

### API Costs (Conservative Estimate)

```
Using Hybrid Strategy (API + Local):

Critical Tasks (API - GPT-4o):
├─ Goal parsing: 300 × $0.02 = $6
├─ Pattern extraction: 90 × $0.05 = $4.50
└─ Validation: 50 × $0.10 = $5
Subtotal: $15.50

High-Volume Tasks (Local - Qwen2.5-Coder-32B):
├─ Code generation: FREE
├─ Drift checking: FREE
└─ Embeddings: FREE

Total API Cost: ~$20-30
```

**Hardware Requirements**:
- GPU: RTX 5090 (32GB) ✅ You have this
- RAM: 96GB ✅ You have this
- Storage: ~100GB for models + data

---

## 🚨 Risk Management

### Risk 1: SWE-bench is too hard (resolve < 25%)

**Mitigation**:
- Start with easy tasks in Week 1
- If Week 3 resolve < 15%, focus on easier subset
- Adjust target: 25% conservative, 30% stretch

**Backup plan**:
- Use SWE-bench Lite easy subset only
- Emphasize component contributions (ablations)
- "First system with real-time drift blocking"

---

### Risk 2: Pattern reuse < 20%

**Mitigation**:
- Week 3 checkpoint catches this early
- Improve pattern extraction prompts
- Lower similarity threshold for retrieval

**Backup plan**:
- Skip Q3, focus on Q1+Q2
- Emphasize drift detection (Q1)
- "Even without high reuse, patterns improve success when used"

---

### Risk 3: Week 3 checkpoint fails

**Decision Tree**:
```
IF reuse < 15% AND resolve < 12%:
    Option A: Pivot to simpler tasks (SWE-bench easy only)
    Option B: Focus on Q1 only (drift detection paper)
    Option C: Extend timeline by 1 week, debug Q2

Recommendation: Option A (safest)
```

---

### Risk 4: Budget overrun

**Mitigation**:
- Use local models for high-volume tasks
- Cache LLM responses during development
- Prompt optimization (reduce tokens)

**Budget allocation**:
- Week 1-2 (dev): $5
- Week 3-4 (val): $10
- Week 5 (eval): $20
- Buffer: $10
- **Total: $45** (well under $100)

---

## 📊 Key Differences from Old Plan

| Aspect | Old Plan | New Plan | Why Changed |
|--------|----------|----------|-------------|
| **Primary Data** | Real conversations | SWE-bench | Standard benchmark, reproducible |
| **Main Metric** | Kappa, F1 (validation) | Resolve rate (application) | Academic rigor, SOTA comparison |
| **Q3 Context** | User expertise | Task/agent context | SWE-bench has no users |
| **Evaluation** | Verify weights | Beat baseline | Show system works end-to-end |
| **Sample Size** | 20 sessions | 200 tasks | Statistical power |
| **Tech Core** | Same (Four-Guard) | **Preserved ✅** | Your unique contribution |

---

## 🎓 Expected Contributions

### To Research Community

1. **Novel Mechanism**: Real-time drift detection with four-guard system
2. **Dynamic Abstraction**: Context-aware multi-level pattern presentation
3. **Empirical Validation**: Performance on standard benchmark (SWE-bench)
4. **Open Source**: Reproducible system + dataset splits

### To Practice

1. **Tool**: Coding agents that don't drift
2. **Efficiency**: 30% time savings through pattern reuse
3. **Reliability**: Higher success rate through monitoring

---

## 📝 Paper Outline (4-6 pages)

```markdown
1. Abstract (150 words)
   - Problem: Agents drift, don't learn, use fixed abstraction
   - Solution: Real-time monitoring + pattern memory + dynamic abstraction
   - Results: 30% resolve (vs 20% SOTA), 30% time savings

2. Introduction (1 page)
   - Motivation with real examples
   - Three research questions
   - Contributions

3. Related Work (0.5 page)
   - Coding agents (AutoCodeRover, Devin)
   - Memory systems (Reflexion, Voyager)
   - Difference: We do dynamic abstraction + real-time drift blocking

4. Method (2 pages)
   - 4.1 Four-Guard Drift Detection (Q1)
   - 4.2 Pattern Learning & Reuse (Q2)
   - 4.3 Dynamic Abstraction Selection (Q3)

5. Experiments (2 pages)
   - 5.1 Setup (SWE-bench, baselines, metrics)
   - 5.2 Main Results (resolve rate, comparisons)
   - 5.3 Ablation Study (component contributions)
   - 5.4 Analysis (learning curves, error taxonomy)

6. Discussion & Conclusion (0.5 page)
   - Limitations (no user study yet, Python only)
   - Future work (multi-language, online learning)
   - Impact
```

---

## ✅ Immediate Next Steps (Today)

1. **Load & Explore SWE-bench** (30 min)
```bash
pip install datasets
python -c "
from datasets import load_dataset
swebench = load_dataset('princeton-nlp/SWE-bench_Lite', split='test')
print(swebench[0])
"
```

2. **Test Goal Parser** (1 hour)
```python
# Test on 3 examples
examples = swebench[:3]
for ex in examples:
    goal = parse_goal(ex['problem_statement'])
    print(goal)
    # Manually verify quality
```

3. **Verify Four-Guard System** (30 min)
```bash
cd agent-memory-lab-v3
./runner.sh pytest tests/
# Should pass 34 tests
```

4. **Setup Hybrid LLM** (1 hour)
```bash
# Local model
ollama pull qwen2.5-coder:32b-instruct-q4_K_M

# API
export OPENAI_API_KEY="sk-..."
```

5. **Plan Week 1** (30 min)
- Review this plan
- Identify any blockers
- Set up development environment

---

## 📧 Questions to Resolve

Before starting, clarify with team:

1. **Budget approval**: Is $50-100 for API calls OK?
2. **Timeline**: Is 6 weeks realistic given other commitments?
3. **Checkpoint**: Week 3 decision criteria agreed?
4. **Publication target**: Workshop or full conference?
5. **Authorship**: Who will be co-authors?

---

## 🎯 Final Checklist

**Before Week 1**:
- [ ] SWE-bench loaded and explored
- [ ] OpenAI API key set up
- [ ] Local model (Qwen-32B) installed
- [ ] Four-Guard tests passing
- [ ] This plan reviewed by team

**Week 3 Checkpoint**:
- [ ] Pattern reuse ≥ 20%?
- [ ] Resolve ≥ 15%?
- [ ] Decision: Continue Q3 or simplify?

**Week 5 Completion**:
- [ ] Resolve rate ≥ 25%?
- [ ] Statistical significance achieved?
- [ ] All ablations complete?

**Week 6 Delivery**:
- [ ] Paper draft ready
- [ ] Demo video created
- [ ] Code cleaned up
- [ ] Results reproducible

---

**This plan balances**:
- ✅ Your existing technical work (Four-Guard System)
- ✅ Academic rigor (SWE-bench, statistical tests)
- ✅ Feasibility (6 weeks, reasonable targets)
- ✅ Risk management (Week 3 checkpoint)

**Ready to start? Let's go! 🚀**
