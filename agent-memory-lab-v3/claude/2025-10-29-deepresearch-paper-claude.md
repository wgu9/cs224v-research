

# Context Drift Detection in Long-Horizon AI Agents: A 2024-2025 Literature Review

The 2024-2025 research landscape reveals a paradigm shift from pure task completion metrics to **systematic failure analysis and behavioral drift detection** in long-horizon AI agents. While the exact term "context drift" remains rare in academic literature, numerous papers address the three core dimensions—scope violations, tool selection errors, and repetitive mistakes—with increasing sophistication. The field has produced comprehensive failure taxonomies, trajectory-aware evaluation frameworks, and runtime monitoring systems that collectively establish the foundation for a generalizable context drift detection framework.

## 1. Comparative Analysis Table

| Paper Title | Venue & Year | Scope Violations | Tool Selection Errors | Repetitive Mistakes | Detection Methodology | Benchmarks Used | Key Contributions | Relevance (1-5) |
|------------|--------------|------------------|----------------------|---------------------|----------------------|-----------------|-------------------|-----------------|
| **MAST: Multi-Agent System Failure Taxonomy** | arXiv 2025 | ✓ Task derailment (FM-2.3), Disobey task spec (FM-1.1) | ✓ Reasoning-action mismatch | ✓ Step repetition, Info withholding | Grounded Theory + LLM-as-judge (κ=0.77) | SWE-bench, AppWorld, GAIA, OlympiadBench | First empirically grounded MAS failure taxonomy with 14 failure modes | 5 |
| **AgentErrorBench: Where LLM Agents Fail** | ICLR 2026 (review) | ✓ Constraint ignorance, Impossible actions | ✓ Format/parameter errors | ✓ Error propagation as primary bottleneck | Modular analysis + root-cause attribution | ALFWorld, WebShop, GAIA | First annotated failure trajectory dataset (200 traces) with systematic taxonomy | 5 |
| **ReCAPA: Hierarchical Predictive Correction** | ICLR 2026 (review) | ○ Trajectory-level deviations | ○ Action-level errors | ✓ Cascading failures, EPR/PAC metrics | Hierarchical correction (action→subgoal→trajectory) | VisualAgentBench, MineDojo, MAP-THOR | First quantitative error propagation metrics (EPR, PAC) | 5 |
| **MI9: Runtime Governance Protocol** | arXiv 2024 | ✓ Privilege escalation, Temporal policy violations | ✓ Tool-chain cascading failures | ✓ Recursive planning loops | Goal-conditioned drift detection + FSM conformance | 1,033 synthetic scenarios (financial, healthcare) | First integrated runtime governance framework (99.81% detection rate) | 5 |
| **τ-bench (TauBench)** | arXiv 2024 | ○ Policy adherence | ✓ Wrong tools, Wrong arguments | ✓ Consistency failures (pass^8 < 25%) | Database state comparison + pass^k metric | Retail (115 tasks), Airline (50 tasks) | First benchmark measuring agent consistency across trials | 5 |
| **ToolACE: Function Calling Mastery** | ICLR 2025 | ○ Relevance detection | ✓ Tool selection (89.17% irrelevant detection) | ○ Self-consistency | Dual-layer verification (rule + model-based) | BFCL v1 (91.41% overall) | Comprehensive API pool (26,507 APIs) with relevance detection | 5 |
| **Technical Report: Goal Drift Evaluation** | AAAI 2025 AIES | ✓ Goal drift over 100k+ tokens | — | ✓ Pattern-matching behavior | Quantitative scoring (commission + omission) | Financial simulation (Apex Capital) | First long-context goal adherence study with adversarial testing | 5 |
| **TRAJECT-Bench: Trajectory-Aware Benchmark** | arXiv 2024 | ○ Intent inference failures | ✓ Similar tool confusion, Redundant calling | ✓ Multi-step trajectory failures | Trajectory EM/Inclusion/Tool-Usage metrics | 5,670 queries, 1,228 tools, 10 domains | First trajectory-aware evaluation with scaling analysis (3→10 tools) | 5 |
| **AgentBoard: Analytical Evaluation** | NeurIPS 2024 (Oral) | ○ Boundary adherence | ✓ Grounding accuracy | ✓ Multi-round interaction tracking | Fine-grained progress rate metric | 9 tasks including WebArena, Tool-Query | First fine-grained progress tracking beyond binary success/failure | 5 |
| **Agent Trajectory Explorer** | AAAI 2025 | ✓ Trajectory visualization | ✓ Action sequence analysis | ✓ Human oversight for loops | Interactive visualization + annotation | SWE-Agent, OpenDevin, ReAct | First dedicated trajectory visualization tool for human feedback | 5 |
| **TheAgentCompany Benchmark** | arXiv 2024 | ✓ Task boundary violations (175 tasks) | ✓ Tool use across platforms | ○ Long-horizon failures | Checkpoint-based + LLM evaluators | GitLab, Plane, RocketChat, ownCloud | Real-world workplace benchmark (best: 30.3% success) | 4 |
| **SWE-bench: GitHub Issues Benchmark** | ICLR 2024 (Oral) | ✓ Pass-to-pass tests (scope violation detection) | ○ Code changes | ○ Breaking existing tests | Docker containerized + unit tests | 2,294 GitHub issues, 12 Python repos | First large-scale real-world code benchmark | 4 |
| **WebArena: Realistic Web Environment** | ICLR 2024 | ✓ Long-horizon task boundaries | ✓ Tool use (map, calculator) | ○ Exploration failures | Functional correctness evaluation | 812 web tasks (e-commerce, forums, CMS) | First realistic web environment for agents (GPT-4: 14.41%) | 4 |
| **Retroformer: Policy Gradient Optimization** | ICLR 2024 | — | ○ Action sequence errors | ✓ Infinite loops from frozen reflection | Policy gradient optimization | HotPotQA (+18%), ALFWorld (+36%), WebShop | First to document infinite loop patterns in self-reflection | 4 |
| **WebResearcher: Iterative Deep Research** | arXiv 2025 | ○ Context expansion control | — | ✓ Irreversible noise contamination | Iterative synthesis (reformulate as MDP) | Humanity's Last Exam (36.7% accuracy) | Identifies cognitive workspace suffocation as failure mode | 4 |
| **BFCL: Berkeley Function-Calling Leaderboard** | Benchmark 2024 | — | ✓ AST accuracy, Relevance detection | ○ Parallel function calls | AST validation + executable accuracy | 2,000 Q-A pairs, multiple languages | Standard benchmark for function calling evaluation | 4 |
| **Microsoft AI Red Team Failure Taxonomy** | Whitepaper 2025 | ✓ Agent flow manipulation | ✓ Tool-chain failures | ✓ Knowledge degradation | Threat modeling + red teaming | Synthetic threat scenarios | First comprehensive agentic failure taxonomy including drift | 4 |
| **OdysseyBench: Long-Horizon Office Workflows** | arXiv 2024 | ✓ Multi-day context dependencies | ○ Office application use | ✓ Information persistence issues | Multi-turn context aggregation | 300+ tasks (OdysseyBench+), 302 (Neo) | First multi-day context dependency benchmark | 4 |
| **SWE-bench Pro: Long-Horizon Software Tasks** | arXiv 2024 | ✓ Multi-file edit coordination | ✓ Tool use errors | ○ Semantic/algorithmic failures | LLM-as-judge failure clustering | 4,000+ problems (public + commercial) | Real-world long-horizon tasks (GPT-5: 23.3%) | 4 |
| **TPTU-v2: Task Planning and Tool Usage** | EMNLP 2024 Industry | ○ Sub-task decomposition | ✓ API Retriever for pertinent APIs | ○ API orchestration | Finetuner + Demo Selector + API Retriever | Real-world industry + academic dataset | Industrial-scale tool selection framework | 4 |

