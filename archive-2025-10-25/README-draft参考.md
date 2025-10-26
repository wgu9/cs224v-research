# Adaptive Memory System for Coding Agents: Learning from Experience with Dynamic Abstraction

**Project Proposal**  
**Student**: Jeremy Gu (Director of Data Science, SageSure)  
**Advisor**: Yucheng (Prof. Lam's Group)  
**Quarter**: Fall 2024  
**Date**: October 23, 2024

---

## 1. Project Title

**Adaptive Memory System for Coding Agents: Learning from Experience with Dynamic Abstraction**

**Alternative titles**:
- Goal-Aware Memory for Cross-Session Code Generation
- Self-Evolving Coding Agents with Decontextualized Experience

---

## 2. Top 3-4 Research Questions

### **Q1: How can coding agents maintain goal alignment across multi-step tasks?**
- **Problem**: Current coding agents (Cursor, Claude Code) frequently "drift" from the original objective during iterative code modifications, leading to scope creep and wasted effort.
- **Gap**: Existing systems lack real-time goal tracking and distraction detection mechanisms.
- **Our approach**: Design a goal-aware memory system that logs intended objectives, monitors action alignment, and provides checkpoint/rollback capabilities.

### **Q2: How can agents learn generalizable patterns from past coding sessions?**
- **Problem**: Each coding session is treated independently; agents cannot leverage previously solved problems to accelerate future tasks.
- **Gap**: While RAG-based retrieval exists, true decontextualization (extracting high-level patterns from specific solutions) remains unsolved.
- **Our approach**: Develop automatic pattern extraction that transforms concrete solutions (e.g., "added null check in payment.py line 45") into reusable abstractions (e.g., "payment objects require null validation").

### **Q3: How should abstraction levels dynamically adapt to different contexts and users?**
- **Problem**: The same experience may require different levels of detail depending on: (a) user expertise, (b) task complexity, (c) domain familiarity.
- **Gap**: As Prof. Yucheng noted: "abstraction level needs to be adjusted on the fly. Nobody is doing that."
- **Our approach**: Build an adaptive memory system that learns optimal abstraction granularity through human feedback and task outcomes.

### **Q4: How can we quantitatively evaluate cross-session learning effectiveness?**
- **Problem**: Memory systems lack standardized metrics for measuring learning transfer and efficiency gains.
- **Gap**: Existing evaluations focus on single-session performance (e.g., pass@1), not cross-session improvement.
- **Our approach**: Establish metrics including: pattern reuse rate, time-to-solution reduction, distraction frequency, and first-attempt success rate on similar problems.

---

## 3. Motivation

### **3.1 The Core Problem: Coding Agents Are Inefficient and Forgetful**

Despite rapid advances in LLM-based coding assistants (GitHub Copilot, Cursor, Claude Code), users face persistent frustrations:

1. **Context Drift**: AI frequently strays from the original task, attempting unnecessary refactoring or over-engineering simple fixes.
2. **Repetitive Explanations**: Users must re-explain project conventions, dependencies, and past decisions in every new session.
3. **No Learning Transfer**: Solving a bug on Monday doesn't help the agent solve a similar bug on Friday.
4. **Lack of Accountability**: When things go wrong, there's no audit trail of what was changed and why.

**Real-world impact**: 
- At SageSure (my current company), our data science team spends ~30% of coding time "babysitting" AI agents to prevent scope creep.
- A recent study showed developers using Cursor spend 15-20 minutes per session just providing context that should be remembered.

### **3.2 Why Existing Solutions Fall Short**

| Approach | Limitation |
|----------|-----------|
| **In-context learning** | Token limits (~200K) mean memory is ephemeral |
| **RAG-based retrieval** | Retrieves *what* was done but not *why* or *how to generalize* |
| **ChatGPT Memory** | Stores facts ("user prefers Python") but not *procedural knowledge* ("how to debug race conditions") |
| **Cursor's workspace history** | File-level tracking without goal alignment or pattern learning |

**Key insight from Prof. Yucheng**: Coding is already an abstraction layer, making it more tractable than survey paper generation. The challenge is **decontextualizing specific solutions into reusable patterns** and **dynamically adjusting abstraction levels**.

### **3.3 Why This Matters (Scientific & Practical Value)**

**Scientific contribution**:
- First system to demonstrate **dynamic abstraction level adjustment** in agent memory
- Novel architecture combining goal tracking + cross-session learning + human-in-the-loop feedback
- Establishes evaluation benchmarks for measuring cross-session learning transfer

**Practical impact**:
- **For developers**: 50%+ reduction in context-providing overhead; fewer "runaway refactoring" incidents
- **For enterprises**: Codifiable team knowledge; onboarding acceleration; compliance audit trails
- **For my career**: Direct path to productization (cursor extensions, enterprise tools) aligned with my CTO aspirations

---

## 4. Project Description

### **4.1 System Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERACTION                     │
│  "Fix the payment processing bug on Safari browser"    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────┐
│              GOAL PARSER & TRACKER                      │
│  • Parse user intent → structured goal                  │
│  • Define scope (allowed files, forbidden actions)      │
│  • Set success criteria (tests pass, no regressions)    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ↓ Store in Memory
┌─────────────────────────────────────────────────────────┐
│                   MEMORY SYSTEM                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Session Memory (Short-term)                       │ │
│  │ • Current goal + constraints                      │ │
│  │ • Action log (file changes, tests, feedback)     │ │
│  │ • Checkpoints for rollback                       │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Pattern Memory (Long-term)                        │ │
│  │ • Decontextualized solutions                     │ │
│  │ • Success/failure cases                          │ │
│  │ • Abstraction levels + applicability contexts    │ │
│  └───────────────────────────────────────────────────┘ │
└────────────────┬────────────────────────────────────────┘
                 │
                 ↓ Retrieved when needed
┌─────────────────────────────────────────────────────────┐
│           CODING AGENT (Claude/GPT-4)                   │
│  • Receives goal + relevant past patterns              │
│  • Proposes code changes                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ↓ Every action
┌─────────────────────────────────────────────────────────┐
│            ALIGNMENT CHECKER                            │
│  • Is this action aligned with the goal?               │
│  • Is this change in allowed scope?                    │
│  • Should we create a checkpoint?                      │
│  Decision: ALLOW / ASK_USER / BLOCK / ROLLBACK         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ↓ If allowed
┌─────────────────────────────────────────────────────────┐
│            CODE EXECUTION & TESTING                     │
│  • Apply code changes                                  │
│  • Run tests (unit, integration)                       │
│  • Collect feedback (pass/fail, errors, human review)  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ↓ After session
┌─────────────────────────────────────────────────────────┐
│         DECONTEXTUALIZATION ENGINE                      │
│  • Extract high-level patterns from session log        │
│  • Determine optimal abstraction level                 │
│  • Store in Pattern Memory for future reuse            │
└─────────────────────────────────────────────────────────┘
```

### **4.2 Key Components**

#### **Component 1: Goal-Aware Session Management**
**Problem addressed**: Q1 (goal alignment)

**Functionality**:
- Parse natural language goals into structured objectives
- Example: "Fix payment bug" → `{objective: "fix NPE", files: ["payment.py"], forbidden: ["refactor", "add_features"]}`
- Track goal progress with checkpoints every N actions or M minutes
- Detect distractions: flag actions outside allowed scope

**Technical approach**:
- LLM-based goal parsing with structured output (JSON schema)
- Rule-based + LLM-based alignment checking (hybrid for reliability)
- Git-based checkpointing for clean rollbacks

**Innovation**: First system to enforce goal boundaries *during* code generation, not just post-hoc.

---

#### **Component 2: Cross-Session Pattern Learning**
**Problem addressed**: Q2 (learning from experience)

**Functionality**:
- After each session, extract generalizable patterns
- Example transformation:
  ```
  Specific: "Added if user is not None check in payment.py line 45"
  ↓
  Pattern: "Payment objects require null validation before use"
  ↓
  Metadata: {
    applicability: ["payment", "user", "order"],
    confidence: 0.85,
    success_count: 3,
    failure_count: 0
  }
  ```
- Semantic search over pattern library when starting new tasks
- Suggest relevant patterns: "Last time we solved this with X, try that?"

**Technical approach**:
- **Extraction**: LLM prompt engineering to distill lessons learned
- **Storage**: Vector database (ChromaDB/Pinecone) for semantic retrieval
- **Retrieval**: Hybrid search (semantic + keyword + temporal)

**Innovation**: Goes beyond RAG by transforming specific actions into reusable abstractions.

---

#### **Component 3: Adaptive Abstraction Engine**
**Problem addressed**: Q3 (dynamic abstraction)

**Functionality**:
- Adjust pattern detail based on context:
  - **Novice user**: Show concrete code examples
  - **Expert user**: High-level hints only
  - **New domain**: More guidance; **Familiar domain**: Less handholding
- Learn abstraction preferences from human feedback
  - User says "too detailed" → increase abstraction level
  - User says "too vague" → decrease abstraction level

**Technical approach**:
- **User modeling**: Track expertise per domain (inferred from success rates)
- **Multi-level pattern storage**:
  ```python
  pattern = {
    "level_1": "Check for null",
    "level_2": "Add null validation before accessing object properties",
    "level_3": "if obj is not None: obj.method() else: handle_error()",
    "code_example": "if payment is not None:\n    payment.process()\nelse:\n    log_error('Payment object is None')"
  }
  ```
- **Reinforcement learning**: Optimize abstraction level selection based on task outcomes

**Innovation**: This is the "nobody is doing" part Prof. Yucheng mentioned—active, on-the-fly abstraction adjustment.

---

#### **Component 4: Feedback Loop & Reward System**
**Problem addressed**: All questions (provides training signal)

**Functionality**:
- **Human feedback**:
  - Thumbs up/down on proposed solutions
  - Explicit corrections ("don't refactor, just fix")
  - Post-session ratings ("was this helpful?")
- **Automated feedback**:
  - Test outcomes (pass/fail)
  - Code quality metrics (complexity, duplication)
  - Production monitoring (if deployed)
- Reward signal:
  ```
  reward = 
    + test_pass_bonus
    + human_approval
    + time_efficiency_gain
    - distraction_penalty
    - rollback_penalty
  ```

**Technical approach**:
- Reward shaping based on multiple signals
- Store reward alongside patterns to prioritize high-value lessons
- Optional: Fine-tune small adapter (LoRA) on high-reward trajectories

**Innovation**: Multi-modal feedback (human + automated) to ground learning in real outcomes.

---

### **4.3 Implementation Plan (6 Weeks)**

#### **Week 1-2: Foundation**
- [ ] Set up SQLite/PostgreSQL for memory storage
- [ ] Implement goal parsing + structured storage
- [ ] Build basic action logging (file changes, timestamps)
- [ ] Create rule-based alignment checker (file scope, keyword filtering)
- [ ] Integrate with Claude API for code generation
- **Deliverable**: Can record one coding session with goal tracking

#### **Week 3: Cross-Session Learning**
- [ ] Implement pattern extraction (LLM-based summarization)
- [ ] Set up ChromaDB for vector storage
- [ ] Build semantic retrieval system
- [ ] Test on 10 SWE-bench problems: does pattern reuse work?
- **Deliverable**: Can retrieve and apply patterns from past sessions

#### **Week 4: Adaptive Abstraction**
- [ ] Implement multi-level pattern storage (4 abstraction levels)
- [ ] Build user modeling (track expertise by domain)
- [ ] Add feedback collection UI (thumbs up/down)
- [ ] Test abstraction level selection on diverse users
- **Deliverable**: System adapts detail level based on user/context

#### **Week 5: Evaluation**
- [ ] Run 50-100 SWE-bench tasks with memory system
- [ ] Compute metrics: reuse rate, time savings, distraction frequency
- [ ] Compare against baselines: no memory, static memory
- [ ] Conduct user study with my SageSure team (5 participants)
- **Deliverable**: Quantitative + qualitative results

#### **Week 6: Polish & Write-up**
- [ ] Create demo video showing key features
- [ ] Draft conference paper (4-6 pages)
- [ ] Prepare final presentation for class
- [ ] Document code for open-source release
- **Deliverable**: Complete demo + paper draft

---

### **4.4 Dataset & Evaluation**

#### **Primary Dataset: SWE-bench**
- **Description**: 2,294 real-world GitHub issues from 12 popular Python repositories
- **Why suitable**:
  - Real bugs (not toy problems)
  - Human-written fixes available (ground truth)
  - Covers diverse domains (web, data, ML)
  - Standard benchmark in coding agent research
- **Usage**: Train memory on first 50% of issues, evaluate cross-session learning on second 50%

#### **Secondary Dataset: Team Usage Data**
- **Description**: Real coding sessions from my SageSure data science team
- **Why suitable**:
  - Authentic user feedback
  - Domain-specific patterns (insurance, fraud detection)
  - Can measure actual productivity impact
- **Usage**: Qualitative evaluation + case studies

#### **Evaluation Metrics**

| Metric | Definition | Baseline | Target |
|--------|-----------|----------|--------|
| **Pattern Reuse Rate** | % of sessions where past pattern was applied | 0% | 40%+ |
| **Time to Solution** | Minutes to complete task | 30 min | 15 min |
| **First-Try Success** | % of solutions that pass tests on first attempt | 40% | 65%+ |
| **Distraction Frequency** | Out-of-scope actions per session | 3.0 | <1.0 |
| **Rollback Rate** | % of sessions requiring rollback | 20% | <5% |
| **Human Approval** | % of solutions approved by developers | 60% | 80%+ |

---

## 5. Expected Demo at End of Quarter

### **5.1 Live Demonstration Scenario**

**Setup**: Real-time coding session showing all system components

**Act 1: Goal Setting & Tracking (3 minutes)**
```
USER: "Fix the race condition in the payment processing pipeline"

SYSTEM: 
✓ Goal parsed: Fix race condition
✓ Scope: payment_service.py, payment_worker.py
✓ Forbidden: Refactoring entire pipeline
✓ Success criteria: Integration tests pass + no duplicates

[System displays goal dashboard with progress tracker]
```

**Act 2: Pattern Retrieval (2 minutes)**
```
SYSTEM: "Found 2 relevant past patterns:"

Pattern #1 (from 2024-09-15):
  Problem: Payment duplicates due to concurrent requests
  Solution: Added distributed lock using Redis
  Confidence: 0.9
  
Pattern #2 (from 2024-08-22):
  Problem: Race condition in order processing
  Solution: Implemented idempotency keys
  Confidence: 0.7

Would you like to apply Pattern #1? [Yes/No/Customize]
```

**Act 3: Distraction Prevention (2 minutes)**
```
AI: "I'll fix the race condition and also refactor the entire payment module for better performance..."

SYSTEM: 🚨 ALIGNMENT ALERT
  Action: Refactor payment module
  Status: OUT OF SCOPE
  Reason: Goal is to fix race condition only
  
[User approves: Block refactoring]

SYSTEM: Blocked. AI will focus on race condition fix only.
```

**Act 4: Checkpoint & Recovery (2 minutes)**
```
[AI makes changes to payment_service.py]

SYSTEM: Checkpoint created at 5 actions
  Files changed: payment_service.py (+15 lines)
  Tests: Running...
  
TESTS: FAILED (introduced new bug)

SYSTEM: Rollback to checkpoint? [Yes/No]
[User: Yes]

SYSTEM: Rolled back to checkpoint. AI will try alternative approach.
```

**Act 5: Success & Learning (2 minutes)**
```
[AI applies distributed lock solution]

TESTS: PASSED ✓
Human feedback: [Thumbs up] "Clean solution"

SYSTEM: Learning from this session...
  
New pattern extracted:
  "For payment race conditions, use Redis distributed locks with 30s TTL"
  Applicability: payment, order, transaction processing
  Abstraction level: Auto-adjusted based on user expertise
  
Pattern saved for future reuse.

Session summary:
  Time: 18 minutes (vs. 35 min baseline)
  Distractions blocked: 2
  Pattern reused: 1
  New pattern learned: 1
```

---

### **5.2 Demo Dashboard**

**Visual interface showing**:
1. **Goal Tracker**: Real-time progress toward objective
2. **Memory Browser**: Searchable library of learned patterns
3. **Session Timeline**: Chronological log of all actions + checkpoints
4. **Metrics Dashboard**:
   - Pattern reuse rate over time
   - Average time-to-solution (trending down)
   - Distraction frequency (trending down)
   - Success rate (trending up)
5. **Team Knowledge Graph**: Visualization of team's collective patterns

---

### **5.3 Deliverables**

#### **Technical Deliverables**
1. **Working System**:
   - Integrated with Claude API (or local LLM)
   - CLI + Web UI
   - Persistent memory database with 50+ learned patterns
   
2. **Open Source Repository**:
   - Clean, documented codebase
   - Setup instructions + examples
   - Integration guide for Cursor/VS Code

3. **Evaluation Results**:
   - Performance on 50+ SWE-bench tasks
   - User study results (5+ participants)
   - Comparison with baselines

#### **Academic Deliverables**
1. **Conference Paper Draft** (4-6 pages):
   - Title: "Adaptive Memory for Coding Agents: Learning from Experience with Dynamic Abstraction"
   - Target venues: ICML, NeurIPS, ICLR (workshop track)
   - Sections: Intro, Related Work, Method, Experiments, Results, Discussion
   
2. **Final Presentation** (15 minutes):
   - Problem motivation
   - Technical approach
   - Live demo
   - Results & impact
   - Future work

#### **Practical Deliverables**
1. **Case Studies** from SageSure team usage:
   - Documenting real productivity gains
   - Identifying edge cases for future work
   
2. **Product Roadmap** for commercialization:
   - Cursor extension (Phase 1)
   - Enterprise version with team memory sharing (Phase 2)
   - API for other coding tools (Phase 3)

---

## Appendix: Concise Q&A

### **What you aim to achieve (main goals)**

1. **Build a goal-aware memory system** that prevents coding agents from drifting off-task
2. **Enable cross-session learning** by decontextualizing specific solutions into reusable patterns
3. **Dynamically adjust abstraction levels** based on user expertise and task context
4. **Establish quantitative benchmarks** for measuring cross-session learning effectiveness

### **Why the project is important or interesting**

**Scientific importance**:
- Addresses the "decontextualization" research gap Prof. Yucheng identified: extracting generalizable knowledge from specific experiences and adapting abstraction levels on-the-fly
- First system to combine goal tracking + memory + dynamic abstraction in coding agents
- Establishes new evaluation paradigm for cross-session learning

**Practical importance**:
- Coding assistants (Cursor, Claude Code) are used by millions but remain inefficient due to lack of memory and goal tracking
- Directly saves developer time: 50%+ reduction in context overhead and distraction incidents
- Enables team knowledge sharing: codify institutional knowledge automatically
- Strong commercialization potential aligned with my CTO career goals

**Personal importance**:
- Leverages my background in data science, ML systems, and engineering leadership
- Solves pain points I experience daily at SageSure
- Creates a differentiator vs. other agent memory projects (focus on coding + dynamic abstraction)

### **The approach or methods you plan to use**

**Core methodology**:
1. **Goal Parsing & Tracking**: LLM-based structured output + state machine for progress monitoring
2. **Pattern Extraction**: Post-session LLM prompting to distill high-level lessons from action logs
3. **Memory Architecture**: Hybrid system with session memory (short-term) + pattern memory (long-term)
4. **Retrieval**: Semantic search (embeddings) + keyword matching + temporal filtering
5. **Alignment Checking**: Rule-based (scope validation) + LLM-based (context-aware decisions)
6. **Adaptive Abstraction**: User modeling + multi-level pattern storage + reinforcement from feedback
7. **Evaluation**: SWE-bench benchmark (quantitative) + SageSure team study (qualitative)

**Technical stack**:
- **LLM**: Claude Sonnet 4.5 API (or GPT-4)
- **Memory storage**: PostgreSQL (structured data) + ChromaDB (vector embeddings)
- **Integration**: MCP (Model Context Protocol) for Cursor/Claude Code
- **UI**: Streamlit (prototype) → React (production)
- **Evaluation**: Python scripts on SWE-bench dataset

### **Expected final deliverable**

**Primary deliverable**: 
A working adaptive memory system for coding agents with:
- Real-time goal tracking and distraction prevention
- Cross-session pattern learning and reuse
- Dynamic abstraction level adjustment
- Demonstrated 40%+ pattern reuse rate and 50%+ time savings on SWE-bench

**Academic deliverable**:
4-6 page conference paper draft with:
- Novel architecture combining goal awareness + memory + dynamic abstraction
- Quantitative evaluation on 50+ SWE-bench tasks
- User study results from real developers
- Analysis of what patterns generalize well and why

**Practical deliverable**:
Open-source repository + demo video showing:
- Live coding session with all features
- Metrics dashboard visualization
- Integration guide for Cursor/VS Code

---

## Success Criteria

This project will be considered successful if:

1. ✅ **System works end-to-end**: Can complete 10+ SWE-bench tasks with memory-based assistance
2. ✅ **Learning transfer demonstrated**: Pattern reuse rate ≥30% (vs. 0% baseline)
3. ✅ **Efficiency gains measured**: ≥30% reduction in time-to-solution on repeated problem types
4. ✅ **Distraction prevention validated**: <1.0 out-of-scope actions per session (vs. 3.0 baseline)
5. ✅ **User validation**: Positive feedback from ≥4 out of 5 SageSure team members
6. ✅ **Research contribution**: Clear evidence that dynamic abstraction improves outcomes
7. ✅ **Deliverables complete**: Working demo + paper draft + open-source code

---

## Timeline Summary

| Week | Focus | Key Milestone |
|------|-------|---------------|
| 1-2 | Foundation | Goal tracking + action logging working |
| 3 | Cross-session learning | Pattern extraction + retrieval working |
| 4 | Adaptive abstraction | Multi-level patterns + user modeling |
| 5 | Evaluation | SWE-bench results + user study |
| 6 | Polish & write-up | Demo video + paper draft |

**Total timeline**: 6 weeks (end of quarter)  
**Checkpoint**: Week 3 (should have working cross-session learning to show progress)

---

## Conclusion

This project addresses a critical gap in coding agent capabilities: the inability to learn from experience and maintain focus on user goals. By combining goal-aware tracking, cross-session pattern learning, and dynamic abstraction adjustment, we create a system that gets smarter over time and adapts to different users and contexts.

The project is ambitious but achievable within the 6-week timeframe, with clear milestones and measurable success criteria. It balances scientific contribution (dynamic abstraction), engineering rigor (SWE-bench evaluation), and practical impact (real user testing).

Most importantly, this directly addresses Prof. Yucheng's research direction on agent memory with decontextualization, while differentiating from other groups by focusing on the tractable domain of coding and introducing the novel dimension of goal tracking.

I'm excited to pursue this direction and believe it will result in both strong academic output and practical tools that benefit the developer community.

---

**Contact**: Jeremy Gu | jeremy.gu@sagesure.com  
**Code repository**: [To be created]  
**Demo video**: [To be recorded Week 6]