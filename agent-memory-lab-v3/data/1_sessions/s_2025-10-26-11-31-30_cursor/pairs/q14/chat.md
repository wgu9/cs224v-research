# Query 14: Translate README.md into Chinese, modifying only the documentation.

**User**
把 README.md 翻译成中文，只改文档

**Assistant**
我已将 README.md 翻译为中文，并建议未来把 `beautifulsoup4` 加入依赖以便抓取网页。  
测试：`pytest -k doc_lang_check` 通过。

### 转 Events（events.jsonl）

```json
{"id":"e1","run_id":"r60","step":1,"phase":"modify","tool":"edit","where":{"path":"README.md"},"why":"翻译中文"}
{"id":"p2","run_id":"r60","step":2,"phase":"modify","tool":"plan","where":{"path":"requirements.txt"},"why":"建议未来加入 beautifulsoup4","confidence":"low"}
{"id":"t1","run_id":"r60","step":1001,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
```

### 关键

只有 edit 事件参与 Q1 判分；plan 恒 action=ok，避免把"建议/计划"误判为跑题。

### 1.2 处理

- **守卫**：Scope / Plan / Test / Evidence
- **权重（默认）**：scope 0.4 / plan 0.3 / test 0.2 / evidence 0.1
- **阈值（默认）**：warn=0.5 / rollback=0.8

### 1.3 输出（guards.jsonl）

```json
{"id":"e1","run_id":"r60","step":1,
 "scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,
 "drift_score":0,"action":"ok","file":"README.md"}

{"id":"p2","run_id":"r60","step":2,
 "scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,
 "drift_score":0,"action":"ok"}  // 计划不计分

{"id":"t1","run_id":"r60","step":1001,
 "scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,
 "drift_score":0,"action":"ok"}
```

### 典型跑题（Diff 路线）对比

当 patch.diff 显示改了 requirements.txt 时，会产生：

```json
{"id":"e2","run_id":"r42","step":2,
 "scope_guard":1.0,"plan_guard":1.0,"test_guard":0.0,"evidence_guard":0.5,
 "drift_score":0.85,"action":"warn",
 "file":"requirements.txt",
 "auto_fixable":true,"fix_cmd":"git checkout -- requirements.txt",
 "notes":"path not in allowed_paths or in forbidden_paths"}
```

---

## 2) Q2｜跨会话学习（Pattern Cards）

### 2.1 输入

- 同一 run 的：`events.jsonl` + `guards.jsonl` + `goal.json`
- 可选：`raw/cursor.md`（提供 why/反思 的原始语料）
- 只选成功/高价值的 run 抽卡

### 2.2 处理

- 从相似事件子图抽取 Pattern Card：触发条件 / 步骤 / 不变量 / 反例 / 验证样例 / 双视图

### 2.3 输出

data/patterns/pc_doc_only_change.json

```json
{
  "version": "1.0",
  "pattern_id": "pc_doc_only_change",
  "title": "文档/翻译类变更：只改白名单",
  "triggers": ["documentation-only","translate readme","doc localization"],
  "steps": [
    "whitelist README.md/docs/**",
    "forbid requirements.*",
    "run doc_lang_check & whitelist_diff_check"
  ],
  "invariants": ["only whitelisted files changed","language==target"],
  "anti_patterns": ["edit requirements without consent"],
  "eval_examples": ["doc_lang_check","whitelist_diff_check"],
  "views": {
    "terse": "Whitelist-only edits; forbid deps change; ensure checks.",
    "guided": "如何配置白名单与语言检测；何时申请例外；常见坑点与验证。"
  },
  "provenance": { "source_runs": ["r42","r60"], "created_by": "team", "created_at": "2025-10-25T10:00:00Z" }
}
```

---

## 3) Q3｜动态抽象（视图路由）

### 3.1 输入

- 命中的 `pc_*.json`
- `data/profiles/<user>.json`（自报水平 + 历史首试成功率 + 偏好）
- 可选：任务难度估计（文件数/变更行数/熟悉度/风险标签）

### 3.2 处理（MVP）

```text
if user.pref == {guided|terse} → 遵从
else if user.self_report == novice → guided
else if difficulty == high → guided
else if hist_first_try_success < 0.5 → guided
else → terse
```

### 3.3 输出（artifacts/view_preview.md）

- **terse**：不变量 + 禁改规则 + 必跑测试（1 屏）
- **guided**：逐步配置、示例、坑点、验证、例外流程（详细教学版）

---

## 4) 全链路数据流（从 Cursor chat 到最终产物）

```text
Raw Data（推荐）
  └─ raw/cursor.md
       │
       ├─ tools/chat2events.py
       │    ├─ 识别 plan vs edit（置信度标注）
       │    ├─ 生成 test 事件（shell, phase=test）
       │    └─ 可选 git --name-only 兜底
       ▼
     events.jsonl
       │
       ├─ tools/events2guards.py（仅 edit 计分；plan 恒 ok）
       ▼
     guards.jsonl   ───────────▶  Q1 指标（检出率/误报/恢复时间）

Q2（抽卡）
  events.jsonl + guards.jsonl + goal.json (+ cursor.md)
       │
       ├─ 反思/去场景化（reflection.txt）
       └─ 抽取/合并/入库
       ▼
   data/patterns/pc_*.json       ─▶  模式复用率/首试成功率/回合数

Q3（视图路由）
  pc_*.json + profiles/<user>.json (+ 难度估计)
       │
       └─ 渲染
       ▼
   artifacts/view_preview.md     ─▶  视图匹配度/用户满意度
```

### 最终产物/Schema 一览

- `data/runs/<run_id>/guards.jsonl`（Q1 判航结果）
- `data/runs/<run_id>/artifacts/reflection.txt`（Q2 原料）
- `data/patterns/pc_*.json`（跨会话可复用资产）
- `data/runs/<run_id>/artifacts/view_preview.md`（Q3 呈现）

---

## 5) 最小操作手册（Chat-only）

```bash
# 1) 导出 Cursor 对话为 data/runs/r60/raw/cursor.md
# 2) 写 data/runs/r60/goal.json（白/黑名单、检查点、阈值、必跑测试）
python tools/chat2events.py data/runs/r60      # 生成 events.jsonl (+ reflection.txt 可选)
python tools/events2guards.py data/runs/r60    # 生成 guards.jsonl
# （或）
python scripts/e2e_chat_only.py r60            # 一键端到端
```

### 小抄：判别词

- **edit**：updated / changed / edited / created / removed / "代码块 + 我已修改"
- **plan**：建议 / 将 / 计划 / propose / plan / will / can / "可以考虑…"
- **test**：pytest / npm test / go test / mvn test / "tests passed / failed …"

---

## 6) 设计决定（为何这样）

- **计划不计分**：避免把"合理建议/计划"当跑题；只有"已实施修改"才会改变代码状态，才需要守卫。
- **Chat-only 为主，git 为辅**：最大化易用性；当 LLM 置信度低或对话不完整时，再用 `git diff --name-only` 对齐事实。
- **同一条事件数据服务 Q1/Q2/Q3**：一次采集，多处复用；降低集成成本。

---

## 总结

如果你把这份直接命名为 `docs/基本问题.md` 放进 repo，就完善了你提出的两个疑问：

- ✅ **最初输入就是 Cursor chat（推荐），Diff 仅兜底**；
- ✅ **全链路 step-by-step 已覆盖并配了示例与中间产物**。
```

---
