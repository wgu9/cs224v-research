#!/usr/bin/env python3
"""
Main entry point for running Q1 drift analysis in batch on a pre-processed session.

This script reads a session directory created by `process_long_conversation.py`,
iterates through all sub-tasks (queries), and orchestrates the full Q1
analysis pipeline (`chat2events` -> `events2guards`) for each one. It saves
the final analysis results in the `data/2_runs` directory.

**LLM Usage**: ❌ NO LLM CALLS
  - chat2events: Uses regex/heuristics only
  - events2guards: Uses rule-based logic only
  - All data generated from Step 1 (process_long_conversation.py) metadata

**Usage**: Run with runner.sh to ensure correct PYTHONPATH
  ./runner.sh python tools/run_q1_batch.py data/1_sessions/s_xxx
"""

import sys
import json
import pathlib
import subprocess
import argparse
import os
from typing import List, Dict, Any

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

    # 创建session级别的目录（与1_sessions结构一致）
    session_run_dir = output_dir / session_dir.name
    session_run_dir.mkdir(parents=True, exist_ok=True)

    # 创建query级别的run目录（使用query_id: q01, q02, ...）
    run_dir = session_run_dir / query_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # 创建raw子目录
    raw_dir = run_dir / 'raw'
    raw_dir.mkdir(exist_ok=True)

    # 复制文件到run目录
    import shutil
    shutil.copy(goal_path, run_dir / 'goal.json')
    shutil.copy(chat_path, raw_dir / 'cursor.md')

    # Display relative path from project root for clarity
    try:
        rel_path = run_dir.relative_to(pathlib.Path.cwd())
    except ValueError:
        rel_path = run_dir
    print(f"   📁 Created run directory: {rel_path}")

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

    # 统计drift（收集详细信息用于session-level统计）
    drift_count = 0
    warn_count = 0
    rollback_count = 0
    ok_count = 0

    drift_scores = []
    guard_failures = {
        "scope": 0,
        "plan": 0,
        "test": 0,
        "evidence": 0
    }

    with open(guards_path) as f:
        for line in f:
            guard = json.loads(line)
            action = guard.get('action', 'ok')
            drift_score = guard.get('drift_score', 0.0)

            drift_scores.append(drift_score)

            if action == 'warn':
                warn_count += 1
                drift_count += 1
            elif action == 'rollback':
                rollback_count += 1
                drift_count += 1
            else:
                ok_count += 1

            # 统计各守卫失败情况（score > 0表示失败）
            if guard.get('scope_guard', 0) > 0:
                guard_failures['scope'] += 1
            if guard.get('plan_guard', 0) > 0:
                guard_failures['plan'] += 1
            if guard.get('test_guard', 0) > 0:
                guard_failures['test'] += 1
            if guard.get('evidence_guard', 0) > 0:
                guard_failures['evidence'] += 1

    return {
        "run_id": run_id,
        "query_id": query_id,
        "status": "success",
        "drift_events": drift_count,
        "warnings": warn_count,
        "rollbacks": rollback_count,
        "ok_events": ok_count,

        # 新增：详细统计信息
        "drift_scores": drift_scores,
        "guard_failures": guard_failures
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

    # 先计算session-level统计，用于显示
    # 收集所有drift_scores
    all_drift_scores = []
    for r in successful:
        all_drift_scores.extend(r.get('drift_scores', []))

    avg_drift = sum(all_drift_scores) / len(all_drift_scores) if all_drift_scores else 0.0
    max_drift = max(all_drift_scores) if all_drift_scores else 0.0
    drift_rate = len(drift_detected) / len(successful) if successful else 0.0

    print(f"📊 Summary:")
    print(f"   - Total Queries: {len(results)}")
    print(f"   - Successful: {len(successful)}")
    print(f"   - Failed: {len(failed)}")
    print(f"   - Drift Detected: {len(drift_detected)}")
    print(f"\n📈 Session-Level Metrics:")
    print(f"   - Drift Rate: {drift_rate:.1%}")
    print(f"   - Avg Drift Score: {avg_drift:.3f}")
    print(f"   - Max Drift Score: {max_drift:.3f}")

    if drift_detected:
        print(f"\n⚠️  Queries with Drift:")
        for r in drift_detected:
            print(f"   - {r['query_id']}: {r['drift_events']} events "
                  f"({r['warnings']} warns, {r['rollbacks']} rollbacks)")

    # ============================================
    # 计算Session-Level统计（L的P0字段）
    # ============================================

    # 累加守卫失败和action计数
    total_guard_failures = {"scope": 0, "plan": 0, "test": 0, "evidence": 0}
    total_ok = 0
    total_warn = 0
    total_rollback = 0

    for r in successful:
        # 累加守卫失败计数
        gf = r.get('guard_failures', {})
        for guard in ['scope', 'plan', 'test', 'evidence']:
            total_guard_failures[guard] += gf.get(guard, 0)

        # 累加action计数
        total_ok += r.get('ok_events', 0)
        total_warn += r.get('warnings', 0)
        total_rollback += r.get('rollbacks', 0)

    # 计算健康等级（L的阈值）
    def calculate_health(drift_rate, max_drift, has_rollback):
        if has_rollback or drift_rate >= 0.3 or max_drift >= 0.6:
            return "red"
        elif drift_rate >= 0.1 or max_drift >= 0.4:
            return "yellow"
        else:
            return "green"

    health = calculate_health(drift_rate, max_drift, total_rollback > 0)

    # 显示health
    health_emoji = {"green": "✅", "yellow": "⚠️", "red": "🔴"}
    print(f"   - Health: {health_emoji.get(health, '')} {health.upper()}")

    # 构建增强的summary
    session_summary = {
        "session_id": session_dir.name,
        "total_queries": len(results),
        "successful_queries": len(successful),
        "failed_queries": len(failed),

        # L的P0字段
        "queries_with_drift": len(drift_detected),
        "drift_rate": round(drift_rate, 3),
        "avg_drift": round(avg_drift, 3),
        "max_drift": round(max_drift, 3),

        "action_mix": {
            "ok": total_ok,
            "warn": total_warn,
            "rollback": total_rollback
        },

        "by_guard_failed": total_guard_failures,

        "health": health,

        # 详细的per-query结果
        "queries": results
    }

    # 保存summary（在session目录下，与1_sessions结构一致）
    session_run_dir = output_dir / session_dir.name
    summary_path = session_run_dir / "summary.json"
    with open(summary_path, 'w') as f:
        json.dump(session_summary, f, indent=2, ensure_ascii=False)

    # Display relative path from project root
    try:
        rel_summary_path = summary_path.relative_to(pathlib.Path.cwd())
    except ValueError:
        rel_summary_path = summary_path
    print(f"\n💾 Summary saved: {rel_summary_path}")

    # Next Steps
    print(f"\n{'=' * 80}")
    print(f"🚀 NEXT STEPS")
    print(f"{'=' * 80}")
    print(f"\n1️⃣  Review individual query results:")
    for r in successful[:3]:  # Show first 3 as examples
        print(f"   cd data/2_runs/{session_dir.name}/{r['query_id']}")
        print(f"   cat guards.jsonl | head -5")
        print()

    print(f"2️⃣  Analyze drift patterns (if any):")
    if drift_detected:
        print(f"   # View queries with drift")
        for r in drift_detected:
            print(f"   cat data/2_runs/{session_dir.name}/{r['query_id']}/guards.jsonl | grep '\"action\": \"warn\"'")
    else:
        print(f"   ✅ No drift detected in this session!")

    print(f"\n3️⃣  Aggregate analysis across multiple sessions:")
    print(f"   # Process more cursor chats:")
    print(f"   ./runner.sh python tools/process_long_conversation.py another_chat.md")
    print(f"   ./runner.sh python tools/run_q1_batch.py data/1_sessions/s_<new_session>")
    print(f"")
    print(f"   # Then analyze all summaries:")
    print(f"   cat data/2_runs/*/summary.json | python -c \"")
    print(f"   import sys, json")
    print(f"   summaries = [json.load(open(f)) for f in sys.argv[1:]]")
    print(f"   # Calculate overall drift statistics")
    print(f"   \"")

    print(f"\n4️⃣  Export results for Q2 (pattern learning):")
    print(f"   # Coming soon: tools/export_for_q2.py")

    print(f"\n{'=' * 80}")

    # 退出码
    if failed:
        print(f"\n⚠️  Warning: {len(failed)} queries failed")
        sys.exit(1)
    else:
        print(f"\n🎉 All queries processed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
