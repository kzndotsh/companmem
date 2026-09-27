# Requirements: Harness Eval Rigor — Per-Behavior Scores and pass^k

## Problem

The harness gates on a single composite score: `resolved_count / runnable_count`
across all 9 fixtures for a baseline. This has two concrete failure modes:

1. **Behavior masking.** A hallucination regression in B0 can be hidden by
   improvement in B5. The gate passes while a whole behavior axis breaks.
2. **Single-run overconfidence.** A companion that resolves a fixture 70% of the
   time will "pass" on every run where the lucky draw goes right, but fails
   roughly one in three real sessions (pass^3 ≈ 0.34). Neither the report nor
   `report.json` makes this visible.

Both gaps are confirmed in the current codebase:
- `BaselineResult` has one `resolved_count` integer; no per-behavior breakdown
  exists in `from_trials()`, `to_dict()`, or `print_summary()`.
- `_run_trial` is called exactly once per (baseline, fixture); no multi-run
  orchestration exists in `runner.py`.

## Scope

Files in scope: `harness/trial.py`, `harness/runner.py`,
`tests/test_trial.py`, `tests/test_runner.py`.

Out of scope: extraction-level predicates (`must_write_op`), corrective RAG
routing, memory metadata, temporal decay. Gap 3 (ingestion-time write
predicates) requires adapter write-log support and belongs in a separate spec.

## User-Visible Behaviour

### 1. Per-behavior pass rate in the summary and report

**What changes:** `BaselineResult` gains a `resolved_by_behavior` field:
a mapping from behavior code (`"b0"`, `"b1"`, `"b3"`, `"b5"`) to
`[resolved, runnable]` for that axis. Always counts at the **fixture level**
(not trial level): a fixture is counted as resolved only if all N runs for
that fixture resolved. With N == 1 this is identical to the current
per-fixture resolved count.

Example: 4 B0 fixtures, N == 3 → `b0: [4, 4]` means all 4 B0 fixtures had
all 3 runs resolve. With N == 1 the same 4 fixtures passing gives `b0: [4, 4]`.

Trials with `behavior=None` contribute to the `total` count only and are
excluded from the `resolved_by_behavior` dict.

**`report.json`** — `BaselineResult.to_dict()` explicitly emits three new
fields on every baseline object:

- `resolved_by_behavior`: the behavior dict as `{code: [resolved, runnable]}`,
  fixture-level counts as defined above.
- `pass_at_k`: `float` or `null` (null when N == 1).
- `pass_k`: `float` or `null` (null when N == 1).

`BaselineResult` has no `from_dict()` — these fields are always recomputed
from trials via `from_trials()`, never loaded from JSON.

Example (N == 1):

```json
"resolved_by_behavior": {
  "b0": [4, 4],
  "b1": [1, 1],
  "b3": [2, 2],
  "b5": [2, 2]
},
"pass_at_k": null,
"pass_k": null
```

### 2. `--runs N` flag for multi-run pass@k / pass^k

**What changes:** the `run` subcommand gains `--runs N` (default `1`,
backward compatible). `--runs N` requires N ≥ 1; `--runs 0` exits with
return code 1 and the message `"error: --runs must be ≥ 1"`. When N > 1,
each fixture is run N times per baseline, producing N `TrialResult` rows per
fixture tagged with `run_index: int` (0-based, default `0`). With `--runs 1`
behavior is identical to today.

`--runs` may be combined with `--behavior` or `--fixture`; pass@k / pass^k
compute over the filtered fixture set.

#### Artifact directory path

For N == 1 (or `--runs` absent), the artifact path is unchanged:

```
results_root / run_id / baseline_id / fixture_id
```

For N > 1, `run_index` is appended so each run has its own directory and no
run overwrites another's artifacts:

```
results_root / run_id / baseline_id / fixture_id / f"run_{run_index}"
```

`rescore()` reconstructs the artifact directory from `orig_trial.artifacts_path`
(already stored on `TrialResult`) rather than rebuilding the path from parts,
so it handles both conventions without special-casing.

#### `run_index` serialization

`TrialResult.to_dict()` always emits `"run_index"`. `TrialResult.from_dict()`
loads it with `d.get("run_index", 0)` so existing single-run reports
round-trip without modification.

