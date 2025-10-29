"""
Enhanced batch prediction generator with Q1 drift metrics.

For each task, generates:
1. predictions.jsonl (for SWE-bench evaluator)
2. drift_metrics.json (for Q2 pattern extraction)

This combines the work of:
- batch_generate_predictions.py (patch generation)
- Q1 monitoring (drift calculation)
"""

from pathlib import Path
import argparse
import os
import json
from typing import Optional
from datetime import datetime

# Allow local imports
import sys
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "utils"))
sys.path.insert(0, str(Path(__file__).parent / "steps"))

from steps.step1_load_data import load_task
from steps.step2_init_guards import FourGuardMonitor
from steps.step5_evaluate import evaluate_scope, extract_files_from_patch
from utils import SimpleBedrockAgent, prepare_predictions
from generate_predictions import (
    _ensure_repo_mirror,
    _ensure_worktree_at_commit,
    _apply_and_rediff,
    _check_unified_diff_format,
)


def bool_flag(x: str) -> bool:
    return str(x).lower() in {"1", "true", "yes", "y"}


def compute_q1_drift_metrics(task, patch, agent_actions=None):
    """
    Compute Q1 drift metrics for a solution.

    Returns:
        dict with:
        - drift_rate: overall drift rate
        - scope_precision: how precise is the scope
        - scope_recall: how complete is the scope
        - num_files_modified: number of files changed
        - drift_details: breakdown by guard
    """
    try:
        # Initialize Q1 guard
        guard = FourGuardMonitor(task)

        # Extract files from patch
        agent_files = extract_files_from_patch(patch)
        gold_files = extract_files_from_patch(task.ground_truth_patch)

        # Scope analysis
        scope_metrics = evaluate_scope(patch, task.ground_truth_patch)

        # Simple drift estimation (without full action history)
        # Based on scope violation
        num_files = len(agent_files)
        scope_limit = guard.scope_file_limit

        scope_violation = 1.0 if num_files > scope_limit else 0.0
        if num_files <= scope_limit and agent_files - gold_files:
            # Modified files outside gold set
            scope_violation = 0.5

        # Estimated drift score (simplified)
        # In real Q1, this would come from monitoring each action
        # Here we estimate based on final patch
        drift_score = 0.4 * scope_violation  # Only scope component for now

        return {
            'drift_rate': drift_score,
            'scope_precision': scope_metrics['scope_precision'],
            'scope_recall': scope_metrics['scope_recall'],
            'num_files_modified': num_files,
            'scope_file_limit': scope_limit,
            'scope_violation': scope_violation,
            'extra_files': list(scope_metrics.get('extra_files', [])),
            'missed_files': list(scope_metrics.get('missed_files', [])),
            'gold_files': list(gold_files),
            'agent_files': list(agent_files),
        }
    except Exception as e:
        print(f"⚠️  Warning: Failed to compute Q1 metrics: {e}")
        return {
            'drift_rate': None,
            'scope_precision': None,
            'scope_recall': None,
            'error': str(e),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Batch-generate predictions with Q1 drift metrics"
    )
    parser.add_argument("--start", type=int, default=0, help="Start task index")
    parser.add_argument("--end", type=int, default=None, help="End task index")
    parser.add_argument("--base_dir", type=str, default="", help="Run root directory")
    parser.add_argument("--use_gold", type=bool_flag, default=False, help="Use gold patch")
    parser.add_argument("--unified", type=int, default=3, help="git diff context lines")
    parser.add_argument(
        "--cache_dir",
        type=str,
        default=os.getenv("Q1_REPO_CACHE", str(Path.home() / ".cache/swebench_repos")),
    )
    parser.add_argument(
        "--work_dir",
        type=str,
        default=os.getenv("Q1_WORK_DIR", "/tmp/swebench_work"),
    )
    args = parser.parse_args()

    data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"

    # Determine run root
    if args.base_dir:
        run_root = Path(args.base_dir)
    else:
        ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        run_root = Path("logs") / ts

    predictions_root = run_root / "predictions"
    drift_metrics_root = run_root / "drift_metrics"
    predictions_root.mkdir(parents=True, exist_ok=True)
    drift_metrics_root.mkdir(parents=True, exist_ok=True)

    # Initialize agent if needed
    agent: Optional[SimpleBedrockAgent] = None
    if not args.use_gold:
        try:
            agent = SimpleBedrockAgent(require_token=True)
        except Exception as e:
            raise SystemExit(f"❌ LLM agent failed: {e}")

    # Count total tasks
    total = 0
    while True:
        try:
            _ = load_task(data_file, task_index=total)
            total += 1
        except Exception:
            break

    start = max(0, args.start)
    end = total if args.end is None else min(args.end, total)

    print("=" * 80)
    print(f"Batch generating predictions WITH Q1 METRICS")
    print(f"Tasks: [{start}, {end}) of {total}")
    print(f"Run root: {run_root}")
    print(f"Mode: {'GOLD' if args.use_gold else 'AGENT (LLM)'}")
    print("=" * 80)

    # Statistics
    stats = {
        'attempted': end - start,
        'success': 0,
        'success_with_metrics': 0,
        'load_failed': 0,
        'agent_failed': 0,
        'metrics_failed': 0,
        'high_quality': 0,  # drift < 0.2 and resolved
        'medium_quality': 0,  # drift < 0.35
        'low_quality': 0,  # drift >= 0.35
    }

    for idx in range(start, end):
        try:
            task = load_task(data_file, task_index=idx)
        except Exception as e:
            print(f"❌ Failed to load task {idx}: {e}")
            stats['load_failed'] += 1
            continue

        # Folder structure
        folder = predictions_root / f"input_data_{idx}" / f"{task.instance_id}"
        folder.mkdir(parents=True, exist_ok=True)
        pred_file = folder / "predictions.jsonl"
        drift_file = drift_metrics_root / f"input_data_{idx}_drift.json"

        # Get patch
        if args.use_gold:
            patch = task.ground_truth_patch
        else:
            try:
                raw_patch = agent.solve(task)
                mirror = _ensure_repo_mirror(task.repo, Path(args.cache_dir))
                wt = _ensure_worktree_at_commit(mirror, task.base_commit, Path(args.work_dir))
                try:
                    patch = _apply_and_rediff(raw_patch, wt, unified=args.unified)
                finally:
                    try:
                        from subprocess import run as _run
                        _run(["git", "worktree", "remove", "--force", str(wt)], cwd=str(mirror), text=True)
                    except Exception:
                        import shutil as _shutil
                        _shutil.rmtree(wt, ignore_errors=True)
            except Exception as e:
                print(f"❌ Agent failed for {task.instance_id}: {e}")
                stats['agent_failed'] += 1
                continue

        # Validate patch
        try:
            _check_unified_diff_format(patch)
        except Exception as e:
            print(f"❌ Invalid patch for {task.instance_id}: {e}")
            bad = folder / "bad_patch.diff"
            bad.write_text(patch)
            continue

        # Write predictions.jsonl
        try:
            prepare_predictions([task], [patch], pred_file)
            stats['success'] += 1
        except Exception as e:
            print(f"❌ Failed writing predictions for {task.instance_id}: {e}")
            continue

        # ✨ NEW: Compute Q1 drift metrics
        try:
            drift_metrics = compute_q1_drift_metrics(task, patch)

            # Save drift metrics
            with open(drift_file, 'w') as f:
                json.dump({
                    'task_id': task.instance_id,
                    'task_index': idx,
                    'difficulty': task.difficulty,
                    'repo': task.repo,
                    'drift_metrics': drift_metrics,
                    'patch_length': len(patch),
                    'used_gold': args.use_gold,
                }, f, indent=2)

            stats['success_with_metrics'] += 1

            # Classify quality
            drift_rate = drift_metrics.get('drift_rate')
            if drift_rate is not None:
                if drift_rate < 0.2:
                    stats['high_quality'] += 1
                    quality = "HIGH"
                elif drift_rate < 0.35:
                    stats['medium_quality'] += 1
                    quality = "MEDIUM"
                else:
                    stats['low_quality'] += 1
                    quality = "LOW"

                print(f"✅ {idx}/{end} {task.instance_id[:30]:30s} | "
                      f"Drift: {drift_rate:.3f} | Quality: {quality}")
            else:
                print(f"✅ {idx}/{end} {task.instance_id[:30]:30s} | "
                      f"Metrics: FAILED")
        except Exception as e:
            print(f"⚠️  Metrics failed for {task.instance_id}: {e}")
            stats['metrics_failed'] += 1

    # Final summary
    print("\n" + "=" * 80)
    print("Batch Summary")
    print("=" * 80)
    print(f"Attempted:              {stats['attempted']}")
    print(f"Success (predictions):  {stats['success']}")
    print(f"Success (with metrics): {stats['success_with_metrics']}")
    print(f"\nQuality Distribution (for Q2 pattern extraction):")
    print(f"  High-quality (drift < 0.2):   {stats['high_quality']} "
          f"({stats['high_quality']/max(1,stats['success_with_metrics'])*100:.1f}%)")
    print(f"  Medium-quality (0.2-0.35):    {stats['medium_quality']} "
          f"({stats['medium_quality']/max(1,stats['success_with_metrics'])*100:.1f}%)")
    print(f"  Low-quality (drift >= 0.35):  {stats['low_quality']} "
          f"({stats['low_quality']/max(1,stats['success_with_metrics'])*100:.1f}%)")
    print(f"\nFailures:")
    print(f"  Load failed:    {stats['load_failed']}")
    print(f"  Agent failed:   {stats['agent_failed']}")
    print(f"  Metrics failed: {stats['metrics_failed']}")
    print("=" * 80)
    print(f"\n💡 Next step: Extract patterns from high-quality solutions")
    print(f"   python extract_patterns_from_drift_metrics.py --input {drift_metrics_root}")


if __name__ == "__main__":
    main()
