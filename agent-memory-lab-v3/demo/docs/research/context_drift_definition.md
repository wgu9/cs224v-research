# Context Drift: Formal Definition

**Date**: 2025-10-29
**Status**: To Be Written (After Literature Survey)
**Based on**: Literature survey findings

---

## Formal Definition

[TO BE FILLED - After completing literature survey]

**Context Drift** is defined as:

> [1-2 paragraph formal definition]

---

## Scope

Context drift applies to:
- Long-horizon agent tasks (>10 steps)
- Goal-oriented agents
- Sequential decision-making
- [Other scope criteria]

Context drift does NOT apply to:
- [Exclusions]

---

## Dimensions of Context Drift

Based on literature survey and Yucheng's feedback, we identify the following dimensions:

### 1. Wrong Scope ✅ (We have)

**Definition**:
[TO BE FILLED]

**Why it matters**:
- [Justification from literature]
- [Real-world impact]

**When it occurs**:
- [Scenarios]

**How we detect it**:
- [Detection method]

---

### 2. Repetitive Mistakes ⭐ (NEW - Yucheng emphasized)

**Definition**:
Agent repeats the same failed action multiple times within one session without learning or adapting.

**Why it matters**:
- Wastes computational resources
- Indicates lack of learning/adaptation
- Often leads to task failure
- Especially evident in Web Arena and Tau Bench (per Yucheng)

**When it occurs**:
- Agent tries same API call after failure
- Agent clicks same broken button repeatedly
- Agent re-applies same failed code patch

**How we detect it**:
- Track action history
- Compute action similarity (using embeddings)
- Count repetitions before success/failure
- Threshold: >3 repetitions = high drift

**Literature support**:
[TO BE FILLED - Papers that discuss repetitive errors]

---

### 3. Not Following Plan ✅ (We have)

**Definition**:
[TO BE FILLED]

**Why it matters**:
[TO BE FILLED]

**When it occurs**:
[TO BE FILLED]

**How we detect it**:
[TO BE FILLED]

**Literature support**:
[TO BE FILLED]

---

### 4. Irrelevant Tool Use (NEW)

**Definition**:
[TO BE FILLED - Based on Yucheng's mention]

**Why it matters**:
[TO BE FILLED]

**When it occurs**:
[TO BE FILLED]

**How we detect it**:
[TO BE FILLED]

**Literature support**:
[TO BE FILLED]

---

### 5. Lack of Evidence ✅ (We have)

**Definition**:
[TO BE FILLED]

**Why it matters**:
[TO BE FILLED]

**When it occurs**:
[TO BE FILLED]

**How we detect it**:
[TO BE FILLED]

**Literature support**:
[TO BE FILLED]

---

### 6. Test Coverage Issues ✅ (We have)

**Definition**:
[TO BE FILLED]

**Why it matters**:
[TO BE FILLED]

**When it occurs**:
[TO BE FILLED]

**How we detect it**:
[TO BE FILLED]

**Literature support**:
[TO BE FILLED]

---

### 7. [Other Dimensions from Literature]

[TO BE FILLED - Add dimensions found in literature survey]

---

## Justification for Each Dimension

**Why these dimensions and not others?**

[TO BE FILLED - Cannot be arbitrary! Must justify from literature]

1. **Wrong Scope**: [Justification]
2. **Repetitive Mistakes**: [Justification]
3. **Not Following Plan**: [Justification]
4. [etc.]

---

## Relationship to Related Concepts

### vs. Goal Drift
[TO BE FILLED - How is our "context drift" different from "goal drift"?]

### vs. Off-Policy Behavior
[TO BE FILLED - How does it relate to off-policy in RL?]

### vs. Task Deviation
[TO BE FILLED]

---

## Mapping to Prior Work

| Our Dimension | Related Work | Their Term |
|---------------|--------------|------------|
| Wrong Scope | [Paper] | [Their term] |
| Repetitive Mistakes | [Paper] | [Their term] |
| ... | ... | ... |

---

## Success Criteria

An agent trajectory is considered to have **high context drift** if:
1. [Criterion 1]
2. [Criterion 2]
3. [Criterion 3]

An agent trajectory is considered to have **low context drift** if:
1. [Criterion 1]
2. [Criterion 2]
3. [Criterion 3]

---

## Examples

### Example 1: High Drift (SWE-bench)

**Task**: Fix null pointer exception in payment processing

**Agent behavior**:
- Step 1: Modifies `payment.py` (correct)
- Step 2: Modifies `database.py` (wrong scope!)
- Step 3: Modifies `utils.py` (wrong scope!)
- Step 4: Tries to modify `payment.py` again with same patch (repetitive!)
- Step 5: Modifies `config.py` (wrong scope!)

**Drift scores**:
- Wrong Scope: 0.6 (3/5 files wrong)
- Repetitive Mistakes: 1.0 (repeated failed patch)
- Overall Drift: 0.8 (HIGH)

### Example 2: Low Drift (SWE-bench)

**Task**: Fix null pointer exception in payment processing

**Agent behavior**:
- Step 1: Analyzes error trace
- Step 2: Modifies `payment.py` with fix
- Step 3: Runs test to verify
- Step 4: Success

**Drift scores**:
- Wrong Scope: 0.0 (all files correct)
- Repetitive Mistakes: 0.0 (no repetitions)
- Overall Drift: 0.0 (LOW)

---

## Next Steps

After finalizing this definition:
1. Send to Yucheng for review
2. Create Detection Cards for each dimension
3. Implement detection algorithms
4. Validate on real trajectories

---

**Review Checklist**:
- [ ] All dimensions have clear definitions
- [ ] All dimensions have literature support
- [ ] All dimensions have justification (not arbitrary)
- [ ] Examples provided for each dimension
- [ ] Sent to Yucheng for review
