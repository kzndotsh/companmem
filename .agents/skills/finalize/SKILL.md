---
name: finalize
description: >-
  Use when finishing a chunk of work, before considering a task done, or
  when the user types /finalize, "wrap this up", "close the loop", or
  "run the post-change checks". Hygiene, test gaps, gates, then a
  conventional commit plan for approval. Do NOT trigger mid-implementation
  or when the user names one specific command (e.g. "run pytest").
metadata:
  owner: companmem
  sources: harness/pyproject.toml, pyproject.toml, mise.toml, .gitignore
---

# Finalize

Closes a work chunk so gates pass, then drafts grouped commits
and **stops for approval**.

## Outcomes

- **Clean** — close-out done; gates pass; commit plan posted; nothing committed.
- **Changed** — files were edited to close the chunk; list them.
- **Committed** — only after explicit approval; list SHAs.
- **Blocked** — gate failure or missing tests; report verbatim and stop.

## Edit scope

May edit tests for the dirty behavior, `fixture.json` hygiene, and files
a failing gate points at. May `git commit` only after the user approves
the posted plan. Does not push or change gate config unless asked.

## Instructions

1. List dirty paths (`git status --porcelain`; add `git diff --name-only` if needed).
2. Load [close-out.md](references/close-out.md) and apply hygiene, test-gap, and fixture metadata checks on those paths.
3. Docs: patch `docs/BUILDING.md` only if a CLI flag, adapter entry, or fixture schema field changed. Read the file before editing. No new docs unless asked.
4. Touch `.kiro/specs/` only if a spec is still in-progress and the diff contradicts a stated requirement.
5. Run gates in order — fastest first. On failure: read the error, fix, rerun that gate. Same gate still failing after one fix → **Blocked**.

   | Gate | Command | Pass condition |
   |------|---------|----------------|
   | Lint | `.venv/bin/ruff check harness/ tests/` | zero errors |
   | Types | `.venv/bin/python -m basedpyright` | 0 errors (warnings ok) |
   | Tests | `.venv/bin/python -m pytest tests/ -q` | ≥75 passed, 0 failed |
   | Smoke | `.venv/bin/python -m harness run --baseline oracle` | 9/9 PASS |

   Run the smoke gate only if `evals/fixtures/`, `harness/scorer.py`, `harness/runner.py`, or `harness/world.py` is dirty. Skip it otherwise.

6. Load [commit-plan.md](references/commit-plan.md), review **all** uncommitted work, draft the grouping, post it, and **stop**.
7. On explicit approval only, execute that plan (or the user's edited version).

## Gotchas

- Always use `.venv/bin/python` (or `.venv/bin/ruff`, `.venv/bin/pytest`) — never the system python. mise manages the venv at the repo root.
- basedpyright must be run as `basedpyright --project harness/` — not per-file. It will not find `pyproject.toml` config otherwise.
- `evals/results/` is gitignored — never stage or commit anything from it.
- `.kiro/specs/*/` `.spec-state.json` files are internal Kiro state — only commit them if spec work is the explicit focus of the chunk.
- `pytest` requires `pytest-socket` installed; if the venv is fresh, run `.venv/bin/pip install -e "harness/[dev]"` first.
- No `--no-verify`, `--amend`, or push unless the user explicitly asks.
- Do not start this while implementation is still in progress.
- Do not run a repo-wide docs or refactor pass; stay on the dirty set.
