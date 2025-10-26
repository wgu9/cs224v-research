def drift_score(guards: dict, w=(0.4,0.3,0.2,0.1)) -> float:
    sg = guards.get("scope_guard",0.0)
    pg = guards.get("plan_guard",0.0)
    tg = guards.get("test_guard",0.0)
    eg = guards.get("evidence_guard",0.0)
    a,b,c,d = w
    return a*sg + b*pg + c*tg + d*eg
