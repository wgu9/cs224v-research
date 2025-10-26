# Q3 Analyze — Dynamic Views for Personalized Responses

Purpose: adapt how we respond (abstraction level and wording) to the user’s background, without building any UI. Q2 learns what to do (Pattern Cards); Q3 decides how to say it (view routing + rendering).

## Scope
- Q3 generates personalized, difficulty‑matched textual replies from the same Pattern Card.
- Not a UI feature. Output is plain text, suitable for prompts or assistant replies.

## Q2 vs Q3
- Q2 (What): Pattern Card = triggers, steps, invariants, anti_patterns, eval_examples.
- Q3 (How): pick a view (terse/guided) per user/profile and render tailored guidance.

## Current Implementation (MVP)
- Views: two variants in each pattern
  - terse: expert quick‑read (short rules + invariants)
  - guided: novice walkthrough (what to configure, checks, when to request exceptions)
- Data sources
  - Pattern: includes `views.terse` / `views.guided` and `invariants`.
  - Profile: `data/profiles/<user>.json` (uses `pref`, `hist_first_try_success`).
- Routing rule (implemented)
  - If `pref == "terse"` OR `hist_first_try_success >= 0.5` → `terse`
  - Else → `guided`
- Rendering (implemented)
  - Emit the selected `views.<view>` text and append `Invariants: ...` from the pattern.

Key files
- `q3_views/render.py`: `choose_view(profile)` + `render(pattern, view)`
- `data/patterns/pattern.pc_doc_only_change.json`: example pattern with two views
- `data/profiles/jeremy.json`: example profile used for routing
- `scripts/e2e_cursor_doc_task.py`: demonstrates retrieve → choose_view → render; writes `artifacts/view_preview.md`

## Data Structures
- Pattern Card (subset)
  ```json
  {
    "pattern_id": "pc_doc_only_change",
    "invariants": ["only whitelisted files changed", "language==target"],
    "views": {
      "terse": "Whitelist-only edits; forbid deps change; ensure checks.",
      "guided": "How to set whitelist & language checks; when to request exceptions."
    }
  }
  ```
- Profile (subset)
  ```json
  { "user_id": "<id>", "self_report": "novice|intermediate|expert", "hist_first_try_success": 0.35, "pref": "terse|guided|none" }
  ```

## Output Artifact
- `data/runs/<run_id>/artifacts/view_preview.md` — rendered textual view (terse or guided).

## What Q3 Is (and Isn’t)
- Is: a textual presentation strategy (personalized guidance level).
- Isn’t: a front‑end or UI. It produces text for prompts/replies.

## Planned Extensions (not yet implemented)
- Routing signals: respect `self_report`; add task difficulty estimate (files/lines/risk tags); fallbacks.
- Templates: expand `render()` into structured templates (steps, checks, examples, pitfalls, exception flow).
- Contextualization: conditionally include Q1 guard findings (e.g., drift notes) and Q2 reflection cues.
- Governance: add `version`, `title`, `provenance` to pattern outputs for auditability.

## Limitations (current)
- Only two coarse views; no dynamic difficulty estimator.
- Minimal profile signals; `pref` and historical success only.
- Simple concatenative render (view text + invariants), no rich templating.

## Usage (no UI)
1) Retrieve a relevant pattern (Q2).  
2) Choose view via profile: `choose_view(profile_path)`.  
3) Render text: `render(pattern, view)` and return as the assistant/system reply.

