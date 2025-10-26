#!/usr/bin/env bash
set -euo pipefail
# Example shell wrapper (edit paths and instance_id as needed).
# Requires SWE-bench to be installed on your machine.
python -m swebench.harness.run_evaluation \
  --dataset_name princeton-nlp/SWE-bench_Lite \  --instance_ids sympy__sympy-20590 \  --predictions_path ./data/examples/predictions.sample.jsonl \  --run_id my_eval
