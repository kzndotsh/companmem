# Census discoveries

Slice E extras only. Required player cards are under `research/census/cards/`.

- Mem0 replaced archived `mem0ai/mem0-mcp` with hosted MCP at `https://mcp.mem0.ai/mcp` (docs `https://docs.mem0.ai/platform/mem0-mcp`). Same tool family, memories stay in the Mem0 account.
- Hindsight ships `@vectorize-io/hindsight-coding-agents` (per-repo bank from git and sessions). Adjacent coding-agent overlap with `claude-mem` and ByteRover. Not a separate required id.
- ByteRover V4 is Desktop plus spaces plus `npx skills add campfirein/skills`. The public engine repo is `campfirein/byterover-cli` (formerly Cipher, Elastic-2.0). Query ranking internals are not in the V4 skill docs.
- Official MCP memory search is substring, not embeddings. `KnowledgeGraphManager.searchNodes` in `modelcontextprotocol/servers` `src/memory/index.ts`.
- Memobase first-party MCP lives in `memodb-io/memobase` `src/mcp` (`save_memory`, `search_memories`, `get_user_profiles`), separate from both mem0 MCP servers.
