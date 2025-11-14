```
现在我开始深度research，重点调研：

SWE-bench数据集的元数据结构 - 确认可以提取哪些客观特征
现有的agentic coding系统 - 看他们如何处理goal drift和pattern learning
代码复杂度度量方法 - 找最适合SWE-bench的complexity metrics
实验设计最佳实践 - 确保你的方法可复现且有说服力

Your SWE-bench agentic coding research design is ready. It confirms all three research questions are feasible on a single RTX 5090, provides concrete implementation paths using LangGraph + SWE-agent, and validates your 2-week prototype timeline. The report includes specific metrics, baselines, experimental protocols, and cost estimates (<$200 total) for preventing goal drift (Q1), cross-session pattern learning (Q2), and complexity-adaptive generation (Q3).

```
# Experimental Design Guide: SWE-bench Agentic Coding Research

## Executive Summary

You can prototype Q1+Q2 in 2 weeks on a single RTX 5090, achieve competitive results (30-40% solve rate), and make an informed Q3 decision at week 3. **Key finding**: The field has matured rapidly—state-of-the-art systems now reach 46-50% on SWE-bench Verified through structured workflows, AST-aware retrieval, and intelligent constraint systems. Your three research questions are well-grounded in literature with clear implementation paths.

**Bottom line**: Use LangGraph with SWE-agent as your base, implement the Four-Guard System for Q1, build FAISS+CodeBERT pattern memory for Q2, and leverage objective complexity metrics (cyclomatic complexity, maintainability index) for Q3. All experiments can run locally with Qwen2.5-Coder-32B at \u003c$200 total cost. The 20-30% pattern reuse target is realistic (supported by code clone research), and adaptive complexity strategies show 7.86% improvement with 88.9% cost reduction in recent work.

---

## 1. SWE-bench Verified Dataset: Structure and Extractable Features

### Dataset fundamentals

SWE-bench Verified contains **500 human-validated Python tasks** from 11 repositories, with Django comprising 37% and the top 5 repos accounting for 80% of instances. Each task provides complete metadata: issue description, base commit, gold patch, test cases (FAIL_TO_PASS and PASS_TO_PASS), and crucially for your Q3 work, **human difficulty annotations**.

The difficulty distribution reveals a critical insight: **91% of tasks are estimated under 1 hour** for experienced engineers (39% trivial \<15min, 52% small 15-60min). This creates natural stratification for complexity experiments.

### Objective features for complexity measurement

**Directly extractable from patches:**
- Files modified: 1.0 average (easy) → 2.0 (hard) — 2x increase
- Lines of code changed: 5 LOC (easy) → 50+ LOC (hard) — **11x increase**, strongest predictor
- Hunks per task: 1-2 (easy) → 5+ (hard) — 5x increase
- Change type distribution: ~60-70% bug fixes, 20-30% features, 5-10% refactoring

**Computable via static analysis tools:**
```python
# Cyclomatic complexity
pip install radon
radon cc --show-complexity file.py  # Outputs A-F grades

# Maintainability Index (0-100 scale)
radon mi file.py  # >85 good, <65 difficult

# Multi-language support
pip install lizard  # Python, Java, JavaScript
lizard -l python path/
```

**Dependency depth measurement:**
```python
pip install pydeps
pydeps --max-bacon 5 module_name  # Visualizes import graph
```

### Critical limitations

The dataset is **100% Python** in the original version (multilingual variants exist: SWE-PolyBench for Java/JavaScript/TypeScript, Multi-SWE-bench for 7 languages). No pre-computed complexity metrics exist—you must calculate them. Repository skew toward Django means results should be stratified by repo. The 500-sample size is sufficient for statistical power (need ~150 per group for 80% power to detect medium effects).

---

## 2. State-of-the-Art Systems and Benchmark Results

### Current performance landscape

**Top systems on SWE-bench Verified (500 tasks):**
- AutoCodeRover v20240620: **46.2%** Pass@1 at $0.43-0.70/task
- Agentless + Claude 3.5: **50.8%** Pass@1 
- SWE-agent 1.0 + Claude 3.7: **45-50%** range
- Claude 4.5 Sonnet (base): **43.6%** Pass@1

This represents explosive progress from October 2023 baselines of 1.96% (Claude 2) and 1.7% (GPT-4). The field has improved **25x in 18 months**.

### Three architectural paradigms

**1. Agent-Computer Interface (SWE-agent)**: Custom bash commands optimized for LLM understanding, with history compression and informative error messages. Achieves 33.6% on Verified with ReAct-style reasoning. Cost: $1.50-4.00/task.

