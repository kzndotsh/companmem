# Tasks: Harness Eval Rigor — Per-Behavior Scores and pass^k

## Task 1: Add `run_index` to `TrialResult`

**File:** `harness/trial.py`

- [x] Add `run_index: int = 0` as the last field on `TrialResult` (after `behavior`)
- [x] In `to_dict()`, add `"run_index": self.run_index` to the returned dict
- [x] In `from_dict()`, load as `run_index=int(d.get("run_index", 0))`

**Verify:** existing `_make_trial()` in `tests/test_trial.py` constructs without `run_index` and still works (default covers it).

---

## Task 2: Add `resolved_by_behavior`, `pass_at_k`, `pass_k` to `BaselineResult`

**File:** `harness/trial.py`

- [x] Add three fields after `tokens_per_resolved` on the `BaselineResult` dataclass:
  ```python
  resolved_by_behavior: dict[str, list[int]]
  pass_at_k: float | None
  pass_k: float | None
  ```
- [x] In `to_dict()`, emit all three after `tokens_per_resolved`:
  ```python
  "resolved_by_behavior": self.resolved_by_behavior,
  "pass_at_k": self.pass_at_k,
  "pass_k": self.pass_k,
  ```

---

## Task 3: Update `BaselineResult.from_trials()` to compute new fields

**File:** `harness/trial.py`

- [x] At the top of `from_trials()`, import `defaultdict` from `collections` (add to module-level imports if not present)
- [x] Build `fixture_runs: dict[str, list[TrialResult]]` and `fixture_behavior: dict[str, str | None]` by iterating `trials`:
  - Use unconditional overwrite for non-None behavior: `fixture_behavior[t.fixture_id] = t.behavior`
  - Use `setdefault` only for None: `fixture_behavior.setdefault(t.fixture_id, None)`
- [x] Compute `resolved_by_behavior` using fixture-level resolution (a fixture counts as resolved only if all its `TrialStatus.OK` runs have `resolved=True`); exclude fixtures where `fixture_behavior[fid]` is `None`
- [x] Determine `n = max((t.run_index for t in trials), default=0) + 1`
- [x] Compute `pass_at_k` and `pass_k` as `None` when `n == 1`; otherwise use the eligible-fixture denominator defined in the design (fixtures with ≥1 OK trial)
- [x] Pass all three new fields to the `cls(...)` constructor call

---

## Task 4: Update `RunReport.rescore()` for multi-run keying

**File:** `harness/trial.py`

- [x] Change `original_trials` key type from `tuple[str, str]` to `tuple[str, str, int]`
- [x] In the population loop, add `run_idx = int(t_dict.get("run_index", 0))` and key as `(bid, fid, run_idx)`
- [x] Replace the inner fixture iteration (currently `for fid in old_report.get("fixture_ids", [])`) with iteration over all `(bid, fid, run_idx)` keys matching the current baseline, sorted for determinism
- [x] Reconstruct artifact directory as `art_dir = artifacts_root.parent.parent / orig_trial.artifacts_path`
  - `artifacts_root` = `results_root / run_id`, so `.parent.parent` = `results_root.parent` — the base used when the path was originally stored

---

## Task 5: Restructure `RunReport.print_summary()` and add summary lines

**File:** `harness/trial.py`

- [x] Restructure `print_summary()` to iterate `self.baselines` explicitly (one block per baseline) instead of the current flat `all_pairs` approach
- [x] Per-baseline: scope behavior grouping and row printing to that baseline's trials only (existing `_row` helper and `_behavior_header` unchanged)
- [x] After per-fixture rows, emit a summary line:
  - If `bl.pass_at_k is None` (N == 1): `"b0: 4/4  b1: 1/1  b3: 2/2  b5: 2/2  total: 9/9"` — only behavior codes present in `resolved_by_behavior`, two spaces between entries
  - If `bl.pass_at_k is not None` (N > 1): `"oracle   pass@3=1.00  pass^3=0.89  b0: 4/4 ..."` — N inferred from `max(t.run_index)+1` only for label formatting, not for branching

---

## Task 6: Add `--runs N` flag to `_cmd_run`

**File:** `harness/runner.py`

- [x] Add `--runs` argument to the `run` subparser: `type=int`, `default=1`, `metavar="N"`
- [x] At the top of `_cmd_run` (after the `--fixture`/`--behavior` mutual-exclusion guard), add:
  ```python
  if args.runs < 1:
      print("error: --runs must be ≥ 1")
      return 1
  ```
- [x] Replace the existing `for idx, fid in enumerate(fixture_ids, 1)` loop with a two-level loop using global progress counters. Both `total_trials` and `global_idx` are **initialized inside the `for adapter_entry in selected:` loop** (not outside it) so they reset per adapter and `--baseline all` with two adapters prints `(1/9)…(9/9)` twice, not `(1/18)…(18/18)`:
  ```python
  for adapter_entry in selected:
      ...
      total_trials = args.runs * len(fixture_ids)
      global_idx = 0
      for run_index in range(args.runs):
          for fid in fixture_ids:
              global_idx += 1
              print(f"{bid:24} {fid:28} running ({global_idx}/{total_trials}) ...")
              trial = _run_trial(..., run_index=run_index, runs=args.runs)
              trials.append(trial)
  ```
- [x] Add `"runs": args.runs` to `run_manifest.json`

---

## Task 7: Update `_run_trial` for multi-run artifact paths

**File:** `harness/runner.py`

- [x] Add `run_index: int = 0` and `runs: int = 1` parameters to `_run_trial`
- [x] Replace the single `art_dir = results_root / run_id / baseline_id / fixture_id` line with:
  ```python
  art_base = results_root / run_id / baseline_id / fixture_id
  art_dir = art_base / f"run_{run_index}" if runs > 1 else art_base
  ```
