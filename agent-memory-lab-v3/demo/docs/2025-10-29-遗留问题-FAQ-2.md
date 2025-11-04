# FAQ-2 · Drift-aware Agent（Q1/Q2/Q3）速查

**Date:** 2025-10-29

本页归档我们对 SWE-bench Verified、Q1/Q2 设计、drift 评分与评测环境的共识。面向“可直接贴进计划/README”的简洁要点。

---

## 0) 术语速览
- **gold patch**：SWE-bench/Verified 提供的官方修复补丁（ground truth），用于复现实验与评测对齐，不应作为 Agent 的输入。
- **agent patch**：LLM/Agent 生成的补丁（我们要评分/评测的对象）。
- **drift_online**：线上（运行时）四守卫加权分（Scope/Plan/Test/Evidence），∈[0,1]。
- **drift_offline**：事后（仅最终补丁/日志）计算的 drift。最小形态可用 **Scope-only**，建议 `drift_offline := score_scope`（∈[0,1]）。
- **resolved**：官方 evaluator（Docker）判定 FAIL_TO_PASS 通过且不破坏 PASS_TO_PASS。

---

## 1) Verified 里的 patch 是什么？
- 是**金标准修复**（gold patch）。在 `base_commit` 上应用并运行测试应通过（FAIL_TO_PASS）且不破坏 PASS_TO_PASS。
- 数据项还常包含：`problem_statement`、`FAIL_TO_PASS`/`PASS_TO_PASS`、有时有 `test_patch`、`difficulty`、`hints_text` 等。
- **用途**：对齐/复现；**不作为 Agent 输入**，也不作为被评分对象。

---

## 2) 我们的 A/B 对比在哪里？
- **Baseline（A）**：不开 Q1（非漂移感知）。
- **Q1（B）**：开启四守卫评分（advisory）。可选 Feature Flag：**二次 LLM 修补**（用 drift/WARN/ROLLBACK 触发二次调用）。
- **后续（B’）**：引入 Q2 的 pattern 检索/排序，再与 A/B 对比。
- **指标**：`resolved`、平均动作数/LLM 调用、平均 drift、patch 长度等。

---

## 3) “第一步打分”打给谁？gold 的 drift 会不会很低？
- **线上打分**：打给 **Agent 当次解的行为与产物**（动作级）。
- **事后打分**：打给 **agent patch**（与 gold 做 scope 对齐）；**gold-only** 时 **不计算 drift（N/A）**。
- 若仅有 gold patch 用于自检，最多证明流程与 evaluator 打通，不代表 Agent 性能。

---

## 4) drift score 的输入到底是什么？
- **Scope**：来自 *agent patch*（`files_modified[]`、`num_files_modified`、可选 `patch_length`、`scope_limit`）。
- **Plan**：来自 *Agent 轨迹*（阶段序列、越级/跳步/返工计数）。
- **Test**：
  - 触达：是否运行相关 FAIL_TO_PASS（命令/日志）。
  - 通过：真实测试结果（官方 evaluator 或运行报告）。
- **Evidence**：是否引用 stacktrace、失败用例 ID、复现命令/最小复现实验（来自 Agent 输出/日志）。
> 规则：各子分先 **clamp 到 [0,1]**，再加权；仅 Scope 时建议 `drift_offline := score_scope`，**不要再乘 0.4** 以免阈值失真。

---

## 5) 四个守卫是否都必要？
- 是。四维度分别约束：**改到点（Scope）／流程稳定（Plan）／验证到位（Test）／证据支撑（Evidence）**；缺一会漏判。
- MVP（Q1-lite）：先上 **Scope+Test（通过）**；随后补 **Plan/Evidence**（需轨迹/日志）。

---

## 6) Verified 是否足以支撑四守卫的数据？
- **Scope**：✅（用 agent patch；gold 用于对齐与 P/R）。
- **Test**：✅ 通过**实际跑测**得到（建议官方 evaluator + Docker）。
- **Plan / Evidence**：❌ 原始数据无。需在 Agent 运行期**记录轨迹/日志**。

---

## 7) 只有 LLM 生成的 patch 时能评估什么？
- 可完整做 **Scope**（与 gold 对齐的 P/R、extra/missed、`score_scope` → `drift_offline`）。
- 若能跑测：可拿到 **Test（通过）**；若保存命令/日志：可近似 **Test（触达）**。
- 无轨迹时 **Plan/Evidence=N/A**。

