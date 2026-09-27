# Tasks: Companion Memory Evaluation Harness

## Overview

Ordered, checkable implementation tasks derived from `requirements.md` and `design.md`. Tasks are sequenced so each step builds on a working foundation. Run `python -m harness run --baseline oracle` and `python -m harness run --baseline naive-retrieve` as the final acceptance gate.

Type-check each phase with `basedpyright --project harness/` (not per-file — basedpyright requires the project root to pick up `pyproject.toml` config).

---

## Phase 0: Repo scaffolding

- [x] 0.1 Create `harness/` directory and all empty `__init__.py` files:
  - `harness/__init__.py`
  - `harness/adapters/__init__.py`
- [x] 0.2 Create `tests/__init__.py` (empty) at the repo root (sibling of `harness/`, not inside it).
- [x] 0.3 Create `harness/pyproject.toml` with:
  - Build system: `hatchling`; `[tool.hatch.build.targets.wheel] packages = ["harness"]` (excludes `tests/` from the wheel automatically since it lives outside `harness/`)
  - `requires-python = ">=3.11"`, `dependencies = []`
  - Dev extras: `ruff`, `basedpyright`, `pytest`, `pytest-socket`, `pytest-cov`, `coverage`
  - Ruff rules: `E`, `F`, `W`, `I`, `UP`, `B`, `SIM`, `RUF`, `PTH`, `DTZ`
  - basedpyright: `typeCheckingMode = "strict"`, `reportUnnecessaryTypeIgnoreComment = "warning"`
  - pytest: `testpaths = ["tests"]`, `addopts = "--import-mode=importlib --strict-markers --disable-socket --allow-unix-socket"`
  - coverage: `branch = true`, `source = ["harness"]`
- [x] 0.4 Create `harness/requirements.txt` (empty file — core is stdlib-only).
- [x] 0.5 Run `pip install -e harness/` in the project venv and confirm the package installs cleanly: `python -c "import harness; print('ok')"` should print `ok` with no import error. (`python -m harness` is not yet testable — `__main__.py` is created in Phase 10.)

---

## Phase 1: `world.py`

- [x] 1.1 Implement all frozen dataclasses in `harness/world.py`:
- [x] 1.2 Implement `World.from_path(world_dir: Path, solution_dir: Path | None = None) -> World`:
- [x] 1.3 Write `tests/test_world.py`:
- [x] 1.4 Confirm `ruff check harness/world.py` and `basedpyright --project harness/` pass with no errors.

---

## Phase 2: `artifacts.py`

- [x] 2.1 Implement `harness/artifacts.py`:
- [x] 2.2 Write unit tests in `tests/test_artifacts.py`:
- [x] 2.3 Confirm `ruff check` and `basedpyright --project harness/` pass.

---

## Phase 3: `adapter.py`

- [x] 3.1 Implement `harness/adapter.py`:
- [x] 3.2 Implement `harness/adapters/_base.py` — re-exports `Adapter`, `AdapterMetrics`, `AdapterNotReadyError`, `World`, `Artifacts`.
- [x] 3.3 Confirm `ruff check` and `basedpyright --project harness/` pass (the Protocol structural subtyping is the primary check here).

---

## Phase 4: `scorer.py`

- [x] 4.1 Implement `harness/scorer.py`:
- [x] 4.2 Implement the four predicate kinds in `score()`:
- [x] 4.3 Implement target resolution: `"reply"`, `"export"`, `"export.<dotted.path>"`
- [x] 4.4 Implement scoring groups: `fail_to_pass AND pass_to_pass = resolved`. Empty group → that group fails.
- [x] 4.5 Implement optional LLM judge pass:
- [x] 4.6 Write `tests/test_scorer.py`:
- [x] 4.7 Confirm `ruff check` and `basedpyright --project harness/` pass.

---

## Phase 5: `trial.py`

- [x] 5.1 Implement `harness/trial.py`:
- [x] 5.2 `rescore()` implementation:
- [x] 5.3 Write unit tests in `tests/test_trial.py`:
- [x] 5.4 Confirm `ruff check` and `basedpyright --project harness/` pass.

---

## Phase 6: Fixture files

- [x] 6.1 Copy the 9 fixture directories from `sandbox/research/evals/fixtures/` to `evals/fixtures/` as-is:
- [x] 6.2 Confirm each copied fixture has `environment/world/`, `tests/predicates.json`, and `solution/` with `gold_reply.txt` and `gold_memory_export.json`.
- [x] 6.3 Confirm `evals/results/` exists (create empty if needed).

---

## Phase 7: `adapters/naive.py`

- [x] 7.1 Implement `OracleAdapter` in `harness/adapters/naive.py`:
- [x] 7.2 Implement `NaiveRetrieveAdapter`:
- [x] 7.3 Implement `NaiveRagAdapter`:
- [x] 7.4 Implement `LongContextStuffAdapter`:
- [x] 7.5 Write unit tests in `tests/test_naive_adapters.py`:

---

## Phase 8: External adapter stubs

- [x] 8.1 Create stub classes in each adapter file under `harness/adapters/`:

---

## Phase 9: `registry.json`

- [x] 9.1 Create `harness/registry.json` with all 14 adapter entries (4 naive + 10 stubs) exactly as specified in the design.

---

## Phase 10: `runner.py` and `__main__.py`

- [x] 10.1 Create `harness/__main__.py`: (verified: `python -m harness` gives usage error)
- [x] 10.2 Implement `harness/runner.py` with two argparse subcommands: `run` and `score`.
- [x] 10.3 Implement `run` subcommand:
- [x] 10.4 Implement `score` subcommand:
- [x] 10.5 Write unit tests in `tests/test_runner.py`:
- [x] 10.6 Confirm `ruff check harness/ tests/` and `basedpyright --project harness/` pass.

---

## Phase 11: Acceptance test

- [x] 11.1 Run `python -m harness run --baseline oracle` from the repo root. ✅ all 9 → PASS
- [x] 11.2 Run `python -m harness run --baseline naive-retrieve` from the repo root. ✅ all 9 → FAIL
- [x] 11.3 Run `python -m harness run --baseline naive-rag` and `--baseline long-context-stuff`. ✅ all 9 → FAIL for both
- [x] 11.4 Run `python -m harness run --baseline mem0` (stub). ✅ all 9 → INFRA_ERROR
- [x] 11.5 Smoke-test `rescore`. ✅ same scores, updated scored_at
- [x] 11.6 Run the full test suite: `pytest --cov=harness --cov-report=term-missing`. ✅ 69 passed
- [x] 11.7 Run `ruff check harness/ tests/` and `basedpyright --project harness/` — zero errors. ✅
