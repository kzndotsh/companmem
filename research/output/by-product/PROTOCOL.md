# Product memory audit protocol

Frozen before harvest. Mapping study of shipped memory products: what they persist and retrieve, with evidence, so we know what to copy or refuse for companion continuity.

Not a medical systematic review. Steal Kitchenham protocol-first discipline, Wohlin seed+snowball, and an exclusion log. Drop PRISMA diagrams.

**Decision.** If we built companion memory tomorrow, what in this system is load-bearing, what is cargo-cult, and what would we refuse? Being wrong means cloning a retrieve-then-speak stack or missing a real technique.

Census JSON cards under `sandbox/research/census/cards/` are harvest leads (URLs). Do not copy `companion_fit` or 12-axis scores into `audit.json`. Do not edit sandbox.

## Research questions

- **RQ1.** What does this product persist, and what does it retrieve, according to its own code and docs?
- **RQ2.** What do users and issues say breaks?
- **RQ3.** What would we copy, and what would we refuse, for companion continuity?
- **RQ4.** After several `audit.json` files, which mechanisms recur, and which gaps are shared?

## Inclusion and exclusion

**Include.** A shipped or actively maintained product or library that stores or injects state across turns for chat or agents.

**Exclude.** Pure papers. Pure evals. Dead pages with no docs and no repo.

Borderline items go in [`excluded.json`](excluded.json), not the trash.

## Source quality

| Kind | Treat as |
|------|----------|
| Code at a pinned SHA | Behavior |
| Official docs / `llms.txt` | Supported product behavior (claims) |
| GitHub issues | Operational limits |
| First-party blog | Claim, interested party |
| Third-party blog / search hit | Discovery until a first-party page corroborates |

Vendor LoCoMo numbers are scores under *their* harness. Do not treat them as independent of that reader and scaffold.

Absence needs a search boundary **and the page it was checked on**: "not in the inspected API reference at URL X" is allowed. "Does not exist" is not. `unknowns[].url` is required.

## Search

**Seed.** Every id in `seed.json`. Then snowball: related-work pages, issues, and blogs that name siblings. Append new ids to the snowball appendix below. Do not auto-harvest snowball ids in v1.

**Harvest** (no LLM) into `.cache/by-product/<slug>/`:

| Lane | Method | Cap |
|------|--------|-----|
| Repo | `git clone --depth 1 --single-branch`. Skip if `.git` exists unless `--force`. No submodules. Closed products skip clone. Manifest `repo` is the public https URL, not `ssh://`. License: AGPL before GPL. | **Inclusion list.** `seed.json` `open_code` is the files to copy, picked by looking at the tree (`just harvest-inventory <id>`). Harvest fetches those paths only. No memory-word ranker. No cap-fill. Missing listed paths are skipped and recorded. `open_code: []` means inspected, no code. Missing `open_code` is an error. |
| Docs | GET the URLs in `seed.json` `open_docs`. First-party only. No sitemap snowball. No llms.txt link expansion. Missing `open_docs` is an error. Empty list means no docs pages. | listed URLs |
| Issues | GitHub search `is:issue` plus memory/forget/persona/"lost context"/"user experience". Fetch up to 50, drop bots/dependabot/chore/duplicates, rank UX/product language over stack-trace bugs. | 20 |
| Blog | Census URLs that are not forge hosts. `/blog` on the product site (apex if docs are on `docs.` / `help.`) | 10 |
| Web search | Claim-shaped queries (forget / lost context / LoCoMo / graph). Fetch landing pages into `search/`. First-party extras and third-party pages that name the product. Skip marketing home when `open_docs` is listed. Wikipedia `site:` only if `clone` is false. Skip community hosts, forge chrome, arxiv, DeepWiki / GitHub Pages mirrors. Do not expand `open_docs`. Snippets are not evidence. | 10 |
| Community | Seed forum URLs plus web search on HN, Reddit, Product Hunt, Stack Overflow, X/Twitter, Discourse/forums. Thread URL or title must name the product. A snippet-only mention is not enough: one confirm search on that host (`intitle` / Product Hunt `/products/<id>`) keeps or replaces the URL. Harvest stays no LLM. Skip profile/home URLs. Quality `medium`. Reddit `/comments/` and `redd.it` threads fetch post + comments from [Arctic Shift](https://github.com/ArthurHeitmann/arctic_shift) JSON so the JS shell does not empty the body. `url.txt` stays the reddit.com link. | 10 |

Search snippets are not evidence. `ledger.kind` is `docs \| code \| issue \| community \| blog`. The `search/` folder is where the file was saved.

**Prose conversion.** Docs, blog, search, and community GET with `Accept: text/markdown`. Native markdown is stored as-is. HTML is stripped locally. If origin fails or the strip is thin, try the same path with `.md` (skip if the URL already has an extension). Then one [markdown.new](https://markdown.new/) POST (`method=auto`). A first-party `.md` URL is the source; markdown.new keeps the origin URL. Reddit thread URLs try Arctic Shift first (`converter: arctic_shift`) and fall back to that HTML path if the API misses. Do not use `/crawl`. Git clone and GitHub issue search stay as they are. markdown.new is 500 requests/day/IP; a 429 disables it for the rest of the process.

## Extraction and fold

One Kiro call per harvested page, temperature 0.1, no tools. Prompt v3: extract **this product only**; memory is persistent cross-session state, not retrieve-then-speak. Quote before claim. Prefer store/reader/forget/conflict/isolation when the page states them. Empty unknowns beat a laundry list. `label` is `measured` for verbatim code/docs behavior, `inferred` for issues/blogs/vendor benches. LoCoMo-class scores stay inferred.

Fold unions pages into one candidate. Drop `claimed_purpose` / `mechanisms` that do not match a ledger quote or overlapping claim text. Do not emit `claim_ids`. Drop a page-local absence unknown ("not on this page/file") unless the same stem appears on two or more URLs. `copy`, `refuse`, `consensus`, `contested` stay empty after fold.

Those four fields are **interpretation**: what we would copy or refuse from this product for companion continuity, and what the sources agree or fight about. They are not quotes. Extract is forbidden from filling them. There is no `just grill` yet. A later human/agent pass writes them into `audit.json`. Apply keeps non-empty values so a harvest rerun does not wipe that work.

Apply replaces `claimed_purpose`, `mechanisms`, `unknowns`, `sources`, and `ledger` from the candidate. Keep non-empty `copy` / `refuse` / `consensus` / `contested`.

Every ledger row needs `url` or `locator`. Lint fails otherwise.

## Synthesis

After `audit.json` files exist, write [`_synthesis.json`](_synthesis.json) over **all of them**. Themes from ledgers, not from a predefined axis list. If several products share retrieve-then-speak with no forget/update, that is a theme. Vendor LoCoMo is not companion proof. Missing seed products are listed in `missing`; they are not a reason to wait.

## Seed

Every id in [`../../pipeline/seed.json`](../../pipeline/seed.json) is in scope. No priority slices. Census cards are URL leads only.

Ids from [`sandbox/research/_contracts/PLAYER-LIST.md`](../../../sandbox/research/_contracts/PLAYER-LIST.md).

| id | name | repo | docs | notes |
| --- | --- | --- | --- | --- |
| mem0 | Mem0 | https://github.com/mem0ai/mem0 | https://docs.mem0.ai/llms.txt | |
| graphiti | Graphiti | https://github.com/getzep/graphiti | https://help.getzep.com/graphiti | |
| zep | Zep Cloud | none (closed core) | https://help.getzep.com/llms.txt | Skip clone. Docs, blog, search only. Do not treat Graphiti code as Zep Cloud behavior |
| letta | Letta | https://github.com/letta-ai/letta | https://docs.letta.com/llms.txt | Follow GitHub redirect to letta-code |
| cognee | Cognee | https://github.com/topoteretes/cognee | census | |
| memos | MemOS | https://github.com/MemTensor/MemOS | census | |
| memoryos | MemoryOS | https://github.com/BAI-LAB/MemoryOS | census | |
| supermemory | SuperMemory | https://github.com/supermemoryai/supermemory | census | |
| openviking | OpenViking | https://github.com/volcengine/OpenViking | census | |
| memori | Memori | https://github.com/MemoriLabs/Memori | census | |
| memu | memU | https://github.com/NevaMind-AI/memU | census | |
| everos | EverOS | https://github.com/EverMind-AI/EverOS | census | |
| lightrag | LightRAG | census | census | Graph-RAG cargo-cult. Same schema |
| microsoft-graphrag | Microsoft GraphRAG | census | census | Graph-RAG cargo-cult. Same schema |
| honcho | Honcho | https://github.com/plastic-labs/honcho | https://docs.honcho.dev/llms.txt | |
| telemem | TeleMem | https://github.com/TeleAI-UAGI/telemem | census | |
| sillytavern | SillyTavern | https://github.com/SillyTavern/SillyTavern | census | One audit covers worldinfo/vectors/summarize |
| agnai | Agnai | census | census | If the repo is still alive |
| risuai | RisuAI | census | census | If the repo is still alive |
| kindroid | Kindroid | none | census | Closed. Docs/blogs/search only |
| nomi | Nomi.ai | none | census | Closed. Docs/blogs/search only |
| characterai | Character.AI | none | census | Closed. Docs/blogs/search only |
| replika | Replika | none | census | Closed. Docs/blogs/search only |
| mcp-memory | MCP official knowledge-graph memory | census | census | |
| mcp-mem0-community | coleam00/mcp-mem0 | https://github.com/coleam00/mcp-mem0 | census | |
| langmem | LangMem | census | census | |
| memobase | Memobase | census | census | |
| hindsight | Hindsight | census | census | |
| byterover | ByteRover | census | census | |
| claude-mem | claude-mem | https://github.com/thedotmack/claude-mem | census | Negative control (`adjacent-coding-agent`) |

`st-worldinfo`, `st-vectors`, `st-summarize` → `covered_by: sillytavern`. `honcho-sillytavern` → `covered_by: honcho`. `mem0-mcp` → `archived`. `memorybank`, `generative-agents` → `academic_paper` (arxiv + demo repo; not product harvest). See [`excluded.json`](excluded.json). `by-paper/` stays reserved until a paper protocol exists.

## Snowball appendix

None yet. Append ids here when a harvest names a sibling. Do not auto-harvest snowball ids in v1.

## Observed

Protocol frozen 2026-09-11. Seed is the full product list; harvest and extract treat every id equally.
