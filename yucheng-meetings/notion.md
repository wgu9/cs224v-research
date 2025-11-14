### 2025-10-15 student proposal

<aside>
📋 Student Proposal Details

</aside>

## Weekend update (week 7)

2025-11-05 Meeting Prep

## Weekend update (week 6)

[2025-11-3 Week Summary](https://www.notion.so/2025-11-3-Week-Summary-2a274e3ea00380778afcdc36eb3a344c?pvs=21)

TL;DR: Stood up a Dockerized SWE-bench workflow, validated it end-to-end on a case, and scaffolded a runner to process the 500 SWE-bench Verified tasks using Claude Sonnet on AWS Bedrock. Drafted a full “Adaptive Memory System for Coding Agents” proposal (Q1–Q3), then—per Yucheng—pivoted the quarter to Q1-only: Context Drift Detection with a clear metric suite and cross-benchmark plan.

Details:
I completed a dry-run on a single SWE-bench instance to confirm dataset layout, evaluator hooks, and container I/O (tests, patches, logs). The pipeline now mounts per-task repos, calls Bedrock (Claude Sonnet) through a fixed agent scaffold, and records actions/tests for analysis. Result: a reproducible runner that’s ready to batch the 500 Verified tasks once guard instrumentation is finalized.

I wrote the full proposal detailing: Q1 drift monitoring (Scope/Plan/Test/Evidence guards with WARN/rollback thresholds), Q2 pattern extraction and decontextualized reuse (multi-level memory), and Q3 dynamic abstraction selection; plus metrics (Resolve Rate, Drift Rate, reuse stats), dataset strategy (train for memory, Verified for eval), and a 6-week timeline with ablations. After a 10/29 sync, we narrowed to Q1 as a standalone, paper-worthy problem, aiming to generalize across SWE-bench Verified, τ-bench, and WebArena, and to prefer existing trajectories where possible.

I also compiled a Q1-focused literature review across Scope / Tool / Loop drift: MAST/AgentErrorBench/ReAct/Retroformer for looping & error propagation, MI9 & Goal-Drift/AIES for scope formalization, and ToolACE/BFCL/TRAJECT-Bench for tool misuse. Key takeaway: Loop (repetition/error propagation) dominates failures, with strong prior art to calibrate thresholds and detectors. Next week: finalize a crisp drift definition + metric suite, instrument guards in the runner, curate small trajectory subsets for SWE-bench / τ-bench / WebArena, and run sanity evaluator checks to set initial thresholds and false-positive budgets.

[Context Drift Detection Framework](https://www.notion.so/Context-Drift-Detection-Framework-29c74e3ea00380d9aa83d5d070b754bb?pvs=21) ( new proposal)

**Author**: Jeremy Gu

**Date**: October 29, 2025

**Status**: Draft for Yucheng Review

**Purpose**: Establish theoretical foundation and detection methods for Context Drift

## Executive Summary

### This Framework Establishes:

1. **Formal Definition**: Context Drift as measurable deviation across three orthogonal dimensions
2. **Theoretical Grounding**: Distinction from Goal Drift, Error Propagation, Hallucination
3. **Intra-Session Scope**: Single task execution
4. **Detection Methods**: Operational algorithms (BV, EPR, Trajectory EM) with thresholds
5. **Literature Foundation**: 30+ papers surveyed, quantitative metrics identified
6. **Validation Plan**: Concrete next steps for Week 1-2

### Literature Support Summary

| Dimension | Direct Support | Key Evidence | Primary Metric |
| --- | --- | --- | --- |
| **Scope Drift** | 12 papers | MAST (7.15%), MI9 (99.81%) | BV > 0.3 |
| **Tool Drift** | 14 papers | TRAJECT-Bench (5-7), ToolACE (89.17%) | Traj EM < 0.5 |
| **Loop Drift** | 15 papers | AgentErrorBench (PRIMARY), ReCAPA (73-82%) | EPR₁₀ > 0.15 |

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
Therefore: Violates "make progress" → Context Drift\
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
| --- | --- | --- | --- | --- |
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

### 3.3 Open Questions

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

[2025-10-30 research papers](https://www.notion.so/2025-10-30-research-papers-29b74e3ea003807c8c81e993575de161?pvs=21)

# Context Drift Detection: Q1-Focused Literature Review

**Purpose**: Comprehensive literature foundation for 3-dimensional Context Drift detection framework (Scope, Tool, Loop)

**Scope**: Intra-session agent drift only (single task execution, 50-100 actions)

**Last Updated**: October 30, 2025

---

## 🏆 Tier 1: Core Papers (Must Know)

| # | Paper Title | Authors | Venue | Year | arXiv/DOI | Dimension | Key Metric | How It Supports Your Framework |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [**Why Do Multi-Agent LLM Systems Fail?** (MAST Taxonomy)](https://arxiv.org/abs/2503.13657) | Cemri, M., et al. | arXiv:2503.13657 | 2025 | 2503.13657 | **Loop + Scope + Tool** | **17.14%** Step Repetition (highest), **7.15%** Task Derailment, **13.98%** Reasoning-Action Mismatch | **Primary empirical foundation**: BV>0.3 derived from 7.15%, EPR detection justified by 17.14%, Tool Drift from 13.98% |
| 2 | [**AgentErrorBench: Where LLM Agents Fail and How They can Learn From Failures**](https://arxiv.org/abs/2509.25370) | Kunlun Zhu, Zijia Liu, et al. (18 authors) | ICLR 2026 (under review) | 2025 | 2509.25370 | **Loop (PRIMARY)** | Error propagation = PRIMARY bottleneck | **Core justification** for "Loop Drift is HIGHEST PRIORITY" - directly referenced in Part 1.2 and 2.3 |
| 3 | [**ReCAPA: Error Propagation Rate Analysis**](https://openreview.net/pdf/d65336a32883e5adc23f68a3ce890b8f0500e4c8.pdf) | (TBD - authors unknown) | ICLR 2026 (under review) | 2025 | TBD | **Loop** | EPR₁₀: 0.3-0.45 → 0.082 (**73-82%** improvement) | **Threshold calibration source**: EPR₁₀ > 0.15 derived from this benchmark; PAC metric alternative |
| 4 | [**MI9: Runtime Governance Framework for Agentic AI**](https://arxiv.org/abs/2508.03858) | MI9 Research Team | arXiv:2508.03858 | 2024 | 2508.03858 | **Scope** | **99.81%** privilege escalation detection | **Scope Drift detection methodology**: JS divergence, Mann-Whitney U tests; production-level accuracy proof |
| 5 | [**SWE-bench: Can Language Models Resolve Real-World GitHub Issues?**](https://arxiv.org/abs/2310.06770) | Jimenez, C. E., et al. | ICLR | 2024 | 2310.06770 | **Scope (P2P)** | 14.41% success, 54.9% early stopping | **Validation benchmark**: Defines session boundary (1 issue = 1 session), Pass-to-Pass test metric, trajectory format |

---

## 🥈 Tier 2: Essential Support Papers (Week 1-2 Reference)

| # | Paper Title | Authors | Venue | Year | arXiv/DOI | Dimension | Key Contribution | Direct Support to Your Metrics |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6 | [**τ-bench: A Benchmark for Tool-Agent-User Interaction](https://arxiv.org/abs/2406.12045) Note**: [τ2-Bench](https://github.com/sierra-research/tau2-bench) (arXiv:2506.07982) extends this to dual-control environments | Shunyu Yao, Noah Shinn, Karthik Narasimhan | arXiv | 2024 | 2406.12045 | **Tool + Loop** | **pass^8 < 25%** instability | Yucheng explicitly mentioned; dual evidence for Tool selection instability + Loop-induced failures.  |
| 7 | [**WebArena: A Realistic Web Environment**](https://arxiv.org/abs/2307.13854) | Zhou, S., et al. | ICLR | 2024 | 2307.13854 | **Loop + Scope** | 14.41% GPT-4 vs 78% human, observation bias | Yucheng explicitly mentioned; Loop Drift manifestation (lack of recovery), Scope Drift (observation bias) |
| 8 | [**TRAJECT-Bench: Trajectory-Aware Tool Use**](https://arxiv.org/abs/2510.04550) | Pengfei He, Zhenwei Dai, et al. (13 authors) | arXiv | 2025 | 2510.04550 | **Tool** | **5-7 tools** = critical failure point | Explains why Tool Drift occurs; Trajectory EM metric theoretical source |
| 9 | [**Evaluating Goal Drift in Language Model Agents**](https://arxiv.org/abs/2505.02709) | Arike, R., Denison, C., Goldowsky-Dill, N., Hobbhahn, M. | AAAI AIES | 2025 | 2505.02709 | **Scope** | GD scores 0.51-0.93, 100k+ adversarial samples | Formal goal drift definition; supports "Goal Drift ⊂ Scope Drift" (Part 1.3) |
| 10 | [**ToolACE: Winning the Points of LLM Function Calling**](https://arxiv.org/abs/2409.00920) | Weiwen Liu, Xu Huang, et al. (27 authors) | ICLR | 2025 | 2409.00920 | **Tool** | **89.17%** tool misuse detection | Tool Drift detection accuracy benchmark; proves detection feasibility |
| 11 | **ReAct: Synergizing Reasoning and Acting** | Yao, J., et al. | ICLR | 2023 | 2210.03629 | **Loop** | **47%** reasoning errors include repetitive loops | Foundational evidence for Loop Drift; identifies repetition as reasoning failure |
| 12 | **Retroformer: Retrospective Large Language Agents** | Weiran Yao, Shelby Heinecke, et al. | ICLR | 2024 | 2308.02151 | **Loop** | **+36%** improvement via retrospection | Loop Drift mitigation effectiveness; proves error recovery is valuable |
| 13 | **Agent Trajectory Explorer** | Yiheng Xu, Dunjie Lu, et al. | AAAI | 2025 | 2412.09605 | **All 3** | Trajectory visualization framework | Detection methodology architectural reference |
| 14 | **AgentBoard: Multi-turn LLM Agent Evaluation** | Chang Ma, Junlei Zhang, et al. (9 authors) | NeurIPS | 2024 | 2401.13178 | **Tool + Loop** | Multi-turn evaluation framework | Benchmark environment for Loop Drift detection |
| 15 | **Reflexion: Language Agents with Verbal Reinforcement Learning** | Shinn, N., et al. | NeurIPS | 2023 | 2303.11366 | **Loop** | Bounded memory (1-3 experiences) to prevent context explosion | Addresses why Loop Drift occurs; memory management as mitigation |

---

## 🥉 Tier 3: Supplementary Papers (Domain-Specific / Edge Cases)

| # | Paper Title | Authors | Venue | Year | arXiv/DOI | Dimension | Why Included |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | **Microsoft AI Red Team: Taxonomy of Failure Modes** | Bryan, P., Severi, G., et al. | Microsoft White Paper | 2025 | N/A | **All 3** | Comprehensive 27 failure modes; memory poisoning case study (80% attack success) validates Scope Drift risks |
| 17 | **SWE-bench Pro: Long-Horizon Software Engineering** | Deng, Y., et al. | arXiv | 2025 | 2509.16941 | **All 3** | Enterprise tasks (hours-days); GPT-4 23.3% success; extreme test case for drift detection |
| 18 | **TheAgentCompany: Benchmarking LLM Agents** | Frank F. Xu, Yufan Song, et al. (21 authors) | arXiv | 2024 | 2412.14161 | **Scope + Tool** | Real-world enterprise scenarios; scope violation patterns |
| 19 | **BFCL: Berkeley Function Calling Leaderboard** | Shishir G. Patil, Huanzhi Mao, et al. | ICML | 2025 | Leaderboard | **Tool** | AST-based tool validation; technical implementation reference |
| 20 | **TPTU-v2: Tool Planning and Usage** | Yilun Kong, Jingqing Ruan, et al. (13 authors) | EMNLP | 2024 | 2311.11315 | **Tool** | Tool parameter error analysis; complements ToolACE |

---

## 📊 Literature Statistics

### By Venue Tier

| Tier | Venues | Count | Papers |
| --- | --- | --- | --- |
| **Top-Tier Conferences** | ICLR, NeurIPS, AAAI, EMNLP | **11** | #2,3,5,7,9,10,11,12,13,14,15,20 |
| **Under Review (High Impact)** | ICLR 2026 | **2** | #2 (AgentErrorBench), #3 (ReCAPA) |
| **Strong arXiv** | Recent with high relevance | **6** | #1,4,6,8,16,17,18,19 |
| **Industry/Leaderboard** | Microsoft, Berkeley | **1** | #16,19 |

### By Dimension Coverage

| Dimension | Primary Papers | Secondary Papers | Total |
| --- | --- | --- | --- |
| **Loop Drift** | 1,2,3,11,12,15 (6) | 6,7,14 (3) | **9 papers** |
| **Scope Drift** | 1,4,5,9 (4) | 7,16,17,18 (4) | **8 papers** |
| **Tool Drift** | 8,10 (2) | 1,6,14,19,20 (5) | **7 papers** |

### By Year

| Year | Count | Trend Analysis |
| --- | --- | --- |
| 2025 | **8** | MAST, AgentErrorBench, ReCAPA, Goal Drift, ToolACE, Agent Trajectory Explorer, Microsoft AI Red Team, SWE-bench Pro |
| 2024 | **11** | MI9, τ-bench, SWE-bench, WebArena, TRAJECT-Bench, Retroformer, AgentBoard, TheAgentCompany, TPTU-v2, BFCL |
| 2023 | **2** | ReAct, Reflexion (foundational) |

**Observation**: 85% of papers published in 2024-2025 → **Emerging research area**, your work is timely
[2025-10-29 Meeting Notes](https://www.notion.so/2025-10-29-Meeting-Notes-29b74e3ea003800ca3f7ea9ce415f39f?pvs=21)

# Q1-Only Focus — Meeting Minutes & Next Steps

**Date:** 2025-10-29

**Attendees:** Yucheng (CS224v), Jeremy

## One-line takeaway

**Shift from “Q1+Q2” to “Q1-only: Context Drift Detection.”** Treat drift detection as a standalone, paper-worthy problem.

## Key decisions

- **Primary scope this quarter:** In-session **Context Drift Detection** (Q1).
    - Not do: Defer cross-session learning/reuse (Q2/Q3).
- **Formalization first:** Write a precise **definition** of “context drift” and a small **metric suite** (dimensions + how to instantiate).
- **Generalization target:** Validate across **3 benchmarks**
    - SWE-bench Verified, **TAU Bench**, **WebArena**.
- **Data strategy:** Prefer **existing trajectories/logs** over re-running agents (cost/time).
    - Not now: Use evaluator/Docker only when needed.
- **New dimension to add:**
    - **Repetitive Mistakes** (looping/failure recurrences), especially salient in WebArena/TAU.

## Clarifications / guardrails

- **Gold-only self-check**: do not compute drift; record as **N/A** (sanity of pipeline only).
- **Resolved metric**: use **official evaluator + Docker**.

## Immediate next steps (this week)

1. **Literature survey (P0, today start)**
    - Search: “context drift”, “goal drift”, “trajectory evaluation”, “long-horizon agents”.
2. **Explore TAU Bench (P0)**
    - Read tasks, check if **public trajectories** exist; gather notes on metrics mapping.

## Risks / assumptions

- Availability/format of open trajectories; potential effort to normalize logs.
- Metric generalization across benchmarks; threshold calibration.
- Cost/time of evaluator runs; keep subsets small.

Deliverable

[Context Drift Detection Framework](https://www.notion.so/Context-Drift-Detection-Framework-29c74e3ea00380d9aa83d5d070b754bb?pvs=21)

[2025-10-28 Full Proposal](https://www.notion.so/2025-10-28-Full-Proposal-29a74e3ea0038004b7dccbdc895fae59?pvs=21)

# Adaptive Memory System for Coding Agents

**CS224V Project Proposal | Jeremy Gu**

---

## Motivation

Following our Oct 22 discussion on agent memory systems that (1) learn across sessions, (2) improve from feedback, and (3) decontextualize experiences into transferable patterns. Your key insight: *"abstraction level needs to be adjusted on the fly—nobody is doing that."*

---

## Three Research Questions

Current coding agents (Claude Code, Cursor, GitHub Copilot) lack three critical capabilities:

### Q1: How can agents maintain goal alignment during multi-step tasks?

**Problem**: Agents drift from original objectives—research on SWE-agent shows 75% of failures relate to scope control breakdown (52% incorrect/overly specific implementations, 23.4% cascading errors), SWE-agent（NeurIPS 2024).

Our preliminary analysis of 10 real coding sessions confirms agents frequently modify files outside intended scope or skip verification steps.

**Solution**: Multi-dimensional alignment checking

- **Scope**: File modifications within intended scope?
- **Plan**: Tool usage matches current phase?
- **Test**: Verification steps executed?
- **Evidence**: Changes have supporting rationale?

**Mechanism**: Track alignment violations through weighted combination of four guards, WARN at drift ≥0.5 and issue a rollback advisory (block submission) at ≥0.8, following shadow→advisory rollout.

**Evaluation on SWE-bench Verified**:

- Primary metric: Drift Rate (% actions violating any of four guards)
- Secondary metrics: Scope alignment, False positive rate
- Baseline: Unmonitored agent (Q1 disabled)
- Target: Drift rate <15% (exact target TBD after baseline, Week 1)

---

### Q2: How can agents extract and reuse patterns across sessions?

**Problem**: Each task solved from scratch—no knowledge accumulation across sessions.

**Solution**: Pattern extraction and retrieval

**Workflow**:

1. **Extract**: LLM analyzes successful task → Identifies reusable pattern
2. **Decontextualize**: Transform specific solution into general approach
3. **Store at multiple abstraction levels**:
    - Level 1: High-level approach (e.g., "validate inputs before processing")
    - Level 2: Conceptual explanation with key steps
    - Level 3: Concrete code template
4. **Retrieve**: Semantic search when new task matches problem signature
5. **Apply**: Inject relevant pattern into agent context

**Evaluation on SWE-bench Verified**:

- **Pattern Reuse Rate**: % test tasks where pattern was retrieved (similarity ≥ 0.7)
- **Success with Pattern**: Resolve rate when pattern applied vs not applied
- **Coverage**: % test tasks with available relevant pattern from training
- Target: Demonstrate positive correlation between pattern availability and success

---

### Q3: How should abstraction levels adapt dynamically?

**Problem**: Static responses don't match varying needs—some situations need detailed guidance, others need concise hints.

**Solution**: Context-based abstraction selection

**Context Signals** (all observable from SWE-bench):

- **Task indicators**: Problem statement length, number of files mentioned
- **Pattern factors**: First time seeing this pattern type vs repeated
- **Execution state**: Number of prior attempts, recent action success

**Selection Approach**:

- Initial strategy: Rule-based heuristics
- If time permits (Week 4): Learn from outcomes (which level worked best in which contexts)

**Evaluation on SWE-bench Verified**:

- **Primary**: Compare resolve rate of dynamic selection vs fixed-level baselines
- **Secondary**: Analyze which levels work best for which task types
- Target: Dynamic ≥ Fixed (any improvement validates approach)

**Novel Contribution**: This addresses your insight—"nobody is doing dynamic abstraction." Current systems (AutoCodeRover, SWE-agent) use fixed retrieval depth.

---

## Data & Evaluation

### Dataset: SWE-bench Verified (500 high-quality tasks)

**What SWE-bench Provides**:

- Real-world bug reports from popular Python projects
- Ground truth solutions (for evaluation only)
- Test suites for objective pass/fail measurement
- Human-annotated difficulty labels (e.g., "<15 min fix"), enabling stratified analysis

Note: A chronological variant (e.g., SWE-bench-CL) can be used as an auxiliary dataset to stress-test cross-session learning (Q2), but the primary benchmark remains Verified for comparability.

**What SWE-bench Cannot Provide**:

- Interactive user feedback (no real users in loop)
- Time measurements (automated execution)

**Our Split**:

- Memory-building corpus (for Q2): Use the official `princeton-nlp/SWE-bench` train split to extract and store patterns (no overlap with final test set)
- Final evaluation: Use the full SWE-bench Verified (500) as an independent test set for reportable results

For Q2/Q3 auxiliary analysis, we may additionally construct time-ordered subsets (e.g., repository-wise sequences or SWE-bench-CL) to assess temporal generalization, while keeping Verified as the primary report.

**Dataset Justification**: We report main results on SWE-bench Verified (comparability, reproducibility). We additionally evaluate on time-ordered subsets/CL to stress-test cross-session effects; these are supplementary and do not replace Verified as the primary benchmark.

---

### Metrics

**Primary Metric**: Resolve Rate

- Definition: % tasks where all required tests pass
- Current landscape (Verified): top closed-source systems report >70% (e.g., Claude Sonnet 4.5 ~77%, OpenAI o3 ~71% at the time of writing); research baselines vary widely by agent scaffold (framework/pipeline)
- Our Target (Verified context): set relative to published research baselines under similar constraints (e.g., ≥30% with our guard/pattern/dynamic-abstraction pipeline), finalized after baseline runs

**Q1 Metrics**:

- Drift Rate (primary): % actions violating alignment guards (weighted combination of Scope/Plan/Test/Evidence)
- Scope alignment (secondary): report as Precision/Recall —
    - Precision: % of edited files within gold patch scope
    - Recall: % of gold patch files that were edited
- Baseline: Will establish in Week 1 by running unmonitored agent
- Target: Drift rate <15% (improvement over baseline, exact target TBD)

**Q2 Metrics**:

- Pattern reuse rate: % tasks where pattern retrieved
- Success with pattern: Resolve rate (pattern used) vs (pattern not used)
- Target: Demonstrate statistical significance using proportion/paired tests (Fisher/χ² or McNemar) or logistic regression; report 95% CIs

Pattern usage levels (operational definitions):

- retrieved_only: pattern retrieved and shown; no evidence of application.
- used_like: partial application (step/template overlap ≥ τ, or guard improvement Δdrift > 0).
- used_strict: clear adherence to steps/templates and corresponding guard improvements.

Logging chain: log retrieve → present → adopt (level) with failure_reason (e.g., mismatch, conflict, low confidence).

**Q3 Metrics**:

- Dynamic vs Fixed: Resolve rate comparison
- Level distribution: Which levels used most often
- Target: Dynamic ≥ best fixed level

**Statistical Requirements**:

- Prefer proportion tests (Fisher/χ²), paired McNemar for within-task comparisons, or logistic regression with fixed effects; report 95% CIs and effect sizes
- Ablation study: Q1 only, Q2 only, Q1+Q2, Full

---

## Implementation

**Tech Stack**:

- Agent scaffold (fixed for comparability): tools/control/validation/budget configuration is locked per experiment
- LLM API: GPT-4o for critical reasoning tasks (goal parsing, pattern extraction)
- Local LLM: Qwen-32B for high-volume tasks (code generation)
- Vector DB: ChromaDB for pattern retrieval
- Budget: per-task cap (compute-matched) + total budget note (hybrid strategy)

**Agent Scaffold (Fixed, versioned)**:
To ensure fair comparisons and reproducibility, all experiments run under a fixed agent scaffold — a versioned configuration that explicitly locks the agent's tools, control logic, validation rules, and resource budgets. We log a `scaffold_id` (plus key knobs like τ/top‑k/cap) per run so any observed gains are attributable to our mechanisms, not incidental parameter changes.

**Run Policy & Reproducibility**:

- Q1: start in shadow mode (warn-only), enable rollback advisory after threshold calibration
- Q2: retrieval threshold τ tuned on validation; top‑k ≤ 3 with dedup; log retrieve → present → adopt(level)
- Repro: single entry command via [runner.sh](http://runner.sh/); log seed, scaffold config, per-task cost, tokens/calls/actions

**Timeline** (6 weeks):

- **Week 1-2**: Q1+Q2 implementation, establish baselines
- **Week 3**: **Checkpoint evaluation on 50 validation tasks**
    - Go/No-Go decision: If pattern reuse ≥20% AND resolve rate improvement observed → proceed with Q3
    - Otherwise: Focus on strengthening Q1+Q2
- **Week 4**: Q3 implementation (conditional on Week 3 results)
- **Week 5**: Main evaluation on SWE-bench Verified (500 tasks)
- **Week 6**: Paper + Demo

---

## Expected Contributions

1. **Mechanism**: Multi-dimensional alignment monitoring for coding agents
2. **Framework**: Pattern decontextualization with multi-level storage
3. **Exploration**: Context-based abstraction selection (addresses "nobody is doing this")
4. **Evaluation**: Rigorous comparison with SOTA on standard benchmark

---

## Open Questions / Limitations

**Known from start**:

- Optimal alignment weights: Will tune during training (Week 1-2)
- Pattern quality: Depends on LLM extraction accuracy (will validate manually)
- Abstraction selection: Starting with rules, learning if time permits
- Time savings: Cannot measure actual time on automated benchmark (will use proxy metrics like action count, token usage)

**To be determined Week 3**:

- Whether Q3 is feasible given Q2 results
- Exact target numbers after baseline establishment

**Future work**:

- User study to validate original "user expertise" adaptation hypothesis
- Multi-language support (currently Python-only via SWE-bench)

---

## Comparison with Research Systems

While commercial tools (Claude Code, Cursor, GitHub Copilot) exhibit the problems motivating this work, we evaluate against research systems on the standard SWE-bench benchmark:

| System | Drift Monitoring | Cross-Session Memory | Dynamic Abstraction |
| --- | --- | --- | --- |
| AutoCodeRover | ❌ | Static retrieval | ❌ |
| SWE-agent | ❌ | ❌ | ❌ |
| **Ours (proposed)** | ✅ Multi-dimensional | ✅ Decontextualized patterns | ✅ Context-aware |

**Differentiation**: Only research system proposing all three capabilities with dynamic abstraction adjustment.

**References (placeholders; add split/time/DOI/links on update)**

- AutoCodeRover — ISSTA 2024 (Lite 19–22%; Verified ~46%).
- SWE-agent — NeurIPS 2024 (Full ~12.5%).
- Claude Sonnet 4.5 — Verified ~77% (2025‑09).
- OpenAI o3 — Verified ~71% (2024‑12, high compute).

---

## Appendix: Key Definitions and Assumptions

### Notation

Throughout this proposal:

- **Bold**: Key terms being defined
- *Italics*: Emphasis or quoted concepts
- `Code`: Variable names, file paths, function calls
- Percentages: Always out of 100 (e.g., 20% = 20/100)

---

### Core Concepts

**Memory**

- **Definition**: A system's ability to store, retrieve, and apply knowledge from previous task executions to improve future performance.
- **In our context**: Cross-session pattern storage where successful solutions are extracted, decontextualized, and made available for future similar tasks.
- **Contrast**: Current agents have no memory—each task starts from zero knowledge.

**Goal Alignment**

- **Definition**: The degree to which an agent's actions match the intended task scope and plan.
- **Measurement**: Tracked through four weighted dimensions with combined drift score:
    - Scope Guard (weight 0.4): File modifications within intended boundaries?
    - Plan Guard (weight 0.3): Tool usage matches current task phase?
    - Test Guard (weight 0.2): Verification steps executed?
    - Evidence Guard (weight 0.1): Changes have supporting rationale?
- **Drift Score Calculation**: `drift_score = 0.4×scope + 0.3×plan + 0.2×test + 0.1×evidence`
- **Action Decision**:
    - `drift_score < 0.5` → OK (proceed)
    - `0.5 ≤ drift_score < 0.8` → WARN (log but allow)
    - `drift_score ≥ 0.8` → rollback advisory (suggest rollback/block submission)
- **Example of drift**:
    - Task: "Fix login validation to accept emails with '+' character"
    - Expected scope: `login_validator.py` (1 file, ~5 line change)
    - Agent did: Modified 12 files, refactored authentication system, changed database schema, skipped testing
    - Result: Goal drift detected, rollback advisory triggered (submission blocked)

**Multi-step Task**

- **Definition**: A task requiring multiple sequential actions across different phases (e.g., understand → reproduce → implement → verify → test).
- **In SWE-bench**: Each GitHub issue requires an estimated 5-15 agent actions on average (will validate on training set), spanning file reading, editing, test execution, and debugging.
- **Why it matters**: Single-step tasks don't exhibit goal drift; multi-step tasks are where agents lose track of original objectives.

**Scope** (Task Scope)

- **Definition**: The set of files, functions, and test cases that are relevant to a specific task.
- **In SWE-bench**: Inferred from problem statement and (for evaluation) validated against ground truth patch.
- **Components**:
    - `allowed_paths`: Files mentioned in problem or likely related
    - `forbidden_paths`: System files, configs, unrelated modules
    - `required_tests`: Test cases that must pass for success
- **Example**:
    - Task: "Fix null pointer in payment validation"
    - Scope: `[payment_processor.py, payment_validator.py, test_payment.py]`
    - Out of scope: `user_auth.py`, `database_config.py`
- **Measurement**: % actions that modify files within scope

**Phase** (Task Execution Phase)

- **Definition**: The current stage of problem-solving in a multi-step task.
- **Standard phases** (adapted from software debugging methodology):
    1. **Understand**: Read files, search code, analyze problem
        - Allowed tools: `read_file`, `grep`, `search`
        - Forbidden tools: `edit_file`, `submit`
    2. **Reproduce**: Run tests, observe failures
        - Allowed tools: `run_test`, `bash`
        - Forbidden tools: `edit_file` (don't fix before confirming bug)
    3. **Implement**: Modify code, make changes
        - Allowed tools: `edit_file`, `insert`, `replace`
        - Required before: Must have run failing test
    4. **Verify**: Test changes, check for regressions
        - Allowed tools: `run_test`
        - Required before: Must have edited at least one file
- **Transition logic**: Phases can overlap but must follow partial order (can't implement before understanding)
- **In practice**: Inferred from action history, not explicitly declared
    
    Mapping note (terminology alignment with implementation):
    Understand/Reproduce/Implement/Verify ↔ reproduce/modify/test/regress
    

**Action**

- **Definition**: A single atomic operation that an agent performs during task execution.
- **Types** (from SWE-bench agent toolkit):
    - Read: `read_file(path)`, `search(pattern)`, `grep(query)`
    - Write: `edit_file(path, old, new)`, `insert(path, line, content)`
    - Execute: `run_test(test_name)`, `bash(command)`
    - Control: `submit(solution)`, `rollback()`, `checkpoint()`
- **Metadata** (logged for each action):
    - Timestamp, current phase (inferred), files affected, success/failure outcome
- **Constraints**: Max 100 actions per task (SWE-bench standard), 5 min timeout per action
- **Why it matters**: Unit of analysis for drift detection (Q1) and efficiency measurement (Q2)

**Pattern**

- **Definition**: A reusable problem-solution pair extracted from a successfully completed task.
- **Components**:
    - Problem signature: Type of bug/issue (e.g., "null pointer exception")
    - Solution approach: General strategy (e.g., "add validation before object access")
    - Code template: Concrete implementation (optional, for Level 3)
- **Example**: "When encountering AttributeError on None, check for None before accessing attributes"

**Decontextualize**

- **Definition**: The process of transforming a context-specific solution into a general, transferable pattern.
- **Process**: Strip away specific variable names, file paths, and project details → Retain core logic and approach
- **Example transformation**:
    - Context-specific: "In `payment_processor.py:45`, added `if customer.account is None: return` before `customer.account.debit(amount)`"
    - Decontextualized: "Before accessing object attributes, validate that object is not None to prevent AttributeError"

**Extract**

- **Definition**: The automated process of identifying key patterns from successful task executions using LLM analysis.
- **Input**: Complete task trajectory (problem description, actions taken, final solution, test results)
- **Output**: Structured pattern with problem signature, solution approach, and abstraction levels
- **Trigger**: Only executed when task succeeds (all tests pass)

**Abstraction Level**

- **Definition**: The degree of detail in presenting a pattern, ranging from high-level hint to concrete implementation.
- **Three levels**:
    - Level 1 (Hint): One-sentence guidance (e.g., "Check for None before accessing attributes")
    - Level 2 (Explanation): Conceptual approach with key steps (e.g., "When object might be None: (1) add if-check, (2) handle None case, (3) proceed with safe access")
    - Level 3 (Code): Full implementation template with example
- **Selection criteria**: Based on task complexity, pattern familiarity, and agent's recent performance (Q3 research question)

**Context** (for Abstraction Selection)

- **Definition**: Observable signals about the current task and agent state that inform which abstraction level is most appropriate.
- **Three categories**:
    1. **Task indicators**: Problem statement length, # files mentioned, repository size
    2. **Pattern factors**: Times this pattern type has been seen (0 = first, 5+ = familiar)
    3. **Execution state**: # prior attempts on this task, recent action success rate
- **Key distinction**: All signals are observable from SWE-bench execution (no user profile needed)
- **Why it matters**: Enables dynamic selection without interactive user feedback
- **Example**:
    - High context (complex task + unfamiliar pattern + low success rate) → Level 3
    - Low context (simple task + familiar pattern + high success rate) → Level 1

---

### Data Structures

**SWE-bench Data Format**

- **Definition**: A benchmark dataset of 2,294 real-world GitHub issues from 12 popular Python repositories.
- **Key fields per task**:
    - `instance_id`: Unique identifier (e.g., "django__django-12453")
    - `problem_statement`: GitHub issue description (user-reported bug)
    - `repo`: Repository name and URL
    - `base_commit`: Git commit hash before the fix
    - `patch`: Ground truth solution (used only for evaluation, not visible to agent)
    - `test_patch`: Test file demonstrating the bug
    - `PASS_TO_PASS` / `FAIL_TO_PASS`: Test names that define success criteria
- **What it provides**: Real-world complexity, objective test-based evaluation, ground truth for comparison
- **What it lacks**: No interactive users; no time measurements
    - Note: Difficulty labels are available in the Verified subset and used for stratified analysis
- **Why SWE-bench for this research**:
    1. Objective evaluation: Test pass/fail eliminates subjective judgment
    2. Reproducibility: Dockerized environment ensures consistent results
    3. Real-world relevance: Issues from production codebases
    4. Community benchmarks: Enables comparison with published systems
    5. Scale: 500 tasks (SWE-bench Verified) provide statistical power for final evaluation

**Our Data Split (Final)**

- **Memory-building corpus (Q2)**: Use the official SWE-bench train split to extract/store patterns; strictly disjoint from final eval
- **Final evaluation (Q1–Q3)**: Full SWE-bench Verified (500) as the independent test set for reportable results
- **Supplementary**: Time-ordered subsets/CL used only to stress-test cross-session effects; main results remain on Verified
- **Why this split**: Ensures comparability/reproducibility (Verified) while enabling temporal analyses as add‑ons

**Task Execution** (in SWE-bench)

- **Definition**: A complete automated attempt to solve one SWE-bench task from start to terminal state.
- **Lifecycle**:
    - Begins with: Task loading and initial problem analysis
    - Contains: All agent actions (reads, edits, tests, searches)
    - Ends with: Test suite execution and pass/fail result
    - Duration: TBD (depends on action limit, typically 50-100 actions)
- **Characteristics**: Deterministic, automated, single-shot execution with no human intervention

**Chat Session** (in Cursor/AI Assistants)

- **Definition**: An interactive conversation between a human developer and an AI coding assistant for solving a coding problem.
- **Structure** (typical format):
    - User message: Task request or clarification
    - Assistant message: Analysis, code, or questions
    - Tool calls: File reads, edits, bash commands
    - Results: Output from tool executions
- **Lifecycle**:
    - Begins with: User's initial request
    - Contains: All user-AI exchanges and tool operations
    - Ends with: User satisfaction or abandonment
    - Duration: Variable (5 minutes to several hours)
- **Characteristics**: Interactive, non-deterministic, human-guided throughout
- **Key difference from Task Execution**:
    - Task Execution: Single initial prompt → automated agent → test evaluation
    - Chat Session: Back-and-forth dialogue → human guidance → subjective success
- **Our usage**: Supplementary data for validating chat2events extraction (not for quantitative evaluation)

**Baseline** (Comparison Systems)

- **Definition**: Reference systems used to evaluate relative performance of our approach.
- **External baselines** (three levels):
    1. **Weak baseline**: Vanilla GPT-4
        - Single-shot patch generation from problem statement
        - No tool use, no iteration
    2. **Medium baseline**: Static RAG
        - Retrieve similar past solutions (no decontextualization)
        - Present to agent without abstraction selection
    3. **Strong baseline**: AutoCodeRover (research baseline)
        - Published system; we report under the Verified split with split/time/scaffold noted (compute‑matched)
        - Static retrieval depth, no goal tracking
        - Reference: Zhang et al. 2024
- **Internal baselines** (for ablation):
    - **Unmonitored agent**: Our system WITHOUT drift detection (Q1 disabled)
        - Purpose: Measure Q1 effectiveness by comparing drift rate before/after monitoring
        - Expected: Higher drift rate than monitored version
    - Q1 only: Goal tracking without pattern memory
    - Q2 only: Pattern learning without goal tracking
    - Fixed-level: Pattern with Level 1/2/3 always (for Q3 comparison)
- **Measurement**: All baselines run on same test set for fair comparison

**Note on recent SOTA systems**: Recent proprietary systems (Claude 3.7: 70.3%, o3: 71.7%) achieve higher scores through massive test-time compute scaling ($1,600+ per task for o3). We compare against research systems with comparable compute budgets and documented methods (AutoCodeRover, SWE-agent) to evaluate our novel contributions—drift monitoring, pattern learning, and dynamic abstraction—rather than competing solely on compute resources. Our target (Verified, compute‑matched) is ≥30%, finalized after baseline runs.

---

### Assumptions

1. **Pattern transferability**: Patterns extracted from training tasks will be relevant to test tasks (validated through semantic similarity threshold ≥ 0.7 in retrieval).
2. **LLM extraction quality**: GPT-4o can reliably identify reusable patterns from successful solutions (will validate manually on sample of 20 patterns in Week 2).
3. **Guard weight tunability**: Optimal weights for Four-Guard system (currently 0.4/0.3/0.2/0.1) can be learned from training data (Week 1-2 tuning phase).
4. **Context signals sufficiency**: Task complexity can be estimated from observable features (problem statement length, number of files, repository size). For SWE-bench Verified subset, difficulty labels ("<15min", "15min-1h", "1-4h", ">4h") are available and can be used directly. For other datasets, we fall back to heuristic estimation.
5. **Action limit**: Agent can complete most tasks within 50-100 actions (standard SWE-bench practice).
6. **Test suite reliability**: SWE-bench test suites accurately reflect task success (validated by benchmark creators).
7. **Proxy metrics validity**: Action count and token usage serve as reasonable proxies for time savings when direct time measurement isn't available.
8. **Pattern diversity**: A subset of the official train split will yield diverse pattern types covering common bug categories (null checks, type mismatches, boundary conditions, concurrency). We will validate by inspecting problem statements in the memory-building corpus.
9. **Retrieval threshold**: Cosine similarity ≥ 0.7 is appropriate for semantic matching (too low = irrelevant patterns, too high = miss useful patterns). Will validate on validation set and adjust if needed.
10. **Single pattern per task**: For tasks with multiple matching patterns, agent receives top-1 pattern only (to avoid overwhelming context). Future work could explore multi-pattern presentation.
11. **Phase inference accuracy**: Current phase can be reliably inferred from action history using heuristics (e.g., no edits yet → understand phase). Will validate by manual inspection of 20 task executions in Week 1.
12. **File mention extraction**: Number of files mentioned in problem statement can be reliably extracted using NLP parsing (regex + heuristics). Will validate on sample of 20 problem statements in Week 1.

---

### Scaffold Config Template (minimal)

Example minimal YAML for the primary setup:

```yaml
scaffold_id: v1_verified_guard
tools:
  plan_then_edit: true
  allow_shell: test_only
  edit_granularity: hunk_or_file
q1:
  shadow_mode: true
  weights: {scope: 0.4, plan: 0.3, test: 0.2, evidence: 0.1}
  thresholds: {warn: 0.5, rollback: 0.8}
q2:
  tau: 0.70
  top_k: 3
  dedup: true
  compress: true
budget:
  per_task_cap_usd: 2.0
  max_steps: 100
  max_runtime_min: 30
logging:
  log_chain: true   # retrieve → present → adopt(level)
```

## Weekend update (week 5)

Week Summary

> After Wednesday’s first meeting with Yucheng, Alberto and I re-evaluated our direction. We moved away from terminology alignment and the survey-paper track, and refocused on the broader “agent memory” theme: learning from past experience of runs with cross-session memory and feedback to improve future outputs. We discussed next steps, demo settings and several key questions.
> 

> Getting permissions from Monica and Yucheng, we decided to split and proceed independently so each of us can pursue a clear, tractable scope. We chose to split because our problem framing, evaluation plan, and collaboration style diverged: Alberto preferred a code-with-context track, while I prioritized an adaptive memory system for coding agents. Alberto will continue with a code-with-context memory direction, and I will pursue an adaptive memory system for coding agents, targeting a 5–6 week demo.
> 

[2025-10-22 Changing Directions & Split](https://www.notion.so/2025-10-22-Changing-Directions-Split-29b74e3ea0038099ad10fd27e18e3316?pvs=21)

- **Adaptive Memory System for Coding Agents**
- **Adaptive Memory System for Coding Agents** 

**Part 1. Executive Summary**

**Oct 22 Yucheng's Research Direction [[Link to notes](https://www.notion.so/2025-10-22-1st-meeting-with-Yucheng-29474e3ea003803a93c2c6f0e9c040d0?pvs=21)]**: Agent memory systems that (1) learn across sessions, (2) improve from feedback, and (3) decontextualize specific experiences into transferable patterns. His key insight: *"abstraction level needs to be adjusted on the fly—nobody is doing that."*

**Key Questions**: Current coding agents (Cursor, Claude Code, SWE-agent) fail at critical tasks:

1. **Context Drift**: Agents stray from original objectives during multi-step tasks, attempting unnecessary refactoring or exploring irrelevant code paths
    - **Q1**: How can agents maintain goal alignment during long coding tasks?
2. **Zero Cross-Session Learning**: Each coding session starts from scratch—agents cannot leverage previously solved problems to accelerate future tasks
    - **Q2**: How can agents extract and reuse patterns across sessions?
3. **Static Abstraction**: Agents provide one-size-fits-all responses that don't adapt to user expertise or task complexity
    - **Q3**: How should abstraction levels adapt dynamically?

**Why Coding**: As Yucheng noted, coding is already an abstraction layer, making decontextualization tractable. We will use SWE-bench which provides 2,294 real-world tasks for rigorous evaluation.

**Novel Contribution**: Dynamic abstraction adjustment—the research gap Yucheng identified that "nobody is doing."


## 2025-11-10 
Overview: Meeting with Yucheng on Nov 5 to discuss context drift detection research direction. The project pivoted from terminology/agent memory to focusing specifically on context drift detection and intervention.

Method: Yucheng requires shifting from rule-based detection (hard-coded rules) to intent-based detection. Core approach: extract high-level intent/goal for each action, then analyze intent sequences to detect drift, rather than directly analyzing complex raw trajectories. This makes it easier to identify: same intent + repeated failures = Loop Drift, intent outside scope = Scope Drift.

Progress & Next Steps: 

1) Already completed manual annotation for 1 trajectory, including intent labeling, success/failure status, and drift identification. Built side-by-side table (left: raw actions, right: intent + drift detection). 

2) Next step: develop automation approach to scale intent extraction across more trajectories using LLM, test on 10-20 trajectories, and refine the method. Don't wait for perfect definitions—focus on proving the method works, then automate.

## 2025-11-12
自我反思：跟着导师做 coding agent 方向的 research，用的是 SWE-Bench Verify 这个数据集；你已经有了四个版本的 drift 定义，也知道可以直接利用网上现成的大模型 trajectories，而不用自己再去跑 Docker 或重跑模型，但你脑子很乱，一边在面试、一边落了几节课、一边又在想 research plan，卡在「怎么定义 drift、怎么实现、怎么往上抽象」这些问题上，导致没有真正把东西跑起来。下一步你要做的其实很简单、很具体：先选一小部分现成的 SWE-Bench Verify trajectory，把它们 parse 成一个统一的结构（按 task 拆成多步，每步包括 action、修改的文件、diff、测试结果等），然后从你已有的四个 drift 定义里先挑一个最重要的（比如 goal drift），写成一个可以对单步或整条 trajectory 判定 True/False 的函数，在这几条 trajectory 上跑一遍，算出最基本的统计——一共多少步被判定为 drift、一般出现在什么阶段、和任务成功/失败有没有明显相关——只要做到这一步，你就有了一个「跑得起来的最小框架」，可以跟导师清楚地说：我已经用自己的 drift 定义在 SWE-Bench trajectory 上做了初步检测和统计，接下来可以再增加其他几类 drift、再考虑 intent 标注和提醒机制以及是否要用 LLM 来做更高层的抽象。