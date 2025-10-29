"""
Step 4: 实时监控详细流程
Four-Guard监控每个action，计算drift score
"""

from typing import Dict, Any
from pathlib import Path
from step1_load_data import load_task
from step2_init_guards import FourGuardMonitor
from step3_mock_agent import MockAgent, Action


class ActionMonitor:
    """Action级别的监控器（封装Four-Guard检查逻辑）"""

    def __init__(self, guard: FourGuardMonitor):
        self.guard = guard

    def monitor_action(self, action: Action, action_index: int) -> Dict[str, Any]:
        """
        监控单个action，计算drift score

        Args:
            action: agent的action
            action_index: action序号

        Returns:
            监控结果，包含各guard的violation和drift score
        """
        print("\n" + "-" * 80)
        print(f"📍 Action #{action_index}: {action}")
        print("-" * 80)

        # 1. Scope Guard
        scope_violation = self._check_scope(action)
        print(f"   🔵 Scope Guard: {scope_violation:.2f}")

        # 2. Plan Guard
        plan_violation = self._check_plan(action)
        print(f"   🟢 Plan Guard: {plan_violation:.2f}")

        # 3. Test Guard
        test_violation = self._check_test(action)
        print(f"   🟡 Test Guard: {test_violation:.2f}")

        # 4. Evidence Guard (mock, 实际需要LLM)
        evidence_violation = self._check_evidence(action)
        print(f"   🟠 Evidence Guard: {evidence_violation:.2f}")

        # 5. 计算drift score
        drift_score = (
            self.guard.config.weights['scope'] * scope_violation +
            self.guard.config.weights['plan'] * plan_violation +
            self.guard.config.weights['test'] * test_violation +
            self.guard.config.weights['evidence'] * evidence_violation
        )

        print(f"\n   📊 Drift Score Calculation:")
        print(f"      {self.guard.config.weights['scope']:.1f} × {scope_violation:.2f} + "
              f"{self.guard.config.weights['plan']:.1f} × {plan_violation:.2f} + "
              f"{self.guard.config.weights['test']:.1f} × {test_violation:.2f} + "
              f"{self.guard.config.weights['evidence']:.1f} × {evidence_violation:.2f}")
        print(f"      = {drift_score:.3f}")

        # 6. 决策
        decision = self._make_decision(drift_score)
        print(f"\n   🎯 Decision: {decision['action']} {decision['emoji']}")
        if decision['message']:
            print(f"      Message: {decision['message']}")

        return {
            'action': str(action),
            'action_index': action_index,
            'scope_violation': scope_violation,
            'plan_violation': plan_violation,
            'test_violation': test_violation,
            'evidence_violation': evidence_violation,
            'drift_score': drift_score,
            'decision': decision,
        }

    def _check_scope(self, action: Action) -> float:
        """
        Scope Guard检查（基于规则，不需要LLM）

        核心规则：基于difficulty限制文件数
        - 数据支持：85.8%的SWE-bench任务只修改1个文件
        - <15min: 最多2个文件
        - 15min-1h: 最多3个文件
        - 1-4h: 最多5个文件
        """
        if action.action_type != "edit_file":
            return 0.0

        # 更新已修改文件
        self.guard.modified_files.add(action.file_path)

        # 唯一检查：文件数是否超过difficulty阈值
        num_files = len(self.guard.modified_files)
        limit = self.guard.scope_file_limit

        if num_files > limit:
            # 超出越多，violation越高
            excess = num_files - limit
            return min(1.0, 0.5 + 0.2 * excess)  # 0.5, 0.7, 0.9, 1.0...

        return 0.0  # 在限制内

    def _check_plan(self, action: Action) -> float:
        """Plan Guard检查"""
        # 更新phase
        self._update_phase()

        # Phase规则
        phase_rules = {
            'understand': ['read_file'],
            'reproduce': ['run_test', 'bash'],
            'implement': ['edit_file'],
            'verify': ['run_test'],
        }

        allowed_actions = phase_rules.get(self.guard.current_phase, [])

        # 检查action是否符合当前phase
        if action.action_type not in allowed_actions:
            # 特殊情况：在implement前必须先run test
            if action.action_type == 'edit_file' and len(self.guard.tests_run) == 0:
                return 1.0  # 严重违规：没测试就改代码

            # submit总是允许的
            if action.action_type == 'submit':
                return 0.0

            return 0.5  # 一般违规

        return 0.0

    def _check_test(self, action: Action) -> float:
        """Test Guard检查"""
        # 更新测试集合
        if action.action_type == "run_test":
            self.guard.tests_run.add(action.test_name)

        # 检查：如果已经修改了文件，是否运行了必需的测试
        if len(self.guard.modified_files) > 0:
            # 检查是否运行了FAIL_TO_PASS中的任何测试
            f2p_tests_run = self.guard.tests_run & set(self.guard.fail_to_pass)
            if len(f2p_tests_run) == 0:
                return 0.6  # 中等违规：改代码但没运行必需测试

        return 0.0

    def _check_evidence(self, action: Action) -> float:
        """
        Evidence Guard检查

        注意：这是mock实现，实际需要调用LLM
        """
        if action.action_type != "edit_file":
            return 0.0

        # Mock: 检查之前是否读取过该文件
        read_actions = [a for a in self.guard.action_history if a.action_type == 'read_file']
        read_files = [a.file_path for a in read_actions]

        if action.file_path in read_files:
            return 0.1  # 有证据（读过文件）
        else:
            return 0.5  # 缺乏证据（没读过就改）

    def _update_phase(self):
        """从action历史推断当前phase"""
        if len(self.guard.modified_files) > 0 and len(self.guard.tests_run) > 0:
            self.guard.current_phase = "verify"
        elif len(self.guard.modified_files) > 0:
            self.guard.current_phase = "implement"
        elif len(self.guard.tests_run) > 0:
            self.guard.current_phase = "reproduce"
        else:
            self.guard.current_phase = "understand"

    def _make_decision(self, drift_score: float) -> Dict[str, Any]:
        """根据drift score做决策"""
        if drift_score < self.guard.config.thresholds['warn']:
            return {
                'action': 'ALLOW',
                'emoji': '✅',
                'message': None,
            }
        elif drift_score < self.guard.config.thresholds['rollback']:
            return {
                'action': 'WARN',
                'emoji': '⚠️',
                'message': f'Moderate drift detected (score={drift_score:.2f})',
            }
        else:
            return {
                'action': 'ROLLBACK',
                'emoji': '🚫',
                'message': f'High drift! Recommend rollback (score={drift_score:.2f})',
            }


