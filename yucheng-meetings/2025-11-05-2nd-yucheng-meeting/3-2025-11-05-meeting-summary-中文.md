# Meeting Summary: Context Drift Detection
**Date**: November 5, 2025 | **Attendees**: Jeremy, Yucheng

---

## 🎯 核心转变：研究方法调整

### ❌ 旧方法（被否决）
- Rule-based detection (硬编码规则)
- 直接分析raw trajectory内容
- Dataset-specific approach

### ✅ 新方法（Yucheng要求）
- **Intent-based detection** (意图驱动)
- 提取高层goal，分析intent序列
- Generic framework (跨domain通用)

**原因**：规则太ad-hoc，不通用；直接分析raw content太复杂

---

## 📋 核心方法：Intent-Action Mapping

### Yucheng的要求
对每个action提取**intent/goal**，建立映射表：

| Action (What) | Intent (Why) | Result | Drift? |
|---------------|--------------|--------|--------|
| `view(symbol.py)` | Understand code | Success | None |
| `edit(symbol.py)` | Fix bug | Success | None |
| `view(auth.py)` | ??? | Success | **Scope Drift** ✓ |
| `edit(symbol.py)` | Fix bug (again) | Failed | **Loop Drift** ✓ |

### 为什么有效？
- **Loop Drift**: Same intent + repeated failure
- **Scope Drift**: Intent不明确 or 超出task goal
- **比raw content容易分析**：不需要读几千行代码

---

## 🔑 关键观点

### 1. Drift定义 = Paper的主贡献
> "Clearly defining context drift is already a research contribution, could take a large chunk in your paper."

**含义**：
- 不要小看taxonomy的价值
- 要做得rigorous（严谨）
- 需要empirical evidence + 文献支持

---

### 2. 当前3个drift类型不够
**Yucheng指出缺失**：
- ❌ Repetition (无意识重复，不是loop)
- ❌ Plan deviation (偏离既定计划)

**要求**：
- ✅ 持续调研文献补充类型
- ✅ 从empirical data derive新类型
- ✅ 记录supporting papers用于citation

---

### 3. 检测算法要Generic
> "Don't do rule-based. Be more generic so this can be applied to any domain."

**原则**：
- Model-agnostic (不依赖特定LLM)
- Domain-agnostic (SWE/τ-bench/WebArena通用)
- 既能检测也能预防 (detection = prevention)

---

### 4. 实证驱动 > 文献综述
> "Derive the issue from existing trajectory... conduct empirical study."

**不是做survey paper**，而是：
1. 从真实trajectories观察drift patterns
2. 用文献支持你发现的patterns
3. Propose rigorous taxonomy
4. 开发detection algorithm

---

## ✅ To-Do List (Due: Nov 12)

### Priority 1: 手动标注Trajectories
**任务**：
- [ ] 选2-3个trajectories (优先选弱模型的，错误多)
- [ ] 对每个action手动标注：
  - Intent/goal是什么？
  - 成功/失败？
  - 如果失败，为什么？
  - 是否drift？哪种类型？

**Example标注格式**：
```
Task: Fix sympy symbols() bug

Step 3: view(/testbed/sympy/core/symbol.py)
  Intent: Understand implementation
  Result: Success
  Drift: None

Step 15: view(/testbed/sympy/auth/permissions.py)
  Intent: ??? (unclear, unrelated to task)
  Result: Success
  Drift: Scope Drift (out of scope)

Step 16: edit(/testbed/sympy/core/symbol.py)
  Intent: Fix bug
  Result: Failed (same error as before)
  Drift: Loop Drift (repeated failure)
```

---

### Priority 2: 制作Intent-Action Table
**要求**：
- [ ] 左边：Raw trajectory content
- [ ] 右边：Intent + Drift detection
- [ ] 展示1个完整例子给Yucheng

**Table格式**：

| Step | Action | Intent/Goal | Result | Drift Detected |
|------|--------|-------------|--------|----------------|
| 1 | `grep "bug" /testbed/` | Locate error | Success | None |
| 2 | `view(payment.py)` | Understand bug | Success | None |
| ... | ... | ... | ... | ... |
| 12 | `view(auth.py)` | ??? | Success | Scope Drift ✓ |
| 13 | `edit(payment.py)` | Fix bug | Failed | Loop Drift ✓ |

