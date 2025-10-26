# Agent Memory Lab 端到端流程详解

## 概述
这个系统模拟了一个完整的软件开发代理工作流程，从原始数据（patch、日志）到最终的模式学习和视图渲染。

## 具体流程分析

### 输入数据
**原始数据文件**：
- `goal.json`: 任务目标定义
- `patch.diff`: 代码变更补丁
- `term.log`: 终端执行日志
- `cursor.md`: Cursor 编辑器的操作记录

### Step 1: 从 Patch 构建事件 (`patch2events.py`)
**输入**: `patch.diff`
**输出**: `events.jsonl`

**具体做了什么**：
1. 解析 patch 文件，识别修改的文件
2. 为每个修改的文件创建一个"edit"事件
3. 记录修改位置、工具类型、阶段等信息

**示例输出**：
```json
{"run_id": "r42", "step": 1, "phase": "modify", "tool": "edit", "where": "README.md:?", "what": {"diff": "(omitted hunk)", "ast_hint": null}, "why": "from patch.diff", "evidence": {}}
{"run_id": "r42", "step": 2, "phase": "modify", "tool": "edit", "where": "requirements.txt:?", "what": {"diff": "(omitted hunk)", "ast_hint": null}, "why": "from patch.diff", "evidence": {}}
```

### Step 2: 从终端日志追加事件 (`term2events.py`)
**输入**: `term.log`
**输出**: 追加到 `events.jsonl`

**具体做了什么**：
1. 解析终端日志，识别 pytest 命令
2. 为每个测试命令创建"shell"事件
3. 区分测试阶段（test）和回归测试（regress）

**示例输出**：
```json
{"run_id": "r42", "step": 3, "phase": "test", "tool": "shell", "cmd": "pytest -k doc_lang_check", "result": "unknown"}
{"run_id": "r42", "step": 4, "phase": "test", "tool": "shell", "cmd": "pytest -k whitelist_diff_check", "result": "unknown"}
{"run_id": "r42", "step": 5, "phase": "regress", "tool": "shell", "cmd": "pytest", "result": "unknown"}
```

### Step 3: 计算守卫和漂移 (`events2guards.py`)
**输入**: `events.jsonl` + `goal.json`
**输出**: `guards.jsonl`

**具体做了什么**：
1. **Scope Guard**: 检查是否修改了允许的文件
2. **Plan Guard**: 检查是否违反了计划约束
3. **Test Guard**: 检查是否执行了必要的测试
4. **Evidence Guard**: 检查是否有足够的证据支持修改
5. **Drift Score**: 综合计算漂移分数

**关键发现**：
- Step 1 (README.md): 所有守卫都通过，drift_score = 0.05
- Step 2 (requirements.txt): 违反范围守卫，drift_score = 0.75，触发警告

### Step 4: 提取模式 (`extract_and_save`)
**输入**: 事件数据和反思
**输出**: `pattern.pc_doc_only_change.json`

**具体做了什么**：
1. 分析事件序列，识别模式
2. 提取触发词、步骤、不变量、反模式等
3. 生成可重用的模式卡

**生成的模式**：
```json
{
  "pattern_id": "pc_doc_only_change",
  "triggers": ["documentation-only", "translate readme"],
  "steps": ["whitelist README.md/docs/**", "forbid requirements.*", "doc_lang_check & whitelist_diff_check"],
  "invariants": ["only whitelisted files changed", "language==target"],
  "anti_patterns": ["edit requirements without consent"],
  "eval_examples": ["doc_lang_check", "whitelist_diff_check"]
}
```

### Step 5: 复制到全局库
将模式卡复制到 `data/patterns/` 目录，供后续检索使用。

### Step 6: 模式检索 (`retrieve`)
**输入**: 新任务目标 + 全局模式库
**输出**: 最佳匹配模式

**具体做了什么**：
1. 分析任务目标："Translate README; documentation-only; avoid dependency changes"
2. 与模式库中的模式进行匹配
3. 返回最佳匹配：`pc_doc_only_change`，得分 1.0

### Step 7: 视图渲染 (`choose_view` + `render`)
**输入**: 模式 + 用户配置文件
**输出**: `view_preview.md`

**具体做了什么**：
1. 根据用户配置文件选择视图类型（terse/guided）
2. 渲染相应的视图内容
3. 生成预览文档

## 关键洞察

### 1. 漂移检测
系统成功检测到了违规行为：
- 修改 `requirements.txt` 违反了 `forbidden_paths` 约束
- 触发了 scope_guard 和 plan_guard 警告
- drift_score 达到 0.75，触发警告

### 2. 模式学习
系统从这次运行中学习到了"文档翻译"模式：
- 识别了触发条件（documentation-only, translate readme）
- 总结了最佳实践（whitelist 策略、测试要求）
- 记录了反模式（不要随意修改依赖）

### 3. 知识复用
当遇到类似任务时，系统能够：
- 检索到相关模式
- 提供具体的操作指导
- 根据用户水平调整视图详细程度

## 实际应用价值

这个系统展示了如何：
1. **监控开发过程**：实时检测偏离目标的行为
2. **学习最佳实践**：从成功案例中提取可重用的模式
3. **提供智能指导**：为新任务提供基于经验的建议
4. **个性化体验**：根据用户水平调整信息详细程度

这正是 Q1（执行监控）、Q2（跨会话学习）、Q3（动态抽象）三个核心能力的完美体现！
