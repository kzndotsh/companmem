# companmem

Research on memory for realistic human and companion communication. Not a retrieve-then-speak product. Not another LoCoMo chase.

This is mission-critical work. The mission is to build the memory technology that makes the most human-like companion we can, then show it with a number someone else can rerun. We still do not know what we are shipping, and we still do not know what that number measures. The field map exists so we do not copy everyone else's extract-and-search pipeline. The missing piece is a number we would bet the company on. We get it by running the same situation on our companion and on other products, then reading a result someone else can run again. That number is what tells us the product. Path: [`TODO.md`](TODO.md). Docs: [`docs/INDEX.md`](docs/INDEX.md).

An example in [`TODO.md`](TODO.md) or [`README.md`](README.md) is not the assignment. A single borrowed probe is not the exam. Product code at the repo root stays blocked until questions are `settled` and the user asks.

**Source of truth:** the question docs listed in [`docs/QUESTIONS.md`](docs/QUESTIONS.md). Attach [`companmem-research-gate`](.agents/skills/companmem-research-gate/SKILL.md) for any edit to those files.

## Constraints

- No product implementation at the repo root until groups of questions are `settled` and the user asks for code
- Do not commit unless asked
- Cite primary sources. Do not invent citations
- Do not draft an ADR, product spec, or implementation for a question that is `open` or `deferred`
- Settled answers need a **Falsifier:**
- Never commit `.env`, `.cache/`, or cloned harvest trees

## Layout

```
TODO.md                    # roadmap. Pending and done
IDEA.md                    # not work yet
mise.toml                  # Python 3.11 + venv (.venv/) managed by mise
pyproject.toml             # pytest config (root-level, scoped to tests/)
pyrightconfig.json         # basedpyright config pointing at harness/ + tests/
harness/                   # eval harness package (runner, scorer, trial, world, adapters)
tests/                     # unit tests for harness (75 tests; pytest --import-mode=importlib)
evals/fixtures/            # 9 behavior-coded eval fixtures (b0/b1/b3/b5 prefix convention)
evals/results/             # run output — gitignored, ephemeral
experiments/               # time-boxed pilots. Not maintained product code
docs/INDEX.md              # which doc owns what
docs/QUESTIONS.md          # index of the question docs
docs/PROCESS.md            # how we run the research
docs/DEFINITIONS.md        # what the words mean
docs/CONTEXT.md            # prompt versus memory
docs/MEMORY.md             # what a store has to do
docs/BEHAVIORS.md          # what would count as knowing a person (B0–B8)
docs/FIELD.md              # what already exists, and who it is for
docs/EXAM.md               # how we would tell if a behavior happened
docs/BUILDING.md           # how the work would get built, once settled
docs/INSIGHTS.md           # checked paper reads
docs/EVALS.md              # how those benchmarks cluster
docs/PIPELINE.md           # how an audit is produced
docs/AUDIT.md              # per-product notes for all 61 audited products, with synthesis
artifacts/                 # one-off outputs: eval grids, audit analysis, artifact documents
docs/decisions/            # ADRs, only after Decide gate (may not exist yet)
research/pipeline/         # harvest / extract / fold / apply
research/output/           # audit.json records. See docs/PIPELINE.md
.agents/skills/            # git-tracked agent skills
.kiro/specs/               # Kiro spec files (requirements → design → tasks)
.cache/                    # harvest clones and extracts. gitignored + cursorignored
```

## Research gate

| Gate | Allowed | Blocked until |
|------|---------|---------------|
| Explore | Read sources, draft cited bullets | — |
| Tag | `open` / `deferred` | An answer bullet exists |
| Settle | `settled` | Cited + **Falsifier:** |
| Decide | ADR in `docs/decisions/` | `settled` and user agrees |

Skills: `research`, `evidence-driven-research`, `research-summarizer`, `grill-with-docs`, `adr-drafting`, `finalize`. Versions: [`skills-lock.json`](skills-lock.json).

## Audit records (when present)

Canonical file is `research/output/by-product/<slug>/audit.json`.

- `sources`: URLs we opened (search boundary)
- `ledger`: claims with quote + locator. Lint fails without `url` or `locator`
- `copy` / `refuse`: interpretation. Extract must not invent them
- Search snippets are discovery, not quotes

Pipeline: harvest (no LLM) → one-shot extract (Kiro, no tools) → fold → apply dry-run → lint then write. Products: `.cache/by-product/<slug>/` (six harvest lanes). Evals: `.cache/by-eval/<slug>/` (repo, docs, issues only). `seed.json` has `products` and `evals`. `.cache/` stays out of git and Cursor context.

## Commands

```bash
# Harness
.venv/bin/python -m harness run --baseline oracle          # 9/9 PASS smoke test
.venv/bin/python -m harness run --baseline naive-retrieve  # 9/9 FAIL baseline
.venv/bin/python -m harness run --baseline <id> --behavior <b0|b1|b3|b5>
.venv/bin/python -m pytest tests/ -q                       # 75 unit tests
.venv/bin/ruff check harness/ tests/                       # lint
.venv/bin/pip install -e "harness/[dev]"                   # first-time venv setup

# Research pipeline
just harvest mem0
just harvest-all         # every product in seed.json
just harvest-eval locomo
just audit mem0          # extract → fold → apply dry-run
just audit-write mem0    # lint temp, then write audit.json
just audit-write-eval locomo
just audit-write-all
just lint-audits
just lint-eval-audits
just lint-seed          # validate seed.json products + evals
just synthesize
just synthesize-dry-run
just matrix
just matrix-dry-run
just test-pipeline
```

Protocol: [`research/output/by-product/PROTOCOL.md`](research/output/by-product/PROTOCOL.md). How-to: [`research/output/README.md`](research/output/README.md).

Env: `KIRO_GATEWAY_URL`, `KIRO_GATEWAY_API_KEY` (fallback `PROXY_API_KEY`). Harvest: `GITHUB_TOKEN`, optional `BRAVE_API_KEY`. See `.env.example`.

## Style

- Conventional commits: `type(scope): subject` (no trailing period). Types: `docs`, `feat`, `fix`, `chore`, `ci`, `refactor`. Scope when useful: `harness`, `evals`, `tests`, `specs`, `research`, `pipeline`
- Python (when added): Ruff, 4-space, typed, `Type | None`, no bare `except`, no inline imports, no `any`
- Nested `AGENTS.md` files stay thin. Do not duplicate the question docs or schema here
