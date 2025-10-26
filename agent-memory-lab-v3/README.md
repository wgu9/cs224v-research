# 智能编程代理的跨会话学习与执行监控（Q2/Q3/Q1 一体化）

## 🎯 一句话总结

用同一条"事件总线 + 目标图"的数据底座，同时实现：
- **Q2 跨会话学习**（模式卡复用）
- **Q3 动态抽象**（两档视图按人群路由）
- **Q1 执行监控**（偏航守卫与回滚）

### 核心能力
- **Q2｜Cross-Session Learning**：从过往会话沉淀"模式卡 Pattern Cards"，新任务自动检索与复用，不再每次从零开始
- **Q3｜Dynamic Abstraction**：同一张模式卡提供 terse（要点/不变量）与 guided（示例/坑点/测试）的两档视图，按用户画像 × 任务难度自动路由
- **Q1｜Execution Monitoring & Drift Guards**：在"复现→修改→测试→回归"四个检查点上，运行 Scope/Plan/Test/Evidence 守卫，计算 drift_score，超阈提醒/回滚，防止长任务跑题

---

## 🎯 Business Problem（商业痛点）

现代团队在使用 Cursor / Claude Code / Copilot 等智能编程代理时，主要时间消耗在：

### 1. 每次都从零开始（Q2）
上周刚解决过的类问题，这周仍需重新理解项目与探索路径 —— 经验无法沉淀与迁移，造成重复劳动。

### 2. 输出粒度不匹配（Q3）
初学者偏好步骤与示例，资深更需要策略与不变量。代理难以按"用户水平 × 任务难度"自动调节抽象层级，输出要么啰嗦、要么含糊。

### 3. 长任务易跑偏（Q1）
多步修复/重构中常发生"只要改文档，却去改依赖"等跑题行为，缺少目标-检查点-守卫的持续对齐与回滚能力。

**目标**：把编程代理从"一次性助手"，升级为"会成长、会复用、会自我约束"的合作者。

---

## 🧱 方案概览（Chat-only 主路径 + Diff 兜底）

- 数据底座：
  - 事件总线 `events.jsonl`（append-only）统一记录事实；
  - 目标图 `goal.json`（白/黑名单 + 检查点 + 阈值/权重）。
- 三能一体：同一份 `events.jsonl` 同时驱动 Q1（守卫）、Q2（抽卡复用）、Q3（个性化呈现）。
- Chat-first：优先从 `raw/cursor.md` 提取 plan/edit/test 事件；当置信度低或对话不完整，使用 `git diff --name-only` 轻量兜底；必要时可直接走 `patch.diff` + `term.log` 路径。

---

## 🚀 快速开始（Quick Start）

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Chat-only 一键端到端
python scripts/e2e_chat_only.py <run_id> [user]

# 或使用 Diff 兜底路径
python tools/patch2events.py data/runs/<run_id>
python tools/events2guards.py data/runs/<run_id>
```

运行完成后，在 `data/runs/<run_id>/` 下可见：
- `events.jsonl`（事件）
- `guards.jsonl`（守卫 + drift_score + action）
- `artifacts/reflection.txt`（反思素材）
- `artifacts/pattern.pc_*.json`（模式卡）
- `artifacts/view_preview.md`（按画像路由的回复文本）

---

## 🗂️ 仓库与数据结构

```
agent-memory-lab-v3/
├─ tools/
│  ├─ chat2events.py         # Chat-only：cursor.md → events.jsonl
│  ├─ events2guards.py       # 事件 → 守卫（drift_score + warn/rollback + fix_cmd）
│  ├─ patch2events.py        # 兜底：patch.diff → events.jsonl
│  └─ term2events.py         # 兜底：term.log → events.jsonl（test）
├─ agent/
│  ├─ reflexion.py           # 反思生成（生产接 LLM）
│  └─ extract_card.py        # 反思 → 模式卡（含 version/title/provenance）
├─ q2_memory/retrieve.py     # 模式卡检索（轻触发）
├─ q3_views/render.py        # 视图路由（terse/guided）与渲染
├─ scripts/
│  ├─ e2e_chat_only.py       # 一键 Chat-only 全链路
│  └─ e2e_cursor_doc_task.py # 一键 Diff 示例
└─ data/
   ├─ runs/<run_id>/raw/{cursor.md|patch.diff|term.log}
   ├─ runs/<run_id>/events.jsonl | guards.jsonl | artifacts/
   ├─ patterns/pc_*.json      # 全局模式卡库（跨会话复用）
   └─ profiles/<user>.json    # 用户画像（路由）