- [x] Pass `run_index=run_index` to all three `TrialResult` constructors in `_run_trial`: the docker-skip return (~line 140), the import-error return (~line 170), and the normal return after scoring (~line 251)

---

## Task 8: New tests for `TrialResult` and `BaselineResult`

**File:** `tests/test_trial.py`

Extend `_make_trial()` to accept `run_index: int = 0` and `behavior: str | None = None` kwargs.

Add these tests:

- [x] `test_run_index_default_zero` — `_make_trial()` with no `run_index` kwarg; `to_dict()["run_index"] == 0`
- [x] `test_run_index_serializes` — `run_index=2` survives `to_dict()` → `from_dict()` round-trip
- [x] `test_from_dict_missing_run_index_defaults_zero` — `from_dict` on a dict without `"run_index"` key returns `run_index == 0`
- [x] `test_resolved_by_behavior_all_pass` — four b0 trials, N=1, all resolved → `b0: [4, 4]`
- [x] `test_resolved_by_behavior_partial` — three b0 trials, one fails → `b0: [2, 3]`
- [x] `test_resolved_by_behavior_excludes_none_behavior` — trials with `behavior=None` do not appear in `resolved_by_behavior`
- [x] `test_resolved_by_behavior_none_trial_before_behavior_trial` — for the same fixture_id, a `behavior=None` trial at index 0 followed by a `behavior="b0"` trial at index 1 → fixture correctly maps to `"b0"` (guards the overwrite fix)
- [x] `test_pass_at_k_none_when_n1` — N=1 → `pass_at_k is None` and `pass_k is None`
- [x] `test_pass_at_k_computed_n3` — 3 fixtures × 3 runs (run_index 0/1/2 per fixture), 2 fixtures fully resolve across all 3 runs → `pass_k == 2/3`
- [x] `test_pass_at_k_partial_resolve` — 1 fixture × 2 runs, run_index=0 resolves, run_index=1 does not → `pass_at_k == 1.0`, `pass_k == 0.0`
- [x] `test_infra_error_within_multirun_excluded_from_denominator_when_all_error` — 1 fixture × 2 runs, both INFRA_ERROR → `pass_at_k` and `pass_k` are `None` (denom == 0)
- [x] `test_to_dict_emits_three_new_fields` — `to_dict()` output always contains `"resolved_by_behavior"`, `"pass_at_k"`, `"pass_k"` keys

---

## Task 9: New test for `rescore()` multi-run keying

**File:** `tests/test_trial.py`

- [x] `test_rescore_multirun_keying` — construct a `RunReport` with 1 baseline, 9 fixtures, 3 runs each (27 `TrialResult` rows with `run_index` 0/1/2, all `TrialStatus.OK`); write `run_manifest.json` and `report.json` to `tmp_path`; patch `harness.trial.Scorer` with `unittest.mock.patch` so `Scorer(pred_path).score(artifacts)` returns a fixed `ScorerResult`; call `RunReport.rescore(artifacts_root, fixtures_root)`; assert the result has exactly 27 trials for the baseline

---

## Task 10: New tests for runner flags and artifact paths

**File:** `tests/test_runner.py`

- [x] `test_runs_flag_zero_exits_1` — construct a complete `argparse.Namespace` (matching the shape `_cmd_run` expects before hitting any guard) and call `_cmd_run`; assert return code 1 and `"error: --runs must be ≥ 1"` in captured stdout:
  ```python
  ns = argparse.Namespace(
      baseline="oracle",
      fixture=None,
      behavior=None,
      fixtures_root=None,
      results_root=None,
      include_docker=False,
      runs=0,
  )
  rc = _cmd_run(ns)
  assert rc == 1
  assert "error: --runs must be ≥ 1" in capsys.readouterr().out
  ```
- [x] `test_runs_flag_default_1` — directly instantiate `argparse.Namespace(runs=1)` and assert `args.runs == 1`; this confirms the default value without requiring access to the unexported subparser
- [x] `test_multirun_artifact_paths_use_run_subdirs` — patch `harness.runner.World`, `harness.runner.Artifacts`, and `importlib.import_module`; call `_run_trial` with `runs=3, run_index=0`; assert `result.artifacts_path` ends with `"run_0"`; repeat for `run_index=2` → ends with `"run_2"`
- [x] `test_singlerun_artifact_paths_unchanged` — same three patches; call `_run_trial` with `runs=1, run_index=0`; assert `"run_"` does not appear in `result.artifacts_path`

---

## Task 11: Verify acceptance criteria

Run these commands from the repo root and confirm each passes:

- [x] `AC1` — `.venv/bin/python -m harness run --baseline oracle` prints a line matching `b0: 4/4  b1: 1/1  b3: 2/2  b5: 2/2  total: 9/9`
- [x] `AC2` — `.venv/bin/python -m harness run --baseline oracle --runs 3` produces 27 trials in `report.json`, artifact dirs contain `run_0/`…`run_2/` subdirs, and the summary line contains `pass@3=` and `pass^3=`
- [x] `AC3` — `report.json` from AC2 contains `"resolved_by_behavior"`, `"pass_at_k"`, and `"pass_k"` in the baseline object
- [x] `AC4` — `.venv/bin/python -m harness run --baseline oracle --runs 1` behaves identically to the `--runs`-less invocation: 9 trials, flat artifact paths, per-behavior summary line, no pass^k line
- [x] `AC5` — `.venv/bin/python -m harness run --baseline oracle --runs 0` exits with code 1 and prints `"error: --runs must be ≥ 1"`
- [x] `AC6` — `.venv/bin/python -m pytest tests/ -q` passes with ≥ 75 tests and zero failures; `.venv/bin/ruff check harness/ tests/` reports zero errors
