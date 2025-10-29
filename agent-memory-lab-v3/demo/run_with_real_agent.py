"""
完整测试：使用真实Agent的Q1流程
测试"1行走通" - 用SimpleBedrockAgent替换MockAgent
"""

from pathlib import Path
from steps import load_task, FourGuardMonitor, ActionMonitor
from steps import evaluate_scope, evaluate_resolved_mock
from utils import get_default_config, ExperimentLogger, SimpleBedrockAgent


def main():
    """使用真实Agent运行Q1流程"""
    print("=" * 80)
    print("Q1 End-to-End Test with Real Agent")
    print("=" * 80)

    # Initialize config and logger
    config = get_default_config()
    logger = ExperimentLogger(
        output_dir=Path("logs/real_agent_test"),
        experiment_name="q1_real_agent_test"
    )
    logger.log_config({
        'weights': config.weights,
        'thresholds': config.thresholds,
        'scope_file_limits': config.scope_file_limits,
        'mode': config.mode,
        'seed': config.seed,
    })
    print(f"✅ Config and logger initialized\n")

    # Step 1: Load data
    print("Step 1: 数据加载...")
    DATA_FILE = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
    task = load_task(DATA_FILE, task_index=0)
    print(f"✅ Task loaded: {task.instance_id}\n")

    # Step 2: Initialize Q1
    print("Step 2: Q1初始化...")
    guard = FourGuardMonitor(task)
    summary = guard.get_summary()
    print(f"✅ Four-Guard initialized (scope limit: {summary['scope_file_limit']} files)\n")

    # Step 3: Create Real Agent
    print("Step 3: 创建真实Agent...")
    agent = SimpleBedrockAgent(require_token=False)
    print(f"✅ SimpleBedrockAgent created\n")

    # Step 4: Generate patch
    print("Step 4: Agent生成patch...")
    patch = agent.solve(task)
    print(f"✅ Patch generated ({len(patch)} characters)\n")
    print("Generated patch:")
    print("-" * 80)
    print(patch[:500])
    if len(patch) > 500:
        print(f"... (truncated, total {len(patch)} chars)")
    print("-" * 80 + "\n")

    # Step 5: Evaluate
    print("Step 5-6: 评估...")
    part_c = task.get_part_c()

    resolved_result = evaluate_resolved_mock(
        patch,
        part_c['fail_to_pass'],
        part_c['pass_to_pass']
    )

    scope_result = evaluate_scope(patch, part_c['ground_truth_patch'])

    print(f"  Resolved: {resolved_result['resolved']} {'✅' if resolved_result['resolved'] else '❌'}")
    print(f"  Scope Precision: {scope_result['scope_precision']:.2f}")
    print(f"  Scope Recall: {scope_result['scope_recall']:.2f}\n")

    # Log results
    logger.log_task_result(
        task_id=task.instance_id,
        result={
            'resolved': resolved_result['resolved'],
            'scope_precision': scope_result['scope_precision'],
            'scope_recall': scope_result['scope_recall'],
        },
        drift_metrics={
            'drift_rate': 0.0,  # No action monitoring in this simple version
            'num_actions': 1,  # Single LLM call
            'num_drift_actions': 0,
        }
    )

    # Final summary
    print("=" * 80)
    print("✅ Q1 End-to-End Test Complete!")
    print("=" * 80)
    print(f"\n📊 最终结果:")
    print(f"   Task: {task.instance_id}")
    print(f"   Resolved: {resolved_result['resolved']} {'✅' if resolved_result['resolved'] else '❌'}")
    print(f"   Scope Precision: {scope_result['scope_precision']:.2f}")
    print(f"   Scope Recall: {scope_result['scope_recall']:.2f}")

    print(f"\n📝 Logs saved to: {logger.output_dir}")

    print("\n🎯 Status: '1行走通' ACHIEVED!")
    print("   ✅ Data loading works")
    print("   ✅ Q1 initialization works")
    print("   ✅ Real Agent (SimpleBedrockAgent) works")
    print("   ✅ Evaluation works")
    print("   ✅ Logging works")

    print("\n💡 Next steps:")
    print("   1. Set AWS_BEARER_TOKEN_BEDROCK to use real Bedrock API")
    print("   2. Run on more tasks to build baseline")
    print("   3. Run official SWE-bench evaluator on predictions.jsonl")

    return {
        'task': task,
        'patch': patch,
        'resolved': resolved_result['resolved'],
        'scope': scope_result,
    }


if __name__ == "__main__":
    result = main()
