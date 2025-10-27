# Query 2: The user wants to know the logical next steps for progressing with the AI coding agent monitoring project.

## Context from Previous Query

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
  ...

---

## Current Query-Answer

**User**
what would be next steps? 

---

**Assistant**
Based on the comprehensive documentation I've read, here are the logical next steps for this project:

## Clarifying Questions

Before I can create a detailed plan, I need to understand your priorities:

1. Which direction do you want to pursue next?
   - a) Validate Q1 with more real data (collect 50-100 cursor chats, analyze drift patterns, tune thresholds)
   - b) Implement session-level drift detection (Q1.5 - classify session types, detect objective consistency drift)
   - c) Begin Q2 implementation (pattern card extraction and retrieval from successful runs)
   - d) Create analysis/reporting tools for existing Q1 output (aggregation scripts, visualizations)

2. If you choose session-level drift (option b), which approach?
   - a) Start with the minimal "aggregate statistics" approach (avg_drift, max_drift, health scores) without session type classification
   - b) Implement full session type classification first (single-goal vs multi-goal vs exploratory)
   - c) Focus only on objective consistency drift detection using LLM

3. Do you have existing cursor chat data ready to process?
   - a) Yes, I have 10+ cursor chat files ready
   - b) No, I need to collect/export data first
   - c) I have a few samples but want to start with synthetic/test data

Please answer with the letter choices (e.g., "1a, 2b, 3a") so I can create a specific implementation plan.

---
