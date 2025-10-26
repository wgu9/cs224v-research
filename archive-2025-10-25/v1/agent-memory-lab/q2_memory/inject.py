def inject(goal_sketch: str, pattern: dict) -> str:
    if not pattern:
        return goal_sketch
    hint = f"Pattern hint: triggers={pattern.get('triggers')} invariants={pattern.get('invariants')} steps={pattern.get('steps')}"
    return goal_sketch + "\n\n" + hint
