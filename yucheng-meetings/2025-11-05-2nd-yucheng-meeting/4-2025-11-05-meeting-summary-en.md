# Meeting Summary: Context Drift Detection
**Date**: November 5, 2025 | **Attendees**: Jeremy, Yucheng

---

## 🎯 Core Shift: Research Method Adjustment

### ❌ Old Approach (Rejected)
- Rule-based detection (hard-coded rules)
- Direct analysis of raw trajectory content
- Dataset-specific approach

### ✅ New Approach (Yucheng's Requirement)
- **Intent-based detection** (goal-driven)
- Extract high-level goals, analyze intent sequences
- Generic framework (domain-agnostic)

**Reason**: Rules are too ad-hoc and not generalizable; raw content analysis is too complex

---

## 📋 Core Method: Intent-Action Mapping

### Yucheng's Requirement
Extract **intent/goal** for each action, build mapping table:

| Action (What) | Intent (Why) | Result | Drift? |
|---------------|--------------|--------|--------|
| `view(symbol.py)` | Understand code | Success | None |
| `edit(symbol.py)` | Fix bug | Success | None |
| `view(auth.py)` | ??? | Success | **Scope Drift** ✓ |
| `edit(symbol.py)` | Fix bug (again) | Failed | **Loop Drift** ✓ |

### Why Effective?
- **Loop Drift**: Same intent + repeated failure
- **Scope Drift**: Intent unclear or outside task goal
- **Easier than raw content**: No need to read thousands of lines of code

---

## 🔑 Key Insights

### 1. Drift Definition = Main Paper Contribution
> "Clearly defining context drift is already a research contribution, could take a large chunk in your paper."

**Meaning**:
- Don't underestimate the value of taxonomy
- Must be rigorous
- Needs empirical evidence + literature support

---

### 2. Current 3 Drift Types Not Comprehensive
**Yucheng identified missing types**:
- ❌ Repetition (unconscious repetition, not loop)
- ❌ Plan deviation (deviating from established plan)

**Requirements**:
- ✅ Continuously survey literature for more types
- ✅ Derive new types from empirical data
- ✅ Track supporting papers for citations

---

### 3. Detection Algorithm Must Be Generic
> "Don't do rule-based. Be more generic so this can be applied to any domain."

**Principles**:
- Model-agnostic (not dependent on specific LLM)
- Domain-agnostic (works across SWE/τ-bench/WebArena)
- Detection = Prevention (same method for both)

---

### 4. Empirical-Driven > Literature Survey
> "Derive the issue from existing trajectory... conduct empirical study."

**Not a survey paper**, but rather:
1. Observe drift patterns from real trajectories
2. Use literature to support your discovered patterns
3. Propose rigorous taxonomy
4. Develop detection algorithm

---

## ✅ To-Do List (Due: Nov 12)

### Priority 1: Manual Trajectory Annotation
**Tasks**:
- [ ] Select 2-3 trajectories (prefer weaker models - more errors)
- [ ] Manually annotate each action:
  - What's the intent/goal?
  - Success/failure?
  - If failed, why?
  - Is it drift? Which type?

**Example annotation format**:
```
Task: Fix sympy symbols() bug

Step 3: view(/testbed/sympy/core/symbol.py)
  Intent: Understand implementation
  Result: Success
  Drift: None

Step 15: view(/testbed/sympy/auth/permissions.py)
  Intent: ??? (unclear, unrelated to task)
  Result: Success
  Drift: Scope Drift (out of scope)

Step 16: edit(/testbed/sympy/core/symbol.py)
  Intent: Fix bug
  Result: Failed (same error as before)
  Drift: Loop Drift (repeated failure)
```

---

### Priority 2: Create Intent-Action Table
**Requirements**:
- [ ] Left side: Raw trajectory content
- [ ] Right side: Intent + Drift detection
- [ ] Show 1 complete example to Yucheng

**Table format**:

| Step | Action | Intent/Goal | Result | Drift Detected |
|------|--------|-------------|--------|----------------|
| 1 | `grep "bug" /testbed/` | Locate error | Success | None |
| 2 | `view(payment.py)` | Understand bug | Success | None |
| ... | ... | ... | ... | ... |
| 12 | `view(auth.py)` | ??? | Success | Scope Drift ✓ |
| 13 | `edit(payment.py)` | Fix bug | Failed | Loop Drift ✓ |

