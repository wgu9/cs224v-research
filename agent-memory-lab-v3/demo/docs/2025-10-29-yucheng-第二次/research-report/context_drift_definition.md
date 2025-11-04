# Context Drift: Formal Definition

**Date**: 2025-10-29
**Status**: Complete - Ready for Review
**Based on**: Literature survey of 30+ papers (2024-2025)

---

## Formal Definition

**Context Drift** is the **measurable divergence of an agent's behavioral trajectory from its specified objectives, manifested across three core dimensions over time in long-horizon tasks**.

Formally, an agent exhibits context drift when its action sequence A = {a₁, a₂, ..., aₜ} deviates from the optimal or expected trajectory A* given goal G and observations O, resulting in:

1. **Spatial violations**: Operating on resources R ⊄ R_authorized outside defined task boundaries
2. **Instrumental errors**: Selecting tools T_selected that are suboptimal or irrelevant for current sub-goals
3. **Temporal loops**: Repeating failed actions without learning, where ∃ action subsequences S_t ≈ S_{t-k} that both failed

**Key Properties**:
- **Measurable**: Quantifiable through metrics (EPR, PAC, Trajectory EM, Goal Adherence)
- **Multidimensional**: Manifests across spatial, instrumental, and temporal dimensions
- **Progressive**: Increases severity over trajectory length without intervention
- **Context-dependent**: Thresholds vary by task domain (coding, web, API)

**Why "Context Drift" (New Terminology)**:
The literature uses 10+ fragmented terms (task derailment, goal drift, behavioral drift, etc.) without consensus. We propose "Context Drift" as the **unifying framework** that:
- Bridges short-term task derailment and long-term goal drift
- Encompasses both spatial (scope) and temporal (loops) dimensions
- Provides operational definition for detection and measurement

---

## Scope

### Context drift applies to:
- **Long-horizon agent tasks**: >10 steps, requiring sustained goal maintenance
- **Goal-oriented agents**: Systems with explicit objectives or task specifications
- **Sequential decision-making**: Multi-step trajectories where early errors affect later actions
- **Partially observable environments**: Where agents must maintain context across observations
- **Tool-using agents**: Systems with access to multiple functions/APIs/commands

### Context drift does NOT apply to:
- **Single-turn interactions**: No trajectory to drift from (e.g., simple Q&A)
- **Exploration tasks**: Where "drift" is intentional discovery
- **Adversarial testing**: Where deviation is the goal (e.g., jailbreaking)
- **Human-in-the-loop**: Where human constantly corrects (no autonomous drift)

---

## Dimensions of Context Drift

Based on literature survey and quantitative evidence from 30+ papers, we identify **three core dimensions**:

### Dimension 1: Scope Drift (Spatial) ⭐ PRIORITY

**Formal Definition**:
An agent exhibits scope drift at step t when it operates on resources R_accessed ⊄ R_authorized outside the defined task boundary, or pursues sub-goals G_current ⊄ G_specified not aligned with the specified objective.

**Literature Terms** (unified by our definition):
- Task Derailment (MAST 2025): 7.15% of failures
- Goal Drift (Arike et al. 2025): Deviation over 100k+ tokens
- Disobey Task Specification (MAST)
- Constraint Ignorance (AgentErrorBench)

**Why it matters**:
- **Prevalence**: Appears in 12/30 papers surveyed
- **Cross-domain**: Manifests in coding (SWE-bench), web (WebArena), API tasks (τ-bench)
- **Safety-critical**: Unauthorized access, privilege escalation (MI9)
- **Resource waste**: Modifying irrelevant files, accessing unnecessary data
- **Task failure**: 7.15% baseline failure rate (MAST)

**When it occurs**:
- Agent edits files outside PR scope (SWE-bench)
- Agent navigates to irrelevant website sections (WebArena)
- Agent calls APIs without proper authorization (τ-bench, MI9)
- Agent pursues tangential sub-goals unrelated to main task
- Agent breaks existing functionality while fixing one issue

**How we detect it** (5 methods from literature):

