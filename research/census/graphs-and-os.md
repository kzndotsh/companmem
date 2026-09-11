# Graphs, memory OS, and RAG memory

Reading path for slice B. Cards under `research/census/cards/` are the record. This file is the order to read them.

Shared premise under test. If we retrieve the right past text or extracted facts into the prompt, the model will act as if it remembers the relationship.

Canonical Graph-RAG repos found. `HKUDS/LightRAG` and `microsoft/graphrag`. Both scored.

## Overview

These products store memory as a graph, a file wiki, or a hierarchical OS. Almost all of them still remember by stuffing retrieved text into the next prompt. measured from their own loops.

For a months-long companion, the failure that matters is identity mix. User bio, character autobiography, and relationship state land in one bag. Graph-RAG that cannot split those three is a misfit. That is the brief, and the two Graph-RAG cards match it. measured.

None of these ten ship silence (skip a high-score hit because recall would be creepy). measured from the docs and modules named on the cards.

## Key concepts

**Retrieve equals remember.** yes on eight cards. OpenViking is mixed because `identity.md` and `soul.md` are standing files, not only search hits. measured.

**Isolation is not ontology.** `user_id`, `containerTag`, `entity_id`, `workspace`, and `dataset` keep tenants apart. They do not type user vs character vs relationship. measured.

**Profile is a prompt blob.** MemOS, SuperMemory, MemoryOS, EverOS, and OpenViking all maintain a profile-like document and inject it. That helps name and preference recall. It does not encode relationship state as its own kind. measured.

## How it works

### Cognee

Start if you need a self-hosted document/code graph.

**Loop.** measured. `remember()` builds the graph. `recall()` auto-routes (`HYBRID_COMPLETION` default, session cache first when `session_id` is set). `forget()` deletes item, dataset, or memory-only state. Sources. `docs.cognee.ai` introduction, recall, forget. `DataPoint` in `cognee/infrastructure/engine/models/DataPoint.py`.

**Identity.** measured. Cognee user plus dataset ACL. `parent_user_id` is child agent accounts. Default graph is one dataset bag. OWL can ground types if you bring an ontology. Companion roles are not shipped.

**Premise.** yes. Recall text is the remember path.

**Eval.** measured. BEAM 0.79 at 100K tokens, 0.67 at 10M, with a README warning that the two runs are not comparable. LLM-judge on synthetic long conversations.

**Fit.** MISFIT. Graph-RAG for agents and code. Custom OWL is not a companion ontology.

### MemOS

Read next. It is the largest OS-shaped product in this slice.

**Types.** measured. Facts, preferences, skill, profile, event, tool memory. Dream `TargetMemoryType` in `src/memos/dream/types.py`. Profile templates bind to `user_id` or `agent_id`. Independent agent memory is a flag, not a character card.

**Loop.** measured. `addMessage` extracts. `searchMemory` returns profile plus hits. The product pastes them into the chat model. Delete by `memory_ids` or wipe `user_id`/`agent_id`.

**Premise.** yes.

**Eval.** measured. README LoCoMo 88.83, LongMemEval 89.20, via OmniMemEval. Fact QA and agent tasks. Not drift or silence.

**Fit.** PARTIAL. User vs agent profile and lockable fields help. Relationship is at best a profile attribute. No silence.

### MemoryOS (BAI-LAB)

Academic OS metaphor. Do not confuse with MemOS.

**Stores.** measured. Short-term QA, mid-term segments, long-term `user_profiles[user_id]` string, user knowledge deque, assistant knowledge deque. `LongTermMemory` in `memoryos-pypi/long_term.py`. Profile merge appends an "Updated on" block.

**Loop.** measured. Add QA. Updater spills STM to mid-term with an LLM. Retriever pulls all four stores into Generation.

**Eval.** measured. README relative LoCoMo F1 +49.11% and BLEU-1 +46.18% versus their baseline. Absolute F1 is an open unknown.

**Fit.** PARTIAL. User vs assistant knowledge exists. Relationship is not a type. Forget is capacity eviction.

### SuperMemory

Managed memory graph plus optional local binary.

