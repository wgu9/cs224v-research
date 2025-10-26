from pathlib import Path
import json

def reflection_to_pattern(reflection: str) -> dict:
    # Very naive extractor: emits a fixed demo card.
    return {
        "pattern_id":"pc_delimited_tail",
        "triggers":["delimited import","trailing delimiter","empty field drops"],
        "steps":["use library parser (avoid naive split)",
                 "keep_empty_fields=True",
                 "add boundary tests for trailing delimiter"],
        "invariants":["len(parsed_row)==len(header)","quoted delimiter must not split"],
        "anti_patterns":["raw str.split(',') on lines"],
        "eval_examples":["test_tail_delimiter","test_empty_last_col"],
        "views":{"terse":"3 invariants + 1 assertion",
                 "guided":"example code + pitfalls + 3 boundary tests"}
    }

def save_pattern(pattern: dict, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(pattern, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    from agent.reflexion import make_reflection
    ref = make_reflection("data/examples/events/events.r1.jsonl")
    pat = reflection_to_pattern(ref)
    save_pattern(pat, "data/examples/patterns/pc_delimited_tail.json")
    print("Pattern saved.")