1. **Goal Adherence Score** (Goal Drift paper, AAAI 2025):
   ```
   GA(t) = 1 - (Runtime_investment(t) / Baseline_investment)
   Threshold: GA < θ_GA indicates drift
   Tested over 100k+ tokens
   ```

2. **Boundary Violation Count**:
   ```
   BV = |R_accessed - R_authorized| / |R_authorized|
   Threshold: BV > 0.3 indicates high drift
   ```

3. **Jensen-Shannon Divergence** (MI9, arXiv 2024):
   ```
   JS(P(actions|goal,t₀) || P(actions|goal,t)) > 0.2
   99.81% detection rate in 1,033 scenarios
   ```

4. **FSM Conformance** (MI9):
   - Define allowed state transitions as finite-state machine
   - Track privilege escalations and temporal policy violations
   - Binary: conforming or non-conforming

5. **Pass-to-Pass Testing** (SWE-bench):
   - Ensure existing tests still pass
   - Measure: Tests_passed_before = Tests_passed_after
   - Violations indicate scope drift

**Literature Support** (12 papers):
- MAST (arXiv 2025): Task derailment 7.15%
- Goal Drift (AAAI 2025): 100k+ token evaluation
- MI9 (arXiv 2024): 99.81% detection, FSM conformance
- SWE-bench (ICLR 2024): Pass-to-pass tests
- TheAgentCompany (arXiv 2024): Checkpoint evaluation
- AgentBoard (NeurIPS 2024): Fine-grained progress tracking
- Microsoft AI Red Team (2025): Goal/behavioral drift taxonomy
- [5 additional papers - see literature survey]

**Quantitative Evidence**:
- 7.15% of MAS failures due to task derailment (MAST)
- 99.81% detection rate with MI9 framework
- Goal Adherence measurable over 100k+ tokens

---

### Dimension 2: Tool Drift (Instrumental)

**Formal Definition**:
An agent exhibits tool drift when it selects tools T_selected that are inappropriate, irrelevant, or suboptimal for current sub-goals G_sub given available context C, resulting in Trajectory_EM < 0.5 or pass^k consistency < 0.5 for k≥4.

**Literature Terms** (unified by our definition):
- Similar Tool Confusion (TRAJECT-Bench)
- Parameter-Blind Tool Selection (TRAJECT-Bench)
- Redundant Tool Calling (TRAJECT-Bench)
- Wrong Tool/Wrong Argument (τ-bench)
- Relevance Detection Failures (ToolACE, BFCL)

**Why it matters**:
- **Prevalence**: Appears in 8/30 papers surveyed
- **Scaling bottleneck**: 5-7 tools is critical failure point (TRAJECT-Bench)
- **Resource waste**: Unnecessary API calls, redundant operations
- **Efficiency loss**: 25% pass rate on 8 trials (τ-bench) indicates severe instability
- **Compounding errors**: Wrong tool leads to wrong output, propagating downstream

**When it occurs**:
- Agent selects visually similar tools without checking parameters (TRAJECT-Bench)
- Agent calls APIs repeatedly with same failed parameters (τ-bench)
- Agent uses tools when none are appropriate (ToolACE)
- Agent confuses overlapping tool capabilities (5-7 tool threshold)
- Agent invokes functions with incorrect argument types (BFCL)

**How we detect it** (4 methods from literature):

1. **Trajectory Exact-Match (EM)** (TRAJECT-Bench, arXiv 2024):
   ```
   Trajectory_EM = |T_selected ∩ T_optimal| / |T_optimal|
   Threshold: EM < 0.5 indicates tool drift
   Best models (Claude-4, Gemini-2.5): ~44-45% on hard queries
   ```

2. **pass^k Consistency** (τ-bench, arXiv 2024):
   ```
   pass^k = Success_rate over k trials
   Threshold: pass^k < 0.5 for k≥4 indicates instability
   Evidence: pass^8 < 25% (severe drift)
   Single trial: <50% success
   ```

3. **Relevance Detection** (ToolACE, ICLR 2025):
   ```
   Relevance(tool_i, context_t) = P(tool_i relevant | context_t)
   Threshold: < 0.3 = irrelevant
   Detection accuracy: 89.17%
   ```

