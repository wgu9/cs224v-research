# Context Drift in AI Agent Systems: Literature Review and Detection Framework

## Literature Review and Formal Definition

### Defining Context Drift in Agent Systems

**Context drift** in AI agent systems refers to the progressive degradation of an agent's ability to maintain alignment with its original task objectives and utilize relevant historical information as action trajectory length increases within a single execution session. This phenomenon manifests through four interrelated mechanisms: **goal deviation** (drifting from original objectives), **memory degradation** (losing access to earlier context), **behavioral inconsistency** (changes in tool usage or reasoning patterns), and **error accumulation** (compounding mistakes across sequential actions).

This definition synthesizes emerging research on Goal Drift, Context Rot, and Task Derailment while distinguishing agent-specific degradation from traditional machine learning concept drift. Unlike concept drift (changes in P(Y|X) over time in static models), context drift occurs within single-session, long-horizon tasks (50-100+ actions) where the agent must maintain coherent behavior across an expanding action history.

### Boundary Clarification: What IS vs. IS NOT Context Drift

**Context drift IS:**
- **Repetitive failed actions**: Agent executes the same unsuccessful tool call multiple times without learning (17.14% of failures in MAST study)
- **Memory failures**: Agent re-reads files previously processed or forgets earlier decisions (3.33% incidence)
- **Goal wandering**: Agent pursues actions unrelated to original objective at step 80+ in trajectory (7.15% task derailment rate)
- **Action-thought misalignment**: Agent's reasoning diverges from executed actions over time (13.98% incidence)
- **Context rot**: Decreased ability to recall information from early trajectory as context window fills

**Context drift IS NOT:**
- **Cross-session learning degradation**: Performance changes across multiple different tasks over days/weeks (out of scope)
- **Concept drift**: Statistical distribution shifts in training data over time
- **Single reasoning errors**: One-off mistakes that don't propagate or indicate systematic degradation
- **Intentional strategy changes**: Adaptive behavior in response to new information
- **Environmental changes**: External system failures unrelated to agent state

**Uncertain boundary case - Reasoning quality degradation**: Research shows "overthinking" and "thought-skipping" patterns correlate with failure, and LLM brain rot causes up to 32% reasoning degradation. However, whether gradual shifts from detailed to brief reasoning constitute "drift" depends on whether performance degrades. Recommendation: Include when accompanied by measurable performance decline; exclude when reasoning style changes without accuracy loss.

### Intra-Session vs. Inter-Session Distinction

**Intra-session drift** (FOCUS of this research):
- Occurs within one task execution (one GitHub issue = one session in SWE-bench)
- Trajectory length: 50-100+ actions in single continuous session
- Measured by degradation from action 1 to action N within same task
- Example: Agent successfully edits file at step 5, attempts identical edit at step 45 having forgotten earlier success

**Inter-session drift** (EXCLUDED):
- Performance changes across multiple separate tasks over days/weeks
- Continual learning effects, model updates between sessions
- Distribution shift in task types over time
- Example: Agent performs well on Monday's tasks but poorly on Friday's different task distribution (agent drift framework by Ponnambalam captures this)

Critical distinction: Intra-session drift stems from context window constraints and error propagation within a single trajectory. Inter-session drift involves statistical distribution changes or model degradation over time. This research addresses only intra-session phenomena observable in SWE-bench and WebArena trajectories.

### Comprehensive Related Work Survey

#### Agent Memory and Planning Architectures

**ReAct (Yao et al., 2023, ICLR)** introduced synergized reasoning and acting through interleaved thoughts and actions. The architecture augments action space A to Â = A ∪ L where L represents reasoning traces. Critical finding: 47% of failures stem from reasoning errors including **repetitive action loops** where agents fail to reason about proper next steps. The paper explicitly identifies that "the model repetitively generates the previous thoughts and actions" as a core failure mode. ReAct overcomes some hallucination (0% vs 56% for CoT) through environment grounding but struggles with error propagation across long trajectories.

**Reflexion (Shinn et al., 2023, NeurIPS)** adds self-reflection capabilities with episodic memory bounded to 1-3 recent experiences to prevent context explosion. The architecture includes Actor, Evaluator, Self-Reflection, and Memory components. Achieves 97% on ALFWorld but uses bounded memory buffers specifically to manage context accumulation. Heuristic-based self-evaluation detects repeated actions with same observations, directly addressing drift detection. Limited discussion of 50-100+ step horizons suggests memory management remains challenging at extreme lengths.

