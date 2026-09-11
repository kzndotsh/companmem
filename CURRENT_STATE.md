# Current state

Overwrite this file each session. The audit TSV is the log. This is the snapshot.

- Date. 2026-09-11
- LLM. Kiro gateway (`.env` auto-loaded). No OpenAI.
- Comparison run. `2026-09-11T201041Z-96d88cc2.json` (`--baseline comparison`, git `96d88cc`).
- Scoreboard. `research/evals/BAKEOFF.md` (regenerated from comparison report).

## Public fixture matrix (9 scenarios)

| baseline | resolved | notes |
| --- | --- | --- |
| oracle | 9/9 | upper bound |
| naive-retrieve | 0/9 | retrieve-then-speak |
| naive-rag | 0/9 | top-k chunks |
| long-context-stuff | 0/9 | stuff full world |
| mem0 (per agent_id) | 2/9 | passes cross-character-leak, social-silence |
| mem0-shared-bag | 1/9 | fails hole 5; passes social-silence only |
| graphiti | 1/9 | cross-character-leak PASS; JSON retry + embedder cache; ~703s wall |
| companmem-sketch-a | 9/9 | typed memory sketch |
| companmem-sketch-b | 9/9 | append-only atoms sketch |
| companmem | 9/9 | reference impl |

## Other verified runs

- Kiro frozen reader. 9/9 (`run_frozen_reader.py`).
- Kiro LLM extract (no heuristic fallback). 9/9 (`run_llm_extract.py`).
- Held-out `persona-poison-alt`. oracle PASS, naive FAIL, companmem PASS (`run_held_out.py`).

## Harness changes this session

- `--baseline comparison` = local baselines + `mem0-shared-bag` + `graphiti`.
- Per-trial `Exception` caught as `infra_error` so one adapter failure does not abort the run.
- Graphiti Kiro JSON parse/retry (gang.guide pattern), 300s timeout, embedder singleton.
- Live per-fixture progress logging in harness.

## Stubs / not done

- Letta, Honcho, ST World Info adapters.
- CI workflow added (`.github/workflows/ci.yml`): contracts, oracles, unit tests, script baselines + companmem. Mem0/Graphiti need local run with deps + Kiro + Neo4j.
- Multi-month simulation, hole-8 cost curve as sessions grow.

## Freeze

Public fixture predicates are frozen. Adapt harness and candidates, not the exam.
