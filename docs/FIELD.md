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