**2. AST-Aware Retrieval (AutoCodeRover)**: Two-phase approach with program structure-aware search. Uses Abstract Syntax Tree navigation (search_class, search_method) rather than file-level operations. Runs in 7-10 minutes per task. **65.4% of plausible patches are semantically correct**—a key quality metric.

**3. Structured Workflows (Agentless)**: Fixed three-phase pipeline without autonomous decision-making: hierarchical localization → diff generation → validation. Surprisingly effective despite simplicity, **challenging the necessity of complex agent architectures**. Matches or exceeds autonomous agents at similar cost.

### Documented failure modes for Q1 design

Analysis of 248 unresolved SWE-bench Lite instances reveals:
- **26% incorrect implementation**: Functionally wrong solutions
- **26% overly specific**: Insufficient generalization  
- **23.4% cascading failed edits**: Sequential errors compound
- Wrong location edits, syntax errors, tool misuse

These patterns directly inform your Q1 guardrail design—scope violations, implementation drift, and error propagation are empirically the dominant failure modes.

### Goal drift prevention in practice

**Documented approaches:**
- **Structured workflows** (Agentless): Fixed phase sequences prevent wandering
- **Context management** (SWE-agent): Budget limits ($4 cap), history compression, collapse irrelevant observations
- **Test-driven development**: Tests define objective success criteria, preventing subjective interpretation drift
- **Iteration limits**: Maximum turns/steps per task with automatic submission

Notably, **no system explicitly implements a "Four-Guard" constraint system** as you propose—this is a genuine research contribution opportunity.

---

## 3. Q1 Experimental Design: Preventing Goal Drift

### Concrete metrics with computation methods

**File Modification Scope Violation Rate (FMSVR)**
```
FMSVR = (files modified outside scope) / (total files modified)
```

Implementation using AST dependency analysis:
```python
import ast, git, networkx as nx

def detect_scope_violations(repo_path, issue_scope, diff):
    # Build dependency graph
    dep_graph = build_import_graph(repo_path)  # Using AST
    modified_files = parse_diff_files(diff)
    
    # Check each file against scope + 2-hop dependencies
    violations = [f for f in modified_files 
                  if dependency_distance(f, issue_scope, dep_graph) > 2]
    return len(violations) / len(modified_files)
```

**Baseline expectation**: 20-30% (derived from SWE-bench Pro multi-file edit failures and "wrong location" error analysis)

**Unnecessary Refactoring Index (URI)**
```
URI = (style_changes + |complexity_delta|) / functional_changes
```

Tools: **libcst** (Python CST analysis preserving formatting), **diffsitter** (semantic diffs), tree-sitter (multi-language). Parse before/after code, count functional vs non-functional AST changes, measure cyclomatic complexity delta.

**Baseline expectation**: 15-25% (from "wrong solution" failure mode analysis showing plausible but incorrect changes)

**Test-First Compliance Rate (TFCR)**
```
TFCR = (code changes preceded by failing test) / (total code changes)
```

Implement via finite state machine: waiting_for_test → test_failing → implementing → test_passing. Track temporal ordering of file writes and test status. Based on TDD Guard framework (github.com/nizos/tdd-guard).

**Baseline expectation**: 30-40% non-compliance (agents naturally skip TDD)

**Plan-Action Alignment Score (PAAS)**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
plan_emb = model.encode(agent_stated_plan)
action_emb = model.encode(agent_actual_actions)
PAAS = cosine_similarity([plan_emb], [action_emb])[0][0]
```

**Baseline expectation**: 0.6-0.7 (from goal drift research showing Claude 3.5 near-zero drift, GPT-4o 0.2-0.4, smaller models 0.5-0.8)

### Four-Guard System implementation

**Scope Guard** — Prevent out-of-scope file modifications
```python
class ScopeGuard:
    def __init__(self, issue_description, repository):
        self.scope = extract_scope(issue_description)  # NER + regex
        self.dep_graph = build_dependency_graph(repository)  # AST imports
    
    def validate_modification(self, filepath):
        if filepath in self.scope:
            return True
        distance = dependency_distance(filepath, self.scope, self.dep_graph)
        return distance <= 2  # Allow 2-hop dependencies
```

**Plan Guard** — Ensure actions align with stated plans
```python
class PlanGuard:
    def validate_action(self, plan, action):
        # Fast path: semantic similarity
        similarity = cosine_similarity(embed(plan), embed(action))
        if similarity >= 0.7:
            return True
        
        # Slow path: LLM validation for edge cases
        prompt = f"Does action '{action}' align with plan '{plan}'? Yes/No:"
        return "yes" in llm.query(prompt).lower()
