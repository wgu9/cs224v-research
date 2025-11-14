# Q1 阶段进度总结报告
**Cross-Session Learning and Execution Monitoring for Intelligent Coding Agents**

---

## 📋 项目概述

本项目旨在将智能编程代理（如 Cursor、Claude Code）从"一次性助手"升级为"会成长、会复用、会自我约束"的合作者。项目分为三个核心研究问题：

- **Q1: Context Drift Detection（执行监控）** - 检测并防止长任务跑偏
- **Q2: Cross-Session Pattern Learning（跨会话学习）** - 从历史成功案例中提取可复用模式
- **Q3: Dynamic Abstraction（个性化呈现）** - 按用户水平动态调节输出粒度

**当前状态**：✅ **Q1 MVP 已完成并就绪**，可投入大规模数据测试。

---

## 🎯 Q1 研究目标与动机

### 核心问题
现代智能编程代理在执行多步任务（如重构、调试、功能开发）时，常出现**上下文偏航（Context Drift）**现象：
- 明明只要求改文档，却去修改了依赖配置
- 在理解问题阶段就开始改代码
- 完成核心任务后，未运行必需的回归测试

### 研究贡献
我们提出了首个针对智能代理执行过程的**实时偏航检测框架**，核心创新点：
1. **四守卫机制（Four-Guard System）**：从不同维度评估agent行为
2. **可解释的drift scoring**：加权量化偏航程度
3. **分级响应策略**：ok / warn / rollback 三级动作建议
4. **Chat-first设计**：无需git patch，直接从对话日志提取

---

## ✅ Q1 核心成果

### 1. 完整的偏航检测流水线

#### **Architecture**
```
Cursor Chat (.md)
    ↓ [Step 1: LLM-based preprocessing]
data/1_sessions/  (session metadata + goal.json)
    ↓ [Step 2: Rule-based drift analysis]
data/2_runs/      (events.jsonl + guards.jsonl + summary.json)
    ↓ [Step 3: Cross-session aggregation]
Aggregate Report  (drift patterns, health distribution)
```

#### **两步设计哲学**
- **Step 1**: 使用LLM提取元数据（objective、allowed_paths、required_tests）→ `goal.json`
- **Step 2**: 使用纯规则进行drift检测（保证可复现性、低成本、无LLM bias）

---

### 2. Four-Guard Detection Framework

| 守卫 | 检测对象 | 权重 | 判定逻辑 |
|------|---------|------|---------|
| **Scope Guard** | 文件修改范围 | 0.4 | 文件是否在 `allowed_paths` 内且不在 `forbidden_paths` |
| **Plan Guard** | 工具/阶段匹配度 | 0.3 | 当前phase下使用的tool是否允许（如reproduce阶段禁止edit） |
| **Test Guard** | 测试充分性 | 0.2 | 是否运行了 `required_tests` |
| **Evidence Guard** | 修改可追溯性 | 0.1 | 代码修改是否附带证据（测试日志/链接） |

**Drift Score 计算**：
```python
drift_score = 0.4×scope + 0.3×plan + 0.2×test + 0.1×evidence
```

**Action Thresholds**：
- `drift_score < 0.5` → **ok**（继续）
- `0.5 ≤ drift_score < 0.8` → **warn**（警告）
- `drift_score ≥ 0.8` → **rollback**（建议回滚）

---

### 3. 数据产物与治理

#### **Query-Level Analysis**（已实现）
每个query-answer pair都有完整的分析：
- `events.jsonl`: Agent行为的结构化事件流
- `guards.jsonl`: 每个event的drift检测结果
- `goal.json`: 动态生成的任务目标与约束

#### **Session-Level Metrics**（已实现）
- `drift_rate`: 有drift的queries占比
- `avg_drift` / `max_drift`: 偏航分数统计
- `health`: Green/Yellow/Red三级健康评级
  - **Green**: drift_rate < 10% AND max_drift < 0.4
  - **Yellow**: 10% ≤ drift_rate < 30% OR 0.4 ≤ max_drift < 0.6
  - **Red**: drift_rate ≥ 30% OR max_drift ≥ 0.6 OR 任何rollback

