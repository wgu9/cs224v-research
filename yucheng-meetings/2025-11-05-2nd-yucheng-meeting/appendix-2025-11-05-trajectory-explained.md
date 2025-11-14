# Understanding Trajectories: Why They Save Resources
**Complete Explanation | November 5, 2025**

---

## What is a Trajectory?

**Trajectory = Complete behavioral log of an agent executing a task**

### A complete trajectory contains:
```json
{
  "task_id": "django__django-12345",
  "problem": "Fix null pointer in payment validation",
  "trajectory": [
    {
      "step": 1,
      "action": "read_file",
      "args": {"path": "payment_processor.py"},
      "result": "[file content...]",
      "timestamp": "2024-10-15T10:00:00"
    },
    {
      "step": 2,
      "action": "search",
      "args": {"pattern": "null pointer"},
      "result": "[search results...]",
      "timestamp": "2024-10-15T10:00:15"
    },
    {
      "step": 3,
      "action": "edit_file",
      "args": {"path": "payment_processor.py", "old": "...", "new": "..."},
      "result": "success",
      "timestamp": "2024-10-15T10:01:30"
    },
    {
      "step": 4,
      "action": "run_test",
      "args": {"test": "test_payment"},
      "result": "failed: AssertionError...",
      "timestamp": "2024-10-15T10:02:00"
    },
    {
      "step": 5,
      "action": "edit_file",
      "args": {"path": "database_config.py", "old": "...", "new": "..."},
      "result": "success",
      "timestamp": "2024-10-15T10:03:00"
    }
  ],
  "final_result": "resolved/failed",
  "total_cost": "$3.50",
  "total_time": "8 minutes"
}
```

---

## Two Approaches: Cost Comparison

### Approach A: Re-run Agents (Expensive)

**Workflow**:
```
Your code → Call LLM API → Agent executes → Generate trajectory → Analyze drift
```

**Cost breakdown**:
- **API calls**: 50-100 calls to Claude Sonnet per task
- **Cost per task**: $2-10
- **500 tasks total cost**: $1,000-5,000
- **Time**: 3-7 days (API rate limits + compute time)

**Example code**:
```python
# You need to run this 500 times
for task in swe_bench_verified:
    agent = ClaudeAgent()  # Calls Bedrock API every time
    trajectory = agent.solve(task)  # Expensive!
    drift_score = analyze_drift(trajectory)
```

---

### Approach B: Use Existing Trajectories (Free)

**Workflow**:
```
Download public trajectories → Analyze drift directly (no LLM calls)
```

**Cost breakdown**:
- **API calls**: 0 (trajectories already exist)
- **Total cost**: $0 (or minimal storage/compute)
- **Time**: A few hours (download + local analysis)

**Example code**:
```python
# Just analyze existing data
trajectories = download_from_s3("swe-bench-trajectories/")  # Free
for trajectory in trajectories:
    # Local computation, no API calls
    drift_score = analyze_drift(trajectory)
```

---

## Why Do Public Trajectories Exist?

Many research teams (SWE-bench authors, AutoCodeRover team, etc.) have already spent significant resources running agents and publicly released their trajectories:

### Known Public Trajectory Sources:
1. **SWE-bench Official**:
   - May have baseline trajectories
   - Check: `https://github.com/princeton-nlp/SWE-bench` or AWS S3 buckets

2. **AutoCodeRover**:
   - Paper mentions trajectories
   - Check: GitHub repo releases or supplementary materials

3. **Other Research Systems**:
   - SWE-agent, Aider, Mentat may have published execution logs

---

## How to Use Trajectories in Your Research?

### Week 1-2: Develop Drift Detection Algorithm

**Input**: 3 existing trajectories (1 success + 1 failure + 1 partial)

**Workflow**:
```
1. Download trajectory.json

2. Manual annotation for each action:
   - Step 1: no_drift
   - Step 2: no_drift
   - Step 3: no_drift
   - Step 4: tool_drift (wrong test selected)
   - Step 5: scope_drift (edited unrelated file)
   - Step 6: loop_drift (repeated failed action)

3. Implement detection algorithms:
   - compute_BV_score(trajectory) → 0.4
   - compute_EPR(trajectory) → 0.25
   - compute_EM(trajectory) → 0.6

4. Validate accuracy:
   - Your algorithm's detection vs. manual annotation
   - Accuracy: 85%? 90%?
```

**Key point**: The entire process requires NO LLM API calls!

---

### Week 3-5: Large-Scale Evaluation

**If 500 public trajectories are available**:
```python
# $0 cost, completed in a few hours
results = []
for traj in all_500_trajectories:
    drift_scores = {
        'scope': compute_BV(traj),
        'tool': compute_EM(traj),
        'loop': compute_EPR(traj)
    }
    results.append(drift_scores)

# Analysis:
# - How many tasks have high drift?
# - Correlation between drift and success rate?
# - Which dimension is most critical?
```

