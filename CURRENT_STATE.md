# Current state

Overwrite this file each session. The audit TSV is the log. This is the snapshot.

- Date. 2026-09-11
- LLM. Kiro gateway (`.env` auto-loaded). No OpenAI.
- Scoreboard. `research/evals/BAKEOFF.md` from `2026-09-11T203346Z-merged-scoreboard.json`.

## Public fixture matrix (9 scenarios)

| baseline | resolved | notes |
| --- | --- | --- |
| oracle | 9/9 | upper bound |
| naive-retrieve / naive-rag / long-context-stuff | 0/9 | retrieve-then-speak family |
| mem0 (per agent_id) | 2/9 | cross-character-leak, social-silence |
| mem0-shared-bag | 1/9 | fails hole 5 |
| graphiti | 1/9 | cross-character-leak PASS; Kiro + Neo4j |
| letta (MemFS sim) | 1/9 | cross-character-leak PASS |
| honcho (sim) | 1/9 | cross-character-leak PASS |
| st-world-info (sim) | 2/9 | cross-character-leak, social-silence |
| companmem + sketches | 9/9 | reference impl |

## Harness

- `--baseline comparison` — mem0, graphiti, local baselines (Neo4j + Kiro for Graphiti).
- All external baselines now have runnable simulation adapters (no vendor servers).
- `merge_reports.py` overlays baseline rows into a scoreboard report.
- CI: contracts, oracles, script baselines + letta/honcho/st-world-info + companmem.

## Not done

- Live vendor server adapters (Letta/Honcho APIs) optional.
- Multi-month simulation, hole-8 cost curve fixture.
- Fresh single-shot `--baseline comparison` run (current scoreboard uses merged reports).

## Freeze

Public fixture predicates are frozen. Adapt harness and candidates, not the exam.
