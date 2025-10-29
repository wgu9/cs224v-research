# Research Phase: Context Drift Detection

**Phase**: Week 1 (Oct 29 - Nov 5)
**Goal**: Establish theoretical foundation for Context Drift detection
**Type**: Research & Writing (NO CODING YET!)

---

## 📋 Overview

This research phase focuses on:
1. Understanding existing work on context drift
2. Formally defining Context Drift
3. Identifying detection dimensions
4. Understanding how drift manifests in different benchmarks

**Important**: Yucheng emphasized: "**This is foundation of your paper**" - must be solid before any implementation!

---

## 🎯 Deliverables

### 1. Literature Survey (`literature_survey.md`)
- **Timeline**: Day 1-2 (Oct 29-30)
- **Goal**: Survey 5-10 papers on context/goal/task drift
- **Output**: Synthesis of definitions, dimensions, and gaps
- **Review**: Send to Yucheng on Day 2

### 2. Formal Definition (`context_drift_definition.md`)
- **Timeline**: Day 3-4 (Oct 31 - Nov 1)
- **Goal**: Define Context Drift and all dimensions
- **Output**: Formal definition + justified dimensions
- **Review**: Send to Yucheng on Day 4

### 3. Benchmark Comparison (`benchmark_comparison.md`)
- **Timeline**: Day 5-7 (Nov 2-5)
- **Goal**: Understand 3 benchmarks and how drift manifests
- **Output**: Comparison table + trajectory sources
- **Review**: Send to Yucheng on Day 7

---

## 📚 Document Status

| Document | Status | Last Updated | Ready for Review |
|----------|--------|--------------|------------------|
| `literature_survey.md` | 📝 Template created | Oct 29 | ❌ Not yet |
| `context_drift_definition.md` | 📝 Template created | Oct 29 | ❌ Not yet |
| `benchmark_comparison.md` | 📝 Template created | Oct 29 | ❌ Not yet |

---

## 🔍 Research Resources

### Required Papers (Yucheng Recommended)
1. **Agent Trajectory Dataset**: https://arxiv.org/pdf/2505.02820
2. **Auto-Metrics Paper**: https://arxiv.org/pdf/2504.07971
3. **Model Cards Paper**: (PDF from Yucheng)

### Benchmarks to Study
1. **SWE-bench**: https://www.swebench.com/
   - We have experience with this
   - Trajectories: https://github.com/SWE-bench/experiments

2. **Tau Bench**: https://taubench.com/
   - NEW - need to research
   - Leaderboard: https://taubench.com/#leaderboard
   - Yucheng: "Repetitive mistakes especially evident"

3. **Web Arena**: (Need to find URL)
   - NEW - need to research
   - Yucheng: "Repetitive mistakes especially evident"

### Search Keywords
- "context drift" agent
- "goal drift"
- "task drift"
- "off-policy" agent behavior
- agent trajectory evaluation
- long-horizon agent tasks
- repetitive mistakes in agents

---

## ✅ Week 1 Daily Plan

### Day 1-2 (Oct 29-30): Literature Survey

**Morning (Oct 29)**:
1. ✅ Send confirmation email to Yucheng
2. 📚 Read Agent Trajectory Dataset paper
3. 📚 Read Auto-Metrics paper
4. 📚 Read Model Cards paper

**Afternoon**:
5. 🔍 Search Google Scholar for 5-10 additional papers
6. 📝 Fill in `literature_survey.md` template

**Day 2 Morning**:
7. 📝 Complete synthesis section
8. 📝 Identify research gaps
9. ✉️ Send to Yucheng for review on Slack

---

### Day 3-4 (Oct 31 - Nov 1): Formal Definition

**Day 3**:
1. 📝 Write formal definition based on literature
2. 📝 Define all dimensions with justifications
3. 📝 Add examples for each dimension

**Day 4**:
4. 📝 Refine definition
5. 📝 Ensure all dimensions are justified from literature
6. ✉️ Send to Yucheng for review on Slack

---

### Day 5-7 (Nov 2-5): Benchmark Research

**Day 5 - Tau Bench**:
1. 🔍 Visit https://taubench.com/
2. 📚 Read documentation
3. 📚 Explore task examples
4. 📝 Fill in Tau Bench section

**Day 6 - Web Arena**:
5. 🔍 Search for Web Arena
6. 📚 Read documentation
7. 📚 Explore task examples
8. 📝 Fill in Web Arena section

**Day 7 - Synthesis**:
9. 📝 Complete comparison table
10. 📝 Document trajectory sources
11. ✉️ Send to Yucheng for review on Slack

---

## 🚨 Important Reminders

