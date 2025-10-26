# 长对话处理：Session管理与嵌套结构设计

## 🎯 问题定义

**场景**：cursor对话非常长（几万行，50个user query），直接处理会遇到：
1. **Token限制**：单个LLM调用无法处理全部内容
2. **任务混合**：不同query可能是完全不同的任务
3. **上下文依赖**：同session内的query可能有依赖关系
4. **效率问题**：一次性处理所有内容浪费计算资源

**目标**：设计嵌套结构，既能处理长对话，又能保留上下文，还能独立分析每个query-answer pair。

---

## 📐 数据结构设计

### 1. Session Metadata（会话元数据）

定义位置：`types/cursor-chat/session.ts`

```typescript
export interface SessionMetadata {
  session_id: string;              // 唯一标识，如 "s_20251026_cursor_001"
  source: string;                  // "cursor" | "claude" | "aider"
  start_datetime: string;          // ISO8601: "2025-10-26T10:00:00Z"
  end_datetime?: string;           // 可选，会话结束时间
  total_queries: number;           // user query总数，如 50
  total_turns: number;             // 总轮次（user + assistant），如 100
  project_context?: string;        // 项目上下文（从第一轮推断）
  overall_objective?: string;      // 整体目标（LLM推断）
  tags?: string[];                 // 标签，如 ["documentation", "refactoring"]
  meta?: Record<string, any>;      // 扩展字段
}
```

### 2. Query-Answer Pair Metadata（每个QA对的元数据）

定义位置：`types/cursor-chat/pair.ts`

```typescript
export interface QueryAnswerPair {
  pair_id: string;                 // "s_20251026_cursor_001_q05"
  session_id: string;              // 关联到session
  query_index: number;             // 1, 2, 3, ..., 50

  // 时间信息
  timestamp?: string;              // 该query的时间

  // 内容引用
  markdown_path: string;           // 该pair的markdown文件路径

  // 上下文信息
  prev_pair_id?: string;           // 前一个pair的ID
  has_context_dependency: boolean; // 是否依赖前面的上下文

  // 任务信息（LLM提取）
  objective: string;               // 该query的具体目标
  task_type: TaskType;             // "doc" | "code" | "test" | "debug" | "refactor"
  related_files: string[];         // 提到的文件
  is_followup: boolean;            // 是否是前一个query的后续

  // Goal.json引用
  goal_json_path?: string;         // 该pair生成的goal.json路径

  meta?: Record<string, any>;
}

export type TaskType = 'doc' | 'code' | 'test' | 'debug' | 'refactor' | 'config';
```

### 3. 目录结构

```
data/sessions/<session_id>/
├── session.json                      # Session metadata
├── pairs.json                        # 所有QA pairs的元数据列表
├── raw/
│   └── full_conversation.md          # 原始完整对话
├── pairs/
│   ├── q01_translate_readme.md       # Query 1的QA pair
│   ├── q02_fix_test.md               # Query 2的QA pair
│   ├── ...
│   └── q50_final_review.md           # Query 50的QA pair
├── goals/
│   ├── q01_goal.json                 # Query 1的goal.json
│   ├── q02_goal.json                 # Query 2的goal.json
│   └── ...
└── runs/
    ├── q01/                          # Query 1的Q1分析结果
    │   ├── events.jsonl
    │   └── guards.jsonl
    ├── q02/
    │   ├── events.jsonl
    │   └── guards.jsonl
    └── ...
```

---

## 🔪 长对话拆分策略

### 策略1：基于Pattern的智能拆分

使用正则表达式识别User-Assistant轮次边界：

