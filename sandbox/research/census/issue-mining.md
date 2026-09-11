# Issue and feedback mining

Cards score what vendors **ship**. Issues score where they **break in the wild**.

Census slice I. Optional. Run after unit 5 harness exists. Do not block sketch work on this finishing.

## Why

READMEs and LoCoMo leaderboards hide companion failures. Users report them as GitHub issues, discussions, Reddit threads, and app-store reviews. Those are primary signals for holes 2, 7, 8, 9, and 10.

## Scope

Every `kind` in `agent-memory-lib`, `memory-os`, `temporal-graph`, `companion-native`, `roleplay-client` from `research/_contracts/PLAYER-LIST.md`. Skip pure `eval-benchmark` and `academic` unless the issue is about memory in production.

Closed apps (Kindroid, Nomi, Character.AI, Replika). Official help docs and public status pages only. Mark internals `INCONCLUSIVE`. No scraper dumps.

## Sources, in order

1. GitHub Issues and Discussions on the canonical repo. Label filters: `bug`, `memory`, `regression`.
2. Closed issues with maintainer replies that admit a limitation.
3. PR review threads that reject a design for a stated reason.
4. Vendor community forums only when they link a reproducible report.

Do not treat SEO listicles or "top 10 memory tools" as sources.

## What to extract per report

| field | content |
| --- | --- |
| `player_id` | census card id |
| `source_url` | issue or discussion permalink |
| `observed_at` | date you read it |
| `user_symptom` | what the human experienced, in their words |
| `hole` | which of the ten companion holes (1–10), or `none` |
| `dimension` | rubric dimension if obvious (`silence`, `poisoning`, …) |
| `label` | `measured` if maintainer confirmed; `inferred` if you mapped symptom to hole; `guess` otherwise |
| `fixture_idea` | one sentence if this could become a harness case |
| `steal_or_avoid` | mechanism to copy or failure mode to make illegal |

## Output

One file per player.

`research/census/issue-signals/<player-id>.md`

End each file with a table. Link new rows in `research/census/GAP-MAP.md` under **Field failure signals** when a hole gains evidence.

Do not edit JSON cards unless a primary source changes a dimension score. Issue mining feeds fixtures and gap map, not card churn.

## Search prompts

Use these when skimming issues.

- forget / deleted / still remembers / brought up unprompted
- wrong character / other bot / leaked / shared memory
- lore / world info / canon / contradicted
- persona / jailbreak / system prompt / overwritten
- expensive / slow / tokens / context window
- OOC / meta / out of character
- after N sessions / long term / drift

## Done check

Slice I is `VERIFIED` for a player when `issue-signals/<id>.md` exists with at least three labeled rows or an explicit `no public signal` with the search you ran.

Priority queue for mining (holes still weak in public evals).

1. mem0, letta, graphiti, honcho
2. sillytavern, memobase, hindsight
3. closed companion apps with public help docs

## Not a substitute for the harness

An issue that says "it forgot my name" is not a passing fixture. Mine issues to **propose** predicates. Humans still confirm hole 2 is silence, not forgetfulness, before freeze.
