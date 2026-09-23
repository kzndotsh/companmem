# Pipeline

How an audit is produced. The records are not in this folder.

Product audits: [`research/output/by-product/PROTOCOL.md`](../research/output/by-product/PROTOCOL.md). Eval audits: [`research/output/by-eval/PROTOCOL.md`](../research/output/by-eval/PROTOCOL.md). Commands and query examples: [`research/output/README.md`](../research/output/README.md).

```bash
just harvest mem0
just harvest-all
just harvest-eval locomo
just audit mem0
just audit-write mem0
just audit-write-eval locomo
just audit-write-all
just lint-audits
just lint-eval-audits
just lint-seed
just synthesize-dry-run
just synthesize
just matrix-dry-run
just matrix
just test-pipeline
```

`just synthesize` writes `synthesis.json` only after a dry-run is accepted. Harvest clones stay in `.cache/` and out of git.

Paper prose is [`INSIGHTS.md`](INSIGHTS.md). `research/output/by-paper/` is reserved.
