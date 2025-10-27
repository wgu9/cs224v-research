# Query 1: The user wants to know if their proposed changes to README (v3).md and plan (V3).md are acceptable and seeks feedback and direct revision suggestions.

**User**
@README (v3).md @plan (V3).md  需要改，这么改可以吗？```
结论先说：你的文档方向正确、逻辑清晰，但有几处需要“与当前实现对齐”的关键更新，主要集中在：（1）引入 Chat‑only 采集管线与 planned/applied 区分，（2）事件 schema 示例修正，（3）脚本/工具命名更新，（4）事实来源表述微调，（5）Q1 对 plan 事件“不计分”的策略写清楚。下面我给出 “改什么、为什么、怎么改（可直接粘贴）”。

⸻

一、需要修改的要点（高优先级）
	1.	补充“Chat‑only 采集管线”并写清 planned vs applied

	•	现在文档默认以 patch.diff 为主；而 v3 已支持“只用 Cursor 导出 chat（无需 git/diff）”。
	•	影响：目录结构/最小脚本/FAQ/示例都要提到 Chat‑only 与 Diff 两条等价路径；且 仅对 tool=edit（applied）计分，tool=plan（planned）不计分。

	2.	修正 events.jsonl 的示例 schema

	•	你文档里出现了 where:"README.md:?" 这种字符串写法；实际实现是：

"where": { "path": "README.md" }


	•	请把所有示例改为 对象结构，以免读者按错了格式。

	3.	工具/脚本命名与现状对齐

	•	文档里还提到 scripts/e2e_cursor_doc_task.py、agent/reflexion.py 等老名字。
	•	现有 v3：
	•	tools/chat2events.py（Chat-only 提取器）
	•	tools/events2guards.py（守卫）
	•	scripts/e2e_chat_only.py（一键 Chat-only）
	•	Diff 线路保留：tools/patch2events.py、tools/term2events.py、scripts/e2e_one.py

	4.	“事实来源”表述要更贴近 v3

	•	你的 FAQ 里写“Cursor 导出仅作 why/反思，‘改了什么/是否通过’以 diff/测试日志为准”。
	•	建议改为：Chat‑only 模式下，当 chat 明确出现“已修改/显示代码片段/测试命令”时，可作为事实来源；若只有“计划修改”，标记为 tool=plan，不计分；当置信度低或空缺时，可选用轻量 git diff --name-only 兜底。

	5.	Q1 对 plan 事件不计分要写进正文

	•	你在实现里已经这样做了，但正文未强调。把“仅 tool=edit 进入 Scope/Plan/Evidence 守卫；plan 恒 action=ok（留痕不计分）”写成规则，避免误用。

⸻

二、可直接粘贴的修订段落

2.1 在“统一方案”后新增一节：两条采集路径（Chat‑only 与 Diff）

（插在 “共同底座：事件总线＋目标图” 之后）

### 采集与规范化：两条等价路径

我们支持两条并行但等价的数据采集路径：

1) **Chat‑only 路线（推荐）**
   - 原始输入：`raw/cursor.md`（Cursor 导出聊天，无需 git/diff）
   - 工具：`tools/chat2events.py`
   - 产物：`events.jsonl`（将自然对话提取为事件）
     - **已实施修改** → `tool=edit, phase=modify`（进入 Q1 计分）
     - **计划修改** → `tool=plan, phase=modify`（仅留痕，**不计分**）
     - **测试执行** → `tool=shell, phase=test`（触发 TestGuard）
   - 当提取结果置信度低或空缺时，可选启用轻量 `git diff --name-only` 作**兜底校验**。

2) **Diff 路线**
   - 原始输入：`raw/patch.diff`（统一 diff）和可选 `raw/term.log`
   - 工具：`tools/patch2events.py`、`tools/term2events.py`
   - 产物：`events.jsonl`（每个文件 1 条 `tool=edit` 事件；`term.log` 生成测试事件）

**两条路线后续完全一致**：`events.jsonl` + `goal.json` → `tools/events2guards.py` → `guards.jsonl`。


⸻

2.2 更新“目录结构（团队数据湖）”

（把 Chat‑only 工具与脚本补上，并保留 Diff 线路）

tools/
  chat2events.py                # ★ Chat-only：raw/cursor.md → events.jsonl（planned/applied＋置信度）
  events2guards.py              # 四守卫（仅 edit 计分；plan 恒 ok）
  patch2events.py               # Diff 路线：raw/patch.diff → events.jsonl
  term2events.py                # 解析 raw/term.log → 测试事件
scripts/
  e2e_chat_only.py              # 一键：chat → events → guards
  e2e_one.py                    # Diff 路线单 run 演示


⸻

2.3 修正 events.jsonl 示例（对象结构 + plan/edit 区分）

（替换你“数据格式（关键文件）/events.jsonl”片段）

{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit",
 "where":{"path":"README.md"},"what":{"diff":"(omitted)"},"why":"from patch.diff","evidence":{}}

{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit",
 "where":{"path":"requirements.txt"},"what":{"diff":"(omitted)"},"why":"(none)","evidence":{}}

{"id":"e1001","run_id":"r42","step":1001,"phase":"test","tool":"shell",
 "cmd":"pytest -k doc_lang_check"}

Chat‑only 下若仅有“计划修改”，则为：

{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan",
 "where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}

说明：tool=plan 不计分，仅留痕；只有 tool=edit 会进入 Q1 守卫判分。

⸻

2.4 “最小可用脚本（MVP）”段落替换

（给出 Chat‑only 与 Diff 两套最小命令）

### Chat‑only（无需 git/diff）
```bash
# 准备
# 1) 导出 Cursor 对话到 data/runs/<run_id>/raw/cursor.md
# 2) 写 data/runs/<run_id>/goal.json（白/黑名单、必跑测试）

python tools/chat2events.py data/runs/<run_id>   # 生成 events.jsonl（plan/edit/test）
python tools/events2guards.py data/runs/<run_id> # 生成 guards.jsonl（仅 edit 计分）

# 或一键：
python scripts/e2e_chat_only.py <run_id>

Diff 路线

python tools/patch2events.py data/runs/<run_id>
python tools/term2events.py  data/runs/<run_id>   # 若有 term.log
python tools/events2guards.py data/runs/<run_id>

---

### 2.5 FAQ 条目修改（“Cursor 导出能当事实来源吗？”）
（替换你的原回答）

