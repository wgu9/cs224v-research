# Q1 Context Drift Detection - 进度检查清单

**Last Updated**: 2025-10-25
**Project**: Agent Memory Lab V3 - Q1 Implementation

---

## 📊 总体进度概览

| 模块 | 完成度 | 状态 |
|------|--------|------|
| 核心数据结构 | 100% | ✅ 完成 |
| Q1核心工具 | 80% | 🟡 进行中 |
| 长对话处理系统 | 95% | 🟡 待测试 |
| 测试套件 | 60% | 🟡 进行中 |
| 文档 | 90% | ✅ 基本完成 |
| **Q1整体** | **80%** | **🟡 核心完成，待验证** |

---

## ✅ 已完成的工作

### 1. 核心数据结构定义 (100%)

**文件**: `types/index.ts`
- ✅ `Phase` 类型: reproduce, modify, test, regress
- ✅ `Tool` 类型: edit, shell, browse, plan
- ✅ `GuardAction` 类型: ok, warn, rollback
- ✅ `GoalConfig` 接口: 包含 run_id, objective, allowed_paths, forbidden_paths, checkpoints, required_tests, thresholds, weights
- ✅ `BaseEvent` 接口: id, run_id, step, ts, phase, tool, why, evidence, confidence
- ✅ `EditEvent` 和 `ShellEvent` 接口
- ✅ `GuardScores` 接口: 四个guard分数, drift_score, action, auto_fixable

**文件**: `types/cursor-chat/session.ts`
- ✅ `SessionMetadata` 接口: session_id, source, cursor导出信息 (title, datetime, version), start/end datetime, 查询数量, 项目上下文
- ✅ Cursor导出元数据字段:
  - `conversation_title`: 对话标题
  - `exported_datetime`: ISO8601格式导出时间
  - `cursor_version`: Cursor版本号

**文件**: `types/cursor-chat/pair.ts`
- ✅ `TaskType` 类型: doc, code, debug, test, refactor, config
- ✅ `QueryAnswerPair` 接口: pair_id, session_id, query_index, markdown路径, 上下文依赖, objective, task_type, related_files

**文件**: `types/cursor-chat/index.ts`
- ✅ 导出所有类型定义

### 2. Q1核心工具 (80%)

**文件**: `tools/events2guards.py` ✅
- ✅ 实现四个守卫计算逻辑:
  - `scope_guard` (0.4权重): 检查路径是否在allowed/forbidden列表
  - `plan_guard` (0.3权重): 检查工具是否允许在当前phase使用
  - `test_guard` (0.2权重): 检查required_tests是否运行
  - `evidence_guard` (0.1权重): 检查modify阶段是否附加evidence
- ✅ 加权drift_score计算: 0.4×scope + 0.3×plan + 0.2×test + 0.1×evidence
- ✅ Action决策: drift ≥ 0.8 → rollback, ≥ 0.5 → warn, < 0.5 → ok
- ✅ Plan事件特殊处理: 总是返回 action=ok, drift=0.0 (计划不算偏移)
- ✅ 已测试: r42数据运行成功 (requirements.txt被标记为drift_score=0.75)

**文件**: `tools/chat2events.py` ✅
- ✅ 从cursor.md chat提取Event列表
- ✅ 解析RUNLOG YAML块
- ✅ 提取edit/shell events with phase
- ⚠️ 已知问题: YAML解析可能将applied标记为plan (待修复)

**文件**: `tools/patch2events.py` ✅ (备用路径)
- ✅ 从git diff提取Event列表
- ✅ 解析patch格式并提取文件路径

### 3. 长对话处理系统 (95%)

**文件**: `tools/llm_client.py` ✅
- ✅ LLMClient类: 封装用户的OpenAI兼容API
- ✅ 支持从.env加载配置 (LLM_API_KEY, LLM_API_ENDPOINT)
- ✅ `generate_json()` 方法: 返回结构化JSON
- ✅ 自动移除markdown代码围栏 (```json ... ```)
- ✅ 温度默认0.1 (一致性输出)

