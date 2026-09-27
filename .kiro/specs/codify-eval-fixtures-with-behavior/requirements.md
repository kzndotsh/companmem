# Requirements: Codify Eval Fixtures with Behavior Metadata

## Overview

The eval harness at `harness/` currently works with 9 fixture directories whose names do not convey the research behaviors they test, and whose `fixture.json` files carry a loose, undocumented schema. This feature:

1. Renames all 9 fixture directories to a `b{N}-{scenario}` convention tied to `docs/BEHAVIORS.md`.
2. Replaces each fixture's `fixture.json` with a self-describing schema that captures what the test proves and why a naive retriever fails it.
3. Adds a `FixtureMeta` dataclass to the runner so the harness can read and act on that metadata at run time.
4. Adds a `--behavior <id>` filter to `python -m harness run` so a developer can run only the fixtures for one behavior.
5. Adds a `behavior: str | None` field to `TrialResult` and groups the summary table by behavior.

The harness's correctness — oracle passing all 9, naive-retrieve failing all 9 — is preserved exactly. No predicate files, world files, session history, gold solutions, adapter code, or scorer logic is changed.

---

## User Stories

### US-1 — Fixture names convey behavior

**As a** developer reading the eval output,  
**I want** each fixture directory name to start with the behavior code it tests,  
**so that** I can tell at a glance which research behavior a test targets without opening any file.

**Acceptance criteria:**

- AC1-1: The 9 fixture directories under `evals/fixtures/` are renamed according to the mapping in the design document. No other directories under `evals/fixtures/` are renamed, created, or deleted.
- AC1-2: All existing sub-contents of each renamed directory (`environment/`, `tests/`, `solution/`, `instruction.md`, `task.toml`) are preserved bit-for-bit.
- AC1-3: `python -m harness run --baseline oracle` completes with all 9 fixtures `TrialStatus.OK` and `resolved=True`.
- AC1-4: `python -m harness run --baseline naive-retrieve` completes with all 9 fixtures `TrialStatus.OK` and `resolved=False`.

---

### US-2 — Fixture self-describes what it tests

**As a** developer reading a fixture's `fixture.json`,  
**I want** the file to tell me: which behavior it tests, what a passing result proves, what a failing result reveals, and why a naive retriever is expected to fail,  
**so that** I can understand the test's purpose without reading the predicate file or the world.

**Acceptance criteria:**

- AC2-1: Every `fixture.json` in all 9 renamed fixture directories contains exactly the fields defined in the schema below and no others. All fields are non-empty strings.
- AC2-2: The `id` field equals the directory name.
- AC2-3: The `behavior` field is one of `b0`, `b1`, `b3`, `b5`.
- AC2-4: The `probe_type` field is one of: `appropriate-silence`, `user-state-update`, `claim-classification`, `stable-self`, `relational-continuity`, `character-isolation`.
- AC2-5: The legacy fields `hole`, `visibility`, `active_character_id`, `next_user`, `human_check` are absent from all 9 files.

**fixture.json schema:**

```json
{
  "id": "<new directory name>",
  "behavior": "<b0|b1|b3|b5>",
  "title": "<one sentence>",
  "description": "<2-3 sentences: what the history establishes, what the probe is, what must happen>",
  "probe_type": "<one of: appropriate-silence | user-state-update | claim-classification | stable-self | relational-continuity | character-isolation>",
  "pass_proves": "<one sentence: what passing demonstrates about the system>",
  "fail_reveals": "<one sentence: what failing reveals about the system's failure mode>",
  "why_naive_fails": "<one sentence: why naive-retrieve or naive-rag is expected to fail this>"
}
```

---

### US-3 — Runner loads fixture metadata

**As a** developer extending the harness,  
**I want** the runner to load `fixture.json` into a typed `FixtureMeta` dataclass for each fixture before running it,  
**so that** downstream code (filters, summary output) can use the metadata without re-parsing JSON.

**Acceptance criteria:**

