#!/usr/bin/env python3
"""
Test Conversation Splitting Logic

测试对话拆分逻辑，不需要调用LLM
"""

import sys
import pathlib

# 添加父目录到路径，以便导入tools模块
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from tools.process_long_conversation import split_conversation


# ============================================
# Test Cases
# ============================================

TEST_CONVERSATION_1 = """
**User**
把 README.md 翻译成中文

**Cursor**
好的，我会将 README.md 翻译成中文。

**Cursor**
我已经完成了翻译，将英文内容改为中文。

**User**
谢谢，请再修复一下 setup.py 里的typo

**Cursor**
好的，我来检查 setup.py。

**Cursor**
已修复 setup.py 中的拼写错误。
"""


TEST_CONVERSATION_2 = """
**User**
Add authentication to the API

**Cursor**
I'll add JWT-based authentication. Let me start by creating the auth module.

**Cursor**
Created src/auth/jwt.py with token generation and validation.

**User**
Great! Now add login endpoint

**Cursor**
Adding login endpoint to src/api/routes.py

**Cursor**
Done. The login endpoint is now available at /api/login

**User**
Can you also add tests?

**Cursor**
Sure, creating tests/test_auth.py

**Cursor**
Tests created. All 5 tests passing.
"""


TEST_CONVERSATION_3 = """
**User**
Fix the bug in calculate_total()

**Cursor**
Let me check the function...

**Cursor**
Found the issue - division by zero when cart is empty. Fixed in src/cart.py:42

**User**
Thanks
"""


# ============================================
# Test Functions
# ============================================

def test_split_basic():
    """测试基本拆分功能"""
    print("\n" + "="*60)
    print("Test 1: Basic Splitting (2 queries)")
    print("="*60)

    pairs = split_conversation(TEST_CONVERSATION_1)

    print(f"✅ Found {len(pairs)} query-answer pairs")
    assert len(pairs) == 2, f"Expected 2 pairs, got {len(pairs)}"

    # 检查第一个pair
    idx1, user1, assistant1 = pairs[0]
    print(f"\nPair 1 (index={idx1}):")
    print(f"  User: {user1[:50]}...")
    print(f"  Assistant: {assistant1[:100]}...")
    assert "README.md" in user1
    assert "翻译" in user1

    # 检查第二个pair
    idx2, user2, assistant2 = pairs[1]
    print(f"\nPair 2 (index={idx2}):")
    print(f"  User: {user2[:50]}...")
    print(f"  Assistant: {assistant2[:100]}...")
    assert "setup.py" in user2
    assert "typo" in user2

    print("✅ Test 1 PASSED")


def test_split_multiple_assistant_messages():
    """测试多个assistant消息的情况"""
    print("\n" + "="*60)
    print("Test 2: Multiple Assistant Messages (3 queries)")
    print("="*60)

    pairs = split_conversation(TEST_CONVERSATION_2)

    print(f"✅ Found {len(pairs)} query-answer pairs")
    assert len(pairs) == 3, f"Expected 3 pairs, got {len(pairs)}"

    # 检查第一个pair（有2个assistant消息）
    idx1, user1, assistant1 = pairs[0]
    print(f"\nPair 1 (index={idx1}):")
    print(f"  User: {user1[:50]}...")
    print(f"  Assistant messages: {len(assistant1.split('**Cursor**'))}")
    assert "authentication" in user1.lower()
    assert "JWT" in assistant1 or "jwt" in assistant1

    # 检查第二个pair
    idx2, user2, assistant2 = pairs[1]
    print(f"\nPair 2 (index={idx2}):")
    print(f"  User: {user2[:50]}...")
    assert "login" in user2.lower()

    # 检查第三个pair
    idx3, user3, assistant3 = pairs[2]
    print(f"\nPair 3 (index={idx3}):")
    print(f"  User: {user3[:50]}...")
    assert "test" in user3.lower()

    print("✅ Test 2 PASSED")


def test_split_short_conversation():
    """测试短对话"""
    print("\n" + "="*60)
    print("Test 3: Short Conversation (1 query)")
    print("="*60)

    pairs = split_conversation(TEST_CONVERSATION_3)

    print(f"✅ Found {len(pairs)} query-answer pairs")
    assert len(pairs) == 2, f"Expected 2 pairs, got {len(pairs)}"

    idx1, user1, assistant1 = pairs[0]
    print(f"\nPair 1 (index={idx1}):")
    print(f"  User: {user1[:50]}...")
    print(f"  Assistant: {assistant1[:100]}...")

    print("✅ Test 3 PASSED")


def test_split_real_file():
    """测试真实文件（r60的cursor.md）"""
    print("\n" + "="*60)
    print("Test 4: Real File (r60/raw/cursor.md)")
    print("="*60)

    r60_path = pathlib.Path("data/runs/r60/raw/cursor.md")

    if not r60_path.exists():
        print("⚠️  Skipping: r60/raw/cursor.md not found")
        return

    content = r60_path.read_text(encoding='utf-8')
    pairs = split_conversation(content)

    print(f"✅ Found {len(pairs)} query-answer pairs")

    for idx, (q_idx, user, assistant) in enumerate(pairs[:3]):  # 只显示前3个
        print(f"\nPair {idx+1} (index={q_idx}):")
        print(f"  User ({len(user)} chars): {user[:50]}...")
        print(f"  Assistant ({len(assistant)} chars): {assistant[:50]}...")

    print("✅ Test 4 PASSED")


# ============================================
# Main Test Runner
# ============================================

def main():
    """运行所有测试"""
    print("🧪 Testing Conversation Splitting Logic")
    print("="*60)

    try:
        test_split_basic()
        test_split_multiple_assistant_messages()
        test_split_short_conversation()
        test_split_real_file()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
