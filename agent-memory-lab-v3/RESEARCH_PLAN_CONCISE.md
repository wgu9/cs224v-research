# Adaptive Memory System for Coding Agents
**CS224V Project | 6 Weeks | Jeremy Gu**

---

## Part 1: Business Problems

Current coding agents (AutoCodeRover, SWE-agent, Devin) suffer from three critical failures:

**Problem 1: Goal Drift During Multi-Step Tasks**
- Agents modify wrong files, skip required tests, attempt unnecessary refactoring
- Example: Asked to fix login bug, agent refactors entire authentication system
- Impact: 28% of agent actions drift off-task (baseline measurement)

**Problem 2: No Cross-Session Learning**
- Each task solved from scratch—null pointer bugs solved 100+ times without learning
- Example: Fix payment.py null check → Week later, same issue in user.py, agent doesn't recognize pattern
- Impact: Wasted time, repeated mistakes, no knowledge accumulation

**Problem 3: One-Size-Fits-All Abstraction**
- Simple tasks get verbose explanations, complex tasks get insufficient guidance
- Example: Experienced agent gets step-by-step tutorial; struggling agent gets cryptic hint
- Impact: Inefficient communication, suboptimal success rates

**Market Gap**: No system combines real-time drift monitoring + pattern learning + dynamic abstraction.

---

## Part 2: Solution - Three Research Questions

### Q1: How to Maintain Goal Alignment?

**Innovation**: Four-Guard System with real-time blocking

| Guard | Function | Weight |
|-------|----------|--------|
| Scope Guard | Check file modifications against allowed paths | 0.4 |
| Plan Guard | Verify tool/phase matching (e.g., no editing during reproduce) | 0.3 |
| Test Guard | Ensure required tests executed | 0.2 |
| Evidence Guard | Validate modification rationale | 0.1 |

**Mechanism**:
```
drift_score = weighted_sum(guard_violations)
IF drift_score ≥ 0.8: BLOCK action + rollback
ELIF drift_score ≥ 0.5: WARN
ELSE: OK
```

**Target**: Drift rate < 15% (vs baseline 28%)

**Existing Work**: 85% code implemented—34 unit tests, chat2events extraction, events2guards scoring

---

### Q2: How to Extract & Reuse Patterns?

**Innovation**: Decontextualization → Multi-level storage → Context-aware retrieval

**Workflow**:
1. **Extract**: LLM analyzes successful session → Identifies core pattern
2. **Decontextualize**: `payment.py line 45 null check` → `"Objects need validation before access"`
3. **Store at 3 levels**:
   - Level 1 (Hint): "Check for None before using object"
   - Level 2 (Explanation): "When object might be None, add validation: if obj is None..."
   - Level 3 (Code): Full implementation with example
4. **Retrieve**: Semantic search (embeddings) when new task matches problem signature
5. **Apply**: Inject pattern at selected abstraction level

**Target**: Pattern reuse ≥ 30%, Time savings ≥ 30%

---

### Q3: How to Adapt Abstraction Dynamically?

**Innovation**: Context-aware selection (task complexity + pattern familiarity + agent history)

**Selection Logic**:
```
IF task_complexity = hard OR first_time_seeing_pattern:
    → Level 3 (detailed code)
ELIF task_complexity = simple AND pattern_familiar:
    → Level 1 (concise hint)
ELSE:
    → Level 2 (explanation)
```

**Context Features**:
- Task complexity: Estimated from problem statement, files mentioned, repo size
- Pattern familiarity: Agent's exposure count to this pattern (0, 1-3, 4+)
- Agent performance: Recent success rate on similar tasks

**Target**: Dynamic selection outperforms fixed level by >10% in efficiency (success/time)

**Note**: This addresses the same core problem Yucheng identified—"nobody is doing dynamic abstraction"—adapted for automated benchmarks where interactive users aren't available.

---

## Part 3: System Architecture

```
GitHub Issue (SWE-bench) → [Goal Parser] → [Pattern Retrieval] → [Abstraction Selector]
    ↓
[Agent Loop]: Generate → Check Drift (Q1) → Execute → Observe
    ↓
[Test Execution]: Pass/Fail
    ↓ (if Pass)
[Pattern Extraction] → Store for future use (Q2)
```

**Tech Stack**:
- LLM: GPT-4o (critical tasks: goal parsing, pattern extraction)
- Local LLM: Qwen-32B on RTX 5090 (high-volume: code gen, drift checks) → **75% cost savings**
- Vector DB: ChromaDB (pattern embeddings)
- Benchmark: SWE-bench Lite (300 tasks)

**Cost**: ~$15-20 total (hybrid API + local strategy)

---

## Part 4: Data & Evaluation

### Dataset: SWE-bench Lite (300 real GitHub issues)

**Split**:
- Train (50): Extract patterns, tune thresholds
- Validation (50): Week 3 checkpoint
- Test (200): Final evaluation

**Why SWE-bench**:
- ✅ Standard benchmark (reproducible)
- ✅ Ground truth (test suites)
- ✅ Real-world complexity (Django, scikit-learn, matplotlib)
- ✅ SOTA baselines for comparison

**Supplementary**: 10-20 real Cursor conversations for chat2events validation

---

### Metrics & Targets

