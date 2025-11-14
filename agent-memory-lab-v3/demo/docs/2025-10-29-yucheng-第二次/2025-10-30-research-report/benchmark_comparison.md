# Benchmark Comparison: SWE-bench, Tau Bench, Web Arena

**Date**: 2025-10-29
**Status**: To Be Written
**Goal**: Understand how Context Drift manifests in different benchmarks

---

## Overview

We need to generalize Context Drift detection to 3 benchmarks:
1. **SWE-bench** - Coding tasks (we have experience)
2. **Tau Bench** - API calling tasks (NEW)
3. **Web Arena** - Web navigation tasks (NEW)

---

## Benchmark 1: SWE-bench

### Basic Information
- **Focus**: Code generation and bug fixing
- **Task type**: GitHub issues → patches
- **Horizon**: Variable (5-50 steps typical)
- **Dataset size**: 500 verified tasks
- **Official site**: https://www.swebench.com/

### Task Example
```
Input:
- GitHub issue description
- Repository context
- Test cases

Output:
- Code patch (unified diff format)

Evaluation:
- FAIL_TO_PASS tests pass
- PASS_TO_PASS tests don't break
```

### How Drift Manifests

| Dimension | Manifestation in SWE-bench | Example |
|-----------|---------------------------|---------|
| **Wrong Scope** | Editing irrelevant files | Task: fix payment.py, Agent: edits database.py, config.py, utils.py |
| **Repetitive Mistakes** | Re-applying failed patches | Agent tries same patch 3 times without modification |
| **Not Following Plan** | Deviating from stated code plan | Plan: "modify validator", Action: modifies database instead |
| **Irrelevant Tool Use** | Using wrong commands | Using web search when should be reading code |
| **Lack of Evidence** | No reference to error trace | Makes changes without analyzing stack trace |
| **Test Coverage** | Not running relevant tests | Modifies code but doesn't run FAIL_TO_PASS tests |

### Trajectory Availability
- **Source**: https://github.com/SWE-bench/experiments
- **Location**: S3 buckets (`s3://swe-bench-experiments/verified/`)
- **Format**: JSON logs + trajectory files
- **Models available**: Claude, GPT-4, Deepseek, etc.

### Our Experience
- ✅ We have implemented Four Guards for SWE-bench
- ✅ We have run spot tests
- ✅ We understand the data format
- ✅ We have 408/500 predictions generated

---

## Benchmark 2: Tau Bench ⭐ (NEW)

### Basic Information
- **Focus**: API calling and function composition
- **Official site**: https://taubench.com/
- **Leaderboard**: https://taubench.com/#leaderboard
- **Horizon**: 30-50 steps (per Yucheng)
- **Task type**: Multi-step API orchestration

### Task Example (To Research)
[TO BE FILLED - After exploring Tau Bench]

```
Input:
- Natural language goal
- Available APIs

Output:
- Sequence of API calls

Evaluation:
- Goal achieved
- Valid API usage
```

### How Drift Manifests (Hypothesized)

| Dimension | Manifestation in Tau Bench | Example (To Verify) |
|-----------|---------------------------|---------------------|
| **Wrong Scope** | Calling irrelevant APIs | Task: book flight, Agent: calls weather API repeatedly |
| **Repetitive Mistakes** ⭐ | Retrying failed API calls | Agent calls same API with same params after 400 error |
| **Not Following Plan** | Wrong API call sequence | Plan: auth → search → book, Action: search → search → search |
| **Irrelevant Tool Use** | Using wrong APIs | Using database API when should use REST API |
| **Lack of Evidence** | Ignoring API error messages | 400 error returned, agent doesn't check error message |
| **Test Coverage** | Not validating API responses | Makes API call but doesn't check response status |

**Note from Yucheng**: "Repetitive mistakes especially evident in Tau Bench"

### Trajectory Availability
[TO BE FILLED - Need to research]
- Does Tau Bench publish trajectories?
- What format?
- Which models have public runs?

### To Research
- [ ] Visit https://taubench.com/
- [ ] Read documentation
- [ ] Explore task examples
- [ ] Check for public trajectories
- [ ] Understand evaluation metrics

---

## Benchmark 3: Web Arena ⭐ (NEW)

### Basic Information
- **Focus**: Web navigation and interaction
- **Task type**: Multi-step web browsing tasks
- **Horizon**: Long (per Yucheng: repetitive mistakes evident)

### Task Example (To Research)
[TO BE FILLED - After exploring Web Arena]

```
Input:
- Natural language goal
- Starting webpage

Output:
- Sequence of web actions (click, type, scroll)

Evaluation:
- Goal achieved
- Valid navigation
```

### How Drift Manifests (Hypothesized)