**文件**: `tools/process_long_conversation.py` ✅
- ✅ `split_conversation()`: 使用正则表达式拆分User/Assistant对话
  - 支持 `**User**` 和 `**Cursor**`/`**Assistant**` 标记
  - 处理多段assistant回复
  - 返回 (query_index, user_msg, assistant_msg) 元组列表
- ✅ `extract_cursor_export_header()`: 提取cursor导出文件头部信息
  - 第1行: `# Title` → conversation_title
  - 第2行: `_Exported on ... from Cursor (version)_` → exported_datetime (ISO8601), cursor_version
  - 支持多个时区: PDT/PST/EDT/EST/CDT/CST/MDT/MST/UTC
- ✅ `extract_session_metadata()`: LLM提取会话级元数据
  - 从前20个query-answer pairs提取样本 (max 4000 chars)
  - 返回: project_context, overall_objective, tags
- ✅ `extract_pair_metadata()`: LLM提取单个pair元数据
  - 返回: objective, task_type, related_files, is_followup, has_context_dependency
- ✅ `generate_goal_for_pair()`: LLM生成goal.json
  - 返回: objective, allowed_paths, forbidden_paths, checkpoints, required_tests
- ✅ `process_long_conversation()`: 完整pipeline
  - 拆分对话 → 提取session metadata → 为每个pair提取metadata + 生成goal.json
  - 保存文件: session_<id>/session.json, pairs.json, q_<N>.md, q_<N>/goal.json

**LLM Prompts** ✅
- ✅ `EXTRACT_SESSION_METADATA_PROMPT`: 会话级提取
- ✅ `EXTRACT_PAIR_METADATA_PROMPT`: Pair级提取
- ✅ `GENERATE_GOAL_FROM_PAIR_PROMPT`: Goal.json生成
- 所有prompt包含严格的schema约束和多个示例

### 4. 测试套件 (60%)

**文件**: `tools/test_conversation_split.py` ✅
- ✅ 测试1: 基本拆分 (2个queries)
- ✅ 测试2: 多assistant消息 (3个queries)
- ✅ 测试3: 短对话
- ✅ 测试4: 真实文件 (spot-test/cursor_document_updates_and_alignment_s.md)
- **状态**: 所有测试通过 ✅

**文件**: `tools/test_cursor_header.py` ✅
- ✅ 测试1: 完整header提取
- ✅ 测试2: 无header
- ✅ 测试3: 部分header
- ✅ 测试4: 真实spot-test文件
- **状态**: 所有测试通过 ✅
- **验证输出**:
  ```
  conversation_title: Document updates and alignment suggestions
  exported_datetime: 2025-10-25T20:26:15-07:00
  cursor_version: 1.7.53
  ```

**手动测试**: `tools/events2guards.py` ✅
```bash
PYTHONPATH=. python tools/events2guards.py data/runs/r42
```
- ✅ 成功检测到requirements.txt偏移 (drift_score=0.75, action=warn)

### 5. 文档 (90%)

**文件**: `USAGE_long_conversation.md` ✅
- ✅ 快速开始指南
- ✅ 使用示例
- ✅ 故障排查
- ✅ 性能提示

**文件**: `claude/long-session-plan.md` (需创建) ⏳
- ⏳ 完整的长对话处理设计文档 (之前讨论了，但未保存)

**文件**: `claude/q1-input-goaljson.md` (需创建) ⏳
- ⏳ LLM生成goal.json的设计文档 (之前讨论了，但未保存)

**文件**: `README.md` ✅
- ✅ 项目整体说明已存在

---

## ⏳ 待完成的工作

### Priority 0: 立即验证 (核心功能测试)

#### 1. 小文件LLM测试 ⭐⭐⭐
**目标**: 验证完整pipeline (拆分 → LLM提取 → goal.json生成)

