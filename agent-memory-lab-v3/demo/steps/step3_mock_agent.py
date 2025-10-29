"""
Step 3: Mock Agent执行
模拟一个简单的agent执行过程，生成一系列actions
注意：这是demo，实际Q1会集成真实的agent（如SWE-agent或简化版agent）
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Action:
    """Agent的单个action"""
    action_type: str  # read_file, edit_file, run_test, bash, submit
    file_path: str = ""
    content: str = ""
    test_name: str = ""
    command: str = ""
    result: str = ""

    def __str__(self):
        if self.action_type == "read_file":
            return f"read_file({self.file_path})"
        elif self.action_type == "edit_file":
            return f"edit_file({self.file_path})"
        elif self.action_type == "run_test":
            return f"run_test({self.test_name})"
        elif self.action_type == "bash":
            return f"bash({self.command[:30]}...)"
        elif self.action_type == "submit":
            return "submit()"
        else:
            return f"{self.action_type}()"


class MockAgent:
    """
    Mock Agent - 模拟agent执行过程

    注意：这是演示用的简化版agent
    实际Q1会使用真实agent（SWE-agent或自定义agent）

    ✨ NEW: 支持Q1监控和ROLLBACK控制
    """

    def __init__(self, task_description: str, repo: str, monitor=None):
        self.task_description = task_description
        self.repo = repo
        self.actions: List[Action] = []
        self.current_patch = ""
        self.monitor = monitor  # Q1 Monitor（可选）
        self.rollback_triggered = False

    def execute(self) -> Dict[str, Any]:
        """
        执行任务，返回结果

        如果接入了Q1 Monitor，会在每个action前检查drift
        如果drift >= rollback阈值，停止执行

        Returns:
            包含patch和actions的字典
        """
        print("\n" + "=" * 80)
        print("🤖 Mock Agent开始执行")
        print("=" * 80)

        # 模拟一系列典型的agent actions
        # 这个序列模拟了一个"好的"执行过程

        # Phase 1: Understand
        print("\n📖 Phase 1: Understand")
        self._action_read_file("django/template/engine.py")
        self._action_read_file("django/template/context.py")

        # Phase 2: Reproduce
        print("\n🔬 Phase 2: Reproduce")
        self._action_run_test("test_autoescape_off")

        # Phase 3: Implement
        print("\n✏️ Phase 3: Implement")
        self._action_edit_file(
            "django/template/engine.py",
            "Added autoescape parameter to Context initialization"
        )

        # Phase 4: Verify
        print("\n✅ Phase 4: Verify")
        self._action_run_test("test_autoescape_off")
        self._action_run_test("test_autoescape_on")  # 确保没破坏其他功能

        # Submit
        print("\n📤 Submit")
        self._action_submit()

        # 生成mock patch
        self.current_patch = self._generate_mock_patch()

        result = {
            'patch': self.current_patch,
            'actions': self.actions,
            'success': True,
        }

        print("\n✅ Mock Agent执行完成")
        print(f"   Total actions: {len(self.actions)}")

        return result

    def _check_with_monitor(self, action: Action) -> bool:
        """
        用Q1 Monitor检查action

        Returns:
            True if should continue, False if should stop
        """
        if not self.monitor:
            return True  # 没有monitor，继续执行

        # 这里需要导入ActionMonitor来检查
        # 为了简化，我们直接检查monitor的状态
        return True  # 暂时always继续，实际会在step4集成

    def _action_read_file(self, file_path: str):
        """读取文件"""
        action = Action(
            action_type="read_file",
            file_path=file_path,
            result="File content read successfully"
        )

        # ✨ NEW: Q1监控检查
        if not self._check_with_monitor(action):
            return

        self.actions.append(action)
        print(f"   {len(self.actions)}. {action}")

    def _action_edit_file(self, file_path: str, description: str):
        """编辑文件"""
        action = Action(
            action_type="edit_file",
            file_path=file_path,
            content=description,
            result="File edited successfully"
        )

        # ✨ NEW: Q1监控检查
        if not self._check_with_monitor(action):
            return

        self.actions.append(action)
        print(f"   {len(self.actions)}. {action}")

    def _action_run_test(self, test_name: str):
        """运行测试"""
        action = Action(
            action_type="run_test",
            test_name=test_name,
            result="Test passed"
        )

        # ✨ NEW: Q1监控检查
        if not self._check_with_monitor(action):
            return

        self.actions.append(action)
        print(f"   {len(self.actions)}. {action}")

    def _action_submit(self):
        """提交结果"""
        action = Action(
            action_type="submit",
            result="Submitted"
        )

        # ✨ NEW: Q1监控检查
        if not self._check_with_monitor(action):
            return

        self.actions.append(action)
        print(f"   {len(self.actions)}. {action}")

    def _generate_mock_patch(self) -> str:
        """生成mock patch（模拟agent的输出）"""
        return """diff --git a/django/template/engine.py b/django/template/engine.py
--- a/django/template/engine.py
+++ b/django/template/engine.py
@@ -160,7 +160,7 @@ def render_to_string(self, template_name, context=None):
         if isinstance(context, Context):
             return t.render(context)
         else:
-            return t.render(Context(context))
+            return t.render(Context(context, autoescape=self.autoescape))

     def select_template(self, template_name_list):
         \"\"\"
"""


def main():
    """演示Mock Agent执行"""
    print("=" * 80)
    print("Step 3: Agent执行任务 (Mock)")
    print("=" * 80)

    # 创建mock agent
    task_description = "Engine.render_to_string() should honor the autoescape attribute"
    repo = "django/django"

    print(f"\n📋 Task: {task_description}")
    print(f"📦 Repo: {repo}")

    agent = MockAgent(task_description, repo)

    # 执行
    result = agent.execute()

    # 展示结果
    print("\n" + "=" * 80)
    print("Agent执行结果")
    print("=" * 80)

    print(f"\n📝 Generated Patch:")
    print(result['patch'])

    print(f"\n📊 Action Summary:")
    print(f"   Total actions: {len(result['actions'])}")

    # 统计action类型
    action_types = {}
    for action in result['actions']:
        action_types[action.action_type] = action_types.get(action.action_type, 0) + 1

    print(f"\n   Action breakdown:")
    for action_type, count in action_types.items():
        print(f"     • {action_type}: {count}")

    print("\n" + "=" * 80)
    print("✅ Step 3 完成！Mock Agent已执行")
    print("=" * 80)

    print("\n💡 说明:")
    print("   - 这是一个mock agent，实际Q1会使用真实agent")
    print("   - 真实agent可以是:")
    print("     1. SWE-agent (官方提供)")
    print("     2. 简化版GPT-4 agent (自己实现)")
    print("     3. 其他coding agent")
    print("   - Mock agent模拟了一个'好的'执行过程（低drift）")

    return result


if __name__ == "__main__":
    result = main()
