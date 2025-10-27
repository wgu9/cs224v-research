# Fix Python module import error
_Exported on 10/26/2025 at 10:29:00 PDT from Cursor (1.7.53)_

---

**User**

fix this. do you know the problem? 

python tools/run_q1_batch.py data/1_sessions/s_2025-10-26-10-20-36_cursor
Traceback (most recent call last):
  File "/Users/jeremy/Dropbox/cs224v-project/cs224v-research/agent-memory-lab-v3/tools/run_q1_batch.py", line 20, in <module>
    from tools import chat2events, events2guards
ModuleNotFoundError: No module named 'tools'

---

**Cursor**


Reading the script to diagnose the import issue.


The script is in `tools/` and tries to import from `tools`, but Python can't find the package. Adding the parent directory to `sys.path` before the imports:


```python
#!/usr/bin/env python3
"""
Main entry point for running Q1 drift analysis in batch on a pre-processed session.

This script reads a session directory created by `process_long_conversation.py`,
iterates through all sub-tasks (queries), and orchestrates the full Q1 
analysis pipeline (`chat2events` -> `events2guards`) for each one. It saves 
the final analysis results in the `data/2_runs` directory.
"""

import sys
import json
import pathlib
import subprocess
import argparse
import os
from typing import List, Dict, Any

# Add parent directory to path to allow imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from tools import chat2events, events2guards

def run_q1_analysis(
    session_dir: pathlib.Path,
    query_id: str,
    output_dir: pathlib.Path
) -> Dict[str, Any]:
    """
    对单个query运行Q1分析

    Args:
        session_dir: Session目录路径
        query_id: Query ID (如 'q01')
        output_dir: 输出根目录 (data/2_runs)

    Returns:
        分析结果摘要
    """
    query_dir = session_dir / 'pairs' / query_id
    goal_path = query_dir / 'goal.json'
    chat_path = query_dir / 'chat.md'

    # 验证文件存在
    if not goal_path.exists():
        return {"error": f"goal.json not found in {query_dir}"}
    if not chat_path.exists():
        return {"error": f"chat.md not found in {query_dir}"}

    # 读取goal.json获取run_id
    with open(goal_path) as f:
        goal = json.load(f)

    run_id = goal.get('run_id', f"{session_dir.name}_{query_id}")

    # 创建run目录
    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # 创建raw子目录
    raw_dir = run_dir / 'raw'
    raw_dir.mkdir(exist_ok=True)

    # 复制文件到run目录
    import shutil
    shutil.copy(goal_path, run_dir / 'goal.json')
    shutil.copy(chat_path, raw_dir / 'cursor.md')

    print(f"   📁 Created run directory: {run_dir.relative_to(output_dir.parent)}")

    # Step 1: Run chat2events
    print(f"   🔄 Running chat2events...")
    try:
        chat2events.main(str(run_dir))
        print(f"   ✅ Events extracted")
    except Exception as e:
        print(f"   ❌ chat2events error: {e}")
        return {"error": f"chat2events error: {e}"}

    # Step 2: Run events2guards
    print(f"   🛡️  Running events2guards...")
    try:
        events2guards.main(str(run_dir))
        print(f"   ✅ Guards calculated")
    except Exception as e:
        print(f"   ❌ events2guards error: {e}")
        return {"error": f"events2guards error: {e}"}

    # 读取结果统计
    guards_path = run_dir / 'guards.jsonl'

    if not guards_path.exists():
        return {"error": "guards.jsonl not generated"}

    # 统计drift
    drift_count = 0
    warn_count = 0
    rollback_count = 0

    with open(guards_path) as f:
        for line in f:
            guard = json.loads(line)
            action = guard.get('action', 'ok')
            if action == 'warn':
                warn_count += 1
                drift_count += 1
            elif action == 'rollback':
                rollback_count += 1
                drift_count += 1

    return {
        "run_id": run_id,
        "query_id": query_id,
        "status": "success",
        "drift_events": drift_count,
        "warnings": warn_count,
        "rollbacks": rollback_count
    }


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="批量运行Q1分析",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 分析整个session
  python tools/run_q1_batch.py data/1_sessions/s_2025-10-26-10-00-00_cursor

  # 只分析特定queries
  python tools/run_q1_batch.py data/1_sessions/s_2025-10-26-10-00-00_cursor --queries q01,q02

  # 指定输出目录
  python tools/run_q1_batch.py data/1_sessions/s_2025-10-26-10-00-00_cursor --output data/my_runs
        """
    )

    parser.add_argument(
        'session_dir',
        help='Session目录路径 (如 data/1_sessions/s_2025-10-26-10-00-00_cursor)'
    )
    parser.add_argument(
        '--queries',
        help='逗号分隔的query IDs (如 q01,q02,q03)。不指定则处理所有queries',
        default=None
    )
    parser.add_argument(
        '--output',
        help='输出目录 (默认: data/2_runs)',
        default='data/2_runs'
    )

    args = parser.parse_args()

    # 验证session目录
    session_dir = pathlib.Path(args.session_dir)
    if not session_dir.exists():
        print(f"❌ Error: Session directory not found: {session_dir}")
        sys.exit(1)

    pairs_dir = session_dir / 'pairs'
    if not pairs_dir.exists():
        print(f"❌ Error: pairs/ directory not found in {session_dir}")
        sys.exit(1)

    # 获取query列表
    if args.queries:
        query_ids = [q.strip() for q in args.queries.split(',')]
    else:
        # 自动发现所有queries
        query_dirs = sorted(pairs_dir.glob('q*'))
        query_ids = [d.name for d in query_dirs if d.is_dir()]

    if not query_ids:
        print(f"❌ Error: No queries found in {pairs_dir}")
        sys.exit(1)

    output_dir = pathlib.Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 开始批处理
    print(f"🚀 Starting Q1 Batch Analysis")
    print(f"=" * 80)
    print(f"📁 Session: {session_dir}")
    print(f"📊 Queries: {len(query_ids)}")
    print(f"💾 Output: {output_dir}")
    print(f"=" * 80)

    results = []

    for i, query_id in enumerate(query_ids, 1):
        print(f"\n{'=' * 60}")
        print(f"Processing {i}/{len(query_ids)}: {query_id}")
        print(f"{'=' * 60}")

        result = run_q1_analysis(session_dir, query_id, output_dir)
        results.append(result)

        if 'error' in result:
            print(f"   ❌ Failed: {result['error']}")
        else:
            status_emoji = "✅" if result['drift_events'] == 0 else "⚠️"
            print(f"   {status_emoji} Completed")
            if result['drift_events'] > 0:
                print(f"      - Drift Events: {result['drift_events']}")
                print(f"      - Warnings: {result['warnings']}")
                print(f"      - Rollbacks: {result['rollbacks']}")

    # 最终总结
    print(f"\n{'=' * 80}")
    print(f"✅ Q1 BATCH ANALYSIS COMPLETE")
    print(f"{'=' * 80}")

    successful = [r for r in results if 'error' not in r]
    failed = [r for r in results if 'error' in r]
    drift_detected = [r for r in successful if r.get('drift_events', 0) > 0]

    print(f"📊 Summary:")
    print(f"   - Total Queries: {len(results)}")
    print(f"   - Successful: {len(successful)}")
    print(f"   - Failed: {len(failed)}")
    print(f"   - Drift Detected: {len(drift_detected)}")

    if drift_detected:
        print(f"\n⚠️  Queries with Drift:")
        for r in drift_detected:
            print(f"   - {r['query_id']}: {r['drift_events']} events "
                  f"({r['warnings']} warns, {r['rollbacks']} rollbacks)")

    # 保存summary
    summary_path = output_dir / f"{session_dir.name}_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Summary saved: {summary_path}")

    # 退出码
    if failed:
        print(f"\n⚠️  Warning: {len(failed)} queries failed")
        sys.exit(1)
    else:
        print(f"\n🎉 All queries processed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()

```

Added the parent directory to `sys.path` so Python can find the `tools` module.

When running `python tools/run_q1_batch.py`, Python couldn't find `tools`. Appending the project root to `sys.path` enables the import.

The command should work now:
```bash
python tools/run_q1_batch.py data/1_sessions/s_2025-10-26-10-20-36_cursor
```

```shellscript
python tools/run_q1_batch.py data/1_sessions/s_2025-10-26-10-20-36_cursor
```