**步骤**:
```bash
# 创建小测试文件 (2-3个user queries)
cat > test_small.md << 'EOF'
# Small Test Session
_Exported on 10/25/2025 at 21:30:00 PDT from Cursor (1.7.53)_

**User**
帮我修复login.py中的bug，用户无法登录

**Cursor**
我发现问题在第42行，缺少了密码验证...

**User**
测试通过了吗？

**Cursor**
是的，我运行了pytest tests/test_login.py，所有测试通过
EOF

# 运行完整pipeline
python tools/process_long_conversation.py test_small.md
```

**检查**:
- [ ] session.json生成且包含cursor元数据
- [ ] pairs.json包含2个pair
- [ ] 每个pair的goal.json质量检查:
  - [ ] allowed_paths合理
  - [ ] objective准确
  - [ ] task_type正确分类
- [ ] has_context_dependency检测准确

**预期时间**: 5-10分钟

#### 2. Q1 Unit Tests ⭐⭐⭐
**目标**: 确保Q1核心逻辑正确

**创建**: `tests/test_guards.py`

**测试用例**:
```python
def test_scope_guard_allowed_path():
    # 编辑allowed_paths中的文件 → scope_guard=0.0

def test_scope_guard_forbidden_path():
    # 编辑forbidden_paths中的文件 → scope_guard=1.0

def test_plan_guard_legal_tool():
    # reproduce阶段使用browse → plan_guard=0.0

def test_plan_guard_illegal_tool():
    # reproduce阶段使用edit → plan_guard=1.0

def test_test_guard_tests_run():
    # required_tests都运行了 → test_guard=0.0

def test_test_guard_tests_missing():
    # required_tests未运行 → test_guard=1.0

def test_evidence_guard_with_evidence():
    # modify阶段附加evidence → evidence_guard=0.0

def test_evidence_guard_no_evidence():
    # modify阶段无evidence → evidence_guard=0.5

def test_plan_event_always_ok():
    # tool=plan → action=ok, drift_score=0.0

def test_drift_calculation():
    # scope=1.0, plan=0.5, test=0.0, evidence=0.0
    # → drift = 0.4*1.0 + 0.3*0.5 + 0.2*0.0 + 0.1*0.0 = 0.55
    # → action = warn

def test_rollback_threshold():
    # drift=0.85 → action=rollback

def test_warn_threshold():
    # drift=0.6 → action=warn
```

**运行**:
```bash
pytest tests/test_guards.py -v
```

**预期时间**: 30-60分钟编写 + 10分钟调试

#### 3. Spot-test文件处理 (如果queries<30) ⭐⭐
**目标**: 真实数据验证

**步骤**:
```bash
# 先检查query数量
python -c "
from tools.process_long_conversation import split_conversation
with open('spot-test/cursor_document_updates_and_alignment_s.md') as f:
    pairs = split_conversation(f.read())
print(f'Total queries: {len(pairs)}')
"

# 如果<30，运行完整处理
python tools/process_long_conversation.py spot-test/cursor_document_updates_and_alignment_s.md
```

**质量检查**:
- [ ] Session metadata准确
- [ ] 每个pair的objective有意义
- [ ] Goal.json的allowed_paths不是空列表
- [ ] has_context_dependency识别合理

**预期时间**: 5-15分钟 (取决于query数量)

---

### Priority 1: 完善集成 (让Q1真正可用)

#### 4. Q1批量运行器 ⭐⭐
**目标**: 对session中每个pair运行Q1分析

**创建**: `tools/run_q1_on_session.py`

