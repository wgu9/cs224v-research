# Progress Summary for Yucheng

**Date**: 2025-10-29
**Status**: Research Phase Complete - Ready for Integration

---

## ✅ 已完成的工作（Literature Survey）

### 1. 全面的文献调研

**覆盖范围**：
- **30+ 篇论文**（2024-2025 年最新研究）
- 顶级会议：ICLR, NeurIPS, AAAI, ACL
- 包括 arxiv 最新 preprints

**关键论文（Tier 1 - 最相关）**：
1. MAST: Multi-Agent System Failure Taxonomy (arXiv 2025)
2. AgentErrorBench (ICLR 2026 under review)
3. ReCAPA: Hierarchical Predictive Correction (ICLR 2026 under review)
4. MI9: Runtime Governance Protocol (arXiv Aug 2024)
5. τ-bench (TauBench) (arXiv Jun 2024) ⭐ Yucheng 推荐

**完整列表**：详见 `/claude/2025-10-29-deepresearch-paper-claude.md`

---

### 2. Context Drift 定义与维度

#### 核心发现：术语极度碎片化

> **"Context Drift"** 这个词在学术文献中几乎不存在！

**现有术语**（10+ 个不同名称）：
- Task Derailment (MAST 2025) - 7.15% 失败案例
- Goal Drift (Arike et al. 2025)
- Behavioral Drift (Microsoft 2025)
- Agentic Drift (IBM 2024)
- Instruction Drift
- Reasoning Drift
- Conversation Drift
- ...

**这就是我们的机会**：提出统一的 Context Drift 框架！

---

#### 提出的统一定义

**Context Drift** = 可测量的偏差，Agent 的行为轨迹与指定目标在长时程任务中的偏离

**三大核心维度**（已从文献中验证）：

##### 维度 1: Scope Drift（范围漂移）⭐ Priority

**文献支持**：
- MAST: Task Derailment - 7.15% 失败率
- Goal Drift paper: 量化评分，100k+ tokens 测试
- MI9: 99.81% 检测率，FSM 状态机验证
- SWE-bench: Pass-to-Pass 测试检测范围违规
- TheAgentCompany: 检查点评估

**检测方法**：
- Goal Adherence Score: 1 - (Runtime/Baseline)
- Boundary violation count
- JSensity divergence > 0.2
- FSM conformance

**为什么重要**：
- 出现在 12/30 篇论文中
- 跨多个领域（coding, dialogue, web）
- 安全关键（unauthorized access, privilege escalation）

---

##### 维度 2: Tool Drift（工具漂移）

**文献支持**：
- TRAJECT-Bench: Similar tool confusion, redundant calling
- τ-bench: Wrong tool/wrong argument - pass^8 < 25%
- ToolACE: 89.17% irrelevant tool detection
- BFCL: AST accuracy 91.41%

**检测方法**：
- Trajectory Exact-Match (Trajectory EM)
- pass^k consistency (k≥4, score<0.5 表示漂移)
- Relevance detection (P(relevant|context) < 0.3)
- Tool selection stability

**为什么重要**：
- Scaling bottleneck: 5-7 tools 是关键失败点
- 出现在 8/30 篇论文中
- 浪费资源，降低效率

---

##### 维度 3: Loop Drift（循环漂移）⭐⭐ Yucheng 强调

**文献支持** - **最强**：
- AgentErrorBench: **Error propagation 是首要瓶颈**
- ReCAPA: **首个量化指标** EPR, PAC
  - EPR₁₀ = 0.082 (最佳) vs 0.3+ (基线)
  - PAC = 传播衰减系数
- Retroformer: Infinite loops 文档化
- MI9: Recursive planning loops
- τ-bench: **Yucheng 说 "especially evident"**
- WebArena: **Yucheng 说 "especially evident"**

**检测方法**：
- **EPR (Error Propagation Rate)**:
  ```
  EPRₖ = Pr(eₜ₀₊ₖ = 1 | eₜ₀ = 1) - Pr(eₜ₀₊ₖ = 1 | eₜ₀ = 0)
  ```
- **PAC (Propagation Attenuation Coefficient)**:
  ```
  PAC = -slope(Δ, ln Pr(eₜ₀₊Δ = 1 | eₜ₀ = 1))
  ```
- Loop detection: 重复动作序列
- Root-cause attribution

**为什么重要**：
- **最重要的维度**（AgentErrorBench 明确指出）
- 出现在 10/30 篇论文中
- 导致任务失败，无法恢复
- 浪费计算资源

---

### 3. 提出的统一框架

#### Context Drift Index (CDI)

```
CDI = w₁·ScopeScore + w₂·ToolScore + w₃·LoopScore

其中：
- ScopeScore: 基于 Goal Adherence + Boundary violations
- ToolScore: 基于 Trajectory EM + pass^k
- LoopScore: 基于 EPR + PAC
- w₁, w₂, w₃: 任务相关权重（建议 0.4, 0.3, 0.3）
```

