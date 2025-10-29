# Context Drift – 分析打包 (Markdown)

**生成时间：** 2025-10-29 21:38:00

## 文件列表

本压缩包包含以下文件：

- `01_context_drift_framework_cn.md`：面向长时程智能体的 Context Drift（语境/任务漂移）定义、检测与解决的两阶段框架（中文综述）。
- `02_context_drift_dimensions_table_cn.md`：Context Drift 维度与可检测指标对照表（Markdown 表格，中文）。
- `03_notes_scope_tool_loop_cn.md`：工程实施要点（Scope Guard、工具调用监控、循环检测/早停等）。

> **说明：** 这些内容整理自本对话中的分析与总结，供论文写作与系统实现时直接引用或改写。
>
> **主题：** Context Drift Detection and Resolution in Long-Horizon AI Agents

---

## 1. Defining Context Drift in Multi-Turn Agents

Context drift refers to a gradual deviation of an AI agent's behavior or focus away from the user's original intent or task as an interaction progresses. Unlike one-off errors or hallucinations, context drift is a slow erosion of the initial goal or constraints over time. For example, a summarization assistant might gradually lose the requested tone, or an autonomous image editor might drift from the target aesthetic as more edits are applied. In long conversations or extended tasks, an agent can even forget the user's goals and constraints it started with. This phenomenon is distinct from "alignment drift" (which concerns values/policies) – context drift specifically corrupts the relevant task information or intent in the agent's working context. Recent studies have identified context drift (also called task drift or instruction drift in related work) as a critical failure mode for large language model (LLM) based agents. For instance, LLM outputs tend to deviate from earlier context, leading to incoherence or neglect of the original goal in long conversations. Abdelnabi et al. (2024) explicitly showed that LLMs can "lose track" of the task under malicious or irrelevant prompts and proposed methods to catch this drift. Similarly, Mehri et al. (2025) found that even capable user simulators suffer instruction drift, failing to sustain the given user goals consistently over multi-turn dialogues. In summary, context drift is a progressive, temporal misalignment where an agent's actions or responses stray from the original task objectives.

### Why it matters

Left unchecked, context drift can cause an agent to produce incorrect or undesired outcomes despite starting from a correct instruction. It often goes unnoticed by traditional evaluations that only check final success or per-turn quality. Detecting and mitigating context drift is crucial for reliability in long-horizon tasks where we expect the agent to maintain coherence, goal alignment, and scope adherence throughout the task. As agents become more autonomous and are trusted with extended operations (e.g. coding assistants modifying codebases, or autonomous web agents browsing on our behalf), ensuring they stay on track with user intent is vital for safety and performance.

---

## 2. Key Dimensions of Context Drift and Metrics

Researchers are beginning to characterize context drift along multiple dimensions, each capturing a distinct way an agent can "drift" off-course. We outline several proposed dimensions (with example failure modes, how to detect them, and why they matter):

### 2.1 Operating on the Wrong Scope

This is when an agent's actions stray outside the intended scope or subtask. For example, a coding agent told to modify specific files might gradually start editing unrelated files or directories that were supposed to remain untouched. This scope drift violates task constraints and can introduce errors (e.g. editing "forbidden" parts of a codebase).

**Detection:** A simple metric is to track whether the agent's targets (files, modules, sections of a task) remain within an allowed set. Scope-guarding mechanisms can flag if the agent attempts to access or modify out-of-scope items (as noted in some coding agent frameworks).

**Why it matters:** Wrong-scope operations often mean the agent is pursuing an irrelevant subgoal or misunderstanding instructions, leading to wasted effort or harmful changes. In safety-critical settings, scope violations raise serious concerns. By formally defining scope and monitoring the agent's focus, we can catch when it starts operating in the wrong context.

### 2.2 Utilizing Irrelevant or Unnecessary Tools