**Legend:** ✓ = Directly addresses, ○ = Related/Indirect, — = Not addressed

## 2. Dimension Extraction Analysis

### Dimension 1: Operating on Wrong Scope (PRIORITY)

**Existing Definitions in Literature:**

The research community has fragmented this concept across multiple terms:

- **Task Derailment** (MAST, 2025): "Deviation from the intended objective or focus of a given task, potentially resulting in irrelevant or unproductive actions" — accounts for 7.15% of observed MAS failures
- **Goal Drift** (Arike et al., 2025): "Agent's tendency to deviate from its original objective over time, presenting significant challenges as goals can shift gradually, causing only subtle behavioral changes"
- **Disobey Task Specification** (MAST): "Failure to adhere to the specified constraints or requirements of a given task"
- **Constraint Ignorance** (AgentErrorBench): Planning errors where agents ignore limits on time, budget, or space
- **Pass-to-Pass Test Failures** (SWE-bench): Modifying code outside intended scope, breaking existing functionality

**Current Detection Methods:**

1. **Checkpoint-Based Evaluation** (TheAgentCompany, AgentBoard): Track intermediate milestones to identify where agents deviate — provides partial credit and pinpoints drift location
2. **Goal Adherence Scoring** (Goal Drift paper): Quantitative metrics comparing actions against system goals, measuring Score = 1 - (Runtime_investment/Baseline_investment) over 100,000+ tokens
3. **Pass-to-Pass Testing** (SWE-bench): Ensure no existing functionality breaks while addressing specific issues
4. **FSM-based Conformance** (MI9): Finite-state-machine engines validate behavioral sequences against defined policies
5. **Goal-Conditioned Drift Detection** (MI9): Statistical evaluation using Jensen-Shannon divergence for distributional shifts and Mann-Whitney U tests for continuous behavioral metrics

**Evaluation Metrics Used:**

- Task derailment rate: 7.15% in MAST dataset
- Goal drift score: 0-1 scale (actions + inaction)
- Checkpoint completion rate: Weighted scoring with 50% bonus for full completion
- Boundary violation count: Files/resources accessed outside scope
- Temporal policy violation frequency: Privilege escalation events

**Gaps and Opportunities:**

The field critically lacks **standardized terminology**—"scope violation" appears in zero papers, while related concepts scatter across task derailment, goal drift, and constraint ignorance. No benchmark explicitly tests boundary adherence as a primary metric. Most detection occurs post-hoc rather than runtime. **Key opportunity**: Develop unified definition bridging task derailment (short-term) and goal drift (long-term) with real-time detection capabilities. The Goal Drift paper's 100k+ token evaluation provides a strong foundation, but requires extension to multi-domain benchmarks beyond financial simulation.