**LATS (Zhou et al., 2024, ICML)** integrates Monte Carlo Tree Search with language agents, achieving 92.7% on HumanEval by exploring multiple trajectories before committing. Can recover from errors through backtracking, but tree rollout requires substantial additional compute. Paper notes context accumulation remains an issue despite tree search benefits, as long trajectories still accumulate context across explored paths.

**Agent Workflow Memory (Wang et al., 2024)** enables workflow induction and reuse, improving WebArena performance by 51.1%. The "snowball effect" of building complex workflows on simpler ones demonstrates how successful patterns can combat drift, but quality depends on accurate trajectory evaluation. Addresses efficiency (reducing steps needed) but doesn't explicitly tackle drift in unsuccessful trajectories.

**Memory architectures (2024-2025)** show rapid innovation: **MEM1** achieves 3.5x performance improvement with 3.7x memory reduction through constant-size memory on 16-objective multi-hop QA. **HiAgent** uses hierarchical subgoal-based memory management, doubling success rates while reducing steps by 3.8. **Memory-R1** deploys specialized Memory Manager and Answer agents trained via RL on just 152 examples. **STMA** combines spatial (knowledge graph) and temporal (summarized history) memory with planner-critic mechanisms, significantly outperforming ReAct and Reflexion. Critical insight: All recent architectures recognize context management as bottleneck for long-horizon tasks.

#### LLM Context Window Degradation

**"Lost in the Middle" (Liu et al., 2024, TACL)** established the foundational U-shaped performance curve where LLMs exhibit primacy bias (high performance at context start), recency bias (high at end), and middle degradation (20%+ accuracy loss when critical information appears mid-context). Quantitative results show GPT-3.5-Turbo dropping from 76.8% accuracy (info at position 1) to 53.8% (position 10 of 20) to 63.2% (position 20). The 30-document setting shows worst-case 50.5% vs best-case 73.4%—a 23-point swing. Critical for agents: performance drops **below closed-book baseline** when information is mid-context, meaning agents with long action histories effectively lose access to early decisions.

**Positional bias research** reveals the mechanism: "Found in the Middle" (Hsieh et al., 2024) demonstrates LLMs assign higher attention to beginning/end tokens **regardless of relevance**. Linear model shows attention = α × relevance + β × positional_bias, with 83% of document pairs satisfying positional bias monotonicity. Vicuna-7B improves 54.1% → 63.5% with attention calibration, proving models CAN locate middle information but bias overwhelms the signal. "Know but Don't Tell" (Lu et al., 2024) reveals the encoding-utilization gap: probing shows LLMs accurately encode target position in hidden representations but fail to leverage this in generation, with performance degrading in deeper layers.

**Long-context performance studies** (16K-128K+ tokens) show consistent patterns: GPT-4 Turbo (128K) exhibits recall degradation above 82K tokens with "rather poor" performance at 128K compared to flawless 8K performance. Claude 2/2.1 (100K) performs strongly through 96K but shows noticeable slowdown at 192K. ∞Bench testing reveals GPT-4 achieves 79.7% on word extraction but only 59.0% on QA despite near-perfect needle-in-haystack scores, showing synthetic benchmarks poorly predict production performance. Critical finding: **no consistent position bias pattern** at 100K+ tokens, differing from shorter contexts.

**Mechanisms causing degradation**: (1) **Softmax attention diffusion** spreads attention more thinly as context grows, (2) **Positional encoding failures** where RoPE's base frequency limits distinguishability and ALiBi suffers precision issues at long distances, (3) **Attention sink phenomenon** where initial tokens accumulate disproportionate attention regardless of relevance, (4) **KV cache degradation** where cached key-value pairs lose distinctiveness. Decoder-only models (GPT, LLaMA) show strong recency bias from causal masking, with primacy bias emerging in models 13B+.

**Implications for agent systems**: After 10-20 actions, critical early context (task specifications, initial observations) becomes "lost in the middle" of action history. Recent actions receive over-weighted attention in planning decisions. Multi-hop reasoning requiring distant context shows increased failure rates. Tool definitions at context start suffer attention dilution. The "context rot" phenomenon (Anthropic, 2025) describes this decreased recall ability as context fills.

#### Trajectory Analysis and Error Propagation in Agent Systems