| Metric | Target | Baseline |
|--------|--------|----------|
| **Resolve Rate** (Overall) | ≥25% (conservative)<br>≥30% (stretch) | AutoCodeRover: 20%<br>SWE-agent: 13%<br>GPT-4: 8% |
| **Drift Rate** (Q1) | <15% | 28% (unmonitored) |
| **Pattern Reuse Rate** (Q2) | ≥30% | 0% (no memory) |
| **Time Savings** (Q2) | ≥30% when pattern applied | - |
| **Dynamic Efficiency** (Q3) | >10% gain vs fixed level | - |

---

### Statistical Rigor

**Required**:
- T-tests: Your system vs each baseline (p < 0.05)
- Effect size: Cohen's d > 0.5
- Confidence intervals: Bootstrap 95% CI
- Ablation study: Q1 only, Q2 only, Q1+Q2, Full system

**Baselines**:
1. Vanilla GPT-4 (weak)
2. GPT-4 + Static RAG (medium)
3. AutoCodeRover (strong, published SOTA)

---

## Part 5: 6-Week Timeline

### Week 1-2: Foundation (Q1 + Q2)
**Week 1**: Goal Parser + Four-Guard adaptation to SWE-bench → Test on 10 tasks
**Week 2**: Pattern Extractor + Storage + Retrieval → Test on 20-30 tasks

**Deliverable**: Q1+Q2 working pipeline

---

### Week 3: CHECKPOINT ⚠️ Critical Decision Point

**Activity**: Run Q1+Q2 on 50 validation tasks

**Success Criteria**:
- ✅ Pattern reuse ≥ 20%
- ✅ Resolve rate ≥ 12%
- ✅ Drift rate < 25%

**Decision**:
- **If 3/3 met**: Proceed with Q3 (dynamic abstraction)
- **If 2/3 met**: Simplified Q3 (fixed rules only)
- **If <2/3 met**: Skip Q3, debug Q2, focus on Q1+Q2

---

### Week 4: Q3 Implementation (Conditional)

**If checkpoint passes**:
- Context feature extraction
- Abstraction selector (rule-based)
- Dynamic vs fixed comparison

**Deliverable**: Q3 integrated into pipeline

---

### Week 5: Full Evaluation

**Activities**:
- Run full system on 200 test tasks
- Run all baselines on same tasks
- Run ablations (Q1 only, Q2 only, etc.)
- Statistical analysis (t-tests, effect sizes)
- Error analysis (categorize 50 failures)

**Deliverable**: Complete results package

---

### Week 6: Deliverables

**Monday-Tuesday**: 5-min demo video + polished CLI
**Wednesday-Thursday**: Paper draft (4-6 pages)
**Friday**: GitHub repo cleanup + final submission

**Deliverable**: Paper + Demo + Code

---

## Part 6: Success Criteria

| Grade | Requirements |
|-------|-------------|
| **B (Minimum)** | Resolve ≥20% (100 tasks), Pattern reuse ≥15%, Drift detection working, Demo shows all components |
| **A (Strong)** | Resolve ≥25% (200 tasks), Pattern reuse ≥25%, Drift <15%, Statistical significance (p<0.05), Complete ablations |
| **A+ (Exceptional)** | Resolve ≥30% (beat AutoCodeRover), All metrics hit targets, Publication-ready paper |

---

## Part 7: Risk Management

### Week 3 Checkpoint Failure

**If pattern reuse < 15%**:
- Debug pattern extraction quality
- Lower retrieval threshold
- Allocate Week 4 to fixing Q2, skip Q3

**If resolve rate < 10%**:
- Option A: Pivot to easier task subset
- Option B: Focus on Q1-only (drift detection paper)
- Option C: Extend Q2 debugging by 1 week

### Budget Overrun

**Mitigation**: Local model (Qwen-32B) handles 90% of calls
**Buffer**: 50% overhead already included in $15-20 estimate

---

## Part 8: Key Contributions

**To Research**:
1. First system with real-time drift blocking (not just detection)
2. First coding agent with dynamic abstraction (addresses gap: "nobody is doing this")
3. Rigorous evaluation on SWE-bench with SOTA comparison

**To Practice**:
1. 30% time savings through pattern reuse
2. 50% reduction in goal drift (15% vs 28%)
3. Measurable ROI for development teams

---

## Part 9: Comparison with SOTA

| System | Drift Detection | Pattern Learning | Dynamic Abstraction | SWE-bench Result |
|--------|----------------|------------------|--------------------|--------------------|
| AutoCodeRover | ❌ | Retrieval only | ❌ | 19.6% |
| SWE-agent | ❌ | ❌ | ❌ | 12.8% |
| Devin | Implicit | Proprietary | ❌ | 13.9% |
| **Ours (Target)** | ✅ Four-Guard | ✅ Decontextualization | ✅ Context-aware | **25-30%** |

**Unique**: Only system combining all three capabilities

---

## Immediate Next Steps (Week 0)

**Today**:
1. Load SWE-bench Lite, explore 5 examples
2. Test goal parsing on 3 examples
3. Verify Four-Guard tests (34 should pass)

**This Week**:
1. Setup local model (Qwen-32B) + test quality
2. Implement baseline (Vanilla GPT-4)
3. Run baseline on 10 easy tasks → establish floor

**Ready to proceed**: ✅

---

**Contact**: Jeremy Gu | jeremy.gu@stanford.edu
**Timeline**: 6 weeks | **Budget**: $15-20 | **Target**: A grade (25%+ resolve rate)
