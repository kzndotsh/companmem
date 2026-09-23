# Context and scaffolding

What sits in the prompt, separate from memory. Index: [Questions](QUESTIONS.md).

Answers are working notes. Citations are inline links. A question stays `open` until it has a falsifier.

---

## Prompt engineering, context & scaffolding

*Audited against [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) (cloned 2026-09-11).*

- What is **prompt engineering** vs **context engineering**?
  - **Prompt engineering:** crafting instructions and examples for one or few LLM calls ([PEG: elements of a prompt](https://www.promptingguide.ai/introduction/elements)).
  - **Context engineering:** designing the *full* context window — system prompt, tools, RAG, memory, state, structured I/O, eval loops ([PEG: context engineering guide](https://www.promptingguide.ai/guides/context-engineering-guide); [Karpathy](https://x.com/karpathy/status/1937902205765607626) cited therein).
  - For companions: memory is only half the problem; how retrieved facts are **stuffed and instructed** is the other half.

- What are the **elements of a prompt**?
  - **Instruction** — what to do ([PEG: elements](https://www.promptingguide.ai/introduction/elements)).
  - **Context** — external info steering the model (includes retrieved memories).
  - **Input data** — user message / query.
  - **Output indicator** — format or type expected (sentiment label, JSON, etc.).

- What is a **reader** vs **memory store** vs **prompt scaffold**?
  - **Store:** persists facts across sessions (vector DB, files, graph).
  - **Reader:** policy that selects, orders, and formats what enters context this turn.
  - **Scaffold:** system prompt + instructions + tool defs that tell the model how to use what it sees ([PEG: layered context — system / task / tool / memory](https://www.promptingguide.ai/agents/context-engineering)).
  - Fair eval must hold scaffold + reader constant when comparing stores ([Harbor task model](https://www.harborframework.com/docs/run-jobs/run-evals)).

- Does **where** retrieved text sits in the prompt matter?
  - Yes. LLMs attend more to start and end of long context; middle gets lost ([Liu et al., *lost in the middle*](https://arxiv.org/abs/2307.03172); [PEG RAG survey](https://www.promptingguide.ai/research/rag): relocate relevant chunks to edges).
  - Recall also varies with small prompt changes ([Machlab & Battle, 2024](https://arxiv.org/abs/2404.08865); [PEG summary](https://www.promptingguide.ai/research/llm-recall)).

- Do **sampling settings** (temperature, top-p) affect memory behavior?
  - Yes. Lower temperature → more deterministic, factual-sounding replies; higher → more varied/creative ([PEG: LLM settings](https://www.promptingguide.ai/introduction/settings)).
  - Companion tension: consistency wants low temperature; lively dialogue may want higher — memory errors vs voice drift.

- What is **context dilution**?
  - Stale, redundant, or irrelevant tokens in the window that hurt performance ([PEG: context engineering guide](https://www.promptingguide.ai/guides/context-engineering-guide): "filtering out noisy information").
  - Needs eval to detect — not visible from retrieval score alone.

- What is **context caching** vs **long-term memory**?
  - **Caching:** reuse preprocessed context within a session/TTL to cut cost/latency ([Gemini context caching](https://ai.google.dev/gemini-api/docs/caching); [PEG guide](https://www.promptingguide.ai/applications/context-caching)).
  - **Memory:** persists across sessions. Caching optimizes repeated reads; memory optimizes cross-session continuity.

- What are **Naive / Advanced / Modular RAG**?
  - **Naive:** index → retrieve → generate; suffers low precision/recall, redundancy ([Gao et al. survey](https://arxiv.org/abs/2312.10997); [PEG RAG research](https://www.promptingguide.ai/research/rag)).
  - **Advanced:** pre-retrieval (chunking, metadata), post-retrieval (re-rank, compress, relocate).
  - **Modular:** pluggable modules — search, memory, fusion, routing, Self-RAG, etc.

- Does **chunking** change what gets remembered?
  - Yes. Chunk size/strategy changes what embeds and retrieves together ([PEG RAG survey](https://www.promptingguide.ai/research/rag): chunking is first-class design choice).
  - Wrong chunks → right fact stored but never retrieved for the query.

- When does the model **ignore retrieved memory**?
  - **Faithfulness tug-of-war:** correct retrieval fixes most errors; wrong or contradicting context can lose to strong model priors ([Wu et al., 2024](https://arxiv.org/abs/2404.10198); [PEG summary](https://www.promptingguide.ai/research/rag-faithfulness)).
  - Model may over-rely on augmented text or parrot it without integrating ([Gao et al.](https://arxiv.org/abs/2312.10997): generation overly dependent on retrieved passages).

- Should the system **always retrieve**?
  - No. **Adaptive / active retrieval** decides when and what to fetch ([FLARE](https://arxiv.org/abs/2305.06983); [Self-RAG](https://arxiv.org/abs/2310.11511) — [PEG RAG survey](https://www.promptingguide.ai/research/rag)).
  - Companion analog: social silence = retrieve but do not speak; or do not retrieve at all this turn.

- What is **prompt injection** and why does it matter for memory?
  - Untrusted user text concatenated with trusted instructions → model follows attacker intent ([PEG: adversarial](https://www.promptingguide.ai/risks/adversarial); [Simon Willison, 2022](https://simonwillison.net/2022/Sep/12/prompt-injection/)).
  - **Jailbreak / roleplay** (DAN, etc.) can override persona — same class as persona poisoning ([PEG: jailbreaking](https://www.promptingguide.ai/risks/adversarial)).
  - Defenses partial: instruction hardening, parameterizing inputs, fine-tuned models, moderation ([PEG adversarial defenses](https://www.promptingguide.ai/risks/adversarial)).

- What is **prompt leaking**?
  - Attacks designed to exfiltrate system prompt or private context ([PEG: adversarial](https://www.promptingguide.ai/risks/adversarial)).
  - Relevant if companion system prompts contain hidden rules or other users' data.

- What is the **Reflexion** pattern?
  - Agent loop: act → evaluate → verbal self-reflection → store in memory → retry ([Shinn et al., 2023](https://arxiv.org/pdf/2303.11366.pdf); [PEG: reflexion](https://www.promptingguide.ai/techniques/reflexion)).
  - Uses short-term trajectory + long-term verbal memory; sliding window limits noted in guide.

- **Workflow vs agent** — which is a companion?
  - **Workflow:** predefined code paths, predictable ([PEG: workflows vs agents](https://www.promptingguide.ai/agents/ai-workflows-vs-ai-agents)).
  - **Agent:** LLM directs its own tool use and steps.
  - Memory **store** can be workflow; **speak** layer may be agent. Hybrids common ([PEG: prompt chaining, routing, orchestrator patterns](https://www.promptingguide.ai/agents/ai-workflows-vs-ai-agents)).

- What agent **components** matter besides memory?
  - **Planning** (decompose, reflect), **tools**, **memory** (short vs long) — three pillars ([PEG: agent components](https://www.promptingguide.ai/agents/components)).
  - Companion failures often blamed on memory when planning or tool policy is wrong ([PEG: deep-dive agent forgot searches](https://www.promptingguide.ai/agents/context-engineering-deep-dive)).

- How do you iterate on the speak layer?
  - Deploy → observe failures → refine prompts/constraints → measure ([PEG: context engineering iteration](https://www.promptingguide.ai/agents/context-engineering)).
  - Metrics: task completion, behavioral consistency, error rate, debugging time ([PEG: measuring success](https://www.promptingguide.ai/agents/context-engineering)).
  - Avoid over-constraint (brittle) and under-specification (chaotic) ([PEG: pitfalls](https://www.promptingguide.ai/agents/context-engineering)).

- RAG vs **fine-tuning** — when which?
  - **RAG:** fresh/external knowledge without retraining ([PEG RAG survey](https://www.promptingguide.ai/research/rag)).
  - **Fine-tuning:** internal knowledge, format, tone, complex instruction following.
  - Often combined; not mutually exclusive ([Gao et al.](https://arxiv.org/abs/2312.10997)).

---
