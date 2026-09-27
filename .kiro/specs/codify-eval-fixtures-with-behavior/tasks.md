# Tasks: Codify Eval Fixtures with Behavior Metadata

Tasks follow the execution order from design §8. Each task is independently verifiable. Do not reorder steps — later tasks depend on earlier ones compiling cleanly.

## Task 1: Rename fixture directories

Rename all 9 fixture directories under `evals/fixtures/`. Each rename moves the entire directory tree; no sub-contents are touched.

- [x] 1.1 `mv evals/fixtures/social-silence       evals/fixtures/b5-silence-on-casual-invite`
- [x] 1.2 `mv evals/fixtures/forget-that           evals/fixtures/b3-retracted-allergy`
- [x] 1.3 `mv evals/fixtures/joke-as-fact          evals/fixtures/b0-joke-not-stored-as-fact`
- [x] 1.4 `mv evals/fixtures/lore-vs-lived         evals/fixtures/b0-lore-not-autobiography`
- [x] 1.5 `mv evals/fixtures/three-month-reunion   evals/fixtures/b1-three-month-gap`
- [x] 1.6 `mv evals/fixtures/identity-50           evals/fixtures/b0-stable-self-50-sessions`
- [x] 1.7 `mv evals/fixtures/typed-retcon         evals/fixtures/b3-stale-job-purged`
- [x] 1.8 `mv evals/fixtures/cross-character-leak  evals/fixtures/b5-firing-stays-isolated`
- [x] 1.9 `mv evals/fixtures/persona-poison        evals/fixtures/b0-injection-quarantined`
- [x] 1.10 Verify: `ls evals/fixtures/` shows exactly 9 directories all matching `b{0|1|3|5}-*`, none of the old names remain.

## Task 2: Overwrite fixture.json in all 9 directories

Replace the contents of each `fixture.json` with the verbatim content from design §2.1. Use the exact JSON shown — no field additions, no omissions.

- [x] 2.1 Write `evals/fixtures/b5-silence-on-casual-invite/fixture.json`
- [x] 2.2 Write `evals/fixtures/b3-retracted-allergy/fixture.json`
- [x] 2.3 Write `evals/fixtures/b0-joke-not-stored-as-fact/fixture.json`
- [x] 2.4 Write `evals/fixtures/b0-lore-not-autobiography/fixture.json`
- [x] 2.5 Write `evals/fixtures/b1-three-month-gap/fixture.json`
- [x] 2.6 Write `evals/fixtures/b0-stable-self-50-sessions/fixture.json`
- [x] 2.7 Write `evals/fixtures/b3-stale-job-purged/fixture.json`
- [x] 2.8 Write `evals/fixtures/b5-firing-stays-isolated/fixture.json`
- [x] 2.9 Write `evals/fixtures/b0-injection-quarantined/fixture.json`
- [x] 2.10 Verify: for each file, `"id"` matches the directory name and `"behavior"` is one of `b0`, `b1`, `b3`, `b5`.

## Task 3: Add `behavior` field to `TrialResult` (harness/trial.py)

This must come before runner.py changes so the `TrialResult(behavior=...)` constructor calls in task 5 compile.

- [x] 3.1 Append `behavior: str | None = None` as the last field of the `TrialResult` dataclass (after `error: str | None`).
- [x] 3.2 Add `"behavior": self.behavior` to `to_dict()`.
- [x] 3.3 Add `behavior=d.get("behavior")` to `from_dict()`.
- [x] 3.4 In `RunReport.rescore()`, add `behavior=orig_trial.behavior` to the manual `TrialResult(...)` constructor call (the one that builds `new_trial`).
- [x] 3.5 Verify: `python -c "from harness.trial import TrialResult"` exits 0.

## Task 4: Rewrite `print_summary()` (harness/trial.py)

- [x] 4.1 Add the `_BEHAVIOR_LABELS` module-level dict to `trial.py`:
  ```python
  _BEHAVIOR_LABELS: dict[str, str] = {
      "b0": "stable self",
      "b1": "relational texture",
      "b3": "knows who you are now",
      "b5": "appropriate silence",
  }
  ```
- [x] 4.2 Add the `_behavior_header(behavior: str | None) -> str` helper using the corrected implementation from design §5.4 (uses `fill`, not a dead `dashes` variable).
- [x] 4.3 Rewrite `RunReport.print_summary()` to:
  - Collect all `(baseline_id, trial)` pairs from all baselines into a flat list.
  - If no trial has a non-`None` `behavior`, fall back to the existing flat print loop (no change in output).
  - Otherwise group by behavior key order `b0 → b1 → b3 → b5 → None`; within each group sort rows by `(baseline_id, fixture_id)`; emit a header line before each non-empty group; omit the `(no behavior)` group if empty.
- [x] 4.4 Verify: `python -c "from harness.trial import RunReport"` exits 0.

## Task 5: Add `FixtureMeta`, `load_fixture_meta`, `--behavior` support (harness/runner.py)

