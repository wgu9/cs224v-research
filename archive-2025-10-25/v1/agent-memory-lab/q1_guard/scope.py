def scope_guard(event: dict, allowed_paths: list) -> float:
    where = event.get("where") or ""
    # shell commands aren't file edits; treat as within scope by default
    if event.get("tool") == "edit":
        return 0.0 if any(where.startswith(p) for p in allowed_paths) else 1.0
    return 0.0
