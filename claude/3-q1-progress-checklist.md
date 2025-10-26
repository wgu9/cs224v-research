# Q1 项目进度清单

## 📊 整体进度概览

**当前状态**: Phase 1 基本完成，准备测试和验证

**完成度**:
- Q1 基础功能: 80% ✅
- 长对话处理: 95% ✅
- 测试验证: 40% ⏳
- 文档: 90% ✅

---

## ✅ 已完成的工作

### 1. 核心数据结构定义 (100%)

**文件**: `types/`

- ✅ `types/index.ts` - Q1基础类型
  - GoalConfig
  - Event (EditEvent, ShellEvent)
  - GuardScores
  - Phase, Tool, GuardAction枚举

- ✅ `types/cursor-chat/` - 长对话类型
  - `session.ts` - SessionMetadata
  - `pair.ts` - QueryAnswerPair, TaskType
  - `index.ts` - 统一导出
  - **新增**: conversation_title, exported_datetime, cursor_version

**验证**: ✅ 类型定义完整，有详细注释

---

### 2. Q1核心工具 (80%)

**文件**: `tools/`

#### 2.1 事件提取 ✅
- ✅ `tools/chat2events.py` - Chat-only路径
  - 支持RUNLOG YAML
  - 启发式提取
  - plan vs edit区分

- ✅ `tools/patch2events.py` - Diff路径
  - 从patch.diff提取

- ✅ `tools/term2events.py` - 测试事件提取

#### 2.2 守卫计算 ✅
- ✅ `tools/events2guards.py` - 四守卫实现
  - Scope Guard (0.4)
  - Plan Guard (0.3)
  - Test Guard (0.2)
  - Evidence Guard (0.1)
  - **重要**: plan事件不计分（action=ok）
  - drift_score计算
  - warn/rollback判断
  - auto_fixable + fix_cmd

#### 2.3 辅助工具 ✅
- ✅ `tools/utils.py` - 通用函数
  - in_allowed(), is_forbidden()
  - path匹配

**验证**: ✅ 已在r42/r60上成功运行

---

### 3. 长对话处理系统 (95%)

**文件**: `tools/`

#### 3.1 LLM客户端 ✅
- ✅ `tools/llm_client.py`
  - OpenAI兼容API
  - 从.env读取配置
  - generate_json() / generate_text()
  - 错误处理和重试

**验证**: ✅ 测试通过

#### 3.2 长对话处理器 ✅
- ✅ `tools/process_long_conversation.py`
  - ✅ 对话拆分 (split_conversation)
  - ✅ Cursor header提取 (extract_cursor_export_header)
    - 标题提取
    - 导出时间解析（ISO8601）
    - Cursor版本提取
    - 时区处理（PDT, PST, EDT, EST等）
  - ✅ Session metadata提取（LLM）
  - ✅ Pair metadata提取（LLM）
  - ✅ Goal.json生成（LLM）
  - ✅ 上下文保留策略
  - ✅ 完整的目录结构生成
  - ✅ 详细的进度输出

**验证**: ✅ 拆分逻辑测试通过，header提取测试通过

---

### 4. 测试套件 (60%)

**文件**: `tools/`

- ✅ `tools/test_conversation_split.py`
  - 4个测试用例
  - 测试通过 ✅

- ✅ `tools/test_cursor_header.py`
  - 4个测试用例
  - 测试通过 ✅

- ✅ `test_llm_connection.py` (你的原有文件)
  - LLM连接测试

- ⏳ **缺少**: Q1端到端测试
- ⏳ **缺少**: 守卫逻辑单元测试

---

### 5. 文档 (90%)

**文件**: `claude/`, 根目录

- ✅ `claude/long-session-plan.md` - 完整设计方案
- ✅ `claude/q1-input-goaljson.md` - Goal.json生成方案
- ✅ `USAGE_long_conversation.md` - 使用指南
- ✅ `README.md` - 项目总览
- ✅ `plan-V3.md` - Q1/Q2/Q3整体规划

**验证**: ✅ 文档完整，有示例

---

## ⏳ 进行中/待完成的工作

### Phase 1: Q1验证和优化 (Priority: P0)

#### 1.1 基础功能测试 ⏳

- [ ] **创建Q1单元测试套件**
  - [ ] 测试四个守卫的计算逻辑
  - [ ] 测试drift_score计算
  - [ ] 测试plan事件不计分
  - [ ] 测试override机制
  - [ ] 测试auto_fixable判断

  **文件**: `tests/test_guards.py`（待创建）

- [ ] **端到端测试**
  - [x] r42测试（Diff路径）✅ 已验证
  - [x] r60测试（Chat-only路径）✅ 已验证
  - [ ] 创建自动化测试脚本

  **文件**: `tests/test_e2e_q1.py`（待创建）

#### 1.2 长对话处理实战测试 ⏳

