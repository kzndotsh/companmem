# Requirements: Companion Memory Evaluation Harness

## Overview

Build `harness/` — an installable Python package that evaluates companion-memory systems against a fixed set of fictional-world fixtures. The harness is self-contained, stdlib-only in its core, and produces a deterministic `RunReport` from two CLI entry points. It is the authoritative mechanism for comparing adapters: oracle must pass all 9 fixtures, naive-retrieve must fail all 9.

---

## Functional Requirements

### FR-1: Package installation

**User story:** As a researcher, I want to install the harness with `pip install -e harness/` so that `python -m harness` works from any working directory without `sys.path.insert` hacks.

**Acceptance criteria:**
- `pip install -e harness/` succeeds in a clean Python 3.11 environment
- `python -m harness run --help` prints usage without error
- `python -m harness score --help` prints usage without error
- No `sys.path.insert` or `sys.path.append` appears anywhere inside `harness/`
- `harness/` does not import from `src/companmem/` (separate packages, separate concerns)

---

### FR-2: Fixture world loading

**User story:** As a researcher, I want each trial to receive a typed `World` object derived from the fixture files so that adapter code never reads fixture paths directly.

**Acceptance criteria:**
- `World.from_path(world_dir: Path, solution_dir: Path | None = None)` — the runner passes both paths explicitly. The method reads only from `world_dir` and (optionally) `solution_dir`; it never navigates to parent directories or infers paths from its arguments.
- `World` carries: `meta`, `characters`, `lore`, `next_user`, `fixture_hash`, and `solution`.
- `WorldMeta` is a frozen dataclass with `active_character_id` (str), `character_ids` (tuple[str, ...]), `last_interaction` (str | None), `as_of` (str | None).
- `Character` is a frozen dataclass with `character_id` (str), `identity` (str), `sessions` (tuple[SessionRow, ...]).
- `SessionRow` is a frozen dataclass with `session` (int), `date` (str), `summary` (str).
- All dataclasses are frozen. `sessions` and `character_ids` use `tuple` so the type checker enforces non-mutation. The `characters` dict and `FixtureSolution.gold_export` dict remain structurally mutable (Python has no immutable dict); this is an accepted limitation.
- `fixture_hash` is the sha256 of: for each file under `world_dir`, sorted by relative POSIX path, concatenate `<relative_path>\n<file_content>` for each file; sha256 the entire result as UTF-8. This definition is deterministic across implementations.
- Adapters receive a `World` object; they are never given a `Path`.

---

### FR-3: Adapter protocol

**User story:** As a developer adding a new memory system, I want a single `run(world, artifacts)` method signature so that the harness can call any adapter the same way.

**Acceptance criteria:**
- Every adapter implements `run(self, world: World, artifacts: Artifacts) -> AdapterMetrics`.
- `AdapterMetrics` carries `tokens_in` (int), `tokens_out` (int), and `memory_tokens` (int, tokens from retrieved memory specifically; defaults to 0).
- An adapter that raises `AdapterNotReadyError` (missing dependency, misconfigured environment) produces `TrialStatus.SKIPPED` with the exception message in `TrialResult.error`.
- Any other exception raised by an adapter produces `TrialStatus.INFRA_ERROR` with `"<ExceptionType>: <message>"` in `TrialResult.error`. It is never silently swallowed or treated as a predicate miss.
- `registry.json` maps each adapter id to a `"module.ClassName"` class path — adapters are loaded by this registry, not by filename convention.

---

### FR-4: Artifact persistence

**User story:** As a researcher, I want adapter outputs persisted to disk per run so that I can re-score them later against updated predicates without re-running expensive adapters.

**Acceptance criteria:**
- Each trial writes artifacts to `evals/results/<run_id>/<baseline_id>/<fixture_id>/`.
- Artifacts include at minimum `reply.txt` (the adapter's text reply) and `memory_export.json` (the adapter's structured memory dump).
- `Artifacts.write_reply(text)` and `Artifacts.write_export(data)` are the only write paths for adapters.
- `Artifacts.reply()` raises `ArtifactMissing` if `write_reply` was never called; same for `export()`.
- `Artifacts.output_dir` exposes the directory path so `RunReport` can record `artifacts_path`.
- Infra errors that prevent artifact writing are recorded as `TrialStatus.INFRA_ERROR` — they never silently become predicate misses.

