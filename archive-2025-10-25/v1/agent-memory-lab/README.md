# Agent Memory Lab (Q2/Q3/Q1 统一演示)

> **一条流水线，三种能力**：跨会话学习（**Q2**）、动态抽象（**Q3**）、目标/检查点/漂移守卫（**Q1**），全部基于单一的**事件总线**和**目标图**驱动。

## 项目概述（Foundation-first 架构）

**核心原则**：一套数据驱动三件事

- **共同底座（Foundation）**：事件总线 + 目标图（4个检查点：复现 → 修改 → 测试 → 回归）
- **事件**（`events.jsonl`）：记录每个动作的 where/what/why/evidence
- **检查点**：每步有允许动作/验收条件

**三件事放在一条管道里**：
1. **Q2 跨会话学习**：事件 → 反思（LLM）→ 模式卡（triggers/steps/invariants/anti-patterns/eval）→ 检索与注入
2. **Q3 动态抽象**：同一张模式卡，两档视图（terse/guided），按 `profiles.json` 路由
3. **Q1 执行监控**：在相同事件流上跑 4 类守卫（scope/plan/test/evidence）→ drift_score 超阈提醒/回滚

**里程碑**：
- **第1周**：打通事件总线+四检查点、沉淀 3 张模式卡
- **第2周**：上检索/注入+最小守卫；SWE-bench Lite 上做 1 次 A/B
- **第3周**：上动态抽象（两档视图），做消融（–retrieval/–views/–guards）
- **第4周**：扩模式卡与实例，完善报告与 Demo

## 数据长什么样（都在仓库 docs/data_schema.md + data/examples/）

| 数据类型 | 作用 | 示例文件 |
|----------|------|----------|
| `events.jsonl` | 基础事件流水，供 Q1/Q2/Q3 共用 | `data/examples/events/events.r1.jsonl` |
| `guards.jsonl` | 跑题信号（scope/plan/test/evidence）与 drift_score | `data/examples/guards/guards.r1.jsonl` |
| `patterns/*.json` | 模式卡（Q2 复用；Q3 分层展示） | `data/examples/patterns/pc_delimited_tail.json` |
| `profiles.json` | 用户画像（Q3 路由） | `data/examples/profiles.json` |
| `predictions.jsonl` | SWE-bench 官方评测输入（补丁） | `data/examples/predictions.sample.jsonl` |

**来源**：
- **SWE-bench**（网上拿）：给真实任务与统一打分（打 patch → 跑测试 → 结果）
- **你最终要把你的补丁写入 predictions.jsonl，用官方 run_evaluation 打分**
- **我们必须自己生成**：
  - 过程数据（events/guards）→ 这是 Q1/Q2/Q3 的共同底座
  - 反思与模式卡（LLM + 模板抽取）→ Q2/Q3
  - 画像（profiles）→ Q3

## SWE-bench 能做什么？我们还要自己做什么？

**SWE-bench 提供**：
- 真实任务和统一打分（patch → test → results）
- 你提交 patches 在 `predictions.jsonl` 格式给官方 `run_evaluation` 打分

**我们必须自己构建**：
- **过程数据**（events/guards）→ Q1/Q2/Q3 的 Foundation
- **反思与模式卡**（LLM + 模板抽取）→ Q2/Q3
- **画像** → Q3

**端到端工作流**：
1. 从 SWE-bench 取单个 `instance_id`
2. 在该工作区内跑你的代理（带事件记录和守卫）
3. 产反思 → 抽模式卡
4. 再在同实例或相似实例复用
5. 把最终补丁交回 SWE-bench 评测

## 快速开始（本地 Demo - 不需要联网）

```bash
# 1) 创建并激活虚拟环境
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) 跑一遍"有日志的解题过程"，并产出守卫/模式卡/两档视图
python scripts/run_demo.py
# 输出包括：events/guards、pattern.json、检索得分、注入后的提示、选择的视图

# 3) 生成 SWE-bench predictions 示例文件（占位 diff）
python eval/make_predictions.py
# 若你的代理产出了真实 patch，把它覆盖写入 data/examples/predictions.sample.jsonl

# 4) （可选）在装好 SWE-bench 的机器上执行官方评测命令
# bash eval/run_swebench.sh
```

## 三件事如何在同一套数据上体现

**Q1（跑题）**：
- 守卫对 `events.jsonl` 的每步进行判分（scope/plan/test/evidence）→ `drift_score`
- 超阈提醒与软回滚；偏航恢复时间可从守卫触发与下一次通过 checkpoint 的时间差统计

**Q2（复用）**：
- 从同一 run 的事件产反思 → 抽模式卡
- 在下一次 run（同实例或相似实例）检索/注入该卡
- 指标：首试成功率↑、回合数↓、模式复用率