Tool-using agents sometimes call tools or APIs that are not relevant to the current goal, indicating a drift in strategy. For instance, an agent might invoke a web search tool or an API that has no bearing on the task at hand – a sign that it has lost context or is "thrashing."

**Detection:** We can monitor the sequence of tool calls and compare against an optimal or expected plan. If the agent frequently invokes tools outside its specialization or unrelated to the active subtask, it can be flagged. In practice, capability-based restrictions can be used to prevent such drift – e.g. disallowing an agent from accessing tools outside its role or domain.

**Why it matters:** Using irrelevant tools wastes time and can derail progress. It often correlates with confusion in the agent's policy. By measuring unnecessary tool usage (for example, counting how often the agent calls an API that yields no new information or repeats a useless action), we quantify this drift. Keeping the agent on the minimal relevant toolset helps reinforce task boundaries and avoid spurious actions.

### 2.3 Repetitive Mistakes and Loops

A hallmark of context drift is when an agent falls into a loop of repeating the same error or action without making progress. The agent might cycle over a step (or a set of steps) even after it fails, indicating it hasn't integrated the feedback from failure. This has been observed often in complex interactive settings – e.g. a web navigation agent clicking the same button endlessly or retyping the same query when it can't find an item. In coding or tool-use scenarios, an agent might attempt the same API call over and over despite an error response, effectively "spinning its wheels."

**Detection:** A straightforward metric is loop detection – if the agent repeats an identical (or semantically identical) action X times in a row, or oscillates between a small set of states, a loop warning is triggered. Indeed, practitioners note that "agents easily get stuck in loops, endlessly repeating the same actions", which we can detect by analyzing the action trace for cycles. Another signal is a high number of consecutive failed attempts of the same type. Academic benchmarks have flagged this behavior: for example, in one study a coding agent got a KeyError, tried an alternative approach, but again failed and continued this loop of failures until hitting the retry limit. This pattern – failure without learning – is precisely what we want to catch.

**Why it matters:** Repetitive mistakes indicate the agent is no longer effectively adapting; it's stuck in a local minimum or misinterpretation. Not only does this waste computation and time, it also often means the agent will never reach the goal unless external intervention occurs. In benchmarks like WebArena and TauBench, such looping behavior was a prominent cause of low success rates. By identifying loops early, a supervisor module could intervene (more on resolution later). Reducing this dimension of drift is crucial for efficiency and reliability.

### 2.4 Other Potential Drift Aspects

In our literature survey, a few other drift-related failure patterns emerged, though they are sometimes viewed as consequences of the above dimensions. One is **Neglecting Required Information or Justification**. Over a long task, an agent might start ignoring parts of the user's instructions or failing to justify its decisions, because it has lost some context or is rushing. For example, an analysis agent might provide an answer that only addresses half of the user's question, effectively "ignoring parts of the instructions". This can be seen as a form of drift where the agent's focus narrows improperly. Another example, especially in analytical or QA tasks, is when the agent stops citing evidence it was initially expected to cite – potentially because the earlier context that required justification scrolled out of its working memory.

**Detection:** For instruction neglect, one can compare the final output against the full set of user requirements (e.g., check if all sub-questions are answered or all requested elements are present). For justification lapses, one could track whether the agent's responses include expected evidence (such as citations or tests executed). If an agent's earlier outputs contained evidence or reasoning steps that later outputs lack, that might signal drift in the rigor of its approach.

**Why it matters:** These aspects impact the quality and trustworthiness of the agent's performance. An agent that forgets to follow a constraint (like "explain each step") or omits verification (like not running tests on code when it should) is drifting from the process, even if it hasn't totally gone off-topic. While these dimensions are a bit more task-specific, we include them for completeness – they underscore that context drift can manifest as a decrease in thoroughness or adherence to implicit expectations over time. (We note that these need further study; current benchmarks have not standardized metrics for "justification drift" yet.)

### Metrics for Each Dimension

