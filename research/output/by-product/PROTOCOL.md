# Product memory audit protocol

Mapping study of shipped memory products: what they persist and retrieve, with evidence, so we know what to copy or refuse for companion continuity.

Not a medical systematic review. Kitchenham-style protocol discipline, Wohlin seed list, exclusion log in [`excluded.json`](excluded.json). No PRISMA diagrams.

**Decision lens.** If we built companion memory tomorrow, what is load-bearing, what is cargo-cult, and what would we refuse? Being wrong means cloning retrieve-then-speak or missing a real technique.

Do not write `companion_fit` or fixed multi-axis scores into `audit.json`.

## Research questions

- **RQ1.** What does this product persist and retrieve, per its code and docs?
- **RQ2.** What do users and issues say breaks?
- **RQ3.** What would we copy or refuse for companion continuity?
- **RQ4.** After many `audit.json` files, which mechanisms recur and which gaps are shared?

## Inclusion and exclusion

**Include.** Shipped or actively maintained product/library that stores or injects state across turns for chat or agents.

**Exclude.** Pure papers, pure evals, dead pages with no docs and no repo.

Borderline ids go in [`excluded.json`](excluded.json), not the trash. `by-paper/` and `by-eval/` stay reserved.

## Source quality

| Kind | Treat as |
|------|----------|
| Code at pinned SHA | Behavior |
| Official docs / `llms.txt` | Supported behavior (claims) |
| GitHub issues | Operational limits |
| First-party blog | Claim, interested party |
| Third-party blog / search hit | Discovery until first-party corroborates |

Vendor LoCoMo numbers are scores under *their* harness, not independent companion proof.

**Absence claims** need a search boundary and the page checked: “not in API reference at URL X” is allowed; bare “does not exist” is not. Every `unknowns[]` entry needs `url`.

Search snippets are not evidence. `ledger.kind` is `docs | code | issue | community | blog`. Files under `search/` are saved prose, not ledger proof by themselves.

## Artifacts

| Path | Role |
|------|------|
| [`../../pipeline/seed.json`](../../pipeline/seed.json) | Product census and harvest config (source of truth) |
| `.cache/by-product/<slug>/` | Harvest manifest, pages, extract shards (gitignored) |
| `research/output/by-product/<slug>/audit.json` | Published audit (lint-clean before write) |
| `synthesis.json` | Optional cross-product themes (`just synthesize`; not required for audits) |

Canonical audit fields: `identity`, `claimed_purpose`, `mechanisms`, `ledger`, `sources`, `unknowns`, `copy`, `refuse`, `consensus`, `contested`. Every ledger row needs `url` or `locator` and a non-empty `quote`.

## Seed

Every key in `seed.json` → `products` is in scope (**61** products as of 2026-09-19). No priority slices. Add or change products only in seed, then `just lint-seed` and `just lint-open-code`.

**Required per product:** `id`, `name`, `repo`, `docs`, `clone`, `community`, `skip_url_prefixes`, `open_code`, `open_docs`.

**Optional:** `body_markers` — string list used in harvest to reject third-party search/community pages whose fetched body does not mention the real product (homonyms: MemoryOS vs Kickstarter app, Memori vs journaling, memU vs Android emulator, short names like Vestige). When omitted, name-based matching only.

**Rules:**

- `clone: true` → non-empty `open_code` (paths under cloned repo; list via `just harvest-inventory <id>`).
- `clone: false` → empty `repo` and `open_code`; harvest is docs/blog/search/community only (companion SKUs: Kindroid, Nomi, Character.AI, Replika, Zep Cloud).
- `open_docs` — first-party doc URLs only; may include `llms.txt`. Empty list fails lint.
- `skip_url_prefixes` — never fetch or keep URLs under these prefixes (e.g. Zep must skip Graphiti repo/docs; disambiguate shared hosts).
- `community` — extra forum/thread seeds for the community lane.

**Edge cases (details in seed, not duplicated here):**

- **graphiti** vs **zep** — Graphiti is open repo on help.getzep.com/graphiti; Zep Cloud is closed, separate `open_docs`, no Graphiti paths.
- **letta** — current MemFS / Agent SDK docs; skip legacy v1 memory-block SDK paths in seed skips.
- **sillytavern** — one audit covers worldinfo / vectors / summarize extensions (`excluded.json` `covered_by`).
- **claude-mem** — adjacent coding-agent memory (negative control in research notes).
- **lightrag**, **microsoft-graphrag** — graph-RAG baselines, same audit schema.

