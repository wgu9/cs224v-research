#!/usr/bin/env python3
import sys, json, pathlib, uuid, datetime, re
from tools.utils import parse_pytest_summary, sha1_short

def main(run_dir: str):
    rd = pathlib.Path(run_dir)
    goal = json.loads((rd / "goal.json").read_text(encoding="utf-8"))
    events_path = rd / "events.jsonl"
    term_path = rd / "raw/term.log"
    if not term_path.exists():
        print("No term.log; skip shell/test events")
        return
    text = term_path.read_text(encoding="utf-8", errors="ignore")

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    step = 0
    if events_path.exists():
        step = sum(1 for _ in open(events_path, "r", encoding="utf-8"))
    now = datetime.datetime.utcnow().isoformat() + "Z"
    with events_path.open("a", encoding="utf-8") as fh:
        for ln in lines:
            if "pytest" in ln:
                step += 1
                ev = {
                    "id": str(uuid.uuid4()),
                    "run_id": goal.get("run_id","run"),
                    "step": step,
                    "ts": now,
                    "phase": "test" if "-k" in ln else "regress",
                    "tool": "shell",
                    "cmd": ln,
                    "stdout_digest": sha1_short(ln)
                }
                fh.write(json.dumps(ev, ensure_ascii=False)+"\n")

    summary = parse_pytest_summary(text)
    (rd/"artifacts").mkdir(parents=True, exist_ok=True)
    (rd/"artifacts/pytest_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Appended shell events and wrote artifacts/pytest_summary.json")

if __name__ == "__main__":
    main(sys.argv[1])
