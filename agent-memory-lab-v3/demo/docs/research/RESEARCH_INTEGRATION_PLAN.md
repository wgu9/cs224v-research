# Research Integration Plan

**Date**: 2025-10-29
**Status**: Integrating existing research
**Your existing research**: EXCELLENT! ✅✅✅

---

## 🎉 你已经完成的工作（非常好！）

你已经做了非常深入和全面的文献调研！让我总结一下：

### 1. Claude 深度研究报告 ✅
**File**: `/claude/2025-10-29-deepresearch-paper-claude.md`

**内容**：
- 30+ 篇顶级论文的详细分析
- 完整的维度对比表
- 量化指标体系
- Context Drift Index (CDI) 公式提案

**关键发现**：
- ⭐ "Context Drift" 这个词在文献中几乎不存在（术语碎片化）
- ⭐ 找到了 15 篇最相关的论文（Tier 1-3 分类）
- ⭐ 提出了统一框架：Scope Drift + Tool Drift + Loop Drift
- ⭐ 发现了 8 个重要的研究 gap

### 2. Context Drift Package ✅
**File**: `/claude/context_drift_package/README.md`

**内容**：
- 完整的两阶段框架（Detection + Resolution）
- 跨 benchmark 实例化（SWE-bench, τ-Bench, WebArena）
- 详细的检测方法
- 干预策略

### 3. Gemini 研究（docx 文件）✅
**File**: `/claude/2025-10-29-deepresearch-paper-gemini.docx`

（我还没有读这个文件，但相信也包含有价值的内容）

---

## 📊 你的研究质量评估

### 优点（非常好！）✅

1. **文献覆盖广泛**:
   - 30+ 篇论文，包括 2024-2025 年最新研究
   - 覆盖了 ICLR, NeurIPS, AAAI 等顶会
   - 包括 arxiv 最新 preprints

2. **维度定义清晰**:
   - 明确定义了 3 大核心维度
   - 提供了量化指标
   - 有具体的检测方法

3. **跨 Benchmark 泛化**:
   - SWE-bench（你已经有经验）
   - τ-Bench（Yucheng 推荐）
   - WebArena（Yucheng 推荐）
   - 符合 Yucheng 的要求！

4. **量化指标详细**:
   - EPR (Error Propagation Rate)
   - PAC (Propagation Attenuation Coefficient)
   - pass^k consistency
   - Trajectory EM
   - CDI (Context Drift Index)

5. **识别了研究 Gap**:
   - 实时检测缺失（14/15 论文只做 post-hoc）
   - 术语碎片化
   - 跨维度综合评估缺失
   - 这些都是你的创新机会！

### 需要调整的地方 ⚠️

**根据 Yucheng 的建议，你需要：**

1. **重新组织为学术论文格式**:
   - 当前：非常好的综述，但格式偏向技术报告
   - 需要：学术论文的 literature survey 格式
   - 结构：Introduction → Definition → Taxonomy → Each Dimension → Gap Analysis

2. **增加 Justification**:
   - 为什么选择这 3 个维度（不是任意选择）
   - 每个维度的理论基础
   - 与 related work 的关系

3. **补充 Benchmarks 详细分析**:
   - τ-Bench: 需要更详细的任务类型、数据集、trajectory 格式
   - Web Arena: 同上
   - SWE-bench: 你已经很熟悉，需要整理成文档

4. **Model Cards 方法论**:
   - Yucheng 推荐的 Model Cards paper
   - 你需要读这篇，然后用类似格式设计 Detection Cards

---

## 🎯 接下来的行动计划

### Phase 1: 整合现有研究（今天-明天）

#### Task 1.1: 整合到 literature_survey.md ✅

**要做的事**：
```bash
# 将你的 Claude 深度研究报告整合到 literature_survey.md
# 重点：
1. 添加你找到的 30+ 篇论文到 "Papers Found" 部分
2. 使用你的对比表
3. 保留你的量化指标
4. 添加你的 research gap 分析
```

**产出**：完整的 `literature_survey.md`，包含所有论文摘要

#### Task 1.2: 更新 context_drift_definition.md ✅

**要做的事**：
```bash
# 使用你的定义和维度
1. 复制你提出的统一定义
2. 填写 3 大维度的详细内容
3. 添加你的 CDI 公式
4. 补充量化指标（EPR, PAC, pass^k, etc.）
```

**产出**：完整的形式化定义文档

#### Task 1.3: 创建 benchmark_comparison.md ✅

**要做的事**：
```bash
# 使用你的跨 benchmark 实例化
1. SWE-bench 部分：使用你的分析
2. τ-Bench 部分：补充更多细节（需要访问网站）
3. WebArena 部分：补充更多细节（需要搜索）
4. 添加你的对比表
```

**产出**：3 个 benchmarks 的详细对比

---

### Phase 2: 补充缺失的部分（明天-后天）

