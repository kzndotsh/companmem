# Current state

Overwrite this file each session. The audit TSV is the log. This is the snapshot.

- Date. 2026-09-11
- LLM. Kiro gateway (`.env` auto-loaded). No OpenAI.
- Scoreboard. `research/evals/BAKEOFF.md` from `2026-09-11T204924Z-comparison-full.json` (single comparison run + sim overlay merge).

## Public fixture matrix (9 scenarios)

| baseline | resolved | notes |
| --- | --- | --- |
| oracle | 9/9 | upper bound |
| naive-retrieve / naive-rag / long-context-stuff | 0/9 | retrieve-then-speak family |
| mem0 (per agent_id) | 2/9 | cross-character-leak, social-silence |
| mem0-shared-bag | 1/9 | fails hole 5 |
| graphiti | 1/9 | cross-character-leak PASS; ~797s wall |
| letta / honcho | 1/9 each | MemFS / peer sim; hole 5 |
| st-world-info | 2/9 | holes 5 + social-silence |
| companmem-sketch-a | 8/9 | joke-as-fact FAIL this run (investigate) |
| companmem-sketch-b | 9/9 | |
| companmem | 9/9 | reference impl |

## Harness

- `--baseline comparison` includes all 13 runnable baselines (Graphiti needs Neo4j + Kiro).
- Live per-fixture progress logging; `merge_reports.py` for overlay merges.
- CI fast path (no mem0/graphiti).

## Not done

- sketch-a joke-as-fact flake on full comparison run.
- Multi-month simulation, hole-8 cost curve fixture.
- Live vendor server adapters (optional).

## Freeze

Public fixture predicates are frozen. Adapt harness and candidates, not the exam.
