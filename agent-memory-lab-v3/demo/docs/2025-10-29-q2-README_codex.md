Q2: Cross‑Session Pattern Learning — End‑to‑End Plan (with single‑row example)

Purpose
- Reuse successful fixes across tasks by learning transferable “patterns,” then retrieving and injecting them to help the same Agent solve new tasks with higher resolve rate and lower drift.

What stays the same vs Q1
- Agent writes code (may use LLM). Evaluated by official SWE‑bench evaluator (FAIL_TO_PASS + PASS_TO_PASS).
- Q1 remains as process guard; here it is repurposed as pattern quality signal (low‑drift runs → higher‑quality patterns).

Data and split
- Train/source for patterns: SWE‑bench train split or prior runs (no overlap with final eval).
- Final eval: SWE‑bench Verified (500). Primary metric: Resolve Rate. Secondary: Drift Rate, Pattern Reuse Rate, Scope P/R, cost.

End‑to‑end workflow
1) Collect runs (no Q2)
   - Run baseline Agent on a training corpus (not Verified test set).
   - Log actions (events.jsonl), patch, resolved, and Q1 guard scores.
   - Label each successful run with drift stats (e.g., run_drift = mean/warn share).

2) Pattern extraction (decontextualize)
   - Input: successful, low‑drift trajectories + final patch + minimal context (problem signature).
   - Output: pattern card with fields:
     - id, title, problem_signature (symptoms/keywords/tests)
     - approach (key steps), risks/constraints
     - code anchors (file/function hints), minimal code template (optional)
     - quality signals: success_count, resolve_rate, avg_drift, scope_stats

3) Pattern store
   - Vector index for semantic recall (problem_statement → embeddings).
   - Relational/JSON store for metadata (quality + usage logs).
   - Keep running stats (success/failure with pattern, drift deltas).

4) Retrieval (inference time)
   - Stage‑1 semantic recall: top‑K by embedding similarity.
   - Stage‑2 ML ranking (optional but recommended): rank by features:
     - task features: difficulty, length, keywords, repo size bucket
     - pattern features: prior success, avg drift, scope compactness
     - interaction: keyword overlap, file/namespace hints match
   - Select 1–3 patterns; dedup; prefer high‑quality (low‑drift) patterns.

5) Application (agent loop)
   - Inject pattern summary (approach + anchors + pitfalls) into Agent context.
   - Keep Q1 guard on (shadow/advisory) to observe whether pattern lowers drift.
   - Log retrieve → present → adopt(level) with outcome.

6) Evaluation
   - Experiment arms (same Agent and budget/seed):
     A) Baseline (no Q2), B) Q2 retrieval (stage‑1 only), C) Q2 retrieval (stage‑1 + ML ranker).
   - Primary: Resolve Rate (official evaluator). Secondary: Drift Rate, Pattern Reuse Rate, Scope P/R, tokens/calls.
   - Ablations: with/without Q1 guard feedback; high‑ vs low‑quality patterns; top‑1 vs top‑k.

Single‑row example (from verified.jsonl line 0)
- instance_id: astropy__astropy-12907
- repo: astropy/astropy
- difficulty: 15 min - 1 hour
- problem_statement: len ≈ 1246 chars (details omitted here)

Illustrative run (not executed here; outline only)
1) Retrieval
   - Stage‑1 returns patterns tagged with “array broadcasting”, “separable/modeling”, “mask handling”.
   - Stage‑2 ranker promotes a pattern with: high prior success in astropy‑like repos, low avg drift, matching keywords.

2) Application
   - Inject pattern card summary: key steps (e.g., “reproduce with FAIL_TO_PASS test X; adjust mask logic in separable path; verify P2P sample”).
   - Agent proceeds; Q1 guard monitors scope (file count ≤ 3 for this difficulty), plan (test before heavy edits), test coverage.

3) Outcome and logging
   - predictions.jsonl generated; official evaluator run externally (Docker) to get resolved=True/False.
   - Pattern usage logged as retrieved → adopted_strict/like/retrieved_only.
   - Update pattern quality stats (success_count, drift deltas).

Minimal artifacts to log (for reproducibility)
- events.jsonl: action‑level log (type, args, ts).
- guards.jsonl: per‑action guard scores and decisions.
- retrieval.jsonl: candidates, scores (semantic + ranker), chosen.
- predictions.jsonl: instance_id, model_patch (for evaluator).
- run_meta.json: seed, budget, flags (use_q2, use_q1), versions.

Metrics (reporting)
- Primary: Resolve Rate across Verified.
- Secondary: Drift Rate; Pattern Reuse Rate (% tasks where pattern retrieved ≥τ and presented); Scope P/R; cost.
- Success with pattern: resolve_with_pattern vs without; McNemar/χ² for significance.

Suggested baseline grid
- Agent fixed; seeds/budget fixed.
- A) No Q2; B) Q2(stage‑1 semantic only); C) Q2(stage‑1 + ML ranker).
- Optional: +Q1 advisory vs shadow to see interaction.

Implementation notes (non‑binding)
- Feature list for ranker (examples):
  - task: len(problem), difficulty bucket, repo token count bucket, test name tokens
  - pattern: success_rate, avg_drift, scope_compactness (median files edited), domain tags
  - interaction: keyword Jaccard, anchor path overlap, cosine(problem, pattern_description)
- Start with semantic‑only; add ranker once logs accumulate (≥300–500 pattern uses).

How Q1 feeds Q2 (quality estimation)
- Use guard logs to compute per‑pattern avg_drift and warn/rollback frequency.
- Prefer patterns with low drift and stable scope; downweight those correlated with WARN/ROLLBACK.

Minimal day‑1 checklist (using existing code skeleton)
- Run N training tasks (not Verified test set) to collect successful, low‑drift runs.
- Extract 20–50 initial pattern cards manually+script assisted.
- Build stage‑1 retrieval (embedding + top‑k); wire inject path to Agent.
- Produce predictions.jsonl and run the official evaluator externally; record Resolve/Drift/Reuse.

Notes
- Do not surface gold patch to the Agent; gold is for evaluation and scope analysis only.
- Keep seeds/budget fixed across arms; report cost.

