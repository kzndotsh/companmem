# Companion-native and academic census

Reading path for slice C. Cards are the record. This file is the order to read them.

Shared premise under test. If we retrieve the right past text or extracted facts into the prompt, the model will act as if it remembers the relationship.

## Overview

Honcho is the only system here that treats users and characters as the same peer type and then reasons in the background. MemoryBank is the classic companion paper that still does retrieve-then-prompt. Generative Agents is a town simulation memory stream. TeleMem is a Mem0-shaped library that isolates per-character `user_id` profiles. The SillyTavern extension is how Honcho enters roleplay clients.

## Honcho

Start here. Docs index is https://docs.honcho.dev/llms.txt. Repo is `plastic-labs/honcho`.

**Write vs read.** measured. `session.add_messages` writes Postgres and enqueues work. The API returns before any LLM. The Deriver then extracts explicit and deductive `Document` rows. The Summarizer rolls short summaries every 20 messages and long summaries every 60. The Dreamer later consolidates, deletes stale facts, writes inductive conclusions, and updates peer cards. Read is `session.context()`, which injects a summary plus recent messages, or `peer.chat()` / `honcho.chat()`, a Dialectic agent that searches memory inline. Sources. architecture.md, get-context.md, chat.md, `src/models.py`.

**Peers and identity.** measured. A Workspace holds Peers and Sessions. A Collection is unique on `(observer, observed, workspace_name)`. `observe_me` is Honcho's view of a peer. `observe_others` builds Alice's view of Bob from sessions Alice actually joined. That is the directional representation. Peer cards are `list[str]` biographical facts, max 40, with optional INSTRUCTION prefix lines. Sources. `src/models.py` Collection, directional-representations.md, peer-card.md.

**Scopes.** measured. A named scope is a projection of the peer's unified representation onto a set of sessions, not a second store. `scope="therapy"` swaps the observer to the scope's own reasoned view. A list of scopes is an allowlist of sessions and returns explicit conclusions only. Unscoped requests still see everything. Scopes follow where a fact was said, not what it is about. Source. scopes.md.

**License and local.** measured. Repo LICENSE is AGPL-3.0. Self-host is documented as `honcho start --setup` or compose. The process will not start without an LLM provider. Defaults are OpenAI. Official MCP lives at https://mcp.honcho.dev and in `mcp/`. Sources. LICENSE, self-hosting.md, mcp.md.

**Premise.** mixed, measured from their own wording. They reject static RAG and say they reconstruct state by exhaustive reasoning. The companion still sees that reconstruction as text stuffed into a prompt via `context()` or a dialectic answer. They do not have a separate rememberer from the chat model.

**Eval.** measured from the research blog they publish. 89.9% LoCoMo with LLM-as-judge, not token F1. 90.4% LongMem S. Haiku alone 83.9% on LoCoMo. Those benches score assistant fact QA. They do not score character drift or social silence. Source. https://plasticlabs.ai/blog/research/Benchmarking-Honcho.

**Gaps.** measured. No silence filter on embedding rank. No poisoning or trust tags. Derived conclusions survive session delete. Peers and individual messages cannot be deleted. Sources. peer-card.md, scopes.md, deleting-data.md.

Dimension sources for every scored dimension.

| dimension | score | label | primary source |
| --- | --- | --- | --- |
| ontology | partial | measured | `src/models.py`, `src/utils/types.py` DocumentLevel |
| write_policy | present | measured | architecture.md, dreaming.md |
| read_policy | present | measured | get-context.md, chat.md |
| supersession | partial | measured | dreaming.md, deleting-data.md |
| temporal | partial | inferred | message `created_at` in `src/models.py`, summary cadence in architecture.md. No last-Tuesday query type. |
| identity_split | present | measured | Collection unique key in `src/models.py`, directional-representations.md |
| silence | partial | measured | INSTRUCTION lines in peer-card.md, provenance not topic in scopes.md |
| poisoning | absent | measured | no trust tags in `src/models.py`, derived rows survive session delete in deleting-data.md |
| forgetting | partial | measured | deleting-data.md |
| cost_shape | present | measured | architecture.md, dreaming.md, chat.md reasoning_level |
| local | partial | measured | LICENSE AGPL-3.0, self-hosting.md |
| mcp | present | measured | mcp.md, https://mcp.honcho.dev |

## Honcho SillyTavern

Read after Honcho. Source. https://honcho.dev/docs/v3/guides/integrations/sillytavern.md.

**What it is.** measured. A SillyTavern client extension plus a Node plugin that proxies to Honcho. Installer clones `plastic-labs/sillytavern-honcho`. That GitHub repo is archived, 8 stars, observed 2026-09-11. The v3 docs page is still live and still points at that install.

**Read path.** measured. Every generation injects `session.context()` with stale-while-revalidate. Modes are Context only, Reasoning (default, `peer.chat()` every N turns), and Tool call (`honcho_query_memory`, `honcho_save_conclusion`, `honcho_search_history`). First turn of a session blocks to fill the cache. Later turns add zero extra latency from cache.

