import json, pathlib

def choose_view(profile_path: str, difficulty: str | None = None) -> str:
    p = json.loads(pathlib.Path(profile_path).read_text(encoding="utf-8"))
    pref = p.get("pref")
    if pref in {"terse","guided"}:
        return pref
    if p.get("self_report") == "novice":
        return "guided"
    if (difficulty or "").lower() == "high":
        return "guided"
    if p.get("hist_first_try_success",0) < 0.5:
        return "guided"
    return "terse"

def render(pattern: dict, view: str) -> str:
    return pattern.get("views",{}).get(view,"(no view)") + "\n\nInvariants: " + ", ".join(pattern.get("invariants",[]))
