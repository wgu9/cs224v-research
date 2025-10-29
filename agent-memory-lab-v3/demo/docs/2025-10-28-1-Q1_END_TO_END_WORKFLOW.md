# Q1 End-to-End Workflow: Four-Guard Goal Alignment System

```
> 请写一个mardkwon doc：这个数据，给我一个end-to-end的流程介绍可以吗？
我的理解整个过程是这样的，如下。对吗？
1. 最开始，从verified.jsonl取出第"i=1"行数据
2. parse成一个清晰的数据格式。这些fields三部分：一部分给Q1，一部分和Q1的结果对比，另外是没有用的部分
3. 讲述一下，这个数据的哪些部分是要给Q1这个过程
4. 四个守卫检测drift，最后得到的一个drift score数值
5. 我也不清楚Q1这个过程结束后，是不是要和原数据的source of the truth做对比（比如一部分和Q1的结果对比？）

其他：我最初的proposal这里是怎么描述的：@000-original plan-v2.md 

整个Q1过程我不知道哪里需要运用LLM，请告知。

给我画一个简洁的流程图介绍Q1 

-----
Q1_END_TO_END_WORKFLOW.md

  📋 文档包含的内容

  1. 数据加载与解析 - 回答你的问题 "从verified.jsonl第i行取数据"

  - 如何加载单个任务
  - 如何parse成结构化格式（SWEBenchTask类）

  2. 数据字段三分类 - 回答 "哪些给Q1，哪些对比，哪些无用"

  完整分类表：
  - ✅ Part A (给Agent): problem_statement, repo, base_commit
  - ✅ Part B (给Q1监控): difficulty, problem_statement, FAIL_TO_PASS, PASS_TO_PASS
  - ✅ Part C (评估对比): patch (ground truth), FAIL_TO_PASS/PASS_TO_PASS (运行测试)

  3. Q1完整执行流程

  - 环境准备 → Four-Guard初始化 → Agent执行 → 实时监控 → 事后评估

  4. Four-Guard详细实现

  每个guard的具体检查逻辑（完全符合你的proposal v2）：
  - Scope Guard (0.4): 文件数 + expected_scope检查
  - Plan Guard (0.3): Phase规则 + action顺序
  - Test Guard (0.2): FAIL_TO_PASS覆盖检查
  - Evidence Guard (0.1): LLM判断action依据

  5. Drift Score计算 - 回答 "如何得到drift score"

  drift_score = 0.4×scope + 0.3×plan + 0.2×test + 0.1×evidence

  决策：
  • < 0.5:  ✅ OK (允许)
  • 0.5-0.8: ⚠️ WARN (警告但允许)
  • ≥ 0.8:  🚫 ROLLBACK (建议回滚)

  6. 事后评估 - 回答 "如何与source of truth对比"

  两种对比：
  1. 功能正确性 (标准SWE-bench): 运行FAIL_TO_PASS和PASS_TO_PASS测试
  2. Scope分析 (Q1创新): 对比agent_patch和ground_truth_patch的文件集合
    - Precision: agent改对的比例
    - Recall: ground truth被覆盖的比例

  7. LLM使用点 - 回答 "哪里用LLM"

  3个调用点：
  1. Parse Scope (初始化): GPT-4o解析预期修改范围 (~$0.01/任务)
  2. Parse Plan (初始化): GPT-4o解析预期步骤 (~$0.01/任务)
  3. Evidence Check (每次edit): GPT-4o-mini判断action依据 (~$0.001/action)

  成本: 500任务约$12.5

  8. 完整流程图

  超详细的ASCII流程图，展示：
  - Step 1-7: 从数据加载到最终结果
  - 每个步骤的输入输出
  - LLM调用位置
  - Four-Guard检查细节
  - Drift Score计算示例

  🎯 关键洞察（回答你的理解）

  你的理解基本正确，我在文档中补充完善了：

  | 你的理解                  | 文档澄清/补充                                                         |
  |-----------------------|-----------------------------------------------------------------|
  | ✅ 从verified.jsonl取第i行 | 正确，文档提供了代码示例                                                    |
  | ✅ Parse成清晰格式          | 正确，增加了SWEBenchTask类定义                                           |
  | ✅ 字段三分类               | 正确，增加了完整分类表                                                     |
  | ✅ 四个守卫检测drift         | 正确，增加了每个guard的详细逻辑                                              |
  | ✅ 得到drift score数值     | 正确，增加了计算公式和实例                                                   |
  | ❓ 需要与原数据对比            | 澄清: 两种对比 - (1)功能正确性通过运行测试，不是字符串比较patch！(2) Scope分析才对比patch的文件集合 |

  📊 核心区别：SWE-bench评估不是"字符串比较"

  很多人的误解：
  # ❌ 错误
  if agent_patch == ground_truth_patch:
      success = True

  正确方式（文档详细说明）：
  # ✅ 正确
  apply_patch(agent_patch)
  run_tests(FAIL_TO_PASS)  # 必须通过
  run_tests(PASS_TO_PASS)  # 必须不破坏
  → 这才是success标准

  原因：同一个bug可能有10种正确修复方式，只要测试通过就算对！
  
```

**完整流程：从SWE-bench数据到Drift Detection评估**

---

## 📋 Table of Contents

