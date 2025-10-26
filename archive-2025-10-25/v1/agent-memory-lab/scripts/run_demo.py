import sys
import os

# Add the parent directory to Python path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.loop import simulate_run
from agent.reflexion import make_reflection
from agent.extract_card import reflection_to_pattern, save_pattern
from q2_memory.retrieve import retrieve
from q2_memory.inject import inject
from q3_views.render import render

# 1) simulate a run, producing events/guards (Foundation + Q1 data)
simulate_run()

# 2) reflection (would be LLM in prod), then extract a pattern (Q2)
ref = make_reflection("data/examples/events/events.r1.jsonl")
pat = reflection_to_pattern(ref)
save_pattern(pat, "data/examples/patterns/pc_delimited_tail.json")

# 3) retrieve & inject for a new goal (Q2)
goal = "Fix delimited import where trailing delimiter drops the last column"
best, score = retrieve(goal)
print("\n[Retrieve] score =", score, "| pattern_id =", best.get("pattern_id"))

prompt = inject(goal, best)
print("\n[Injected Prompt]\n", prompt)

# 4) choose a view (Q3)
view, content = render("data/examples/patterns/pc_delimited_tail.json","data/examples/profiles.json")
print("\n[View =", view, "]\n", content)
print("\nDone. See data/examples for artifacts.")
