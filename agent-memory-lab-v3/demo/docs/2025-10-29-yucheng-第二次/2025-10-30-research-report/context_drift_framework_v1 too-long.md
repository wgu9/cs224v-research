# Context Drift Detection Framework

**Date**: 2025-10-29
**Status**: Draft for Yucheng Review
**Purpose**: 建立Context Drift的理论基础和检测方法

---

## Part 1: 概念框架 (Conceptual Framework)

### 1.1 Context Drift定义

**Definition**:
Context Drift是指agent在执行长horizon任务时，其行为轨迹逐步偏离原始目标或任务约束的现象，表现为三个核心维度（Scope漂移、Tool漂移、Loop陷阱），最终导致任务失败或资源浪费。

**Formal Definition**:
```
给定：
- 任务目标 G
- 初始状态 s₀
- 动作序列 A = {a₁, a₂, ..., aₜ}
- 期望轨迹 τ*

Context Drift发生当且仅当：
∃t, d(τₜ, τ*) > θ

其中：
- τₜ = 实际轨迹到时刻t
- d(·,·) = 偏离度量函数
- θ = 漂移阈值
```

**关键特征**:
- **渐进性 (Progressive)**: 不是突然失败，而是逐步偏离
- **可测量 (Measurable)**: 通过轨迹分析可量化
- **可干预 (Intervable)**: 检测到后可以纠正

---

### 1.2 为什么Context Drift是个问题？

**1. 任务失败的主要原因**
- AgentErrorBench: Error propagation是PRIMARY bottleneck
- MAST: Task derailment占7.15%的失败案例
- τ-bench: pass^8 < 25% 表明严重不一致性

**2. 资源浪费**
- 重复尝试相同的失败action（Loop Drift）
- 修改无关文件（Scope Drift）
- 调用错误API（Tool Drift）

**3. 安全风险**
- MI9: Privilege escalation（越权访问）
- 修改critical files outside scope
- 执行unauthorized operations

**理论框架 - 因果链**:
```
Initial Error/Deviation
    ↓
Context Drift (Scope/Tool/Loop)
    ↓
Compounding Failures (EPR > 0.15)
    ↓
Resource Exhaustion / Security Violation
    ↓
Task Failure
```

---

### 1.3 Context Drift vs. 相关概念

| 概念 | 定义 | 关系 | 我们的扩展 |
|------|------|------|-----------|
| **Goal Drift** | 最终目标偏离 | **子集关系** - Goal Drift是Scope Drift的特例 | 我们关注execution过程，不只是final goal |
| **Error Propagation** | 错误级联传播 | **因果关系** - Error Propagation导致Loop Drift | 我们关注deviation pattern，不只是single error |
| **Hallucination** | 生成虚假内容 | **正交关系** - Hallucination可导致Tool Drift | 我们关注behavioral drift，不只是factual error |
| **Off-Policy** | RL中策略偏离 | **类比关系** - 但Off-Policy是训练策略，我们是执行偏离 | 我们是unintentional deviation，Off-Policy是intentional |
| **Task Derailment** | 任务脱轨（MAST术语） | **同义关系** - Task Derailment ≈ Scope Drift | 我们统一了10+个碎片化术语 |

**关键区别**:
1. **粒度**: 我们关注step-by-step的deviation，不只是final outcome
2. **可操作性**: 我们提供实时检测方法，不只是post-hoc分析
3. **多维度**: 我们综合Scope/Tool/Loop三个维度，不是单一视角

---

### 1.4 会话内 vs 跨会话的边界

**本工作聚焦：会话内Context Drift (Intra-Session)**

**定义**:
- **会话内**: 单次任务执行过程中的漂移（e.g., 一个GitHub issue的修复过程）
- **跨会话**: 多次对话/任务之间的模式变化（Q2 - 不在本季度scope）

**边界条件**:
```
会话内：
- 时间跨度: 单次任务完成时间（10-100 steps）
- 状态持续: Agent context/memory在同一对话中连续
- 目标固定: 任务目标G在整个会话中不变

跨会话：
- 时间跨度: 多天/多周
- 状态断裂: 新对话，context重置
- 目标变化: 不同任务有不同目标
```

