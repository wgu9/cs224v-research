# Yucheng Meeting Summary - Focus on Q1 (Context Drift Detection)

**Date**: 2025-10-29
**Meeting with**: Yucheng (CS224v Advisor)

---

## 🎯 核心结论：Focus on Q1, Not Q2

### Yucheng 的关键观点

**原计划**：
- Q1: In-session memory (Context Drift Detection) - 监控 agent 是否偏离目标
- Q2: Cross-session memory (Pattern Extraction & Reuse) - 跨任务学习和复用

**Yucheng 的建议**：
> "Those two problems are kind of too big of scope for one quarter. So I think you either focus on in-session memory... **That is one question, one very hard question**, and the other one is how to generalize
across sessions. So **I think you kind of need to pick one** for this quarter."

**决定**：**Focus on Q1 - Context Drift Detection**

理由：
- Q1 本身就值得一篇论文（"deserve a paper alone"）
- 范围足够深，一个季度刚好
- Q2（跨会话记忆）可以分离出来，作为未来工作

---

## 📋 新的 Q1 方向：Context Drift Detection & Resolution

### Two-Stage Approach

**Stage 1: Detection (优先)**
- 正式定义什么是 Context Drift
- 设计检测指标和维度
- 在多个 benchmarks 上验证

**Stage 2: Resolution (第二阶段)**
- 检测到 drift 后如何解决
- 干预策略（例如：回滚、警告、重新规划）

---

## 🔍 重新定义：什么是 Context Drift？

### Yucheng 提出的 Context Drift 维度

根据 meeting，Context Drift 包括以下几种情况：

#### 1. **Operating on Wrong Scope** (最重要)
- 修改了不相关的文件
- 超出了任务范围
- **你已经实现**: Scope Guard

#### 2. **Utilizing Irrelevant Tools**
- 使用了与当前任务无关的工具
- 调用了不必要的 API

#### 3. **Repetitive Mistakes** (重点！)
- 在一个 session 内重复同样的错误操作
- 陷入循环（making the same mistake over and over again）
- **Yucheng 强调**: This is especially evident in Web Arena and Tau Bench

#### 4. **Not Following the Plan** (你已经实现)
- Agent 给出了计划，但没有遵循
- **你已经实现**: Plan Guard

可能的其他维度（需要 literature survey 确定）：
- Lack of evidence/justification
- Test coverage issues
- ...

---

## 📊 关键要求：泛化到多个 Benchmarks

### Yucheng 的重要观点

> "I think the dimensions here could be more generalized... instead of being specific to coding agent."

**要求**：
- ✅ 不能只针对 SWE-bench
- ✅ 要泛化到其他 long-horizon agent tasks
- ✅ 提出通用的 Context Drift 检测框架

### 推荐的 Benchmarks

#### 1. **SWE-bench** (你已经在做)
- Coding agent benchmark
- 500 verified tasks
- 你已经有初步结果（gold patch drift = 0）

#### 2. **Tau Bench** (新增！)⭐
- URL: https://taubench.com/
- **Focus**: API calls and function calling
- **Horizon**: 30-50 steps
- **特点**: Repetitive mistakes 很明显
- **Leaderboard**: https://taubench.com/#leaderboard

Yucheng 说：
> "There are Tau bench. Tau bench is basically testing the agent's capability in calling API calls and function calling to complete the task in 30 to 50 steps."

#### 3. **Web Arena** (新增！)⭐
- Web navigation tasks
- **特点**: Repetitive mistakes 很明显
- Long-horizon tasks

**Yucheng 的评价**：
> "It's [repetitive mistakes] especially evident in Web Arena and Tau Bench."

---

## 🎨 方法论：Context Drift Evaluation Framework

### Paper 结构建议

根据 Yucheng 的指导，paper 应该包括以下部分：

#### Section: **Context Drift Evaluation Framework**

**结构**：

1. **Formal Definition of Context Drift**
   - 基于 literature survey
   - 明确定义什么算 drift，什么不算

2. **Dimensions & Metrics (类似 Model Cards)**
   - 每个维度需要定义：
      - **What it is**: 这个维度是什么
      - **How to evaluate**: 如何测量
      - **Why it matters**: 为什么重要
      - **Justification**: 为什么选择这个维度（不能随机选）

3. **Instantiation to Different Benchmarks**
   - SWE-bench: 如何将维度映射到 coding tasks
   - Tau Bench: 如何映射到 API calling tasks
   - Web Arena: 如何映射到 web navigation tasks

4. **Detection Algorithm**
   - 通用的检测算法
   - 可以作为 plug-and-play module
   - 可以与 agent 并行运行（"sleep time compute"）

