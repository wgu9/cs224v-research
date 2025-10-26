from pathlib import Path
import json, time
from q1_guard.scope import scope_guard
from q1_guard.plan import plan_guard
from q1_guard.test import test_guard
from q1_guard.evidence import evidence_guard
from q1_guard.drift_score import drift_score

EVENTS_PATH = Path("data/examples/events/events.r1.jsonl")
GUARDS_PATH = Path("data/examples/guards/guards.r1.jsonl")

ALLOWED_PATHS = ["ingest/"]  # demo scope
PLAN = {
    "reproduce": {"allowed_tools": ["shell"], "required_cmd_contains": ["pytest", "-k"]},
    "modify": {"allowed_tools": ["edit"]},
    "test": {"allowed_tools": ["shell"], "required_cmd_contains": ["pytest"]},
    "regress": {"allowed_tools": ["shell"], "required_cmd_contains": ["pytest"]},
}

def log_event(ev):
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")

def log_guard(g):
    GUARDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with GUARDS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(g, ensure_ascii=False) + "\n")

def simulate_run():
    # Step 1: reproduce (fail)
    ev1 = {"run_id":"r1","step":1,"phase":"reproduce","tool":"shell","cmd":"pytest -k test_tail_delimiter","result":"fail"}
    log_event(ev1)
    g1 = {
        "run_id":"r1","step":1,
        "scope_guard": scope_guard(ev1, ALLOWED_PATHS),
        "plan_guard": plan_guard(ev1, PLAN),
        "test_guard": test_guard(ev1),
        "evidence_guard": evidence_guard(ev1),
    }
    g1["drift_score"] = drift_score(g1)
    g1["action"] = "ok" if g1["drift_score"] < 0.5 else "warn"
    log_guard(g1)

    # Step 2: modify (edit inside allowed path)
    ev2 = {"run_id":"r1","step":2,"phase":"modify","tool":"edit",
           "where":"ingest/csv_loader.py:120",
           "what":{"diff":"@@ -120,7 +120,9 @@ ...","ast_hint":"Call(csv.reader, keep_empty=True)"},
           "why":"fix trailing delimiter dropping last column",
           "evidence":{"tests":["test_tail_delimiter"]}}
    log_event(ev2)
    g2 = {
        "run_id":"r1","step":2,
        "scope_guard": scope_guard(ev2, ALLOWED_PATHS),
        "plan_guard": plan_guard(ev2, PLAN),
        "test_guard": test_guard(ev2),
        "evidence_guard": evidence_guard(ev2),
    }
    g2["drift_score"] = drift_score(g2)
    g2["action"] = "ok" if g2["drift_score"] < 0.5 else "warn"
    log_guard(g2)

    # Step 3: test (pass)
    ev3 = {"run_id":"r1","step":3,"phase":"test","tool":"shell","cmd":"pytest -k test_tail_delimiter","result":"pass"}
    log_event(ev3)
    g3 = {
        "run_id":"r1","step":3,
        "scope_guard": scope_guard(ev3, ALLOWED_PATHS),
        "plan_guard": plan_guard(ev3, PLAN),
        "test_guard": test_guard(ev3),
        "evidence_guard": evidence_guard(ev3),
    }
    g3["drift_score"] = drift_score(g3)
    g3["action"] = "ok" if g3["drift_score"] < 0.5 else "warn"
    log_guard(g3)

    # Step 4: regress (pass all)
    ev4 = {"run_id":"r1","step":4,"phase":"regress","tool":"shell","cmd":"pytest","result":"pass"}
    log_event(ev4)
    g4 = {
        "run_id":"r1","step":4,
        "scope_guard": scope_guard(ev4, ALLOWED_PATHS),
        "plan_guard": plan_guard(ev4, PLAN),
        "test_guard": test_guard(ev4),
        "evidence_guard": evidence_guard(ev4),
    }
    g4["drift_score"] = drift_score(g4)
    g4["action"] = "ok" if g4["drift_score"] < 0.5 else "warn"
    log_guard(g4)

    print("Demo run complete. See data/examples/events and data/examples/guards.")

if __name__ == "__main__":
    simulate_run()
