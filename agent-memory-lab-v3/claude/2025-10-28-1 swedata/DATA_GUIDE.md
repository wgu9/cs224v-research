# SWE-bench Data Guide

## ✅ Current Status

**Downloaded**: SWE-bench Verified (500 tasks) ✅

- Location: `data/swebench/verified.jsonl`
- Size: 7.7 MB
- Usage: Primary evaluation dataset (Q1/Q2/Q3)

---

## 📥 Download Train Split (For Q2)

The train split is used for Q2 pattern extraction. Download it with:

```bash
python scripts/download_train.py
```

This will download ~2,294 tasks (~20-30MB) for pattern extraction.

---

## 📊 Data Structure

Each task in the JSONL file has these fields:

### Core Fields
- `instance_id`: Unique identifier (e.g., "astropy__astropy-12907")
- `repo`: Repository name (e.g., "astropy/astropy")
- `base_commit`: Git commit hash before the fix
- `problem_statement`: GitHub issue description (user-reported bug)

### Test Fields
- `FAIL_TO_PASS`: **String** (JSON array) of test names that should go from failing to passing
- `PASS_TO_PASS`: **String** (JSON array) of tests that should remain passing
- `test_patch`: Git patch containing test changes

### Solution Field (Don't Use During Execution!)
- `patch`: Ground truth solution (ONLY for evaluation)

### Metadata
- `created_at`: Issue creation timestamp (ISO format)
- `version`: Repository version string
- `difficulty`: Time estimate (e.g., "15 min - 1 hour") - **Verified only**
- `environment_setup_commit`: Commit for setting up test environment
- `hints_text`: Additional hints (usually empty string)

### ⚠️ Important: String vs Array
- `FAIL_TO_PASS` and `PASS_TO_PASS` are **JSON strings**, not arrays
- Use `json.loads()` to parse them:
```python
import json
fail_to_pass = json.loads(task['FAIL_TO_PASS'])  # Returns actual list
```

---

## 🔍 Inspect Data

View data structure and statistics:

```bash
python scripts/inspect_swebench.py
```

This will show:
- Dataset statistics (repo distribution, test counts, etc.)
- Example task in detail
- Interactive task browser

---

## 💻 Load Data in Python

### Load Single Task

```python
import json

def load_task(instance_id):
    """Load a specific task by ID."""
    with open("data/swebench/verified.jsonl") as f:
        for line in f:
            task = json.loads(line)
            if task['instance_id'] == instance_id:
                return task
    return None

# Example
task = load_task("astropy__astropy-12907")
print(f"Problem: {task['problem_statement'][:200]}...")
print(f"Tests to fix: {len(task['FAIL_TO_PASS'])}")
```

### Load All Tasks

```python
import json

def load_all_tasks():
    """Load all tasks."""
    tasks = []
    with open("data/swebench/verified.jsonl") as f:
        for line in f:
            tasks.append(json.loads(line))
    return tasks

# Example
tasks = load_all_tasks()
print(f"Total tasks: {len(tasks)}")

# Filter by repo
astropy_tasks = [t for t in tasks if 'astropy' in t['repo']]
print(f"Astropy tasks: {len(astropy_tasks)}")
```

### Filter by Difficulty (Verified Only)

```python
def get_easy_tasks(tasks):
    """Get tasks with <15 min difficulty."""
    return [t for t in tasks if t.get('difficulty') == '< 15 min']

def get_hard_tasks(tasks):
    """Get tasks with >4 hour difficulty."""
    return [t for t in tasks if t.get('difficulty') == '> 4 hours']

tasks = load_all_tasks()
easy = get_easy_tasks(tasks)
hard = get_hard_tasks(tasks)

print(f"Easy tasks: {len(easy)}")
print(f"Hard tasks: {len(hard)}")
```

---

## 🎯 Usage According to Proposal

### For Final Evaluation (Q1/Q2/Q3)

```python
# Use the full Verified set (500 tasks)
verified_tasks = load_all_tasks()

# For your 6-week project, you might start with a subset
# e.g., first 50 tasks for quick iteration
dev_subset = verified_tasks[:50]
```

### For Q2 Pattern Extraction

```python
# Load train split (after downloading)
train_tasks = []
with open("data/swebench/train.jsonl") as f:
    for line in f:
        train_tasks.append(json.loads(line))

# Filter successful runs to extract patterns
# (You'll implement this based on your agent's results)
successful_tasks = [t for t in train_tasks if check_success(t)]
```

---

## 🚀 Quick Start Workflow

### Day 1: Verify Setup
```bash
# 1. Check you have verified data
ls -lh data/swebench/verified.jsonl  # Should show 7.7MB

# 2. Inspect structure
python scripts/inspect_swebench.py

# 3. Load a few tasks in Python
python -c "
import json
with open('data/swebench/verified.jsonl') as f:
    task = json.loads(f.readline())
    print(f'First task: {task[\"instance_id\"]}')
"
```

### Day 2: Download Train (Optional, for Q2)
```bash
# Only needed when you start Q2 implementation
python scripts/download_train.py
```

### Day 3: Start Q1 Baseline
```bash
# Run a baseline agent on 5-10 easy tasks
# (You'll implement this next)
```

---

## 📝 Important Notes

### ⚠️ Don't Use `patch` During Execution

The `patch` field contains the ground truth solution. **Never** show this to your agent during execution! Only use it for:
- Post-execution evaluation (compare your agent's patch with ground truth)
- Computing metrics like Scope alignment

### ✅ Use Test Results for Evaluation

The correct way to evaluate:
1. Agent generates a patch
2. Apply patch to repository at `base_commit`
3. Run tests specified in `FAIL_TO_PASS` and `PASS_TO_PASS`
4. Check if all FAIL_TO_PASS pass and no PASS_TO_PASS fail

### 📊 Difficulty Labels (Verified Only)

Difficulty categories in Verified subset:
- `"< 15 min"`: Quick fixes
- `"15 min - 1 hour"`: Moderate complexity
- `"1-4 hours"`: Complex issues
- `"> 4 hours"`: Very challenging

This is perfect for Q3 (dynamic abstraction based on task complexity)!

---

## 🔗 References

- [SWE-bench GitHub](https://github.com/princeton-nlp/SWE-bench)
- [SWE-bench Paper](https://arxiv.org/abs/2310.06770)
- [HuggingFace Dataset](https://huggingface.co/datasets/princeton-nlp/SWE-bench)

---

## ❓ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'datasets'"
```bash
pip install datasets huggingface-hub
```

### Issue: "File too large / download timeout"
The download scripts cache data in `~/.cache/huggingface/datasets/`. If interrupted, just re-run the script - it will resume.

### Issue: "How do I filter by repository?"
```python
# List all repos
repos = set(t['repo'] for t in tasks)
print(sorted(repos))

# Filter
django_tasks = [t for t in tasks if 'django' in t['repo'].lower()]
```

---

**Next**: Ready to implement Q1! 🎉
