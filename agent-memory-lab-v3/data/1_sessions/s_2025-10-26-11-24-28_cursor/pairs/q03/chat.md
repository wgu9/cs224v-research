# Query 3: Request a prioritized (P0/P1/P2) to-do list for the project's next steps.

## Context from Previous Query

**User**
what would be next steps? 

---

**Assistant**
Based on the comprehensive documentation I've read, here are the logical next steps for this project:

## Clarifying Questions

Before I can create a detailed plan, I need to understand your priorities:

1. Which direction do you want to pursue next?
   - a) Validate Q1 with more real data (collect 50-100 cursor chats, analyze drift patterns, tune thresholds)
   - b) Implement session-level drift detection (Q1.5 - classify session types, de...

---

## Current Query-Answer

**User**
what do you think about the next steps? can you give me a p0/p1/p2 prioritization of to-do?

---

**Assistant**
## P0 - Critical Immediate Steps (This Week)

**Goal: Establish a data-driven foundation before building more features**

1. Collect data (about 2 hours)
   - Export 20–50 cursor chat files
   - Run them through the existing Q1 pipeline
   - Build a baseline dataset

2. Create basic analysis script (about 1 hour)
   - File: `tools/analyze_drift_summary.py`
   - Input: all `data/2_runs/*/summary.json` files
   - Output: simple stats:
     - Total sessions processed
     - Session drift rate distribution
     - Top drift causes
     - Task type vs drift correlation
   - Purpose: quantify current drift patterns

3. Manual review sample (about 2–3 hours)
   - Review 10–15 sessions manually
   - Tag session types (single-goal/multi-goal/exploratory)
   - Note false positives/negatives
   - Validate guard thresholds

## P1 - High-Value Quick Wins (Next 1–2 Weeks)

4. Implement session-level aggregation (about 3–4 hours)
   - Update `tools/run_q1_batch.py` to output:
     - `avg_drift`, `max_drift`, `drift_rate`
     - `action_mix` (ok/warn/rollback counts)
     - `by_guard_failed` (which guards trigger most)
     - `health` score (green/yellow/red)
   - Documented in `2025-10-26-6B-q1-summary.md`
   - No session type classification yet

5. Session type classification (about 1 day)
   - Heuristic rules (simple, no LLM)
   - Test on manually labeled data
   - Choose detailed vs basic classification (noted in lines 1027–1090)

6. Error handling and edge cases (about 1 day)
   - Validate inputs (malformed cursor.md, missing goal.json)
   - Handle empty sessions
   - Add dry-run option to preview LLM costs

## P2 - Strategic Extensions (1+ Months)

7. Objective consistency drift (depends on step 5)
   - Only worth doing if P0 shows 30%+ sessions are single-goal
   - Otherwise low priority

8. Q2 pattern card extraction (after adequate data)
   - Extract reusable patterns from successful runs
   - Requires stable dataset

9. Session progression analysis
   - Track drift over time within sessions
   - Detect loops and repetitive failures
   - Useful for multi-goal sessions

## Why this prioritization?

- Q1 is done; test it on real data before expanding.
- Data informs session-type mix and threshold tuning, reducing wasted work.
- The heavy strategic work on session-level drift (and Q2) can wait until patterns are clear.

## My recommendation

- Spend the next week on P0 (data + analysis).
- With ~50 sessions, answer:
  - What percentage have drift issues?
  - Which guards trigger most?
  - What’s the session type distribution?
  - Are current thresholds too strict/loose?
- Then invest in P1 features using the results.

Proceed with P0? I can write the analysis script and test on your data when ready.