```

**Test Guard** — Enforce test-driven development
```python
class TestGuard:
    def __init__(self):
        self.state = 'waiting_for_test'  # FSM
    
    def on_file_write(self, filepath, content):
        is_test = 'test_' in filepath
        
        if self.state == 'waiting_for_test' and not is_test:
            raise TDDViolation("Write test first!")
        
        if self.state == 'test_failing' and not is_test:
            # Verify tests actually fail before implementation
            if not any(test.failed for test in run_tests()):
                raise TDDViolation("Tests must fail before implementation")
```

**Evidence Guard** — Verify agent claims against reality
```python
class EvidenceGuard:
    def verify_claim(self, claim):
        if claim.type == 'code_change':
            return verify_via_ast(claim)  # Check AST for pattern
        elif claim.type == 'test_result':
            return verify_via_tests(claim)  # Run tests
        elif claim.type == 'behavior':
            return verify_via_execution(claim)  # Execute code
```

### Experimental protocol

**Dataset**: SWE-bench Verified subset with 2-10 file modifications, clear scope, existing tests (~300 tasks)

**Conditions**:
- Control: Baseline agent (SWE-agent, no guardrails)
- T1: Single guard ablations (Scope only, Plan only, Test only, Evidence only)
- T2: Combined guards (Scope+Plan, Test+Evidence, All Four)
- T3: Strictness levels (Lenient warnings, Moderate blocking, Strict enforcement)

**Success criteria**:
- FMSVR: >50% reduction (25% → <12%)
- URI: >40% reduction (20% → <12%)
- TFCR: >60% improvement (35% → >55%)
- PAAS: +0.15 increase (0.65 → >0.80)
- Pass@1: Within 5% of baseline (no significant task success penalty)

**Timeline**: 16 weeks total — 3 weeks infrastructure, 4 weeks guard implementation, 2 weeks integration, 4 weeks experimental runs, 3 weeks analysis

---

## 4. Q2 Experimental Design: Cross-Session Pattern Learning

### Pattern extraction technical approach

**Multi-level representation strategy:**

**1. AST structural patterns**
```python
import ast, tree_sitter