**SWE-bench (Jimenez et al., 2024)** established the gold-standard benchmark with 2,294 real GitHub issues, defining "one session" as one issue resolution attempt. Typical maximum 30 steps with early termination if agents repeat actions 3+ times or generate 3 consecutive invalid actions. Documented failure modes: **54.9% early stopping** on feasible tasks, observation bias (latching onto first related information), action repetition loops, and poor context interpretation. **SWE-bench Pro** (Deng et al., 2025) extends to enterprise-level tasks requiring "hours to days for professional engineers" with GPT-4 achieving only 23.3% Pass@1. Clustered failure modes include **analysis paralysis** (extended reasoning without action), **rogue actions** (deviating from intent), **premature disengagement**, and thought-action misalignment (12/30 failing vs 1/10 successful trajectories for RepairAgent).

**WebArena (Zhou et al., 2024, ICLR)** tests 812 long-horizon web tasks (5-50+ actions) across 4 functional websites. GPT-4 achieves only 14.41% success vs 78.24% human performance. Key failure modes: **observation bias** (agents latch onto first information without verification), failures in observation interpretation (overlook granular details, disregard previous actions), and lack of crucial capabilities (active exploration, failure recovery, long-term reasoning, memory). The benchmark explicitly identifies that "limited performance stems from lack of active exploration and failure recovery to successfully perform complex tasks." Trajectory characteristics show context can exceed model limits, requiring truncation/summarization.

**Trajectory analysis studies** reveal systematic patterns: The "Understanding Software Engineering Agents" paper (2025) analyzed 120 trajectories with 2,822 LLM interactions, finding **thought-action misalignment more prevalent in failing trajectories** (12/30 failing vs 1/10 successful). Token consumption analysis shows unsuccessful debugging uses dramatically more tokens: OpenHands averages 1.2M tokens (median 900K) vs AutoCodeRover's 23K mean (14K median)—a **52x difference**. Behavioral patterns in unsuccessful trajectories include redundant exploration, premature fixes, repeated identical actions without follow-up, and higher misalignment prevalence.

**Error propagation mechanisms**: Single errors early in trajectories propagate through subsequent decisions ("indecisive errors propagate along the path and become fatal"). Context loss through multi-hop information flow, hallucination accumulation without external grounding, and goal drift as original objectives become buried. Microsoft's AI Red Team identifies cascading hallucination attacks that "spread through memory, influence planning, trigger tool calls." Multi-agent systems amplify propagation through inter-agent dependencies creating cascade paths.

**UC Berkeley MAST taxonomy** (Cemri et al., 2025) provides empirically grounded classification across 200+ traces with Cohen's κ=0.88 inter-rater reliability. **14 failure modes** in 3 categories: (FC1) Flawed Setup including **Step Repetition at 17.14%** (highest single mode), Disobey Task Specification (10.98%), Loss of Conversation History (3.33%); (FC2) Inter-Agent Misalignment including Reasoning-Action Mismatch (13.98%), Fail to Ask for Clarification (11.65%), Task Derailment (7.15%); (FC3) Insufficient Verification (21.30% total). Empirical failure rates across systems: ChatDev 67%, MetaGPT 60%, HyperAgent 75%, AppWorld 87%, AG2 41%, Magentic-One 62%. Key insight: system design outweighs prompt engineering, with tactical fixes yielding only 9-15% gains.

**Microsoft AI Red Team taxonomy** (Bryan et al., 2025) identifies **27 failure modes** (6 novel security, 4 novel safety, 10 existing security, 7 existing safety). Novel safety modes include intra-agent RAI issues, harms of allocation, organizational knowledge loss, and prioritization leading to safety issues. Case study shows memory poisoning attacks achieve 40% baseline success, jumping to 80% with better prompting. Mitigation strategies span identity management, memory hardening, control flow control, and environment isolation.

**AgentDiet** (2025) analysis of SWE-bench Verified trajectories identifies typical inefficiencies achieving 39.9% token reduction with minimal performance impact (-0.4% to +2.0% on Pass%). Types of waste include redundant context repetition, unnecessarily long tool outputs, and repeated observations of unchanged state. **Overthinking analysis** shows extended reasoning without action (analysis paralysis) correlates with decreased performance, with mitigation yielding 30% improvement and 43% cost reduction.

**Common patterns across benchmarks**: Poor long-term reasoning (universal), observation bias/premature conclusions, action repetition/loops, tool/parameter selection errors, lack of failure recovery, redundant exploration, context length explosion, and overthinking vs action imbalance. Performance degradation with trajectory length shows steepest drop at 3-5 tool/action transition (TRAJECT-Bench).