**为什么先做会话内？**（Yucheng建议）
1. **复杂度可控**: 单次任务有明确起点和终点
2. **数据可得**: SWE-bench/τ-bench都是单会话任务
3. **影响更大**: AgentErrorBench指出intra-session error propagation是PRIMARY bottleneck

---

### 1.5 三维度的理论关系

**问题**: Scope/Tool/Loop是并列关系还是有hierarchy？

**答案**: **并列且正交** (Parallel and Orthogonal)

**理论基础**:
```
三维度对应agent执行的三个方面：

Scope Drift (WHERE)  - 空间维度
    ↓
    问题: Agent在哪里操作？
    偏离: 操作了unauthorized resources

Tool Drift (HOW)     - 工具维度
    ↓
    问题: Agent用什么工具？
    偏离: 选择了irrelevant/wrong tools

Loop Drift (WHEN)    - 时间维度
    ↓
    问题: Agent何时重复？
    偏离: 陷入repetitive patterns without progress
```

**正交性证明** - 可以独立发生:
1. **高Scope + 低Loop**: Agent快速探索错误区域（偏离但不重复）
2. **低Scope + 高Tool**: Agent在正确区域但用错工具
3. **低Scope + 低Tool + 高Loop**: Agent在正确地方用正确工具，但陷入循环

**不是Hierarchy**:
- Loop不是Scope或Tool的"下游"
- 三者可以同时发生（Example 1 in definition doc: CDI=0.66）

**能否cover所有drift类型？**

**理论论证**:
- **Scope**: 覆盖所有"WHERE"相关的偏离（files, APIs, pages, resources）
- **Tool**: 覆盖所有"HOW"相关的偏离（commands, actions, methods）
- **Loop**: 覆盖所有"WHEN"相关的偏离（repetition, cycles, stuck patterns）

**实证验证**（从30篇论文）:
- 所有识别的drift现象都可归类到这3个维度
- 文献中的其他术语（hallucination, communication failure）要么是特殊场景，要么可归入3维度

**反例讨论**:
- **Hallucination**: 可归入Tool Drift（选择non-existent tool）或Scope Drift（访问non-existent resource）
- **Communication Failure**: Multi-agent特有，不在单agent scope内
- **Planning Error**: 表现为Scope/Tool/Loop中的一种或多种

---

## Part 2: 检测卡片 (Detection Cards)

### 2.1 Detection Card: Scope Drift

#### What（现象定义）

**定义**:
Agent访问或修改了超出任务边界的资源（files, APIs, pages），或追求了与任务目标不相关的子目标。

**具体表现**:
1. **SWE-bench**: 修改了PR scope外的文件
2. **τ-bench**: 调用了unauthorized customer records
3. **WebArena**: 访问了无关网页section

**例子** (SWE-bench):
```
Task: Fix null pointer in payment/processor.py
Authorized scope: payment/*.py, tests/test_payment.py

Drift detected:
- Edit database/schema.py  ← SCOPE DRIFT (超出payment module)
- Edit auth/permissions.py ← SCOPE DRIFT (完全无关)
```

#### Why（为什么重要）

**1. 安全风险**
- MI9: 99.81%检测到privilege escalation
- 可能修改critical infrastructure code

**2. 破坏现有功能**
- SWE-bench: Pass-to-pass test failures
- 引入regression bugs

**3. 效率损失**
- 浪费时间在irrelevant areas
- MAST: 7.15%的任务因task derailment失败

**因果链**:
```
Scope Drift → Modify irrelevant code → Break existing tests → Task failure
                                    ↓
                                Security violation
```

#### How（检测算法）

**Method 1: Boundary Violation Count**
```python
def detect_scope_drift_bv(trajectory, authorized_resources):
    """
    检测访问了多少unauthorized resources

    Args:
        trajectory: List[Action] - agent的动作序列
        authorized_resources: Set[str] - 允许访问的资源集合

    Returns:
        bv_score: float - boundary violation score [0, 1]
    """
    accessed = set()
    for action in trajectory:
        if action.type in ['edit', 'read', 'call']:
            accessed.add(action.target_resource)

    violations = accessed - authorized_resources
    bv_score = len(violations) / len(accessed) if accessed else 0.0

    return bv_score, violations

# Threshold: bv_score > 0.3 → HIGH Scope Drift
```