- [ ] **小文件测试**（推荐先做）
  - [ ] 创建test_small.md（2-3个queries）
  - [ ] 运行完整pipeline
  - [ ] 检查生成的metadata质量
  - [ ] 检查生成的goal.json质量

  **命令**:
  ```bash
  # 创建小测试文件
  cat > test_small.md << 'EOF'
  # Test Conversation
  _Exported on 10/26/2025 at 10:00:00 PDT from Cursor (1.7.53)_

  **User**
  把 README.md 翻译成中文

  **Cursor**
  好的，我已完成翻译。

  **User**
  谢谢

  **Cursor**
  不客气！
  EOF

  # 运行处理
  python tools/process_long_conversation.py test_small.md

  # 检查结果
  ls -la data/sessions/s_*/
  cat data/sessions/s_*/session.json | jq .
  ```

- [ ] **spot-test文件测试**（大文件，谨慎）
  - [ ] 先检查会拆分多少queries
    ```bash
    python -c "
    from tools.process_long_conversation import split_conversation
    import pathlib
    content = pathlib.Path('spot-test/cursor_document_updates_and_alignment_s.md').read_text()
    pairs = split_conversation(content)
    print(f'Queries: {len(pairs)}')
    print(f'Estimated LLM calls: {1 + len(pairs) * 2}')
    "
    ```
  - [ ] 如果queries数量合理（<20），运行完整处理
  - [ ] 检查metadata提取质量
  - [ ] 抽查几个goal.json

#### 1.3 LLM Prompt优化 ⏳

- [ ] **测试并优化session metadata提取**
  - [ ] 检查project_context准确性
  - [ ] 检查overall_objective准确性
  - [ ] 检查tags相关性

- [ ] **测试并优化pair metadata提取**
  - [ ] 检查objective提取准确性
  - [ ] 检查task_type分类准确性
  - [ ] 检查is_followup判断准确性
  - [ ] 检查has_context_dependency判断准确性

- [ ] **测试并优化goal.json生成**
  - [ ] 检查allowed_paths合理性
  - [ ] 检查forbidden_paths合理性
  - [ ] 检查required_tests提取准确性

---

### Phase 2: Q1与长对话集成 (Priority: P1)

#### 2.1 为每个Query运行Q1分析 ⏳

- [ ] **创建批量Q1分析脚本**

  **文件**: `tools/run_q1_on_session.py`（待创建）

  ```python
  # 伪代码
  def run_q1_on_session(session_id):
      session_dir = Path(f"data/sessions/{session_id}")
      pairs = json.loads((session_dir / "pairs.json").read_text())

      for pair in pairs:
          q_idx = pair['query_index']
          pair_md = session_dir / pair['markdown_path']
          goal_json = session_dir / pair['goal_json_path']

          run_dir = session_dir / 'runs' / f"q{q_idx:02d}"
          run_dir.mkdir(exist_ok=True)

          # 运行chat2events
          # 运行events2guards
          # 保存结果
  ```

- [ ] **Q1结果聚合和可视化**

  **文件**: `tools/analyze_session_results.py`（待创建）

  - [ ] 统计多少queries触发drift
  - [ ] 分析drift类型分布
  - [ ] 生成summary报告

#### 2.2 数据质量验证 ⏳

- [ ] **检查生成的goal.json质量**
  - [ ] 随机抽查10个goal.json
  - [ ] 验证allowed_paths合理性
  - [ ] 验证required_tests正确性

- [ ] **检查metadata质量**
  - [ ] 验证task_type分类准确性
  - [ ] 验证上下文依赖判断准确性

---

### Phase 3: Q2和Q3实现 (Priority: P2)

#### 3.1 Q2: 模式卡提取与复用 ⏳

**当前状态**: 设计完成，未实现

**待实现**:
- [ ] `agent/reflexion.py` - 反思生成
- [ ] `agent/extract_card.py` - 模式卡提取
- [ ] `q2_memory/retrieve.py` - 模式卡检索
- [ ] 模式卡数据结构验证

**依赖**: 需要Q1成功运行的数据（events.jsonl + guards.jsonl）

#### 3.2 Q3: 动态抽象与视图路由 ⏳

**当前状态**: 设计完成，未实现

**待实现**:
- [ ] `q3_views/render.py` - 视图路由和渲染
- [ ] `data/profiles/` - 用户画像
- [ ] terse/guided视图生成

**依赖**: 需要模式卡数据（Q2）

---

## 🎯 建议的下一步行动

### 立即可做（今天/明天）

1. **小文件测试** ⭐⭐⭐
   ```bash
   # 创建小测试文件并运行完整pipeline
   python tools/process_long_conversation.py test_small.md
   ```
   - 预期时间: 5-10分钟（含LLM调用）
   - 目标: 验证整个流程work

2. **检查spot-test文件大小**
   ```bash
   python -c "from tools.process_long_conversation import split_conversation; import pathlib; print(f'Queries: {len(split_conversation(pathlib.Path(\"spot-test/cursor_document_updates_and_alignment_s.md\").read_text()))}')"
   ```
   - 预期时间: 5秒
   - 目标: 了解处理成本

3. **创建Q1单元测试** ⭐⭐
   - 为四个守卫创建测试
   - 验证计算逻辑正确性
   - 预期时间: 1-2小时

### 本周可做

4. **运行spot-test文件**（如果queries<30）
   - 完整处理
   - 检查质量
   - 预期时间: 30分钟-2小时（取决于queries数量）