4. **Tool Selection Stability**:
   ```
   Stability = Var(tool_selections across trials)
   Threshold: High variance = drift
   ```

**Literature Support** (8 papers):
- TRAJECT-Bench (arXiv 2024): Similar tool confusion, 5-7 tool bottleneck
- τ-bench (arXiv 2024): pass^8 < 25%, wrong tool/argument
- ToolACE (ICLR 2025): 89.17% irrelevant detection, 91.41% BFCL
- BFCL (2024): AST validation, 2000 Q-A pairs
- TPTU-v2 (EMNLP 2024): API Retriever framework
- [3 additional papers - see literature survey]

**Quantitative Evidence**:
- 5-7 tools = critical scaling bottleneck (TRAJECT-Bench)
- pass^8 drops to 25% (τ-bench)
- 89.17% irrelevant tool detection (ToolACE)
- 91.41% overall function calling accuracy (BFCL)

---

### Dimension 3: Loop Drift (Temporal) ⭐⭐ HIGHEST PRIORITY (Yucheng Emphasis)

**Formal Definition**:
An agent exhibits loop drift when it repeats failed actions without correction, indicated by EPR₁₀ > 0.15 or repeated action subsequences S_t ≈ S_{t-k} where both failed, demonstrating failure to learn from feedback.

**Literature Terms** (unified by our definition):
- **Error Propagation** (AgentErrorBench): "Primary bottleneck to LLM agent reliability"
- Cascading Failures (ReCAPA)
- Infinite Loops (Retroformer)
- Recursive Planning Loops (MI9)
- Self-Conditioning on Errors (ICLR 2025)
- Step Repetition (MAST)

**Why it matters** - **MOST IMPORTANT DIMENSION**:
- **Primary bottleneck**: AgentErrorBench explicitly identifies error propagation as #1 failure mode
- **Prevalence**: Appears in 10/30 papers surveyed
- **Quantitative metrics**: ReCAPA provides first metrics (EPR, PAC)
- **Yucheng emphasis**: "Especially evident in τ-Bench and WebArena"
- **Task failure**: Leads to unrecoverable failures, no learning
- **Resource waste**: Repeated failing attempts consume compute

**When it occurs**:
- Agent applies same code patch after test failure (SWE-bench)
- Agent calls same API with failed parameters repeatedly (τ-bench)
- Agent clicks same broken UI element multiple times (WebArena)
- Agent repeats same failed search query (web research)
- Agent gets stuck in frozen self-reflection loops (Retroformer)
- Early errors distort later reasoning, compounding degradation

**How we detect it** (4 methods from literature):

1. **Error Propagation Rate (EPR)** (ReCAPA, ICLR 2026 under review):
   ```
   EPRₖ = Pr(error at t₀+k | error at t₀) - Pr(error at t₀+k | no error at t₀)

   Threshold: EPR₁₀ > 0.15 indicates severe drift

   Benchmarks:
   - ReCAPA: EPR₁₀ = 0.082 (best)
   - GPT-4o-mini: EPR₁₀ = 0.3
   - Claude-4-sonnet: EPR₁₀ = 0.45
   ```

2. **Propagation Attenuation Coefficient (PAC)** (ReCAPA):
   ```
   PAC = -slope(Δ, ln Pr(error at t₀+Δ | error at t₀))

   Threshold: PAC < 0.05 indicates risk not dissipating
   Measures how quickly error risk decays
   ```

3. **Loop Pattern Detection** (Retroformer, ICLR 2024):
   ```
   Detect: ∃ subsequences S_t, S_{t-k} where:
   - Similarity(S_t, S_{t-k}) > 0.8 (using embeddings)
   - Both failed
   - No learning occurred

   Retroformer improvements: +18% HotPotQA, +36% ALFWorld
   ```

4. **Root-Cause Attribution** (AgentErrorBench):
   ```
   Modular error taxonomy:
   - Memory errors: 38 instances
   - Reflection errors: 39 instances
   - Planning errors: 78 instances (most common)
   - Action errors
   - System errors

   AgentDebug: 24.3% all-correct (vs 0.3% baseline)
   ```

