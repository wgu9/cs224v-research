# Q1 工作流最终总结 (Gemini Wrap-up)

本文档旨在清晰、简洁地总结当前 Q1 偏航检测（Context Drift Detection）的最终工作流、核心脚本、数据产物和关键概念。

---

## 最终工作流概览

我们已经将整个流程升级为一个**“端到端同步器”**。你只需要运行一个主控制器脚本，它就能自动完成从“预处理”到“分析”的全过程，并能智能跳过已完成的工作，甚至在遇到兼容性问题时进行“自愈”。

**数据流向示意图:**

```
原始 .md 对话文件 (在 spot-test/ 中)
         ↓
┌──────────────────────────────────┐
│ scripts/batch_process_with_check.py  │  ← 你唯一需要运行的命令
└──────────────────────────────────┘
         │
         ├─ (如果 session 不存在) ─→ 调用 [tools/process_long_conversation.py]
         │                              ↓
         │                      data/1_sessions/ (生成预处理结果)
         │
         └─ (如果 analysis 不存在) ─→ 调用 [tools/run_q1_batch.py]
                                        ↓
                                data/2_runs/ (生成最终分析报告)
```

---

## 核心脚本及其职责

| 脚本 (Script) | 职责 (Responsibility) |
| :--- | :--- |
| **`scripts/batch_process_with_check.py`** | **主控制器 / 端到端同步器**。遍历输入文件，智能决策是跳过、预处理还是分析。 |
| `tools/process_long_conversation.py` | **第 1 步：预处理器**。负责拆分长对话，并调用 LLM 生成 `goal.json`。 |
| `tools/run_q1_batch.py` | **第 2 步：批量分析器**。读取预处理好的 session，并对其中所有子任务运行 Q1 分析。 |
| `tools/chat2events.py` | **事件提取器**。将对话的自然语言解析为结构化的 `events.jsonl`。 |
| `tools/events2guards.py` | **偏航计算器**。Q1 核心，根据 `goal.json` 和 `events.jsonl` 计算出 `guards.jsonl`。 |

---

## 关键数据产物解读

| 路径 (Path) | 作用 | 来源 | 与主题关系 |
| :--- | :--- | :--- | :--- |
| **`data/1_sessions/`** | **预处理好的“食材库”** | `process_long_conversation.py` | **Q1, Q2, Q3 的长期数据资产** |
| `.../pairs/q.../goal.json` | 单个子任务的“规则” | LLM (在第 1 步) | **Q1 的核心输入** |
| `.../pairs/q.../chat.md` | 单个子任务的对话片段 | 脚本拆分 (在第 1 步) | Q1 的原始上下文 |
| **`data/2_runs/`** | **最终的“分析报告”** | `run_q1_batch.py` | **Q1 的最终输出** |
| `.../s_..._q.../events.jsonl` | 事实日志 (Agent 的具体操作) | `chat2events.py` (在第 2 步) | Q1 的分析依据，**Q2 的学习材料** |
| `.../s_..._q.../guards.jsonl` | **偏航分析结果** | `events2guards.py` (在第 2 步) | **Q1 的核心成果**，Q2 用它筛选成功案例 |
| `.../s_..._q.../summary.json` | 单个 Session 的分析总结 | `run_q1_batch.py` (在第 2 步) | Q1 的宏观统计 |

---

## 核心概念解析

*   **`goal.json` 的动态性**
    *   它不是一个全局配置文件，而是针对**每一个子任务**动态生成的**“规则契约”**。
    *   这使得 Q1 的偏航标准可以灵活适应不同类型的任务（如“修 Bug”和“加测试”的规则权重完全不同）。

*   **四个守卫的工作机制**
    *   `Scope Guard`: 检查文件修改是否“越界”（是否在 `allowed_paths` 内）。
    *   `Plan Guard`: 检查工具使用是否“按计划”（在正确的 `phase` 使用了允许的 `tool`）。
    *   `Test Guard`: 检查测试是否“充分”（是否运行了 `required_tests`）。
    *   `Evidence Guard`: 检查代码修改是否“有理有据”（是否附带了 `evidence`）。

*   **Drift 的分析层级**
    *   **Pair-Level (已实现)**: 我们当前实现的 Q1 分析，是针对单个子任务（query-answer pair）的“战术偏航”检测。
    *   **Session-Level (未来方向)**: 更高阶的“战略偏航”检测，用于判断 Agent 在整个长对话中的行为是否偏离了总体目标。这可以作为 Q1 的一个进阶功能来探索。

---

## 如何使用

现在，你只需要运行一个命令，即可同步所有 `spot-test` 目录下的分析：

```bash
python scripts/batch_process_with_check.py
```

脚本会自动处理所有必需的步骤。

---


---

## Next Steps (Moving to Q2 and Q3)

随着 Q1 的工作流已经稳固，我们成功地将原始对话转化为了高质量、结构化的“学习材料”。下一步就是利用这些材料，启动 Q2 和 Q3 的工作。

### 联系：Q1 的输出是 Q2 的输入

Q1 的核心产出——`data/2_runs/` 目录中的每一次运行记录——是 Q2 阶段进行模式学习的“养料”。

*   一个**成功的运行案例**（即 `guards.jsonl` 中 `drift_score` 很低的记录），其对应的**“任务卷宗”**（`goal.json` + `events.jsonl` + `guards.jsonl`）就构成了一个完美的“最佳实践”样本，可以被 LLM 用来学习。

### 分叉：从“评判”到“创造”

工作性质将发生根本性转变：

| 阶段 | 核心任务 | LLM 角色 |
| :--- | :--- | :--- |
| **Q1** | **评判 (Judgment)** | **产品经理** (在第 1 步生成 `goal.json` 定义规则) |
| **Q2/Q3** | **创造 (Creation)** | **架构师/导师** (提炼模式、生成个性化教学) |

### 下一步具体做什么

1.  **(Q2) 实现“模式提取” Agent (`agent/extract_pattern.py`)**
    *   **输入**: 一个成功的 `run` 目录路径（来自 `data/2_runs/`）。
    *   **动作**:
        1.  读取该 `run` 的 `goal.json`, `events.jsonl`, `guards.jsonl`。
        2.  将这些信息组合成一个 prompt，喂给一个新的“反思型” LLM。
        3.  LLM 的任务是分析这次成功的执行过程，并**合成**一个通用的、可复用的 **`Pattern Card` JSON 对象**。
    *   **输出**: 一个新的 `pc_*.json` 文件，存入 `data/patterns/` 目录。

2.  **(Q3) 实现“视图渲染器” (`q3_views/render.py`)**
    *   **输入**: 一张 `Pattern Card` (`pc_*.json`) 和一个用户画像 (`data/profiles/user.json`)。
    *   **动作**:
        1.  根据用户画像的水平（如 `novice`）和任务难度，从 `Pattern Card` 的 `views` 字段中选择 `terse`（简洁）或 `guided`（引导）视图。
        2.  （可选）可以让 LLM 将选中的视图内容，根据用户偏好，以更友好的语气重新渲染。
    *   **输出**: 一个 `view_preview.md` 文件，作为最终给用户的、高度个性化的回复。
