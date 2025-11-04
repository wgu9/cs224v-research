# Batch Workflow - 500 任务批量处理

完整的批量处理流程：生成 500 个任务的预测并计算 Q1 drift metrics。

---

## 🎯 目标

1. ✅ 批量生成 500 个 SWE-bench 任务的预测
2. ✅ 批量计算所有任务的 Q1 drift metrics
3. ✅ 分析 quality 分布，准备 Q2 pattern extraction

**预计时间**:
- 生成 500 个预测: 10-20 小时（取决于 LLM API 速度）
- 计算 drift metrics: 10-15 分钟

---

## 📋 完整工作流程

### 方案 A: 一步到位（推荐）

使用 `batch_generate_with_q1_metrics.py` 同时生成预测和计算 drift：

```bash
# 设置环境变量
export AWS_BEARER_TOKEN_BEDROCK=your_token_here

# 批量生成 500 个任务（同时计算 drift）
python batch_generate_with_q1_metrics.py \
  --start 0 \
  --end 500 \
  --full_file_mode true
```

**优点**:
- ✅ 一次运行，自动生成 predictions + drift metrics
- ✅ 节省时间，不需要后处理
- ✅ 适合新项目

**输出**:
```
logs/<timestamp>/
├── predictions/
│   ├── input_data_0/astropy__astropy-12907/predictions.jsonl
│   ├── input_data_1/django__django-12856/predictions.jsonl
│   └── ...
└── drift_metrics/
    ├── input_data_0_drift.json
    ├── input_data_1_drift.json
    └── ...
```

---

### 方案 B: 分两步（适合已有预测）

如果你已经有了 predictions，只需要添加 drift metrics：

#### Step 1: 批量生成预测

```bash
export AWS_BEARER_TOKEN_BEDROCK=your_token_here

# 批量生成（不计算 drift）
python batch_generate_predictions.py \
  --start 0 \
  --end 500 \
  --full_file_mode true \
  --base_dir logs/batch_500
```

#### Step 2: 批量计算 Drift Metrics

```bash
# 一次性计算所有 drift metrics
python compute_drift_from_predictions.py \
  --predictions_dir logs/batch_500/predictions
```

**优点**:
- ✅ 适合已经运行了 `batch_generate_predictions.py` 的情况
- ✅ 可以多次重算 drift metrics（如果算法改进）
- ✅ 不浪费已生成的预测

---

## 📊 预期输出示例

### 批量生成进度

```
================================================================================
Batch generating predictions WITH Q1 METRICS
Tasks: [0, 500) of 500
Run root: logs/2025-10-29-12-00-00
Mode: AGENT (LLM)
================================================================================

✅   0/500 astropy__astropy-12907        | Drift: 0.000 | Quality: HIGH
✅   1/500 django__django-12856          | Drift: 0.200 | Quality: MEDIUM
✅   2/500 sympy__sympy-18532            | Drift: 0.000 | Quality: HIGH
✅   3/500 matplotlib__matplotlib-23913  | Drift: 0.450 | Quality: LOW
...
✅ 497/500 scikit-learn__scikit-learn... | Drift: 0.150 | Quality: HIGH
✅ 498/500 requests__requests-2317      | Drift: 0.300 | Quality: MEDIUM
✅ 499/500 pytest__pytest-5692          | Drift: 0.100 | Quality: HIGH

================================================================================
Batch Summary
================================================================================
Attempted:              500
Success (predictions):  485
Success (with metrics): 482

Quality Distribution (for Q2 pattern extraction):
  High-quality (drift < 0.2):   330 (68.5%)  ← 用于 Q2
  Medium-quality (0.2-0.35):    105 (21.8%)
  Low-quality (drift >= 0.35):   47 ( 9.7%)

Failures:
  Load failed:    2
  Agent failed:   13
  Metrics failed: 3
================================================================================

💡 Next step: Extract patterns from high-quality solutions
   python extract_patterns_from_drift_metrics.py --input logs/.../drift_metrics
```

### 批量计算 Drift Metrics

```
================================================================================
Computing Q1 drift metrics from existing predictions
Predictions dir: logs/batch_500/predictions
Output dir: logs/batch_500/drift_metrics
Found 485 prediction folders
================================================================================

✅   0 astropy__astropy-12907                   | Drift: 0.000 | Quality: HIGH
✅   1 django__django-12856                     | Drift: 0.200 | Quality: MEDIUM
✅   2 sympy__sympy-18532                       | Drift: 0.000 | Quality: HIGH
...

================================================================================
Summary
================================================================================
Total predictions:  485
Success:            482
Failed:             3

Quality Distribution (for Q2 pattern extraction):
  High-quality:    330 (68.5%)  ← 这些用于 Q2 pattern extraction
  Medium-quality:  105 (21.8%)
  Low-quality:      47 ( 9.7%)
================================================================================

✅ Drift metrics saved to: logs/batch_500/drift_metrics
```

