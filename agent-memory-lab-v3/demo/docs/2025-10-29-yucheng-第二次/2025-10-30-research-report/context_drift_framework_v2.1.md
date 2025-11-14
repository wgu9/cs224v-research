**Author**: Jeremy Gu

**Date**: October 29, 2025

**Status**: Draft for Yucheng Review

**Purpose**: Establish theoretical foundation and detection methods for Context Drift

## Summary

### ✅ This Framework Establishes:

1. **Formal Definition**: Context Drift as measurable deviation across three orthogonal dimensions
2. **Theoretical Grounding**: Distinction from Goal Drift, Error Propagation, Hallucination
3. **Intra-Session Scope**: Single task execution
4. **Detection Methods**: Operational algorithms (BV, EPR, Trajectory EM) with thresholds
5. **Literature Foundation**: 30+ papers surveyed, quantitative metrics identified
6. **Validation Plan**: Concrete next steps for Week 1-2

### 📊 Literature Support Summary

| Dimension | Direct Support | Key Evidence | Primary Metric |
| --- | --- | --- | --- |
| Scope Drift | 12 papers | MAST (7.15%), MI9 (99.81%) | BV > 0.3 |
| Tool Drift | 14 papers | TRAJECT-Bench (5-7), ToolACE (89.17%) | Traj EM < 0.5 |
| **Loop Drift** | **15 papers** | **AgentErrorBench (PRIMARY), ReCAPA (73-82%)** | **EPR₁₀ > 0.15** |

---

## Part 1: Conceptual Framework

### 1.1 Definition

**Context Drift** is the measurable deviation of an agent's behavioral trajectory from specified objectives, manifesting across three orthogonal dimensions (Scope, Tool, Loop) during long-horizon task (session) execution.

**Formal Definition (TBD)**

```
Given:
- Task goal G with constraints C
- Actual trajectory τₜ = {a₁, a₂, ..., aₜ}

Context Drift at step t occurs when:

  Drift_score(τₜ, G) > θ

where Drift_score aggregates three dimensions:
  Drift_score = w₁·Scope_drift + w₂·Tool_drift + w₃·Loop_drift

with dimension-specific metrics:
  • Scope_drift:  BV(τₜ, R_authorized)     [boundary violations]
  • Tool_drift:   1 - EM(τₜ, T_optimal)    [1 - trajectory exact match]
  • Loop_drift:   EPR(τₜ)                  [error propagation rate]

Note: We avoid defining a fixed "optimal trajectory" τ* as such 
trajectories are task-dependent and often unknowable a priori. 
Instead, we measure deviation from goal-conditioned constraints 
using established metrics (BV, EM, EPR) from recent literature.
```

**Key Properties**:

- **Progressive**: Gradual deviation, not sudden failure
- **Measurable**: Quantifiable through trajectory analysis
- **Correctable**: Can be corrected when detected early

---

### 1.2 Why Context Drift Matters

**Primary Evidence**:

1. **AgentErrorBench** (under review at ICLR 2026): Error propagation identified as **PRIMARY bottleneck** to agent reliability
2. **MAST** (arXiv 2025): Task derailment causes 7.15% of failures
3. **τ-bench** (arXiv 2024): pass^8 < 25% indicates severe instability
4. **ReCAPA** (ICLR 2026 under review): EPR₁₀ reduction from 0.3-0.45 (baselines) to 0.082 demonstrates **73-82% relative improvement in error propagation**

**Impact**:

- **Task failure**: Leads to unrecoverable states
- **Resource waste**: Repeated failed actions, irrelevant modifications
- **Security risk**: Unauthorized access (MI9: 99.81% detection rate)

---

### 1.3 Context Drift vs. Related Concepts

| Concept | Relationship | Our Extension |
| --- | --- | --- |
| **Goal Drift** | Subset - Goal Drift ⊂ Scope Drift | We focus on **execution process**, not just final goal |
| **Error Propagation** | Causal - Error Propagation → Loop Drift | We focus on **deviation patterns**, not single errors |
| **Hallucination** | Orthogonal - Can cause Tool Drift | We focus on **behavioral drift**, not factual errors |

**Key Distinctions**:

- **Granularity**: Step-by-step deviation, not just final outcome
- **Operationality**: Real-time detection methods, not only post-hoc analysis
- **Multi-dimensional**: Combines Scope/Tool/Loop, not single perspective

---

### 1.4 Research Scope

**Focus: Intra-Session Context Drift**

**Definition**:

