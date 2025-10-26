#!/usr/bin/env python3
import sys, json, re, pathlib

run_dir = pathlib.Path(sys.argv[1])
patch = (run_dir / "raw/patch.diff").read_text(encoding="utf-8", errors="ignore")
goal = json.loads((run_dir / "goal.json").read_text(encoding="utf-8"))
run_id = run_dir.name.split("_")[1] if "_" in run_dir.name else goal.get("run_id","run")

events_path = run_dir / "events.jsonl"
events_path.write_text("", encoding="utf-8")

step = 0
current_file = None

for line in patch.splitlines():
    m = re.match(r"^\+\+\+ b/(.+)$", line)
    if m:
        current_file = m.group(1)
        continue
    # capture first hunk header to create a minimal edit event
    h = re.match(r"^@@ .* @@", line)
    if h and current_file:
        step += 1
        ev = {
            "run_id": goal.get("run_id","run"),
            "step": step,
            "phase": "modify",
            "tool": "edit",
            "where": f"{current_file}:?",
            "what": {"diff": "(omitted hunk)", "ast_hint": None},
            "why": "from patch.diff",
            "evidence": {}
        }
        with events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        current_file = None  # only one event per file for simplicity

print("Wrote", events_path)
