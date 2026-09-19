# by-eval

Benchmark and harness audits: tasks, graders, metrics, rerunnability.

- Protocol: [`PROTOCOL.md`](PROTOCOL.md)
- Census: [`../../pipeline/seed.json`](../../pipeline/seed.json) → `evals`
- Cache: `.cache/by-eval/<slug>/` (gitignored)
- Output: `<slug>/audit.json`

```bash
just harvest-eval locomo
just audit-write-eval locomo
just lint-eval-audits
```

## Status

All **25** `seed.json` eval slugs have lint-clean `audit.json` under this directory.

**ATOD:** OpenReview forum URLs redirect to a bot-check page over HTTP harvest; seed also lists [arXiv HTML](https://arxiv.org/html/2601.11854v2) for full paper text. Harvest keeps seed-listed `open_docs` through redirects (`docs_harvest_url_allowed`).

**Paper-only / monorepo evals** (`clone: false`): `memoryarena`, `msc`, `dulemon` — harvest is docs-only until a dedicated repo exists or we accept a monorepo clone.

Field guide (synthesis, not ledger quotes): [Mnemoverse memory benchmark field guide](https://mnemoverse.com/docs/research/evaluation/ai-memory-benchmarks-field-guide).
