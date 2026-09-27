# Design: Companion Memory Evaluation Harness

## Overview

`harness/` is a standalone installable Python package. Its core is six modules (`world`, `artifacts`, `adapter`, `scorer`, `trial`, `runner`) that depend only on the stdlib. Adapter implementations live under `harness/adapters/` and carry their own optional deps. The runner is invoked as `python -m harness run` or `python -m harness score`.

This document covers the technical design for each module, the data flow through a trial, the registry format, and the naive adapter implementations.

---

## Directory Layout

```
harness/
  __init__.py           # package marker, exports nothing
  __main__.py           # delegates to runner.main()
  world.py              # World dataclass + World.from_path()
  artifacts.py          # Artifacts container + ArtifactMissing
  adapter.py            # Adapter Protocol + AdapterMetrics + AdapterNotReadyError
  scorer.py             # Scorer class + predicate evaluation
  trial.py              # TrialResult, BaselineResult, RunReport dataclasses
  runner.py             # CLI entry points: run + score
  registry.json         # adapter registry + cost budgets
  pyproject.toml        # build config, ruff, basedpyright, pytest, coverage
  requirements.txt      # empty (core is stdlib-only)
  adapters/
    __init__.py
    _base.py            # shared imports / re-exports for adapter authors
    naive.py            # OracleAdapter, NaiveRetrieveAdapter, NaiveRagAdapter, LongContextStuffAdapter
    mem0.py             # stub → NotImplementedError
    memoryos.py
    langmem.py
    a_mem.py
    graphiti.py
    letta.py
    cognee.py
    hindsight.py
    telemem.py
    honcho.py
```

`tests/` and `evals/` live at the repo root, not inside `harness/` (so they are not packaged into the wheel):

```
tests/
  __init__.py           # empty; makes tests a package for --import-mode=importlib
  test_scorer.py        # unit tests for predicate engine (all 4 kinds + judge pass)
  test_world.py         # unit tests for World.from_path(), fixture_hash, solution loading
  # further test files added alongside each harness module
```

`evals/` lives at the repo root, not inside `harness/`:

```
evals/
  fixtures/             # read-only; never written by harness
    <fixture_id>/
      environment/
        world/          # world files read by World.from_path()
      solution/         # gold_reply.txt, gold_memory_export.json
      tests/
        predicates.json
  results/              # written by runner; one subdir per run_id
    <run_id>/
      report.json
      run_manifest.json
      <baseline_id>/
        <fixture_id>/
          reply.txt
          memory_export.json
```

---

## Module Designs

### `world.py`

```python
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class SessionRow:
    session: int
    date: str
    summary: str

@dataclass(frozen=True)
class Character:
    character_id: str
    identity: str
    sessions: tuple[SessionRow, ...]  # tuple so mypy enforces non-mutation

@dataclass(frozen=True)
class WorldMeta:
    active_character_id: str
    character_ids: tuple[str, ...]    # tuple for same reason
    last_interaction: str | None
    as_of: str | None

@dataclass(frozen=True)
class FixtureSolution:
    gold_reply: str
    gold_export: dict[str, Any]       # fully parameterized; no type: ignore

@dataclass(frozen=True)
class World:
    meta: WorldMeta
    characters: dict[str, Character]  # values are frozen; see immutability note
    lore: str | None
    next_user: str
    fixture_hash: str
    solution: FixtureSolution | None

    @classmethod
    def from_path(cls, world_dir: Path, solution_dir: Path | None = None) -> "World":
        ...
```

**Immutability note:** `frozen=True` prevents attribute reassignment on all dataclasses. `sessions` and `character_ids` use `tuple` so mypy enforces non-mutation. The `characters` dict and `gold_export` dict remain structurally mutable (Python has no immutable dict); this is an accepted limitation — harness code must not mutate them. No `# type: ignore` is used anywhere.

**`from_path` implementation logic:**

1. Read `world_dir / "meta.json"` → `WorldMeta` (with `character_ids` as `tuple[str, ...]`).
2. For each `character_id` in `meta.character_ids`:
   - Read `world_dir / "companions" / character_id / "character.md"` → `identity` (empty string if absent).
   - Read `world_dir / "companions" / character_id / "sessions.jsonl"` → `tuple[SessionRow, ...]` (empty tuple if absent).