**逻辑**:
```python
import json
from pathlib import Path
from tools.chat2events import extract_events_from_chat
from tools.events2guards import calculate_guards

def run_q1_on_session(session_dir: str):
    """
    For each pair in session:
    1. Load goal.json
    2. Load q_N.md
    3. Run chat2events
    4. Run events2guards
    5. Save to runs/session_<id>_q<N>/
    """
    session_path = Path(session_dir)
    pairs_json = session_path / "pairs.json"

    with open(pairs_json) as f:
        pairs = json.load(f)

    results = []
    for pair in pairs:
        pair_id = pair['pair_id']
        goal_path = session_path / f"q_{pair['query_index']}" / "goal.json"
        md_path = Path(pair['markdown_path'])

        # Run Q1
        goal = json.load(open(goal_path))
        events = extract_events_from_chat(md_path.read_text(), goal)
        guards = [calculate_guards(e, goal) for e in events]

        # Save results
        output_dir = Path("data/runs") / f"{pair_id}"
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / "events.json", 'w') as f:
            json.dump(events, f, indent=2)
        with open(output_dir / "guards.json", 'w') as f:
            json.dump(guards, f, indent=2)

        results.append({
            "pair_id": pair_id,
            "drift_events": [g for g in guards if g['action'] in ['warn', 'rollback']]
        })

    # Summary report
    with open(session_path / "q1_summary.json", 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✅ Processed {len(pairs)} pairs")
    print(f"⚠️  Drift detected in {sum(1 for r in results if r['drift_events'])} pairs")

if __name__ == "__main__":
    import sys
    run_q1_on_session(sys.argv[1])
```

**使用**:
```bash
python tools/run_q1_on_session.py session_20251025_cursor_001
```

**预期时间**: 1小时编写 + 30分钟测试

#### 5. LLM Prompt优化 ⭐
**目标**: 基于测试结果改进prompt质量

**待验证**:
- [ ] task_type分类准确率 (预期>90%)
- [ ] has_context_dependency检测准确率 (预期>85%)
- [ ] allowed_paths是否过于宽泛 (手动review)
- [ ] objective是否准确提取用户意图

**调整策略**:
- 如果task_type错误 → 在prompt中增加更多示例
- 如果allowed_paths过宽 → 强调"只列出直接修改的文件"
- 如果objective偏离 → 强调"从用户消息中提取，不要添加额外推测"

**预期时间**: 1-2小时 (迭代调整)

#### 6. End-to-End测试 ⭐
**目标**: 自动化测试完整流程

**创建**: `tests/test_e2e_q1.py`

```python
def test_e2e_simple_session():
    """测试: 小对话 → 拆分 → LLM → Q1分析 → 验证结果"""
    # 1. 创建test.md
    # 2. process_long_conversation(test.md)
    # 3. run_q1_on_session(session_dir)
    # 4. 断言: drift检测结果符合预期

def test_e2e_with_drift():
    """测试: 包含明确偏移的对话 → 应该检测到drift"""

def test_e2e_chat_vs_diff():
    """测试: chat路径和diff路径结果一致性"""
```

**预期时间**: 2小时

---

### Priority 2: 扩展到Q2和Q3

#### 7. Q2 Pattern Cards 实现
**文件待创建**:
- `agent/reflexion.py`: LLM反思成功/失败原因
- `agent/extract_card.py`: 从run中提取pattern card
- `q2_memory/retrieve.py`: 检索相似pattern cards

**依赖**: Q1必须稳定运行并产生高质量数据

#### 8. Q3 Dynamic Abstraction 实现
**文件待创建**:
- `q3_views/render.py`: 根据user_level渲染不同详细程度
- User profile管理

**依赖**: Q2必须有一定数量的pattern cards

---

## 🗂️ 文件结构概览

```
agent-memory-lab-v3/
├── types/
│   ├── index.ts                     ✅ Q1核心类型
│   └── cursor-chat/
│       ├── session.ts               ✅ Session元数据
│       ├── pair.ts                  ✅ Pair元数据
│       └── index.ts                 ✅ 导出
├── tools/
│   ├── llm_client.py                ✅ LLM API封装
│   ├── process_long_conversation.py ✅ 长对话处理pipeline
│   ├── chat2events.py               ✅ Chat → Events
│   ├── patch2events.py              ✅ Diff → Events (备用)
│   ├── events2guards.py             ✅ Events → Guards (核心Q1)
│   ├── test_conversation_split.py   ✅ 拆分逻辑测试
│   ├── test_cursor_header.py        ✅ Header提取测试
│   └── run_q1_on_session.py         ⏳ 待创建
├── tests/
│   ├── test_guards.py               ⏳ 待创建 (P0)
│   └── test_e2e_q1.py               ⏳ 待创建 (P1)
├── claude/
│   ├── q1-progress-checklist.md     ✅ 本文档
│   ├── q1-input-goaljson.md         ⏳ 待创建
│   └── long-session-plan.md         ⏳ 待创建
├── data/runs/
│   └── r42/                         ✅ 测试数据 (已验证)
├── spot-test/
│   └── cursor_document_updates...md ✅ 真实cursor导出文件
├── USAGE_long_conversation.md       ✅ 使用文档
└── README.md                        ✅ 项目说明
```

