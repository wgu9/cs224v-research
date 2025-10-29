# Quick Start - Spot Test 端到端验证

一个任务的完整工作流程：从生成预测到计算 Q1 drift metrics。

---

## 🎯 目标

验证整个 pipeline 在单个任务上正常工作：
1. ✅ 生成 predictions.jsonl
2. ✅ 计算 Q1 drift metrics
3. ✅ 确认输出格式正确

**预计时间**: 2-3 分钟

---

## 🚀 一键运行（推荐）

### Option A: 使用 Gold Patch（最快，用于验证）

```bash
# Step 1: 生成预测
python generate_predictions.py --task_index 0 --use_gold true

# Step 2: 创建标准目录结构
mkdir -p logs/spot_test/predictions/input_data_0/astropy__astropy-12907
cp logs/predictions.jsonl logs/spot_test/predictions/input_data_0/astropy__astropy-12907/

# Step 3: 计算 drift metrics
python compute_drift_from_predictions.py \
  --predictions_dir logs/spot_test/predictions \
  --task_index 0

# Step 4: 查看结果
cat logs/spot_test/drift_metrics/input_data_0_drift.json | python -m json.tool
```

### Option B: 使用 LLM Agent（真实场景）

```bash
# 需要设置 AWS token
export AWS_BEARER_TOKEN_BEDROCK=your_token_here

# Step 1: 生成预测（使用 full-file mode 提高成功率）
python generate_predictions.py --task_index 0 --full_file_mode true

# Step 2-4: 同上
mkdir -p logs/spot_test/predictions/input_data_0/astropy__astropy-12907
cp logs/predictions.jsonl logs/spot_test/predictions/input_data_0/astropy__astropy-12907/

python compute_drift_from_predictions.py \
  --predictions_dir logs/spot_test/predictions \
  --task_index 0

cat logs/spot_test/drift_metrics/input_data_0_drift.json | python -m json.tool
```

---

## 📊 预期输出

### Step 1: 生成预测

```
================================================================================
Generating predictions.jsonl for SWE-bench Evaluator
================================================================================

✅ Task loaded: astropy__astropy-12907
   Repo: astropy/astropy
   Base commit: d16bfe05a744...
✅ Using GOLD patch from dataset (470 characters)
✅ Predictions saved to: logs/predictions.jsonl
```

**输出文件**: `logs/predictions.jsonl`
```json
{
  "instance_id": "astropy__astropy-12907",
  "model_patch": "diff --git a/astropy/modeling/separable.py ...",
  "model_name_or_path": "q1-monitored-agent"
}
```

### Step 3: 计算 Drift Metrics

```
================================================================================
🔍 SPOT TEST MODE: Processing task_index=0
================================================================================

✅   0 astropy__astropy-12907                   | Drift: 0.000 | Quality: HIGH

================================================================================
📊 DETAILED DRIFT METRICS
================================================================================
Task ID:           astropy__astropy-12907
Task Index:        0
Difficulty:        15 min - 1 hour
Repo:              astropy/astropy

Drift Metrics:
  Drift Rate:      0.000    ← 完美！
  Quality Label:   HIGH     ← Q2 ready
  Scope Precision: 1.000    ← 无多余文件
  Scope Recall:    1.000    ← 无遗漏文件
  Files Modified:  1
  File Limit:      3
  Scope Violation: 0.000

File Analysis:
  Agent files:  ['astropy/modeling/separable.py']
  Gold files:   ['astropy/modeling/separable.py']
  Extra files:  []
  Missed files: []

Output saved to: logs/spot_test/drift_metrics/input_data_0_drift.json
================================================================================
```

### Step 4: 查看 JSON 结果

```json
{
  "task_id": "astropy__astropy-12907",
  "task_index": 0,
  "difficulty": "15 min - 1 hour",
  "repo": "astropy/astropy",
  "drift_metrics": {
    "drift_rate": 0.0,
    "scope_precision": 1.0,
    "scope_recall": 1.0,
    "num_files_modified": 1,
    "scope_file_limit": 3,
    "scope_violation": 0.0,
    "quality_label": "HIGH",
    "extra_files": [],
    "missed_files": [],
    "gold_files": ["astropy/modeling/separable.py"],
    "agent_files": ["astropy/modeling/separable.py"]
  },
  "patch_length": 470
}
```

---

## ✅ 验证成功标准

1. ✅ `logs/predictions.jsonl` 存在且包含正确字段
2. ✅ `drift_metrics/input_data_0_drift.json` 存在
3. ✅ `quality_label` 为 HIGH/MEDIUM/LOW 之一
4. ✅ `drift_rate` 是 0.0-1.0 之间的数字
5. ✅ `agent_files` 和 `gold_files` 列表存在

**如果以上全部通过，说明 pipeline 工作正常！** 🎉

---

## 🔍 测试其他任务

### 按任务索引测试

```bash
# 测试第 5 个任务
python generate_predictions.py --task_index 5 --use_gold true

mkdir -p logs/spot_test/predictions/input_data_5/<instance_id>
cp logs/predictions.jsonl logs/spot_test/predictions/input_data_5/<instance_id>/

python compute_drift_from_predictions.py \
  --predictions_dir logs/spot_test/predictions \
  --task_index 5
```

### 按 instance_id 测试

```bash
python compute_drift_from_predictions.py \
  --predictions_dir logs/spot_test/predictions \
  --instance_id astropy__astropy-12907
```

---

## 📈 结果解读

| 指标 | 含义 | 好的值 |
|------|------|--------|
| `drift_rate` | 总体 drift 程度 | < 0.2 (HIGH quality) |
| `quality_label` | 质量分类 | HIGH |
| `scope_precision` | 是否修改了额外文件 | 1.0 (完美) |
| `scope_recall` | 是否遗漏了应改文件 | 1.0 (完美) |
| `scope_violation` | Scope guard 违规程度 | 0.0 (无违规) |
| `extra_files` | 多余修改的文件 | [] (空) |
| `missed_files` | 遗漏的文件 | [] (空) |

---

## 🔧 故障排查

### 问题 1: "predictions.jsonl not found"

**原因**: 目录结构不正确

**解决方案**: 确保目录结构为 `predictions/input_data_{idx}/{instance_id}/predictions.jsonl`

### 问题 2: "Invalid patch format"

**原因**: Patch 不是合法的 unified diff

**解决方案**: 使用 `--full_file_mode true` 提高成功率

### 问题 3: "AWS_BEARER_TOKEN_BEDROCK not found"

**原因**: 使用 LLM agent 但没有设置 token

**解决方案**:
- 设置环境变量: `export AWS_BEARER_TOKEN_BEDROCK=...`
- 或使用 gold patch: `--use_gold true`

---

## 📚 下一步

**Spot test 成功后**，查看 `BATCH_WORKFLOW.md` 了解如何批量处理 500 个任务。

**关键命令**:
```bash
# 批量生成 500 个任务的预测
python batch_generate_predictions.py --start 0 --end 500

# 批量计算所有 drift metrics
python compute_drift_from_predictions.py \
  --predictions_dir logs/<timestamp>/predictions
```
