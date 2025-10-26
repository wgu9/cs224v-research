#!/usr/bin/env python3
"""
Test Cursor Export Header Extraction

测试从Cursor导出文件中提取header信息
"""

import sys
import pathlib

# 添加父目录到路径
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from tools.process_long_conversation import extract_cursor_export_header


# ============================================
# Test Cases
# ============================================

TEST_CURSOR_EXPORT = """# Document updates and alignment suggestions
_Exported on 10/25/2025 at 20:26:15 PDT from Cursor (1.7.53)_

---

**User**
Hello
"""


TEST_NO_HEADER = """**User**
Hello

**Cursor**
Hi there!
"""


TEST_PARTIAL_HEADER = """# My Conversation

**User**
Hello
"""


# ============================================
# Test Functions
# ============================================

def test_full_header():
    """测试完整的Cursor导出header"""
    print("\n" + "="*60)
    print("Test 1: Full Cursor Export Header")
    print("="*60)

    header_info = extract_cursor_export_header(TEST_CURSOR_EXPORT)

    print(f"Extracted header info:")
    print(f"  conversation_title: {header_info.get('conversation_title')}")
    print(f"  exported_datetime: {header_info.get('exported_datetime')}")
    print(f"  cursor_version: {header_info.get('cursor_version')}")

    # 验证
    assert header_info.get('conversation_title') == 'Document updates and alignment suggestions'
    assert header_info.get('cursor_version') == '1.7.53'
    assert '2025-10-25' in header_info.get('exported_datetime', '')

    print("✅ Test 1 PASSED")


def test_no_header():
    """测试没有header的文件"""
    print("\n" + "="*60)
    print("Test 2: No Header")
    print("="*60)

    header_info = extract_cursor_export_header(TEST_NO_HEADER)

    print(f"Extracted header info: {header_info}")

    # 应该返回空字典
    assert len(header_info) == 0

    print("✅ Test 2 PASSED")


def test_partial_header():
    """测试只有标题没有导出信息的文件"""
    print("\n" + "="*60)
    print("Test 3: Partial Header (Title Only)")
    print("="*60)

    header_info = extract_cursor_export_header(TEST_PARTIAL_HEADER)

    print(f"Extracted header info: {header_info}")

    # 应该只有title
    assert header_info.get('conversation_title') == 'My Conversation'
    assert 'exported_datetime' not in header_info
    assert 'cursor_version' not in header_info

    print("✅ Test 3 PASSED")


def test_real_file():
    """测试真实的spot-test文件"""
    print("\n" + "="*60)
    print("Test 4: Real File (spot-test)")
    print("="*60)

    spot_test_path = pathlib.Path("spot-test/cursor_document_updates_and_alignment_s.md")

    if not spot_test_path.exists():
        print("⚠️  Skipping: spot-test file not found")
        return

    content = spot_test_path.read_text(encoding='utf-8')
    header_info = extract_cursor_export_header(content)

    print(f"Extracted header info:")
    for key, value in header_info.items():
        print(f"  {key}: {value}")

    # 验证至少有title
    assert 'conversation_title' in header_info
    print(f"✅ Title: {header_info['conversation_title']}")

    if 'exported_datetime' in header_info:
        print(f"✅ Exported: {header_info['exported_datetime']}")

    if 'cursor_version' in header_info:
        print(f"✅ Cursor Version: {header_info['cursor_version']}")

    print("✅ Test 4 PASSED")


# ============================================
# Main Test Runner
# ============================================

def main():
    """运行所有测试"""
    print("🧪 Testing Cursor Export Header Extraction")
    print("="*60)

    try:
        test_full_header()
        test_no_header()
        test_partial_header()
        test_real_file()

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
