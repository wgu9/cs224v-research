# Design: One Pipeline for Q1/Q2/Q3

## Foundation
- **Event Bus**: append-only JSONL; each step is an event with `where/what/why/evidence`.
- **Goal Graph (checkpoints)**: `reproduce -> modify -> test -> regress`.

## Q1 — Execution Monitoring (Drift / Guards)
- **ScopeGuard**: edits outside allowed paths/functions.
- **PlanGuard**: actions not allowed in current checkpoint.
- **TestGuard**: skipping critical tests or proceeding with new failures.
- **EvidenceGuard**: step lacks relevant evidence (no logs/assertions/edge-case tests).
- **Drift score**: weighted sum; above threshold → warn + soft rollback.

## Q2 — Cross-Session Learning (Patterns)
- From events → reflection (verbal) → **Pattern Card** with:
  - `triggers`, `steps`, `invariants`, `anti_patterns`, `eval_examples`, `views:{terse,guided}`.
- Retrieval: simple text+path features, then optional vector similarity, then rule re-ranking.
- Injection: merge pattern hints into the planning prompt or tool plan.

## Q3 — Dynamic Abstraction (Views)
- Same pattern, two presentations:
  - **terse**: 3 invariants + 1 assertion + change hints.
  - **guided**: example code + pitfalls + 3 boundary tests.
- Routing by **profiles.json** + task difficulty (repo size, change size, failure types).

## Data Flow
events → guards/drift → reflection → pattern → retrieve → inject → views → (evaluate)