```python
import re
from typing import List, Tuple

def split_conversation(full_md: str) -> List[Tuple[int, str, str]]:
    """
    拆分长对话为多个query-answer pairs

    Returns:
        List of (query_index, user_message, assistant_messages)
    """
    pairs = []
    lines = full_md.split('\n')

    current_user = None
    current_assistant = []
    query_idx = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # 检测到新的User消息
        if re.match(r'\*\*User\*\*', line, re.IGNORECASE):
            # 保存前一个pair
            if current_user is not None:
                pairs.append((
                    query_idx,
                    current_user,
                    '\n\n'.join(current_assistant)
                ))
                query_idx += 1

            # 开始新的pair
            current_user = ''
            current_assistant = []
            i += 1

            # 收集user消息直到遇到assistant
            while i < len(lines) and not re.match(
                r'\*\*(?:Cursor|Claude|Assistant)\*\*',
                lines[i],
                re.IGNORECASE
            ):
                current_user += lines[i] + '\n'
                i += 1
            continue

        # 检测到Assistant消息
        if re.match(r'\*\*(?:Cursor|Claude|Assistant)\*\*', lines[i], re.IGNORECASE):
            i += 1
            assistant_msg = ''
            # 收集assistant消息直到遇到下一个User
            while i < len(lines) and not re.match(r'\*\*User\*\*', lines[i], re.IGNORECASE):
                assistant_msg += lines[i] + '\n'
                i += 1
            current_assistant.append(assistant_msg)
            continue

        i += 1

    # 保存最后一个pair
    if current_user is not None:
        pairs.append((query_idx, current_user, '\n\n'.join(current_assistant)))

    return pairs
```

### 策略2：保留上下文的方式

每个pair的markdown包含两部分：

```markdown
# Query 5: Fix authentication bug

## Context from Previous Query (Q4)

**Previous User Request:**
> Add user registration feature

**Previous Assistant Summary:**
> Created user registration endpoint in src/auth/register.py

---

## Current Query-Answer

**User**
Fix the authentication bug in login.py

**Cursor**
I'll fix the token validation logic...
```

---

## 🤖 LLM处理流程

### Phase 1: 提取Session Metadata

**输入**：完整对话的前2000行 + 最后500行

**Prompt**：
```python
EXTRACT_SESSION_METADATA_PROMPT = """
Analyze this long cursor conversation and extract session-level metadata.

**Input**: First 2000 lines + last 500 lines of the conversation

**Task**: Generate session metadata JSON

**Schema**:
```json
{
  "session_id": "s_<timestamp>_<source>_<seq>",
  "source": "cursor",
  "start_datetime": "2025-10-26T10:00:00Z",
  "total_queries": 50,
  "project_context": "Python web API project",
  "overall_objective": "Add authentication and internationalization",
  "tags": ["authentication", "i18n", "refactoring"]
}
```

**Instructions**:
1. Infer project_context from the first few queries
2. Summarize overall_objective across all queries
3. Count total_queries by counting "**User**" occurrences
4. Extract tags based on task types mentioned

Output pure JSON.
"""
```

**实现**：
```python
def extract_session_metadata(full_md: str, api_key: str) -> dict:
    """从完整对话提取session metadata"""
    # 取前2000行 + 后500行
    lines = full_md.split('\n')
    sample = '\n'.join(lines[:2000] + ['...'] + lines[-500:])

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        system=EXTRACT_SESSION_METADATA_PROMPT,
        messages=[{"role": "user", "content": sample}]
    )

    content = response.content[0].text.strip()
    if content.startswith("```"):
        content = '\n'.join(content.split('\n')[1:-1])

    meta = json.loads(content)

    # 生成session_id如果不存在
    if not meta.get('session_id'):
        import time
        meta['session_id'] = f"s_{int(time.time())}_{meta.get('source', 'cursor')}"

    return meta
```

### Phase 2: 为每个QA Pair生成Metadata

**输入**：
- 当前pair的完整内容
- 前一个pair的完整内容（可选）

**Prompt**：
```python
EXTRACT_PAIR_METADATA_PROMPT = """
Analyze this query-answer pair and extract metadata.

**Context** (if exists):
Previous query-answer pair for reference

**Current Query-Answer**:
{current_pair}

**Task**: Generate pair metadata JSON

**Schema**:
```json
{
  "pair_id": "s_xxx_q05",
  "query_index": 5,
  "objective": "Fix authentication bug in login.py",
  "task_type": "debug",
  "related_files": ["src/auth/login.py"],
  "is_followup": true,
  "has_context_dependency": true
}
```

**Task Types**:
- "doc": Documentation/translation
- "code": New feature/implementation
- "debug": Bug fix
- "test": Testing
- "refactor": Code refactoring
- "config": Configuration change

**is_followup**: true if this query builds on the previous query
**has_context_dependency**: true if understanding this query requires previous context

Output pure JSON.
"""
```

**实现**：
```python
def extract_pair_metadata(
    pair_content: str,
    query_index: int,
    session_id: str,
    api_key: str
) -> dict:
    """从单个QA pair提取metadata"""
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        system=EXTRACT_PAIR_METADATA_PROMPT,
        messages=[{"role": "user", "content": pair_content[:4000]}]
    )

    content = response.content[0].text.strip()
    if content.startswith("```"):
        content = '\n'.join(content.split('\n')[1:-1])

    meta = json.loads(content)
    meta['query_index'] = query_index
    meta['session_id'] = session_id
    meta['pair_id'] = f"{session_id}_q{query_index:02d}"

    return meta
