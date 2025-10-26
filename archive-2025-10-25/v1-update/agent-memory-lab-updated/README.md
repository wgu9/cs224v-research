# Agent Memory Lab - Updated

已根据我们最新讨论，给你更新后的完整仓库（含端到端示例、Cursor 导出与 git diff 的采集、事件与守卫、模式卡抽取、两档视图渲染），可直接下载：

⬇️ 下载 agent-memory-lab-updated.zip

下面是"更新点总览 → 数据怎么来 → 如何落到 Q1/Q2/Q3 → 端到端示例步骤"。仓库里的 README.md、docs/、scripts/ 也都同步好了。

⸻

## ✅ 这次更新了什么（和我们讨论一致）

1. 统一底座：事件总线 events.jsonl + 目标图 goal.json（4 检查点）。
2. 原始证据层：支持把 Cursor 导出（cursor.md）、git diff（patch.diff）、测试日志（term.log）一起落盘到 data/runs/<run_id>/raw/。
3. 规范化工具（已内置）：
   - tools/patch2events.py：把 patch.diff 解析成 edit 事件；
   - tools/term2events.py：把 term.log 解析成 shell/test 事件；
   - tools/events2guards.py：计算 Scope/Plan/Test/Evidence 守卫与 drift_score（≥0.5 即判定跑题）。
4. Q2/Q3：
   - agent/reflexion.py + agent/extract_card.py：从 events + cursor.md 生成 reflection，结构化为 模式卡（pattern）；
   - q2_memory/retrieve.py：按 objective 检索并注入模式；
   - q3_views/render.py：基于 data/profiles/<user>.json 路由两档视图（terse/guided）。
5. 端到端示例：scripts/e2e_cursor_doc_task.py 复现"只翻译 README 却误改 requirements.txt"的跑题→提醒→抽卡→下次复用→分层呈现 全流程。
6. 文档：README.md、docs/design.md、docs/data_schema.md、docs/eval_protocol.md 已按新方案更新。

⸻

## 📦 仓库结构（关键目录）

```
agent-memory-lab-updated/
├─ README.md
├─ docs/
│  ├─ design.md            # 统一流水线设计（Foundation→Q1/Q2/Q3）
│  ├─ data_schema.md       # goal/events/guards/pattern/profile 格式
│  └─ eval_protocol.md     # SWE‑bench + 你的指标 + 消融
├─ tools/
│  ├─ patch2events.py      # patch.diff → edit 事件
│  ├─ term2events.py       # term.log → shell/test 事件
│  └─ events2guards.py     # events + goal → 守卫与 drift_score
├─ agent/
│  ├─ reflexion.py         # （生产接 LLM）生成反思
│  └─ extract_card.py      # 反思 → 模式卡（pattern card）
├─ q2_memory/retrieve.py   # 模式检索与打分
├─ q3_views/render.py      # 两档视图路由与渲染
├─ scripts/
│  └─ e2e_cursor_doc_task.py  # 端到端示例（r42）
├─ data/
│  ├─ runs/2025-10-25_r42_jw/     # 本次示例 run（已内置原始证据与目标）
│  │  ├─ raw/
│  │  │  ├─ base_commit.txt
│  │  │  ├─ patch.diff            # 改了 README.md 且误改 requirements.txt
│  │  │  ├─ term.log
│  │  │  └─ cursor.md
│  │  └─ goal.json                # 白名单: 只许 README.md/docs/**
│  ├─ patterns/                   # 团队模式库（脚本会自动复制进来）
│  ├─ profiles/jeremy.json        # Q3: 用户画像（terse/guided 路由）
│  └─ eval/predictions.sample.jsonl
└─ requirements.txt
```

⸻

## 🧪 端到端示例（一步跑通）

场景：只翻译 README.md，但代理同时修改了 requirements.txt → 典型跑题；我们检测→提醒→抽成**"文档白名单模式"**→下次自动触发，并按用户水平渲染两档解释。

