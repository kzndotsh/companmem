# companmem

Research on memory for realistic human and companion communication. Not a retrieve-then-speak product. Not another LoCoMo chase.

**Source of truth:** [`docs/QUESTIONS.md`](docs/QUESTIONS.md). Attach [`companmem-research-gate`](.agents/skills/companmem-research-gate/SKILL.md) for any edit to that file.

## Constraints

- No product implementation at the repo root until groups of questions are `settled` and the user asks for code
- Do not extend [`sandbox/`](sandbox/). Sprint 1 is archived reference (harness, census cards, fixtures)
- Do not commit unless asked
- Cite primary sources. Do not invent citations
- Do not draft an ADR, product spec, or implementation for a question that is `open` or `deferred`
- Settled answers need a **Falsifier:**
- Never commit `.env`, `.cache/`, or cloned harvest trees

## Layout

```
ROADMAP.md                 # human-like companion via memory; direction after evidence
docs/QUESTIONS.md          # active research
docs/decisions/            # ADRs, only after Decide gate (may not exist yet)
research/pipeline/         # harvest / extract / fold / apply (when built)
research/output/
  by-product/             # audit.json per product
  by-paper/               # reserved
  by-eval/                # reserved
sandbox/                   # archived sprint 1. read-only
.agents/skills/            # git-tracked agent skills
.cache/                    # harvest clones and extracts. gitignored + cursorignored
```

Census JSON under `sandbox/research/census/` is a lead (URLs). Do not copy FIT scores into new audits. Do not edit sandbox.

## Research gate

| Gate | Allowed | Blocked until |
|------|---------|---------------|
| Explore | Read sources, draft cited bullets | — |
| Tag | `open` / `deferred` | An answer bullet exists |
| Settle | `settled` | Cited + **Falsifier:** |
| Decide | ADR in `docs/decisions/` | `settled` and user agrees |

Skills: `research`, `evidence-driven-research`, `research-summarizer`, `grill-with-docs`, `adr-drafting`. Versions: [`skills-lock.json`](skills-lock.json).

## Audit records (when present)

Canonical file is `research/output/by-product/<slug>/audit.json`.

- `sources`: URLs we opened (search boundary)
- `ledger`: claims with quote + locator. Lint fails without `url` or `locator`
- `copy` / `refuse`: interpretation. Extract must not invent them
- Search snippets are discovery, not quotes

Pipeline: harvest (no LLM) → one-shot extract (Kiro, no tools) → fold → apply dry-run → lint then write. Harvest fills `.cache/by-product/<slug>/` (clone, docs, issues, blogs, search-then-fetch). `.cache/` stays out of git and Cursor context.

## Commands

```bash
just harvest mem0
just harvest-all         # every product in seed.json
just audit mem0          # extract → fold → apply dry-run
just audit-write mem0    # lint temp, then write audit.json
just audit-write-all
just lint-audits
just synthesize
just test-pipeline
```

Protocol: [`research/output/by-product/PROTOCOL.md`](research/output/by-product/PROTOCOL.md). How-to: [`research/output/README.md`](research/output/README.md).

Env: `KIRO_GATEWAY_URL`, `KIRO_GATEWAY_API_KEY` (fallback `PROXY_API_KEY`). Harvest: `GITHUB_TOKEN`, optional `BRAVE_API_KEY`. See `.env.example`.

## Style

- Conventional commits: `type(scope): subject` (no trailing period). Types: `docs`, `feat`, `fix`, `chore`, `ci`, `refactor`. Scope when useful: `research`, `pipeline`, `sandbox`
- Python (when added): Ruff, 4-space, typed, `Type | None`, no bare `except`, no inline imports, no `any`
- Nested `AGENTS.md` files stay thin. Do not duplicate QUESTIONS.md or schema here