**Method 2: Pass-to-Pass Testing** (SWE-bench specific)
```python
def detect_scope_drift_p2p(initial_tests, final_tests):
    """
    检测是否破坏了原本passing的tests

    Returns:
        broken_tests: List[str] - 被破坏的test names
    """
    initial_pass = set(initial_tests['passing'])
    final_pass = set(final_tests['passing'])

    broken_tests = initial_pass - final_pass

    # Threshold: len(broken_tests) > 0 → SCOPE DRIFT detected
    return broken_tests
```

**Method 3: Goal Adherence Score** (from Goal Drift paper)
```python
def detect_scope_drift_ga(actions, goal, baseline_investment):
    """
    测量actions与goal的对齐度

    Args:
        actions: List[Action]
        goal: str - 任务目标描述
        baseline_investment: float - 预期的resource investment

    Returns:
        ga_score: float - goal adherence [0, 1]
    """
    runtime_investment = compute_investment(actions)  # tokens, API calls, etc.
    ga_score = 1 - (runtime_investment / baseline_investment)

    # Threshold: ga_score < 0.5 → Goal Drift
    return ga_score
```

#### Evaluation Metrics

| Metric | Formula | Threshold | Literature |
|--------|---------|-----------|------------|
| **BV Score** | violations / total_accesses | > 0.3 | Derived from MAST (7.15%) |
| **Pass-to-Pass** | len(broken_tests) | > 0 (binary) | SWE-bench |
| **Goal Adherence** | 1 - (runtime/baseline) | < 0.5 | Goal Drift (AAAI 2025) |
| **JS Divergence** | JS(P(actions\|goal,t₀) \|\| P(actions\|goal,t)) | > 0.2 | MI9 (99.81% detection) |

#### Evidence（文献支持）

**直接支持 (12 papers)**:
1. **MAST** (arXiv 2025): Task derailment 7.15%, κ=0.77 agreement
2. **Goal Drift** (AAAI 2025): 100k+ token evaluation, quantitative GA scoring
3. **MI9** (arXiv 2024): 99.81% detection, FSM conformance, JS divergence
4. **SWE-bench** (ICLR 2024): Pass-to-pass tests as scope violation detector
5. **TheAgentCompany** (arXiv 2024): 175 tasks, checkpoint-based boundary tracking
6. **AgentBoard** (NeurIPS 2024): Fine-grained progress, boundary adherence
7. **Agent Trajectory Explorer** (AAAI 2025): Trajectory visualization for scope
8. **WebArena** (ICLR 2024): Long-horizon task boundaries
9. **Microsoft AI Red Team** (2025): Agent flow manipulation taxonomy
10. **OdysseyBench** (arXiv 2024): Multi-day context dependencies
11. **SWE-bench Pro** (arXiv 2024): Multi-file coordination scope
12. **AgentErrorBench** (ICLR 2026): Constraint ignorance

---

### 2.2 Detection Card: Tool Drift

#### What（现象定义）

**定义**:
Agent选择了不适合当前子目标的工具、使用了错误参数、或在不需要时调用工具。

**具体表现**:
1. **Similar Tool Confusion** (TRAJECT-Bench): 混淆功能相似的工具
2. **Wrong Tool/Argument** (τ-bench): API参数错误或选错API
3. **Redundant Calling**: 不必要的重复调用
4. **Relevance Failure** (ToolACE): 使用与context无关的工具

**例子** (τ-bench):
```
Task: Update customer address
Available tools: get_customer(), update_address(), update_phone()

Drift detected:
- Call update_customer(full_data) ← TOOL DRIFT (应该用update_address)
- Call update_address(id=123, street="5th") ← Missing required param: zip
- Call update_phone(id=123) ← TOOL DRIFT (completely irrelevant)
```

#### Why（为什么重要）

**1. 效率损失**
- TRAJECT-Bench: 5-7 tools是scaling bottleneck
- 错误tool导致无效output，需重试

**2. 级联错误**
- Wrong tool → Wrong output → 下游step使用错误信息
- τ-bench: pass^8 < 25% 表明严重consistency问题