```markdown
### Cursor 导出能当“事实来源”吗？
**可以**，在 Chat‑only 模式下满足以下任一条件即可视为“已实施修改（edit）”的证据：
- 明确表述“已修改/updated/changed/edited/已应用”等；
- 展示具体代码片段/patch；
- 关联出现并通过了对应测试命令。

若仅出现“计划修改/建议/可以/将要”等，则标记为 `tool=plan`（不计分，留痕）。  
当提取结果置信度低或空缺时，可**可选**调用 `git diff --name-only` 做兜底校验。


⸻

2.6 在 Q1 规则里显式写入“plan 忽略策略”

（加在“Q1｜执行监控/偏航守卫”小节末尾）

> **判分策略（重要）**  
> 仅对 `tool=edit` 的事件计算 `Scope/Plan/Evidence`；`tool=plan` 恒 `action=ok`（不计分）。  
> 测试事件（`tool=shell, phase=test`）触发 `TestGuard`；`override.acknowledged=true` 会将违规降级为轻度（避免 warn/rollback）。


⸻

三、次要但建议优化的地方
	•	示例一致性：你在前文主推 Cursor/Claude/Aider 多源聊天，但端到端示例只写了 patch.diff。建议补一个 Chat‑only 示例片段（你可直接取我在 v3 包里 data/runs/r60/raw/cursor.md 的 RUNLOG 示例），或用自然对话 + 启发式提取的例子，让读者明白“无需 git 也能跑通 Q1”。
	•	脚本清单：文末的“最小可用脚本（MVP）”里列了 agent/reflexion.py / agent/extract_card.py / q2_memory/retrieve.py / q3_views/render.py 等占位名，而 v3 还未提供这些文件。
	•	建议将它们移动到“后续工作/占位”小节或删掉，避免读者以为仓库里已经有。
	•	权重/阈值：你在正文固定 0.4/0.3/0.2/0.1 与 0.5/0.8，与实现一致，但可以在 goal.json 示例中显式演示可覆盖（v3 已支持 weights / thresholds 字段）。

⸻

四、给你一段可替换的“端到端（Chat‑only）示例”（可插入在现有 Diff 示例之后）

## 🧪 端到端示例（Chat‑only：只用 Cursor 导出）

**目标**：只把 README.md 翻译成中文（doc‑only）  
**实际**：Cursor 在建议里提到“将来可把 beautifulsoup4 加到 requirements.txt”，但并未真正修改 → 该部分记为 `plan`，不计分。

### 第 0 步｜原始输入
- `data/runs/r60/raw/cursor.md`（Cursor 导出聊天）
- `data/runs/r60/goal.json`（允许 `README.md`／`docs/**`，禁止 `requirements.txt`）

### 第 1 步｜提取事件
```bash
python tools/chat2events.py data/runs/r60

产生 events.jsonl（节选）：

{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan","where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}
{"id":"e2","run_id":"r60","step":2,"phase":"modify","tool":"edit","where":{"path":"README.md"},"why":"已将英文内容改为中文","confidence":"high"}
{"id":"t1001","run_id":"r60","step":1001,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}

第 2 步｜判航

python tools/events2guards.py data/runs/r60

产生 guards.jsonl：
	•	对 plan 事件 → action=ok（不计分）
	•	对 edit 事件（README.md）→ action=ok
	•	若有对 requirements.txt 的 edit，会触发 warn/rollback（越界）

要点：Chat‑only 同样能稳定识别“已实施 vs 计划”，避免把“建议/计划”误判为“跑题改动”。

---

## 五、总体评价

- **一致性**：你的叙事、优先级（Q1→Q2→Q3）、评测指标、四守卫设计都与我们达成的一致结论吻合。  
- **需修订**：把 **Chat‑only 与 Diff 两条路径**写成“等价首层概念”，把 **plan/edit 区分与 plan 不计分**写成“硬规则”，修正 **schema 示例** 与 **脚本命名**。  
- **风险缓释**：在 FAQ/规则里明确“低置信度→提示下一轮让 Cursor 明确‘已修改哪些文件’或可选 git 兜底”，可显著降低早期误报。

如果你愿意，我也可以把上面这些**修改过的段落直接合并成一版完整 README**发你（与 v3 压缩包一致的命名/脚本/示例）。
```

---

**Assistant**
我完全同意你的修改建议！这些更新确实能让文档与当前实现更好地对齐。让我按照你的建议来更新这两个文档。


```markdown
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
初学者偏好步骤与示例，资深更需要策略与不变量。代理**难以按"用户水平 × 任务难度"**自动调节抽象层级，输出要么啰嗦、要么含糊。

### 3. 长任务易跑偏（Q1）
多步修复/重构中常发生"只要改文档，却去改依赖"等跑题行为，缺少目标-检查点-守卫的持续对齐与回滚能力。

**目标**：把编程代理从"一次性助手"，升级为"会成长、会复用、会自我约束"的合作者。

---

## 🏗️ 统一方案（同一底座，三段合一）

### 共同底座：事件总线（Event Bus）＋ 目标图（Goal Graph）
- **事件总线**：按步骤记录 where/what/why/evidence（改了什么、为何改、证据/日志）
- **目标图**：四检查点 复现→修改→测试→回归，定义允许动作、白/黑名单与验收条件

### 采集与规范化：两条等价路径

我们支持两条并行但等价的数据采集路径：

**1) Chat‑only 路线（推荐）**
- 原始输入：`raw/cursor.md`（Cursor 导出聊天，无需 git/diff）
- 工具：`tools/chat2events.py`
- 产物：`events.jsonl`（将自然对话提取为事件）
  - **已实施修改** → `tool=edit, phase=modify`（进入 Q1 计分）
  - **计划修改** → `tool=plan, phase=modify`（仅留痕，**不计分**）
  - **测试执行** → `tool=shell, phase=test`（触发 TestGuard）
- 当提取结果置信度低或空缺时，可选启用轻量 `git diff --name-only` 作**兜底校验**

**2) Diff 路线**
- 原始输入：`raw/patch.diff`（统一 diff）和可选 `raw/term.log`
- 工具：`tools/patch2events.py`、`tools/term2events.py`
- 产物：`events.jsonl`（每个文件 1 条 `tool=edit` 事件；`term.log` 生成测试事件）

**两条路线后续完全一致**：`events.jsonl` + `goal.json` → `tools/events2guards.py` → `guards.jsonl`

### 三个能力如何由同一数据产生

#### Q1｜执行监控/偏航守卫
读取 `events.jsonl` + `goal.json`，计算：
- **ScopeGuard**：编辑的文件是否在 allowed_paths
- **PlanGuard**：当前 checkpoint 是否允许此类动作
- **TestGuard**：必跑测试是否执行且通过
- **EvidenceGuard**：修改阶段是否引用相关证据

合成 `drift_score = 0.4*scope + 0.3*plan + 0.2*test + 0.1*evidence`；≥阈值（如 0.5）→ warn/rollback

#### Q2｜跨会话学习（模式卡）
从同一条事件流 +（可选）会话导出的文字材料（Cursor/Claude/Aider 导出）中，提取可迁移的"模式卡"：

```json
{
  "pattern_id": "pc_xxx",
  "triggers": ["问题/任务的关键词"],
  "steps": ["关键步骤"],
  "invariants": ["必须满足的不变量"],
  "anti_patterns": ["禁止/常见误用"],
  "eval_examples": ["相关测试/验证样例"],
  "views": {
    "terse": "专家版要点",
    "guided": "新手版步骤+示例+坑点+验证"
  }
}
```

存入 `data/patterns/*.json`，新任务时检索与注入，实现复用与迁移。

#### Q3｜动态抽象（两档视图路由）
同一卡、双视图：
- **terse**：策略/不变量/禁改规则（适合熟练者）
- **guided**：配置步骤/示例/坑点/必跑测试/例外流程（适合新手或高风险任务）

由 `data/profiles/<user>.json`（自报水平 + 历史首试成功率）自动选择视图。

---

## 📦 目录结构（团队数据湖）

```
data/
└─ runs/<run_id>/                   # 每次会话一个 run（人/日期可入名）
   ├─ raw/                          # 原始证据（只追加，不改写）
   │  ├─ base_commit.txt            # git rev-parse HEAD（基线）
   │  ├─ patch.diff                 # git diff -U0（统一 diff；不必 commit）
   │  ├─ term.log                   # 测试/命令输出（可选）
   │  └─ cursor.md                  # Cursor/Claude/Aider 导出（可选，用作"why/反思"）
   ├─ goal.json                     # 目标图/白名单/检查点/必跑测试
   ├─ events.jsonl                  # 规范化事件（Canonical facts）
   ├─ guards.jsonl                  # 守卫评分与 drift_score（Q1）
   └─ artifacts/
      ├─ reflection.txt             # 反思文本（Q2 原料，可由 LLM 生成）
      ├─ pattern.pc_*.json          # 本 run 抽出的模式卡（Q2）
      └─ view_preview.md            # 视图渲染示例（Q3）
data/patterns/                      # 团队模式库（跨 run 复用）
data/profiles/<user>.json           # 用户画像（Q3 路由）
data/eval/                          # SWE-bench predictions.jsonl 与评测产物
tools/                              
  patch2events.py                   # raw/patch.diff → events.jsonl（edit 事件）
  term2events.py                    # raw/term.log  → events.jsonl（test/shell 事件）
  events2guards.py                  # events + goal → guards（Q1）
scripts/
  e2e_cursor_doc_task.py            # 端到端脚本（下方示例）
```

---

## 🧪 端到端示例（"翻译 README 却误改依赖"的典型跑题）

**目标**：只把 README.md 翻译成中文（doc-only）  
**实际**：代理同时修改了 requirements.txt（新增依赖） → 跑题

### 第 0 步｜准备基线与目标

**data/runs/r42/raw/base_commit.txt**：
```
deadbeefcafebabe
```

**data/runs/r42/raw/patch.diff（节选）**：
```diff
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,2 +1,2 @@
-# Project
+# 项目
 Documentation in English.
diff --git a/requirements.txt b/requirements.txt
--- a/requirements.txt
+++ b/requirements.txt
@@ -1 +1,2 @@
+beautifulsoup4
 requests
```

**data/runs/r42/goal.json**：
```json
{
  "run_id": "r42",
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce", "modify", "test", "regress"],
  "required_tests": ["doc_lang_check", "whitelist_diff_check"]
}
```

> **说明**：证据最小集为 base_commit.txt + patch.diff（与 SWE-bench 的"基线快照 + 统一 diff"一致）。无需每步 commit。

### 第 1 步｜规范化与判航

```bash
python tools/patch2events.py data/runs/r42
python tools/term2events.py  data/runs/r42   # 若有 term.log
python tools/events2guards.py data/runs/r42
```

**得到**：
- `events.jsonl`：包含对 README.md 与 requirements.txt 的 edit 事件
- `guards.jsonl`：对 requirements.txt 那一行给出
  - ScopeGuard=1.0（不在 allowed_paths）+ PlanGuard=1.0（modify 阶段不允许）
  - → drift_score ≈ 0.85 ≥ 0.5 → warn/rollback

### 第 2 步｜抽"模式卡"（Q2）

把本次 run 的事件与反思生成模式卡 `pc_doc_only_change`：

```json
{
  "pattern_id": "pc_doc_only_change",
  "triggers": ["documentation-only", "translate readme"],
  "steps": [
    "whitelist README.md/docs/**",
    "forbid requirements.*",
    "run doc_lang_check & whitelist_diff_check"
  ],
  "invariants": ["only whitelisted files changed", "language==target"],
  "anti_patterns": ["edit requirements without consent"],
  "eval_examples": ["doc_lang_check", "whitelist_diff_check"],
  "views": {
    "terse": "Whitelist-only edits; forbid deps change; ensure checks.",
    "guided": "如何配置白名单&语言检测；何时申请例外；常见坑点与验证。"
  }
}
```

复制到 `data/patterns/`，作为团队共享的可复用资产。

### 第 3 步｜动态抽象渲染（Q3）

**data/profiles/jeremy.json（示例）**：
```json
{"user_id":"jeremy","self_report":"intermediate","hist_first_try_success":0.35,"pref":"terse"}
```

**渲染逻辑**：成功率≥阈值或偏好 terse → terse；否则 guided。  
输出到 `artifacts/view_preview.md`，用于 UI 呈现或提示注入。

**到此**，同一份事件数据完成：Q1 判跑题 → Q2 抽模式 → Q3 两档视图。下次遇到"文档/翻译"任务，系统会先天触发该模式，极大降低跑题概率与沟通成本。

---

## 🧰 数据格式（关键文件）

### goal.json
```json
{
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce","modify","test","regress"],
  "required_tests": ["doc_lang_check","whitelist_diff_check"]
}
```

### events.jsonl（每行一个 JSON）
```json
{"run_id":"r42","step":1,"phase":"modify","tool":"edit",
 "where":"README.md:?","what":{"diff":"(omitted)"},"why":"from patch.diff","evidence":{}}
{"run_id":"r42","step":2,"phase":"modify","tool":"edit",
 "where":"requirements.txt:?","what":{"diff":"(omitted)"},"why":"(none)","evidence":{}}
```

### guards.jsonl
```json
{"run_id":"r42","step":1,"scope_guard":0.0,"plan_guard":0.0,"test_guard":0.0,"evidence_guard":0.0,"drift_score":0.0,"action":"ok","file":"README.md"}
{"run_id":"r42","step":2,"scope_guard":1.0,"plan_guard":1.0,"test_guard":0.0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt"}
```

### 模式卡 pc_*.json
见上方"抽卡"示例。

### 用户画像 profiles/*.json
```json
{"user_id":"<id>","self_report":"novice|intermediate|expert","hist_first_try_success":0.42,"pref":"guided|terse"}
```


---

## ⚙️ 最小可用脚本（MVP）

你可以先手工填充 `events.jsonl`/`guards.jsonl` 跑通；再用下面脚本自动化。

- `tools/patch2events.py`：解析 `raw/patch.diff` → 生成 edit 事件（每文件 1 条）
- `tools/term2events.py`：解析 `raw/term.log` → 追加 shell/test 事件
- `tools/events2guards.py`：按 `goal.json` 计算四守卫与 drift_score（≥0.5 → warn）
- `agent/reflexion.py`：读取 `cursor.md`（如有）与 events，生成简要反思文本
- `agent/extract_card.py`：反思 → 模式卡（结构化 JSON）
- `q2_memory/retrieve.py`：依据 objective/关键词检索最匹配模式
- `q3_views/render.py`：依据用户画像选择 terse/guided 并渲染
- `scripts/e2e_cursor_doc_task.py`：一键端到端（示例 r42）

---

## 🧪 评测（社区对齐 + 自定义指标）

### 社区对齐：SWE-bench
- 生成 `data/eval/predictions.jsonl`（每行 `{"instance_id","model_patch"}`），用官方 harness 评 %Resolved
- 我们本地的 base_commit + unified diff 与它的"基线快照 + 统一 diff"一致

### 我们新增指标（体现 Q2/Q3/Q1 价值）
- **Q2**：模式复用率、首试成功率↑、平均回合数/用时↓
- **Q3**：视图匹配度（guided 对新手更稳、terse 不打扰专家）
- **Q1**：偏航检出率、误报率、偏航恢复时间（warn→回到正确 checkpoint 的步数/秒）

### 消融（Ablation）
```
baseline → +pattern → +pattern+views → +pattern+views+guards
```
在同一批任务上成对比较，展示复用与守卫带来的复利收益。

---

## 🗺️ 实施计划（4 周样例）

### Week 1｜打底
搭事件总线；采 3–5 个真实案例，手工沉淀 3 张模式卡（如：空指针防护、依赖冲突、off-by-one）。

### Week 2｜能用
接检索+注入；新任务自动推荐模式卡（先用 terse）；打通最小 Q1 守卫（4 checkpoint）。

### Week 3｜过 Gate
上动态抽象路由（画像=自报水平 + 历史成功率）；完成"相似任务首试成功率显著提升"演示与 ablation。

### Week 4｜打磨
扩大到 8–10 张模式卡；补"偏航恢复时间/复用率"可视化；记录失败案例与改进方向。

> **Q1 坚持"最低可用"**：4 checkpoint + 2 条硬规则（白/黑名单；未过前置测试禁止合并）。把时间投给 Q2/Q3。

---

## 🧑‍🤝‍🧑 团队 SOP（最简可执行）

1. **每次会话结束至少落 3 件**：
   `raw/base_commit.txt`、`raw/patch.diff`、`goal.json`（可选：`raw/term.log`、`raw/cursor.md`）

2. **跑脚本**：
   ```bash
   python tools/patch2events.py data/runs/<run_id>
   python tools/term2events.py  data/runs/<run_id>   # 若有 term.log
   python tools/events2guards.py data/runs/<run_id>
   ```

3. **通过/有价值 → 抽卡**：生成 `artifacts/pattern.*.json` 并复制到 `data/patterns/`

4. **周会汇总** `guards.jsonl` 为"偏航榜单"，共建与复用模式卡

5. **每两周做一次** SWE-bench Lite/Verified 小规模对齐评测 + 我们指标报表

---

## ❓ FAQ

### 必须每次 commit 吗？
不需要。`git diff -U0` + `git rev-parse HEAD` 就足以作为"可复现实锤"。Commit 有助于审计与回滚，但不是 Q1/Q2/Q3 的硬依赖。

### Cursor 导出能当"事实来源"吗？
建议只作"why/反思"；"改了什么/是否通过"以 `patch.diff` 与测试日志为准。

### 和 RAG 有什么不同？
RAG 一般检索静态知识；本系统沉淀的是你团队亲手做成的"可复用做法"（模式卡），是经验资产。

### 如何防止模式卡误触发？
通过 triggers 细化关键词/正则；在检索后加入人工确认或风险打分（约束冲突时降权/不注入）。

### 误报的偏航提醒如何处理？
UI 提供"我确认需要"按钮并记录为例外证据，用于改进 EvidenceGuard 与模式卡的 anti_patterns。

---

## ⚠️ 风险与边界

- 事件抽取过于粗糙可能导致误报/漏报；先从**"白名单 + 必跑测试"**的硬规则开始
- 模式卡过多会稀释检索精度；以"有明显 uplift"为标准进入模式库
- 用户画像初期可简单（自报 + 首试成功率）；后续再升级为偏好学习

---

## 🧭 TL;DR（落地步骤）

1. **落证据**：`base_commit.txt` + `patch.diff` (+ `term.log` + `cursor.md`)
2. **目标**：写 `goal.json`（白名单 + 检查点 + 必跑测试）
3. **生成**：`events.jsonl` → `guards.jsonl`，大于阈值则 warn/rollback
4. **沉淀**：抽"模式卡"，放入 `data/patterns/`，下次自动检索触发
5. **呈现**：按 `profiles/<user>.json` 渲染 terse/guided 两档视图
6. **评测**：SWE-bench %Resolved + 我们的 Q1/Q2/Q3 指标与 ablation

**同一份事件数据，三件事一次到位**：不跑题、能复用、会因人施教。

```

```markdown
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
初学者偏好步骤与示例，资深更需要策略与不变量。代理**难以按"用户水平 × 任务难度"**自动调节抽象层级，输出要么啰嗦、要么含糊。

### 3. 长任务易跑偏（Q1）
多步修复/重构中常发生"只要改文档，却去改依赖"等跑题行为，缺少目标-检查点-守卫的持续对齐与回滚能力。

**目标**：把编程代理从"一次性助手"，升级为"会成长、会复用、会自我约束"的合作者。

---

## 🏗️ 统一方案（同一底座，三段合一）

### 共同底座：事件总线（Event Bus）＋ 目标图（Goal Graph）
- **事件总线**：按步骤记录 where/what/why/evidence（改了什么、为何改、证据/日志）
- **目标图**：四检查点 复现→修改→测试→回归，定义允许动作、白/黑名单与验收条件

### 采集与规范化：两条等价路径

我们支持两条并行但等价的数据采集路径：

**1) Chat‑only 路线（推荐）**
- 原始输入：`raw/cursor.md`（Cursor 导出聊天，无需 git/diff）
- 工具：`tools/chat2events.py`
- 产物：`events.jsonl`（将自然对话提取为事件）
  - **已实施修改** → `tool=edit, phase=modify`（进入 Q1 计分）
  - **计划修改** → `tool=plan, phase=modify`（仅留痕，**不计分**）
  - **测试执行** → `tool=shell, phase=test`（触发 TestGuard）
- 当提取结果置信度低或空缺时，可选启用轻量 `git diff --name-only` 作**兜底校验**

**2) Diff 路线**
- 原始输入：`raw/patch.diff`（统一 diff）和可选 `raw/term.log`
- 工具：`tools/patch2events.py`、`tools/term2events.py`
- 产物：`events.jsonl`（每个文件 1 条 `tool=edit` 事件；`term.log` 生成测试事件）

**两条路线后续完全一致**：`events.jsonl` + `goal.json` → `tools/events2guards.py` → `guards.jsonl`

### 三个能力如何由同一数据产生

#### Q1｜执行监控/偏航守卫
读取 `events.jsonl` + `goal.json`，计算：
- **ScopeGuard**：编辑的文件是否在 allowed_paths
- **PlanGuard**：当前 checkpoint 是否允许此类动作
- **TestGuard**：必跑测试是否执行且通过
- **EvidenceGuard**：修改阶段是否引用相关证据

合成 `drift_score = 0.4*scope + 0.3*plan + 0.2*test + 0.1*evidence`；≥阈值（如 0.5）→ warn/rollback

> **判分策略（重要）**  
> 仅对 `tool=edit` 的事件计算 `Scope/Plan/Evidence`；`tool=plan` 恒 `action=ok`（不计分）。  
> 测试事件（`tool=shell, phase=test`）触发 `TestGuard`；`override.acknowledged=true` 会将违规降级为轻度（避免 warn/rollback）

#### Q2｜跨会话学习（模式卡）
从同一条事件流 +（可选）会话导出的文字材料（Cursor/Claude/Aider 导出）中，提取可迁移的"模式卡"：

```json
{
  "pattern_id": "pc_xxx",
  "triggers": ["问题/任务的关键词"],
  "steps": ["关键步骤"],
  "invariants": ["必须满足的不变量"],
  "anti_patterns": ["禁止/常见误用"],
  "eval_examples": ["相关测试/验证样例"],
  "views": {
    "terse": "专家版要点",
    "guided": "新手版步骤+示例+坑点+验证"
  }
}
```

存入 `data/patterns/*.json`，新任务时检索与注入，实现复用与迁移。

#### Q3｜动态抽象（两档视图路由）
同一卡、双视图：
- **terse**：策略/不变量/禁改规则（适合熟练者）
- **guided**：配置步骤/示例/坑点/必跑测试/例外流程（适合新手或高风险任务）

由 `data/profiles/<user>.json`（自报水平 + 历史首试成功率）自动选择视图。

---

## 📦 目录结构（团队数据湖）

```
data/
└─ runs/<run_id>/                   # 每次会话一个 run（人/日期可入名）
   ├─ raw/                          # 原始证据（只追加，不改写）
   │  ├─ base_commit.txt            # git rev-parse HEAD（基线）
   │  ├─ patch.diff                 # git diff -U0（统一 diff；不必 commit）
   │  ├─ term.log                   # 测试/命令输出（可选）
   │  └─ cursor.md                  # Cursor/Claude/Aider 导出（可选，用作"why/反思"）
   ├─ goal.json                     # 目标图/白名单/检查点/必跑测试
   ├─ events.jsonl                  # 规范化事件（Canonical facts）
   ├─ guards.jsonl                  # 守卫评分与 drift_score（Q1）
   └─ artifacts/
      ├─ reflection.txt             # 反思文本（Q2 原料，可由 LLM 生成）
      ├─ pattern.pc_*.json          # 本 run 抽出的模式卡（Q2）
      └─ view_preview.md            # 视图渲染示例（Q3）
data/patterns/                      # 团队模式库（跨 run 复用）
data/profiles/<user>.json           # 用户画像（Q3 路由）
data/eval/                          # SWE-bench predictions.jsonl 与评测产物
tools/                              
  patch2events.py                   # raw/patch.diff → events.jsonl（edit 事件）
  term2events.py                    # raw/term.log  → events.jsonl（test/shell 事件）
  events2guards.py                  # events + goal → guards（Q1）
scripts/
  e2e_cursor_doc_task.py            # 端到端脚本（下方示例）
```

---

## 🧪 端到端示例（"翻译 README 却误改依赖"的典型跑题）

**目标**：只把 README.md 翻译成中文（doc-only）  
**实际**：代理同时修改了 requirements.txt（新增依赖） → 跑题

### 第 0 步｜准备基线与目标

**data/runs/r42/raw/base_commit.txt**：
```
deadbeefcafebabe
```

**data/runs/r42/raw/patch.diff（节选）**：
```diff
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,2 +1,2 @@
-# Project
+# 项目
 Documentation in English.
diff --git a/requirements.txt b/requirements.txt
--- a/requirements.txt
+++ b/requirements.txt
@@ -1 +1,2 @@
+beautifulsoup4
 requests
```

**data/runs/r42/goal.json**：
```json
{
  "run_id": "r42",
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce", "modify", "test", "regress"],
  "required_tests": ["doc_lang_check", "whitelist_diff_check"]
}
```

> **说明**：证据最小集为 base_commit.txt + patch.diff（与 SWE-bench 的"基线快照 + 统一 diff"一致）。无需每步 commit。

### 第 1 步｜规范化与判航

```bash
python tools/patch2events.py data/runs/r42
python tools/term2events.py  data/runs/r42   # 若有 term.log
python tools/events2guards.py data/runs/r42
```

**得到**：
- `events.jsonl`：包含对 README.md 与 requirements.txt 的 edit 事件
- `guards.jsonl`：对 requirements.txt 那一行给出
  - ScopeGuard=1.0（不在 allowed_paths）+ PlanGuard=1.0（modify 阶段不允许）
  - → drift_score ≈ 0.85 ≥ 0.5 → warn/rollback

### 第 2 步｜抽"模式卡"（Q2）

把本次 run 的事件与反思生成模式卡 `pc_doc_only_change`：

```json
{
  "pattern_id": "pc_doc_only_change",
  "triggers": ["documentation-only", "translate readme"],
  "steps": [
    "whitelist README.md/docs/**",
    "forbid requirements.*",
    "run doc_lang_check & whitelist_diff_check"
  ],
  "invariants": ["only whitelisted files changed", "language==target"],
  "anti_patterns": ["edit requirements without consent"],
  "eval_examples": ["doc_lang_check", "whitelist_diff_check"],
  "views": {
    "terse": "Whitelist-only edits; forbid deps change; ensure checks.",
    "guided": "如何配置白名单&语言检测；何时申请例外；常见坑点与验证。"
  }
}
```

复制到 `data/patterns/`，作为团队共享的可复用资产。

### 第 3 步｜动态抽象渲染（Q3）

**data/profiles/jeremy.json（示例）**：
```json
{"user_id":"jeremy","self_report":"intermediate","hist_first_try_success":0.35,"pref":"terse"}
```

**渲染逻辑**：成功率≥阈值或偏好 terse → terse；否则 guided。  
输出到 `artifacts/view_preview.md`，用于 UI 呈现或提示注入。

**到此**，同一份事件数据完成：Q1 判跑题 → Q2 抽模式 → Q3 两档视图。下次遇到"文档/翻译"任务，系统会先天触发该模式，极大降低跑题概率与沟通成本。

---

## 🧰 数据格式（关键文件）

### goal.json
```json
{
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce","modify","test","regress"],
  "required_tests": ["doc_lang_check","whitelist_diff_check"]
}
```

### events.jsonl（每行一个 JSON）
```json
{"run_id":"r42","step":1,"phase":"modify","tool":"edit",
 "where":"README.md:?","what":{"diff":"(omitted)"},"why":"from patch.diff","evidence":{}}
{"run_id":"r42","step":2,"phase":"modify","tool":"edit",
 "where":"requirements.txt:?","what":{"diff":"(omitted)"},"why":"(none)","evidence":{}}
```

### guards.jsonl
```json
{"run_id":"r42","step":1,"scope_guard":0.0,"plan_guard":0.0,"test_guard":0.0,"evidence_guard":0.0,"drift_score":0.0,"action":"ok","file":"README.md"}
{"run_id":"r42","step":2,"scope_guard":1.0,"plan_guard":1.0,"test_guard":0.0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt"}
```

### 模式卡 pc_*.json
见上方"抽卡"示例。

### 用户画像 profiles/*.json
```json
{"user_id":"<id>","self_report":"novice|intermediate|expert","hist_first_try_success":0.42,"pref":"guided|terse"}
```


---

## ⚙️ 最小可用脚本（MVP）

你可以先手工填充 `events.jsonl`/`guards.jsonl` 跑通；再用下面脚本自动化。

- `tools/patch2events.py`：解析 `raw/patch.diff` → 生成 edit 事件（每文件 1 条）
- `tools/term2events.py`：解析 `raw/term.log` → 追加 shell/test 事件
- `tools/events2guards.py`：按 `goal.json` 计算四守卫与 drift_score（≥0.5 → warn）
- `agent/reflexion.py`：读取 `cursor.md`（如有）与 events，生成简要反思文本
- `agent/extract_card.py`：反思 → 模式卡（结构化 JSON）
- `q2_memory/retrieve.py`：依据 objective/关键词检索最匹配模式
- `q3_views/render.py`：依据用户画像选择 terse/guided 并渲染
- `scripts/e2e_cursor_doc_task.py`：一键端到端（示例 r42）

---

## 🧪 评测（社区对齐 + 自定义指标）

### 社区对齐：SWE-bench
- 生成 `data/eval/predictions.jsonl`（每行 `{"instance_id","model_patch"}`），用官方 harness 评 %Resolved
- 我们本地的 base_commit + unified diff 与它的"基线快照 + 统一 diff"一致

### 我们新增指标（体现 Q2/Q3/Q1 价值）
- **Q2**：模式复用率、首试成功率↑、平均回合数/用时↓
- **Q3**：视图匹配度（guided 对新手更稳、terse 不打扰专家）
- **Q1**：偏航检出率、误报率、偏航恢复时间（warn→回到正确 checkpoint 的步数/秒）

### 消融（Ablation）
```
baseline → +pattern → +pattern+views → +pattern+views+guards
```
在同一批任务上成对比较，展示复用与守卫带来的复利收益。

---

## 🗺️ 实施计划（4 周样例）

### Week 1｜打底
搭事件总线；采 3–5 个真实案例，手工沉淀 3 张模式卡（如：空指针防护、依赖冲突、off-by-one）。

### Week 2｜能用
接检索+注入；新任务自动推荐模式卡（先用 terse）；打通最小 Q1 守卫（4 checkpoint）。

### Week 3｜过 Gate
上动态抽象路由（画像=自报水平 + 历史成功率）；完成"相似任务首试成功率显著提升"演示与 ablation。

### Week 4｜打磨
扩大到 8–10 张模式卡；补"偏航恢复时间/复用率"可视化；记录失败案例与改进方向。

> **Q1 坚持"最低可用"**：4 checkpoint + 2 条硬规则（白/黑名单；未过前置测试禁止合并）。把时间投给 Q2/Q3。

---

## 🧑‍🤝‍🧑 团队 SOP（最简可执行）

1. **每次会话结束至少落 3 件**：
   `raw/base_commit.txt`、`raw/patch.diff`、`goal.json`（可选：`raw/term.log`、`raw/cursor.md`）

2. **跑脚本**：
   ```bash
   python tools/patch2events.py data/runs/<run_id>
   python tools/term2events.py  data/runs/<run_id>   # 若有 term.log
   python tools/events2guards.py data/runs/<run_id>
   ```

3. **通过/有价值 → 抽卡**：生成 `artifacts/pattern.*.json` 并复制到 `data/patterns/`

4. **周会汇总** `guards.jsonl` 为"偏航榜单"，共建与复用模式卡

5. **每两周做一次** SWE-bench Lite/Verified 小规模对齐评测 + 我们指标报表

---

## ❓ FAQ

### 必须每次 commit 吗？
不需要。`git diff -U0` + `git rev-parse HEAD` 就足以作为"可复现实锤"。Commit 有助于审计与回滚，但不是 Q1/Q2/Q3 的硬依赖。

### Cursor 导出能当"事实来源"吗？
建议只作"why/反思"；"改了什么/是否通过"以 `patch.diff` 与测试日志为准。

### 和 RAG 有什么不同？
RAG 一般检索静态知识；本系统沉淀的是你团队亲手做成的"可复用做法"（模式卡），是经验资产。

### 如何防止模式卡误触发？
通过 triggers 细化关键词/正则；在检索后加入人工确认或风险打分（约束冲突时降权/不注入）。

### 误报的偏航提醒如何处理？
UI 提供"我确认需要"按钮并记录为例外证据，用于改进 EvidenceGuard 与模式卡的 anti_patterns。

---

## ⚠️ 风险与边界

- 事件抽取过于粗糙可能导致误报/漏报；先从**"白名单 + 必跑测试"**的硬规则开始
- 模式卡过多会稀释检索精度；以"有明显 uplift"为标准进入模式库
- 用户画像初期可简单（自报 + 首试成功率）；后续再升级为偏好学习

---

## 🧭 TL;DR（落地步骤）

1. **落证据**：`base_commit.txt` + `patch.diff` (+ `term.log` + `cursor.md`)
2. **目标**：写 `goal.json`（白名单 + 检查点 + 必跑测试）
3. **生成**：`events.jsonl` → `guards.jsonl`，大于阈值则 warn/rollback
4. **沉淀**：抽"模式卡"，放入 `data/patterns/`，下次自动检索触发
5. **呈现**：按 `profiles/<user>.json` 渲染 terse/guided 两档视图
6. **评测**：SWE-bench %Resolved + 我们的 Q1/Q2/Q3 指标与 ablation

**同一份事件数据，三件事一次到位**：不跑题、能复用、会因人施教。

```

```markdown
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
初学者偏好步骤与示例，资深更需要策略与不变量。代理**难以按"用户水平 × 任务难度"**自动调节抽象层级，输出要么啰嗦、要么含糊。

### 3. 长任务易跑偏（Q1）
多步修复/重构中常发生"只要改文档，却去改依赖"等跑题行为，缺少目标-检查点-守卫的持续对齐与回滚能力。

**目标**：把编程代理从"一次性助手"，升级为"会成长、会复用、会自我约束"的合作者。

---

## 🏗️ 统一方案（同一底座，三段合一）

### 共同底座：事件总线（Event Bus）＋ 目标图（Goal Graph）
- **事件总线**：按步骤记录 where/what/why/evidence（改了什么、为何改、证据/日志）
- **目标图**：四检查点 复现→修改→测试→回归，定义允许动作、白/黑名单与验收条件

### 采集与规范化：两条等价路径

我们支持两条并行但等价的数据采集路径：

**1) Chat‑only 路线（推荐）**
- 原始输入：`raw/cursor.md`（Cursor 导出聊天，无需 git/diff）
- 工具：`tools/chat2events.py`
- 产物：`events.jsonl`（将自然对话提取为事件）
  - **已实施修改** → `tool=edit, phase=modify`（进入 Q1 计分）
  - **计划修改** → `tool=plan, phase=modify`（仅留痕，**不计分**）
  - **测试执行** → `tool=shell, phase=test`（触发 TestGuard）
- 当提取结果置信度低或空缺时，可选启用轻量 `git diff --name-only` 作**兜底校验**

**2) Diff 路线**
- 原始输入：`raw/patch.diff`（统一 diff）和可选 `raw/term.log`
- 工具：`tools/patch2events.py`、`tools/term2events.py`
- 产物：`events.jsonl`（每个文件 1 条 `tool=edit` 事件；`term.log` 生成测试事件）

**两条路线后续完全一致**：`events.jsonl` + `goal.json` → `tools/events2guards.py` → `guards.jsonl`

### 三个能力如何由同一数据产生

#### Q1｜执行监控/偏航守卫
读取 `events.jsonl` + `goal.json`，计算：
- **ScopeGuard**：编辑的文件是否在 allowed_paths
- **PlanGuard**：当前 checkpoint 是否允许此类动作
- **TestGuard**：必跑测试是否执行且通过
- **EvidenceGuard**：修改阶段是否引用相关证据

合成 `drift_score = 0.4*scope + 0.3*plan + 0.2*test + 0.1*evidence`；≥阈值（如 0.5）→ warn/rollback

> **判分策略（重要）**  
> 仅对 `tool=edit` 的事件计算 `Scope/Plan/Evidence`；`tool=plan` 恒 `action=ok`（不计分）。  
> 测试事件（`tool=shell, phase=test`）触发 `TestGuard`；`override.acknowledged=true` 会将违规降级为轻度（避免 warn/rollback）

#### Q2｜跨会话学习（模式卡）
从同一条事件流 +（可选）会话导出的文字材料（Cursor/Claude/Aider 导出）中，提取可迁移的"模式卡"：

```json
{
  "pattern_id": "pc_xxx",
  "triggers": ["问题/任务的关键词"],
  "steps": ["关键步骤"],
  "invariants": ["必须满足的不变量"],
  "anti_patterns": ["禁止/常见误用"],
  "eval_examples": ["相关测试/验证样例"],
  "views": {
    "terse": "专家版要点",
    "guided": "新手版步骤+示例+坑点+验证"
  }
}
```

存入 `data/patterns/*.json`，新任务时检索与注入，实现复用与迁移。

#### Q3｜动态抽象（两档视图路由）
同一卡、双视图：
- **terse**：策略/不变量/禁改规则（适合熟练者）
- **guided**：配置步骤/示例/坑点/必跑测试/例外流程（适合新手或高风险任务）

由 `data/profiles/<user>.json`（自报水平 + 历史首试成功率）自动选择视图。

---

## 📦 目录结构（团队数据湖）

```
data/
└─ runs/<run_id>/                   # 每次会话一个 run（人/日期可入名）
   ├─ raw/                          # 原始证据（只追加，不改写）
   │  ├─ base_commit.txt            # git rev-parse HEAD（基线）
   │  ├─ patch.diff                 # git diff -U0（统一 diff；不必 commit）
   │  ├─ term.log                   # 测试/命令输出（可选）
   │  └─ cursor.md                  # Cursor/Claude/Aider 导出（可选，用作"why/反思"）
   ├─ goal.json                     # 目标图/白名单/检查点/必跑测试
   ├─ events.jsonl                  # 规范化事件（Canonical facts）
   ├─ guards.jsonl                  # 守卫评分与 drift_score（Q1）
   └─ artifacts/
      ├─ reflection.txt             # 反思文本（Q2 原料，可由 LLM 生成）
      ├─ pattern.pc_*.json          # 本 run 抽出的模式卡（Q2）
      └─ view_preview.md            # 视图渲染示例（Q3）
data/patterns/                      # 团队模式库（跨 run 复用）
data/profiles/<user>.json           # 用户画像（Q3 路由）
data/eval/                          # SWE-bench predictions.jsonl 与评测产物
tools/                              
  chat2events.py                    # ★ Chat-only：raw/cursor.md → events.jsonl（planned/applied＋置信度）
  events2guards.py                  # 四守卫（仅 edit 计分；plan 恒 ok）
  patch2events.py                   # Diff 路线：raw/patch.diff → events.jsonl
  term2events.py                    # 解析 raw/term.log → 测试事件
scripts/
  e2e_chat_only.py                  # 一键：chat → events → guards
  e2e_one.py                        # Diff 路线单 run 演示
```

---

## 🧪 端到端示例（"翻译 README 却误改依赖"的典型跑题）

**目标**：只把 README.md 翻译成中文（doc-only）  
**实际**：代理同时修改了 requirements.txt（新增依赖） → 跑题

### 第 0 步｜准备基线与目标

**data/runs/r42/raw/base_commit.txt**：
```
deadbeefcafebabe
```

**data/runs/r42/raw/patch.diff（节选）**：
```diff
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,2 +1,2 @@
-# Project
+# 项目
 Documentation in English.
diff --git a/requirements.txt b/requirements.txt
--- a/requirements.txt
+++ b/requirements.txt
@@ -1 +1,2 @@
+beautifulsoup4
 requests
```

**data/runs/r42/goal.json**：
```json
{
  "run_id": "r42",
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce", "modify", "test", "regress"],
  "required_tests": ["doc_lang_check", "whitelist_diff_check"]
}
```

> **说明**：证据最小集为 base_commit.txt + patch.diff（与 SWE-bench 的"基线快照 + 统一 diff"一致）。无需每步 commit。

### 第 1 步｜规范化与判航

```bash
python tools/patch2events.py data/runs/r42
python tools/term2events.py  data/runs/r42   # 若有 term.log
python tools/events2guards.py data/runs/r42
```

**得到**：
- `events.jsonl`：包含对 README.md 与 requirements.txt 的 edit 事件
- `guards.jsonl`：对 requirements.txt 那一行给出
  - ScopeGuard=1.0（不在 allowed_paths）+ PlanGuard=1.0（modify 阶段不允许）
  - → drift_score ≈ 0.85 ≥ 0.5 → warn/rollback

### 第 2 步｜抽"模式卡"（Q2）

把本次 run 的事件与反思生成模式卡 `pc_doc_only_change`：

```json
{
  "pattern_id": "pc_doc_only_change",
  "triggers": ["documentation-only", "translate readme"],
  "steps": [
    "whitelist README.md/docs/**",
    "forbid requirements.*",
    "run doc_lang_check & whitelist_diff_check"
  ],
  "invariants": ["only whitelisted files changed", "language==target"],
  "anti_patterns": ["edit requirements without consent"],
  "eval_examples": ["doc_lang_check", "whitelist_diff_check"],
  "views": {
    "terse": "Whitelist-only edits; forbid deps change; ensure checks.",
    "guided": "如何配置白名单&语言检测；何时申请例外；常见坑点与验证。"
  }
}
```

复制到 `data/patterns/`，作为团队共享的可复用资产。

### 第 3 步｜动态抽象渲染（Q3）

**data/profiles/jeremy.json（示例）**：
```json
{"user_id":"jeremy","self_report":"intermediate","hist_first_try_success":0.35,"pref":"terse"}
```

**渲染逻辑**：成功率≥阈值或偏好 terse → terse；否则 guided。  
输出到 `artifacts/view_preview.md`，用于 UI 呈现或提示注入。

**到此**，同一份事件数据完成：Q1 判跑题 → Q2 抽模式 → Q3 两档视图。下次遇到"文档/翻译"任务，系统会先天触发该模式，极大降低跑题概率与沟通成本。

---

## 🧰 数据格式（关键文件）

### goal.json
```json
{
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce","modify","test","regress"],
  "required_tests": ["doc_lang_check","whitelist_diff_check"]
}
```

### events.jsonl（每行一个 JSON）
```json
{"run_id":"r42","step":1,"phase":"modify","tool":"edit",
 "where":"README.md:?","what":{"diff":"(omitted)"},"why":"from patch.diff","evidence":{}}
{"run_id":"r42","step":2,"phase":"modify","tool":"edit",
 "where":"requirements.txt:?","what":{"diff":"(omitted)"},"why":"(none)","evidence":{}}
```

### guards.jsonl
```json
{"run_id":"r42","step":1,"scope_guard":0.0,"plan_guard":0.0,"test_guard":0.0,"evidence_guard":0.0,"drift_score":0.0,"action":"ok","file":"README.md"}
{"run_id":"r42","step":2,"scope_guard":1.0,"plan_guard":1.0,"test_guard":0.0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt"}
```

### 模式卡 pc_*.json
见上方"抽卡"示例。

### 用户画像 profiles/*.json
```json
{"user_id":"<id>","self_report":"novice|intermediate|expert","hist_first_try_success":0.42,"pref":"guided|terse"}
```


---

## ⚙️ 最小可用脚本（MVP）

你可以先手工填充 `events.jsonl`/`guards.jsonl` 跑通；再用下面脚本自动化。

- `tools/patch2events.py`：解析 `raw/patch.diff` → 生成 edit 事件（每文件 1 条）
- `tools/term2events.py`：解析 `raw/term.log` → 追加 shell/test 事件
- `tools/events2guards.py`：按 `goal.json` 计算四守卫与 drift_score（≥0.5 → warn）
- `agent/reflexion.py`：读取 `cursor.md`（如有）与 events，生成简要反思文本
- `agent/extract_card.py`：反思 → 模式卡（结构化 JSON）
- `q2_memory/retrieve.py`：依据 objective/关键词检索最匹配模式
- `q3_views/render.py`：依据用户画像选择 terse/guided 并渲染
- `scripts/e2e_cursor_doc_task.py`：一键端到端（示例 r42）

---

## 🧪 评测（社区对齐 + 自定义指标）

### 社区对齐：SWE-bench
- 生成 `data/eval/predictions.jsonl`（每行 `{"instance_id","model_patch"}`），用官方 harness 评 %Resolved
- 我们本地的 base_commit + unified diff 与它的"基线快照 + 统一 diff"一致

### 我们新增指标（体现 Q2/Q3/Q1 价值）
- **Q2**：模式复用率、首试成功率↑、平均回合数/用时↓
- **Q3**：视图匹配度（guided 对新手更稳、terse 不打扰专家）
- **Q1**：偏航检出率、误报率、偏航恢复时间（warn→回到正确 checkpoint 的步数/秒）

### 消融（Ablation）
```
baseline → +pattern → +pattern+views → +pattern+views+guards
```
在同一批任务上成对比较，展示复用与守卫带来的复利收益。

---

## 🗺️ 实施计划（4 周样例）

### Week 1｜打底
搭事件总线；采 3–5 个真实案例，手工沉淀 3 张模式卡（如：空指针防护、依赖冲突、off-by-one）。

### Week 2｜能用
接检索+注入；新任务自动推荐模式卡（先用 terse）；打通最小 Q1 守卫（4 checkpoint）。

### Week 3｜过 Gate
上动态抽象路由（画像=自报水平 + 历史成功率）；完成"相似任务首试成功率显著提升"演示与 ablation。

### Week 4｜打磨
扩大到 8–10 张模式卡；补"偏航恢复时间/复用率"可视化；记录失败案例与改进方向。

> **Q1 坚持"最低可用"**：4 checkpoint + 2 条硬规则（白/黑名单；未过前置测试禁止合并）。把时间投给 Q2/Q3。

---

## 🧑‍🤝‍🧑 团队 SOP（最简可执行）

1. **每次会话结束至少落 3 件**：
   `raw/base_commit.txt`、`raw/patch.diff`、`goal.json`（可选：`raw/term.log`、`raw/cursor.md`）

2. **跑脚本**：
   ```bash
   python tools/patch2events.py data/runs/<run_id>
   python tools/term2events.py  data/runs/<run_id>   # 若有 term.log
   python tools/events2guards.py data/runs/<run_id>
   ```

3. **通过/有价值 → 抽卡**：生成 `artifacts/pattern.*.json` 并复制到 `data/patterns/`

4. **周会汇总** `guards.jsonl` 为"偏航榜单"，共建与复用模式卡

5. **每两周做一次** SWE-bench Lite/Verified 小规模对齐评测 + 我们指标报表

---

## ❓ FAQ

### 必须每次 commit 吗？
不需要。`git diff -U0` + `git rev-parse HEAD` 就足以作为"可复现实锤"。Commit 有助于审计与回滚，但不是 Q1/Q2/Q3 的硬依赖。

### Cursor 导出能当"事实来源"吗？
建议只作"why/反思"；"改了什么/是否通过"以 `patch.diff` 与测试日志为准。

### 和 RAG 有什么不同？
RAG 一般检索静态知识；本系统沉淀的是你团队亲手做成的"可复用做法"（模式卡），是经验资产。

### 如何防止模式卡误触发？
通过 triggers 细化关键词/正则；在检索后加入人工确认或风险打分（约束冲突时降权/不注入）。

### 误报的偏航提醒如何处理？
UI 提供"我确认需要"按钮并记录为例外证据，用于改进 EvidenceGuard 与模式卡的 anti_patterns。

---

## ⚠️ 风险与边界

- 事件抽取过于粗糙可能导致误报/漏报；先从**"白名单 + 必跑测试"**的硬规则开始
- 模式卡过多会稀释检索精度；以"有明显 uplift"为标准进入模式库
- 用户画像初期可简单（自报 + 首试成功率）；后续再升级为偏好学习

---

## 🧭 TL;DR（落地步骤）

1. **落证据**：`base_commit.txt` + `patch.diff` (+ `term.log` + `cursor.md`)
2. **目标**：写 `goal.json`（白名单 + 检查点 + 必跑测试）
3. **生成**：`events.jsonl` → `guards.jsonl`，大于阈值则 warn/rollback
4. **沉淀**：抽"模式卡"，放入 `data/patterns/`，下次自动检索触发
5. **呈现**：按 `profiles/<user>.json` 渲染 terse/guided 两档视图
6. **评测**：SWE-bench %Resolved + 我们的 Q1/Q2/Q3 指标与 ablation

**同一份事件数据，三件事一次到位**：不跑题、能复用、会因人施教。

```

```markdown
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
初学者偏好步骤与示例，资深更需要策略与不变量。代理**难以按"用户水平 × 任务难度"**自动调节抽象层级，输出要么啰嗦、要么含糊。

### 3. 长任务易跑偏（Q1）
多步修复/重构中常发生"只要改文档，却去改依赖"等跑题行为，缺少目标-检查点-守卫的持续对齐与回滚能力。

**目标**：把编程代理从"一次性助手"，升级为"会成长、会复用、会自我约束"的合作者。

---

## 🏗️ 统一方案（同一底座，三段合一）

### 共同底座：事件总线（Event Bus）＋ 目标图（Goal Graph）
- **事件总线**：按步骤记录 where/what/why/evidence（改了什么、为何改、证据/日志）
- **目标图**：四检查点 复现→修改→测试→回归，定义允许动作、白/黑名单与验收条件

### 采集与规范化：两条等价路径

我们支持两条并行但等价的数据采集路径：

**1) Chat‑only 路线（推荐）**
- 原始输入：`raw/cursor.md`（Cursor 导出聊天，无需 git/diff）
- 工具：`tools/chat2events.py`
- 产物：`events.jsonl`（将自然对话提取为事件）
  - **已实施修改** → `tool=edit, phase=modify`（进入 Q1 计分）
  - **计划修改** → `tool=plan, phase=modify`（仅留痕，**不计分**）
  - **测试执行** → `tool=shell, phase=test`（触发 TestGuard）
- 当提取结果置信度低或空缺时，可选启用轻量 `git diff --name-only` 作**兜底校验**

**2) Diff 路线**
- 原始输入：`raw/patch.diff`（统一 diff）和可选 `raw/term.log`
- 工具：`tools/patch2events.py`、`tools/term2events.py`
- 产物：`events.jsonl`（每个文件 1 条 `tool=edit` 事件；`term.log` 生成测试事件）

**两条路线后续完全一致**：`events.jsonl` + `goal.json` → `tools/events2guards.py` → `guards.jsonl`

### 三个能力如何由同一数据产生

#### Q1｜执行监控/偏航守卫
读取 `events.jsonl` + `goal.json`，计算：
- **ScopeGuard**：编辑的文件是否在 allowed_paths
- **PlanGuard**：当前 checkpoint 是否允许此类动作
- **TestGuard**：必跑测试是否执行且通过
- **EvidenceGuard**：修改阶段是否引用相关证据

合成 `drift_score = 0.4*scope + 0.3*plan + 0.2*test + 0.1*evidence`；≥阈值（如 0.5）→ warn/rollback

> **判分策略（重要）**  
> 仅对 `tool=edit` 的事件计算 `Scope/Plan/Evidence`；`tool=plan` 恒 `action=ok`（不计分）。  
> 测试事件（`tool=shell, phase=test`）触发 `TestGuard`；`override.acknowledged=true` 会将违规降级为轻度（避免 warn/rollback）

#### Q2｜跨会话学习（模式卡）
从同一条事件流 +（可选）会话导出的文字材料（Cursor/Claude/Aider 导出）中，提取可迁移的"模式卡"：

```json
{
  "pattern_id": "pc_xxx",
  "triggers": ["问题/任务的关键词"],
  "steps": ["关键步骤"],
  "invariants": ["必须满足的不变量"],
  "anti_patterns": ["禁止/常见误用"],
  "eval_examples": ["相关测试/验证样例"],
  "views": {
    "terse": "专家版要点",
    "guided": "新手版步骤+示例+坑点+验证"
  }
}
```

存入 `data/patterns/*.json`，新任务时检索与注入，实现复用与迁移。

#### Q3｜动态抽象（两档视图路由）
同一卡、双视图：
- **terse**：策略/不变量/禁改规则（适合熟练者）
- **guided**：配置步骤/示例/坑点/必跑测试/例外流程（适合新手或高风险任务）

由 `data/profiles/<user>.json`（自报水平 + 历史首试成功率）自动选择视图。

---

## 📦 目录结构（团队数据湖）

```
data/
└─ runs/<run_id>/                   # 每次会话一个 run（人/日期可入名）
   ├─ raw/                          # 原始证据（只追加，不改写）
   │  ├─ base_commit.txt            # git rev-parse HEAD（基线）
   │  ├─ patch.diff                 # git diff -U0（统一 diff；不必 commit）
   │  ├─ term.log                   # 测试/命令输出（可选）
   │  └─ cursor.md                  # Cursor/Claude/Aider 导出（可选，用作"why/反思"）
   ├─ goal.json                     # 目标图/白名单/检查点/必跑测试
   ├─ events.jsonl                  # 规范化事件（Canonical facts）
   ├─ guards.jsonl                  # 守卫评分与 drift_score（Q1）
   └─ artifacts/
      ├─ reflection.txt             # 反思文本（Q2 原料，可由 LLM 生成）
      ├─ pattern.pc_*.json          # 本 run 抽出的模式卡（Q2）
      └─ view_preview.md            # 视图渲染示例（Q3）
data/patterns/                      # 团队模式库（跨 run 复用）
data/profiles/<user>.json           # 用户画像（Q3 路由）
data/eval/                          # SWE-bench predictions.jsonl 与评测产物
tools/                              
  chat2events.py                    # ★ Chat-only：raw/cursor.md → events.jsonl（planned/applied＋置信度）
  events2guards.py                  # 四守卫（仅 edit 计分；plan 恒 ok）
  patch2events.py                   # Diff 路线：raw/patch.diff → events.jsonl
  term2events.py                    # 解析 raw/term.log → 测试事件
scripts/
  e2e_chat_only.py                  # 一键：chat → events → guards
  e2e_one.py                        # Diff 路线单 run 演示
```

---

## 🧪 端到端示例（"翻译 README 却误改依赖"的典型跑题）

**目标**：只把 README.md 翻译成中文（doc-only）  
**实际**：代理同时修改了 requirements.txt（新增依赖） → 跑题

### 第 0 步｜准备基线与目标

**data/runs/r42/raw/base_commit.txt**：
```
deadbeefcafebabe
```

**data/runs/r42/raw/patch.diff（节选）**：
```diff
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,2 +1,2 @@
-# Project
+# 项目
 Documentation in English.
diff --git a/requirements.txt b/requirements.txt
--- a/requirements.txt
+++ b/requirements.txt
@@ -1 +1,2 @@
+beautifulsoup4
 requests
```

**data/runs/r42/goal.json**：
```json
{
  "run_id": "r42",
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce", "modify", "test", "regress"],
  "required_tests": ["doc_lang_check", "whitelist_diff_check"]
}
```

> **说明**：证据最小集为 base_commit.txt + patch.diff（与 SWE-bench 的"基线快照 + 统一 diff"一致）。无需每步 commit。

### 第 1 步｜规范化与判航

```bash
python tools/patch2events.py data/runs/r42
python tools/term2events.py  data/runs/r42   # 若有 term.log
python tools/events2guards.py data/runs/r42
```

**得到**：
- `events.jsonl`：包含对 README.md 与 requirements.txt 的 edit 事件
- `guards.jsonl`：对 requirements.txt 那一行给出
  - ScopeGuard=1.0（不在 allowed_paths）+ PlanGuard=1.0（modify 阶段不允许）
  - → drift_score ≈ 0.85 ≥ 0.5 → warn/rollback

### 第 2 步｜抽"模式卡"（Q2）

把本次 run 的事件与反思生成模式卡 `pc_doc_only_change`：

```json
{
  "pattern_id": "pc_doc_only_change",
  "triggers": ["documentation-only", "translate readme"],
  "steps": [
    "whitelist README.md/docs/**",
    "forbid requirements.*",
    "run doc_lang_check & whitelist_diff_check"
  ],
  "invariants": ["only whitelisted files changed", "language==target"],
  "anti_patterns": ["edit requirements without consent"],
  "eval_examples": ["doc_lang_check", "whitelist_diff_check"],
  "views": {
    "terse": "Whitelist-only edits; forbid deps change; ensure checks.",
    "guided": "如何配置白名单&语言检测；何时申请例外；常见坑点与验证。"
  }
}
```

复制到 `data/patterns/`，作为团队共享的可复用资产。

### 第 3 步｜动态抽象渲染（Q3）

**data/profiles/jeremy.json（示例）**：
```json
{"user_id":"jeremy","self_report":"intermediate","hist_first_try_success":0.35,"pref":"terse"}
```

**渲染逻辑**：成功率≥阈值或偏好 terse → terse；否则 guided。  
输出到 `artifacts/view_preview.md`，用于 UI 呈现或提示注入。

**到此**，同一份事件数据完成：Q1 判跑题 → Q2 抽模式 → Q3 两档视图。下次遇到"文档/翻译"任务，系统会先天触发该模式，极大降低跑题概率与沟通成本。

---

## 🧰 数据格式（关键文件）

### goal.json
```json
{
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce","modify","test","regress"],
  "required_tests": ["doc_lang_check","whitelist_diff_check"]
}
```

### events.jsonl（每行一个 JSON）
```json
{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit",
 "where":{"path":"README.md"},"what":{"diff":"(omitted)"},"why":"from patch.diff","evidence":{}}
{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit",
 "where":{"path":"requirements.txt"},"what":{"diff":"(omitted)"},"why":"(none)","evidence":{}}
{"id":"e1001","run_id":"r42","step":1001,"phase":"test","tool":"shell",
 "cmd":"pytest -k doc_lang_check"}
```

**Chat‑only 下若仅有"计划修改"，则为：**
```json
{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan",
 "where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}
```

> **说明**：`tool=plan` 不计分，仅留痕；只有 `tool=edit` 会进入 Q1 守卫判分

### guards.jsonl
```json
{"run_id":"r42","step":1,"scope_guard":0.0,"plan_guard":0.0,"test_guard":0.0,"evidence_guard":0.0,"drift_score":0.0,"action":"ok","file":"README.md"}
{"run_id":"r42","step":2,"scope_guard":1.0,"plan_guard":1.0,"test_guard":0.0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt"}
```

### 模式卡 pc_*.json
见上方"抽卡"示例。

### 用户画像 profiles/*.json
```json
{"user_id":"<id>","self_report":"novice|intermediate|expert","hist_first_try_success":0.42,"pref":"guided|terse"}
```


---

## ⚙️ 最小可用脚本（MVP）

你可以先手工填充 `events.jsonl`/`guards.jsonl` 跑通；再用下面脚本自动化。

- `tools/patch2events.py`：解析 `raw/patch.diff` → 生成 edit 事件（每文件 1 条）
- `tools/term2events.py`：解析 `raw/term.log` → 追加 shell/test 事件
- `tools/events2guards.py`：按 `goal.json` 计算四守卫与 drift_score（≥0.5 → warn）
- `agent/reflexion.py`：读取 `cursor.md`（如有）与 events，生成简要反思文本
- `agent/extract_card.py`：反思 → 模式卡（结构化 JSON）
- `q2_memory/retrieve.py`：依据 objective/关键词检索最匹配模式
- `q3_views/render.py`：依据用户画像选择 terse/guided 并渲染
- `scripts/e2e_cursor_doc_task.py`：一键端到端（示例 r42）

---

## 🧪 评测（社区对齐 + 自定义指标）

### 社区对齐：SWE-bench
- 生成 `data/eval/predictions.jsonl`（每行 `{"instance_id","model_patch"}`），用官方 harness 评 %Resolved
- 我们本地的 base_commit + unified diff 与它的"基线快照 + 统一 diff"一致

### 我们新增指标（体现 Q2/Q3/Q1 价值）
- **Q2**：模式复用率、首试成功率↑、平均回合数/用时↓
- **Q3**：视图匹配度（guided 对新手更稳、terse 不打扰专家）
- **Q1**：偏航检出率、误报率、偏航恢复时间（warn→回到正确 checkpoint 的步数/秒）

### 消融（Ablation）
```
baseline → +pattern → +pattern+views → +pattern+views+guards
```
在同一批任务上成对比较，展示复用与守卫带来的复利收益。

---

## 🗺️ 实施计划（4 周样例）

### Week 1｜打底
搭事件总线；采 3–5 个真实案例，手工沉淀 3 张模式卡（如：空指针防护、依赖冲突、off-by-one）。

### Week 2｜能用
接检索+注入；新任务自动推荐模式卡（先用 terse）；打通最小 Q1 守卫（4 checkpoint）。

### Week 3｜过 Gate
上动态抽象路由（画像=自报水平 + 历史成功率）；完成"相似任务首试成功率显著提升"演示与 ablation。

### Week 4｜打磨
扩大到 8–10 张模式卡；补"偏航恢复时间/复用率"可视化；记录失败案例与改进方向。

> **Q1 坚持"最低可用"**：4 checkpoint + 2 条硬规则（白/黑名单；未过前置测试禁止合并）。把时间投给 Q2/Q3。

---

## 🧑‍🤝‍🧑 团队 SOP（最简可执行）

1. **每次会话结束至少落 3 件**：
   `raw/base_commit.txt`、`raw/patch.diff`、`goal.json`（可选：`raw/term.log`、`raw/cursor.md`）

2. **跑脚本**：
   ```bash
   python tools/patch2events.py data/runs/<run_id>
   python tools/term2events.py  data/runs/<run_id>   # 若有 term.log
   python tools/events2guards.py data/runs/<run_id>
   ```

3. **通过/有价值 → 抽卡**：生成 `artifacts/pattern.*.json` 并复制到 `data/patterns/`

4. **周会汇总** `guards.jsonl` 为"偏航榜单"，共建与复用模式卡

5. **每两周做一次** SWE-bench Lite/Verified 小规模对齐评测 + 我们指标报表

---

## ❓ FAQ

### 必须每次 commit 吗？
不需要。`git diff -U0` + `git rev-parse HEAD` 就足以作为"可复现实锤"。Commit 有助于审计与回滚，但不是 Q1/Q2/Q3 的硬依赖。

### Cursor 导出能当"事实来源"吗？
建议只作"why/反思"；"改了什么/是否通过"以 `patch.diff` 与测试日志为准。

### 和 RAG 有什么不同？
RAG 一般检索静态知识；本系统沉淀的是你团队亲手做成的"可复用做法"（模式卡），是经验资产。

### 如何防止模式卡误触发？
通过 triggers 细化关键词/正则；在检索后加入人工确认或风险打分（约束冲突时降权/不注入）。

### 误报的偏航提醒如何处理？
UI 提供"我确认需要"按钮并记录为例外证据，用于改进 EvidenceGuard 与模式卡的 anti_patterns。

---

## ⚠️ 风险与边界

- 事件抽取过于粗糙可能导致误报/漏报；先从**"白名单 + 必跑测试"**的硬规则开始
- 模式卡过多会稀释检索精度；以"有明显 uplift"为标准进入模式库
- 用户画像初期可简单（自报 + 首试成功率）；后续再升级为偏好学习

---

## 🧭 TL;DR（落地步骤）

1. **落证据**：`base_commit.txt` + `patch.diff` (+ `term.log` + `cursor.md`)
2. **目标**：写 `goal.json`（白名单 + 检查点 + 必跑测试）
3. **生成**：`events.jsonl` → `guards.jsonl`，大于阈值则 warn/rollback
4. **沉淀**：抽"模式卡"，放入 `data/patterns/`，下次自动检索触发
5. **呈现**：按 `profiles/<user>.json` 渲染 terse/guided 两档视图
6. **评测**：SWE-bench %Resolved + 我们的 Q1/Q2/Q3 指标与 ablation

**同一份事件数据，三件事一次到位**：不跑题、能复用、会因人施教。

```

```markdown
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
初学者偏好步骤与示例，资深更需要策略与不变量。代理**难以按"用户水平 × 任务难度"**自动调节抽象层级，输出要么啰嗦、要么含糊。

### 3. 长任务易跑偏（Q1）
多步修复/重构中常发生"只要改文档，却去改依赖"等跑题行为，缺少目标-检查点-守卫的持续对齐与回滚能力。

**目标**：把编程代理从"一次性助手"，升级为"会成长、会复用、会自我约束"的合作者。

---

## 🏗️ 统一方案（同一底座，三段合一）

### 共同底座：事件总线（Event Bus）＋ 目标图（Goal Graph）
- **事件总线**：按步骤记录 where/what/why/evidence（改了什么、为何改、证据/日志）
- **目标图**：四检查点 复现→修改→测试→回归，定义允许动作、白/黑名单与验收条件

### 采集与规范化：两条等价路径

我们支持两条并行但等价的数据采集路径：

**1) Chat‑only 路线（推荐）**
- 原始输入：`raw/cursor.md`（Cursor 导出聊天，无需 git/diff）
- 工具：`tools/chat2events.py`
- 产物：`events.jsonl`（将自然对话提取为事件）
  - **已实施修改** → `tool=edit, phase=modify`（进入 Q1 计分）
  - **计划修改** → `tool=plan, phase=modify`（仅留痕，**不计分**）
  - **测试执行** → `tool=shell, phase=test`（触发 TestGuard）
- 当提取结果置信度低或空缺时，可选启用轻量 `git diff --name-only` 作**兜底校验**

**2) Diff 路线**
- 原始输入：`raw/patch.diff`（统一 diff）和可选 `raw/term.log`
- 工具：`tools/patch2events.py`、`tools/term2events.py`
- 产物：`events.jsonl`（每个文件 1 条 `tool=edit` 事件；`term.log` 生成测试事件）

**两条路线后续完全一致**：`events.jsonl` + `goal.json` → `tools/events2guards.py` → `guards.jsonl`

### 三个能力如何由同一数据产生

#### Q1｜执行监控/偏航守卫
读取 `events.jsonl` + `goal.json`，计算：
- **ScopeGuard**：编辑的文件是否在 allowed_paths
- **PlanGuard**：当前 checkpoint 是否允许此类动作
- **TestGuard**：必跑测试是否执行且通过
- **EvidenceGuard**：修改阶段是否引用相关证据

合成 `drift_score = 0.4*scope + 0.3*plan + 0.2*test + 0.1*evidence`；≥阈值（如 0.5）→ warn/rollback

> **判分策略（重要）**  
> 仅对 `tool=edit` 的事件计算 `Scope/Plan/Evidence`；`tool=plan` 恒 `action=ok`（不计分）。  
> 测试事件（`tool=shell, phase=test`）触发 `TestGuard`；`override.acknowledged=true` 会将违规降级为轻度（避免 warn/rollback）

#### Q2｜跨会话学习（模式卡）
从同一条事件流 +（可选）会话导出的文字材料（Cursor/Claude/Aider 导出）中，提取可迁移的"模式卡"：

```json
{
  "pattern_id": "pc_xxx",
  "triggers": ["问题/任务的关键词"],
  "steps": ["关键步骤"],
  "invariants": ["必须满足的不变量"],
  "anti_patterns": ["禁止/常见误用"],
  "eval_examples": ["相关测试/验证样例"],
  "views": {
    "terse": "专家版要点",
    "guided": "新手版步骤+示例+坑点+验证"
  }
}
```

存入 `data/patterns/*.json`，新任务时检索与注入，实现复用与迁移。

#### Q3｜动态抽象（两档视图路由）
同一卡、双视图：
- **terse**：策略/不变量/禁改规则（适合熟练者）
- **guided**：配置步骤/示例/坑点/必跑测试/例外流程（适合新手或高风险任务）

由 `data/profiles/<user>.json`（自报水平 + 历史首试成功率）自动选择视图。

---

## 📦 目录结构（团队数据湖）

```
data/
└─ runs/<run_id>/                   # 每次会话一个 run（人/日期可入名）
   ├─ raw/                          # 原始证据（只追加，不改写）
   │  ├─ base_commit.txt            # git rev-parse HEAD（基线）
   │  ├─ patch.diff                 # git diff -U0（统一 diff；不必 commit）
   │  ├─ term.log                   # 测试/命令输出（可选）
   │  └─ cursor.md                  # Cursor/Claude/Aider 导出（可选，用作"why/反思"）
   ├─ goal.json                     # 目标图/白名单/检查点/必跑测试
   ├─ events.jsonl                  # 规范化事件（Canonical facts）
   ├─ guards.jsonl                  # 守卫评分与 drift_score（Q1）
   └─ artifacts/
      ├─ reflection.txt             # 反思文本（Q2 原料，可由 LLM 生成）
      ├─ pattern.pc_*.json          # 本 run 抽出的模式卡（Q2）
      └─ view_preview.md            # 视图渲染示例（Q3）
data/patterns/                      # 团队模式库（跨 run 复用）
data/profiles/<user>.json           # 用户画像（Q3 路由）
data/eval/                          # SWE-bench predictions.jsonl 与评测产物
tools/                              
  chat2events.py                    # ★ Chat-only：raw/cursor.md → events.jsonl（planned/applied＋置信度）
  events2guards.py                  # 四守卫（仅 edit 计分；plan 恒 ok）
  patch2events.py                   # Diff 路线：raw/patch.diff → events.jsonl
  term2events.py                    # 解析 raw/term.log → 测试事件
scripts/
  e2e_chat_only.py                  # 一键：chat → events → guards
  e2e_one.py                        # Diff 路线单 run 演示
```

---

## 🧪 端到端示例（"翻译 README 却误改依赖"的典型跑题）

**目标**：只把 README.md 翻译成中文（doc-only）  
**实际**：代理同时修改了 requirements.txt（新增依赖） → 跑题

### 第 0 步｜准备基线与目标

**data/runs/r42/raw/base_commit.txt**：
```
deadbeefcafebabe
```

**data/runs/r42/raw/patch.diff（节选）**：
```diff
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,2 +1,2 @@
-# Project
+# 项目
 Documentation in English.
diff --git a/requirements.txt b/requirements.txt
--- a/requirements.txt
+++ b/requirements.txt
@@ -1 +1,2 @@
+beautifulsoup4
 requests
```

**data/runs/r42/goal.json**：
```json
{
  "run_id": "r42",
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce", "modify", "test", "regress"],
  "required_tests": ["doc_lang_check", "whitelist_diff_check"]
}
```

> **说明**：证据最小集为 base_commit.txt + patch.diff（与 SWE-bench 的"基线快照 + 统一 diff"一致）。无需每步 commit。

### 第 1 步｜规范化与判航

```bash
python tools/patch2events.py data/runs/r42
python tools/term2events.py  data/runs/r42   # 若有 term.log
python tools/events2guards.py data/runs/r42
```

**得到**：
- `events.jsonl`：包含对 README.md 与 requirements.txt 的 edit 事件
- `guards.jsonl`：对 requirements.txt 那一行给出
  - ScopeGuard=1.0（不在 allowed_paths）+ PlanGuard=1.0（modify 阶段不允许）
  - → drift_score ≈ 0.85 ≥ 0.5 → warn/rollback

### 第 2 步｜抽"模式卡"（Q2）

把本次 run 的事件与反思生成模式卡 `pc_doc_only_change`：

```json
{
  "pattern_id": "pc_doc_only_change",
  "triggers": ["documentation-only", "translate readme"],
  "steps": [
    "whitelist README.md/docs/**",
    "forbid requirements.*",
    "run doc_lang_check & whitelist_diff_check"
  ],
  "invariants": ["only whitelisted files changed", "language==target"],
  "anti_patterns": ["edit requirements without consent"],
  "eval_examples": ["doc_lang_check", "whitelist_diff_check"],
  "views": {
    "terse": "Whitelist-only edits; forbid deps change; ensure checks.",
    "guided": "如何配置白名单&语言检测；何时申请例外；常见坑点与验证。"
  }
}
```

复制到 `data/patterns/`，作为团队共享的可复用资产。

### 第 3 步｜动态抽象渲染（Q3）

**data/profiles/jeremy.json（示例）**：
```json
{"user_id":"jeremy","self_report":"intermediate","hist_first_try_success":0.35,"pref":"terse"}
```

**渲染逻辑**：成功率≥阈值或偏好 terse → terse；否则 guided。  
输出到 `artifacts/view_preview.md`，用于 UI 呈现或提示注入。

**到此**，同一份事件数据完成：Q1 判跑题 → Q2 抽模式 → Q3 两档视图。下次遇到"文档/翻译"任务，系统会先天触发该模式，极大降低跑题概率与沟通成本。

---

## 🧰 数据格式（关键文件）

### goal.json
```json
{
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce","modify","test","regress"],
  "required_tests": ["doc_lang_check","whitelist_diff_check"]
}
```

### events.jsonl（每行一个 JSON）
```json
{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit",
 "where":{"path":"README.md"},"what":{"diff":"(omitted)"},"why":"from patch.diff","evidence":{}}
{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit",
 "where":{"path":"requirements.txt"},"what":{"diff":"(omitted)"},"why":"(none)","evidence":{}}
{"id":"e1001","run_id":"r42","step":1001,"phase":"test","tool":"shell",
 "cmd":"pytest -k doc_lang_check"}
```

**Chat‑only 下若仅有"计划修改"，则为：**
```json
{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan",
 "where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}
```

> **说明**：`tool=plan` 不计分，仅留痕；只有 `tool=edit` 会进入 Q1 守卫判分

### guards.jsonl
```json
{"run_id":"r42","step":1,"scope_guard":0.0,"plan_guard":0.0,"test_guard":0.0,"evidence_guard":0.0,"drift_score":0.0,"action":"ok","file":"README.md"}
{"run_id":"r42","step":2,"scope_guard":1.0,"plan_guard":1.0,"test_guard":0.0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt"}
```

### 模式卡 pc_*.json
见上方"抽卡"示例。

### 用户画像 profiles/*.json
```json
{"user_id":"<id>","self_report":"novice|intermediate|expert","hist_first_try_success":0.42,"pref":"guided|terse"}
```


---

## ⚙️ 最小可用脚本（MVP）

### Chat‑only（无需 git/diff）
```bash
# 准备
# 1) 导出 Cursor 对话到 data/runs/<run_id>/raw/cursor.md
# 2) 写 data/runs/<run_id>/goal.json（白/黑名单、必跑测试）

python tools/chat2events.py data/runs/<run_id>   # 生成 events.jsonl（plan/edit/test）
python tools/events2guards.py data/runs/<run_id> # 生成 guards.jsonl（仅 edit 计分）

# 或一键：
python scripts/e2e_chat_only.py <run_id>
```

### Diff 路线
```bash
python tools/patch2events.py data/runs/<run_id>
python tools/term2events.py  data/runs/<run_id>   # 若有 term.log
python tools/events2guards.py data/runs/<run_id>
```

**后续工作（占位）**：
- `agent/reflexion.py`：读取 `cursor.md`（如有）与 events，生成简要反思文本
- `agent/extract_card.py`：反思 → 模式卡（结构化 JSON）
- `q2_memory/retrieve.py`：依据 objective/关键词检索最匹配模式
- `q3_views/render.py`：依据用户画像选择 terse/guided 并渲染

---

## 🧪 评测（社区对齐 + 自定义指标）

### 社区对齐：SWE-bench
- 生成 `data/eval/predictions.jsonl`（每行 `{"instance_id","model_patch"}`），用官方 harness 评 %Resolved
- 我们本地的 base_commit + unified diff 与它的"基线快照 + 统一 diff"一致

### 我们新增指标（体现 Q2/Q3/Q1 价值）
- **Q2**：模式复用率、首试成功率↑、平均回合数/用时↓
- **Q3**：视图匹配度（guided 对新手更稳、terse 不打扰专家）
- **Q1**：偏航检出率、误报率、偏航恢复时间（warn→回到正确 checkpoint 的步数/秒）

### 消融（Ablation）
```
baseline → +pattern → +pattern+views → +pattern+views+guards
```
在同一批任务上成对比较，展示复用与守卫带来的复利收益。

---

## 🗺️ 实施计划（4 周样例）

### Week 1｜打底
搭事件总线；采 3–5 个真实案例，手工沉淀 3 张模式卡（如：空指针防护、依赖冲突、off-by-one）。

### Week 2｜能用
接检索+注入；新任务自动推荐模式卡（先用 terse）；打通最小 Q1 守卫（4 checkpoint）。

### Week 3｜过 Gate
上动态抽象路由（画像=自报水平 + 历史成功率）；完成"相似任务首试成功率显著提升"演示与 ablation。

### Week 4｜打磨
扩大到 8–10 张模式卡；补"偏航恢复时间/复用率"可视化；记录失败案例与改进方向。

> **Q1 坚持"最低可用"**：4 checkpoint + 2 条硬规则（白/黑名单；未过前置测试禁止合并）。把时间投给 Q2/Q3。

---

## 🧑‍🤝‍🧑 团队 SOP（最简可执行）

1. **每次会话结束至少落 3 件**：
   `raw/base_commit.txt`、`raw/patch.diff`、`goal.json`（可选：`raw/term.log`、`raw/cursor.md`）

2. **跑脚本**：
   ```bash
   python tools/patch2events.py data/runs/<run_id>
   python tools/term2events.py  data/runs/<run_id>   # 若有 term.log
   python tools/events2guards.py data/runs/<run_id>
   ```

3. **通过/有价值 → 抽卡**：生成 `artifacts/pattern.*.json` 并复制到 `data/patterns/`

4. **周会汇总** `guards.jsonl` 为"偏航榜单"，共建与复用模式卡

5. **每两周做一次** SWE-bench Lite/Verified 小规模对齐评测 + 我们指标报表

---

## ❓ FAQ

### 必须每次 commit 吗？
不需要。`git diff -U0` + `git rev-parse HEAD` 就足以作为"可复现实锤"。Commit 有助于审计与回滚，但不是 Q1/Q2/Q3 的硬依赖。

### Cursor 导出能当"事实来源"吗？
建议只作"why/反思"；"改了什么/是否通过"以 `patch.diff` 与测试日志为准。

### 和 RAG 有什么不同？
RAG 一般检索静态知识；本系统沉淀的是你团队亲手做成的"可复用做法"（模式卡），是经验资产。

### 如何防止模式卡误触发？
通过 triggers 细化关键词/正则；在检索后加入人工确认或风险打分（约束冲突时降权/不注入）。

### 误报的偏航提醒如何处理？
UI 提供"我确认需要"按钮并记录为例外证据，用于改进 EvidenceGuard 与模式卡的 anti_patterns。

---

## ⚠️ 风险与边界

- 事件抽取过于粗糙可能导致误报/漏报；先从**"白名单 + 必跑测试"**的硬规则开始
- 模式卡过多会稀释检索精度；以"有明显 uplift"为标准进入模式库
- 用户画像初期可简单（自报 + 首试成功率）；后续再升级为偏好学习

---

## 🧭 TL;DR（落地步骤）

1. **落证据**：`base_commit.txt` + `patch.diff` (+ `term.log` + `cursor.md`)
2. **目标**：写 `goal.json`（白名单 + 检查点 + 必跑测试）
3. **生成**：`events.jsonl` → `guards.jsonl`，大于阈值则 warn/rollback
4. **沉淀**：抽"模式卡"，放入 `data/patterns/`，下次自动检索触发
5. **呈现**：按 `profiles/<user>.json` 渲染 terse/guided 两档视图
6. **评测**：SWE-bench %Resolved + 我们的 Q1/Q2/Q3 指标与 ablation

**同一份事件数据，三件事一次到位**：不跑题、能复用、会因人施教。

```

```markdown
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
初学者偏好步骤与示例，资深更需要策略与不变量。代理**难以按"用户水平 × 任务难度"**自动调节抽象层级，输出要么啰嗦、要么含糊。

### 3. 长任务易跑偏（Q1）
多步修复/重构中常发生"只要改文档，却去改依赖"等跑题行为，缺少目标-检查点-守卫的持续对齐与回滚能力。

**目标**：把编程代理从"一次性助手"，升级为"会成长、会复用、会自我约束"的合作者。

---

## 🏗️ 统一方案（同一底座，三段合一）

### 共同底座：事件总线（Event Bus）＋ 目标图（Goal Graph）
- **事件总线**：按步骤记录 where/what/why/evidence（改了什么、为何改、证据/日志）
- **目标图**：四检查点 复现→修改→测试→回归，定义允许动作、白/黑名单与验收条件

### 采集与规范化：两条等价路径

我们支持两条并行但等价的数据采集路径：

**1) Chat‑only 路线（推荐）**
- 原始输入：`raw/cursor.md`（Cursor 导出聊天，无需 git/diff）
- 工具：`tools/chat2events.py`
- 产物：`events.jsonl`（将自然对话提取为事件）
  - **已实施修改** → `tool=edit, phase=modify`（进入 Q1 计分）
  - **计划修改** → `tool=plan, phase=modify`（仅留痕，**不计分**）
  - **测试执行** → `tool=shell, phase=test`（触发 TestGuard）
- 当提取结果置信度低或空缺时，可选启用轻量 `git diff --name-only` 作**兜底校验**

**2) Diff 路线**
- 原始输入：`raw/patch.diff`（统一 diff）和可选 `raw/term.log`
- 工具：`tools/patch2events.py`、`tools/term2events.py`
- 产物：`events.jsonl`（每个文件 1 条 `tool=edit` 事件；`term.log` 生成测试事件）

**两条路线后续完全一致**：`events.jsonl` + `goal.json` → `tools/events2guards.py` → `guards.jsonl`

### 三个能力如何由同一数据产生

#### Q1｜执行监控/偏航守卫
读取 `events.jsonl` + `goal.json`，计算：
- **ScopeGuard**：编辑的文件是否在 allowed_paths
- **PlanGuard**：当前 checkpoint 是否允许此类动作
- **TestGuard**：必跑测试是否执行且通过
- **EvidenceGuard**：修改阶段是否引用相关证据

合成 `drift_score = 0.4*scope + 0.3*plan + 0.2*test + 0.1*evidence`；≥阈值（如 0.5）→ warn/rollback

> **判分策略（重要）**  
> 仅对 `tool=edit` 的事件计算 `Scope/Plan/Evidence`；`tool=plan` 恒 `action=ok`（不计分）。  
> 测试事件（`tool=shell, phase=test`）触发 `TestGuard`；`override.acknowledged=true` 会将违规降级为轻度（避免 warn/rollback）

#### Q2｜跨会话学习（模式卡）
从同一条事件流 +（可选）会话导出的文字材料（Cursor/Claude/Aider 导出）中，提取可迁移的"模式卡"：

```json
{
  "pattern_id": "pc_xxx",
  "triggers": ["问题/任务的关键词"],
  "steps": ["关键步骤"],
  "invariants": ["必须满足的不变量"],
  "anti_patterns": ["禁止/常见误用"],
  "eval_examples": ["相关测试/验证样例"],
  "views": {
    "terse": "专家版要点",
    "guided": "新手版步骤+示例+坑点+验证"
  }
}
```

存入 `data/patterns/*.json`，新任务时检索与注入，实现复用与迁移。

#### Q3｜动态抽象（两档视图路由）
同一卡、双视图：
- **terse**：策略/不变量/禁改规则（适合熟练者）
- **guided**：配置步骤/示例/坑点/必跑测试/例外流程（适合新手或高风险任务）

由 `data/profiles/<user>.json`（自报水平 + 历史首试成功率）自动选择视图。

---

## 📦 目录结构（团队数据湖）

```
data/
└─ runs/<run_id>/                   # 每次会话一个 run（人/日期可入名）
   ├─ raw/                          # 原始证据（只追加，不改写）
   │  ├─ base_commit.txt            # git rev-parse HEAD（基线）
   │  ├─ patch.diff                 # git diff -U0（统一 diff；不必 commit）
   │  ├─ term.log                   # 测试/命令输出（可选）
   │  └─ cursor.md                  # Cursor/Claude/Aider 导出（可选，用作"why/反思"）
   ├─ goal.json                     # 目标图/白名单/检查点/必跑测试
   ├─ events.jsonl                  # 规范化事件（Canonical facts）
   ├─ guards.jsonl                  # 守卫评分与 drift_score（Q1）
   └─ artifacts/
      ├─ reflection.txt             # 反思文本（Q2 原料，可由 LLM 生成）
      ├─ pattern.pc_*.json          # 本 run 抽出的模式卡（Q2）
      └─ view_preview.md            # 视图渲染示例（Q3）
data/patterns/                      # 团队模式库（跨 run 复用）
data/profiles/<user>.json           # 用户画像（Q3 路由）
data/eval/                          # SWE-bench predictions.jsonl 与评测产物
tools/                              
  chat2events.py                    # ★ Chat-only：raw/cursor.md → events.jsonl（planned/applied＋置信度）
  events2guards.py                  # 四守卫（仅 edit 计分；plan 恒 ok）
  patch2events.py                   # Diff 路线：raw/patch.diff → events.jsonl
  term2events.py                    # 解析 raw/term.log → 测试事件
scripts/
  e2e_chat_only.py                  # 一键：chat → events → guards
  e2e_one.py                        # Diff 路线单 run 演示
```

---

## 🧪 端到端示例（"翻译 README 却误改依赖"的典型跑题）

**目标**：只把 README.md 翻译成中文（doc-only）  
**实际**：代理同时修改了 requirements.txt（新增依赖） → 跑题

### 第 0 步｜准备基线与目标

**data/runs/r42/raw/base_commit.txt**：
```
deadbeefcafebabe
```

**data/runs/r42/raw/patch.diff（节选）**：
```diff
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,2 +1,2 @@
-# Project
+# 项目
 Documentation in English.
diff --git a/requirements.txt b/requirements.txt
--- a/requirements.txt
+++ b/requirements.txt
@@ -1 +1,2 @@
+beautifulsoup4
 requests
```

**data/runs/r42/goal.json**：
```json
{
  "run_id": "r42",
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce", "modify", "test", "regress"],
  "required_tests": ["doc_lang_check", "whitelist_diff_check"]
}
```

> **说明**：证据最小集为 base_commit.txt + patch.diff（与 SWE-bench 的"基线快照 + 统一 diff"一致）。无需每步 commit。

### 第 1 步｜规范化与判航

```bash
python tools/patch2events.py data/runs/r42
python tools/term2events.py  data/runs/r42   # 若有 term.log
python tools/events2guards.py data/runs/r42
```

**得到**：
- `events.jsonl`：包含对 README.md 与 requirements.txt 的 edit 事件
- `guards.jsonl`：对 requirements.txt 那一行给出
  - ScopeGuard=1.0（不在 allowed_paths）+ PlanGuard=1.0（modify 阶段不允许）
  - → drift_score ≈ 0.85 ≥ 0.5 → warn/rollback

### 第 2 步｜抽"模式卡"（Q2）

把本次 run 的事件与反思生成模式卡 `pc_doc_only_change`：

```json
{
  "pattern_id": "pc_doc_only_change",
  "triggers": ["documentation-only", "translate readme"],
  "steps": [
    "whitelist README.md/docs/**",
    "forbid requirements.*",
    "run doc_lang_check & whitelist_diff_check"
  ],
  "invariants": ["only whitelisted files changed", "language==target"],
  "anti_patterns": ["edit requirements without consent"],
  "eval_examples": ["doc_lang_check", "whitelist_diff_check"],
  "views": {
    "terse": "Whitelist-only edits; forbid deps change; ensure checks.",
    "guided": "如何配置白名单&语言检测；何时申请例外；常见坑点与验证。"
  }
}
```

复制到 `data/patterns/`，作为团队共享的可复用资产。

### 第 3 步｜动态抽象渲染（Q3）

**data/profiles/jeremy.json（示例）**：
```json
{"user_id":"jeremy","self_report":"intermediate","hist_first_try_success":0.35,"pref":"terse"}
```

**渲染逻辑**：成功率≥阈值或偏好 terse → terse；否则 guided。  
输出到 `artifacts/view_preview.md`，用于 UI 呈现或提示注入。

**到此**，同一份事件数据完成：Q1 判跑题 → Q2 抽模式 → Q3 两档视图。下次遇到"文档/翻译"任务，系统会先天触发该模式，极大降低跑题概率与沟通成本。

---

## 🧰 数据格式（关键文件）

### goal.json
```json
{
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce","modify","test","regress"],
  "required_tests": ["doc_lang_check","whitelist_diff_check"]
}
```

### events.jsonl（每行一个 JSON）
```json
{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit",
 "where":{"path":"README.md"},"what":{"diff":"(omitted)"},"why":"from patch.diff","evidence":{}}
{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit",
 "where":{"path":"requirements.txt"},"what":{"diff":"(omitted)"},"why":"(none)","evidence":{}}
{"id":"e1001","run_id":"r42","step":1001,"phase":"test","tool":"shell",
 "cmd":"pytest -k doc_lang_check"}
```

**Chat‑only 下若仅有"计划修改"，则为：**
```json
{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan",
 "where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}
```

> **说明**：`tool=plan` 不计分，仅留痕；只有 `tool=edit` 会进入 Q1 守卫判分

### guards.jsonl
```json
{"run_id":"r42","step":1,"scope_guard":0.0,"plan_guard":0.0,"test_guard":0.0,"evidence_guard":0.0,"drift_score":0.0,"action":"ok","file":"README.md"}
{"run_id":"r42","step":2,"scope_guard":1.0,"plan_guard":1.0,"test_guard":0.0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt"}
```

### 模式卡 pc_*.json
见上方"抽卡"示例。

### 用户画像 profiles/*.json
```json
{"user_id":"<id>","self_report":"novice|intermediate|expert","hist_first_try_success":0.42,"pref":"guided|terse"}
```


---

## ⚙️ 最小可用脚本（MVP）

### Chat‑only（无需 git/diff）
```bash
# 准备
# 1) 导出 Cursor 对话到 data/runs/<run_id>/raw/cursor.md
# 2) 写 data/runs/<run_id>/goal.json（白/黑名单、必跑测试）

python tools/chat2events.py data/runs/<run_id>   # 生成 events.jsonl（plan/edit/test）
python tools/events2guards.py data/runs/<run_id> # 生成 guards.jsonl（仅 edit 计分）

# 或一键：
python scripts/e2e_chat_only.py <run_id>
```

### Diff 路线
```bash
python tools/patch2events.py data/runs/<run_id>
python tools/term2events.py  data/runs/<run_id>   # 若有 term.log
python tools/events2guards.py data/runs/<run_id>
```

**后续工作（占位）**：
- `agent/reflexion.py`：读取 `cursor.md`（如有）与 events，生成简要反思文本
- `agent/extract_card.py`：反思 → 模式卡（结构化 JSON）
- `q2_memory/retrieve.py`：依据 objective/关键词检索最匹配模式
- `q3_views/render.py`：依据用户画像选择 terse/guided 并渲染

---

## 🧪 评测（社区对齐 + 自定义指标）

### 社区对齐：SWE-bench
- 生成 `data/eval/predictions.jsonl`（每行 `{"instance_id","model_patch"}`），用官方 harness 评 %Resolved
- 我们本地的 base_commit + unified diff 与它的"基线快照 + 统一 diff"一致

### 我们新增指标（体现 Q2/Q3/Q1 价值）
- **Q2**：模式复用率、首试成功率↑、平均回合数/用时↓
- **Q3**：视图匹配度（guided 对新手更稳、terse 不打扰专家）
- **Q1**：偏航检出率、误报率、偏航恢复时间（warn→回到正确 checkpoint 的步数/秒）

### 消融（Ablation）
```
baseline → +pattern → +pattern+views → +pattern+views+guards
```
在同一批任务上成对比较，展示复用与守卫带来的复利收益。

---

## 🗺️ 实施计划（4 周样例）

### Week 1｜打底
搭事件总线；采 3–5 个真实案例，手工沉淀 3 张模式卡（如：空指针防护、依赖冲突、off-by-one）。

### Week 2｜能用
接检索+注入；新任务自动推荐模式卡（先用 terse）；打通最小 Q1 守卫（4 checkpoint）。

### Week 3｜过 Gate
上动态抽象路由（画像=自报水平 + 历史成功率）；完成"相似任务首试成功率显著提升"演示与 ablation。

### Week 4｜打磨
扩大到 8–10 张模式卡；补"偏航恢复时间/复用率"可视化；记录失败案例与改进方向。

> **Q1 坚持"最低可用"**：4 checkpoint + 2 条硬规则（白/黑名单；未过前置测试禁止合并）。把时间投给 Q2/Q3。

---

## 🧑‍🤝‍🧑 团队 SOP（最简可执行）

1. **每次会话结束至少落 3 件**：
   `raw/base_commit.txt`、`raw/patch.diff`、`goal.json`（可选：`raw/term.log`、`raw/cursor.md`）

2. **跑脚本**：
   ```bash
   python tools/patch2events.py data/runs/<run_id>
   python tools/term2events.py  data/runs/<run_id>   # 若有 term.log
   python tools/events2guards.py data/runs/<run_id>
   ```

3. **通过/有价值 → 抽卡**：生成 `artifacts/pattern.*.json` 并复制到 `data/patterns/`

4. **周会汇总** `guards.jsonl` 为"偏航榜单"，共建与复用模式卡

5. **每两周做一次** SWE-bench Lite/Verified 小规模对齐评测 + 我们指标报表

---

## ❓ FAQ

### 必须每次 commit 吗？
不需要。`git diff -U0` + `git rev-parse HEAD` 就足以作为"可复现实锤"。Commit 有助于审计与回滚，但不是 Q1/Q2/Q3 的硬依赖。

### Cursor 导出能当"事实来源"吗？
**可以**，在 Chat‑only 模式下满足以下任一条件即可视为"已实施修改（edit）"的证据：
- 明确表述"已修改/updated/changed/edited/已应用"等；
- 展示具体代码片段/patch；
- 关联出现并通过了对应测试命令。

若仅出现"计划修改/建议/可以/将要"等，则标记为 `tool=plan`（不计分，留痕）。  
当提取结果置信度低或空缺时，可**可选**调用 `git diff --name-only` 做兜底校验。

### 和 RAG 有什么不同？
RAG 一般检索静态知识；本系统沉淀的是你团队亲手做成的"可复用做法"（模式卡），是经验资产。

### 如何防止模式卡误触发？
通过 triggers 细化关键词/正则；在检索后加入人工确认或风险打分（约束冲突时降权/不注入）。

### 误报的偏航提醒如何处理？
UI 提供"我确认需要"按钮并记录为例外证据，用于改进 EvidenceGuard 与模式卡的 anti_patterns。

---

## ⚠️ 风险与边界

- 事件抽取过于粗糙可能导致误报/漏报；先从**"白名单 + 必跑测试"**的硬规则开始
- 模式卡过多会稀释检索精度；以"有明显 uplift"为标准进入模式库
- 用户画像初期可简单（自报 + 首试成功率）；后续再升级为偏好学习

---

## 🧭 TL;DR（落地步骤）

1. **落证据**：`base_commit.txt` + `patch.diff` (+ `term.log` + `cursor.md`)
2. **目标**：写 `goal.json`（白名单 + 检查点 + 必跑测试）
3. **生成**：`events.jsonl` → `guards.jsonl`，大于阈值则 warn/rollback
4. **沉淀**：抽"模式卡"，放入 `data/patterns/`，下次自动检索触发
5. **呈现**：按 `profiles/<user>.json` 渲染 terse/guided 两档视图
6. **评测**：SWE-bench %Resolved + 我们的 Q1/Q2/Q3 指标与 ablation

**同一份事件数据，三件事一次到位**：不跑题、能复用、会因人施教。

```

现在让我添加 Chat-only 的端到端示例：


```markdown
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
初学者偏好步骤与示例，资深更需要策略与不变量。代理**难以按"用户水平 × 任务难度"**自动调节抽象层级，输出要么啰嗦、要么含糊。

### 3. 长任务易跑偏（Q1）
多步修复/重构中常发生"只要改文档，却去改依赖"等跑题行为，缺少目标-检查点-守卫的持续对齐与回滚能力。

**目标**：把编程代理从"一次性助手"，升级为"会成长、会复用、会自我约束"的合作者。

---

## 🏗️ 统一方案（同一底座，三段合一）

### 共同底座：事件总线（Event Bus）＋ 目标图（Goal Graph）
- **事件总线**：按步骤记录 where/what/why/evidence（改了什么、为何改、证据/日志）
- **目标图**：四检查点 复现→修改→测试→回归，定义允许动作、白/黑名单与验收条件

### 采集与规范化：两条等价路径

我们支持两条并行但等价的数据采集路径：

**1) Chat‑only 路线（推荐）**
- 原始输入：`raw/cursor.md`（Cursor 导出聊天，无需 git/diff）
- 工具：`tools/chat2events.py`
- 产物：`events.jsonl`（将自然对话提取为事件）
  - **已实施修改** → `tool=edit, phase=modify`（进入 Q1 计分）
  - **计划修改** → `tool=plan, phase=modify`（仅留痕，**不计分**）
  - **测试执行** → `tool=shell, phase=test`（触发 TestGuard）
- 当提取结果置信度低或空缺时，可选启用轻量 `git diff --name-only` 作**兜底校验**

**2) Diff 路线**
- 原始输入：`raw/patch.diff`（统一 diff）和可选 `raw/term.log`
- 工具：`tools/patch2events.py`、`tools/term2events.py`
- 产物：`events.jsonl`（每个文件 1 条 `tool=edit` 事件；`term.log` 生成测试事件）

**两条路线后续完全一致**：`events.jsonl` + `goal.json` → `tools/events2guards.py` → `guards.jsonl`

### 三个能力如何由同一数据产生

#### Q1｜执行监控/偏航守卫
读取 `events.jsonl` + `goal.json`，计算：
- **ScopeGuard**：编辑的文件是否在 allowed_paths
- **PlanGuard**：当前 checkpoint 是否允许此类动作
- **TestGuard**：必跑测试是否执行且通过
- **EvidenceGuard**：修改阶段是否引用相关证据

合成 `drift_score = 0.4*scope + 0.3*plan + 0.2*test + 0.1*evidence`；≥阈值（如 0.5）→ warn/rollback

> **判分策略（重要）**  
> 仅对 `tool=edit` 的事件计算 `Scope/Plan/Evidence`；`tool=plan` 恒 `action=ok`（不计分）。  
> 测试事件（`tool=shell, phase=test`）触发 `TestGuard`；`override.acknowledged=true` 会将违规降级为轻度（避免 warn/rollback）

#### Q2｜跨会话学习（模式卡）
从同一条事件流 +（可选）会话导出的文字材料（Cursor/Claude/Aider 导出）中，提取可迁移的"模式卡"：

```json
{
  "pattern_id": "pc_xxx",
  "triggers": ["问题/任务的关键词"],
  "steps": ["关键步骤"],
  "invariants": ["必须满足的不变量"],
  "anti_patterns": ["禁止/常见误用"],
  "eval_examples": ["相关测试/验证样例"],
  "views": {
    "terse": "专家版要点",
    "guided": "新手版步骤+示例+坑点+验证"
  }
}
```

存入 `data/patterns/*.json`，新任务时检索与注入，实现复用与迁移。

#### Q3｜动态抽象（两档视图路由）
同一卡、双视图：
- **terse**：策略/不变量/禁改规则（适合熟练者）
- **guided**：配置步骤/示例/坑点/必跑测试/例外流程（适合新手或高风险任务）

由 `data/profiles/<user>.json`（自报水平 + 历史首试成功率）自动选择视图。

---

## 📦 目录结构（团队数据湖）

```
data/
└─ runs/<run_id>/                   # 每次会话一个 run（人/日期可入名）
   ├─ raw/                          # 原始证据（只追加，不改写）
   │  ├─ base_commit.txt            # git rev-parse HEAD（基线）
   │  ├─ patch.diff                 # git diff -U0（统一 diff；不必 commit）
   │  ├─ term.log                   # 测试/命令输出（可选）
   │  └─ cursor.md                  # Cursor/Claude/Aider 导出（可选，用作"why/反思"）
   ├─ goal.json                     # 目标图/白名单/检查点/必跑测试
   ├─ events.jsonl                  # 规范化事件（Canonical facts）
   ├─ guards.jsonl                  # 守卫评分与 drift_score（Q1）
   └─ artifacts/
      ├─ reflection.txt             # 反思文本（Q2 原料，可由 LLM 生成）
      ├─ pattern.pc_*.json          # 本 run 抽出的模式卡（Q2）
      └─ view_preview.md            # 视图渲染示例（Q3）
data/patterns/                      # 团队模式库（跨 run 复用）
data/profiles/<user>.json           # 用户画像（Q3 路由）
data/eval/                          # SWE-bench predictions.jsonl 与评测产物
tools/                              
  chat2events.py                    # ★ Chat-only：raw/cursor.md → events.jsonl（planned/applied＋置信度）
  events2guards.py                  # 四守卫（仅 edit 计分；plan 恒 ok）
  patch2events.py                   # Diff 路线：raw/patch.diff → events.jsonl
  term2events.py                    # 解析 raw/term.log → 测试事件
scripts/
  e2e_chat_only.py                  # 一键：chat → events → guards
  e2e_one.py                        # Diff 路线单 run 演示
```

---

## 🧪 端到端示例（"翻译 README 却误改依赖"的典型跑题）

**目标**：只把 README.md 翻译成中文（doc-only）  
**实际**：代理同时修改了 requirements.txt（新增依赖） → 跑题

### 第 0 步｜准备基线与目标

**data/runs/r42/raw/base_commit.txt**：
```
deadbeefcafebabe
```

**data/runs/r42/raw/patch.diff（节选）**：
```diff
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,2 +1,2 @@
-# Project
+# 项目
 Documentation in English.
diff --git a/requirements.txt b/requirements.txt
--- a/requirements.txt
+++ b/requirements.txt
@@ -1 +1,2 @@
+beautifulsoup4
 requests
```

**data/runs/r42/goal.json**：
```json
{
  "run_id": "r42",
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce", "modify", "test", "regress"],
  "required_tests": ["doc_lang_check", "whitelist_diff_check"]
}
```

> **说明**：证据最小集为 base_commit.txt + patch.diff（与 SWE-bench 的"基线快照 + 统一 diff"一致）。无需每步 commit。

### 第 1 步｜规范化与判航

```bash
python tools/patch2events.py data/runs/r42
python tools/term2events.py  data/runs/r42   # 若有 term.log
python tools/events2guards.py data/runs/r42
```

**得到**：
- `events.jsonl`：包含对 README.md 与 requirements.txt 的 edit 事件
- `guards.jsonl`：对 requirements.txt 那一行给出
  - ScopeGuard=1.0（不在 allowed_paths）+ PlanGuard=1.0（modify 阶段不允许）
  - → drift_score ≈ 0.85 ≥ 0.5 → warn/rollback

### 第 2 步｜抽"模式卡"（Q2）

把本次 run 的事件与反思生成模式卡 `pc_doc_only_change`：

```json
{
  "pattern_id": "pc_doc_only_change",
  "triggers": ["documentation-only", "translate readme"],
  "steps": [
    "whitelist README.md/docs/**",
    "forbid requirements.*",
    "run doc_lang_check & whitelist_diff_check"
  ],
  "invariants": ["only whitelisted files changed", "language==target"],
  "anti_patterns": ["edit requirements without consent"],
  "eval_examples": ["doc_lang_check", "whitelist_diff_check"],
  "views": {
    "terse": "Whitelist-only edits; forbid deps change; ensure checks.",
    "guided": "如何配置白名单&语言检测；何时申请例外；常见坑点与验证。"
  }
}
```

复制到 `data/patterns/`，作为团队共享的可复用资产。

### 第 3 步｜动态抽象渲染（Q3）

**data/profiles/jeremy.json（示例）**：
```json
{"user_id":"jeremy","self_report":"intermediate","hist_first_try_success":0.35,"pref":"terse"}
```

**渲染逻辑**：成功率≥阈值或偏好 terse → terse；否则 guided。  
输出到 `artifacts/view_preview.md`，用于 UI 呈现或提示注入。

**到此**，同一份事件数据完成：Q1 判跑题 → Q2 抽模式 → Q3 两档视图。下次遇到"文档/翻译"任务，系统会先天触发该模式，极大降低跑题概率与沟通成本。

---

## 🧪 端到端示例（Chat‑only：只用 Cursor 导出）

**目标**：只把 README.md 翻译成中文（doc‑only）  
**实际**：Cursor 在建议里提到"将来可把 beautifulsoup4 加到 requirements.txt"，但并未真正修改 → 该部分记为 `plan`，不计分。

### 第 0 步｜原始输入
- `data/runs/r60/raw/cursor.md`（Cursor 导出聊天）
- `data/runs/r60/goal.json`（允许 `README.md`／`docs/**`，禁止 `requirements.txt`）

### 第 1 步｜提取事件
```bash
python tools/chat2events.py data/runs/r60
```

**产生 events.jsonl（节选）：**
```json
{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan","where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}
{"id":"e2","run_id":"r60","step":2,"phase":"modify","tool":"edit","where":{"path":"README.md"},"why":"已将英文内容改为中文","confidence":"high"}
{"id":"t1001","run_id":"r60","step":1001,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
```

### 第 2 步｜判航
```bash
python tools/events2guards.py data/runs/r60
```

**产生 guards.jsonl：**
- 对 plan 事件 → action=ok（不计分）
- 对 edit 事件（README.md）→ action=ok
- 若有对 requirements.txt 的 edit，会触发 warn/rollback（越界）

**要点**：Chat‑only 同样能稳定识别"已实施 vs 计划"，避免把"建议/计划"误判为"跑题改动"。

---

## 🧰 数据格式（关键文件）

### goal.json
```json
{
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt", "src/", "setup.py"],
  "checkpoints": ["reproduce","modify","test","regress"],
  "required_tests": ["doc_lang_check","whitelist_diff_check"]
}
```

### events.jsonl（每行一个 JSON）
```json
{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit",
 "where":{"path":"README.md"},"what":{"diff":"(omitted)"},"why":"from patch.diff","evidence":{}}
{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit",
 "where":{"path":"requirements.txt"},"what":{"diff":"(omitted)"},"why":"(none)","evidence":{}}
{"id":"e1001","run_id":"r42","step":1001,"phase":"test","tool":"shell",
 "cmd":"pytest -k doc_lang_check"}
```

**Chat‑only 下若仅有"计划修改"，则为：**
```json
{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan",
 "where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}
```

> **说明**：`tool=plan` 不计分，仅留痕；只有 `tool=edit` 会进入 Q1 守卫判分

### guards.jsonl
```json
{"run_id":"r42","step":1,"scope_guard":0.0,"plan_guard":0.0,"test_guard":0.0,"evidence_guard":0.0,"drift_score":0.0,"action":"ok","file":"README.md"}
{"run_id":"r42","step":2,"scope_guard":1.0,"plan_guard":1.0,"test_guard":0.0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt"}
```

### 模式卡 pc_*.json
见上方"抽卡"示例。

### 用户画像 profiles/*.json
```json
{"user_id":"<id>","self_report":"novice|intermediate|expert","hist_first_try_success":0.42,"pref":"guided|terse"}
```


---

## ⚙️ 最小可用脚本（MVP）

### Chat‑only（无需 git/diff）
```bash
# 准备
# 1) 导出 Cursor 对话到 data/runs/<run_id>/raw/cursor.md
# 2) 写 data/runs/<run_id>/goal.json（白/黑名单、必跑测试）

python tools/chat2events.py data/runs/<run_id>   # 生成 events.jsonl（plan/edit/test）
python tools/events2guards.py data/runs/<run_id> # 生成 guards.jsonl（仅 edit 计分）

# 或一键：
python scripts/e2e_chat_only.py <run_id>
```

### Diff 路线
```bash
python tools/patch2events.py data/runs/<run_id>
python tools/term2events.py  data/runs/<run_id>   # 若有 term.log
python tools/events2guards.py data/runs/<run_id>
```

**后续工作（占位）**：
- `agent/reflexion.py`：读取 `cursor.md`（如有）与 events，生成简要反思文本
- `agent/extract_card.py`：反思 → 模式卡（结构化 JSON）
- `q2_memory/retrieve.py`：依据 objective/关键词检索最匹配模式
- `q3_views/render.py`：依据用户画像选择 terse/guided 并渲染

---

## 🧪 评测（社区对齐 + 自定义指标）

### 社区对齐：SWE-bench
- 生成 `data/eval/predictions.jsonl`（每行 `{"instance_id","model_patch"}`），用官方 harness 评 %Resolved
- 我们本地的 base_commit + unified diff 与它的"基线快照 + 统一 diff"一致

### 我们新增指标（体现 Q2/Q3/Q1 价值）
- **Q2**：模式复用率、首试成功率↑、平均回合数/用时↓
- **Q3**：视图匹配度（guided 对新手更稳、terse 不打扰专家）
- **Q1**：偏航检出率、误报率、偏航恢复时间（warn→回到正确 checkpoint 的步数/秒）

### 消融（Ablation）
```
baseline → +pattern → +pattern+views → +pattern+views+guards
```
在同一批任务上成对比较，展示复用与守卫带来的复利收益。

---

## 🗺️ 实施计划（4 周样例）

### Week 1｜打底
搭事件总线；采 3–5 个真实案例，手工沉淀 3 张模式卡（如：空指针防护、依赖冲突、off-by-one）。

### Week 2｜能用
接检索+注入；新任务自动推荐模式卡（先用 terse）；打通最小 Q1 守卫（4 checkpoint）。

### Week 3｜过 Gate
上动态抽象路由（画像=自报水平 + 历史成功率）；完成"相似任务首试成功率显著提升"演示与 ablation。

### Week 4｜打磨
扩大到 8–10 张模式卡；补"偏航恢复时间/复用率"可视化；记录失败案例与改进方向。

> **Q1 坚持"最低可用"**：4 checkpoint + 2 条硬规则（白/黑名单；未过前置测试禁止合并）。把时间投给 Q2/Q3。

---

## 🧑‍🤝‍🧑 团队 SOP（最简可执行）

1. **每次会话结束至少落 3 件**：
   `raw/base_commit.txt`、`raw/patch.diff`、`goal.json`（可选：`raw/term.log`、`raw/cursor.md`）

2. **跑脚本**：
   ```bash
   python tools/patch2events.py data/runs/<run_id>
   python tools/term2events.py  data/runs/<run_id>   # 若有 term.log
   python tools/events2guards.py data/runs/<run_id>
   ```

3. **通过/有价值 → 抽卡**：生成 `artifacts/pattern.*.json` 并复制到 `data/patterns/`

4. **周会汇总** `guards.jsonl` 为"偏航榜单"，共建与复用模式卡

5. **每两周做一次** SWE-bench Lite/Verified 小规模对齐评测 + 我们指标报表

---

## ❓ FAQ

### 必须每次 commit 吗？
不需要。`git diff -U0` + `git rev-parse HEAD` 就足以作为"可复现实锤"。Commit 有助于审计与回滚，但不是 Q1/Q2/Q3 的硬依赖。

### Cursor 导出能当"事实来源"吗？
**可以**，在 Chat‑only 模式下满足以下任一条件即可视为"已实施修改（edit）"的证据：
- 明确表述"已修改/updated/changed/edited/已应用"等；
- 展示具体代码片段/patch；
- 关联出现并通过了对应测试命令。

若仅出现"计划修改/建议/可以/将要"等，则标记为 `tool=plan`（不计分，留痕）。  
当提取结果置信度低或空缺时，可**可选**调用 `git diff --name-only` 做兜底校验。

### 和 RAG 有什么不同？
RAG 一般检索静态知识；本系统沉淀的是你团队亲手做成的"可复用做法"（模式卡），是经验资产。

### 如何防止模式卡误触发？
通过 triggers 细化关键词/正则；在检索后加入人工确认或风险打分（约束冲突时降权/不注入）。

### 误报的偏航提醒如何处理？
UI 提供"我确认需要"按钮并记录为例外证据，用于改进 EvidenceGuard 与模式卡的 anti_patterns。

---

## ⚠️ 风险与边界

- 事件抽取过于粗糙可能导致误报/漏报；先从**"白名单 + 必跑测试"**的硬规则开始
- 模式卡过多会稀释检索精度；以"有明显 uplift"为标准进入模式库
- 用户画像初期可简单（自报 + 首试成功率）；后续再升级为偏好学习

---

## 🧭 TL;DR（落地步骤）

1. **落证据**：`base_commit.txt` + `patch.diff` (+ `term.log` + `cursor.md`)
2. **目标**：写 `goal.json`（白名单 + 检查点 + 必跑测试）
3. **生成**：`events.jsonl` → `guards.jsonl`，大于阈值则 warn/rollback
4. **沉淀**：抽"模式卡"，放入 `data/patterns/`，下次自动检索触发
5. **呈现**：按 `profiles/<user>.json` 渲染 terse/guided 两档视图
6. **评测**：SWE-bench %Resolved + 我们的 Q1/Q2/Q3 指标与 ablation

**同一份事件数据，三件事一次到位**：不跑题、能复用、会因人施教。

```

现在更新 plan (V3).md 文档：


```markdown
## 💭 问题分析与执行策略

> **核心思考**：我觉得这个框架已经搭好了，但是我认为这三个问题和它们的解决我们还没有完全地做好。就是说我想先解决最简单的这个问题，就是最后这个偏移的问题，就是这个drift的问题。然后再解决第二个和第三个问题，你觉得这个方法是不是好？因为我最后是想从简单到难开始，从一个实践的顺序来说，我是想先解决一个简单的问题，然后再解决其他的复杂的问题。
> 
> 我感觉第一个问题就是有一个数据之后，我们判断这个AI它是不是偏移了。这个数据是其他两个问题的先驱，因为如果没有这个数据的话，我们也没法match这个匹配度，对吧？我们也没有办法做这个复用的情况，learning from experience的情况。Q2和Q3其实取决于Q1，这是我的理解。所以我想先做Q1，再做Q2，再做Q3，不知道你同意这个方案吗？我觉得大体框架是有的，我们现在就要走一遍细节。
> 
> **技术细节需要细化**：举个例子比如Q1的四个守卫+计算score的方式+数据input/output都可以继续细化（是否要定一个ts or数据库结构，枚举结构），Q2的pattern的定义（这些如何定义：经验无法沉淀与迁移，造成重复劳动，是否要定一个ts or数据库结构，枚举结构），Q3的"用户水平 × 任务难度" 这两个也可以定义，是否要定一个ts or数据库结构，枚举结构）
> 
> 这是我的想法

## ✅ 执行策略确认

我完全同意你的执行顺序：先打穿 Q1（偏航检测）→ 再做 Q2（模式复用）→ 最后 Q3（动态抽象）。

理由很简单也很工程化：Q1 产出的"规范化事件 + 守卫分数"就是 Q2 抽卡与 Q3 路由的训练/检索数据。没有 Q1，就没有可复用的"事实语料库"。

下面我把三块一次性讲清楚：先给你实现顺序与验收标准，然后给精确的数据结构（TypeScript + 可选 SQLite DDL）与算法细节，最后给端到端示例（和你当前"翻译 README 却误改 requirements.txt"的例子完全对齐）。

---

## 📋 一、实施顺序（从简单到难）

### Phase 1（Q1：偏航检测，P0）

**目标**：对任意一次会话/提交，输出事件流与 drift 评分，并能告警/回滚。

**交付物**：
1. `events.jsonl`（来自 patch.diff/term.log 的规范化事件）
2. `guards.jsonl`（四守卫 + drift_score + action）
3. "最小 UI/CLI"：列出高分事件、显示原因、提供回滚命令

**验收**：
- ≥95% 的越界改动（不在 allowed_paths）被检出
- 假阳性 ≤10%（可通过例外机制逐步下降）

### Phase 2（Q2：模式复用，P1）

**目标**：把"做成的经历"沉淀成模式卡，能在新任务自动检索触发。

**交付物**：
1. `patterns/pc_*.json`（从多个 runs 抽取）
2. 检索与注入：给定 objective/issue_text → 返回命中的模式卡（含两档视图的文案骨架）

**验收**：
- 模式复用率↑、首试成功率↑、平均回合数↓（以小 A/B 验证）

### Phase 3（Q3：动态抽象，P1）

**目标**：同一卡两档视图，按"用户水平 × 任务难度"自动路由。

**交付物**：
1. `profiles/<user>.json`（画像）
2. 路由器：根据画像与任务难度，输出 terse | guided

**验收**：
- 新手在 guided 下成功率/稳定性更高；专家在 terse 下不中断

---

## 🔧 二、数据与接口规范（TS + JSONL + 可选 SQLite）

### 0) 共同枚举

```typescript
// phases/checkpoints
export type Phase = 'reproduce' | 'modify' | 'test' | 'regress';

// tools（新增 plan 类型）
export type Tool = 'edit' | 'shell' | 'browse' | 'plan';

// guard action
export type GuardAction = 'ok' | 'warn' | 'rollback';

// user level & task difficulty
export type UserLevel = 'novice' | 'intermediate' | 'expert';
export type TaskDifficulty = 'low' | 'medium' | 'high';

// confidence levels（Chat-only 用）
export type Confidence = 'low' | 'medium' | 'high';
```

---

### 1) Q1：输入/输出与算法

#### 1.1 目标定义（goal.json）

```typescript
export interface GoalConfig {
  run_id: string;
  objective: string;                         // e.g., "Translate README.md to Chinese"
  allowed_paths: string[];                   // allow-list (prefix match)
  forbidden_paths?: string[];                // optional block-list
  checkpoints: Phase[];                      // ["reproduce","modify","test","regress"]
  required_tests?: string[];                 // names/regex you expect to run/ pass
  allowed_tools_by_phase?: Partial<Record<Phase, Tool[]>>; // default 见下
  thresholds?: { warn: number; rollback: number };         // default 0.5/0.8
  meta?: Record<string, any>;                // 任意扩展
}
```

**默认策略**（若 allowed_tools_by_phase 未给出）：
- reproduce: ['shell','browse']
- modify:    ['edit','shell']
- test:      ['shell']
- regress:   ['shell']

**默认阈值**：warn=0.5，rollback=0.8

#### 1.2 事件（events.jsonl）

```typescript
export interface BaseEvent {
  id: string;                 // uuid
  run_id: string;
  step: number;               // 1,2,3...
  ts?: string;                // ISO time
  phase: Phase;
  tool: Tool;
  why?: string;               // rationale in short
  evidence?: {
    tests?: string[];         // tests names/assertions referenced
    logs?: string[];          // log lines digests or links
    links?: string[];         // issue/PR/docs links
  };
}

export interface EditEvent extends BaseEvent {
  tool: 'edit';
  where: { path: string; start?: number; end?: number };
  what: { diff?: string; ast_hint?: string };
}

export interface ShellEvent extends BaseEvent {
  tool: 'shell';
  cmd: string;
  exit_code?: number;
  stdout_digest?: string;     // hash/first-N lines
}

export type Event = EditEvent | ShellEvent;
```

**JSONL 示例**（与你的 README/requirements 例子一致）：

```json
{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit","where":{"path":"README.md"},"what":{"diff":"(hunk)"},"why":"from patch.diff"}
{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit","where":{"path":"requirements.txt"},"what":{"diff":"(hunk)"}}
{"id":"e3","run_id":"r42","step":3,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
{"id":"e4","run_id":"r42","step":4,"phase":"test","tool":"shell","cmd":"pytest -k whitelist_diff_check"}
```

#### 1.3 守卫输出（guards.jsonl）

```typescript
export interface GuardScores {
  id: string;                 // match event id
  run_id: string;
  step: number;
  scope_guard: number;        // 0~1
  plan_guard: number;         // 0~1
  test_guard: number;         // 0~1
  evidence_guard: number;     // 0~1
  drift_score: number;        // weighted sum
  action: GuardAction;        // ok | warn | rollback
  file?: string;              // for edit events
  notes?: string;             // reason for flag
}
```

**打分算法**（可直接落地）：

```typescript
// 权重（可配置）
const W = { scope: 0.4, plan: 0.3, test: 0.2, evidence: 0.1 };

// ScopeGuard：编辑是否越界（prefix allow-list）
scope_guard = (event.tool==='edit')
  ? (inAllowed(event.where.path, goal.allowed_paths) ? 0 : 1)
  : 0;

// PlanGuard：此 phase 是否允许此 tool/此路径类别
plan_guard = (() => {
  const allowTools = goal.allowed_tools_by_phase?.[event.phase] || defaultTools[event.phase];
  if (!allowTools.includes(event.tool)) return 1;
  if (event.tool==='edit' && !inAllowed(event.where.path, goal.allowed_paths)) return 1;
  return 0;
})();

// TestGuard：若 phase 是 test/regress，是否跑了/通过了 required_tests
// MVP：看到相应 pytest 命令则 0，否则 1（或结合 term.log 解析通过率）
test_guard = ((event.phase==='test' || event.phase==='regress') && event.tool==='shell')
  ? (coversRequired(event.cmd, goal.required_tests) ? 0 : 1)
  : 0;

// EvidenceGuard：modify 阶段的 edit 事件，是否带有 tests/logs/links 作为证据
evidence_guard = (event.phase==='modify' && event.tool==='edit')
  ? (event.evidence && (event.evidence.tests?.length || event.evidence.logs?.length || event.evidence.links?.length) ? 0 : 0.5)
  : 0;

// 综合：
drift_score = W.scope*scope_guard + W.plan*plan_guard + W.test*test_guard + W.evidence*evidence_guard;

// 动作：
action = (drift_score >= (goal.thresholds?.rollback ?? 0.8)) ? 'rollback'
       : (drift_score >= (goal.thresholds?.warn ?? 0.5))     ? 'warn'
       : 'ok';
```

**JSONL 示例**：

```json
{"id":"e1","run_id":"r42","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md"}
{"id":"e2","run_id":"r42","step":2,"scope_guard":1,"plan_guard":1,"test_guard":0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt","notes":"not in allowed_paths"}
```

**Q1 的评测**：
- 检出率（真正例 / 全部偏航）
- 误报率（假正例 / 全部告警）
- 偏航恢复时间（首次 warn → 回到正确 checkpoint 的步数/秒）
- 覆盖面（被守卫覆盖的偏航类型占比：路径越界/错误 phase/未跑测试/无证据）

---

### 2) Q2：模式卡定义与检索（在 Q1 打好后做）

#### 2.1 模式卡（patterns/pc_*.json）

```typescript
export interface PatternCard {
  version: string;                     // e.g., "1.0"
  pattern_id: string;                  // "pc_doc_only_change"
  title: string;                       // 人类可读标题
  triggers: string[];                  // 检索关键词/正则
  steps: string[];                     // 关键步骤（可用于计划/提示）
  invariants: string[];                // 不变量（必须成立的约束）
  anti_patterns?: string[];            // 禁止或常见误用
  eval_examples?: string[];            // 相关测试/验证名
  risks?: string[];                    // 风险提示（何时需要升级审核/例外）
  views: {                             // Q3 用
    terse: string;                     // 专家版
    guided: string;                    // 新手版
  };
  provenance: {                        // 溯源
    source_runs: string[];             // ["r42","r51"...]
    created_by: string;                // user id
    created_at: string;
  };
  metrics?: {                          // 可选：这张卡带来的 uplift 记录
    reuse_count: number;
    first_try_uplift?: number;
  };
}
```

**最小检索打分**（先规则 + 关键词覆盖；后续可接向量）：

```typescript
score = hits(triggers, goal.objective + issue_text) / triggers.length
// 冲突降权：若卡的 invariants 与 goal.allowed_paths/forbidden_paths 冲突，score -= 0.3
// 阶段性加权：若 Q1 的守卫告警类型与卡的 anti_patterns 相符，优先级↑
```

**沉淀策略**：
- 触发条件：本次 run 通过验证（或人工确认"做对了"）
- 合并：多 run 同类卡可合并（并保留 source_runs 列表）
- 进入库标准：能带来明显 uplift（首试成功率/回合数/时间）才纳入团队库

---

### 3) Q3：画像与路由

#### 3.1 用户画像（profiles/*.json）

```typescript
export interface UserProfile {
  user_id: string;
  self_report: UserLevel;                // 自报水平
  hist_first_try_success: number;        // 0~1
  pref?: 'guided' | 'terse';             // 明示偏好（可覆盖自动路由）
  notes?: string;
}
```

#### 3.2 任务难度估计（无需完美，先启发式）

```typescript
export interface TaskDescriptor {
  files_touched_est?: number;    // 预估修改文件数
  loc_delta_est?: number;        // 预估变更行数
  repo_familiarity?: number;     // 0~1（按贡献/最近互动/文件相似度）
  risk_flags?: string[];         // e.g., ["dependency","security","db-migration"]
}

function estimateDifficulty(d: TaskDescriptor): TaskDifficulty {
  const score = (d.files_touched_est||0)/5 + (d.loc_delta_est||0)/200 + (1-(d.repo_familiarity||0));
  if (score < 0.8) return 'low';
  if (score < 1.6) return 'medium';
  return 'high';
}
```

#### 3.3 视图路由（MVP）

```typescript
function chooseView(profile: UserProfile, task: TaskDescriptor): 'guided'|'terse' {
  const diff = estimateDifficulty(task);
  if (profile.pref) return profile.pref;
  if (profile.self_report === 'novice') return 'guided';
  if (diff === 'high') return 'guided';
  if (profile.hist_first_try_success < 0.5) return 'guided';
  return 'terse';
}
```


---

### 4) 可选数据库（SQLite DDL，占位可后置）

JSONL 先跑通，SQLite 便于做统计/报表/多用户协作。

```sql
-- runs
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY,
  created_at TEXT,
  objective TEXT
);

-- goals
CREATE TABLE goals (
  run_id TEXT,
  content JSON,
  PRIMARY KEY(run_id)
);

-- events
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  ts TEXT,
  phase TEXT,
  tool TEXT,
  path TEXT,
  cmd TEXT,
  payload JSON
);

-- guards
CREATE TABLE guard_scores (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  scope REAL, plan REAL, test REAL, evidence REAL,
  drift REAL, action TEXT, file TEXT, notes TEXT
);

-- patterns
CREATE TABLE patterns (
  pattern_id TEXT PRIMARY KEY,
  version TEXT,
  title TEXT,
  content JSON,
  reuse_count INTEGER DEFAULT 0
);

-- profiles
CREATE TABLE profiles (
  user_id TEXT PRIMARY KEY,
  content JSON
);
```

---

## 🚀 三、端到端（以你的"文档任务跑题"为例）

**输入**：
- `goal.json`：只允许 README.md / docs/**
- `patch.diff`：改了 README.md 并误改 requirements.txt
- （可选）`term.log`：包含 pytest -k doc_lang_check 与 pytest -k whitelist_diff_check

**步骤**：
1. `patch2events` → 生成两条 edit 事件（README.md / requirements.txt）
2. `term2events` → 生成两条 shell 事件（测试）
3. `events2guards` → 对 requirements.txt 给出 Scope=1.0，Plan=1.0，Evidence=0.5 → drift=0.85 → action=warn
4. （通过/确认后）抽卡 → `pc_doc_only_change` 入库
5. 新任务"翻译文档"启动时，检索命中该卡：
   - terse 给专家：白名单 + 禁改依赖 + 两个检查
   - guided 给新手：逐步配置白名单/语言检测/例外流程/坑点
6. 度量：相似任务在有卡 vs 无卡下，比较首试成功率/回合数/用时，出 ablation 图。

---

## 🛠️ 四、你今天就能推进的细节（Q1 打穿）

1. **把四个守卫写成纯函数**（方便单元测试）
   - `scopeGuard(e, goal) -> 0|1`
   - `planGuard(e, goal) -> 0|1`
   - `testGuard(e, goal, termLog?) -> 0|1`
   - `evidenceGuard(e) -> 0|0.5`
   - `driftScore(scores, weights, thresholds) -> {score, action}`

2. **建立 6 个最小单测**
   - 允许路径编辑 / 非允许路径编辑
   - modify 阶段使用非法 tool
   - 测试应跑未跑 / 已跑
   - 有/无 evidence
   - 综合 case 触发 warn 与 rollback

3. **做一个"例外机制"**（把假阳性降下来）
   - UI/CLI：`ack --reason="需要临时改依赖以修 build"`
   - 例外写入 `events.jsonl` 的 `evidence.links/notes`，下一次守卫见到 有效例外 可降权

---

## 🔗 五、为何 Q1→Q2→Q3 是正确的依赖关系

- **Q1 输出 = Q2/Q3 的训练与检索数据**：没有 `events.jsonl` 的"事实"，模式卡只能凭空想象。
- **Q1 还能给 Q2 提供"anti_patterns/risks"**：哪些越界最常见？直接写进卡，下次先天规避。
- **Q3 的"难度估计/视图路由"需要 Q1 的统计**：历史首试成功率、偏航率、偏航恢复时间 → 画像与路由的依据。

---

## ✅ 下一步行动

如果你认可上面的规范，我可以把这些 TS 接口 + 守卫函数样例直接合入你仓库的 `types/` 与 `src/guards/`，并加上6 条单测；你就能马上跑 Phase 1 的端到端（不依赖外部模型）。

接着，我们用 3–5 次真实 run 抽出 第一批模式卡（Q2），最后再接上 视图路由（Q3）。
```

```markdown
## 💭 问题分析与执行策略

> **核心思考**：我觉得这个框架已经搭好了，但是我认为这三个问题和它们的解决我们还没有完全地做好。就是说我想先解决最简单的这个问题，就是最后这个偏移的问题，就是这个drift的问题。然后再解决第二个和第三个问题，你觉得这个方法是不是好？因为我最后是想从简单到难开始，从一个实践的顺序来说，我是想先解决一个简单的问题，然后再解决其他的复杂的问题。
> 
> 我感觉第一个问题就是有一个数据之后，我们判断这个AI它是不是偏移了。这个数据是其他两个问题的先驱，因为如果没有这个数据的话，我们也没法match这个匹配度，对吧？我们也没有办法做这个复用的情况，learning from experience的情况。Q2和Q3其实取决于Q1，这是我的理解。所以我想先做Q1，再做Q2，再做Q3，不知道你同意这个方案吗？我觉得大体框架是有的，我们现在就要走一遍细节。
> 
> **技术细节需要细化**：举个例子比如Q1的四个守卫+计算score的方式+数据input/output都可以继续细化（是否要定一个ts or数据库结构，枚举结构），Q2的pattern的定义（这些如何定义：经验无法沉淀与迁移，造成重复劳动，是否要定一个ts or数据库结构，枚举结构），Q3的"用户水平 × 任务难度" 这两个也可以定义，是否要定一个ts or数据库结构，枚举结构）
> 
> 这是我的想法

## ✅ 执行策略确认

我完全同意你的执行顺序：先打穿 Q1（偏航检测）→ 再做 Q2（模式复用）→ 最后 Q3（动态抽象）。

理由很简单也很工程化：Q1 产出的"规范化事件 + 守卫分数"就是 Q2 抽卡与 Q3 路由的训练/检索数据。没有 Q1，就没有可复用的"事实语料库"。

下面我把三块一次性讲清楚：先给你实现顺序与验收标准，然后给精确的数据结构（TypeScript + 可选 SQLite DDL）与算法细节，最后给端到端示例（和你当前"翻译 README 却误改 requirements.txt"的例子完全对齐）。

---

## 📋 一、实施顺序（从简单到难）

### Phase 1（Q1：偏航检测，P0）

**目标**：对任意一次会话/提交，输出事件流与 drift 评分，并能告警/回滚。

**交付物**：
1. `events.jsonl`（来自 patch.diff/term.log 的规范化事件）
2. `guards.jsonl`（四守卫 + drift_score + action）
3. "最小 UI/CLI"：列出高分事件、显示原因、提供回滚命令

**验收**：
- ≥95% 的越界改动（不在 allowed_paths）被检出
- 假阳性 ≤10%（可通过例外机制逐步下降）

### Phase 2（Q2：模式复用，P1）

**目标**：把"做成的经历"沉淀成模式卡，能在新任务自动检索触发。

**交付物**：
1. `patterns/pc_*.json`（从多个 runs 抽取）
2. 检索与注入：给定 objective/issue_text → 返回命中的模式卡（含两档视图的文案骨架）

**验收**：
- 模式复用率↑、首试成功率↑、平均回合数↓（以小 A/B 验证）

### Phase 3（Q3：动态抽象，P1）

**目标**：同一卡两档视图，按"用户水平 × 任务难度"自动路由。

**交付物**：
1. `profiles/<user>.json`（画像）
2. 路由器：根据画像与任务难度，输出 terse | guided

**验收**：
- 新手在 guided 下成功率/稳定性更高；专家在 terse 下不中断

---

## 🔧 二、数据与接口规范（TS + JSONL + 可选 SQLite）

### 0) 共同枚举

```typescript
// phases/checkpoints
export type Phase = 'reproduce' | 'modify' | 'test' | 'regress';

// tools（新增 plan 类型）
export type Tool = 'edit' | 'shell' | 'browse' | 'plan';

// guard action
export type GuardAction = 'ok' | 'warn' | 'rollback';

// user level & task difficulty
export type UserLevel = 'novice' | 'intermediate' | 'expert';
export type TaskDifficulty = 'low' | 'medium' | 'high';

// confidence levels（Chat-only 用）
export type Confidence = 'low' | 'medium' | 'high';
```

---

### 1) Q1：输入/输出与算法

#### 1.1 目标定义（goal.json）

```typescript
export interface GoalConfig {
  run_id: string;
  objective: string;                         // e.g., "Translate README.md to Chinese"
  allowed_paths: string[];                   // allow-list (prefix match)
  forbidden_paths?: string[];                // optional block-list
  checkpoints: Phase[];                      // ["reproduce","modify","test","regress"]
  required_tests?: string[];                 // names/regex you expect to run/ pass
  allowed_tools_by_phase?: Partial<Record<Phase, Tool[]>>; // default 见下
  thresholds?: { warn: number; rollback: number };         // default 0.5/0.8
  meta?: Record<string, any>;                // 任意扩展
}
```

**默认策略**（若 allowed_tools_by_phase 未给出）：
- reproduce: ['shell','browse']
- modify:    ['edit','shell']
- test:      ['shell']
- regress:   ['shell']

**默认阈值**：warn=0.5，rollback=0.8

#### 1.2 事件（events.jsonl）

```typescript
export interface BaseEvent {
  id: string;                 // uuid
  run_id: string;
  step: number;               // 1,2,3...
  ts?: string;                // ISO time
  phase: Phase;
  tool: Tool;
  why?: string;               // rationale in short
  evidence?: {
    tests?: string[];         // tests names/assertions referenced
    logs?: string[];          // log lines digests or links
    links?: string[];         // issue/PR/docs links
  };
}

export interface EditEvent extends BaseEvent {
  tool: 'edit';
  where: { path: string; start?: number; end?: number };
  what: { diff?: string; ast_hint?: string };
}

export interface PlanEvent extends BaseEvent {
  tool: 'plan';
  where: { path: string; start?: number; end?: number };
  confidence?: Confidence;  // Chat-only 提取的置信度
}

export interface ShellEvent extends BaseEvent {
  tool: 'shell';
  cmd: string;
  exit_code?: number;
  stdout_digest?: string;     // hash/first-N lines
}

export type Event = EditEvent | PlanEvent | ShellEvent;
```

**JSONL 示例**（与你的 README/requirements 例子一致）：

```json
{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit","where":{"path":"README.md"},"what":{"diff":"(hunk)"},"why":"from patch.diff"}
{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit","where":{"path":"requirements.txt"},"what":{"diff":"(hunk)"}}
{"id":"e3","run_id":"r42","step":3,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
{"id":"e4","run_id":"r42","step":4,"phase":"test","tool":"shell","cmd":"pytest -k whitelist_diff_check"}
```

#### 1.3 守卫输出（guards.jsonl）

```typescript
export interface GuardScores {
  id: string;                 // match event id
  run_id: string;
  step: number;
  scope_guard: number;        // 0~1
  plan_guard: number;         // 0~1
  test_guard: number;         // 0~1
  evidence_guard: number;     // 0~1
  drift_score: number;        // weighted sum
  action: GuardAction;        // ok | warn | rollback
  file?: string;              // for edit events
  notes?: string;             // reason for flag
}
```

**打分算法**（可直接落地）：

```typescript
// 权重（可配置）
const W = { scope: 0.4, plan: 0.3, test: 0.2, evidence: 0.1 };

// ScopeGuard：编辑是否越界（prefix allow-list）
scope_guard = (event.tool==='edit')
  ? (inAllowed(event.where.path, goal.allowed_paths) ? 0 : 1)
  : 0;

// PlanGuard：此 phase 是否允许此 tool/此路径类别
plan_guard = (() => {
  const allowTools = goal.allowed_tools_by_phase?.[event.phase] || defaultTools[event.phase];
  if (!allowTools.includes(event.tool)) return 1;
  if (event.tool==='edit' && !inAllowed(event.where.path, goal.allowed_paths)) return 1;
  return 0;
})();

// TestGuard：若 phase 是 test/regress，是否跑了/通过了 required_tests
// MVP：看到相应 pytest 命令则 0，否则 1（或结合 term.log 解析通过率）
test_guard = ((event.phase==='test' || event.phase==='regress') && event.tool==='shell')
  ? (coversRequired(event.cmd, goal.required_tests) ? 0 : 1)
  : 0;

// EvidenceGuard：modify 阶段的 edit 事件，是否带有 tests/logs/links 作为证据
evidence_guard = (event.phase==='modify' && event.tool==='edit')
  ? (event.evidence && (event.evidence.tests?.length || event.evidence.logs?.length || event.evidence.links?.length) ? 0 : 0.5)
  : 0;

// 综合：
drift_score = W.scope*scope_guard + W.plan*plan_guard + W.test*test_guard + W.evidence*evidence_guard;

// 动作：
action = (drift_score >= (goal.thresholds?.rollback ?? 0.8)) ? 'rollback'
       : (drift_score >= (goal.thresholds?.warn ?? 0.5))     ? 'warn'
       : 'ok';
```

**JSONL 示例**：

```json
{"id":"e1","run_id":"r42","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md"}
{"id":"e2","run_id":"r42","step":2,"scope_guard":1,"plan_guard":1,"test_guard":0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt","notes":"not in allowed_paths"}
```

**Q1 的评测**：
- 检出率（真正例 / 全部偏航）
- 误报率（假正例 / 全部告警）
- 偏航恢复时间（首次 warn → 回到正确 checkpoint 的步数/秒）
- 覆盖面（被守卫覆盖的偏航类型占比：路径越界/错误 phase/未跑测试/无证据）

---

### 2) Q2：模式卡定义与检索（在 Q1 打好后做）

#### 2.1 模式卡（patterns/pc_*.json）

```typescript
export interface PatternCard {
  version: string;                     // e.g., "1.0"
  pattern_id: string;                  // "pc_doc_only_change"
  title: string;                       // 人类可读标题
  triggers: string[];                  // 检索关键词/正则
  steps: string[];                     // 关键步骤（可用于计划/提示）
  invariants: string[];                // 不变量（必须成立的约束）
  anti_patterns?: string[];            // 禁止或常见误用
  eval_examples?: string[];            // 相关测试/验证名
  risks?: string[];                    // 风险提示（何时需要升级审核/例外）
  views: {                             // Q3 用
    terse: string;                     // 专家版
    guided: string;                    // 新手版
  };
  provenance: {                        // 溯源
    source_runs: string[];             // ["r42","r51"...]
    created_by: string;                // user id
    created_at: string;
  };
  metrics?: {                          // 可选：这张卡带来的 uplift 记录
    reuse_count: number;
    first_try_uplift?: number;
  };
}
```

**最小检索打分**（先规则 + 关键词覆盖；后续可接向量）：

```typescript
score = hits(triggers, goal.objective + issue_text) / triggers.length
// 冲突降权：若卡的 invariants 与 goal.allowed_paths/forbidden_paths 冲突，score -= 0.3
// 阶段性加权：若 Q1 的守卫告警类型与卡的 anti_patterns 相符，优先级↑
```

**沉淀策略**：
- 触发条件：本次 run 通过验证（或人工确认"做对了"）
- 合并：多 run 同类卡可合并（并保留 source_runs 列表）
- 进入库标准：能带来明显 uplift（首试成功率/回合数/时间）才纳入团队库

---

### 3) Q3：画像与路由

#### 3.1 用户画像（profiles/*.json）

```typescript
export interface UserProfile {
  user_id: string;
  self_report: UserLevel;                // 自报水平
  hist_first_try_success: number;        // 0~1
  pref?: 'guided' | 'terse';             // 明示偏好（可覆盖自动路由）
  notes?: string;
}
```

#### 3.2 任务难度估计（无需完美，先启发式）

```typescript
export interface TaskDescriptor {
  files_touched_est?: number;    // 预估修改文件数
  loc_delta_est?: number;        // 预估变更行数
  repo_familiarity?: number;     // 0~1（按贡献/最近互动/文件相似度）
  risk_flags?: string[];         // e.g., ["dependency","security","db-migration"]
}

function estimateDifficulty(d: TaskDescriptor): TaskDifficulty {
  const score = (d.files_touched_est||0)/5 + (d.loc_delta_est||0)/200 + (1-(d.repo_familiarity||0));
  if (score < 0.8) return 'low';
  if (score < 1.6) return 'medium';
  return 'high';
}
```

#### 3.3 视图路由（MVP）

```typescript
function chooseView(profile: UserProfile, task: TaskDescriptor): 'guided'|'terse' {
  const diff = estimateDifficulty(task);
  if (profile.pref) return profile.pref;
  if (profile.self_report === 'novice') return 'guided';
  if (diff === 'high') return 'guided';
  if (profile.hist_first_try_success < 0.5) return 'guided';
  return 'terse';
}
```


---

### 4) 可选数据库（SQLite DDL，占位可后置）

JSONL 先跑通，SQLite 便于做统计/报表/多用户协作。

```sql
-- runs
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY,
  created_at TEXT,
  objective TEXT
);

-- goals
CREATE TABLE goals (
  run_id TEXT,
  content JSON,
  PRIMARY KEY(run_id)
);

-- events
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  ts TEXT,
  phase TEXT,
  tool TEXT,
  path TEXT,
  cmd TEXT,
  payload JSON
);

-- guards
CREATE TABLE guard_scores (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  scope REAL, plan REAL, test REAL, evidence REAL,
  drift REAL, action TEXT, file TEXT, notes TEXT
);

-- patterns
CREATE TABLE patterns (
  pattern_id TEXT PRIMARY KEY,
  version TEXT,
  title TEXT,
  content JSON,
  reuse_count INTEGER DEFAULT 0
);

-- profiles
CREATE TABLE profiles (
  user_id TEXT PRIMARY KEY,
  content JSON
);
```

---

## 🚀 三、端到端（以你的"文档任务跑题"为例）

**输入**：
- `goal.json`：只允许 README.md / docs/**
- `patch.diff`：改了 README.md 并误改 requirements.txt
- （可选）`term.log`：包含 pytest -k doc_lang_check 与 pytest -k whitelist_diff_check

**步骤**：
1. `patch2events` → 生成两条 edit 事件（README.md / requirements.txt）
2. `term2events` → 生成两条 shell 事件（测试）
3. `events2guards` → 对 requirements.txt 给出 Scope=1.0，Plan=1.0，Evidence=0.5 → drift=0.85 → action=warn
4. （通过/确认后）抽卡 → `pc_doc_only_change` 入库
5. 新任务"翻译文档"启动时，检索命中该卡：
   - terse 给专家：白名单 + 禁改依赖 + 两个检查
   - guided 给新手：逐步配置白名单/语言检测/例外流程/坑点
6. 度量：相似任务在有卡 vs 无卡下，比较首试成功率/回合数/用时，出 ablation 图。

---

## 🛠️ 四、你今天就能推进的细节（Q1 打穿）

1. **把四个守卫写成纯函数**（方便单元测试）
   - `scopeGuard(e, goal) -> 0|1`
   - `planGuard(e, goal) -> 0|1`
   - `testGuard(e, goal, termLog?) -> 0|1`
   - `evidenceGuard(e) -> 0|0.5`
   - `driftScore(scores, weights, thresholds) -> {score, action}`

2. **建立 6 个最小单测**
   - 允许路径编辑 / 非允许路径编辑
   - modify 阶段使用非法 tool
   - 测试应跑未跑 / 已跑
   - 有/无 evidence
   - 综合 case 触发 warn 与 rollback

3. **做一个"例外机制"**（把假阳性降下来）
   - UI/CLI：`ack --reason="需要临时改依赖以修 build"`
   - 例外写入 `events.jsonl` 的 `evidence.links/notes`，下一次守卫见到 有效例外 可降权

---

## 🔗 五、为何 Q1→Q2→Q3 是正确的依赖关系

- **Q1 输出 = Q2/Q3 的训练与检索数据**：没有 `events.jsonl` 的"事实"，模式卡只能凭空想象。
- **Q1 还能给 Q2 提供"anti_patterns/risks"**：哪些越界最常见？直接写进卡，下次先天规避。
- **Q3 的"难度估计/视图路由"需要 Q1 的统计**：历史首试成功率、偏航率、偏航恢复时间 → 画像与路由的依据。

---

## ✅ 下一步行动

如果你认可上面的规范，我可以把这些 TS 接口 + 守卫函数样例直接合入你仓库的 `types/` 与 `src/guards/`，并加上6 条单测；你就能马上跑 Phase 1 的端到端（不依赖外部模型）。

接着，我们用 3–5 次真实 run 抽出 第一批模式卡（Q2），最后再接上 视图路由（Q3）。
```

```markdown
## 💭 问题分析与执行策略

> **核心思考**：我觉得这个框架已经搭好了，但是我认为这三个问题和它们的解决我们还没有完全地做好。就是说我想先解决最简单的这个问题，就是最后这个偏移的问题，就是这个drift的问题。然后再解决第二个和第三个问题，你觉得这个方法是不是好？因为我最后是想从简单到难开始，从一个实践的顺序来说，我是想先解决一个简单的问题，然后再解决其他的复杂的问题。
> 
> 我感觉第一个问题就是有一个数据之后，我们判断这个AI它是不是偏移了。这个数据是其他两个问题的先驱，因为如果没有这个数据的话，我们也没法match这个匹配度，对吧？我们也没有办法做这个复用的情况，learning from experience的情况。Q2和Q3其实取决于Q1，这是我的理解。所以我想先做Q1，再做Q2，再做Q3，不知道你同意这个方案吗？我觉得大体框架是有的，我们现在就要走一遍细节。
> 
> **技术细节需要细化**：举个例子比如Q1的四个守卫+计算score的方式+数据input/output都可以继续细化（是否要定一个ts or数据库结构，枚举结构），Q2的pattern的定义（这些如何定义：经验无法沉淀与迁移，造成重复劳动，是否要定一个ts or数据库结构，枚举结构），Q3的"用户水平 × 任务难度" 这两个也可以定义，是否要定一个ts or数据库结构，枚举结构）
> 
> 这是我的想法

## ✅ 执行策略确认

我完全同意你的执行顺序：先打穿 Q1（偏航检测）→ 再做 Q2（模式复用）→ 最后 Q3（动态抽象）。

理由很简单也很工程化：Q1 产出的"规范化事件 + 守卫分数"就是 Q2 抽卡与 Q3 路由的训练/检索数据。没有 Q1，就没有可复用的"事实语料库"。

下面我把三块一次性讲清楚：先给你实现顺序与验收标准，然后给精确的数据结构（TypeScript + 可选 SQLite DDL）与算法细节，最后给端到端示例（和你当前"翻译 README 却误改 requirements.txt"的例子完全对齐）。

---

## 📋 一、实施顺序（从简单到难）

### Phase 1（Q1：偏航检测，P0）

**目标**：对任意一次会话/提交，输出事件流与 drift 评分，并能告警/回滚。

**交付物**：
1. `events.jsonl`（来自 patch.diff/term.log 的规范化事件）
2. `guards.jsonl`（四守卫 + drift_score + action）
3. "最小 UI/CLI"：列出高分事件、显示原因、提供回滚命令

**验收**：
- ≥95% 的越界改动（不在 allowed_paths）被检出
- 假阳性 ≤10%（可通过例外机制逐步下降）

### Phase 2（Q2：模式复用，P1）

**目标**：把"做成的经历"沉淀成模式卡，能在新任务自动检索触发。

**交付物**：
1. `patterns/pc_*.json`（从多个 runs 抽取）
2. 检索与注入：给定 objective/issue_text → 返回命中的模式卡（含两档视图的文案骨架）

**验收**：
- 模式复用率↑、首试成功率↑、平均回合数↓（以小 A/B 验证）

### Phase 3（Q3：动态抽象，P1）

**目标**：同一卡两档视图，按"用户水平 × 任务难度"自动路由。

**交付物**：
1. `profiles/<user>.json`（画像）
2. 路由器：根据画像与任务难度，输出 terse | guided

**验收**：
- 新手在 guided 下成功率/稳定性更高；专家在 terse 下不中断

---

## 🔧 二、数据与接口规范（TS + JSONL + 可选 SQLite）

### 0) 共同枚举

```typescript
// phases/checkpoints
export type Phase = 'reproduce' | 'modify' | 'test' | 'regress';

// tools（新增 plan 类型）
export type Tool = 'edit' | 'shell' | 'browse' | 'plan';

// guard action
export type GuardAction = 'ok' | 'warn' | 'rollback';

// user level & task difficulty
export type UserLevel = 'novice' | 'intermediate' | 'expert';
export type TaskDifficulty = 'low' | 'medium' | 'high';

// confidence levels（Chat-only 用）
export type Confidence = 'low' | 'medium' | 'high';
```

---

### 1) Q1：输入/输出与算法

#### 1.1 目标定义（goal.json）

```typescript
export interface GoalConfig {
  run_id: string;
  objective: string;                         // e.g., "Translate README.md to Chinese"
  allowed_paths: string[];                   // allow-list (prefix match)
  forbidden_paths?: string[];                // optional block-list
  checkpoints: Phase[];                      // ["reproduce","modify","test","regress"]
  required_tests?: string[];                 // names/regex you expect to run/ pass
  allowed_tools_by_phase?: Partial<Record<Phase, Tool[]>>; // default 见下
  thresholds?: { warn: number; rollback: number };         // default 0.5/0.8
  meta?: Record<string, any>;                // 任意扩展
}
```

**默认策略**（若 allowed_tools_by_phase 未给出）：
- reproduce: ['shell','browse']
- modify:    ['edit','shell']
- test:      ['shell']
- regress:   ['shell']

**默认阈值**：warn=0.5，rollback=0.8

#### 1.2 事件（events.jsonl）

```typescript
export interface BaseEvent {
  id: string;                 // uuid
  run_id: string;
  step: number;               // 1,2,3...
  ts?: string;                // ISO time
  phase: Phase;
  tool: Tool;
  why?: string;               // rationale in short
  evidence?: {
    tests?: string[];         // tests names/assertions referenced
    logs?: string[];          // log lines digests or links
    links?: string[];         // issue/PR/docs links
  };
}

export interface EditEvent extends BaseEvent {
  tool: 'edit';
  where: { path: string; start?: number; end?: number };
  what: { diff?: string; ast_hint?: string };
}

export interface PlanEvent extends BaseEvent {
  tool: 'plan';
  where: { path: string; start?: number; end?: number };
  confidence?: Confidence;  // Chat-only 提取的置信度
}

export interface ShellEvent extends BaseEvent {
  tool: 'shell';
  cmd: string;
  exit_code?: number;
  stdout_digest?: string;     // hash/first-N lines
}

export type Event = EditEvent | PlanEvent | ShellEvent;
```

**JSONL 示例**（Diff 路线）：

```json
{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit","where":{"path":"README.md"},"what":{"diff":"(hunk)"},"why":"from patch.diff"}
{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit","where":{"path":"requirements.txt"},"what":{"diff":"(hunk)"}}
{"id":"e3","run_id":"r42","step":3,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
{"id":"e4","run_id":"r42","step":4,"phase":"test","tool":"shell","cmd":"pytest -k whitelist_diff_check"}
```

**Chat-only 示例**：

```json
{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan","where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}
{"id":"e2","run_id":"r60","step":2,"phase":"modify","tool":"edit","where":{"path":"README.md"},"why":"已将英文内容改为中文","confidence":"high"}
{"id":"t1001","run_id":"r60","step":1001,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
```

#### 1.3 守卫输出（guards.jsonl）

```typescript
export interface GuardScores {
  id: string;                 // match event id
  run_id: string;
  step: number;
  scope_guard: number;        // 0~1
  plan_guard: number;         // 0~1
  test_guard: number;         // 0~1
  evidence_guard: number;     // 0~1
  drift_score: number;        // weighted sum
  action: GuardAction;        // ok | warn | rollback
  file?: string;              // for edit events
  notes?: string;             // reason for flag
}
```

**打分算法**（可直接落地）：

```typescript
// 权重（可配置）
const W = { scope: 0.4, plan: 0.3, test: 0.2, evidence: 0.1 };

// ScopeGuard：编辑是否越界（prefix allow-list）
scope_guard = (event.tool==='edit')
  ? (inAllowed(event.where.path, goal.allowed_paths) ? 0 : 1)
  : 0;

// PlanGuard：此 phase 是否允许此 tool/此路径类别
plan_guard = (() => {
  const allowTools = goal.allowed_tools_by_phase?.[event.phase] || defaultTools[event.phase];
  if (!allowTools.includes(event.tool)) return 1;
  if (event.tool==='edit' && !inAllowed(event.where.path, goal.allowed_paths)) return 1;
  return 0;
})();

// TestGuard：若 phase 是 test/regress，是否跑了/通过了 required_tests
// MVP：看到相应 pytest 命令则 0，否则 1（或结合 term.log 解析通过率）
test_guard = ((event.phase==='test' || event.phase==='regress') && event.tool==='shell')
  ? (coversRequired(event.cmd, goal.required_tests) ? 0 : 1)
  : 0;

// EvidenceGuard：modify 阶段的 edit 事件，是否带有 tests/logs/links 作为证据
evidence_guard = (event.phase==='modify' && event.tool==='edit')
  ? (event.evidence && (event.evidence.tests?.length || event.evidence.logs?.length || event.evidence.links?.length) ? 0 : 0.5)
  : 0;

// 综合：
drift_score = W.scope*scope_guard + W.plan*plan_guard + W.test*test_guard + W.evidence*evidence_guard;

// 动作：
action = (drift_score >= (goal.thresholds?.rollback ?? 0.8)) ? 'rollback'
       : (drift_score >= (goal.thresholds?.warn ?? 0.5))     ? 'warn'
       : 'ok';
```

**JSONL 示例**：

```json
{"id":"e1","run_id":"r42","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md"}
{"id":"e2","run_id":"r42","step":2,"scope_guard":1,"plan_guard":1,"test_guard":0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt","notes":"not in allowed_paths"}
```

**Q1 的评测**：
- 检出率（真正例 / 全部偏航）
- 误报率（假正例 / 全部告警）
- 偏航恢复时间（首次 warn → 回到正确 checkpoint 的步数/秒）
- 覆盖面（被守卫覆盖的偏航类型占比：路径越界/错误 phase/未跑测试/无证据）

---

### 2) Q2：模式卡定义与检索（在 Q1 打好后做）

#### 2.1 模式卡（patterns/pc_*.json）

```typescript
export interface PatternCard {
  version: string;                     // e.g., "1.0"
  pattern_id: string;                  // "pc_doc_only_change"
  title: string;                       // 人类可读标题
  triggers: string[];                  // 检索关键词/正则
  steps: string[];                     // 关键步骤（可用于计划/提示）
  invariants: string[];                // 不变量（必须成立的约束）
  anti_patterns?: string[];            // 禁止或常见误用
  eval_examples?: string[];            // 相关测试/验证名
  risks?: string[];                    // 风险提示（何时需要升级审核/例外）
  views: {                             // Q3 用
    terse: string;                     // 专家版
    guided: string;                    // 新手版
  };
  provenance: {                        // 溯源
    source_runs: string[];             // ["r42","r51"...]
    created_by: string;                // user id
    created_at: string;
  };
  metrics?: {                          // 可选：这张卡带来的 uplift 记录
    reuse_count: number;
    first_try_uplift?: number;
  };
}
```

**最小检索打分**（先规则 + 关键词覆盖；后续可接向量）：

```typescript
score = hits(triggers, goal.objective + issue_text) / triggers.length
// 冲突降权：若卡的 invariants 与 goal.allowed_paths/forbidden_paths 冲突，score -= 0.3
// 阶段性加权：若 Q1 的守卫告警类型与卡的 anti_patterns 相符，优先级↑
```

**沉淀策略**：
- 触发条件：本次 run 通过验证（或人工确认"做对了"）
- 合并：多 run 同类卡可合并（并保留 source_runs 列表）
- 进入库标准：能带来明显 uplift（首试成功率/回合数/时间）才纳入团队库

---

### 3) Q3：画像与路由

#### 3.1 用户画像（profiles/*.json）

```typescript
export interface UserProfile {
  user_id: string;
  self_report: UserLevel;                // 自报水平
  hist_first_try_success: number;        // 0~1
  pref?: 'guided' | 'terse';             // 明示偏好（可覆盖自动路由）
  notes?: string;
}
```

#### 3.2 任务难度估计（无需完美，先启发式）

```typescript
export interface TaskDescriptor {
  files_touched_est?: number;    // 预估修改文件数
  loc_delta_est?: number;        // 预估变更行数
  repo_familiarity?: number;     // 0~1（按贡献/最近互动/文件相似度）
  risk_flags?: string[];         // e.g., ["dependency","security","db-migration"]
}

function estimateDifficulty(d: TaskDescriptor): TaskDifficulty {
  const score = (d.files_touched_est||0)/5 + (d.loc_delta_est||0)/200 + (1-(d.repo_familiarity||0));
  if (score < 0.8) return 'low';
  if (score < 1.6) return 'medium';
  return 'high';
}
```

#### 3.3 视图路由（MVP）

```typescript
function chooseView(profile: UserProfile, task: TaskDescriptor): 'guided'|'terse' {
  const diff = estimateDifficulty(task);
  if (profile.pref) return profile.pref;
  if (profile.self_report === 'novice') return 'guided';
  if (diff === 'high') return 'guided';
  if (profile.hist_first_try_success < 0.5) return 'guided';
  return 'terse';
}
```


---

### 4) 可选数据库（SQLite DDL，占位可后置）

JSONL 先跑通，SQLite 便于做统计/报表/多用户协作。

```sql
-- runs
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY,
  created_at TEXT,
  objective TEXT
);

-- goals
CREATE TABLE goals (
  run_id TEXT,
  content JSON,
  PRIMARY KEY(run_id)
);

-- events
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  ts TEXT,
  phase TEXT,
  tool TEXT,
  path TEXT,
  cmd TEXT,
  payload JSON
);

-- guards
CREATE TABLE guard_scores (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  scope REAL, plan REAL, test REAL, evidence REAL,
  drift REAL, action TEXT, file TEXT, notes TEXT
);

-- patterns
CREATE TABLE patterns (
  pattern_id TEXT PRIMARY KEY,
  version TEXT,
  title TEXT,
  content JSON,
  reuse_count INTEGER DEFAULT 0
);

-- profiles
CREATE TABLE profiles (
  user_id TEXT PRIMARY KEY,
  content JSON
);
```

---

## 🚀 三、端到端（以你的"文档任务跑题"为例）

**输入**：
- `goal.json`：只允许 README.md / docs/**
- `patch.diff`：改了 README.md 并误改 requirements.txt
- （可选）`term.log`：包含 pytest -k doc_lang_check 与 pytest -k whitelist_diff_check

**步骤**：
1. `patch2events` → 生成两条 edit 事件（README.md / requirements.txt）
2. `term2events` → 生成两条 shell 事件（测试）
3. `events2guards` → 对 requirements.txt 给出 Scope=1.0，Plan=1.0，Evidence=0.5 → drift=0.85 → action=warn
4. （通过/确认后）抽卡 → `pc_doc_only_change` 入库
5. 新任务"翻译文档"启动时，检索命中该卡：
   - terse 给专家：白名单 + 禁改依赖 + 两个检查
   - guided 给新手：逐步配置白名单/语言检测/例外流程/坑点
6. 度量：相似任务在有卡 vs 无卡下，比较首试成功率/回合数/用时，出 ablation 图。

---

## 🛠️ 四、你今天就能推进的细节（Q1 打穿）

1. **把四个守卫写成纯函数**（方便单元测试）
   - `scopeGuard(e, goal) -> 0|1`
   - `planGuard(e, goal) -> 0|1`
   - `testGuard(e, goal, termLog?) -> 0|1`
   - `evidenceGuard(e) -> 0|0.5`
   - `driftScore(scores, weights, thresholds) -> {score, action}`

2. **建立 6 个最小单测**
   - 允许路径编辑 / 非允许路径编辑
   - modify 阶段使用非法 tool
   - 测试应跑未跑 / 已跑
   - 有/无 evidence
   - 综合 case 触发 warn 与 rollback

3. **做一个"例外机制"**（把假阳性降下来）
   - UI/CLI：`ack --reason="需要临时改依赖以修 build"`
   - 例外写入 `events.jsonl` 的 `evidence.links/notes`，下一次守卫见到 有效例外 可降权

---

## 🔗 五、为何 Q1→Q2→Q3 是正确的依赖关系

- **Q1 输出 = Q2/Q3 的训练与检索数据**：没有 `events.jsonl` 的"事实"，模式卡只能凭空想象。
- **Q1 还能给 Q2 提供"anti_patterns/risks"**：哪些越界最常见？直接写进卡，下次先天规避。
- **Q3 的"难度估计/视图路由"需要 Q1 的统计**：历史首试成功率、偏航率、偏航恢复时间 → 画像与路由的依据。

---

## ✅ 下一步行动

如果你认可上面的规范，我可以把这些 TS 接口 + 守卫函数样例直接合入你仓库的 `types/` 与 `src/guards/`，并加上6 条单测；你就能马上跑 Phase 1 的端到端（不依赖外部模型）。

接着，我们用 3–5 次真实 run 抽出 第一批模式卡（Q2），最后再接上 视图路由（Q3）。
```

```markdown
## 💭 问题分析与执行策略

> **核心思考**：我觉得这个框架已经搭好了，但是我认为这三个问题和它们的解决我们还没有完全地做好。就是说我想先解决最简单的这个问题，就是最后这个偏移的问题，就是这个drift的问题。然后再解决第二个和第三个问题，你觉得这个方法是不是好？因为我最后是想从简单到难开始，从一个实践的顺序来说，我是想先解决一个简单的问题，然后再解决其他的复杂的问题。
> 
> 我感觉第一个问题就是有一个数据之后，我们判断这个AI它是不是偏移了。这个数据是其他两个问题的先驱，因为如果没有这个数据的话，我们也没法match这个匹配度，对吧？我们也没有办法做这个复用的情况，learning from experience的情况。Q2和Q3其实取决于Q1，这是我的理解。所以我想先做Q1，再做Q2，再做Q3，不知道你同意这个方案吗？我觉得大体框架是有的，我们现在就要走一遍细节。
> 
> **技术细节需要细化**：举个例子比如Q1的四个守卫+计算score的方式+数据input/output都可以继续细化（是否要定一个ts or数据库结构，枚举结构），Q2的pattern的定义（这些如何定义：经验无法沉淀与迁移，造成重复劳动，是否要定一个ts or数据库结构，枚举结构），Q3的"用户水平 × 任务难度" 这两个也可以定义，是否要定一个ts or数据库结构，枚举结构）
> 
> 这是我的想法

## ✅ 执行策略确认

我完全同意你的执行顺序：先打穿 Q1（偏航检测）→ 再做 Q2（模式复用）→ 最后 Q3（动态抽象）。

理由很简单也很工程化：Q1 产出的"规范化事件 + 守卫分数"就是 Q2 抽卡与 Q3 路由的训练/检索数据。没有 Q1，就没有可复用的"事实语料库"。

下面我把三块一次性讲清楚：先给你实现顺序与验收标准，然后给精确的数据结构（TypeScript + 可选 SQLite DDL）与算法细节，最后给端到端示例（和你当前"翻译 README 却误改 requirements.txt"的例子完全对齐）。

---

## 📋 一、实施顺序（从简单到难）

### Phase 1（Q1：偏航检测，P0）

**目标**：对任意一次会话/提交，输出事件流与 drift 评分，并能告警/回滚。

**交付物**：
1. `events.jsonl`（来自 patch.diff/term.log 的规范化事件）
2. `guards.jsonl`（四守卫 + drift_score + action）
3. "最小 UI/CLI"：列出高分事件、显示原因、提供回滚命令

**验收**：
- ≥95% 的越界改动（不在 allowed_paths）被检出
- 假阳性 ≤10%（可通过例外机制逐步下降）

### Phase 2（Q2：模式复用，P1）

**目标**：把"做成的经历"沉淀成模式卡，能在新任务自动检索触发。

**交付物**：
1. `patterns/pc_*.json`（从多个 runs 抽取）
2. 检索与注入：给定 objective/issue_text → 返回命中的模式卡（含两档视图的文案骨架）

**验收**：
- 模式复用率↑、首试成功率↑、平均回合数↓（以小 A/B 验证）

### Phase 3（Q3：动态抽象，P1）

**目标**：同一卡两档视图，按"用户水平 × 任务难度"自动路由。

**交付物**：
1. `profiles/<user>.json`（画像）
2. 路由器：根据画像与任务难度，输出 terse | guided

**验收**：
- 新手在 guided 下成功率/稳定性更高；专家在 terse 下不中断

---

## 🔧 二、数据与接口规范（TS + JSONL + 可选 SQLite）

### 0) 共同枚举

```typescript
// phases/checkpoints
export type Phase = 'reproduce' | 'modify' | 'test' | 'regress';

// tools（新增 plan 类型）
export type Tool = 'edit' | 'shell' | 'browse' | 'plan';

// guard action
export type GuardAction = 'ok' | 'warn' | 'rollback';

// user level & task difficulty
export type UserLevel = 'novice' | 'intermediate' | 'expert';
export type TaskDifficulty = 'low' | 'medium' | 'high';

// confidence levels（Chat-only 用）
export type Confidence = 'low' | 'medium' | 'high';
```

---

### 1) Q1：输入/输出与算法

#### 1.1 目标定义（goal.json）

```typescript
export interface GoalConfig {
  run_id: string;
  objective: string;                         // e.g., "Translate README.md to Chinese"
  allowed_paths: string[];                   // allow-list (prefix match)
  forbidden_paths?: string[];                // optional block-list
  checkpoints: Phase[];                      // ["reproduce","modify","test","regress"]
  required_tests?: string[];                 // names/regex you expect to run/ pass
  allowed_tools_by_phase?: Partial<Record<Phase, Tool[]>>; // default 见下
  thresholds?: { warn: number; rollback: number };         // default 0.5/0.8
  meta?: Record<string, any>;                // 任意扩展
}
```

**默认策略**（若 allowed_tools_by_phase 未给出）：
- reproduce: ['shell','browse']
- modify:    ['edit','shell']
- test:      ['shell']
- regress:   ['shell']

**默认阈值**：warn=0.5，rollback=0.8

#### 1.2 事件（events.jsonl）

```typescript
export interface BaseEvent {
  id: string;                 // uuid
  run_id: string;
  step: number;               // 1,2,3...
  ts?: string;                // ISO time
  phase: Phase;
  tool: Tool;
  why?: string;               // rationale in short
  evidence?: {
    tests?: string[];         // tests names/assertions referenced
    logs?: string[];          // log lines digests or links
    links?: string[];         // issue/PR/docs links
  };
}

export interface EditEvent extends BaseEvent {
  tool: 'edit';
  where: { path: string; start?: number; end?: number };
  what: { diff?: string; ast_hint?: string };
}

export interface PlanEvent extends BaseEvent {
  tool: 'plan';
  where: { path: string; start?: number; end?: number };
  confidence?: Confidence;  // Chat-only 提取的置信度
}

export interface ShellEvent extends BaseEvent {
  tool: 'shell';
  cmd: string;
  exit_code?: number;
  stdout_digest?: string;     // hash/first-N lines
}

export type Event = EditEvent | PlanEvent | ShellEvent;
```

**JSONL 示例**（Diff 路线）：

```json
{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit","where":{"path":"README.md"},"what":{"diff":"(hunk)"},"why":"from patch.diff"}
{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit","where":{"path":"requirements.txt"},"what":{"diff":"(hunk)"}}
{"id":"e3","run_id":"r42","step":3,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
{"id":"e4","run_id":"r42","step":4,"phase":"test","tool":"shell","cmd":"pytest -k whitelist_diff_check"}
```

**Chat-only 示例**：

```json
{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan","where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}
{"id":"e2","run_id":"r60","step":2,"phase":"modify","tool":"edit","where":{"path":"README.md"},"why":"已将英文内容改为中文","confidence":"high"}
{"id":"t1001","run_id":"r60","step":1001,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
```

#### 1.3 守卫输出（guards.jsonl）

```typescript
export interface GuardScores {
  id: string;                 // match event id
  run_id: string;
  step: number;
  scope_guard: number;        // 0~1
  plan_guard: number;         // 0~1
  test_guard: number;         // 0~1
  evidence_guard: number;     // 0~1
  drift_score: number;        // weighted sum
  action: GuardAction;        // ok | warn | rollback
  file?: string;              // for edit events
  notes?: string;             // reason for flag
}
```

**打分算法**（可直接落地）：

```typescript
// 权重（可配置）
const W = { scope: 0.4, plan: 0.3, test: 0.2, evidence: 0.1 };

// 重要：仅对 tool=edit 计分，tool=plan 恒 action=ok
if (event.tool === 'plan') {
  return { scope_guard: 0, plan_guard: 0, test_guard: 0, evidence_guard: 0, 
           drift_score: 0, action: 'ok' };
}

// ScopeGuard：编辑是否越界（prefix allow-list）
scope_guard = (event.tool==='edit')
  ? (inAllowed(event.where.path, goal.allowed_paths) ? 0 : 1)
  : 0;

// PlanGuard：此 phase 是否允许此 tool/此路径类别
plan_guard = (() => {
  const allowTools = goal.allowed_tools_by_phase?.[event.phase] || defaultTools[event.phase];
  if (!allowTools.includes(event.tool)) return 1;
  if (event.tool==='edit' && !inAllowed(event.where.path, goal.allowed_paths)) return 1;
  return 0;
})();

// TestGuard：若 phase 是 test/regress，是否跑了/通过了 required_tests
// MVP：看到相应 pytest 命令则 0，否则 1（或结合 term.log 解析通过率）
test_guard = ((event.phase==='test' || event.phase==='regress') && event.tool==='shell')
  ? (coversRequired(event.cmd, goal.required_tests) ? 0 : 1)
  : 0;

// EvidenceGuard：modify 阶段的 edit 事件，是否带有 tests/logs/links 作为证据
evidence_guard = (event.phase==='modify' && event.tool==='edit')
  ? (event.evidence && (event.evidence.tests?.length || event.evidence.logs?.length || event.evidence.links?.length) ? 0 : 0.5)
  : 0;

// 综合：
drift_score = W.scope*scope_guard + W.plan*plan_guard + W.test*test_guard + W.evidence*evidence_guard;

// 动作：
action = (drift_score >= (goal.thresholds?.rollback ?? 0.8)) ? 'rollback'
       : (drift_score >= (goal.thresholds?.warn ?? 0.5))     ? 'warn'
       : 'ok';
```

**JSONL 示例**：

```json
{"id":"e1","run_id":"r42","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md"}
{"id":"e2","run_id":"r42","step":2,"scope_guard":1,"plan_guard":1,"test_guard":0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt","notes":"not in allowed_paths"}
```

**Q1 的评测**：
- 检出率（真正例 / 全部偏航）
- 误报率（假正例 / 全部告警）
- 偏航恢复时间（首次 warn → 回到正确 checkpoint 的步数/秒）
- 覆盖面（被守卫覆盖的偏航类型占比：路径越界/错误 phase/未跑测试/无证据）

---

### 2) Q2：模式卡定义与检索（在 Q1 打好后做）

#### 2.1 模式卡（patterns/pc_*.json）

```typescript
export interface PatternCard {
  version: string;                     // e.g., "1.0"
  pattern_id: string;                  // "pc_doc_only_change"
  title: string;                       // 人类可读标题
  triggers: string[];                  // 检索关键词/正则
  steps: string[];                     // 关键步骤（可用于计划/提示）
  invariants: string[];                // 不变量（必须成立的约束）
  anti_patterns?: string[];            // 禁止或常见误用
  eval_examples?: string[];            // 相关测试/验证名
  risks?: string[];                    // 风险提示（何时需要升级审核/例外）
  views: {                             // Q3 用
    terse: string;                     // 专家版
    guided: string;                    // 新手版
  };
  provenance: {                        // 溯源
    source_runs: string[];             // ["r42","r51"...]
    created_by: string;                // user id
    created_at: string;
  };
  metrics?: {                          // 可选：这张卡带来的 uplift 记录
    reuse_count: number;
    first_try_uplift?: number;
  };
}
```

**最小检索打分**（先规则 + 关键词覆盖；后续可接向量）：

```typescript
score = hits(triggers, goal.objective + issue_text) / triggers.length
// 冲突降权：若卡的 invariants 与 goal.allowed_paths/forbidden_paths 冲突，score -= 0.3
// 阶段性加权：若 Q1 的守卫告警类型与卡的 anti_patterns 相符，优先级↑
```

**沉淀策略**：
- 触发条件：本次 run 通过验证（或人工确认"做对了"）
- 合并：多 run 同类卡可合并（并保留 source_runs 列表）
- 进入库标准：能带来明显 uplift（首试成功率/回合数/时间）才纳入团队库

---

### 3) Q3：画像与路由

#### 3.1 用户画像（profiles/*.json）

```typescript
export interface UserProfile {
  user_id: string;
  self_report: UserLevel;                // 自报水平
  hist_first_try_success: number;        // 0~1
  pref?: 'guided' | 'terse';             // 明示偏好（可覆盖自动路由）
  notes?: string;
}
```

#### 3.2 任务难度估计（无需完美，先启发式）

```typescript
export interface TaskDescriptor {
  files_touched_est?: number;    // 预估修改文件数
  loc_delta_est?: number;        // 预估变更行数
  repo_familiarity?: number;     // 0~1（按贡献/最近互动/文件相似度）
  risk_flags?: string[];         // e.g., ["dependency","security","db-migration"]
}

function estimateDifficulty(d: TaskDescriptor): TaskDifficulty {
  const score = (d.files_touched_est||0)/5 + (d.loc_delta_est||0)/200 + (1-(d.repo_familiarity||0));
  if (score < 0.8) return 'low';
  if (score < 1.6) return 'medium';
  return 'high';
}
```

#### 3.3 视图路由（MVP）

```typescript
function chooseView(profile: UserProfile, task: TaskDescriptor): 'guided'|'terse' {
  const diff = estimateDifficulty(task);
  if (profile.pref) return profile.pref;
  if (profile.self_report === 'novice') return 'guided';
  if (diff === 'high') return 'guided';
  if (profile.hist_first_try_success < 0.5) return 'guided';
  return 'terse';
}
```


---

### 4) 可选数据库（SQLite DDL，占位可后置）

JSONL 先跑通，SQLite 便于做统计/报表/多用户协作。

```sql
-- runs
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY,
  created_at TEXT,
  objective TEXT
);

-- goals
CREATE TABLE goals (
  run_id TEXT,
  content JSON,
  PRIMARY KEY(run_id)
);

-- events
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  ts TEXT,
  phase TEXT,
  tool TEXT,
  path TEXT,
  cmd TEXT,
  payload JSON
);

-- guards
CREATE TABLE guard_scores (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  scope REAL, plan REAL, test REAL, evidence REAL,
  drift REAL, action TEXT, file TEXT, notes TEXT
);

-- patterns
CREATE TABLE patterns (
  pattern_id TEXT PRIMARY KEY,
  version TEXT,
  title TEXT,
  content JSON,
  reuse_count INTEGER DEFAULT 0
);

-- profiles
CREATE TABLE profiles (
  user_id TEXT PRIMARY KEY,
  content JSON
);
```

---

## 🚀 三、端到端（以你的"文档任务跑题"为例）

**输入**：
- `goal.json`：只允许 README.md / docs/**
- `patch.diff`：改了 README.md 并误改 requirements.txt
- （可选）`term.log`：包含 pytest -k doc_lang_check 与 pytest -k whitelist_diff_check

**步骤**：
1. `patch2events` → 生成两条 edit 事件（README.md / requirements.txt）
2. `term2events` → 生成两条 shell 事件（测试）
3. `events2guards` → 对 requirements.txt 给出 Scope=1.0，Plan=1.0，Evidence=0.5 → drift=0.85 → action=warn
4. （通过/确认后）抽卡 → `pc_doc_only_change` 入库
5. 新任务"翻译文档"启动时，检索命中该卡：
   - terse 给专家：白名单 + 禁改依赖 + 两个检查
   - guided 给新手：逐步配置白名单/语言检测/例外流程/坑点
6. 度量：相似任务在有卡 vs 无卡下，比较首试成功率/回合数/用时，出 ablation 图。

---

## 🛠️ 四、你今天就能推进的细节（Q1 打穿）

1. **把四个守卫写成纯函数**（方便单元测试）
   - `scopeGuard(e, goal) -> 0|1`
   - `planGuard(e, goal) -> 0|1`
   - `testGuard(e, goal, termLog?) -> 0|1`
   - `evidenceGuard(e) -> 0|0.5`
   - `driftScore(scores, weights, thresholds) -> {score, action}`

2. **建立 6 个最小单测**
   - 允许路径编辑 / 非允许路径编辑
   - modify 阶段使用非法 tool
   - 测试应跑未跑 / 已跑
   - 有/无 evidence
   - 综合 case 触发 warn 与 rollback

3. **做一个"例外机制"**（把假阳性降下来）
   - UI/CLI：`ack --reason="需要临时改依赖以修 build"`
   - 例外写入 `events.jsonl` 的 `evidence.links/notes`，下一次守卫见到 有效例外 可降权

---

## 🔗 五、为何 Q1→Q2→Q3 是正确的依赖关系

- **Q1 输出 = Q2/Q3 的训练与检索数据**：没有 `events.jsonl` 的"事实"，模式卡只能凭空想象。
- **Q1 还能给 Q2 提供"anti_patterns/risks"**：哪些越界最常见？直接写进卡，下次先天规避。
- **Q3 的"难度估计/视图路由"需要 Q1 的统计**：历史首试成功率、偏航率、偏航恢复时间 → 画像与路由的依据。

---

## ✅ 下一步行动

如果你认可上面的规范，我可以把这些 TS 接口 + 守卫函数样例直接合入你仓库的 `types/` 与 `src/guards/`，并加上6 条单测；你就能马上跑 Phase 1 的端到端（不依赖外部模型）。

接着，我们用 3–5 次真实 run 抽出 第一批模式卡（Q2），最后再接上 视图路由（Q3）。
```

```markdown
**JSONL 示例**：

```json
{"id":"e1","run_id":"r42","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md"}
{"id":"e2","run_id":"r42","step":2,"scope_guard":1,"plan_guard":1,"test_guard":0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt"}
{"id":"p1","run_id":"r60","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md","notes":"plan event, not scored"}
```
```

```markdown
## 💭 问题分析与执行策略

> **核心思考**：我觉得这个框架已经搭好了，但是我认为这三个问题和它们的解决我们还没有完全地做好。就是说我想先解决最简单的这个问题，就是最后这个偏移的问题，就是这个drift的问题。然后再解决第二个和第三个问题，你觉得这个方法是不是好？因为我最后是想从简单到难开始，从一个实践的顺序来说，我是想先解决一个简单的问题，然后再解决其他的复杂的问题。
> 
> 我感觉第一个问题就是有一个数据之后，我们判断这个AI它是不是偏移了。这个数据是其他两个问题的先驱，因为如果没有这个数据的话，我们也没法match这个匹配度，对吧？我们也没有办法做这个复用的情况，learning from experience的情况。Q2和Q3其实取决于Q1，这是我的理解。所以我想先做Q1，再做Q2，再做Q3，不知道你同意这个方案吗？我觉得大体框架是有的，我们现在就要走一遍细节。
> 
> **技术细节需要细化**：举个例子比如Q1的四个守卫+计算score的方式+数据input/output都可以继续细化（是否要定一个ts or数据库结构，枚举结构），Q2的pattern的定义（这些如何定义：经验无法沉淀与迁移，造成重复劳动，是否要定一个ts or数据库结构，枚举结构），Q3的"用户水平 × 任务难度" 这两个也可以定义，是否要定一个ts or数据库结构，枚举结构）
> 
> 这是我的想法

## ✅ 执行策略确认

我完全同意你的执行顺序：先打穿 Q1（偏航检测）→ 再做 Q2（模式复用）→ 最后 Q3（动态抽象）。

理由很简单也很工程化：Q1 产出的"规范化事件 + 守卫分数"就是 Q2 抽卡与 Q3 路由的训练/检索数据。没有 Q1，就没有可复用的"事实语料库"。

下面我把三块一次性讲清楚：先给你实现顺序与验收标准，然后给精确的数据结构（TypeScript + 可选 SQLite DDL）与算法细节，最后给端到端示例（和你当前"翻译 README 却误改 requirements.txt"的例子完全对齐）。

---

## 📋 一、实施顺序（从简单到难）

### Phase 1（Q1：偏航检测，P0）

**目标**：对任意一次会话/提交，输出事件流与 drift 评分，并能告警/回滚。

**交付物**：
1. `events.jsonl`（来自 patch.diff/term.log 的规范化事件）
2. `guards.jsonl`（四守卫 + drift_score + action）
3. "最小 UI/CLI"：列出高分事件、显示原因、提供回滚命令

**验收**：
- ≥95% 的越界改动（不在 allowed_paths）被检出
- 假阳性 ≤10%（可通过例外机制逐步下降）

### Phase 2（Q2：模式复用，P1）

**目标**：把"做成的经历"沉淀成模式卡，能在新任务自动检索触发。

**交付物**：
1. `patterns/pc_*.json`（从多个 runs 抽取）
2. 检索与注入：给定 objective/issue_text → 返回命中的模式卡（含两档视图的文案骨架）

**验收**：
- 模式复用率↑、首试成功率↑、平均回合数↓（以小 A/B 验证）

### Phase 3（Q3：动态抽象，P1）

**目标**：同一卡两档视图，按"用户水平 × 任务难度"自动路由。

**交付物**：
1. `profiles/<user>.json`（画像）
2. 路由器：根据画像与任务难度，输出 terse | guided

**验收**：
- 新手在 guided 下成功率/稳定性更高；专家在 terse 下不中断

---

## 🔧 二、数据与接口规范（TS + JSONL + 可选 SQLite）

### 0) 共同枚举

```typescript
// phases/checkpoints
export type Phase = 'reproduce' | 'modify' | 'test' | 'regress';

// tools（新增 plan 类型）
export type Tool = 'edit' | 'shell' | 'browse' | 'plan';

// guard action
export type GuardAction = 'ok' | 'warn' | 'rollback';

// user level & task difficulty
export type UserLevel = 'novice' | 'intermediate' | 'expert';
export type TaskDifficulty = 'low' | 'medium' | 'high';

// confidence levels（Chat-only 用）
export type Confidence = 'low' | 'medium' | 'high';
```

---

### 1) Q1：输入/输出与算法

#### 1.1 目标定义（goal.json）

```typescript
export interface GoalConfig {
  run_id: string;
  objective: string;                         // e.g., "Translate README.md to Chinese"
  allowed_paths: string[];                   // allow-list (prefix match)
  forbidden_paths?: string[];                // optional block-list
  checkpoints: Phase[];                      // ["reproduce","modify","test","regress"]
  required_tests?: string[];                 // names/regex you expect to run/ pass
  allowed_tools_by_phase?: Partial<Record<Phase, Tool[]>>; // default 见下
  thresholds?: { warn: number; rollback: number };         // default 0.5/0.8
  meta?: Record<string, any>;                // 任意扩展
}
```

**默认策略**（若 allowed_tools_by_phase 未给出）：
- reproduce: ['shell','browse']
- modify:    ['edit','shell']
- test:      ['shell']
- regress:   ['shell']

**默认阈值**：warn=0.5，rollback=0.8

#### 1.2 事件（events.jsonl）

```typescript
export interface BaseEvent {
  id: string;                 // uuid
  run_id: string;
  step: number;               // 1,2,3...
  ts?: string;                // ISO time
  phase: Phase;
  tool: Tool;
  why?: string;               // rationale in short
  evidence?: {
    tests?: string[];         // tests names/assertions referenced
    logs?: string[];          // log lines digests or links
    links?: string[];         // issue/PR/docs links
  };
}

export interface EditEvent extends BaseEvent {
  tool: 'edit';
  where: { path: string; start?: number; end?: number };
  what: { diff?: string; ast_hint?: string };
}

export interface PlanEvent extends BaseEvent {
  tool: 'plan';
  where: { path: string; start?: number; end?: number };
  confidence?: Confidence;  // Chat-only 提取的置信度
}

export interface ShellEvent extends BaseEvent {
  tool: 'shell';
  cmd: string;
  exit_code?: number;
  stdout_digest?: string;     // hash/first-N lines
}

export type Event = EditEvent | PlanEvent | ShellEvent;
```

**JSONL 示例**（Diff 路线）：

```json
{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit","where":{"path":"README.md"},"what":{"diff":"(hunk)"},"why":"from patch.diff"}
{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit","where":{"path":"requirements.txt"},"what":{"diff":"(hunk)"}}
{"id":"e3","run_id":"r42","step":3,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
{"id":"e4","run_id":"r42","step":4,"phase":"test","tool":"shell","cmd":"pytest -k whitelist_diff_check"}
```

**Chat-only 示例**：

```json
{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan","where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}
{"id":"e2","run_id":"r60","step":2,"phase":"modify","tool":"edit","where":{"path":"README.md"},"why":"已将英文内容改为中文","confidence":"high"}
{"id":"t1001","run_id":"r60","step":1001,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
```

#### 1.3 守卫输出（guards.jsonl）

```typescript
export interface GuardScores {
  id: string;                 // match event id
  run_id: string;
  step: number;
  scope_guard: number;        // 0~1
  plan_guard: number;         // 0~1
  test_guard: number;         // 0~1
  evidence_guard: number;     // 0~1
  drift_score: number;        // weighted sum
  action: GuardAction;        // ok | warn | rollback
  file?: string;              // for edit events
  notes?: string;             // reason for flag
}
```

**打分算法**（可直接落地）：

```typescript
// 权重（可配置）
const W = { scope: 0.4, plan: 0.3, test: 0.2, evidence: 0.1 };

// 重要：仅对 tool=edit 计分，tool=plan 恒 action=ok
if (event.tool === 'plan') {
  return { scope_guard: 0, plan_guard: 0, test_guard: 0, evidence_guard: 0, 
           drift_score: 0, action: 'ok' };
}

// ScopeGuard：编辑是否越界（prefix allow-list）
scope_guard = (event.tool==='edit')
  ? (inAllowed(event.where.path, goal.allowed_paths) ? 0 : 1)
  : 0;

// PlanGuard：此 phase 是否允许此 tool/此路径类别
plan_guard = (() => {
  const allowTools = goal.allowed_tools_by_phase?.[event.phase] || defaultTools[event.phase];
  if (!allowTools.includes(event.tool)) return 1;
  if (event.tool==='edit' && !inAllowed(event.where.path, goal.allowed_paths)) return 1;
  return 0;
})();

// TestGuard：若 phase 是 test/regress，是否跑了/通过了 required_tests
// MVP：看到相应 pytest 命令则 0，否则 1（或结合 term.log 解析通过率）
test_guard = ((event.phase==='test' || event.phase==='regress') && event.tool==='shell')
  ? (coversRequired(event.cmd, goal.required_tests) ? 0 : 1)
  : 0;

// EvidenceGuard：modify 阶段的 edit 事件，是否带有 tests/logs/links 作为证据
evidence_guard = (event.phase==='modify' && event.tool==='edit')
  ? (event.evidence && (event.evidence.tests?.length || event.evidence.logs?.length || event.evidence.links?.length) ? 0 : 0.5)
  : 0;

// 综合：
drift_score = W.scope*scope_guard + W.plan*plan_guard + W.test*test_guard + W.evidence*evidence_guard;

// 动作：
action = (drift_score >= (goal.thresholds?.rollback ?? 0.8)) ? 'rollback'
       : (drift_score >= (goal.thresholds?.warn ?? 0.5))     ? 'warn'
       : 'ok';
```

**JSONL 示例**：

```json
{"id":"e1","run_id":"r42","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md"}
{"id":"e2","run_id":"r42","step":2,"scope_guard":1,"plan_guard":1,"test_guard":0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt","notes":"not in allowed_paths"}
{"id":"p1","run_id":"r60","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md","notes":"plan event, not scored"}
```

**Q1 的评测**：
- 检出率（真正例 / 全部偏航）
- 误报率（假正例 / 全部告警）
- 偏航恢复时间（首次 warn → 回到正确 checkpoint 的步数/秒）
- 覆盖面（被守卫覆盖的偏航类型占比：路径越界/错误 phase/未跑测试/无证据）

---

### 2) Q2：模式卡定义与检索（在 Q1 打好后做）

#### 2.1 模式卡（patterns/pc_*.json）

```typescript
export interface PatternCard {
  version: string;                     // e.g., "1.0"
  pattern_id: string;                  // "pc_doc_only_change"
  title: string;                       // 人类可读标题
  triggers: string[];                  // 检索关键词/正则
  steps: string[];                     // 关键步骤（可用于计划/提示）
  invariants: string[];                // 不变量（必须成立的约束）
  anti_patterns?: string[];            // 禁止或常见误用
  eval_examples?: string[];            // 相关测试/验证名
  risks?: string[];                    // 风险提示（何时需要升级审核/例外）
  views: {                             // Q3 用
    terse: string;                     // 专家版
    guided: string;                    // 新手版
  };
  provenance: {                        // 溯源
    source_runs: string[];             // ["r42","r51"...]
    created_by: string;                // user id
    created_at: string;
  };
  metrics?: {                          // 可选：这张卡带来的 uplift 记录
    reuse_count: number;
    first_try_uplift?: number;
  };
}
```

**最小检索打分**（先规则 + 关键词覆盖；后续可接向量）：

```typescript
score = hits(triggers, goal.objective + issue_text) / triggers.length
// 冲突降权：若卡的 invariants 与 goal.allowed_paths/forbidden_paths 冲突，score -= 0.3
// 阶段性加权：若 Q1 的守卫告警类型与卡的 anti_patterns 相符，优先级↑
```

**沉淀策略**：
- 触发条件：本次 run 通过验证（或人工确认"做对了"）
- 合并：多 run 同类卡可合并（并保留 source_runs 列表）
- 进入库标准：能带来明显 uplift（首试成功率/回合数/时间）才纳入团队库

---

### 3) Q3：画像与路由

#### 3.1 用户画像（profiles/*.json）

```typescript
export interface UserProfile {
  user_id: string;
  self_report: UserLevel;                // 自报水平
  hist_first_try_success: number;        // 0~1
  pref?: 'guided' | 'terse';             // 明示偏好（可覆盖自动路由）
  notes?: string;
}
```

#### 3.2 任务难度估计（无需完美，先启发式）

```typescript
export interface TaskDescriptor {
  files_touched_est?: number;    // 预估修改文件数
  loc_delta_est?: number;        // 预估变更行数
  repo_familiarity?: number;     // 0~1（按贡献/最近互动/文件相似度）
  risk_flags?: string[];         // e.g., ["dependency","security","db-migration"]
}

function estimateDifficulty(d: TaskDescriptor): TaskDifficulty {
  const score = (d.files_touched_est||0)/5 + (d.loc_delta_est||0)/200 + (1-(d.repo_familiarity||0));
  if (score < 0.8) return 'low';
  if (score < 1.6) return 'medium';
  return 'high';
}
```

#### 3.3 视图路由（MVP）

```typescript
function chooseView(profile: UserProfile, task: TaskDescriptor): 'guided'|'terse' {
  const diff = estimateDifficulty(task);
  if (profile.pref) return profile.pref;
  if (profile.self_report === 'novice') return 'guided';
  if (diff === 'high') return 'guided';
  if (profile.hist_first_try_success < 0.5) return 'guided';
  return 'terse';
}
```


---

### 4) 可选数据库（SQLite DDL，占位可后置）

JSONL 先跑通，SQLite 便于做统计/报表/多用户协作。

```sql
-- runs
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY,
  created_at TEXT,
  objective TEXT
);

-- goals
CREATE TABLE goals (
  run_id TEXT,
  content JSON,
  PRIMARY KEY(run_id)
);

-- events
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  ts TEXT,
  phase TEXT,
  tool TEXT,
  path TEXT,
  cmd TEXT,
  payload JSON
);

-- guards
CREATE TABLE guard_scores (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  scope REAL, plan REAL, test REAL, evidence REAL,
  drift REAL, action TEXT, file TEXT, notes TEXT
);

-- patterns
CREATE TABLE patterns (
  pattern_id TEXT PRIMARY KEY,
  version TEXT,
  title TEXT,
  content JSON,
  reuse_count INTEGER DEFAULT 0
);

-- profiles
CREATE TABLE profiles (
  user_id TEXT PRIMARY KEY,
  content JSON
);
```

---

## 🚀 三、端到端（以你的"文档任务跑题"为例）

**输入**：
- `goal.json`：只允许 README.md / docs/**
- `patch.diff`：改了 README.md 并误改 requirements.txt
- （可选）`term.log`：包含 pytest -k doc_lang_check 与 pytest -k whitelist_diff_check

**步骤**：
1. `patch2events` → 生成两条 edit 事件（README.md / requirements.txt）
2. `term2events` → 生成两条 shell 事件（测试）
3. `events2guards` → 对 requirements.txt 给出 Scope=1.0，Plan=1.0，Evidence=0.5 → drift=0.85 → action=warn
4. （通过/确认后）抽卡 → `pc_doc_only_change` 入库
5. 新任务"翻译文档"启动时，检索命中该卡：
   - terse 给专家：白名单 + 禁改依赖 + 两个检查
   - guided 给新手：逐步配置白名单/语言检测/例外流程/坑点
6. 度量：相似任务在有卡 vs 无卡下，比较首试成功率/回合数/用时，出 ablation 图。

---

## 🛠️ 四、你今天就能推进的细节（Q1 打穿）

1. **把四个守卫写成纯函数**（方便单元测试）
   - `scopeGuard(e, goal) -> 0|1`
   - `planGuard(e, goal) -> 0|1`
   - `testGuard(e, goal, termLog?) -> 0|1`
   - `evidenceGuard(e) -> 0|0.5`
   - `driftScore(scores, weights, thresholds) -> {score, action}`

2. **建立 6 个最小单测**
   - 允许路径编辑 / 非允许路径编辑
   - modify 阶段使用非法 tool
   - 测试应跑未跑 / 已跑
   - 有/无 evidence
   - 综合 case 触发 warn 与 rollback

3. **做一个"例外机制"**（把假阳性降下来）
   - UI/CLI：`ack --reason="需要临时改依赖以修 build"`
   - 例外写入 `events.jsonl` 的 `evidence.links/notes`，下一次守卫见到 有效例外 可降权

---

## 🔗 五、为何 Q1→Q2→Q3 是正确的依赖关系

- **Q1 输出 = Q2/Q3 的训练与检索数据**：没有 `events.jsonl` 的"事实"，模式卡只能凭空想象。
- **Q1 还能给 Q2 提供"anti_patterns/risks"**：哪些越界最常见？直接写进卡，下次先天规避。
- **Q3 的"难度估计/视图路由"需要 Q1 的统计**：历史首试成功率、偏航率、偏航恢复时间 → 画像与路由的依据。

---

## ✅ 下一步行动

如果你认可上面的规范，我可以把这些 TS 接口 + 守卫函数样例直接合入你仓库的 `types/` 与 `src/guards/`，并加上6 条单测；你就能马上跑 Phase 1 的端到端（不依赖外部模型）。

接着，我们用 3–5 次真实 run 抽出 第一批模式卡（Q2），最后再接上 视图路由（Q3）。
```

```markdown
## 💭 问题分析与执行策略

> **核心思考**：我觉得这个框架已经搭好了，但是我认为这三个问题和它们的解决我们还没有完全地做好。就是说我想先解决最简单的这个问题，就是最后这个偏移的问题，就是这个drift的问题。然后再解决第二个和第三个问题，你觉得这个方法是不是好？因为我最后是想从简单到难开始，从一个实践的顺序来说，我是想先解决一个简单的问题，然后再解决其他的复杂的问题。
> 
> 我感觉第一个问题就是有一个数据之后，我们判断这个AI它是不是偏移了。这个数据是其他两个问题的先驱，因为如果没有这个数据的话，我们也没法match这个匹配度，对吧？我们也没有办法做这个复用的情况，learning from experience的情况。Q2和Q3其实取决于Q1，这是我的理解。所以我想先做Q1，再做Q2，再做Q3，不知道你同意这个方案吗？我觉得大体框架是有的，我们现在就要走一遍细节。
> 
> **技术细节需要细化**：举个例子比如Q1的四个守卫+计算score的方式+数据input/output都可以继续细化（是否要定一个ts or数据库结构，枚举结构），Q2的pattern的定义（这些如何定义：经验无法沉淀与迁移，造成重复劳动，是否要定一个ts or数据库结构，枚举结构），Q3的"用户水平 × 任务难度" 这两个也可以定义，是否要定一个ts or数据库结构，枚举结构）
> 
> 这是我的想法

## ✅ 执行策略确认

我完全同意你的执行顺序：先打穿 Q1（偏航检测）→ 再做 Q2（模式复用）→ 最后 Q3（动态抽象）。

理由很简单也很工程化：Q1 产出的"规范化事件 + 守卫分数"就是 Q2 抽卡与 Q3 路由的训练/检索数据。没有 Q1，就没有可复用的"事实语料库"。

下面我把三块一次性讲清楚：先给你实现顺序与验收标准，然后给精确的数据结构（TypeScript + 可选 SQLite DDL）与算法细节，最后给端到端示例（和你当前"翻译 README 却误改 requirements.txt"的例子完全对齐）。

---

## 📋 一、实施顺序（从简单到难）

### Phase 1（Q1：偏航检测，P0）

**目标**：对任意一次会话/提交，输出事件流与 drift 评分，并能告警/回滚。

**交付物**：
1. `events.jsonl`（来自 patch.diff/term.log 的规范化事件）
2. `guards.jsonl`（四守卫 + drift_score + action）
3. "最小 UI/CLI"：列出高分事件、显示原因、提供回滚命令

**验收**：
- ≥95% 的越界改动（不在 allowed_paths）被检出
- 假阳性 ≤10%（可通过例外机制逐步下降）

### Phase 2（Q2：模式复用，P1）

**目标**：把"做成的经历"沉淀成模式卡，能在新任务自动检索触发。

**交付物**：
1. `patterns/pc_*.json`（从多个 runs 抽取）
2. 检索与注入：给定 objective/issue_text → 返回命中的模式卡（含两档视图的文案骨架）

**验收**：
- 模式复用率↑、首试成功率↑、平均回合数↓（以小 A/B 验证）

### Phase 3（Q3：动态抽象，P1）

**目标**：同一卡两档视图，按"用户水平 × 任务难度"自动路由。

**交付物**：
1. `profiles/<user>.json`（画像）
2. 路由器：根据画像与任务难度，输出 terse | guided

**验收**：
- 新手在 guided 下成功率/稳定性更高；专家在 terse 下不中断

---

## 🔧 二、数据与接口规范（TS + JSONL + 可选 SQLite）

### 0) 共同枚举

```typescript
// phases/checkpoints
export type Phase = 'reproduce' | 'modify' | 'test' | 'regress';

// tools（新增 plan 类型）
export type Tool = 'edit' | 'shell' | 'browse' | 'plan';

// guard action
export type GuardAction = 'ok' | 'warn' | 'rollback';

// user level & task difficulty
export type UserLevel = 'novice' | 'intermediate' | 'expert';
export type TaskDifficulty = 'low' | 'medium' | 'high';

// confidence levels（Chat-only 用）
export type Confidence = 'low' | 'medium' | 'high';
```

---

### 1) Q1：输入/输出与算法

#### 1.1 目标定义（goal.json）

```typescript
export interface GoalConfig {
  run_id: string;
  objective: string;                         // e.g., "Translate README.md to Chinese"
  allowed_paths: string[];                   // allow-list (prefix match)
  forbidden_paths?: string[];                // optional block-list
  checkpoints: Phase[];                      // ["reproduce","modify","test","regress"]
  required_tests?: string[];                 // names/regex you expect to run/ pass
  allowed_tools_by_phase?: Partial<Record<Phase, Tool[]>>; // default 见下
  thresholds?: { warn: number; rollback: number };         // default 0.5/0.8
  meta?: Record<string, any>;                // 任意扩展
}
```

**默认策略**（若 allowed_tools_by_phase 未给出）：
- reproduce: ['shell','browse']
- modify:    ['edit','shell']
- test:      ['shell']
- regress:   ['shell']

**默认阈值**：warn=0.5，rollback=0.8

#### 1.2 事件（events.jsonl）

```typescript
export interface BaseEvent {
  id: string;                 // uuid
  run_id: string;
  step: number;               // 1,2,3...
  ts?: string;                // ISO time
  phase: Phase;
  tool: Tool;
  why?: string;               // rationale in short
  evidence?: {
    tests?: string[];         // tests names/assertions referenced
    logs?: string[];          // log lines digests or links
    links?: string[];         // issue/PR/docs links
  };
}

export interface EditEvent extends BaseEvent {
  tool: 'edit';
  where: { path: string; start?: number; end?: number };
  what: { diff?: string; ast_hint?: string };
}

export interface PlanEvent extends BaseEvent {
  tool: 'plan';
  where: { path: string; start?: number; end?: number };
  confidence?: Confidence;  // Chat-only 提取的置信度
}

export interface ShellEvent extends BaseEvent {
  tool: 'shell';
  cmd: string;
  exit_code?: number;
  stdout_digest?: string;     // hash/first-N lines
}

export type Event = EditEvent | PlanEvent | ShellEvent;
```

**JSONL 示例**（Diff 路线）：

```json
{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit","where":{"path":"README.md"},"what":{"diff":"(hunk)"},"why":"from patch.diff"}
{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit","where":{"path":"requirements.txt"},"what":{"diff":"(hunk)"}}
{"id":"e3","run_id":"r42","step":3,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
{"id":"e4","run_id":"r42","step":4,"phase":"test","tool":"shell","cmd":"pytest -k whitelist_diff_check"}
```

**Chat-only 示例**：

```json
{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan","where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}
{"id":"e2","run_id":"r60","step":2,"phase":"modify","tool":"edit","where":{"path":"README.md"},"why":"已将英文内容改为中文","confidence":"high"}
{"id":"t1001","run_id":"r60","step":1001,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
```

#### 1.3 守卫输出（guards.jsonl）

```typescript
export interface GuardScores {
  id: string;                 // match event id
  run_id: string;
  step: number;
  scope_guard: number;        // 0~1
  plan_guard: number;         // 0~1
  test_guard: number;         // 0~1
  evidence_guard: number;     // 0~1
  drift_score: number;        // weighted sum
  action: GuardAction;        // ok | warn | rollback
  file?: string;              // for edit events
  notes?: string;             // reason for flag
}
```

**打分算法**（可直接落地）：

```typescript
// 权重（可配置）
const W = { scope: 0.4, plan: 0.3, test: 0.2, evidence: 0.1 };

// 重要：仅对 tool=edit 计分，tool=plan 恒 action=ok
if (event.tool === 'plan') {
  return { scope_guard: 0, plan_guard: 0, test_guard: 0, evidence_guard: 0, 
           drift_score: 0, action: 'ok' };
}

// ScopeGuard：编辑是否越界（prefix allow-list）
scope_guard = (event.tool==='edit')
  ? (inAllowed(event.where.path, goal.allowed_paths) ? 0 : 1)
  : 0;

// PlanGuard：此 phase 是否允许此 tool/此路径类别
plan_guard = (() => {
  const allowTools = goal.allowed_tools_by_phase?.[event.phase] || defaultTools[event.phase];
  if (!allowTools.includes(event.tool)) return 1;
  if (event.tool==='edit' && !inAllowed(event.where.path, goal.allowed_paths)) return 1;
  return 0;
})();

// TestGuard：若 phase 是 test/regress，是否跑了/通过了 required_tests
// MVP：看到相应 pytest 命令则 0，否则 1（或结合 term.log 解析通过率）
test_guard = ((event.phase==='test' || event.phase==='regress') && event.tool==='shell')
  ? (coversRequired(event.cmd, goal.required_tests) ? 0 : 1)
  : 0;

// EvidenceGuard：modify 阶段的 edit 事件，是否带有 tests/logs/links 作为证据
evidence_guard = (event.phase==='modify' && event.tool==='edit')
  ? (event.evidence && (event.evidence.tests?.length || event.evidence.logs?.length || event.evidence.links?.length) ? 0 : 0.5)
  : 0;

// 综合：
drift_score = W.scope*scope_guard + W.plan*plan_guard + W.test*test_guard + W.evidence*evidence_guard;

// 动作：
action = (drift_score >= (goal.thresholds?.rollback ?? 0.8)) ? 'rollback'
       : (drift_score >= (goal.thresholds?.warn ?? 0.5))     ? 'warn'
       : 'ok';
```

**JSONL 示例**：

```json
{"id":"e1","run_id":"r42","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md"}
{"id":"e2","run_id":"r42","step":2,"scope_guard":1,"plan_guard":1,"test_guard":0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt","notes":"not in allowed_paths"}
{"id":"p1","run_id":"r60","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md","notes":"plan event, not scored"}
```

**Q1 的评测**：
- 检出率（真正例 / 全部偏航）
- 误报率（假正例 / 全部告警）
- 偏航恢复时间（首次 warn → 回到正确 checkpoint 的步数/秒）
- 覆盖面（被守卫覆盖的偏航类型占比：路径越界/错误 phase/未跑测试/无证据）

---

### 2) Q2：模式卡定义与检索（在 Q1 打好后做）

#### 2.1 模式卡（patterns/pc_*.json）

```typescript
export interface PatternCard {
  version: string;                     // e.g., "1.0"
  pattern_id: string;                  // "pc_doc_only_change"
  title: string;                       // 人类可读标题
  triggers: string[];                  // 检索关键词/正则
  steps: string[];                     // 关键步骤（可用于计划/提示）
  invariants: string[];                // 不变量（必须成立的约束）
  anti_patterns?: string[];            // 禁止或常见误用
  eval_examples?: string[];            // 相关测试/验证名
  risks?: string[];                    // 风险提示（何时需要升级审核/例外）
  views: {                             // Q3 用
    terse: string;                     // 专家版
    guided: string;                    // 新手版
  };
  provenance: {                        // 溯源
    source_runs: string[];             // ["r42","r51"...]
    created_by: string;                // user id
    created_at: string;
  };
  metrics?: {                          // 可选：这张卡带来的 uplift 记录
    reuse_count: number;
    first_try_uplift?: number;
  };
}
```

**最小检索打分**（先规则 + 关键词覆盖；后续可接向量）：

```typescript
score = hits(triggers, goal.objective + issue_text) / triggers.length
// 冲突降权：若卡的 invariants 与 goal.allowed_paths/forbidden_paths 冲突，score -= 0.3
// 阶段性加权：若 Q1 的守卫告警类型与卡的 anti_patterns 相符，优先级↑
```

**沉淀策略**：
- 触发条件：本次 run 通过验证（或人工确认"做对了"）
- 合并：多 run 同类卡可合并（并保留 source_runs 列表）
- 进入库标准：能带来明显 uplift（首试成功率/回合数/时间）才纳入团队库

---

### 3) Q3：画像与路由

#### 3.1 用户画像（profiles/*.json）

```typescript
export interface UserProfile {
  user_id: string;
  self_report: UserLevel;                // 自报水平
  hist_first_try_success: number;        // 0~1
  pref?: 'guided' | 'terse';             // 明示偏好（可覆盖自动路由）
  notes?: string;
}
```

#### 3.2 任务难度估计（无需完美，先启发式）

```typescript
export interface TaskDescriptor {
  files_touched_est?: number;    // 预估修改文件数
  loc_delta_est?: number;        // 预估变更行数
  repo_familiarity?: number;     // 0~1（按贡献/最近互动/文件相似度）
  risk_flags?: string[];         // e.g., ["dependency","security","db-migration"]
}

function estimateDifficulty(d: TaskDescriptor): TaskDifficulty {
  const score = (d.files_touched_est||0)/5 + (d.loc_delta_est||0)/200 + (1-(d.repo_familiarity||0));
  if (score < 0.8) return 'low';
  if (score < 1.6) return 'medium';
  return 'high';
}
```

#### 3.3 视图路由（MVP）

```typescript
function chooseView(profile: UserProfile, task: TaskDescriptor): 'guided'|'terse' {
  const diff = estimateDifficulty(task);
  if (profile.pref) return profile.pref;
  if (profile.self_report === 'novice') return 'guided';
  if (diff === 'high') return 'guided';
  if (profile.hist_first_try_success < 0.5) return 'guided';
  return 'terse';
}
```


---

### 4) 可选数据库（SQLite DDL，占位可后置）

JSONL 先跑通，SQLite 便于做统计/报表/多用户协作。

```sql
-- runs
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY,
  created_at TEXT,
  objective TEXT
);

-- goals
CREATE TABLE goals (
  run_id TEXT,
  content JSON,
  PRIMARY KEY(run_id)
);

-- events
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  ts TEXT,
  phase TEXT,
  tool TEXT,
  path TEXT,
  cmd TEXT,
  payload JSON
);

-- guards
CREATE TABLE guard_scores (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  scope REAL, plan REAL, test REAL, evidence REAL,
  drift REAL, action TEXT, file TEXT, notes TEXT
);

-- patterns
CREATE TABLE patterns (
  pattern_id TEXT PRIMARY KEY,
  version TEXT,
  title TEXT,
  content JSON,
  reuse_count INTEGER DEFAULT 0
);

-- profiles
CREATE TABLE profiles (
  user_id TEXT PRIMARY KEY,
  content JSON
);
```

---

## 🚀 三、端到端（以你的"文档任务跑题"为例）

**输入**：
- `goal.json`：只允许 README.md / docs/**
- `patch.diff`：改了 README.md 并误改 requirements.txt
- （可选）`term.log`：包含 pytest -k doc_lang_check 与 pytest -k whitelist_diff_check

**步骤**：
1. `patch2events` → 生成两条 edit 事件（README.md / requirements.txt）
2. `term2events` → 生成两条 shell 事件（测试）
3. `events2guards` → 对 requirements.txt 给出 Scope=1.0，Plan=1.0，Evidence=0.5 → drift=0.85 → action=warn
4. （通过/确认后）抽卡 → `pc_doc_only_change` 入库
5. 新任务"翻译文档"启动时，检索命中该卡：
   - terse 给专家：白名单 + 禁改依赖 + 两个检查
   - guided 给新手：逐步配置白名单/语言检测/例外流程/坑点
6. 度量：相似任务在有卡 vs 无卡下，比较首试成功率/回合数/用时，出 ablation 图。

---

## 🛠️ 四、你今天就能推进的细节（Q1 打穿）

1. **把四个守卫写成纯函数**（方便单元测试）
   - `scopeGuard(e, goal) -> 0|1`
   - `planGuard(e, goal) -> 0|1`
   - `testGuard(e, goal, termLog?) -> 0|1`
   - `evidenceGuard(e) -> 0|0.5`
   - `driftScore(scores, weights, thresholds) -> {score, action}`

2. **建立 8 个最小单测**
   - 允许路径编辑 / 非允许路径编辑
   - modify 阶段使用非法 tool
   - 测试应跑未跑 / 已跑
   - 有/无 evidence
   - **plan 事件恒 action=ok（不计分）**
   - **Chat-only vs Diff 路线等价性**
   - 综合 case 触发 warn 与 rollback

3. **做一个"例外机制"**（把假阳性降下来）
   - UI/CLI：`ack --reason="需要临时改依赖以修 build"`
   - 例外写入 `events.jsonl` 的 `evidence.links/notes`，下一次守卫见到 有效例外 可降权

4. **工具链验证**
   - `tools/chat2events.py`：Chat-only 提取器（planned vs applied）
   - `tools/events2guards.py`：四守卫 + plan 忽略策略
   - `scripts/e2e_chat_only.py`：一键 Chat-only 流程

---

## 🔗 五、为何 Q1→Q2→Q3 是正确的依赖关系

- **Q1 输出 = Q2/Q3 的训练与检索数据**：没有 `events.jsonl` 的"事实"，模式卡只能凭空想象。
- **Q1 还能给 Q2 提供"anti_patterns/risks"**：哪些越界最常见？直接写进卡，下次先天规避。
- **Q3 的"难度估计/视图路由"需要 Q1 的统计**：历史首试成功率、偏航率、偏航恢复时间 → 画像与路由的依据。

---

## ✅ 下一步行动

如果你认可上面的规范，我可以把这些 TS 接口 + 守卫函数样例直接合入你仓库的 `types/` 与 `src/guards/`，并加上6 条单测；你就能马上跑 Phase 1 的端到端（不依赖外部模型）。

接着，我们用 3–5 次真实 run 抽出 第一批模式卡（Q2），最后再接上 视图路由（Q3）。
```

现在让我检查一下是否有任何语法错误：


这些都是 Markdown 格式的警告，主要是关于空行和标题格式的。由于这些是文档文件，这些格式问题不会影响功能，但我们可以快速修复一些关键问题。让我修复 plan (V3).md 的开头问题：


```markdown
# 💭 问题分析与执行策略

> **核心思考**：我觉得这个框架已经搭好了，但是我认为这三个问题和它们的解决我们还没有完全地做好。就是说我想先解决最简单的这个问题，就是最后这个偏移的问题，就是这个drift的问题。然后再解决第二个和第三个问题，你觉得这个方法是不是好？因为我最后是想从简单到难开始，从一个实践的顺序来说，我是想先解决一个简单的问题，然后再解决其他的复杂的问题。
>
> 我感觉第一个问题就是有一个数据之后，我们判断这个AI它是不是偏移了。这个数据是其他两个问题的先驱，因为如果没有这个数据的话，我们也没法match这个匹配度，对吧？我们也没有办法做这个复用的情况，learning from experience的情况。Q2和Q3其实取决于Q1，这是我的理解。所以我想先做Q1，再做Q2，再做Q3，不知道你同意这个方案吗？我觉得大体框架是有的，我们现在就要走一遍细节。
>
> **技术细节需要细化**：举个例子比如Q1的四个守卫+计算score的方式+数据input/output都可以继续细化（是否要定一个ts or数据库结构，枚举结构），Q2的pattern的定义（这些如何定义：经验无法沉淀与迁移，造成重复劳动，是否要定一个ts or数据库结构，枚举结构），Q3的"用户水平 × 任务难度" 这两个也可以定义，是否要定一个ts or数据库结构，枚举结构）
>
> 这是我的想法

## ✅ 执行策略确认

我完全同意你的执行顺序：先打穿 Q1（偏航检测）→ 再做 Q2（模式复用）→ 最后 Q3（动态抽象）。

理由很简单也很工程化：Q1 产出的"规范化事件 + 守卫分数"就是 Q2 抽卡与 Q3 路由的训练/检索数据。没有 Q1，就没有可复用的"事实语料库"。

下面我把三块一次性讲清楚：先给你实现顺序与验收标准，然后给精确的数据结构（TypeScript + 可选 SQLite DDL）与算法细节，最后给端到端示例（和你当前"翻译 README 却误改 requirements.txt"的例子完全对齐）。

---

## 📋 一、实施顺序（从简单到难）

### Phase 1（Q1：偏航检测，P0）

**目标**：对任意一次会话/提交，输出事件流与 drift 评分，并能告警/回滚。

**交付物**：
1. `events.jsonl`（来自 patch.diff/term.log 的规范化事件）
2. `guards.jsonl`（四守卫 + drift_score + action）
3. "最小 UI/CLI"：列出高分事件、显示原因、提供回滚命令

**验收**：
- ≥95% 的越界改动（不在 allowed_paths）被检出
- 假阳性 ≤10%（可通过例外机制逐步下降）

### Phase 2（Q2：模式复用，P1）

**目标**：把"做成的经历"沉淀成模式卡，能在新任务自动检索触发。

**交付物**：
1. `patterns/pc_*.json`（从多个 runs 抽取）
2. 检索与注入：给定 objective/issue_text → 返回命中的模式卡（含两档视图的文案骨架）

**验收**：
- 模式复用率↑、首试成功率↑、平均回合数↓（以小 A/B 验证）

### Phase 3（Q3：动态抽象，P1）

**目标**：同一卡两档视图，按"用户水平 × 任务难度"自动路由。

**交付物**：
1. `profiles/<user>.json`（画像）
2. 路由器：根据画像与任务难度，输出 terse | guided

**验收**：
- 新手在 guided 下成功率/稳定性更高；专家在 terse 下不中断

---

## 🔧 二、数据与接口规范（TS + JSONL + 可选 SQLite）

### 0) 共同枚举

```typescript
// phases/checkpoints
export type Phase = 'reproduce' | 'modify' | 'test' | 'regress';

// tools（新增 plan 类型）
export type Tool = 'edit' | 'shell' | 'browse' | 'plan';

// guard action
export type GuardAction = 'ok' | 'warn' | 'rollback';

// user level & task difficulty
export type UserLevel = 'novice' | 'intermediate' | 'expert';
export type TaskDifficulty = 'low' | 'medium' | 'high';

// confidence levels（Chat-only 用）
export type Confidence = 'low' | 'medium' | 'high';
```

---

### 1) Q1：输入/输出与算法

#### 1.1 目标定义（goal.json）

```typescript
export interface GoalConfig {
  run_id: string;
  objective: string;                         // e.g., "Translate README.md to Chinese"
  allowed_paths: string[];                   // allow-list (prefix match)
  forbidden_paths?: string[];                // optional block-list
  checkpoints: Phase[];                      // ["reproduce","modify","test","regress"]
  required_tests?: string[];                 // names/regex you expect to run/ pass
  allowed_tools_by_phase?: Partial<Record<Phase, Tool[]>>; // default 见下
  thresholds?: { warn: number; rollback: number };         // default 0.5/0.8
  meta?: Record<string, any>;                // 任意扩展
}
```

**默认策略**（若 allowed_tools_by_phase 未给出）：
- reproduce: ['shell','browse']
- modify:    ['edit','shell']
- test:      ['shell']
- regress:   ['shell']

**默认阈值**：warn=0.5，rollback=0.8

#### 1.2 事件（events.jsonl）

```typescript
export interface BaseEvent {
  id: string;                 // uuid
  run_id: string;
  step: number;               // 1,2,3...
  ts?: string;                // ISO time
  phase: Phase;
  tool: Tool;
  why?: string;               // rationale in short
  evidence?: {
    tests?: string[];         // tests names/assertions referenced
    logs?: string[];          // log lines digests or links
    links?: string[];         // issue/PR/docs links
  };
}

export interface EditEvent extends BaseEvent {
  tool: 'edit';
  where: { path: string; start?: number; end?: number };
  what: { diff?: string; ast_hint?: string };
}

export interface PlanEvent extends BaseEvent {
  tool: 'plan';
  where: { path: string; start?: number; end?: number };
  confidence?: Confidence;  // Chat-only 提取的置信度
}

export interface ShellEvent extends BaseEvent {
  tool: 'shell';
  cmd: string;
  exit_code?: number;
  stdout_digest?: string;     // hash/first-N lines
}

export type Event = EditEvent | PlanEvent | ShellEvent;
```

**JSONL 示例**（Diff 路线）：

```json
{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit","where":{"path":"README.md"},"what":{"diff":"(hunk)"},"why":"from patch.diff"}
{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit","where":{"path":"requirements.txt"},"what":{"diff":"(hunk)"}}
{"id":"e3","run_id":"r42","step":3,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
{"id":"e4","run_id":"r42","step":4,"phase":"test","tool":"shell","cmd":"pytest -k whitelist_diff_check"}
```

**Chat-only 示例**：

```json
{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan","where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}
{"id":"e2","run_id":"r60","step":2,"phase":"modify","tool":"edit","where":{"path":"README.md"},"why":"已将英文内容改为中文","confidence":"high"}
{"id":"t1001","run_id":"r60","step":1001,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
```

#### 1.3 守卫输出（guards.jsonl）

```typescript
export interface GuardScores {
  id: string;                 // match event id
  run_id: string;
  step: number;
  scope_guard: number;        // 0~1
  plan_guard: number;         // 0~1
  test_guard: number;         // 0~1
  evidence_guard: number;     // 0~1
  drift_score: number;        // weighted sum
  action: GuardAction;        // ok | warn | rollback
  file?: string;              // for edit events
  notes?: string;             // reason for flag
}
```

**打分算法**（可直接落地）：

```typescript
// 权重（可配置）
const W = { scope: 0.4, plan: 0.3, test: 0.2, evidence: 0.1 };

// 重要：仅对 tool=edit 计分，tool=plan 恒 action=ok
if (event.tool === 'plan') {
  return { scope_guard: 0, plan_guard: 0, test_guard: 0, evidence_guard: 0, 
           drift_score: 0, action: 'ok' };
}

// ScopeGuard：编辑是否越界（prefix allow-list）
scope_guard = (event.tool==='edit')
  ? (inAllowed(event.where.path, goal.allowed_paths) ? 0 : 1)
  : 0;

// PlanGuard：此 phase 是否允许此 tool/此路径类别
plan_guard = (() => {
  const allowTools = goal.allowed_tools_by_phase?.[event.phase] || defaultTools[event.phase];
  if (!allowTools.includes(event.tool)) return 1;
  if (event.tool==='edit' && !inAllowed(event.where.path, goal.allowed_paths)) return 1;
  return 0;
})();

// TestGuard：若 phase 是 test/regress，是否跑了/通过了 required_tests
// MVP：看到相应 pytest 命令则 0，否则 1（或结合 term.log 解析通过率）
test_guard = ((event.phase==='test' || event.phase==='regress') && event.tool==='shell')
  ? (coversRequired(event.cmd, goal.required_tests) ? 0 : 1)
  : 0;

// EvidenceGuard：modify 阶段的 edit 事件，是否带有 tests/logs/links 作为证据
evidence_guard = (event.phase==='modify' && event.tool==='edit')
  ? (event.evidence && (event.evidence.tests?.length || event.evidence.logs?.length || event.evidence.links?.length) ? 0 : 0.5)
  : 0;

// 综合：
drift_score = W.scope*scope_guard + W.plan*plan_guard + W.test*test_guard + W.evidence*evidence_guard;

// 动作：
action = (drift_score >= (goal.thresholds?.rollback ?? 0.8)) ? 'rollback'
       : (drift_score >= (goal.thresholds?.warn ?? 0.5))     ? 'warn'
       : 'ok';
```

**JSONL 示例**：

```json
{"id":"e1","run_id":"r42","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md"}
{"id":"e2","run_id":"r42","step":2,"scope_guard":1,"plan_guard":1,"test_guard":0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt","notes":"not in allowed_paths"}
{"id":"p1","run_id":"r60","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md","notes":"plan event, not scored"}
```

**Q1 的评测**：
- 检出率（真正例 / 全部偏航）
- 误报率（假正例 / 全部告警）
- 偏航恢复时间（首次 warn → 回到正确 checkpoint 的步数/秒）
- 覆盖面（被守卫覆盖的偏航类型占比：路径越界/错误 phase/未跑测试/无证据）

---

### 2) Q2：模式卡定义与检索（在 Q1 打好后做）

#### 2.1 模式卡（patterns/pc_*.json）

```typescript
export interface PatternCard {
  version: string;                     // e.g., "1.0"
  pattern_id: string;                  // "pc_doc_only_change"
  title: string;                       // 人类可读标题
  triggers: string[];                  // 检索关键词/正则
  steps: string[];                     // 关键步骤（可用于计划/提示）
  invariants: string[];                // 不变量（必须成立的约束）
  anti_patterns?: string[];            // 禁止或常见误用
  eval_examples?: string[];            // 相关测试/验证名
  risks?: string[];                    // 风险提示（何时需要升级审核/例外）
  views: {                             // Q3 用
    terse: string;                     // 专家版
    guided: string;                    // 新手版
  };
  provenance: {                        // 溯源
    source_runs: string[];             // ["r42","r51"...]
    created_by: string;                // user id
    created_at: string;
  };
  metrics?: {                          // 可选：这张卡带来的 uplift 记录
    reuse_count: number;
    first_try_uplift?: number;
  };
}
```

**最小检索打分**（先规则 + 关键词覆盖；后续可接向量）：

```typescript
score = hits(triggers, goal.objective + issue_text) / triggers.length
// 冲突降权：若卡的 invariants 与 goal.allowed_paths/forbidden_paths 冲突，score -= 0.3
// 阶段性加权：若 Q1 的守卫告警类型与卡的 anti_patterns 相符，优先级↑
```

**沉淀策略**：
- 触发条件：本次 run 通过验证（或人工确认"做对了"）
- 合并：多 run 同类卡可合并（并保留 source_runs 列表）
- 进入库标准：能带来明显 uplift（首试成功率/回合数/时间）才纳入团队库

---

### 3) Q3：画像与路由

#### 3.1 用户画像（profiles/*.json）

```typescript
export interface UserProfile {
  user_id: string;
  self_report: UserLevel;                // 自报水平
  hist_first_try_success: number;        // 0~1
  pref?: 'guided' | 'terse';             // 明示偏好（可覆盖自动路由）
  notes?: string;
}
```

#### 3.2 任务难度估计（无需完美，先启发式）

```typescript
export interface TaskDescriptor {
  files_touched_est?: number;    // 预估修改文件数
  loc_delta_est?: number;        // 预估变更行数
  repo_familiarity?: number;     // 0~1（按贡献/最近互动/文件相似度）
  risk_flags?: string[];         // e.g., ["dependency","security","db-migration"]
}

function estimateDifficulty(d: TaskDescriptor): TaskDifficulty {
  const score = (d.files_touched_est||0)/5 + (d.loc_delta_est||0)/200 + (1-(d.repo_familiarity||0));
  if (score < 0.8) return 'low';
  if (score < 1.6) return 'medium';
  return 'high';
}
```

#### 3.3 视图路由（MVP）

```typescript
function chooseView(profile: UserProfile, task: TaskDescriptor): 'guided'|'terse' {
  const diff = estimateDifficulty(task);
  if (profile.pref) return profile.pref;
  if (profile.self_report === 'novice') return 'guided';
  if (diff === 'high') return 'guided';
  if (profile.hist_first_try_success < 0.5) return 'guided';
  return 'terse';
}
```


---

### 4) 可选数据库（SQLite DDL，占位可后置）

JSONL 先跑通，SQLite 便于做统计/报表/多用户协作。

```sql
-- runs
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY,
  created_at TEXT,
  objective TEXT
);

-- goals
CREATE TABLE goals (
  run_id TEXT,
  content JSON,
  PRIMARY KEY(run_id)
);

-- events
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  ts TEXT,
  phase TEXT,
  tool TEXT,
  path TEXT,
  cmd TEXT,
  payload JSON
);

-- guards
CREATE TABLE guard_scores (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  scope REAL, plan REAL, test REAL, evidence REAL,
  drift REAL, action TEXT, file TEXT, notes TEXT
);

-- patterns
CREATE TABLE patterns (
  pattern_id TEXT PRIMARY KEY,
  version TEXT,
  title TEXT,
  content JSON,
  reuse_count INTEGER DEFAULT 0
);

-- profiles
CREATE TABLE profiles (
  user_id TEXT PRIMARY KEY,
  content JSON
);
```

---

## 🚀 三、端到端（以你的"文档任务跑题"为例）

**输入**：
- `goal.json`：只允许 README.md / docs/**
- `patch.diff`：改了 README.md 并误改 requirements.txt
- （可选）`term.log`：包含 pytest -k doc_lang_check 与 pytest -k whitelist_diff_check

**步骤**：
1. `patch2events` → 生成两条 edit 事件（README.md / requirements.txt）
2. `term2events` → 生成两条 shell 事件（测试）
3. `events2guards` → 对 requirements.txt 给出 Scope=1.0，Plan=1.0，Evidence=0.5 → drift=0.85 → action=warn
4. （通过/确认后）抽卡 → `pc_doc_only_change` 入库
5. 新任务"翻译文档"启动时，检索命中该卡：
   - terse 给专家：白名单 + 禁改依赖 + 两个检查
   - guided 给新手：逐步配置白名单/语言检测/例外流程/坑点
6. 度量：相似任务在有卡 vs 无卡下，比较首试成功率/回合数/用时，出 ablation 图。

---

## 🛠️ 四、你今天就能推进的细节（Q1 打穿）

1. **把四个守卫写成纯函数**（方便单元测试）
   - `scopeGuard(e, goal) -> 0|1`
   - `planGuard(e, goal) -> 0|1`
   - `testGuard(e, goal, termLog?) -> 0|1`
   - `evidenceGuard(e) -> 0|0.5`
   - `driftScore(scores, weights, thresholds) -> {score, action}`

2. **建立 8 个最小单测**
   - 允许路径编辑 / 非允许路径编辑
   - modify 阶段使用非法 tool
   - 测试应跑未跑 / 已跑
   - 有/无 evidence
   - **plan 事件恒 action=ok（不计分）**
   - **Chat-only vs Diff 路线等价性**
   - 综合 case 触发 warn 与 rollback

3. **做一个"例外机制"**（把假阳性降下来）
   - UI/CLI：`ack --reason="需要临时改依赖以修 build"`
   - 例外写入 `events.jsonl` 的 `evidence.links/notes`，下一次守卫见到 有效例外 可降权

4. **工具链验证**
   - `tools/chat2events.py`：Chat-only 提取器（planned vs applied）
   - `tools/events2guards.py`：四守卫 + plan 忽略策略
   - `scripts/e2e_chat_only.py`：一键 Chat-only 流程

---

## 🔗 五、为何 Q1→Q2→Q3 是正确的依赖关系

- **Q1 输出 = Q2/Q3 的训练与检索数据**：没有 `events.jsonl` 的"事实"，模式卡只能凭空想象。
- **Q1 还能给 Q2 提供"anti_patterns/risks"**：哪些越界最常见？直接写进卡，下次先天规避。
- **Q3 的"难度估计/视图路由"需要 Q1 的统计**：历史首试成功率、偏航率、偏航恢复时间 → 画像与路由的依据。

---

## ✅ 下一步行动

如果你认可上面的规范，我可以把这些 TS 接口 + 守卫函数样例直接合入你仓库的 `types/` 与 `src/guards/`，并加上6 条单测；你就能马上跑 Phase 1 的端到端（不依赖外部模型）。

接着，我们用 3–5 次真实 run 抽出 第一批模式卡（Q2），最后再接上 视图路由（Q3）。
```

现在让我添加一个结尾换行符：


```markdown
# 💭 问题分析与执行策略

> **核心思考**：我觉得这个框架已经搭好了，但是我认为这三个问题和它们的解决我们还没有完全地做好。就是说我想先解决最简单的这个问题，就是最后这个偏移的问题，就是这个drift的问题。然后再解决第二个和第三个问题，你觉得这个方法是不是好？因为我最后是想从简单到难开始，从一个实践的顺序来说，我是想先解决一个简单的问题，然后再解决其他的复杂的问题。
>
> 我感觉第一个问题就是有一个数据之后，我们判断这个AI它是不是偏移了。这个数据是其他两个问题的先驱，因为如果没有这个数据的话，我们也没法match这个匹配度，对吧？我们也没有办法做这个复用的情况，learning from experience的情况。Q2和Q3其实取决于Q1，这是我的理解。所以我想先做Q1，再做Q2，再做Q3，不知道你同意这个方案吗？我觉得大体框架是有的，我们现在就要走一遍细节。
>
> **技术细节需要细化**：举个例子比如Q1的四个守卫+计算score的方式+数据input/output都可以继续细化（是否要定一个ts or数据库结构，枚举结构），Q2的pattern的定义（这些如何定义：经验无法沉淀与迁移，造成重复劳动，是否要定一个ts or数据库结构，枚举结构），Q3的"用户水平 × 任务难度" 这两个也可以定义，是否要定一个ts or数据库结构，枚举结构）
>
> 这是我的想法

## ✅ 执行策略确认

我完全同意你的执行顺序：先打穿 Q1（偏航检测）→ 再做 Q2（模式复用）→ 最后 Q3（动态抽象）。

理由很简单也很工程化：Q1 产出的"规范化事件 + 守卫分数"就是 Q2 抽卡与 Q3 路由的训练/检索数据。没有 Q1，就没有可复用的"事实语料库"。

下面我把三块一次性讲清楚：先给你实现顺序与验收标准，然后给精确的数据结构（TypeScript + 可选 SQLite DDL）与算法细节，最后给端到端示例（和你当前"翻译 README 却误改 requirements.txt"的例子完全对齐）。

---

## 📋 一、实施顺序（从简单到难）

### Phase 1（Q1：偏航检测，P0）

**目标**：对任意一次会话/提交，输出事件流与 drift 评分，并能告警/回滚。

**交付物**：
1. `events.jsonl`（来自 patch.diff/term.log 的规范化事件）
2. `guards.jsonl`（四守卫 + drift_score + action）
3. "最小 UI/CLI"：列出高分事件、显示原因、提供回滚命令

**验收**：
- ≥95% 的越界改动（不在 allowed_paths）被检出
- 假阳性 ≤10%（可通过例外机制逐步下降）

### Phase 2（Q2：模式复用，P1）

**目标**：把"做成的经历"沉淀成模式卡，能在新任务自动检索触发。

**交付物**：
1. `patterns/pc_*.json`（从多个 runs 抽取）
2. 检索与注入：给定 objective/issue_text → 返回命中的模式卡（含两档视图的文案骨架）

**验收**：
- 模式复用率↑、首试成功率↑、平均回合数↓（以小 A/B 验证）

### Phase 3（Q3：动态抽象，P1）

**目标**：同一卡两档视图，按"用户水平 × 任务难度"自动路由。

**交付物**：
1. `profiles/<user>.json`（画像）
2. 路由器：根据画像与任务难度，输出 terse | guided

**验收**：
- 新手在 guided 下成功率/稳定性更高；专家在 terse 下不中断

---

## 🔧 二、数据与接口规范（TS + JSONL + 可选 SQLite）

### 0) 共同枚举

```typescript
// phases/checkpoints
export type Phase = 'reproduce' | 'modify' | 'test' | 'regress';

// tools（新增 plan 类型）
export type Tool = 'edit' | 'shell' | 'browse' | 'plan';

// guard action
export type GuardAction = 'ok' | 'warn' | 'rollback';

// user level & task difficulty
export type UserLevel = 'novice' | 'intermediate' | 'expert';
export type TaskDifficulty = 'low' | 'medium' | 'high';

// confidence levels（Chat-only 用）
export type Confidence = 'low' | 'medium' | 'high';
```

---

### 1) Q1：输入/输出与算法

#### 1.1 目标定义（goal.json）

```typescript
export interface GoalConfig {
  run_id: string;
  objective: string;                         // e.g., "Translate README.md to Chinese"
  allowed_paths: string[];                   // allow-list (prefix match)
  forbidden_paths?: string[];                // optional block-list
  checkpoints: Phase[];                      // ["reproduce","modify","test","regress"]
  required_tests?: string[];                 // names/regex you expect to run/ pass
  allowed_tools_by_phase?: Partial<Record<Phase, Tool[]>>; // default 见下
  thresholds?: { warn: number; rollback: number };         // default 0.5/0.8
  meta?: Record<string, any>;                // 任意扩展
}
```

**默认策略**（若 allowed_tools_by_phase 未给出）：
- reproduce: ['shell','browse']
- modify:    ['edit','shell']
- test:      ['shell']
- regress:   ['shell']

**默认阈值**：warn=0.5，rollback=0.8

#### 1.2 事件（events.jsonl）

```typescript
export interface BaseEvent {
  id: string;                 // uuid
  run_id: string;
  step: number;               // 1,2,3...
  ts?: string;                // ISO time
  phase: Phase;
  tool: Tool;
  why?: string;               // rationale in short
  evidence?: {
    tests?: string[];         // tests names/assertions referenced
    logs?: string[];          // log lines digests or links
    links?: string[];         // issue/PR/docs links
  };
}

export interface EditEvent extends BaseEvent {
  tool: 'edit';
  where: { path: string; start?: number; end?: number };
  what: { diff?: string; ast_hint?: string };
}

export interface PlanEvent extends BaseEvent {
  tool: 'plan';
  where: { path: string; start?: number; end?: number };
  confidence?: Confidence;  // Chat-only 提取的置信度
}

export interface ShellEvent extends BaseEvent {
  tool: 'shell';
  cmd: string;
  exit_code?: number;
  stdout_digest?: string;     // hash/first-N lines
}

export type Event = EditEvent | PlanEvent | ShellEvent;
```

**JSONL 示例**（Diff 路线）：

```json
{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit","where":{"path":"README.md"},"what":{"diff":"(hunk)"},"why":"from patch.diff"}
{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit","where":{"path":"requirements.txt"},"what":{"diff":"(hunk)"}}
{"id":"e3","run_id":"r42","step":3,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
{"id":"e4","run_id":"r42","step":4,"phase":"test","tool":"shell","cmd":"pytest -k whitelist_diff_check"}
```

**Chat-only 示例**：

```json
{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan","where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}
{"id":"e2","run_id":"r60","step":2,"phase":"modify","tool":"edit","where":{"path":"README.md"},"why":"已将英文内容改为中文","confidence":"high"}
{"id":"t1001","run_id":"r60","step":1001,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
```

#### 1.3 守卫输出（guards.jsonl）

```typescript
export interface GuardScores {
  id: string;                 // match event id
  run_id: string;
  step: number;
  scope_guard: number;        // 0~1
  plan_guard: number;         // 0~1
  test_guard: number;         // 0~1
  evidence_guard: number;     // 0~1
  drift_score: number;        // weighted sum
  action: GuardAction;        // ok | warn | rollback
  file?: string;              // for edit events
  notes?: string;             // reason for flag
}
```

**打分算法**（可直接落地）：

```typescript
// 权重（可配置）
const W = { scope: 0.4, plan: 0.3, test: 0.2, evidence: 0.1 };

// 重要：仅对 tool=edit 计分，tool=plan 恒 action=ok
if (event.tool === 'plan') {
  return { scope_guard: 0, plan_guard: 0, test_guard: 0, evidence_guard: 0, 
           drift_score: 0, action: 'ok' };
}

// ScopeGuard：编辑是否越界（prefix allow-list）
scope_guard = (event.tool==='edit')
  ? (inAllowed(event.where.path, goal.allowed_paths) ? 0 : 1)
  : 0;

// PlanGuard：此 phase 是否允许此 tool/此路径类别
plan_guard = (() => {
  const allowTools = goal.allowed_tools_by_phase?.[event.phase] || defaultTools[event.phase];
  if (!allowTools.includes(event.tool)) return 1;
  if (event.tool==='edit' && !inAllowed(event.where.path, goal.allowed_paths)) return 1;
  return 0;
})();

// TestGuard：若 phase 是 test/regress，是否跑了/通过了 required_tests
// MVP：看到相应 pytest 命令则 0，否则 1（或结合 term.log 解析通过率）
test_guard = ((event.phase==='test' || event.phase==='regress') && event.tool==='shell')
  ? (coversRequired(event.cmd, goal.required_tests) ? 0 : 1)
  : 0;

// EvidenceGuard：modify 阶段的 edit 事件，是否带有 tests/logs/links 作为证据
evidence_guard = (event.phase==='modify' && event.tool==='edit')
  ? (event.evidence && (event.evidence.tests?.length || event.evidence.logs?.length || event.evidence.links?.length) ? 0 : 0.5)
  : 0;

// 综合：
drift_score = W.scope*scope_guard + W.plan*plan_guard + W.test*test_guard + W.evidence*evidence_guard;

// 动作：
action = (drift_score >= (goal.thresholds?.rollback ?? 0.8)) ? 'rollback'
       : (drift_score >= (goal.thresholds?.warn ?? 0.5))     ? 'warn'
       : 'ok';
```

**JSONL 示例**：

```json
{"id":"e1","run_id":"r42","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md"}
{"id":"e2","run_id":"r42","step":2,"scope_guard":1,"plan_guard":1,"test_guard":0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt","notes":"not in allowed_paths"}
{"id":"p1","run_id":"r60","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md","notes":"plan event, not scored"}
```

**Q1 的评测**：
- 检出率（真正例 / 全部偏航）
- 误报率（假正例 / 全部告警）
- 偏航恢复时间（首次 warn → 回到正确 checkpoint 的步数/秒）
- 覆盖面（被守卫覆盖的偏航类型占比：路径越界/错误 phase/未跑测试/无证据）

---

### 2) Q2：模式卡定义与检索（在 Q1 打好后做）

#### 2.1 模式卡（patterns/pc_*.json）

```typescript
export interface PatternCard {
  version: string;                     // e.g., "1.0"
  pattern_id: string;                  // "pc_doc_only_change"
  title: string;                       // 人类可读标题
  triggers: string[];                  // 检索关键词/正则
  steps: string[];                     // 关键步骤（可用于计划/提示）
  invariants: string[];                // 不变量（必须成立的约束）
  anti_patterns?: string[];            // 禁止或常见误用
  eval_examples?: string[];            // 相关测试/验证名
  risks?: string[];                    // 风险提示（何时需要升级审核/例外）
  views: {                             // Q3 用
    terse: string;                     // 专家版
    guided: string;                    // 新手版
  };
  provenance: {                        // 溯源
    source_runs: string[];             // ["r42","r51"...]
    created_by: string;                // user id
    created_at: string;
  };
  metrics?: {                          // 可选：这张卡带来的 uplift 记录
    reuse_count: number;
    first_try_uplift?: number;
  };
}
```

**最小检索打分**（先规则 + 关键词覆盖；后续可接向量）：

```typescript
score = hits(triggers, goal.objective + issue_text) / triggers.length
// 冲突降权：若卡的 invariants 与 goal.allowed_paths/forbidden_paths 冲突，score -= 0.3
// 阶段性加权：若 Q1 的守卫告警类型与卡的 anti_patterns 相符，优先级↑
```

**沉淀策略**：
- 触发条件：本次 run 通过验证（或人工确认"做对了"）
- 合并：多 run 同类卡可合并（并保留 source_runs 列表）
- 进入库标准：能带来明显 uplift（首试成功率/回合数/时间）才纳入团队库

---

### 3) Q3：画像与路由

#### 3.1 用户画像（profiles/*.json）

```typescript
export interface UserProfile {
  user_id: string;
  self_report: UserLevel;                // 自报水平
  hist_first_try_success: number;        // 0~1
  pref?: 'guided' | 'terse';             // 明示偏好（可覆盖自动路由）
  notes?: string;
}
```

#### 3.2 任务难度估计（无需完美，先启发式）

```typescript
export interface TaskDescriptor {
  files_touched_est?: number;    // 预估修改文件数
  loc_delta_est?: number;        // 预估变更行数
  repo_familiarity?: number;     // 0~1（按贡献/最近互动/文件相似度）
  risk_flags?: string[];         // e.g., ["dependency","security","db-migration"]
}

function estimateDifficulty(d: TaskDescriptor): TaskDifficulty {
  const score = (d.files_touched_est||0)/5 + (d.loc_delta_est||0)/200 + (1-(d.repo_familiarity||0));
  if (score < 0.8) return 'low';
  if (score < 1.6) return 'medium';
  return 'high';
}
```

#### 3.3 视图路由（MVP）

```typescript
function chooseView(profile: UserProfile, task: TaskDescriptor): 'guided'|'terse' {
  const diff = estimateDifficulty(task);
  if (profile.pref) return profile.pref;
  if (profile.self_report === 'novice') return 'guided';
  if (diff === 'high') return 'guided';
  if (profile.hist_first_try_success < 0.5) return 'guided';
  return 'terse';
}
```


---

### 4) 可选数据库（SQLite DDL，占位可后置）

JSONL 先跑通，SQLite 便于做统计/报表/多用户协作。

```sql
-- runs
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY,
  created_at TEXT,
  objective TEXT
);

-- goals
CREATE TABLE goals (
  run_id TEXT,
  content JSON,
  PRIMARY KEY(run_id)
);

-- events
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  ts TEXT,
  phase TEXT,
  tool TEXT,
  path TEXT,
  cmd TEXT,
  payload JSON
);

-- guards
CREATE TABLE guard_scores (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  scope REAL, plan REAL, test REAL, evidence REAL,
  drift REAL, action TEXT, file TEXT, notes TEXT
);

-- patterns
CREATE TABLE patterns (
  pattern_id TEXT PRIMARY KEY,
  version TEXT,
  title TEXT,
  content JSON,
  reuse_count INTEGER DEFAULT 0
);

-- profiles
CREATE TABLE profiles (
  user_id TEXT PRIMARY KEY,
  content JSON
);
```

---

## 🚀 三、端到端（以你的"文档任务跑题"为例）

**输入**：
- `goal.json`：只允许 README.md / docs/**
- `patch.diff`：改了 README.md 并误改 requirements.txt
- （可选）`term.log`：包含 pytest -k doc_lang_check 与 pytest -k whitelist_diff_check

**步骤**：
1. `patch2events` → 生成两条 edit 事件（README.md / requirements.txt）
2. `term2events` → 生成两条 shell 事件（测试）
3. `events2guards` → 对 requirements.txt 给出 Scope=1.0，Plan=1.0，Evidence=0.5 → drift=0.85 → action=warn
4. （通过/确认后）抽卡 → `pc_doc_only_change` 入库
5. 新任务"翻译文档"启动时，检索命中该卡：
   - terse 给专家：白名单 + 禁改依赖 + 两个检查
   - guided 给新手：逐步配置白名单/语言检测/例外流程/坑点
6. 度量：相似任务在有卡 vs 无卡下，比较首试成功率/回合数/用时，出 ablation 图。

---

## 🛠️ 四、你今天就能推进的细节（Q1 打穿）

1. **把四个守卫写成纯函数**（方便单元测试）
   - `scopeGuard(e, goal) -> 0|1`
   - `planGuard(e, goal) -> 0|1`
   - `testGuard(e, goal, termLog?) -> 0|1`
   - `evidenceGuard(e) -> 0|0.5`
   - `driftScore(scores, weights, thresholds) -> {score, action}`

2. **建立 8 个最小单测**
   - 允许路径编辑 / 非允许路径编辑
   - modify 阶段使用非法 tool
   - 测试应跑未跑 / 已跑
   - 有/无 evidence
   - **plan 事件恒 action=ok（不计分）**
   - **Chat-only vs Diff 路线等价性**
   - 综合 case 触发 warn 与 rollback

3. **做一个"例外机制"**（把假阳性降下来）
   - UI/CLI：`ack --reason="需要临时改依赖以修 build"`
   - 例外写入 `events.jsonl` 的 `evidence.links/notes`，下一次守卫见到 有效例外 可降权

4. **工具链验证**
   - `tools/chat2events.py`：Chat-only 提取器（planned vs applied）
   - `tools/events2guards.py`：四守卫 + plan 忽略策略
   - `scripts/e2e_chat_only.py`：一键 Chat-only 流程

---

## 🔗 五、为何 Q1→Q2→Q3 是正确的依赖关系

- **Q1 输出 = Q2/Q3 的训练与检索数据**：没有 `events.jsonl` 的"事实"，模式卡只能凭空想象。
- **Q1 还能给 Q2 提供"anti_patterns/risks"**：哪些越界最常见？直接写进卡，下次先天规避。
- **Q3 的"难度估计/视图路由"需要 Q1 的统计**：历史首试成功率、偏航率、偏航恢复时间 → 画像与路由的依据。

---

## ✅ 下一步行动

如果你认可上面的规范，我可以把这些 TS 接口 + 守卫函数样例直接合入你仓库的 `types/` 与 `src/guards/`，并加上8 条单测；你就能马上跑 Phase 1 的端到端（不依赖外部模型）。

接着，我们用 3–5 次真实 run 抽出 第一批模式卡（Q2），最后再接上 视图路由（Q3）。
```

完美！我已经按照你的建议完成了两个文档的更新。让我总结一下主要的修改：

## ✅ 已完成的更新

### README (v3).md 的主要更新：

1. **添加了"采集与规范化：两条等价路径"**章节，明确区分：
   - **Chat‑only 路线**（推荐）：使用 `raw/cursor.md` + `tools/chat2events.py`
   - **Diff 路线**：使用 `raw/patch.diff` + `tools/patch2events.py`

2. **修正了事件 schema 示例**：
   - 将 `"where":"README.md:?"` 改为 `"where":{"path":"README.md"}`
   - 添加了 `tool=plan` 的示例和说明

3. **更新了工具/脚本命名**：
   - `tools/chat2events.py`（Chat-only 提取器）
   - `scripts/e2e_chat_only.py`（一键 Chat-only）
   - 保留了 Diff 路线的工具

4. **调整了事实来源表述**：
   - Chat‑only 模式下，明确表述"已修改"、展示代码片段、通过测试命令等可作为事实来源
   - 仅"计划修改"标记为 `tool=plan`（不计分）

5. **添加了 Chat-only 端到端示例**：
   - 展示了完整的 Chat-only 流程
   - 说明了如何区分"计划"vs"已实施"

6. **更新了最小可用脚本**：
   - 提供了 Chat-only 和 Diff 两套命令
   - 将未实现的工具移到"后续工作（占位）"

### plan (V3).md 的主要更新：

1. **添加了 `PlanEvent` 类型**和 `Confidence` 枚举
2. **更新了打分算法**，明确 `tool=plan` 恒 `action=ok`（不计分）
3. **添加了 Chat-only 示例**到 JSONL 示例中
4. **更新了单测要求**，从6个增加到8个，包含 plan 事件和 Chat-only 等价性测试
5. **添加了工具链验证**部分

## 🎯 关键改进点

- **两条路径等价**：Chat-only 和 Diff 都能产生相同的 `events.jsonl`，后续处理完全一致
- **plan vs edit 区分**：明确只有 `tool=edit` 进入守卫计分，`tool=plan` 仅留痕
- **置信度机制**：Chat-only 提取时提供置信度，低置信度时可启用 git 兜底
- **实现对齐**：所有工具命名、数据结构都与当前 v3 实现保持一致

这些更新让文档与你的实际实现完全对齐，同时保持了原有的清晰逻辑和完整的技术规范。现在读者可以清楚地理解如何同时使用 Chat-only 和 Diff 两条路径，以及为什么 `tool=plan` 不计分的设计是合理的。

---
