import json, os
from pathlib import Path

# This writes a minimal predictions.jsonl with a placeholder patch.
# Replace `model_patch` with your agent-produced diff for a real evaluation.
pred = {
  "instance_id":"sympy__sympy-20590",
  "model_name_or_path":"your-agent",
  "model_patch":"diff --git a/path/to/file.py b/path/to/file.py\nindex 000..111 100644\n--- a/path/to/file.py\n+++ b/path/to/file.py\n@@ -1,3 +1,4 @@\n def foo():\n-    return 1\n+    return 2\n"
}

out = Path("data/examples/predictions.sample.jsonl")
out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", encoding="utf-8") as f:
    f.write(json.dumps(pred) + "\n")
print("Wrote", out)
