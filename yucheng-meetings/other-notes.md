2025-10-28 
jeremy_gu
  3:46 PM
Hi Yucheng,
Hope you’re doing well. I’ve copied my project proposal into Notion here:
https://www.notion.so/Jeremy-s-project-29974e3ea003800f9350ca8942c34f19
Would you have 20–30 minutes this week to meet? I’m happy to meet in person or on Zoom—whichever is easier for you. I can accommodate your availability.
I’m currently focusing on Q1 and would love your feedback on evaluation design and metrics. For context, the three questions I’m studying are:
WIP. Context Drift – Agents stray from the original objective during multi-step tasks (e.g., unnecessary refactors, irrelevant code paths). I've created a first set of code and testing SWE Bench Lite for now.
(not started) Zero Cross-Session Learning – Each session starts from scratch; agents don’t leverage previously solved problems to accelerate future tasks.
(not started) Static Abstraction – One-size-fits-all responses that don’t adapt to user expertise or task complexity.
Thanks so much for your time—please let me know what works for you.
Best,
Jeremy Gu


yucheng_jiang
  8:25 PM
Let's meeting during our previously scheduled time (edited) 


jeremy_gu
  8:38 PM
Thanks, Yucheng. I really appreciate it. I'll be there at the office tomorrow 12:20pm. Is this correct?


yucheng_jiang
  8:58 PM
yep

2025-10-29
jeremy_gu
  12:25 PM
https://www.notion.so/Jeremy-s-project-29974e3ea003800f9350ca8942c34f19


yucheng_jiang
  12:51 PM
https://arxiv.org/pdf/2504.07971
12:54
https://arxiv.org/pdf/2505.02820



2025-10-29 session
本次会议主要讨论了以下几个方面，现做详细说明：

AI上下文漂移（Context Drift）问题的定义和重要性
会议重点讨论了在长流程智能体任务（如代码自动化、API调用等）中，AI系统经常“跑偏”而未持续朝预期目标推进的现象。大家认为明确“什么是context drift”及其具体表现非常关键。

Drift检测的指标与评价标准
Jeremy提出用四个“guard”（守卫指标）来衡量AI的偏离程度，包括：

是否完成原定scope内的问题
是否按照既定计划执行
是否能通过相应测试
操作是否有充分证据支撑
讨论过程中，大家认为还需扩展和规范这些指标，例如：是否反复犯同样错误、是否错误调用工具、操作范围定义等。
借鉴“model card”思路系统化检测标准
Yucheng建议，可参考机器学习领域“model card”的形式，把“上下文漂移检测指标”做成卡片式维度定义，把每一项的含义、评价方式、应用范围标准化，提升方法的通用性与可解释性。

相关文献与benchmark调研
会议梳理了当前业界广泛用的评测集如SWBench、WebArena、TAUBench等，并建议调研文献中已有的相关定义和评测方法，为后续工作夯实理论基础。

实验与资源安排
讨论了实验的本地和云端成本，建议优先利用benchmark已有轨迹数据先行开发和评估漂移检测的方法，而不是盲目大规模新数据跑实验。

后续计划与任务分工

Jeremy负责整理文献，梳理上下文漂移定义与维度指标，并率先在SWBench、WebArena等benchmark上实例化评测方法。
团队会根据Jeremy的梳理结果，继续细化检测与评估标准，实现多轮迭代。
在完成定义和检测指标梳理后，再推进漂移修正算法的研究和实验。
整体来看，会议从“问题定义—标准规范—资源选择—行动计划”形成了清晰的研究推进路径，强调了基础理论和方法先行，稳步向后续实验开发过渡。

------
# Q1-Only Focus — Meeting Minutes & Next Steps

**Date:** 2025-10-29

**Attendees:** Yucheng (CS224v), Jeremy

## One-line takeaway

**Shift from “Q1+Q2” to “Q1-only: Context Drift Detection.”** Treat drift detection as a standalone, paper-worthy problem.

## Key decisions

- **Primary scope this quarter:** In-session **Context Drift Detection** (Q1).
    - Not do: Defer cross-session learning/reuse (Q2/Q3).