**Summary for each trajectory**:
- Total actions: X
- Drift instances: Y (breakdown by type)
- Final result: Resolved/Failed
- Drift score: Y/X

---

### Priority 3: Prove Feasibility
**Questions**:
- [ ] Is manual intent extraction feasible?
- [ ] Can drift be clearly identified from intents?
- [ ] Which drift types are most common?

**Prepare for discussion**:
- Show your analysis approach
- Explain what's easy/difficult
- Propose automation ideas

---

## 🚫 Explicitly NOT Doing

1. ❌ **Don't wait for perfect drift definition** - Start with current 3, iterate
2. ❌ **Don't use hard-coded rules** - Be generic, use LLM assistance
3. ❌ **Don't feed full trajectory to LLM** - Too long, extract intents first
4. ❌ **Don't write paper** - Focus on method development now
5. ❌ **Don't run large-scale experiments** - Manual validation first

---

## 💡 Key Conclusions

### Research Pipeline Clarified

```
Week 1-2 (Now):
  Manual analysis → Design intent extraction → Prove feasibility

Week 2-3:
  LLM auto-extract intents → Test on 10-20 trajectories

Week 3-4:
  Complete detection algorithm → Pilot experiment (50+50)

Week 4-5:
  Full experiment (100+100) → Statistical analysis

Week 6:
  Paper + Demo
```

---

### Methodology Upgrade

| Dimension | Old Method | New Method |
|-----------|------------|------------|
| **Detection** | Rule-based | Intent-based |
| **Analysis Unit** | Raw action content | High-level intent |
| **Generalizability** | Dataset-specific | Domain-agnostic |
| **Theoretical Basis** | Literature survey | Empirical + Literature |
| **Contribution** | Experimental improvement | Taxonomy + Detection |

---

### Paper Contribution Repositioned

**Main Contributions**:
1. Rigorous context drift taxonomy (empirical-driven)
2. Generic intent-based detection framework
3. Evidence that drift intervention improves performance

**Space Allocation**:
- 40%: Drift definition & taxonomy (main contribution)
- 30%: Detection method
- 30%: Experimental validation

---

## 📅 Timeline Adjustment

### This week (Nov 5-12): Manual Analysis ← WE ARE HERE
- Manually annotate 2-3 trajectories
- Design intent-action table
- Show 1 complete example

### Next week (Nov 13-19): Automation
- LLM extract intents
- Test on 10-20 trajectories
- Refine drift taxonomy

### Week 3-4 (Nov 20-Dec 3): Implementation
- Complete detection algorithm
- Pilot experiment
- Evaluate accuracy

### Week 5-6 (Dec 4-17): Scale & Write
- Full experiment
- Statistical analysis
- Paper + Demo

---

## 🔄 Mindset Shift

**From**: Quick experiments to see if resolution rate improves
**To**: Rigorously define problem, develop generic method, then validate

**From**: Rule-driven
**To**: Data + theory-driven

**From**: Dataset-specific tricks
**To**: Generic framework

---

## 💬 Key Quotes

### On rigor:
> "In a paper, clearly defining context drift is already a research contribution. We want to make this part more rigorous."

### On approach:
> "Don't do rule-based. Be more generic so this can be applied to any domain."

### On intent:
> "Intent is the reason why the agent is taking this action. When we analyze, we only look at those short labels instead of raw trajectory."

### On timeline:
> "You don't need to wait until you have a good definition to start experiments. Start with current three."

### On focus:
> "We can leave paper here and review later. Right now, focus on the method."

---

## 🎯 Success Criteria (Next Meeting)

**Must demonstrate**:
1. ✅ Complete intent annotation for 2-3 trajectories
2. ✅ Side-by-side table (action | intent | drift)
3. ✅ At least 5+ drift instances identified

**Prepare to discuss**:
- Challenges in annotation process
- Which drift types are most obvious/hardest to identify
- Initial ideas for automation approach

---

**Bottom line**: Start with manual analysis, prove intent-based method is feasible, then consider automation and large-scale experiments. This week focus on understanding drift patterns in real trajectories.