5. **Evaluation**
   - 在 trajectories 上运行检测
   - Manual inspection 验证
   - 与人类判断对比

---

## 📚 推荐阅读的 Papers

### 1. Model Cards Paper (方法论参考)
- Yucheng 分享的 PDF
- **用途**: 学习如何定义和证明维度

### 2. Agent Trajectory Paper ⭐
- **Title**: Agent Trajectory Dataset
- **URL**: https://arxiv.org/pdf/2505.02820
- **用途**:
   - 获取已有的 agent trajectories
   - 不需要自己重新运行 agent（省钱！）
   - 可以直接在这些 trajectories 上运行你的检测算法

### 3. Auto-Metrics Paper
- **URL**: https://arxiv.org/pdf/2504.07971
- **Focus**: Automatically evaluate agent trajectories
- **Relevance**: 他们收集了很多 trajectories，可以复用

---

## 💡 重要洞察：Use Existing Trajectories!

### 问题：运行 agent 很贵

你提到：
- 每个任务 70 分钟（local Docker）
- LLM 成本：$2-3 per task
- 500 tasks = $1000-1500

### Yucheng 的解决方案：使用已发布的 Trajectories ⭐⭐⭐

**SWE-bench 的 Trajectories**：

```bash
# SWE-bench 的实验结果都发布在 S3 上
# 例如：
logs: s3://swe-bench-experiments/verified/20250928_trae_doubao_seed_code/logs
trajs: s3://swe-bench-experiments/verified/20250928_trae_doubao_seed_code/trajs
```

**如何使用**：
1. 访问 SWE-bench GitHub: https://github.com/SWE-bench/experiments
2. 查看 `evaluation/verified/` 目录
3. 每个提交都有 `metadata.yaml` 文件
4. 下载已发布的 trajectories（logs + trajs）
5. **在这些 trajectories 上运行你的 drift detection**

**优点**：
- ✅ 不需要自己运行 agent（省钱）
- ✅ 可以评估所有 baseline models
- ✅ 快速验证你的检测算法
- ✅ 可以与不同模型对比（GPT-4, Claude, etc.）

Yucheng 说：
> "You don't have to run it... You already got everyone's trajectory, and you can just run your drift detection scripts on top of that."

---

## 🎯 具体行动步骤（Yucheng 建议的顺序）

### Step 1: Literature Survey & Definition ⭐ (最优先)

**任务**：
1. Survey 相关文献，找出之前关于 "context drift", "goal drift", "task drift" 的工作
2. 正式定义 Context Drift
3. 识别所有可能的 drift 维度

**产出**：
- 清晰的 Context Drift 定义
- 维度列表（带 justification）

**Yucheng 强调**：
> "Each part, I think, is very important. So **this is foundation of your paper**. So I want to make sure you get this solid before you run any experiment."

---

### Step 2: Design Context Drift Detection Cards

**任务**：
1. 为每个维度创建 "Detection Card"（类似 Model Card）
2. 每个 card 包含：
   - Dimension name
   - Definition
   - Why it matters
   - How to measure
   - Scope of this dimension

**产出**：
- Context Drift Detection Framework 文档
- 每个维度的详细说明

**Yucheng 建议**：
- 先设计通用的 cards（不针对特定 benchmark）
- 然后再 instantiate 到具体 benchmarks

---

### Step 3: Instantiate to SWE-bench, Tau Bench, Web Arena

**任务**：
1. 为每个 benchmark 定义如何应用这些维度
2. 设计具体的 metrics

**示例**：

| Dimension | SWE-bench | Tau Bench | Web Arena |
|-----------|-----------|-----------|-----------|
| **Wrong Scope** | 修改无关文件 | 调用无关 API | 访问无关网页 |
| **Repetitive Mistakes** | 重复同样的 patch | 重复调用失败的 API | 重复点击同一个无效按钮 |
| **Not Following Plan** | 偏离代码修改计划 | 偏离 API 调用序列 | 偏离导航计划 |

**产出**：
- 每个 benchmark 的具体 metrics 定义

---

### Step 4: Implement Detection Algorithm

**任务**：
1. 实现通用的 drift detection 算法
2. 设计为 plug-and-play module
3. 可以并行运行（与 agent 同时）

**产出**：
- `drift_detector.py` - 通用检测器
- 支持多种 benchmarks

---

### Step 5: Evaluate on Existing Trajectories

**任务**：
1. 下载 SWE-bench 的已发布 trajectories
2. 在这些 trajectories 上运行检测算法
3. Manual inspection - 对比你的检测结果与人工判断