**3. 用户体验差**
- 冗余API calls浪费用户时间和quota
- ToolACE: 89.17%能检测到irrelevant tools

**因果链**:
```
Tool Drift → Wrong output → Downstream errors → Task failure
                         ↓
                    Resource waste (API calls, compute)
```

#### How（检测算法）

**Method 1: Trajectory Exact-Match** (from TRAJECT-Bench)
```python
def detect_tool_drift_em(actual_tools, optimal_tools):
    """
    比较实际工具序列与最优序列的匹配度

    Args:
        actual_tools: List[str] - agent实际使用的工具序列
        optimal_tools: List[str] - 专家标注的最优序列

    Returns:
        em_score: float - exact match score [0, 1]
    """
    matches = sum(1 for a, o in zip(actual_tools, optimal_tools) if a == o)
    em_score = matches / max(len(actual_tools), len(optimal_tools))

    # Threshold: em_score < 0.5 → Tool Drift
    return em_score
```

**Method 2: Tool Relevance Detection** (from ToolACE)
```python
def detect_tool_drift_relevance(tool_calls, context):
    """
    检测tool是否与当前context相关

    Args:
        tool_calls: List[ToolCall]
        context: str - 当前对话/任务context

    Returns:
        irrelevant_ratio: float - 不相关工具的比例
    """
    irrelevant_count = 0
    for tool_call in tool_calls:
        relevance_score = compute_relevance(tool_call, context)  # LLM-based or rule-based
        if relevance_score < 0.3:  # ToolACE threshold
            irrelevant_count += 1

    irrelevant_ratio = irrelevant_count / len(tool_calls)

    # Threshold: irrelevant_ratio > 0.3 → Tool Drift
    return irrelevant_ratio
```

**Method 3: pass^k Consistency** (from τ-bench)
```python
def detect_tool_drift_consistency(task, agent, k=8):
    """
    运行k次，测量tool selection的consistency

    Args:
        task: Task object
        agent: Agent object
        k: int - number of trials

    Returns:
        consistency_score: float - [0, 1]
    """
    tool_sequences = []
    for _ in range(k):
        trajectory = agent.execute(task)
        tools = [action.tool for action in trajectory]
        tool_sequences.append(tools)

    # Compute pairwise similarity
    similarities = []
    for i in range(k):
        for j in range(i+1, k):
            sim = sequence_similarity(tool_sequences[i], tool_sequences[j])
            similarities.append(sim)

    consistency_score = np.mean(similarities)

    # Threshold: consistency < 0.5 (for k≥4) → Tool Drift
    # τ-bench: pass^8 < 0.25 is severe
    return consistency_score
```

#### Evaluation Metrics

| Metric | Formula | Threshold | Literature |
|--------|---------|-----------|------------|
| **Trajectory EM** | matches / max(len_actual, len_optimal) | < 0.5 | TRAJECT-Bench (44-45% best) |
| **Relevance** | P(tool relevant \| context) | < 0.3 | ToolACE (89.17% detection) |
| **pass^k** | Success rate over k trials | < 0.5 (k≥4) | τ-bench (pass^8 < 25%) |
| **AST Accuracy** | Syntactic/semantic correctness | Binary | BFCL (91.41%) |

#### Evidence（文献支持）

**直接支持 (14 papers)**:
1. **TRAJECT-Bench** (arXiv 2024): Similar tool confusion, 5-7 tool bottleneck, Trajectory EM
2. **τ-bench** (arXiv 2024): Wrong tool/argument, pass^8 < 25%, database state comparison
3. **ToolACE** (ICLR 2025): 89.17% irrelevant detection, 91.41% BFCL, 26,507 APIs
4. **BFCL** (2024): AST validation, 2000 Q-A pairs, multi-language
5. **TPTU-v2** (EMNLP 2024): API Retriever, industrial-scale tool selection
6. **AgentBoard** (NeurIPS 2024): Grounding accuracy, parameter extraction
7. **MAST** (arXiv 2025): Reasoning-action mismatch
8. **AgentErrorBench** (ICLR 2026): Format/parameter errors
9. **MI9** (arXiv 2024): Tool-chain cascading failures
10. **Agent Trajectory Explorer** (AAAI 2025): Action sequence analysis
11. **TheAgentCompany** (arXiv 2024): Tool use across platforms
12. **WebArena** (ICLR 2024): Tool use (map, calculator)
13. **Microsoft AI Red Team** (2025): Tool-chain failures
14. **SWE-bench Pro** (arXiv 2024): Tool use errors

