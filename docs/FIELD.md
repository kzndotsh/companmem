# Field

What already exists, and who it is for. Index: [Questions](QUESTIONS.md).

Answers are working notes. Citations are inline links. A question stays `open` until it has a falsifier.

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
  - Path may be wrong if bottleneck is read policy and social timing, not retrieval accuracy ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827) ⚠️ *planned study, no results*).

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
  - **Assistant:** correct recall when asked; minimal creepiness ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827) ⚠️ *planned study, no results*).
  - **Enterprise:** traceable, deletable, access-controlled ([GDPR](https://gdpr-info.eu/art-17-gdpr/); [Multigrid on erasure](https://multigrid.ai/learn/right-to-erasure-ai)).
  - **Companion:** feels continuous over weeks; character stable; social timing ([LoCoMo multi-session generation task](https://aclanthology.org/2024.acl-long.747/); [Maharana et al.](https://arxiv.org/abs/2402.17753)).
  - **Open:** our bar not set yet.

---

## Studies & prior art

- What research exists on humanizing AI?
  - **CASA:** people mindlessly apply social rules to computers ([Nass & Moon, 2000](https://doi.org/10.1111/0022-4537.00153)).
  - **Media Equation:** people treat media as real social actors ([Reeves & Nass, 1996](https://doi.org/10.30658/hmc.1.5) — discussed in [HMC extension](https://doi.org/10.30658/hmc.1.5)).
  - **Creepiness of AI recall:** when memory feels intrusive ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827) ⚠️ *planned study, no results*).
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
  - The volume of competing products is itself a signal: if any one of them had cracked it, the others would not keep appearing. The complaint data confirms it — 40% of all user complaints across 61 products are forgetting and continuity failures, and the field has not converged on a solution.

- Is that a sign the problem is unsolved, or that the market is fragmented?
  - Unsolved at the core. The fragmentation is downstream of the unsolved problem, not a cause of it.
  - Core mechanic unsettled: no product has a speak/silent policy; forget is missing from 80% of products; the benchmark that would measure relationship quality doesn't exist ([CMA on RAG limits](https://arxiv.org/pdf/2601.09913v1); AUDIT-ANALYSIS.md).
  - User complaints persist despite the number of competing products ([r/CharacterAI](https://www.reddit.com/r/CharacterAI/comments/1s5j419/the_memory_is_horrendous/)).
  - The analogy that clarifies it: coding assistants work well because the context problem for code is well-specified — open files, diffs, test failures. The context problem for a companion relationship has never been specified. That is the actual gap.

- What does the field actually implement, across 61 audited products?
  - ⚠️ *Sampling bias: the 61-product audit is heavily weighted toward open-source and GitHub-discoverable products. The four largest consumer companions (CharacterAI, Replika, Nomi, Kindroid) are closed and could not be audited architecturally — only their user complaint data was available. "What the field has built" should be read as "what the auditable part of the field has built." Proprietary implementations may differ significantly.*
  - Frequency across 61 products (2026-09-26 matrix.json): persist 53/61 (87%), retrieve 56/61 (92%), conflict/supersession 34/61 (56%), isolation 39/61 (64%), forget-delete 12/61 (20%), forget-suppress 10/61 (16%).
  - Persist and retrieve are commodity — nearly universal. Forget is rare. The field has mostly built read-only stores.
  - Three natural tiers emerge from co-occurrence: (1) bare minimum — persist + retrieve only, no isolation or forget (4 products, e.g. a-mem, mcp-memory); (2) standard — persist + retrieve + isolation + conflict, no forget (25 products, 41% of the field); (3) fuller — adds at least one forget variant on top of tier 2 (12 products).
  - Forget-delete and forget-suppress almost never co-occur (2/20, 10%). Products pick one or neither. There is no field consensus on what forget means.
  - `log_vs_curated`: 56/61 products expose both raw log and curated memory paths; 2 are log-only; 3 unknown.
  - Storage stack: most products layer multiple backends. 32/61 use 4–5 storage types simultaneously. Vector+SQL+file is the most common combo. Graph+vector (28/61, 46%) is the emerging serious tier — Graphiti, Letta, Cognee, Honcho, LightRAG all here. This is not convergence; it is hedging.
  - Retrieval: hybrid search (semantic+BM25+graph) already at 34/61 (56%). Semantic-only is no longer the default in serious products. The field moved past pure vector search faster than eval benchmarks did — most evals still score retrieval rank as a single number.
  - Append-only write path (25/61, 41%) with no forget mechanism: 18 of those 25 have no forget at all. Committed to immutability with no eviction on top. The store grows forever by design.
  - Write path: LLM extraction 36/61 (59%), user-written/editable 30/61 (49%), rule-based 27/61 (44%), append-only 25/61 (41%). Most products offer multiple write paths; none dominates.
  - **Status:** open

- What do users actually complain about, and does it match what the field implements?
  - 425 community rows across 61 product audits (2026-09-26). Top buckets: forgetting/continuity loss 105 (25%), context overflow 99 (23%), cross-session failure 64 (15%), persona/character drift 63 (15%), cannot edit/correct 54 (13%), isolation/leak 50 (12%), wrong facts/hallucination 29 (7%), timing/when-to-speak 3 (<1%).
  - Continuity loss + cross-session failure together = 169 rows (40% of all complaints). Users do not distinguish "it forgot" from "it forgot between sessions" — both read as the same failure.
  - "Cannot edit/correct" is 54 rows yet zero evals score it and 80% of products have no forget path. Users want to see and fix what was stored; the field has not built that.
  - Timing has only 3 rows. Nobody complains about a companion speaking at the wrong moment — because no product tries to stay silent at the right moment. Users cannot complain about a failure mode the product never attempted. This is a gap invisible to complaint analysis.
  - High-complaint products (≥55 issue/community rows) are more likely to implement advanced axes — isolation 90% vs 50%, conflict 67% vs 50% — because active OSS projects attract both features and issues. But every top-10 complaint product is still missing forget-suppress, and 7/10 are missing forget-delete entirely.
  - **Status:** open

---

## Product vision & scope

- What does the API surface vocabulary of 62 products reveal about the field's mental model?
  - Dominant method names: `search` (23 products), `get` (22), `delete` (18), `add` (17), `clear` (16). Generic CRUD with memory branding. The API surface is indistinguishable from a database client.
  - Memory-specific verbs are rare: `recall` (9), `remember` (3), `forget` (1 — imprint-memory only), `suppress` (1 — Vestige only). The field hasn't developed a memory-native API vocabulary.
  - Speak/silent axis: `speak`, `silence`, `withhold`, `surface` — absent from every product. The decision of when to surface a memory vs stay silent is not a named API concept anywhere. It is buried in prompt scaffolding, invisible to callers.
  - Forget as a named API concept: `forget` as a method name in 1 product. `suppress` in 1. `promote`, `purge`, `consolidate`, `prune`, `evict` absent as method names across all 62. The matrix showed forget missing from 80% of products; the API surface confirms it is not a named concept in most of the remaining 20% either.
  - `relationship` is the most common memory-framing word in codebases (20 products) yet no product has a relationship-scoped memory API — no `add(relationship_id=...)`, no `recall(for_relationship=...)`. The word is in the docs; the concept did not reach the API.
  - Temporal horizon segmentation: `LongTermMemory`, `ShortTermMemory`, `MidTermMemory` class names in 3 products each. Episodic framing in 9. The neuroscience vocabulary is aspirational, not structural.
  - Compound tool names confirm retrieval is the core concept: `memory_search` (7), `search_memory` (4), `memory_recall` (3). `memory_forget` appears in only 2 products. Lifecycle signals (promote, purge, suppress) are Vestige-only.
  - **Status:** open

- What does the dependency audit of 62 product repos reveal about actual tech choices?
  - Primary language: Python 38/62 (61%), TypeScript 13/62 (21%), Rust 4/62 (6%), JavaScript 2/62, unknown 5/62 (closed apps). This is a Python-dominant ecosystem; TS is second tier.
  - LLM providers: 28/62 products have zero LLM provider dependencies in manifests — they route through abstraction layers or are closed. Of those that hardcode: OpenAI 26/62 (42%), Anthropic 16/62 (26%), HuggingFace 14/62 (23%). LiteLLM only 3/62 despite widespread multi-provider claims.
  - Vector DBs: 42/62 have zero vector DB dependencies in manifests — treated as pluggable, not architectural. Mem0 wires 7 backends, LightRAG wires 5. Among those that commit: Redis 11/62 (18%), FAISS 7/62 (11%), Qdrant 6/62 (10%).
  - LangChain: only 8/38 Python products (21%) depend on it. LlamaIndex 3/38 (8%). The field has largely moved to building directly against provider SDKs, not framework abstractions. TypeScript products: zero LangChain dependencies.
  - Database split by language: Python products lean Postgres (34%) + SQLAlchemy (18%); TypeScript products lean SQLite (27%) + Postgres (20%). TS products are lighter/embedded; Python products are server infrastructure.
  - LLM provider breadth: 28/62 hardcode none; 13 hardcode exactly one; 21 hardcode 2–8. Multi-provider is a declared feature but often not wired in manifests.
  - **Status:** open

- What is the Rust cluster, and why does it matter?
  - Four products built in Rust: llm-wiki-cli, Memvid, RisuAI (Tauri shell), Vestige.
  - RisuAI is Rust only at the Tauri desktop shell layer — the memory logic is TypeScript/JS. Not a Rust memory system.
  - The other three are genuinely Rust-native memory systems, each betting on a different property: llm-wiki-cli bets on deterministic lexical search (no vector DB, explicit document weights, auditable retrieval); Memvid bets on portable single-file storage (.mv2 format, crash-safe, zstd/lz4 compressed, deterministic); Vestige bets on FSRS-based memory scheduling with prediction-error gating and explicit promote/purge signals.
  - What they share: all three reject the default extract-embed-retrieve pipeline in favor of something with more explicit control — deterministic retrieval, structured memory cards, or spaced-repetition scheduling. Performance is a secondary motivation; auditability and explicit semantics are primary.
  - Vestige is the most companion-relevant: retention_strength drives five memory states (Active/Dormant/Silent/Unavailable), retrieval is audit-only (recalling does not strengthen), explicit promote required, purge is irreversible and advertised as requiring user interaction. That is closer to a speak/silent policy than anything in the Python tier.
  - Vestige is the most architecturally distinctive product in the field for companion-relevant memory. FSRS-6 spaced repetition governs memory decay — stability, difficulty, reps, and lapses tracked per node. Retrieval is audit-only; recalling does not strengthen. Five memory states (Active/Dormant/Silent/Unavailable) derived from `retention_strength` thresholds. Prediction Error Gating on ingest: only novel facts stored, redundant writes merge on write. Suppression is reversible within a 24-hour labile window and accelerates FSRS decay without deleting the row. A background Rac1 cascade sweep spreads decay to up to 100 co-activated neighbours over 72 hours. Signed receipts on every retrieval. Bitemporal validity (`valid_from`/`valid_until`) on every node. Known issues: stability can compound to 1.4e24 days (unclamped sentiment, issue #121); in-memory prospective engine never hydrated from storage in production; batch ingest non-atomic. Own benchmark ("Silent Rotation"): 20/23 correct vs 0/25 no-memory and 4/23 dense cosine RAG — not independently verified.
  - **Status:** open

- What do we want to be best at?
  - **Open — not decided yet.** Direction: memory for realistic human/companion communication, not generic RAG leaderboard ([LoCoMo ≠ companion social eval](https://aclanthology.org/2024.acl-long.747/)).

- How would we prove it?
  - Reproducible evals on companion-relevant failures ([Heilmeier #8](https://www.darpa.mil/about/heilmeier-catechism); [Harbor third-party runs](https://www.harborframework.com/docs/run-jobs/run-evals)).
  - Third party can run harness and get same ranking.

- Who is the first user?
  - **Open.** Candidates: builders ([Mem0 audience](https://doi.org/10.48550/arxiv.2504.19413)), roleplayers ([r/CharacterAI](https://www.reddit.com/r/CharacterAI/)), agent platforms ([Harbor agents](https://www.harborframework.com/docs/agents)).

- What would we refuse to optimize for?
  - **Candidates:** raw LoCoMo score alone ([Maharana et al. task scope](https://aclanthology.org/2024.acl-long.747/)), infinite recall ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827) ⚠️ *planned study, no results*), latency over relationship quality.
  - Field default is extract-embed-retrieve; companion exams are a later refuse, not a Mem0-shaped leaderboard ([EVALS.md](EVALS.md); [LoCoMo](https://aclanthology.org/2024.acl-long.747/) measures fact QA in long chat, not timing or relationship feel).
  - **Open:** formal list not set.
  - **Status:** open

- If we succeed, what becomes possible that isn't today?
  - Companions stable over months ([Park et al. multi-day sim](https://arxiv.org/abs/2304.03442); [LoCoMo 32-session scale](https://aclanthology.org/2024.acl-long.747/)).
  - Trustworthy memory layer for builders ([Mem0 thesis](https://doi.org/10.48550/arxiv.2504.19413)).
  - Apps beyond chat with real continuity ([Generative Agents party coordination](https://arxiv.org/abs/2304.03442)).
  - **Speculative until goal is locked** ([Heilmeier #4](https://www.darpa.mil/about/heilmeier-catechism)).
