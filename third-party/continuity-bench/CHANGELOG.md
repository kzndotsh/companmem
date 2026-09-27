# Changelog

## Unreleased

### Interactive Explorer

`docs/index.html` is a self-contained explorer for the published results,
deployable as a static GitHub Pages site from the `docs/` directory. It lets a
reader vary the continuity dimensions, stressor-family selection and aggregation
weights, and see how the ranking moves — with per-item scores and the retained
judge evidence behind them.

It runs wholly in the browser: no external scripts or stylesheets, no `fetch`,
`XMLHttpRequest` or `WebSocket`, no network access of any kind. Its embedded data
covers the 19 leaderboard models on the 26 official variants; no legacy or
experimental item appears in it.

`docs/.nojekyll` disables Jekyll processing so the page is served verbatim.

### The official leaderboard set

The leaderboard set is the **26 variant IDs listed in `configs/default`**, and
nothing else. `--leaderboard` selects exactly those IDs. Every other selection,
including `--stressors all`, is not leaderboard-comparable.

### Legacy variant quarantine

19 v1-era variants moved out of the official stressor files into
`stressors/legacy/`. No item was deleted and no existing result was changed.

| moved | from | to |
|---|---|---|
| `ah_001`–`ah_005` | `abstraction_hop.jsonl` | `legacy/abstraction_hop_v1.jsonl` |
| `ds_002`–`ds_005` | `domain_switch.jsonl` | `legacy/domain_switch_v1.jsonl` |
| `gi_001`–`gi_005` | `goal_interrupt.jsonl` | `legacy/goal_interrupt_v1.jsonl` |
| `sp_001`–`sp_005` | `style_pull.jsonl` | `legacy/style_pull_v1.jsonl` |

Filed as legacy on **version identity**, not measured performance. The ceiling
compression measured on `ah_001`–`ah_005` is not extrapolated to the other 14,
which have not been evaluated for discriminability.

Successor relationships are recorded as **set-level**: each type's official
representation is now its v2 variants. No item-level 1:1 mapping is documented
or asserted.

All 19 had been sitting in the same files as the v2 leaderboard items with
nothing marking them retired, so `--stressors all` mixed them in silently and a
directory listing implied every variant of a type was interchangeable.

Separately, and for `ah_001`–`ah_005` **only**: a diagnostic pilot (n=5 models,
`docs/construct_validity_audit.md`) measured severe ceiling compression on those
five — every score at or above 0.95, cross-model spread roughly a tenth of the
official `abstraction_hop` slice's on the same models. Reading the item text,
each abstraction change and the return are explicitly cued, so the items score
compliance with an instruction rather than unprompted return. That is a finding
about those five items on those five models; it says nothing about the other 14.
See `stressors/legacy/README.md`.

- legacy variants are never loaded by default, including under `--stressors all`
- `--include-legacy` is required to load them, prints a warning, and is rejected
  together with `--leaderboard`
- loaded items carry a `_legacy` flag; unmatched `--stressor-ids` now report
  when the missing ID is a legacy variant
- the four affected files now hold only their official variants;
  `--stressors all` covers 32 variants, down from 51

### Stressor manifest

New `stressors/manifest.json` records `status`, `leaderboard_eligible`,
`superseded_by` and `supersede_scope` for all 51 variants — 26 official,
6 experimental, 19 legacy.

Status is not inferable from an ID or a filename: `adf_001`, `bsm_001`,
`lc_001` and `se_001` use v1-style names and are official, while `ds_002` and
`gi_001` use the same style and are retired. The manifest exists so identity is
never guessed from naming or file location again.

### Cost controls

**Judge call accounting corrected.** `JudgeSystem.evaluate()` issues one call per
(dimension, pass), so a 26-variant set at 3 passes makes **312** judge calls. The
first version of the estimator counted passes only and reported 78 — a 4x
underestimate of the judge bill.

Estimates are now mode-aware, per item:

| mode | judge calls |
|---|---|
| `traditional` / `vanilla` | dims x passes |
| `sef` | 1 anchor + dims x passes |
| `sef_energy` | 1 anchor + 1 energy probe + dims x passes |

Deliberation is variable, so it is priced as a **separate conservative ceiling**
rather than folded into the expected figure; modes carrying it report both an
expected total and a ceiling. `sef` and `sef_energy` are selectable for pricing
only — the SEF judge was removed in e22fa20, and attempting to run those modes
exits with an error.

- `--dry-run` reports **target-model generation** and **judge** separately —
  calls, tokens and cost for each — then the total, and makes no API calls
- `--max-cost-usd` renamed **`--max-estimated-usd`** (old flag still accepted,
  prints a deprecation notice). It is an **estimated-cost gate**, not a spend
  cap: it refuses to *start* a run whose pre-flight estimate exceeds the
  threshold (exit code 2), and cannot bound or halt a run in progress. Provider-
  side spend limits are the only real ceiling. Gating uses the conservative
  figure when a mode has deliberation.
- `scripts/sweep.py` runs a stressor selection across several models and
  **stops at a checkpoint before any model flagged expensive**; continuing
  requires `--confirm-expensive`, so a sweep cannot walk from cheap models into
  Opus / GPT-5.4 / Gemini Pro on its own
- cost figures come from a rate table in `run_eval.py` and are planning
  estimates, not quotes

### Statistics

- `scripts/significance.py` reproduces the leaderboard significance analysis
- README states the resolution limit (~0.036 BC-Score at n=26) and which models
  are actually separable from the top after Holm correction
- two Key Findings that asserted differences below the resolution limit were
  restated at the strength the data supports
- `scipy` added to `requirements.txt`

### Reports

- all 19 v3 reports share one schema; `glm5`, `ernie5`, `kimi_k2.5` and
  `gemini_3.1_pro` were rebuilt from raw runs with no new API calls
- `kimi_k2.5` re-aggregated over individual runs rather than per-stressor means,
  matching every other multi-run row
- reports whose per-run judge records were not retained now say so via
  `meta.individual_records`
