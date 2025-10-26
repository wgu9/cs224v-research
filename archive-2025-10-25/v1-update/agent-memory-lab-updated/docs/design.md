# Design (Updated)

**Foundation**: One Event Bus (`events.jsonl`) and one Goal Graph (4 checkpoints).
All Q1/Q2/Q3 consume the **same events**.

- **Q1**: Guards (scope/plan/test/evidence) → `drift_score` → warn/rollback.
- **Q2**: From events(+cursor.md) → reflection → Pattern Card → retrieve+inject.
- **Q3**: Two abstraction views (terse/guided) using the **same pattern**; routing by user profile.

**Data flow**: raw (patch/test/chat) → events → guards → reflection → pattern → retrieve → views → (eval).
