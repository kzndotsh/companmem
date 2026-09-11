# Slice A. Infra big three

Reading path for the census parent. JSON cards are the record. This file is how the four engines actually work for a long-term digital companion, not a coding agent.

Companion user. One person talks to one character for months. Winning LoCoMo is not the job.

**Shared premise.** All four still mostly assume that putting the right past text or facts into the prompt makes the model act as if it remembers the relationship. Letta is the exception that also keeps identity files in the system prompt every turn.

## Overview

Mem0, Graphiti, Zep, and Letta are the high-star agent-memory stack people cargo-cult into companions. They are extract-and-retrieve or filesystem-memory products. None ships user-bio / character-autobiography / relationship-state / lore / OOC as types.

## Key concepts

- Extract loop. An LLM turns a turn into stored facts (Mem0, Graphiti, Zep) or the agent writes Markdown (Letta).
- Retrieve loop. The app or the agent pulls a subset of that store into the next prompt.
- Validity. Graphiti and Zep mark facts true then false without deleting them. Mem0 ADD-only keeps both sentences unless Dream or delete runs. Letta overwrites files.
- MemFS. Letta's current memory is a git repo of Markdown. The old MemGPT core / recall / archival tiers are retired.

## How it works

### Mem0

Official index. [docs.mem0.ai/llms.txt](https://docs.mem0.ai/llms.txt). Repo [mem0ai/mem0](https://github.com/mem0ai/mem0). Apache-2.0. Stars observed 65121 on 2026-09-11. measured.

The live OSS add path is ADD-only. measured. `mem0/memory/main.py` `_add_to_vector_store` sets `system_prompt = ADDITIVE_EXTRACTION_PROMPT` and returns `event: ADD`. The old ADD / UPDATE / DELETE / NONE prompt still sits in `mem0/configs/prompts.py` as `DEFAULT_UPDATE_MEMORY_PROMPT`, but `main.py` does not import it. measured.

`core-concepts/memory-types.md` still describes a four-way extract loop. measured. That page is stale against the V3 add path. inferred.

How-it-works and add.md match the source. New facts accumulate. Explicit `update` and `delete` exist. Platform Dream supersedes and merges in the background. Superseded rows stay visible unless `latest_only=true`. measured.

The app must call `search` and stuff hits into the prompt. measured. That is retrieve-equals-remember. Platform fuses semantic, keyword, entity, and temporal scores. OSS is vector plus optional keyword/entity boost, no temporal-reasoning product page. measured.

Identity is `user_id` / `agent_id` / `run_id` / `app_id`. Default extraction puts a fact on the speaker, so a row is not jointly user-and-agent. measured. Categories are tags such as `user_preferences`, not companion kinds. measured.

Silence and poisoning filters are absent. measured. Delete and expiration exist. measured. Hosted MCP at `https://mcp.mem0.ai/mcp`. measured. OSS can run with Ollama. measured.

Published scores are Platform LoCoMo 92.5, LongMemEval 94.4, BEAM 64.1 / 48.6 at top_200 and about 7k tokens. measured. Those benches are assistant fact QA.

Companion fit PARTIAL. Companion cookbooks exist. The ontology and silence gaps remain.

### Graphiti

Official README and [help.getzep.com/graphiti](https://help.getzep.com/graphiti). Apache-2.0. Stars observed 30809 on 2026-09-11. measured.

Write path. `add_episode` with `EpisodeType` text, message, or json. LLM extracts entities and RELATES_TO facts. `reference_time` stamps the episode. measured.

`EntityEdge` in `graphiti_core/edges.py` has `valid_at`, `invalid_at`, `expired_at`, and `reference_time`. measured. README. Old facts are invalidated, not deleted. Query what is true now or what was true then. measured. `add_episode_bulk` skips invalidation. measured.

Read path. Hybrid semantic + BM25, RRF, optional node-distance rerank, optional cross-encoder. The app injects facts. measured.

`group_id` namespaces graphs. Custom Pydantic entity and edge types are optional ontology. measured. No shipped companion types. measured.

Official experimental MCP in-repo. Tools add_episode, search_facts, search_nodes, delete_episode, clear_graph. measured.

Local. Yes, with Neo4j or FalkorDB and an LLM. Default still wants structured-output models. measured.

Overview claims LoCoMo 94.7% at 155ms and LongMemEval 90.2% at 162ms. measured. Same assistant-QA limitation as Mem0.

Companion fit PARTIAL. Validity windows help time skip and retcons. Prompt policy is still on you.

### Zep Cloud

Closed core on Graphiti. Docs [help.getzep.com/llms.txt](https://help.getzep.com/llms.txt). License and stars unknown. Graphiti README. Zep uses a proprietary Context Graph Engine. measured.

Users, threads, user graphs, standalone graphs. `thread.add_messages` and `graph.add` ingest. `thread.get_user_context` builds a Context Block. `graph.search(scope="auto")` packs a character-budgeted string (default 2500). measured.

Context types. Facts, entities, episodes, thread summaries, observations (Flex Plus / Enterprise), user summary. measured. Still not lore vs experienced vs OOC.

Fact invalidation copies Graphiti. measured. Auto search can treat "yesterday" as a time window. measured.

Poisoning. `memory-security.md` tells the app to treat memory as untrusted data, keep it out of system/developer channels, attach episode metadata, filter on source, and authorize tools outside the model. measured. That is the only first-party poisoning write-up in this slice. Zep does not document a built-in jailbreak classifier on ingest. measured.

Local intimate chat. Absent on Zep Cloud. Use Graphiti. measured.

Official Memory MCP at `https://api.getzep.com/mcp`. Docs MCP at `help.getzep.com/_mcp/server`. measured.

Paper arXiv 2501.13956. DMR 94.8% gpt-4-turbo. LongMemEval-s 71.2% gpt-4o vs 60.2% full context, about 1.6k tokens. measured.

Companion fit PARTIAL. Strongest ops and temporal story. Closed. Still retrieve-equals-remember.

### Letta

Docs [docs.letta.com/llms.txt](https://docs.letta.com/llms.txt). PLAYER-LIST repo [letta-ai/letta](https://github.com/letta-ai/letta) now redirects active source to [letta-ai/letta-code](https://github.com/letta-ai/letta-code). Apache-2.0 with brand-asset exclusion. Stars observed 24699 on 2026-09-11 for letta-ai/letta. measured.

MemFS replaced core / recall / archival. measured. letta README. Historical V1 lives on the `archive` branch. measured.

Memory is Markdown in a git repo. `system/persona.md` and `system/human.md` load every turn. Other files stay out of context until the agent reads them. The tree listing is always in the prompt. measured. Optional MemFS Search mod for keyword/vector. Default is ordinary file tools. measured.

Writes. Agent file edits, `/remember`, dreaming subagents, user edits. measured. Not a per-turn extract LLM.

Read. Always-on identity files plus agent tool reads. mixed retrieve-equals-remember. The persona does not depend on a top-k search.

Local backend can keep agent state on disk with Ollama. measured. Cloud agents store state at Letta. Inference still follows the chosen provider.

MCP. Letta is an MCP client, not a memory MCP server. measured.

Published MemFS companion-memory scores. None found. The Zep paper cites historical MemGPT DMR 93.4%. That is not a current MemFS claim. measured.

Companion fit PARTIAL. Always-on persona/human is closer to a person than a fact store. The harness is still coworker/coding first. Silence absent. The agent can rewrite its own persona.

## Where things live

| Player | Engine files / API | Docs index |
| --- | --- | --- |
| mem0 | `mem0/memory/main.py`, `mem0/configs/prompts.py` | docs.mem0.ai |
| graphiti | `graphiti_core/edges.py`, `add_episode` | help.getzep.com/graphiti |
| zep | closed; Graphiti + Context Lake APIs | help.getzep.com |
| letta | MemFS under `~/.letta/.../memory`; live code in letta-code | docs.letta.com |

## Gotchas

- Do not implement Mem0 as ADD/UPDATE/DELETE/NOOP on the current OSS add path. That loop is dead in `main.py`. Platform Dream is a separate supersede/merge layer. measured.
- Do not implement Letta as MemGPT tiers. MemFS is the current model. measured.
- Graphiti bulk load will not invalidate contradicting edges. measured.
- Zep Context Blocks are untrusted data by their own security doc. Putting them in `system` is the failure mode they warn about. measured.
- None of the four implement social silence. measured.

## Verdicts

| id | companion_fit | one-line reason |
| --- | --- | --- |
| mem0 | PARTIAL | Companion cookbooks plus extract/search. No companion types, silence, or poisoning filter. OSS lacks Dream/temporal. |
| graphiti | PARTIAL | Real validity windows. Generic KG. App owns prompt, ontology, silence. |
| zep | PARTIAL | Best temporal + poisoning docs. Closed. Retrieve-into-prompt. Not local. |
| letta | PARTIAL | Always-on persona/human and local MemFS. Coworker harness. Agent can overwrite identity. No silence. |
