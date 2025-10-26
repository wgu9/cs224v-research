#!/usr/bin/env python3
import sys, json, pathlib

run_dir = pathlib.Path(sys.argv[1])
goal = json.loads((run_dir/"goal.json").read_text(encoding="utf-8"))
allowed = goal.get("allowed_paths", [])
required_cmds = {"test": ["pytest"], "regress": ["pytest"]}
warn_t = goal.get("thresholds", {}).get("warn", 0.5)
rollback_t = goal.get("thresholds", {}).get("rollback", 0.8)

def in_allowed(p):
    return any(p==a or p.startswith(a.rstrip('/')+'/') for a in allowed)

def file_from_where(ev):
    w = ev.get("where")
    if not w:
        return ""
    if isinstance(w, str):
        return w.split(":")[0]
    if isinstance(w, dict):
        p = w.get("path", "")
        return p.split(":")[0]
    return ""

def scope_guard(ev):
    if ev.get("tool") == "edit":
        path = file_from_where(ev)
        return 0.0 if (path and in_allowed(path)) else 1.0
    return 0.0

def plan_guard(ev):
    # Only consider planning around edit targets during modify phase.
    if ev.get("tool") == "edit" and ev.get("phase") == "modify":
        path = file_from_where(ev)
        return 0.0 if (path and in_allowed(path)) else 1.0
    return 0.0

def test_guard(ev):
    # For demo: if we see required tokens in shell cmd for test/regress phases.
    if ev.get("phase") in {"test","regress"} and ev.get("tool")=="shell":
        phase = ev.get("phase")
        cmd = ev.get("cmd", "")
        req = required_cmds.get(phase, [])
        return 0.0 if all(tok in cmd for tok in req) else 1.0
    return 0.0

def evidence_guard(ev):
    if ev.get("phase")=="modify" and ev.get("tool")=="edit":
        evd = ev.get("evidence") or {}
        return 0.0 if (evd.get("tests") or evd.get("logs")) else 0.5
    return 0.0

def drift_score(scores, w=(0.4,0.3,0.2,0.1)):
    sg, pg, tg, eg = scores
    a,b,c,d = w
    return a*sg + b*pg + c*tg + d*eg

guards_path = run_dir/"guards.jsonl"
guards_path.write_text("", encoding="utf-8")
events = [json.loads(l) for l in (run_dir/"events.jsonl").open("r",encoding="utf-8")]
for ev in events:
    # plan events never score
    if ev.get("tool") == "plan":
        g = {"run_id":ev.get("run_id"),"step":ev.get("step"),
             "scope_guard":0.0,"plan_guard":0.0,"test_guard":0.0,"evidence_guard":0.0,
             "drift_score":0.0,"action":"ok"}
        with guards_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(g, ensure_ascii=False)+"\n")
        continue

    sg = scope_guard(ev)
    pg = plan_guard(ev)
    tg = test_guard(ev)
    eg = evidence_guard(ev)
    ds = drift_score((sg,pg,tg,eg))
    action = "rollback" if ds >= rollback_t else ("warn" if ds >= warn_t else "ok")
    g = {"run_id":ev.get("run_id"),"step":ev.get("step"),
         "scope_guard":sg,"plan_guard":pg,"test_guard":tg,"evidence_guard":eg,
         "drift_score":ds,"action":action}
    # include file + fix suggestion if rollback on out-of-scope edit
    if ev.get("tool")=="edit":
        file_path = file_from_where(ev)
        if file_path:
            g["file"] = file_path
            if action == "rollback" and not in_allowed(file_path):
                g["auto_fixable"] = True
                g["fix_cmd"] = f"git checkout -- {file_path}"
    with guards_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(g, ensure_ascii=False)+"\n")
print("Wrote", guards_path)
