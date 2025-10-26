# Data Schemas (Updated)

## goal.json
```json
{
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md", "docs/"],
  "forbidden_paths": ["requirements.txt","src/","setup.py"],
  "checkpoints": ["reproduce","modify","test","regress"],
  "required_tests": ["doc_lang_check","whitelist_diff_check"]
}
```

## events.jsonl
One JSON per line:
```json
{"run_id":"r42","step":1,"phase":"modify","tool":"edit",
 "where":"README.md:1",
 "what":{"diff":"@@ -1 +1 @@ ..."},
 "why":"translate to zh-CN","evidence":{"tests":["doc_lang_check"]}}
```

## guards.jsonl
```json
{"run_id":"r42","step":2,"scope_guard":1.0,"plan_guard":1.0,
 "test_guard":0.0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn",
 "file":"requirements.txt"}
```

## pattern card (pc_*.json)
```json
{"pattern_id":"pc_doc_only_change",
 "triggers":["documentation-only","translate readme"],
 "steps":["whitelist README.md/docs/**","forbid requirements.*",
          "doc_lang_check & whitelist_diff_check"],
 "invariants":["only whitelisted files changed","language==target"],
 "anti_patterns":["edit requirements without consent"],
 "eval_examples":["doc_lang_check","whitelist_diff_check"],
 "views":{"terse":"rule+invariants",
          "guided":"how to set whitelist & checks"}}
```
