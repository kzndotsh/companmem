# Eval / benchmark audit protocol

Mapping study of **official memory and long-dialogue benchmarks and harnesses**: tasks, graders, metrics, and limitations — with evidence — so we know what companion exams should steal or refuse.

Not a leaderboard chase. Do not invent scores not on the page.

Product memory audits live under [`../by-product/PROTOCOL.md`](../by-product/PROTOCOL.md). Pure evals are **excluded** from the product census.

## Research questions

- **RQ-E1.** What tasks and inputs does this benchmark define (splits, format, session structure)?
- **RQ-E2.** How are responses scored (exact match, LLM judge, human, rubric)?
- **RQ-E3.** What do the primary metrics actually measure (and what do they miss for companion continuity)?
- **RQ-E4.** Where does this benchmark fail to test remembering-as-behavior (timing, restraint, conflict, activation)?
- **RQ-E5.** Can a third party rerun the harness (open data, open grader, pinned deps)?

## Inclusion and exclusion

**Include.** Published benchmark or official harness with defined tasks + scoring; paper + repo or docs-only when `clone: false`.

**Exclude.** Vendor blog LoCoMo numbers without harness; product `eval/` scorecards inside memory libraries (audit as **product**); awesome-list rows without primary sources.

## Semantic mapping (same JSON schema as products)

| Field | Eval meaning |
|--------|----------------|
| `identity` | Benchmark id, paper URL, repo, commit |
| `claimed_purpose` | What authors claim the benchmark measures |
| `mechanisms` | Task design, dataset construction, grader pipeline, reported metrics |
| `ledger` | Verbatim quotes on tasks, metrics, judge rules, splits, leakage |
| `unknowns` | Gaps on canonical task/grader docs only |
| `copy` / `refuse` | Empty after fold; later = adopt/reject for **our** exam |

## Source quality

| Kind | Treat as |
|------|----------|
| `paper` | Task/metric claims (arxiv, ACL HTML, PDF landing) |
| `code` | Actual grader/runner behavior |
| `docs` | README, dataset card, official site |
| `issue` | Reproducibility, judge bugs, data leakage reports |

`ledger.kind` is `docs | code | issue | community | blog | paper`. Community/blog lanes are not harvested in eval v1.

**Absence claims** need a URL on the canonical doc checked. Do not ledger leaderboard numbers unless the same page defines the metric and harness.

## Artifacts

| Path | Role |
|------|------|
| [`../../pipeline/seed.json`](../../pipeline/seed.json) → `evals` | Eval census and harvest config |
| `.cache/by-eval/<slug>/` | Harvest manifest, pages, extract shards (gitignored) |
| `research/output/by-eval/<slug>/audit.json` | Published audit (lint-clean before write) |

Shared extract → fold → apply rules match by-product where identical; eval uses **eval-v1** extract prompt and a lighter fold profile.

## Seed

Every key in `seed.json` → `evals` is in scope. Same required fields as products: `id`, `name`, `repo`, `docs`, `clone`, `community`, `skip_url_prefixes`, `open_code`, `open_docs`.

- `clone: true` → non-empty `open_code` (eval scripts, grader paths).
- `clone: false` → empty `repo` and `open_code` (e.g. closed scorecard sites).
- `open_docs` may include arxiv, Hugging Face dataset cards, and paper HTML; seed-listed URLs are always in the search boundary.
- No slug may appear in both `products` and `evals`.

## Harvest (eval profile)

Lanes: **repo**, **docs**, **issues** only (no blog, search, community).

Issues query targets metrics, judges, splits, leakage, reproducibility — not companion UX “forgot my name” threads.

## Commands

```bash
just harvest-eval <slug>
just harvest-eval-inventory <slug>
just audit-write-eval <slug>
just lint-eval-audits
just lint-seed          # products + evals
```

Product commands unchanged (`just harvest`, `just audit-write`, `just lint-audits`, `just synthesize`).
