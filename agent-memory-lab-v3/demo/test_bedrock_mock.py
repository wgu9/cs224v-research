"""
测试 Bedrock API - Mock 模式（不需要真实 token）
"""

import os
from utils.simple_agent import SimpleBedrockAgent
from steps.step1_load_data import load_task
from pathlib import Path


def test_with_mock():
    """使用 Mock 模式测试（无需真实 token）"""

    print("=" * 80)
    print("Bedrock Agent 测试 - Mock 模式")
    print("=" * 80)

    # 加载一个测试任务
    data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
    task = load_task(data_file, task_index=0)

    print(f"\n📋 Task: {task.instance_id}")
    print(f"📦 Repo: {task.repo}")

    # 创建 Agent（不需要真实 token）
    print("\n🔧 创建 Agent (Mock 模式 - 无需真实 token)...")
    agent = SimpleBedrockAgent(require_token=False)

    print(f"   Has Token: {agent.has_token}")
    print(f"   Model: {agent.model}")

    # 生成 patch
    print("\n🤖 生成 patch...")
    patch = agent.solve(task)

    print(f"\n✅ 生成的 Mock Patch ({len(patch)} 字符):")
    print("-" * 80)
    print(patch)
    print("-" * 80)

    # 验证格式
    if "diff --git" in patch:
        print("\n✅ Patch 格式正确!")
    else:
        print("\n⚠️  Patch 格式可能有问题")

    print("\n" + "=" * 80)
    print("✅ Mock 测试完成")
    print("=" * 80)
    print("\n💡 提示: 这是 Mock 数据，实际使用需要设置 AWS_BEARER_TOKEN_BEDROCK")

    return patch


if __name__ == "__main__":
    test_with_mock()
