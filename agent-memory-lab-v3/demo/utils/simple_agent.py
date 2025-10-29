"""
Simple LLM Agent - 使用Bedrock API
最简化的Agent实现，只为让1行走通
"""

import os
from litellm import completion


class SimpleBedrockAgent:
    """
    最简化的Agent - 使用AWS Bedrock

    只用1个LLM调用生成patch，不需要工具调用
    """

    def __init__(self):
        """初始化Agent"""
        # 检查环境变量
        if not os.getenv('AWS_BEARER_TOKEN_BEDROCK'):
            raise ValueError(
                "Missing AWS_BEARER_TOKEN_BEDROCK environment variable. "
                "Please set: export AWS_BEARER_TOKEN_BEDROCK=..."
            )

        self.model = "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"

    def solve(self, task):
        """
        生成patch解决任务

        Args:
            task: SWEBenchTask对象

        Returns:
            patch: git diff格式的字符串
        """
        # 构造prompt
        prompt = f"""You are a software engineer fixing a bug.

Problem:
{task.problem_statement}

Repository: {task.repo}

Generate a git diff patch to fix this bug. The patch should be in standard git diff format.
Only output the patch, nothing else.

Example format:
diff --git a/path/to/file.py b/path/to/file.py
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -10,7 +10,7 @@ def function():
-    old line
+    new line
"""

        try:
            # 调用Bedrock
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
            )

            # 提取patch
            patch = response.choices[0].message.content

            return patch

        except Exception as e:
            print(f"❌ Error calling Bedrock: {e}")
            # 返回空patch作为fallback
            return "diff --git a/placeholder.py b/placeholder.py\n"


def test_agent():
    """测试Agent是否能工作"""
    from pathlib import Path
    import sys

    # 添加路径
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from steps.step1_load_data import load_task

    print("=" * 80)
    print("Testing SimpleBedrockAgent")
    print("=" * 80)

    # 加载1个任务
    data_file = Path(__file__).parent.parent.parent / "data" / "swebench" / "verified.jsonl"
    task = load_task(data_file, task_index=0)

    print(f"\n📋 Task: {task.instance_id}")
    print(f"📦 Repo: {task.repo}")
    print(f"📝 Problem: {task.problem_statement[:100]}...")

    # 创建Agent
    agent = SimpleBedrockAgent()

    print(f"\n🤖 Calling Bedrock API...")
    patch = agent.solve(task)

    print(f"\n✅ Generated patch ({len(patch)} characters):")
    print("-" * 80)
    print(patch[:500])
    if len(patch) > 500:
        print(f"... (truncated, total {len(patch)} chars)")
    print("-" * 80)

    # 验证patch格式
    if "diff --git" in patch:
        print("\n✅ Patch format looks valid!")
    else:
        print("\n⚠️  Warning: Patch may not be in correct format")

    return patch


if __name__ == "__main__":
    test_agent()