---

## ⚠️ 已知问题和风险

### 1. YAML解析精度 (中风险)
**问题**: `chat2events.py`可能将applied edits错误标记为plan events
**影响**: 影响drift计算准确性
**缓解**: 使用diff路径作为fallback，或改进YAML解析逻辑
**优先级**: P1

### 2. LLM输出质量 (中风险)
**问题**: LLM可能生成不准确的allowed_paths或task_type
**影响**: Q1分析准确性下降
**缓解**: 通过真实数据测试并迭代优化prompt
**优先级**: P0 (通过测试验证)

### 3. Token成本 (低风险)
**问题**: 50个queries需要~101次LLM调用
**影响**: API成本
**缓解**: 用户已有LLM API，成本可控；可设置并发限制
**优先级**: P2

### 4. 长上下文截断 (低风险)
**问题**: 单个query-answer pair可能超过LLM上下文
**影响**: 提取质量下降
**缓解**: 当前设计限制每个chunk 4000-6000字符
**优先级**: P2

---

## 📋 验证标准

### Q1核心功能验证
- [ ] **拆分准确性**: 100% queries正确拆分
- [ ] **Header提取**: 100% cursor元数据提取成功
- [ ] **LLM元数据**: >90% task_type分类准确
- [ ] **Goal.json质量**: >85% allowed_paths合理 (手动review)
- [ ] **Drift检测**: 已知drift case全部检测到
- [ ] **No false positives**: 正常操作不触发warn/rollback

### 性能验证
- [ ] 10-query session: <2分钟处理完成
- [ ] 50-query session: <10分钟处理完成
- [ ] API调用成功率: >95%

---

## 🎯 建议的下一步行动

### 立即可做 (今天/明天)

1. **小文件测试** ⭐⭐⭐
   ```bash
   # 创建小测试文件并运行完整pipeline
   python tools/process_long_conversation.py test_small.md
   ```
   - 预期时间: 5-10分钟 (含LLM调用)
   - 目标: 验证整个流程work

2. **Q1 Unit Tests** ⭐⭐⭐
   ```bash
   # 创建并运行单元测试
   pytest tests/test_guards.py -v
   ```
   - 预期时间: 1-2小时
   - 目标: 确保Q1核心逻辑正确

3. **Spot-test处理** (如果queries<30) ⭐⭐
   ```bash
   python tools/process_long_conversation.py spot-test/cursor_document_updates_and_alignment_s.md
   ```
   - 预期时间: 5-15分钟
   - 目标: 真实数据验证

### 本周可做

4. **创建Q1批量运行器** ⭐⭐
   - 预期时间: 1-2小时
   - 目标: 让Q1真正可用

5. **End-to-End测试** ⭐
   - 预期时间: 2小时
   - 目标: 自动化完整流程

### 下周可做

6. **LLM Prompt优化** (基于测试结果)
7. **开始Q2设计和实现**

---

## 💡 总结

**当前状态**: Q1基础功能已完成80%，长对话处理系统完成95%

**核心成就**:
- ✅ 完整的数据结构定义
- ✅ 四个guard的完整实现和验证
- ✅ 长对话拆分和处理pipeline
- ✅ Cursor元数据提取
- ✅ LLM集成完成
- ✅ 基础测试通过

**关键缺失**:
- ⏳ 真实数据的LLM测试验证
- ⏳ Q1 unit tests
- ⏳ Q1批量运行器

**建议**: 优先完成P0任务 (小文件测试 + unit tests)，验证Q1核心功能稳定后再扩展到Q2/Q3。