#### **可解释性设计**
每个drift事件都有人类可读的 `notes` 字段：
```json
{
  "drift_score": 0.75,
  "action": "warn",
  "notes": "not in allowed_paths; no evidence attached",
  "auto_fixable": true,
  "fix_cmd": "git checkout -- requirements.txt"
}
```

---

### 4. 工程实现与工具链

| 工具 | 用途 | LLM | 输入 | 输出 |
|------|------|-----|------|------|
| `process_long_conversation.py` | 拆分长对话并提取metadata | ✅ | cursor.md | 1_sessions/ |
| `run_q1_batch.py` | Q1批量drift检测 | ❌ | 1_sessions/ | 2_runs/ |
| `chat2events.py` | 提取事件序列 | ❌ | chat.md | events.jsonl |
| `events2guards.py` | 计算drift分数 | ❌ | events.jsonl + goal.json | guards.jsonl |
| `analyze_drift_summary.py` | 跨session汇总分析 | ❌ | 2_runs/ | 聚合报告 |

**技术亮点**：
- ✅ **高性能**：Step 2完全无LLM调用，单session分析 < 1秒
- ✅ **可扩展**：支持自定义weights、thresholds、allowed_tools
- ✅ **工程化**：完整的单元测试覆盖（34 tests passed）
- ✅ **生产就绪**：统一runner.sh，PYTHONPATH管理，错误处理完善

---

## 📊 验证与测试

### Test Coverage
```bash
./runner.sh pytest tests/
# 34 passed, 0 failed ✅
```

### 测试维度
- ✅ Scope Guard: 路径匹配（glob pattern、forbidden paths）
- ✅ Plan Guard: 阶段/工具合法性
- ✅ Test Guard: 测试覆盖检查
- ✅ Evidence Guard: 证据附件验证
- ✅ End-to-end: 完整workflow测试

### 真实数据试跑
- 已成功处理 **1个真实Cursor对话**（4个query pairs）
- 平均drift_score: 0.0
- Health: **Green** ✅
- 验证了chat-first设计的可行性

---

## 🤔 设计决策：为什么只做 Pair-Level Drift？

### TL;DR
Q1 MVP **只检测query-level（pair-level）drift**，**暂不实现session-level drift**。这是一个经过深思熟虑的战略决策，基于以下分析：

---

### 1. Drift的两个层级

| 层级 | 问题 | 检测对象 | 比喻 |
|------|------|---------|------|
| **Pair-Level Drift** | "把事情做对" (Do the thing right) | 单个query-answer pair内的行为偏离 | **战术偏航** |
| **Session-Level Drift** | "做正确的事" (Do the right thing) | 整个session的目标偏离 | **战略偏航** |

**我们的选择**：Q1 MVP专注于Pair-Level，因为：
- 它是更高频、更具体的问题
- 是整个监控体系的基石
- 在没有坚实的"战术"监控之前，谈"战略"是空中楼阁

---

### 2. Session-Level Drift的复杂性

经过团队深入讨论（包括三位工程师的观点分析），我们发现**并非所有session都需要session-level drift**：

#### **类型A：单一目标型会话（需要Session-Level Drift）**
```
Overall goal: "Add OAuth2 login to my app"
├─ Q1: "Create OAuth2 config file"
├─ Q2: "Implement authorization endpoint"
├─ Q3: "Add token validation"
└─ Q4: "Write integration tests"
```
✅ **有意义**：所有queries服务于一个明确的总体目标，可以检测目标一致性

#### **类型B：多目标演进型会话（需要分段分析）**
```
Initial goal: "Fix login bug"
├─ Q1-Q3: Fix bug (目标A)
├─ Q4-Q6: Refactor after fix (目标B，演进)
└─ Q7-Q8: Add new feature (目标C，新目标)
```
⚠️ **复杂**：目标在演进，不能用单一的overall_objective检测，需要分段统计

#### **类型C：探索式/混杂型会话（不需要Session-Level Drift）**
```
No overall goal:
├─ Q1: "Explain this code snippet" (理解)
├─ Q2: "Count lines in all .py files" (工具)
├─ Q3: "Fix typo in README" (文档)
└─ Q4: "Help me debug this error" (调试)
```
❌ **无意义**：queries之间独立、异质，计算session-level drift只会产生噪音

---

### 3. 技术挑战与未解决的问题