---

### 4. 跨 Benchmark 泛化（符合 Yucheng 要求）

#### SWE-bench（我们已有经验）✅

**Drift 表现**：
| 维度 | 表现形式 | 检测方法 |
|------|---------|---------|
| Scope | 编辑无关文件 | Pass-to-Pass 测试 |
| Tool | 冗余命令 | 工具调用序列分析 |
| Loop | 重复失败的 patch | EPR 计算 |

**Trajectory 可用性**：
- S3: `s3://swe-bench-experiments/verified/`
- Multiple models: Claude, GPT-4, Deepseek
- Format: JSON logs + trajs

---

#### τ-Bench（Yucheng 推荐）⭐

**核心特点**：
- API calling & function composition
- Horizon: 30-50 steps
- Leaderboard: https://taubench.com/#leaderboard
- **Repetitive mistakes especially evident**（Yucheng 原话）

**Drift 表现**：
| 维度 | 表现形式 | 检测方法 |
|------|---------|---------|
| Scope | 调用无关 API | Database state comparison |
| Tool | 错误 API/错误参数 | AST validation |
| Loop | 重复失败的 API 调用 | **pass^k < 25% (k=8)** |

**关键指标**：
- pass^k consistency
- Single trial: <50% 成功
- 8 trials: ~25% 成功
- **这说明一致性问题严重！**

**需要进一步研究**：
- [ ] Trajectory format
- [ ] 公开的 trajectory 数据
- [ ] 具体任务示例

---

#### WebArena（Yucheng 推荐）⭐

**核心特点**：
- Web navigation tasks
- Realistic web environment
- Long-horizon tasks
- **Repetitive mistakes especially evident**（Yucheng 原话）

**Drift 表现**：
| 维度 | 表现形式 | 检测方法 |
|------|---------|---------|
| Scope | 访问无关页面 | Navigation path analysis |
| Tool | 错误的交互类型 | Action sequence validation |
| Loop | **重复点击失效元素** | Pattern recognition |

**文献证据**：
- Invariant Labs 分析："agents easily get stuck in loops, endlessly repeating the same actions"
- GPT-4: 14.41% 成功率
- Loop detection 改进后：+16% 性能提升

**需要进一步研究**：
- [ ] Trajectory format
- [ ] 公开的 trajectory 数据
- [ ] 具体任务示例

---

### 5. 识别的研究 Gaps（我们的创新机会）

#### Gap 1: 术语碎片化 ⭐⭐⭐
**问题**：10+ 不同术语，无统一定义
**我们的贡献**：统一的 Context Drift 定义和框架

#### Gap 2: 实时检测缺失 ⭐⭐⭐
**问题**：14/15 论文只做 post-hoc 分析，只有 MI9 有 runtime
**我们的贡献**：Plug-and-play 并行检测器

#### Gap 3: 跨维度综合评估缺失 ⭐⭐
**问题**：大多数论文单独测试一个维度
**我们的贡献**：CDI 综合评分，跨所有 3 个维度

#### Gap 4: Benchmark 领域不平衡 ⭐
**问题**：重点在 code (SWE-bench) 和 web (WebArena)
**我们的贡献**：包含 API calling (τ-bench)

#### Gap 5: 标准化报告缺失 ⭐⭐
**问题**：无 "Model Cards for Agents" 方法
**我们的贡献**：Detection Cards（借鉴 SPHERE 方法论）

#### Gap 6: 恢复机制未测量 ⭐
**问题**：只测量失败，不测量恢复
**我们的贡献**：Recovery metrics（基于 PAC）

#### Gap 7: 多智能体漂移 ⭐
**问题**：Agent A 的漂移如何影响 Agent B？
**潜在贡献**：级联漂移分析

#### Gap 8: 上下文窗口限制 ⭐
**问题**：只有 Goal Drift paper 测试 >100k tokens
**潜在贡献**：长上下文漂移评估

---

### 6. 量化指标体系（完整）

| 指标类别 | 具体指标 | 计算公式 | 阈值建议 | 来源论文 |
|---------|---------|---------|---------|---------|
| **错误传播率** | EPR | EPRₖ = Pr(eₜ₀₊ₖ = 1 \| eₜ₀ = 1) - Pr(eₜ₀₊ₖ = 1 \| eₜ₀ = 0) | > 0.15 表示严重 | ReCAPA |
| **传播衰减系数** | PAC | PAC = -slope(Δ, ln Pr(eₜ₀₊Δ = 1 \| eₜ₀ = 1)) | < 0.05 表示风险未消散 | ReCAPA |
| **一致性评分** | pass^k | k次试验成功率 | < 0.5 (k≥4) 表示不稳定 | τ-bench |
| **轨迹匹配度** | Trajectory EM | 工具选择序列精确匹配率 | < 0.5 表示工具漂移 | TRAJECT-Bench |
| **目标依赖度** | Goal Adherence | 1 - (运行时投入/基线投入) | < θ_GA 表示目标漂移 | Goal Drift paper |
| **JS 散度** | Jensen-Shannon | P(actions\|goal, t) vs P(actions\|goal, t₀) | > 0.2 表示行为漂移 | MI9 |
| **任务脱轨率** | Task Derailment | 偏离任务目标的比例 | 7.15% 基线 | MAST |
| **相关性检测** | Relevance | P(tool_i is relevant \| context_t) | < 0.3 表示无关 | ToolACE |