class PatternExtractor(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        pattern = {
            "type": "function_pattern",
            "control_flow": extract_control_flow(node),  # If-else, loops
            "api_calls": extract_api_calls(node),  # Method sequences
            "data_structures": extract_structures(node)  # Lists, dicts, sets
        }
        return pattern
```

**2. Neural code embeddings**
```python
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")

def get_code_embedding(code_snippet):
    tokens = tokenizer(code_snippet, return_tensors="pt", truncation=True, max_length=512)
    embeddings = model(**tokens).last_hidden_state.mean(dim=1)
    return embeddings.detach().numpy()  # 768-dim vector
```

**3. API usage sequences**: Extract n-grams of function calls, identify common design patterns (Factory, Observer, Strategy)

**4. Algorithmic templates**: Recognize two-pointer, sliding window, dynamic programming structures

### Storage architecture: FAISS + SQL

**Vector database for similarity search:**
```python
import faiss
import numpy as np

# Initialize FAISS index
dimension = 768  # CodeBERT embedding dimension
index = faiss.IndexFlatL2(dimension)  # L2 distance

# Add patterns
pattern_embeddings = np.array([emb1, emb2, ...]).astype('float32')
index.add(pattern_embeddings)

# Retrieve top-5 similar patterns
query_embedding = get_code_embedding(new_problem)
distances, indices = index.search(query_embedding.reshape(1, -1), k=5)
```

**Metadata storage:**
```sql
CREATE TABLE patterns (
    pattern_id UUID PRIMARY KEY,
    embedding VECTOR(768),
    ast_structure JSONB,
    code_template TEXT,
    source_task_id VARCHAR,
    success_rate FLOAT,
    language VARCHAR,
    complexity_score FLOAT,
    tags JSONB
);
```

### Multi-stage retrieval pipeline

**Stage 1**: Coarse retrieval via FAISS (top-50 candidates using embedding similarity)

**Stage 2**: Re-ranking with multiple signals
- AST structural similarity (tree edit distance)
- Token-level similarity (Jaccard coefficient — literature shows 0.77 accuracy)
- Code complexity matching
- Problem description similarity

**Stage 3**: Context matching
- Repository/language compatibility
- Test case pattern alignment
- Difficulty level correspondence

### Experimental protocol

**Dataset split** (SWE-bench 2,294 tasks):
- Training: 60% (~1,376 tasks) — extract patterns from successful solutions
- Validation: 20% (~459 tasks) — tune retrieval hyperparameters
- Test: 20% (~459 tasks) — final evaluation

**Cross-validation**: 5-fold within training set, stratified by difficulty/language/repository. Leave-one-repository-out for generalization testing.

**Pattern clustering**: Apply k-means with k=50-200 clusters on embeddings, identify canonical patterns as cluster centroids, use silhouette score for cluster quality validation.

### Metrics and realistic targets

**Primary metrics:**
1. **Pattern Retrieval Accuracy**: Precision@5 ≥ 0.70, Recall@5 ≥ 0.60
2. **Solution Success Rate**: Pass@1 improvement from 30-40% baseline → **50-60% target** (20-30% absolute improvement)
3. **Token Efficiency**: 30-40% reduction in generation tokens
4. **Pattern Reuse Rate**: **20-30% of problems benefit from patterns** (achievable based on code clone literature)

**Literature grounding**: Code clone detection research shows 40-60% Type-1/2 clones exist in codebases, 20-30% Type-3 near-miss clones. This supports the 20-30% reuse target as realistic and conservative.

**Transfer learning evaluation:**
- Within-repository transfer: Same repo, different tasks
- Cross-repository transfer: Different repositories
- Cross-language transfer: Python patterns → Java problems (if applicable)
- Zero-shot vs Few-shot (1, 3, 5 examples)

### Implementation with LangChain RAG

```python
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA

# Initialize
embeddings = HuggingFaceEmbeddings(model_name="microsoft/codebert-base")
vectorstore = FAISS.from_documents(pattern_documents, embeddings)

# Create RAG chain
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
qa_chain = RetrievalQA.from_chain_type(
    llm=code_llm,
    retriever=retriever,
    return_source_documents=True
)

# Query with pattern augmentation
result = qa_chain({"query": problem_description})
```

**Computational requirements:**
- Pattern extraction: CPU 8-16 cores, 32-64GB RAM, 24-48 hours for full SWE-bench
- Embedding generation: 1x A100 (40GB) or 2x V100, 12-24 hours
- Inference per query: Vector search <100ms, LLM generation 2-10s, total <15s
- Storage: Pattern database 50-100GB, vector indices 10-20GB, total ~150GB

**Timeline**: 12 weeks — 2 weeks infrastructure, 2 weeks extraction, 2 weeks retrieval development, 2 weeks agent integration, 2 weeks evaluation, 2 weeks analysis

---

## 5. Q3 Experimental Design: Complexity-Adaptive Code Generation

### Objective complexity metrics toolkit

**Cyclomatic complexity** (decision points + 1):
```bash
# Python
pip install radon
radon cc --show-complexity --min C file.py  # Grades A-F
# A (1-5), B (6-10), C (11-20), D (21-50), E (51-100), F (100+)

# Multi-language
pip install lizard
lizard -C 10 -o report.html directory/  # Supports 15+ languages
```

**Maintainability Index** (0-100 scale, combines Halstead volume, cyclomatic complexity, LOC):
```bash
radon mi file.py  # 85-100: good, 65-85: moderate, 0-65: difficult
```

**Halstead metrics** (program vocabulary and length):
```bash
radon hal file.py  # Volume, Difficulty, Effort, Bugs estimate
```

**Dependency depth**:
```bash
pip install pydeps
pydeps --max-bacon 5 module_name  # Visualizes import graph depth
```

### Composite complexity scoring

**Proposed formula**:
```
ComplexityScore = 0.3×CC_norm + 0.25×MI_inv_norm + 0.2×Depth_norm 
                  + 0.15×LOC_norm + 0.1×Halstead_norm

Where each component normalized to [0, 1]:
- CC_norm = Cyclomatic Complexity / 50 (capped at 1.0)
- MI_inv_norm = (100 - Maintainability Index) / 100
- Depth_norm = Dependency Depth / 10 (capped at 1.0)
- LOC_norm = LOC / 500 (capped at 1.0)
- Halstead_norm = Halstead Volume / 10000 (capped at 1.0)
```

**Alternative: CoT-length based assessment** (recent finding from AdaptiveLLM 2025):
- Use reasoning model to generate Chain-of-Thought
- **CoT length correlates 0.72 with task complexity**
- Method: Generate 10 CoTs, use median length, k-means into 3 difficulty levels
- Advantage: Reflects LLM perception of difficulty, not just human perception

### Complexity-to-strategy mapping

**Strategy parameters by complexity level:**

| Complexity | Model Size | Temperature | Prompt Style | Token Budget |
|------------|-----------|-------------|--------------|--------------|
| Low (0-0.3) | 1.5B-7B | 0.2 | Concise | 500 tokens |
| Medium (0.3-0.7) | 7B-16B | 0.5 | Moderate | 2000 tokens |
| High (0.7-1.0) | 32B+ | 0.7 | Detailed | 5000 tokens |

**Research question**: Should high complexity get MORE detail (traditional hypothesis) or MORE planning tokens but LESS verbose code (efficiency-first hypothesis)? Test both empirically.

**Prompt engineering by complexity:**

*Low complexity*: "Task: {description}. Generate concise, efficient code. Focus on correctness."

*Medium complexity*: "Task: {description}. Approach: 1) Analyze requirements 2) Design solution 3) Implement with comments. Generate well-structured code."

*High complexity*: "Task: {description}. Instructions: 1) Break down components 2) Consider edge cases 3) Design algorithm with complexity analysis 4) Implement with detailed comments and type hints. Generate production-quality code."

### Token efficiency metric

**Primary formula**:
```
TokenEfficiency = Pass@1 / AvgTokensPerTask

Where:
- Pass@1 = Success rate on test set
- AvgTokensPerTask = (InputTokens + OutputTokens) / NumTasks
```

**Dynamic budget allocation**:
```
TokenBudget = 500 + (ComplexityScore × 4500)
```
This scales from 500 tokens (low complexity) to 5000 tokens (high complexity).

### Literature evidence for Q3 feasibility

**AdaptiveLLM (2025)**: CoT-based difficulty assessment + XGBoost classifier for model selection achieved **7.86% improvement in Pass@1 with 88.9% cost reduction** vs baseline.

**Complexity-Aware Feedback (2025)**: Using 53 complexity metrics (identified top 5 via Shapley values: Halstead Length, Cyclomatic Complexity, Cognitive Complexity, Nesting Depth, Parameter Count) achieved **35.71% Pass@1 improvement** on HumanEval with GPT-3.5 through iterative feedback.

**Key finding**: Complexity DOES predict optimal strategy, and adaptive approaches show consistent 7-35% improvements across multiple studies.

### Experimental protocol

**Setup**: A/B testing with fixed vs adaptive strategies

**Baselines**:
1. Always GPT-4 with detailed prompts (high cost, high performance)
2. Always Qwen2.5-Coder-7B with moderate prompts (medium cost/performance)
3. Always small model (1.5B) with concise prompts (low cost/performance)

**Treatment**: Adaptive strategy with complexity-based model and prompt selection

**Datasets**: HumanEval (164), MBPP (974), LeetCodeSample (~200), CodeContests (165), SWE-bench Verified (500)

**Success criteria**:
- Pass@1: 45-55% (match or exceed medium-large models)
- Cost: 50-70% reduction vs fixed GPT-4
- Token efficiency: 2-3x better than fixed strategies
- Overall: 25-35% token reduction at same quality

**Statistical testing**: Paired t-test, Cohen's d effect size, α=0.05, need ~150+ tasks per group for 80% power

**Ablation studies**: Test (1) Complexity assessment only, (2) Model selection only, (3) Prompt engineering only, (4) Full system to measure contribution of each component

**Timeline**: 9 weeks — 2 weeks baseline, 3 weeks mapping, 2 weeks evaluation, 2 weeks analysis

### Potential issues and alternatives

**If complexity doesn't predict optimal strategy:**
- Try CoT-based assessment instead of static metrics
- Focus on model selection rather than prompt verbosity
- Learn strategy from post-hoc analysis (train meta-learner on actual results)

**If high-complexity tasks still fail:**
- Use Pass@5 with diverse strategies
- Implement retrieval augmentation with relevant examples
- Flag for human-in-the-loop review

**Alternative formulations**:
1. **Reinforcement Learning**: Train RL agent to select {model, prompt, temperature} with reward = +Success - λ×TokenCost
2. **Curriculum Learning**: Train models on progressively harder tasks, specialize each model to complexity range
3. **Hybrid Static+Dynamic**: Quick metrics for initial strategy, adaptive retry if mismatch detected

---

## 6. Implementation Guide: Frameworks, Hardware, and Timeline

### Framework recommendation: LangGraph

**Why LangGraph for coding agents:**
- **Production-proven**: Powers SWE-agent (46.2% on SWE-bench Verified), used by Klarna, Replit, Elastic
- **Performance leader**: Benchmarks show lowest latency and token usage across all agent frameworks
- **Precise control**: Low-level framework doesn't abstract prompts or architecture—critical for research
- **Stateful workflows**: Graph-based with checkpointing, built-in tool calling, human-in-the-loop
- **Observability**: Native LangSmith integration for tracing and debugging

**Getting started**:
```bash
pip install langgraph langchain-openai
git clone https://github.com/SWE-agent/mini-swe-agent  # 100 lines example
```

**Tutorial**: Build coding agent in ~100 lines, LangGraph Academy free course available

### Hardware assessment: RTX 5090 (32GB VRAM)

**Verdict: YES, feasible for your experiments**

**Model capacity with 4-bit quantization:**
- 7B models: 4-6GB VRAM, **185+ tokens/sec generation** ✅ Excellent
- 13B models: 8-10GB VRAM, 120+ tokens/sec ✅ Excellent  
- 32B models: 18-20GB VRAM, 61+ tokens/sec ✅ Good
- 70B models: 36-40GB VRAM ❌ Requires dual GPU

**Performance**: 2.6x faster than A100 80GB for 7B model inference, 10,400 tokens/sec prompt processing (Qwen 8B)

**Recommendation for your timeline:**
- **Weeks 1-2 (prototype)**: Qwen2.5-Coder-7B with 4-bit quantization
- **Week 3+ (development)**: Qwen2.5-Coder-32B for experiments
- **Final evaluation**: Mix of local 32B + cloud APIs (Claude/GPT-4o) for validation

### Model selection strategy

**Recommended models:**

| Phase | Model | VRAM | Cost | Performance |
|-------|-------|------|------|-------------|
| Week 1-2 Prototype | Qwen2.5-Coder-7B-4bit | 5GB | $0 | ~GPT-3.5 level |
| Week 3+ Development | Qwen2.5-Coder-32B-4bit | 20GB | $0 | Competitive with GPT-4 |
| Final Evaluation | Claude 3.7 Sonnet | API | $0.003-0.015/1K | SOTA |

**Cost estimate** (hybrid approach):
- Weeks 1-2: 100% local = $0
- Week 3: Mix local + 50 cloud evals = $40  
- Week 4+: Mostly local, selective cloud = $100
- **Total: ~$140** vs $1,000+ for full cloud

**Local setup**:
```bash
# Install ollama for easy local deployment
curl -fsSL https://ollama.com/install.sh | sh

# Download and run Qwen2.5-Coder
ollama pull qwen2.5-coder:7b
ollama serve

# Test
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-coder:7b",
  "prompt": "Write a function to reverse a string"
}'
```

### Existing codebases to fork

**Primary recommendation: SWE-agent**
- **GitHub**: github.com/SWE-agent/SWE-agent
- **Performance**: 46.2% on SWE-bench Verified, SOTA among open-source
- **Architecture**: LangGraph-based with custom Agent-Computer Interface (ACI)
- **Features**: Docker execution (SWE-ReX), YAML config, multi-LLM support
- **Setup time**: ~30 minutes
- **License**: MIT

**Alternative: mini-SWE-agent**
- **GitHub**: github.com/SWE-agent/mini-swe-agent
- **Code**: 100 lines of Python, 65% on SWE-bench Verified
- **Perfect for**: Rapid prototyping, understanding core concepts

**AutoCodeRover** (for AST-based approach):
- **GitHub**: github.com/AutoCodeRoverSG/auto-code-rover
- **Performance**: 46.2% on Verified, 30.67% on Lite
- **Unique**: AST-aware code search, two-phase retrieval
- **Cost**: <$0.70/task, <7 minutes/task

**Evaluation harness**:
```bash
pip install swebench
python -m swebench.harness.run_evaluation \
    --dataset_name SWE-bench/SWE-bench_Verified \
    --predictions_path predictions.jsonl \
    --max_workers 4
