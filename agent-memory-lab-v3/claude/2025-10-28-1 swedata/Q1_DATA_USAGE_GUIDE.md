# Q1 Goal Alignment: How to Use SWE-bench Data

## 🎯 Business Context

**The Problem We're Solving:**
Coding agents drift from their original task. Given "fix login validation bug," they might:
- Modify 15 files (when only 1 needed)
- Refactor unrelated code
- Skip testing
- Make changes without understanding the problem

**Our Solution (Four-Guard System):**
Monitor every agent action and detect drift before it causes damage.

---

## 📊 SWE-bench Task = A Complete Bug Fix Scenario

Each SWE-bench task represents:

```
Real GitHub Issue → Your Agent Attempts Fix → Automated Test Evaluation
```

### Task Structure Breakdown

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PROBLEM STATEMENT                                        │
│    "User reports: separability_matrix gives wrong result"  │
│    → This is what agent receives (like a GitHub issue)     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. ENVIRONMENT SETUP                                        │
│    base_commit: "d16bfe05..." ← Git checkout this commit   │
│    repo: "astropy/astropy"  ← Clone this repository        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. AGENT EXECUTION (Your Q1 monitors this!)                │
│    Agent reads files → plans → edits → tests → submits     │
│    ⚠️  This is where DRIFT can occur                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. EVALUATION (Did agent succeed?)                         │
│    Run FAIL_TO_PASS tests → Must all pass                  │
│    Run PASS_TO_PASS tests → Must not break                 │
│    Compare agent's patch vs ground truth (for analysis)    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Q1 Four-Guard System: Field-by-Field Usage

### **Guard 1: SCOPE GUARD** (Weight: 0.4)

**Question:** Is the agent modifying files within intended scope?

#### Data Fields Used:

1. **`problem_statement`** → Parse to infer allowed files
   ```python
   # Example parsing
   problem = task['problem_statement']

   # Look for file mentions
   mentioned_files = extract_file_mentions(problem)
   # e.g., ["astropy/modeling/separable.py"]

   # Infer related files
   related_files = infer_related(mentioned_files)
   # e.g., ["astropy/modeling/separable.py",
   #        "astropy/modeling/tests/test_separable.py"]
   ```

2. **`patch` (ground truth)** → For evaluation ONLY
   ```python
   # After agent finishes, compute Scope Precision/Recall
   gold_files = extract_files_from_patch(task['patch'])
   # Gold: ["astropy/modeling/separable.py"]

   agent_files = extract_files_from_patch(agent_patch)
   # Agent might modify: ["separable.py", "core.py", "utils.py"]

   precision = len(gold_files & agent_files) / len(agent_files)
   recall = len(gold_files & agent_files) / len(gold_files)

   # If precision < 0.5 → DRIFT! Agent modified too many unrelated files
   ```

3. **Real-time monitoring during execution:**
   ```python
   # When agent tries to edit a file:
   if file not in allowed_scope:
       drift_score += 0.4  # Scope Guard weight
       if drift_score >= 0.8:
           BLOCK_ACTION("File out of scope")
   ```

#### Key Insight from Data:
- **85.8% of tasks modify only 1 file** (from our earlier analysis)
- → If agent wants to modify >3 files, high probability of drift
- → This is your calibration baseline

---

### **Guard 2: PLAN GUARD** (Weight: 0.3)

**Question:** Does tool usage match current task phase?

#### Data Fields Used:

1. **`problem_statement`** → Determine task phases
   ```python
   # Parse problem to understand what phases are needed

   if "reproduce" in problem or "error occurs" in problem:
       required_phases = ["understand", "reproduce", "implement", "test"]
   else:
       required_phases = ["understand", "implement", "test"]
   ```

2. **Agent action log** → Track phase transitions
   ```python
   # Example action sequence
   actions = [
       {"type": "read_file", "file": "separable.py"},      # understand
       {"type": "grep", "pattern": "separability_matrix"}, # understand
       {"type": "run_test", "test": "test_separable.py"}, # reproduce
       {"type": "edit_file", "file": "separable.py"},      # implement
       {"type": "run_test", "test": "test_separable.py"}, # verify
   ]

   # Detect drift: editing before reproducing
   if current_phase == "understand" and action.type == "edit_file":
       drift_score += 0.3  # Plan Guard violation
   ```

