# Evaluation Protocol (Updated)

**Community metrics**: SWE-bench %Resolved via official harness (apply diff, run tests).  
**Our metrics**:
- Q1: drift detection rate, false positives, **drift recovery time**.
- Q2: **pattern reuse rate**, **first-try success uplift**, **avg rounds/time ↓**.
- Q3: view-match quality (success & stability under terse vs guided).

**Ablations**: baseline → +pattern → +pattern+views → +pattern+views+guards.