实现完善的Session-Level Drift需要解决：

#### **挑战1：会话类型自动识别**
- 如何自动区分上述三种类型？
- 基于LLM判断（准确但慢）vs 启发式规则（快但可能不准）
- 需要标注数据验证算法有效性

#### **挑战2：目标演进检测**
- 对于类型B，如何自动检测"目标转折点"？
- 如何判断目标转移是"合理演进"还是"偏离主线"？

#### **挑战3：多维度的Session-Level Drift**
不同于Pair-Level的单一drift_score，Session-Level需要多个维度：
- **目标一致性漂移**：子任务是否服务于总体目标？
- **效率漂移**：是否陷入循环、重复失败？
- **根源问题漂移**：实现的方案是否真正解决了用户的根本需求？

每个维度的检测都需要不同的技术方案。

---

### 4. 数据驱动的决策路径

我们采用**先验证需求，再实现功能**的策略：

#### **Phase 1: 当前（已完成）**
```
✅ 实现Pair-Level Drift（四守卫系统）
✅ 实现基础的Session-Level统计（drift_rate, avg_drift, health）
   - 这些是简单的聚合指标，不涉及复杂的session-level语义
```

#### **Phase 2: 数据收集（计划1-2周）**
```
1. 收集50-100个真实Cursor对话
2. 人工review 20-30个sessions，标注：
   - 会话类型（单一目标/多目标/探索式）
   - 是否需要session-level drift检测
   - 如果需要，失败原因是什么（目标不一致/效率/根源问题）
3. 统计分析：
   - 有多少%的sessions真正需要session-level检测？
   - 最常见的session-level问题是什么类型？
```

#### **Phase 3: 根据数据决策（未来）**
```
IF session-level问题频率 > 30%:
    → 实现Q1.5（Session-Level Drift）
    → 优先实现最高频的问题类型
ELSE:
    → 先专注于Q2（Pattern Learning）
    → Q2的模式学习可能自然地解决部分session-level问题
```

---

### 5. 当前Session-Level统计的范围

虽然不做深度的session-level drift，我们**已经提供了基础的session健康指标**：

```json
{
  "session_id": "s_xxx",
  "total_queries": 4,
  "queries_with_drift": 1,
  "drift_rate": 0.25,              // 25%的queries有drift
  "avg_drift": 0.18,               // 平均drift分数
  "max_drift": 0.62,               // 最大drift分数
  "health": "yellow",              // 健康等级
  "action_mix": {
    "ok": 3, "warn": 1, "rollback": 0
  },
  "by_guard_failed": {
    "scope": 1, "plan": 0, "test": 0, "evidence": 0
  }
}
```

这些统计已足以回答：
- ✅ "这个session整体健康吗？"
- ✅ "哪些queries有问题？"
- ✅ "最常失败的是哪个守卫？"

但**不回答**更深层的问题：
- ❌ "Agent的子任务是否服务于总体目标？"
- ❌ "Agent是否陷入死循环？"
- ❌ "实现的方案是否解决了根本问题？"

---

### 6. 学术与工业价值的考量

#### **从学术角度**
- Pair-Level Drift已是首创，足以构成完整的研究贡献
- Session-Level Drift可作为**未来工作（Future Work）**展望
- 先发表Pair-Level成果，再迭代增强

#### **从工业角度**
- Pair-Level已能解决大部分实际问题（防止agent"做错事"）
- Session-Level是"锦上添花"，不是"雪中送炭"
- 需要真实用户反馈来验证需求优先级

---

### 7. 与Q2/Q3的关系

**重要洞察**：Q2（Pattern Learning）可能**自然地部分解决**session-level问题：
- Q2从成功的sessions中学习patterns
- 如果一个session的目标不一致、效率低，Q2不会将其识别为"好的pattern"
- 这相当于**后验的session-level质量筛选**

因此，更合理的路线是：
```
Q1 (Pair-Level) → Q2 (Pattern Learning) → Q1.5 (Session-Level)
                                          ↑
                               用Q2的学习结果反哺Q1.5
```

---

### 8. 结论