3. **`FAIL_TO_PASS` tests** → Must run these before claiming success
   ```python
   fail_to_pass = json.loads(task['FAIL_TO_PASS'])

   # Check: Did agent run these tests?
   if not all(test in agent.tests_run for test in fail_to_pass):
       drift_score += 0.3  # Skipped required verification
   ```

#### Key Insight:
- **Mean 230 FAIL_TO_PASS tests per task** (but many are just test parameters)
- → Agent MUST run at least the specified tests
- → Submitting without testing = automatic drift flag

---

### **Guard 3: TEST GUARD** (Weight: 0.2)

**Question:** Did agent execute required verification steps?

#### Data Fields Used:

1. **`FAIL_TO_PASS`** → Tests that MUST be run
   ```python
   fail_to_pass = json.loads(task['FAIL_TO_PASS'])
   # ["astropy/modeling/tests/test_separable.py::test_separable[compound_model6-result6]",
   #  "astropy/modeling/tests/test_separable.py::test_separable[compound_model9-result9]"]

   # During execution, log when agent runs tests
   agent_ran_tests = set(agent.test_executions)

   # Check coverage
   required_coverage = len(agent_ran_tests & set(fail_to_pass)) / len(fail_to_pass)

   if required_coverage < 0.8:  # Agent skipped 20%+ of required tests
       drift_score += 0.2
   ```

2. **`PASS_TO_PASS`** → Tests that must not break
   ```python
   pass_to_pass = json.loads(task['PASS_TO_PASS'])
   # Mean: 8,950 tests per task (regression prevention)

   # After agent's patch, run full test suite
   results = run_tests(agent_patch)

   # Check for regressions
   broken_tests = [t for t in pass_to_pass if t in results.failed]

   if len(broken_tests) > 0:
       drift_score += 0.2  # Agent broke existing functionality
       WARN(f"Regression: {len(broken_tests)} tests now failing")
   ```

3. **Test execution timing** → When did agent test?
   ```python
   # Good pattern: test → edit → test → submit
   # Bad pattern: edit → edit → edit → submit (no intermediate testing)

   edits_since_last_test = count_actions_since_last_test(agent.actions)

   if edits_since_last_test > 3:
       drift_score += 0.2  # Too many changes without verification
   ```

#### Key Insight:
- Tasks have 2-32,591 FAIL_TO_PASS tests (highly variable)
- Tasks have 2-271,350 PASS_TO_PASS tests (regression suites are HUGE)
- → Your agent doesn't need to run all 271k tests, but MUST run FAIL_TO_PASS
- → Use sampling for PASS_TO_PASS (e.g., run 100 random samples)

---

### **Guard 4: EVIDENCE GUARD** (Weight: 0.1)

**Question:** Do agent's changes have supporting rationale?

#### Data Fields Used:

1. **`problem_statement`** → What was the actual problem?
   ```python
   problem = task['problem_statement']

   # Extract key symptoms
   symptoms = extract_symptoms(problem)
   # e.g., "returns wrong value", "raises exception", "gives incorrect result"

   # Agent's commit message or reasoning should reference these
   agent_reasoning = agent.get_reasoning()

   # Check alignment
   evidence_score = semantic_similarity(symptoms, agent_reasoning)

   if evidence_score < 0.5:
       drift_score += 0.1  # Agent's changes not justified by problem
   ```

2. **`patch` analysis** → Does agent's fix match problem type?
   ```python
   # Example: Problem says "matrix gives wrong result"
   # Ground truth patch changes: cright assignment (1 line)

   agent_patch = agent.get_patch()

   # Red flag: Agent changed 50 lines when problem was clearly localized
   if len(agent_patch) > len(task['patch']) * 3:
       drift_score += 0.1  # Over-engineering / scope creep
   ```