**Literature Support** (10 papers) - **STRONGEST EVIDENCE**:
- **AgentErrorBench** (ICLR 2026): Error propagation is PRIMARY bottleneck
- **ReCAPA** (ICLR 2026): First quantitative metrics EPR, PAC
- **τ-bench** (arXiv 2024): pass^8 < 25% - Yucheng emphasized
- **WebArena** (ICLR 2024): Navigation loops - Yucheng emphasized
- Retroformer (ICLR 2024): Infinite loops documented, +36% improvement
- MI9 (arXiv 2024): Recursive planning loops
- MAST (arXiv 2025): Step repetition
- [3 additional papers - see literature survey]

**Quantitative Evidence**:
- EPR₁₀ = 0.082 (ReCAPA) vs 0.3-0.45 (baselines) - **50-80% reduction**
- pass^8 < 25% (τ-bench) - **severe consistency failure**
- AgentDebug: 24.3% vs 0.3% baseline - **80x improvement**
- Retroformer: +36% improvement (ALFWorld) with loop prevention
- Most failures occur steps 6-15 (mid-trajectory clustering)

---

## Justification for Each Dimension

**Why these three dimensions and not others?**

Our selection of Scope Drift, Tool Drift, and Loop Drift is **NOT arbitrary** - it is grounded in:

### 1. Literature Coverage
- **Scope Drift**: 12/30 papers (40% prevalence)
- **Tool Drift**: 8/30 papers (27% prevalence)
- **Loop Drift**: 10/30 papers (33% prevalence)
- **Total**: All 3 dimensions appear in 30/30 papers combined

### 2. Quantitative Metrics Availability
Each dimension has **measurable, validated metrics**:
- **Scope**: Goal Adherence (100k+ tokens), JS Divergence (99.81% detection), BV count
- **Tool**: Trajectory EM (44-45% best models), pass^k (<25% at k=8), Relevance (89.17%)
- **Loop**: EPR (0.082 vs 0.3+), PAC (<0.05), Root-cause attribution (80x improvement)

### 3. Cross-Domain Generalization
All 3 dimensions manifest across multiple task types:
- **SWE-bench** (coding): Scope (file edits), Tool (commands), Loop (patches)
- **τ-Bench** (API): Scope (authorization), Tool (selection), Loop (retries)
- **WebArena** (web): Scope (navigation), Tool (interactions), Loop (clicks)

### 4. Temporal Coverage
The 3 dimensions capture different failure modes:
- **Scope**: Where the agent operates (spatial)
- **Tool**: How the agent acts (instrumental)
- **Loop**: When errors compound (temporal)

### 5. Theoretical Orthogonality
The dimensions are **independent and complementary**:
- Agent can have high Scope Drift but low Loop Drift (explores wrong areas efficiently)
- Agent can have low Scope Drift but high Tool Drift (stays in scope but uses wrong tools)
- Agent can have low Scope+Tool but high Loop Drift (right place, right tools, but repeats failures)

### 6. Actionable Intervention
Each dimension has **distinct remediation strategies**:
- **Scope**: Boundary enforcement, goal reminders
- **Tool**: Tool recommendation, parameter validation
- **Loop**: Error detection, retry limiting, alternative strategies

### 7. Industry Validation
Microsoft AI Red Team (2025) explicitly includes "goal drift, context drift, behavior drift" in their taxonomy, confirming **industry recognition** of these failure modes.

**Dimensions Explicitly NOT Chosen** (and why):
- **Hallucination**: Covered by Tool Drift (selecting non-existent tools) and Scope Drift (accessing non-existent resources)
- **Formatting Errors**: Too specific to coding tasks, not generalizable
- **Communication Failures**: Primarily multi-agent (out of scope for single-agent focus)
- **Lack of Evidence**: Overlaps with Tool Drift (wrong information source) and Scope Drift (wrong data accessed)

**Conclusion**: Our 3 dimensions represent the **minimal sufficient set** to characterize context drift across domains, supported by 30+ papers, measurable metrics, and cross-benchmark validation.

---

## Relationship to Related Concepts

