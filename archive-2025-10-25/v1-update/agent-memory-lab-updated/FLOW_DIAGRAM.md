# Agent Memory Lab 端到端流程图

```
原始数据输入
├── goal.json (任务目标)
├── patch.diff (代码变更)
├── term.log (终端日志)
└── cursor.md (编辑器记录)

    ↓
    
Step 1: patch2events.py
├── 解析 patch.diff
├── 识别修改的文件 (README.md, requirements.txt)
└── 生成 edit 事件
    ↓
    
Step 2: term2events.py  
├── 解析 term.log
├── 识别 pytest 命令
└── 生成 shell 事件
    ↓
    
events.jsonl (完整事件序列)
├── Step 1: edit README.md (modify phase)
├── Step 2: edit requirements.txt (modify phase) 
├── Step 3: pytest -k doc_lang_check (test phase)
├── Step 4: pytest -k whitelist_diff_check (test phase)
└── Step 5: pytest (regress phase)

    ↓
    
Step 3: events2guards.py
├── Scope Guard: 检查文件路径是否允许
├── Plan Guard: 检查是否违反计划
├── Test Guard: 检查是否执行必要测试
├── Evidence Guard: 检查证据充分性
└── 计算综合 Drift Score

guards.jsonl (守卫结果)
├── Step 1: README.md ✅ (drift_score: 0.05)
├── Step 2: requirements.txt ⚠️ (drift_score: 0.75) 
├── Step 3: pytest ✅ (drift_score: 0.0)
├── Step 4: pytest ✅ (drift_score: 0.0)
└── Step 5: pytest ✅ (drift_score: 0.0)

    ↓
    
Step 4: extract_and_save
├── 分析事件序列
├── 识别模式特征
└── 生成模式卡

pattern.pc_doc_only_change.json
├── triggers: ["documentation-only", "translate readme"]
├── steps: ["whitelist README.md/docs/**", "forbid requirements.*"]
├── invariants: ["only whitelisted files changed", "language==target"]
├── anti_patterns: ["edit requirements without consent"]
└── eval_examples: ["doc_lang_check", "whitelist_diff_check"]

    ↓
    
Step 5: 复制到全局库
└── data/patterns/pc_doc_only_change.json

    ↓
    
Step 6: retrieve (模拟新任务)
├── 输入: "Translate README; documentation-only; avoid dependency changes"
├── 匹配模式库
└── 返回: pc_doc_only_change (score: 1.0)

    ↓
    
Step 7: choose_view + render
├── 读取用户配置文件 (jeremy.json)
├── 选择视图类型 (terse)
└── 生成视图内容

view_preview.md
└── "Whitelist-only edits; forbid deps change; ensure checks."
```

## 关键发现

### 🚨 漂移检测成功
- **Step 2**: 修改 `requirements.txt` 违反了 `forbidden_paths` 约束
- **触发警告**: drift_score = 0.75 (阈值: 0.5)
- **原因**: scope_guard = 1.0, plan_guard = 1.0

### 📚 模式学习成功  
- **识别模式**: "文档翻译"模式
- **提取知识**: whitelist 策略、测试要求、反模式
- **可重用性**: 下次遇到类似任务可直接应用

### 🎯 智能检索成功
- **任务匹配**: "Translate README" → "pc_doc_only_change"
- **完美匹配**: score = 1.0
- **即时指导**: 提供具体操作建议

## 系统价值

1. **实时监控**: 开发过程中即时发现偏离目标的行为
2. **经验积累**: 从每次运行中学习最佳实践
3. **智能复用**: 为新任务提供基于经验的指导
4. **个性化**: 根据用户水平调整信息详细程度

这正是 Q1/Q2/Q3 三个核心能力的完美体现！