3. Read `world_dir / "lore.md"` → `lore` (None if absent).
4. Read `world_dir / "next_user.txt"` → `next_user`.
5. Compute `fixture_hash`: walk all files under `world_dir`, sort by relative POSIX path, concatenate `f"{rel_path}\n{content}"` for each, sha256 the UTF-8 bytes, hex-encode.
6. If `solution_dir` is not None: read `solution_dir / "gold_reply.txt"` and `solution_dir / "gold_memory_export.json"`. If both exist, create `FixtureSolution`; if either is absent, `solution = None`.

The method never navigates above `world_dir` or `solution_dir`. No path inference from parent directories.

---

### `artifacts.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

class ArtifactMissing(RuntimeError): ...

class Artifacts:
    def __init__(self, output_dir: Path) -> None: ...
    def write_reply(self, text: str) -> None: ...          # writes reply.txt
    def write_export(self, data: dict[str, Any]) -> None: ... # writes memory_export.json as JSON
    def reply(self) -> str: ...                             # raises ArtifactMissing if not written
    def export(self) -> dict[str, Any]: ...                 # raises ArtifactMissing if not written
    @property
    def output_dir(self) -> Path: ...
```

**Implementation notes:**
- `write_reply` / `write_export` create `output_dir` on first write (`mkdir(parents=True, exist_ok=True)`).
- `reply()` and `export()` check for the file on disk (not an in-memory flag) so they work after process restart for regrading.
- No caching of in-memory state beyond what's on disk — regrading reads from disk.

---

### `adapter.py`

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol
from harness.world import World
from harness.artifacts import Artifacts

@dataclass
class AdapterMetrics:
    tokens_in: int
    tokens_out: int
    memory_tokens: int = field(default=0)

class AdapterNotReadyError(RuntimeError): ...

class Adapter(Protocol):
    def run(self, world: World, artifacts: Artifacts) -> AdapterMetrics: ...
```

**Adapter loading:** `runner.py` loads adapters by reading `registry.json`, splitting `"class"` on the last `.` to get `(module_path, class_name)`, calling `importlib.import_module(module_path)`, and `getattr(module, class_name)()` to instantiate. No `spec_from_file_location` — everything is importable by module path because `harness` is an installed package.

**Error handling in runner:**
```
AdapterNotReadyError  →  TrialStatus.SKIPPED      ("missing dependency / misconfigured env")
NotImplementedError   →  TrialStatus.INFRA_ERROR   ("stub not yet written")
any other exception   →  TrialStatus.INFRA_ERROR
```
Error message in `TrialResult.error` is `f"{type(exc).__name__}: {exc}"` for all INFRA_ERROR cases.

---

### `scorer.py`

```python
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from harness.artifacts import Artifacts

@dataclass
class ScorerResult:
    resolved: bool
    fail_to_pass: bool
    pass_to_pass: bool
    predicate_details: list[str]
    judge_score: float | None
    judge_model: str | None

class Scorer:
    def __init__(self, predicates_path: Path) -> None: ...
    def score(self, artifacts: Artifacts) -> ScorerResult: ...
```

**Predicate evaluation:**

Four kinds, each with `id`, `kind`, `target`, `needles: list[str]`:

| Kind | Passes when |
|------|------------|
| `must_not` | no needle appears in haystack (case-insensitive) |
| `must_any` | at least one needle appears |
| `must_contain` | all needles appear |
| `must_json_path` | target is a dotted path into export; subtree serialized to JSON; all needles appear (must_contain semantics) |

Target resolution:
- `"reply"` → `artifacts.reply()`
- `"export"` → `json.dumps(artifacts.export(), ensure_ascii=True)`
- `"export.<path>"` → walk dotted path into export dict, serialize subtree

Per-predicate result appended to `predicate_details` as `"<id>: ok"` or `"<id>: <reason>"`.

