"""
SWE-bench Evaluator Bridge
生成predictions.jsonl并提供官方evaluator使用说明
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from step1_load_data import SWEBenchTask


def prepare_predictions(
    tasks: List[SWEBenchTask],
    patches: List[str],
    output_file: Path
) -> None:
    """
    生成predictions.jsonl供SWE-bench官方evaluator使用

    Args:
        tasks: SWE-bench任务列表
        patches: 对应的agent生成的patch列表
        output_file: 输出文件路径
    """
    if len(tasks) != len(patches):
        raise ValueError(f"Tasks ({len(tasks)}) and patches ({len(patches)}) must have same length")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        for task, patch in zip(tasks, patches):
            prediction = {
                'instance_id': task.instance_id,
                'model_patch': patch,
                'model_name_or_path': 'q1-monitored-agent',  # 可自定义
            }
            f.write(json.dumps(prediction) + '\n')

    print(f"✅ Predictions saved to: {output_file}")
    print(f"   {len(tasks)} predictions written")


def print_evaluator_instructions(
    predictions_file: Path,
    swebench_file: Path,
    log_dir: Path
) -> None:
    """
    打印如何运行SWE-bench官方evaluator的说明

    Args:
        predictions_file: predictions.jsonl路径
        swebench_file: verified.jsonl路径
        log_dir: 日志输出目录
    """
    print("\n" + "=" * 80)
    print("📋 How to Run SWE-bench Official Evaluator")
    print("=" * 80)

    print("\n1. Install SWE-bench (if not already installed):")
    print("   ```bash")
    print("   git clone https://github.com/princeton-nlp/SWE-bench.git")
    print("   cd SWE-bench")
    print("   pip install -e .")
    print("   ```")

    print("\n2. Run evaluation:")
    print("   ```bash")
    print(f"   python -m swebench.harness.run_evaluation \\")
    print(f"       --predictions_path {predictions_file} \\")
    print(f"       --swe_bench_tasks {swebench_file} \\")
    print(f"       --log_dir {log_dir} \\")
    print(f"       --testbed /tmp/testbed")
    print("   ```")

    print("\n3. Wait for results (this may take a while):")
    print("   - Docker containers will be created for each task")
    print("   - Tests will be run automatically")
    print("   - Results saved to log_dir/")

    print("\n4. View results:")
    print(f"   ```bash")
    print(f"   cat {log_dir}/results.json")
    print("   ```")

    print("\n" + "=" * 80)
    print("💡 Expected output format:")
    print("=" * 80)
    print("""
{
    "instance_id": {
        "django__django-11119": true,
        "astropy__astropy-12907": false,
        ...
    },
    "resolved": {
        "count": 150,
        "percentage": 30.0
    }
}
""")

    print("\n⚠️  Important Notes:")
    print("   - Evaluation requires Docker")
    print("   - Each task takes ~2-5 minutes")
    print("   - 500 tasks ≈ 16-40 hours total")
    print("   - Can run in parallel with --num_workers")


def load_evaluation_results(results_file: Path) -> Dict[str, Any]:
    """
    加载SWE-bench evaluator的结果

    Args:
        results_file: 官方evaluator输出的results.json

    Returns:
        包含resolved状态的字典
    """
    if not results_file.exists():
        raise FileNotFoundError(
            f"Results file not found: {results_file}\n"
            f"Please run the official evaluator first (see print_evaluator_instructions)"
        )

    with open(results_file) as f:
        results = json.load(f)

    return results


def calculate_metrics(results: Dict[str, Any]) -> Dict[str, float]:
    """
    从evaluator结果计算metrics

    Args:
        results: 官方evaluator的输出

    Returns:
        包含resolve_rate等指标的字典
    """
    if 'resolved' not in results:
        raise ValueError("Invalid results format: missing 'resolved' field")

    resolved_count = results['resolved']['count']
    total_count = len(results['instance_id'])

    resolve_rate = resolved_count / total_count if total_count > 0 else 0.0

    return {
        'resolve_rate': resolve_rate,
        'resolved_count': resolved_count,
        'total_count': total_count,
    }


# ===== 使用示例 =====
def main():
    """演示如何使用evaluator bridge"""
    from step1_load_data import load_task

    print("=" * 80)
    print("Evaluator Bridge Demo")
    print("=" * 80)

    # 模拟：加载1个任务
    DATA_FILE = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
    task = load_task(DATA_FILE, task_index=0)

    # 模拟：agent生成的patch
    mock_patch = """diff --git a/astropy/modeling/separable.py b/astropy/modeling/separable.py
--- a/astropy/modeling/separable.py
+++ b/astropy/modeling/separable.py
@@ -242,7 +242,7 @@ def _cstack(left, right):
         cright = _coord_matrix(right, 'right', noutp)
     else:
         cright = np.zeros((noutp, right.shape[1]))
-        cright[-right.shape[0]:, -right.shape[1]:] = 1
+        cright[-right.shape[0]:, -right.shape[1]:] = right

     return np.hstack([cleft, cright])
"""

    # 1. 准备predictions.jsonl
    print("\n1. Preparing predictions.jsonl...")
    output_file = Path("predictions.jsonl")
    prepare_predictions([task], [mock_patch], output_file)

    # 2. 打印evaluator使用说明
    print_evaluator_instructions(
        predictions_file=output_file,
        swebench_file=DATA_FILE,
        log_dir=Path("logs")
    )

    print("\n" + "=" * 80)
    print("✅ Demo complete!")
    print("=" * 80)

    print("\n📝 Next steps:")
    print("   1. Run the official evaluator command shown above")
    print("   2. Wait for evaluation to complete")
    print("   3. Load results with: load_evaluation_results('logs/results.json')")
    print("   4. Calculate metrics with: calculate_metrics(results)")


if __name__ == "__main__":
    main()
