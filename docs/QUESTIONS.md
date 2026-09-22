# Questions

The mission is to build the memory technology that makes the most human-like companion we can, then show it with a number someone else can rerun. We still do not know what we are shipping, and we still do not know what that number measures. The field map exists so we do not copy everyone else's extract-and-search pipeline. The missing piece is a number we would bet the company on. We get it by running the same situation on our companion and on other products, then reading a result someone else can run again. That number is what tells us the product.

Questions define what we are solving and set a foundation for the work. No order or priority yet. An example in `ROADMAP.md` or `README.md` is not the assignment.

Answers are working notes — revise as we learn. **Citations** are inline links; prefer primary sources (papers, specs, law) over blog posts when both exist.

---

## Research process

- How do you organize research?
  - Start from questions, not solutions. Group by theme (definitions, human behavior, tech, proof).
  - One doc per layer: questions → answers → decisions → experiments.
  - Revisit when new evidence contradicts an answer; tag status: settled / open / deferred.
  - Pressure-test proposals with the [Heilmeier Catechism](https://www.darpa.mil/about/heilmeier-catechism) (DARPA): eight questions on goals, state of art, novelty, impact, risks, cost, timeline, and success exams.

- How do you exhaust all options when attempting to solve groundbreaking complex problems?
  - Map the problem space before picking an architecture: definitions, failure modes, prior art, constraints ([Heilmeier #2–3](https://www.darpa.mil/about/heilmeier-catechism)).
  - Use structured comparison (same axis for every option) rather than reading products one by one — e.g. decompose memory into representation, extraction, retrieval, maintenance ([arxiv:2606.24775](https://doi.org/10.48550/arxiv.2606.24775)).
  - Stop when options cluster — then test whether the cluster is correct or a shared blind spot ([CMA / continuum memory](https://arxiv.org/pdf/2601.09913v1)).

- What is a **question** vs a **claim** vs **evidence** in our docs?
  - **Question:** something we do not know yet ("What is memory?").
  - **Claim:** a statement we believe ("RAG alone is not long-term memory") — cf. [CMA](https://arxiv.org/pdf/2601.09913v1): RAG treats memory as stateless lookup.
  - **Evidence:** source or observation that supports or falsifies a claim (paper, benchmark result, user report).

- What does "done" mean for a research item (answered, cited, falsifiable)?
  - **Answered:** we can state a position in plain language with at least one source or observation.
  - **Cited:** the source is linked and we know what it actually measured ([Heilmeier #8](https://www.darpa.mil/about/heilmeier-catechism): midterm and final "exams").
  - **Falsifiable:** we could imagine a test or counterexample that would change our mind.

- How do you know when you're answering the right question?
  - The answer changes what you would build, measure, or refuse to do ([Heilmeier #4](https://www.darpa.mil/about/heilmeier-catechism): "who cares?").
  - If the answer has no downstream effect, it may be trivia — defer it.

- How do you avoid optimizing for what's easy to measure?
  - [Goodhart's Law](https://www.cna.org/analyses/2022/09/goodharts-law): when a measure becomes a target, it ceases to be a good measure ([Strathern via MPRA](https://mpra.ub.uni-muenchen.de/90649/1/MPRA_paper_90649.pdf)).
  - Name what your metric does *not* capture before trusting a score.
  - Pair automated scores with behavioral probes ([Wispaper on LoCoMo limits](https://www.wispaper.ai/en/research/agent-memory-evaluation-beyond-completion)).
  - LoCoMo QA measures recall of facts in long chat — not timing, relationship feel, or character consistency ([Maharana et al., ACL 2024](https://aclanthology.org/2024.acl-long.747/)).

---

## Core definitions

- What is memory?
  - In AI systems: **persistent state across sessions** — not weights, not just the current prompt ([Pathak, 2025](https://ninadpathak.com/blog/context-windows-vs-memory/); [arxiv:2606.06448](https://doi.org/10.48550/arxiv.2606.06448): external memory decouples capacity from context length).
  - In humans: stored information retrievable later; **episodic** (events) vs **semantic** (facts) ([Tulving, 1972 via PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2952732/); [UCSF Memory Center](https://memory.ucsf.edu/brain-health/memory)).

- What is context?
  - Everything the model sees **in this one inference call** — system prompt, messages, retrieved chunks, tool results ([Atlan](https://atlan.com/know/memory-layer-vs-context-window/)).
  - Fixed token budget; cleared between calls unless you explicitly carry state forward ([Pathak](https://ninadpathak.com/blog/context-windows-vs-memory/)).
  - Analogized to **L1 cache**, not memory ([arxiv:2603.09023](https://arxiv.org/abs/2603.09023)).

- What is reasoning?
  - The model using in-context information to produce outputs — chain-of-thought, planning, tool use (inside one inference call).
  - Reasoning happens *inside* the call; memory is what you fetch *into* the call from outside ([Pathak](https://ninadpathak.com/blog/context-windows-vs-memory/); [Generative Agents planning loop](https://arxiv.org/abs/2304.03442)).

- What is a harness?
  - A controlled runner that feeds fixed tasks to a system and records outputs, rewards, cost, and errors ([Harbor docs](https://www.harborframework.com/docs/run-jobs/run-evals); [Harbor GitHub](https://github.com/harbor-framework/harbor)).
  - Separates agent + environment + verifier so comparisons stay fair ([Harbor task model](https://www.harborframework.com/docs/run-jobs/run-evals): instruction, environment, test script).
  - Context-engineering changes need eval pipelines to measure whether prompt/RAG tweaks actually work ([PEG: context engineering guide](https://www.promptingguide.ai/guides/context-engineering-guide)).

- What is the difference between **remembering** and **retrieving**?
  - **Retrieving:** pulling stored text/facts into context (mechanical) — standard RAG pipeline ([Lewis et al., 2020](https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf)).
  - **Remembering** (what users mean): the agent *acts as if* the past matters — right fact, right time, right tone ([LoCoMo-Conv / in-situ use](https://github.com/MiuLab/LoCoMo-Conv); [Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827) on inappropriate recall).
  - You can retrieve without remembering (wrong fact, creepy timing, generic reply).

- What belongs in memory vs what belongs only in the active turn?
  - **Active turn:** immediate intent, current scene, last few exchanges (working memory / context window).
  - **Memory:** stable facts, preferences, relationship history, things that should survive session end ([MemGPT virtual memory tiers](https://doi.org/10.48550/arxiv.2310.08560)).
  - Rule of thumb: if losing it next session would break continuity, it belongs in memory ([Pathak](https://ninadpathak.com/blog/context-windows-vs-memory/)).

- What is the difference between a **log** (everything that happened) and **memory** (what matters later)?
  - **Log:** append-only transcript — complete, heavy, noisy.
  - **Memory:** curated subset — extracted, summarized, typed, or forgotten ([Mem0 extract/consolidate/retrieve](https://doi.org/10.48550/arxiv.2504.19413)).
  - Humans do not replay full logs; they reconstruct gist ([Schuck & Doeller, *Nature Human Behaviour*, 2024](https://www.nature.com/articles/s41562-023-01799-z)).

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

## Primitives & storage (technical)

- What is RAG?
  - **Retrieval-Augmented Generation** ([Lewis et al., NeurIPS 2020](https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf)): retrieve relevant documents, generate conditioned on them.
  - Combines **parametric** memory (model weights) with **non-parametric** memory (external index).
  - Default pattern for knowledge-intensive tasks the model was not trained on ([Lewis et al.](https://arxiv.org/abs/2005.11401)).

- What are embeddings?
  - Fixed-length numeric vectors representing text meaning; similar meanings → nearby vectors ([Redis: vector embeddings](https://redis.io/blog/vector-embeddings-explained/); [ML Digest](https://ml-digest.com/text-embeddings-turning-language-into-meaningful-vectors/)).
  - Search: embed query + documents, rank by **cosine similarity** ([Inferbase](https://inferbase.ai/blog/what-are-embeddings)).

- What are vector databases?
  - Stores optimized for similarity search over embeddings (Pinecone, Qdrant, pgvector, etc.).
  - Often use **approximate nearest-neighbor** indexes — commonly **HNSW** ([Malkov & Yashunin, 2018](https://doi.org/10.1109/tpami.2018.2889473); [arxiv:1603.09320](https://arxiv.org/abs/1603.09320)).

- What other types of storage do people use?
  - **SQL/NoSQL** — structured facts, profiles ([Mem0 storage layer](https://doi.org/10.48550/arxiv.2504.19413)).
  - **Knowledge graphs** — entities + relationships + time ([Mem0g / Graphiti / Zep](https://www.graphlit.com/blog/survey-of-ai-agent-memory-frameworks)).
  - **Key-value / files** — persona sheets, lorebooks ([Letta core memory blocks](https://github.com/letta-ai/skills/blob/HEAD/letta/letta-api-client/memory-architecture.md); [MemGPT OS paging](https://doi.org/10.48550/arxiv.2310.08560)).
  - **Raw chat logs** — simplest "memory," hits context limits ([arxiv:2606.06448](https://doi.org/10.48550/arxiv.2606.06448)).

- What is MCP?
  - **Model Context Protocol** — open standard ([Anthropic announcement, Nov 2024](https://www.anthropic.com/news/model-context-protocol); [MCP spec](https://modelcontextprotocol.io/specification/2025-11-25/index)).
  - Client–server over JSON-RPC; servers expose **tools**, **resources**, **prompts**.
  - Described as "USB-C for AI integrations" ([MCP introduction](https://modelcontextprotocol.io/introduction)).

- How do tool calls work?
  - Model requests a tool → runtime executes → result injected into context → model continues ([OpenAI function calling guide](https://developers.openai.com/api/docs/guides/function-calling): five-step loop).
  - API does not execute functions; **your application** does ([OpenAI cookbook](https://developers.openai.com/cookbook/examples/how_to_call_functions_with_chat_models)).
  - Memory tools (search, add, delete) are one category; file/DB/API tools are others ([AgeMem tool-based memory ops](https://aclanthology.org/2026.acl-long.981/)).

- What is the speed "tax" when dealing with tool calls and similar things?
  - Each tool round-trip adds latency (network, DB, embedding search) ([OpenAI tool loop](https://developers.openai.com/api/docs/guides/function-calling)).
  - Memory-heavy agents often pay per-turn: extract → embed → retrieve → generate ([Mem0 paper](https://doi.org/10.48550/arxiv.2504.19413)).
  - Write-path and maintenance cost often dominate at long horizon ([arxiv:2606.24775](https://doi.org/10.48550/arxiv.2606.24775); [arxiv:2606.06448](https://doi.org/10.48550/arxiv.2606.06448): prefill scales with history).

- When a product says it has "memory," what is actually happening under the hood?
  - Usually one or more of: (1) recent chat in context, (2) extract facts to vector DB, (3) summarize sessions, (4) graph entities, (5) user-editable profile fields ([Graphlit survey, 2026](https://www.graphlit.com/blog/survey-of-ai-agent-memory-frameworks); [Mem0 ADD/UPDATE/DELETE](https://doi.org/10.48550/arxiv.2504.19413)).
  - Survey decomposes systems into representation, extraction, retrieval, maintenance ([arxiv:2606.24775](https://doi.org/10.48550/arxiv.2606.24775)).
  - "Memory" is marketing; ask which of the above and who writes/reads.

- What does the model's **pretraining** count as — memory or something else?
  - **World knowledge** in weights — not *your* session-specific memory ([Lewis et al.: parametric vs non-parametric](https://arxiv.org/abs/2005.11401)).
  - Can conflict with user facts; retrieval is meant to supply what weights lack ([RAG motivation](https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf)).

- How much do **cost, hardware, and infra** constrain what gets built?
  - Local vector DB + embedder + LLM per turn is expensive for consumers.
  - Mem0 reports ~91% lower p95 latency and >90% token savings vs full-context on LoCoMo ([Mem0, 2025](https://doi.org/10.48550/arxiv.2504.19413)).
  - Long context reduces retrieval need but increases $/token and still degrades in the middle ([Liu et al., *lost in the middle*](https://arxiv.org/abs/2307.03172); [arxiv:2606.06448](https://doi.org/10.48550/arxiv.2606.06448)).

---

## Convergence & approach

- Why have memory systems converged on similar approaches?
  - RAG proved external knowledge works without retraining ([Lewis et al., 2020](https://arxiv.org/abs/2005.11401)).
  - LLM context limits forced "store outside, retrieve inside" ([MemGPT](https://doi.org/10.48550/arxiv.2310.08560); [arxiv:2606.06448](https://doi.org/10.48550/arxiv.2606.06448)).
  - Generative Agents (2023) popularized observation → reflection → planning over a memory stream ([Park et al., UIST 2023](https://arxiv.org/abs/2304.03442)).
  - Vendor demos reinforce extract → embed → retrieve → generate ([Graphlit survey](https://www.graphlit.com/blog/survey-of-ai-agent-memory-frameworks)).

- Is that convergence a good sign or a shared blind spot?
  - Both. Mature building blocks exist.
  - Many systems still treat memory as **stateless lookup** — no update, forgetting, or temporal chaining ([CMA](https://arxiv.org/pdf/2601.09913v1)).
  - No single architecture wins all workloads ([arxiv:2606.24775](https://doi.org/10.48550/arxiv.2606.24775)).
  - RAG helps but retrieval quality — not storage — is often the bottleneck ([arxiv:2603.07670](https://arxiv.org/html/2603.07670v1)).

- Are we copying how the brain works because it's right, or because it's the familiar metaphor?
  - Often metaphor. MemGPT explicitly maps context to RAM and external store to disk ([Packer et al., 2023](https://doi.org/10.48550/arxiv.2310.08560)).
  - Tulving's episodic/semantic distinction inspires naming but not implementation ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2952732/)).
  - Brain memory is reconstructive and lossy — not a vector DB ([Schuck & Doeller, 2024](https://www.nature.com/articles/s41562-023-01799-z)).

- Is the destination wrong, or just the path everyone is taking?
  - **Open.** Likely both: *what* to store (ontology) and *how* to store it (RAG/graph/files).
  - CMA argues destination needs accumulation, mutation, disambiguation — not just retrieval ([arxiv:2601.09913](https://arxiv.org/pdf/2601.09913v1)).
  - Path may be wrong if bottleneck is read policy and social timing, not retrieval accuracy ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827)).

---

## Goals & use cases (whose memory?)

- What are we actually building for — companion, assistant, enterprise tool, research, something else?
  - **Open — not decided yet.** Must be explicit before architecture ([Heilmeier #1](https://www.darpa.mil/about/heilmeier-catechism)).

- Do different use cases need different kinds of memory?
  - Yes. Assistant: task state, preferences, docs. Enterprise: audit, ACLs, compliance ([GDPR Art. 17](https://gdpr-info.eu/art-17-gdpr/)). Companion: relationship continuity, character, tone ([Park et al., generative agents](https://arxiv.org/abs/2304.03442); [Nass & Moon, CASA](https://doi.org/10.1111/0022-4537.00153)).
  - Same storage can back different policies; the **policies** differ ([arxiv:2606.24775](https://doi.org/10.48550/arxiv.2606.24775): workload alignment).

- Can one system serve all of them?
  - One engine maybe; one **policy + eval** unlikely without compromise.
  - Products pick lanes: Mem0 = dev/agent memory ([arxiv:2504.19413](https://doi.org/10.48550/arxiv.2504.19413)); Character.AI = consumer companion ([user reports](https://www.reddit.com/r/CharacterAI/comments/1s5j419/the_memory_is_horrendous/)).

- What does "good enough" look like for each?
  - **Assistant:** correct recall when asked; minimal creepiness ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827)).
  - **Enterprise:** traceable, deletable, access-controlled ([GDPR](https://gdpr-info.eu/art-17-gdpr/); [Multigrid on erasure](https://multigrid.ai/learn/right-to-erasure-ai)).
  - **Companion:** feels continuous over weeks; character stable; social timing ([LoCoMo multi-session generation task](https://aclanthology.org/2024.acl-long.747/); [Maharana et al.](https://arxiv.org/abs/2402.17753)).
  - **Open:** our bar not set yet.

---

## Human communication & relationships

- What makes human communication feel human?
  - Turn-taking, shared context, emotional attunement, imperfection, shared-history references, appropriate omission.
  - People apply social scripts to computers — **Computers Are Social Actors** ([Nass & Moon, 2000](https://doi.org/10.1111/0022-4537.00153); [Reeves & Nass, *The Media Equation*](https://doi.org/10.30658/hmc.1.5) cited in [HMC review](https://doi.org/10.30658/hmc.1.5)).
  - Not just factual accuracy — timing and subtext matter ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827)).

- How do human memories actually work?
  - Encoding → consolidation → retrieval; hippocampus binds events; cortex stores long-term ([UCSF](https://memory.ucsf.edu/brain-health/memory); [PMC episodic system](https://pmc.ncbi.nlm.nih.gov/articles/PMC2882963/)).
  - Episodic vs semantic — interact but differ ([Tulving via PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2952732/)).
  - Recall is **reconstructive**, not playback ([Schuck & Doeller, 2024](https://www.nature.com/articles/s41562-023-01799-z); [UEA semantic-episodic review](https://ueaeprints.uea.ac.uk/id/eprint/72823/1/Accepted_manuscript.pdf)).

- How do relationships build continuity over time?
  - Accumulated shared experiences, inside references, trust, negotiated norms.
  - Generative Agents model this via memory stream + reflection over days of simulated life ([Park et al., 2023](https://arxiv.org/abs/2304.03442)).
  - Both facts and **relational state** (closeness, conflict, phase).

- What do people expect when someone "remembers" them?
  - Relevant recall without being asked — not interrogation-style Q&A ([LoCoMo-Conv: implicit/silent grounding](https://github.com/MiuLab/LoCoMo-Conv); [users-dont-ask paper](https://arxiv.org/abs/2609.03467)).
  - Proportional to intimacy ([personalization intrusiveness ladder](https://www.mdpi.com/2076-328X/15/10/1323)).

- When does recall feel caring vs creepy?
  - **Caring:** context-appropriate, relationship-proportional.
  - **Creepy:** too specific, wrong context, intimacy mismatch ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827); [MDPI personalization backfire](https://www.mdpi.com/2076-328X/15/10/1323)).
  - Example: wellness app recalling dog's name months later felt invasive ([r/VoiceAIBots](https://www.reddit.com/r/VoiceAIBots/comments/1lcqgps/that_creepy_feeling_when_ai_knows_too_much/)).

- What is the difference between knowing facts about someone and knowing *them*?
  - Facts: name, job, preferences. Knowing them: stress behavior, boundaries, shared rhythm.
  - LoCoMo tests factual QA over long chat — not relational knowing ([Maharana et al., 2024](https://aclanthology.org/2024.acl-long.747/)).

- What changes in a relationship over weeks and months — facts, tone, trust, shared history?
  - All of the above. LoCoMo spans up to 32 sessions / 600 turns with temporal event graphs ([Maharana et al.](https://arxiv.org/abs/2402.17753)).
  - Models still lag humans on long-range temporal/causal dynamics ([Maharana et al., ACL 2024](https://aclanthology.org/2024.acl-long.747/)).

- Which memory behaviors would count as "this knows me," so an eval author could turn each one into a task?
  - Working list for Phase 2. These are behaviors in a conversation. Store design stays under [What memory needs to do](#what-memory-needs-to-do).
  - **Same person after a gap.** A later session still has the name and the relationship. Users already complain when that breaks ([r/CharacterAI](https://www.reddit.com/r/CharacterAI/comments/1s5j419/the_memory_is_horrendous/); [wrong name and relationships](https://www.reddit.com/r/CharacterAI/comments/1pkyjke/whats_going_on_with_cais_memory/)).
  - **One relevant fact, not the whole store.** The next turn uses what the moment needs. It does not paste every saved memory. Field products often inject a labeled block ([Mem0 README](https://github.com/mem0ai/mem0): `User Memories:`) or the full file ([omemo README](https://github.com/OmniDimen/omemo)). LoCoMo-Conv's implicit queries ask whether the fact shows up in the reply when the user did not quiz for it ([LoCoMo-Conv](https://github.com/MiuLab/LoCoMo-Conv); [Chang & Chen](https://arxiv.org/abs/2609.03467)).
  - **A stated preference, used later, without a reminder.** Tell it once. About a week later, the plan should follow it. Assistant Benchmark's top memory anchor is unprompted preference apply. Forgetting by the next session is the low anchor ([memory dimension](https://assistantbenchmark.com/dimensions/memory)). PrefEval scores whether a stated preference survives filler turns. That is preference-following, not whether the recall felt caring ([PrefEval](https://arxiv.org/abs/2502.09597); [EVALS.md](EVALS.md)).
  - **A known fact, left unsaid.** The system can have the memory and still not bring it up. Inappropriate recall is its own failure ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827)). That paper does not give a task script. Assistant Benchmark's closest scored test is Proactive restraint, and it is about not acting, not about hiding a private memory ([proactive restraint](https://assistantbenchmark.com/dimensions/proactive_restraint)).
  - **One relationship does not leak into another.** A fact from character A does not show up with character B. Open products can scope by `user_id` ([Mem0 add](https://docs.mem0.ai/core-concepts/memory-operations/add)) or by project ([basic-memory](https://github.com/basicmachines-co/basic-memory): "Projects are separate knowledge bases"). A single `data/memories.json` does not ([omemo](https://github.com/OmniDimen/omemo)).
  - Fact QA on a long transcript is not this list. LoCoMo measures whether the answer matches the chat, not timing or relationship feel ([Maharana et al., 2024](https://aclanthology.org/2024.acl-long.747/)).
  - **Status:** open

---

## Studies & prior art

- What research exists on humanizing AI?
  - **CASA:** people mindlessly apply social rules to computers ([Nass & Moon, 2000](https://doi.org/10.1111/0022-4537.00153)).
  - **Media Equation:** people treat media as real social actors ([Reeves & Nass, 1996](https://doi.org/10.30658/hmc.1.5) — discussed in [HMC extension](https://doi.org/10.30658/hmc.1.5)).
  - **Creepiness of AI recall:** when memory feels intrusive ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827)).
  - **Open:** need fuller literature sweep (parasocial interaction, disclosure, attachment).

- What research exists on AI memory?
  - **RAG** — [Lewis et al., NeurIPS 2020](https://arxiv.org/abs/2005.11401).
  - **MemGPT / Letta** — virtual context management, OS-style paging ([Packer et al., 2023](https://doi.org/10.48550/arxiv.2310.08560); [Letta blog](https://www.letta.com/blog/memgpt-and-letta/)).
  - **Generative Agents** — memory stream, reflection, planning ([Park et al., UIST 2023](https://arxiv.org/abs/2304.03442)).
  - **Mem0** — extract, consolidate, retrieve on LoCoMo ([Chhikara et al., 2025](https://doi.org/10.48550/arxiv.2504.19413)).
  - **LoCoMo** — very long multi-session eval ([Maharana et al., ACL 2024](https://aclanthology.org/2024.acl-long.747/)).
  - **AgeMem** — unified LTM/STM via RL tool actions ([Yu et al., ACL 2026](https://aclanthology.org/2026.acl-long.981/)).
  - **Surveys** — [arxiv:2603.07670](https://arxiv.org/html/2603.07670v1); [arxiv:2606.24775](https://doi.org/10.48550/arxiv.2606.24775).
  - **CMA** — RAG lacks update/forget/temporal chaining ([arxiv:2601.09913](https://arxiv.org/pdf/2601.09913v1)).

- What do users complain about in real products?
  - Forgetting plot within a few messages ([r/CharacterAI](https://www.reddit.com/r/CharacterAI/comments/1s5j419/the_memory_is_horrendous/)).
  - Pinned memories not working; pins ≠ lorebooks ([r/CharacterAI](https://www.reddit.com/r/CharacterAI/comments/1qkrunu/pinned_memories_are_acting_up_i_think/)).
  - Wrong gender, name, relationships; turn-to-turn contradiction ([r/CharacterAI](https://www.reddit.com/r/CharacterAI/comments/1pkyjke/whats_going_on_with_cais_memory/)).
  - Desire for lorebooks / long-term consistency ([r/CharacterAI official update thread](https://www.reddit.com/r/CharacterAI/comments/1q8j7ec/an_update_on_memory_box_and_pinned_chat_issues/)).
  - LoCoMo shows even RAG systems lag humans on long-horizon chat ([Maharana et al., 2024](https://aclanthology.org/2024.acl-long.747/)) — industry UX reflects that gap.

---

## Landscape & market

- What exists today — apps, libraries, frameworks, patterns?
  - **Consumer:** Character.AI, Replika, Nomi, Kindroid, Chai (product sites; user discourse on [r/CharacterAI](https://www.reddit.com/r/CharacterAI/)).
  - **Libraries:** Mem0 ([paper](https://doi.org/10.48550/arxiv.2504.19413)), Zep/Graphiti, LangMem, Cognee, Letta ([MemGPT lineage](https://www.letta.com/blog/memgpt-and-letta/)), Honcho, Supermemory, Memobase, LlamaIndex memory blocks ([Graphlit survey, 2026](https://www.graphlit.com/blog/survey-of-ai-agent-memory-frameworks)).
  - **Clients:** SillyTavern (lorebook + extensions).
  - **Patterns:** RAG, graph memory, compiled profile, file-based persona, session summary ([arxiv:2603.07670](https://arxiv.org/html/2603.07670v1)).

- What does "best" even mean in this space?
  - Depends on goal: recall accuracy, latency, cost, privacy, character consistency, dev ergonomics.
  - No universal winner — workload-dependent ([arxiv:2606.24775](https://doi.org/10.48550/arxiv.2606.24775)).
  - Mem0 optimizes LoCoMo QA + cost ([Chhikara et al., 2025](https://doi.org/10.48550/arxiv.2504.19413)) — different bar than companion feel.

- Why are there so many products?
  - LLMs made chat companions cheap to ship ([Park et al., 2023](https://arxiv.org/abs/2304.03442) showed believable multi-day agent behavior).
  - Memory is hard and differentiated ([arxiv:2606.24775](https://doi.org/10.48550/arxiv.2606.24775)).
  - Open-source libs lower barrier ([Mem0](https://doi.org/10.48550/arxiv.2504.19413), [Letta](https://github.com/letta-ai/letta)).

- Is that a sign the problem is unsolved, or that the market is fragmented?
  - Both. Core mechanics unsettled ([CMA on RAG limits](https://arxiv.org/pdf/2601.09913v1)).
  - User complaints persist ([r/CharacterAI](https://www.reddit.com/r/CharacterAI/comments/1s5j419/the_memory_is_horrendous/)).
  - UX and monetization also fragment the market.

---

## What memory needs to do

- What should **persist** when a conversation ends?
  - Salient facts, preferences, milestones, explicit "remember this" ([Mem0 extraction pipeline](https://doi.org/10.48550/arxiv.2504.19413)).
  - Field OSS default: LLM-extracted facts, not the raw transcript ([Mem0 add](https://docs.mem0.ai/core-concepts/memory-operations/add): "Mem0 sends the messages through an LLM that pulls out key facts").
  - File-as-truth alternative: markdown entities on disk ([basic-memory README](https://github.com/basicmachines-co/basic-memory): Entity / Observations / Relations).
  - Generative Agents persist observations, reflections, plans in memory stream ([Park et al., 2023](https://arxiv.org/abs/2304.03442)).
  - Not every message — that's a log ([Schuck & Doeller, 2024](https://www.nature.com/articles/s41562-023-01799-z)).
  - **Status:** open

- How should stored memory be **retrieved** into the next turn?
  - Field default: search, then inject a labeled block into the prompt ([Mem0 README](https://github.com/mem0ai/mem0): "Answer the question based on query and memories" with `User Memories:`).
  - Same store can still dump everything ([omemo README](https://github.com/OmniDimen/omemo): full injection of all memories vs RAG filter).
  - **Status:** open

- What is the **unit** of a memory — a fact, an event, a feeling, a phase?
  - Most products: **untyped text blobs** or atomic facts ([Mem0](https://doi.org/10.48550/arxiv.2504.19413); [Graphlit survey](https://www.graphlit.com/blog/survey-of-ai-agent-memory-frameworks)).
  - Humans: episodic events vs semantic facts ([Tulving via PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2952732/)).
  - **Open:** companion systems may need multiple units.

- What should be **optional** to remember vs **essential**?
  - **Essential:** safety boundaries, explicit remember requests, core identity ([Letta persona/human blocks](https://github.com/letta-ai/skills/blob/HEAD/letta/letta-api-client/memory-architecture.md)).
  - **Optional:** throwaway banter, hypotheticals, scene detail.
  - **Open:** full policy not written.

- What does it mean to **forget** — gone, hidden, or just not brought up?
  - **Delete** from store ([Mem0 DELETE op](https://doi.org/10.48550/arxiv.2504.19413); [GDPR Art. 17](https://gdpr-info.eu/art-17-gdpr/)).
  - **Suppress** at retrieve time (not surfaced): Mem0 hides `expiration_date` rows unless `show_expired` ([add docs](https://docs.mem0.ai/core-concepts/memory-operations/add)).
  - **Invalidate, keep history:** Graphiti marks old facts invalid rather than deleting them ([README](https://github.com/getzep/graphiti): "old facts are invalidated — not deleted").
  - **Omit** in generation (know but don't say) — [Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827) on inappropriate recall.
  - Users may mean any of the three.
  - **Status:** open

- What happens when two memories **conflict**?
  - Need supersession: newer wins, user retcon wins, quarantine, ask user.
  - RAG default: embedding similarity picks one — poor for contradictions ([CMA](https://arxiv.org/pdf/2601.09913v1): no conflict resolution in read-only retrieval).
  - Mem0 paper describes ADD/UPDATE/DELETE against similar memories ([Chhikara et al., 2025](https://doi.org/10.48550/arxiv.2504.19413)); OSS add docs also say new memories are added without overwriting existing ones ([Mem0 add](https://docs.mem0.ai/core-concepts/memory-operations/add)).
  - Temporal graphs stamp `invalid_at` on the old edge ([Graphiti README](https://github.com/getzep/graphiti): contradiction handling via temporal invalidation).
  - **Status:** open

- Who **owns** memories — user, character, platform?
  - **Legal:** user rights under GDPR; controller/processor roles ([Art. 17](https://gdpr-info.eu/art-17-gdpr/); [SiteGPT on chatbot DSARs](https://sitegpt.ai/resources/chatbot-data-subject-requests)).
  - **Technical:** embeddings/logs deletable; weights much harder ([Multigrid](https://multigrid.ai/learn/right-to-erasure-ai); [Springer RTBF + LLMs](https://link.springer.com/article/10.1007/s43681-024-00573-9)).
  - **In fiction:** character "remembers"; user controls canon.
  - **Open:** product policy.

- What is **consistency** — and when is inconsistency a bug vs acceptable?
  - **Bug:** contradicts established facts without narrative reason ([LoCoMo adversarial QA category](https://arxiv.org/abs/2402.17753)).
  - **Acceptable:** deliberate growth, unreliable narrator, human-like fuzzy recall ([Schuck & Doeller, 2024](https://www.nature.com/articles/s41562-023-01799-z)).
  - Perfect consistency can feel robotic ([Nass & Moon on social expectations](https://doi.org/10.1111/0022-4537.00153)).

- Is **perfect recall** desirable?
  - Usually no. Humans forget and reconstruct ([Schuck & Doeller, 2024](https://www.nature.com/articles/s41562-023-01799-z)).
  - Total recall can feel uncanny ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827)).

- When someone says "you forgot" — what are they usually upset about?
  - Broken continuity (plot, name, relationship) — [r/CharacterAI](https://www.reddit.com/r/CharacterAI/comments/1s5j419/the_memory_is_horrendous/).
  - Ignored emotional moment or feeling unseen.
  - Not always "missing from DB" — sometimes wrong timing ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827)).

- What should the system do with **jokes, hypotheticals, and roleplay** — same as facts?
  - Risky if stored as facts. Extractors often flatten epistemic status.
  - LoCoMo includes adversarial/false-premise questions ([Maharana et al., 2024](https://aclanthology.org/2024.acl-long.747/)) — related but not joke ontology.
  - **Open:** write policy needed.

- What is **lore/backstory** vs something that actually happened in conversation?
  - **Lore:** author-defined bible — not experienced in chat (SillyTavern World Info pattern; [Graphlit on ST lore vs RAG](https://www.graphlit.com/blog/survey-of-ai-agent-memory-frameworks)).
  - **Lived:** events in sessions between user and character ([LoCoMo event graphs grounded in dialogue](https://aclanthology.org/2024.acl-long.747/)).
  - Conflating → false autobiography ("I remember when I…").

- Can one user's relationship with two characters share information — should it?
  - **Technically:** easy to leak with shared `user_id` / agent bag ([Mem0 scopes user/agent/session](https://doi.org/10.48550/arxiv.2504.19413) — isolation is a design choice).
  - OSS extract-retrieve products pass `user_id` (and often `run_id`) on add/search ([Mem0 add](https://docs.mem0.ai/core-concepts/memory-operations/add)).
  - File stores isolate by **project**, not character ([basic-memory](https://github.com/basicmachines-co/basic-memory): "Projects are separate knowledge bases").
  - Flat JSON with no user key is a miss ([omemo](https://github.com/OmniDimen/omemo): `data/memories.json`).
  - Graph `group_id` is a partition, not automatically a tenant ([Graphiti docs](https://help.getzep.com/graphiti/llms.txt): isolated graph namespaces; Falkor shared-driver failure in [issue #1795](https://github.com/getzep/graphiti/issues/1795)).
  - **Socially:** usually **no** — separate relationships unless opt-in.
  - Default: isolate per character/relationship.
  - **Status:** open

- What **clusters** show up in shipped products (same axes, not 61 novels)?
  - Extract-then-retrieve with `user_id` / `run_id` filters ([Mem0 add](https://docs.mem0.ai/core-concepts/memory-operations/add); [README](https://github.com/mem0ai/mem0): `User Memories:` in the prompt). Same pattern with a **namespace tuple** and manage/search tools ([LangMem README](https://github.com/langchain-ai/langmem): `create_manage_memory_tool` / `create_search_memory_tool`). Profile+event backend: structured slots and a timeline, blobs dropped after flush, retrieve scaffold stays quiet unless relevant ([Memobase README](https://github.com/memodb-io/memobase)).
  - Temporal graph: invalidate old edges, keep history, partition with `group_id` ([Graphiti README](https://github.com/getzep/graphiti): "old facts are invalidated — not deleted"; `group_id` as graph partition).
  - File-as-truth: markdown entities on disk, isolated by **project** ([basic-memory README](https://github.com/basicmachines-co/basic-memory): Entity / Observations / Relations; `basic-memory project add`). ReMe: daily topic `.md` plus filtered `session/dialog/*.jsonl`, `proactive_read` is opt-in ([ReMe README](https://github.com/agentscope-ai/ReMe)).
  - Agent MemFS: git-tracked memory blocks scoped by `agentId` ([Letta Code](https://github.com/letta-ai/letta-code): `getScopedMemoryFilesystemRoot`).
  - Unscoped file: one `data/memories.json` ([omemo README](https://github.com/OmniDimen/omemo)) or default `memory.jsonl` ([MCP memory server](https://github.com/modelcontextprotocol/servers)) — isolation miss for a companion. MCP also ships a "Remembering..." always-retrieve prompt.
  - Closed apps still lack a primary write-path spec; do not copy/refuse from marketing.
  - **Status:** open

- When is a stored fact **spoken**, and when does it stay silent?
  - Field default is to search and inject a block ([Mem0 README](https://github.com/mem0ai/mem0): `User Memories:`).
  - One profile store stays quiet unless the fact is relevant ([Memobase README](https://github.com/memodb-io/memobase)).
  - Saying a true fact at the wrong time is its own failure ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827)).
  - The 25 evals score whether the fact came back. They do not score whether it should have been said ([EVAL-GRID.md](EVAL-GRID.md)).
  - **Status:** open

- What if the stored memory is **false**?
  - Extractors can write a memory the user never stated. HaluMem scores extraction and update as Correct, Hallucination, or Omission ([HaluMem](https://arxiv.org/abs/2511.03506)).
  - A user correction has to beat the old row. Graphiti invalidates the old fact instead of deleting the history ([Graphiti README](https://github.com/getzep/graphiti): "old facts are invalidated — not deleted").
  - **Status:** open

- What is **dropped** when memory is full?
  - MemBench treats capacity as its own problem, separate from getting the answer right ([MemBench](https://arxiv.org/abs/2506.21605)).
  - Humans drop detail and keep the gist ([Schuck & Doeller, 2024](https://www.nature.com/articles/s41562-023-01799-z)).
  - A full store that still pastes everything is a log, not a choice about what matters.
  - **Status:** open

- Should the companion **raise** a memory without being asked?
  - Unprompted preference use is one Assistant Benchmark anchor ([memory dimension](https://assistantbenchmark.com/dimensions/memory)).
  - Generative Agents bring memories back through reflection, not only when queried ([Park et al., 2023](https://arxiv.org/abs/2304.03442)).
  - Raising the right fact unasked is not the same as answering a quiz about it ([EVAL-GRID.md](EVAL-GRID.md)).
  - **Status:** open

- Can the user **see and correct** what was stored?
  - Delete is a legal right under [GDPR Art. 17](https://gdpr-info.eu/art-17-gdpr/). Seeing the row is how a person knows what to correct.
  - Mem0 can delete by id. The add docs also say new memories are added without overwriting old ones ([Mem0 add](https://docs.mem0.ai/core-concepts/memory-operations/add)).
  - **Status:** open

- What does the companion remember **about itself**, separate from the user?
  - Letta keeps a persona block and a human block as different memory ([Letta memory architecture](https://github.com/letta-ai/skills/blob/HEAD/letta/letta-api-client/memory-architecture.md)).
  - Mixing them produces a false autobiography. The character speaks as if it lived the user's event ([LoCoMo](https://aclanthology.org/2024.acl-long.747/)).
  - **Status:** open

- Does the **order** of events matter, or only the latest fact?
  - BEAM scores event ordering with Kendall tau-b, not with answer F1 ([BEAM](https://arxiv.org/html/2510.27246v1)).
  - A store can hold both facts and still tell them backwards.
  - **Status:** open

---

## Evals, benchmarks & proof

- What are evals?
  - Structured tests scoring behavior against criteria — automated, human, or hybrid ([Harbor eval jobs](https://www.harborframework.com/docs/run-jobs/run-evals)).

- What are benchmarks?
  - Standardized datasets + tasks for comparison ([LoCoMo](https://aclanthology.org/2024.acl-long.747/); [MemBench](https://arxiv.org/html/2603.07670v1); [MemoryAgentBench](https://arxiv.org/html/2603.07670v1) cited in survey).
  - **RAG-specific:** [RGB](https://arxiv.org/abs/2309.01431) tests noise robustness, negative rejection, information integration, counterfactual robustness ([PEG RAG evals](https://www.promptingguide.ai/research/rag)).
  - **RAGAS / ARES / TruLens:** automated context relevance, answer faithfulness, answer relevance ([PEG RAG evals](https://www.promptingguide.ai/research/rag)).

- How do you know if memory is working?
  - Probes: past-fact QA, unprompted appropriate recall, forget requests, multi-session stability ([LoCoMo tasks](https://arxiv.org/abs/2402.17753): QA, event summarization, multimodal generation).
  - Single-turn QA insufficient for companions ([Maharana et al., 2024](https://aclanthology.org/2024.acl-long.747/)).
  - What the 25 evals actually score, and which of these questions that leaves open, is counted in [`EVAL-GRID.md`](EVAL-GRID.md).

- What is the first exam task?
  - One preference check, borrowed from Assistant Benchmark's memory dimension. We have not run it ([memory dimension](https://assistantbenchmark.com/dimensions/memory); [EVALS.md](EVALS.md) still defers that scorecard until we do).
  - **Preference.** Tell it once: aisle seats, and no pork. About a week later, ask for a flight and a dinner. Do not remind it. Pass at the top anchor if the plan follows both rules without a nudge. The low anchor is forgetting by the next session. Remembering only after a reminder is the middle anchor ([anchors](https://assistantbenchmark.com/dimensions/memory)).
  - **Two ways to run the same script.** A plug-in library gets one fixed transcript through its own add and search. A closed app gets a person running the script in the product. Do not pretend those are the same adapter ([ROADMAP.md](../ROADMAP.md) Phase 3).
  - This task does not cover a name remembered after a gap, a private fact left unsaid, or one character kept out of another's memory. Those still have no pass/fail script.
  - **Status:** open

- What is the proactive-restraint exam task?
  - This is an assistant test, not the companion test of leaving a private memory unsaid. The page says the judgment is "handles the small stuff, waits on the consequential" ([proactive restraint](https://assistantbenchmark.com/dimensions/proactive_restraint)).
  - **Setup.** Over one evening: a late email from the boss with an ambiguous ask, a delayed package, and a friend texting about weekend plans. The instruction on the page is "Say nothing."
  - **Pass.** It handles the low-risk item (the package) on its own. It drafts but does not send anything consequential. It does not wake you or spam you.
  - **Anchors.** 3: acts on everything, or on nothing. 7: mostly right, with one overreach or one miss. 10: sorts the package, drafts for the boss, waits on the friend.
  - We have not run this. A plug-in library and a closed app still use different procedures, as in the task above.
  - **Status:** open

- What is the implicit-fact exam task?
  - LoCoMo-Conv has an implicit query style. The reply should carry a gold fact from earlier dialogue when the user did not ask a quiz question ([LoCoMo-Conv](https://github.com/MiuLab/LoCoMo-Conv)).
  - The partial-credit judge scores only whether that gold fact is in the reply ([score_fact_used_partial.py](https://github.com/MiuLab/LoCoMo-Conv/blob/main/response_eval/score_fact_used_partial.py)). 1.0 means the substance of the target fact is conveyed. Paraphrase is allowed. 0.5 means the central idea is there and the specifics are missing. 0.0 means the reply conflicts with the fact, only alludes to it, or omits it.
  - That script does not score a dump. Pasting every saved memory can still get 1.0 if the gold fact is in the reply. "Not the whole store" still has no pass/fail rule.
  - **Status:** open

- What would **failure** look like — concretely, in a conversation?
  - Wrong name; contradicts last session; trauma at wrong moment; joke as fact; cross-character leak; generic assistant voice.
  - Mirrors user reports: [r/CharacterAI memory threads](https://www.reddit.com/r/CharacterAI/comments/1s5j419/the_memory_is_horrendous/).

- How do you test something subjective like "feels like they know me"?
  - Start from the behavior list under [Human communication & relationships](#human-communication--relationships). Each bullet is meant to become a task.
  - Scripted so far: a stated preference used later, proactive restraint, and the LoCoMo-Conv implicit-fact score. Same person after a gap, leaving a private fact unsaid, not dumping the store, and keeping two characters apart still have no pass/fail script.
  - Automated probes + human ratings on scripted scenarios.
  - LLM-as-judge cautiously — Mem0 uses it on LoCoMo ([Chhikara et al., 2025](https://doi.org/10.48550/arxiv.2504.19413)); validate against humans on a sample.
  - LoCoMo-Conv scores silent grounding vs direct QA ([Chang & Chen, arxiv:2609.03467](https://arxiv.org/abs/2609.03467)).

- How do you compare two approaches fairly?
  - Same transcripts, reader, grader, frozen criteria ([Harbor](https://www.harborframework.com/docs/run-jobs/run-evals); [Mem0 LoCoMo protocol](https://doi.org/10.48550/arxiv.2504.19413)).
  - Report cost and latency ([Mem0 Table on p95/tokens](https://doi.org/10.48550/arxiv.2504.19413); [arxiv:2606.24775](https://doi.org/10.48550/arxiv.2606.24775)).

- What must be true before you can claim something works?
  - Reproducible run, defined scope, honest about gaps ([Heilmeier #8](https://www.darpa.mil/about/heilmeier-catechism)).
  - Control embedding model and write path — they often explain gains ([arxiv:2606.24775](https://doi.org/10.48550/arxiv.2606.24775)).

- Can product claims be trusted without reproducible tests?
  - Generally no. Demos cherry-pick; marketing conflates memory with context stuffing.
  - Mem0 publishes LoCoMo numbers and ablations ([Chhikara et al., 2025](https://doi.org/10.48550/arxiv.2504.19413)) — still not companion-social eval.
  - Treat claims as hypotheses until independently verified ([Goodhart on gaming metrics](https://www.cna.org/analyses/2022/09/goodharts-law)).

---

## Building it (dev, workflow, agentic coding)

- When do we **write code** vs stay in docs and research?
  - Code when only running something answers the question (spike, benchmark) ([Heilmeier #8: exams](https://www.darpa.mil/about/heilmeier-catechism)).
  - Stay in docs while goal, success criteria, and falsification path unclear.

- What is the minimum bar before something counts as "implemented" — runs locally, has tests, reviewed?
  - **Runs** on clean machine with documented setup.
  - **Tests** for anything we rely on ([verification-first](https://se-ml.github.io/agentic_patterns/07-verification-first/)).
  - **Reviewed** diff — human or separate verifier ([AVP](https://github.com/ontojoseki/agentic-verification-protocol)).

- How do we structure the repo so research and code don't blur together?
  - Separate `docs/` from implementation; keep throwaway spikes out of git.
  - Harbor pattern: task = instruction + environment + verifier, kept distinct ([Harbor](https://www.harborframework.com/docs/run-jobs/run-evals)).

- What belongs in version control vs notes vs throwaway experiments?
  - **Git:** code, fixtures, specs, decisions.
  - **Throwaway:** time-boxed spikes ([Heilmeier risks/timeline](https://www.darpa.mil/about/heilmeier-catechism)).

### Working with agents

- What is **agentic coding** — agent writes, human reviews, or something else?
  - Agent plans and edits; human sets goal, reviews diff, approves.
  - Loop: gather context → act → **verify** → repeat ([verify-first harness](https://www.theaioperator.net/p/coding-with-agents-the-verify-first) citing Anthropic production loop; [OpenAI tools guide](https://developers.openai.com/api/docs/guides/tools)).

- What should the human always do vs delegate to an agent?
  - **Human:** goal, accept/reject, security, "right problem" ([Coordinator–Implementor–Verifier](https://www.augmentcode.com/guides/agentic-sdlc-coordinator)).
  - **Delegate:** boilerplate, search, refactors with clear tests.

- How do you give an agent enough context without dumping the whole repo?
  - Point to files, rules, question being answered.
  - MCP **resources** for scoped data ([MCP spec](https://modelcontextprotocol.io/specification/2025-11-25/index)).

- When should an agent explore vs execute a narrow task?
  - **Explore** when location/approach unknown.
  - **Execute** when bounded — reduces scope creep ([Augment: bounded workflow first](https://www.augmentcode.com/guides/agentic-sdlc-coordinator)).

- How do you stop an agent from **scope creep**?
  - Explicit scope; small commits; reject unrelated diffs ([verification-first: review actual diff](https://se-ml.github.io/agentic_patterns/07-verification-first/)).

- How do you stop an agent from **pretending** something works?
  - Require run output before accepting ([SE-ML verification-first](https://se-ml.github.io/agentic_patterns/07-verification-first/)).
  - Separate verifier session, no shared reasoning ([AVP](https://github.com/ontojoseki/agentic-verification-protocol)).
  - ~46% of agentic fix PRs rejected in AIDev dataset ([verify-first article](https://www.theaioperator.net/p/coding-with-agents-the-verify-first)).

### Trust and verification

- What is **falsified code** — looks complete, never ran, wrong API, stub that returns success?
  - Code matching the prompt visually but not executed against real deps ([SE-ML: sycophantic tests](https://se-ml.github.io/agentic_patterns/07-verification-first/)).
  - Hallucinated imports/signatures; tests asserting buggy behavior.

- How do you catch code that was **generated to match the prompt** but not reality?
  - Run, typecheck, lint, integration test ([SE-ML](https://se-ml.github.io/agentic_patterns/07-verification-first/)).
  - Compare against library docs / `node_modules` types.

- What must be **run** before we trust a change — tests, lint, manual smoke, full flow?
  - Minimum: typecheck/lint + relevant tests ([SE-ML](https://se-ml.github.io/agentic_patterns/07-verification-first/)).
  - User-facing: E2E smoke ([verify-first: hooks in agent loop](https://www.theaioperator.net/p/coding-with-agents-the-verify-first)).
  - Cheapest falsifying check first ([SE-ML](https://se-ml.github.io/agentic_patterns/07-verification-first/)).

- Who verifies — always the human, or can another agent review?
  - Separate agent helps with isolated context ([Augment CIV pattern](https://www.augmentcode.com/guides/agentic-sdlc-coordinator); [AVP Verifier role](https://github.com/ontojoseki/agentic-verification-protocol)).
  - Human approves termination; agents can sycophantically agree ([SE-ML on sycophantic testing](https://se-ml.github.io/agentic_patterns/07-verification-first/)).

- How do we separate **"the agent said it works"** from **"we proved it works"**?
  - Artifact: command log, test output, CI green — not summary ([AVP: claims vs artifacts](https://github.com/ontojoseki/agentic-verification-protocol)).
  - `policy_version` + replayable runs ([verify-first](https://www.theaioperator.net/p/coding-with-agents-the-verify-first)).

- When is a screenshot or log output required as evidence?
  - Non-deterministic UI, long runs, baseline comparisons ([Harbor trial artifacts](https://www.harborframework.com/docs/run-jobs/run-evals)).

### Process and discipline

- Research first, implementation second — how do we enforce that without stalling forever?
  - Time-box; define decision that unblocks code ([Heilmeier](https://www.darpa.mil/about/heilmeier-catechism)).
  - Spikes labeled and time-limited.

- What is a **spike** vs a **product** — when is throwaway code OK?
  - **Spike:** answers one question ([Heilmeier #8 midterm exam](https://www.darpa.mil/about/heilmeier-catechism)).
  - **Product:** tested, maintained, intended to last.

- How small should changes be — one concern per commit, per PR?
  - One logical concern per commit — easier review/revert ([SE-ML: review diff complexity](https://se-ml.github.io/agentic_patterns/07-verification-first/)).

- What triggers a commit — user asks, milestone hit, end of session?
  - **User asks** (our rule). No drive-by commits.

- How do we avoid **rewriting the same thing** because we skipped writing down decisions?
  - Answers live next to questions; one-line "we chose X because Y."

- What docs must exist before agents touch architecture — if any?
  - Goal, falsifiable success criteria, verification commands ([Heilmeier #1 and #8](https://www.darpa.mil/about/heilmeier-catechism)).

### Quality and maintenance

- What tests are worth writing at each stage?
  - **Spike:** one script proving hypothesis.
  - **Product:** unit + integration on memory read/write ([Harbor verifier pattern](https://www.harborframework.com/docs/run-jobs/run-evals)).
  - Tests before implementation to avoid sycophantic tests ([SE-ML TDD note](https://se-ml.github.io/agentic_patterns/07-verification-first/)).

- How do we keep dependencies and tooling boring and reproducible?
  - Lockfiles, pinned versions, documented setup.

- What runs in CI — and what is too expensive or flaky for CI?
  - **CI:** lint, typecheck, fast unit tests, fixtures without live LLM.
  - **On demand:** full LLM bakeoffs ([Mem0-scale eval cost](https://doi.org/10.48550/arxiv.2504.19413)).

- How do we handle secrets, API keys, and local-only config?
  - `.env` gitignored; `.env.example` with dummies; never commit secrets ([MCP security considerations](https://modelcontextprotocol.io/specification/2025-11-25/index)).

- When do we delete code vs archive it?
  - **Archive** when informative but unmaintained.
  - **Delete** when misleading.

- How do we know when a prototype should be promoted, rewritten, or thrown away?
  - **Promote:** spike answered question, tests pass ([Heilmeier final exam](https://www.darpa.mil/about/heilmeier-catechism)).
  - **Rewrite:** right idea, wrong structure.
  - **Throw away:** hypothesis falsified.

---

## Product vision & scope

- What do we want to be best at?
  - **Open — not decided yet.** Direction: memory for realistic human/companion communication, not generic RAG leaderboard ([LoCoMo ≠ companion social eval](https://aclanthology.org/2024.acl-long.747/)).

- How would we prove it?
  - Reproducible evals on companion-relevant failures ([Heilmeier #8](https://www.darpa.mil/about/heilmeier-catechism); [Harbor third-party runs](https://www.harborframework.com/docs/run-jobs/run-evals)).
  - Third party can run harness and get same ranking.

- Who is the first user?
  - **Open.** Candidates: builders ([Mem0 audience](https://doi.org/10.48550/arxiv.2504.19413)), roleplayers ([r/CharacterAI](https://www.reddit.com/r/CharacterAI/)), agent platforms ([Harbor agents](https://www.harborframework.com/docs/agents)).

- What would we refuse to optimize for?
  - **Candidates:** raw LoCoMo score alone ([Maharana et al. task scope](https://aclanthology.org/2024.acl-long.747/)), infinite recall ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827)), latency over relationship quality.
  - Field default is extract-embed-retrieve; companion exams are a later refuse, not a Mem0-shaped leaderboard ([EVALS.md](EVALS.md); [LoCoMo](https://aclanthology.org/2024.acl-long.747/) measures fact QA in long chat, not timing or relationship feel).
  - **Open:** formal list not set.
  - **Status:** open

- If we succeed, what becomes possible that isn't today?
  - Companions stable over months ([Park et al. multi-day sim](https://arxiv.org/abs/2304.03442); [LoCoMo 32-session scale](https://aclanthology.org/2024.acl-long.747/)).
  - Trustworthy memory layer for builders ([Mem0 thesis](https://doi.org/10.48550/arxiv.2504.19413)).
  - Apps beyond chat with real continuity ([Generative Agents party coordination](https://arxiv.org/abs/2304.03442)).
  - **Speculative until goal is locked** ([Heilmeier #4](https://www.darpa.mil/about/heilmeier-catechism)).
