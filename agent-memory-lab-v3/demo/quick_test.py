"""
快速测试：验证所有步骤都能正常运行
不需要用户交互，自动运行所有步骤
"""

from pathlib import Path
from step1_load_data import load_task
from step2_init_guards import FourGuardMonitor
from step3_mock_agent import MockAgent
from step4_monitor_actions import ActionMonitor
from step5_evaluate import evaluate_scope, evaluate_resolved_mock


def main():
    """快速测试所有步骤"""
    print("=" * 80)
    print("Q1 Quick Test - 验证所有步骤正常运行")
    print("=" * 80)

    DATA_FILE = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"

    try:
        # Step 1
        print("\n✓ Step 1: 数据加载...")
        task = load_task(DATA_FILE, task_index=0)
        print(f"  Task: {task.instance_id}")

        # Step 2
        print("\n✓ Step 2: Four-Guard初始化...")
        guard = FourGuardMonitor(task)
        summary = guard.get_summary()
        print(f"  Scope limit: {summary['scope_file_limit']} files")

        # Step 3
        print("\n✓ Step 3: Mock Agent执行...")
        agent = MockAgent(task.problem_statement, task.repo)
        result = agent.execute()
        print(f"  Actions: {len(result['actions'])}")

        # Step 4
        print("\n✓ Step 4: 实时监控...")
        monitor = ActionMonitor(guard)
        monitoring_results = []

        for idx, action in enumerate(result['actions'], 1):
            guard.action_history.append(action)
            monitor_result = monitor.monitor_action(action, idx)
            monitoring_results.append(monitor_result)

        drift_rate = sum(1 for r in monitoring_results if r['drift_score'] >= 0.5) / len(monitoring_results)
        print(f"  Drift rate: {drift_rate*100:.1f}%")

        # Step 5-6
        print("\n✓ Step 5-6: 事后评估...")
        part_c = task.get_part_c()

        resolved_result = evaluate_resolved_mock(
            result['patch'],
            part_c['fail_to_pass'],
            part_c['pass_to_pass']
        )

        scope_result = evaluate_scope(result['patch'], part_c['ground_truth_patch'])

        print(f"  Resolved: {resolved_result['resolved']}")
        print(f"  Scope Precision: {scope_result['scope_precision']:.2f}")
        print(f"  Scope Recall: {scope_result['scope_recall']:.2f}")

        # 总结
        print("\n" + "=" * 80)
        print("✅ 所有测试通过！")
        print("=" * 80)

        print("\n📊 最终结果:")
        print(f"   Task: {task.instance_id}")
        print(f"   Resolved: {resolved_result['resolved']} {'✅' if resolved_result['resolved'] else '❌'}")
        print(f"   Drift Rate: {drift_rate*100:.1f}% {'✅' if drift_rate < 0.15 else '⚠️'}")
        print(f"   Scope Precision: {scope_result['scope_precision']:.2f}")
        print(f"   Scope Recall: {scope_result['scope_recall']:.2f}")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