**关键**：
- 不要自己重新运行 agent（太贵）
- 使用已有的 trajectories

**Yucheng 建议**：
> "Start with a small subset... You don't need to run all of them."

**产出**：
- Detection 结果
- Manual evaluation 报告
- 与人类判断的 agreement 分析

---

### Step 6: Iterate with Yucheng

**重要**：
> "For each of these steps, you can message me on Slack, and we can iterate more before you get to another point."

**建议的沟通节奏**：
- Step 1 完成 → 发给 Yucheng review
- Step 2 完成 → 发给 Yucheng review
- Step 3 完成 → 发给 Yucheng review
- ...

**不要等到全部完成才发**！

---

## 🚫 暂时不做的事情（重要！）

### Don't Run Full SWE-bench Yet

Yucheng 明确说：
> "I think right now you don't need to run SWE-bench on your own... Make sure you get the context drift detection method work before let's dive into coding the suite bench to heal/climb on the suite bench."

**原因**：
- 太贵（时间 + 金钱）
- 先验证方法论
- 使用已有 trajectories 更高效

---

### Don't Work on Q2 (Cross-Session Memory) Yet

**Q2 相关的事情暂停**：
- ❌ Pattern extraction
- ❌ Pattern retrieval
- ❌ Pattern reuse
- ❌ ML ranker
- ❌ SWE-bench Lite

**Yucheng 明确说**：
> "I think you kind of need to pick one for this quarter."

**Q2 可以作为 Future Work**。

---

## 🎨 更新后的 Q1 Scope

### 原来的 Q1 (你已经做的)

```
Four Guards:
   1. Scope Guard - 是否改对了文件
   2. Plan Guard - 是否遵循计划
   3. Test Guard - 是否通过测试
   4. Evidence Guard - 是否有证据支撑
```

**状态**: 已实现，在 SWE-bench 上初步验证

---

### 新的 Q1 (Yucheng 建议)

```
Context Drift Detection & Resolution Framework:

Phase 1: Detection (优先)
   1. Literature survey
   2. Formal definition of Context Drift
   3. Design detection dimensions (不限于 4 个 guards)
      - Wrong Scope ✅ (你已经有)
      - Not Following Plan ✅ (你已经有)
      - Repetitive Mistakes ⭐ (新增，重点)
      - Irrelevant Tool Use (可能新增)
      - ... (其他维度，待 survey 确定)
   4. Generalize to 3 benchmarks:
      - SWE-bench ✅
      - Tau Bench ⭐ (新增)
      - Web Arena ⭐ (新增)
   5. Evaluate on existing trajectories
   6. Manual validation

Phase 2: Resolution (后续)
   7. Design intervention strategies
   8. Test on full benchmark
   9. Measure improvement in success rate
```

---

## 📊 Success Metrics

### Detection Phase

**Primary Metrics**:
- Agreement with human judgment (最重要)
- Precision & Recall of drift detection
- Generalizability across benchmarks

### Resolution Phase (后续)

**Primary Metric**:
- Resolve Rate improvement
- 你提到的: `resolve_rate_with_intervention > resolve_rate_baseline`

**Secondary Metrics**:
- Number of interventions needed
- Cost reduction (fewer wasted actions)
- Time to completion

---

## 🛠️ Technical Details

### Definition of Session

你问 Yucheng:
> "How do we define a session? Like, do we consider trajectory as a session?"

**Yucheng 的回答**:
> "One task is one session."

**含义**:
- SWE-bench: 1 个 GitHub issue = 1 session
- Tau Bench: 1 个 task = 1 session
- Web Arena: 1 个 navigation task = 1 session

---

### Model Choice

你问关于使用哪个 LLM。

**Yucheng 的建议**:
- GPT-4.1 或 GPT-5 mini (推荐)
- OSS 120B models
- 如果有 AWS budget: Claude (你有 AWS partnership)

**重要**: 模型选择不是最关键的
> "It doesn't really matter which model you're using, any good models."

---

### Cost Optimization

**问题**: 运行 500 个 tasks 太贵

**解决方案** (Yucheng 建议):
1. **使用已发布的 trajectories** (最重要!)
2. Start with small subset (不需要跑全部)
3. Focus on detection algorithm 验证，不急着跑完整实验

---

## 📝 下一步具体行动 (优先级排序)

### P0 (本周必须做) ⚡⚡⚡

#### 1. Literature Survey (最高优先级)
```bash
# 搜索关键词
- "context drift" agent
- "goal drift"
- "task drift"
- "off-policy" agent behavior
- agent trajectory evaluation
- long-horizon agent tasks
```