To evaluate an agent on context drift, we propose defining quantitative metrics per dimension. For instance, "scope violations per 100 actions," "% of tool calls that were irrelevant," "loop duration (in steps) before recovery or stop," and "instruction compliance score" could be reported. Such metrics would complement overall task success rates by diagnosing why an agent might be failing. In fact, a Context Drift evaluation framework could mirror the idea of model cards or diagnostic checklists, enumerating these dimensions and measuring them for any given agent's trajectory.

---

## 3. A Generalized Context Drift Evaluation Framework

To systematically detect and address context drift, we outline a two-stage framework: **Detection** followed by **Resolution**. This framework is meant to be benchmark-agnostic, applying to coding agents, dialogue agents, web agents, etc., with appropriate instantiations. Below we describe each component and how it can plug into different agent scenarios.

### 3.1 Detection of Context Drift

#### How to detect drift?

Modern research suggests combining learned signals from the model's internals with observable behavioral cues in the agent's trajectory. One cutting-edge approach is to monitor the model's activations for signs of drift. Abdelnabi et al. (2024) introduced an activation-based drift detector: by comparing the LLM's hidden representations before vs. after a new piece of input, they could detect if the input caused the model to stray from its prior task. Remarkably, a simple linear probe on the final layer activations was able to catch task drift with near-perfect accuracy (AUC ~1.0) on test data, generalizing well to unseen attack types like prompt injections and jailbreaks. This kind of approach doesn't rely on the model's generated output (it works without any text generation) and thus can run in parallel with the agent's operation, making it a practical "watchdog" module. In essence, if the model's internal state shifts in a way indicative of losing the original instruction, the detector flags it.

Aside from activations, trajectory analysis provides external clues of drift. We can instrument the agent's cognitive loop (sense-think-act cycle) to look for anomalies corresponding to the dimensions above. For example, loop detection can be automated by logging all actions and using pattern recognition to spot repetition. If an agent issues the same tool command 5 times with no state change, that's a clear signal. Similarly, scope monitors can be built: e.g., in a coding environment, each file edit action can trigger a check "Is this file in the allowed list?". If not, raise an alert. Researchers have also suggested intent-aware monitoring: in multi-agent systems, one can classify the "intent" of each message and catch when agents start falling outside productive intents or rehashing the same point, which is essentially a drift from productive dialogue. High-quality intent classification models can flag when an agent's response is irrelevant to the current goal, providing an early warning that it has lost focus.

The detection algorithms should be lightweight and parallelizable, running as the agent operates (what one might call a "sleep time compute"). Concretely, this means we design these detectors to use either the transcripts or the model's intermediate states without interrupting the main agent loop. For example, a context divergence metric can run in the background: Dongre et al. (2025) formalize drift as the KL divergence between the agent's policy and a hypothetical goal-consistent reference policy. In practice, we might not have a perfect reference model, but we could approximate one (for instance, the agent's own behavior at the beginning of the task, or a higher-quality model's behavior). A rising divergence score turn by turn would signal drift accumulation. If computing KL between full distributions is infeasible, even a simpler proxy like comparing the agent's current action to the originally intended action (if known) could be used.

#### Validation of Detection

It's important that these detection mechanisms be validated against human judgment. In evaluations, one would run the agent on many tasks, have humans label when drift occurred, and then check detection accuracy. Prior work on agent failures has employed human annotators to categorize errors from execution logs – we can leverage similar methodology for drift specifically. For instance, human evaluators could mark points in a conversation where the assistant's response no longer followed the user's request. The detector's job is to catch those points (high true-positive) while not crying wolf during stable periods (low false-positive). Abdelnabi et al.'s study, for example, created a dataset called TaskTracker with over 500k instances, including many with injected distractor inputs, to train and test their drift probes. We envisage an evaluation where detectors are scored on benchmarks (perhaps an extension of SWE-Bench, τ-Bench, WebArena trajectories annotated for drift) for standardized comparison.

### 3.2 Resolution Strategies for Context Drift

