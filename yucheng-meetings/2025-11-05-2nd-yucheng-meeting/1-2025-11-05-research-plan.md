# Q1 Research Plan: Context Drift Detection & Intervention
**Jeremy Gu | For Discussion with Yucheng | November 5, 2025**

---

## Research Question

**Does detecting and intervening on context drift improve coding agent performance?**

Specifically: Can we increase **Resolution Rate** by detecting when agents drift from their goals and intervening early?

---

## Overall Approach (4 Phases)

### Phase 1: Define Context Drift (Week 1-2)
**Goal**: Establish formal definition and detection metrics

**Deliverables**:
- Drift definition across 3 dimensions (Scope, Tool, Loop)
- Detection algorithms (BV score, EPR, Trajectory EM)
- Thresholds calibrated from literature

**Status**: Framework drafted, awaiting your feedback

---

### Phase 2: Analyze Existing Data (Week 2-3)
**Goal**: Validate drift-performance correlation using public trajectories

**Method**:
```
1. Collect public trajectories (GPT-4, Claude, AutoCodeRover runs)
2. Annotate with drift detection algorithm
3. Analyze: High drift tasks vs Low drift tasks
   → Hypothesis: High drift → Lower resolution rate
```

**Cost**: $0 (no new runs, pure analysis)

**Deliverable**: Evidence that drift predicts failure

---

### Phase 3: Controlled Experiment (Week 3-5) ⭐ CORE
**Goal**: Prove drift intervention improves performance

**Experimental Design**:

| Group | Setup | Tasks | Cost |
|-------|-------|-------|------|
| **Control** | Your LLM + No drift detection | N tasks | $X |
| **Treatment** | Your LLM + Drift detection + Intervention | N tasks | $X |

**Intervention mechanism**:
- When drift detected (score > threshold) → Issue warning/rollback
- Agent adjusts behavior before task fails

**Sample size options**:
- **Minimum**: N=50 per group (100 runs total) → $200-500
- **Recommended**: N=100 per group (200 runs total) → $400-1000
- **Full**: N=500 per group (1000 runs total) → $2000-5000

**Primary metric**: Resolution Rate improvement
- Example: Control 30% → Treatment 40% = +10% absolute gain

**Statistical requirement**:
- N≥50 per group for 80% power to detect 10% improvement

---

### Phase 4 (Optional): Benchmark Comparison
**Goal**: Compare your method against published baselines

**Method**:
```
Run GPT-4 baseline (no drift) on same N tasks
Compare: Your Treatment vs GPT-4 baseline
```

**Cost**: Additional $X for N tasks

**Value**: Shows your method competitive with/better than SOTA

**Decision point**: Only do if Phase 3 shows significant improvement

---

## Key Design Decisions to Discuss

### 1. Sample Size
**Options**:
- **Conservative**: 50 per group (100 total) = $200-500
  - Pro: Affordable, fast turnaround (1 week)
  - Con: Lower statistical power

- **Standard**: 100 per group (200 total) = $400-1000
  - Pro: Adequate power, publishable
  - Con: Moderate cost

- **Comprehensive**: 500 per group (1000 total) = $2000-5000
  - Pro: High confidence, full benchmark coverage
  - Con: Expensive, time-consuming

**My recommendation**: Start with 100, expand if promising

---

### 2. Which LLM to Use?
**Options**:
- **Your own model** (e.g., Claude Sonnet via Bedrock)
- **GPT-4** (for direct comparison with baselines)
- **Both** (most rigorous but doubles cost)

**My recommendation**: Your model for main experiment, GPT-4 optional

---

### 3. Intervention Strategy
**Options**:
- **Warn only**: Alert agent but don't force action
- **Soft rollback**: Suggest agent revert last action
- **Hard rollback**: Automatically revert when drift > threshold

**My recommendation**: Start with soft rollback (warn + suggest)

---

### 4. Dataset Split
**How to ensure fair comparison?**

**Option A - Randomized**:
```
500 tasks → Randomly split → 250 control, 250 treatment
```
Pro: Standard experimental design
Con: Different task difficulty between groups

**Option B - Paired**:
```
Same 250 tasks → Run twice (control + treatment)
```
Pro: Perfect matching, higher statistical power
Con: Doubles the runs (500 total for 250 tasks)

**My recommendation**: Option A with stratified sampling by difficulty

---

## Resource Requirements

### Compute/API Costs

| Scenario | Runs | Estimated Cost | Timeline |
|----------|------|----------------|----------|
| **Pilot** | 100 (50+50) | $200-500 | 1 week |
| **Standard** | 200 (100+100) | $400-1000 | 2 weeks |
| **Full** | 1000 (500+500) | $2000-5000 | 3-4 weeks |

### What Reduces Cost?
1. ✅ Using public trajectories for Phase 2 (saves full re-run)
2. ✅ Smaller pilot first (validate before scaling)
3. ✅ Efficient LLM (e.g., Sonnet vs Opus)
4. ✅ Action limits (max 100 steps per task)

