# Data Schemas (examples)

## `events.jsonl` (one line per event)
```json
{"run_id":"r1","step":1,"phase":"reproduce",
 "tool":"shell","cmd":"pytest -k failing_case","result":"fail"}
{"run_id":"r1","step":2,"phase":"modify","tool":"edit",
 "where":"ingest/csv_loader.py:120",
 "what":{"diff":"@@ -a,+b ...","ast_hint":"Call(csv.reader, keep_empty=True)"},
 "why":"fix trailing delimiter dropping last column",
 "evidence":{"tests":["test_tail_comma"],"logs":["..."]}}
```

## `guards.jsonl`
```json
{"run_id":"r1","step":2,"scope_guard":1,"plan_guard":0,"test_guard":0,"evidence_guard":0.3,
 "drift_score":0.58,"action":"warn"}
```

## `patterns/*.json`
```json
{"pattern_id":"pc_delimited_tail",
 "triggers":["delimited import","trailing delimiter","empty field drops"],
 "steps":["use library parser (avoid naive split)",
          "keep_empty_fields=True",
          "add boundary tests for trailing delimiter"],
 "invariants":["len(parsed_row)==len(header)","quoted delimiter must not split"],
 "anti_patterns":["raw str.split(',') on lines"],
 "eval_examples":["test_tail_delimiter","test_empty_last_col"],
 "views":{"terse":"3 invariants + 1 assertion",
          "guided":"example code + pitfalls + 3 boundary tests"}}
```

## `profiles.json`
```json
{"user_id":"u1","self_report":"intermediate",
 "hist_first_try_success":0.35,"pref":"terse"}
```

## SWE-bench predictions format
```json
{"instance_id":"sympy__sympy-20590","model_name_or_path":"your-agent",
 "model_patch":"diff --git a/... (unified diff) ..."}
```
