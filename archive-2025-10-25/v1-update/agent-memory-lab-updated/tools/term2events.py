#!/usr/bin/env python3
import sys, json, pathlib
run_dir = pathlib.Path(sys.argv[1])
log = (run_dir/"raw/term.log").read_text(encoding="utf-8", errors="ignore") if (run_dir/"raw/term.log").exists() else ""
goal = json.loads((run_dir/"goal.json").read_text(encoding="utf-8"))
events_path = run_dir / "events.jsonl"
step = sum(1 for _ in events_path.open("r",encoding="utf-8")) if events_path.exists() else 0

for line in log.splitlines():
    if "pytest" in line:
        step += 1
        ev = {"run_id":goal.get("run_id","run"),"step":step,
              "phase":"test" if "-k" in line else "regress",
              "tool":"shell","cmd":line.strip(),"result":"unknown"}
        with events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False)+"\n")

print("Appended test/shell events to", events_path)
