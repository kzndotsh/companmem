# Slice E. MCP, LangMem, Memobase, Hindsight

Reading path for the eight assigned players. JSON cards under `research/census/cards/` are the record.

Shared premise tested here. If we retrieve the right past text or extracted facts into the prompt, the model will act as if it remembers the relationship. Every player in this slice assumes that sentence except Hindsight's `reflect` path, which still starts from retrieved facts.

Canonical repos for Hindsight and ByteRover were found. `vectorize-io/hindsight` and `campfirein/byterover-cli`.

## How to read this slice

MCP wrappers sit in front of someone else's store. Score the wrapper you can audit. Do not treat Mem0 Platform internals as proven by `mem0-mcp`.

`claude-mem` and ByteRover are coding-agent memory. They are negative controls.

## mcp-memory

Official knowledge-graph memory in `modelcontextprotocol/servers` at `src/memory`. Package `@modelcontextprotocol/server-memory`. `measured`.

Types are `Entity`, `Relation`, and string `observations`. `entityType` is a free string. `measured` from `src/memory/index.ts` `KnowledgeGraphManager`.

Writes are agent tools. `create_entities`, `create_relations`, `add_observations`. Nothing is refused. `measured`.

Reads are model tool calls. `searchNodes` is case-insensitive substring over name, type, and observations. `measured` from `searchNodes` in `src/memory/index.ts`. `read_graph` can dump the whole JSONL.

Supersession is absent. `add_observations` appends. Duplicate entity names are ignored. `measured`.

Temporal fields are absent on `Entity` and `Relation`. `measured`.

Identity is one file (`MEMORY_FILE_PATH`). The README system prompt assumes `default_user`. `measured`.

Silence and poisoning are absent. Matching text always returns. `measured`.

Forgetting is present via `delete_entities`, `delete_observations`, `delete_relations`. `measured`.

Cost is host tokens plus tool calls. The server does no LLM or embed. `measured`.

Local is present. JSONL on disk. Repo `LICENSE` is Apache-2.0 plus remaining MIT. `measured`.

MCP is official. Listed at `https://modelcontextprotocol.io/examples`. `measured`.

Assumes retrieve equals remember. Yes. The README prompt says retrieve from the graph then treat it as memory. `measured`.

Companion fit. MISFIT.

## mem0-mcp

GitHub `mem0ai/mem0-mcp` is archived as of 2026-03-24. `measured` from `gh repo view`. Apache-2.0. 660 stars on 2026-09-11. `measured`.

The archive is FastMCP over `mem0.MemoryClient`. Tools in `src/mem0_mcp_server/server.py` include `add_memory`, `search_memories`, `get_memories`, `update_memory`, `delete_memory`, `delete_all_memories`, `delete_entities`. `measured`.

Replacement is hosted HTTPS MCP at `https://mcp.mem0.ai/mcp`. Docs `https://docs.mem0.ai/platform/mem0-mcp` say nothing runs on your machine. `measured`.

Ontology at this layer is absent. Untyped text plus `user_id` / `agent_id` / `app_id` / `run_id`. `measured`.

Write and read are agent tools. Search is Mem0 semantic search. `measured`.

Supersession is partial. `update_memory` overwrites by id. Add-time consolidation is Mem0 Platform, not this repo. `measured` for overwrite, `unknown` for extract merge.

Temporal is partial. Docs show `created_at` filters. No last-Tuesday parser in the server. `measured`.

Identity split is partial. Coding-agent scopes, not user / character / relationship. `measured`.

Silence and poisoning are absent at the MCP layer. `measured`.

Forgetting is present. Delete tools are in both archive and hosted docs. `measured`.

Cost shape is unknown. Extract runs in Mem0 Platform. `inferred`.

Local is absent. API key required. `measured`.

MCP is present, official then hosted. `measured`.

Assumes retrieve equals remember. Yes. `measured` from hosted docs (save, look up, update).

Companion fit. MISFIT.

## mcp-mem0-community

`coleam00/mcp-mem0`. MIT. 684 stars. Last push 2025-04-13. `measured`.

Three tools in `src/main.py`. `save_memory`, `search_memories` (limit 3), `get_all_memories`. `DEFAULT_USER_ID` is `"user"`. `measured`.

`CUSTOM_INSTRUCTIONS` in `src/utils.py` are not wired. `custom_fact_extraction_prompt` is commented out. `measured`.

Forgetting is absent. No delete tool. `measured`.

Local is partial. Ollama is an option. Supabase `DATABASE_URL` is required. `measured`.

Assumes retrieve equals remember. Yes. The search docstring tells the model to search before decisions. `measured`.

Companion fit. MISFIT.

## langmem