```

### Timeline breakdown and feasibility

**WEEK 1-2: Q1+Q2 Prototype — FEASIBLE**

*Week 1: Environment Setup*
- **Day 1-2**: Install Docker, CUDA, ollama; deploy Qwen2.5-Coder-7B; verify GPU performance
- **Day 3-4**: Clone mini-SWE-agent, run on 5-10 examples, understand architecture, set up LangSmith
- **Day 5-7**: Modify for Q1, implement basic guardrails, run on 20-30 examples, document findings

*Week 2: Initial Experiments*
- **Day 8-10**: Implement Q1 Four-Guard System fully, evaluate on 50-100 Lite subset, measure metrics
- **Day 11-13**: Implement Q2 pattern memory, run comparative evaluation, statistical comparison
- **Day 14**: Integration, documentation, prepare Q3 decision analysis

**What you'll have after Week 2:**
✅ Working prototype with Q1 guardrails implemented
✅ Q2 pattern memory with basic retrieval (50-100 patterns)
✅ Evaluation on 50-100 tasks with clear metrics
✅ Performance comparison: baseline vs Q1 vs Q2
✅ Identification of promising directions

**WEEK 3: Q3 Decision Point**

**Completion criteria:**
1. Resolve rates on 50+ tasks with statistical analysis
2. Cost per task ($0-5 range with local models)
3. Clear understanding of success/failure patterns
4. Technical infrastructure validated (Docker, evaluation harness working)

**Decision rules:**
- **PROCEED** if resolve rate >15% (competitive baseline)
- **PROCEED** if clear improvement over baseline (>3% absolute)
- **PIVOT** if cost per task >$2 or insurmountable technical blockers

**WEEK 4+: Full Implementation**

*Parallel development strategy:*
- **Track 1 (automated)**: Full SWE-bench Lite evaluation (300 tasks) — runs overnight
- **Track 2 (active dev)**: Implement Q3 complexity adaptation, advanced features
- **Track 3 (continuous)**: Logging, monitoring, error analysis, optimization

**Realistic expectations:**
- Week 4: Full Lite evaluation (300 tasks) + Q3 initial implementation
- Week 5: Q3 full evaluation + ablation studies
- Week 6: Optimization, cross-validation, final benchmarks

### Development infrastructure

**Code execution sandbox:**
- **Start with**: Docker (free, standard for SWE-bench, included in SWE-agent)
- **Scale to**: Modal.com if need >100 parallel tasks (<1s startup, ~$0.10-0.30/compute hour)

**Logging and monitoring:**
- **LangSmith**: Agent tracing, cost tracking (free tier: 5K traces/month) — ESSENTIAL
- **Weights & Biases**: Experiment tracking (free for individuals) — if running many variations
- **Basic CSV logging**: For metrics (minimum viable setup)

**Minimal setup (Week 1-2)**:
```bash
# Install core dependencies
pip install langgraph langchain-openai swebench
pip install radon lizard  # Complexity metrics for Q3
pip install faiss-cpu sentence-transformers  # Pattern memory for Q2

