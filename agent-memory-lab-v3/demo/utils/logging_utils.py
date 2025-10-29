"""
可复现日志工具
记录实验配置、actions、guard decisions等，确保实验可复现
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class ExperimentLogger:
    """实验日志记录器"""

    def __init__(self, output_dir: Path, experiment_name: str = "q1_experiment"):
        """
        初始化logger

        Args:
            output_dir: 日志输出目录
            experiment_name: 实验名称
        """
        self.output_dir = Path(output_dir)
        self.experiment_name = experiment_name

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 日志文件路径
        self.events_file = self.output_dir / "events.jsonl"
        self.guards_file = self.output_dir / "guards.jsonl"
        self.results_file = self.output_dir / "results.jsonl"
        self.meta_file = self.output_dir / "run_meta.json"

        print(f"📝 Experiment logger initialized")
        print(f"   Output dir: {self.output_dir}")

    def log_config(self, config: Dict[str, Any]) -> None:
        """
        记录实验配置（run_meta.json）

        Args:
            config: 配置字典（包含weights, thresholds等）
        """
        meta = {
            'experiment_name': self.experiment_name,
            'timestamp': datetime.now().isoformat(),
            'config': config,
        }

        with open(self.meta_file, 'w') as f:
            json.dump(meta, f, indent=2)

        print(f"✅ Config logged to: {self.meta_file}")

    def log_action(self, task_id: str, action_index: int, action: Dict[str, Any]) -> None:
        """
        记录单个action（events.jsonl）

        Args:
            task_id: 任务ID
            action_index: Action序号
            action: Action字典
        """
        event = {
            'task_id': task_id,
            'action_index': action_index,
            'action_type': action.get('action_type', 'unknown'),
            'action_str': str(action),
            'timestamp': datetime.now().isoformat(),
        }

        with open(self.events_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

    def log_guard_decision(
        self,
        task_id: str,
        action_index: int,
        drift_result: Dict[str, Any]
    ) -> None:
        """
        记录guard决策（guards.jsonl）

        Args:
            task_id: 任务ID
            action_index: Action序号
            drift_result: Monitor返回的结果
        """
        guard_log = {
            'task_id': task_id,
            'action_index': action_index,
            'drift_score': drift_result.get('drift_score', 0.0),
            'decision': drift_result.get('decision', {}),
            'violations': {
                'scope': drift_result.get('scope_violation', 0.0),
                'plan': drift_result.get('plan_violation', 0.0),
                'test': drift_result.get('test_violation', 0.0),
                'evidence': drift_result.get('evidence_violation', 0.0),
            },
            'timestamp': datetime.now().isoformat(),
        }

        with open(self.guards_file, 'a') as f:
            f.write(json.dumps(guard_log) + '\n')

    def log_task_result(
        self,
        task_id: str,
        result: Dict[str, Any],
        drift_metrics: Dict[str, float]
    ) -> None:
        """
        记录任务级别结果（results.jsonl）

        Args:
            task_id: 任务ID
            result: 评估结果
            drift_metrics: Drift相关指标
        """
        task_result = {
            'task_id': task_id,
            'resolved': result.get('resolved', False),
            'drift_rate': drift_metrics.get('drift_rate', 0.0),
            'scope_precision': result.get('scope_precision', 0.0),
            'scope_recall': result.get('scope_recall', 0.0),
            'num_actions': drift_metrics.get('num_actions', 0),
            'num_drift_actions': drift_metrics.get('num_drift_actions', 0),
            'timestamp': datetime.now().isoformat(),
        }

        with open(self.results_file, 'a') as f:
            f.write(json.dumps(task_result) + '\n')

    def get_summary(self) -> Dict[str, Any]:
        """
        获取实验汇总统计

        Returns:
            包含各种汇总指标的字典
        """
        # 读取results.jsonl
        if not self.results_file.exists():
            return {'error': 'No results file found'}

        results = []
        with open(self.results_file) as f:
            for line in f:
                results.append(json.loads(line))

        if not results:
            return {'error': 'No results logged'}

        # 计算汇总指标
        total_tasks = len(results)
        resolved_count = sum(1 for r in results if r['resolved'])
        resolve_rate = resolved_count / total_tasks if total_tasks > 0 else 0.0

        avg_drift_rate = sum(r['drift_rate'] for r in results) / total_tasks
        avg_scope_precision = sum(r['scope_precision'] for r in results) / total_tasks
        avg_scope_recall = sum(r['scope_recall'] for r in results) / total_tasks

        return {
            'total_tasks': total_tasks,
            'resolved_count': resolved_count,
            'resolve_rate': resolve_rate,
            'avg_drift_rate': avg_drift_rate,
            'avg_scope_precision': avg_scope_precision,
            'avg_scope_recall': avg_scope_recall,
        }


# ===== 使用示例 =====
def main():
    """演示如何使用logger"""
    print("=" * 80)
    print("Experiment Logger Demo")
    print("=" * 80)

    # 1. 初始化logger
    logger = ExperimentLogger(
        output_dir=Path("logs/demo_experiment"),
        experiment_name="q1_demo"
    )

    # 2. 记录配置
    config = {
        'weights': {'scope': 0.4, 'plan': 0.3, 'test': 0.2, 'evidence': 0.1},
        'thresholds': {'warn': 0.5, 'rollback': 0.8},
        'mode': 'advisory',
        'seed': 42,
    }
    logger.log_config(config)

    # 3. 记录actions和guard decisions
    task_id = "django__django-11119"

    for i in range(3):
        # 记录action
        action = {
            'action_type': 'edit_file' if i == 1 else 'read_file',
            'file_path': f'file{i}.py',
        }
        logger.log_action(task_id, i, action)

        # 记录guard decision
        drift_result = {
            'drift_score': 0.1 * i,
            'decision': {'action': 'ALLOW', 'emoji': '✅'},
            'scope_violation': 0.0,
            'plan_violation': 0.0,
            'test_violation': 0.0,
            'evidence_violation': 0.1 * i,
        }
        logger.log_guard_decision(task_id, i, drift_result)

    # 4. 记录任务结果
    result = {
        'resolved': True,
        'scope_precision': 1.0,
        'scope_recall': 1.0,
    }
    drift_metrics = {
        'drift_rate': 0.0,
        'num_actions': 3,
        'num_drift_actions': 0,
    }
    logger.log_task_result(task_id, result, drift_metrics)

    # 5. 获取汇总
    summary = logger.get_summary()
    print("\n" + "=" * 80)
    print("Experiment Summary")
    print("=" * 80)
    print(json.dumps(summary, indent=2))

    print("\n✅ Demo complete! Check logs in:", logger.output_dir)


if __name__ == "__main__":
    main()
