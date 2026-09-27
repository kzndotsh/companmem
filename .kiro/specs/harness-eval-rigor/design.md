# Design: Harness Eval Rigor — Per-Behavior Scores and pass^k

## Overview

Two changes to two files (`harness/trial.py`, `harness/runner.py`), covered by
new tests in `tests/test_trial.py` and `tests/test_runner.py`.

1. `BaselineResult` gains per-behavior counts and pass@k / pass^k fields,
   computed in `from_trials()` and serialized in `to_dict()`.
2. `_cmd_run` gains `--runs N`, which runs each fixture N times and appends a
   `run_index` to each `TrialResult`. Artifact paths grow a `run_{run_index}/`
   suffix when N > 1.
3. `rescore()` re-keys its trial index by `(baseline_id, fixture_id, run_index)`
   so multi-run reports rescore correctly.
4. `print_summary()` emits a per-behavior line (N == 1) or a combined pass^k
   line (N > 1) after the fixture rows for each baseline.

No changes to `harness/artifacts.py`, `harness/scorer.py`, `harness/adapter.py`,
`harness/world.py`, fixture format, or the predicate DSL.

---

## 1. `TrialResult` — add `run_index`

**File:** `harness/trial.py`

Add one field after `behavior`:

```python
run_index: int = 0  # 0-based; default keeps existing single-run reports valid
```

`to_dict()` always emits `"run_index": self.run_index`.

`from_dict()` loads it as `int(d.get("run_index", 0))`.

No other changes to `TrialResult`.

---

## 2. `BaselineResult` — new fields and updated `from_trials()`

**File:** `harness/trial.py`

### 2a. New dataclass fields

Add three fields after `tokens_per_resolved`:

```python
resolved_by_behavior: dict[str, list[int]]
# e.g. {"b0": [4, 4], "b1": [1, 1]}
# always present; empty dict when all trials have behavior=None

pass_at_k: float | None  # None when n == 1
pass_k: float | None     # None when n == 1
```

### 2b. `from_trials()` — compute new fields

The signature is **unchanged**: `(baseline_id, title, trials)`.

#### Determine N

```python
n = max((t.run_index for t in trials), default=0) + 1
```

#### Per-behavior fixture-level counts

A fixture is "resolved at fixture level" only when **all N runs** for that
`fixture_id` resolved. Algorithm:

```python
# Group trials by (fixture_id, behavior).
# For each (fixture_id, behavior) group:
#   - runnable: at least one TrialStatus.OK in the group
#   - resolved: all N run_index slots that are TrialStatus.OK are resolved=True
#     AND there is at least one TrialStatus.OK trial
#
# Accumulate into resolved_by_behavior[code] = [resolved_count, runnable_count]
```

Trials with `behavior=None` are excluded from `resolved_by_behavior` (they
still count toward `resolved_count` and `runnable_count` as before).

Implementation sketch (stays in `from_trials`, no helper needed):

```python
from collections import defaultdict

# fixture_id → behavior (take from first trial with non-None behavior)
fixture_behavior: dict[str, str | None] = {}
# fixture_id → list[TrialResult] across all run_index values
fixture_runs: dict[str, list[TrialResult]] = defaultdict(list)

for t in trials:
    fixture_runs[t.fixture_id].append(t)
    if t.behavior is not None:
        fixture_behavior[t.fixture_id] = t.behavior  # always overwrite; prefer non-None
    else:
        fixture_behavior.setdefault(t.fixture_id, None)  # only if not yet set

beh_resolved: dict[str, int] = defaultdict(int)
beh_runnable: dict[str, int] = defaultdict(int)

for fid, runs in fixture_runs.items():
    beh = fixture_behavior.get(fid)
    if beh is None:
        continue
    ok_runs = [r for r in runs if r.status == TrialStatus.OK]
    if not ok_runs:
        continue  # no OK trial → not runnable; skip denominator
    beh_runnable[beh] += 1
    if all(r.resolved for r in ok_runs):
        beh_resolved[beh] += 1

resolved_by_behavior: dict[str, list[int]] = {
    beh: [beh_resolved[beh], beh_runnable[beh]]
    for beh in beh_runnable  # only codes that appeared
}
```

