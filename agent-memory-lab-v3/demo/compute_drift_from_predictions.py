"""
Compute Q1 drift metrics from existing predictions.jsonl files.

This script processes already-generated predictions and adds drift metrics.
Useful when you've already run batch_generate_predictions.py.
"""

from pathlib import Path
import json
import argparse
from typing import List

import sys
sys.path.insert(0, str(Path(__file__).parent))

from steps.step1_load_data import load_task
from steps.step2_init_guards import FourGuardMonitor
from steps.step5_evaluate import evaluate_scope, extract_files_from_patch


def compute_drift_metrics(task, patch):
    """
    Compute Q1 drift metrics for a given task and patch.

    Returns dict with:
        - drift_rate: estimated drift score
        - scope_precision/recall: alignment with gold patch
        - num_files_modified: file count
        - quality_label: HIGH/MEDIUM/LOW
    """
    try:
        # Initialize Q1 guard
        guard = FourGuardMonitor(task)

        # Extract files
        agent_files = extract_files_from_patch(patch)
        gold_files = extract_files_from_patch(task.ground_truth_patch)

        # Scope analysis
        scope_metrics = evaluate_scope(patch, task.ground_truth_patch)

        # Scope violation estimation
        num_files = len(agent_files)
        scope_limit = guard.scope_file_limit

        # Drift score (simplified, based on final patch only)
        scope_violation = 0.0
        if num_files > scope_limit:
            scope_violation = 1.0
        elif agent_files - gold_files:
            # Has extra files
            scope_violation = len(agent_files - gold_files) / num_files

        # Weighted drift score (only scope component)
        drift_score = 0.4 * scope_violation

        # Quality label
        if drift_score < 0.2:
            quality = "HIGH"
        elif drift_score < 0.35:
            quality = "MEDIUM"
        else:
            quality = "LOW"

        return {
            'drift_rate': drift_score,
            'scope_precision': scope_metrics['scope_precision'],
            'scope_recall': scope_metrics['scope_recall'],
            'num_files_modified': num_files,
            'scope_file_limit': scope_limit,
            'scope_violation': scope_violation,
            'quality_label': quality,
            'extra_files': list(scope_metrics.get('extra_files', [])),
            'missed_files': list(scope_metrics.get('missed_files', [])),
            'gold_files': list(gold_files),
            'agent_files': list(agent_files),
        }
    except Exception as e:
        return {
            'drift_rate': None,
            'scope_precision': None,
            'scope_recall': None,
            'quality_label': "UNKNOWN",
            'error': str(e),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Compute drift metrics from existing predictions"
    )
    parser.add_argument(
        "--predictions_dir",
        type=str,
        required=True,
        help="Directory containing predictions (e.g., logs/2025-10-29-02-22-26/predictions)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=None,
        help="Output directory for drift metrics (default: same as predictions_dir parent + '/drift_metrics')",
    )
    parser.add_argument(
        "--task_index",
        type=int,
        default=None,
        help="Process only specific task index (for spot testing)",
    )
    parser.add_argument(
        "--instance_id",
        type=str,
        default=None,
        help="Process only specific instance_id (for spot testing)",
    )
    args = parser.parse_args()

    predictions_dir = Path(args.predictions_dir)
    if not predictions_dir.exists():
        raise SystemExit(f"❌ Predictions directory not found: {predictions_dir}")

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = predictions_dir.parent / "drift_metrics"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all prediction folders
    prediction_folders = sorted([
        f for f in predictions_dir.iterdir()
        if f.is_dir() and f.name.startswith("input_data_")
    ])

    data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"

    # Spot test mode: filter to specific task
    if args.task_index is not None:
        target_folder = f"input_data_{args.task_index}"
        prediction_folders = [f for f in prediction_folders if f.name == target_folder]
        if not prediction_folders:
            raise SystemExit(f"❌ No predictions found for task_index={args.task_index}")
        print("=" * 80)
        print(f"🔍 SPOT TEST MODE: Processing task_index={args.task_index}")
        print(f"Predictions dir: {predictions_dir}")
        print(f"Output dir: {output_dir}")
        print("=" * 80)
    elif args.instance_id is not None:
        # Find folder containing this instance_id
        matched = []
        for f in prediction_folders:
            instance_dirs = list(f.iterdir())
            if instance_dirs and instance_dirs[0].name == args.instance_id:
                matched.append(f)
        prediction_folders = matched
        if not prediction_folders:
            raise SystemExit(f"❌ No predictions found for instance_id={args.instance_id}")
        print("=" * 80)
        print(f"🔍 SPOT TEST MODE: Processing instance_id={args.instance_id}")
        print(f"Predictions dir: {predictions_dir}")
        print(f"Output dir: {output_dir}")
        print("=" * 80)
    else:
        print("=" * 80)
        print(f"Computing Q1 drift metrics from existing predictions")
        print(f"Predictions dir: {predictions_dir}")
        print(f"Output dir: {output_dir}")
        print(f"Found {len(prediction_folders)} prediction folders")
        print("=" * 80)

    stats = {
        'total': len(prediction_folders),
        'success': 0,
        'failed': 0,
        'high_quality': 0,
        'medium_quality': 0,
        'low_quality': 0,
    }

    for folder in prediction_folders:
        # Extract index from folder name: input_data_123
        try:
            idx_str = folder.name.split('_')[-1]
            task_index = int(idx_str)
        except (ValueError, IndexError):
            print(f"⚠️  Cannot parse index from {folder.name}, skipping")
            continue

        # Find predictions.jsonl
        instance_dirs = list(folder.iterdir())
        if not instance_dirs:
            print(f"⚠️  Empty folder: {folder.name}")
            continue

        instance_dir = instance_dirs[0]  # Should be only one
        pred_file = instance_dir / "predictions.jsonl"

        if not pred_file.exists():
            print(f"⚠️  No predictions.jsonl in {folder.name}")
            continue

        try:
            # Load task
            task = load_task(data_file, task_index=task_index)

            # Load patch from predictions.jsonl
            with open(pred_file) as f:
                pred = json.load(f)
            patch = pred['model_patch']

            # Compute drift metrics
            drift_metrics = compute_drift_metrics(task, patch)

            # Save metrics
            output_file = output_dir / f"input_data_{task_index}_drift.json"
            with open(output_file, 'w') as f:
                json.dump({
                    'task_id': task.instance_id,
                    'task_index': task_index,
                    'difficulty': task.difficulty,
                    'repo': task.repo,
                    'drift_metrics': drift_metrics,
                    'patch_length': len(patch),
                }, f, indent=2)

            # Update stats
            quality = drift_metrics.get('quality_label', 'UNKNOWN')
            if quality == 'HIGH':
                stats['high_quality'] += 1
            elif quality == 'MEDIUM':
                stats['medium_quality'] += 1
            elif quality == 'LOW':
                stats['low_quality'] += 1

            stats['success'] += 1

            drift_rate = drift_metrics.get('drift_rate', 'N/A')
            print(f"✅ {task_index:3d} {task.instance_id[:40]:40s} | "
                  f"Drift: {drift_rate if isinstance(drift_rate, str) else f'{drift_rate:.3f}'} | "
                  f"Quality: {quality}")

            # In spot test mode, show detailed output
            if args.task_index is not None or args.instance_id is not None:
                print("\n" + "=" * 80)
                print("📊 DETAILED DRIFT METRICS")
                print("=" * 80)
                print(f"Task ID:           {task.instance_id}")
                print(f"Task Index:        {task_index}")
                print(f"Difficulty:        {task.difficulty}")
                print(f"Repo:              {task.repo}")
                print(f"\nDrift Metrics:")
                print(f"  Drift Rate:      {drift_metrics.get('drift_rate', 'N/A'):.3f}" if isinstance(drift_metrics.get('drift_rate'), float) else f"  Drift Rate:      {drift_metrics.get('drift_rate', 'N/A')}")
                print(f"  Quality Label:   {drift_metrics.get('quality_label', 'UNKNOWN')}")
                print(f"  Scope Precision: {drift_metrics.get('scope_precision', 'N/A'):.3f}" if isinstance(drift_metrics.get('scope_precision'), float) else f"  Scope Precision: {drift_metrics.get('scope_precision', 'N/A')}")
                print(f"  Scope Recall:    {drift_metrics.get('scope_recall', 'N/A'):.3f}" if isinstance(drift_metrics.get('scope_recall'), float) else f"  Scope Recall:    {drift_metrics.get('scope_recall', 'N/A')}")
                print(f"  Files Modified:  {drift_metrics.get('num_files_modified', 0)}")
                print(f"  File Limit:      {drift_metrics.get('scope_file_limit', 0)}")
                print(f"  Scope Violation: {drift_metrics.get('scope_violation', 0.0):.3f}")
                print(f"\nFile Analysis:")
                print(f"  Agent files:  {drift_metrics.get('agent_files', [])}")
                print(f"  Gold files:   {drift_metrics.get('gold_files', [])}")
                print(f"  Extra files:  {drift_metrics.get('extra_files', [])}")
                print(f"  Missed files: {drift_metrics.get('missed_files', [])}")
                print(f"\nOutput saved to: {output_file}")
                print("=" * 80)

        except Exception as e:
            print(f"❌ Failed for {folder.name}: {e}")
            stats['failed'] += 1

            # In spot test mode, show error details
            if args.task_index is not None or args.instance_id is not None:
                import traceback
                print("\n" + "=" * 80)
                print("🔴 ERROR DETAILS")
                print("=" * 80)
                traceback.print_exc()
                print("=" * 80)

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total predictions:  {stats['total']}")
    print(f"Success:            {stats['success']}")
    print(f"Failed:             {stats['failed']}")
    print(f"\nQuality Distribution (for Q2 pattern extraction):")
    total_valid = stats['high_quality'] + stats['medium_quality'] + stats['low_quality']
    if total_valid > 0:
        print(f"  High-quality:    {stats['high_quality']:3d} ({stats['high_quality']/total_valid*100:5.1f}%)")
        print(f"  Medium-quality:  {stats['medium_quality']:3d} ({stats['medium_quality']/total_valid*100:5.1f}%)")
        print(f"  Low-quality:     {stats['low_quality']:3d} ({stats['low_quality']/total_valid*100:5.1f}%)")
    print("=" * 80)
    print(f"\n✅ Drift metrics saved to: {output_dir}")
    print(f"\n💡 Next step: Extract patterns from high-quality solutions")
    print(f"   python extract_patterns_from_drift_metrics.py --drift_dir {output_dir}")


if __name__ == "__main__":
    main()
