def plan_guard(event: dict, plan: dict) -> float:
    phase = event.get("phase")
    tool = event.get("tool")
    cfg = plan.get(phase, {})
    allowed = cfg.get("allowed_tools", [])
    if allowed and tool not in allowed:
        return 1.0
    req = cfg.get("required_cmd_contains")
    if req and event.get("tool") == "shell":
        cmd = event.get("cmd","")
        if not all(tok in cmd for tok in req):
            return 1.0
    return 0.0
