Adaptive Memory System for Coding Agents
CS224V Project | 6 Weeks | Jeremy Gu 
 
Part 1. Executive Summary
Oct 22 Yucheng's Research Direction [Link to notes]: Agent memory systems that (1) learn across sessions, (2) improve from feedback, and (3) decontextualize specific experiences into transferable patterns. His key insight: "abstraction level needs to be adjusted on the fly—nobody is doing that."
Key Questions: Current coding agents (Cursor, Claude Code, SWE-agent) fail at critical tasks:
1.	Context Drift: Agents stray from original objectives during multi-step tasks, attempting unnecessary refactoring or exploring irrelevant code paths
○	Q1: How can agents maintain goal alignment during long coding tasks?
○	Sub-tasks: Parse goals into machine-checkable objectives, detect divergence, implement checkpoint/rollback
2.	Zero Cross-Session Learning: Each coding session starts from scratch—agents cannot leverage previously solved problems to accelerate future tasks
○	Q2: How can agents extract and reuse patterns across sessions?
○	Sub-tasks: Decontextualize solutions into generalizable patterns, retrieve relevant patterns, measure reuse rate
3.	Static Abstraction: Agents provide one-size-fits-all responses that don't adapt to user expertise or task complexity
○	Q3: How should abstraction levels adapt dynamically?
○	Sub-tasks: Model user expertise from outcomes, store multi-level patterns, select appropriate detail
Result: Developers waste 15-20 minutes per session re-explaining context, and agents produce off-target solutions requiring rollback.
Our Project: We build a coding agent memory system addressing all three requirements. When an agent fixes a bug (e.g., null pointer in payment.py), we extract a generalizable pattern ("objects need null validation") stored at multiple abstraction levels (hint/explanation/code). Future sessions retrieve and recontextualize this pattern to new contexts (user objects, order objects). The system self-learns optimal abstraction levels: novice users get detailed code, experts get concise hints, adapting based on outcomes and feedback.
Why Coding: As Yucheng noted, coding is already an abstraction layer, making decontextualization tractable. We will use SWE-bench which provides 2,294 real-world tasks for rigorous evaluation.
Novel Contribution: Dynamic abstraction adjustment—the research gap Yucheng identified that "nobody is doing."
Expected Impact: See Evaluation Metrics table below for quantifiable targets.
 
Part 2. Alignment with Yucheng's Research Direction
Yucheng's Requirements (from our 10/22/2024 meeting):
1.	✅ Cross-session memory: Store and retrieve knowledge across conversations
2.	✅ Feedback loops: Learn from both test outcomes (pass/fail) and human ratings
3.	✅ Decontextualization → Recontextualization: Transform specific examples → general patterns → apply to new contexts
Yucheng's Key Insight:
"Coding is already abstraction.. abstraction level needs to be adjusted on the fly. Nobody is doing that."
 
How We Address Yucheng's Three Requirements
1. Cross-Session Memory
●	Store learned patterns in searchable database
●	Retrieve relevant past solutions for new similar problems
●	Example: Session 1 learns "payment null check" → Session 10 reuses for user objects
2. Feedback-Driven Learning
●	Pattern confidence adjusts based on test pass/fail
●	User feedback ("too detailed") updates abstraction preferences
●	System improves which patterns work for which contexts
3. Decontextualization → Transfer
●	Extract: "payment.py line 45 null check" → "Objects need null validation"
●	Generalize: Pattern applies to payment, user, order, transaction domains
●	Recontextualize: When new task mentions "user object", suggest null check pattern
●	Result: 60% time savings via pattern reuse vs. solving from scratch
 
Our Novel Contribution: Dynamic Abstraction
The "Nobody Is Doing" Part Yucheng Identified:
Static systems always return same detail level. Our system adapts based on:
●	User expertise (inferred from success rate)
●	Past feedback ("last time user said 'too detailed'")
●	Task complexity
Example Self-Learning:
Novice user gets pattern → detailed code example → succeeds → remember user needs detail
Expert user gets same pattern → concise hint → succeeds → remember user prefers brevity  
User says "too detailed" → system adjusts user model → next time provides less detail
This is true self-improvement: system gets better at teaching patterns (choosing right abstraction), not just collecting them.
 
Part 3. System Design
High-Level Architecture
User Input → Goal Parser → Memory System → Coding Agent
                ↓              ↑              ↓
         Goal Tracker ← Alignment Checker → Execute & Test
                              ↓
                    Decontextualization
                              ↓
                      Pattern Library
