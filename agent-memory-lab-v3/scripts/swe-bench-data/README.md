# 重要的脚本
## 两个脚本的对比

### `example_load_data.py` — 示例代码
- 作用：教学示例
- 方式：一次性运行所有分析
- 输出：统计图表（分发难度、测试数量等）
- 目标：展示数据用法
- 使用场景：学习与参考

### `inspect_swebench.py` — 交互式检查器
- 作用：深度浏览数据集
- 方式：交互式，按需选择任务
- 功能：
  - 浏览任务详情（ID、repo、问题描述、测试）
  - 按索引选择任务（交互式）
  - 数据集概览
  - 列出可用字段
- 使用场景：调试、探索单个任务、验证数据

## 使用建议
```bash
# 查看整体统计（一次性）
python scripts/swe-bench-data/example_load_data.py

# 交互式浏览单个任务
python scripts/swe-bench tell-data/inspect_swebench.py
```

需要实时查看某个任务时用 `inspect_swebench.py`，批量分析与统计用 `example_load_data.py`。


# SWE-bench Data Scripts

Scripts for downloading, inspecting, and analyzing SWE-bench datasets.

## 📥 Download Scripts

### `download_swebench.py`
Download SWE-bench Verified (500 tasks) and optionally Train split.

```bash
python scripts/swe-bench-data/download_swebench.py
```

**Downloads:**
- SWE-bench Verified (500 tasks, ~7.7 MB) → `data/swebench/verified.jsonl`
- SWE-bench Train (2,294 tasks, optional) → `data/swebench/train.jsonl`
- SWE-bench Lite (300 tasks, optional) → `data/swebench/lite.jsonl`

### `download_train.py`
Download only the Train split (for Q2 pattern extraction).

```bash
python scripts/swe-bench-data/download_train.py
```

**Downloads:**
- SWE-bench Train (2,294 tasks, ~20-30 MB) → `data/swebench/train.jsonl`

---

## 🔍 Inspection Scripts

### `inspect_swebench.py`
Interactive data inspector with detailed analysis.

```bash
python scripts/swe-bench-data/inspect_swebench.py
```

**Features:**
- Dataset statistics (repo distribution, test counts, patch sizes)
- Interactive task browser
- Detailed task inspection

### `example_load_data.py`
Comprehensive examples of data analysis.

```bash
python scripts/swe-bench-data/example_load_data.py
```

**Shows:**
- Basic statistics (repositories, difficulty distribution)
- Filter by difficulty (for Q3 dynamic abstraction)
- Test analysis (for Q1 Test Guard)
- Pattern extraction hints (for Q2)
- Scope analysis (for Q1 Scope Guard)

---

## 📊 Quick Usage

### Check Data Status
```bash
# See what's downloaded
ls -lh data/swebench/

# Quick stats
python scripts/swe-bench-data/example_load_data.py
```

### Load Data in Python
```python
import json
from pathlib import Path

# Load all tasks
data_file = Path("data/swebench/verified.jsonl")
tasks = []
with open(data_file) as f:
    for line in f:
        tasks.append(json.loads(line))

print(f"Total tasks: {len(tasks)}")
```

---

## 📋 Data Structure

Each task (JSONL line) contains:
- `instance_id`: Unique identifier
- `repo`: Repository name
- `problem_statement`: Bug description
- `base_commit`: Git commit hash
- `FAIL_TO_PASS`: Tests that must pass (JSON-encoded array)
- `PASS_TO_PASS`: Tests that must not break (JSON-encoded array)
- `patch`: Ground truth solution (don't show to agent!)
- `difficulty`: Time estimate (Verified only)

See `../../Q1_DATA_USAGE_GUIDE.md` for detailed usage.

---

## 🛠️ Dependencies

```bash
pip install datasets huggingface-hub
```

Or:
```bash
pip install -r ../../requirements_swebench.txt
```

---

## 📖 Related Documentation

- `../../DATA_GUIDE.md` - Complete data guide
- `../../Q1_DATA_USAGE_GUIDE.md` - Q1 specific usage
- `../../claude/2025-10-27-rethink/000-original plan-v2.md` - Project proposal