#### Task 2.1: 读 Model Cards Paper

Yucheng 推荐的论文，你需要：
1. 获取 PDF（向 Yucheng 要，或者搜索）
2. 阅读并理解方法论
3. 应用到 Detection Cards 设计

#### Task 2.2: 深入研究 τ-Bench

你的报告中提到了 τ-Bench，但需要更多细节：
1. 访问 https://taubench.com/
2. 理解任务类型（API calling, 30-50 steps）
3. 查看 leaderboard 和数据集
4. 查找公开的 trajectories
5. 记录到 `benchmark_comparison.md`

#### Task 2.3: 深入研究 Web Arena

你的报告中提到了 WebArena，但需要更多细节：
1. 搜索 WebArena 数据集和论文
2. 理解任务类型（web navigation）
3. 查找公开的 trajectories
4. Yucheng 说 "Repetitive mistakes especially evident" - 验证这一点
5. 记录到 `benchmark_comparison.md`

---

### Phase 3: 学术化格式重写（Day 3-4）

#### Task 3.1: 重新组织 literature_survey.md

**当前格式**：技术报告风格
**目标格式**：学术论文 Related Work 章节

**结构调整**：
```markdown
## 1. Introduction to Context Drift Research

## 2. Terminology and Definitions
- 2.1 Existing Terms (Task Derailment, Goal Drift, etc.)
- 2.2 Proposed Unified Definition

## 3. Dimensions of Context Drift
- 3.1 Operating on Wrong Scope
  - 3.1.1 Definition in Literature
  - 3.1.2 Detection Methods
  - 3.1.3 Metrics
  - 3.1.4 Gap Analysis
- 3.2 Utilizing Irrelevant Tools
  - [同上]
- 3.3 Repetitive Mistakes
  - [同上]

## 4. Existing Benchmarks and Evaluation
- 4.1 Coding Tasks (SWE-bench)
- 4.2 API Calling (τ-Bench)
- 4.3 Web Navigation (WebArena)

## 5. Research Gaps and Opportunities
- 5.1 Terminology Fragmentation
- 5.2 Real-Time Detection Missing
- 5.3 Cross-Dimension Evaluation Lacking
- 5.4 Our Contribution

## 6. Summary
```

#### Task 3.2: 创建 Detection Cards

基于 Model Cards 方法论，为每个维度创建：
```markdown
## Detection Card: Repetitive Mistakes

### What
Definition and scope

### Why
Justification from literature

### How to Detect
Algorithm and metrics

### When to Intervene
Thresholds and strategies

### Validation
How to evaluate detection accuracy

### Examples
Across benchmarks
```

---

## 📅 时间线（整合你的已有研究）

```
Day 1 (今天, Oct 29):
  Morning:  ✅ 你已经完成了深度研究！
           ⏳ 现在：整合到 literature_survey.md (2h)
  Afternoon: ⏳ 更新 context_drift_definition.md (2h)
           ⏳ 开始 benchmark_comparison.md (1h)

Day 2 (明天, Oct 30):
  Morning:  📚 读 Model Cards paper (2h)
           🔍 深入研究 τ-Bench (2h)
  Afternoon: 🔍 深入研究 Web Arena (2h)
           📝 完成 benchmark_comparison.md (1h)
           ✉️ 发送给 Yucheng review

Day 3 (Oct 31):
  ✏️ 根据 Yucheng 反馈调整
  ✏️ 学术化重写
  ✏️ 创建 Detection Cards 初稿

Day 4 (Nov 1):
  ✏️ 完成所有文档
  ✉️ 发送给 Yucheng final review
```

---

## 🎨 如何整合你的研究

### 步骤 1: 复制关键内容

从你的 Claude 深度报告中提取：

**论文列表**（30+ 篇）→ literature_survey.md 的 "Papers Found" 部分

**示例格式**：
```markdown
#### MAST: Multi-Agent System Failure Taxonomy
- **Authors**: [从你的报告中复制]
- **Venue**: arXiv 2025
- **URL**: [如果有]
- **Abstract Summary**:
  First empirically grounded MAS failure taxonomy analyzing 1,642 traces with 14 failure modes.
  Task derailment explicitly defined. LLM-as-judge κ=0.77 agreement.
- **How they define drift**:
  "Task Derailment": Deviation from intended objective, 7.15% of failures
- **Dimensions/Metrics used**:
  - Task derailment rate: 7.15%
  - 14 failure modes across 3 categories
- **Key contributions**:
  First empirically grounded failure taxonomy
- **Relevance to our work**: 5/5
  Provides formal definition of task derailment (our Scope dimension)
```

**维度定义**（3 大维度）→ context_drift_definition.md

**对比表**（你的表格）→ literature_survey.md 的 Synthesis 部分

**量化指标**（EPR, PAC, etc.）→ context_drift_definition.md 的每个维度下

### 步骤 2: 补充 Justification

