"""
生成predictions.jsonl供SWE-bench官方evaluator使用
"""

from pathlib import Path
from steps import load_task
from utils import SimpleBedrockAgent, prepare_predictions


def main():
    """生成1个任务的predictions.jsonl"""
    print("=" * 80)
    print("Generating predictions.jsonl for SWE-bench Evaluator")
    print("=" * 80)

    # Load task
    DATA_FILE = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
    task = load_task(DATA_FILE, task_index=0)
    print(f"\n✅ Task loaded: {task.instance_id}")

    # Generate patch
    agent = SimpleBedrockAgent(require_token=False)
    patch = agent.solve(task)
    print(f"✅ Patch generated ({len(patch)} characters)")

    # Prepare predictions
    output_file = Path("logs/predictions.jsonl")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    prepare_predictions(
        tasks=[task],
        patches=[patch],
        output_file=output_file
    )

    print(f"\n✅ Predictions saved to: {output_file}")

    # Show content
    import json
    with open(output_file) as f:
        prediction = json.load(f)

    print("\n📝 Predictions content:")
    print("-" * 80)
    print(f"instance_id: {prediction['instance_id']}")
    print(f"model_patch: {prediction['model_patch'][:200]}...")
    print(f"model_name_or_path: {prediction['model_name_or_path']}")
    print("-" * 80)

    print("\n💡 Next step: Run official SWE-bench evaluator")
    print("   See utils/evaluator_bridge.py for instructions")

    return output_file


if __name__ == "__main__":
    output_file = main()
