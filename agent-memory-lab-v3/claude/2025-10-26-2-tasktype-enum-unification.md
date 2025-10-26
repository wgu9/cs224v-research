# TaskType 枚举统一 - 总结

**日期**: 2025-10-26
**改进**: 统一TypeScript和Python中的TaskType枚举定义，添加验证机制

---

## 🎯 问题

**发现不一致**：

| 位置 | 定义 |
|------|------|
| **TypeScript** (旧) | `'code' \| 'doc' \| 'test' \| 'debug' \| 'qa' \| 'other'` |
| **Python Prompt** (旧) | `"doc" \| "code" \| "debug" \| "test" \| "refactor" \| "config"` |

**问题**：
- TypeScript 有 `qa`, `other`，但 Python 没有
- Python 有 `refactor`, `config`，但 TypeScript 没有

---

## ✅ 解决方案

### 统一的 TaskType 枚举（8个值）

```
code | doc | test | debug | refactor | config | qa | other
```

### 每个值的含义

| 枚举值 | 英文描述 | 中文描述 | 示例 |
|--------|----------|----------|------|
| `code` | New feature implementation / code writing | 新功能实现 / 代码编写 | "Add authentication API" |
| `doc` | Documentation updates / translation / README | 文档更新 / 翻译 / README修改 | "Translate README to Chinese" |
| `test` | Test writing / test execution | 测试编写 / 测试运行 | "Add unit tests for login" |
| `debug` | Bug fixing / debugging | Bug修复 / 调试 | "Fix login page crash" |
| `refactor` | Code refactoring / optimization | 代码重构 / 优化 | "Refactor auth module" |
| `config` | Configuration file changes / environment setup | 配置文件修改 / 环境设置 | "Update .env template" |
| `qa` | Q&A / code explanation / consultation | 问答 / 代码解释 / 咨询 | "Explain how auth works" |
| `other` | Other types not listed above | 其他类型 | "Miscellaneous tasks" |

---

## 📝 已修改的文件

### 1. TypeScript 定义

**文件**: `types/cursor-chat/pair.ts`

```typescript
/**
 * Task Type枚举（LLM生成时使用）：
 * - code: 新功能实现 / 代码编写
 * - doc: 文档更新 / 翻译 / README修改
 * - test: 测试编写 / 测试运行
 * - debug: Bug修复 / 调试
 * - refactor: 代码重构 / 优化
 * - config: 配置文件修改 / 环境设置
 * - qa: 问答 / 代码解释 / 咨询
 * - other: 其他类型
 */
export type TaskType = 'code' | 'doc' | 'test' | 'debug' | 'refactor' | 'config' | 'qa' | 'other';
```

**改动**：
- ✅ 添加 `refactor`, `config` （从Python同步）
- ✅ 保留 `qa`, `other`
- ✅ 添加详细注释

### 2. Python 类型定义

**文件**: `tools/process_long_conversation.py`

**新增类型定义**：
```python
from typing import Literal

# TaskType枚举（与types/cursor-chat/pair.ts保持一致）
TaskType = Literal['code', 'doc', 'test', 'debug', 'refactor', 'config', 'qa', 'other']

VALID_TASK_TYPES = ['code', 'doc', 'test', 'debug', 'refactor', 'config', 'qa', 'other']
```

**新增验证函数**：
```python
def validate_task_type(task_type: str) -> str:
    """
    验证并修正task_type

    Args:
        task_type: LLM返回的task_type

    Returns:
        有效的task_type（如果无效则返回'other'）
    """
    if task_type in VALID_TASK_TYPES:
        return task_type
    else:
        print(f"   ⚠️  Invalid task_type '{task_type}', defaulting to 'other'")
        return 'other'
```

**调用验证**（在 `extract_pair_metadata` 中）：
```python
# 验证task_type_llm
if 'task_type_llm' in meta:
    meta['task_type_llm'] = validate_task_type(meta['task_type_llm'])
```

### 3. LLM Prompt 更新

**文件**: `tools/process_long_conversation.py`

**更新 `EXTRACT_PAIR_METADATA_PROMPT`**：
```python
**Output Schema** (Pure JSON, no markdown fences):
{
  "task_type_llm": "code" | "doc" | "test" | "debug" | "refactor" | "config" | "qa" | "other",
  ...
}

**Task Types** (MUST use one of these exact values):
- "code": New feature implementation / code writing
- "doc": Documentation updates / translation / README modifications
- "test": Test writing / test execution
- "debug": Bug fixing / debugging
- "refactor": Code refactoring / optimization
- "config": Configuration file changes / environment setup
- "qa": Q&A / code explanation / consultation
- "other": Other types not listed above
```