**Identity.** measured. By default only the user peer is derived. The character's persona stays on the SillyTavern card. Group chats register one peer per character. Peer mode can share one user peer across personas or isolate a peer per persona.

**Premise.** mixed. Same as Honcho, plus ST prompt injection. Context-only can retrieve nothing on a fresh session, measured from the guide.

| dimension | score | label | primary source |
| --- | --- | --- | --- |
| ontology | partial | measured | sillytavern.md Peer Observability |
| write_policy | partial | measured | sillytavern.md tool-call `honcho_save_conclusion` |
| read_policy | present | measured | sillytavern.md context injection and enrichment modes |
| supersession | partial | measured | sillytavern.md Reset, plus Honcho dreaming.md |
| temporal | partial | measured | sillytavern.md Refresh every N turns, Reason every N turns |
| identity_split | partial | measured | sillytavern.md peer mode and group chats |
| silence | absent | measured | no silence knob in sillytavern.md |
| poisoning | absent | inferred | `honcho_save_conclusion` with no trust tags in the guide |
| forgetting | partial | measured | sillytavern.md Reset orphans the session |
| cost_shape | present | measured | sillytavern.md first-turn block and SWR |
| local | partial | measured | sillytavern.md requires a Honcho API key, archived repo |
| mcp | absent | measured | this path is an ST extension, not MCP. Honcho MCP is mcp.md |

## MemoryBank / SiliconFriend

Zhong et al., AAAI 2024, arXiv 2305.10250. Code `zhongwanjun/MemoryBank-SiliconFriend`, MIT, 449 stars, last push 2023-05-24.

**Ontology.** measured. Per-user JSON with dated `history`, daily `summary`, daily `personality`, `overall_history`, `overall_personality`. `summarize_memory.py` is the writer. SiliconFriend is the companion demo, LoRA-tuned on 38k psychological dialogs for ChatGLM and BELLE.

**Read.** measured. Current utterance embeds and FAISS-retrieves turns and summaries (`LocalMemoryRetrieval.search_memory`, `VECTOR_SEARCH_TOP_K = 6`). Those chunks plus the global portrait go into the next prompt. This is the shared premise, labeled yes.

**Forgetting.** measured. `forget_memory.py` `forgetting_curve(t, S)` and `MemoryForgetterLoader.initial_load_forget_and_save` drop turns when `random() > retention_probability`. Recalled items increment `memory_strength`. There is no user "forget that".

**Eval.** measured. 194 probing questions on 10 days of ChatGPT-simulated chats with 15 users. Best variant SiliconFriend ChatGPT English correctness 0.716. That is fact recall in a companion framing, not silence or identity drift. Source. paper Table 2.

| dimension | score | label | primary source |
| --- | --- | --- | --- |
| ontology | partial | measured | paper §2.1, `memory_bank/summarize_memory.py` |
| write_policy | present | measured | paper §3, `summarize_memory.py` |
| read_policy | present | measured | paper §2.2, `search_memory` top_k=6 |
| supersession | absent | inferred | dated JSON keys in `summarize_memory.py`, no delete-on-contradiction |
| temporal | partial | measured | YYYY-MM-DD history keys, `forget_memory.py` day deltas |
| identity_split | absent | measured | one JSON object per `user_name` |
| silence | absent | measured | FAISS top-k in `search_memory`, no filter in paper or `forget_memory.py` |
| poisoning | absent | measured | retrieved dialog text goes into the prompt, paper §2.2 |
| forgetting | present | measured | `forget_memory.py`, paper §2.3 Ebbinghaus |
| cost_shape | partial | inferred | one query embed plus FAISS then companion LLM, summaries offline |
| local | partial | measured | MIT LICENSE, ChatGLM/BELLE plus local MiniLM/FAISS |
| mcp | absent | measured | 2023 research repo, no MCP in the tree |

## Generative Agents

Park et al., UIST 2023, arXiv 2304.03442. Code `joonspk-research/generative_agents`, Apache-2.0, 22090 stars.

**Memory stream.** measured. `ConceptNode` in `associative_memory.py` with types `event`, `thought`, `chat`, SPO, poignancy, embeddings, `created`, `expiration`, `last_accessed`. Reflection writes higher-depth thoughts whose `filling` cites evidence ids.

**Retrieve.** measured. `new_retrieve` in `retrieve.py` uses weights `gw = [0.5, 3, 2]` on recency, relevance, importance, top 30, and refreshes `last_accessed`.

**Fit.** MISFIT. measured from the architecture. Each persona remembers a simulated town. There is no companion user, no relationship type, no silence. Eval is believability of sandbox behavior.

**Premise.** mixed. Retrieval still injects natural-language memories into planning and dialogue prompts. Reflection adds a synthesis step the raw RAG products skip.