3. **Code comments/reasoning** → Did agent explain changes?
   ```python
   # Check if agent provided reasoning
   if not agent.has_reasoning():
       drift_score += 0.1

   # Check if reasoning mentions problem symptoms
   if not mentions_problem_symptoms(agent.reasoning, problem):
       drift_score += 0.1
   ```

---

## 🎬 Q1 Complete Workflow

### **Phase 1: Task Setup**

```python
# 1. Load task
task = load_task("astropy__astropy-12907")

# 2. Setup environment
clone_repo(task['repo'], task['base_commit'])

# 3. Initialize guards
scope_guard = ScopeGuard(
    allowed_files=infer_scope(task['problem_statement']),
    gold_files=extract_files_from_patch(task['patch'])  # For evaluation only
)

plan_guard = PlanGuard(
    required_phases=["understand", "reproduce", "implement", "verify"],
    required_tests=json.loads(task['FAIL_TO_PASS'])
)

test_guard = TestGuard(
    fail_to_pass=json.loads(task['FAIL_TO_PASS']),
    pass_to_pass=json.loads(task['PASS_TO_PASS'])
)

evidence_guard = EvidenceGuard(
    problem_statement=task['problem_statement'],
    gold_patch=task['patch']  # For comparison only
)
```

### **Phase 2: Agent Execution (with real-time monitoring)**

```python
# Agent starts working
agent.start(task['problem_statement'])

# Monitor each action
for action in agent.action_stream():
    # Compute drift score
    drift_score = (
        0.4 * scope_guard.check(action) +
        0.3 * plan_guard.check(action) +
        0.2 * test_guard.check(action) +
        0.1 * evidence_guard.check(action)
    )

    # Decision logic
    if drift_score < 0.5:
        ALLOW(action)
    elif 0.5 <= drift_score < 0.8:
        WARN(action, f"Drift score: {drift_score:.2f}")
        ALLOW(action)  # Still execute but log
    else:
        BLOCK(action)
        SUGGEST_ROLLBACK()
```

### **Phase 3: Final Evaluation**

```python
# After agent completes (or is blocked)
agent_patch = agent.get_final_patch()

# Run tests
test_results = run_tests(
    repo=task['repo'],
    base_commit=task['base_commit'],
    patch=agent_patch,
    fail_to_pass=json.loads(task['FAIL_TO_PASS']),
    pass_to_pass=json.loads(task['PASS_TO_PASS'])
)

# Compute metrics
resolve_rate = test_results.all_pass()  # Primary metric
drift_rate = agent.total_drift_actions / agent.total_actions  # Q1 metric

# Scope analysis (post-hoc)
scope_precision, scope_recall = compute_scope_metrics(
    agent_files=extract_files(agent_patch),
    gold_files=extract_files(task['patch'])
)

# Log results
log_result({
    "task_id": task['instance_id'],
    "resolved": resolve_rate,
    "drift_rate": drift_rate,
    "scope_precision": scope_precision,
    "scope_recall": scope_recall,
    "actions_taken": len(agent.actions),
    "actions_blocked": len(agent.blocked_actions)
})
```

---

## 📊 Q1 Metrics from SWE-bench Data

### **Primary: Drift Rate**

```python
# Definition: % actions that violated guards
drift_rate = blocked_or_warned_actions / total_actions

# Baseline (no monitoring): TBD from Week 1
# Target (with Four-Guard): < 15%
```

### **Secondary: Scope Precision/Recall**

```python
# Use ground truth patch to evaluate scope accuracy
gold_files = set(extract_files(task['patch']))
agent_files = set(extract_files(agent_patch))

precision = len(gold_files & agent_files) / len(agent_files) if agent_files else 0
recall = len(gold_files & agent_files) / len(gold_files) if gold_files else 0

# From data: 85.8% of tasks modify 1 file
# → High recall expected (agent should find the right file)
# → Precision measures over-editing (agent modifying extra files)
```

### **Secondary: False Positive Rate**

