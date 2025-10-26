#!/usr/bin/env python3
import sys, json, re, pathlib, subprocess

# Heuristic keyword sets (MVP)
EDIT_KEYS = [r"updated", r"changed", r"edited", r"created", r"removed", r"已修改", r"修改了", r"改为", r"重构", r"已翻译", r"翻译"]
PLAN_KEYS = [r"建议", r"将", r"计划", r"propose", r"plan", r"will", r"can", r"可以考虑", r"考虑"]
TEST_KEYS = [r"pytest", r"npm test", r"go test", r"mvn test", r"gradle test", r"vitest"]

FILE_HINT_RE = re.compile(r"`([^`]+\.(?:py|md|txt|json|yml|yaml|js|ts|tsx|jsx|go|rs|java|cs))`")
FILE_COARSE_RE = re.compile(r"([A-Za-z0-9_./-]+\.(?:py|md|txt|json|yml|yaml|js|ts|tsx|jsx|go|rs|java|cs))")

def load_text(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

def guess_file_path(line: str) -> tuple[str, str]:
    """Return (path, confidence). If unknown, path="" and confidence="low"."""
    m = FILE_HINT_RE.search(line)
    if m:
        return m.group(1), "high"
    m2 = FILE_COARSE_RE.search(line)
    if m2:
        return m2.group(1), "low"
    return "", "low"

def git_diff_name_only(cwd: pathlib.Path) -> list[str]:
    try:
        out = subprocess.check_output(["git", "diff", "--name-only"], cwd=str(cwd), text=True)
        return [l.strip() for l in out.splitlines() if l.strip()]
    except Exception:
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/chat2events.py data/runs/<run_id>", file=sys.stderr)
        sys.exit(2)

    run_dir = pathlib.Path(sys.argv[1])
    rd_raw = run_dir / "raw"
    cursor_md_path = rd_raw / "cursor.md"
    if not cursor_md_path.exists():
        print(f"cursor.md not found: {cursor_md_path}", file=sys.stderr)
        sys.exit(1)

    goal_path = run_dir / "goal.json"
    goal = json.loads(goal_path.read_text(encoding="utf-8")) if goal_path.exists() else {}
    run_id = goal.get("run_id", run_dir.name)

    lines = load_text(cursor_md_path).splitlines()
    events_path = run_dir / "events.jsonl"
    events_path.write_text("", encoding="utf-8")
    step = 0

    def emit(ev: dict):
        nonlocal step
        step += 1
        ev.setdefault("run_id", run_id)
        ev.setdefault("step", step)
        with events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        # test events
        if any(re.search(k, line, re.I) for k in TEST_KEYS):
            emit({
                "phase": "test",
                "tool": "shell",
                "cmd": line
            })
            continue

        # edit events
        if any(re.search(k, line, re.I) for k in EDIT_KEYS):
            path, conf = guess_file_path(line)
            if not path:
                # fallback to git diff --name-only; prefer first file if available
                names = git_diff_name_only(run_dir)
                if names:
                    path, conf = names[0], conf
            if path:
                # keep where as string for compatibility: "<path>:?"
                emit({
                    "phase": "modify",
                    "tool": "edit",
                    "where": f"{path}:?",
                    "why": line,
                    "confidence": conf
                })
            else:
                # cannot resolve path → treat as plan(low), do not score
                emit({
                    "phase": "modify",
                    "tool": "plan",
                    "why": line,
                    "confidence": "low"
                })
            continue

        # plan events
        if any(re.search(k, line, re.I) for k in PLAN_KEYS):
            emit({
                "phase": "modify",
                "tool": "plan",
                "why": line,
                "confidence": "high"
            })

    # optional reflection stub
    art = run_dir / "artifacts"
    art.mkdir(parents=True, exist_ok=True)
    (art / "reflection.txt").write_text(
        "Reflection: prefer doc-only whitelist; avoid deps changes; ensure doc_lang & whitelist checks.",
        encoding="utf-8"
    )

    print("Wrote", events_path)

if __name__ == "__main__":
    main()
