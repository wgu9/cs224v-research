# CS224V Project: Context Drift Detection Framework
**Meeting Prep | November 5, 2025 | Jeremy Gu**

---

## Project Timeline: What We've Done

### Week 5 (Oct 22): Project Initiation
- **Direction shift**: From terminology alignment → Agent Memory systems
- **Split decision**: Alberto (code-with-context) | Jeremy (adaptive memory for coding agents)
- **Initial scope**: Three research questions (Q1: Context Drift, Q2: Cross-Session Learning, Q3: Dynamic Abstraction)

### Week 6 (Oct 28-29): First Meeting with Yucheng → Strategic Pivot
**Key Decision: Q1-Only Focus**
- Treat **Context Drift Detection** as standalone, paper-worthy problem
- **Defer Q2/Q3** (cross-session learning, dynamic abstraction) to future work
- **Validation targets**: 3 benchmarks (SWE-bench Verified, τ-bench, WebArena)
- **Data strategy**: Use existing trajectories first (cost/time efficiency)
- **New dimension identified**: Repetitive Mistakes (especially salient in WebArena/τ-bench)

### Week 6 (Oct 30): Literature Survey Completed
- **30+ papers** surveyed across 3 tiers
- **Core findings**:
  - Loop Drift = PRIMARY bottleneck (AgentErrorBench)
  - Strong empirical baselines established (MAST 7.15%, ReCAPA EPR 0.082, MI9 99.81%)
  - Gap identified: No unified detection framework across Scope/Tool/Loop dimensions

### Week 6 (Nov 3): Framework Delivered
**Context Drift Detection Framework** submitted to Yucheng:

**Formal Definition**:
> Context Drift is the measurable deviation of an agent's behavioral trajectory from specified objectives, manifesting across three orthogonal dimensions (Scope, Tool, Loop) during single-task execution.

**Three-Dimensional Detection Framework**:

| Dimension | Core Metric | Threshold | Priority | Top Evidence |
|-----------|-------------|-----------|----------|--------------|
| **Scope Drift** (WHERE) | BV Score | > 0.3 | Medium | MI9: 99.81% detection |
| **Tool Drift** (HOW) | Trajectory EM | < 0.5 | Medium | τ-bench: pass^8 < 25% |
| **Loop Drift** (WHEN) | EPR₁₀ | > 0.15 | **HIGHEST** | ReCAPA: 73-82% improvement |

**Key Distinctions**:
- Goal Drift ⊂ Scope Drift (we focus on execution process, not just final goal)
- Error Propagation → Loop Drift (we focus on deviation patterns, not single errors)
- Hallucination ⊥ Context Drift (orthogonal: factual vs. behavioral drift)

### Week 7 (Nov 3-5): Infrastructure & Preparation
- ✅ Dockerized SWE-bench workflow (end-to-end validated on 1 case)
- ✅ Runner scaffold ready for 500 SWE-bench Verified tasks (AWS Bedrock + Claude Sonnet)
- ✅ Framework document completed

---

## Today's Discussion with Yucheng

### 1. Framework Validation
**Seeking feedback on**:
- Is the 3-dimensional definition (Scope/Tool/Loop) theoretically sound and sufficiently distinct from prior work?
- Are the proposed metrics (BV, Trajectory EM, EPR₁₀) appropriate for each dimension?
- Should we consider hierarchical relationships between dimensions, or maintain orthogonality?
- Loop Drift justification: Is "repetition = deviation from implicit 'make progress' goal" convincing?

### 2. Next Steps Clarification
**Week 1-2 plan (from Framework §3.1)**:
- Download existing SWE-bench trajectories (prefer public logs over re-running)
- Manual annotation: 3 representative tasks (success/failure/partial)
- Implement detection algorithms (priority: Loop → Scope → Tool)
- Validation on annotated trajectories

**Open questions**:
- Is 3 trajectories sufficient for initial validation, or expand to 10-20?
- Should we implement online (real-time) or offline (post-hoc) detection first?
- Which benchmark after SWE-bench: τ-bench or WebArena priority?

### 3. Practical Constraints
**Resource planning**:
- Where to find public SWE-bench/τ-bench/WebArena trajectories? (format/availability)
- Evaluator cost management: subset size strategy?
- Threshold calibration: how much validation data needed before full run?

**Metric operationalization**:
- For Loop Drift: EPR₁₀ vs. simple repetition count — which is more practical to implement?
- For Tool Drift: Do we need reference "optimal trajectories," or use self-consistency (pass^k)?
- For Scope Drift: How to define "authorized resource set" without ground truth?

### 4. Timeline Confirmation
**Proposed 6-week schedule**:
- **Week 1-2** (Nov 5-19): Manual annotation + detector implementation + validation
- **Week 3** (Nov 20-26): Small-scale eval (50 tasks) + threshold calibration
- **Week 4** (Nov 27-Dec 3): Cross-benchmark generalization (τ-bench/WebArena)
- **Week 5** (Dec 4-10): Full SWE-bench Verified run (500 tasks)
- **Week 6** (Dec 11-17): Paper draft + demo

**Questions**:
- Is this timeline realistic given manual annotation requirements?
- Should we parallelize benchmark exploration (SWE-bench + τ-bench simultaneously)?
- Any hard deadlines for course deliverables?

---

## Expected Deliverables (Week 2 checkpoint)
1. **Validation Report** (2 pages): Detection accuracy, confusion matrix, failure modes
2. **Case Study** (1 page): Detailed example with ground truth vs. detected drift
3. **Updated Detection Cards**: Refined thresholds, identified edge cases

---

## Open Questions for Discussion
- **Theoretical**: Is our distinction from Goal Drift/Error Propagation clear and convincing?
- **Methodological**: Level of implementation detail expected in framework?
- **Practical**: Should we focus on demonstrating detection feasibility first, or aim for intervention (rollback/warning) mechanisms?
- **Scope**: Is Q1-only sufficient for a strong course project, or should we consider a lightweight Q2 component (pattern extraction without reuse)?

---

**References**:
- [Notion: Context Drift Detection Framework](https://www.notion.so/Context-Drift-Detection-Framework-29c74e3ea00380d9aa83d5d070b754bb)
- [Notion: Literature Survey (30+ papers)](https://www.notion.so/2025-10-30-research-papers-29b74e3ea003807c8c81e993575de161)
- [Notion: Week 6 Summary](https://www.notion.so/2025-11-3-Week-Summary-2a274e3ea00380778afcdc36eb3a344c)
