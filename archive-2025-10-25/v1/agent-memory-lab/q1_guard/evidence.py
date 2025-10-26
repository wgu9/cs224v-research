def evidence_guard(event: dict) -> float:
    # demo heuristic: in modify phase, require some evidence (tests or logs) to be referenced
    if event.get("phase") == "modify" and event.get("tool") == "edit":
        ev = event.get("evidence") or {}
        has_ref = bool(ev.get("tests") or ev.get("logs"))
        return 0.0 if has_ref else 0.7
    return 0.0
