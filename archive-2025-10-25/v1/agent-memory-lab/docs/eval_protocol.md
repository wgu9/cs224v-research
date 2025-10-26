# Evaluation Protocol

## Community-aligned (SWE-bench)
- Metric: Resolution rate (tests pass after applying your patch).
- Tooling: `swebench.harness.run_evaluation` (Dockerized).

## Our contribution-specific
- **First-try success** (with vs without patterns).
- **Avg. rounds** (edit/test loops).
- **Drift recovery time** (warn → back-on-track).
- **Pattern reuse rate**.
- **View match** (success under terse vs guided).

## Ablations
- –retrieval, –views, –guards; report deltas on the above metrics.