**Model.** measured. Documents vs memories vs profile. Edges `updates` / `extends` / `derives`. `isLatest` hides stale facts. Time-based expiry and noise filtering. Isolation is one `containerTag`. Sources. `docs/concepts/graph-memory.md`, `user-profiles.md`.

**Loop.** measured. `add` then dreaming. `profile()` is always-on context. `search` is hybrid RAG plus memory. Official MCP at `mcp.supermemory.ai`.

**Premise.** yes. Profile still rides in the prompt.

**Eval.** measured. README claims #1 on LongMemEval, LoCoMo, ConvoMem. LongMemEval 95% Recall@15 at about 720 tokens.

**Fit.** PARTIAL. Temporal update and forget are real. One tag still mixes user, character, and lore unless the app invents more tags.

### OpenViking

Context filesystem. Strongest identity files in this slice.

**Types.** measured. Resource, Memory, Skill. Files `profile.md`, `identity.md`, `soul.md`, `preferences/`, `entities/`, `events/`, plus peer memories at `viking://user/{user_id}/peers/{peer_id}/memories/`. Source. repo `docs/en/concepts/02-context-types.md`.

**Loop.** measured. `session.commit()` extracts. `find()` is cheap search. `search()` spends an LLM planner. Privacy configs strip secrets from `SKILL.md`, not trauma from chat.

**License.** measured. Repo `LICENSE` is AGPL-3.0. The VitePress footer that says Apache-2.0 is wrong.

**Premise.** mixed. Standing persona files plus retrieve.

**Eval.** measured. README LoCoMo 80-83% with OpenViking vs 24-57% native agent memory. tau2-bench retail/airline lifts.

**Fit.** PARTIAL. `identity`/`soul`/`profile`/`peer` is the right split for a coding agent, not a complete companion ontology. No silence.

### Memori

Agent-native BYODB.

**Attribution.** measured. `entity_id` + `process_id` + `session_id`. Types facts, preferences, skills, rules, events, traces. `_struct.py` `Entity` / `Process` / `SemanticTriple`. Facts are shared across processes for one entity, so a support bot leaks into a sales bot.

**Loop.** measured. Wrap the LLM client. Automatic recall injects facts into the system prompt every call. Augmentation is async.

**Forget.** unknown. The how-memory-works and README pages we read do not name a delete API.

**Eval.** measured. LoCoMo 87.0% judge, 721 tokens. `docs/memori-cloud/benchmark/results.mdx`.

**Fit.** MISFIT. CRM-style user vs agent, not companion roles. Automatic inject is the premise. Supersession not specified.

### memU

Coding-agent wiki sidecar.

**Tracks.** measured. Memory files from messages. Skill files from messages plus tools. `docs/developer.md`. `MemoryService` does not call an LLM. The host agent writes the Markdown.

**Loop.** measured. Scheduled `prepare` / agent jobs / `commit`. Inject seam runs `<binary> retrieve` before answers. No MCP. SKILL.md plus host binaries.

**Temporal.** measured. v1 session schema rejects timestamps.

**Fit.** MISFIT. Personal coding wiki. Shared `~/.memu` across hosts is a cross-character leak if two companions used it.

### EverOS

Read if you want user vs agent tracks with contradiction merge.

**Types.** measured. `episode`, `profile`, `agent_case`, `agent_skill`. `models.py` `_Track` is `user_memory` or `agent_memory`. `sender_id` on every message. Search needs `user_id` or `agent_id`.

**Loop.** measured. `POST /api/v2/memory/add` then async extract. Recommended search hybrid, then generate, then add. Empty search is allowed. Delete and profile edit are Cloud-only per `docs.evermind.ai/llms.txt`.

**Eval.** measured. Same llms.txt. LoCoMo 93.05%, LongMemEval 83.00%.

**MCP.** measured. Community `tt-a1i/evermemos-mcp` linked from README. Not in-repo official.

**Fit.** PARTIAL. Tracks, timestamps, and contradiction merge help a long companion. Relationship is still not a type. No silence. OSS forget is weak.

### LightRAG

Cargo-cult Graph-RAG. Canonical repo `HKUDS/LightRAG`.

**Model.** measured. `ExtractedEntity` / `ExtractedRelationship` in `lightrag/types.py`. Query modes local, global, hybrid, naive, mix. Workspace namespaces a knowledge base, not a person.