**目标**:
- 找到 5-10 篇相关论文
- 理解已有的 drift 定义
- 识别研究 gap

**产出**:
- `literature_survey.md` - 文献综述
- 发给 Yucheng review

---

#### 2. 正式定义 Context Drift

**任务**:
- 基于 literature survey 给出正式定义
- 列出所有可能的 drift 维度（不只是你的 4 guards）
- 每个维度给出 justification

**产出**:
- `context_drift_definition.md`
- 发给 Yucheng review

---

#### 3. 熟悉 Tau Bench 和 Web Arena

**Tau Bench**:
- 访问 https://taubench.com/
- 查看 leaderboard 和数据集
- 理解任务类型
- 查看是否有公开的 trajectories

**Web Arena**:
- 搜索 Web Arena 数据集
- 理解任务类型
- 查看是否有公开的 trajectories

**产出**:
- `benchmark_comparison.md` - 对比三个 benchmarks

---

### P1 (下周)

#### 4. 设计 Context Drift Detection Cards

**任务**:
- 为每个维度创建 detection card
- 参考 Model Cards paper 的格式

**示例 Card 结构**:
```markdown
## Dimension: Repetitive Mistakes

### Definition
Agent repeats the same failed action multiple times within one session.

### Why It Matters
- Wastes computational resources
- Indicates lack of learning/adaptation
- Often leads to task failure

### How to Measure
- Track action history
- Detect repeated action patterns
- Measure similarity between actions (using embeddings)
- Count repetitions before success/failure

### Scope
Applies to any sequential decision-making task where:
- Actions can be compared for similarity
- Agent has opportunity to learn from feedback
- Session has multiple steps

### Instantiation Examples
- SWE-bench: Repeated attempts to modify same file with similar patches
- Tau Bench: Repeated calls to same API with same parameters
- Web Arena: Repeated clicks on same element
```

**产出**:
- `context_drift_cards.md` - 所有维度的 detection cards
- 发给 Yucheng review

---

#### 5. Download Existing Trajectories

**SWE-bench**:
```bash
# 从 S3 下载已发布的 trajectories
# 参考: https://github.com/SWE-bench/experiments

# 示例
aws s3 cp s3://swe-bench-experiments/verified/20250928_trae_doubao_seed_code/trajs/ ./trajs/ --recursive
```

**Tau Bench**:
- 查看是否有公开的 trajectories

**产出**:
- `data/trajectories/swebench/` - SWE-bench trajectories
- `data/trajectories/taubench/` - Tau Bench trajectories (如果有)

---

### P2 (两周后)

#### 6. 实现通用检测算法

**任务**:
- 重构你现有的 Four Guards 代码
- 添加 Repetitive Mistakes detection
- 设计为 plug-and-play module

**产出**:
- `drift_detector/` - 通用检测框架
   - `detector.py` - 主检测器
   - `dimensions/` - 各个维度的检测逻辑
   - `benchmarks/` - 不同 benchmark 的 adapters

---

#### 7. 在 Trajectories 上评估

**任务**:
1. 在 SWE-bench trajectories 上运行检测
2. 随机采样 20-50 个 trajectories
3. Manual inspection - 你自己判断是否有 drift
4. 对比你的检测结果与人工判断

**产出**:
- Detection 结果
- Agreement analysis
- Error analysis (哪些 cases 检测错了)

---

### P3 (一个月后)

#### 8. Resolution Phase

**任务**:
- 设计干预策略
- 在真实 agent 上测试
- 测量 resolve rate 提升

---

## 🎯 Paper Outline (基于 Yucheng 的建议)

```markdown
Title: A Framework for Detecting and Resolving Context Drift in Long-Horizon Agent Tasks

Abstract
- Problem: Agents drift from original goals in long tasks
- Solution: Unified detection framework + resolution strategies
- Results: Validated on 3 benchmarks

1. Introduction
   - Motivation: Why context drift matters
   - Problem: Current agents lack drift awareness
   - Contribution:
      * Formal definition of context drift
      * Generalizable detection framework
      * Resolution strategies
      * Evaluation on 3 benchmarks

2. Related Work
   - Agent trajectory evaluation
   - Goal-oriented agents
   - Error detection in autonomous systems

3. Context Drift: Definition & Dimensions
   - 3.1 Formal Definition
   - 3.2 Drift Dimensions (Detection Cards)
      * Wrong Scope
      * Repetitive Mistakes
      * Not Following Plan
      * Irrelevant Tool Use
      * ...
   - 3.3 Why These Dimensions Matter

4. Context Drift Detection Framework
   - 4.1 Framework Overview
   - 4.2 Detection Algorithm
   - 4.3 Generalization to Different Task Types
   - 4.4 Implementation as Plug-and-Play Module

5. Instantiation to Benchmarks
   - 5.1 SWE-bench (Coding Tasks)
   - 5.2 Tau Bench (API Calling)
   - 5.3 Web Arena (Web Navigation)

6. Evaluation
   - 6.1 Detection Accuracy
      * Agreement with human judgment
      * Precision & Recall
   - 6.2 Cross-Benchmark Generalization
   - 6.3 Ablation Studies

7. Resolution Strategies (Phase 2)
   - 7.1 Intervention Methods
   - 7.2 Impact on Success Rate
   - 7.3 Cost-Benefit Analysis

8. Discussion & Limitations

9. Conclusion & Future Work
```