#### `BaselineResult` new fields

Two new fields on `BaselineResult`, both `None` when N == 1:

- `pass_at_k: float | None` — fraction of eligible fixtures where ≥1 of the
  N runs resolved (pass@k).
- `pass_k: float | None` — fraction of eligible fixtures where all N runs
  resolved (pass^k; measures reliability).

**Denominator and error handling:** the denominator for both metrics is the
count of distinct `fixture_id` values that have at least one
`TrialStatus.OK` trial across all N runs. An INFRA_ERROR or SKIPPED run
within a multi-run fixture counts as `resolved=False` for that slot; it does
not remove the fixture from the denominator as long as at least one run for
that fixture was `TrialStatus.OK`.

#### How N is determined in `from_trials()`

`from_trials()` signature is unchanged: `(baseline_id, title, trials)`.
N is inferred from the trial data:

```python
n = max((t.run_index for t in trials), default=0) + 1
```

This is correct for both the live run path and `RunReport.rescore()`.
`from_trials()` sets `pass_at_k = pass_k = None` when `n == 1`.

`run_manifest.json` gains `"runs": N` for human readability; it is not the
source of truth for computation.

#### `rescore()` multi-run keying

`RunReport.rescore()` currently keys `original_trials` by
`(baseline_id, fixture_id)`. With N > 1, that dict is overwritten N times
per fixture and only the last run survives, silently producing 9 trials
instead of 27 and making `from_trials()` infer `n == 1`.

`rescore()` must key `original_trials` by `(baseline_id, fixture_id, run_index)`
and iterate over all `(bid, fid, run_index)` triples from `old_report`,
preserving every row. It reconstructs the artifact directory from
`orig_trial.artifacts_path` directly (not from parts), so both the flat
single-run and the `run_{run_index}` multi-run layouts are handled correctly.

### 3. Summary print order

For each baseline, output is in this order:

1. Per-fixture row groups (existing behavior-grouped output, unchanged).
2. **When N == 1:** a per-behavior summary line:
   ```
   b0: 4/4  b1: 1/1  b3: 2/2  b5: 2/2  total: 9/9
   ```
3. **When N > 1:** a single combined pass^k line that replaces the
   per-behavior summary line (no separate per-behavior line in this case):
   ```
   oracle   pass@3=1.00  pass^3=0.89  b0: 4/4  b1: 1/1  b3: 2/2  b5: 2/2
   ```

Format for both: `<code>: <resolved>/<runnable>` with two spaces between
entries. Only behavior codes that actually appear in the trial set are
printed.

When `--baseline all` runs multiple baselines, each baseline emits its own
block in this order sequentially. There is no combined cross-baseline table.

## Acceptance Criteria

1. `python -m harness run --baseline oracle` prints a per-behavior summary
   line showing `b0: 4/4  b1: 1/1  b3: 2/2  b5: 2/2  total: 9/9`.

2. `python -m harness run --baseline oracle --runs 3` produces exactly 27
   trials (9 fixtures × 3 runs), each run's artifacts in
   `run_{run_index}/` subdirectories, prints a combined pass^k line (no
   separate per-behavior line), and serializes `pass_at_k` and `pass_k` in
   `report.json`.

3. `report.json` contains `resolved_by_behavior`, `pass_at_k`, and `pass_k`
   in every baseline object.

4. `python -m harness run --baseline oracle --runs 1` is identical in
   behavior to today's `--runs`-less invocation: same trial count, same
   artifact paths, same report shape, per-behavior summary line present,
   no pass^k line.

5. `python -m harness run --baseline oracle --runs 0` exits with return
   code 1 and prints `"error: --runs must be ≥ 1"`.

6. `python -m pytest tests/ -q` passes with ≥ 75 tests and zero failures.
   `ruff check harness/ tests/` reports zero errors.

## Non-Goals

- Changing the predicate DSL or the scorer.
- Adding ingestion-time write predicates (`must_write_op`).
- Changing the fixture format or adding new fixtures.
- Changing how `--behavior` filtering works.
- Producing per-behavior pass@k / pass^k breakdowns (per-behavior multi-run
  is a follow-on, not part of this spec).