**关键改进**：
- ✅ 添加 `"qa"` 和 `"other"` 到枚举
- ✅ 强调 "MUST use one of these exact values"
- ✅ 每个类型都有英文描述

---

## 🔒 一致性保证

### 单一真相源 (Single Source of Truth)

```
TypeScript: types/cursor-chat/pair.ts
    ↓
    定义权威的 TaskType 枚举
    ↓
Python: tools/process_long_conversation.py
    ↓
    同步并验证
```

### 验证流程

```
LLM 返回 task_type_llm
    ↓
validate_task_type(task_type_llm)
    ↓
在 VALID_TASK_TYPES 中？
    ├─ Yes → 返回原值
    └─ No  → 打印警告，返回 'other'
```

---

## 📊 使用示例

### TypeScript 中使用

```typescript
import { TaskType, QueryAnswerPair } from './types/cursor-chat';

const pair: QueryAnswerPair = {
  pair_id: "s_2025-10-26-10-00-00_cursor_q01",
  session_id: "s_2025-10-26-10-00-00_cursor",
  query_index: 1,
  markdown_path: "pairs/q01/chat.md",
  objective_llm: "Translate README to Chinese",
  task_type_llm: "doc",  // ✅ 必须是 TaskType 中的一个
  related_files_llm: ["README.md"],
  is_followup_llm: false,
  has_context_dependency_llm: false
};
```

### Python 中验证

```python
from tools.process_long_conversation import validate_task_type

# 有效的task_type
task_type = validate_task_type("doc")
# 返回: "doc"

# 无效的task_type
task_type = validate_task_type("invalid")
# 打印: ⚠️  Invalid task_type 'invalid', defaulting to 'other'
# 返回: "other"
```

---

## 🧪 测试建议

### 手动测试

```bash
# 1. 重新运行pipeline
python tools/process_long_conversation.py spot-test/small_chat.md

# 2. 检查生成的task_type_llm
cat data/1_sessions/s_*/pairs.json | jq '.[].task_type_llm'

# 预期输出（8种类型之一）:
# "code"
# "doc"
# "test"
# "debug"
# "refactor"
# "config"
# "qa"
# "other"
```

### 单元测试（待实现）

创建 `tests/test_task_type.py`:

```python
def test_valid_task_types():
    """测试所有有效的task_type"""
    for task_type in VALID_TASK_TYPES:
        assert validate_task_type(task_type) == task_type

def test_invalid_task_type():
    """测试无效的task_type默认为other"""
    assert validate_task_type("invalid") == "other"
    assert validate_task_type("CODE") == "other"  # 大小写敏感
    assert validate_task_type("") == "other"
```

---

## 📋 检查清单

- [x] ✅ TypeScript `TaskType` 枚举定义（8个值）
- [x] ✅ Python `TaskType` 类型提示
- [x] ✅ Python `VALID_TASK_TYPES` 常量
- [x] ✅ Python `validate_task_type()` 函数
- [x] ✅ 在 `extract_pair_metadata()` 中调用验证
- [x] ✅ 更新 LLM Prompt
- [x] ✅ 添加详细注释和说明
- [ ] ⏳ 创建单元测试
- [ ] ⏳ 用真实数据测试验证

---

## 🚀 下一步

1. **重新生成测试数据**
   ```bash
   rm -rf data/1_sessions/s_2025-10-26-10-00-00_cursor
   python tools/process_long_conversation.py spot-test/small_chat.md
   ```

2. **验证task_type分布**
   ```bash
   cat data/1_sessions/s_*/pairs.json | jq '[.[].task_type_llm] | group_by(.) | map({type: .[0], count: length})'
   ```

3. **创建单元测试**
   ```bash
   # 创建 tests/test_task_type.py
   pytest tests/test_task_type.py -v
   ```

---

## 💡 为什么这很重要？

1. **类型安全**
   - TypeScript 在编译时检查
   - Python 在运行时验证
   - 防止拼写错误和无效值

2. **数据质量**
   - LLM 可能返回意外值
   - 验证确保数据一致性
   - 自动修正为 `'other'` 而不是失败

3. **可维护性**
   - 单一真相源
   - 修改一处即可同步
   - 明确的枚举含义

4. **未来扩展**
   - 容易添加新类型
   - 只需在两处更新（TS + Python）
   - 验证自动生效

---

**总结**：
- ✅ TypeScript 和 Python 现在完全一致
- ✅ 8个明确定义的 TaskType 值
- ✅ 自动验证和修正机制
- ✅ 详细的注释和文档
