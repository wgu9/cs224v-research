There are several benchmark datasets specifically designed to evaluate AI coding and code generation performance. These benchmarks are commonly used by researchers and organizations to assess the ability of models like Codex, Claude Code, and others to generate, complete, and reason about code[1][2][9].

### Major Coding Benchmarks

- **HumanEval**: Consists of 164 programming problems, each with unit tests for automatic verification of generated code. Used widely to measure code generation accuracy in language models[1][4].
- **SWE-Bench Pro**: Provides a rigorous benchmark for complex, real-world software engineering tasks, such as bug fixes, feature requests, and multi-file edits. It includes public and private subsets for broad evaluation, showing clear differences in model generalization ability between Codex, Claude, GPT-4o, and others[2].
- **RepoBench**: Focuses on repository-level code completion and retrieval tasks, evaluating an AI’s ability to perform cross-file code completion in multi-file projects[1].
- **DS-1000**: Targets code generation for data science problems, with 1000 tasks drawn from StackOverflow to simulate realistic coding scenarios[1].
- **Comprehensive RAG Benchmark (CRAG)**: Factual QA and code reasoning for models with retrieval-augmented generation capabilities[1].

### Broader LLM Benchmarks Database

- The Evidently AI database lists over 250 LLM benchmarks and datasets for tasks such as coding, reasoning, safety, and more, including links and descriptions for each dataset[9].
- LiveBench is an actively maintained, contamination-free LLM benchmark platform designed to provide ongoing, objective evaluation of coding and other reasoning tasks[6].

### Coding Performance Metrics

- These datasets are used to report performance metrics like code correctness (pass rate), repository-specific success rates, programming language coverage, and robustness against more difficult, real-world codebase challenges[2][1][4].

These benchmarks are open and often available for community use, helping drive transparency and progress in AI code generation research[9][10].

Sources
[1] 25 AI benchmarks: examples of AI models evaluation - Evidently AI https://www.evidentlyai.com/blog/ai-benchmarks
[2] SWE-Bench Pro (Public Dataset) - Scale AI https://scale.com/leaderboard/swe_bench_pro_public
[3] Comparison of AI Models across Intelligence, Performance, Price https://artificialanalysis.ai/models
[4] Test scores of AI systems on various capabilities relative to human ... https://ourworldindata.org/grapher/test-scores-ai-capabilities-relative-human-performance
[5] Benchmark Work | Benchmarks MLCommons https://mlcommons.org/benchmarks/
[6] LiveBench https://livebench.ai
[7] AI Benchmarking | Epoch AI https://epoch.ai/benchmarks
[8] Are there any real benchmarks showing these AI coding tools ... https://www.reddit.com/r/ClaudeAI/comments/1mwtyan/are_there_any_real_benchmarks_showing_these_ai/
[9] 250 LLM benchmarks and evaluation datasets - Evidently AI https://www.evidentlyai.com/llm-evaluation-benchmarks-datasets
[10] A collection of benchmarks and datasets for evaluating LLM. - GitHub https://github.com/leobeeson/llm_benchmarks


Most widely used coding benchmarks such as HumanEval, SWE-Bench, and RepoBench, while structured as task-oriented problem sets, do not natively provide datasets in a true multi-turn chat format (i.e., full conversational history of user prompts and multi-turn AI-generated completions as seen in IDE chat logs)[1][2][3].

### Dataset Structures

- **HumanEval**: Contains natural language prompts and canonical solutions, but each item is a single prompt with a single code completion—not a full chat dialogue with multiple exchanges[1][4][5][6].
- **SWE-Bench**: Supports custom prompt generation (including issue reports and context), and the benchmarking process can involve multi-step interaction, but the public datasets are released primarily as single-turn tasks: prompt/issue plus code patch. You can script multi-turn chat logs during evaluation, but the benchmarks themselves are not released as conversational datasets[2][3][7].
- **RepoBench**: Similar setup—structured as one-shot or single-prompt tasks, sometimes with extended context (file contents, codebase snippets), but not true chat transcripts[8][9][10].

### Chat-Like Formats

- Datasets occasionally include prompt history or context (as in retrieval-augmented variants or when using tools to simulate step-by-step reasoning), but these are not released as multi-exchange chat logs with alternating user and model utterances as typically found in IDE coding assistants[1][2].
- For chat-style datasets (prompt + response, potentially multi-turn), most are synthetic or created by logging interaction histories during live evaluation, not by design in these main benchmarks.

### Summary Table

| Benchmark      | Chat-like Format | Notes                                                            |
|----------------|------------------|------------------------------------------------------------------|
| HumanEval      | No               | Single prompt + completion, no multi-turn chat history[1]   |
| SWE-Bench      | Partial          | Single shot, custom prompts; chat log possible via scripting[2][3] |
| RepoBench      | No               | Single prompt + completion, sometimes extended context[8][9] |

For true training data mimicking chat logs (user prompt and multi-step AI guidance), these main coding benchmarks do not directly provide multi-turn chat formats, but allow you to create them during evaluation workflows[1][2][9].

Sources
[1] HumanEval Dataset: Code Synthesis Benchmark - Emergent Mind https://www.emergentmind.com/topics/humaneval-dataset
[2] Create RAG Datasets - SWE-bench https://www.swebench.com/SWE-bench/guides/create_rag_datasets/
[3] SWE-bench Datasets https://www.swebench.com/SWE-bench/guides/datasets/
[4] Human Eval - Unitxt https://www.unitxt.ai/en/main/catalog/catalog.cards.human_eval.html
[5] Human Eval — Unitxt https://www.unitxt.ai/en/1.15.9/catalog/catalog.cards.human_eval.html
[6] openai/openai_humaneval · Datasets at Hugging Face https://huggingface.co/datasets/openai/openai_humaneval
[7] scaleapi/SWE-bench_Pro-os: SWE-Bench Pro - GitHub https://github.com/scaleapi/SWE-bench_Pro-os
[8] Building Repo Bench – Repo Prompt Blog https://repoprompt.com/blog/building-repo-bench
[9] [PDF] REPOBENCH: BENCHMARKING REPOSITORY-LEVEL CODE ... https://proceedings.iclr.cc/paper_files/paper/2024/file/d191ba4c8923ed8fd8935b7c98658b5f-Paper-Conference.pdf
[10] RepoBench: Benchmarking Repository-Level Code Auto ... - GitHub https://github.com/Leolty/repobench
