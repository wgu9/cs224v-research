# Query 16: Translate the entire @addfiles.md document into Chinese, keeping important terms, functions, and variables in English.

**User**
@addfiles.md 中文全文翻译 重要名词，function和变量等保留英文

---

**Assistant**
```markdown
# Addfiles 计划书 — Chat‑First Pipeline（骨架接口）

目标：为五个变更提供骨架代码和一致的接口，暂不修改仓库。本计划描述文件意图、CLI、schemas 和 patch points，以便团队快速实现/合并。

---

## 1) tools/chat2events.py（新增）

- **目的**：解析 `raw/cursor.md`（Cursor chat markdown）→ 输出 `events.jsonl` 和可选的 `artifacts/reflection.txt`
- **CLI**：`python tools/chat2events.py data/runs/<run_id>`
- **输入**：`data/runs/<run_id>/raw/cursor.md`、`data/runs/<run_id>/goal.json`（用于 run_id/objective）
- **输出**：`events.jsonl`（必需）、`artifacts/reflection.txt`（可选）
- **启发式规则（MVP）**：
  - edit：包含关键词或代码块的语句，如"已修改/updated/changed/edited/created/removed/…"
  - plan："建议/将/计划/propose/plan/will/can/可以考虑 …"
  - test：包含 `pytest|npm test|go test|mvn test` 的命令
  - low‑confidence：如果 edit 目标不明确，设置 `confidence="low"` 并可选调用 `git diff --name-only` 作为 fallback 来填充 `where.path`
- **Event schema（每行 JSONL）**：
  - 通用：`{ id?, run_id, step, phase, tool, why?, confidence? }`
  - edit：`where: { path, region? }, what?: { diff_hint?|code? }, evidence?: { tests?|logs? }`
  - plan：`where?: { path? }`（不计分）
  - shell(test)：`{ cmd, phase: "test"|"regress" }`
- **骨架代码（仅作说明）**：

```python
#!/usr/bin/env python3
import sys, json, re, pathlib, subprocess

EDIT_KEYS = [r"updated", r"changed", r"edited", r"created", r"removed", r"已修改", r"改为"]
PLAN_KEYS = [r"建议", r"将", r"计划", r"propose", r"plan", r"will", r"can", r"可以考虑"]
TEST_KEYS = [r"pytest", r"npm test", r"go test", r"mvn test"]

def main(run_dir: str):
    rd = pathlib.Path(run_dir); raw = (rd/"raw/cursor.md").read_text(encoding="utf-8", errors="ignore")
    goal = json.loads((rd/"goal.json").read_text(encoding="utf-8"))
    run_id = goal.get("run_id", rd.name)
    out = rd/"events.jsonl"; out.write_text("", encoding="utf-8")
    step = 0

    def emit(ev):
        nonlocal step
        step += 1; ev.setdefault("run_id", run_id); ev.setdefault("step", step)
        with out.open("a", encoding="utf-8") as f: f.write(json.dumps(ev, ensure_ascii=False)+"\n")

    # 简单的基于行的解析；团队可以用更好的 LLM/regex parser 替换
    for line in raw.splitlines():
        s = line.strip()
        if any(re.search(k, s, re.I) for k in TEST_KEYS):
            emit({"phase":"test","tool":"shell","cmd":s})
            continue
        if any(re.search(k, s, re.I) for k in EDIT_KEYS):
            where = {"path": "(unknown)"}; conf = "low"
            m = re.search(r"`([^`]+\.(?:py|md|txt|json|yml|yaml|js))`", s)
            if m: where["path"], conf = m.group(1), "high"
            emit({"phase":"modify","tool":"edit","where": where, "why": s, "confidence": conf})
            continue
        if any(re.search(k, s, re.I) for k in PLAN_KEYS):
            emit({"phase":"modify","tool":"plan","why": s, "confidence": "high"})

    # 可选：通过轻量级 git fallback 填充未知路径
    if any('"path": "(unknown)"' in l for l in out.read_text(encoding="utf-8").splitlines()):
        try:
            files = subprocess.check_output(["git","diff","--name-only"], cwd=str(rd), text=True).splitlines()
        except Exception:
            files = []
        if files:
            lines = []
            for l in out.read_text(encoding="utf-8").splitlines():
                if '"tool":"edit"' in l and '"path": "(unknown)"' in l:
                    ev = json.loads(l); ev["where"]["path"] = files[0]; ev["confidence"] = ev.get("confidence","low")
                    lines.append(json.dumps(ev, ensure_ascii=False))
                else:
                    lines.append(l)
            out.write_text("\n".join(lines)+"\n", encoding="utf-8")

    # 可选反思
    (rd/"artifacts").mkdir(parents=True, exist_ok=True)
    (rd/"artifacts"/"reflection.txt").write_text("Doc-only task reflection (placeholder).", encoding="utf-8")