```

---

## 🛡️ Q1 执行监控（Drift Guards）

- 守卫：Scope / Plan / Test / Evidence；权重默认 `0.4/0.3/0.2/0.1`。
- 动作阈值（可在 `goal.json.thresholds` 覆盖）：
  - `drift < 0.5` → `ok`
  - `0.5 ≤ drift < 0.8` → `warn`
  - `drift ≥ 0.8` → `rollback`
- 计分对象：
  - `edit` 参与 Scope/Plan/Evidence；
  - `shell(test)` 参与 Test；
  - `plan` 永远不计分（仅留痕，`action=ok`）。
- 自动修复建议：当 `rollback` 且路径越界时输出 `auto_fixable=true` 与 `fix_cmd="git checkout -- <file>"`。

---

## 🧠 Q2 跨会话学习（Pattern Cards）

- 抽取对象：成功/高价值的 run；输入 `events.jsonl + guards.jsonl + goal.json (+ cursor.md)`。
- 模式卡字段（治理就绪）：
```
{
  "version": "1.0",
  "pattern_id": "pc_doc_only_change",
  "title": "文档/翻译类变更：只改白名单",
  "triggers": ["documentation-only","translate readme"],
  "steps": ["whitelist README.md/docs/**","forbid requirements.*","run doc_lang_check & whitelist_diff_check"],
  "invariants": ["only whitelisted files changed","language==target"],
  "anti_patterns": ["edit requirements without consent"],
  "eval_examples": ["doc_lang_check","whitelist_diff_check"],
  "views": {"terse": "...", "guided": "..."},
  "provenance": {"source_runs": ["r42","r60"], "created_by": "team", "created_at": "2025-10-25T10:00:00Z"}
}
```
- 复用：保存到 `data/patterns/`，新任务按 `objective`/触发词检索并注入。

---

## 🎛️ Q3 动态抽象（个性化回复，非 UI）

- 目标：针对不同用户/任务难度，输出不同抽象层级的文本回复（非前端）。
- 两档视图：
  - `terse`（专家速读）：规则 + 不变量，一屏读完；
  - `guided`（新手教学）：步骤、示例、坑点、必跑测试与例外流程。
- 路由规则（MVP）：
  - 若画像 `pref` 指定 → 直接用；
  - 否则 `self_report=novice` 或 `difficulty=high` 或 `hist_first_try_success<0.5` → `guided`；
  - 其他 → `terse`。
- 产物：`data/runs/<run_id>/artifacts/view_preview.md`，可直接作为系统提示或回复文本。

---

## 🔄 数据流（Chat → Events → Guards → Pattern → View）

1) `raw/cursor.md`（推荐）/ `patch.diff`（兜底）
2) `chat2events.py` / `patch2events.py` → `events.jsonl`
3) `events2guards.py` → `guards.jsonl`（drift_score + action + fix_cmd）
4) `extract_card.py` → `artifacts/pattern.pc_*.json`（并复制到 `data/patterns/`）
5) `retrieve.py`（按 objective/触发词检索）
6) `render.py`（按画像路由 terse/guided）→ `artifacts/view_preview.md`

---

## 🧪 评测与指标

- 本地指标：
  - Q1：偏航检出率、误报率、恢复时间；
  - Q2：模式复用率、首试成功率、回合数/用时；
  - Q3：视图匹配度（guided 下新手更稳）。
- SWE‑bench 对齐：生成 `data/eval/predictions.jsonl`，在装好官方 harness 的环境中运行评测。

---

## 📝 最小 SOP（Chat-only）

1) 导出 Cursor 对话为 `data/runs/<run_id>/raw/cursor.md`
2) 编写 `data/runs/<run_id>/goal.json`（白/黑名单、检查点、阈值、必跑测试）
3) 执行：
```bash
python tools/chat2events.py data/runs/<run_id>
python tools/events2guards.py data/runs/<run_id>
# 通过后抽卡并复用
python scripts/e2e_chat_only.py <run_id> [user]
```

小抄（判别词）：
- edit：updated / changed / edited / created / removed / 已修改 / 已翻译 / “代码块 + 我已修改/翻译 …”
- plan：建议 / 将 / 计划 / propose / plan / will / can / 可以考虑 …
- test：pytest / npm test / go test / mvn test / vitest …

---

## 📎 附：Schema 摘要

- events.jsonl（并列并集）
  - edit：`{ run_id, step, phase:"modify", tool:"edit", where:"<path>:?", why?, confidence?, evidence? }`
  - plan：`{ run_id, step, phase:"modify", tool:"plan", why, confidence? }`
  - shell(test)：`{ run_id, step, phase:"test"|"regress", tool:"shell", cmd }`
- guards.jsonl：`{ run_id, step, scope_guard, plan_guard, test_guard, evidence_guard, drift_score, action, file?, auto_fixable?, fix_cmd? }`
- pattern：见上（含 `version/title/provenance`）
- profile：`{ user_id, self_report, hist_first_try_success, pref }`

——

若需更多案例（依赖修复、超时重试、日志降噪等），可补充对应的 `goal.json + events.jsonl` fixtures 并纳入评测。
