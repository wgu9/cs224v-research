#!/usr/bin/env python3
"""
Aggregate drift analysis across multiple sessions.

Reads all summary.json files from data/2_runs/ and generates
an aggregate report showing drift patterns, health distribution,
and guard failure statistics across all sessions.

**LLM Usage**: ❌ NO LLM CALLS
  - Pure statistical aggregation

**Usage**: Run with runner.sh
  ./runner.sh python tools/analyze_drift_summary.py [data/2_runs]
"""

import sys
import json
import pathlib
from typing import List, Dict, Any
from collections import Counter, defaultdict


def load_all_summaries(runs_dir: pathlib.Path) -> List[Dict[str, Any]]:
    """Load all summary.json files from runs directory."""
    summaries = []

    for session_dir in runs_dir.iterdir():
        if not session_dir.is_dir():
            continue

        summary_path = session_dir / "summary.json"
        if not summary_path.exists():
            continue

        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                summary = json.load(f)
                summaries.append(summary)
        except Exception as e:
            print(f"⚠️  Failed to load {summary_path}: {e}")

    return summaries


def analyze_aggregate(summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregate statistics across all sessions."""

    if not summaries:
        return {"error": "No summaries found"}

    total_sessions = len(summaries)
    total_queries = sum(s.get('total_queries', 0) for s in summaries)
    total_successful = sum(s.get('successful_queries', 0) for s in summaries)
    total_failed = sum(s.get('failed_queries', 0) for s in summaries)

    # Drift statistics
    queries_with_drift = sum(s.get('queries_with_drift', 0) for s in summaries)
    overall_drift_rate = queries_with_drift / total_successful if total_successful > 0 else 0

    # Collect drift scores
    all_drift_scores = []
    for s in summaries:
        for query in s.get('queries', []):
            all_drift_scores.extend(query.get('drift_scores', []))

    avg_drift = sum(all_drift_scores) / len(all_drift_scores) if all_drift_scores else 0
    max_drift = max(all_drift_scores) if all_drift_scores else 0

    # Health distribution
    health_counts = Counter(s.get('health', 'unknown') for s in summaries)

    # Guard failures aggregation
    total_guard_failures = defaultdict(int)
    for s in summaries:
        gf = s.get('by_guard_failed', {})
        for guard, count in gf.items():
            total_guard_failures[guard] += count

    # Action mix aggregation
    total_actions = defaultdict(int)
    for s in summaries:
        actions = s.get('action_mix', {})
        for action, count in actions.items():
            total_actions[action] += count

    # Top problematic sessions
    sessions_by_drift = sorted(
        summaries,
        key=lambda s: s.get('max_drift', 0),
        reverse=True
    )
    top_problematic = sessions_by_drift[:5]

    return {
        "total_sessions": total_sessions,
        "total_queries": total_queries,
        "successful_queries": total_successful,
        "failed_queries": total_failed,

        "drift_statistics": {
            "queries_with_drift": queries_with_drift,
            "overall_drift_rate": round(overall_drift_rate, 3),
            "avg_drift": round(avg_drift, 3),
            "max_drift": round(max_drift, 3)
        },

        "health_distribution": dict(health_counts),

        "guard_failures": dict(total_guard_failures),

        "action_distribution": dict(total_actions),

        "top_problematic_sessions": [
            {
                "session_id": s.get('session_id'),
                "max_drift": s.get('max_drift'),
                "drift_rate": s.get('drift_rate'),
                "health": s.get('health')
            }
            for s in top_problematic
        ]
    }


def print_report(analysis: Dict[str, Any]):
    """Print a human-readable report."""

    if "error" in analysis:
        print(f"❌ Error: {analysis['error']}")
        return

    print("=" * 80)
    print("📊 AGGREGATE DRIFT ANALYSIS REPORT")
    print("=" * 80)

    print(f"\n📁 Overview:")
    print(f"   - Total Sessions: {analysis['total_sessions']}")
    print(f"   - Total Queries: {analysis['total_queries']}")
    print(f"   - Successful: {analysis['successful_queries']}")
    print(f"   - Failed: {analysis['failed_queries']}")

    drift = analysis['drift_statistics']
    print(f"\n📈 Drift Statistics:")
    print(f"   - Queries with Drift: {drift['queries_with_drift']}")
    print(f"   - Overall Drift Rate: {drift['overall_drift_rate']:.1%}")
    print(f"   - Avg Drift Score: {drift['avg_drift']:.3f}")
    print(f"   - Max Drift Score: {drift['max_drift']:.3f}")

    health_dist = analysis['health_distribution']
    print(f"\n🏥 Health Distribution:")
    for health, count in sorted(health_dist.items()):
        emoji = {"green": "✅", "yellow": "⚠️", "red": "🔴"}.get(health, "❓")
        pct = count / analysis['total_sessions'] * 100
        print(f"   {emoji} {health.upper()}: {count} ({pct:.1f}%)")

    guard_failures = analysis['guard_failures']
    total_failures = sum(guard_failures.values())
    if total_failures > 0:
        print(f"\n🛡️  Guard Failures (Total: {total_failures}):")
        for guard in ['scope', 'plan', 'test', 'evidence']:
            count = guard_failures.get(guard, 0)
            pct = count / total_failures * 100 if total_failures > 0 else 0
            print(f"   - {guard.capitalize()}: {count} ({pct:.1f}%)")

    actions = analysis['action_distribution']
    total_actions = sum(actions.values())
    if total_actions > 0:
        print(f"\n⚡ Action Distribution (Total: {total_actions}):")
        for action in ['ok', 'warn', 'rollback']:
            count = actions.get(action, 0)
            pct = count / total_actions * 100 if total_actions > 0 else 0
            print(f"   - {action.upper()}: {count} ({pct:.1f}%)")

    problematic = analysis['top_problematic_sessions']
    if problematic and problematic[0].get('max_drift', 0) > 0:
        print(f"\n⚠️  Top Problematic Sessions:")
        for i, s in enumerate(problematic[:3], 1):
            if s.get('max_drift', 0) > 0:
                print(f"   {i}. {s['session_id']}")
                print(f"      Max Drift: {s['max_drift']:.3f}, "
                      f"Drift Rate: {s['drift_rate']:.1%}, "
                      f"Health: {s['health']}")

    print(f"\n{'=' * 80}")


def main():
    """Command line entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Aggregate drift analysis across sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze all sessions in data/2_runs
  python tools/analyze_drift_summary.py

  # Analyze specific runs directory
  python tools/analyze_drift_summary.py my_runs/

  # Save report to file
  python tools/analyze_drift_summary.py --output report.json
        """
    )

    parser.add_argument(
        'runs_dir',
        nargs='?',
        default='data/2_runs',
        help='Runs directory containing session summaries (default: data/2_runs)'
    )

    parser.add_argument(
        '--output',
        '-o',
        help='Save JSON report to file'
    )

    args = parser.parse_args()

    runs_dir = pathlib.Path(args.runs_dir)
    if not runs_dir.exists():
        print(f"❌ Error: Directory not found: {runs_dir}")
        sys.exit(1)

    print(f"📂 Loading summaries from: {runs_dir}")
    summaries = load_all_summaries(runs_dir)

    if not summaries:
        print(f"❌ No summary.json files found in {runs_dir}")
        print(f"\n💡 Tip: Run Q1 analysis first:")
        print(f"   ./runner.sh python tools/run_q1_batch.py data/1_sessions/s_xxx")
        sys.exit(1)

    print(f"✅ Loaded {len(summaries)} sessions\n")

    analysis = analyze_aggregate(summaries)

    print_report(analysis)

    if args.output:
        output_path = pathlib.Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Report saved to: {output_path}")


if __name__ == "__main__":
    main()