---

### FR-5: Predicate scoring

**User story:** As a researcher, I want the harness to score adapter outputs against predicates loaded from fixture files so that the scoring logic is completely decoupled from adapter execution.

**Acceptance criteria:**
- Scorer reads predicates from `evals/fixtures/<fixture_id>/tests/predicates.json` — this path is never passed to adapters.
- Scorer runs strictly after the adapter returns; it calls `artifacts.reply()` and `artifacts.export()`, never the adapter or world directly.
- Four predicate kinds are supported, each taking a `needles` list (one or more strings):
  - `must_not` — none of the needles appear in the target (case-insensitive substring match).
  - `must_any` — at least one needle appears in the target.
  - `must_contain` — all needles appear in the target.
  - `must_json_path` — the `target` field is a dotted path (e.g. `export.characters.mara.kinds.user_bio`) walked into the export dict; the resulting subtree is serialized to a JSON string; all needles in `needles` are checked against that string (case-insensitive); passes if all needles are found (must_contain semantics). `needles` is a list, consistent with the other three kinds.
- Target resolution rules:
  - `"reply"` — the adapter's reply text.
  - `"export"` — the full export dict serialized as `json.dumps(export, ensure_ascii=True)`.
  - `"export.<dotted.path>"` — walk the dotted path into the export dict, serialize the resulting subtree to JSON.
- Two groups exist: `fail_to_pass` and `pass_to_pass`; `resolved = fail_to_pass AND pass_to_pass`.
- A `judge_prompt` field in `predicates.json` optionally triggers an LLM judge pass. The judge model is resolved in order: (1) a `judge_model` field in `predicates.json` for per-fixture overrides; (2) the `HARNESS_JUDGE_MODEL` environment variable as a fallback. `HARNESS_JUDGE_API_KEY` is required when a judge prompt is present. `HARNESS_JUDGE_BASE_URL` is optional (defaults to `https://api.openai.com/v1`) for non-OpenAI-compatible endpoints. If any required credential is absent and `judge_prompt` is present, the scorer raises `TrialStatus.INFRA_ERROR`. The judge runs at temperature=0. Judge score is stored separately in `TrialResult.judge_score` (float 0.0–1.0) and `TrialResult.judge_model` (str | None, the model name actually used) — neither is collapsed into `resolved`.
- Infra errors during scoring produce `TrialStatus.INFRA_ERROR` explicitly — never treated as predicate failures.

---

### FR-6: Run report

**User story:** As a researcher, I want a single `RunReport` object that captures all trial outcomes so that I can print a summary or write JSON without bespoke reporting scripts.

**Acceptance criteria:**
- `RunReport` carries: `run_id` (uuid), `observed_at` (ISO string, when adapters ran), `scored_at` (ISO string, when predicates were scored — distinct fields, may differ), `git_sha`, `fixture_ids`, and a list of `BaselineResult`.
- `BaselineResult` carries: `baseline_id`, `title`, trials list, `resolved_count`, `runnable_count`, `fixture_count`, `total_wall_ms`, `total_tokens_in`, `total_tokens_out`, `total_memory_tokens`, and `tokens_per_resolved` (int | None; None when `resolved_count` is 0; computed as `(total_tokens_in + total_tokens_out) / resolved_count` rounded to int). The field is named `tokens_per_resolved`, not `cost_per_resolved`, because the harness has no per-token pricing information.
- `TrialResult` carries: `fixture_id`, `fixture_hash`, `status`, `resolved`, `fail_to_pass`, `pass_to_pass`, `predicate_details`, `judge_score` (float | None), `judge_model` (str | None), `wall_ms`, `tokens_in`, `tokens_out`, `memory_tokens`, `export_tokens_approx`, `cost_flags` (list[str], e.g. `["export_tokens_over_budget", "wall_ms_over_budget"]`), `artifacts_path` (relative path, for regrading), `error`.
- `RunReport.to_json()` serializes to a valid JSON string.
- `RunReport.print_summary()` prints a human-readable table to stdout.
- At run time, the runner writes a `run_manifest.json` alongside `report.json` in `evals/results/<run_id>/`. The manifest records: `run_id`, `observed_at`, `git_sha`, `fixture_ids`, `cost_budgets` (copied from `registry.json` so `rescore()` can recompute cost flags without registry access), and for each baseline: `baseline_id`, `title`, `class` (from registry), `needs_docker`.
- `RunReport.rescore(artifacts_root, fixtures_root)` loads `run_manifest.json` and `report.json` from `artifacts_root` — the manifest provides adapter metadata and cost budgets, and `report.json` carries per-trial timing and token fields (`wall_ms`, `tokens_in`, `tokens_out`, `memory_tokens`, `export_tokens_approx`) that cannot be reconstructed from artifact files alone. Only scoring fields are overwritten (`resolved`, `fail_to_pass`, `pass_to_pass`, `predicate_details`, `judge_score`, `judge_model`); timing and token fields are carried forward from the original report. `observed_at` is preserved; `scored_at` is updated to the current time. `cost_flags` are recomputed from `cost_budgets` in the manifest. Raises `FileNotFoundError` with a clear message if either file is absent; raises `ValueError` if either is malformed.