Detection is only the first step – once drift is detected, what should the agent or system do? We propose a set of intervention strategies (some immediate, some for longer-term training fixes) that constitute a Resolution stage. Depending on the scenario, the system might:

#### 3.2.1 Remind or Refocus the Agent

A gentle intervention is to supply a contextual reminder of the original goal or constraints when drift is detected. Dongre et al. found that "simple reminder interventions reliably reduce divergence" and can push the conversation back toward the goal. In practice, if an agent's responses start veering off, the system could inject a prompt like, "Recall: the user's request is to do X in tone/style Y." This has been shown to help re-anchor the model's attention and effectively counteract drift in multi-turn dialogues. Such reminders act as a "restore point" for the agent's intent.

#### 3.2.2 Roll Back to a Safe State

In tasks where the agent can make irreversible changes (like editing code or databases), a viable resolution is to pause the agent and revert any changes made after the drift began. For example, if an agent was editing files and then started editing the wrong file (scope drift), the system could undo those changes and instruct the agent to focus on the correct location. This kind of checkpointing or transactional execution ensures that drift does not cause permanent damage. After rollback, a higher-level planner might reconsider the strategy.

#### 3.2.3 Re-plan or Adjust the Strategy

Often drift implies the current chain-of-thought is flawed. A resolution module (possibly a meta-agent) can intervene to re-plan from scratch or from an earlier context. For instance, if an agent has attempted the same failing approach multiple times (caught by our loop detector), the resolution could be: "Let's try a different approach to this problem." Some research prototypes allow an agent to call for a fresh plan when stuck, or even switch to an alternative tool specifically designed for recovery. Zhang et al. (2023) and others have explored agents that can decide to abandon the current plan and form a new one when encountering repeated failures. Having a feedback-aware planner that adapts to failure signals is a powerful way to resolve drift – essentially, the agent learns from its mistake and charts a new course, instead of stubbornly persisting. This idea connects to the concept of Reflexion or self-correction loops in recent LLM agent research, where the agent maintains a memory of errors and avoids repeating them.

#### 3.2.4 Early-Stopping and Human Alert

In cases of severe drift – e.g., the agent is completely off the rails or stuck in an endless loop – the best resolution might be to halt the agent and request human intervention or guidance. As one study suggests, if the system "detects repetitive, unresolved errors, it should trigger an early stop, halting the process before hitting maximum rounds to save resources". An early-stop can be accompanied by an alert or explanation: "The agent has deviated from the task and was stopped to prevent further errors." This is a safer fail-fast mechanism. It prevents the agent from causing more damage (or incurring cost in API calls, etc.) once drift is evident and irrecoverable internally. The human operator could then step in to either reset the agent or provide corrective instructions.

#### 3.2.5 Preventative Guardrails

Another angle of resolution is prevention: design the agent with guardrails that make drift less likely. For example, one can impose role or tool usage constraints so that even if the agent's policy drifts, it cannot execute an out-of-scope action. The Galileo AI team recommends "capability-based routing to prevent agents from accessing tools or APIs outside their specialization – reinforcing behavioral boundaries." By hard-coding some limits (like the agent cannot call a certain API unless a certain condition is met, or cannot write outside a directory), you effectively sandbox the agent's possible drift. These constraints act as resolution in the sense that they automatically correct or block a drifting action (e.g., a scope guard might automatically refuse an out-of-scope file write and prompt the agent to reconsider). Another guardrail is maintaining a "responsibility matrix" for multi-agent setups to avoid role drift – each agent is reminded of its role and cannot override another agent's duties.

Many of these resolution techniques can be implemented as a plug-and-play module alongside the agent. For instance, one can wrap an autonomous agent loop in a supervisory layer that monitors for drift signals and intervenes accordingly (inject reminder, reset plan, or stop). Importantly, such a module can run during the agent's "think" pauses (or even asynchronously), so that it doesn't slow down normal operation except when needed. This aligns with the idea of a meta-controller overseeing the main controller.