### Key Papers Summary Table

| Paper | Citation | Core Contribution | Relevance to Context Drift |
|-------|----------|-------------------|---------------------------|
| ReAct | Yao et al., 2023, ICLR | Synergized reasoning and acting through interleaved thoughts/actions | Identifies repetitive action loops (47% reasoning errors) as core failure mode |
| Reflexion | Shinn et al., 2023, NeurIPS | Self-reflection with bounded episodic memory (1-3 experiences) | Addresses context explosion through memory bounds; detects repeated actions |
| Lost in the Middle | Liu et al., 2024, TACL | U-shaped performance: 20%+ degradation when info mid-context | Explains why agents lose early task specifications in long trajectories |
| Found in the Middle | Hsieh et al., 2024 | Intrinsic positional attention bias regardless of relevance | Reveals mechanism: bias can be calibrated (15-point improvement) |
| SWE-bench | Jimenez et al., 2024 | 2,294 real GitHub issues; one session = one issue | Defines evaluation context; documents 54.9% early stopping, action loops |
| SWE-bench Pro | Deng et al., 2025 | Enterprise tasks requiring hours-days; GPT-4 23.3% success | Identifies analysis paralysis, rogue actions, premature disengagement |
| WebArena | Zhou et al., 2024, ICLR | 812 long-horizon web tasks; 14.41% GPT-4 vs 78.24% human | Observation bias, lack of exploration/recovery capabilities |
| MAST Taxonomy | Cemri et al., 2025, arXiv:2503.13657 | 14 empirically validated failure modes; 41-87% failure rates | Step repetition 17.14% (highest), reasoning-action mismatch 13.98% |
| Microsoft Red Team | Bryan et al., 2025 | 27 failure modes (security + safety); memory poisoning case study | Comprehensive taxonomy with mitigation strategies |
| Agent Workflow Memory | Wang et al., 2024 | Workflow induction/reuse; 51.1% WebArena improvement | Addresses efficiency but not drift in unsuccessful trajectories |

### Supporting Citations

**Memory Systems**: MEM1 (Zhou et al., 2025, arXiv:2506.15841), HiAgent (Hu et al., 2024, arXiv:2408.09559), Memory-R1 (Yan et al., 2025, arXiv:2508.19828), STMA (2025, arXiv:2502.10177)

**Long-Context**: Know but Don't Tell (Lu et al., 2024, arXiv:2406.14673), ∞Bench (Zhang et al., 2024, arXiv:2402.13718), LongBench (Bai et al., 2024, ACL), Context Rot (Anthropic Engineering, 2025)

**Trajectory Analysis**: Understanding SE Agents (arXiv:2506.18824), AgentDiet (arXiv:2509.23586), TRAJECT-Bench (arXiv:2510.04550), Overthinking in Reasoning Models (SWE-bench Verified analysis)

**Failure Modes**: Goal Drift (arXiv:2505.02709), Tool Hallucination (arXiv:2412.04141), LLM Brain Rot (UT Austin, 2024), Agent Drift Framework (Ponnambalam, 2025)

---

## Detection Card Framework Design

### Investigation of Existing Frameworks

**Model Cards (Mitchell et al., 2019, FAT\*)** provide 1-2 page documents with nine structured sections: Model Details, Intended Use, Factors (demographic/phenotypic groups), Metrics, Evaluation Data, Training Data, Quantitative Analyses (unitary and intersectional results), Ethical Considerations, and Caveats. Design principles emphasize **disaggregated evaluation** (inspired by FDA clinical trial mandates), **intersectionality theory** (characteristics interact, not just add), and **transparency through standardization**. Target audiences span ML practitioners, developers, policymakers, organizations, and impacted individuals. Critical insight: Dimensions defined through stakeholder analysis and domain-relevant characteristics, with groups using self-identified labels when possible.

**Datasheets for Datasets (Gebru et al., 2021, CACM)** document dataset lifecycle through seven sections: Motivation, Composition, Collection Process, Preprocessing, Uses, Distribution, and Maintenance. Design emphasizes **stakeholder-centered approach** (creators for reflection, consumers for informed decisions), **flexibility by design** (adapt to domain), and **GDPR alignment**. Questions organized by lifecycle stage to match natural workflow. Particularly relevant for agent research: documentation of interaction logs, tool usage traces, and trajectory data as specialized dataset types.

