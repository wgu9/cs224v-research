# 长对话处理工具使用指南

## 📦 已创建的工具

### 1. `tools/llm_client.py` - LLM客户端
通用的LLM API客户端，使用你的OpenAI兼容API。

**配置**：从 `.env` 文件读取
```bash
LLM_API_KEY=your_api_key
LLM_API_ENDPOINT=https://your-endpoint.com
```

### 2. `tools/process_long_conversation.py` - 主处理工具
完整的长对话处理pipeline。

### 3. `tools/run_q1_batch.py` - Q1批处理工具 ⭐ NEW
批量运行Q1分析，打通端到端工作流。

### 4. `tests/test_conversation_split.py` - 拆分测试
测试对话拆分逻辑（不需要LLM）。

### 5. `tests/test_cursor_header.py` - Header提取测试
测试Cursor导出头部信息提取。

---

## 🚀 快速开始

### Step 1: 配置环境

```bash
# 1. 确保.env文件存在并配置正确
cat .env
# LLM_API_KEY=sk-...
# LLM_API_ENDPOINT=https://...

# 2. 安装依赖
pip install requests python-dotenv
```

### Step 2: 测试拆分逻辑（不需要LLM）

```bash
# 测试对话拆分是否正常工作
python tests/test_conversation_split.py

# 测试Header提取
python tests/test_cursor_header.py

# 预期输出：
# ✅ ALL TESTS PASSED
```

### Step 3: 测试LLM连接

```bash
# 使用你的test_llm_connection.py测试
python test_llm_connection.py

# 或者测试LLM客户端
python tools/llm_client.py
```

### Step 4: 处理长对话（第1步）

```bash
# 处理你的spot-test文件
python tools/process_long_conversation.py \
  spot-test/cursor_document_updates_and_alignment_s.md

# 或指定输出目录
python tools/process_long_conversation.py \
  spot-test/cursor_document_updates_and_alignment_s.md \
  data/my_sessions
```

### Step 5: 运行Q1批量分析（第2步）⭐ NEW

```bash
# 分析整个session（自动处理所有queries）
python tools/run_q1_batch.py data/1_sessions/s_2025-10-26-10-00-00_cursor

# 只分析特定queries
python tools/run_q1_batch.py data/1_sessions/s_2025-10-26-10-00-00_cursor --queries q01,q02,q03

# 查看结果摘要
cat data/2_runs/s_2025-10-26-10-00-00_cursor_summary.json
```

---

## 📊 输出结构

处理完成后，会生成以下目录结构：

```
data/
├── 1_sessions/                               # 第1步：预处理长对话
│   └── s_2025-10-26-10-00-00_cursor/        # Session目录（友好的时间戳格式）
│       ├── session.json                      # Session元数据
│       ├── pairs.json                        # 所有QA pairs的索引
│       ├── raw/
│       │   └── full_conversation.md          # 原始对话
│       └── pairs/                            # ⭐ 按query聚合的结构
│           ├── q01/                          # Query 1
│           │   ├── chat.md                   # 对话内容
│           │   └── goal.json                 # Goal配置
│           ├── q02/                          # Query 2
│           │   ├── chat.md
│           │   └── goal.json
│           └── ...
│
└── 2_runs/                                   # 第2步：对单个子任务运行Q1分析
    └── s_2025-10-26-10-00-00_cursor_q01/    # 单次运行目录
        ├── goal.json                         # 从1_sessions自动复制
        ├── raw/
        │   └── cursor.md                     # 从1_sessions自动复制
        ├── events.jsonl                      # Q1分析结果
        └── guards.jsonl                      # Drift检测结果
```

---

## 🧪 处理示例

### 示例1：小文件测试（推荐先测试）

创建一个小的测试文件 `test_conversation.md`：

```markdown
**User**
把 README.md 翻译成中文，不要改任何代码文件。

**Cursor**
好的，我会只修改 README.md。

**Cursor**
已完成翻译。运行测试：
pytest -k doc_lang_check  # passed

**User**
谢谢，再检查一下有没有typo。

**Cursor**
检查完毕，没有发现拼写错误。
```

然后处理：

```bash
python tools/process_long_conversation.py test_conversation.md
```

### 示例2：处理spot-test文件

**注意**：这个文件有10287行，可能包含50+个queries，会消耗大量LLM API调用！

```bash
# 先检查文件大小
wc -l spot-test/cursor_document_updates_and_alignment_s.md

# 处理（可能需要10-30分钟，取决于queries数量）
python tools/process_long_conversation.py \
  spot-test/cursor_document_updates_and_alignment_s.md
```

**建议**：
- 先用小文件测试
- 确保API有足够的quota
- 考虑分批处理（可以修改代码添加`--max-queries`参数）

---

## 🔍 查看结果

### 查看Session概览

```bash
# 查看session.json
cat data/1_sessions/s_*/session.json | jq .

# 输出示例：
# {
#   "session_id": "s_2025-10-26-10-00-00_cursor",
#   "conversation_title": "Add authentication and i18n support",
#   "exported_datetime": "2025-10-26T10:00:00-07:00",
#   "cursor_version": "1.7.53",
#   "total_queries": 50,
#   "project_context": "Python web API project",
#   "overall_objective": "Add authentication and i18n",
#   "tags": ["authentication", "i18n", "refactoring"]
# }
```

### 查看Pairs列表