#### pass@k / pass^k

Denominator: count of distinct `fixture_id` values that have at least one
`TrialStatus.OK` trial across all runs.

```python
if n == 1:
    pass_at_k = None
    pass_k = None
else:
    eligible = {
        fid for fid, runs in fixture_runs.items()
        if any(r.status == TrialStatus.OK for r in runs)
    }
    denom = len(eligible)
    if denom == 0:
        pass_at_k = None
        pass_k = None
    else:
        at_k_count = sum(
            1 for fid in eligible
            if any(
                r.resolved for r in fixture_runs[fid]
                if r.status == TrialStatus.OK
            )
        )
        k_count = sum(
            1 for fid in eligible
            if all(
                r.resolved for r in fixture_runs[fid]
                if r.status == TrialStatus.OK
            )
        )
        pass_at_k = at_k_count / denom
        pass_k = k_count / denom
```

### 2c. `to_dict()` — emit new fields

Add after `tokens_per_resolved`:

```python
"resolved_by_behavior": self.resolved_by_behavior,
"pass_at_k": self.pass_at_k,
"pass_k": self.pass_k,
```

No `from_dict()` on `BaselineResult`; these are always recomputed.

---

## 3. `runner.py` — `--runs N` flag and artifact paths

**File:** `harness/runner.py`

### 3a. Argument parser

Add to the `run` subparser:

```python
run_p.add_argument(
    "--runs",
    type=int,
    default=1,
    metavar="N",
    help="Number of times to run each fixture (default 1)",
)
```

### 3b. `_cmd_run` — validate and loop

At the top of `_cmd_run`, after the `--fixture`/`--behavior` guard:

```python
if args.runs < 1:
    print("error: --runs must be ≥ 1")
    return 1
```

Replace the per-fixture loop body with an outer `run_index` loop:

```python
for run_index in range(args.runs):
    for idx, fid in enumerate(fixture_ids, 1):
        ...
        trial = _run_trial(
            ...
            run_index=run_index,
            runs=args.runs,
        )
        trials.append(trial)
```

The existing `for idx, fid` loop body is otherwise unchanged. The `run_index`
loop is the outer loop so that all fixtures complete at `run_index=0` before
moving to `run_index=1` — this keeps the progress output coherent.

**Progress output:** use global counters so `(1/27)` through `(27/27)` print
once each, not `(1/9)` through `(9/9)` repeated three times:

```python
total_trials = args.runs * len(fixture_ids)
global_idx = 0
for run_index in range(args.runs):
    for fid in fixture_ids:
        global_idx += 1
        print(f"{bid:24} {fid:28} running ({global_idx}/{total_trials}) ...")
        trial = _run_trial(...)
        trials.append(trial)
```

This replaces the existing `for idx, fid in enumerate(fixture_ids, 1)` and
its `running ({idx}/{total})` print.

### 3c. `_run_trial` — accept `run_index` and `runs`, adjust artifact path

Add parameters:

```python
def _run_trial(
    ...
    run_index: int = 0,
    runs: int = 1,
) -> TrialResult:
```

Artifact path logic (replaces current single line):

```python
art_base = results_root / run_id / baseline_id / fixture_id
art_dir = art_base / f"run_{run_index}" if runs > 1 else art_base
artifacts = Artifacts(art_dir)
artifacts_path = art_dir.relative_to(results_root.parent).as_posix()
```

Pass `run_index=run_index` when constructing the returned `TrialResult`.

### 3d. `run_manifest.json` — add `"runs"` field

```python
manifest: dict[str, Any] = {
    "run_id": run_id,
    "runs": args.runs,      # ← new; human-readable, not the computation source
    ...
}
```

---

## 4. `rescore()` — multi-run keying

**File:** `harness/trial.py`

### 4a. Re-key `original_trials`

Change the type and the population loop:

```python
# Before:
original_trials: dict[tuple[str, str], dict[str, Any]] = {}
for bl_dict in old_report.get("baselines", []):
    bid = str(bl_dict["baseline_id"])
    for t_dict in bl_dict.get("trials", []):
        fid = str(t_dict["fixture_id"])
        original_trials[(bid, fid)] = t_dict

# After:
original_trials: dict[tuple[str, str, int], dict[str, Any]] = {}
for bl_dict in old_report.get("baselines", []):
    bid = str(bl_dict["baseline_id"])
    for t_dict in bl_dict.get("trials", []):
        fid = str(t_dict["fixture_id"])
        run_idx = int(t_dict.get("run_index", 0))
        original_trials[(bid, fid, run_idx)] = t_dict
```

### 4b. Iterate over all `(bid, fid, run_index)` triples

Replace the inner loop that iterates over `fixture_ids`:

```python
# Collect all (bid, fid, run_index) keys for this baseline
keys_for_baseline = [
    (bid2, fid2, ri)
    for (bid2, fid2, ri) in original_trials
    if bid2 == bid
]

for _, fid, run_idx in sorted(keys_for_baseline):
    key = (bid, fid, run_idx)
    orig = original_trials.get(key)
    if orig is None:
        continue
    orig_trial = TrialResult.from_dict(orig)

    if orig_trial.status != TrialStatus.OK:
        new_trials.append(orig_trial)
        continue

    # Reconstruct artifact directory from stored path (handles both layouts).
    # artifacts_path is relative to results_root.parent (i.e. the parent of
    # results_root). In rescore(), artifacts_root = results_root / run_id, so:
    #   artifacts_root.parent         = results_root
    #   artifacts_root.parent.parent  = results_root.parent  ← correct base
    art_dir = artifacts_root.parent.parent / orig_trial.artifacts_path
    ...
```

All other `rescore()` logic is unchanged.

---

## 5. `print_summary()` — per-behavior and pass^k lines

**File:** `harness/trial.py`

After the existing per-fixture row loop for each baseline, add a summary
block. `print_summary()` currently iterates `self.baselines` implicitly
through `all_pairs`; the summary lines are appended after all rows for the
full run are printed. To align with the requirement (each baseline emits its
own block), restructure `print_summary()` to iterate baselines explicitly:

### Restructured `print_summary()`

```python
def print_summary(self) -> None:
    for bl in self.baselines:
        pairs: list[tuple[str, TrialResult]] = [
            (bl.baseline_id, t) for t in bl.trials
        ]

        # Behavior grouping (existing logic, scoped to this baseline)
        if not any(t.behavior is not None for _, t in pairs):
            for bid, t in pairs:
                _row(bid, t)
        else:
            groups: dict[str | None, list[tuple[str, TrialResult]]] = {}
            for beh in _BEHAVIOR_ORDER:
                groups[beh] = []
            groups[None] = []
            for bid, t in pairs:
                key = t.behavior if t.behavior in groups else None
                groups[key].append((bid, t))
            for beh in [*_BEHAVIOR_ORDER, None]:
                rows = sorted(groups[beh], key=lambda p: (p[0], p[1].fixture_id))
                if not rows:
                    continue
                print(_behavior_header(beh))
                for bid, t in rows:
                    _row(bid, t)

        # Summary line(s).
        # Branch on pass_at_k is not None rather than recomputing N — BaselineResult
        # already encodes whether N > 1 via that field.
        beh_parts = "  ".join(
            f"{code}: {counts[0]}/{counts[1]}"
            for code in _BEHAVIOR_ORDER
            if code in bl.resolved_by_behavior
        )
        if bl.pass_at_k is None:
            # N == 1: per-behavior line + total
            total_part = f"total: {bl.resolved_count}/{bl.runnable_count}"
            parts = f"{beh_parts}  {total_part}" if beh_parts else total_part
            print(parts)
        else:
            # N > 1: combined pass^k line; N inferred here only for label formatting
            n = max((t.run_index for t in bl.trials), default=0) + 1
            pak = f"pass@{n}={bl.pass_at_k:.2f}"
            pk  = f"pass^{n}={bl.pass_k:.2f}" if bl.pass_k is not None else f"pass^{n}=n/a"
            parts = f"{bl.baseline_id}   {pak}  {pk}  {beh_parts}"
            print(parts.strip())
```