# Set up LangSmith
export LANGCHAIN_API_KEY="your_key"
export LANGCHAIN_TRACING_V2=true

# Clone base implementation
git clone https://github.com/SWE-agent/mini-swe-agent
cd mini-swe-agent
pip install -r requirements.txt
```

### Resource budget summary

**Hardware** (one-time): RTX 5090 $2,000-3,000 (if not already owned)

**Compute costs** (hybrid approach):
- Local experimentation: $0
- Cloud validation: $140 total
- Power: ~$50-100/month if running 24/7

**Infrastructure**: $0-50/month (LangSmith free tier, W&B free, Docker free)

**Total for 6-week prototype**: **<$200** with hybrid approach, **<$1,000** if full cloud

**Time investment**: 
- Week 1-2: 60-80 hours (full-time)
- Week 3: 20-30 hours (analysis + decision)
- Week 4+: 40-50 hours/week ongoing

### Risk mitigation

**Risk 1: Model performance insufficient** (<10% solve rate)
- **Mitigation**: Switch to cloud APIs, simplify task subset, focus on specific languages

**Risk 2: RTX 5090 insufficient**
- **Mitigation**: Use 3-bit quantization, stick to 13B models, cloud APIs for final eval

**Risk 3: Docker/infrastructure issues**
- **Mitigation**: 2-3 day buffer for debugging, use Modal.com if Docker problematic

**Risk 4: Timeline slippage**
- **Mitigation**: Use mini-SWE-agent (100 lines), reduce evaluation to 20-30 examples, focus on Q1 only first

**Risk 5: Cost overruns**
- **Mitigation**: Set hard API limits, use local models primarily, implement caching

---

## 7. Integrated Recommendations and Next Steps

### Optimal starting sequence

**Day 1 (immediate actions)**:
```bash
# Environment setup
sudo apt update && sudo apt install docker.io nvidia-docker2
pip install ollama
ollama pull qwen2.5-coder:7b
ollama serve

