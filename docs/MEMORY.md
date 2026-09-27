# Memory

What a store has to do. Index: [Questions](QUESTIONS.md).

Answers are working notes. Citations are inline links. A question stays `open` until it has a falsifier.

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
  - A later fine-tune can put a trait into those weights from data that never names it. A student trained on number lists from an owl-loving copy of itself picks owls "over 60% of the time," up from 12%. The shift fails if the student and teacher do not share an initialization, and it fails if the same lists are only shown in context. "Filtering may be insufficient to prevent this transmission, even in principle" ([Cloud et al.](https://arxiv.org/abs/2507.14805)). That is still not a fact about the user.

- How much do **cost, hardware, and infra** constrain what gets built?
  - Local vector DB + embedder + LLM per turn is expensive for consumers.
  - Mem0 reports ~91% lower p95 latency and >90% token savings vs full-context on LoCoMo ([Mem0, 2025](https://doi.org/10.48550/arxiv.2504.19413)).
  - Long context reduces retrieval need but increases $/token and still degrades in the middle ([Liu et al., *lost in the middle*](https://arxiv.org/abs/2307.03172); [arxiv:2606.06448](https://doi.org/10.48550/arxiv.2606.06448)).

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
  - **Omit** in generation (know but don't say) — [Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827) on inappropriate recall ⚠️ *planned study, no results*.
  - Users may mean any of the three.
  - A retention gate can weight a past state down without deleting it. Behrouz et al. rename the forget gate for that reason, and cite the claim that the brain "does not erase memories but they might become inaccessible due to retrieval failures" ([Miras](https://arxiv.org/abs/2504.13173)). Their experiments score needle retrieval and perplexity, not a person.
  - A different gate can wipe the store. In Titans, α_t near 1 "can clear the entire memory" ([Behrouz, Zhong, and Mirrokni](https://arxiv.org/abs/2501.00663)). That is a deletion, not a failure to retrieve. The score is still a needle and a language-model loss, not a person.
  - A faster block can drop a fact while a slower block still holds it. "Higher-frequency neurons are responsible for fast adaption but store memories/knowledge for a short period of time, while lower frequency neurons are responsible for more persistent knowledge." When a block is updated, "the potentially forgotten knowledge" from that block "is still stored in other components" at a lower frequency, and "knowledge can partially be recovered when it is forgotten." They also say catastrophic forgetting "is not 'solved' in general" and "is a natural consequence of compression" ([Nested Learning](https://arxiv.org/abs/2512.24695)). The scores are perplexity, needles, and class-incremental figures, not a person.
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
  - Total recall can feel uncanny ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827) ⚠️ *planned study, no results*).

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
  - Saying a true fact at the wrong time is its own failure ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827) ⚠️ *planned study, no results*).
  - The 25 evals score whether the fact came back. They do not score whether it should have been said ([eval-grid](../artifacts/2026-09-22_eval-grid.md)).
  - LoCoMo's adversarial questions ask the model to recognize an unanswerable query. A-MEM still scores them with F1 and BLEU. The baseline that puts the whole conversation in the prompt scores higher there. The paper credits "robust pre-trained knowledge in simple fact retrieval," not a decision to stay silent ([A-MEM](https://arxiv.org/abs/2502.12110)).
  - **Status:** open

- What if the stored memory is **false**?
  - Extractors can write a memory the user never stated. HaluMem scores extraction and update as Correct, Hallucination, or Omission ([HaluMem](https://arxiv.org/abs/2511.03506)).
  - A user correction has to beat the old row. Graphiti invalidates the old fact instead of deleting the history ([Graphiti README](https://github.com/getzep/graphiti): "old facts are invalidated — not deleted").
  - In a recommender, "an erroneous or outdated fact written to memory is not a one-time error: it is retrieved and re-applied on every subsequent request until it is corrected" ([Maragheh and Deldjoo](https://arxiv.org/abs/2507.02097)).
  - A confident false answer can also come from the weights, with no bad row in a store. A sparse set of neurons, "less than 0.1% of total neurons," predicts hallucination and is "causally linked to over-compliance behaviors." They are already in the pretrained base model. "Simple suppression or amplification of neuron activations proves insufficient for effective control" ([Gao et al.](https://arxiv.org/abs/2512.01797)).
  - The aelios audit documents the clearest field case: the dream distillation pipeline fabricated a specific event (user complained about something after work) that existed in none of the 233 source messages for that day. The companion repeated it as fact. The user caught it only by manually checking every raw message. The fabricated memory had realistic texture — neither agent nor user could self-verify. Any summarization or distillation pipeline that produces condensed narrative from message batches carries this risk.
  - **Status:** open

- Can LLM extraction at write time reach companion-grade trustworthiness?
  - Converging evidence against extraction pipelines: taosmd measures 18.8% partially or unsupported facts across 526 claims. paramecium's prior pipeline produced 36% paraphrase rather than verbatim content before building a quote-verification guard. aelios documents a fabricated event with realistic texture that neither agent nor user could self-verify. honcho misattributes AI speech to the human user by default.
  - Mitigations each address one failure mode: quote-verification guard (paramecium) prevents fabricated memories. Speaker attribution prevents AI-speech contamination. Claims gate (taosmd) prevents serving unverified extractions. But each is a patch on a fundamentally untrusted pipeline.
  - The deeper question: can a pipeline that uses an LLM to decide what to remember about a real person — someone who will notice when the memory is wrong — be made reliable enough that users trust it the way they trust a human who remembers them?
  - Alternatives documented in the audit: human-in-the-loop review gates (aelios, byterover), model-self-authored memories via structured tags (omemo builtin mode, paramecium's `<mem>` tag path), append-only with manual curation (kimi-core). None scale cleanly to continuous passive use.
  - No product has measured whether users trust the extraction output enough to rely on it emotionally. That measurement must come before the architecture is locked in.
  - **Status:** open

- Does speaker attribution matter — whose words are being extracted?
  - Systemic failure across the field. honcho's deriver misattributes AI agent speech to the human user. hermes-agent stored routing metadata as user-authored content. mem0's entity linking merges across user/assistant scopes even when extraction prompts are separate.
  - A companion that builds its model of the user partly from its own prior outputs will drift toward a self-confirming mirror — not a model of a real person. Facts attributed to the wrong speaker contaminate the user model permanently.
  - Fix: explicit speaker tag on every ingested turn, enforced in the extraction prompt. Not advisory.
  - **Status:** open

- What happens to stored memory when the underlying model is updated?
  - Documented across five independent products: CharacterAI (auto-memory stopped picking up details after a recent update), Replika (post-2.0 rollout caused partial memory loss and personality drift), Nomi (post-update degradation breaking memory and personality coherence), Kindroid (LLM model updates cause loss of established character memory), Supermemory (upgrade-induced memory unsearchability across multiple versions).
  - This is not a storage problem. The memory store can be intact while the model behavior shifts, effectively resetting the relationship. The model that reads a given memory is not the model that wrote the context that produced it. No product has an architecture that survives model updates with continuity intact.
  - **Status:** open

- How much does memory processing **cost**, and does that constrain design?
  - claude-mem hit 64% of the user's primary model spend on memory processing alone. kiwi-mem estimates $0.22/day for active use with local embeddings. SimpleMem's intent-aware retrieval planning adds multiple LLM calls per turn. taosmd documents ~531 tokens per query vs 25,000+ for full-context baselines.
  - For a companion that runs continuously over months, these numbers determine what is commercially viable. A multi-LLM-call write pipeline that runs on every turn is not affordable at consumer scale.
  - Cost is a first-class constraint on write-path architecture, not an optimization pass later.
  - **Status:** open

- What is the "never admit no information found" failure mode?
  - Some systems include a scaffold instruction telling the model to produce a response even when retrieval returns nothing relevant, rather than admitting the gap. mem0's reader scaffold explicitly instructs the model not to acknowledge retrieval failure. The replika pattern follows the same approach.
  - This is an active design choice to manufacture confabulation. For a companion, the failure mode is worse than missing a fact: the companion confidently describes an event the user never shared, and the user cannot distinguish this from genuine recall. Discovery destroys trust in everything the companion has said.
  - The correct design: abstain rather than fabricate when the corpus does not contain a relevant memory. mnemosyne implements this — it returns nothing rather than generating a response that might be wrong.
  - "Never admit no information found" is a companion-destroying scaffold default, not a minor retrieval policy choice.
  - **Status:** open

- What **design decisions from the field are worth stealing** for a companion write path?
  - These are specific mechanisms documented in audited products, ranked by companion relevance.
  - **Quote-verification guard (paramecium):** Before any extracted memory enters the store, check that the verbatim source quote exists in the source batch. If the quote cannot be found, drop the memory. Eliminates fabricated memories with realistic texture. taosmd documents 18.8% of LLM-extracted facts as partially or unsupported; paramecium's prior pipeline produced 36% paraphrase. Adds one string-search per extracted fact at write time. No other product implements this.
  - **MEMORY.md / USER.md split (soul-of-waifu):** Character psychology (beliefs, emotional state, internal tensions, self-model) and user-facing facts (name, preferences, relationship history, shared milestones, promises) stored as separate schemas with different write paths and different authorities. The character owns the first store; the user's behavior populates the second. No funded product makes this split structural.
  - **Zero-loss append-only archive as rebuild target (taosmd):** Every ingested message goes to an append-only archive unconditionally before anything else. All derived layers — curated facts, vector index, knowledge graph — are rebuildable from the archive when a bug corrupts them or the extraction pipeline improves.
  - **Reads-never-reinforce; explicit promote-only strengthening (vestige, paramecium, ombre-brain):** Retrieving a memory does not increase its retrieval score. Only an explicit positive outcome signal strengthens a memory. Three products independently converge on this. Prevents highly-retrieved stale facts from becoming confidently wrong when circumstances change.
  - **Echo lane retrieval (paramecium):** At retrieval time, two separate query vectors: one from the user's message, one from the companion's previous reply. The second lane surfaces memories relevant to what the companion was just discussing, not only what the user asked. Two-vector retrieval at negligible incremental cost.
  - **Status:** open

- What is the right **build order** — foundational requirements vs aspirational ones?
  - The analysis of 61 products distinguishes two tiers. Getting the first tier right puts the system ahead of everything in the field. The second tier is the right long-term target but not necessary to be better than the field.
  - **Foundational (required to be better than the field):** Zero-loss append-only archive. Curated fact store with verbatim source quotes, speaker attribution, and subject labels. Quote-verification guard at write time. Abstain-not-fabricate retrieve scaffold. Hard failure logging on extraction errors (no silent cursor advancement).
  - **Aspirational (required to be the best possible companion):** Emotional state tracking with decay tied to emotional processing. Relational quality tracking (trust, promises, milestones). Affect-conditioned speak/silent policy. Circumplex affect model. CONTRADICTS-link force inclusion in retrieval.
  - A companion with a reliable, hallucination-checked, speaker-attributed fact store that admits uncertainty when it has nothing is far ahead of anything in the field — even without affect modeling.
  - **Status:** open
  - MemBench treats capacity as its own problem, separate from getting the answer right ([MemBench](https://arxiv.org/abs/2506.21605)).
  - Humans drop detail and keep the gist ([Schuck & Doeller, 2024](https://www.nature.com/articles/s41562-023-01799-z)).
  - A full store that still pastes everything is a log, not a choice about what matters.
  - MEM1 does not wait until a store is full. After each turn it allows "all external tool outputs to be discarded after use," and the only retained memory is one consolidated state. On sixteen composed questions, their 7B model "improves performance by 3.5× while reducing memory usage by 3.7×" against Qwen2.5-14B. Exact match there is a count of correct sub-questions, not a rate. They "assume access to environments with well-defined and verifiable rewards" ([Zhou et al.](https://arxiv.org/abs/2506.15841)).
  - A summary can drop the wrong thing before a store is full. "A summary that is too short can drop a binding constraint, such as a gluten restriction. A summary that is too long lets contradictions pile up" ([Maragheh and Deldjoo](https://arxiv.org/abs/2507.02097)).
  - **Status:** open

- Should the companion **raise** a memory without being asked?
  - Unprompted preference use is one Assistant Benchmark anchor ([memory dimension](https://assistantbenchmark.com/dimensions/memory)).
  - Generative Agents bring memories back through reflection, not only when queried ([Park et al., 2023](https://arxiv.org/abs/2304.03442)).
  - Raising the right fact unasked is not the same as answering a quiz about it ([eval-grid](../artifacts/2026-09-22_eval-grid.md)).
  - **Status:** open

- Can the user **see and correct** what was stored?
  - Delete is a legal right under [GDPR Art. 17](https://gdpr-info.eu/art-17-gdpr/). Seeing the row is how a person knows what to correct.
  - Mem0 can delete by id. The add docs also say new memories are added without overwriting old ones ([Mem0 add](https://docs.mem0.ai/core-concepts/memory-operations/add)).
  - A recommender paper names deletion compliance as "the fraction of removal requests honored on subsequent retrieval," and a privacy gate that excludes items "the user has asked to delete" even when they are the closest match ([Maragheh and Deldjoo](https://arxiv.org/abs/2507.02097)).
  - **Status:** open

- What does the companion remember **about itself**, separate from the user?
  - Letta keeps a persona block and a human block as different memory ([Letta memory architecture](https://github.com/letta-ai/skills/blob/HEAD/letta/letta-api-client/memory-architecture.md)).
  - Mixing them produces a false autobiography. The character speaks as if it lived the user's event ([LoCoMo](https://aclanthology.org/2024.acl-long.747/)).
  - A persona vector is a direction in the model's activations for a trait such as evil, sycophancy, or hallucination. It can be read before the reply is generated. It is not a block the user can open and edit. The score is 0 to 100 trait expression. A higher score means more of that trait. The authors say single-turn questions "may not fully reflect" how the traits show up in multi-turn use ([Chen et al.](https://arxiv.org/abs/2507.21509)).
  - The default assistant is also a direction. On Gemma 2 27B, Qwen 3 32B, and Llama 3.3 70B, "the model's position along the Assistant Axis depends most strongly on the most recent user message rather than where it was before" (R² 0.53–0.77 for the next position, R² 0.10 for the change). Drift "is often driven by conversations demanding meta-reflection on the model's processes or featuring emotionally vulnerable users." That position correlates with a harmful next reply at r = 0.39–0.52. Steered off the assistant end, Qwen starts "hallucinating lived experiences." Clamping the axis cut harmful jailbreak replies by nearly 60% on their judge, without a drop on IFEval, MMLU Pro, GSM8K, and EQ-Bench. They say the right reply to a person in distress "is outside the scope of this work" ([Lu et al.](https://arxiv.org/abs/2601.10387)).
  - **Status:** open

- Does the **order** of events matter, or only the latest fact?
  - BEAM scores event ordering with Kendall tau-b, not with answer F1 ([BEAM](https://arxiv.org/html/2510.27246v1)).
  - A store can hold both facts and still tell them backwards.
  - **Status:** open

---