**Judge pass** (optional, runs after predicate scoring):
- Triggered by `judge_prompt` field in `predicates.json`.
- Judge model resolved in order: `predicates["judge_model"]` (per-fixture override) → `os.environ["HARNESS_JUDGE_MODEL"]` (fallback). If neither is set and `judge_prompt` is present, scorer raises, which the runner catches as INFRA_ERROR.
- `HARNESS_JUDGE_API_KEY` env var is required when a judge prompt is present. If absent, scorer raises → INFRA_ERROR.
- `HARNESS_JUDGE_BASE_URL` env var is optional; defaults to `https://api.openai.com/v1`. Set this for non-OpenAI-compatible endpoints.
- Calls the judge model at temperature=0 via stdlib `urllib.request` (OpenAI-compatible JSON API). No third-party HTTP library in scorer core.
- Returns a float 0.0–1.0 stored in `ScorerResult.judge_score`; `judge_model` records the model name used. Neither is collapsed into `resolved`.

**Scorer is the only code that knows the predicates path.** The runner passes `evals/fixtures/<fixture_id>/tests/predicates.json` to `Scorer.__init__`; adapters never see this path.

---

### `trial.py`

Dataclasses use `@dataclass` (not frozen — assembled incrementally by the runner). Serialization uses a custom `to_dict()` method that converts `TrialStatus` enum members to their `.value` string. `RunReport.to_json()` calls `json.dumps(self.to_dict())` — no custom `JSONEncoder` needed. `dataclasses.asdict()` is not used for serialization because it does not serialize enum members as strings by default.

```python
from __future__ import annotations
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

class TrialStatus(Enum):
    OK = "ok"
    INFRA_ERROR = "infra_error"
    SKIPPED = "skipped"

@dataclass
class TrialResult:
    fixture_id: str
    fixture_hash: str
    status: TrialStatus
    resolved: bool
    fail_to_pass: bool
    pass_to_pass: bool
    predicate_details: list[str]
    judge_score: float | None
    judge_model: str | None
    wall_ms: int
    tokens_in: int
    tokens_out: int
    memory_tokens: int
    export_tokens_approx: int
    cost_flags: list[str]        # e.g. ["export_tokens_over_budget", "wall_ms_over_budget"]
    artifacts_path: str          # relative to repo root
    error: str | None

    def to_dict(self) -> dict[str, Any]:
        # status serialized as status.value; all other fields are JSON-native
        ...

@dataclass
class BaselineResult:
    baseline_id: str
    title: str
    trials: list[TrialResult]
    resolved_count: int
    runnable_count: int
    fixture_count: int
    total_wall_ms: int
    total_tokens_in: int
    total_tokens_out: int
    total_memory_tokens: int
    tokens_per_resolved: int | None  # (total_tokens_in + total_tokens_out) // resolved_count

    def to_dict(self) -> dict[str, Any]:
        # calls to_dict() on each TrialResult in trials
        ...

    @classmethod
    def from_trials(cls, baseline_id: str, title: str, trials: list[TrialResult]) -> "BaselineResult":
        """Aggregate trial results into a BaselineResult. Runner calls this; never constructs manually."""
        ok = [t for t in trials if t.status == TrialStatus.OK]
        resolved = [t for t in ok if t.resolved]
        total_in = sum(t.tokens_in for t in ok)
        total_out = sum(t.tokens_out for t in ok)
        return cls(
            baseline_id=baseline_id,
            title=title,
            trials=trials,
            resolved_count=len(resolved),
            runnable_count=len(ok),
            fixture_count=len(trials),
            total_wall_ms=sum(t.wall_ms for t in ok),
            total_tokens_in=total_in,
            total_tokens_out=total_out,
            total_memory_tokens=sum(t.memory_tokens for t in ok),
            tokens_per_resolved=(total_in + total_out) // len(resolved) if resolved else None,
        )

@dataclass
class RunReport:
    run_id: str
    observed_at: str
    scored_at: str
    git_sha: str
    fixture_ids: list[str]
    baselines: list[BaselineResult]

    def to_dict(self) -> dict[str, Any]:
        # calls to_dict() on each BaselineResult in baselines
        ...

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def print_summary(self) -> None: ...

    @classmethod
    def rescore(cls, artifacts_root: Path, fixtures_root: Path) -> "RunReport": ...
```

**`cost_flags` on `TrialResult`:** set by the runner after the trial completes, by comparing `TrialResult.export_tokens_approx` against `registry["cost_budgets"]["export_tokens_approx_per_trial"]` and `TrialResult.wall_ms` against `registry["cost_budgets"]["wall_ms_per_trial"]`. Values: `"export_tokens_over_budget"`, `"wall_ms_over_budget"`. Budgets are informational — they do not abort the trial or change `status`, but they appear in the summary output.

