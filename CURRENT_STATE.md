# Current state

Overwrite this file each session. The audit TSV is the log. This is the snapshot.

- Date. 2026-09-11
- LLM. Kiro gateway (`.env` auto-loaded). No OpenAI.
- Scoreboard. `research/evals/BAKEOFF.md` from `2026-09-11T203204Z-merged-scoreboard.json`.

## Public fixture matrix (9 scenarios)

| baseline | resolved | notes |
| --- | --- | --- |
| oracle | 9/9 | upper bound |
| naive-retrieve / naive-rag / long-context-stuff | 0/9 | retrieve-then-speak family |
| mem0 (per agent_id) | 2/9 | cross-character-leak, social-silence |
| mem0-shared-bag | 1/9 | fails hole 5 |
| graphiti | 1/9 | cross-character-leak PASS; Kiro + Neo4j |
| letta (MemFS sim) | 1/9 | cross-character-leak PASS; no server |
| companmem + sketches | 9/9 | reference impl |

## Harness

- `--baseline comparison` — full public scoreboard (Neo4j + Kiro for Graphiti).
- Graphiti: JSON retry, embedder singleton, live progress logging.
- Letta: MemFS simulation adapter (`research/harness/lib/letta_memfs.py`).
- CI: `.github/workflows/ci.yml` (contracts, oracles, script baselines + letta + companmem).

## Stubs / not done

- Honcho, ST World Info adapters.
- Letta live server adapter (optional; simulation encodes MemFS read policy).
- Multi-month simulation, hole-8 cost curve fixture.

## Freeze

Public fixture predicates are frozen. Adapt harness and candidates, not the exam.