---

## 💡 你的实际情况（已有 408 个预测）

你已经在运行 `batch_generate_predictions.py`，有两个目录：
- `logs/2025-10-29-02-22-26/predictions/` - 408 个任务 ✅
- `logs/2025-10-29-08-45-10/predictions/` - 15 个任务 ✅

**推荐操作**:

### Step 1: 计算现有 408 个任务的 drift metrics

```bash
python compute_drift_from_predictions.py \
  --predictions_dir logs/2025-10-29-02-22-26/predictions
```

预计时间: 5-8 分钟

### Step 2: 计算第二批 15 个任务的 drift metrics

```bash
python compute_drift_from_predictions.py \
  --predictions_dir logs/2025-10-29-08-45-10/predictions
```

预计时间: < 1 分钟

### Step 3: 等待 batch_generate_predictions.py 完成

剩余任务数: 500 - 423 = 77 个

### Step 4: 完成后计算最后一批的 drift metrics

```bash
python compute_drift_from_predictions.py \
  --predictions_dir logs/<new_timestamp>/predictions
```

### Step 5: 合并所有 drift metrics（可选）

```bash
# 创建合并目录
mkdir -p logs/all_drift_metrics

# 复制所有 drift metrics
cp logs/2025-10-29-02-22-26/drift_metrics/*.json logs/all_drift_metrics/
cp logs/2025-10-29-08-45-10/drift_metrics/*.json logs/all_drift_metrics/
cp logs/<new_timestamp>/drift_metrics/*.json logs/all_drift_metrics/

# 统计质量分布
python -c "
import json
from pathlib import Path

metrics_dir = Path('logs/all_drift_metrics')
high, med, low = 0, 0, 0

for f in metrics_dir.glob('*.json'):
    data = json.loads(f.read_text())
    quality = data.get('drift_metrics', {}).get('quality_label', 'UNKNOWN')
    if quality == 'HIGH': high += 1
    elif quality == 'MEDIUM': med += 1
    elif quality == 'LOW': low += 1

total = high + med + low
print(f'Total: {total}')
print(f'HIGH: {high} ({high/total*100:.1f}%)')
print(f'MEDIUM: {med} ({med/total*100:.1f}%)')
print(f'LOW: {low} ({low/total*100:.1f}%)')
"
```

---

## 🎨 分批处理策略（避免长时间运行）

如果不想一次性跑 500 个任务，可以分批处理：

### 策略 1: 按 100 个任务分批

```bash
# Batch 1: 0-99
python batch_generate_predictions.py --start 0 --end 100 --base_dir logs/batch_0_99
python compute_drift_from_predictions.py --predictions_dir logs/batch_0_99/predictions

# Batch 2: 100-199
python batch_generate_predictions.py --start 100 --end 200 --base_dir logs/batch_100_199
python compute_drift_from_predictions.py --predictions_dir logs/batch_100_199/predictions

# ...继续
```

### 策略 2: 按难度分批

```bash
# Part A (简单任务, 15 min - 1 hour)
python batch_generate_predictions.py --start 0 --end 200 --base_dir logs/part_a

# Part B (中等任务, 1-4 hours)
python batch_generate_predictions.py --start 200 --end 400 --base_dir logs/part_b

# Part C (困难任务, > 4 hours)
python batch_generate_predictions.py --start 400 --end 500 --base_dir logs/part_c
```

---

## 📈 质量分析

### 查看单个任务的详细 drift metrics

```bash
cat logs/batch_500/drift_metrics/input_data_0_drift.json | python -m json.tool
```

### 提取所有 HIGH quality 任务

```bash
python -c "
import json
from pathlib import Path

metrics_dir = Path('logs/batch_500/drift_metrics')
high_quality = []

for f in sorted(metrics_dir.glob('input_data_*_drift.json')):
    data = json.loads(f.read_text())
    if data.get('drift_metrics', {}).get('quality_label') == 'HIGH':
        high_quality.append({
            'task_id': data['task_id'],
            'task_index': data['task_index'],
            'drift_rate': data['drift_metrics']['drift_rate'],
        })

print(f'Found {len(high_quality)} HIGH quality solutions:')
for item in high_quality[:10]:  # 显示前 10 个
    print(f\"  [{item['task_index']:3d}] {item['task_id']:40s} drift={item['drift_rate']:.3f}\")
"
```

