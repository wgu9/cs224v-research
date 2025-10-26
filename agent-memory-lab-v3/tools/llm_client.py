#!/usr/bin/env python3
"""
LLM Client - 通用的LLM API客户端

支持OpenAI兼容的API（包括自部署的模型）
从.env文件读取配置：LLM_API_KEY 和 LLM_API_ENDPOINT
"""

import requests
import os
import json
from dotenv import load_dotenv
from typing import Optional, Dict, Any


class LLMClient:
    """
    LLM客户端，封装API调用逻辑
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化LLM客户端

        Args:
            api_key: API密钥（可选，默认从环境变量读取）
            base_url: API端点（可选，默认从环境变量读取）
        """
        # 加载.env文件
        load_dotenv(".env")

        # 优先使用传入的参数，否则从环境变量读取
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("LLM_API_ENDPOINT")

        if not self.api_key:
            raise ValueError("LLM_API_KEY not found. Set it in .env or pass it to LLMClient()")
        if not self.base_url:
            raise ValueError("LLM_API_ENDPOINT not found. Set it in .env or pass it to LLMClient()")

        # 移除base_url末尾的斜杠
        self.base_url = self.base_url.rstrip('/')

    def chat_completion(
        self,
        messages: list,
        model: str = "gpt-4.1",
        max_tokens: int = 2000,
        temperature: float = 0.1,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        调用chat completion API

        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "..."}]
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            timeout: 超时时间（秒）

        Returns:
            API响应的JSON字典

        Raises:
            requests.RequestException: API调用失败
        """
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            timeout=timeout
        )

        if response.status_code != 200:
            raise requests.RequestException(
                f"API call failed with status {response.status_code}: {response.text}"
            )

        return response.json()

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "gpt-4.1",
        max_tokens: int = 2000,
        temperature: float = 0.1
    ) -> dict:
        """
        生成JSON格式的响应

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数

        Returns:
            解析后的JSON字典

        Raises:
            json.JSONDecodeError: 响应不是有效的JSON
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = self.chat_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )

        # 提取content
        content = response['choices'][0]['message']['content'].strip()

        # 移除可能的markdown代码块
        if content.startswith("```"):
            lines = content.split('\n')
            # 移除第一行和最后一行（代码块标记）
            if len(lines) > 2:
                content = '\n'.join(lines[1:-1])

        # 解析JSON
        return json.loads(content)

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "gpt-4.1",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """
        生成纯文本响应

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数

        Returns:
            生成的文本内容
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = self.chat_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response['choices'][0]['message']['content']


# 便捷函数
def get_llm_client() -> LLMClient:
    """
    获取LLM客户端实例（从环境变量读取配置）

    Returns:
        LLMClient实例
    """
    return LLMClient()


# 测试代码
if __name__ == "__main__":
    print("🧪 Testing LLM Client...")

    try:
        client = get_llm_client()
        print(f"✅ Client initialized")
        print(f"   Endpoint: {client.base_url}")

        # 测试文本生成
        print("\n📝 Testing text generation...")
        text = client.generate_text(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say hello in one sentence.",
            max_tokens=50
        )
        print(f"✅ Response: {text}")

        # 测试JSON生成
        print("\n📊 Testing JSON generation...")
        json_response = client.generate_json(
            system_prompt="You are a JSON generator. Always respond with valid JSON.",
            user_prompt='Generate a JSON object with fields: name (string), age (number), hobbies (array of strings)',
            max_tokens=100
        )
        print(f"✅ JSON Response: {json.dumps(json_response, indent=2)}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