```

### Phase 3: 为每个Pair生成Goal.json

对于每个pair，根据是否有上下文依赖：

```python
def generate_goal_for_pair(
    pair: QueryAnswerPair,
    pair_content: str,
    prev_pair_content: Optional[str] = None,
    api_key: str
) -> dict:
    """为单个QA pair生成goal.json"""

    if pair.has_context_dependency and prev_pair_content:
        # 包含前一个pair的内容
        context = f"""
## Previous Query-Answer:
{prev_pair_content}

## Current Query-Answer:
{pair_content}
"""
    else:
        # 独立分析
        context = pair_content

    # 调用之前设计的generate_goal_from_cursor
    goal = generate_goal_from_cursor(context, api_key)
    goal["run_id"] = f"{pair.session_id}_q{pair.query_index:02d}"

    return goal
```

---

## 🔄 完整处理流程

### 主流程实现

```python
#!/usr/bin/env python3
"""
处理长对话：拆分 → 提取metadata → 生成goal.json
"""

import json
import pathlib
from typing import List, Optional
import anthropic

def process_long_conversation(
    full_md_path: str,
    output_dir: str,
    api_key: str
) -> str:
    """
    处理长对话的完整流程

    Args:
        full_md_path: 完整对话markdown路径
        output_dir: 输出目录（data/sessions）
        api_key: Anthropic API key

    Returns:
        session_id
    """
    full_md = pathlib.Path(full_md_path).read_text(encoding='utf-8')

    # Step 1: 提取session metadata
    print("📊 Extracting session metadata...")
    session_meta = extract_session_metadata(full_md, api_key)
    session_id = session_meta['session_id']

    # 创建目录结构
    session_dir = pathlib.Path(output_dir) / session_id
    (session_dir / 'raw').mkdir(parents=True, exist_ok=True)
    (session_dir / 'pairs').mkdir(parents=True, exist_ok=True)
    (session_dir / 'goals').mkdir(parents=True, exist_ok=True)

    # 保存原始对话
    (session_dir / 'raw' / 'full_conversation.md').write_text(full_md, encoding='utf-8')

    # Step 2: 拆分对话
    print("🔪 Splitting conversation into query-answer pairs...")
    pairs = split_conversation(full_md)
    print(f"   Found {len(pairs)} query-answer pairs")

    # Step 3: 为每个pair生成metadata和goal.json
    pair_metas = []
    prev_pair_content = None

    for idx, (query_idx, user_msg, assistant_msg) in enumerate(pairs):
        print(f"\n📝 Processing Q{idx+1}/{len(pairs)}...")

        # 构建pair内容
        pair_content = f"**User**\n{user_msg}\n\n**Assistant**\n{assistant_msg}"

        # 如果需要上下文，附加前一个pair
        if idx > 0:
            pair_content_with_context = f"""## Previous Query-Answer:
{prev_pair_content}

---

## Current Query-Answer:
{pair_content}
"""
        else:
            pair_content_with_context = pair_content

        # 提取pair metadata
        pair_meta = extract_pair_metadata(
            pair_content_with_context,
            idx + 1,
            session_id,
            api_key
        )

        # 保存pair markdown
        pair_filename = f"q{idx+1:02d}_{sanitize_filename(pair_meta['objective'])}.md"
        pair_path = session_dir / 'pairs' / pair_filename

        # 如果有上下文依赖，保存带上下文的版本
        if pair_meta.get('has_context_dependency') and prev_pair_content:
            final_content = f"""# Query {idx+1}: {pair_meta['objective']}

## Context from Previous Query

{prev_pair_content[:500]}...

---

## Current Query-Answer

{pair_content}
"""
        else:
            final_content = f"""# Query {idx+1}: {pair_meta['objective']}

{pair_content}
"""

        pair_path.write_text(final_content, encoding='utf-8')
        pair_meta['markdown_path'] = str(pair_path)

        # 生成goal.json
        print(f"   🎯 Generating goal.json for Q{idx+1}...")

        # 根据has_context_dependency决定输入
        goal_input = pair_content_with_context if pair_meta.get('has_context_dependency') else pair_content
        goal = generate_goal_from_cursor(goal_input, api_key)
        goal['run_id'] = f"{session_id}_q{idx+1:02d}"

        goal_path = session_dir / 'goals' / f"q{idx+1:02d}_goal.json"
        goal_path.write_text(json.dumps(goal, indent=2, ensure_ascii=False), encoding='utf-8')
        pair_meta['goal_json_path'] = str(goal_path)

        pair_metas.append(pair_meta)
        prev_pair_content = pair_content

        print(f"   ✅ Q{idx+1}: {pair_meta['objective'][:50]}...")

    # Step 4: 保存session metadata和pairs列表
    session_meta['total_queries'] = len(pairs)
    (session_dir / 'session.json').write_text(
        json.dumps(session_meta, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    (session_dir / 'pairs.json').write_text(
        json.dumps(pair_metas, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )

    print(f"\n✅ Session processed: {session_id}")
    print(f"   📁 Output: {session_dir}")
    print(f"   📊 {len(pairs)} query-answer pairs extracted")

    return session_id


def sanitize_filename(s: str) -> str:
    """清理文件名"""
    import re
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[-\s]+', '_', s)
    return s[:50].lower()


# ============================================
# 使用示例
# ============================================

if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) < 2:
        print("Usage: python process_long_conversation.py <full_conversation.md>")
        print("\nRequires: ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    full_md_path = sys.argv[1]
    output_dir = "data/sessions"

    session_id = process_long_conversation(full_md_path, output_dir, api_key)

    print(f"\n🎉 Done! Session: {session_id}")
    print(f"\nNext steps:")
    print(f"  1. Review session.json and pairs.json")
    print(f"  2. Run Q1 analysis on each pair:")
    print(f"     for goal in data/sessions/{session_id}/goals/*.json; do")
    print(f"       PYTHONPATH=. python tools/chat2events.py \\")
    print(f"         data/sessions/{session_id}/runs/$(basename $goal .json)")
    print(f"     done")
```

---

## 🎯 上下文保留策略（关键设计）

### 两种模式

#### 模式A：轻量级（默认推荐）
```python
# 总是附加完整的前一个pair
if idx > 0:
    full_input = prev_pair_content + "\n---\n" + current_pair_content
else:
    full_input = current_pair_content

# LLM会自动判断has_context_dependency
pair_meta = extract_pair_metadata(full_input, ...)
```

#### 模式B：智能选择
```python
# 先用轻量prompt判断是否需要上下文
needs_context = check_if_needs_context(current_pair_content)

if needs_context and prev_pair_content:
    full_input = prev_pair_content + "\n---\n" + current_pair_content
else:
    full_input = current_pair_content
```

### 推荐策略

**默认：总是附加前一个pair**
- 优点：LLM能看到完整上下文，判断更准确
- 缺点：token消耗稍高
- 适用：大多数场景

**限制：只有前500字符**
```python
prev_summary = prev_pair_content[:500] + "..."
```

---

## 📊 数据查询与分析

### 查询Session概览

```python
def get_session_overview(session_id: str) -> dict:
    """获取session概览"""
    session_dir = pathlib.Path(f"data/sessions/{session_id}")

    session_meta = json.loads((session_dir / 'session.json').read_text())
    pairs_meta = json.loads((session_dir / 'pairs.json').read_text())

    return {
        "session": session_meta,
        "total_queries": len(pairs_meta),
        "task_types": [p['task_type'] for p in pairs_meta],
        "followup_count": sum(1 for p in pairs_meta if p.get('is_followup')),
        "context_dependent_count": sum(1 for p in pairs_meta if p.get('has_context_dependency'))
    }
```

### 查询特定Query

```python
def get_query_details(session_id: str, query_index: int) -> dict:
    """获取特定query的详细信息"""
    session_dir = pathlib.Path(f"data/sessions/{session_id}")
    pairs_meta = json.loads((session_dir / 'pairs.json').read_text())

    pair = pairs_meta[query_index - 1]
    goal = json.loads(pathlib.Path(pair['goal_json_path']).read_text())

    # 检查是否已运行Q1分析
    run_dir = session_dir / 'runs' / f"q{query_index:02d}"
    if run_dir.exists():
        events = [json.loads(line) for line in (run_dir / 'events.jsonl').read_text().splitlines()]
        guards = [json.loads(line) for line in (run_dir / 'guards.jsonl').read_text().splitlines()]
    else:
        events = None
        guards = None

    return {
        "pair": pair,
        "goal": goal,
        "events": events,
        "guards": guards,
        "has_drift": any(g['action'] != 'ok' for g in guards) if guards else None
    }
```

---

## 🧪 测试示例

### 示例：处理10287行的对话

```bash
# 1. 处理长对话
export ANTHROPIC_API_KEY=sk-xxx
python tools/process_long_conversation.py \
  spot-test/cursor_document_updates_and_alignment_s.md

# 输出：
# 📊 Extracting session metadata...
#    ✅ Session: s_1730001234_cursor
# 🔪 Splitting conversation...
#    Found 50 query-answer pairs
# 📝 Processing Q1/50...
#    🎯 Generating goal.json for Q1...
#    ✅ Q1: Update README documentation
# 📝 Processing Q2/50...
#    🎯 Generating goal.json for Q2...
#    ✅ Q2: Fix typo in setup.py
# ...
# ✅ Session processed: s_1730001234_cursor

# 2. 查看session结构
tree data/sessions/s_1730001234_cursor/
# ├── session.json
# ├── pairs.json
# ├── raw/
# │   └── full_conversation.md
# ├── pairs/
# │   ├── q01_update_readme_documentation.md
# │   ├── q02_fix_typo_in_setup.md
# │   └── ...
# └── goals/
#     ├── q01_goal.json
#     ├── q02_goal.json
#     └── ...

# 3. 对每个pair运行Q1分析
for i in {1..50}; do
  pair_id=$(printf "q%02d" $i)
  echo "Analyzing $pair_id..."

  # 创建run目录
  mkdir -p data/sessions/s_1730001234_cursor/runs/$pair_id

  # 读取goal.json
  goal_path=data/sessions/s_1730001234_cursor/goals/${pair_id}_goal.json

  # 读取pair markdown
  pair_md=$(ls data/sessions/s_1730001234_cursor/pairs/${pair_id}_*.md)

  # 运行Q1分析
  PYTHONPATH=. python tools/chat2events.py \
    --cursor-md="$pair_md" \
    --goal="$goal_path" \
    --output=data/sessions/s_1730001234_cursor/runs/$pair_id
done
```

---

## ✅ 总结

### 核心设计原则

| 设计点 | 实现方案 |
|--------|---------|
| **Session管理** | 独立的session.json，包含整体metadata |
| **Query拆分** | 正则匹配`**User**`和`**Assistant**`边界 |
| **上下文保留** | 默认附加前一个pair的完整内容 |
| **Metadata提取** | LLM分两层：session级 + pair级 |
| **Goal生成** | 每个pair独立生成goal.json |
| **Q1分析** | 每个pair独立运行Q1，结果存入runs/<query_id>/ |

### 优势

✅ **可扩展**：支持任意长度的对话
✅ **上下文感知**：保留必要的依赖关系
✅ **独立分析**：每个pair可独立运行Q1
✅ **可追溯**：完整的metadata链路
✅ **易查询**：结构化的数据便于统计分析

### 下一步实施

1. ✅ 数据结构定义已完成（`types/cursor-chat/`）
2. ⏳ 实现`tools/process_long_conversation.py`
3. ⏳ 测试10287行的spot-test文件
4. ⏳ 优化LLM prompt提高准确性
5. ⏳ 添加查询和可视化工具

---

## 📚 相关文档

- `types/cursor-chat/session.ts` - Session数据结构
- `types/cursor-chat/pair.ts` - Query-Answer Pair数据结构
- `q1-input-goaljson.md` - Goal.json生成方案
- `tools/process_long_conversation.py` - 主处理脚本（待实现）
