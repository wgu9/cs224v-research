"""
简单测试 Bedrock API - 用简单的问题测试连接性
"""

import os
from litellm import completion


def test_simple_query(query: str):
    """测试一个简单的查询"""

    print("=" * 80)
    print("Bedrock API 简单测试")
    print("=" * 80)

    # 检查 token
    has_token = bool(os.getenv('AWS_BEARER_TOKEN_BEDROCK'))
    print(f"\n✓ AWS Token 状态: {'已设置' if has_token else '未设置'}")

    if not has_token:
        print("❌ 缺少 AWS_BEARER_TOKEN_BEDROCK 环境变量")
        print("请设置: export AWS_BEARER_TOKEN_BEDROCK=...")
        return

    # 模型配置
    model = os.getenv(
        "Q1_BEDROCK_MODEL",
        "bedrock/arn:aws:bedrock:us-west-2:339713039693:inference-profile/global.anthropic.claude-sonnet-4-20250514-v1:0"
    )

    print(f"✓ 模型: {model}")
    print(f"\n📝 用户问题: {query}")
    print("\n🤖 调用 Bedrock API...")
    print("-" * 80)

    try:
        # 调用 API
        response = completion(
            model=model,
            messages=[{"role": "user", "content": query}],
            max_tokens=500,
            temperature=0.1,
        )

        # 提取回答
        answer = response.choices[0].message.content or ""

        print(f"\n✅ API 响应:\n")
        print(answer)
        print("\n" + "-" * 80)

        # 显示一些元数据
        if hasattr(response, 'usage'):
            print(f"\n📊 Token 使用:")
            print(f"   输入: {getattr(response.usage, 'prompt_tokens', 'N/A')}")
            print(f"   输出: {getattr(response.usage, 'completion_tokens', 'N/A')}")
            print(f"   总计: {getattr(response.usage, 'total_tokens', 'N/A')}")

        print("\n" + "=" * 80)
        print("✅ 测试成功!")
        print("=" * 80)

        return answer

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n" + "=" * 80)
        print("❌ 测试失败")
        print("=" * 80)
        return None


if __name__ == "__main__":
    # 测试简单的数学问题
    test_simple_query("How much is 2+5? Please answer concisely.")