| dimension | score | label | primary source |
| --- | --- | --- | --- |
| ontology | present | measured | `associative_memory.py` ConceptNode |
| write_policy | present | measured | paper architecture, `add_event` / `add_thought` / `add_chat` |
| read_policy | present | measured | `retrieve.py` `new_retrieve` |
| supersession | absent | measured | prepend-only in `associative_memory.py` |
| temporal | present | measured | `created`, `expiration`, `last_accessed`, recency decay |
| identity_split | partial | measured | one stream per persona, no companion user |
| silence | absent | measured | score-max in `retrieve.py` |
| poisoning | absent | measured | perceived text stored as natural language |
| forgetting | partial | measured | `expiration` field, recency decay. Enforce-at-retrieve is unknown |
| cost_shape | present | inferred | paper notes cost, released code uses OpenAI ChatGPT |
| local | partial | measured | Apache-2.0 LICENSE, runtime in the paper is ChatGPT |
| mcp | absent | measured | 2023 UIST research code |

## TeleMem

`TeleAI-UAGI/telemem`, Apache-2.0, 489 stars. Docs https://teleai-uagi.github.io/telemem/. Paper arXiv 2601.06037. Claims character memory for role-play and companions.

**Write.** measured. `TeleMemory` subclasses `mem0.Memory`. `add` / `add_batch` extract with `get_person_prompt` when `user_id` is set, or `get_recent_messages_prompt` for the shared `events` scope. `infer=False` stores raw text. Batch flush clusters by cosine then LLM-fuses and ADDs (`_flush_buffer`).

**Read.** measured. `search` always queries the named `user_id` and also `events`, tags `source`, optional rerank, then truncates to `limit`. The LangChain example injects hits into the system prompt. Premise is yes.

**Identity.** partial, measured. `examples/multi_npc.py` writes one private profile per NPC plus shared events. Cross-character private facts are the selling point. World plot still comes back on every character search because events are always included.

**Local and MCP.** measured. Default stack is local Qwen or Ollama plus FAISS. Official `telemem[mcp]` server with eight tools including `delete_memory`.

**Eval.** measured from their site. ZH-4O 86.33% QA versus Mem0 70.20%. 600-turn Chinese multi-character dialogues. In-repo LongMemEval harness exists. README does not print a LongMemEval number.

**Gaps.** measured. No silence. No trust tags. Fusion ADDs fused summaries. Unclear whether old vector ids are deleted.

| dimension | score | label | primary source |
| --- | --- | --- | --- |
| ontology | partial | measured | `telemem/mem0.py` `add_batch`, events scope |
| write_policy | present | measured | `telemem/mem0.py` infer path and `_flush_buffer` |
| read_policy | present | measured | `telemem/mem0.py` `search`, `examples/langchain_memory.py` |
| supersession | partial | measured | `_flush_buffer` ADD after fusion, MCP `update_memory` |
| temporal | partial | inferred | `run_id` scene scope in `mem0.py` |
| identity_split | partial | measured | `examples/multi_npc.py`, search still mixes events |
| silence | absent | measured | `search` is cosine plus rerank, no filter in mem0.py or MCP.md |
| poisoning | absent | measured | extracted strings stored as trusted memory |
| forgetting | partial | measured | MCP.md `delete_memory`, `delete_all_memories` |
| cost_shape | present | measured | extract LLM plus embed plus fusion LLM in `add` / `add_batch` |
| local | present | measured | Apache-2.0, site default Qwen or Ollama plus FAISS |
| mcp | present | measured | docs/MCP.md, `telemem[mcp]` |

## Gotchas

- Honcho AGPL is real (measured, repo LICENSE). Local intimate chat is possible. Network service of a modified copy triggers AGPL §13.
- Honcho hosted evals are not companion evals (measured). LoCoMo here is LLM-as-judge on assistant QA.
- SillyTavern Honcho does not grow a character memory by default (measured). Character-as-peer is extra configuration, not the panel default.
- TeleMem `search(user_id=character)` is not a closed character vault (measured). The events scope is always mixed in.
- MemoryBank forgetting is stochastic at index rebuild time (measured). It is not a user command and it is not guaranteed gone next turn.
- Generative Agents `expiration` is stored (measured). Whether retrieve drops expired nodes is an open unknown.

## Verdicts

| id | companion_fit | reason |
| --- | --- | --- |
| honcho | PARTIAL | Closest engine. Peers, directional views, scopes, dialectic. No silence or poisoning. Evals are assistant QA. AGPL. |
| honcho-sillytavern | PARTIAL | Real RP client path. Derives the user, not the character. Hosted key. Archived extension repo. |
| memorybank | PARTIAL | Classic companion RAG plus forget curve and user portrait. One user bag. 194 fact probes. |
| generative-agents | MISFIT | Town NPC memory stream. Not a 1:1 companion store. |
| telemem | PARTIAL | Per-character profiles plus events, local, MCP. Still Mem0 retrieve-into-prompt. |