---

## 6. New tests

### `tests/test_trial.py` additions (~10 new tests)

All use the existing `_make_trial()` helper, extended to accept `run_index`
and `behavior` kwargs.

| Test | What it checks |
|---|---|
| `test_run_index_default_zero` | `_make_trial()` has `run_index=0`; `to_dict()["run_index"] == 0` |
| `test_run_index_serializes` | `run_index=2` round-trips through `to_dict()`/`from_dict()` |
| `test_from_dict_missing_run_index_defaults_zero` | `from_dict` on a dict without `run_index` returns 0 |
| `test_resolved_by_behavior_all_pass` | 4 b0 trials N=1 → `b0: [4, 4]` |
| `test_resolved_by_behavior_partial` | 3 b0 trials, 1 fails → `b0: [2, 3]` |
| `test_resolved_by_behavior_excludes_none_behavior` | behavior=None trials absent from dict |
| `test_pass_at_k_none_when_n1` | N=1 → `pass_at_k is None`, `pass_k is None` |
| `test_pass_at_k_computed_n3` | 3 fixtures × 3 runs, 2 fully resolve → `pass_k = 2/3` |
| `test_pass_at_k_partial_resolve` | fixture where run0 passes, run1 fails → counted in pass@k not pass^k |
| `test_infra_error_within_multirun_not_denominator_when_all_error` | fixture with only INFRA_ERROR runs excluded from denominator |
| `test_rescore_multirun_keying` | rescore on 9-fixture × 3-run report produces 27 new trials. **Approach:** patch `harness.trial.Scorer` with `unittest.mock.patch` so `score()` returns a fixed `ScorerResult`; write only `run_manifest.json` and `report.json` into `tmp_path` — no artifact tree required. The patch intercepts the `Scorer(pred_path)` constructor call, so the test is not coupled to `Artifacts` internals or disk layout. |
| `test_to_dict_emits_three_new_fields` | `resolved_by_behavior`, `pass_at_k`, `pass_k` always in `to_dict()` output |

### `tests/test_runner.py` additions (~5 new tests)

| Test | What it checks |
|---|---|
| `test_runs_flag_zero_exits_1` | `_cmd_run` with `--runs 0` returns 1 and prints the error message |
| `test_runs_flag_default_1` | parser default for `--runs` is 1 |
| `test_runs_manifest_gains_runs_field` | `run_manifest.json` written during a run contains `"runs": N` |
| `test_multirun_artifact_paths_use_run_subdirs` | N > 1 → artifact dirs end with `run_0/`, `run_1/`, etc. **Approach:** patch `importlib.import_module` and `harness.runner.Artifacts` so `_run_trial` returns without running real adapter code; assert that the `artifacts_path` field on each returned `TrialResult` ends with `run_0`, `run_1`, etc. |
| `test_singlerun_artifact_paths_unchanged` | N == 1 → artifact dir is `run_id/baseline_id/fixture_id` (no suffix). **Approach:** same patches as above; assert `artifacts_path` does not contain `run_` segments. |

---

## Change summary

| File | Change |
|---|---|
| `harness/trial.py` | `TrialResult`: add `run_index: int = 0` field |
| `harness/trial.py` | `BaselineResult`: add `resolved_by_behavior`, `pass_at_k`, `pass_k` fields |
| `harness/trial.py` | `BaselineResult.from_trials()`: compute all three new fields |
| `harness/trial.py` | `BaselineResult.to_dict()`: emit three new fields |
| `harness/trial.py` | `RunReport.print_summary()`: restructure to per-baseline; add summary line |
| `harness/trial.py` | `RunReport.rescore()`: re-key by `(bid, fid, run_index)`; iterate all triples |
| `harness/runner.py` | `_run_trial()`: accept `run_index`, `runs`; branch artifact path |
| `harness/runner.py` | `_cmd_run()`: add `--runs` arg, validate, outer run-index loop |
| `harness/runner.py` | `_cmd_run()`: write `"runs"` into `run_manifest.json` |
| `tests/test_trial.py` | ~12 new unit tests |
| `tests/test_runner.py` | ~5 new unit tests |
