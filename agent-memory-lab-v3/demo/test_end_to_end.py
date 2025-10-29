"""
End-to-End Tests for Q1 Demo
测试完整流程，包括1-2行数据的处理
"""

from pathlib import Path
from steps import (
    load_task,
    FourGuardMonitor,
    MockAgent,
    ActionMonitor,
    evaluate_scope,
    evaluate_resolved_mock,
)
from utils import (
    get_default_config,
    ExperimentLogger,
    SimpleBedrockAgent,
    prepare_predictions,
)


class TestDataLoading:
    """测试数据加载"""

    def test_load_single_task(self):
        """测试加载第1个任务"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
        task = load_task(data_file, task_index=0)

        assert task is not None
        assert task.instance_id is not None
        assert task.problem_statement is not None
        assert task.repo is not None

    def test_load_two_tasks(self):
        """测试加载前2个任务"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"

        task0 = load_task(data_file, task_index=0)
        task1 = load_task(data_file, task_index=1)

        assert task0.instance_id != task1.instance_id
        assert task0.difficulty is not None
        assert task1.difficulty is not None

    def test_task_parts(self):
        """测试任务三部分数据"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
        task = load_task(data_file, task_index=0)

        part_a = task.get_part_a()
        part_b = task.get_part_b()
        part_c = task.get_part_c()

        # Part A: Agent inputs
        assert 'problem' in part_a or 'problem_statement' in part_a
        assert 'repo' in part_a
        assert 'commit' in part_a or 'base_commit' in part_a

        # Part B: Q1 monitoring
        assert 'difficulty' in part_b
        assert 'fail_to_pass' in part_b
        assert 'pass_to_pass' in part_b

        # Part C: Evaluation
        assert 'ground_truth_patch' in part_c
        assert 'fail_to_pass' in part_c
        assert 'pass_to_pass' in part_c


class TestGuardInitialization:
    """测试Four-Guard初始化"""

    def test_guard_init(self):
        """测试初始化守卫"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
        task = load_task(data_file, task_index=0)

        guard = FourGuardMonitor(task)
        summary = guard.get_summary()

        assert summary['weights']['scope'] == 0.4
        assert summary['weights']['plan'] == 0.3
        assert summary['weights']['test'] == 0.2
        assert summary['weights']['evidence'] == 0.1
        assert summary['thresholds']['warn'] == 0.5
        assert summary['thresholds']['rollback'] == 0.8
        assert summary['scope_file_limit'] > 0

    def test_guard_for_multiple_tasks(self):
        """测试多个任务的守卫初始化"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"

        for idx in [0, 1]:
            task = load_task(data_file, task_index=idx)
            guard = FourGuardMonitor(task)
            summary = guard.get_summary()

            assert summary['scope_file_limit'] in [2, 3, 5]  # Based on difficulty


class TestAgentExecution:
    """测试Agent执行"""

    def test_mock_agent_execution(self):
        """测试Mock Agent"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
        task = load_task(data_file, task_index=0)

        agent = MockAgent(task.problem_statement, task.repo)
        result = agent.execute()

        assert 'actions' in result
        assert 'patch' in result
        assert len(result['actions']) > 0
        assert len(result['patch']) > 0

    def test_real_agent_initialization(self):
        """测试真实Agent初始化"""
        agent = SimpleBedrockAgent(require_token=False)
        assert agent is not None
        assert agent.model == "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"

    def test_real_agent_patch_generation(self):
        """测试真实Agent生成patch"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
        task = load_task(data_file, task_index=0)

        agent = SimpleBedrockAgent(require_token=False)
        patch = agent.solve(task)

        assert patch is not None
        assert len(patch) > 0
        assert "diff --git" in patch


class TestMonitoring:
    """测试实时监控"""

    def test_action_monitoring(self):
        """测试action监控"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
        task = load_task(data_file, task_index=0)

        guard = FourGuardMonitor(task)
        agent = MockAgent(task.problem_statement, task.repo)
        result = agent.execute()

        monitor = ActionMonitor(guard)
        monitoring_results = []

        for idx, action in enumerate(result['actions'], 1):
            guard.action_history.append(action)
            monitor_result = monitor.monitor_action(action, idx)
            monitoring_results.append(monitor_result)

        assert len(monitoring_results) == len(result['actions'])
        for r in monitoring_results:
            assert 'drift_score' in r
            assert 'decision' in r
            assert 0 <= r['drift_score'] <= 1

    def test_monitoring_two_tasks(self):
        """测试监控2个任务"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"

        for task_idx in [0, 1]:
            task = load_task(data_file, task_index=task_idx)
            guard = FourGuardMonitor(task)
            agent = MockAgent(task.problem_statement, task.repo)
            result = agent.execute()

            monitor = ActionMonitor(guard)
            for idx, action in enumerate(result['actions'], 1):
                guard.action_history.append(action)
                monitor_result = monitor.monitor_action(action, idx)
                assert monitor_result['drift_score'] >= 0


class TestEvaluation:
    """测试评估"""

    def test_scope_evaluation(self):
        """测试Scope评估"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
        task = load_task(data_file, task_index=0)

        agent = MockAgent(task.problem_statement, task.repo)
        result = agent.execute()

        part_c = task.get_part_c()
        scope_result = evaluate_scope(result['patch'], part_c['ground_truth_patch'])

        assert 'scope_precision' in scope_result
        assert 'scope_recall' in scope_result
        assert 0 <= scope_result['scope_precision'] <= 1
        assert 0 <= scope_result['scope_recall'] <= 1

    def test_resolved_evaluation(self):
        """测试Resolved评估"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
        task = load_task(data_file, task_index=0)

        agent = MockAgent(task.problem_statement, task.repo)
        result = agent.execute()

        part_c = task.get_part_c()
        resolved_result = evaluate_resolved_mock(
            result['patch'],
            part_c['fail_to_pass'],
            part_c['pass_to_pass']
        )

        assert 'resolved' in resolved_result
        assert isinstance(resolved_result['resolved'], bool)


class TestLogging:
    """测试日志系统"""

    def test_logger_initialization(self):
        """测试日志初始化"""
        config = get_default_config()
        logger = ExperimentLogger(
            output_dir=Path("logs/test"),
            experiment_name="test_experiment"
        )

        assert logger.output_dir.exists()

    def test_logger_task_logging(self):
        """测试任务日志记录"""
        logger = ExperimentLogger(
            output_dir=Path("logs/test"),
            experiment_name="test_task_logging"
        )

        logger.log_task_result(
            task_id="test_task_1",
            result={'resolved': True, 'scope_precision': 0.9},
            drift_metrics={'drift_rate': 0.1, 'num_actions': 5}
        )

        summary = logger.get_summary()
        assert summary['total_tasks'] == 1


class TestPredictions:
    """测试predictions.jsonl生成"""

    def test_predictions_generation(self):
        """测试生成predictions.jsonl"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
        task = load_task(data_file, task_index=0)

        agent = SimpleBedrockAgent(require_token=False)
        patch = agent.solve(task)

        output_file = Path("logs/test_predictions.jsonl")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        prepare_predictions(
            tasks=[task],
            patches=[patch],
            output_file=output_file
        )

        assert output_file.exists()

        # Verify format
        import json
        with open(output_file) as f:
            prediction = json.load(f)

        assert 'instance_id' in prediction
        assert 'model_patch' in prediction
        assert 'model_name_or_path' in prediction

    def test_predictions_two_tasks(self):
        """测试2个任务的predictions生成"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"

        tasks = [load_task(data_file, task_index=i) for i in [0, 1]]
        agent = SimpleBedrockAgent(require_token=False)
        patches = [agent.solve(task) for task in tasks]

        output_file = Path("logs/test_predictions_two.jsonl")
        prepare_predictions(
            tasks=tasks,
            patches=patches,
            output_file=output_file
        )

        assert output_file.exists()


class TestEndToEnd:
    """完整端到端测试"""

    def test_full_pipeline_one_task(self):
        """测试1个任务的完整流程"""
        # Step 1: Load data
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
        task = load_task(data_file, task_index=0)

        # Step 2: Initialize guard
        guard = FourGuardMonitor(task)

        # Step 3: Agent execution
        agent = SimpleBedrockAgent(require_token=False)
        patch = agent.solve(task)

        # Step 4: Evaluation
        part_c = task.get_part_c()
        scope_result = evaluate_scope(patch, part_c['ground_truth_patch'])
        resolved_result = evaluate_resolved_mock(
            patch, part_c['fail_to_pass'], part_c['pass_to_pass']
        )

        # Verify results
        assert patch is not None
        assert 'scope_precision' in scope_result
        assert 'resolved' in resolved_result

    def test_full_pipeline_two_tasks(self):
        """测试2个任务的完整流程"""
        data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"

        results = []
        for task_idx in [0, 1]:
            # Load task
            task = load_task(data_file, task_index=task_idx)

            # Initialize guard
            guard = FourGuardMonitor(task)

            # Agent execution
            agent = SimpleBedrockAgent(require_token=False)
            patch = agent.solve(task)

            # Evaluation
            part_c = task.get_part_c()
            scope_result = evaluate_scope(patch, part_c['ground_truth_patch'])
            resolved_result = evaluate_resolved_mock(
                patch, part_c['fail_to_pass'], part_c['pass_to_pass']
            )

            results.append({
                'task_id': task.instance_id,
                'patch_length': len(patch),
                'scope_precision': scope_result['scope_precision'],
                'resolved': resolved_result['resolved'],
            })

        assert len(results) == 2
        for r in results:
            assert r['patch_length'] > 0


if __name__ == "__main__":
    # Run tests manually
    print("Running end-to-end tests...")

    # Test 1: Data loading
    print("\n✅ Test 1: Data Loading")
    test = TestDataLoading()
    test.test_load_single_task()
    test.test_load_two_tasks()
    test.test_task_parts()
    print("   All data loading tests passed!")

    # Test 2: Guard initialization
    print("\n✅ Test 2: Guard Initialization")
    test = TestGuardInitialization()
    test.test_guard_init()
    test.test_guard_for_multiple_tasks()
    print("   All guard initialization tests passed!")

    # Test 3: Agent execution
    print("\n✅ Test 3: Agent Execution")
    test = TestAgentExecution()
    test.test_mock_agent_execution()
    test.test_real_agent_initialization()
    test.test_real_agent_patch_generation()
    print("   All agent execution tests passed!")

    # Test 4: Monitoring
    print("\n✅ Test 4: Monitoring")
    test = TestMonitoring()
    test.test_action_monitoring()
    test.test_monitoring_two_tasks()
    print("   All monitoring tests passed!")

    # Test 5: Evaluation
    print("\n✅ Test 5: Evaluation")
    test = TestEvaluation()
    test.test_scope_evaluation()
    test.test_resolved_evaluation()
    print("   All evaluation tests passed!")

    # Test 6: Predictions
    print("\n✅ Test 6: Predictions")
    test = TestPredictions()
    test.test_predictions_generation()
    test.test_predictions_two_tasks()
    print("   All predictions tests passed!")

    # Test 7: End-to-end
    print("\n✅ Test 7: End-to-End")
    test = TestEndToEnd()
    test.test_full_pipeline_one_task()
    test.test_full_pipeline_two_tasks()
    print("   All end-to-end tests passed!")

    print("\n" + "=" * 80)
    print("🎉 All tests passed!")
    print("=" * 80)
