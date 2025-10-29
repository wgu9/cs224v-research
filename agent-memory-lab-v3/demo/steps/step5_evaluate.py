"""
Step 5-6: 事后评估
对比agent的结果与ground truth，计算resolve rate和scope metrics
"""

import re
from typing import Set, Dict, Any
from pathlib import Path
from step1_load_data import load_task


def extract_files_from_patch(patch: str) -> Set[str]:
    """
    从git diff patch中提取修改的文件列表

    Args:
        patch: git diff格式的patch

    Returns:
        修改的文件路径集合
    """
    # 匹配 "diff --git a/path/to/file.py b/path/to/file.py"
    pattern = r'diff --git a/(.*?) b/'
    files = set(re.findall(pattern, patch))
    return files


def evaluate_scope(agent_patch: str, ground_truth_patch: str) -> Dict[str, Any]:
    """
    评估Scope对齐情况（对比ground truth）

    Args:
        agent_patch: agent生成的patch
        ground_truth_patch: 标准答案patch

    Returns:
        Scope评估结果（precision, recall等）
    """
    # 提取文件列表
    gold_files = extract_files_from_patch(ground_truth_patch)
    agent_files = extract_files_from_patch(agent_patch)

    if not agent_files:
        return {
            'scope_precision': 0.0,
            'scope_recall': 0.0,
            'gold_files': list(gold_files),
            'agent_files': [],
            'extra_files': [],
            'missed_files': list(gold_files),
        }

    # 计算Precision和Recall
    true_positives = len(gold_files & agent_files)

    precision = true_positives / len(agent_files) if agent_files else 0.0
    recall = true_positives / len(gold_files) if gold_files else 0.0

    return {
        'scope_precision': precision,
        'scope_recall': recall,
        'gold_files': list(gold_files),
        'agent_files': list(agent_files),
        'extra_files': list(agent_files - gold_files),  # agent多改的
        'missed_files': list(gold_files - agent_files),  # agent漏改的
    }


def evaluate_resolved_mock(agent_patch: str, fail_to_pass: list, pass_to_pass: list) -> Dict[str, Any]:
    """
    Mock版本的resolved评估

    注意：实际应该使用SWE-bench官方evaluator在Docker中运行测试
    这里是简化版mock，只比较patch是否合理

    Args:
        agent_patch: agent生成的patch
        fail_to_pass: 必须通过的测试列表
        pass_to_pass: 必须保持通过的测试列表

    Returns:
        评估结果
    """
    # Mock: 简化版判断（实际需要运行测试）
    # 这里假设如果patch不为空且修改了文件，就算部分成功

    has_changes = bool(extract_files_from_patch(agent_patch))

    # Mock resolved判断
    # 实际应该是: 运行FAIL_TO_PASS和PASS_TO_PASS测试，全部通过才算resolved
    resolved = has_changes  # 简化版：有改动就算成功

    return {
        'resolved': resolved,
        'f2p_total': len(fail_to_pass),
        'f2p_passed': len(fail_to_pass) if resolved else 0,  # Mock
        'p2p_total': len(pass_to_pass),
        'p2p_passed': len(pass_to_pass) if resolved else 0,  # Mock
        'note': 'This is a MOCK evaluation. Real evaluation requires SWE-bench Docker evaluator.'
    }