Snowball: related products named in harvest can be listed in [Snowball appendix](#snowball-appendix). Do not auto-harvest snowball ids until explicitly added to seed.

## Harvest

No LLM. Output: `.cache/by-product/<slug>/manifest.json` and page trees.

| Lane | Method | Cap |
|------|--------|-----|
| Repo | Shallow clone (`--depth 1 --single-branch`). Skip if `.git` exists unless `--force`. No submodules. `open_code` paths only; missing paths logged. `open_code: []` with `clone: true` fails seed lint. | listed paths |
| Docs | GET `open_docs` URLs. No sitemap snowball, no llms.txt expansion. | listed URLs |
| Issues | GitHub `is:issue` + memory/forget/persona/UX queries; fetch up to 50, keep 20 ranked for product language. | 20 |
| Blog | Product `/blog`, `blog.{apex}`; path-aware when docs use a prefix. | 10 |
| Web search | Forget / lost context / LoCoMo / graph queries; fetch into `search/`. Skip forge chrome, arxiv, mirrors, community hosts, marketing home when docs exist. Third-party pages need product in snippet or `body_markers` in **body** after fetch. | 10 |
| Community | Seed `community` URLs + HN/Reddit/PH/SO/X/Discourse search. Thread must name product; confirm pass replaces weak snippet hits. Reddit via Arctic Shift JSON (`url.txt` stays reddit.com). `body_markers` on fetched body for third-party. | 10 |

**Prose conversion.** GET with `Accept: text/markdown`; local HTML strip; try `.md` / `index.md`; then one markdown.new POST (`method=auto`, 500/day/IP, 429 disables for process). Reddit: Arctic Shift first. No `/crawl`.

Env: `GITHUB_TOKEN` (issues/clone), optional `BRAVE_API_KEY` (search; falls back to DDG). Client-rendered docs may need Playwright (`research/output/README.md`).

## Extract, fold, apply

1. **Extract** — one Kiro call per harvested page (temp 0.1, no tools). Prompt v3: this product only; memory = cross-session state, not retrieve-then-speak. Quote before claim. Prefer store / read / forget / conflict / isolation. Empty `unknowns` beats a laundry list. `label`: `measured` (code/docs behavior), `inferred` (issues, blogs, vendor benches).

2. **Fold** — union pages into `.cache/.../candidate.json`. Drop mechanisms without ledger support. Drop page-local absence unknowns unless same stem on ≥2 URLs. `copy`, `refuse`, `consensus`, `contested` stay empty.

3. **Apply** — merge candidate into `audit.json` (or temp for dry-run). Replaces `claimed_purpose`, `mechanisms`, `unknowns`, `sources`, `ledger`. Preserves non-empty interpretation fields (`copy`, `refuse`, `consensus`, `contested`) when the candidate leaves them empty.

**Interpretation** (`copy`, `refuse`, `consensus`, `contested`) is not extract output. A later human/agent pass fills it for RQ3. There is no `just grill` yet. Re-harvest + apply does not wipe non-empty interpretation.

**Lint:** `just lint-audits` (all published audits). Per file: `uv run --project research/pipeline python -m companmem_pipeline.lint --path research/output/by-product/<slug>/audit.json`.

## Field matrix

`just matrix` writes [`matrix.json`](matrix.json) from lint-clean product audits. No LLM. Axes: persist, retrieve, forget_delete, forget_suppress, conflict_or_supersession, isolation, log_vs_curated, plus `clone` from seed. A true axis needs a **ledger quote that contains the needle** (mechanisms alone do not count). Persist needs a store or cross-session phrase, not a lone "long-term". Retrieve does not use bare `search`. Isolation hits (`user_id`, `group_id`, …) beat miss phrases. Forget delete vs suppress: if both quotes are the same evidence, keep suppress. `contradict` alone is not conflict. Isolation misses still cite a shared/missing-scope quote when there is no hit. `just matrix-dry-run` prints JSON without writing.

## Synthesis

Optional. `just synthesize` writes [`synthesis.json`](synthesis.json) from seed product audits that exist **and** pass `lint_audit` (one Kiro call). After parse, a product id is kept only if an on-card quote supports the sentence by distinctive-token precision (generic field words like persist/retrieve/store/thread do not count; Kiro may omit quotes; post-process attaches them). If the sentence names persist, retrieve, forget, conflict, or isolation, the quote must contain that axis's ledger needles (same family as `matrix.json`). Shared-gap quotes and absence sentences (`no automatic forget`, `no per-user isolation`) must also contain a negation cue (`no`, `not`, `absent`, …) so a delete API cannot evidence “no forget.” Every listed `product_id` must have an evidence quote. Each row is capped at 8 ids. One slug may appear in at most 3 cited rows across themes + recurring + gaps (higher-precision rows kept; rows that fall below 2 ids drop). Split into `clone_true` / `clone_false`; gaps that repeat a theme are dropped. Themes come from compact cards (ranked ledger rows with short quotes, capped unknowns, `clone` from seed). `missing` is seed ids with no file or a lint-fail (`dirty` lists lint-fails). Eval audits are not included. `just synthesize-dry-run` prints JSON without writing. Do not write `synthesis.json` until a dry-run looks good. Run only when you want RQ4 rollup; audits do not depend on it.

## Grill copy / refuse (clusters)

There is no `just grill`. Do not use the ADR-drafting grill skill.

1. Group `matrix.json` rows: extract-then-retrieve, temporal graph, file-as-truth, no isolation, closed companion.
2. For **one or two** clone-true examples per cluster that still have empty `copy`/`refuse`, write short `text` bullets the way `byterover`, `claude-mem`, `hindsight`, `langmem`, `mcp-memory`, and `memobase` already do. Ground in that audit’s ledger. No fake quotes.
3. Closed companions stay in unknowns / contested unless a primary URL supports copy/refuse.
4. Merge only interpretation fields (apply already preserves them). Lint that audit.

Do not fill every product. Pattern plus a handful of cluster exemplars.

## Snowball appendix

None yet. Append candidate ids here when a harvest names a sibling worth seeding later.

## Commands

```bash
just harvest <slug>
just harvest-inventory <slug>
just harvest-all
just audit <slug>              # extract → fold → apply (dry-run)
just audit-write <slug>
just audit-write-all
just lint-audits
just lint-seed                   # structure + optional URL check
just lint-open-code              # open_code paths exist in clones
just matrix
just matrix-dry-run
just synthesize
just synthesize-dry-run
just test-pipeline
```

Pipeline implementation: [`../../pipeline/`](../../pipeline/). Operator notes: [`../README.md`](../README.md).

## Observed

Protocol updated 2026-09-19. Full seed census harvested and audited (`audit.json` per seed id). Interpretation and synthesis are deliberate follow-ons, not gate for publish.