---

### 2.3 Detection Card: Loop Drift ⭐⭐ (HIGHEST PRIORITY)

#### What（现象定义）

**定义**:
Agent重复执行相似或相同的action sequence，但没有取得progress，陷入无效循环。

**关键特征** - 区别于正常retry:
- **Repetition**: 重复相似actions（similarity > 80%）
- **No Progress**: 每次结果相同或相似（无改进）
- **No Learning**: 不调整策略，完全重复

**具体表现**:
1. **Identical Action Loops**: 完全相同的API call重复调用
2. **Error Propagation**: 早期错误导致后续连锁错误
3. **Stuck Patterns**: Navigation loops（repeatedly clicking broken element）

**例子** (WebArena):
```
Task: Add laptop to shopping cart

Loop detected:
Step 3: Click "Add to Cart" → fails (out of stock)
Step 4: Click "Add to Cart" → fails (same error)  ← LOOP START
Step 5: Click "Add to Cart" → fails (same error)
Step 6: Click "Add to Cart" → fails (same error)
Step 7: Click "Add to Cart" → fails (same error)  ← 5x repetition!

No strategy change, no alternative product, stuck in loop.
```

#### Why（为什么重要） - MOST CRITICAL

**1. PRIMARY BOTTLENECK**
- **AgentErrorBench**: "Error propagation is the primary bottleneck to LLM agent reliability"
- 不是偶发现象，是系统性瓶颈

**2. 量化证据最强**
- ReCAPA: EPR₁₀ = 0.082 (best) vs 0.3-0.45 (baselines) - **50-80% improvement potential**
- τ-bench: pass^8 < 25% - 严重consistency failure
- Retroformer: +36% improvement on ALFWorld by preventing loops

**3. 资源浪费严重**
- 重复API calls消耗quota
- 循环可能无限持续（需timeout机制）
- 计算资源浪费（重复相同reasoning）

**4. Yucheng强调**
- "Especially evident in τ-Bench and WebArena"
- Repetitive mistakes是关键observation

**因果链** - 为什么repetition算drift?:
```
Initial Error (e₀)
    ↓
Agent无法recover（缺乏error handling）
    ↓
Repeat same action (drift from "make progress" goal)
    ↓
Error propagates (EPR > 0.15)
    ↓
Cascading failures
    ↓
Task timeout/failure
```

**理论justification**:
- **隐含目标**: 每个agent都有"make progress"的meta-goal
- **偏离**: Repetition without progress = 偏离了make progress goal
- **不同于正常retry**: 正常retry会调整参数或策略，loop是完全重复

#### How（检测算法）

**Method 1: Error Propagation Rate (EPR)** from ReCAPA
```python
def compute_epr(trajectory, k=10):
    """
    计算错误传播率 - 早期错误导致后续错误的概率

    Args:
        trajectory: List[Step] - agent执行轨迹，每个step有success/fail标记
        k: int - 向前看k步

    Returns:
        epr_k: float - Error Propagation Rate at distance k
    """
    epr_values = []

    for t0 in range(len(trajectory) - k):
        # 如果t0时刻有错误
        if trajectory[t0].is_error:
            # 看t0+k时刻的错误概率
            errors_at_k = sum(1 for i in range(k)
                             if trajectory[t0+i].is_error)
            p_error_given_error = errors_at_k / k
        else:
            # 如果t0没错误，看t0+k的baseline error rate
            p_error_given_no_error = baseline_error_rate

        epr = p_error_given_error - p_error_given_no_error
        epr_values.append(epr)

    epr_k = np.mean(epr_values)

    # Threshold: EPR₁₀ > 0.15 → Severe Loop Drift
    # ReCAPA: 0.082 (good), 0.3-0.45 (bad)
    return epr_k
```

