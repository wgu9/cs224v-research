"""
Batch-generate per-task predictions.jsonl files (no evaluations).

For each task in data/swebench/verified.jsonl, write exactly one-line
predictions.jsonl to a folder named like:

  logs/predictions/input_data_{index}_{instance_id}/predictions.jsonl

By default, uses the LLM agent (requires AWS_BEARER_TOKEN_BEDROCK).
Pass --use_gold true to use the dataset GOLD patch instead.

Supports --full_file_mode and --unified for higher success rates
mirroring generate_predictions.py behavior.
"""

from pathlib import Path
import argparse
import os
from typing import Optional
from datetime import datetime

# Allow local imports
import sys
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "utils"))
sys.path.insert(0, str(Path(__file__).parent / "steps"))

from steps.step1_load_data import load_task
from utils import SimpleBedrockAgent, prepare_predictions
from generate_predictions import (
    _ensure_repo_mirror,
    _ensure_worktree_at_commit,
    _apply_and_rediff,
    _check_unified_diff_format,
    infer_target_files,
)


def bool_flag(x: str) -> bool:
    return str(x).lower() in {"1", "true", "yes", "y"}


def main():
    parser = argparse.ArgumentParser(description="Batch-generate per-task predictions.jsonl")
    parser.add_argument("--start", type=int, default=0, help="Start task index (inclusive)")
    parser.add_argument("--end", type=int, default=None, help="End task index (exclusive); default: all")
    parser.add_argument("--base_dir", type=str, default="", help="Run root directory. Default: logs/<timestamp>")
    parser.add_argument("--use_gold", type=bool_flag, default=False, help="Use dataset gold patch instead of LLM")
    parser.add_argument("--full_file_mode", type=bool_flag, default=False, help="Use full-file rewrite pipeline")
    parser.add_argument("--target_files", type=str, default="", help="Comma-separated relative paths to rewrite in full-file mode")
    parser.add_argument("--unified", type=int, default=3, help="git diff context lines for re-diff/full-file mode")
    parser.add_argument("--cache_dir", type=str, default=os.getenv("Q1_REPO_CACHE", str(Path.home() / ".cache/swebench_repos"))),
    parser.add_argument("--work_dir", type=str, default=os.getenv("Q1_WORK_DIR", "/tmp/swebench_work")),
    args = parser.parse_args()

    data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
    # Determine run root: logs/yyyy-mm-dd-hh-mm-ss
    if args.base_dir:
        run_root = Path(args.base_dir)
    else:
        ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        run_root = Path("logs") / ts
    predictions_root = run_root / "predictions"
    predictions_root.mkdir(parents=True, exist_ok=True)

    # Prepare agent (only if needed). Require a real token when using LLM.
    agent: Optional[SimpleBedrockAgent] = None
    if not args.use_gold:
        try:
            agent = SimpleBedrockAgent(require_token=True)
        except Exception as e:
            raise SystemExit(
                f"❌ LLM agent initialization failed: {e}\n"
                "Set AWS_BEARER_TOKEN_BEDROCK in your environment and try again."
            )

    # Determine total tasks by probing until failure
    # We avoid loading the entire JSONL into memory
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
    print(f"Batch generating predictions: tasks [{start}, {end}) of {total}")
    print(f"Run root: {run_root}")
    print(f"Predictions root: {predictions_root}")
    print(f"Mode: {'GOLD' if args.use_gold else 'AGENT (LLM)'} | Full-file: {args.full_file_mode} | Unified: {args.unified}")
    print("=" * 80)

    # Summary statistics
    stats = {
        'attempted': end - start,
        'success': 0,
        'load_failed': 0,
        'agent_failed': 0,
        'fullfile_failed': 0,
        'rediff_failed': 0,
        'invalid_patch': 0,
        'write_failed': 0,
        'no_targets': 0,
    }

    for idx in range(start, end):
        try:
            task = load_task(data_file, task_index=idx)
        except Exception as e:
            print(f"❌ Failed to load task index {idx}: {e}")
            stats['load_failed'] += 1
            continue

        # Folder name follows the input_data naming scheme
        # logs/<ts>/predictions/input_data_{idx}/{instance_id}/
        folder = predictions_root / f"input_data_{idx}" / f"{task.instance_id}"
        folder.mkdir(parents=True, exist_ok=True)
        output_file = folder / "predictions.jsonl"

        # Get patch
        if args.use_gold:
            patch = task.ground_truth_patch
        else:
            if args.full_file_mode:
                # Full-file rewrite pipeline (baseline checkout, file rewrite, stage+diff)
                try:
                    mirror = _ensure_repo_mirror(task.repo, Path(args.cache_dir))
                    wt = _ensure_worktree_at_commit(mirror, task.base_commit, Path(args.work_dir))
                    try:
                        # Infer targets if not provided
                        targets = [p.strip() for p in args.target_files.split(',') if p.strip()]
                        if not targets:
                            targets = infer_target_files(task, wt, agent=agent, allow_agent_diff=True)
                        if not targets:
                            print(f"❌ No target files inferred for {task.instance_id}; skip")
                            stats['no_targets'] += 1
                            continue

                        originals = {}
                        for rel in targets:
                            fpath = wt / rel
                            if not fpath.exists():
                                print(f"❌ Target file not found in baseline: {rel}")
                                raise FileNotFoundError(rel)
                            originals[rel] = fpath.read_text()

                        new_files = agent.produce_new_files(task, originals)
                        for rel, text in new_files.items():
                            abs_f = wt / rel
                            abs_f.parent.mkdir(parents=True, exist_ok=True)
                            if text and not text.endswith("\n"):
                                text += "\n"
                            abs_f.write_text(text or "")
                        # Stage and diff
                        import subprocess
                        subprocess.run(["git", "add", "-A"], cwd=str(wt), check=True, text=True)
                        from subprocess import run, PIPE
                        p = run(["git", "diff", "--staged", f"--unified={args.unified}"], cwd=str(wt), text=True, capture_output=True)
                        if p.returncode != 0:
                            raise RuntimeError(p.stderr)
                        patch = p.stdout.replace("\r\n", "\n").replace("\r", "\n")
                        if not patch:
                            raise RuntimeError("Full-file rewrite produced empty diff")
                        if not patch.endswith("\n"):
                            patch += "\n"
                    finally:
                        try:
                            from subprocess import run as _run
                            _run(["git", "worktree", "remove", "--force", str(wt)], cwd=str(mirror), text=True)
                        except Exception:
                            import shutil as _shutil
                            _shutil.rmtree(wt, ignore_errors=True)
                except Exception as e:
                    print(f"❌ Full-file mode failed for {task.instance_id}: {e}")
                    stats['fullfile_failed'] += 1
                    continue
            else:
                # Simple patch mode + re-diff against baseline for stability
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
                    print(f"❌ Agent patch+rediff failed for {task.instance_id}: {e}")
                    stats['rediff_failed'] += 1
                    continue

        # Validate and write predictions.jsonl with one entry
        try:
            _check_unified_diff_format(patch)
        except Exception as e:
            print(f"❌ Patch format invalid for {task.instance_id}: {e}")
            # Save bad patch for inspection
            bad = folder / "bad_patch.diff"
            bad.write_text(patch)
            stats['invalid_patch'] += 1
            continue

        try:
            prepare_predictions([task], [patch], output_file)
            print(f"✅ Wrote {output_file}")
            stats['success'] += 1
        except Exception as e:
            print(f"❌ Failed writing predictions for {task.instance_id}: {e}")
            stats['write_failed'] += 1

    # Final summary
    print("\n" + "=" * 80)
    print("Batch Summary")
    print("=" * 80)
    print(f"Attempted: {stats['attempted']}")
    print(f"Success:   {stats['success']}")
    failures = stats['attempted'] - stats['success']
    print(f"Failures:  {failures}")
    print("- Breakdown:")
    print(f"  - load_failed:   {stats['load_failed']}")
    print(f"  - agent_failed:  {stats['agent_failed']}")
    print(f"  - fullfile_failed: {stats['fullfile_failed']}")
    print(f"  - rediff_failed: {stats['rediff_failed']}")
    print(f"  - invalid_patch: {stats['invalid_patch']}")
    print(f"  - write_failed:  {stats['write_failed']}")
    print(f"  - no_targets:    {stats['no_targets']}")
    print("=" * 80)
    print("Done.")


if __name__ == "__main__":
    main()
