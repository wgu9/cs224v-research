# Documentation Index

Q1 + Q2 系统的完整文档索引。

---

## 🚀 快速上手

### 新手入门（推荐顺序）

1. **[QUICKSTART.md](QUICKSTART.md)** - ⭐ 从这里开始！
   - Spot test 单个任务的完整流程
   - 验证 pipeline 是否正常工作
   - 预计时间: 2-3 分钟

2. **[BATCH_WORKFLOW.md](BATCH_WORKFLOW.md)** - 批量处理
   - 500 个任务的批量处理流程
   - 适合生产环境使用
   - 包含实际使用建议和故障排查

3. **[FAQ.md](FAQ.md)** - ⭐ 常见问题解答
   - 核心概念澄清（职责分离、metrics 关系）
   - ML ranker 训练数据方案对比
   - 包含错误示例和正确方案

---

## 📚 详细文档

### Q1 系统（Four-Guard Goal Alignment）

- **[Q1_COMPLETION_SUMMARY-v2.md](Q1_COMPLETION_SUMMARY-v2.md)** - ⭐ Q1 完成度总结
  - 所有已实现功能清单
  - 完成度：85% P0（核心系统完成）
  - 最终文件结构
  - 验收标准
  - 快速验证方法

- **[2025-10-28-1-Q1_END_TO_END_WORKFLOW.md](2025-10-28-1-Q1_END_TO_END_WORKFLOW.md)**
  - Q1 系统的完整技术规格
  - Four-Guard 设计细节
  - Drift 计算方法
  - 适合深入了解 Q1 原理

- **[2025-10-28-4-COMPLETION_SUMMARY.md](2025-10-28-4-COMPLETION_SUMMARY.md)** (deprecated)
  - v1 版本（已被 v2 替代）
  - 保留作为历史参考

### Q2 系统（Cross-Session Pattern Learning）

- **[2025-10-29-Q2_END_TO_END_WORKFLOW.md](2025-10-29-Q2_END_TO_END_WORKFLOW.md)**
  - Q2 系统的完整技术规格
  - Pattern extraction 方法
  - Two-stage retrieval 架构
  - Q1-Q2 集成说明

- **[2025-10-29-q2-README_codex.md](2025-10-29-q2-README_codex.md)**
  - Q2 系统概要（简洁版）

### 项目文档

- **[2025-10-28-2-README.md](2025-10-28-2-README.md)**
  - 项目整体 README
  - 包含 demo 使用说明

- **[2025-10-28-3-遗留问题-DEMO_SUMMARY-需要review.md](2025-10-28-3-遗留问题-DEMO_SUMMARY-需要review.md)**
  - 遗留问题和讨论点
  - 需要 review 的内容

---

## 🎯 按使用场景选择文档

### 场景 1: 我想快速验证系统是否工作

➡️ **[QUICKSTART.md](QUICKSTART.md)**
- 3 分钟跑通单个任务
- 验证输出格式正确

### 场景 2: 我想批量处理 500 个任务

➡️ **[BATCH_WORKFLOW.md](BATCH_WORKFLOW.md)**
- 完整的批量处理流程
- 包含你当前 408 个任务的处理建议

### 场景 3: 我想深入了解 Q1 的技术细节

➡️ **[2025-10-28-1-Q1_END_TO_END_WORKFLOW.md](2025-10-28-1-Q1_END_TO_END_WORKFLOW.md)**
- Four-Guard 设计原理
- Drift 计算公式
- 实现细节

### 场景 4: 我想了解 Q2 如何工作

➡️ **[2025-10-29-Q2_END_TO_END_WORKFLOW.md](2025-10-29-Q2_END_TO_END_WORKFLOW.md)**
- Pattern extraction 流程
- Retrieval 架构
- Q1-Q2 如何集成

### 场景 5: 我想知道项目完成了多少

➡️ **[Q1_COMPLETION_SUMMARY-v2.md](Q1_COMPLETION_SUMMARY-v2.md)**
- Q1 完成度: 85% P0
- 所有已实现功能
- 验收标准
- 快速验证方法

