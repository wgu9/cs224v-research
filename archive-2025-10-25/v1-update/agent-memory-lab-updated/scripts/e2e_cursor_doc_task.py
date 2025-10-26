# End-to-end: ingest raw -> events -> guards -> reflection -> pattern -> retrieve -> render
import pathlib, shutil, sys, os

# Add the parent directory to Python path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import modules without executing their main code
from subprocess import check_call
from agent.extract_card import extract_and_save
from q2_memory.retrieve import retrieve
from q3_views.render import choose_view, render

RUN_DIR = pathlib.Path("data/runs/2025-10-25_r42_jw")
GLOBAL_PAT_DIR = pathlib.Path("data/patterns")
PROFILE = pathlib.Path("data/profiles/jeremy.json")

def run(cmd):
    print("$", cmd)
    check_call(cmd, shell=True)

def main():
    print("== Step 1: build events from patch")
    run(f"python tools/patch2events.py {RUN_DIR}")

    if (RUN_DIR/'raw/term.log').exists():
        print("== Step 2: append test/shell events from term.log")
        run(f"python tools/term2events.py {RUN_DIR}")

    print("== Step 3: compute guards & drift")
    run(f"python tools/events2guards.py {RUN_DIR}")

    print("== Step 4: extract pattern from reflection")
    pat_local = RUN_DIR/'artifacts/pattern.pc_doc_only_change.json'
    extract_and_save(str(RUN_DIR), str(pat_local))

    print("== Step 5: copy pattern to global library")
    GLOBAL_PAT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pat_local, GLOBAL_PAT_DIR/pat_local.name)

    print('== Step 6: retrieve for a NEW run (simulated)')
    goal_text = "Translate README; documentation-only; avoid dependency changes"
    best, score = retrieve(goal_text, str(GLOBAL_PAT_DIR))
    print("Retrieved:", best.get("pattern_id"), "score=", score)

    print("== Step 7: render view per profile")
    view = choose_view(str(PROFILE))
    output = render(best, view)
    (RUN_DIR/'artifacts/view_preview.md').write_text(f"# View: {view}\n\n{output}", encoding='utf-8')
    print("Rendered view:", view)
    print("\nDone. See:", RUN_DIR)

if __name__ == "__main__":
    main()