**`rescore()` implementation:**
1. Load `artifacts_root / "run_manifest.json"`. Raise `FileNotFoundError` (clear message) if absent; `ValueError` if malformed.
2. Load `artifacts_root / "report.json"` to recover per-trial timing and token fields (`wall_ms`, `tokens_in`, `tokens_out`, `memory_tokens`, `export_tokens_approx`). These fields came from the adapter run and are not reconstructible from artifact files alone. Raise `FileNotFoundError` if absent; `ValueError` if malformed.
3. For each baseline in the manifest, walk `artifacts_root / baseline_id / fixture_id /`.
4. Instantiate `Artifacts(that_dir)` and `Scorer(fixtures_root / fixture_id / "tests" / "predicates.json")`.
5. Call `scorer.score(artifacts)` — re-runs predicate evaluation against existing artifact files.
6. Overwrite only scoring fields on each trial: `resolved`, `fail_to_pass`, `pass_to_pass`, `predicate_details`, `judge_score`, `judge_model`. Carry forward from the original report: `wall_ms`, `tokens_in`, `tokens_out`, `memory_tokens`, `export_tokens_approx`, `status`, `fixture_hash`, `artifacts_path`.
7. Recompute `cost_flags` from `cost_budgets` read out of the manifest (not from `registry.json` — `rescore()` has no path to it) using the carried-forward `wall_ms` and `export_tokens_approx`.
8. Preserve `observed_at` from manifest; set `scored_at` to `datetime.now(timezone.utc).isoformat()`.

---

### `runner.py`

Two sub-commands via `argparse` subparsers, dispatched from `__main__.py`.

**`run` sub-command flow:**

CLI: `python -m harness run --baseline <id|all> [--fixture <id>] [--fixtures-root <path>] [--results-root <path>] [--include-docker]`

```
1. Parse args; resolve fixtures_root (--fixtures-root or cwd/evals/fixtures; FileNotFoundError if absent)
2. Resolve results_root (--results-root or cwd/evals/results; created if absent)
3. Enumerate fixture_ids: sorted subdirs of fixtures_root not starting with "_"
4. Filter to --fixture <id> if given
5. Load registry.json; resolve selected baseline(s)
6. Generate run_id = uuid4().hex
7. For each baseline:
   a. Load adapter class via importlib
   b. For each fixture_id:
      i.  Read world: World.from_path(
              fixtures_root / fixture_id / "environment" / "world",
              solution_dir = fixtures_root / fixture_id / "solution"
          )
      ii. Construct artifacts: Artifacts(results_root / run_id / baseline_id / fixture_id)
      iii. If needs_docker and not --include-docker: record SKIPPED, continue
      iv.  t0 = perf_counter(); run adapter; wall_ms = elapsed
      v.   Score: Scorer(fixtures_root / fixture_id / "tests" / "predicates.json").score(artifacts)
      vi.  Compute cost_flags from registry budgets
      vii. Build TrialResult
   c. BaselineResult.from_trials(baseline_id, title, trials)
8. Build RunReport; write results_root / run_id / report.json + run_manifest.json
9. Print summary; print the report path
```

`--results-root <path>` controls where all run output lands. There is no `--out` flag — the report path is always `<results_root>/<run_id>/report.json` and is printed to stdout after each run. FR-7's `[--out <path>]` is superseded by `--results-root` in this design: `--results-root` scopes the whole output directory rather than a single file path, which is necessary because each run writes multiple files (`report.json`, `run_manifest.json`, artifact directories).

**`score` sub-command flow:**

```
1. Parse args; resolve results_root (--results-root or cwd/evals/results)
2. resolve fixtures_root (--fixtures-root or cwd/evals/fixtures)
3. artifacts_root = results_root / run_id
4. report = RunReport.rescore(artifacts_root, fixtures_root)
5. Write updated report.json to artifacts_root
6. Print summary
```

CLI for `score`: `python -m harness score --run-id <id> [--results-root <path>] [--fixtures-root <path>]`

**`__main__.py`:**

```python
from harness.runner import main
raise SystemExit(main())
```

---

### `registry.json`

Full contents — all 14 adapters (4 naive + 10 external stubs):

