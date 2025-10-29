#!/usr/bin/env python3
# 该脚本专门用于下载 SWE-bench 训练集（约 2,294 个任务），用于 Q2 的模式提取任务。
# 由于数据量较大，单独提供下载脚本便于按需下载。
# 训练集主要用于学习常见的代码修复模式和规律。
"""
Download SWE-bench train split for Q2 pattern extraction.
This is a separate script because it's larger (~2,294 tasks).
"""

import json
from pathlib import Path
from datasets import load_dataset

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "swebench"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("=" * 60)
    print("Downloading SWE-bench Train Split")
    print("=" * 60)
    print("\nThis will download ~2,294 tasks for Q2 pattern extraction.")
    print("Size: ~20-30MB, ETA: 1-2 minutes\n")

    # Load from HuggingFace
    print("📥 Loading from HuggingFace...")
    dataset = load_dataset("princeton-nlp/SWE-bench", split="train")

    # Save to JSONL
    output_file = DATA_DIR / "train.jsonl"
    print(f"💾 Saving to {output_file}...")

    with open(output_file, "w") as f:
        for i, item in enumerate(dataset):
            f.write(json.dumps(item) + "\n")
            if (i + 1) % 500 == 0:
                print(f"   Saved {i + 1}/{len(dataset)} tasks...")

    size_mb = output_file.stat().st_size / 1024 / 1024
    print(f"\n✅ Complete!")
    print(f"   Tasks: {len(dataset)}")
    print(f"   File: {output_file}")
    print(f"   Size: {size_mb:.2f} MB")

    # Show example
    print(f"\n📋 First task:")
    print(f"   Instance: {dataset[0]['instance_id']}")
    print(f"   Repo: {dataset[0]['repo']}")

if __name__ == "__main__":
    main()