5. **创建Q1批量运行脚本**
   - 对session的每个query运行Q1
   - 聚合结果
   - 预期时间: 2-3小时

6. **优化LLM prompts**
   - 根据实际结果调整
   - 提高准确性
   - 预期时间: 1-2小时

---

## 📁 文件结构总览

```
agent-memory-lab-v3/
├── types/                          ✅ 完成
│   ├── index.ts                    ✅ Q1基础类型
│   └── cursor-chat/                ✅ 长对话类型
│       ├── index.ts
│       ├── session.ts
│       └── pair.ts
│
├── tools/                          ✅ 80%完成
│   ├── llm_client.py               ✅ LLM客户端
│   ├── process_long_conversation.py ✅ 长对话处理
│   ├── chat2events.py              ✅ Chat→Events
│   ├── patch2events.py             ✅ Diff→Events
│   ├── term2events.py              ✅ Terminal→Events
│   ├── events2guards.py            ✅ Events→Guards
│   ├── utils.py                    ✅ 工具函数
│   ├── test_conversation_split.py  ✅ 拆分测试
│   ├── test_cursor_header.py       ✅ Header测试
│   └── run_q1_on_session.py        ⏳ 待创建
│
├── tests/                          ⏳ 待创建
│   ├── test_guards.py              ⏳ 守卫单元测试
│   └── test_e2e_q1.py              ⏳ Q1端到端测试
│
├── agent/                          ⏳ Q2待实现
│   ├── reflexion.py                ⏳ 反思生成
│   └── extract_card.py             ⏳ 模式卡提取
│
├── q2_memory/                      ⏳ Q2待实现
│   └── retrieve.py                 ⏳ 模式卡检索
│
├── q3_views/                       ⏳ Q3待实现
│   └── render.py                   ⏳ 视图路由
│
├── data/
│   ├── runs/                       ✅ 示例数据
│   │   ├── r42/                    ✅ Diff示例
│   │   └── r60/                    ✅ Chat示例
│   ├── sessions/                   ✅ 长对话输出
│   └── patterns/                   ⏳ Q2模式卡库
│
├── claude/                         ✅ 文档
│   ├── long-session-plan.md        ✅ 设计方案
│   ├── q1-input-goaljson.md        ✅ Goal生成
│   └── q1-progress-checklist.md    ✅ 本文件
│
├── README.md                       ✅ 项目说明
├── plan-V3.md                      ✅ 总体规划
├── USAGE_long_conversation.md      ✅ 使用指南
├── test_llm_connection.py          ✅ LLM测试
└── requirements.txt                ✅ 依赖
```

---

## 🚦 风险和注意事项

### 高风险项

1. **LLM API成本** ⚠️
   - 每个session: 1次调用
   - 每个query: 2次调用（metadata + goal）
   - 50个queries = 101次调用
   - **缓解**: 先用小文件测试

2. **LLM输出质量** ⚠️
   - JSON格式可能不正确
   - metadata可能不准确
   - **缓解**: 已添加容错处理，使用默认值

3. **Token限制** ⚠️
   - 单个query可能超过token限制
   - **缓解**: 已限制输入长度（4000-6000字符）

### 中风险项

4. **时区解析** ⚠️
   - 支持主要美国时区
   - **缓解**: 不识别的时区使用UTC

5. **文件格式变化** ⚠️
   - Cursor导出格式可能变化
   - **缓解**: 容错处理，部分解析失败不影响主流程

---

## ✅ 验收标准

### Q1基础功能验收

- [x] 能从patch.diff提取events ✅
- [x] 能从cursor.md提取events ✅
- [x] 能计算四个守卫分数 ✅
- [x] 能正确判断warn/rollback ✅
- [x] plan事件不计分 ✅

### 长对话处理验收

- [x] 能拆分长对话 ✅
- [x] 能提取Cursor header ✅
- [ ] LLM能提取准确的session metadata ⏳
- [ ] LLM能提取准确的pair metadata ⏳
- [ ] LLM能生成合理的goal.json ⏳
- [ ] 能为每个query运行Q1分析 ⏳

### 整体系统验收

- [ ] 端到端测试通过 ⏳
- [ ] 文档完整且准确 ✅
- [ ] 有足够的测试覆盖 ⏳
- [ ] 性能可接受（<5分钟处理50个queries） ⏳

---

## 📊 总结

**完成的核心工作**:
1. ✅ 完整的数据结构定义
2. ✅ Q1核心功能实现并验证
3. ✅ 长对话拆分和header提取
4. ✅ LLM集成和prompt设计
5. ✅ 基础测试套件
6. ✅ 完整文档

**下一步关键任务**:
1. ⏳ 小文件测试验证完整流程
2. ⏳ 创建Q1单元测试
3. ⏳ 优化LLM prompts
4. ⏳ 实现Q1批量运行
5. ⏳ Q2/Q3实现（Phase 2）

**当前状态**: 🟢 Ready for Testing
**建议优先级**: 先测试验证，再优化，最后扩展到Q2/Q3

---

**更新时间**: 2025-10-26
**文档维护者**: Claude + Jeremy