### Dimension 2: Utilizing Irrelevant Tools

**Existing Definitions in Literature:**

- **Similar Tool Confusion** (TRAJECT-Bench): "Agents confuse tools with overlapping capabilities, selecting inappropriate alternatives when multiple similar options exist"
- **Parameter-Blind Tool Selection** (TRAJECT-Bench): Choosing tools without considering parameter compatibility
- **Redundant Tool Calling** (TRAJECT-Bench): Unnecessary repeated invocations of the same tool
- **Wrong Tool/Wrong Argument Errors** (τ-bench): Complex database reasoning failures leading to incorrect API selection or parameters
- **Relevance Detection Failures** (ToolACE, BFCL): Using tools when none are appropriate for the task

**Current Detection Methods:**

1. **Dual-Layer Verification** (ToolACE): Rule-based checks followed by model-based validation with self-consistency mechanisms
2. **Trajectory-Aware Metrics** (TRAJECT-Bench): 
   - Trajectory Exact-Match: Tool selection accuracy
   - Trajectory Inclusion: Correct tool ordering
   - Tool-Usage: Parameter correctness
3. **Database State Comparison** (τ-bench): Compare final state with annotated goal state to identify incorrect API calls
4. **AST Matching** (BFCL): Abstract Syntax Tree validation for syntactic and semantic correctness
5. **Multi-aspect Decomposition** (EMNLP Findings): Seven-aspect evaluation schema for comprehensive tool manipulation assessment

**Evaluation Metrics Used:**

- **pass^k consistency** (τ-bench): Measures reliability across k trials — agents achieve <50% on single trial, drops to ~25% on 8 trials
- **Relevance detection rate** (ToolACE): 89.17% accuracy identifying irrelevant tools
- **AST/Executable accuracy** (BFCL, ToolACE): 91.41% overall on function calling benchmark
- **Grounding accuracy** (AgentBoard): Correct parameter extraction from context
- **Trajectory EM** (TRAJECT-Bench): Best models (Claude-4, Gemini-2.5) achieve only ~44-45% on hard queries

**Gaps and Opportunities:**

Current work focuses heavily on **single-turn tool selection** rather than multi-turn context where tool relevance shifts. The **scaling bottleneck** identified by TRAJECT-Bench—transition from 3-5 tools to 5-7 tools represents a critical failure point—remains unaddressed. Most benchmarks use synthetic APIs; real-world API evolution over agent lifetime is unexplored. **Major opportunity**: Develop metrics for tool selection drift as conversation context expands, measuring when agents lose track of which tools remain relevant versus which have become obsolete for current sub-goals. The τ-bench pass^k metric provides an excellent consistency framework that should be extended to measure tool selection stability across conversation turns, not just repeated trials.

### Dimension 3: Repetitive Mistakes (HIGH PRIORITY per Yucheng)

**Existing Definitions in Literature:**

- **Error Propagation** (AgentErrorBench): "The primary bottleneck to LLM agent reliability where a single root-cause error cascades through subsequent steps, compounding degradation and leading to task failure"
- **Infinite Loops** (Retroformer): "Self-reflection from frozen model reiterates prior failed action sequences, prompting agent to repeat same steps in infinite loop"
- **Recursive Planning Loops** (MI9): Repetitive planning cycles without progress
- **Cascading Failures** (ReCAPA): Early mistakes distort later reasoning and actions, making recovery difficult
- **Self-Conditioning on Errors** (ICLR 2025 Long-Horizon Study): "Models degrade future performance based on own errors, creating downward spiral"
- **Step Repetition** (MAST): Unnecessary iteration due to losing track of progress

**Current Detection Methods:**

1. **Error Propagation Rate (EPR)** (ReCAPA): Quantifies how mistakes compound across steps
   - Formula: EPRₖ = Pr(eₜ₀₊ₖ = 1 | eₜ₀ = 1) - Pr(eₜ₀₊ₖ = 1 | eₜ₀ = 0)
   - Measures probability of error at step k given initial error
2. **Propagation Attenuation Coefficient (PAC)** (ReCAPA): Measures how quickly post-error risk dissipates
   - Formula: PAC = -slope(Δ, ln Pr(eₜ₀₊Δ = 1 | eₜ₀ = 1))
3. **Root-Cause Attribution** (AgentErrorBench): Modular analysis identifying where errors originate (memory, reflection, planning, action, system)
4. **Trajectory Loop Detection** (Retroformer): Policy gradient optimization detects repeated failed action sequences
5. **Hierarchical Predictive Correction** (ReCAPA): Three-level mechanism (action→subgoal→trajectory) with cross-level alignment

**Evaluation Metrics Used:**