```json
{
  "cost_budgets": {
    "export_tokens_approx_per_trial": 8000,
    "wall_ms_per_trial": 60000
  },
  "adapters": [
    {"id": "oracle",           "title": "Fixture oracle (solvability check)",        "class": "harness.adapters.naive.OracleAdapter",          "needs_network": false, "needs_api_key": false, "needs_docker": false},
    {"id": "naive-retrieve",   "title": "Retrieve-then-speak, one user bag",          "class": "harness.adapters.naive.NaiveRetrieveAdapter",   "needs_network": false, "needs_api_key": false, "needs_docker": false},
    {"id": "naive-rag",        "title": "Top-k chunk overlap bag, no isolation",      "class": "harness.adapters.naive.NaiveRagAdapter",        "needs_network": false, "needs_api_key": false, "needs_docker": false},
    {"id": "long-context-stuff","title": "Stuff full world text into reply",           "class": "harness.adapters.naive.LongContextStuffAdapter","needs_network": false, "needs_api_key": false, "needs_docker": false},
    {"id": "mem0",             "title": "Mem0 extract-every-turn",                    "class": "harness.adapters.mem0.Mem0Adapter",             "needs_network": true,  "needs_api_key": true,  "needs_docker": false},
    {"id": "memoryos",         "title": "MemoryOS 3-tier hierarchy",                  "class": "harness.adapters.memoryos.MemoryOSAdapter",     "needs_network": true,  "needs_api_key": true,  "needs_docker": false},
    {"id": "langmem",          "title": "LangMem curated primitives",                 "class": "harness.adapters.langmem.LangMemAdapter",       "needs_network": true,  "needs_api_key": true,  "needs_docker": false},
    {"id": "a-mem",            "title": "A-MEM agentic memory ChromaDB",              "class": "harness.adapters.a_mem.AMemAdapter",            "needs_network": true,  "needs_api_key": true,  "needs_docker": false},
    {"id": "graphiti",         "title": "Graphiti temporal graph",                    "class": "harness.adapters.graphiti.GraphitiAdapter",     "needs_network": true,  "needs_api_key": true,  "needs_docker": true},
    {"id": "letta",            "title": "Letta typed memory blocks",                  "class": "harness.adapters.letta.LettaAdapter",           "needs_network": true,  "needs_api_key": false, "needs_docker": false},
    {"id": "cognee",           "title": "Cognee knowledge graph",                     "class": "harness.adapters.cognee.CogneeAdapter",         "needs_network": true,  "needs_api_key": true,  "needs_docker": false},
    {"id": "hindsight",        "title": "Hindsight embedded DB",                      "class": "harness.adapters.hindsight.HindsightAdapter",   "needs_network": false, "needs_api_key": false, "needs_docker": false},
    {"id": "telemem",          "title": "TeleMem FAISS+JSON fast writes",             "class": "harness.adapters.telemem.TelememAdapter",       "needs_network": true,  "needs_api_key": true,  "needs_docker": false},
    {"id": "honcho",           "title": "Honcho directional peer memory",             "class": "harness.adapters.honcho.HonchoAdapter",         "needs_network": true,  "needs_api_key": false, "needs_docker": true}
  ]
}
```

`"class"` is a fully-qualified dotted path: `importlib.import_module("harness.adapters.naive")` then `getattr(module, "OracleAdapter")()`.

**`cost_budgets`** are applied by the runner after each trial to set `TrialResult.cost_flags`, and are also copied into `run_manifest.json` so `rescore()` can recompute flags without registry access.

---

### `adapters/naive.py`

**`OracleAdapter`**
- `run(world, artifacts)`: if `world.solution is None` raise `AdapterNotReadyError("no solution")`. Otherwise write `world.solution.gold_reply` and `world.solution.gold_export`. Return `AdapterMetrics(tokens_in=0, tokens_out=0)`.
- Guaranteed all-pass: writes the gold solution directly, so all predicates are trivially satisfied.

**`NaiveRetrieveAdapter`**
- Reads `world.meta.active_character_id`, joins all session summaries for that character, prepends this fixed prefix:
  ```
  "I'm here for you as your companion. Based on what I remember: "
  ```
  The prefix contains `"I'm here for you"` and `"as your companion"` — phrases that appear verbatim in `must_not` predicates across multiple fixtures. This guarantees failure on any fixture that includes those `must_not` checks.
