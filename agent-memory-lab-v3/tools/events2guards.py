#!/usr/bin/env python3
"""
Analyzes a sequence of events to detect context drift.

This script reads an `events.jsonl` file and a `goal.json` file. For each
event, it applies a set of "guards" (Scope, Plan, Test, Evidence) to
calculate a `drift_score`. The final output is a `guards.jsonl` file
containing the score and a recommended action (`ok`, `warn`, `rollback`)
for each event.

**LLM Usage**: ❌ NO LLM CALLS
  - Uses rule-based logic only
  - Four guards:
    * Scope Guard: Check if files in allowed_paths (glob pattern matching)
    * Plan Guard: Check if tools allowed in current phase
    * Test Guard: Check if required_tests run (string matching)
    * Evidence Guard: Check if evidence attached in modify phase
  - Default weights: {"scope": 0.4, "plan": 0.3, "test": 0.2, "evidence": 0.1}
  - Default thresholds: {"warn": 0.5, "rollback": 0.8}

**Usage**: Run with runner.sh
  ./runner.sh python tools/events2guards.py data/2_runs/<run_id>
"""
import sys, json, pathlib
from tools.utils import in_allowed, is_forbidden

DEFAULT_TOOLS = {
    "reproduce": ["shell","browse","plan"],
    "modify":    ["edit","shell","plan"],
    "test":      ["shell","plan"],
    "regress":   ["shell","plan"]
}

def load_events(path):
    return [json.loads(line) for line in open(path, "r", encoding="utf-8")]

def covers_required(cmd: str, required_tests):
    if not required_tests: return True
    cmd_low = cmd.lower()
    for t in required_tests:
        if t.lower() in cmd_low:
            return True
    return False

def calc_guards(ev, goal, run_dir):
    weights = goal.get("weights") or {"scope":0.4,"plan":0.3,"test":0.2,"evidence":0.1}
    thresholds = goal.get("thresholds") or {"warn":0.5,"rollback":0.8}

    allowed = goal.get("allowed_paths", [])
    forbidden = goal.get("forbidden_paths", [])
    allowed_tools = goal.get("allowed_tools_by_phase") or DEFAULT_TOOLS

    phase = ev.get("phase"); tool = ev.get("tool")
    # PLAN 事件：不参与任何守卫计分，直接返回 ok
    if tool == "plan":
        return {
            "scope_guard": 0.0, "plan_guard": 0.0, "test_guard": 0.0, "evidence_guard": 0.0,
            "drift_score": 0.0, "action": "ok",
            "auto_fixable": False, "fix_cmd": None,
            "file": (ev.get("where") or {}).get("path"), "notes": "plan-only (ignored)"
        }

    # Scope
    scope = 0.0
    file_path = None
    if tool == "edit":
        file_path = (ev.get("where") or {}).get("path") or ""
        if in_allowed(file_path, allowed) and not is_forbidden(file_path, forbidden):
            scope = 0.0
        else:
            scope = 1.0

    # Plan
    plan = 0.0
    tools_ok = tool in (allowed_tools.get(phase) or [])
    if not tools_ok:
        plan = 1.0
    elif tool == "edit":
        if not in_allowed(file_path or "", allowed) or is_forbidden(file_path or "", forbidden):
            plan = 1.0

    # Test
    test = 0.0
    if phase in ("test","regress") and tool == "shell":
        req = goal.get("required_tests") or []
        test = 0.0 if covers_required(ev.get("cmd",""), req) else 1.0

    # Evidence
    evidence = 0.0
    if phase == "modify" and tool == "edit":
        evd = ev.get("evidence") or {}
        if evd.get("tests") or evd.get("logs") or evd.get("links"):
            evidence = 0.0
        else:
            evidence = 0.5

    # Overrides
    override = (ev.get("override") or {})
    if override.get("acknowledged") and tool == "edit":
        scope = min(scope, 0.2)
        plan = min(plan, 0.2)
        evidence = min(evidence, 0.1)

    drift = (weights["scope"]*scope + weights["plan"]*plan +
             weights["test"]*test + weights["evidence"]*evidence)

    action = "ok"
    if drift >= thresholds["rollback"]:
        action = "rollback"
    elif drift >= thresholds["warn"]:
        action = "warn"

    auto_fixable = False
    fix_cmd = None
    if tool=="edit" and file_path:
        if (scope==1.0) and not override.get("acknowledged"):
            auto_fixable = True
            fix_cmd = f"git checkout -- {file_path}"

    notes = []
    if scope==1.0: notes.append("not in allowed_paths or in forbidden_paths")
    if plan==1.0: notes.append("tool not allowed in phase or disallowed edit at this phase")
    if test==1.0: notes.append("required tests not run/passed")
    if evidence>0.0 and phase=="modify" and tool=="edit": notes.append("no evidence attached")
    if override.get("acknowledged"): notes.append(f"override: {override.get('reason','(no reason)')}")

    return {
        "scope_guard": scope, "plan_guard": plan, "test_guard": test, "evidence_guard": evidence,
        "drift_score": drift, "action": action,
        "auto_fixable": auto_fixable, "fix_cmd": fix_cmd,
        "file": file_path, "notes": "; ".join(notes) if notes else None
    }

def main(run_dir: str):
    rd = pathlib.Path(run_dir)
    goal = json.loads((rd/"goal.json").read_text(encoding="utf-8"))
    events_path = rd/"events.jsonl"
    if not events_path.exists():
        print("No events.jsonl; please run chat2events.py or patch2events.py first")
        return
    events = load_events(events_path)
    guards_path = rd/"guards.jsonl"
    guards_path.write_text("", encoding="utf-8")
    with guards_path.open("a", encoding="utf-8") as fh:
        for ev in events:
            g = calc_guards(ev, goal, run_dir)
            out = {"id": ev.get("id"), "run_id": ev.get("run_id"), "step": ev.get("step"), **g}
            fh.write(json.dumps(out, ensure_ascii=False)+"\n")
    print("Wrote", guards_path)

def cli():
    if len(sys.argv) < 2:
        print("Usage: python -m tools.events2guards <run_directory>")
        sys.exit(1)
    main(sys.argv[1])

if __name__ == "__main__":
    cli()