**Method 2: Action Sequence Loop Detection**
```python
def detect_loop_pattern(trajectory, window=3, similarity_threshold=0.8):
    """
    检测重复的action sequence

    Args:
        trajectory: List[Action]
        window: int - subsequence length to compare
        similarity_threshold: float - 多相似算作repetition

    Returns:
        loop_detected: bool
        loop_count: int - 重复次数
    """
    action_embeddings = [embed_action(a) for a in trajectory]

    loops = []
    for i in range(len(trajectory) - window):
        subsequence_i = action_embeddings[i:i+window]

        for j in range(i+window, len(trajectory) - window):
            subsequence_j = action_embeddings[j:j+window]

            similarity = cosine_similarity(subsequence_i, subsequence_j)
            if similarity > similarity_threshold:
                loops.append((i, j, similarity))

    loop_count = len(loops)

    # Threshold: loop_count >= 3 → Loop Drift
    # (允许2次retry，3次以上算stuck)
    return loop_count >= 3, loop_count
```

**Method 3: Propagation Attenuation Coefficient (PAC)** from ReCAPA
```python
def compute_pac(trajectory):
    """
    计算错误风险的衰减速度

    PAC = -slope of error probability decay

    Low PAC (<0.05) = errors don't dissipate = stuck in loop
    High PAC (>0.1) = errors decay quickly = good recovery
    """
    error_probs = []

    for delta in range(1, 20):  # Look ahead 1-20 steps
        probs = []
        for t0 in range(len(trajectory) - delta):
            if trajectory[t0].is_error:
                p = 1 if trajectory[t0+delta].is_error else 0
                probs.append(p)

        if probs:
            error_probs.append((delta, np.mean(probs)))

    # Fit exponential decay: P(error|t0+Δ) = exp(-PAC * Δ)
    deltas, probs = zip(*error_probs)
    log_probs = [np.log(p + 1e-10) for p in probs]

    pac = -np.polyfit(deltas, log_probs, 1)[0]  # -slope

    # Threshold: PAC < 0.05 → Loop Drift (errors not dissipating)
    return pac
```

**Method 4: pass^k Consistency** from τ-bench
```python
def compute_pass_k_consistency(task, agent, k=8):
    """
    运行k次，测量是否陷入不同的loops

    Low pass^k = agent不稳定，容易陷入loops
    """
    successes = 0

    for trial in range(k):
        result = agent.execute(task)
        if result.success:
            successes += 1

    pass_k = successes / k

    # Threshold: pass^k < 0.5 (for k≥4) → Loop Drift tendency
    # τ-bench: pass^8 < 0.25 is severe
    return pass_k
```

#### Evaluation Metrics

| Metric | Formula | Threshold | Best Result | Literature |
|--------|---------|-----------|-------------|------------|
| **EPR₁₀** | Pr(error\|prior error) - Pr(error\|no error) | > 0.15 severe | 0.082 | ReCAPA (ICLR 2026) |
| **PAC** | -slope of error decay | < 0.05 not dissipating | Varies | ReCAPA |
| **Loop Count** | # repeated subsequences | ≥ 3 repetitions | 0 | Derived from Retroformer |
| **pass^k** | Success rate over k trials | < 0.5 (k≥4) | varies | τ-bench (pass^8 < 25%) |
| **Recovery Rate** | Successful recovery after error | < 0.3 poor | Varies | AgentErrorBench |

#### Evidence（文献支持） - STRONGEST

**直接支持 (15 papers)**:
1. **AgentErrorBench** (ICLR 2026): **"Error propagation is PRIMARY bottleneck"**, root-cause attribution, 24.3% vs 0.3%
2. **ReCAPA** (ICLR 2026): **First quantitative metrics EPR/PAC**, EPR₁₀=0.082 vs 0.3-0.45, hierarchical correction
3. **τ-bench** (arXiv 2024): pass^8 < 25%, consistency failures, **Yucheng emphasized**
4. **WebArena** (ICLR 2024): Navigation loops, **Yucheng emphasized "especially evident"**
5. **Retroformer** (ICLR 2024): Infinite loops documented, +36% improvement on ALFWorld
6. **MI9** (arXiv 2024): Recursive planning loops, FSM-based detection
7. **MAST** (arXiv 2025): Step repetition, info withholding
8. **Goal Drift** (AAAI 2025): Pattern-matching behavior over 100k+ tokens
9. **TRAJECT-Bench** (arXiv 2024): Multi-step trajectory failures
10. **AgentBoard** (NeurIPS 2024): Multi-round interaction tracking
11. **Agent Trajectory Explorer** (AAAI 2025): Human oversight for loops
12. **WebResearcher** (arXiv 2025): Irreversible noise contamination
13. **Microsoft AI Red Team** (2025): Knowledge degradation loops
14. **OdysseyBench** (arXiv 2024): Information persistence issues
15. **ToolACE** (ICLR 2025): Self-consistency checking

