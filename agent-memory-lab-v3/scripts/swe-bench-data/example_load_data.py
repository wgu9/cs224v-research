#!/usr/bin/env python3
# 该脚本展示如何加载和使用 SWE-bench 数据。
# 提供了多个实例，包括统计分析、难度过滤、测试分析和范围分析等功能。
# 可用于快速了解数据结构和为后续基线实现做准备。
"""
Example: How to load and use SWE-bench data.
"""

import json
from pathlib import Path
from collections import Counter

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "swebench" / "verified.jsonl"

def load_tasks():
    """Load all tasks from verified.jsonl."""
    tasks = []
    with open(DATA_FILE) as f:
        for line in f:
            tasks.append(json.loads(line))
    return tasks

def example_basic_stats():
    """Example 1: Basic statistics."""
    print("=" * 80)
    print("Example 1: Basic Statistics")
    print("=" * 80)

    tasks = load_tasks()
    print(f"\n📊 Total tasks: {len(tasks)}")

    # Repository distribution
    repos = Counter(t['repo'] for t in tasks)
    print(f"\n📦 Top 5 repositories:")
    for repo, count in repos.most_common(5):
        print(f"   {count:3d} tasks  {repo}")

    # Difficulty distribution (Verified has this field!)
    if 'difficulty' in tasks[0]:
        difficulties = Counter(t.get('difficulty', 'unknown') for t in tasks)
        print(f"\n⏱️  Difficulty distribution:")
        for diff, count in sorted(difficulties.items()):
            print(f"   {count:3d} tasks  {diff}")

def example_filter_by_difficulty():
    """Example 2: Filter by difficulty for Q3."""
    print("\n" + "=" * 80)
    print("Example 2: Filter by Difficulty (for Q3 Dynamic Abstraction)")
    print("=" * 80)

    tasks = load_tasks()

    # Categorize by difficulty
    easy = [t for t in tasks if t.get('difficulty') == '<15 min fix']
    medium = [t for t in tasks if t.get('difficulty') == '15 min - 1 hour']
    hard = [t for t in tasks if t.get('difficulty') == '1-4 hours']
    very_hard = [t for t in tasks if t.get('difficulty') == '>4 hours']

    print(f"\n📊 Difficulty breakdown:")
    print(f"   Easy (< 15 min):      {len(easy):3d} tasks")
    print(f"   Medium (15m-1h):      {len(medium):3d} tasks")
    print(f"   Hard (1-4h):          {len(hard):3d} tasks")
    print(f"   Very Hard (> 4h):     {len(very_hard):3d} tasks")

    # Example: Show an easy task
    if easy:
        task = easy[0]
        print(f"\n📝 Example easy task:")
        print(f"   ID: {task['instance_id']}")
        print(f"   Repo: {task['repo']}")
        print(f"   Problem: {task['problem_statement'][:150]}...")
        print(f"   Tests to fix: {len(task['FAIL_TO_PASS'])}")

def example_test_analysis():
    """Example 3: Analyze test requirements."""
    print("\n" + "=" * 80)
    print("Example 3: Test Analysis (for Q1 Test Guard)")
    print("=" * 80)

    tasks = load_tasks()

    # Test statistics
    fail_to_pass_counts = [len(t['FAIL_TO_PASS']) for t in tasks]
    pass_to_pass_counts = [len(t['PASS_TO_PASS']) for t in tasks]

    print(f"\n🧪 FAIL_TO_PASS tests (must fix):")
    print(f"   Mean: {sum(fail_to_pass_counts) / len(fail_to_pass_counts):.2f}")
    print(f"   Min: {min(fail_to_pass_counts)}, Max: {max(fail_to_pass_counts)}")

    print(f"\n✅ PASS_TO_PASS tests (must not break):")
    print(f"   Mean: {sum(pass_to_pass_counts) / len(pass_to_pass_counts):.2f}")
    print(f"   Min: {min(pass_to_pass_counts)}, Max: {max(pass_to_pass_counts)}")

    # Example task with multiple tests
    multi_test_tasks = [t for t in tasks if len(t['FAIL_TO_PASS']) > 3]
    if multi_test_tasks:
        task = multi_test_tasks[0]
        print(f"\n📋 Example task with multiple tests:")
        print(f"   ID: {task['instance_id']}")
        print(f"   Tests to fix: {len(task['FAIL_TO_PASS'])}")
        print(f"   First 3 tests:")
        for test in task['FAIL_TO_PASS'][:3]:
            print(f"      - {test}")

def example_pattern_extraction():
    """Example 4: Identify potential patterns (for Q2)."""
    print("\n" + "=" * 80)
    print("Example 4: Pattern Extraction Hints (for Q2)")
    print("=" * 80)

    tasks = load_tasks()

    # Find tasks with common keywords in problem statement
    keywords = ['null', 'none', 'undefined', 'validation', 'type error']

    print(f"\n🔍 Common bug patterns:")
    for keyword in keywords:
        matching = [t for t in tasks if keyword in t['problem_statement'].lower()]
        print(f"   '{keyword}': {len(matching)} tasks")

    # Example null-related task
    null_tasks = [t for t in tasks if 'null' in t['problem_statement'].lower() or 'none' in t['problem_statement'].lower()]
    if null_tasks:
        task = null_tasks[0]
        print(f"\n📝 Example null/None-related task:")
        print(f"   ID: {task['instance_id']}")
        print(f"   Problem snippet: {task['problem_statement'][:200]}...")

def example_scope_analysis():
    """Example 5: Analyze file scope (for Q1 Scope Guard)."""
    print("\n" + "=" * 80)
    print("Example 5: Scope Analysis (for Q1 Scope Guard)")
    print("=" * 80)

    tasks = load_tasks()

    # Analyze patch sizes (ground truth)
    patch_file_counts = []
    for task in tasks:
        if 'patch' in task:
            # Count files in patch (simple heuristic: count 'diff --git')
            files = task['patch'].count('diff --git')
            patch_file_counts.append(files)

    print(f"\n📄 Ground truth patch file counts:")
    print(f"   Mean files modified: {sum(patch_file_counts) / len(patch_file_counts):.2f}")
    print(f"   Min: {min(patch_file_counts)}, Max: {max(patch_file_counts)}")

    # Distribution
    single_file = sum(1 for c in patch_file_counts if c == 1)
    multi_file = sum(1 for c in patch_file_counts if c > 1)

    print(f"\n   Single-file fixes: {single_file} tasks ({single_file/len(tasks)*100:.1f}%)")
    print(f"   Multi-file fixes:  {multi_file} tasks ({multi_file/len(tasks)*100:.1f}%)")

    print(f"\n💡 Insight for Q1 Scope Guard:")
    print(f"   Most fixes are single-file ({single_file/len(tasks)*100:.1f}%)")
    print(f"   → Agent modifying >3 files is likely drift!")

def main():
    """Run all examples."""
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "SWE-bench Data Examples" + " " * 35 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        example_basic_stats()
        example_filter_by_difficulty()
        example_test_analysis()
        example_pattern_extraction()
        example_scope_analysis()

        print("\n" + "=" * 80)
        print("✅ All examples complete!")
        print("=" * 80)
        print("\n📖 Next steps:")
        print("   1. Review DATA_GUIDE.md for detailed usage")
        print("   2. Start implementing Q1 baseline")
        print("   3. Use these patterns to inform your guard design")

    except FileNotFoundError:
        print(f"\n❌ Error: {DATA_FILE} not found")
        print("\n   Run: python scripts/download_swebench.py")

if __name__ == "__main__":
    main()