---

## 📊 对比表（关键论文）

| Paper | Venue | Scope Drift | Tool Drift | Loop Drift | 相关性 (1-5) |
|-------|-------|------------|-----------|-----------|-------------|
| **MAST** | arXiv 2025 | ✓ Task derailment (7.15%) | ✓ Reasoning-action mismatch | ✓ Step repetition | 5 |
| **AgentErrorBench** | ICLR 2026 | ✓ Constraint ignorance | ✓ Format/parameter errors | **✓ Error propagation (首要)** | 5 |
| **ReCAPA** | ICLR 2026 | ○ Trajectory deviation | ○ Action errors | **✓ EPR/PAC 量化** | 5 |
| **MI9** | arXiv 2024 | ✓ Privilege escalation | ✓ Tool-chain failures | ✓ Recursive planning loops | 5 |
| **τ-bench** | arXiv 2024 | ○ Policy adherence | ✓ Wrong tools/arguments | **✓ pass^8 < 25%** | 5 |
| **ToolACE** | ICLR 2025 | ○ Relevance | **✓ 89.17% detection** | ○ Self-consistency | 5 |
| **Goal Drift** | AAAI 2025 | **✓ 100k+ tokens** | — | ✓ Pattern-matching | 5 |
| **TRAJECT-Bench** | arXiv 2024 | ○ Intent inference | **✓ Similar tool confusion** | ✓ Multi-step failures | 5 |

（完整表格包含 30+ 篇论文，详见深度报告）

---

## 🎯 下一步计划

### 立即任务（今天-明天）

1. **整合到正式文档**：
   - [x] 创建 RESEARCH_INTEGRATION_PLAN.md
   - [ ] 更新 literature_survey.md（添加 30+ 篇论文）
   - [ ] 更新 context_drift_definition.md（添加定义和维度）
   - [ ] 创建 Detection Cards（借鉴 SPHERE）

2. **补充 Benchmark 细节**：
   - [ ] 深入研究 τ-Bench（访问网站，找 trajectories）
   - [ ] 深入研究 WebArena（搜索数据集，找 trajectories）
   - [ ] 更新 benchmark_comparison.md

3. **发给 Yucheng Review**（明天下午）：
   - [ ] 完整的 literature_survey.md
   - [ ] 完整的 context_drift_definition.md
   - [ ] Benchmark comparison 初稿

### Week 2 任务

4. **创建 Detection Cards**（基于 SPHERE 方法论）
5. **设计检测算法**（pseudocode）
6. **下载 trajectories**（SWE-bench, τ-bench, WebArena）

---

## 💡 关键洞察（给 Yucheng）

### 1. 术语碎片化是巨大机会
文献中没有统一的 "Context Drift" 定义，这是我们建立标准的机会。

### 2. Repetitive Mistakes 维度最成熟
ReCAPA 提供了首个量化指标（EPR, PAC），这是实现的良好基础。

### 3. 跨 Benchmark 泛化可行
3 个维度在 SWE-bench, τ-Bench, WebArena 中都有明确表现。

### 4. 实时检测是关键创新点
14/15 论文只做 post-hoc，我们可以填补这个 gap。

### 5. τ-Bench 和 WebArena 非常适合测试 Loop Drift
两个 benchmark 都显示出严重的 repetitive mistakes 问题。

---

## 📚 参考资料位置

1. **Claude 深度研究报告**:
   `/claude/2025-10-29-deepresearch-paper-claude.md`
   - 30+ 篇论文详细分析
   - 完整对比表
   - 量化指标体系

2. **Context Drift Package**:
   `/claude/context_drift_package/README.md`
   - 两阶段框架（Detection + Resolution）
   - 跨 benchmark 实例化
   - 干预策略

3. **SPHERE Paper** (Yucheng 推荐):
   https://arxiv.org/pdf/2504.07971
   - 5 个评估维度
   - Card 方法论
   - 我们会借鉴来创建 Detection Cards

---

## ❓ 问题给 Yucheng

1. **Model Cards Paper**:
   是 SPHERE (arXiv 2504.07971) 吗？还是另一篇？

2. **Detection Cards 格式**:
   你希望看到什么样的格式？类似 SPHERE 的 5 维度？

3. **τ-Bench 和 WebArena**:
   你知道哪里可以找到公开的 trajectories 吗？

4. **优先级**:
   应该先完善定义，还是先实现检测算法？

---

**准备发送给 Yucheng！**希望这个总结清楚地展示了研究进展和下一步计划。