### 分析 drift 分布

```bash
python -c "
import json
from pathlib import Path
import statistics

metrics_dir = Path('logs/batch_500/drift_metrics')
drift_rates = []

for f in metrics_dir.glob('input_data_*_drift.json'):
    data = json.loads(f.read_text())
    rate = data.get('drift_metrics', {}).get('drift_rate')
    if rate is not None:
        drift_rates.append(rate)

print(f'Total: {len(drift_rates)} tasks')
print(f'Mean drift: {statistics.mean(drift_rates):.3f}')
print(f'Median drift: {statistics.median(drift_rates):.3f}')
print(f'Min drift: {min(drift_rates):.3f}')
print(f'Max drift: {max(drift_rates):.3f}')
"
```

---

## 🚀 下一步：Q2 Pattern Extraction

当你有了足够的 HIGH quality drift metrics 后（推荐 >= 200 个），就可以进行 Q2 pattern extraction：

```bash
python extract_patterns_from_drift_metrics.py \
  --drift_dir logs/batch_500/drift_metrics \
  --min_quality HIGH \
  --output_dir logs/patterns
```

这将从高质量解决方案中提取可复用的 patterns，用于未来任务的求解。

---

## ⚙️ 高级选项

### Full-file Mode vs Normal Mode

**Full-file mode** (推荐):
```bash
python batch_generate_predictions.py --full_file_mode true
```
- ✅ 更稳定，避免 "Hunk FAILED"
- ❌ 较慢，token 消耗较多

**Normal mode** (默认):
```bash
python batch_generate_predictions.py --full_file_mode false
```
- ✅ 较快，token 消耗较少
- ❌ 可能有补丁应用失败

### 使用 Gold Patch（验证流程）

```bash
# 用 gold patch 验证整个流程
python batch_generate_predictions.py \
  --start 0 \
  --end 10 \
  --use_gold true \
  --base_dir logs/gold_test

python compute_drift_from_predictions.py \
  --predictions_dir logs/gold_test/predictions
```

预期: 所有任务都是 HIGH quality (drift_rate ≈ 0.0)

---

## 🔧 故障排查

### 问题 1: 部分任务失败

**查看失败原因**:
```bash
# 检查 logs 输出，找到失败的 task_index
# 然后单独重试
python generate_predictions.py --task_index 123 --full_file_mode true
```

### 问题 2: LLM API 超时

**解决方案**: 分小批处理
```bash
# 每次只处理 10 个任务
for i in {0..49}; do
  start=$((i * 10))
  end=$((start + 10))
  python batch_generate_predictions.py \
    --start $start \
    --end $end \
    --base_dir logs/batch_${start}_${end}
done
```

### 问题 3: 磁盘空间不足

**预计空间需求**:
- 500 个 predictions: ~50 MB
- 500 个 drift metrics: ~20 MB
- Git repo mirrors: ~2-5 GB

**清理缓存**:
```bash
# 清理 repo 镜像缓存（谨慎！）
rm -rf ~/.cache/swebench_repos

# 清理临时工作树
rm -rf /tmp/swebench_work
```

---

## 📁 最终目录结构

```
logs/
└── <timestamp>/
    ├── predictions/
    │   ├── input_data_0/
    │   │   └── astropy__astropy-12907/
    │   │       └── predictions.jsonl
    │   ├── input_data_1/
    │   │   └── django__django-12856/
    │   │       └── predictions.jsonl
    │   └── ...
    └── drift_metrics/
        ├── input_data_0_drift.json
        ├── input_data_1_drift.json
        └── ...
```

**关键文件**:
- `predictions.jsonl`: SWE-bench evaluator 格式
- `*_drift.json`: Q1 drift metrics + Q2 quality labels

---

## ✅ 成功标准

1. ✅ **Coverage**: >= 450/500 任务成功生成预测 (90%+)
2. ✅ **Quality**: >= 200 个 HIGH quality 解决方案 (40%+)
3. ✅ **Format**: 所有 drift metrics JSON 格式正确
4. ✅ **Ready for Q2**: 有足够的 HIGH quality patterns 用于提取

**达到以上标准后，就可以进入 Q2 Pattern Extraction 阶段！** 🎉