### vs. Goal Drift (Arike et al., AAAI 2025)
**Relationship**: Goal Drift is a **subset** of our Scope Drift dimension.
- **Goal Drift**: Agent deviates from original objective over time (100k+ tokens)
- **Scope Drift**: Agent deviates from task boundary (includes goal drift + resource violations + constraint violations)
- **Our contribution**: We extend goal drift with spatial constraints and quantitative boundary metrics

### vs. Task Derailment (MAST, 2025)
**Relationship**: Task Derailment is the **literature term** for our Scope Drift.
- **Task Derailment**: 7.15% of failures in MAST taxonomy
- **Scope Drift**: Our unified term bridging task derailment, goal drift, constraint ignorance
- **Our contribution**: We provide operational definition with 5 detection methods

### vs. Error Propagation (AgentErrorBench, ReCAPA)
**Relationship**: Error Propagation is the **literature term** for our Loop Drift.
- **Error Propagation**: Primary bottleneck (AgentErrorBench), quantified by EPR/PAC (ReCAPA)
- **Loop Drift**: Our unified term for all repetitive mistake patterns
- **Our contribution**: We extend EPR/PAC with loop pattern detection and root-cause attribution

### vs. Off-Policy Behavior (Reinforcement Learning)
**Relationship**: Context Drift is **orthogonal** to off-policy RL concepts.
- **Off-Policy**: Behavior policy ≠ target policy (intentional for exploration)
- **Context Drift**: Behavior deviates from specified goal (unintentional failure)
- **Key difference**: Off-policy is a training strategy; drift is a failure mode

### vs. Behavioral Drift (Microsoft, 2025)
**Relationship**: Behavioral Drift is the **industry term**, we provide academic rigor.
- **Behavioral Drift**: Industry taxonomy term (Microsoft AI Red Team)
- **Context Drift**: Academic framework with formal definitions, metrics, detection methods
- **Our contribution**: Bridge industry awareness with research-grade evaluation

---

## Context Drift Index (CDI): Unified Scoring

### Formula

```
CDI = w₁·ScopeScore + w₂·ToolScore + w₃·LoopScore

Where:
- ScopeScore ∈ [0, 1]: Normalized scope drift severity
- ToolScore ∈ [0, 1]: Normalized tool drift severity
- LoopScore ∈ [0, 1]: Normalized loop drift severity
- w₁, w₂, w₃: Task-dependent weights (∑wᵢ = 1)
```

### Suggested Weights

**General Long-Horizon Tasks** (default):
```
w₁ = 0.4 (Scope)
w₂ = 0.3 (Tool)
w₃ = 0.3 (Loop)

Rationale: Scope violations most severe (safety-critical)
```

**Coding Tasks** (SWE-bench):
```
w₁ = 0.5 (Scope - file boundaries critical)
w₂ = 0.2 (Tool - fewer tools)
w₃ = 0.3 (Loop - patch retries common)
```

**API Tasks** (τ-Bench):
```
w₁ = 0.3 (Scope - database states)
w₂ = 0.4 (Tool - many APIs, 5-7 tool bottleneck)
w₃ = 0.3 (Loop - consistency failures)
```

**Web Tasks** (WebArena):
```
w₁ = 0.4 (Scope - navigation boundaries)
w₂ = 0.3 (Tool - interaction types)
w₃ = 0.3 (Loop - Yucheng: "especially evident")
```

### Component Score Calculations

**ScopeScore Calculation**:
```python
# Normalize multiple scope metrics
GA = Goal_Adherence(t)  # [0, 1]
BV = Boundary_Violations / Total_actions  # [0, 1]
JS = min(Jensen_Shannon_Divergence / 0.2, 1.0)  # normalize by threshold

ScopeScore = (GA + BV + JS) / 3  # average
```

**ToolScore Calculation**:
```python
# Normalize multiple tool metrics
TEM = 1 - Trajectory_EM  # invert (high EM = low drift)
Consistency = 1 - pass_k  # invert (high pass = low drift)
Relevance = Irrelevant_tools / Total_tools

ToolScore = (TEM + Consistency + Relevance) / 3  # average
```

