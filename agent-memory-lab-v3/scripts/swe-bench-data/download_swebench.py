#!/usr/bin/env python3
# 该脚本用于下载 SWE-bench 数据集到本地。
# 根据项目需求下载 Verified 和 Train 数据集，可选下载 Lite 版本用于快速测试。
# 数据将从 HuggingFace 加载并保存为 JSONL 格式。
"""
Download SWE-bench datasets for the project.

According to proposal:
- SWE-bench Verified (500) for final evaluation
- SWE-bench Train split for Q2 pattern extraction
"""

import json
from pathlib import Path
from datasets import load_dataset

# Setup directories
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "swebench"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def download_verified():
    """Download SWE-bench Verified (500 tasks)."""
    print("📥 Downloading SWE-bench Verified (500 tasks)...")

    # Load from HuggingFace
    dataset = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")

    # Save to JSONL
    output_file = DATA_DIR / "verified.jsonl"
    with open(output_file, "w") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")

    print(f"✅ Saved {len(dataset)} tasks to {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")

    # Print first example
    print("\n📋 First task preview:")
    first_task = dataset[0]
    print(f"   Instance ID: {first_task['instance_id']}")
    print(f"   Repo: {first_task['repo']}")
    print(f"   Problem: {first_task['problem_statement'][:100]}...")

    return dataset

def download_train():
    """Download SWE-bench Train split for Q2 pattern extraction."""
    print("\n📥 Downloading SWE-bench Train split...")

    # Load from HuggingFace
    dataset = load_dataset("princeton-nlp/SWE-bench", split="train")

    # Save to JSONL
    output_file = DATA_DIR / "train.jsonl"
    with open(output_file, "w") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")

    print(f"✅ Saved {len(dataset)} tasks to {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")

    return dataset

def download_lite():
    """Download SWE-bench Lite (optional, for quick testing)."""
    print("\n📥 Downloading SWE-bench Lite (300 tasks, optional)...")

    # Load from HuggingFace
    dataset = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")

    # Save to JSONL
    output_file = DATA_DIR / "lite.jsonl"
    with open(output_file, "w") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")

    print(f"✅ Saved {len(dataset)} tasks to {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")

    return dataset

def analyze_verified(dataset):
    """Analyze Verified dataset for difficulty distribution."""
    print("\n📊 SWE-bench Verified Analysis:")

    # Check for difficulty labels
    if 'FAIL_TO_PASS' in dataset[0]:
        print(f"   ✅ Has FAIL_TO_PASS field")
    if 'PASS_TO_PASS' in dataset[0]:
        print(f"   ✅ Has PASS_TO_PASS field")

    # Repository distribution
    repos = {}
    for item in dataset:
        repo = item['repo']
        repos[repo] = repos.get(repo, 0) + 1

    print(f"\n   Top repositories:")
    for repo, count in sorted(repos.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {repo}: {count} tasks")

    # Key fields check
    print(f"\n   Available fields:")
    for key in sorted(dataset[0].keys()):
        print(f"   - {key}")

def main():
    print("=" * 60)
    print("SWE-bench Data Download Script")
    print("=" * 60)

    # Download datasets
    verified = download_verified()
    train = download_train()

    # Optional: Lite for quick testing
    print("\n" + "=" * 60)
    response = input("Download SWE-bench Lite (300 tasks) for quick testing? [y/N]: ")
    if response.lower() == 'y':
        lite = download_lite()

    # Analyze
    analyze_verified(verified)

    # Summary
    print("\n" + "=" * 60)
    print("✅ Download Complete!")
    print("=" * 60)
    print(f"\nData saved to: {DATA_DIR}")
    print("\nFiles:")
    print(f"  - verified.jsonl  : 500 tasks (primary evaluation)")
    print(f"  - train.jsonl     : ~2,294 tasks (Q2 pattern extraction)")
    if (DATA_DIR / "lite.jsonl").exists():
        print(f"  - lite.jsonl      : 300 tasks (optional, quick testing)")

    print("\n📖 Next steps:")
    print("  1. Inspect data with: python scripts/inspect_swebench.py")
    print("  2. Run baseline: python scripts/run_baseline.py")

if __name__ == "__main__":
    main()
