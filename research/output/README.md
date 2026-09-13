# research/output

Published audit records. Pipeline code is [`../pipeline/`](../pipeline/). Scratch harvest lives in gitignored `.cache/`.

```
output/
  README.md              # this file
  by-product/            # this program
    PROTOCOL.md
    excluded.json
    _synthesis.json      # after audit.json files exist
    <slug>/audit.json
  by-paper/              # reserved
  by-eval/               # reserved
```

## Query

```bash
jq '.ledger[] | select(.confidence=="high")' research/output/by-product/mem0/audit.json
jq '{id: .identity.id, refuse: .refuse}' research/output/by-product/mem0/audit.json
jq -s 'map({id: .identity.id, mechanisms: .mechanisms})' research/output/by-product/*/audit.json
```

`sources` is what we opened. `ledger` is what we claim (quote + locator). `copy` / `refuse` are interpretation (what we would steal or reject for companion continuity). Extract and fold leave them empty. There is no `just grill` yet.

## Run

```bash
just harvest mem0
just harvest-inventory mem0  # print source paths, no ranker
just harvest-all         # every product in seed.json
just audit mem0          # extract → fold → apply dry-run
just audit-write mem0    # lint temp, then write audit.json
just audit-write-all
just lint-audits
just synthesize
just test-pipeline
```

See [`by-product/PROTOCOL.md`](by-product/PROTOCOL.md).