---

### FR-7: CLI entry points

**User story:** As a researcher, I want two CLI commands — `run` and `score` — so that adapter execution and predicate scoring are independently invokable.

**Acceptance criteria:**
- `python -m harness run --baseline <id|all> [--fixture <id>] [--fixtures-root <path>] [--results-root <path>] [--include-docker]` runs adapters and scores immediately, writing `<results_root>/<run_id>/report.json` and `<results_root>/<run_id>/run_manifest.json`. The report path is printed to stdout after each run. There is no `--out` flag — the report path is always derived from `<results_root>/<run_id>/report.json`; use `--results-root` to redirect all output to a different parent directory. When `--fixture` is omitted, the runner enumerates fixtures by listing `evals/fixtures/` subdirectories that do not start with `_` (see FR-10). `--fixture <id>` accepts a single fixture ID; running against multiple specific fixtures requires running the command twice. `--fixtures-root <path>` overrides where the runner looks for `evals/fixtures/`; when omitted, it resolves `evals/fixtures/` relative to CWD and raises a clear error (`FileNotFoundError`) if that directory does not exist.
- `python -m harness score --run-id <id> [--results-root <path>] [--fixtures-root <path>]` re-scores a prior run. Default search: `evals/results/<run_id>/` relative to CWD. `--results-root` overrides the parent directory. `--fixtures-root` overrides the fixture directory (same default and error behaviour as `run`).
- `--baseline all` runs every adapter in the registry. Without `--include-docker`, adapters where `needs_docker: true` are skipped with `TrialStatus.SKIPPED` regardless of whether `--baseline all` or a specific id was passed; this is not an error and the run still completes and writes a report.
- Each trial gets an isolated `World` copy and a fresh `Artifacts` instance pointed at the correct output directory.

---

### FR-8: Oracle adapter and FixtureSolution

**User story:** As a researcher, I want the oracle adapter to produce known-good artifacts so that I can verify all 9 fixtures are scorable before running expensive adapters.

**Acceptance criteria:**
- `FixtureSolution` is a frozen dataclass with `gold_reply` (str) and `gold_export` (dict).
- `World` carries `solution: FixtureSolution | None`. The runner explicitly passes `solution_dir = fixture_dir / "solution"` to `World.from_path()`. The method reads `solution_dir / "gold_reply.txt"` and `solution_dir / "gold_memory_export.json"`; if either is absent, `solution` is `None`.
- `OracleAdapter.run()` writes `world.solution.gold_reply` as the reply and `world.solution.gold_export` as the export; raises `AdapterNotReadyError("no solution")` if `world.solution is None`.
- `OracleAdapter` requires no network, no API key, no Docker.
- Running `python -m harness run --baseline oracle` against all 9 fixtures produces all `resolved=True`.

---

### FR-9: External adapter stubs

**User story:** As a developer, I want adapter files for all 10 external memory systems pre-created so that I can implement them one at a time without modifying the harness core.