### DO:
- ✅ Read papers thoroughly
- ✅ Justify every dimension from literature
- ✅ Send for review at each step (don't wait!)
- ✅ Take notes on trajectory availability
- ✅ Focus on understanding, not implementing

### DON'T:
- ❌ Start coding yet!
- ❌ Run expensive experiments
- ❌ Work on Q2 (cross-session memory)
- ❌ Wait until everything is perfect to send for review

---

## 📬 Communication with Yucheng

### Review Points
Send updates on Slack at these milestones:
1. **Day 2 (Oct 30)**: Literature survey complete
2. **Day 4 (Nov 1)**: Formal definition complete
3. **Day 7 (Nov 5)**: Benchmark comparison complete

### Email Template
```
Subject: [Q1 Research] [Milestone] - Ready for Review

Hi Yucheng,

I've completed [milestone name]. Key findings:

1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

Attached: [document name]

Questions:
1. [Question if any]

Could you review and let me know if I should proceed to [next step]?

Best,
Jeremy
```

---

## 📊 Success Criteria

### Literature Survey
- [ ] Read 3 required papers
- [ ] Find 5-10 additional papers
- [ ] Synthesize definitions of drift
- [ ] Identify all proposed dimensions
- [ ] Identify research gaps
- [ ] Yucheng approved ✅

### Formal Definition
- [ ] Clear formal definition written
- [ ] All dimensions defined
- [ ] All dimensions justified from literature (not arbitrary!)
- [ ] Examples provided
- [ ] Yucheng approved ✅

### Benchmark Comparison
- [ ] SWE-bench section complete
- [ ] Tau Bench researched
- [ ] Web Arena researched
- [ ] Comparison table complete
- [ ] Trajectory sources identified
- [ ] Yucheng approved ✅

---

## 🔄 Next Phase Preview

After Week 1 research is approved by Yucheng:

**Week 2** (Nov 6-12): Framework Design
- Create Detection Cards for each dimension
- Download trajectories from all 3 benchmarks
- Design detection algorithms (pseudocode only)
- Still minimal coding!

**Week 3** (Nov 13-19): Implementation
- THIS is when coding starts
- Refactor existing Four Guards code
- Implement new dimensions (Repetitive Mistakes)
- Create benchmark adapters

**Week 4** (Nov 20-26): Evaluation
- Run detection on trajectories
- Manual validation
- Agreement analysis
- Paper draft

---

## 📝 Notes & Insights

### Key Insights from Yucheng Meeting

1. **Repetitive Mistakes** is a critical dimension
   - Yucheng emphasized twice: "especially evident in Web Arena and Tau Bench"
   - This is NEW - we didn't focus on this before
   - Need to understand how to detect and measure

2. **Use existing trajectories**
   - Don't run expensive experiments yet
   - SWE-bench has public trajectories on S3
   - Saves $1000-1500!

3. **Generalization is key**
   - Can't just work on SWE-bench
   - Must show framework works on 3+ benchmarks
   - This is what makes it a paper-worthy contribution

4. **Definition is foundation**
   - Yucheng: "This is foundation of your paper"
   - Must be solid before implementation
   - Each dimension needs justification

---

## 🎓 Learning Resources

### Understanding Model Cards
- Read the Model Cards paper Yucheng provided
- Each dimension needs:
  - Clear definition
  - Scope (when it applies)
  - How to measure
  - Why it matters
  - Justification (not arbitrary!)

### Understanding Trajectories
- Trajectory = sequence of agent actions
- Usually stored as JSON logs
- Contains: actions, observations, rewards, etc.
- We need to parse different trajectory formats

---

## 📅 Week 1 Schedule

```
Monday (Oct 29):
  Morning:  ✉️ Send email to Yucheng
           📚 Start reading papers
  Afternoon: 📚 Continue reading
           📝 Start filling literature_survey.md

Tuesday (Oct 30):
  Morning:  📝 Complete literature survey
  Afternoon: ✉️ Send to Yucheng for review
           📚 Start on definition

Wednesday (Oct 31):
  Morning:  📝 Write formal definition
  Afternoon: 📝 Define all dimensions

Thursday (Nov 1):
  Morning:  📝 Add examples and justifications
  Afternoon: ✉️ Send to Yucheng for review

Friday (Nov 2):
  Morning:  🔍 Research Tau Bench
  Afternoon: 📝 Fill in Tau Bench section

Weekend (Nov 3-4):
  Saturday:  🔍 Research Web Arena
  Sunday:    📝 Complete comparison table

Monday (Nov 5):
  Morning:  📝 Finalize benchmark comparison
  Afternoon: ✉️ Send to Yucheng for review
```

---

**Let's start with Day 1! Focus on reading papers and filling in the literature survey template.** 📚