- **Formalization first:** Write a precise **definition** of “context drift” and a small **metric suite** (dimensions + how to instantiate).
- **Generalization target:** Validate across **3 benchmarks**
    - SWE-bench Verified, **TAU Bench**, **WebArena**.
- **Data strategy:** Prefer **existing trajectories/logs** over re-running agents (cost/time).
    - Not now: Use evaluator/Docker only when needed.
- **New dimension to add:**
    - **Repetitive Mistakes** (looping/failure recurrences), especially salient in WebArena/TAU.

## Clarifications / guardrails

- **Gold-only self-check**: do not compute drift; record as **N/A** (sanity of pipeline only).
- **Resolved metric**: use **official evaluator + Docker**.

## Immediate next steps (this week)

1. **Literature survey (P0, today start)**
    - Search: “context drift”, “goal drift”, “trajectory evaluation”, “long-horizon agents”.
2. **Explore TAU Bench (P0)**
    - Read tasks, check if **public trajectories** exist; gather notes on metrics mapping.

## Risks / assumptions

- Availability/format of open trajectories; potential effort to normalize logs.
- Metric generalization across benchmarks; threshold calibration.
- Cost/time of evaluator runs; keep subsets small.

Deliverable

[Context Drift Detection Framework](https://www.notion.so/Context-Drift-Detection-Framework-29c74e3ea00380d9aa83d5d070b754bb?pvs=21)

-----
jeremy_gu
  7:31 PM
Thank you Yucheng for today's session.
Our meeting notes is here: 2025-10-29
Following our meeting, I've completed the initial framework for Context Drift detection. Key deliverables: 
1. Formal definition with 3 orthogonal dimensions 
2. Detection cards for each dimension
Looking forward to your thoughts!
Best,
Jeremy
7:31
In the meanwhile, I'll continue to research the datasets tomorrow and Friday (edited) 


yucheng_jiang
  8:12 PM
sounds good! I'll take a look later tonight
8:12
for those papers, how did you find them? Could you attach the link to the paper?

2025-10-30
jeremy_gu
  10:44 AM
yes, happy to
10:44
I use chatgpt deep research and gemini


jeremy_gu
  9:44 PM
Hi Yucheng - Here is the table of papers I did resarch on. The top 10 papers have links
https://www.notion.so/2025-10-30-research-papers-29b74e3ea003807c8c81e993575de161

2025-11-2
jeremy_gu
  5:21 PM
Hi Yucheng,
Do you have 15–20 minutes on Monday to touch base on the next steps?
No worries if not — I just want to make some progress before our regular meeting on Wednesday. I’ve prepared the paper reading summary, and last time the drift definition was my to-do.
Just wanted to check if there’s anything else I can work on before then.


yucheng_jiang
  5:35 PM
is notion page updated? I can give feedback asynchronously. My schedule is quick packed on Mondays.
:yes__:
1


1 reply
3 days agoView thread
New


yucheng_jiang
  8:04 PM
sounds good. Which one is the best place to find the context drift definition and identification criteria?

2025-11-3
jeremy_gu
  12:57 PM
Here please. https://www.notion.so/Context-Drift-Detection-Framework-29c74e3ea00380d9aa83d5d070b754bb
Context Drift is the measurable deviation of an agent's behavioral trajectory from specified objectives, manifesting across three orthogonal dimensions (Scope, Tool, Loop) during long-horizon task (session) execution.
What do you think?



Concept	Relationship	Our Extension
Goal Drift	Subset - Goal Drift ⊂ Scope Drift	We focus on execution process, not just final goal
Error Propagation	Causal - Error Propagation → Loop Drift	We focus on deviation patterns, not single errors
Hallucination	Orthogonal - Can cause Tool Drift	We focus on behavioral drift, not factual errors

2025-11-4
yucheng_jiang
  10:34 PM
Hi @jeremy_gu, let’s meet over zoom for tomorrow’s discussion; gates meeting room is still reserved for us - feel free to use it if you happen to be in gates.


jeremy_gu
  9:26 AM
Sounds good!