**Acceptance criteria:**
- The following stub files exist under `harness/adapters/`: `mem0.py`, `memoryos.py`, `langmem.py`, `a_mem.py`, `graphiti.py`, `letta.py`, `cognee.py`, `hindsight.py`, `telemem.py`, `honcho.py`.
- Each stub raises `NotImplementedError` from `run()` — not `AdapterNotReadyError`. `NotImplementedError` produces `TrialStatus.INFRA_ERROR`, which distinguishes "stub not yet written" from "dependency not installed" (`AdapterNotReadyError` → `SKIPPED`). This distinction is visible in the report.
- Once a developer begins implementing an adapter, they replace `NotImplementedError` with real logic; a missing pip install should then raise `AdapterNotReadyError`.

---

### FR-10: Fixture files

**User story:** As a researcher, I want the 9 evaluation fixtures present at `evals/fixtures/` so that the harness can find them without any path configuration.

**Acceptance criteria:**
- The 9 fixture directories exist at `evals/fixtures/`: `social-silence`, `forget-that`, `joke-as-fact`, `lore-vs-lived`, `three-month-reunion`, `identity-50`, `typed-retcon`, `cross-character-leak`, `persona-poison`.
- Each fixture directory has the structure: `environment/world/`, `tests/predicates.json`, `solution/`.
- Fixture files are copied as-is from `sandbox/research/evals/fixtures/` — world files and predicate files are correct and must not be modified.
- The runner enumerates fixtures by listing subdirectories of `evals/fixtures/` and excluding any that start with `_`. This means adding a new fixture requires only dropping a directory — no manifest file to update.
- `evals/results/` exists as an empty directory ready to receive run output.

---

## Acceptance Test

The harness is complete when **both** of these commands succeed end-to-end:

```
python -m harness run --baseline oracle
# Expected: all 9 fixtures → TrialStatus.OK, resolved=True

python -m harness run --baseline naive-retrieve
# Expected: all 9 fixtures → TrialStatus.OK, resolved=False
```

Oracle passes every fixture (proves the predicates are correct and the harness can produce a pass). Naive-retrieve fails every fixture (proves the harness can detect a wrong answer and the fixtures are hard enough to fail naive retrieval).

---

## Non-Functional Requirements

- **Python 3.11+** — type annotations use `Type | None` syntax throughout.
- **Stdlib-only core** — `world.py`, `artifacts.py`, `adapter.py`, `scorer.py`, `trial.py`, `runner.py` import only from the Python standard library; optional deps live in adapters only.
- **Ruff-clean** — code passes `ruff check harness/` with no errors. Enabled rule sets include `E/F/W` (pycodestyle/pyflakes), `I` (isort), `UP` (pyupgrade), `B` (bugbear), `SIM` (simplify), `RUF` (ruff-specific), `PTH` (enforce `Path` over `os.path`), and `DTZ` (enforce timezone-aware datetimes).
- **Type-checked** — code passes `basedpyright --project harness/` with `typeCheckingMode = "strict"` and no errors. basedpyright is used over mypy for its superior `Protocol` structural subtyping support. No `# type: ignore` comments anywhere.
- **Network-isolated tests** — pytest runs with `--disable-socket --allow-unix-socket --import-mode=importlib --strict-markers` and `testpaths = ["tests"]`. Naive adapter tests must never make real network calls; an accidental real-adapter instantiation fails loudly rather than silently hitting an API. `testpaths` prevents pytest from scanning the whole repo. Dev deps include both `pytest-cov` (pytest `--cov` integration) and `coverage` (branch coverage reporting).
- **Branch coverage** — `coverage run` uses `branch = true`. The scorer's predicate logic has multiple branches per predicate kind; branch coverage catches paths line coverage misses.
- **No path leakage** — the predicates path is never passed to adapters; raw fixture directory paths are not passed after `World` construction.
- **Fixtures are read-only** — the harness never writes to `evals/fixtures/`; all run output goes to `evals/results/`.
- **Reproducible results** — given the same fixtures and adapter code, two runs produce identical `resolved` values (adapters themselves may be nondeterministic, but the harness does not introduce additional non-determinism).
