# Trajectory Data Discovery & Next Steps
**Jeremy Gu | November 5, 2025**

---

## Key Finding: Public Trajectory Data Available

I found existing trajectory logs in my research data folder:
- **Location**: `/research-data/20250928_trae_doubao_seed_code/trajs/`
- **Format**: JSON files, one per SWE-bench task
- **Example**: `sympy__sympy-23534.json` (28K tokens, 41 messages)

---

## Trajectory Structure Analysis

**Sample trajectory `sympy__sympy-23534.json`:**

```json
{
  "total_messages": 41,
  "roles": {
    "system": 1,    // Agent instructions
    "user": 20,     // Task description + execution results
    "assistant": 20 // Agent reasoning + actions
  },
  "task": "sympy__sympy-23534",
  "issue": "Fix symbols() with tuple + cls parameter",
  "final_status": "resolved"
}
```

**Action sequence extracted:**
1. Explore codebase (`find`, `grep`)
2. Read relevant files (`view symbol.py`)
3. Create test script (`create test.py`)
4. Run tests (`execute_bash`)
5. Fix code (`str_replace`)
6. Verify fix → Success

---

## How This Enables Q1 Development (Zero API Cost)

### Week 1-2: Drift Detection Algorithm

**Input**: Existing trajectories (no LLM calls needed)

**Process**:
```python
# 1. Parse trajectory
trajectory = json.load(open("sympy__sympy-23534.json"))

# 2. Extract actions
actions = extract_assistant_actions(trajectory)
# → ['execute_bash(find)', 'view(symbol.py)', 'str_replace(...)', ...]

# 3. Detect drift (local computation, $0 cost)
scope_drift = compute_BV_score(actions, authorized_scope)
tool_drift = compute_trajectory_EM(actions, reference_tools)
loop_drift = compute_EPR(actions, error_history)

# 4. Manual annotation for ground truth
human_labels = annotate_each_step(trajectory)
# → step_3: no_drift, step_8: no_drift, ...

# 5. Validate detection accuracy
accuracy = compare(detected_drift, human_labels)
```

**Cost**: $0 (vs. $2,500 to re-run 500 agents)

---

## Practical Questions for Yucheng

### 1. Trajectory Data Sources
- **Q**: Are there official SWE-bench trajectories available?
  - GitHub releases?
  - Supplementary materials from papers?
- **Q**: Other research systems with public logs?
  - AutoCodeRover trajectories?
  - SWE-agent execution logs?
- **Q**: τ-bench / WebArena trajectory availability?

### 2. Format Normalization
- **Q**: Do different systems use different formats?
  - OpenHands format (like my example)
  - SWE-bench native format
  - Other agent frameworks
- **Q**: How much effort to normalize across formats?

### 3. Budget & Scope
- **Q**: If public trajectories unavailable, suggested budget?
  - Run 10-20 tasks for algorithm development?
  - Run 50 tasks for validation?
  - Estimated cost: ~$50-500 depending on subset size
- **Q**: Any CS224V shared resources?
  - Pre-run trajectories from course?
  - GPU/AWS credits available?

### 4. Validation Strategy
- **Q**: How many trajectories needed for credible validation?
  - Manual annotation: 3 trajectories (your Week 1-2 plan)
  - Initial validation: 10-20 trajectories
  - Full evaluation: 50+ or rely on existing logs?

---

## Proposed Next Steps

### This Week (Nov 5-12)
1. **Survey trajectory sources** (P0):
   - Check SWE-bench repo for official trajectories
   - Contact authors if needed
   - Explore τ-bench/WebArena data availability

2. **Format analysis** (P1):
   - Document trajectory schema from found sources
   - Write parser to normalize different formats
   - Test on 2-3 examples from different systems

3. **Pilot detection** (P1):
   - Implement basic drift detectors on 1 trajectory
   - Manually annotate that 1 trajectory as ground truth
   - Compute detection accuracy (proof of concept)

### Week 2 Deliverable
- **Trajectory Inventory Report**:
  - List of available sources + formats
  - Normalization code (if needed)
  - 1 annotated case study with detection results

---

## Risk Mitigation

**If public trajectories are unavailable or insufficient:**

**Plan B**: Run small-scale experiments
- Budget: $100-200 for 20-40 tasks
- Focus: Develop + validate algorithm on this subset
- Demonstrate concept before scaling to 500 tasks

**Plan C**: Focus on single benchmark
- Deep dive on SWE-bench only (defer τ-bench/WebArena to future work)
- Use whatever trajectories are available for that benchmark
- Still demonstrates Q1 value: in-session drift detection

---

## Key Takeaway

Having existing trajectory data means:
- ✅ **Zero-cost algorithm development** (no API calls)
- ✅ **Faster iteration** (hours vs. days)
- ✅ **Reproducible research** (same data for comparison)
- ✅ **Focus on innovation** (time on detection logic, not data collection)

**This aligns perfectly with your advice**: *"Prefer existing trajectories over re-running agents (cost/time)."*

---

## Discussion Topics for Today's Meeting

1. Do you know of any public trajectory sources I should check first?
2. What trajectory format should I prioritize (if multiple exist)?
3. What's the minimum number of trajectories needed to validate Q1 detection?
4. Should I normalize formats now, or focus on single-format first?
