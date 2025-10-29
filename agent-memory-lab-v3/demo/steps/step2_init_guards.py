"""
Step 2: Q1初始化 (Four-Guard Monitor)
初始化四个守卫，包含LLM调用解析scope和plan
"""

import os
from typing import Set, Dict, Any, List
from dataclasses import dataclass
from step1_load_data import SWEBenchTask, load_task
from pathlib import Path


@dataclass
class GuardConfig:
    """守卫配置"""
    weights: Dict[str, float]
    thresholds: Dict[str, float]
    scope_file_limits: Dict[str, int]


class FourGuardMonitor:
    """四守卫监控系统"""

    def __init__(self, task: SWEBenchTask, config: GuardConfig = None):
        """
        初始化Four-Guard监控器

        Args:
            task: SWE-bench任务
            config: 守卫配置（如果为None，使用默认配置）
        """
        self.task = task
        self.config = config or self._default_config()

        # 从Part B获取监控信号
        part_b = task.get_part_b()
        self.problem_statement = part_b['problem_statement']
        self.difficulty = part_b['difficulty']
        self.fail_to_pass = part_b['fail_to_pass']
        self.pass_to_pass = part_b['pass_to_pass']
        self.repo = part_b['repo']

        # 根据difficulty设置scope_file_limit（基于数据：85.8%只改1个文件）
        self.scope_file_limit = self.config.scope_file_limits.get(
            self.difficulty, 3  # 默认3个文件
        )

        # 状态追踪
        self.current_phase = "understand"
        self.modified_files: Set[str] = set()
        self.tests_run: Set[str] = set()
        self.action_history: List[Dict[str, Any]] = []

        print(f"\n✅ Four-Guard Monitor initialized")
        print(f"   Scope file limit: {self.scope_file_limit} files (based on difficulty: {self.difficulty})")
        print(f"   Mode: Rule-based monitoring (no LLM needed)")

    def _default_config(self) -> GuardConfig:
        """默认配置（来自proposal v2）"""
        return GuardConfig(
            weights={
                'scope': 0.4,
                'plan': 0.3,
                'test': 0.2,
                'evidence': 0.1,
            },
            thresholds={
                'warn': 0.5,
                'rollback': 0.8,
            },
            scope_file_limits={
                '< 15 min': 2,
                '<15 min': 2,
                '<15 min fix': 2,
                '15 min - 1 hour': 3,
                '1-4 hours': 5,
                '> 4 hours': 8,
            }
        )


    def get_summary(self) -> Dict[str, Any]:
        """获取监控器状态摘要"""
        return {
            'task_id': self.task.instance_id,
            'difficulty': self.difficulty,
            'scope_file_limit': self.scope_file_limit,
            'weights': self.config.weights,
            'thresholds': self.config.thresholds,
            'mode': 'rule-based',
        }


def main():
    """演示Four-Guard初始化"""
    # 数据文件路径
    DATA_FILE = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"

    print("=" * 80)
    print("Step 2: Q1初始化 (Four-Guard Monitor)")
    print("=" * 80)

    # 加载任务
    print("\n📂 Loading task...")
    task = load_task(DATA_FILE, task_index=0)
    print(f"✅ Task loaded: {task.instance_id}")

    # 初始化Four-Guard Monitor
    print("\n" + "=" * 80)
    print("初始化Four-Guard Monitor")
    print("=" * 80)

    monitor = FourGuardMonitor(task)

    # 展示配置
    print("\n" + "=" * 80)
    print("守卫配置")
    print("=" * 80)

    summary = monitor.get_summary()

    print(f"\n⚖️ 守卫权重:")
    for guard, weight in summary['weights'].items():
        print(f"   • {guard.capitalize()}: {weight}")

    print(f"\n🚨 阈值设置:")
    for threshold, value in summary['thresholds'].items():
        print(f"   • {threshold.upper()}: {value}")

    print(f"\n📏 Scope限制:")
    print(f"   • Difficulty: {summary['difficulty']}")
    print(f"   • File limit: {summary['scope_file_limit']} files")

    print(f"\n🎯 预期目标:")
    print(f"   • Target function/class: {summary['expected_target']}")
    print(f"   • Expected scope: {summary['expected_scope']}")

    print("\n" + "=" * 80)
    print("✅ Step 2 完成！Four-Guard Monitor已初始化")
    print("=" * 80)

    print("\n💡 说明:")
    print("   - LLM调用点1和2使用了mock实现（实际需要调用GPT-4o）")
    print("   - 实际实现中，需要:")
    print("     1. 配置OpenAI API key")
    print("     2. 调用GPT-4o解析problem_statement")
    print("     3. 成本约 $0.02/task")

    return monitor


if __name__ == "__main__":
    monitor = main()