---

## 💬 与 Yucheng 的沟通要点

### 沟通频率
- **不要等全部完成才发**
- 每完成一个 step，就发给 Yucheng review
- 使用 Slack

### 沟通内容建议
```
例子：

Subject: [Q1] Step 1 Complete - Context Drift Definition

Hi Yucheng,

I've completed the literature survey and drafted a formal
definition of Context Drift. Key findings:

1. Definition: [你的定义]
2. Identified 5 drift dimensions: [列表]
3. Gap in current research: [你发现的 gap]

Attached: literature_survey.md, context_drift_definition.md

Could you review and let me know if I should proceed to
designing the detection cards?

Best,
Jeremy
```

---

## 📊 Timeline 建议 (基于 Yucheng 的范围)

```
Week 1 (当前周):
   - Literature survey
   - 正式定义 Context Drift
   - 熟悉 Tau Bench & Web Arena
   → Deliverable: Definition document
   → Review with Yucheng

Week 2:
   - 设计 Detection Cards
   - Download existing trajectories
   → Deliverable: Detection Cards document
   → Review with Yucheng

Week 3-4:
   - 实现检测算法
   - 在 trajectories 上测试
   - Manual validation
   → Deliverable: Detection results
   → Review with Yucheng

Week 5-6:
   - 改进检测算法（基于 review）
   - 完整评估
   - 撰写 paper draft

Week 7-8:
   - Resolution strategies (如果时间允许)
   - Paper revision
   - 准备 presentation
```

---

## 🚨 关键 Takeaways

1. **Scope 变化**:
   - ❌ 不做 Q2 (Cross-session memory)
   - ✅ 深入做 Q1 (Context Drift Detection)
   - ✅ 这本身就是一篇论文

2. **方法论变化**:
   - ❌ 不只关注 SWE-bench
   - ✅ 泛化到 3 个 benchmarks
   - ✅ 提出通用框架

3. **成本优化**:
   - ❌ 不自己跑完整实验（太贵）
   - ✅ 使用已发布的 trajectories
   - ✅ 先验证方法论

4. **新维度**:
   - ⭐ **Repetitive Mistakes** - Yucheng 强调，你之前没重点关注
   - 可能还有其他维度（literature survey 确定）

5. **Paper 基础**:
   - ⭐ **Definition 是 foundation** - 必须先做solid
   - 先定义，再实现，再评估
   - 每个 step 都要与 Yucheng iterate

6. **沟通**:
   - 不要等全部完成
   - 每个 step 完成就 review
   - 使用 Slack 保持联系

---

## 🎯 立即行动 (今天就可以开始)

### Action 1: 更新 TODO List
```bash
# 删除所有 Q2 相关的 todos
# 添加新的 Q1 todos
```

### Action 2: 开始 Literature Survey
```bash
# 搜索论文
Google Scholar: "context drift" agent
arXiv: agent trajectory evaluation
找到 5-10 篇相关论文，开始阅读
```

### Action 3: 探索 Tau Bench
```bash
# 访问 https://taubench.com/
# 了解任务类型
# 查看 leaderboard
# 寻找公开的 trajectories
```

### Action 4: 给 Yucheng 发确认邮件
```
Subject: Next Steps - Focusing on Q1 Context Drift

Hi Yucheng,

Thanks for the meeting today! Very helpful direction.

To confirm my understanding:
1. Focus on Q1 (Context Drift Detection), not Q2
2. Start with literature survey & formal definition
3. Generalize to SWE-bench, Tau Bench, Web Arena
4. Use existing trajectories (not run full experiments yet)
5. Iterate with you at each step

I'll start with literature survey this week and send you
the definition document for review.

Best,
Jeremy
```

---

**这就是 Yucheng meeting 的完整总结！接下来应该专注于 Q1 的深度而不是 Q1+Q2 的广度。**