def main():
    """演示实时监控流程"""
    DATA_FILE = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"

    print("=" * 80)
    print("Step 4: 实时监控详细流程")
    print("=" * 80)

    # 1. 加载任务
    print("\n📂 Loading task...")
    task = load_task(DATA_FILE, task_index=0)

    # 2. 初始化Four-Guard
    print("\n🔧 Initializing Four-Guard Monitor...")
    guard = FourGuardMonitor(task)

    # 3. 创建mock agent并执行
    print("\n🤖 Creating and running Mock Agent...")
    agent = MockAgent(task.problem_statement, task.repo)
    result = agent.execute()

    # 4. 实时监控每个action
    print("\n" + "=" * 80)
    print("🔍 监控每个Action")
    print("=" * 80)

    monitor = ActionMonitor(guard)
    monitoring_results = []

    for idx, action in enumerate(result['actions'], 1):
        # 记录action到guard历史
        guard.action_history.append(action)

        # 监控action
        monitor_result = monitor.monitor_action(action, idx)
        monitoring_results.append(monitor_result)

    # 5. 汇总结果
    print("\n" + "=" * 80)
    print("📊 监控结果汇总")
    print("=" * 80)

    total_actions = len(monitoring_results)
    drift_actions = sum(1 for r in monitoring_results if r['drift_score'] >= 0.5)
    avg_drift = sum(r['drift_score'] for r in monitoring_results) / total_actions

    print(f"\n总体统计:")
    print(f"   Total actions: {total_actions}")
    print(f"   Drift actions (≥0.5): {drift_actions}")
    print(f"   Drift rate: {drift_actions/total_actions*100:.1f}%")
    print(f"   Average drift score: {avg_drift:.3f}")

    # 决策统计
    decisions = {}
    for r in monitoring_results:
        decision = r['decision']['action']
        decisions[decision] = decisions.get(decision, 0) + 1

    print(f"\n决策分布:")
    for decision, count in decisions.items():
        emoji = {'ALLOW': '✅', 'WARN': '⚠️', 'ROLLBACK': '🚫'}.get(decision, '')
        print(f"   {emoji} {decision}: {count}")

    print("\n" + "=" * 80)
    print("✅ Step 4 完成！所有actions已监控")
    print("=" * 80)

    return monitoring_results


if __name__ == "__main__":
    results = main()