---

## 4. Instantiation to Different Benchmarks and Domains

Our framework is meant to generalize across long-horizon agent tasks, and we illustrate how the dimensions and detection/resolution methods instantiate in several benchmarks:

### 4.1 Coding Tasks (SWE-Bench and similar)

In a software agent benchmark (e.g., SWE-Bench, which focuses on multi-step coding challenges), context drift often appears as scope creep (editing wrong files) and repetitive debug loops. Our Scope dimension is highly relevant – we can concretely track file paths or functions the agent touches. A drift detector here might scan commit diffs to ensure only intended files are changed. Irrelevant tool use might correspond to using unnecessary library calls or performing redundant computations; metrics like "superfluous API calls" could be measured. Repetitive mistakes are typically seen when the coding agent keeps failing tests and reattempting similar fixes – essentially a debug loop that doesn't converge. We could log test outcomes and flag if the agent runs the same failing test multiple times without new strategy. The resolution might include running an automatic test after each code change (to provide immediate feedback), and if the agent fails the same test N times, trigger a re-plan or request for help. Prior research in code generation agents highlights the need for learning from feedback: e.g., if a compilation fails repeatedly, the agent should try a new approach instead of brute-forcing the same solution. Our framework formalizes that by catching the repetition and prompting a strategic shift. Notably, Arike et al. (2024) specifically mention scope-related drift in coding: the agent might start in the right file but "expand its actions to forbidden directories" over time. Evaluating a coding agent for context drift would involve checking how often it strays from the specified files or requirements, and how it responds to failures (does it loop or learn?).

### 4.2 Tool-Using Dialogue Tasks (τ-Bench and API calling scenarios)

τ-Bench is a benchmark where an agent must converse with a user and use external tools (like APIs) to achieve goals in domains like travel booking or retail. Here context drift can take the form of the agent violating rules or forgetting the user's requests over a long dialogue. For example, the user goal might be to change a flight reservation, but if the dialogue runs long, the agent might start offering irrelevant help or calling an unrelated API. Indeed, maintaining goal alignment in these simulated user interactions is challenging – Mehri et al. (2025) found that LLM-based user simulators failed to stay goal-focused ~40% of the time without special handling. Our instruction drift dimension (part of the context neglect aspect) is evident here: the agent might start ignoring user preferences or constraints (like budget or policies) as the conversation continues. To instantiate detection, one could employ a User Goal State Tracker (UGST) as proposed by Mehri et al., which explicitly tracks the structured goal state through the conversation. Deviations in that state (or the agent's actions not advancing that state) would indicate drift. For irrelevant tool usage, tau-Bench provides a clear mapping: if the agent calls an API that isn't needed (say, querying an unrelated database or using a wrong function), that's a drift event. A metric could be the number of API calls that do not contribute to task completion. As a resolution, the UGST approach effectively grounds the agent's responses in the tracked goal state, preventing it from wandering – this method showed significant improvements (over 10% absolute) in goal alignment metrics on τ-Bench. Additionally, interventions like policy reminders ("You are an airline booking assistant, stick to that role") can reel the agent back when it drifts. If the agent enters a loop (maybe repeatedly asking the user the same question), a detection would flag it and a resolution could be to break the loop by rephrasing the question or ending that line of inquiry. In summary, for tool-augmented dialogues, our framework would watch for rule-breaking (scope), off-track API calls, and dialog loops, all of which are measurable in τ-Bench logs. Encouragingly, industry benchmarks treat τ-Bench as a stress test for consistency: even advanced models like Claude have been evaluated on it, and improving pass^k consistency on τ-Bench (success over repeated trials) is now a target for top labs – essentially aligning with reducing drift across multiple runs.

### 4.3 Web Navigation Tasks (WebArena and WebShop)