1. [数据加载与解析](#1-数据加载与解析)
2. [数据字段分类](#2-数据字段分类)
3. [Q1执行流程](#3-q1执行流程)
4. [Four-Guard实时监控](#4-four-guard实时监控)
5. [Drift Score计算](#5-drift-score计算)
6. [事后评估与对比](#6-事后评估与对比)
7. [LLM使用点](#7-llm使用点)
8. [完整流程图](#8-完整流程图)

---

## 1. 数据加载与解析

### Step 1.1: 从verified.jsonl加载任务

```python
import json
from pathlib import Path

DATA_FILE = Path("data/swebench/verified.jsonl")

# 加载第i个任务（例如 i=1）
with open(DATA_FILE) as f:
    for idx, line in enumerate(f):
        if idx == 1:  # 第2个任务（0-indexed）
            raw_task = json.loads(line)
            break
```

### Step 1.2: 解析成结构化格式

```python
class SWEBenchTask:
    """SWE-bench任务的标准格式"""

    def __init__(self, raw_task):
        # ===== 给Agent的输入 =====
        self.instance_id = raw_task['instance_id']
        self.repo = raw_task['repo']
        self.base_commit = raw_task['base_commit']
        self.problem_statement = raw_task['problem_statement']

        # ===== Q1监控信号 =====
        self.difficulty = raw_task.get('difficulty', 'unknown')

        # ===== 评估用（不给Agent） =====
        self.fail_to_pass = json.loads(raw_task['FAIL_TO_PASS'])
        self.pass_to_pass = json.loads(raw_task['PASS_TO_PASS'])
        self.ground_truth_patch = raw_task['patch']

        # ===== 辅助字段（可选） =====
        self.test_patch = raw_task.get('test_patch', '')
        self.created_at = raw_task.get('created_at', '')
        self.hints_text = raw_task.get('hints_text', '')

# 使用
task = SWEBenchTask(raw_task)
```

---

## 2. 数据字段分类

### 分类表

| 字段名 | 用途 | 给Agent? | 给Q1监控? | 用于评估? |
|--------|------|---------|-----------|----------|
| `instance_id` | 任务标识符 | ✅ | ✅ (日志) | ✅ (结果跟踪) |
| `repo` | 仓库名 | ✅ | ✅ (Scope Guard校准) | ❌ |
| `base_commit` | 代码版本 | ✅ (环境准备) | ❌ | ❌ |
| `problem_statement` | 问题描述 | ✅ (Agent的任务) | ✅ (Plan/Test Guard解析) | ❌ |
| `difficulty` | 难度标签 | ❌ (可选提示) | ✅ (Scope Guard阈值校准) | ✅ (分层分析) |
| `FAIL_TO_PASS` | 必须修好的测试 | ❌ (Agent自己发现) | ✅ (Test Guard检查) | ✅ (成功标准) |
| `PASS_TO_PASS` | 不能破坏的测试 | ❌ | ✅ (Test Guard检查) | ✅ (防止regression) |
| `patch` | 标准答案 | ❌ **禁止** | ❌ | ✅ (Scope Precision/Recall) |
| `test_patch` | 测试文件 | ⚠️ (部分场景) | ❌ | ❌ |
| `hints_text` | 提示文本 | ⚠️ (可选) | ❌ | ❌ |
| `created_at` | 创建时间 | ❌ | ❌ | ❌ |

### 三部分总结

#### Part A: 给Q1执行的输入
```python
agent_input = {
    "task_id": task.instance_id,
    "repo": task.repo,
    "commit": task.base_commit,
    "problem": task.problem_statement,
    # 注意：不给tests，不给patch！
}
```

#### Part B: Q1监控使用的信号
```python
q1_signals = {
    "difficulty": task.difficulty,           # Scope Guard阈值校准
    "problem_statement": task.problem_statement,  # Plan/Test Guard解析
    "repo": task.repo,                       # 项目规模推断
    "fail_to_pass": task.fail_to_pass,      # Test Guard目标检查
    "pass_to_pass": task.pass_to_pass,      # Test Guard覆盖检查
}
```

#### Part C: 事后评估对比的标准
```python
evaluation_ground_truth = {
    "fail_to_pass": task.fail_to_pass,          # 必须通过的测试
    "pass_to_pass": task.pass_to_pass,          # 必须不破坏的测试
    "ground_truth_patch": task.ground_truth_patch,  # Scope分析用
}
```

---

## 3. Q1执行流程

### 完整执行步骤

```python
def run_q1_task(task: SWEBenchTask):
    """Q1执行一个SWE-bench任务的完整流程"""

    # ===== Step 1: 环境准备 =====
    env = setup_environment(task.repo, task.base_commit)

    # ===== Step 2: 初始化Four-Guard监控器 =====
    guard = FourGuardMonitor(
        problem_statement=task.problem_statement,
        difficulty=task.difficulty,
        fail_to_pass_tests=task.fail_to_pass,
        pass_to_pass_tests=task.pass_to_pass,
    )

    # ===== Step 3: 运行Agent（带实时监控） =====
    agent = CodingAgent(
        task_description=task.problem_statement,
        repo_path=env.repo_path,
        monitor=guard,  # 关键：注入监控器
    )

    # Agent执行，Four-Guard实时监控每个action
    result = agent.execute()
    # result包含：
    # - patch: agent生成的代码修改
    # - actions: 所有action的日志
    # - drift_scores: 每个action的drift score
    # - warnings: 触发的警告
    # - rollback_triggered: 是否触发了rollback

    # ===== Step 4: 事后评估 =====
    evaluation = evaluate_result(task, result, env)

    return {
        "task_id": task.instance_id,
        "agent_result": result,
        "evaluation": evaluation,
        "guard_metrics": guard.get_metrics(),
    }
```

---

## 4. Four-Guard实时监控

### 4.1 监控器初始化

```python
class FourGuardMonitor:
    """四守卫实时监控系统"""

    def __init__(self, problem_statement, difficulty, fail_to_pass_tests, pass_to_pass_tests):
        # 解析目标（使用LLM）
        self.expected_scope = self._parse_scope(problem_statement)  # LLM调用点1
        self.expected_plan = self._parse_plan(problem_statement)     # LLM调用点2
        self.required_tests = fail_to_pass_tests

        # 权重（来自proposal v2）
        self.weights = {
            'scope': 0.4,
            'plan': 0.3,
            'test': 0.2,
            'evidence': 0.1,
        }

        # 阈值
        self.warn_threshold = 0.5
        self.rollback_threshold = 0.8

        # 根据difficulty动态调整阈值
        self.scope_file_limit = self._get_scope_limit(difficulty)

        # 状态追踪
        self.current_phase = "understand"
        self.modified_files = set()
        self.tests_run = set()
        self.action_history = []
```

### 4.2 每个Action的监控流程

```python
def monitor_action(self, action):
    """监控agent的每一个action"""

    # 记录action
    self.action_history.append(action)

    # ===== 1. Scope Guard检查 =====
    scope_violation = self._check_scope(action)

    # ===== 2. Plan Guard检查 =====
    plan_violation = self._check_plan(action)

    # ===== 3. Test Guard检查 =====
    test_violation = self._check_test(action)

    # ===== 4. Evidence Guard检查 =====
    evidence_violation = self._check_evidence(action)  # LLM调用点3

    # ===== 5. 计算drift score =====
    drift_score = (
        self.weights['scope'] * scope_violation +
        self.weights['plan'] * plan_violation +
        self.weights['test'] * test_violation +
        self.weights['evidence'] * evidence_violation
    )

    # ===== 6. 决策 =====
    if drift_score >= self.rollback_threshold:
        return ActionDecision.ROLLBACK_ADVISORY
    elif drift_score >= self.warn_threshold:
        return ActionDecision.WARN
    else:
        return ActionDecision.OK
```

### 4.3 四个守卫的具体检查逻辑

#### **Scope Guard (权重 0.4)**
```python
def _check_scope(self, action):
    """检查文件修改是否超出范围"""

    if action.type != "edit_file":
        return 0.0  # 不修改文件，无scope违规

    # 更新已修改文件集合
    self.modified_files.add(action.file_path)

    # 违规条件1: 修改文件数超过difficulty阈值
    if len(self.modified_files) > self.scope_file_limit:
        violation_severity = 1.0

    # 违规条件2: 修改了不在expected_scope的文件
    elif action.file_path not in self.expected_scope:
        violation_severity = 0.7

    else:
        violation_severity = 0.0

    return violation_severity

def _get_scope_limit(self, difficulty):
    """根据难度返回文件数阈值"""
    # 数据依据：85.8%的任务只修改1个文件
    limits = {
        '< 15 min': 2,           # 简单任务，最多2个文件
        '15 min - 1 hour': 3,    # 中等任务，最多3个文件
        '1-4 hours': 5,          # 困难任务，最多5个文件
        '> 4 hours': 8,          # 非常困难任务，最多8个文件
    }
    return limits.get(difficulty, 3)  # 默认3个文件
```

#### **Plan Guard (权重 0.3)**
```python
def _check_plan(self, action):
    """检查action是否符合当前phase"""

    # 推断当前phase
    self._update_phase()

    # Phase规则（来自proposal定义）
    phase_rules = {
        'understand': ['read_file', 'grep', 'search'],
        'reproduce': ['run_test', 'bash'],
        'implement': ['edit_file', 'insert', 'replace'],
        'verify': ['run_test'],
    }

    allowed_actions = phase_rules[self.current_phase]

    # 违规检查
    if action.type not in allowed_actions:
        # 特殊情况：implement阶段必须先运行过failing test
        if action.type == 'edit_file' and len(self.tests_run) == 0:
            return 1.0  # 严重违规：没测试就开始改代码
        else:
            return 0.5  # 一般违规：action不符合phase

    return 0.0

def _update_phase(self):
    """从action历史推断当前phase"""
    if len(self.modified_files) > 0 and len(self.tests_run) > 0:
        self.current_phase = "verify"
    elif len(self.modified_files) > 0:
        self.current_phase = "implement"
    elif len(self.tests_run) > 0:
        self.current_phase = "reproduce"
    else:
        self.current_phase = "understand"
```

#### **Test Guard (权重 0.2)**
```python
def _check_test(self, action):
    """检查测试执行情况"""

    # 更新测试集合
    if action.type == "run_test":
        self.tests_run.add(action.test_name)

    # 违规条件1: 到了verify阶段还没运行FAIL_TO_PASS中的任何测试
    if self.current_phase == "verify":
        f2p_tests_run = self.tests_run & set(self.required_tests)
        if len(f2p_tests_run) == 0:
            return 1.0  # 严重违规：没运行必需的测试

    # 违规条件2: 已经edit了文件，但还没运行任何测试
    if len(self.modified_files) > 0 and len(self.tests_run) == 0:
        return 0.6  # 中等违规：改代码但不测试

    return 0.0
```

#### **Evidence Guard (权重 0.1) - 使用LLM**
```python
def _check_evidence(self, action):
    """检查action是否有充分依据（使用LLM判断）"""

    if action.type != "edit_file":
        return 0.0  # 只检查edit action

    # LLM调用点3: 验证改动是否有依据
    prompt = f"""
    Problem: {self.problem_statement}

    Action history (last 5):
    {self._format_recent_actions(5)}

    Current edit:
    File: {action.file_path}
    Change: {action.diff}

    Question: Does this edit have sufficient evidence from prior actions?
    - Did agent read this file before editing?
    - Is the change related to the problem statement?
    - Is there evidence of understanding what to fix?

    Answer with a score 0.0-1.0 (0=strong evidence, 1=no evidence).
    """

    response = call_llm(prompt, model="gpt-4o-mini")  # 便宜的模型
    violation_score = float(response.strip())

    return violation_score
```

---

## 5. Drift Score计算

### 公式（来自proposal v2）

```
drift_score = 0.4 × scope_violation
            + 0.3 × plan_violation
            + 0.2 × test_violation
            + 0.1 × evidence_violation
```

### 决策逻辑

```python
if drift_score < 0.5:
    # ✅ OK - 允许继续
    action_decision = "ALLOW"

elif 0.5 <= drift_score < 0.8:
    # ⚠️ WARN - 记录警告，但允许继续
    action_decision = "WARN"
    log_warning(action, drift_score)

else:  # drift_score >= 0.8
    # 🚫 ROLLBACK ADVISORY - 建议回滚（block submission）
    action_decision = "ROLLBACK"
    trigger_rollback(action, drift_score)
```

### 实际例子

**场景：简单任务(<15min)，agent修改了4个文件，没运行测试**

```python
# Scope Guard
files_modified = 4
scope_limit = 2  # <15min任务阈值
scope_violation = 1.0  # 超过阈值

# Plan Guard
plan_violation = 0.5  # 在implement阶段但action顺序有问题

# Test Guard
tests_run = 0
modified_files = 4
test_violation = 0.6  # 改了代码但没测试

# Evidence Guard
evidence_violation = 0.3  # LLM判断：有一定依据但不够充分

# 计算drift score
drift_score = 0.4 × 1.0 + 0.3 × 0.5 + 0.2 × 0.6 + 0.1 × 0.3
            = 0.4 + 0.15 + 0.12 + 0.03
            = 0.70

# 决策
# 0.5 <= 0.70 < 0.8 → WARN
```

---

## 6. 事后评估与对比

### 6.1 功能正确性评估（标准SWE-bench）

```python
def evaluate_result(task, agent_result, env):
    """评估agent的解决方案"""

    # Step 1: 应用agent的patch到环境
    env.apply_patch(agent_result.patch)

    # Step 2: 运行FAIL_TO_PASS测试
    f2p_results = env.run_tests(task.fail_to_pass)
    f2p_success = all(t.status == 'PASSED' for t in f2p_results)

    # Step 3: 运行PASS_TO_PASS测试（采样或全部）
    # 注意：500个任务平均每个有8950个p2p测试，全部运行太慢
    # 采样策略：随机采样100个，或全部运行（取决于时间预算）
    p2p_sample = random.sample(task.pass_to_pass, min(100, len(task.pass_to_pass)))
    p2p_results = env.run_tests(p2p_sample)
    p2p_success = all(t.status == 'PASSED' for t in p2p_results)

    # Step 4: 判断resolved
    resolved = f2p_success and p2p_success

    return {
        'resolved': resolved,
        'f2p_passed': sum(1 for t in f2p_results if t.status == 'PASSED'),
        'f2p_total': len(f2p_results),
        'p2p_passed': sum(1 for t in p2p_results if t.status == 'PASSED'),
        'p2p_total': len(p2p_results),
    }
```

### 6.2 Scope分析（与ground truth对比）

```python
def analyze_scope(task, agent_result):
    """分析agent的scope对齐情况（对比ground truth）"""

    # 从ground truth patch提取修改的文件
    gold_files = extract_files_from_patch(task.ground_truth_patch)
    # 例如：{"django/template/engine.py"}

    # 从agent patch提取修改的文件
    agent_files = extract_files_from_patch(agent_result.patch)
    # 例如：{"django/template/engine.py", "django/template/context.py"}

    # 计算Precision和Recall
    true_positives = len(gold_files & agent_files)

    precision = true_positives / len(agent_files) if agent_files else 0
    # 1 / 2 = 0.5 (agent改了2个文件，只有1个是对的)

    recall = true_positives / len(gold_files) if gold_files else 0
    # 1 / 1 = 1.0 (标准答案改1个文件，agent都覆盖了)

    return {
        'scope_precision': precision,
        'scope_recall': recall,
        'gold_files': list(gold_files),
        'agent_files': list(agent_files),
        'extra_files': list(agent_files - gold_files),  # agent多改的文件
        'missed_files': list(gold_files - agent_files),  # agent漏改的文件
    }

def extract_files_from_patch(patch):
    """从git diff提取修改的文件列表"""
    import re
    # 匹配 "diff --git a/path/to/file.py b/path/to/file.py"
    pattern = r'diff --git a/(.*?) b/'
    files = set(re.findall(pattern, patch))
    return files
```

### 6.3 Q1完整评估指标

```python
def compute_q1_metrics(tasks, results):
    """计算Q1的所有评估指标"""

    # ===== Primary Metric: Drift Rate =====
    total_actions = sum(len(r.actions) for r in results)
    drift_actions = sum(
        1 for r in results
        for a in r.actions
        if a.drift_score >= 0.5  # WARN阈值
    )
    drift_rate = drift_actions / total_actions

    # ===== Secondary Metric: Scope Precision/Recall =====
    scope_analyses = [analyze_scope(t, r) for t, r in zip(tasks, results)]
    avg_precision = np.mean([s['scope_precision'] for s in scope_analyses])
    avg_recall = np.mean([s['scope_recall'] for s in scope_analyses])

    # ===== Resolve Rate =====
    evaluations = [evaluate_result(t, r, env) for t, r in zip(tasks, results)]
    resolve_rate = sum(e['resolved'] for e in evaluations) / len(evaluations)

    # ===== False Positive Rate（误报率） =====
    # 定义：drift警告触发，但最终resolved的比例
    warned_tasks = [r for r in results if any(a.drift_score >= 0.5 for a in r.actions)]
    warned_resolved = [e for r, e in zip(results, evaluations)
                       if any(a.drift_score >= 0.5 for a in r.actions) and e['resolved']]
    false_positive_rate = len(warned_resolved) / len(warned_tasks) if warned_tasks else 0

    return {
        'drift_rate': drift_rate,
        'scope_precision': avg_precision,
        'scope_recall': avg_recall,
        'resolve_rate': resolve_rate,
        'false_positive_rate': false_positive_rate,
    }
```

---

## 7. LLM使用点

### 总结：Q1中的3个LLM调用点

| LLM调用点 | 用途 | 频率 | 模型建议 | 成本估算 |
|----------|------|------|---------|---------|
| **1. Parse Scope** | 从problem_statement解析预期修改范围 | 1次/任务（初始化） | GPT-4o | ~$0.01/任务 |
| **2. Parse Plan** | 从problem_statement解析预期步骤 | 1次/任务（初始化） | GPT-4o | ~$0.01/任务 |
| **3. Evidence Check** | 验证edit action是否有充分依据 | N次/任务（每次edit） | GPT-4o-mini | ~$0.001/action |

### 详细说明

#### LLM调用点1: Parse Scope (Scope Guard初始化)
```python
def _parse_scope(self, problem_statement):
    """使用LLM解析预期修改范围"""

    prompt = f"""
    Task: {problem_statement}

    Question: Based on this problem description, which files are likely to need modification?

    Rules:
    - Only list files explicitly mentioned or strongly implied
    - Be conservative (better to miss than to over-predict)
    - Return as JSON array of file paths

    Example output:
    {{"files": ["path/to/file1.py", "path/to/file2.py"]}}
    """

    response = call_llm(prompt, model="gpt-4o")
    expected_scope = json.loads(response)['files']

    return set(expected_scope)
```

#### LLM调用点2: Parse Plan (Plan Guard初始化)
```python
def _parse_plan(self, problem_statement):
    """使用LLM解析预期执行步骤"""

    prompt = f"""
    Task: {problem_statement}

    Question: What are the expected phases to solve this bug?

    Phases:
    - understand: Read code, search for relevant functions
    - reproduce: Run tests to confirm the bug
    - implement: Modify code to fix the bug
    - verify: Run tests to confirm fix works

    Return as JSON with expected target (function/class to fix):
    {{"target": "FunctionName or ClassName", "key_files": ["file1.py"]}}
    """

    response = call_llm(prompt, model="gpt-4o")
    plan = json.loads(response)

    return plan
```

#### LLM调用点3: Evidence Check (Evidence Guard实时检查)
```python
# 见前面4.3节的代码，每次edit_file action都调用
```

### 成本估算（500任务）

```python
# 假设平均每个任务20个action，其中5个是edit
per_task_cost = (
    0.01 +  # Parse Scope
    0.01 +  # Parse Plan
    5 * 0.001  # Evidence Check × 5 edits
) = 0.025

total_cost_for_500 = 0.025 * 500 = $12.5
```

**关键优化**：
- Scope/Plan解析只在任务开始时调用1次（可以缓存）
- Evidence Check使用便宜的GPT-4o-mini
- 可以考虑用本地Qwen-32B替代Evidence Check（降低到接近$0）

---

## 8. 完整流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│  Step 1: 数据加载与解析                                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  verified.jsonl (line i=1)                                          │
│         │                                                            │
│         ↓                                                            │
│  Parse JSON → SWEBenchTask object                                   │
│         │                                                            │
│         ├─→ Part A (给Agent):                                       │
│         │   • problem_statement                                     │
│         │   • repo + base_commit                                    │
│         │                                                            │
│         ├─→ Part B (给Q1监控):                                      │
│         │   • problem_statement (解析scope/plan)                    │
│         │   • difficulty (校准阈值)                                 │
│         │   • FAIL_TO_PASS/PASS_TO_PASS (Test Guard)               │
│         │                                                            │
│         └─→ Part C (评估用):                                        │
│             • patch (ground truth)                                  │
│             • FAIL_TO_PASS/PASS_TO_PASS (运行测试)                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│  Step 2: Q1初始化 (Four-Guard Monitor)                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  🤖 LLM调用点1: Parse Scope                                         │
│     Input: problem_statement                                        │
│     Output: expected_scope = {"file1.py", "file2.py"}              │
│     Cost: ~$0.01/task                                               │
│                                                                      │
│  🤖 LLM调用点2: Parse Plan                                          │
│     Input: problem_statement                                        │
│     Output: expected_target = "FunctionName"                        │
│     Cost: ~$0.01/task                                               │
│                                                                      │
│  初始化守卫权重:                                                      │
│     • Scope: 0.4   • Plan: 0.3                                      │
│     • Test:  0.2   • Evidence: 0.1                                  │
│                                                                      │
│  设置阈值:                                                            │
│     • WARN: 0.5    • ROLLBACK: 0.8                                  │
│                                                                      │
│  根据difficulty设置scope_file_limit:                                │
│     • "<15min": 2 files    • "15min-1h": 3 files                   │
│     • "1-4h": 5 files      • ">4h": 8 files                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│  Step 3: Agent执行任务 (带实时监控)                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Agent.execute(problem_statement)                                   │
│         │                                                            │
│         ↓                                                            │
│  ┌──────────────────────────────────────────────┐                  │
│  │  Agent Action Loop (最多100个action)         │                  │
│  │                                               │                  │
│  │  For each action:                             │                  │
│  │    1. Agent生成action (e.g., edit_file)      │                  │
│  │    2. Four-Guard监控 ──────────────┐         │                  │
│  │    3. 计算drift_score               │         │                  │
│  │    4. 决策: OK/WARN/ROLLBACK        │         │                  │
│  │    5. 执行action (如果允许)          │         │                  │
│  │    6. 更新状态                       │         │                  │
│  │    7. 记录日志                       │         │                  │
│  │                                     │         │                  │
│  │  直到: submit() or 超过action限制    │         │                  │
│  └──────────────────────────────────────────────┘                  │
│                           │                      │                  │
│                           ↓                      ↓                  │
│                    agent_patch           drift_log                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│  Step 4: 实时监控详细流程 (每个action)                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Action: edit_file("django/template/engine.py", diff)               │
│         │                                                            │
│         ├─→ 【Scope Guard】 ───────────────────────────────────┐   │
│         │   • modified_files.add("engine.py")                   │   │
│         │   • Count: 1 file (limit=2 for <15min task)          │   │
│         │   • Is in expected_scope? Yes                         │   │
│         │   → scope_violation = 0.0 ✅                          │   │
│         │                                                        ↓   │
│         ├─→ 【Plan Guard】 ────────────────────────────────────┐│   │
│         │   • Current phase: "implement"                        ││   │
│         │   • Allowed actions: [edit_file, ...]                ││   │
│         │   • Has run tests? Yes (in action history)           ││   │
│         │   → plan_violation = 0.0 ✅                          ││   │
│         │                                                        ↓│   │
│         ├─→ 【Test Guard】 ────────────────────────────────────┐││   │
│         │   • tests_run: {"test_autoescape_off"}               │││   │
│         │   • Covers FAIL_TO_PASS? Yes                         │││   │
│         │   → test_violation = 0.0 ✅                          │││   │
│         │                                                        ↓││   │
│         └─→ 【Evidence Guard】 (🤖 LLM调用点3) ────────────────┐│││   │
│             • Check: Did agent read file before edit? Yes      ││││   │
│             • Check: Change relates to problem? Yes            ││││   │
│             • GPT-4o-mini judges: score=0.1 (strong evidence)  ││││   │
│             → evidence_violation = 0.1 ✅                      ││││   │
│                                                                 ↓│││   │
│         ┌────────────────────────────────────────────────────┐ ││││   │
│         │  Drift Score Calculation                           │ ││││   │
│         │  drift = 0.4×0.0 + 0.3×0.0 + 0.2×0.0 + 0.1×0.1    │←┘│││   │
│         │        = 0.01                                      │  │││   │
│         └────────────────────────────────────────────────────┘  │││   │
│                          ↓                                       │││   │
│         ┌────────────────────────────────────────────────────┐  │││   │
│         │  Decision Logic                                    │  │││   │
│         │  if drift < 0.5:      → ✅ ALLOW (continue)        │  │││   │
│         │  elif drift < 0.8:    → ⚠️ WARN (log + continue)  │  │││   │
│         │  else:                → 🚫 ROLLBACK (block)        │  │││   │
│         │                                                     │  │││   │
│         │  Result: 0.01 < 0.5 → ALLOW ✅                     │  │││   │
│         └────────────────────────────────────────────────────┘  │││   │
│                          │                                       │││   │
│                          ↓                                       │││   │
│                  Execute action                                 │││   │
│                  Log to drift_log                               │││   │
│                                                                  │││   │
└──────────────────────────────────────────────────────────────────┴┴┴───┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│  Step 5: Agent完成 → 产生agent_patch                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  agent_patch = """                                                  │
│  diff --git a/django/template/engine.py                            │
│  --- a/django/template/engine.py                                   │
│  +++ b/django/template/engine.py                                   │
│  @@ -163 +163 @@                                                    │
│  -   return t.render(Context(context))                             │
│  +   return t.render(Context(context, autoescape=self.autoescape)) │
│  """                                                                │
│                                                                      │
│  drift_log = [                                                      │
│    {action: "read_file(engine.py)", drift: 0.0, decision: "OK"},   │
│    {action: "run_test(...)", drift: 0.0, decision: "OK"},          │
│    {action: "edit_file(engine.py)", drift: 0.01, decision: "OK"},  │
│    {action: "run_test(...)", drift: 0.0, decision: "OK"},          │
│  ]                                                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│  Step 6: 事后评估 (与ground truth对比)                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────┐            │
│  │  6.1 功能正确性评估 (标准SWE-bench)                │            │
│  ├────────────────────────────────────────────────────┤            │
│  │  • Apply agent_patch to repo                       │            │
│  │  • Run FAIL_TO_PASS tests                          │            │
│  │    → ["test_autoescape_off"] → ✅ PASSED           │            │
│  │  • Run PASS_TO_PASS tests (sample 100)             │            │
│  │    → 100/100 tests → ✅ PASSED                      │            │
│  │  • Conclusion: resolved = True ✅                   │            │
│  └────────────────────────────────────────────────────┘            │
│                          ↓                                          │
│  ┌────────────────────────────────────────────────────┐            │
│  │  6.2 Scope分析 (对比ground truth patch)            │            │
│  ├────────────────────────────────────────────────────┤            │
│  │  gold_files = {"django/template/engine.py"}        │            │
│  │  agent_files = {"django/template/engine.py"}       │            │
│  │                                                     │            │
│  │  scope_precision = 1/1 = 1.0 ✅                    │            │
│  │  scope_recall    = 1/1 = 1.0 ✅                    │            │
│  │  extra_files     = []    (没有多改)                │            │
│  │  missed_files    = []    (没有漏改)                │            │
│  └────────────────────────────────────────────────────┘            │
│                          ↓                                          │
│  ┌────────────────────────────────────────────────────┐            │
│  │  6.3 Q1 Drift分析                                  │            │
│  ├────────────────────────────────────────────────────┤            │
│  │  total_actions = 4                                 │            │
│  │  drift_actions (≥0.5) = 0                          │            │
│  │  drift_rate = 0/4 = 0% ✅                          │            │
│  │                                                     │            │
│  │  false_positive = N/A (没有警告触发)                │            │
│  └────────────────────────────────────────────────────┘            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│  Step 7: 最终结果                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  {                                                                  │
│    "task_id": "django__django-11119",                              │
│    "resolved": True,              ✅ 功能正确                        │
│    "scope_precision": 1.0,        ✅ 没有改多余文件                  │
│    "scope_recall": 1.0,           ✅ 没有漏改关键文件                │
│    "drift_rate": 0.0,             ✅ 过程完全对齐                    │
│    "drift_log": [...],            📊 详细日志供分析                  │
│  }                                                                  │
│                                                                      │
│  结论: 完美任务 - 功能正确 + 过程对齐 + scope精确                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 9. 关键要点总结

### 数据使用

| 何时 | 哪些Field | 用途 |
|-----|----------|------|
| **任务开始** | `problem_statement`, `difficulty` | 初始化Four-Guard，解析scope/plan |
| **实时监控** | `FAIL_TO_PASS`, `PASS_TO_PASS` | Test Guard检查 |
| **事后评估** | `patch` (ground truth) | Scope Precision/Recall分析 |
| **事后评估** | `FAIL_TO_PASS`, `PASS_TO_PASS` | 运行测试判断resolved |

### Q1核心创新

1. **不是简单的"运行测试"** - 而是多维度实时监控（Scope + Plan + Test + Evidence）
2. **不是静态规则** - 而是动态权重组合（difficulty自适应阈值）
3. **不只看结果** - 而是看过程（即使最终resolved，也分析drift）

### LLM使用策略

- **昂贵模型(GPT-4o)**: 只在任务初始化时用2次（Parse Scope/Plan）
- **便宜模型(GPT-4o-mini)**: 每次edit时检查Evidence
- **可优化**: Evidence Check可以用本地Qwen-32B替代

### 评估双重标准

1. **功能正确性（标准SWE-bench）**: `resolved = FAIL_TO_PASS通过 AND PASS_TO_PASS不破坏`
2. **过程质量（Q1创新）**: `drift_rate = % actions with drift ≥ 0.5`

**关键洞察**: 一个任务可以：
- ✅ Resolved + ✅ Low drift = 完美（目标）
- ✅ Resolved + ❌ High drift = 成功但过程曲折（Q1要改进的）
- ❌ Not resolved = 失败

---

## 10. 对比Baseline（回答"为什么需要Q1"）

### Unmonitored Agent（Q1 disabled）

```python
# 没有Four-Guard监控
agent.execute(problem_statement)
# → 可能resolved，但drift未知
# → 可能改了10个文件，最后撞大运成功
# → 过程不透明，无法改进
```

### With Q1（Four-Guard enabled）

```python
# 有Four-Guard监控
guard = FourGuardMonitor(...)
agent.execute(problem_statement, monitor=guard)
# → resolved + 知道drift_rate
# → 如果drift高，知道是哪个guard触发的
# → 可以分析：为什么drift？如何改进？
```

### 预期结果

| Baseline | Resolve Rate | Drift Rate | Scope Precision |
|---------|--------------|------------|-----------------|
| **Unmonitored** | 25% | 35% ❌ | 0.6 ⚠️ |
| **With Q1** | 30% ✅ | <15% ✅ | 0.85 ✅ |

**Q1价值**: 不仅提升resolve rate，更重要的是降低drift（更可控、可解释、可改进）

---

## Next Steps

1. **Week 1, Day 1-2**: 实现数据加载pipeline（`load_task()`, `SWEBenchTask`类）
2. **Week 1, Day 3-4**: 实现Four-Guard框架（Scope/Plan/Test/Evidence guards）
3. **Week 1, Day 5**: 集成LLM调用（Parse Scope/Plan, Evidence Check）
4. **Week 1, Day 6-7**: 在5个简单任务上测试，建立baseline

**Ready to start?** 🚀


> 还有这些问题（如果你已经回答了，就不用细说了）：
---
Q1:得到了很高的或者很低的drift 
score，然后又如何呢？给AI说偏离了要做的事情，“你走偏了/你走的对”，然后呢，我需要继续设计下一步吗？怎么验证我的AI工具会更好？怎么验证我的AI工具最
后得到了正确的答案（其他的resaerch怎么用这个swebench-verified），这一块是不是工作量很大？或者说我方向说错了，得到了drift 
score之后，Q1就结束了，我只需要report一个分析，就说drift产生的时候，出现在difficulty更难problem 
statement？或者其他的方法、考虑？我只是想知道这个数据对我的Q1和我proposal联系在哪里。我也不清楚解决率（Resolve 
Rate）在这里的地位。最后，我的理解： "resolved = FAIL_TO_PASS 全过 且 PASS_TO_PASS 全过。" 这个怎么得到？SWE 
bench有现成的代码吗、官方提供评测器、他们的要求如何？我不太明白。简述这部分。 

⏺ 好问题！这些是核心问题，我直接回答：

  ---
  🎯 Q1: Drift Score得到后怎么办？

  你的Q1有两个阶段（来自proposal v2）

  Phase 1: Shadow Mode (Week 1, 只监控不干预)

  # Week 1: 建立baseline
  drift_score = calculate_drift(action)

  if drift_score >= 0.5:
      log_warning(action, drift_score)  # 只记录，不阻止
      # Agent不知道drift，继续执行

  # 目的：
  # 1. 收集数据：哪些任务容易drift？
  # 2. 校准阈值：0.5/0.8是否合理？
  # 3. 建立baseline：Unmonitored agent的drift rate是多少？

  结果:
  - Baseline drift rate (例如 35%)
  - Resolve rate without intervention (例如 25%)

  ---
  Phase 2: Advisory Mode (Week 2+, 监控+干预)

  # Week 2+: 实时干预
  drift_score = calculate_drift(action)

  if drift_score >= 0.8:
      # 🚫 ROLLBACK: 阻止agent继续
      send_feedback_to_agent(
          "⚠️ High drift detected (score=0.8)! "
          "You modified 4 files but expected scope is 1-2 files. "
          "Recommend: rollback last 2 edits and focus on core fix."
      )
      block_submission = True  # 不允许submit

  elif drift_score >= 0.5:
      # ⚠️ WARN: 给agent警告，但允许继续
      send_feedback_to_agent(
          "⚠️ Moderate drift (score=0.5). "
          "Consider: Have you run the failing test yet?"
      )

  # Agent接收反馈，调整行为

  关键：Agent在下一个action时会看到这个反馈（类似tool result）

  ---
  实际Agent交互示例

  # Agent的perspective:

  # Action 1
  agent: edit_file("file1.py", ...)
  system: ✅ OK (drift=0.1)

  # Action 2
  agent: edit_file("file2.py", ...)
  system: ✅ OK (drift=0.3)

  # Action 3
  agent: edit_file("file3.py", ...)
  system: ⚠️ WARNING (drift=0.6)
          "You've modified 3 files, but task difficulty suggests 1-2 files.
           Consider: Is file3.py really necessary?"

  # Action 4
  agent: edit_file("file4.py", ...)
  system: 🚫 ROLLBACK ADVISORY (drift=0.85)
          "High drift! Recommend rollback.
           You haven't run the FAIL_TO_PASS test yet.
           Blocking submission until you run tests."

  # Agent调整策略
  agent: run_test("test_autoescape_off")  # 先测试
  agent: rollback_edit("file3.py", "file4.py")  # 撤销多余修改

  ---
  🧪 Q2: 如何验证Q1有效？

  对比实验设计

  | 配置                    | Drift Detection        | 预期Drift Rate | 预期Resolve Rate |
  |-----------------------|------------------------|--------------|----------------|
  | Baseline: Unmonitored | ❌ 关闭Q1                 | ~35% (高)     | ~25%           |
  | Q1: Advisory Mode     | ✅ 开启Q1 (WARN+ROLLBACK) | <15% ✅ (低)   | ≥30% ✅ (提升)    |

  实验流程

  # 1. Week 1: Baseline (Unmonitored)
  results_baseline = []
  for task in validation_tasks[:50]:  # 50个任务
      result = run_agent(task, monitor=None)  # Q1关闭
      results_baseline.append({
          'resolved': evaluate(task, result),
          'drift_rate': calculate_drift_rate(result.actions),  # 事后计算
      })

  baseline_resolve = mean(r['resolved'] for r in results_baseline)
  baseline_drift = mean(r['drift_rate'] for r in results_baseline)

  print(f"Baseline: Resolve={baseline_resolve:.1%}, Drift={baseline_drift:.1%}")
  # 例如: Baseline: Resolve=25%, Drift=35%

  # 2. Week 2: With Q1 (Advisory Mode)
  results_q1 = []
  for task in validation_tasks[:50]:  # 同样50个任务
      guard = FourGuardMonitor(...)  # Q1开启
      result = run_agent(task, monitor=guard)
      results_q1.append({
          'resolved': evaluate(task, result),
          'drift_rate': guard.get_drift_rate(),
      })

  q1_resolve = mean(r['resolved'] for r in results_q1)
  q1_drift = mean(r['drift_rate'] for r in results_q1)

  print(f"With Q1: Resolve={q1_resolve:.1%}, Drift={q1_drift:.1%}")
  # 目标: With Q1: Resolve=30%, Drift=12%

  # 3. 统计检验
  from scipy.stats import chi2_contingency

  # Resolve rate improvement
  contingency_table = [
      [baseline_resolve * 50, (1-baseline_resolve) * 50],
      [q1_resolve * 50, (1-q1_resolve) * 50],
  ]
  chi2, p_value = chi2_contingency(contingency_table)

  print(f"Improvement is significant: p={p_value:.4f}")
  # 如果 p < 0.05 → Q1显著有效

  ---
  ✅ Q3: 如何得到"Resolved"？SWE-bench官方评估器

  官方工具：SWE-bench Docker Evaluator

  好消息：SWE-bench提供现成的评估器，你不需要自己写！

  # 官方仓库
  git clone https://github.com/princeton-nlp/SWE-bench.git
  cd SWE-bench

  # 安装
  pip install -e .

  # 使用官方评估器
  python -m swebench.harness.run_evaluation \
      --predictions_path predictions.jsonl \
      --swe_bench_tasks data/swebench/verified.jsonl \
      --log_dir logs/ \
      --testbed /tmp/testbed

  输入格式（你需要准备的）

  # predictions.jsonl (你的agent输出)
  {"instance_id": "django__django-11119", "model_patch": "diff --git a/django/template/engine.py\n..."}
  {"instance_id": "astropy__astropy-12907", "model_patch": "diff --git a/astropy/modeling/separable.py\n..."}

  官方评估器做什么

  # 官方代码（你不用写！）会做这些：

  for task in swe_bench_tasks:
      # 1. 创建Docker容器
      container = create_docker_container(task['repo'], task['base_commit'])

      # 2. 应用你的patch
      container.apply_patch(predictions[task['instance_id']]['model_patch'])

      # 3. 运行FAIL_TO_PASS测试
      f2p_results = container.run_tests(task['FAIL_TO_PASS'])

      # 4. 运行PASS_TO_PASS测试
      p2p_results = container.run_tests(task['PASS_TO_PASS'])

      # 5. 判断resolved
      resolved = (
          all(t['status'] == 'PASSED' for t in f2p_results) and
          all(t['status'] == 'PASSED' for t in p2p_results)
      )

      # 6. 保存结果
      results.append({
          'instance_id': task['instance_id'],
          'resolved': resolved,
      })

  # 7. 输出最终报告
  print(f"Resolve Rate: {sum(r['resolved'] for r in results) / len(results)}")

  输出结果

  // evaluation_results.json
  {
    "resolved": {
      "django__django-11119": true,
      "astropy__astropy-12907": false,
      ...
    },
    "resolve_rate": 0.30,  // 30%
    "total": 500,
    "resolved_count": 150
  }

  ---
  📊 Q4: Resolve Rate在Q1中的地位

  双重指标系统

  | 指标                 | 含义                         | 用途     | 目标   |
  |--------------------|----------------------------|--------|------|
  | Resolve Rate (主指标) | 功能正确性（测试通过率）               | 证明系统有用 | ≥30% |
  | Drift Rate (Q1主指标) | 过程对齐度（% actions drift≥0.5） | 证明系统可控 | <15% |

  四种可能结果

  | Resolved | Drift         | 含义               | Q1价值      |
  |----------|---------------|------------------|-----------|
  | ✅ Yes    | ✅ Low (<15%)  | 理想 - 功能对+过程优     | ⭐⭐⭐ 完美    |
  | ✅ Yes    | ❌ High (>30%) | 成功但曲折 - 瞎猫碰死耗子   | ⭐⭐ Q1要解决的 |
  | ❌ No     | ✅ Low         | 失败但对齐 - 方向对但能力不足 | ⭐ 不是Q1重点  |
  | ❌ No     | ❌ High        | 双重失败 - 完全走偏      | ❌ Q1要防止的  |

  Q1的核心价值主张

  不仅要"做对"（resolved），还要"做对的方式"（low drift）

  原因：
  1. 可解释性：低drift = agent行为可理解
  2. 可调试性：高drift = 不知道为什么成功/失败
  3. 可改进性：低drift = 知道哪里可以优化
  4. 成本控制：低drift = 更少冗余action，更低成本

  你的论文会这样报告

  ## Results

  ### Overall Performance (Table 1)
  | System | Resolve Rate | Drift Rate | Scope Precision |
  |--------|--------------|------------|-----------------|
  | Baseline (Unmonitored) | 25% | 35% | 0.60 |
  | **Ours (Q1 Advisory)** | **30%** ✅ | **12%** ✅ | **0.85** ✅ |

  ### Key Findings

  1. **Q1 improves both success and alignment**
     - Resolve rate: +5% absolute improvement (25% → 30%)
     - Drift rate: -23% absolute reduction (35% → 12%)

  2. **Success cases breakdown** (Figure 2)
     - Clean success (resolved + low drift): 28% (Q1) vs 18% (baseline)
     - Lucky success (resolved + high drift): 2% (Q1) vs 7% (baseline)

  3. **Drift prevents failures** (Figure 3)
     - Tasks with drift>0.5 at action-10: 68% eventually fail
     - Early WARN intervention → 40% rescue rate

  ---
  🏗️ Q5: Q1工作量评估

  简化方案（利用现成工具）

  | 组件           | 工作量  | 可复用资源                    |
  |--------------|------|--------------------------|
  | 数据加载         | 1天   | ✅ 已完成（你的scripts）         |
  | Four-Guard逻辑 | 2-3天 | ⚠️ 需要实现，但逻辑清晰            |
  | LLM调用        | 1天   | ✅ 简单（OpenAI API）         |
  | Agent集成      | 2天   | ⚠️ 取决于用哪个agent scaffold  |
  | 评估器          | 0.5天 | ✅ 用官方SWE-bench evaluator |
  | 实验运行         | 1天   | ✅ 自动化                    |
  | 分析结果         | 1天   | ✅ 简单统计                   |
  | 总计           | 8-9天 | Week 1-2完成               |

  最大简化：使用现成Agent

  # 不需要从零写agent！用现成的：

  # Option 1: SWE-agent (官方提供)
  from sweagent import SWEAgent
  agent = SWEAgent()
  agent.add_monitor(your_four_guard)  # 注入Q1

  # Option 2: 简化版agent
  class SimpleAgent:
      def execute(self, task):
          # GPT-4调用 + 简单工具
          for step in range(100):
              action = gpt4_decide_action(task, history)
              if self.monitor:
                  decision = self.monitor.check(action)
                  if decision == "ROLLBACK":
                      break  # 停止
              result = execute_action(action)
              history.append((action, result))

  ---
  🎯 Q6: Q1的最终目标（回答你的核心困惑）

  Q1不只是"分析报告"！

  错误理解 ❌:
  "Q1只是得到drift score，然后分析一下drift出现在哪些难度的任务"

  正确理解 ✅:
  "Q1是一个实时干预系统，通过监控drift来改进agent行为，最终提升resolve rate"

  完整循环

  ┌────────────────────────────────────────────────────┐
  │  Week 1: Shadow Mode (被动观察)                     │
  │  → 建立baseline: drift_rate=35%, resolve=25%      │
  │  → 分析：哪些任务drift高？哪个guard最重要？        │
  └────────────────────────────────────────────────────┘
                      ↓
  ┌────────────────────────────────────────────────────┐
  │  Week 2: Advisory Mode (主动干预)                  │
  │  → Agent收到WARN/ROLLBACK反馈                      │
  │  → Agent调整行为（减少drift）                      │
  │  → 结果：drift_rate=12%, resolve=30%               │
  └────────────────────────────────────────────────────┘
                      ↓
  ┌────────────────────────────────────────────────────┐
  │  Paper贡献                                          │
  │  1. 机制：Four-Guard多维度监控                     │
  │  2. 效果：降低drift + 提升resolve                  │
  │  3. 分析：哪种drift最致命？哪个guard最有效？       │
  └────────────────────────────────────────────────────┘

  ---
  📋 总结：回答你的所有问题

  | 问题                 | 答案                                                                    |
  |--------------------|-----------------------------------------------------------------------|
  | 得到drift score后怎么办？ | Week 1: 只记录Week 2+: 给agent反馈(WARN/ROLLBACK)                           |
  | 如何验证Q1有效？          | 对比实验：Unmonitored vs With Q1预期：drift↓, resolve↑                        |
  | 如何得到resolved？      | ✅ 用官方SWE-bench evaluator输入：predictions.jsonl (你的patch)输出：resolve_rate |
  | Resolve Rate的地位？   | Primary metric (证明有用)Drift Rate是Q1 primary metric (证明可控)两者都要报告        |
  | Q1工作量大吗？           | ~8-9天关键：用官方evaluator（不用自己写测试评估）                                       |
  | Q1最终目标？            | 不只是分析！实时干预系统，改进agent行为，提升resolve                                      |

  ---
  🚀 Next Steps (Week 1具体任务)

  # Day 1-2: 数据+基础框架
  ✅ 数据加载（已完成）
  □ SWEBenchTask类
  □ 简单agent或集成SWE-agent

  # Day 3-4: Four-Guard实现
  □ Scope Guard (文件数检查 + expected_scope)
  □ Plan Guard (phase规则)
  □ Test Guard (FAIL_TO_PASS覆盖)
  □ Evidence Guard (LLM调用)

  # Day 5: Shadow Mode测试
  □ 在5个简单任务上运行（Q1关闭）
  □ 建立baseline: drift_rate + resolve_rate

  # Day 6-7: Advisory Mode测试
  □ 开启WARN/ROLLBACK
  □ 同样5个任务
  □ 对比：drift是否降低？resolve是否提升？

  # Week 2: 扩大规模
  □ 50个validation任务
  □ 统计检验
  □ 准备Week 3 checkpoint

  关键简化：
  - ✅ 用官方SWE-bench evaluator（省2-3天）
  - ✅ 用现成agent scaffold（省3-4天）
  - ✅ 你的数据scripts已完成（省1天）

  实际Q1核心工作：Four-Guard逻辑 + LLM集成 = ~3-4天coding

  清楚了吗？

● How is Claude doing this session? (optional)
  1: Bad    2: Fine   3: Good   0: Dismiss

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
>  
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ⏵⏵ accept edits on (shift+tab to cycle)
