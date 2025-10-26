#!/usr/bin/env python3
"""End-to-end (chat-only): chat -> events -> guards -> pattern -> retrieve -> render.

Usage:
    python scripts/e2e_chat_only.py <run_id> [user]

Examples:
    python scripts/e2e_chat_only.py 2025-10-25_r42_jw jeremy
    python scripts/e2e_chat_only.py r60 demo
"""
import sys, os, json, pathlib, shutil
from subprocess import check_call

ROOT = pathlib.Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Ensure project root is importable
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def run(cmd: str):
    print("$", cmd)
    check_call(cmd, shell=True)

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/e2e_chat_only.py <run_id> [user]", file=sys.stderr)
        sys.exit(2)
    run_id = sys.argv[1]
    user = sys.argv[2] if len(sys.argv) >= 3 else "jeremy"

    run_dir = ROOT/"data"/"runs"/run_id
    if not (run_dir/"raw"/"cursor.md").exists():
        print(f"cursor.md not found under {run_dir}/raw/", file=sys.stderr)
        sys.exit(1)

    # 1) chat -> events
    run(f"python tools/chat2events.py {run_dir}")

    # 2) events -> guards
    run(f"python tools/events2guards.py {run_dir}")

    # 3) extract pattern and copy to global library
    from agent.extract_card import extract_and_save
    pat_local = run_dir/"artifacts"/"pattern.pc_doc_only_change.json"
    pat = extract_and_save(str(run_dir), str(pat_local))
    (ROOT/"data"/"patterns").mkdir(parents=True, exist_ok=True)
    shutil.copy2(pat_local, ROOT/"data"/"patterns"/pat_local.name)

    # 4) retrieve for current objective
    from q2_memory.retrieve import retrieve
    goal = json.loads((run_dir/"goal.json").read_text(encoding="utf-8")) if (run_dir/"goal.json").exists() else {}
    objective = goal.get("objective", "") or goal.get("run_id", run_id)
    best, score = retrieve(objective, str(ROOT/"data"/"patterns"))
    print("Retrieved pattern:", (best or {}).get("pattern_id"), "score=", score)

    # 5) choose view and render
    from q3_views.render import choose_view, render
    profile_path = ROOT/"data"/"profiles"/(f"{user}.json")
    view = choose_view(str(profile_path))
    output = render(best, view) if best else "(no pattern)"
    (run_dir/"artifacts").mkdir(parents=True, exist_ok=True)
    (run_dir/"artifacts"/"view_preview.md").write_text(f"# View: {view}\n\n{output}", encoding="utf-8")
    print("Rendered view:", view)
    print("Done. See:", run_dir)

if __name__ == "__main__":
    main()
