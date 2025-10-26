#!/usr/bin/env python3
import sys, json, re, pathlib, uuid, datetime

def write_event(fh, ev):
    fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

def extract_changed_files(patch_text: str):
    files = []
    current = None
    for line in patch_text.splitlines():
        m = re.match(r'^\+\+\+ b\/(.+)$', line)
        if m:
            current = m.group(1)
            files.append(current)
    return list(dict.fromkeys(files))

def main(run_dir: str):
    rd = pathlib.Path(run_dir)
    goal = json.loads((rd / "goal.json").read_text(encoding="utf-8"))
    patch = (rd / "raw/patch.diff").read_text(encoding="utf-8", errors="ignore")
    events_path = rd / "events.jsonl"
    events_path.write_text("", encoding="utf-8")

    files = extract_changed_files(patch)
    step = 0
    now = datetime.datetime.utcnow().isoformat() + "Z"
    with events_path.open("a", encoding="utf-8") as fh:
        for path in files:
            step += 1
            ev = {
                "id": str(uuid.uuid4()),
                "run_id": goal.get("run_id", "run"),
                "step": step,
                "ts": now,
                "phase": "modify",
                "tool": "edit",
                "where": {"path": path},
                "what": {"diff": "(omitted)"},
                "why": "from patch.diff",
                "evidence": {}
            }
            write_event(fh, ev)
    print("Wrote", events_path)

if __name__ == "__main__":
    main(sys.argv[1])