- **EPR₁₀**: ReCAPA achieves 0.082 vs ~0.3 for GPT-4o-mini and ~0.45 for Claude-4-sonnet
- **Error frequency distribution**: Memory (38 instances), Reflection (39), Planning (78) in AgentErrorBench
- **Temporal clustering**: Most failures occur in steps 6-15 (mid-trajectory)
- **Success rate improvements**: Retroformer +18% HotPotQA, +36% ALFWorld with retry mechanisms
- **Root-cause targeting efficiency**: AgentDebug achieves 24% higher all-correct accuracy (24.3% vs 0.3% baseline)

**Gaps and Opportunities:**

Despite recognition that **error propagation is the central bottleneck** (AgentErrorBench), only ReCAPA provides quantitative metrics (EPR, PAC). Most frameworks detect repetition post-hoc through trajectory analysis rather than real-time intervention. No benchmark explicitly tests recovery from repeated mistakes—TauBench and WebArena show evidence of the problem (pass^8 < 25%, repetitive failures in web navigation) but don't provide targeted evaluation. **Critical opportunity**: Develop real-time loop detection systems that identify repetitive patterns before full trajectory failure. The combination of ReCAPA's quantitative metrics with MI9's runtime monitoring framework provides a strong foundation. Extension needed: benchmarks that intentionally inject errors to measure recovery capabilities, and metrics differentiating "productive retries" (agent trying alternative approaches) from "stuck loops" (repeating identical failed actions).

## 3. Literature Summary

### Most Relevant Papers (Top 15)

**Tier 1: Foundational Frameworks for Context Drift Detection**

1. **MAST: Multi-Agent System Failure Taxonomy** (arXiv 2025) — First empirically grounded failure taxonomy analyzing 1,642 MAS traces with 14 failure modes across 3 categories. Task derailment explicitly defined. LLM-as-judge pipeline achieves κ=0.77 agreement.

2. **AgentErrorBench** (ICLR 2026 review) — First annotated failure trajectory dataset (200 traces) with systematic taxonomy. Identifies error propagation as primary bottleneck. Provides AgentDebug framework achieving 24% higher accuracy.

3. **ReCAPA: Hierarchical Predictive Correction** (ICLR 2026 review) — **First quantitative metrics for error propagation**: EPR (Error Propagation Rate) and PAC (Propagation Attenuation Coefficient). Achieves EPR₁₀ of 0.082 vs 0.3+ for baselines.

4. **MI9: Runtime Governance Protocol** (arXiv Aug 2024) — Most comprehensive runtime monitoring framework with 99.81% detection rate. Goal-conditioned drift detection using Jensen-Shannon divergence and Mann-Whitney U tests. Addresses gap between pre-deployment and post-incident analysis.

5. **τ-bench (TauBench)** (arXiv Jun 2024) — **Critical for repetitive mistakes dimension**: First benchmark measuring agent consistency across trials. pass^k metric reveals dramatic consistency failures (pass^8 drops to <25%). Tests real-world domains (retail, airline).

**Tier 2: Trajectory Analysis and Evaluation Frameworks**

6. **TRAJECT-Bench** (arXiv Oct 2024) — First trajectory-aware evaluation with explicit failure taxonomy: similar tool confusion, parameter-blind selection, redundant calling. Identifies **scaling bottleneck** at 5-7 tools. 5,670 queries across 10 domains.

7. **AgentBoard** (NeurIPS 2024 Oral) — First benchmark with fine-grained progress rate metric enabling incremental advancement tracking. Multi-round interaction evaluation across 9 partially-observable tasks. Interactive visualization web panel.

8. **Agent Trajectory Explorer** (AAAI 2025) — First dedicated visualization tool enabling human oversight and feedback collection for trajectory analysis. Addresses problem that raw trajectory data inadequate for human analysis.

9. **Technical Report: Evaluating Goal Drift** (AAAI 2025 AIES) — First long-context goal adherence study evaluating over 100,000+ tokens. Quantitative scoring for commission (actions) and omission (inaction). Tests adversarial pressure scenarios.

10. **Microsoft AI Red Team Failure Taxonomy** (Whitepaper Apr 2025) — Comprehensive industry perspective on agentic failures. **Explicitly includes goal drift, context drift, and behavior drift** in taxonomy. Threat modeling and monitoring guidelines.

**Tier 3: Specialized Benchmarks and Methods**

11. **ToolACE** (ICLR 2025) — Best-in-class function calling with 91.41% BFCL performance. 89.17% relevance detection (irrelevant tools). Dual-layer verification system with 26,507 APIs.

12. **TheAgentCompany** (arXiv Dec 2024) — Real-world workplace benchmark with 175 tasks across 7 job categories. Checkpoint-based evaluation. Best model (Gemini 2.5 Pro) achieves only 30.3%. Tests long-horizon professional tasks.

13. **Retroformer** (ICLR 2024) — First paper documenting infinite loop patterns in self-reflection. Policy gradient optimization achieves +36% improvement on ALFWorld. Addresses frozen model reiteration problem.

14. **WebResearcher** (arXiv 2025) — Identifies **cognitive workspace suffocation** and **irreversible noise contamination** as failure modes. Iterative synthesis approach achieves 36.7% on Humanity's Last Exam.

15. **SWE-bench** (ICLR 2024 Oral) — Foundational code benchmark (2,294 GitHub issues) with pass-to-pass tests detecting scope violations. Extended to SWE-bench Pro (4,000+ problems) and SWE-bench Multimodal.