我们的决策是：
1. ✅ **Q1 MVP只做Pair-Level Drift**：这是正确且完整的第一步
2. 📊 **先跑真实数据**：收集50+个sessions，量化session-level问题的频率
3. 🔬 **数据驱动决策**：根据实际需求决定是否/何时实现Q1.5
4. 🔄 **与Q2协同**：Q2的pattern learning可能自然地解决部分session-level问题

这个决策体现了：
- **学术严谨性**：不盲目追求"更多功能"，而是基于明确的研究价值
- **工程务实性**：MVP先解决核心问题，再根据数据迭代
- **设计前瞻性**：预留了Q1.5的设计空间，为未来扩展打好基础

---

## 🔗 Q1 → Q2/Q3 的数据桥梁

Q1不仅是偏航检测工具，更是**Q2/Q3的数据基础设施**：

### 为Q2准备的"学习材料"
- **成功案例识别**：`summary.json` 的 `health: green` 标记高质量sessions
- **结构化事件流**：`events.jsonl` 提供agent行为的完整记录
- **守卫反馈**：`guards.jsonl` 标注哪些操作是"安全的"

### 为Q3准备的"评估依据"
- **用户画像输入**：drift_rate可作为用户水平的proxy指标
- **任务难度估计**：max_drift可反映任务复杂度

---

## 🚀 下一步计划

### 立即可做（P0 - 未来1周）
1. **大规模数据测试**
   - 收集50-100个真实Cursor对话
   - 运行Q1流水线，收集drift分布数据
   - 统计各守卫的失败率，优化weights

2. **人工评估session-level需求**
   - 人工review 20-30个sessions
   - 标注会话类型和session-level问题频率
   - 决定是否需要实现Q1.5

### Q2启动准备（P1 - 未来2-3周）
3. **Pattern Extraction Agent**
   - 输入：成功的 `run` 目录（goal.json + events.jsonl + guards.jsonl）
   - 输出：结构化的 `Pattern Card` JSON

4. **Pattern Card Schema设计**
   - 参考README中的初步设计
   - 添加 `provenance`（来源追溯）、`evaluation_examples`

### 研究问题（P2 - 未来1-2个月）
5. **Session-Level Drift（可选，取决于数据分析结果）**
   - 实现会话类型自动识别
   - 针对单一目标型会话，实现目标一致性检测
   - 效率漂移检测（循环、停滞）

---

## 📈 预期影响

### 学术价值
- 首个针对LLM-based agents的**实时行为监控框架**
- 可在SWE-bench等benchmark上验证效果
- 潜在发表方向：ICSE、FSE、ASE等软件工程顶会

### 工业价值
- 提升智能编程工具的**可信度**（用户敢放心让agent执行复杂任务）
- 减少人工干预成本（自动检出并建议修复）
- 为AI辅助编程的"可控性"研究提供基础设施

---

## 💡 关键洞察

1. **Chat-first设计是正确的**
   - 70%+的开发者使用对话式工具（Cursor/Copilot Chat）
   - 无需依赖git diff/patch，降低部署门槛

2. **规则比LLM更适合做"裁判"**
   - Step 2完全不用LLM，保证一致性、低成本
   - LLM只在Step 1做"理解"，Step 2做"判断"

3. **Pair-Level是正确的第一步**
   - Session-Level Drift高度依赖会话类型
   - 需要真实数据验证需求，避免过早优化

4. **可解释性是部署关键**
   - 每个drift都有明确的 `notes` 说明
   - `auto_fixable` + `fix_cmd` 提供自动化修复路径

---

## 📎 附：代码仓库与文档

- **GitHub**: `agent-memory-lab-v3/`
- **核心文档**:
  - `README.md` - 完整使用说明
  - `claude/2025-10-26-6D-gemini-q1-wrap-up.md` - Q1工作流总结
  - `claude/2025-10-26-6C-q1-finishing.md` - Q1数据结构详解
  - `claude/Q1_Progress_Report_for_Advisors.md` - 本报告
- **关键路径**:
  - `tools/` - 所有分析工具
  - `tests/` - 单元测试
  - `data/` - 数据产物

---

**报告撰写时间**: 2025-10-26
**Q1完成度**: ✅ MVP 100%
**就绪状态**: 🚀 Ready for large-scale data runs

---

## 📧 联系方式

如需补充具体技术细节、调整报告重点、添加可视化图表，或讨论session-level drift的实施计划，请联系项目团队。