---

## 📊 文档结构

```
docs/
├── README.md (本文件)                         # 文档索引
│
├── 🚀 快速上手
│   ├── QUICKSTART.md                          # Spot test 快速验证
│   └── BATCH_WORKFLOW.md                      # 批量处理流程
│
├── 📘 Q1 技术文档
│   ├── Q1_COMPLETION_SUMMARY-v2.md            # Q1 完成度总结 (v2)
│   ├── 2025-10-28-1-Q1_END_TO_END_WORKFLOW.md # Q1 完整规格
│   └── 2025-10-28-4-COMPLETION_SUMMARY.md     # Q1 完成度 v1 (deprecated)
│
├── 📗 Q2 技术文档
│   ├── 2025-10-29-Q2_END_TO_END_WORKFLOW.md   # Q2 完整规格
│   ├── 2025-10-29-q2-README_codex.md          # Q2 概要
│   └── 2025-10-29-q2.md                       # Q2 早期草稿
│
└── 📋 项目文档
    ├── 2025-10-28-2-README.md                 # 项目 README
    └── 2025-10-28-3-遗留问题-DEMO_SUMMARY-需要review.md  # 待办事项
```

---

## 🔍 常见问题快速查找

### Q: 如何快速验证系统？
A: 查看 [QUICKSTART.md](QUICKSTART.md) - Spot test 部分

### Q: 如何批量处理 500 个任务？
A: 查看 [BATCH_WORKFLOW.md](BATCH_WORKFLOW.md) - 完整工作流程

### Q: 如何处理已有的 408 个预测？
A: 查看 [BATCH_WORKFLOW.md](BATCH_WORKFLOW.md) - "你的实际情况" 部分

### Q: Drift rate 是怎么计算的？
A: 查看 [2025-10-28-1-Q1_END_TO_END_WORKFLOW.md](2025-10-28-1-Q1_END_TO_END_WORKFLOW.md) - Step 4

### Q: Q2 如何从 Q1 中提取 patterns？
A: 查看 [2025-10-29-Q2_END_TO_END_WORKFLOW.md](2025-10-29-Q2_END_TO_END_WORKFLOW.md) - Step 2

### Q: Quality label (HIGH/MEDIUM/LOW) 是如何定义的？
A: 查看 [QUICKSTART.md](QUICKSTART.md) - "结果解读" 部分
- HIGH: drift_rate < 0.2
- MEDIUM: 0.2 <= drift_rate < 0.35
- LOW: drift_rate >= 0.35

---

## 📝 文档更新记录

| 日期 | 文档 | 更新内容 |
|------|------|---------|
| 2025-10-29 | Q1_COMPLETION_SUMMARY-v2.md | 简洁的 Q1 完成度总结（替代 v1） |
| 2025-10-29 | QUICKSTART.md | 整合 spot test 流程 |
| 2025-10-29 | BATCH_WORKFLOW.md | 整合批量处理流程 |
| 2025-10-29 | Q2_END_TO_END_WORKFLOW.md | 创建 Q2 完整规格 |
| 2025-10-28 | Q1_END_TO_END_WORKFLOW.md | 创建 Q1 完整规格 |
| 2025-10-28 | COMPLETION_SUMMARY.md | Q1 完成度总结 v1 (deprecated) |

---

## 🤝 贡献指南

### 添加新文档

1. 在 `docs/` 目录下创建新文件
2. 使用清晰的文件名（建议格式: `YYYY-MM-DD-主题.md`）
3. 更新本文档的索引

### 文档命名规范

- **快速上手**: `QUICKSTART.md`, `BATCH_WORKFLOW.md`
- **技术规格**: `YYYY-MM-DD-主题-WORKFLOW.md`
- **总结文档**: `YYYY-MM-DD-主题-SUMMARY.md`
- **README**: `YYYY-MM-DD-主题-README.md`

---

**从 [QUICKSTART.md](QUICKSTART.md) 开始你的旅程！** 🚀