### 1. 安装与运行

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/e2e_cursor_doc_task.py
```

### 2. 你将看到
- tools/patch2events.py 把 raw/patch.diff 解析为 edit 事件；
- tools/term2events.py 追加 pytest 相关事件；
- tools/events2guards.py 计算守卫，对 requirements.txt 给出高 drift_score（warn）；
- agent/extract_card.py 生成 pattern.pc_doc_only_change.json（同时复制到 data/patterns 用于复用）；
- q2_memory/retrieve.py 基于新目标检索该模式；
- q3_views/render.py 依据 profiles/jeremy.json 选择 terse 或 guided，输出到 artifacts/view_preview.md。

### 3. 文件产物（关键）
- data/runs/2025-10-25_r42_jw/events.jsonl（规范化事件）
- data/runs/2025-10-25_r42_jw/guards.jsonl（requirements.txt: drift_score ≥ 0.5 → warn）
- data/runs/2025-10-25_r42_jw/artifacts/pattern.pc_doc_only_change.json
- data/patterns/pattern.pc_doc_only_change.json（全局库）
- data/runs/2025-10-25_r42_jw/artifacts/view_preview.md（两档视图）

⸻

## 🔍 数据如何对应 Q1/Q2/Q3（同一份事件数据，不是三摊事）

### Q1（跑题检测）

依据 goal.json 的 allowed_paths 与 检查点，对 events.jsonl 的每步计算：
- ScopeGuard：本例对 requirements.txt = 1.0（不在白名单）
- PlanGuard：modify 阶段编辑了不允许文件 = 1.0
- EvidenceGuard：无证据 = 0.5
- drift_score = 0.4*1 + 0.3*1 + 0.2*0 + 0.1*0.5 = 0.85 → warn

输出到 guards.jsonl，可用于 UI 提醒/回滚与团队仪表盘统计。

### Q2（跨会话学习）
用 events + cursor.md 生成 reflection.txt → 结构化为 模式卡 pc_doc_only_change：
触发（documentation-only）、步骤（白名单/禁改依赖/文档检测）、不变量 与 反例。
以后任意"文档/翻译"目标开场即 检索触发 该卡，先天预防跑题。

### Q3（动态抽象）

同一张卡 两档视图：
- terse（专家）：规则+不变量一屏读完；
- guided（新手）：白名单配置、语言检测、例外流程，附示例与坑。

依据 profiles/<user>.json 路由（pref/hist_first_try_success）自动选择。

⸻

## 🧪 评测怎么做（对齐 SWE‑bench + 你的指标）

### SWE‑bench（官方）

把最终补丁写入 data/eval/predictions.jsonl，在装好 SWE-bench 的机器上运行 swebench.harness.run_evaluation，得到 %Resolved。
### 你的指标（仓库自统计）

- Q1：偏航检出率、偏航恢复时间；
- Q2：模式复用率、首试成功率 提升、回合数/用时 下降；
- Q3：视图匹配度（guided 下新手更稳）。
- 消融：baseline → +pattern → +pattern+views → +pattern+views+guards，做成对照曲线。

（说明在 docs/eval_protocol.md，与我们前面讨论一致。）

⸻

## 📝 你日常只需要做的 3 步（最简 SOP）

### 1. 落证据（不必 commit）
- git rev-parse HEAD > raw/base_commit.txt
- git diff -U0 > raw/patch.diff
- pytest … | tee raw/term.log（可选）
- Cursor 导出放 raw/cursor.md（可选，用作"为什么"）

### 2. 写/更新 goal.json（白名单、检查点、必跑测试）

### 3. 跑小脚本

```bash
python tools/patch2events.py data/runs/<run_id>
python tools/term2events.py  data/runs/<run_id>   # 可选
python tools/events2guards.py data/runs/<run_id>
```

通过就 抽卡（agent/extract_card.py），卡会复制进 data/patterns/，下次自动复用。

⸻

需要我再把 SWE‑bench 的单题评测脚本（读取 predictions.jsonl 并调用官方 harness）补一个占位模板吗？或把 UI 小面板（偏航提醒+回滚按钮+两档视图切换）加个更完整的 demo？我可以在这个 updated 仓库里继续扩建。


# Agent Memory Lab — Unified Q2/Q3/Q1 (Updated)

> **One pipeline, three capabilities** powered by the **same data**:
> - **Q2 – Cross‑session learning**: extract reusable **Pattern Cards** from past runs and auto‑trigger them on new tasks.
> - **Q3 – Dynamic abstraction**: the same pattern rendered in **two views** (terse/guided), routed by **user profile + task difficulty**.
> - **Q1 – Goal/Checkpoint/Drift guards**: Scope/Plan/Test/Evidence guards compute a `drift_score` and warn/rollback when off‑track.
>
> **Foundation for all three** = **Event Bus** (append‑only `events.jsonl`) + **Goal Graph** (4 checkpoints: reproduce → modify → test → regress).

This repo includes:
- A **team‑friendly data lake layout** (`data/runs/<run_id>/raw|events|guards|artifacts`) to ingest **Cursor/Claude/Aider exports**, `git diff`, and test logs.
- Minimal **tools** to transform raw evidence → canonical **events** and **guards**, then learn a **Pattern Card** and **render two views**.
- An **end‑to‑end example** (`scripts/e2e_cursor_doc_task.py`) based on the **README translation** scenario with an **off‑scope `requirements.txt` edit** (typical drift).

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# End-to-end demo on provided run r42 (no external deps)
python scripts/e2e_cursor_doc_task.py
# → writes events.jsonl, guards.jsonl (drift detected), reflection & pattern,
#   copies pattern to data/patterns/, retrieves & renders two abstraction views.
```