| Dimension | Manifestation in Web Arena | Example (To Verify) |
|-----------|---------------------------|---------------------|
| **Wrong Scope** | Visiting irrelevant pages | Task: buy product, Agent: visits help page, about page |
| **Repetitive Mistakes** ⭐ | Clicking same broken element | Agent clicks "Submit" button 5 times when it's disabled |
| **Not Following Plan** | Wrong navigation path | Plan: home → search → product, Action: home → about → contact |
| **Irrelevant Tool Use** | Using wrong interaction types | Using scroll when should use search box |
| **Lack of Evidence** | Ignoring page errors | Page shows "404", agent continues clicking |
| **Test Coverage** | Not verifying page state | Clicks submit without checking form validity |

**Note from Yucheng**: "Repetitive mistakes especially evident in Web Arena"

### Trajectory Availability
[TO BE FILLED - Need to research]
- Does Web Arena publish trajectories?
- What format?
- Which models have public runs?

### To Research
- [ ] Search for Web Arena dataset
- [ ] Read documentation
- [ ] Explore task examples
- [ ] Check for public trajectories
- [ ] Understand evaluation metrics

---

## Cross-Benchmark Comparison

### Similarities

All three benchmarks share:
1. Long-horizon tasks (>10 steps)
2. Sequential decision-making
3. Clear goals
4. Opportunity for drift

### Differences

| Aspect | SWE-bench | Tau Bench | Web Arena |
|--------|-----------|-----------|-----------|
| **Domain** | Code editing | API calling | Web browsing |
| **Action Space** | File edits, commands | API calls | Web interactions |
| **Feedback** | Test results | API responses | Page state |
| **Main Drift Type** | Wrong files | Wrong APIs, Repetitions ⭐ | Wrong pages, Repetitions ⭐ |
| **Horizon** | 5-50 steps | 30-50 steps | Long |

### How Our Framework Generalizes

Our Context Drift framework is generic because:

1. **Dimensions are domain-agnostic**:
   - Wrong Scope → Applies to any bounded task
   - Repetitive Mistakes → Applies to any sequential task
   - Not Following Plan → Applies to any planned task
   - [etc.]

2. **Detection is instantiable**:
   - Each benchmark has an "adapter"
   - Adapter translates domain-specific actions to generic dimensions
   - Core detection logic remains the same

3. **Example instantiation**:
```python
# Generic detector
def detect_repetitive_mistakes(trajectory):
    actions = extract_actions(trajectory)
    repetitions = count_similar_actions(actions)
    return repetition_score

# SWE-bench adapter
class SWEBenchAdapter:
    def extract_actions(self, trajectory):
        return [edit for edit in trajectory['file_edits']]

    def count_similar_actions(self, actions):
        # Compare patches using diff similarity
        ...

# Tau Bench adapter
class TauBenchAdapter:
    def extract_actions(self, trajectory):
        return [call for call in trajectory['api_calls']]

    def count_similar_actions(self, actions):
        # Compare API calls using endpoint + params
        ...

# Web Arena adapter
class WebArenaAdapter:
    def extract_actions(self, trajectory):
        return [action for action in trajectory['web_actions']]

    def count_similar_actions(self, actions):
        # Compare clicks using element + coordinates
        ...
```

---

## Trajectory Data Sources

### SWE-bench
```bash
# Example: Download trajectories from S3
aws s3 ls s3://swe-bench-experiments/verified/
aws s3 cp s3://swe-bench-experiments/verified/[model]/trajs/ ./data/swebench/ --recursive
```

**Available models**:
[TO BE FILLED - List available model runs]

### Tau Bench
[TO BE FILLED - Research data sources]

### Web Arena
[TO BE FILLED - Research data sources]

---

## Evaluation Plan

For each benchmark, we will:

1. **Download existing trajectories** (don't run our own!)
2. **Implement benchmark adapter**
3. **Run drift detection**
4. **Manual validation** (sample 20-50 trajectories)
5. **Calculate agreement** with human judgment

---

## Research Tasks

### For Tau Bench:
- [ ] Visit https://taubench.com/
- [ ] Read documentation
- [ ] Explore GitHub repo (if exists)
- [ ] Check for public trajectories
- [ ] Download sample data
- [ ] Understand task format
- [ ] Create notes in this document

### For Web Arena:
- [ ] Search for Web Arena dataset
- [ ] Read documentation
- [ ] Explore GitHub repo
- [ ] Check for public trajectories
- [ ] Download sample data
- [ ] Understand task format
- [ ] Create notes in this document

---

## Next Steps

After completing benchmark research:
1. Update this document with findings
2. Create benchmark-specific detection examples
3. Design adapters for each benchmark
4. Send to Yucheng for review

---

**Completion Checklist**:
- [ ] SWE-bench section complete (mostly done)
- [ ] Tau Bench researched and documented
- [ ] Web Arena researched and documented
- [ ] Cross-benchmark comparison table complete
- [ ] Trajectory sources identified for all 3
- [ ] Sent to Yucheng for review
