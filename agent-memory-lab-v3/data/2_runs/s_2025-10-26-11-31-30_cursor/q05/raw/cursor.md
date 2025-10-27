# Query 5: The user wants the assistant to help fix and format the '基本问题.md' file in proper Markdown style.

## Context from Previous Query

**User**
最初的input是cursor chat吗？如果是，你解释了cursor chat一步一步的结果了吗？@基本问题.md 

---

**Assistant**
让我仔细检查一下 `基本问题.md` 文档，看看是否完整解释了从 Cursor chat 到最终结果的完整流程。


你说得对！`基本问题.md` 文档确实**没有完整解释**从 Cursor chat 到最终结果的**一步一步**的详细流程。让我补充这个缺失的部分：

## 🔍 问题分析

`基本问题.md` 目前的问题：
1. **缺少具体的 Cursor chat 示例** - 没有展示真实的聊天内容
2. **缺少 step-by-step 转换过程** - 从聊天文本到 events.jsonl 的具体转换步骤
3. **缺少中间产物示例** - 没有展示每个中间步骤的具体输出

让我更新这个文档，添加完整的 step-by-step 流程：


```markdown
# 基本问题（Q1/Q2/Q3 的输入与输出，以及数据流）

> 本文回答两个问题：  
> 1) “这个输入和输出长什么样？”—...

---

## Current Query-Answer

**User**
@基本问题.md 我改了 请markdown 格式

---

**Assistant**
我来帮你修正 `基本问题.md` 的 Markdown 格式。让我检查并修复格式问题：


现在我来修正 Markdown 格式问题：


```markdown
# 基本问题（Q1/Q2/Q3 的输入与输出 + 全链路数据流）

> **结论先说**：
> - 最初的输入：建议走"Cursor chat（导出的 markdown）"。Diff 只是可选兜底。
> - 之前的说明里有一点散。我把从 Cursor chat → 事件 → 守卫 → 模式卡 → 动态视图 → 最终产物的整条流程，重新写成一份可直接放仓库的《基本问题.md》完整版，见下。

---

## 回答两个问题

1. **"这个输入和输出长什么样？"**——分别针对 Q1/Q2/Q3；
2. **"数据如何流动？"**——从 raw data（Cursor chat） → Q1 输入/输出 → Q2 输入/输出 → Q3 输入/输出 → 最终产物。

---

## 0) 原始输入（强烈推荐 Chat-only）

- **Primary（推荐）**：`raw/cursor.md`（Cursor 导出的对话 markdown）
- **Fallback（可选）**：`raw/patch.diff`（统一 diff）、`raw/term.log`（测试输出）

**Chat-only 优点**：带有 what/why/test 的上下文；无需强制 RUNLOG；对编辑器无侵入。  
当 LLM 提取置信度低时，再用 `git diff --name-only` 轻量兜底。

---

## 1) Q1｜执行监控 / 偏航守卫（Drift Detection）

### 1.1 输入

- `goal.json`（任务目标/白黑名单/检查点/阈值/权重）
- `events.jsonl`（由 chat2events 或 patch2events/term2events 生成）

### Chat → Events（核心判别规则）

- 出现"已修改/updated/changed/edited/created/removed"或给出具体代码块 → `tool=edit, phase=modify`（计分）
- 出现"计划/将/建议/propose/plan/will/can"但未给出实际修改 → `tool=plan, phase=modify`（不计分，仅留痕）
- 出现测试命令（pytest|npm test|go test 等） → `tool=shell, phase=test`（触发 TestGuard）
- 解析不到但对话强烈暗示有改动 → `confidence="low"`；可用 `git diff --name-only` 兜底补齐

### 示例（cursor.md 片段）
