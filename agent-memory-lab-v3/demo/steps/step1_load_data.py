"""
Step 1: 数据加载与解析
从verified.jsonl读取数据，并按照Part A/B/C分类
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class SWEBenchTask:
    """SWE-bench任务的标准格式"""

    # 原始数据
    instance_id: str
    repo: str
    base_commit: str
    problem_statement: str
    difficulty: str
    fail_to_pass: List[str]
    pass_to_pass: List[str]
    ground_truth_patch: str

    # 可选字段
    test_patch: str = ""
    hints_text: str = ""
    created_at: str = ""

    @classmethod
    def from_raw(cls, raw_task: Dict[str, Any]) -> 'SWEBenchTask':
        """从原始JSON数据创建Task对象"""
        return cls(
            instance_id=raw_task['instance_id'],
            repo=raw_task['repo'],
            base_commit=raw_task['base_commit'],
            problem_statement=raw_task['problem_statement'],
            difficulty=raw_task.get('difficulty', 'unknown'),
            fail_to_pass=json.loads(raw_task['FAIL_TO_PASS']),
            pass_to_pass=json.loads(raw_task['PASS_TO_PASS']),
            ground_truth_patch=raw_task['patch'],
            test_patch=raw_task.get('test_patch', ''),
            hints_text=raw_task.get('hints_text', ''),
            created_at=raw_task.get('created_at', ''),
        )

    def get_part_a(self) -> Dict[str, Any]:
        """Part A: 给Agent的输入"""
        return {
            'task_id': self.instance_id,
            'repo': self.repo,
            'commit': self.base_commit,
            'problem': self.problem_statement,
        }

    def get_part_b(self) -> Dict[str, Any]:
        """Part B: 给Q1监控的信号"""
        return {
            'problem_statement': self.problem_statement,
            'difficulty': self.difficulty,
            'repo': self.repo,
            'fail_to_pass': self.fail_to_pass,
            'pass_to_pass': self.pass_to_pass,
        }

    def get_part_c(self) -> Dict[str, Any]:
        """Part C: 评估用的ground truth"""
        return {
            'ground_truth_patch': self.ground_truth_patch,
            'fail_to_pass': self.fail_to_pass,
            'pass_to_pass': self.pass_to_pass,
        }


def load_task(data_file: Path, task_index: int = 0) -> SWEBenchTask:
    """
    从verified.jsonl加载第i个任务

    Args:
        data_file: verified.jsonl文件路径
        task_index: 任务索引（0-indexed）

    Returns:
        SWEBenchTask对象
    """
    with open(data_file, encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if idx == task_index:
                raw_task = json.loads(line)
                return SWEBenchTask.from_raw(raw_task)

    raise ValueError(f"Task index {task_index} not found in {data_file}")


def main(task_index: int = 0):
    """演示数据加载"""
    # 数据文件路径
    # 注意：本文件位于 demo/steps/ 下，这里需要向上三级到项目根
    DATA_FILE = Path(__file__).parent.parent.parent / "data" / "swebench" / "verified.jsonl"

    print("=" * 80)
    print("Step 1: 数据加载与解析")
    print("=" * 80)

    # 加载指定索引的任务
    print(f"\n📂 Loading task from: {DATA_FILE}")
    print(f"📍 Task index: {task_index} (第{task_index + 1}个任务)")

    task = load_task(DATA_FILE, task_index=task_index)

    print(f"\n✅ Loaded task: {task.instance_id}")
    print(f"   Repository: {task.repo}")
    print(f"   Difficulty: {task.difficulty}")

    # 展示三部分数据
    print("\n" + "=" * 80)
    print("数据分类展示")
    print("=" * 80)

    # Part A: 给Agent
    print("\n📤 Part A: 给Agent的输入 (不包含答案！)")
    print("-" * 80)
    part_a = task.get_part_a()
    print(f"task_id: {part_a['task_id']}")
    print(f"repo: {part_a['repo']}")
    print(f"commit: {part_a['commit'][:12]}...")
    print(f"problem (前200字):\n{part_a['problem'][:200]}...")

    # Part B: 给Q1监控
    print("\n🔍 Part B: 给Q1监控的信号")
    print("-" * 80)
    part_b = task.get_part_b()
    print(f"difficulty: {part_b['difficulty']}")
    print(f"problem_statement length: {len(part_b['problem_statement'])} chars")
    print(f"FAIL_TO_PASS tests: {len(part_b['fail_to_pass'])} tests")
    print(f"  Example: {part_b['fail_to_pass'][0] if part_b['fail_to_pass'] else 'N/A'}")
    print(f"PASS_TO_PASS tests: {len(part_b['pass_to_pass'])} tests")

    # Part C: 评估用
    print("\n📊 Part C: 评估用的Ground Truth (⚠️ 不给Agent看！)")
    print("-" * 80)
    part_c = task.get_part_c()
    print(f"ground_truth_patch length: {len(part_c['ground_truth_patch'])} chars")
    print(f"FAIL_TO_PASS for evaluation: {len(part_c['fail_to_pass'])} tests")
    print(f"PASS_TO_PASS for evaluation: {len(part_c['pass_to_pass'])} tests")

    # 展示patch片段
    print(f"\nGround truth patch (前300字):")
    print(part_c['ground_truth_patch'][:300])
    print("...")

    print("\n" + "=" * 80)
    print("✅ Step 1 完成！数据已加载并分类")
    print("=" * 80)

    # 输出 JSONL 文件到 logs/input_data/
    output_dir = Path(__file__).parent.parent / "logs" / "input_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名：input_data_{task_index}_{instance_id}.jsonl
    output_file = output_dir / f"input_data_{task_index}_{task.instance_id}.jsonl"
    
    # 将任务数据转换为字典并写入 JSONL（标准格式：每行一个 JSON 对象）
    task_dict = asdict(task)
    with open(output_file, 'w', encoding='utf-8') as f:
        # JSONL 格式：每行一个 JSON 对象（无缩进）
        json_str = json.dumps(task_dict, ensure_ascii=False)
        f.write(json_str + '\n')
    
    print(f"\n💾 数据已保存到: {output_file}")
    
    return task


if __name__ == "__main__":
    task = main()