Three Core Components
1. Goal-Aware Tracking
●	Input: "Fix the null pointer bug in payment processing"
●	Output: Structured goal with scope and success criteria
●	Function: Monitor each agent action for alignment with goal
2. Cross-Session Pattern Learning
●	Input: Completed session logs (actions + outcomes)
●	Output: Decontextualized patterns (e.g., "payment objects need null checks")
●	Function: Extract generalizable lessons, store in searchable memory
3. Dynamic Abstraction Engine
●	Input: Pattern + user context + task complexity
●	Output: Appropriate detail level (code example vs. high-level hint)
●	Function: Adapt knowledge granularity on-the-fly
 
Part 4. Implementation Architecture
Data: SWE-bench
●	2,294 real GitHub issues with human-written fixes (ground truth)
●	Train memory on first 50 issues → evaluate on next 100 issues
●	Provides: problem description, repo code, test suite, solution patch
System Components & Dependencies
1. INFRASTRUCTURE SETUP
   ├─ Relational DB (PostgreSQL): Store sessions, actions, patterns
   ├─ Vector DB (ChromaDB): Embeddings for semantic search
   └─ SWE-bench harness: Task loader + test executor

2. GOAL-AWARE TRACKING (addresses Q1)
   ├─ Goal Parser: LLM extracts structured goal from natural language
   ├─ Action Logger: Record all agent actions with timestamps
   └─ Alignment Checker: Rule-based + LLM hybrid validation
       → Dependency: Goal Parser output

3. CROSS-SESSION LEARNING (addresses Q2)
   ├─ Pattern Extractor: LLM summarizes session → generalizable lesson
   │   → Dependency: Action logs + test outcomes
   ├─ Pattern Store: Multi-level storage (hint/explanation/code)
   └─ Retrieval Engine: Semantic search + confidence filtering
       → Dependency: Pattern embeddings

4. DYNAMIC ABSTRACTION (addresses Q3)
   ├─ User Modeler: Track expertise from success rates
   ├─ Abstraction Selector: Choose detail level per context
   └─ Feedback Learner: Update from user reactions ("too detailed")
       → Dependency: User model + pattern multi-levels

5. AGENT EXECUTION LOOP
   Parse goal → Retrieve patterns → Generate fix → Check alignment
   → Execute & test → Learn pattern → Update memory
   → Dependencies: All above components integrated
Tech Stack: Python | LLM API (Claude/GPT-4) | Relational + Vector databases | Docker
Key LLM Uses:
1.	Goal parsing (structured JSON output)
2.	Pattern extraction (session log → generalizable lesson)
3.	Alignment checking (is action on-goal? yes/no)
4.	Code generation (fix proposals with context)
 
Part 5. Demo & Evaluation
What We Will Demonstrate
Core Capabilities (5-minute live demo):
1.	Goal tracking: System parses "fix race condition" → blocks off-topic refactoring
2.	Pattern reuse: Retrieves past solution ("use Redis lock") → applies to new problem
3.	Dynamic abstraction: Different detail levels for same pattern based on user expertise
4.	Learning: Extracts generalizable pattern after solving task
Demo Interface: CLI (required) + simple web UI (optional—if time permits for better visualization)
 
Evaluation Metrics
Automated Metrics (computed from SWE-bench runs):
Metric	How Measured	Baseline	Target	Priority
Pattern Reuse Rate	% sessions where pattern applied	0%	≥30%	P0
Time to Solution	Minutes to passing tests	30 min	<20 min	P0
First-Try Success	% solutions pass on first attempt	40%	≥55%	P1
Distraction Frequency	# off-goal actions blocked/session	3.0	<1.5	P1
Human Evaluation (optional):
Metric	How Measured	Priority
Pattern Quality	Expert: "Would reuse?" (1-5)	P1
Abstraction Fit	User: "Detail level right?"	P2
Statistical Tests: T-tests (p<0.05), Effect sizes (Cohen's d>0.5), Ablation studies
Priority: P0=Must achieve | P1=Strong results | P2=Nice to have
 
Deliverables
1.	Working System: CLI tool + GitHub repo
2.	Evaluation Report: Metrics on 50+ tasks with statistical analysis
3.	Demo Video: 5-min showing all components + results
4.	Paper Draft: 4-6 pages for workshop
Success Criteria:
●	Minimum: Solve ≥10 tasks, demonstrate pattern reuse ≥3 times, show distraction prevention
●	Strong: All P0+P1 metrics hit targets + statistical significance
 
Part 6. Timeline & Milestones
Weeks	Milestone	Deliverable
1-2	Foundation	Goal tracking + logging works on 5 tasks
3	CHECKPOINT	Pattern extraction + retrieval works (must have!)
4	Abstraction	Multi-level patterns + user modeling
5	Evaluation	50-task experiment complete, metrics computed
6	Polish	Demo video + paper draft
Week 3 is critical: If cross-session learning doesn't work by then, we pivot to simpler pattern matching.