`langchain-ai/langmem`. MIT. 1659 stars. `measured`. Docs `https://langchain-ai.github.io/langmem/concepts/conceptual_guide/`. Fetch of `llms.txt` on that host returned 404. `measured`.

Ontology is partial. Semantic profile or collection, episodic `Episode`, procedural prompt rules. Default collection is a `Memory` string. Callers pass Pydantic schemas. `measured`.

Writes are present. Hot path `create_manage_memory_tool` in `src/langmem/knowledge/tools.py`. Background `create_memory_store_manager`. `measured`.

Reads are present. `create_search_memory_tool` calls `BaseStore.search`. Prompt examples inject hits into the system message. `measured`.

Supersession is partial. Update/delete by id. `enable_deletes` defaults false on the store manager. `measured` from `https://langchain-ai.github.io/langmem/reference/memory/`.

Temporal is absent as a query mode. Store timestamps exist. No last-Tuesday parser. `measured`.

Identity split is partial. `{langgraph_user_id}` namespaces. `measured`.

Silence and poisoning are absent. `measured`.

Forgetting is partial. Delete action exists. Background deletes are off by default. `measured`.

Cost is present. Extra LLM extract and embeds per manager or tool path. `measured`.

Local is present. MIT plus your store and LLM. `measured`.

MCP is absent in the repo and docs fetched. `measured`.

Assumes retrieve equals remember. Yes. `measured`.

Companion fit. PARTIAL.

## memobase

`memodb-io/memobase`. Apache-2.0. 2893 stars. `measured`. Docs index `https://docs.memobase.io/llms.txt`. `measured`.

Ontology is present. Topic/subtopic profile slots and events (summary, tags, profile delta, created time). `measured` from `features/profile/profile.md` and `features/event/event.md`.

Writes are present. Insert `ChatBlob`, buffer, LLM extract. `profile_validate_mode` default true. `profile_strict_mode` optional. `measured`.

Reads are present. `user.context()` injects a Memory block. Optional `chats=` ranking. `max_tokens`. `measured` from `features/context.md`.

Supersession is partial. Slots update and re-summarize at `max_pre_profile_token_size`. `measured` from `references/local_config.md`.

Temporal is partial. Event timestamps and `time_range_in_days`. `measured`.

Identity split is partial. `user_id`. Tips doc says map one app user to many Memobase users for two roleplay agents. `measured` from `practices/tips.md`.

Silence is partial. Default template tells the model not to mention memories unless relevant. Not a trauma gate. `measured` from `features/context.md`.

Poisoning is partial. Validation filters junk extracts, not jailbreaks. `measured`.

Forgetting is present. Delete profile, event, user, blob. `measured` from `api-reference/profiles/delete_profile.md`.

Cost is present. Retrieve compiled profile. Batch insert. They claim about 5x cheaper and faster than mem0. `measured` from `cost.md`. That page is not LoCoMo.

Local is present. Self-host or cloud. `measured`.

MCP is present. `src/mcp` tools `save_memory`, `search_memories`, `get_user_profiles`. `measured` from `templates/mcp.md`.

Assumes retrieve equals remember. Yes. `measured`.

Companion fit. PARTIAL. Closest companion-shaped backend in this slice.

## hindsight

Canonical repo `https://github.com/vectorize-io/hindsight`. MIT. 23449 stars. `measured`. Docs `https://hindsight.vectorize.io/llms.txt` and `llms-full.txt`. `measured`. Paper `https://arxiv.org/abs/2512.12818` (abstract page timed out this session). `measured` that the URL is cited by the README.

Ontology is present. World facts, experiences, observations, mental models. `measured` from README Core Concepts.

Writes are present. `retain()` LLM extract. Optional `wrap_openai` auto retain. `document_id` upsert. `measured`.

Reads are present. `recall()` TEMPR (semantic, BM25, graph, temporal), RRF, rerank. `reflect()` agentic loop plus disposition. `measured`.

Supersession is present. Invalidate archives a unit. Observations refine with evidence. `measured` from README Observations and llms-full curation section.

Temporal is present. Date parse for queries such as last spring. `measured` from `developer/rag-vs-hindsight`.

Identity split is partial. One bank per user in the cookbook. World vs experience is fact kind, not companion identity. `measured`.

Silence is absent. Tags filter only if you tagged. `measured`.

Poisoning is partial. Skepticism on reflect. No trust tags on writes. `measured`.

Forgetting is present. Invalidate, delete, clear. `measured`.

Cost is present. Extract LLM plus four-way recall plus optional reflect loop. `measured`.

Local is present. Docker, pip, embedded pg0, Ollama listed. Cloud optional. `measured`.