## Data Lake Layout

```
data/
└─ runs/<run_id>/
   ├─ raw/                 # **Raw Evidence** (append-only)
   │  ├─ base_commit.txt   # `git rev-parse HEAD` (or any baseline id)
   │  ├─ patch.diff        # `git diff -U0` (no need to commit)
   │  ├─ term.log          # test/command log (optional)
   │  └─ cursor.md         # exported chat (optional; used for reflections)
   ├─ goal.json            # **Goal Graph config** (allowed_paths, checkpoints)
   ├─ events.jsonl         # **Canonical facts** (what happened)
   ├─ guards.jsonl         # Q1 outputs (scope/plan/test/evidence + drift_score)
   └─ artifacts/           # Q2/Q3 artifacts
      ├─ reflection.txt    # verbal reflection from this run (LLM in prod)
      ├─ pattern.pc_*.json # pattern card(s) extracted from this run
      └─ view_preview.md   # view render example (terse/guided)
```

**Global stores**:
- `data/patterns/pc_*.json` — **team pattern library** (cross‑run reuse).
- `data/profiles/<user>.json` — user profile for Q3 routing.
- `data/eval/` — SWE-bench `predictions.jsonl` and eval outputs (when you integrate).

## What to ingest from tools like Cursor/Claude/Aider?

- **Facts**: `git diff -U0` (what changed) + optional test logs (what passed/failed).
- **Reasoning**: exported chat markdown (why), used for Q2 reflection/Q3 narratives.
- You **do not** need to commit every time. `base_commit.txt + patch.diff` already
  matches the SWE-bench idea of “apply a unified diff to a known base”.

## End-to-End Example (r42)

We include a realistic doc-only task:

> **Objective**: *Translate README.md to Chinese (doc-only)*.  
> **Drift**: agent also edited `requirements.txt` (unrelated).

Run:
```bash
python scripts/e2e_cursor_doc_task.py
```

You will see:
- `events.jsonl` created from `raw/patch.diff` (+ optional shell/test events).
- `guards.jsonl` with a **high drift_score** for `requirements.txt` (Scope+Plan).
- `artifacts/reflection.txt` and `artifacts/pattern.pc_doc_only_change.json`.
- Pattern copied to `data/patterns/` and **retrieved** for a *new* run, then
  **rendered** as **terse** (expert) and **guided** (novice) views.

## Mapping to Q1/Q2/Q3

- **Q1 (Drift)** — compute guards from `events.jsonl + goal.json`:
  - **ScopeGuard**: file edits outside `allowed_paths` → 1.0
  - **PlanGuard**: action not allowed at current checkpoint **or** editing a file disallowed at this phase → 1.0
  - **TestGuard**: required tests skipped/new failures ignored → 1.0
  - **EvidenceGuard**: modify phase lacking relevant evidence → ~0.3–0.7
  - `drift_score = 0.4*scope + 0.3*plan + 0.2*test + 0.1*evidence`

- **Q2 (Patterns)** — from events (+ cursor.md) → reflection → **Pattern Card**:
  ```json
  {
    "pattern_id":"pc_doc_only_change",
    "triggers":["documentation-only","translate readme"],
    "steps":["whitelist README.md/docs/**","forbid requirements.*",
             "doc_lang_check & whitelist_diff_check"],
    "invariants":["only whitelisted files changed","language==target"],
    "anti_patterns":["edit requirements without consent"],
    "eval_examples":["doc_lang_check","whitelist_diff_check"],
    "views":{"terse":"rule+invariants","guided":"how to set whitelist & checks"}
  }
  ```

- **Q3 (Views)** — same pattern, **two abstraction levels**:
  - **terse** (experts): short rules and invariants.
  - **guided** (novices): step-by-step, examples, pitfalls, when to request exceptions.
  - Routing by `data/profiles/<user>.json` (self-report + historical first‑try success).

## SWE-bench Integration (optional, later)

- Construct `data/eval/predictions.jsonl` with `{"instance_id", "model_patch"}` lines.
- Run the official harness (`swebench.harness.run_evaluation`) locally or in cloud.
- Our local **base_commit + patch.diff** schema aligns with SWE-bench’s evaluator.

See `docs/design.md`, `docs/data_schema.md`, and `docs/eval_protocol.md` for details.
