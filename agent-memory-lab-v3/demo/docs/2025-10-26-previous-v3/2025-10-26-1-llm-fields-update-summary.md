# LLM字段标记和配置添加 - 总结

**日期**: 2025-10-26
**改进**: 为所有LLM生成的字段添加 `_llm` 后缀，添加 model 和 max_mode 配置字段

---

## 📋 改动总结

### 1. SessionMetadata 新增字段

**文件**: `types/cursor-chat/session.ts`

```typescript
export interface SessionMetadata {
  // ... 其他字段 ...

  // ⭐ 新增：LLM配置
  model?: string;                  // LLM模型名称，默认："auto"
  max_mode?: string;               // 最大模式，默认："No"

  // ⭐ 重命名：上下文信息（LLM提取）
  project_context_llm?: string;    // 原: project_context
  overall_objective_llm?: string;  // 原: overall_objective
  tags_llm?: string[];             // 原: tags
}
```

### 2. QueryAnswerPair 字段重命名

**文件**: `types/cursor-chat/pair.ts`

```typescript
export interface QueryAnswerPair {
  // ... 其他字段 ...

  // ⭐ 重命名：任务信息（LLM提取）
  objective_llm: string;               // 原: objective
  task_type_llm: TaskType;             // 原: task_type
  related_files_llm: string[];         // 原: related_files
  is_followup_llm: boolean;            // 原: is_followup
  has_context_dependency_llm: boolean; // 原: has_context_dependency
}
```

---

## 🔄 字段对应表

### Session级别

| 旧字段名 | 新字段名 | 说明 | 生成方式 |
|----------|----------|------|----------|
| `project_context` | `project_context_llm` | 项目上下文 | LLM提取 |
| `overall_objective` | `overall_objective_llm` | 整体目标 | LLM提取 |
| `tags` | `tags_llm` | 任务标签 | LLM提取 |
| - | `model` | LLM模型 | 配置/默认 "auto" |
| - | `max_mode` | 最大模式 | 配置/默认 "No" |

### Pair级别

| 旧字段名 | 新字段名 | 说明 | 生成方式 |
|----------|----------|------|----------|
| `objective` | `objective_llm` | query目标 | LLM提取 |
| `task_type` | `task_type_llm` | 任务类型 | LLM提取 |
| `related_files` | `related_files_llm` | 相关文件列表 | LLM提取 |
| `is_followup` | `is_followup_llm` | 是否后续问题 | LLM提取 |
| `has_context_dependency` | `has_context_dependency_llm` | 是否依赖上下文 | LLM提取 |

---

## 📝 已更新的文件

### TypeScript 定义

1. ✅ `types/cursor-chat/session.ts`
   - 添加 `model` 和 `max_mode` 字段
   - 重命名 `project_context_llm`, `overall_objective_llm`, `tags_llm`

2. ✅ `types/cursor-chat/pair.ts`
   - 重命名所有LLM生成字段（5个字段）
   - 更新 `QueryAnswerPairSummary` 接口

### Python 工具

3. ✅ `tools/process_long_conversation.py`
   - 更新 `EXTRACT_SESSION_METADATA_PROMPT`
   - 更新 `EXTRACT_PAIR_METADATA_PROMPT`
   - 更新所有默认值（exception handlers）
   - 更新所有字段引用（打印、条件判断、统计）

---

## 💡 设计理由

### 为什么添加 `_llm` 后缀？

1. **清晰区分数据来源**
   - `_llm` 后缀 = LLM生成的推断数据
   - 无后缀 = 确定性数据（从对话提取、用户输入、计算得出）

2. **便于调试和验证**
   - 一眼看出哪些字段是LLM生成的
   - 方便评估LLM提取质量
   - 未来可能添加人工校正版本（如 `objective_verified`）

3. **支持多源数据**
   - 未来可能同时有：
     - `objective_llm` (LLM推断)
     - `objective_manual` (人工标注)
     - `objective_verified` (经过校正)

### 为什么添加 `model` 和 `max_mode`？

1. **可追溯性**
   - 记录使用的LLM模型
   - 未来可以比较不同模型的提取质量

2. **可复现性**
   - 知道使用的模型和配置
   - 方便重新生成元数据

3. **默认值友好**
   - `model: "auto"` - 自动选择最佳模型
   - `max_mode: "No"` - 不使用最大上下文模式（节省成本）

---

## 🔍 数据示例

### 新的 session.json 示例