- AC3-1: `harness/runner.py` exports a `FixtureMeta` frozen dataclass with exactly these fields: `id: str`, `behavior: str`, `title: str`, `description: str`, `probe_type: str`, `pass_proves: str`, `fail_reveals: str`, `why_naive_fails: str`.
- AC3-2: A `load_fixture_meta(fixture_dir: Path) -> FixtureMeta | None` function is present in `harness/runner.py`. It returns `None` if `fixture.json` is absent or malformed; it does not raise.
- AC3-3: `FixtureMeta` is not passed to adapters. `harness/world.py` and adapter files are not modified.
- AC3-4: `pytest tests/` passes 69 tests (plus any new tests for `FixtureMeta`). `tests/test_runner.py` includes unit tests for behavior filtering logic analogous to the existing `test_single_fixture_filter`: at minimum, (a) filter returns the correct fixture subset when `--behavior` matches, (b) filter returns an empty list when no fixture has the requested behavior, and (c) combining `--behavior` and `--fixture` is detected as an error.

---

### US-4 — Filter run by behavior

**As a** developer iterating on a specific behavior,  
**I want** to run `python -m harness run --baseline <id> --behavior <b0|b1|b3|b5>` and have only the fixtures for that behavior execute,  
**so that** I get fast feedback on one behavior without waiting for all 9.

**Acceptance criteria:**

- AC4-1: `python -m harness run --baseline oracle --behavior b5` runs exactly 2 fixtures (`b5-silence-on-casual-invite`, `b5-firing-stays-isolated`), both resolving `True`.
- AC4-2: `python -m harness run --baseline oracle --behavior b0` runs exactly 4 fixtures, all resolving `True`.
- AC4-3: `python -m harness run --baseline oracle --behavior b1` runs exactly 1 fixture, resolving `True`.
- AC4-4: `python -m harness run --baseline oracle --behavior b3` runs exactly 2 fixtures, both resolving `True`.
- AC4-5: If `--behavior` is given and no fixture has that behavior, the command prints a clear error message to stdout and exits with return code `1`.
- AC4-6: The existing `--fixture <id>` filter continues to work unchanged.
- AC4-7: `--behavior` and `--fixture` may not be combined. If both are supplied, the command prints an error and exits with return code `1`.

---

### US-5 — Summary grouped by behavior

**As a** developer reading the run summary,  
**I want** the results table grouped under behavior headers when behavior metadata is present,  
**so that** I can see at a glance how the system performs on each behavior.

**Acceptance criteria:**

- AC5-1: `TrialResult` has a field `behavior: str | None`. Default is `None` for backwards compatibility. `to_dict()` includes `"behavior"` and `from_dict()` reads it with `d.get("behavior")`.
- AC5-2: When `python -m harness run` is called, each `TrialResult` produced has `behavior` set to the value from the fixture's `FixtureMeta` (or `None` if `FixtureMeta` could not be loaded). `_run_trial()` accepts an optional `behavior: str | None` parameter populated by the caller from `FixtureMeta` before the call.
- AC5-3: `print_summary()` groups rows under behavior headers when any trial carries a non-`None` `behavior`. The header format is:

  ```
  ── b0: stable self ──────────────────────────────────────
  ── b1: relational texture ───────────────────────────────
  ── b3: knows who you are now ────────────────────────────
  ── b5: appropriate silence ──────────────────────────────
  ── (no behavior) ────────────────────────────────────────
  ```

  Trials with `behavior=None` fall into the `(no behavior)` group, printed last. The `(no behavior)` group is omitted if no such trials exist. When multiple baselines are present, rows within each behavior group are sorted by `(baseline_id, fixture_id)`, so the table structure is always behavior → baseline × fixture (never baseline → behavior → fixture).
- AC5-4: If all trials have `behavior=None`, `print_summary()` behaves identically to today — flat list, no group headers.

---

## AC6 — Lint clean

- AC6-1: `ruff check harness/ tests/` reports zero errors after all changes are applied.

---

## Out of Scope

- `evals/fixtures/*/environment/` — world files, sessions, lore, character sheets are not touched.
- `evals/fixtures/*/tests/predicates.json` — predicate files are not touched.
- `evals/fixtures/*/solution/` — gold files are not touched.
- `harness/scorer.py`, `harness/artifacts.py`, `harness/adapter.py`, `harness/world.py` — not changed (beyond import updates if the rename causes any import path changes, which it should not).
- `evals/fixtures/*/instruction.md` and `task.toml` — not changed.
- The `rescore` path in `RunReport.rescore()` — reads `behavior` from the stored JSON trial dict via `d.get("behavior")` through `from_dict()` into `orig_trial.behavior`, then must explicitly pass `behavior=orig_trial.behavior` when constructing the new `TrialResult` at the end of the rescore loop. Without this, `behavior` is silently dropped and all grouped summaries break for rescored reports.