- **Intra-session**: Drift within single task execution (e.g., one SWE-bench issue)
- **Time span**: 50-100 actions OR 30 min timeout
- **Goal stability**: Task objective G remains fixed throughout session

**Explicitly Excluded** (following Yucheng's guidance):

- ❌ Cross-session learning (Q2 - future work)
- ❌ Multi-day interactions
- ❌ Conversational AI (non-agent systems)

**Session definition and Rationale** (Yucheng, line 639-640):

> "One task is one session.."
> 

---

### 1.5 Three-Dimensional Framework

**Theoretical Basis**: Three dimensions are **parallel and orthogonal**, not hierarchical.

```
Scope Drift (WHERE)  → Spatial dimension
   Question: Where does agent operate?
   Violation: Accesses unauthorized resources

Tool Drift (HOW)     → Instrumental dimension
   Question: Which tools does agent use?
   Violation: Selects irrelevant/wrong tools

Loop Drift (WHEN)    → Temporal dimension
   Question: When does agent repeat?
   Violation: Stuck in repetitive patterns
```

**Orthogonality Proof** - Can occur independently:

- High Scope + Low Loop: Agent explores wrong area quickly
- Low Scope + High Tool: Agent in correct area, wrong tools
- Low Scope + Low Tool + High Loop: Agent stuck despite being in right place

**Coverage**: These three dimensions cover all observed drift types in 30+ papers surveyed.

---

## Part 2: Detection Framework

### 2.1 Scope Drift (Spatial Dimension)

**Definition**: Agent operates outside authorized boundaries or pursues misaligned sub-goals.

**Core Metric**: **Boundary Violation (BV) Score**
- Measures: `violations / total_accesses`
- Threshold: `> 0.3` indicates HIGH drift (derived from MAST 7.15% baseline)

**Why It Matters**:
- **Security**: MI9 detects 99.81% privilege escalation
- **Regression**: SWE-bench pass-to-pass test failures  
- **Efficiency**: MAST reports 7.15% task derailment

**Detection Approach**:
1. Track resources accessed (files, APIs, data)
2. Compare against authorized set R_authorized
3. Compute violation proportion

**Alternative Metrics**:
- Pass-to-Pass tests (SWE-bench): Binary - did agent break existing tests?
- JS Divergence (MI9): `JS(P(t₀) || P(t)) > 0.2` for behavioral distribution shift

**Literature Support** (12 papers): MAST, Goal Drift, MI9, SWE-bench, TheAgentCompany, [7 more]

---

### 2.2 Tool Drift (Instrumental Dimension)

**Definition**: Agent selects inappropriate, irrelevant, or suboptimal tools for current sub-goals.

**Core Metric**: **Trajectory Exact-Match (EM)**
- Measures: Overlap with reference trajectories or self-consistency
- Threshold: `< 0.5` indicates drift

**Why It Matters**:
- **Scaling bottleneck**: TRAJECT-Bench identifies 5-7 tools as critical failure point
- **Instability**: τ-bench shows pass^8 < 25%
- **Resource waste**: Redundant API calls, wrong parameters

**Detection Approach**:
1. Compare tool sequence against successful reference trajectories, OR
2. Measure consistency across k trials (pass^k metric from τ-bench)

**Alternative Metrics**:
- **pass^k**: Success rate over k trials - `< 0.5 (k≥4)` indicates instability
- **Relevance**: P(tool relevant | context) - ToolACE achieves 89.17% detection

**Literature Support** (14 papers): TRAJECT-Bench, τ-bench, ToolACE, BFCL, TPTU-v2, [9 more]

---

### 2.3 Loop Drift (Temporal Dimension) ⭐ HIGHEST PRIORITY

**Definition**: Agent repeats failed actions without learning or correction.

**Core Metric**: **Error Propagation Rate (EPR₁₀)**
- Measures: `Pr(error at t+k | error at t) - Pr(error at t+k | no error at t)`
- Threshold: `> 0.15` indicates severe drift
- Best result: ReCAPA achieves 0.082 (vs. baselines 0.3-0.45)

**Why It Matters - MOST CRITICAL**:
- **PRIMARY BOTTLENECK**: AgentErrorBench identifies error propagation as #1 failure mode
- **73-82% improvement potential**: ReCAPA demonstrates via EPR reduction
- **Yucheng emphasis**: "Especially evident in τ-Bench and WebArena"

**Theoretical Justification**:
```
Implicit meta-goal: All agents must "make progress"
Loop behavior: Repetition without progress  
Therefore: Violates "make progress" → Context Drift
```

**Detection Approach**:
1. Track error patterns across trajectory
2. Compute conditional error probability at distance k
3. Identify repeated failed action subsequences

**Alternative Metrics**:
- **PAC** (Propagation Attenuation Coefficient): Measures error decay rate - `< 0.05` problematic
- **Loop Count**: Number of repeated subsequences - `≥ 3` indicates stuck
- **pass^k**: Consistency metric (also used in Tool Drift)

**Literature Support** (15 papers - STRONGEST): AgentErrorBench, ReCAPA, τ-bench, WebArena, Retroformer, MI9, MAST, [8 more]

---

## Summary: Three-Dimensional Detection Framework

| Dimension | Question | Core Metric | Threshold | Top Evidence |
|-----------|----------|-------------|-----------|--------------|
| **Scope** | WHERE does agent operate? | BV Score | > 0.3 | MI9: 99.81% detection |
| **Tool** | HOW does agent act? | Trajectory EM / pass^k | < 0.5 | τ-bench: pass^8 < 25% |
| **Loop** | WHEN does agent repeat? | EPR₁₀ | > 0.15 | ReCAPA: 0.082 vs 0.3-0.45 |

**Detection Philosophy**: 
- **Progressive**: Monitor continuously, not just final outcome
- **Quantitative**: Establish thresholds from literature benchmarks
- **Orthogonal**: Each dimension detectable independently
- **Actionable**: Enable early intervention before task failure

---

## Part 3: Validation Plan (TBD)

### 3.1 Immediate Next Steps (Week 1-2)

**Week 1: Data Acquisition & Manual Annotation**

**Day 1-2: Download SWE-bench Trajectories**

```bash
# Source: SWE-bench public trajectories
aws s3 sync s3://swe-bench-experiments/verified/ ./trajectories/

# Select 3 representative tasks:
- 1 success case (clean trajectory, low drift)
- 1 failure case (high drift, multiple dimensions)
- 1 partial case (medium drift, mixed results)

```

**Day 3-5: Manual Annotation**

- For each action in each trajectory, label:
    - `{no_drift, scope_drift, tool_drift, loop_drift}`
- Record justification for each label
- Create ground truth CSV format:

```
task_id, step_num, action_type, drift_type, reasoning
django-12345, 3, edit_file, scope_drift, "Modified auth/permissions.py outside payment module"
```
    

**Week 2: Implementation & Validation**

**Day 6-8: Implement Detection Algorithms**

```python
# Priority order (based on Yucheng emphasis):
1. Loop Drift: EPR₁₀ computation (highest priority)
2. Scope Drift: BV score
3. Tool Drift: Trajectory EM

# Output format:
{
  "task_id": "django-12345",
  "scope_drift_score": 0.4,
  "tool_drift_score": 0.3,
  "loop_drift_score": 0.6,
  "cdi": 0.47
}

```

**Day 9-10: Validation & Case Study**

- Run detection on 3 annotated trajectories
- Compute accuracy: (TP + TN) / Total
- Identify failure modes
- Write 1 detailed case study (see Section 3.2)

---

### 3.2 Expected Deliverables

**Deliverable to Yucheng** (Week 2):

1. **Validation Report** (2 pages):
    - Detection accuracy on 3 trajectories
    - Confusion matrix for each dimension
    - Analysis of failure modes
2. **Case Study** (1 page):
    
    ```
    Task: django__django-12345 - Fix QuerySet null pointer
    
    Manual Analysis:
    - Scope violations: Steps 3, 5, 7 (3/10 actions)
    - Loop patterns: Step 6 repeats Step 2
    - Ground truth: FAILED due to scope drift
    
    Detection Results:
    - BV score: 0.4 (HIGH) ✓
    - EPR₁₀: 0.2 (MODERATE) ✓
    - CDI: 0.48 → Predicted FAILURE ✓
    
    Verdict: Detection CORRECT
    
    ```
    
3. **Updated Detection Cards**:
    - Refined thresholds based on empirical results
    - Identified edge cases
    - Suggested algorithm improvements

---

### 3.3 Open Questions for Yucheng

**Theoretical**:

1. Is the distinction between Context Drift and Goal Drift/Error Propagation clear and convincing?
2. Is the orthogonality argument for three dimensions sufficient, or should we consider hierarchical relationships?
3. For Loop Drift: Is the justification that "repetition = deviation from implicit 'make progress' goal" theoretically sound?

**Methodological**:
4. Detection algorithm level of detail: Should we provide more abstract framework or more implementation details?
5. For validation, is 3 trajectories sufficient for initial validation, or should we expand to 10-20?
6. Should we implement online detection (real-time) now, or focus purely on offline (post-hoc) analysis?

**Practical**:
7. Which benchmark should we prioritize after SWE-bench: τ-bench or WebArena?
8. For Loop Drift specifically: EPR₁₀ vs. simple repetition count - which is more practical?

---

---

## Appendix A: Literature Survey (30+ Papers, 20 here)

| # | Paper | Venue | Scope | Tool | Loop | Relevance |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | MAST | arXiv 2025 | ✓ 7.15% | ✓ | ✓ | 5 |
| 2 | AgentErrorBench | ICLR 2026 | ✓ | ✓ | ✓ PRIMARY | 5 |
| 3 | ReCAPA | ICLR 2026 | ○ | ○ | ✓ EPR/PAC | 5 |
| 4 | MI9 | arXiv 2024 | ✓ 99.81% | ✓ | ✓ | 5 |
| 5 | τ-bench | arXiv 2024 | ○ | ✓ | ✓ pass^8<25% | 5 |
| 6 | ToolACE | ICLR 2025 | ○ | ✓ 89.17% | ○ | 5 |
| 7 | Goal Drift | AAAI 2025 | ✓ 100k+ | — | ✓ | 5 |
| 8 | TRAJECT-Bench | arXiv 2024 | ○ | ✓ 5-7 | ✓ | 5 |
| 9 | AgentBoard | NeurIPS 2024 | ○ | ✓ | ✓ | 5 |
| 10 | Agent Trajectory Explorer | AAAI 2025 | ✓ | ✓ | ✓ | 5 |
| 11 | TheAgentCompany | arXiv 2024 | ✓ | ✓ | ○ | 4 |
| 12 | SWE-bench | ICLR 2024 | ✓ P2P | ○ | ○ | 4 |
| 13 | WebArena | ICLR 2024 | ✓ | ✓ | ○ | 4 |
| 14 | Retroformer | ICLR 2024 | — | ○ | ✓ +36% | 4 |
| 15 | WebResearcher | arXiv 2025 | ○ | — | ✓ | 4 |
| 16 | BFCL | 2024 | — | ✓ AST | ○ | 4 |
| 17 | Microsoft AI Red Team | 2025 | ✓ | ✓ | ✓ | 4 |
| 18 | OdysseyBench | arXiv 2024 | ✓ | ○ | ✓ | 4 |
| 19 | SWE-bench Pro | arXiv 2024 | ✓ | ✓ | ○ | 4 |
| 20 | TPTU-v2 | EMNLP 2024 | ○ | ✓ | ○ | 4 |

**Legend**:

- ✓ = Primary focus / Direct evidence
- ○ = Secondary / Indirect
- — = Not addressed

---

## Appendix B: Detailed Examples

### Example 1: High Drift (SWE-bench)

**Task**: Fix null pointer in `payment/processor.py`

**Trajectory**:

```
Step 1: Read error trace ✓
Step 2: Edit payment/processor.py (add null check) ✓
Step 3: Run tests → fails ✗
Step 4: Edit payment/database.py ✗ SCOPE DRIFT
Step 5: Edit utils/config.py ✗ SCOPE DRIFT
Step 6: Re-edit payment/processor.py (SAME patch) ✗ LOOP DRIFT
Step 7: Edit auth/permissions.py ✗ SCOPE DRIFT
Step 8: Re-edit payment/processor.py (SAME patch) ✗ LOOP DRIFT

```

**Detection**:

- Scope: BV = 3/7 = 0.43 (HIGH)
- Tool: EM = 0.4 (LOW)
- Loop: 2 repetitions, EPR₁₀ ≈ 0.4 (HIGH)
- **CDI = 0.66** → HIGH DRIFT ✓

---

### Example 2: Low Drift (SWE-bench)

**Trajectory**:

```
Step 1: Read error trace ✓
Step 2: Read payment/processor.py ✓
Step 3: Edit payment/processor.py (correct fix) ✓
Step 4: Run tests → passes ✓
Step 5: Task success ✓

```

**Detection**:

- Scope: BV = 0.0 (NONE)
- Tool: EM = 1.0 (PERFECT)
- Loop: 0 repetitions, EPR₁₀ = 0.0 (NONE)
- **CDI = 0.0** → VERY LOW DRIFT ✓

---

**END OF DOCUMENT**