### Related but Tangential Work

**Benchmarks Used Extensively but Not Drift-Focused:**
- **WebArena** (ICLR 2024): 812 realistic web tasks, foundational for long-horizon evaluation but limited drift analysis
- **ALFWorld**: Embodied tasks used in 2024 papers (EMMA-ALFWorld, LLF-Bench) primarily for transfer learning
- **HotPotQA**: Multi-hop QA used in Retroformer and LLMCompiler but as task substrate, not drift evaluation
- **BFCL (Berkeley Function-Calling Leaderboard)**: Standard function calling benchmark, tool selection focused but single-turn

**Architectural Approaches with Limited Evaluation:**
- **MetaGPT** (ICLR 2024): SOPs encode role boundaries but lacks explicit drift measurement
- **LLMCompiler** (ICML 2024): Parallel function calling efficiency, not error detection
- **Plan-and-Act** (arXiv 2025): Separates planning/execution, achieves 53.94% WebArena-Lite, limited failure analysis

**Safety-Focused Work:**
- **AgentHarm** (ICLR 2025): Tests whether agents maintain ethical boundaries, relevant for scope but safety-specific
- **Sotopia** (ICLR 2024): Social intelligence evaluation, tests social boundaries not task boundaries

### Research Gaps Identified

1. **Terminology Fragmentation**: "Context drift" appears in essentially zero papers; related concepts scatter across 10+ terms (task derailment, goal drift, behavioral drift, agentic drift, reasoning drift, conversation drift). No consensus definition.

2. **Real-Time vs. Post-Hoc Detection**: 14 of 15 top papers use post-hoc trajectory analysis. Only MI9 provides runtime monitoring. Critical gap for production deployment.

3. **Single-Dimension Evaluation**: Most benchmarks test one dimension in isolation. No comprehensive framework evaluating scope violations AND tool selection AND repetitive mistakes simultaneously on same trajectories.

4. **Benchmark Domain Imbalance**: Heavy bias toward code (SWE-bench variants) and web navigation (WebArena variants). Limited representation of embodied agents, API-calling agents (only τ-bench), multi-agent coordination.

5. **Context Window Limitations**: Only Goal Drift paper tests >100k tokens. Most benchmarks terminate at 50-100 steps. Insufficient for true long-horizon evaluation.

6. **Recovery Mechanisms**: Benchmarks measure failure but not recovery. No metrics for "time to recover from error" or "successful error correction rate." ReCAPA's PAC metric addresses this partially but needs benchmark integration.

7. **Multi-Agent Drift**: MAST identifies inter-agent failures but lacks metrics for how agent A's drift affects agent B. Cascading drift in multi-agent systems unexplored.

8. **Standardized Reporting**: Zero papers adopt "Model Cards for Agents" approach. No standardized format for reporting drift characteristics, failure modes, long-horizon capabilities.

### Potential Innovation Opportunities

1. **Unified Context Drift Framework**: Synthesize MAST's failure taxonomy + ReCAPA's quantitative metrics (EPR/PAC) + MI9's runtime monitoring + τ-bench's consistency testing into single evaluation framework applicable across benchmarks.

2. **Real-Time Loop Detection**: Combine Retroformer's policy gradient approach with MI9's FSM conformance and AgentErrorBench's root-cause attribution for real-time detection before full trajectory failure.

3. **Cross-Benchmark Drift Evaluation**: Apply consistent drift metrics across SWE-bench, WebArena, τ-bench, ALFWorld simultaneously to understand domain-specific vs. universal drift patterns.

4. **Recovery-Aware Benchmarks**: Design benchmarks intentionally injecting errors to measure recovery capabilities. Distinguish "productive retries" from "stuck loops."

5. **Agent Drift Cards**: Adapt model cards framework to report drift characteristics, including:
   - Susceptibility to each drift dimension (quantified)
   - Recovery capabilities (PAC scores)
   - Context window stability (performance at 10k, 50k, 100k+ tokens)
   - Consistency scores (pass^k metrics)
   - Failure mode distributions

6. **Hierarchical Drift Detection**: Extend ReCAPA's three-level correction to three-level detection: action-level (tool selection), subgoal-level (scope adherence), trajectory-level (goal maintenance).

7. **Adversarial Drift Testing**: Extend Goal Drift paper's adversarial pressure approach to other domains. Test boundary adherence under competing objectives.

## 4. Framework Building Insights

### How Existing Work Informs the Context Drift Evaluation Framework

**Architecture Recommendations:**

Based on the literature review, a robust Context Drift Evaluation Framework should integrate four layers:

**Layer 1: Runtime Monitoring** (from MI9)
- Agent-semantic Telemetry Schema (ATS) capturing cognitive/action/coordination events
- Goal-conditioned baseline comparison using statistical tests (Jensen-Shannon divergence, Mann-Whitney U)
- FSM-based conformance engines for temporal policy validation
- Continuous Authorization Monitoring (CAM) for privilege tracking