```bash
# 查看所有pairs
cat data/1_sessions/s_*/pairs.json | jq '.[] | {query_index, objective, task_type}'

# 输出示例：
# {
#   "query_index": 1,
#   "objective": "Translate README to Chinese",
#   "task_type": "doc"
# }
# {
#   "query_index": 2,
#   "objective": "Fix typo in setup.py",
#   "task_type": "code"
# }
```

### 查看特定Query的Goal

```bash
# 查看第一个query的goal.json
cat data/1_sessions/s_*/goals/q01_goal.json | jq .

# 输出示例：
# {
#   "run_id": "s_2025-10-26-10-00-00_cursor_q01",
#   "objective": "Translate README.md to Chinese",
#   "allowed_paths": ["README.md"],
#   "forbidden_paths": ["requirements.txt", "src/**"],
#   "required_tests": ["doc_lang_check"]
# }
```

---

## ⚙️ 高级选项

### 添加Dry-Run模式（只拆分不调用LLM）

如果你想先看看会拆分出多少个queries，可以修改代码添加dry-run模式：

```python
# 在process_long_conversation.py中添加参数
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if args.dry_run:
        # 只拆分，不调用LLM
        pairs = split_conversation(full_md)
        print(f"Would process {len(pairs)} queries")
        return
```

### 限制处理的Queries数量

```python
# 添加max_queries参数
parser.add_argument('--max-queries', type=int, default=None)

# 在处理循环中
for idx, (q_idx, user_msg, assistant_msg) in enumerate(pairs):
    if args.max_queries and idx >= args.max_queries:
        break
    # ... 处理逻辑
```

---

## 🐛 故障排除

### 问题1：ModuleNotFoundError: No module named 'dotenv'

```bash
pip install python-dotenv requests
```

### 问题2：LLM_API_KEY not found

```bash
# 检查.env文件
cat .env

# 确保包含：
# LLM_API_KEY=...
# LLM_API_ENDPOINT=...
```

### 问题3：LLM API调用失败

```bash
# 测试连接
python test_llm_connection.py

# 检查API endpoint是否正确
# 检查API key是否有效
# 检查是否有足够的quota
```

### 问题4：JSON解析失败

LLM有时可能返回格式不正确的JSON。代码已包含容错处理：
- 自动移除markdown代码块
- 失败时使用默认值
- 详细的错误日志

如果仍然失败，可以：
1. 检查LLM的temperature设置（降低到0.1）
2. 增加max_tokens
3. 检查system prompt是否清晰

---

## 📈 性能优化建议

### 1. 批量处理

如果有多个长对话文件，可以批量处理：

```bash
for file in spot-test/*.md; do
  echo "Processing $file..."
  python tools/process_long_conversation.py "$file"
done
```

### 2. 并行处理（谨慎）

如果API支持并发：

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(process_pair, pair) for pair in pairs]
```

**注意**：注意API rate limits！

### 3. 缓存LLM响应

对于相同的输入，可以缓存LLM响应：

```python
import hashlib
import json

def cached_llm_call(prompt, cache_dir="llm_cache"):
    cache_key = hashlib.sha256(prompt.encode()).hexdigest()
    cache_file = Path(cache_dir) / f"{cache_key}.json"

    if cache_file.exists():
        return json.loads(cache_file.read_text())

    result = llm_client.generate_json(...)
    cache_file.parent.mkdir(exist_ok=True)
    cache_file.write_text(json.dumps(result))
    return result
```

---

## ✅ 检查清单

在处理大文件前，确保：

- [ ] .env文件配置正确
- [ ] LLM连接测试通过 (`python test_llm_connection.py`)
- [ ] 拆分逻辑测试通过 (`python tools/test_conversation_split.py`)
- [ ] 已用小文件测试过完整流程
- [ ] API有足够的quota
- [ ] 磁盘空间足够（每个query约10-50KB）

---

## 🎯 下一步

处理完成后，你可以：

1. **查看生成的metadata**
   ```bash
   cat data/1_sessions/s_*/session.json
   cat data/1_sessions/s_*/pairs.json
   ```

2. **对每个query运行Q1分析**
   ```bash
   cd data/1_sessions/s_2025-10-26-10-00-00_cursor
   for goal in goals/*.json; do
     pair_id=$(basename "$goal" .json)
     mkdir -p runs/$pair_id
     # 运行你的Q1分析工具
     PYTHONPATH=. python tools/chat2events.py --goal="$goal" ...
   done
   ```

3. **分析统计数据**
   - 查看task_type分布
   - 查看followup比例
   - 查看context dependency比例

4. **优化prompt**
   - 根据结果调整LLM prompts
   - 提高metadata提取准确性
   - 优化goal.json生成质量

---

## 📚 相关文档

- `claude/long-session-plan.md` - 完整设计方案
- `claude/q1-input-goaljson.md` - Goal.json生成方案
- `types/cursor-chat/` - TypeScript数据结构定义
- `test_llm_connection.py` - LLM连接测试

---

## 💡 提示

1. **先小后大**：先用小文件（2-3个queries）测试，确保一切正常后再处理大文件
2. **监控成本**：每个query会调用3次LLM（session metadata只调用1次），注意API费用
3. **保存中间结果**：代码已自动保存所有中间结果，可以随时中断和继续
4. **检查质量**：处理完成后，随机抽查几个pairs的metadata和goal.json，确保质量