WebArena is a realistic web environment benchmark where an agent must perform tasks like shopping or form-filling via a browser. Context drift in web agents often shows up as the agent getting distracted on the web or stuck in navigational loops. For instance, an agent might click unrelated links or open extra tabs outside the task's scope (e.g., in a shopping task, wandering to a different product category not relevant to the query – an analogue of wrong scope). It might also misuse tools by, say, invoking the browser's search when it already has the info on the current page (irrelevant action). The most notorious problem observed is the looping behavior – web agents commonly get stuck clicking the same element or reloading pages without end. In an analysis of hundreds of WebArena traces, "the most common complaint is agents easily get stuck in loops, endlessly repeating the same actions". Our framework's repetitive mistake detector would clearly catch this by analyzing the click sequence. Additionally, WebArena failures include things like the agent over-relying on partial observations or giving up on sub-tasks too early ("overestimation of task infeasibility" has been noted as a failure mode). That relates to context drift in that the agent prematurely concludes it can't do something (losing the context that it actually could if it tried another strategy). To detect such cases, one could monitor if the agent declares failure incorrectly or if it ignores available cues (similar to the "ignoring instructions" dimension). For resolution, one effective strategy is to give the agent a form of memory or state tracking (e.g., remember which links have been tried, to avoid repeating) – some recent agents incorporate a history of visited states to prevent loops. Another is an early-stop: if the agent clicked the same button 10 times, maybe stop and refresh the page or provide a hint. In the invariantlabs analysis, tools that automatically caught looping or hallucination were used to debug and improve the agent, yielding up to 16% performance improvement on WebArena after fixes. This underlines that systematically addressing drift issues can directly raise success rates. When evaluating web agents, one would instantiate our metrics by counting things like "unique pages visited vs. total clicks" (low ratio might indicate redundant clicks), checking if all required subtasks on a page were completed (to ensure no instruction was skipped), etc. WebSuite, a diagnostic benchmark for web agents, takes a similar approach by breaking tasks into fine-grained actions and pinpointing which action failed – our drift dimensions can map onto those action-level failures (e.g., failing to click the correct link could be a wrong-scope or context misalignment issue). By applying the context drift framework, we aim to not just note that a web task failed, but why – did the agent lose track of the user query, did it get caught in an endless login loop, or start interacting with the wrong website entirely? Each is a different drift scenario requiring a tailored fix.

---

## 5. Evaluating the Framework

To validate a Context Drift Detection & Resolution framework, we need rigorous evaluation on multiple benchmarks and against human judgment:

### 5.1 Benchmark Trajectories

We would run our instrumented agent (with detection & resolution modules) on established benchmarks like SWE-Bench, τ-Bench, WebArena, MultiWOZ, etc., and log detailed trajectories. The evaluation should check two things: (1) **Detection performance** – does the framework successfully catch drift events in the trajectory? and (2) **Impact on task success** – does intervening (resolving) actually improve outcomes? For detection performance, since ground truth drift "events" are not usually labeled in benchmarks, we may create a labeled evaluation set. This could involve taking a sample of agent runs and having experts annotate moments of drift. Similar to how some studies built failure taxonomies by manual log review, we can build a drift annotation schema and label when the agent's action first diverged from the goal or when it entered a loop, etc. Given such ground truth, we can compute precision/recall for the drift detector. For instance, does our loop detector catch all the real loops without flagging normal backtracking as a loop? Abdelnabi's activation-based detector would be evaluated on scenarios of known instruction injections and normal inputs to ensure it flags the malicious drift and not the benign changes (their results on ROC AUC are promising). (If available, we can leverage datasets like TaskTracker for standardized testing of drift detection algorithms on LLMs.)

### 5.2 Human Comparison

