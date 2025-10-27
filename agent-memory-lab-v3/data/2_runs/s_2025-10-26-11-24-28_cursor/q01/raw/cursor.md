# Query 1: The user wants to know the purpose and functionality of the repository.

**User**
what does this repo do?

---

**Assistant**
Reading the key documentation files to summarize the repo's purpose.


## What This Repository Does

This is a research project for monitoring and improving AI coding agents (e.g., Cursor, Claude Code, Copilot) across multiple challenges.

### Main problems it solves

1. Q1 - Execution monitoring and drift detection
   - Tracks whether an agent stays aligned with goals
   - Uses four "guards" (Scope, Plan, Test, Evidence) to spot deviations
   - Produces drift scores and can issue warnings or rollbacks

2. Q2 - Cross-session learning
   - Extracts reusable "pattern cards" from successful tasks
   - Automatically suggests relevant patterns for new tasks

3. Q3 - Dynamic abstraction
   - Adapts output to user skill (novice vs expert)
   - Terse vs guided views based on task difficulty

### Current Implementation Status

- Q1 is implemented and working
- Processes Cursor chat logs → queries → events → drift scores
- Uses TypeScript type definitions and Python processing tools
- Session analysis considers pair-level drift; session-level drift remains future work

This is part of cs224v, focusing on enhancing AI coding assistant reliability and reusability.

---
