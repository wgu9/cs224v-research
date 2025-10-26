import json, re, pathlib

def score_pattern(pattern: dict, goal_text: str) -> float:
    hits = 0
    for t in pattern.get("triggers", []):
        key = t.split()[0]
        if re.search(rf"\b{re.escape(key)}\b", goal_text, re.I):
            hits += 1
    return hits/max(1,len(pattern.get("triggers",[])))

def retrieve(goal_text: str, patterns_dir="data/patterns"):
    best, score = None, -1
    pdir = pathlib.Path(patterns_dir)
    pdir.mkdir(parents=True, exist_ok=True)
    for p in pdir.glob("*.json"):
        data = json.loads(p.read_text(encoding="utf-8"))
        s = score_pattern(data, goal_text)
        if s > score:
            best, score = data, s
    return best, score