**If public trajectories are NOT available**:
```python
# Need to spend $1000-5000, 3-7 days
for task in swe_bench_verified:
    traj = expensive_api_call(task)  # $$$
    drift_scores = compute_drift(traj)
```

---

## When Do You NEED to Re-run Agents?

### Situation 1: Verify Resolve Rate
- Trajectories may only log actions, not final test results
- Need Docker + Evaluator to confirm task is actually solved

### Situation 2: Test Intervention Mechanisms
- You want to test if "rollback on drift detection" improves success rate
- Need to run: agent with intervention vs. agent without intervention

### Situation 3: No Public Trajectories for Benchmark
- If τ-bench or WebArena don't have public trajectories
- Must run yourself (but can test with small subset first)

---

## Yucheng's Advice Summary

### Priority ordering:
1. **First**: Find existing trajectories → Develop detection algorithm → Validate feasibility (Week 1-2)
2. **Then**: If effective, consider small-scale re-runs to test intervention (Week 3-4)
3. **Finally**: Large-scale evaluation (use trajectories if available; run small subset if not)

### Cost control strategy:
- ✅ Use public trajectories for algorithm development
- ✅ Use small subset (50 tasks) for initial validation
- ⚠️ Only run full 500 tasks when necessary
- ❌ Don't start with large-scale agent runs

---

## Action Items This Week

### Immediate investigation (P0):
1. Check if SWE-bench has public trajectories
   - GitHub repo releases
   - Paper supplementary materials
   - Contact authors

2. Check τ-bench trajectory availability
   - Paper GitHub repo
   - Leaderboard submissions

3. Check other research systems' public logs
   - AutoCodeRover
   - SWE-agent
   - Aider

### If No Public Trajectories Found?
- **Plan B**: Run small subset yourself (10-20 tasks) to develop algorithm
- **Budget control**: $20-200 budget for initial development
- **Proof of concept**: Scale up only after demonstrating feasibility

---

## Analogy for Understanding

### Analogy 1: Traffic Flow Research
- **Approach A**: Have 1000 cars drive the highway again, record GPS data (expensive)
- **Approach B**: Use traffic department's existing GPS historical data to analyze congestion patterns (free)

### Analogy 2: Medical Research
- **Approach A**: Recruit 500 patients for new clinical trials (expensive + time-consuming)
- **Approach B**: Analyze existing electronic medical records (fast + low cost)

### Your Context Drift Detection Research:
- **Approach A**: Run 500 agents to generate new trajectories
- **Approach B**: Analyze existing agent execution logs

---

## Key Questions to Ask Yucheng Today

1. Do you know any public trajectory sources?
2. If unavailable, what budget do you suggest for running a small subset?
3. Trajectory formats may vary - how much normalization effort is expected?
4. Are there Stanford/CS224V shared resources (GPU credits, pre-run trajectories)?

---

## Example: Real Trajectory Analysis

**File**: `sympy__sympy-23534.json` (found in my research data)

**Basic info**:
- Total messages: 41
- Roles: 1 system, 20 user, 20 assistant
- Task: Fix sympy `symbols()` bug with tuple + cls parameter
- Final status: Resolved

**Action sequence**:
1. Explore codebase (`find`, `grep`)
2. Read files (`view symbol.py`)
3. Create test (`create test_wild.py`)
4. Run test (`execute_bash`)
5. Fix code (`str_replace`)
6. Verify fix → Success

**Drift analysis** (can be done locally, $0 cost):
```python
# Scope Drift
authorized_files = ["/testbed/sympy/core/symbol.py"]
edited_files = extract_edited_files(trajectory)
bv_score = violations / total_edits
# Result: 0.0 (no scope drift - agent stayed in correct file)

# Loop Drift
repeated_actions = find_repetitions(trajectory)
# Result: 0 (no repetitive failures)

# Tool Drift
optimal_sequence = ["grep", "view", "str_replace", "test"]
actual_sequence = extract_tools(trajectory)
em_score = sequence_match(optimal, actual)
# Result: 1.0 (perfect match)

# Conclusion: This is a CLEAN trajectory with no drift
# Final CDI (Context Drift Index): 0.0
```

---

## Summary

**Your understanding is absolutely correct!**

Trajectories enable you to:

✅ **Free algorithm development** - No LLM API calls needed
✅ **Fast iteration** - Hours vs. days
✅ **Reproducible research** - Same data for comparing different algorithms
✅ **Focus on innovation** - Time spent on drift detection logic, not data collection

**Yucheng's advice in one sentence**: *"Use existing trajectory data to prove your detection method works first, then consider large-scale experiments."*
