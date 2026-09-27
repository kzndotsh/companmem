# Legacy Stressor Variants

Retired variants, kept for version history and construct auditing.
**They are not part of the leaderboard and are never loaded by default.**

The authoritative status registry is [`../manifest.json`](../manifest.json).
Status cannot be inferred from an ID or a filename — `adf_001`, `bsm_001`,
`lc_001` and `se_001` use v1-style names and *are* official leaderboard items.
Read the manifest, not the naming.

## Contents

| File | Variants | Type's official set |
|---|---|---|
| `abstraction_hop_v1.jsonl` | `ah_001`–`ah_005` | `ah_v2_001`–`ah_v2_003` |
| `domain_switch_v1.jsonl` | `ds_002`–`ds_005` | `ds_v2_001`–`ds_v2_003` |
| `goal_interrupt_v1.jsonl` | `gi_001`–`gi_005` | `gi_v2_001`–`gi_v2_003` |
| `style_pull_v1.jsonl` | `sp_001`–`sp_005` | `sp_v2_001`–`sp_v2_003` |

19 variants in total.

## Version identity

Each of these is a **v1-era item** of a type whose official set is now the v2
variants listed above. That relationship is **set-level**: the type's official
representation changed from the v1 items to the v2 items. There is **no
documented item-level 1:1 successor mapping**, and none is asserted here —
`ds_002` was not specifically replaced by `ds_v2_002`.

`ds_001` is absent from the repository; no record explains its removal.

## Why they are quarantined rather than deleted

They sat in the same files as the v2 items with nothing marking them retired, so
`--stressors all` mixed them into result sets and directory listings implied all
variants of a type were interchangeable. Moving them makes the boundary explicit
without discarding version history — no item was deleted and no published result
was changed.

## What is known about `ah_001`–`ah_005` specifically

A diagnostic pilot (n=5 models, `docs/construct_validity_audit.md`) found severe
ceiling compression on these five items: every score at or above 0.95, and
cross-model spread roughly a tenth of the official `abstraction_hop` slice's on
the same models. Reading the item text, each abstraction change and the return
are explicitly cued in the user turns, so the items score compliance with an
instruction rather than unprompted return to an established frame.

**This finding applies to `ah_001`–`ah_005` only.** The other 14 legacy variants
here have **not** been evaluated for discriminability, and nothing about their
behaviour should be inferred from the abstraction-hop result. They are filed as
legacy on the basis of version identity, not measured performance.

## How not to use any of these

- Do not report scores from them as leaderboard results.
- Do not pool them with the v2 items of the same type. The sets are not matched
  on length, topic, authoring round or rubric metadata.
- For `ah_001`–`ah_005` specifically, do not use them to reproduce or corroborate
  v2 findings: under the measured ceiling compression, a rank correlation
  computed on them cannot support an interpretable estimate of ranking
  stability.

## Loading them

```bash
python run_eval.py --model <provider>/<model> \
  --stressors domain_switch --include-legacy --dry-run
```

`--include-legacy` is required, prints a warning, and is rejected together with
`--leaderboard`. Results carry no leaderboard comparability.