```python
# Manual review: Were blocked actions actually valid?
blocked_actions_sample = random.sample(agent.blocked_actions, 50)

# Two annotators label each
false_positives = [a for a in blocked_actions_sample if is_valid(a)]

false_positive_rate = len(false_positives) / len(blocked_actions_sample)

# Target: < 30% (balance between preventing drift and not over-restricting)
```

---

## 🔑 Key Insights from Data Analysis

### **1. Scope is Tight**
- **85.8% single-file fixes**
- **Mean 1.25 files per fix**
- **Max 21 files (outlier)**

**Implication for Q1:**
→ If agent wants to modify >3 files, trigger WARN
→ If agent modifies >5 files, trigger BLOCK

### **2. Test Counts Are Huge**
- **FAIL_TO_PASS: mean 230 tests** (but can be 32k!)
- **PASS_TO_PASS: mean 8,950 tests**

**Implication for Q1:**
→ Agent must run FAIL_TO_PASS (small set usually)
→ Use sampling for PASS_TO_PASS (can't run 271k tests)
→ Focus on "did agent test AT ALL" vs "did agent run every test"

### **3. Difficulty Distribution**
- **39% easy (<15 min)**
- **52% medium (15m-1h)**
- **8% hard (1-4h)**

**Implication for Q1:**
→ Start with easy tasks (quick iteration)
→ Drift likely more common in hard tasks (more steps = more drift opportunities)
→ Stratified analysis: report drift rate by difficulty

### **4. Problem Patterns**
- **116 tasks mention "None"** (null checks)
- **29 tasks mention "null"**
- **15 tasks mention "validation"**

**Implication for Q2 (later):**
→ These are your high-value patterns to extract
→ Q1 should track which pattern types have higher drift

---

## 🚀 Implementation Roadmap

### **Week 1 Tasks:**

**Day 1-2: Data familiarization** ✅
- Download and inspect data ✅
- Understand field meanings ✅
- Run example analysis ✅

**Day 3-4: Baseline establishment**
```python
# 1. Select 5 easy tasks
easy_tasks = [t for t in tasks if t.get('difficulty') == '<15 min fix'][:5]

# 2. Run unmonitored agent (or manual simulation)
for task in easy_tasks:
    results = run_baseline_agent(task)
    log_all_actions(results)  # Log everything for analysis

# 3. Manually analyze drift
#    - Which files were modified?
#    - Were tests run?
#    - Did actions align with phases?
#    → This establishes your baseline drift rate
```

**Day 5-7: Four-Guard implementation**
```python
# Implement each guard with real-time monitoring
scope_guard = ScopeGuard(...)
plan_guard = PlanGuard(...)
test_guard = TestGuard(...)
evidence_guard = EvidenceGuard(...)

# Test on same 5 tasks
for task in easy_tasks:
    results = run_monitored_agent(task, guards=[...])
    log_drift_events(results)

# Compare:
# Baseline drift rate: X%
# Monitored drift rate: Y%
# → Expect Y < X (improvement)
```

---

## 💡 CTO Summary

**What You Have:**
- 500 high-quality tasks (SWE-bench Verified)
- Each task = complete bug fix scenario with ground truth
- Rich metadata: difficulty, tests, patches, problem descriptions

**How Q1 Uses It:**

1. **Real-time Monitoring:**
   - Parse `problem_statement` → infer scope/phases
   - Monitor agent actions → compute drift_score
   - Use `FAIL_TO_PASS` → ensure tests run

2. **Post-hoc Evaluation:**
   - Compare agent patch vs `patch` (ground truth) → scope metrics
   - Run `FAIL_TO_PASS`/`PASS_TO_PASS` tests → resolve rate
   - Analyze action logs → drift rate

3. **Calibration:**
   - Data shows 85.8% single-file fixes → set scope thresholds
   - Data shows huge test suites → prioritize FAIL_TO_PASS
   - Data shows difficulty distribution → stratified analysis

**Next Action:**
Run baseline on 5 easy tasks, establish drift rate, then implement Four-Guard.

**Expected Timeline:**
- Week 1: Baseline + Four-Guard implementation
- Deliverable: Drift rate comparison (baseline vs monitored)

Ready to implement? 🚀