---

## 8) 是否需要搭环境（evaluator/Docker）？
- 做权威的 `resolved` 指标：**需要**官方 evaluator（**建议 Docker**，保证复现与隔离）。
- 仅计算 **Scope**：不必跑代码（可先离线闭环）。
- 推荐顺序：先事后管线（predictions → drift_offline + evaluator），再加线上轨迹用于实时干预与过程分析。

---

## 9) 线上 vs 事后：评分形态与用法

| 维度 | **线上（online）** | **事后（offline）** |
|---|---|---|
| 评分对象 | 行为与产物（动作级） | 最终补丁/运行结果/可选日志 |
| 可用守卫 | Scope / Plan / Test（触达+通过） / Evidence | 最小：Scope；若有日志可补 Test/Evidence；有 evaluator 可得“通过” |
| 产出 | `drift_online`，以及 ALLOW/WARN/ROLLBACK 信号 | `drift_offline`，`resolved`，scope P/R、extra/missed |
| 用途 | 实时干预、过程分析 | 质量标注、Q2 样本筛选、对外可比评估 |
| 是否必须 | 否（研究可先事后） | 是（用于 Q2 与评测） |

---

## 10) Gold-only 自检应如何记录？
- **drift = N/A**，**quality_label = N/A**，`mode: "gold_sanity"`。
- 仅报告：环境打通（evaluator/Docker OK）与 gold 可复现（resolved=1）。
- **严禁**将该模式的样本计入训练/性能统计。

---

## 11) 四守卫 · 数据来源（在线 vs 事后）与依赖

| 守卫 | 度量目标 | **在线：输入/来源** | **事后：输入/来源** | 需 evaluator? | 需 Docker? | 需 LLM/Agent 轨迹? | 备注 |
|---|---|---|---|---|---|---|---|
| **Scope** | 改到点上，避免无关/过多改动 | 实时 patch diff、`files_modified[]`、`num_files_modified`（Agent 日志） | **agent_patch** vs **gold_patch** 的文件集合；scope P/R、extra/missed | 否 | 否 | 在线：是；事后：否（仅需 patch） | `scope_limit` 可随难度配置 |
| **Plan** | 是否按“理解→复现→实现→验证”推进 | 阶段序列、越级/跳步/返工计数（Agent 轨迹） | **N/A**（无轨迹则无法重建；若保留完整日志可离线复原） | 否 | 否 | 是（无轨迹则 N/A） | 数据集不含，需要埋点 |
| **Test（触达）** | 是否运行到相关 FAIL_TO_PASS | 测试命令/目标匹配、执行片段（动作/命令日志） | 若保存了运行日志可离线判定；仅补丁时可做启发式映射（弱） | 否 | 否 | 是（需日志或近似） | 早期弱检查，触发二次修补 |
| **Test（通过）** | FAIL_TO_PASS 通过且不破坏 PASS_TO_PASS | 若在线跑测则用实时结果 | **官方 evaluator**（权威口径）或离线跑测报告 | **是** | **是（推荐）** | 在线：可无；事后：可无 | 统一以官方结果为准 |
| **Evidence** | 是否证据驱动（错误栈/失败用例/复现实验） | 是否引用 stacktrace、fail case id、repro cmd/最小复现（Agent 输出/日志） | **N/A**（仅补丁无法判定；若日志保存可离线提取） | 否 | 否 | 是（需 Agent 生成与引用） | 可先用启发式，后续用 LLM/静态分析增强 |

---

## 12) 实施建议（即刻可落地）
1. **先事后**：生成 `predictions.jsonl` → 算 `drift_offline := score_scope` → 跑官方 evaluator 得到 `resolved` → 以 `resolved=True ∧ drift_offline<0.2` 选 Q2 样本。  
2. **再上线**：为 Agent 加**轨迹与证据**埋点，开启 `drift_online` 与 ALLOW/WARN/ROLLBACK（可加“二次修补”开关）。  
3. **阈值一致性**：各子分 clamp 到 [0,1]；仅 Scope 模式用单维分或重标到 [0,1]；文档中区分 `drift_online` / `drift_offline` 的阈值口径。

---

*End of FAQ-2.*