**System Cards (emerging from Meta, AWS)** extend Model Cards to entire AI systems rather than individual models. Document multiple ML models, AI and non-AI components, system-level behavior vs individual model behavior, and integration effects. **High relevance for agents** as inherently multi-component systems with reasoning models, tool selection, response generation, memory systems, and planning modules. Captures how models work differently in different system contexts.

**FactSheets (IBM)** focus on AI service documentation with automated fact capture at each lifecycle stage. Components include Service Information, Safety and Performance (robustness testing, failure modes), Fairness (bias testing across demographics), Explainability, and Accountability (governance, update history, compliance). IBM Watsonx.governance implementation provides programmatic customization via Python SDK with model inventory tracking and lifecycle status monitoring.

**BenchmarkCards (Sokol et al., 2024)** standardize LLM benchmark documentation through five sections: Benchmark Objectives (what's measured, intended capabilities), Methodology (evaluation approach, scoring, validation), Data Sources (origin, characteristics, biases), Limitations (what's NOT measured, edge cases, saturation risks), and Results Interpretation (score meaning, comparison guidelines). Machine-readable (JSON) and human-readable (Markdown) formats. Design principle: transparency in evaluation to prevent inappropriate application/interpretation.

### Target Audience for Detection Cards

**Primary Users:**

1. **Agent Researchers** (highest priority): Need detailed drift patterns, failure taxonomies, and detection methodologies for benchmarking, comparing approaches, and identifying research gaps. Require technical depth, quantitative metrics, and replicable detection methods.

2. **ML Engineers/Practitioners**: Need actionable insights for production deployment—when to expect drift, which monitoring metrics matter, and intervention thresholds. Require practical detection approaches, cost-efficiency considerations, and integration guidance.

3. **Agent System Developers**: Need architectural guidance for drift-resistant design—memory management strategies, error recovery mechanisms, and failure prevention. Require component-level specifications and design patterns.

**Secondary Users:**

4. **Benchmark Creators**: Need standardized drift evaluation dimensions, test case design, and trajectory annotation guidelines.

5. **Safety/Evaluation Teams**: Need risk assessment frameworks, failure mode severity ratings, and validation protocols.

**Design Rationale**: Following Model Cards' multi-stakeholder approach, Detection Cards should provide layered detail—executive summaries for quick assessment, technical methodology sections for implementation, and empirical results sections for research comparison. Prioritize researchers and practitioners as they directly address drift detection and mitigation.

### Core Detection Dimensions

#### Dimension 1: Goal Adherence Drift

**Formal Definition**: Progressive deviation of agent behavior from original task objectives as measured by semantic similarity between executed actions and initial goal specification over trajectory length. Encompasses **task derailment** (pursuing unrelated objectives) and **scope creep** (expanding beyond specified boundaries).

**Theoretical Justification**: Goal drift research (arXiv:2505.02709) demonstrates agents deviate from instruction-specified goals with GD scores 0.51-0.93 under adversarial pressure. MAST taxonomy identifies task derailment at 7.15% incidence. WebArena failures show observation bias causing agents to latch onto tangential information, leading to goal wandering. The "lost in the middle" phenomenon explains mechanism: original task specifications become buried mid-context, receiving reduced attention as recency bias prioritizes recent observations. Early stopping (54.9% in WebArena) often results from false belief that original goal is unachievable when agent has actually shifted focus.

**Detection Methodology**:

*Offline (post-hoc) measurement*:
1. **Semantic trajectory alignment**: Compute cosine similarity between goal embedding G and action embeddings A_t at each timestep: drift_score(t) = 1 - cos_sim(G, A_t). Threshold: drift when score \> 0.4 for 5+ consecutive steps.
2. **Action-goal relevance scoring**: LLM-as-judge (GPT-4 or o1) rates each action's relevance to original goal on 1-5 scale. Drift when running average drops below 3.0.
3. **Dependency graph analysis**: Map actions to goal prerequisites; detect branches pursuing unreferenced dependencies.
4. **Trajectory clustering**: Cluster successful vs unsuccessful trajectories by action embeddings; detect drift when trajectory leaves successful cluster.

*Metrics*:
- Goal Deviation Score: Average semantic distance from goal over trajectory
- Drift Onset Time: First timestep exceeding threshold
- Drift Severity: Maximum deviation observed
- Recovery Frequency: Number of returns to goal-aligned behavior