**Summary for each trajectory**:
- Total actions: X
- Drift instances: Y (breakdown by type)
- Final result: Resolved/Failed
- Drift score: Y/X

---

### Priority 3: 证明Feasibility
**问题**：
- [ ] 手动提取intent是否可行？
- [ ] 从intent能否清晰识别drift？
- [ ] 哪些drift类型最常见？

**准备讨论**：
- 展示你的分析思路
- 说明哪些容易/困难
- 提出自动化方案设想

---

## 🚫 明确不做的

1. ❌ **不等drift定义完美** - 用现有3个开始，迭代改进
2. ❌ **不用硬编码规则** - 要generic，可用LLM辅助
3. ❌ **不直接喂full trajectory给LLM** - 太长，先提取intent
4. ❌ **不写paper** - 现在focus方法开发
5. ❌ **不做大规模实验** - 先手动验证可行性

---

## 💡 重要结论

### Research Pipeline明确

```
Week 1-2 (现在):
  手动分析 → 设计intent extraction → 证明feasibility

Week 2-3:
  LLM自动提取intent → 在10-20个trajectories测试

Week 3-4:
  完整detection算法 → Pilot实验(50+50)

Week 4-5:
  Full实验(100+100) → 统计分析

Week 6:
  Paper + Demo
```

---

### 方法论升级

| 维度 | 旧方法 | 新方法 |
|-----|--------|--------|
| **检测方式** | Rule-based | Intent-based |
| **分析单位** | Raw action content | High-level intent |
| **通用性** | Dataset-specific | Domain-agnostic |
| **理论基础** | 文献综述 | Empirical + 文献 |
| **贡献定位** | 实验改进 | Taxonomy + Detection |

---

### Paper贡献重新定位

**主贡献**：
1. Rigorous context drift taxonomy (empirical-driven)
2. Generic intent-based detection framework
3. Evidence that drift intervention improves performance

**篇幅分配**：
- 40%: Drift definition & taxonomy (大头)
- 30%: Detection method
- 30%: Experimental validation

---

## 📅 Timeline Adjustment

### This week (Nov 5-12): Manual Analysis ← WE ARE HERE
- 手动标注2-3个trajectories
- 设计intent-action table
- 展示1个完整例子

### Next week (Nov 13-19): Automation
- LLM提取intent
- 测试10-20个trajectories
- 完善drift taxonomy

### Week 3-4 (Nov 20-Dec 3): Implementation
- 完整detection算法
- Pilot实验
- 评估准确率

### Week 5-6 (Dec 4-17): Scale & Write
- Full实验
- 统计分析
- Paper + Demo

---

## 🔄 Mindset Shift

**从**：快速做实验，看能否提升resolution rate
**到**：严谨定义问题，开发通用方法，再验证效果

**从**：规则驱动
**到**：数据+理论驱动

**从**：Dataset-specific tricks
**到**：Generic framework

---

## 💬 关键引用

### On rigor:
> "In a paper, clearly defining context drift is already a research contribution. We want to make this part more rigorous."

### On approach:
> "Don't do rule-based. Be more generic so this can be applied to any domain."

### On intent:
> "Intent is the reason why the agent is taking this action. When we analyze, we only look at those short labels instead of raw trajectory."

### On timeline:
> "You don't need to wait until you have a good definition to start experiments. Start with current three."

### On focus:
> "We can leave paper here and review later. Right now, focus on the method."

---

## 🎯 Success Criteria (Next Meeting)

**必须展示**：
1. ✅ 2-3个trajectories的完整intent标注
2. ✅ Side-by-side table (action | intent | drift)
3. ✅ 至少识别出5+个drift实例

**准备讨论**：
- 标注过程的challenges
- 哪些drift类型最明显/最难识别
- 自动化方案初步设想

---

**Bottom line**: 从手动分析开始，证明intent-based方法可行，再考虑自动化和大规模实验。这周focus在理解真实trajectories的drift patterns。