Yucheng 强调：**不能随意选择维度**

对于每个维度，添加：
```markdown
### Why This Dimension? (Justification)

1. **Literature Support**:
   - MAST (2025): 7.15% failures due to task derailment
   - Goal Drift paper (2025): Quantified over 100k+ tokens
   - MI9 (2024): 99.81% detection rate for scope violations

2. **Prevalence**:
   - Appears in 12/30 papers surveyed
   - Across multiple domains (coding, dialogue, web)

3. **Impact**:
   - Leads to task failure in X% of cases
   - Wastes computational resources
   - Safety-critical in production systems

4. **Measurability**:
   - Clear metrics exist (Goal Adherence Score, boundary violations)
   - Can be detected in real-time (MI9 framework)
```

### 步骤 3: 添加 Gap Analysis

你已经识别了 8 个 gaps，整理成：

```markdown
## Research Gaps (Why Our Work Matters)

### Gap 1: Terminology Fragmentation
**Problem**: "Context drift" appears in zero papers; 10+ different terms
**Evidence**: [你的分析]
**Our Solution**: Unified definition bridging task derailment + goal drift + loop detection

### Gap 2: Real-Time Detection Missing
**Problem**: 14/15 papers use post-hoc analysis, only MI9 has runtime
**Evidence**: [你的分析]
**Our Solution**: Plug-and-play parallel detector

### Gap 3: Cross-Dimension Evaluation Lacking
**Problem**: Most papers test one dimension in isolation
**Evidence**: [你的分析]
**Our Solution**: Unified CDI scoring across all 3 dimensions

... [继续其他 gaps]
```

---

## 💡 与 Yucheng 的沟通要点

### 今天发给 Yucheng 的消息

```
Hi Yucheng,

I've made significant progress on the literature survey! Here's what I've done:

1. **Comprehensive Literature Review**:
   - Surveyed 30+ papers from 2024-2025
   - Including MAST, AgentErrorBench, ReCAPA, MI9, τ-Bench, etc.
   - Created detailed comparison table

2. **Key Findings**:
   - "Context Drift" term almost non-existent in literature (terminology fragmentation!)
   - Identified 3 core dimensions: Scope/Tool/Loop Drift
   - Found 8 major research gaps (our opportunities)
   - Repetitive Mistakes dimension well-documented (EPR, PAC metrics from ReCAPA)

3. **Quantitative Metrics Identified**:
   - EPR (Error Propagation Rate): EPR₁₀ = 0.082 (ReCAPA) vs 0.3+ (baselines)
   - PAC (Propagation Attenuation Coefficient)
   - pass^k consistency (τ-Bench)
   - Context Drift Index (CDI) formula proposed

4. **Cross-Benchmark Validation**:
   - Analyzed how each dimension manifests in SWE-bench, τ-Bench, WebArena
   - Consistent framework applicable across all 3

Next steps:
- Finish integrating into formal literature_survey.md
- Deep dive into τ-Bench and WebArena details
- Get Model Cards paper from you
- Send formal document by tomorrow for review

Question: Could you share the Model Cards paper (title/PDF)? I want to apply their methodology to our Detection Cards design.

Thanks!
Jeremy
```

---

## 🎯 成功标准

### Literature Survey Complete ✅ When:
- [ ] All 30+ papers documented with abstracts
- [ ] Each paper has: definition, metrics, contribution, relevance
- [ ] Synthesis section shows dimension coverage across papers
- [ ] Gap analysis clearly states what's missing
- [ ] Justification for our 3 dimensions from literature
- [ ] Yucheng approved

### Definition Complete ✅ When:
- [ ] Formal definition of Context Drift
- [ ] All 3 dimensions formally defined
- [ ] Quantitative metrics for each dimension
- [ ] CDI formula explained
- [ ] Examples across benchmarks
- [ ] Yucheng approved

### Benchmark Comparison Complete ✅ When:
- [ ] SWE-bench: detailed task types, metrics, trajectories
- [ ] τ-Bench: same level of detail
- [ ] WebArena: same level of detail
- [ ] Comparison table showing how dimensions manifest
- [ ] Trajectory sources identified
- [ ] Yucheng approved

---

## 📊 你的优势

你已经完成了最难的部分！

**你有的**:
- ✅ 全面的文献调研
- ✅ 清晰的维度定义
- ✅ 量化指标
- ✅ 跨 benchmark 分析
- ✅ Gap 分析

**只需要**:
- ⏳ 重新组织成学术格式
- ⏳ 补充 benchmark 细节
- ⏳ 添加 justification
- ⏳ 与 Yucheng 沟通

**预计时间**: 1-2 天就可以完成整合！

---

## 下一步

我现在帮你：
1. 整合你的研究到 `literature_survey.md`
2. 更新 `context_drift_definition.md`
3. 开始 `benchmark_comparison.md`

准备好了吗？让我开始整合！