**Applicability Scope**:
- **Task types**: Well-defined objectives with explicit specifications (SWE-bench issue resolution, WebArena task completion, coding challenges)
- **Trajectory length**: Most relevant 30+ steps when goal specifications become mid-context
- **Limitations**: Requires clear initial goal statement; less applicable to open-ended exploration or multi-objective tasks
- **Domain**: Software engineering, web navigation, structured problem-solving

#### Dimension 2: Memory Consistency Failure

**Formal Definition**: Agent's inability to maintain and utilize information from earlier trajectory states, manifesting as redundant information gathering, contradictory decisions, or failure to reference established context. Encompasses **information re-retrieval** (re-reading files, re-executing queries), **decision contradiction** (actions contradicting earlier conclusions), and **context forgetting** (losing track of established facts).

**Theoretical Justification**: MAST taxonomy documents Loss of Conversation History at 3.33% incidence with "unexpected context truncation, reverting to antecedent state." Agent trajectory analysis shows redundant exploration in unsuccessful trajectories with agents repeating information-gathering actions despite having already obtained the information. "Lost in the middle" research demonstrates 20%+ performance degradation when information appears mid-context, explaining why agents fail to recall early observations. Context rot (Anthropic, 2025) describes decreased recall ability as context fills. Reflexion architecture uses bounded memory (1-3 experiences) specifically because unbounded memory leads to information loss through context dilution.

**Detection Methodology**:

*Offline measurement*:
1. **Redundant observation detection**: Track (observation_content, timestep) pairs; flag when agent requests observation semantically identical (cosine similarity \> 0.85) to earlier observation.
2. **Information retrieval pattern analysis**: Build knowledge graph of facts acquired over trajectory; detect queries for information already in graph.
3. **Decision consistency checking**: Extract agent decisions/conclusions at each step; identify contradictory statements using LLM-based consistency verification.
4. **Reference analysis**: For each action, check if agent references relevant earlier context; compute reference frequency over time (should remain stable).

*Metrics*:
- Redundancy Rate: Percentage of actions repeating earlier information gathering
- Context Utilization Score: Ratio of relevant earlier context referenced in each action
- Memory Decay Curve: Context utilization vs trajectory position (should be flat; decay indicates forgetting)
- Contradiction Frequency: Number of contradictory decision pairs per 10 actions

**Applicability Scope**:
- **Task types**: Information-intensive tasks requiring integration of multiple observations (multi-file code editing, complex web workflows, research tasks)
- **Trajectory length**: Critical beyond 20 steps when context accumulation begins
- **Limitations**: Requires distinguishing redundant from necessary verification; not applicable when environment state changes between observations
- **Domain**: Code editing, multi-document QA, multi-step web navigation, long-horizon planning

#### Dimension 3: Action Loop Pathology

**Formal Definition**: Repetitive execution of similar or identical actions without progress toward goal, encompassing **exact repetition** (identical action sequences), **semantic loops** (functionally equivalent actions with varied syntax), and **failed tool persistence** (repeated calls to tools that previously failed). Distinguished from legitimate retries by lack of environmental change or parameter adjustment.

