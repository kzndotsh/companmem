# Commit plan

Load this when: `/finalize` gates are clean and uncommitted work
remains — draft grouped conventional commits, then stop for approval.

## Review

Read all uncommitted work before grouping: `git status --porcelain`,
`git diff` (unstaged + staged), `git diff --cached`, and
`git log -15 --format='%s'` for this repo's subject style.

Include untracked files. Exclude secrets (`.env*`, credentials, keys).

## Grouping (more commits, not fewer)

Each commit is one reviewable concern. Prefer splitting over a blob.

Keep together: a harness module + its tests; a fixture directory + its
`fixture.json`; a spec change with the code that implements it.

Split: harness core vs adapter stubs; fixture data vs predicate changes;
`fix` vs `feat`; docs-only vs product; tooling/config vs app code.

Assign **whole files** to a commit. Do not `git add -p` or `git add -i`.
If one file mixes two concerns, put it with the later consumer and note
that in the plan, or ask.

Order: dependencies first (world/artifacts → scorer → trial → runner →
adapters → fixtures → docs/specs).

## Message

Conventional: `type(scope): subject`

Types: `feat` `fix` `docs` `refactor` `test` `chore` `ci` `perf`.

Scopes used in this repo:
- `harness` — any file under `harness/`
- `evals` — any file under `evals/fixtures/`
- `tests` — test-only changes under `tests/`
- `specs` — `.kiro/specs/` changes
- omit scope for cross-cutting (tooling, gitignore, mise.toml)

Subject: imperative, lowercase after the colon, no trailing period,
~72 chars. Body (when needed): why, not a file list. No emojis.

Do not invent `CHANGELOG.md`.

## Approval gate

Post the plan as a numbered list: files, proposed message (subject +
body if needed). **Stop. Do not run `git commit`.**

Commit only on an explicit yes in a later turn (`commit that`, `lgtm`,
`approved`, edits to the plan). Re-read status before executing — if
the tree changed, re-draft and stop again.

## Execute (after approval only)

User git protocol: `git status`, `git diff`, `git log -15 --format='%s'`
in parallel, then for each approved commit: `git add` those paths,
`git commit -m "..."`. No `--no-verify`, `--amend`, or push unless
explicitly asked.
After the last commit, `git status` and report SHAs.
