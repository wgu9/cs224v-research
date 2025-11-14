"""
检查 AWS/Bedrock 配置状态
"""

import os
import sys


def check_aws_config():
    """检查 AWS 配置"""

    print("=" * 80)
    print("AWS/Bedrock 配置检查")
    print("=" * 80)

    # 检查各种认证方式
    configs = []

    # 1. Bearer Token
    bearer_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
    if bearer_token:
        configs.append({
            'name': 'Bearer Token',
            'status': '✓ 已设置',
            'value': f'{bearer_token[:30]}... (长度: {len(bearer_token)})',
            'note': 'Short-term tokens 通常 12 小时过期'
        })
    else:
        configs.append({
            'name': 'Bearer Token',
            'status': '✗ 未设置',
            'value': None,
            'note': '需要从 Bedrock Console 生成'
        })

    # 2. AWS Access Keys
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    if access_key and secret_key:
        configs.append({
            'name': 'AWS Access Keys',
            'status': '✓ 已设置',
            'value': f'Access Key: {access_key[:10]}...',
            'note': '长期有效，适合生产环境'
        })
    else:
        configs.append({
            'name': 'AWS Access Keys',
            'status': '✗ 未设置',
            'value': None,
            'note': '可通过 aws configure 设置'
        })

    # 3. AWS Region
    region = os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION')
    if region:
        configs.append({
            'name': 'AWS Region',
            'status': '✓ 已设置',
            'value': region,
            'note': None
        })
    else:
        configs.append({
            'name': 'AWS Region',
            'status': '⚠ 未设置',
            'value': 'us-west-2 (默认)',
            'note': '建议明确设置'
        })

    # 4. Bedrock 模型
    model = os.getenv('Q1_BEDROCK_MODEL',
                      'bedrock/arn:aws:bedrock:us-west-2:339713039693:inference-profile/global.anthropic.claude-sonnet-4-20250514-v1:0')
    configs.append({
        'name': 'Bedrock 模型',
        'status': '✓',
        'value': model.split('/')[-1][:60],
        'note': None
    })

    # 打印配置
    print("\n配置状态:")
    print("-" * 80)
    for cfg in configs:
        print(f"\n{cfg['name']}: {cfg['status']}")
        if cfg['value']:
            print(f"  值: {cfg['value']}")
        if cfg['note']:
            print(f"  注: {cfg['note']}")

    print("\n" + "=" * 80)

    # 给出建议
    print("\n💡 建议:")
    print("-" * 80)

    if bearer_token and not (access_key and secret_key):
        print("""
1. Bearer Token 已设置，但可能已过期
2. 如果认证失败，有以下选项：

   选项 A - 重新生成 Bearer Token (快速测试):
   -----------------------------------------------
   1. 访问 AWS Bedrock Console
   2. 找到你的 API Key: BedrockAPIKey-ej9k-at-339713039693
   3. 生成新的 Bearer Token
   4. 运行: export AWS_BEARER_TOKEN_BEDROCK="新token"

   选项 B - 使用 AWS Access Keys (长期使用):
   -----------------------------------------------
   1. 获取 AWS Access Key ID 和 Secret Access Key
   2. 运行:
      export AWS_ACCESS_KEY_ID="your-key-id"
      export AWS_SECRET_ACCESS_KEY="your-secret-key"
      export AWS_REGION="us-west-2"
      unset AWS_BEARER_TOKEN_BEDROCK  # 移除旧的 bearer token

   选项 C - 使用 aws configure (最标准):
   -----------------------------------------------
   1. 安装 AWS CLI: pip install awscli
   2. 运行: aws configure
   3. 输入你的 credentials
   4. 运行: unset AWS_BEARER_TOKEN_BEDROCK
        """)
    elif access_key and secret_key:
        print("""
✓ AWS Access Keys 已配置
  这是长期有效的配置方式，适合生产使用

  如果仍然认证失败，检查：
  1. Access Key 是否有效
  2. Access Key 是否有 Bedrock 权限
  3. Region 是否正确
        """)
    else:
        print("""
✗ 没有找到任何 AWS 认证配置

  请选择一种方式配置：
  1. Bearer Token (快速测试)
  2. AWS Access Keys (长期使用)
  3. aws configure (标准方式)
        """)

    print("\n" + "=" * 80)

    # 测试建议
    print("\n🧪 测试建议:")
    print("-" * 80)
    print("""
配置完成后，运行以下命令测试：

# 测试 1: 简单问题
python test_bedrock_simple.py

# 测试 2: 完整 Agent
python utils/simple_agent.py

# 测试 3: 完整流程
python run_with_real_agent.py
    """)

    print("=" * 80)


if __name__ == "__main__":
    check_aws_config()