**Loop.** measured. Index extracts a document graph. Query pastes entities, relations, and chunks into a QUERY LLM. Document delete rebuilds affected nodes.

**Fit.** MISFIT. Cannot split user vs character vs relationship. A roleplay workspace will merge lore, user facts, and persona into one graph. Paper arXiv 2410.05779 scores corpus QA, not companion memory.

### Microsoft GraphRAG

Cargo-cult Graph-RAG. Canonical repo `microsoft/graphrag`. Maintenance mode as of the README observed 2026-09-11.

**Model.** measured. TextUnits, entities, relations, claims, Leiden communities, community reports. Query local, global, DRIFT, basic. `RAI_TRANSPARENCY.md` intended use is private corpus analysis by trained users.

**Cost.** measured. README. Indexing is expensive. Global search is map-reduce over community reports.

**Fit.** MISFIT. Batch index over a corpus. No companion write path. No identity split. Re-index to forget.

## Where things live

| Need | Card | Primary door |
| --- | --- | --- |
| Official `llms.txt` | cognee, memos, supermemory, openviking, memori, everos | vendor docs indexes listed on the cards |
| No `llms.txt` | memoryos, memu, lightrag, microsoft-graphrag | GitHub README plus named modules |
| User vs agent split | memos, everos, memoryos, openviking | profile/agent_id, `_Track`, assistant_knowledge, identity.md |
| One bag / one workspace | supermemory, memori, cognee, lightrag, microsoft-graphrag, memu | `containerTag`, `entity_id`, dataset, workspace, `~/.memu` |
| Local, permissive license | cognee Apache-2.0, memos Apache-2.0, memoryos Apache-2.0, supermemory MIT, memori Apache-2.0, memu Apache-2.0, everos Apache-2.0, lightrag MIT, graphrag MIT | OpenViking is AGPL-3.0 |
| Official MCP | cognee, memos, memoryos, supermemory, openviking, memori | memU uses SKILL.md. EverOS MCP is community. LightRAG and GraphRAG have none |

## Gotchas

**MemOS vs MemoryOS.** measured. Different orgs. MemTensor/MemOS vs BAI-LAB/MemoryOS.

**OpenViking license.** measured. `LICENSE` is AGPL-3.0. Do not copy the docs footer.

**EverOS delete.** measured. Cloud-only in `llms.txt`. OSS search/add/flush without a documented wipe.

**Memori fact sharing.** measured. Facts for one `entity_id` are visible to every `process_id`. User facts then leak across agents. That is useful for one companion and harmful if two characters should not share a user bag. inferred.

**Graph-RAG cost.** measured. LightRAG extract-per-chunk. GraphRAG community reports. Neither is a cheap per-turn companion writer.

**Evals.** measured. LoCoMo and LongMemEval score assistant fact QA. They do not score character drift, socially wrong recall, joke stored as fact, or poisoned persona. High scores here do not mean FIT.

## Verdicts

| id | companion_fit | reason |
| --- | --- | --- |
| cognee | MISFIT | Dataset KG for agents. No user/character/relationship types unless you bring OWL. |
| memos | PARTIAL | User vs agent profiles and lockable fields. Still retrieve-into-prompt. No silence. |
| memoryos | PARTIAL | User profile vs assistant knowledge. Profile is an appended string. Forget is capacity. |
| supermemory | PARTIAL | Temporal updates and profiles. One `containerTag` bag. No companion kinds. |
| openviking | PARTIAL | `identity`/`soul`/`profile`/`peer` files. Coding-agent OS. AGPL. No silence. |
| memori | MISFIT | Entity/process CRM memory. Auto system-prompt inject. Forget API not found. |
| memu | MISFIT | Coding-agent wiki. No timestamps. Shared store across hosts. |
| everos | PARTIAL | User vs agent tracks, `sender_id`, contradiction merge. No relationship type. Cloud-only delete. |
| lightrag | MISFIT | Document Graph-RAG. One workspace mixes lore and people. |
| microsoft-graphrag | MISFIT | Corpus Q&A in maintenance mode. Batch index. No companion identity. |
