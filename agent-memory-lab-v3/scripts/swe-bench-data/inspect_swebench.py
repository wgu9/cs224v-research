#!/usr/bin/env python3
# 该脚本用于检查和分析 SWE-bench 数据的结构和内容。
# 可以查看任务详情、统计信息和数据分布，支持交互式浏览特定任务。
# 帮助理解数据的格式、测试要求和问题的复杂程度。
"""
Inspect SWE-bench data to understand structure.
"""

import json
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "swebench"

def load_jsonl(file_path):
    """Load JSONL file."""
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data

def inspect_task(task, verbose=True):
    """Inspect a single task."""
    print("=" * 80)
    print("TASK INSPECTION")
    print("=" * 80)

    print(f"\n📌 Instance ID: {task['instance_id']}")
    print(f"📦 Repository: {task['repo']}")
    print(f"🔗 Issue URL: {task.get('issue_url', 'N/A')}")

    print(f"\n📝 Problem Statement:")
    print("-" * 80)
    problem = task['problem_statement']
    print(problem[:500] + ("..." if len(problem) > 500 else ""))

    if verbose:
        print(f"\n🔧 Base Commit: {task.get('base_commit', 'N/A')}")

        print(f"\n✅ FAIL_TO_PASS tests: {len(task.get('FAIL_TO_PASS', []))}")
        if task.get('FAIL_TO_PASS'):
            for test in task['FAIL_TO_PASS'][:3]:
                print(f"   - {test}")
            if len(task['FAIL_TO_PASS']) > 3:
                print(f"   ... and {len(task['FAIL_TO_PASS']) - 3} more")

        print(f"\n✓ PASS_TO_PASS tests: {len(task.get('PASS_TO_PASS', []))}")

        # Ground truth patch (if available)
        if 'patch' in task:
            patch_lines = task['patch'].count('\n')
            print(f"\n📄 Ground Truth Patch: {patch_lines} lines")
            print("   (Note: Don't use this during agent execution!)")

        # Test patch
        if 'test_patch' in task:
            test_patch_lines = task['test_patch'].count('\n')
            print(f"📄 Test Patch: {test_patch_lines} lines")

    print("\n" + "=" * 80)

def analyze_dataset(data, name):
    """Analyze entire dataset."""
    print(f"\n{'=' * 80}")
    print(f"{name} DATASET ANALYSIS")
    print(f"{'=' * 80}")

    print(f"\n📊 Total tasks: {len(data)}")

    # Repository distribution
    repos = Counter(task['repo'] for task in data)
    print(f"\n🏢 Repositories ({len(repos)} total):")
    for repo, count in repos.most_common(10):
        print(f"   {count:4d} tasks  {repo}")
    if len(repos) > 10:
        print(f"   ... and {len(repos) - 10} more repositories")

    # Test counts
    fail_to_pass_counts = [len(task.get('FAIL_TO_PASS', [])) for task in data]
    pass_to_pass_counts = [len(task.get('PASS_TO_PASS', [])) for task in data]

    print(f"\n🧪 Test Statistics:")
    print(f"   FAIL_TO_PASS tests per task:")
    print(f"      Mean: {sum(fail_to_pass_counts) / len(fail_to_pass_counts):.2f}")
    print(f"      Min: {min(fail_to_pass_counts)}, Max: {max(fail_to_pass_counts)}")
    print(f"   PASS_TO_PASS tests per task:")
    print(f"      Mean: {sum(pass_to_pass_counts) / len(pass_to_pass_counts):.2f}")
    print(f"      Min: {min(pass_to_pass_counts)}, Max: {max(pass_to_pass_counts)}")

    # Problem statement lengths
    problem_lengths = [len(task['problem_statement']) for task in data]
    print(f"\n📝 Problem Statement Lengths (chars):")
    print(f"   Mean: {sum(problem_lengths) / len(problem_lengths):.0f}")
    print(f"   Min: {min(problem_lengths)}, Max: {max(problem_lengths)}")

    # Patch sizes (if available)
    if 'patch' in data[0]:
        patch_sizes = [task['patch'].count('\n') for task in data]
        print(f"\n🔧 Patch Sizes (lines):")
        print(f"   Mean: {sum(patch_sizes) / len(patch_sizes):.1f}")
        print(f"   Min: {min(patch_sizes)}, Max: {max(patch_sizes)}")

    # Available fields
    print(f"\n📋 Available Fields:")
    for key in sorted(data[0].keys()):
        print(f"   - {key}")

def main():
    """Main inspection."""
    print("=" * 80)
    print("SWE-bench Data Inspector")
    print("=" * 80)

    # Check what files exist
    verified_file = DATA_DIR / "verified.jsonl"
    train_file = DATA_DIR / "train.jsonl"
    lite_file = DATA_DIR / "lite.jsonl"

    print("\n📁 Checking for data files...")

    if not DATA_DIR.exists():
        print(f"❌ Data directory not found: {DATA_DIR}")
        print("   Run: python scripts/download_swebench.py first")
        return

    available_datasets = []
    if verified_file.exists():
        available_datasets.append(("Verified", verified_file))
    if train_file.exists():
        available_datasets.append(("Train", train_file))
    if lite_file.exists():
        available_datasets.append(("Lite", lite_file))

    if not available_datasets:
        print(f"❌ No data files found in {DATA_DIR}")
        print("   Run: python scripts/download_swebench.py first")
        return

    print(f"\n✅ Found {len(available_datasets)} datasets:")
    for name, path in available_datasets:
        size_mb = path.stat().st_size / 1024 / 1024
        print(f"   - {name}: {path.name} ({size_mb:.2f} MB)")

    # Inspect first dataset
    print("\n" + "=" * 80)
    name, path = available_datasets[0]
    print(f"Loading {name} dataset...")
    data = load_jsonl(path)

    # Show dataset analysis
    analyze_dataset(data, name)

    # Show example task
    print("\n" + "=" * 80)
    response = input(f"\nInspect first task in detail? [Y/n]: ")
    if response.lower() != 'n':
        inspect_task(data[0], verbose=True)

    # Interactive inspection
    while True:
        print("\n" + "=" * 80)
        response = input(f"\nInspect task by index (0-{len(data)-1}) or 'q' to quit: ")
        if response.lower() == 'q':
            break
        try:
            idx = int(response)
            if 0 <= idx < len(data):
                inspect_task(data[idx], verbose=True)
            else:
                print(f"❌ Index out of range (0-{len(data)-1})")
        except ValueError:
            print("❌ Invalid input")

    print("\n✅ Inspection complete!")

if __name__ == "__main__":
    main()