if __name__ == "__main__":
    main(sys.argv[1])
```

---

## 2) scripts/e2e_chat_only.py（新增）

- **目的**：一键 chat‑first pipeline：chat → events → guards → pattern → retrieve → render
- **CLI**：`python scripts/e2e_chat_only.py <run_id>`（run dir = `data/runs/<run_id>`）
- **步骤（MVP）**：
  1) `python tools/chat2events.py <run_dir>`
  2) `python tools/events2guards.py <run_dir>`
  3) 提取 pattern 到 `<run_dir>/artifacts/pattern.<id>.json` 并复制到 `data/patterns/`
  4) 为新目标文本检索最佳 pattern（从 `goal.json.objective` 或 CLI 参数）
  5) 使用 profile `data/profiles/<user>.json` 和可选 difficulty 选择 view
  6) 渲染到 `<run_dir>/artifacts/view_preview.md`
- **骨架代码（仅作说明）**：

```python
#!/usr/bin/env python3
import sys, os, pathlib, shutil, json
from subprocess import check_call

def run(cmd):
    print("$", cmd); check_call(cmd, shell=True)

def main(run_id: str, user: str = "jeremy", difficulty: str = None):
    rd = pathlib.Path(f"data/runs/{run_id}")
    run(f"python tools/chat2events.py {rd}")
    run(f"python tools/events2guards.py {rd}")
    from agent.extract_card import extract_and_save
    pat_local = rd/"artifacts"/"pattern.pc_doc_only_change.json"
    extract_and_save(str(rd), str(pat_local))
    shutil.copy2(pat_local, pathlib.Path("data/patterns")/pat_local.name)
    from q2_memory.retrieve import retrieve
    goal = json.loads((rd/"goal.json").read_text(encoding="utf-8"))
    pattern, score = retrieve(goal.get("objective",""))
    from q3_views.render import choose_view, render
    profile = pathlib.Path(f"data/profiles/{user}.json")
    view = choose_view(str(profile), difficulty=difficulty)
    out = render(pattern, view)
    (rd/"artifacts").mkdir(parents=True, exist_ok=True)
    (rd/"artifacts"/"view_preview.md").write_text(f"# View: {view}\n\n{out}", encoding="utf-8")

if __name__ == "__main__":
    main(sys.argv[1], *(sys.argv[2:3] or []))
```

---

## 3) tools/events2guards.py（补丁）

- **阈值（可配置）**：`warn >= 0.5`、`rollback >= 0.8`（从 `goal.json.thresholds?` 读取，带默认值）
- **Action 映射**：
  - drift < warn → `action="ok"`
  - warn ≤ drift < rollback → `action="warn"`
  - drift ≥ rollback → `action="rollback"`
- **Auto‑fix 建议（仅 edit）**：当路径在 `allowed_paths` 外且无例外时，输出 `auto_fixable=true` 和 `fix_cmd="git checkout -- <file>"`
- **计分范围**：
  - edit → Scope/Plan/Evidence
  - shell(test) → TestGuard
  - plan → 不计分（`action="ok"`）
- **骨架补丁（仅作说明）**：

```python
# 在 tools/events2guards.py 内部
warn_t = goal.get("thresholds",{}).get("warn", 0.5)
rollback_t = goal.get("thresholds",{}).get("rollback", 0.8)

def action_for(ds: float) -> str:
    return "rollback" if ds >= rollback_t else ("warn" if ds >= warn_t else "ok")

for ev in events:
    # 计算 sg/pg/tg/eg 如今天
    ds = drift_score((sg,pg,tg,eg))
    act = action_for(ds)
    g = {"run_id":ev.get("run_id"),"step":ev.get("step"),
         "scope_guard":sg,"plan_guard":pg,"test_guard":tg,"evidence_guard":eg,
         "drift_score":ds,"action":act}
    if ev.get("tool") == "edit":
        file = (ev.get("where") or "").split(":")[0]
        g["file"] = file
        if act == "rollback" and not in_allowed(file):
            g.update({"auto_fixable": True, "fix_cmd": f"git checkout -- {file}"})
    # plan events：强制 ok
    if ev.get("tool") == "plan":
        g.update({"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,
                  "drift_score":0,"action":"ok"})