def main():
    """演示事后评估流程"""
    DATA_FILE = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"

    print("=" * 80)
    print("Step 5-6: 事后评估 (与Ground Truth对比)")
    print("=" * 80)

    # 1. 加载任务
    print("\n📂 Loading task...")
    task = load_task(DATA_FILE, task_index=0)

    # 2. 获取Part C（评估用数据）
    part_c = task.get_part_c()

    print(f"✅ Task: {task.instance_id}")
    print(f"   FAIL_TO_PASS tests: {len(part_c['fail_to_pass'])}")
    print(f"   PASS_TO_PASS tests: {len(part_c['pass_to_pass'])}")

    # 3. 模拟agent生成的patch（实际来自step3的agent）
    # 这里使用一个与ground truth相同的patch作为示例
    agent_patch = part_c['ground_truth_patch']  # Mock: 假设agent生成了正确的patch

    print("\n" + "=" * 80)
    print("📊 评估1: 功能正确性 (Resolved)")
    print("=" * 80)

    # 评估resolved（mock版本）
    resolved_result = evaluate_resolved_mock(
        agent_patch,
        part_c['fail_to_pass'],
        part_c['pass_to_pass']
    )

    print(f"\n⚠️  {resolved_result['note']}")
    print(f"\n✅ Resolved: {resolved_result['resolved']}")
    print(f"   FAIL_TO_PASS: {resolved_result['f2p_passed']}/{resolved_result['f2p_total']} passed")
    print(f"   PASS_TO_PASS: {resolved_result['p2p_passed']}/{resolved_result['p2p_total']} passed")

    print("\n💡 实际评估流程:")
    print("   1. 使用SWE-bench官方Docker evaluator")
    print("   2. 准备predictions.jsonl:")
    print('      {"instance_id": "django__django-11119", "model_patch": "..."}')
    print("   3. 运行评估器:")
    print("      python -m swebench.harness.run_evaluation \\")
    print("        --predictions_path predictions.jsonl \\")
    print("        --swe_bench_tasks verified.jsonl \\")
    print("        --log_dir logs/")
    print("   4. 得到resolve_rate（% tasks通过所有测试）")

    # 4. Scope分析
    print("\n" + "=" * 80)
    print("📊 评估2: Scope对齐分析")
    print("=" * 80)

    scope_result = evaluate_scope(agent_patch, part_c['ground_truth_patch'])

    print(f"\n📁 Ground truth修改的文件:")
    for f in scope_result['gold_files']:
        print(f"   • {f}")

    print(f"\n📁 Agent修改的文件:")
    for f in scope_result['agent_files']:
        print(f"   • {f}")

    print(f"\n📏 Scope Metrics:")
    print(f"   Precision: {scope_result['scope_precision']:.2f}")
    print(f"   Recall: {scope_result['scope_recall']:.2f}")

    if scope_result['extra_files']:
        print(f"\n⚠️  Agent多改的文件:")
        for f in scope_result['extra_files']:
            print(f"   • {f}")

    if scope_result['missed_files']:
        print(f"\n⚠️  Agent漏改的文件:")
        for f in scope_result['missed_files']:
            print(f"   • {f}")

    # 5. 综合评估
    print("\n" + "=" * 80)
    print("📊 综合评估结果")
    print("=" * 80)

    # 假设从step4得到的drift_rate
    mock_drift_rate = 0.0  # 这个例子是"完美"执行

    print(f"\n✅ Task: {task.instance_id}")
    print(f"   Difficulty: {task.difficulty}")
    print(f"\n结果:")
    print(f"   Resolved: {resolved_result['resolved']} {'✅' if resolved_result['resolved'] else '❌'}")
    print(f"   Scope Precision: {scope_result['scope_precision']:.2f} {'✅' if scope_result['scope_precision'] >= 0.8 else '⚠️'}")
    print(f"   Scope Recall: {scope_result['scope_recall']:.2f} {'✅' if scope_result['scope_recall'] >= 0.8 else '⚠️'}")
    print(f"   Drift Rate: {mock_drift_rate:.1%} {'✅' if mock_drift_rate < 0.15 else '⚠️'}")

    # 分类
    print(f"\n分类:")
    if resolved_result['resolved'] and mock_drift_rate < 0.15:
        print("   ⭐⭐⭐ 完美任务 - 功能对 + 过程优")
    elif resolved_result['resolved'] and mock_drift_rate >= 0.15:
        print("   ⭐⭐ 成功但曲折 - 功能对但过程drift高")
    elif not resolved_result['resolved'] and mock_drift_rate < 0.15:
        print("   ⭐ 失败但对齐 - 方向对但能力不足")
    else:
        print("   ❌ 双重失败 - 功能错 + 过程乱")

    print("\n" + "=" * 80)
    print("✅ Step 5-6 完成！评估完成")
    print("=" * 80)

    return {
        'resolved': resolved_result,
        'scope': scope_result,
        'drift_rate': mock_drift_rate,
    }


if __name__ == "__main__":
    result = main()