MCP is present. Built-in `/mcp/{bank_id}/`. `measured` from README MCP Server.

Assumes retrieve equals remember. Mixed. `recall` still injects facts. `reflect` reasons over them with disposition. The wrapper path recalls then generates. `measured`.

Published eval. Live board `https://benchmarks.hindsight.vectorize.io/` on 2026-09-11. LongMemEval S 94.6%. LoComo 10 92%. PersonaMem 32K 86.6%. BEAM 100K 75%. `measured`. Those benches are conversational fact/retrieval, not companion silence.

Companion fit. PARTIAL.

## byterover

Canonical public repo `https://github.com/campfirein/byterover-cli`. Formerly Cipher. Elastic-2.0. 4958 stars. `measured`. V4 docs `https://docs.byterover.dev/llms.txt`. `measured`.

This is coding-agent project memory. Desktop, spaces, skill commands bind / query / record / dream. `measured`.

Ontology is partial. `bv-topic` with `bv-decision`, `bv-reason`, `bv-fact`. `measured` from `v4/skill/record.md`.

Writes are present. Record after useful work. Dream does not edit. `measured`.

Reads are present. Query returns ranked hits and `should_cite`. Retrieve-nothing is documented. `measured` from `v4/skill/query.md`.

Supersession is partial. Update topic. Dream merge/prune after review. `measured`.

Temporal is unknown. Public V4 docs do not name a time index. `inferred`.

Identity split is absent. Spaces and repos, not persons. `measured`.

Silence and poisoning are absent. `measured`.

Forgetting is partial. `prune.mjs` after Dream. `measured`.

Cost shape is unknown. Query/record LLM cost is unpublished. `inferred`.

Local is partial. ELv2 CLI. V4 Desktop sign-in for spaces. `measured`.

MCP is partial. V4 path is `npx skills add campfirein/skills`. Cipher-era MCP is not the V4 doc path. `measured`.

Assumes retrieve equals remember. Yes. Query then treat hits as constraints. `measured`.

Companion fit. MISFIT. Negative control next to claude-mem.

## claude-mem

`thedotmack/claude-mem`. Apache-2.0. 93673 stars. `measured`. Docs `https://docs.claude-mem.ai/llms.txt`. `measured`. Kind `adjacent-coding-agent`. Negative control.

Ontology is present. Observation types `decision`, `bugfix`, `feature`, `refactor`, `discovery`, `change`. Session summaries. `measured` from `architecture/database.md`.

Writes are present. Hooks plus worker LLM compress. `<private>` tags strip before SQLite. `measured` from `usage/private-tags.md`.

Reads are present. SessionStart inject. MCP/skill search. `measured` from `architecture/overview.md`.

Supersession is absent. Observations append. `measured`.

Temporal is partial. Epoch timestamps and timeline. `measured`.

Identity split is absent. Project and session ids. `measured`.

Silence is partial. Private tags at write time, not retrieve-time social skip. `measured`.

Poisoning is absent. Stored narratives inject later. `inferred` from the pipeline. No trust tags in the database schema. `measured` for schema.

Forgetting is absent as a per-fact forget. Sessions are marked complete, not deleted. `measured`.

Cost is present. Per-tool-use compress plus injected observations. Smart Explore numbers are AST token cost, not memory QA. `measured` from `smart-explore-benchmark.md`.

Local is present. `~/.claude-mem/claude-mem.db`. `measured`.

MCP is present. `mcp-server.cjs`. `measured`.

Assumes retrieve equals remember. Yes. `measured`.

Companion fit. MISFIT.

## Verdicts

| id | companion_fit | reason |
| --- | --- | --- |
| mcp-memory | MISFIT | Substring JSONL graph. No time, identity split, or silence. |
| mem0-mcp | MISFIT | Archived then hosted Mem0 tools. No companion types. Not local. |
| mcp-mem0-community | MISFIT | One `user` id, three tools, no delete. Template. |
| langmem | PARTIAL | Schemas and namespaces exist. Still retrieve-and-inject. No silence. |
| memobase | PARTIAL | Profile slots and events. Roleplay via extra user ids. Prompt-line silence only. |
| hindsight | PARTIAL | Best engine here. Temporal graph, invalidate, local MIT, MCP. Not companion identity. |
| byterover | MISFIT | Coding-agent context tree. Negative control. |
| claude-mem | MISFIT | Coding-agent observations. Negative control. |

## What would change these scores

A first-class character and relationship type with silence that can drop a high embedding hit. None of these eight have that.

Hindsight `reflect` would need a documented path that refuses recall for social reasons, not just disposition tone.

Memobase would need character autobiography and relationship state as types, not a user-id mapping tip.
