# Close-out checks

Load this when: running `/finalize` after a work chunk — hygiene, test
gaps, and scoped doc accuracy. Not a full-repo audit.

## Hygiene (dirty files only)

- No leftover debug prints, commented-out blocks, or unused imports ruff
  would catch after `ruff check`.
- No new `Any`, type ignores, or `cast` to silence basedpyright. Use
  `Type | None`, not `Optional[Type]`. No inline imports outside `TYPE_CHECKING`.
- No file over 400 lines; split rather than land bloat.
- Stay in the requested scope — no drive-by refactors.
- Do not add a `CHANGELOG.md`; this repo does not keep one.
- After gates pass, draft commits via [commit-plan.md](commit-plan.md);
  do not commit in the close-out turn.

## Tests (harness + evals)

Behavior change with no covering test → add one, or report **Blocked**.

Test locations:
- Unit tests: `tests/test_<module>.py` (co-located with `harness/<module>.py`)
- Run: `.venv/bin/python -m pytest tests/`
- Count baseline: 75 tests as of the last clean commit; any change must
  not reduce that count

New tests: one behavior per test, assert contracts not call sequences.
If a gate fails: code bug → fix code; obsolete assertion → update the
test; unclear product → **Blocked**.

Fixture changes (under `evals/fixtures/`):
- If a predicate file changes, re-run `python -m harness run --baseline oracle`
  and confirm 9/9 PASS.
- If a fixture is renamed, confirm old name is absent from `tests/` grep.
- Do not require real adapter calls (mem0, letta, etc.) for close-out.

## Fixture metadata

If any `fixture.json` is added or modified:
- `id` must equal the directory name.
- `behavior` must be one of `b0`, `b1`, `b2`, `b3`, `b4`, `b5`, `b6`, `b7`, `b8`.
- `probe_type` must be one of: `appropriate-silence`, `user-state-update`,
  `claim-classification`, `stable-self`, `relational-continuity`,
  `character-isolation`.
- All fields must be non-empty strings.

## Docs (touched surfaces only)

If the diff changes a public CLI flag, adapter registry entry, fixture
schema field, or harness module API:
- Update the matching section in `docs/BUILDING.md` if the change affects
  the build/run workflow.
- Update `.kiro/specs/` tasks/design only if the spec is still in-progress
  and the change contradicts a stated requirement.
- Do not crawl all `docs/**`; stay on what the diff actually touched.
- Nested `AGENTS.md` changes only if Commands, Boundaries, or Gotchas
  actually changed.