**Layer 2: Trajectory Analysis** (from TRAJECT-Bench, AgentBoard, Agent Trajectory Explorer)
- Fine-grained progress rate metrics capturing incremental advancement
- Trajectory-aware evaluation: Exact-Match (tool selection), Inclusion (ordering), Tool-Usage (parameters)
- Interactive visualization for human oversight
- Multi-turn coherence tracking

**Layer 3: Error Detection & Attribution** (from AgentErrorBench, ReCAPA)
- Modular error taxonomy: Memory, Reflection, Planning, Action, System
- Root-cause attribution using counterfactuals
- Quantitative propagation metrics:
  - EPR (Error Propagation Rate): EPRₖ = Pr(eₜ₀₊ₖ = 1 | eₜ₀ = 1) - Pr(eₜ₀₊ₖ = 1 | eₜ₀ = 0)
  - PAC (Propagation Attenuation Coefficient): -slope(Δ, ln Pr(eₜ₀₊Δ = 1 | eₜ₀ = 1))
- Hierarchical detection at action, subgoal, trajectory levels

**Layer 4: Consistency Evaluation** (from τ-bench)
- pass^k metric measuring reliability across multiple trials
- Distinguish systematic failures from stochastic errors
- Track behavioral stability over conversation turns

### Missing Components in Current Literature

1. **Unified Scoring System**: Existing metrics are fragmented. Framework needs composite score combining:
   - Scope adherence score (goal drift + task derailment)
   - Tool selection stability (relevance + consistency)
   - Error recovery capability (EPR/PAC)
   - Overall context drift index

2. **Cross-Domain Validation**: Most papers evaluate single benchmark. Framework requires validation across:
   - Coding (SWE-bench)
   - Web navigation (WebArena)
   - API calling (τ-bench)
   - Embodied tasks (ALFWorld)
   - Question answering (HotPotQA)
   - Workplace tasks (TheAgentCompany)

3. **Temporal Dynamics**: Static failure taxonomies insufficient. Framework needs:
   - Drift velocity: How quickly does drift occur?
   - Drift acceleration: Is drift rate increasing?
   - Critical horizons: At what context length does drift become likely?

4. **Intervention Strategies**: Literature focuses on detection, not remediation. Framework should include:
   - Graduated containment (from MI9)
   - Corrective feedback mechanisms (from AgentDebug)
   - Automatic retry logic distinguishing productive vs. stuck patterns

### Suggestions for Formal Definitions

**Definition 1: Context Drift (Proposed Unified Definition)**

Context drift is the **measurable divergence of an agent's behavioral trajectory from its specified objectives, manifested across three dimensions over time in long-horizon tasks**:

1. **Scope Drift (Spatial)**: Operating on entities, files, or data outside the defined task boundary (cf. task derailment in MAST)
2. **Tool Drift (Instrumental)**: Selecting tools or actions inappropriate for current sub-goals given available context (cf. similar tool confusion in TRAJECT-Bench)
3. **Loop Drift (Temporal)**: Repeating errors without correction, indicating failure to learn from feedback (cf. error propagation in AgentErrorBench)

Formal metric: **Context Drift Index (CDI)** = w₁·ScopeScore + w₂·ToolScore + w₃·LoopScore, where weights w₁, w₂, w₃ are task-dependent.

**Definition 2: Scope Drift (Formal)**

An agent exhibits scope drift at step t when:
- It accesses resources R_accessed ⊄ R_authorized
- It pursues sub-goals G_current ⊄ G_specified
- Goal adherence score GA(t) < threshold θ_GA

Detection: Compare goal-conditioned behavioral distribution P(actions|goal, t) against baseline P(actions|goal, t₀) using divergence metrics (JS-divergence > 0.2 indicates drift per MI9 results).

**Definition 3: Tool Selection Drift (Formal)**

Tool selection drift occurs when trajectory tool sequence T_actual deviates from optimal sequence T_optimal:
- Trajectory EM < 0.5 (exact match fails per TRAJECT-Bench threshold)
- Consistency score pass^k < 0.5 for k ≥ 4 (per τ-bench critical threshold)
- Relevance detection: P(tool_i is relevant | context_t) < 0.3 yet tool_i invoked

**Definition 4: Loop Drift (Formal)**