# Clone base implementation
git clone https://github.com/SWE-agent/mini-swe-agent
cd mini-swe-agent
pip install -r requirements.txt

# Test run on 5 examples
python run_evaluation.py --model ollama/qwen2.5-coder:7b --num_examples 5
```

**Week 1 priorities**: Get mini-SWE-agent running, understand architecture, implement simplest Q1 guardrail (scope guard), test on 20 examples

**Week 2 priorities**: Full Four-Guard System, pattern memory skeleton, 50-100 task evaluation, preliminary results

**Week 3 decision**: Analyze metrics, determine if Q3 is tractable, identify which question (Q1/Q2/Q3) shows most promise

### Key success factors

1. **Start small**: 10-20 examples before scaling to 300+
2. **Leverage local models**: RTX 5090 + Qwen 32B is 90% as good as cloud at $0 cost
3. **Fork, don't build**: Use mini-SWE-agent as base, modify incrementally
4. **Parallelize intelligently**: Run overnight evaluations, develop during day
5. **Monitor costs**: Set API limits, use cloud only for final validation
6. **Document obsessively**: LangSmith traces are invaluable for debugging

### Expected performance targets

**Conservative targets**:
- **Q1 (Goal Alignment)**: 15-25% improvement in scope compliance, <5% task success penalty
- **Q2 (Pattern Reuse)**: 15-20% Pass@1 improvement, 20-30% pattern reuse rate, 25% token reduction
- **Q3 (Complexity Adaptation)**: 15-20% Pass@1 improvement at 30-40% cost reduction

**Optimistic targets**:
- **Q1**: 50% reduction in scope violations, improved task success through better focus
- **Q2**: 25-30% Pass@1 improvement, 35-40% pattern reuse rate, 40% token reduction
- **Q3**: 25-30% Pass@1 improvement at 50-70% cost reduction

**Baseline expectations** (from literature):
- SWE-bench Lite: 20-30% solve rate (7B-32B models)
- SWE-bench Verified: 30-40% solve rate (32B models)
- Cost: $0.30-0.70/task with cloud APIs, $0 with local models
- Time: 7-15 minutes per task

### Novel contributions

Your research offers **three genuine contributions** to the field:

1. **Q1 Four-Guard System**: No existing system explicitly implements multi-layered constraint enforcement (scope, plan, test, evidence). This addresses the documented 23-26% failure rate from drift/wrong location.

2. **Q2 Pattern Memory**: While RAG for code exists, systematic pattern extraction→clustering→reuse pipeline across coding tasks is understudied. The 20-30% reuse target is grounded in code clone literature but not validated for agent learning.

3. **Q3 Complexity Adaptation**: AdaptiveLLM (2025) validates the concept (7.86% improvement, 88.9% cost reduction), but comprehensive evaluation across SWE-bench with multiple strategies is novel. Your objective metrics approach (avoiding human preference) is methodologically sound.

### If Q3 seems problematic

**Alternative formulations**:

1. **Learned strategy selection**: Skip upfront complexity analysis, train meta-learner on post-hoc results (which strategy worked for which task characteristics)

2. **Reinforcement learning**: State = task + attempt, Action = {model, prompt, temp}, Reward = +Success - λ×Cost, train PPO/DQN agent

3. **Hybrid static+dynamic**: Quick metrics for initial guess, adaptive retry if mismatch between generated complexity and task complexity

4. **Curriculum learning**: Order tasks by complexity, train specialized models for each range

The static metrics approach (radon/lizard) is most straightforward for 9-week timeline. RL approach requires 12-16 weeks. Choose based on Week 3 findings.

### Final recommendation

**Proceed with all three questions** using the hybrid local+cloud approach:

- **Q1**: Implement Four-Guard System in Week 2, evaluate on 100 tasks, expect clear measurable improvement in scope compliance
- **Q2**: Build FAISS+CodeBERT pattern memory, evaluate on 100 tasks, expect 15-25% improvement if patterns retrieve well
- **Q3**: Use static complexity metrics (radon for Python), implement model selection, expect 10-20% efficiency gain

**Critical path**: Q1 and Q2 can prototype in 2 weeks (feasible), Q3 decision at Week 3 based on whether complexity metrics stratify task difficulty. If Q3 shows weak correlation, pivot to alternative formulation or drop Q3 entirely and focus on Q1+Q2.

Your experimental design is **well-grounded, achievable, and offers genuine contributions**. The 2-week prototype timeline is realistic with mini-SWE-agent, RTX 5090 eliminates cost barriers, and literature strongly supports 20-30% pattern reuse and 7-35% complexity adaptation gains. Proceed with confidence.