---

## Part 3: 初步验证 (Preliminary Validation)

### 3.1 验证计划

**目标**: 在少量SWE-bench trajectories上手工验证检测方法

**Steps**:
1. 下载2-3个SWE-bench trajectories（1个success, 1个failure, 1个partial）
2. 手工标注每个step是否有drift（哪个维度）
3. 运行上述检测算法
4. 计算准确率：Detection Accuracy = TP+TN / Total
5. Case study：展示1个clear drift example

**数据来源**:
- SWE-bench Verified trajectories: `s3://swe-bench-experiments/verified/`
- 我们已有408个predictions

### 3.2 Case Study Example

**[TO BE FILLED after downloading trajectories]**

示例格式：
```
Task ID: django__django-12345
Task: Fix null pointer exception in QuerySet.filter()

Manual Annotation:
Step 1: Read error trace ✓ (no drift)
Step 2: Edit django/db/models/query.py ✓ (correct scope)
Step 3: Edit django/db/backends/mysql.py ✗ SCOPE DRIFT (wrong module)
Step 4: Edit django/db/models/query.py (same as step 2) ✗ LOOP DRIFT (repetition)
Step 5: Edit django/core/management.py ✗ SCOPE DRIFT (completely irrelevant)

Detection Results:
- Scope Drift BV: 0.4 (2/5 violations) ✓ Detected (> 0.3)
- Loop Drift: 1 repetition ○ Below threshold (need ≥3)
- Tool Drift: N/A (all edits, no tool variety)

CDI = 0.5 × 0.4 + 0.2 × 0.2 + 0.3 × 0.2 = 0.3 (MEDIUM drift)

Ground Truth: Task failed due to scope violations
Detection: CORRECT ✓
```

---

## Summary for Yucheng

### ✅ 本文档建立了：

1. **Context Drift的正式定义** - 不是现象罗列，而是有理论基础的概念
2. **与相关概念的区别** - Goal Drift, Error Propagation, Hallucination等
3. **会话内vs跨会话边界** - 明确scope在单次任务
4. **三维度的理论关系** - 并列且正交，不是hierarchy
5. **完整的Detection Cards** - 每个维度有What/Why/How/Evidence
6. **可操作的检测算法** - 伪代码级别，可直接实现
7. **量化阈值** - 基于文献的threshold建议

### 📊 文献支持统计

| Dimension | Direct Support | Key Papers | Strongest Metric |
|-----------|---------------|------------|------------------|
| Scope Drift | 12 papers | MAST (7.15%), Goal Drift (100k+), MI9 (99.81%) | BV > 0.3 |
| Tool Drift | 14 papers | TRAJECT-Bench (5-7), ToolACE (89.17%), τ-bench (pass^8<25%) | Trajectory EM < 0.5 |
| **Loop Drift** | **15 papers** | **AgentErrorBench (PRIMARY), ReCAPA (EPR/PAC)** | **EPR₁₀ > 0.15** |

### 🎯 下一步

1. **Yucheng Review** ← 等待反馈
2. **下载trajectories** - SWE-bench 2-3个案例
3. **手工标注** - 验证detection accuracy
4. **Case study** - 填充Part 3的example
5. **调整算法** - 基于初步验证结果

---

**问题给Yucheng**:

1. **Definition是否清晰？** 特别是与Goal Drift/Error Propagation的区别
2. **三维度正交性论证是否充分？** 还是需要改成hierarchy？
3. **检测算法的level of detail是否合适？** 要更抽象还是更具体？
4. **Loop Drift的justification（为什么repetition算drift）是否convincing？**

---

**Status**: Draft for Review - 等待Yucheng feedback后继续