**LoopScore Calculation**:
```python
# Normalize multiple loop metrics
EPR_norm = min(EPR_10 / 0.15, 1.0)  # normalize by threshold
PAC_norm = 1 - min(PAC / 0.05, 1.0)  # invert (high PAC = low drift)
Loop_detected = 1.0 if loop_pattern else 0.0

LoopScore = (EPR_norm + PAC_norm + Loop_detected) / 3  # average
```

### CDI Interpretation

| CDI Range | Severity | Interpretation | Action |
|-----------|----------|----------------|--------|
| **0.0 - 0.2** | Very Low | Minimal drift, on-track | Continue monitoring |
| **0.2 - 0.4** | Low | Slight deviations, manageable | Optional feedback |
| **0.4 - 0.6** | Medium | Noticeable drift, intervention helpful | Provide corrective feedback |
| **0.6 - 0.8** | High | Significant drift, likely task failure | Strong intervention required |
| **0.8 - 1.0** | Critical | Severe drift, task failure imminent | Emergency stop / rollback |

---

## Mapping to Prior Work

| Our Dimension | Related Work (Paper) | Their Term | Metric |
|---------------|---------------------|------------|--------|
| **Scope Drift** | MAST (2025) | Task Derailment | 7.15% failure rate |
| | Goal Drift (AAAI 2025) | Goal Drift | GA score, 100k+ tokens |
| | MI9 (2024) | Privilege Escalation | 99.81% detection |
| | SWE-bench (2024) | Pass-to-Pass Failures | Binary |
| | AgentErrorBench (2026) | Constraint Ignorance | Categorical |
| **Tool Drift** | TRAJECT-Bench (2024) | Similar Tool Confusion | Trajectory EM < 0.5 |
| | τ-bench (2024) | Wrong Tool/Argument | pass^8 < 25% |
| | ToolACE (2025) | Relevance Detection | 89.17% accuracy |
| | BFCL (2024) | Function Calling Errors | 91.41% AST accuracy |
| **Loop Drift** | AgentErrorBench (2026) | Error Propagation | Primary bottleneck |
| | ReCAPA (2026) | Cascading Failures | EPR=0.082, PAC |
| | Retroformer (2024) | Infinite Loops | +36% improvement |
| | MI9 (2024) | Recursive Planning Loops | Categorical |
| | MAST (2025) | Step Repetition | Frequency count |

**Key Insight**: Our "Context Drift" framework **unifies 10+ fragmented terms** under a single operational definition with consistent metrics.

---

## Success Criteria

### An agent trajectory has **HIGH context drift** (CDI > 0.6) if:
1. **Scope violations**: Accesses >30% resources outside authorized boundary (BV > 0.3)
2. **Tool instability**: Trajectory EM < 0.5 OR pass^k < 0.5 for k≥4
3. **Error loops**: EPR₁₀ > 0.15 OR detected repeated action patterns without learning
4. **Combined**: CDI composite score exceeds 0.6 threshold

### An agent trajectory has **LOW context drift** (CDI < 0.2) if:
1. **Scope adherence**: Goal Adherence > 0.8, minimal boundary violations (BV < 0.1)
2. **Tool accuracy**: Trajectory EM > 0.8 AND pass^k > 0.8 for k≥4
3. **Error recovery**: EPR₁₀ < 0.1, PAC > 0.1 (errors dissipate quickly)
4. **Combined**: CDI composite score below 0.2 threshold

---

## Examples Across Benchmarks

### Example 1: HIGH Drift (SWE-bench)

**Task**: Fix null pointer exception in `payment/processor.py`

**Agent Trajectory**:
```
Step 1: Read error trace → identifies line 42 in processor.py ✓
Step 2: Edit payment/processor.py → adds null check ✓ (CORRECT SCOPE)
Step 3: Run tests → test_payment.py fails ✗
Step 4: Edit payment/database.py → modifies schema ✗ (SCOPE DRIFT - irrelevant file)
Step 5: Edit utils/config.py → changes timeout ✗ (SCOPE DRIFT)
Step 6: Re-edit payment/processor.py with SAME patch ✗ (LOOP DRIFT - repeated action)
Step 7: Edit auth/permissions.py ✗ (SCOPE DRIFT)
Step 8: Re-run test → still fails ✗
Step 9: Re-edit payment/processor.py with SAME patch again ✗ (LOOP DRIFT)
Step 10: Task failure
```

