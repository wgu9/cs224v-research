def test_guard(event: dict) -> float:
    # simple demo: if phase is 'test' or 'regress', require cmd contains pytest
    if event.get("phase") in {"test","regress"} and event.get("tool") == "shell":
        return 0.0 if "pytest" in event.get("cmd","") else 1.0
    return 0.0