**Theoretical Justification**: MAST taxonomy identifies Step Repetition as **highest single failure mode at 17.14%**—greater than any other category. ReAct paper documents agents "repetitively generating previous thoughts and actions" as core reasoning error, categorizing this under failure to reason about proper next steps. Practitioners document extensive loop issues across LangChain (Issues #20501, #18279, #17872), OpenAI community reports, and HuggingFace infinite loops. Root causes: planning logic not incorporating observations, stopping conditions unmet, agent unable to parse own output. SWE-bench terminates agents after 3+ repeated actions or 3 consecutive invalid actions, recognizing loops as irrecoverable failure state. Overthinking research shows analysis paralysis (extended reasoning without action) correlates with failure, and mitigating overthinking yields 30% performance improvement.

**Detection Methodology**:

*Offline measurement*:
1. **N-gram sequence matching**: Extract action n-grams (n=2,3,4); flag sequences appearing 3+ times consecutively or 5+ times total.
2. **Semantic action clustering**: Cluster actions by embedding similarity; detect when agent samples from same cluster repeatedly without state change.
3. **Tool call analysis**: Track (tool, parameters, result) tuples; flag repeated calls with same parameters receiving error results.
4. **State progression tracking**: Measure environment state delta between consecutive actions; loops show zero or negative progress.
5. **Edit distance analysis**: Compute Levenshtein distance between action sequences; low distance with time separation indicates loops.

*Metrics*:
- Loop Incidence Rate: Percentage of trajectories containing loops
- Loop Length: Number of actions in repetitive cycle
- Loop Resolution Time: Steps from loop entry to exit (if resolved)
- Persistence Score: Number of times agent retries failed action without modification

*Real-time detection* (for online systems):
- Maintain sliding window of last K actions (K=5-10)
- Compute pairwise action similarity in window
- Alert when similarity \> 0.85 for 3+ actions
- Trigger intervention (prompt modification, external guidance, forced exploration)

**Applicability Scope**:
- **Task types**: Universal—applies to all agent tasks with sequential actions
- **Trajectory length**: Detectable at any length; most critical 10+ steps when error propagation begins
- **Limitations**: Must distinguish loops from legitimate iteration (test-fix cycles in coding); requires domain knowledge to identify progress
- **Domain**: All agent systems, especially critical for tool-using agents where failed tool calls compound

#### Dimension 4: Tool Usage Degradation

**Formal Definition**: Decline in agent's tool selection accuracy, parameter correctness, or appropriate tool abstention over trajectory length. Encompasses **tool confusion** (selecting related but incorrect tools), **parameter errors** (incorrect argument values), **tool hallucination** (referencing non-existent tools), and **excessive tool calling** (redundant or unnecessary invocations).

**Theoretical Justification**: TRAJECT-Bench identifies similar tool confusion and parameter-blind selection as primary failure modes, with steepest performance drop between 3-5 tools. Tool hallucination research (arXiv:2412.04141) demonstrates models improperly select or misuse tools, with impact "more severe than text-based hallucinations" due to physical world interfaces. InterCode CTF analysis shows similar tool confusion and parameter-blind selection reduce reliability. Reasoning-Action Mismatch (13.98% in MAST) often manifests as selecting tools inconsistent with stated reasoning. As trajectories lengthen, tool definitions at context start receive reduced attention (positional bias), and tool usage patterns across trajectory create noise diluting correct usage signals.

**Detection Methodology**:

*Offline measurement*:
1. **Tool selection accuracy**: Compare selected tool vs optimal tool (ground truth from expert trajectories or LLM judge); track accuracy over trajectory position.
2. **Parameter correctness scoring**: Validate tool parameters against tool schemas; flag incorrect types, missing required fields, invalid values.
3. **Tool necessity analysis**: LLM judge evaluates whether tool call was necessary; compute necessity score over time.
4. **Tool-reasoning alignment**: Compare tool selected vs tool mentioned in reasoning; mismatches indicate degradation.
5. **Tool hallucination detection**: Cross-reference called tools against available tool set; identify non-existent tools.

*Metrics*:
- Tool Selection Accuracy: Percentage correct tool choices over time (should remain stable)
- Parameter Error Rate: Invalid parameter frequency per 10 tool calls
- Hallucination Incidence: Percentage of calls to non-existent tools
- Redundancy Score: Percentage of tool calls providing no new information
- Tool Confusion Matrix: Which tools confused with which (reveals systematic patterns)

**Applicability Scope**:
- **Task types**: Any tool-using agent system with defined tool set (API agents, code execution agents, web agents)
- **Trajectory length**: Relevant at all lengths; degradation typically begins 15-20 steps as tool definitions lose attention
- **Limitations**: Requires ground truth tool set; optimal tool selection may be ambiguous when multiple valid approaches exist
- **Domain**: API interaction, web automation, software development, robotic control, any tool-calling agent

#### Dimension 5: Reasoning Quality Decay

**Formal Definition**: Degradation in agent's reasoning depth, logical coherence, or justification quality over trajectory length. Encompasses **thought-skipping** (omitting reasoning steps), **analysis paralysis** (extended reasoning without action), **logical inconsistency** (contradictory reasoning chains), and **reasoning-action misalignment** (reasoning diverging from executed actions).

**Theoretical Justification**: LLM brain rot research demonstrates up to 32% reasoning degradation from low-quality data exposure, showing reasoning quality degrades under adverse conditions. Overthinking research on SWE-bench Verified identifies analysis paralysis (extended reasoning without environmental interaction) correlating with decreased performance. Trajectory analysis reveals thought-action misalignment more prevalent in failing trajectories (12/30 failing vs 1/10 successful in RepairAgent). Reasoning-Action Mismatch constitutes 13.98% of failures in MAST taxonomy. As context lengthens, reasoning quality may degrade due to attention diffusion across expanded history, cognitive load from accumulated information, or drift in reasoning style from detailed early analysis to brief late-stage responses.

**Theoretical Uncertainty**: Unlike other dimensions, it remains unclear whether reasoning style changes (detailed → brief) without performance degradation constitute "drift" or adaptive efficiency. Recommendation: Include in detection framework when accompanied by measurable performance decline; monitor as potential leading indicator even when performance stable.

**Detection Methodology**:

*Offline measurement*:
1. **Reasoning depth scoring**: Measure reasoning length, number of logical steps, depth of causal chains; track over trajectory.
2. **Logical coherence assessment**: LLM judge (GPT-4) evaluates reasoning chain coherence, assigning scores 1-5; track over time.
3. **Reasoning-action alignment**: Compute semantic similarity between reasoning trace and executed action; declining similarity indicates misalignment.
4. **Thought-skipping detection**: Identify omitted intermediate reasoning steps by comparing reasoning density (steps per action) over time.
5. **Analysis paralysis detection**: Track reasoning-to-action ratio; flag when consecutive reasoning steps exceed threshold (e.g., 5+ thoughts per action).

*Metrics*:
- Reasoning Depth Score: Average logical steps per reasoning trace over time
- Coherence Score: LLM-judged logical consistency (1-5 scale) over trajectory
- Alignment Score: Semantic similarity between reasoning and action (should remain high)
- Thought Density: Reasoning steps per action (should remain stable unless task complexity changes)
- Paralysis Incidence: Percentage of actions preceded by excessive reasoning without intermediate actions

**Applicability Scope**:
- **Task types**: Tasks with explicit reasoning traces (ReAct-style agents, Reflexion agents, chain-of-thought systems)
- **Trajectory length**: Most relevant 20+ steps when reasoning patterns stabilize and deviations become detectable
- **Limitations**: Requires explicit reasoning traces; not applicable to agents without thought verbalization; subjective assessment requires reliable LLM judge
- **Domain**: Problem-solving tasks, coding, mathematical reasoning, planning—anywhere reasoning quality directly impacts outcomes

### Framework Design Rationale

**Multi-dimensional approach**: Five dimensions capture distinct manifestations of drift, following Model Cards' disaggregated evaluation principle. Goal adherence addresses "what" (objective alignment), memory consistency addresses "context" (information retention), action loops address "how" (behavioral patterns), tool usage addresses "implementation" (execution quality), and reasoning quality addresses "why" (decision-making coherence).

**Complementary, not redundant**: Dimensions can co-occur (e.g., goal drift may accompany tool degradation) but measure distinct phenomena. Tool confusion without goal drift indicates localized execution issues; goal drift without loops indicates coherent but misdirected behavior.

**Prioritization by empirical prevalence**: Dimensions ordered by documented failure rates—loops (17.14%), reasoning misalignment (13.98%), task derailment (7.15%), memory loss (3.33%)—ensuring highest-impact issues receive primary attention.

**Offline-first philosophy**: All dimensions specify post-hoc detection methods, aligning with stated Phase 1 priority. Real-time detection noted where feasible (loops) but secondary.

**Intersection with existing frameworks**: Detection dimensions align with MAST taxonomy categories (Specification Issues, Inter-Agent Misalignment, Insufficient Verification) and Microsoft Red Team's agent-specific failure modes, enabling comparison across research and integration with established taxonomies.

**Benchmark-validated**: Detection methods designed for application to SWE-bench and WebArena trajectories specifically—all metrics computable from standard trajectory format (observation, thought, action, result) with tool call information.

### Recommendations for Implementation

**For researchers**: Report all five dimension scores when evaluating agent systems; use Detection Cards to document drift characteristics of new architectures; contribute annotated trajectory datasets with ground-truth drift labels.

**For practitioners**: Implement loop detection first (highest incidence, clear intervention path); add goal adherence monitoring second; use Detection Cards to select appropriate monitoring for use case.

**For benchmark creators**: Include drift dimension annotations in trajectory datasets; provide baseline drift scores for benchmark tasks; standardize reporting formats following Detection Card structure.

**Framework evolution**: Detection Card specification should evolve with research—add dimensions as new failure modes emerge, refine thresholds based on empirical validation, integrate community feedback on detection reliability.