- Does not use `world.next_user` as a retrieval query — it dumps the full session bag regardless of the question.
- Guaranteed all-fail: the hardcoded companion-voice prefix triggers `must_not` predicates present in all 9 fixtures.

**`NaiveRagAdapter`**
- Concatenates all world text (identity + all sessions + lore) into one blob, chunks into 200-word windows (100-word step), scores each chunk by word-overlap with `world.next_user`, takes top-3, prepends the same fixed companion-voice prefix as `NaiveRetrieveAdapter`.
- Guaranteed all-fail: the companion-voice prefix triggers the same `must_not` predicates.

**`LongContextStuffAdapter`**
- Serializes the entire `World` object (all characters, all sessions, lore, meta) to a JSON blob and writes it as the reply verbatim. Writes no structured `memory_export.json` (or writes an empty `{}`).
- Guaranteed all-fail primarily via `pass_to_pass` export predicates: every fixture requires specific structured data in `memory_export.json` (e.g. named memory kinds like `user_bio`, specific character entries). Writing a raw JSON dump or empty export fails these structured checks every time, regardless of reply content.
- Secondary failure path for some fixtures: the raw JSON reply may also trip `must_not` predicates if world data contains forbidden phrases, but this is not relied upon as the primary guarantee.

**Failure guarantee rationale:** All 9 fixtures include `must_not` predicates that forbid companion-voice framing (`"I'm here for you"`, `"as your companion"`, `"as an AI"`, `"I'm your assistant"`). `NaiveRetrieveAdapter` and `NaiveRagAdapter` use a hardcoded prefix that matches these needles. `LongContextStuffAdapter` writes raw JSON that either matches those needles in character identity fields or fails `pass_to_pass` export checks. If a fixture is ever added that lacks such `must_not` predicates, the naive adapters would need revisiting.

---

### `adapters/_base.py`

Re-exports the symbols adapter authors need:

```python
from harness.adapter import Adapter, AdapterMetrics, AdapterNotReadyError
from harness.world import World
from harness.artifacts import Artifacts

__all__ = ["Adapter", "AdapterMetrics", "AdapterNotReadyError", "World", "Artifacts"]
```

---

### External adapter stubs

Each stub file follows this pattern:

```python
# harness/adapters/mem0.py
from harness.adapters._base import AdapterMetrics, World, Artifacts

class Mem0Adapter:
    def run(self, world: World, artifacts: Artifacts) -> AdapterMetrics:
        raise NotImplementedError("Mem0Adapter not yet implemented")
```

`NotImplementedError` → `TrialStatus.INFRA_ERROR` (distinguishes "not written yet" from `AdapterNotReadyError` → `SKIPPED` "missing pip install").

---

## Package Setup

`harness/pyproject.toml` (PEP 517, hatchling):

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "harness"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []   # core is stdlib-only

[project.optional-dependencies]
dev = ["ruff", "basedpyright", "pytest", "pytest-socket", "pytest-cov", "coverage"]

[tool.hatch.build.targets.wheel]
packages = ["harness"]

[tool.ruff]
target-version = "py311"

[tool.ruff.lint]
select = [
    "E", "F", "W",   # pycodestyle + pyflakes
    "I",              # isort
    "UP",             # pyupgrade: enforce modern Python syntax
    "B",              # flake8-bugbear: catches real bugs
    "SIM",            # flake8-simplify: simplify redundant constructs
    "RUF",            # ruff-specific rules
    "PTH",            # flake8-use-pathlib: enforce Path over os.path
    "DTZ",            # flake8-datetimez: enforce timezone-aware datetimes
]

[tool.basedpyright]
pythonVersion = "3.11"
typeCheckingMode = "strict"
reportUnnecessaryTypeIgnoreComment = "warning"  # catches stale type: ignore

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--import-mode=importlib --strict-markers --disable-socket --allow-unix-socket"
# --disable-socket: naive adapters must never hit the network in tests;
# an accidental real-adapter instantiation fails loudly instead of silently calling an API.
# --allow-unix-socket: permits local IPC (e.g. filesystem-backed vector stores in tests).
# testpaths = ["tests"]: prevents pytest from scanning the whole repo.