### What Increases Cost?
1. ❌ Running external baselines (GPT-4, etc.)
2. ❌ Multiple intervention strategies (need separate groups)
3. ❌ Cross-benchmark validation (SWE-bench + τ-bench + WebArena)

---

## Timeline (6 weeks total)

```
Week 1-2: Phase 1 (Drift Definition) + Start Phase 2
  ├─ Finalize drift framework
  ├─ Collect public trajectories
  └─ Manual annotation of 10-20 samples

Week 3: Phase 2 Completion + Phase 3 Pilot
  ├─ Analyze existing trajectories (drift-performance correlation)
  ├─ Run pilot experiment (50+50 tasks)
  └─ Go/No-Go decision based on pilot results

Week 4-5: Phase 3 Full Experiment (if pilot successful)
  ├─ Run full experiment (100+100 or 500+500)
  ├─ Statistical analysis
  └─ Optional: Phase 4 baseline comparison

Week 6: Paper + Demo
  ├─ Write-up results
  ├─ Prepare presentation
  └─ Submit deliverables
```

---

## Success Criteria

### Minimum Viable Success (Week 3)
- ✅ Drift definition formalized
- ✅ Pilot shows Treatment > Control (any improvement, p<0.1)
- ✅ Drift detection works (accuracy >70% vs manual annotation)

### Strong Success (Week 5)
- ✅ Treatment significantly better than Control (p<0.05)
- ✅ Absolute improvement ≥5% resolution rate
- ✅ Results hold across task difficulty levels

### Exceptional Success (Week 6)
- ✅ Improvement ≥10% resolution rate
- ✅ Generalizes across 2+ benchmarks
- ✅ Competitive with/beats published baselines

---

## Questions for Yucheng

### 1. Scope & Ambition
- **Q**: Is Q1-only (drift detection) sufficient, or should I attempt lightweight Q2 (pattern learning)?
- **My take**: Focus on Q1 to do it well

### 2. Sample Size & Budget
- **Q**: What sample size do you recommend for a strong project?
  - 50 per group (conservative)?
  - 100 per group (standard)?
  - 500 per group (comprehensive)?
- **My take**: Start with 100, expand if pilot works

### 3. Experiment Design
- **Q**: Should I do paired comparison (same tasks, run twice) or randomized split?
- **My take**: Randomized with stratified sampling

### 4. Benchmark Coverage
- **Q**: Focus on SWE-bench only, or also run on τ-bench/WebArena?
- **My take**: SWE-bench primary, others if time/budget allows

### 5. Baseline Comparison
- **Q**: Must I compare against GPT-4/external baselines, or is control vs treatment sufficient?
- **My take**: Control vs treatment is sufficient; external baselines optional

### 6. Public Trajectories
- **Q**: Do you know where to find SWE-bench/τ-bench public trajectories?
- **Q**: Any CS224V shared resources (pre-run data, AWS credits)?

---

## My Recommendations (Summary)

### Recommended Plan
1. **Phase 1-2**: Drift definition + Analyze existing data (Week 1-3)
   - Cost: $0
   - Validates drift-failure correlation

2. **Phase 3 Pilot**: 50+50 tasks experiment (Week 3)
   - Cost: $200-500
   - Go/No-Go decision point

3. **Phase 3 Full**: 100+100 tasks experiment (Week 4-5)
   - Cost: $400-1000
   - Publishable results

4. **Phase 4**: Optional baseline comparison (Week 5)
   - Cost: $200-500
   - Only if Phase 3 successful

**Total estimated cost**: $600-2000 (depending on what you run)
**Total runs**: 100-400

### Why This Plan?
- ✅ **Affordable**: Fits typical student research budget
- ✅ **Rigorous**: Adequate statistical power (N=100 per group)
- ✅ **Safe**: Pilot first, scale only if promising
- ✅ **Focused**: One clear research question (Q1 only)
- ✅ **Publishable**: Controlled experiment + significance testing

---

## Risk Mitigation

**Risk 1**: Pilot shows no improvement
- **Plan B**: Analyze why (detection accuracy? intervention strategy? task selection?)
- **Plan C**: Pivot to "Drift as diagnostic tool" (predict failure, not prevent it)

**Risk 2**: Budget insufficient
- **Plan B**: Reduce to 50+50 full experiment (still publishable with caveats)
- **Plan C**: Partner with another student to share costs

**Risk 3**: No public trajectories found
- **Plan B**: Skip Phase 2 correlation analysis, go straight to experiment
- **Impact**: Weaker motivation but core contribution remains

---

## Discussion Outline (5 min presentation)

1. **Problem** (30s): Agents drift from goals, causing failures
2. **Solution** (30s): Detect drift + intervene → improve resolution rate
3. **Method** (1 min): 3-dimensional drift detection + controlled experiment
4. **Design** (2 min): Control vs Treatment, sample size options, cost/timeline
5. **Questions** (1 min): Scope, sample size, benchmarks, baselines, data sources

---

**Bottom line**: I need to run **100-200 experiments** (control + treatment) at a cost of **$400-1000** to prove drift intervention improves coding agent performance. This is feasible within the course timeline and produces publishable results.