```

---

## 4) agent/extract_card.py（补丁）

- **添加元数据字段并保持当前内容**：
  - `version`（如 "1.0"）、`title` 和 `provenance`，包含 `source_runs`、`created_by`、`created_at`（ISO8601）
- **骨架补丁**：

```python
pat = {
  "version": "1.0",
  "pattern_id":"pc_doc_only_change",
  "title": "文档/翻译类变更：只改白名单",
  "triggers":["documentation-only","translate readme"],
  "steps":["whitelist README.md/docs/**","forbid requirements.*","doc_lang_check & whitelist_diff_check"],
  "invariants":["only whitelisted files changed","language==target"],
  "anti_patterns":["edit requirements without consent"],
  "eval_examples":["doc_lang_check","whitelist_diff_check"],
  "views":{ "terse":"...", "guided":"..." },
  "provenance":{ "source_runs":["<run_id>"], "created_by":"team", "created_at":"2025-10-25T10:00:00Z" }
}
```

---

## 5) q3_views/render.py（补丁）

- **输入**：`pattern` + `profiles/<user>.json`，包含 `self_report`、`hist_first_try_success`、`pref`；可选的 `difficulty`（"low|medium|high"）
- **路由（MVP）**：
  - 如果指定了 `pref` → 直接使用
  - 否则如果 `self_report == "novice"` 或 `difficulty == "high"` 或 `hist_first_try_success < 0.5` → `guided`
  - 否则 → `terse`
- **骨架补丁**：

```python
def choose_view(profile_path: str, difficulty: str | None = None) -> str:
    p = json.loads(pathlib.Path(profile_path).read_text(encoding="utf-8"))
    if p.get("pref") in {"terse","guided"}: return p["pref"]
    if p.get("self_report") == "novice": return "guided"
    if difficulty == "high": return "guided"
    if p.get("hist_first_try_success", 0.0) < 0.5: return "guided"
    return "terse"
```

---

## Schemas（参考）

- **events.jsonl（联合类型）**：
  - edit：`{ run_id, step, phase:"modify", tool:"edit", where:{path,region?}, why?, confidence?, evidence? }`
  - plan：`{ run_id, step, phase:"modify", tool:"plan", why, confidence? }`
  - shell(test)：`{ run_id, step, phase:"test"|"regress", tool:"shell", cmd }`
- **guards.jsonl**：
  - `{ run_id, step, scope_guard, plan_guard, test_guard, evidence_guard, drift_score, action, file?, auto_fixable?, fix_cmd? }`
- **pattern card（新增字段）**：
  - `{ version, pattern_id, title, triggers[], steps[], invariants[], anti_patterns[], eval_examples[], views:{terse,guided}, provenance:{source_runs[], created_by, created_at} }`
- **profile**：
  - `{ user_id, self_report, hist_first_try_success, pref }`

---

## 兼容性与合并说明

- **非破坏性**：如果缺少阈值或新字段，默认值保持当前行为
- `events2guards.py` 从 `goal.json` 读取可选的 `thresholds.warn|rollback`；回退到 0.5/0.8
- `render.choose_view` 如果省略 `difficulty` 仍保持向后兼容

## 测试计划（MVP）

- **Chat‑only 快乐路径**：README 翻译 chat → edit README + test event → guards=ok
- **Drift 案例**：chat 提议/编辑 `requirements.txt` → 根据阈值 `action=warn/rollback`；在白名单外时存在 `auto_fixable`
- **路由**：带有 `pref=terse` 的 profile → terse；带有 `self_report=novice` 或 `hist_first_try_success=0.3` 或 `difficulty=high` → guided
- **Pattern 元数据**：验证字段存在并复制到 `data/patterns/`

## 开放问题

- 我们是否需要每个仓库的 allowed paths 例外（例如，docs‑only 任务可能触及本地化资源）？
- `git diff --name-only` fallback 应该在仓库根目录还是 run dir 中运行？（当前草图假设 run dir 在仓库根目录上下文中）
- 我们是否在分析中展示带有 `confidence` 的 plan events，即使它们不影响 guards？
```
