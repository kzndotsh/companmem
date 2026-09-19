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

All **13** `seed.json` eval slugs have lint-clean `audit.json` under this directory (harvest → extract → fold → apply).

**ATOD:** OpenReview forum URLs redirect to a bot-check page over HTTP harvest; seed also lists [arXiv HTML](https://arxiv.org/html/2601.11854v2) for full paper text. Harvest keeps seed-listed `open_docs` through redirects (`docs_harvest_url_allowed`).

## Seed v2 candidates (not in census yet)

From literature and field guides; add to `evals` after URL/`open_code` quality gate:

| Slug (proposed) | Why | Primary sources |
|-----------------|-----|-----------------|
| `longmemeval-v2` | Agentic web trajectories (up to ~115M tokens); complements chat-history LongMemEval | [arXiv:2605.12493](https://arxiv.org/abs/2605.12493), [xiaowu0162/LongMemEval-V2](https://github.com/xiaowu0162/LongMemEval-V2) |
| `beam` | 128K–10M token coherent dialogues; contradiction / ordering / preference axes | [arXiv:2510.27246](https://arxiv.org/abs/2510.27246), [mohammadtavakoli78/BEAM](https://github.com/mohammadtavakoli78/BEAM) |
| `membench` | Factual + reflective memory; participation vs observation scenarios | [ACL findings](https://aclanthology.org/2025.findings-acl.989/), [import-myself/Membench](https://github.com/import-myself/Membench) |
| `perltqa` | Large-scale personal LT QA (3.4k dialogues) | Du et al., PerLTQA paper + repo (verify canonical URL before seeding) |
| `prefeval` | Long-horizon preference consistency (pairs with PersonaMem) | Zhao et al., PrefEval (arxiv + repo TBD) |
| `dialsim` | TV-show roleplay; very long multimodal-ish context | Kim et al., DialSim |

Cross-cutting: [Mnemoverse memory benchmark field guide](https://mnemoverse.com/docs/research/evaluation/ai-memory-benchmarks-field-guide) (synthesis, not a primary source for ledger quotes).
