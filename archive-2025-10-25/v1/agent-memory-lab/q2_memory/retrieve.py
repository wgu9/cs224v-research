import json, re
from pathlib import Path

def score_pattern(pattern: dict, goal_text: str) -> float:
    hits = 0
    for t in pattern.get("triggers", []):
        if re.search(rf"\b{re.escape(t.split()[0])}\b", goal_text, re.I):
            hits += 1
    return hits / max(1, len(pattern.get("triggers", [])))

def retrieve(goal_text: str, patterns_dir: str = "data/examples/patterns"):
    best = None
    best_s = -1
    for p in Path(patterns_dir).glob("*.json"):
        pat = json.loads(p.read_text(encoding="utf-8"))
        s = score_pattern(pat, goal_text)
        if s > best_s:
            best, best_s = pat, s
    return best, best_s

if __name__ == "__main__":
    pat, s = retrieve("delimited import with trailing delimiter")
    print("Best score:", s)
    print(json.dumps(pat, ensure_ascii=False, indent=2))