**Drift Analysis**:
- **Scope Drift**:
  - Authorized: `payment/processor.py`, `payment/test_payment.py`
  - Accessed: `database.py`, `config.py`, `permissions.py` (3 violations)
  - BV = 3/5 = 0.6 (HIGH)
  - ScopeScore = 0.6

- **Tool Drift**:
  - Optimal tools: Read, Edit (targeted), Test
  - Used tools: Read, Edit (scattered), Test
  - Trajectory EM = 0.4 (LOW - wrong file targets)
  - ToolScore = 0.6

- **Loop Drift**:
  - Step 6 repeats Step 2 (same patch)
  - Step 9 repeats Step 2/6 (third time!)
  - No learning between attempts
  - EPR₁₀ estimate: 0.4 (HIGH)
  - LoopScore = 0.8

**CDI Calculation** (SWE-bench weights: 0.5, 0.2, 0.3):
```
CDI = 0.5 × 0.6 + 0.2 × 0.6 + 0.3 × 0.8
    = 0.3 + 0.12 + 0.24
    = 0.66 (HIGH DRIFT)
```

**Verdict**: HIGH context drift → Strong intervention required

---

### Example 2: LOW Drift (SWE-bench)

**Task**: Fix null pointer exception in `payment/processor.py`

**Agent Trajectory**:
```
Step 1: Read error trace → identifies line 42 in processor.py ✓
Step 2: Read payment/processor.py → analyzes code ✓
Step 3: Edit payment/processor.py → adds null check at line 41 ✓ (CORRECT)
Step 4: Run tests → test_payment.py passes ✓
Step 5: Run full test suite → all pass ✓
Step 6: Task success ✓
```

**Drift Analysis**:
- **Scope Drift**:
  - Authorized: `payment/processor.py`, `payment/test_payment.py`
  - Accessed: Only these files
  - BV = 0/4 = 0.0 (NONE)
  - ScopeScore = 0.0

- **Tool Drift**:
  - Optimal tools: Read, Edit (targeted), Test
  - Used tools: Exactly optimal sequence
  - Trajectory EM = 1.0 (PERFECT)
  - ToolScore = 0.0

- **Loop Drift**:
  - No repeated actions
  - Linear progression to success
  - EPR₁₀ = 0.0 (NONE)
  - LoopScore = 0.0

**CDI Calculation**:
```
CDI = 0.5 × 0.0 + 0.2 × 0.0 + 0.3 × 0.0
    = 0.0 (VERY LOW DRIFT)
```

**Verdict**: VERY LOW drift → Continue monitoring

---

### Example 3: MEDIUM Drift (τ-Bench)

**Task**: Update customer address using Retail API

**Agent Trajectory**:
```
Step 1: Call get_customer(id=123) → returns customer data ✓
Step 2: Call update_address(id=123, street="5th Ave") → missing zip, fails ✗
Step 3: Call update_address(id=123, street="5th Ave") → SAME call, fails ✗ (LOOP DRIFT)
Step 4: Call update_customer(id=123, full_data) → wrong API ✗ (TOOL DRIFT)
Step 5: Call update_address(id=123, street="5th Ave", zip="10001") → success ✓
```

**Drift Analysis**:
- **Scope Drift**:
  - All API calls within authorized customer record
  - No privilege escalation
  - ScopeScore = 0.1 (minimal)

- **Tool Drift**:
  - Optimal: get_customer, update_address (with correct params)
  - Used: get_customer, update_address (wrong params), update_customer (wrong API)
  - Trajectory EM = 0.6
  - pass^k: 1/3 trials succeed → 0.33 (LOW consistency)
  - ToolScore = 0.5

- **Loop Drift**:
  - Step 3 repeats Step 2 exactly (no param adjustment)
  - EPR₁₀ estimate: 0.2 (MODERATE)
  - LoopScore = 0.4