Ultimately, we want our framework's notion of "drift" to align with human intuition of when the agent is off-track. Thus, an evaluation can include a human study: present annotators with agent transcripts (or action logs) and ask them to identify if/when the agent went astray from the task. Then compare that to the output of our detection system. A high agreement would validate that our dimensions capture the meaningful errors. Such comparisons have precedent – for example, in dialogue consistency evaluation, human judgments are often the gold standard. In the context drift case, humans might notice things like "the agent's solution no longer addresses the user's request at turn 8," which should coincide with our detectors. Any discrepancies could highlight either missed drift (false negatives) or overly sensitive alerts (false positives), guiding further refinement of the detection rules or model.

### 5.3 Ablation and Metrics Analysis

We should also evaluate the contribution of each dimension's handling. For instance, turn off the scope guard and see if scope-related errors increase; disable loop intervention and measure if tasks more often fail due to infinite loops. An ideal table in the paper might show the drift metrics for various agent systems with and without our framework. We expect to see, for example, "average irrelevant tool calls per task" drop when the irrelevant-tool detector/constraint is enabled, or "loop occurrences" drop when loop resolution is enabled. Moreover, we would include overall task success rates (or reward metrics) to show that reducing drift correlates with better performance. In one case study, simply fixing common failure modes (including loops and ignored instructions) led to significant success rate gains on WebArena – we anticipate similar improvements across benchmarks by addressing drift.

### 5.4 Generalization

Yucheng (as mentioned in the prompt) pointed out the importance of a generalized approach. Thus, we should test the framework on diverse agents (coding agent, planning agent, web agent) to ensure the drift dimensions and detection algorithms apply broadly. It's possible certain drift dimensions manifest differently (e.g., "irrelevant tool use" in a pure coding scenario might mean using an unnecessary function rather than an external API), but the core ideas remain. Demonstrating the framework's applicability to multiple top-tier benchmarks will strengthen the claim that our context drift evaluation is comprehensive and domain-agnostic. Indeed, recent surveys position benchmarks like τ-Bench (for tool-using dialog) and SWE-Bench (for code) as complementary, and stress that a robust agent should be evaluated on multi-step reasoning and strict goal-following behaviors across domains. Our framework provides exactly that lens – focusing on how well the agent stays on target in any long-horizon setting.

---

## 6. Conclusion

Context Drift Detection & Resolution is an emerging area of AI agent research, with a number of 2024–2025 works laying the groundwork. By formalizing context drift and breaking it into measurable dimensions, we can build diagnostic tools much like "model cards" but for agent behavior over time. Early approaches like using activation deltas to "catch LLMs off track" and goal-aware simulators to maintain alignment show that drift is detectable and addressable. Our proposed two-stage framework generalizes these ideas: continuously monitor the agent for signs of drifting and intervene with corrective strategies before small divergences snowball into mission failure. The end goal is a more resilient, self-correcting agent that remains aligned with user intentions even as it tackles complex, long tasks. This line of research is crucial for scaling AI agents to real-world applications, and we envision future benchmarks explicitly incorporating context-drift metrics (for instance, reporting how often an agent had to be "reined in" during a task). By evaluating and comparing agents on such metrics, the community can drive progress toward agents that not only can plan and act, but also can stay true to their objectives from start to finish.

---

## Sources

- Dongre et al., "Drift No More? Context Equilibria in Multi-Turn LLM Interactions," 2025
- Abdelnabi et al., "Are You Still on Track!? Catching LLM Task Drift with Activations," 2024
- Arike et al., "Evaluating Goal Drift in Language Model Agents," 2024
- Invariant Labs Blog, "Analyzing Hundreds of AI Web Agent Traces," July 2024
- Lurf et al., "Why Autonomous Agents Fail at Tasks," 2025
- Galileo AI Blog, "7 Reasons Why Multi-Agent Systems Fail," 2025
- Mehri et al., "Goal Alignment in LLM-Based User Simulators," 2025
- Sierra Tech Blog, "τ-Bench for Multi-Turn Agent Evaluation," 2025
- Li & Waldo, "WebSuite: Why Web Agents Fail," 2024
- (Additional citations from the text above are included inline.)