[tool.coverage.run]
branch = true    # branch coverage matters for scorer predicate logic (multiple branches per kind)
source = ["harness"]
```

`harness/requirements.txt` — empty (core stdlib only). Each adapter's optional deps are documented in its module docstring.

---

## Data Flow: Single Trial

```
Runner
  │
  ├── World.from_path(world_dir, solution_dir)   ← reads fixture files
  │     └── returns frozen World
  │
  ├── Artifacts(output_dir)                       ← empty container pointing at results path
  │
  ├── adapter.run(world, artifacts)               ← adapter writes reply.txt + memory_export.json
  │     ├── success → AdapterMetrics
  │     ├── AdapterNotReadyError → SKIPPED
  │     ├── NotImplementedError  → INFRA_ERROR
  │     └── any other exception → INFRA_ERROR
  │
  ├── Scorer(predicates_path).score(artifacts)    ← reads artifacts from disk, never calls adapter
  │     ├── loads predicates.json
  │     ├── evaluates 4 predicate kinds
  │     ├── optionally calls LLM judge
  │     └── returns ScorerResult
  │
  ├── compute cost_flags from registry budgets
  │
  └── TrialResult assembled from all of the above
```

The scorer is the only component that knows `predicates_path`. The adapter is the only component that writes to `Artifacts`. Neither component knows about the other.

---

## `run_manifest.json` Schema

Written alongside `report.json` at `evals/results/<run_id>/run_manifest.json`:

```json
{
  "run_id": "<uuid>",
  "observed_at": "<ISO-8601>",
  "git_sha": "<40-char hex or 'unknown'>",
  "fixture_ids": ["social-silence", "..."],
  "cost_budgets": {
    "export_tokens_approx_per_trial": 8000,
    "wall_ms_per_trial": 60000
  },
  "baselines": [
    {
      "baseline_id": "oracle",
      "title": "Fixture oracle (solvability check)",
      "class": "harness.adapters.naive.OracleAdapter",
      "needs_docker": false
    }
  ]
}
```

`cost_budgets` is copied from `registry.json` at run time and stored in the manifest so `rescore()` can recompute `cost_flags` without access to the installed package or a registry path. This plus `report.json` from the same directory are the two inputs `RunReport.rescore()` needs beyond the artifact directories themselves.

---

## Token Counting

`export_tokens_approx` is computed as `len(json.dumps(export).split())` — a word-split approximation, no tiktoken dependency. This is clearly documented as approximate in field names and comments.

`tokens_in` / `tokens_out` / `memory_tokens` are reported by adapters via `AdapterMetrics`. Adapters that cannot measure them accurately report 0; they are not inferred by the harness.

---

## Type Checking

`basedpyright --project harness/` with `typeCheckingMode = "strict"` must pass. basedpyright is preferred over mypy for this codebase because it handles `typing.Protocol` structural subtyping more reliably — the `Adapter` protocol contract is exactly where mypy has known edge cases. Key implications:

- All `dict` annotations are fully parameterized: `dict[str, Any]` where the value type is heterogeneous, specific types where known. No unparameterized `dict` anywhere.
- `sessions` and `character_ids` use `tuple[..., ...]` so the type checker enforces non-mutation. The `dict` fields remain structurally mutable; this is documented above.
- `Adapter` is a `typing.Protocol` — runtime structural subtyping, no inheritance required. basedpyright validates conformance at the call site.
- `FixtureSolution | None` on `World.solution` must be narrowed before use.
- `TrialStatus` is an `Enum` — `to_dict()` serializes it as `.value`; no bare string comparisons in runner logic.
- No `# type: ignore` comments anywhere. `reportUnnecessaryTypeIgnoreComment = "warning"` catches any that creep in.
- `DTZ` ruff rule enforces `timezone.utc` on all `datetime.now()` calls, preventing naive datetime bugs in `observed_at`/`scored_at`.

---

## What This Design Deliberately Does Not Include

- No async — all adapters are synchronous; concurrency is left to the caller (parallel subprocesses if needed).
- No caching layer — `fixture_hash` is provided for callers to build caching on top; the harness itself always re-runs.
- No Docker orchestration — `needs_docker: true` adapters are simply skipped without `--include-docker`; Docker integration is left to a future extension.
- No web UI or live dashboard — `RunReport.print_summary()` is the only reporting surface.