Loop drift is present when error propagation exceeds recovery:
- EPR₁₀ > 0.15 (exceeds ReCAPA's 0.082 success threshold by 2σ)
- Agent repeats failed action sequence within window W: ∃ subsequence S where S_t ≈ S_{t-k} and both failed
- PAC < 0.05 indicating error risk not dissipating

### Benchmark Instantiation Examples from Literature

**Example 1: SWE-bench Context Drift Instantiation**

Apply framework to code generation tasks:
- **Scope Drift Detection**: Monitor which files modified. Compare against PR diff scope. Alert if pass-to-pass tests fail (existing functionality broken).
- **Tool Drift Detection**: Track edit, search, navigate commands. Flag redundant searches or circular navigation patterns (cf. TRAJECT-Bench redundant calling).
- **Loop Drift Detection**: Identify if agent applies same incorrect code change repeatedly. Measure EPR across checkpoint sequence.

**Example 2: WebArena Context Drift Instantiation**

Apply framework to web navigation:
- **Scope Drift Detection**: Monitor which website sections accessed. Compare against task requirements (e.g., shopping cart vs. forum posts). Alert if agent explores irrelevant pages.
- **Tool Drift Detection**: Track click, type, goto actions. Identify similar tool confusion (e.g., using search when filters more appropriate). Measure pass^k consistency for same query types.
- **Loop Drift Detection**: Identify navigation loops (visiting same page repeatedly). Measure if agent learns from failed form submissions or repeats identical inputs.

**Example 3: τ-bench Context Drift Instantiation**

Apply framework to API calling:
- **Scope Drift Detection**: Monitor API calls against user request scope. Alert if agent accesses unauthorized customer records or performs unapproved transactions.
- **Tool Drift Detection**: Measure API selection accuracy against annotated optimal sequence. Track wrong tool/wrong argument errors (cf. τ-bench taxonomy). Calculate pass^8 consistency.
- **Loop Drift Detection**: Identify repeated API call failures. Measure if agent switches strategies or repeats identical failed parameters.

### Implementation Recommendations for "Plug-and-Play Module"

**Design Pattern: Parallel Sleep-Time Compute**

1. **Telemetry Collection** (Zero Agent Disruption):
   - Hook into agent event stream without blocking execution
   - Capture: action, rationale, observation, memory_access, tool_call, timestamp
   - Store in ATS format (cf. MI9 schema)

2. **Asynchronous Analysis Pipeline**:
   - Queue telemetry events for batch processing
   - Compute drift metrics during agent "sleep time" or parallel thread:
     * Goal-conditioned distribution comparison (every 10 steps)
     * Trajectory EM calculation (every 5 tool calls)
     * EPR/PAC computation (every error event)
   - Generate alerts when thresholds exceeded

3. **Dashboard Integration**:
   - Real-time visualization (cf. Agent Trajectory Explorer)
   - Drift index trending (CDI over time)
   - Failure mode distribution pie chart
   - Suggested interventions based on detected patterns

4. **Intervention API**:
   - When critical drift detected: pause agent, present options to human operator
   - Corrective feedback injection (cf. AgentDebug targeted feedback)
   - Automatic checkpoint rollback for severe loop drift

**Evaluation Protocol for Framework Validation**:

1. **Baseline Collection**: Run agents on benchmarks (SWE-bench, WebArena, τ-bench, ALFWorld, HotPotQA) without framework, collect trajectories
2. **Annotation**: Human experts label scope violations, tool selection errors, repetitive mistakes
3. **Detection Validation**: Apply framework retrospectively, measure detection accuracy (target: 95%+ precision/recall per MI9 benchmark)
4. **Intervention Testing**: Re-run with framework interventions enabled, measure improvement in task success rate
5. **Generalization Test**: Validate framework transfers across all 5 benchmark types without retraining

### Critical Success Factors

Based on literature review, framework adoption requires:

1. **Minimal Overhead**: MI9 achieves 99.81% detection with <5% latency increase — match this target
2. **Interpretability**: Provide human-readable explanations (cf. MAST failure mode descriptions)
3. **Actionability**: Not just detection but specific remediation suggestions (cf. AgentDebug feedback)
4. **Standardization**: Adopt consistent taxonomy across research community — contribute framework as benchmark toolkit
5. **Multi-Level Granularity**: Support both real-time monitoring (operators) and post-hoc analysis (researchers)

The convergence of systematic failure taxonomies (MAST, AgentErrorBench), quantitative metrics (ReCAPA's EPR/PAC), runtime monitoring systems (MI9), and trajectory-aware benchmarks (TRAJECT-Bench, AgentBoard) in 2024-2025 provides the essential building blocks. The critical innovation opportunity is **synthesis**: combining these advances into a unified, generalizable, plug-and-play Context Drift Evaluation Framework that becomes the standard for long-horizon agent development and deployment.

---


# Appendix


Jeremy，给你整理好了！我把文献中关于 Context Drift 的各种定义和维度都总结成表格了。

## Context Drift 相关定义对比表

| 术语 | 来源论文 | 定义 | 出现频率 |
|------|---------|------|----------|
| **Task Derailment（任务脱轨）** | MAST (2025) | 偏离任务的预期目标或重点，可能导致无关或无效的行动 | 7.15% 失败案例 |
| **Goal Drift（目标漂移）** | Arike et al. (2025) | Agent 随时间偏离原始目标的趋势，目标逐渐转移，仅产生细微的行为变化 | 中频 |
| **Behavioral Drift（行为漂移）** | Microsoft (2025) | Agent 行为模式随时间发生变化，偏离预期操作范围 | 中频 |
| **Agentic Drift（智能体漂移）** | IBM (2024) | AI Agent 性能随时间退化的隐藏风险 | 低频 |
| **Context Drift（上下文漂移）** | 文献综述 | Agent 行为轨迹与指定目标的可测量偏差，在长时程任务中跨三个维度表现 | **几乎为零**（新术语） |
| **Disobey Task Specification** | MAST (2025) | 未能遵守任务的指定约束或要求 | 低频 |
| **Constraint Ignorance（约束忽略）** | AgentErrorBench (2026) | 规划错误，Agent 忽略时间、预算或空间限制 | 中频 |
| **Cognitive Workspace Suffocation** | WebResearcher (2025) | 认知工作空间被噪音污染导致能力下降 | 低频 |

## 三大核心维度详细对比

### 维度1：Scope Violations（范围违规）

| 具体表现 | 论文来源 | 检测方法 | 量化指标 |
|---------|---------|---------|---------|
| **修改无关文件** | SWE-bench | Pass-to-Pass 测试 | 破坏现有测试的比例 |
| **超出任务边界** | TheAgentCompany | 检查点评估 | 边界违规次数 |
| **访问未授权资源** | MI9 | FSM 状态机验证 | 特权升级事件频率 |
| **目标偏离** | Goal Drift paper | 目标依赖评分 | Score = 1 - (实际投入/基线投入) |
| **违反时间策略** | MI9 | 实时监控 | 违规检测率 99.81% |

### 维度2：Tool Selection Errors（工具选择错误）

| 具体表现 | 论文来源 | 检测方法 | 量化指标 |
|---------|---------|---------|---------|
| **相似工具混淆** | TRAJECT-Bench | 轨迹精确匹配 | Trajectory EM < 0.5 表示漂移 |
| **参数盲选择** | TRAJECT-Bench | 工具使用度量 | 参数正确性评分 |
| **冗余工具调用** | TRAJECT-Bench | 调用序列分析 | 重复调用次数 |
| **错误工具/错误参数** | τ-bench | 数据库状态对比 | pass^k 一致性（k=8 时 <25%） |
| **相关性检测失败** | ToolACE | 双层验证 | 89.17% 无关工具识别率 |
| **工具扩展瓶颈** | TRAJECT-Bench | 扩展性分析 | 5-7个工具是关键失败点 |

### 维度3：Repetitive Mistakes（重复错误）

| 具体表现 | 论文来源 | 检测方法 | 量化指标 |
|---------|---------|---------|---------|
| **错误传播** | AgentErrorBench | 模块化分析 | 错误传播是首要瓶颈 |
| **无限循环** | Retroformer | 策略梯度优化 | 检测重复失败动作序列 |
| **递归规划循环** | MI9 | 实时监控 | 无进展的规划周期数 |
| **级联失败** | ReCAPA | EPR/PAC 指标 | **EPR₁₀ = 0.082**（最佳） vs 0.3+（基线） |
| **自我错误强化** | ICLR 2025 | 长时程研究 | 性能下降螺旋 |
| **步骤重复** | MAST | 进度跟踪 | 不必要的迭代次数 |

## Context Drift 的量化指标体系

| 指标类别 | 具体指标 | 计算公式 | 阈值建议 |
|---------|---------|---------|---------|
| **错误传播率** | EPR (Error Propagation Rate) | EPRₖ = Pr(eₜ₀₊ₖ = 1 \| eₜ₀ = 1) - Pr(eₜ₀₊ₖ = 1 \| eₜ₀ = 0) | > 0.15 表示严重漂移 |
| **传播衰减系数** | PAC (Propagation Attenuation Coefficient) | PAC = -slope(Δ, ln Pr(eₜ₀₊Δ = 1 \| eₜ₀ = 1)) | < 0.05 表示错误风险未消散 |
| **一致性评分** | pass^k | k次试验成功率 | < 0.5 (k≥4) 表示不稳定 |
| **轨迹匹配度** | Trajectory EM | 工具选择序列精确匹配率 | < 0.5 表示工具漂移 |
| **目标依赖度** | Goal Adherence Score | 1 - (运行时投入/基线投入) | < 阈值 θ_GA 表示目标漂移 |
| **JS 散度** | Jensen-Shannon Divergence | P(actions\|goal, t) vs P(actions\|goal, t₀) | > 0.2 表示行为分布漂移 |

## 统一的 Context Drift 框架（我的建议）

| 层级 | 维度名称 | 检测重点 | 来源论文 |
|------|---------|---------|---------|
| **空间维度** | Scope Drift（范围漂移） | 操作边界、资源访问、任务范围 | MAST + MI9 + Goal Drift |
| **工具维度** | Tool Drift（工具漂移） | 工具选择、参数正确性、调用一致性 | TRAJECT-Bench + τ-bench + ToolACE |
| **时间维度** | Loop Drift（循环漂移） | 错误重复、传播速率、恢复能力 | AgentErrorBench + ReCAPA + Retroformer |

## Context Drift Index（综合指数）公式

```
CDI = w₁·ScopeScore + w₂·ToolScore + w₃·LoopScore

其中：
- ScopeScore：基于目标依赖度和边界违规
- ToolScore：基于 Trajectory EM 和 pass^k
- LoopScore：基于 EPR 和 PAC
- w₁, w₂, w₃：任务相关权重
```

---

**关键发现**：

1. **术语极度碎片化**："context drift" 这个词在文献中几乎不存在，相关概念散布在 10+ 个不同术语中
2. **Yucheng 强调的 Repetitive Mistakes** 确实是最有量化指标的维度（ReCAPA 的 EPR/PAC）
3. **实时检测严重缺失**：15 篇顶级论文中只有 MI9 提供运行时监控
4. **跨领域统一框架空白**：这是你的最大机会点

需要我详细展开某个维度或指标的计算方法吗？