**Q3（分层）**：
- 同一张模式卡提供 terse/guided 两档
- 由 `profiles.json`（自报水平+历史成功率）路由
- 指标：两档视图下不降成功率或新手视图更稳

## 代码结构（已生成，见仓库）

```
agent-memory-lab/
├─ README.md                # 总览 + 快速开始 + 端到端说明
├─ requirements.txt
├─ docs/
│  ├─ design.md             # Q1/Q2/Q3 设计与数据流
│  ├─ data_schema.md        # 事件/守卫/模式卡/画像/预测格式
│  └─ eval_protocol.md      # 评测与消融方案
├─ data/examples/           # 可直接看的样例数据（用于 Demo）
│  ├─ events/events.r1.jsonl
│  ├─ guards/guards.r1.jsonl
│  ├─ patterns/pc_delimited_tail.json
│  ├─ profiles.json
│  └─ predictions.sample.jsonl
├─ agent/                   # 你的代理最小骨架
│  ├─ loop.py               # 模拟一次 run，写 events/guards（Foundation+Q1）
│  ├─ reflexion.py          # 反思（生产用需接 LLM API；本仓库为 stub）
│  └─ extract_card.py       # 反思→模式卡（Q2）
├─ q1_guard/                # 跑题守卫与 drift 评分
│  ├─ scope.py   ├─ plan.py ├─ test.py ├─ evidence.py └─ drift_score.py
├─ q2_memory/
│  ├─ retrieve.py           # 模式检索（触发词+简易重排）（Q2）
│  └─ inject.py             # 把模式提示注入计划/提示（Q2）
├─ q3_views/
│  └─ render.py             # 两档视图路由与渲染（Q3）
├─ eval/
│  ├─ make_predictions.py   # 生成 predictions.jsonl 模板（替换为你的补丁）
│  └─ run_swebench.sh       # 调官方评测命令（本地装好 SWE-bench 后可用）
├─ ui/
│  ├─ panel.html            # 极简"模式面板"示意（要点/详解切换）
│  └─ assets/style.css
└─ scripts/
   ├─ bootstrap.sh          # 下载加速/缓存设置
   └─ run_demo.py           # 一键跑通：events→pattern→retrieve→view
```

## 数据来源说明

| 产物 | 来源 |
|------|------|
| SWE-bench 实例元数据/仓库/测试 | 通过 SWE-bench/HuggingFace 从**互联网**获取 |
| `predictions.jsonl` | **你/你的代理**产出（可选使用 LLM APIs 提出补丁） |
| `events.jsonl`, `guards.jsonl` | **你**本地记录（Foundation；供 Q1/Q2/Q3 使用） |
| `reflections` → `pattern.json` | **LLM API**（反思）+ **你**（提取/结构化） |
| `profiles.json` | **你**（自报 + 简单统计） |

## FAQ

**Q: SWE-bench 很慢怎么办？**
- 先用 streaming/slice 只取 1 条实例（你本地环境中做），或直接通过 `--instance_ids` 让评测器内部取数据
- 本仓库 Demo 不依赖网络，先把 Q1/Q2/Q3 的流水线跑通，再接入 SWE-bench 正式评测

**Q: 如何集成真实的 LLM APIs？**
- `agent/reflexion.py` 目前使用 stubs 进行反思生成
- 你可以用真实的 LLM API 调用（OpenAI/Anthropic/等）替换 stub
- 见 `docs/design.md` 了解集成模式和 `.env` 配置示例

**Q: 可以不使用 SWE-bench 运行吗？**
- 可以！Demo 使用玩具场景在本地产生 events/guards/patterns
- 对于 SWE-bench 评测，在你的机器上使用官方 harness（见 `docs/eval_protocol.md`）

## LLM API 集成

要集成真实的 LLM APIs 进行反思生成：

1. **设置环境变量**：
```bash
# 创建 .env 文件
echo "OPENAI_API_KEY=your_key_here" > .env
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

2. **修改 `agent/reflexion.py`**：
```python
# 用真实 API 调用替换 stub
def make_reflection(events_file):
    # 从文件加载事件
    events = load_events(events_file)
    
    # 调用 LLM API（OpenAI/Anthropic/等）
    reflection = call_llm_api(events)
    
    return reflection
```

3. **在 stub 和真实 API 之间切换**：
- 使用 `USE_STUB=True` 在环境中进行本地测试
- 使用 `USE_STUB=False` 在生产环境中使用真实 LLM APIs

## 路线图

- **第1周**：Foundation（事件总线 + 4个检查点）& 3张高质量模式卡
- **第2周**：检索 + 轻量守卫 + 在5-10个 SWE-bench Lite 实例上做1次A/B
- **第3周**：动态抽象路由；消融研究（–retrieval/–views/–guards）
- **第4周**：扩展模式；仪表板；论文风格报告