```json
{
  "session_id": "s_2025-10-26-10-00-00_cursor",
  "source": "cursor",
  "start_datetime": "2025-10-26T10:00:00Z",
  "total_queries": 4,
  "total_turns": 8,

  "model": "auto",
  "max_mode": "No",

  "project_context_llm": "Testing and validating connection to a LiteLLM API endpoint",
  "overall_objective_llm": "Create and refine a Python script that tests the connection",
  "tags_llm": ["api-testing", "python-scripting", "model-information"],

  "conversation_title": "Test connection and print model information",
  "exported_datetime": "2025-10-25T21:01:12-07:00",
  "cursor_version": "1.7.53"
}
```

### 新的 pairs.json 示例

```json
[
  {
    "pair_id": "s_2025-10-26-10-00-00_cursor_q01",
    "session_id": "s_2025-10-26-10-00-00_cursor",
    "query_index": 1,
    "markdown_path": "pairs/q01/chat.md",

    "objective_llm": "Test connection to LiteLLM API endpoint",
    "task_type_llm": "code",
    "related_files_llm": ["test_llm_connection.py", ".env"],
    "is_followup_llm": false,
    "has_context_dependency_llm": false,

    "goal_json_path": "pairs/q01/goal.json"
  }
]
```

---

## ⚠️ 重要说明

### LLM使用情况确认

**你已经在使用LLM了！**

当你运行 `python tools/process_long_conversation.py small_chat.md` 时，这个脚本：

1. ✅ **调用了LLM 3次**（对于4个queries）:
   - 1次: `extract_session_metadata()` - 提取session级别元数据
   - 4次: `extract_pair_metadata()` - 为每个query提取元数据
   - 4次: `generate_goal_for_pair()` - 为每个query生成goal.json

   **总共**: 1 + 4 + 4 = **9次LLM调用**

2. ✅ **已生成的LLM数据**:
   - `session.json` 中的 `project_context_llm`, `overall_objective_llm`, `tags_llm`
   - `pairs.json` 中每个pair的 `objective_llm`, `task_type_llm`, 等

### 第2步 (run_q1_batch.py) 不使用LLM

- `chat2events.py` - 解析RUNLOG，**不用LLM**
- `events2guards.py` - 计算drift，**不用LLM**

---

## 🧪 验证新字段

### 检查现有数据

```bash
# 查看session.json (应该看到旧字段名)
cat data/1_sessions/s_2025-10-26-10-00-00_cursor/session.json | jq '{project_context, overall_objective, tags}'

# 输出：
# {
#   "project_context": "...",     # 旧字段名
#   "overall_objective": "...",   # 旧字段名
#   "tags": [...]                 # 旧字段名
# }
```

### 重新运行以生成新格式

```bash
# 删除旧的session目录
rm -rf data/1_sessions/s_2025-10-26-10-00-00_cursor

# 重新运行（会使用新的字段名）
python tools/process_long_conversation.py spot-test/small_chat.md

# 查看新的session.json
cat data/1_sessions/s_*/session.json | jq '{model, max_mode, project_context_llm, overall_objective_llm, tags_llm}'

# 输出：
# {
#   "model": "auto",
#   "max_mode": "No",
#   "project_context_llm": "...",     # 新字段名
#   "overall_objective_llm": "...",   # 新字段名
#   "tags_llm": [...]                 # 新字段名
# }
```

---

## 📊 未完成的Target Files

### 回答你的问题1：都完成了！✅

所有target files已经存在：

```
data/2_runs/s_2025-10-26-10-00-00_cursor_q01/
├── events.jsonl   ✅ 已生成
├── guards.jsonl   ✅ 已生成 (这是Q1的核心输出！)
└── goal.json      ✅ 已生成

data/2_runs/s_2025-10-26-10-00-00_cursor_summary.json ✅ 已生成
```

**Q1分析已完成**，所有drift检测结果在 `guards.jsonl` 中。

---

## 🎯 下一步建议

1. **重新生成数据（使用新字段名）** ⭐
   ```bash
   # 删除旧数据
   rm -rf data/1_sessions/s_2025-10-26-10-00-00_cursor
   rm -rf data/2_runs/s_2025-10-26-10-00-00_cursor_*

   # 重新运行完整流程
   python tools/process_long_conversation.py spot-test/small_chat.md
   python tools/run_q1_batch.py data/1_sessions/s_2025-10-26-10-00-00_cursor
   ```

2. **检查新字段**
   ```bash
   cat data/1_sessions/s_*/session.json | jq .
   cat data/1_sessions/s_*/pairs.json | jq '.[0]'
   ```

3. **验证Q1结果**
   ```bash
   cat data/2_runs/s_*_summary.json
   cat data/2_runs/s_*_q01/guards.jsonl
   ```

---

**总结**：
- ✅ 所有TypeScript定义已更新
- ✅ 所有Python代码已更新
- ✅ 所有LLM生成字段添加了 `_llm` 后缀
- ✅ 添加了 `model` 和 `max_mode` 配置字段
- ⏳ 需要重新运行pipeline以生成新格式数据