- [x] 5.1 Add `from dataclasses import dataclass` to the imports in `runner.py` (not currently present).
- [x] 5.2 Add the `FixtureMeta` frozen dataclass after the imports block (8 fields: `id`, `behavior`, `title`, `description`, `probe_type`, `pass_proves`, `fail_reveals`, `why_naive_fails`; all `str`).
- [x] 5.3 Add `load_fixture_meta(fixture_dir: Path) -> FixtureMeta | None` (returns `None` on missing file or any `KeyError`/`JSONDecodeError`).
- [x] 5.4 Add `--behavior` argument to the `run` subparser in `main()`:
  ```python
  run_p.add_argument("--behavior", default=None,
      help="Filter fixtures to those with this behavior id (b0, b1, b3, b5)")
  ```
- [x] 5.5 Add the mutual exclusion guard as the **first statement** in `_cmd_run()`, before `cwd = Path.cwd()`:
  ```python
  if args.fixture and args.behavior:
      print("error: --fixture and --behavior are mutually exclusive")
      return 1
  ```
- [x] 5.6 Replace the **entire** `if args.fixture: ... else: fixture_ids = all_fixture_ids` block with the narrowing logic from design §4.3:
  - Narrow `all_fixture_ids = [args.fixture]` when `--fixture` is set (with not-found check).
  - Run the single-pass loop over `all_fixture_ids` to build `fixture_metas: dict[str, FixtureMeta | None]` and `fixture_ids: list[str]`, filtering by `args.behavior` when set.
  - Return 1 with a clear message if `args.behavior` is set but `fixture_ids` is empty.
  - The old `else: fixture_ids = all_fixture_ids` branch must be removed — it is dead code after the single-pass loop and would cause `fixture_ids` to be set twice if left in place.
- [x] 5.7 Add `behavior: str | None = None` parameter to `_run_trial()`.
- [x] 5.8 Add `behavior=behavior` to **all three** `TrialResult` constructors inside `_run_trial()`: the docker-skip early return, the import-error early return, and the normal return at the end.
- [x] 5.9 Update the trial loop in `_cmd_run()` to read `meta = fixture_metas.get(fid)` and pass `behavior=meta.behavior if meta is not None else None` to `_run_trial()`.
- [x] 5.10 Verify: `python -m harness run --help` shows `--behavior` in the output; `python -c "from harness.runner import FixtureMeta, load_fixture_meta"` exits 0.

## Task 6: Update tests/test_runner.py

- [x] 6.1 Grep `tests/test_runner.py` for old fixture name strings. Update any found to their new names per the rename mapping in design §1.
- [x] 6.2 Add `import json` to the imports (it is not currently present).
- [x] 6.3 Add `load_fixture_meta` to the existing `from harness.runner import ...` line.
- [x] 6.4 Add the three `FixtureMeta` unit tests from design §6.2:
  - `test_load_fixture_meta_returns_none_for_missing_file`
  - `test_load_fixture_meta_returns_none_for_malformed_json`
  - `test_load_fixture_meta_parses_valid_fixture`
- [x] 6.5 Add the three behavior-filter unit tests from design §6.3:
  - `test_behavior_filter_returns_correct_subset`
  - `test_behavior_filter_no_match_returns_empty`
  - `test_behavior_and_fixture_flags_are_mutually_exclusive`

## Task 7: Run full test suite

- [x] 7.1 `pytest tests/` — all tests pass. Count must be ≥ 75 (the original 69 plus the 6 new tests from task 6.4–6.5). Zero failures, zero errors.

## Task 8: Lint

- [x] 8.1 `ruff check harness/ tests/` — zero errors.

## Task 9: CLI smoke tests

Run from the project root (`/home/kaizen/Projects/companmem`).

- [x] 9.1 `python -m harness run --baseline oracle` → 9 fixtures, all `TrialStatus.OK`, all `resolved=True`. Summary shows behavior group headers.
- [x] 9.2 `python -m harness run --baseline naive-retrieve` → 9 fixtures, all `TrialStatus.OK`, all `resolved=False`.
- [x] 9.3 `python -m harness run --baseline oracle --behavior b5` → exactly 2 fixtures run (`b5-silence-on-casual-invite`, `b5-firing-stays-isolated`), both `resolved=True`.
- [x] 9.4 `python -m harness run --baseline oracle --behavior b0` → exactly 4 fixtures run, all `resolved=True`.
- [x] 9.5 `python -m harness run --baseline oracle --behavior b1` → exactly 1 fixture runs (`b1-three-month-gap`), `resolved=True`.
- [x] 9.6 `python -m harness run --baseline oracle --behavior b3` → exactly 2 fixtures run, both `resolved=True`.
- [x] 9.7 `python -m harness run --baseline oracle --behavior b9` → exits with return code 1, message contains `"no fixtures found for behavior"`.
- [x] 9.8 `python -m harness run --baseline oracle --behavior b0 --fixture b0-stable-self-50-sessions` → exits with return code 1, message contains `"mutually exclusive"`.
