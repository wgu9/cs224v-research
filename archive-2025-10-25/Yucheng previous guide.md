# 2025-10-22 1st meeting with Yucheng

- Meeting with **Yucheng** to review project direction and define a deliverable for the next 5–6 weeks.

## **Original Plan → Recent Shift**

- **Original**: Auto-generate a **survey paper** before a cutoff date; compare to a human-written survey published afterward.
- **Recent tweaks** (after Monica’s feedback):
    1. **Narrow scope** to two domains: **NLP** and **A/B testing**.
    2. Emphasize **terminology consistency** across papers/authors.

## **Yucheng’s Core Feedback**

- Survey writing, trip planning, and market analysis are **similar “report-generation” tasks**.
- **De-emphasize terminology alignment/knowledge-graph work**: high effort, narrow audience, likely out of scope.
- Refocus on the **original theme: Agent Memory**—learning from past experience to improve future outputs:
    - Two pillars: **cross-session memory** and **feedback** (human + reward).
    - Learning loop: **learn from past → decontextualize (abstract) → re-contextualize (apply to new tasks)**.

## **Why Not Terminology-Only Approaches**

- Pure embedding/Jaccard/K-means won’t capture **method-level abstraction**; hard to deliver impactful research within a quarter.

## **Examples Clarifying the Memory Paradigm**

- **Market analysis (AAPL)**: Don’t memorize “Apple↔OpenAI”; abstract to **“track key partners/cross-industry collaborations & hot topics.”**
    
    → This becomes **self-evolving** memory that updates its abstraction/granularity over time.
    
- **TikTok/YouTube recsys analogy**: Traditional short-horizon preference learning ≠ **long-horizon deep research**, which needs **concept induction & abstraction**.

## **On Survey-Paper Track**

- **Pros**: Clear “ground truth” (human survey) for evaluation.
- **Cons**: Hard to learn high-level abstractions; may exceed quarter scope and current LLM limits.
- Suggestion: Consider **market analysis/travel planning** as more tractable demos; survey paper can be a **small validation** path.

## **Deliverable & Process**

- Aim for a **demo** (or paper draft if feasible) in ~5–6 weeks.
- **Notion** for high-level notes, decisions, and tracking; Zoom okay for remote.

## **Next Steps (high level)**

1. **Choose the primary task** (recommended: **market analysis**; survey writing optional as a lightweight comparison).
2. **Survey recent work** on **self-evolving agents / cross-session memory** and define **evaluation** (coverage, accuracy, novelty, human preference, etc.).
3. Implement a **minimal pipeline**: initial report → human/heuristic feedback → **decontextualized “experience units”** → apply to a new case → measure gains.
4. Document progress/insights in **Notion**.

**Bottom line:** Shift focus from terminology alignment to **agent memory with feedback**. Build a tractable **long-horizon learning** demo (preferably **market analysis**) that shows **experience → abstraction → transfer**.

Appendix: Photos 

![224D4859-AEAD-4011-9745-94C972FB1C9D.heic](2025-10-22%201st%20meeting%20with%20Yucheng/224D4859-AEAD-4011-9745-94C972FB1C9D.heic)

![8508050A-53AC-4457-9204-3B66BEA8E0EC.heic](2025-10-22%201st%20meeting%20with%20Yucheng/8508050A-53AC-4457-9204-3B66BEA8E0EC.heic)

![14FB4410-3239-49C4-8D27-085503B4EF6B.heic](2025-10-22%201st%20meeting%20with%20Yucheng/14FB4410-3239-49C4-8D27-085503B4EF6B.heic)

![931DBE5D-B2DC-4DE5-B8B7-F17101F44DE4.heic](2025-10-22%201st%20meeting%20with%20Yucheng/931DBE5D-B2DC-4DE5-B8B7-F17101F44DE4.heic)

Market analysis

Stock Apple:

Look at apple today vs apple 1 month ago

Decontextualize the memory → know better investing strategy

LLM must update and revise memory based on new information

Example (hypothetical): 

News source: Apple buys OpenAI for $3 trillion

Prompt: talk to me about Apple’s investments

LLM Response: ……, Apple brought OpenAI

1 week later

News source: Apple sells OpenAI

Hypothetical project ideas:

- Market Analysis
- Coding README (create agentic README that reads all code files). Knows what code is more important than the other parts of the code)