**CDI Calculation** (τ-bench weights: 0.3, 0.4, 0.3):
```
CDI = 0.3 × 0.1 + 0.4 × 0.5 + 0.3 × 0.4
    = 0.03 + 0.2 + 0.12
    = 0.35 (MEDIUM DRIFT)
```

**Verdict**: MEDIUM drift → Optional corrective feedback helpful

---

### Example 4: HIGH Loop Drift (WebArena)

**Task**: Add item to shopping cart on e-commerce site

**Agent Trajectory**:
```
Step 1: Navigate to products page ✓
Step 2: Click product "Laptop" ✓
Step 3: Click "Add to Cart" button → fails (out of stock) ✗
Step 4: Click "Add to Cart" button → fails again ✗ (LOOP - no learning)
Step 5: Click "Add to Cart" button → fails again ✗ (LOOP)
Step 6: Click "Add to Cart" button → fails again ✗ (LOOP)
Step 7: Click "Add to Cart" button → fails again ✗ (LOOP - 5x repetition!)
Step 8: Navigate to cart → empty, task failure ✗
```

**Drift Analysis**:
- **Scope Drift**:
  - Stayed within product/cart pages (correct scope)
  - ScopeScore = 0.1

- **Tool Drift**:
  - Should have tried different product or checked stock
  - Stuck with one interaction type (click)
  - ToolScore = 0.3

- **Loop Drift**:
  - Repeated identical click 5 times
  - No alternative strategy
  - **Yucheng: "especially evident in WebArena"** ✓ confirmed
  - EPR₁₀ = 0.5 (SEVERE)
  - LoopScore = 1.0 (CRITICAL)

**CDI Calculation** (WebArena weights: 0.4, 0.3, 0.3):
```
CDI = 0.4 × 0.1 + 0.3 × 0.3 + 0.3 × 1.0
    = 0.04 + 0.09 + 0.3
    = 0.43 (MEDIUM-HIGH DRIFT)
```

**Verdict**: MEDIUM-HIGH drift, dominated by loop drift → Emergency loop detection required

---

## Cross-Benchmark Summary

| Benchmark | Primary Drift Mode | Typical CDI | Key Indicator |
|-----------|-------------------|-------------|---------------|
| **SWE-bench** | Scope Drift | 0.3-0.7 | File edit boundaries |
| **τ-Bench** | Tool + Loop Drift | 0.4-0.6 | pass^k < 25%, API consistency |
| **WebArena** | Loop Drift | 0.4-0.8 | Repeated clicks (Yucheng emphasis) |
| **General** | Balanced | 0.2-0.6 | CDI composite |

---

## Next Steps

After finalizing this definition:
1. **✅ Send to Yucheng for review** ← IMMEDIATE
2. Create Detection Cards for each dimension (using SPHERE methodology)
3. Deep research τ-Bench and WebArena (trajectory formats, datasets)
4. Implement detection algorithms (Week 3)
5. Validate on real trajectories (Week 4)

---

**Review Checklist**:
- [x] All dimensions have clear formal definitions
- [x] All dimensions have literature support (30+ papers)
- [x] All dimensions have justification (NOT arbitrary - 7 criteria)
- [x] Quantitative metrics specified (EPR, PAC, Trajectory EM, GA, etc.)
- [x] Examples provided across all 3 benchmarks
- [x] CDI formula with task-specific weights
- [x] Relationship to prior work clarified
- [ ] **Send to Yucheng for review** ← NEXT ACTION

---

**Status**: This definition is **COMPLETE** and ready for Yucheng's review. It establishes:

1. ✅ **Unified "Context Drift" framework** bridging 10+ fragmented terms
2. ✅ **Three literature-justified dimensions** (not arbitrary)
3. ✅ **Quantitative metrics from 30+ papers** (EPR, PAC, Trajectory EM, etc.)
4. ✅ **Cross-benchmark generalization** (SWE-bench, τ-Bench, WebArena)
5. ✅ **CDI composite scoring** with task-specific weights
6. ✅ **Concrete examples** demonstrating detection in practice
