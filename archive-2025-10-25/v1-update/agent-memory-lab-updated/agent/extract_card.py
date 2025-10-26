import json, pathlib, datetime
from agent.reflexion import make_reflection

def reflection_to_pattern(reflection: str) -> dict:
    # Note: reflection parameter is currently unused but kept for future enhancement
    return {
        "version": "1.0",
        "pattern_id":"pc_doc_only_change",
        "title": "文档/翻译类变更：只改白名单",
        "triggers":["documentation-only","translate readme"],
        "steps":["whitelist README.md/docs/**","forbid requirements.*",
                 "doc_lang_check & whitelist_diff_check"],
        "invariants":["only whitelisted files changed","language==target"],
        "anti_patterns":["edit requirements without consent"],
        "eval_examples":["doc_lang_check","whitelist_diff_check"],
        "views":{"terse":"Whitelist-only edits; forbid deps change; ensure checks.",
                 "guided":"How to set whitelist & language checks; when to request exceptions."},
        "provenance": {
            "source_runs": [],
            "created_by": "team",
            "created_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
        }
    }

def save_pattern(pattern_data: dict, out_path: str):
    p = pathlib.Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(pattern_data, ensure_ascii=False, indent=2), encoding="utf-8")

def extract_and_save(run_dir: str, out_path: str):
    ref = make_reflection(run_dir)
    pat = reflection_to_pattern(ref)
    # fill provenance with this run id if available
    rd = pathlib.Path(run_dir)
    run_id = rd.name
    try:
        goal = json.loads((rd/"goal.json").read_text(encoding="utf-8"))
        run_id = goal.get("run_id", run_id)
    except Exception:
        pass
    pat.setdefault("provenance", {}).setdefault("source_runs", []).append(run_id)
    save_pattern(pat, out_path)
    return pat

if __name__ == "__main__":
    pattern = extract_and_save("data/runs/2025-10-25_r42_jw", "data/runs/2025-10-25_r42_jw/artifacts/pattern.pc_doc_only_change.json")
    print("Saved pattern:", pattern["pattern_id"])
