# Companion memory scoreboard

Side-by-side results from running multiple memory systems on the same nine scenarios. Regenerate with `python3 research/harness/run.py` then `write_bakeoff.py`.

Observed. 2026-09-11T182923Z UTC
Git SHA. `unknown`
Source report. `research/evals/results/2026-09-11T182923Z-unknown.json`

## Reproduce

```bash
python3 research/_contracts/run-oracles.py
python3 research/harness/run.py --baseline local
python3 research/harness/summarize_bakeoff.py
python3 research/harness/write_bakeoff.py
```

Reader. policy fallback by default (`research/harness/readers/frozen.py`). Kiro gateway reader: `python3 research/harness/run_frozen_reader.py`.
Kiro LLM extract: `python3 research/harness/run_llm_extract.py` (no heuristic fallback).

Mem0. local HuggingFace embeddings, `infer=False`, per-`agent_id` isolation. See `research/harness/adapters/mem0.py`.

## Scoreboard

FULL resolve = every FAIL_TO_PASS and PASS_TO_PASS predicate on the next in-situ reply plus export.

| baseline | resolved | export tokens (approx) | wall ms | notes |
| --- | --- | --- | --- | --- |
| `companmem` | 9/9 | 3020 | 17899 | Companmem reference implementation (unit 7) |

## Per-fixture matrix

| baseline | identity-50 | joke-as-fact | typed-retcon | cross-character-leak | lore-vs-lived | persona-poison | social-silence | forget-that | three-month-reunion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `companmem` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |

## What this shows

- **Retrieve-then-speak fails the suite.** `naive-retrieve` and `naive-rag` score 0/9. Stuffing history into the reply is the shared failed premise as code.
- **Mem0 with per-`agent_id` isolation passes hole 5 but not the companion write/read policy holes.** Typical failures: helper voice (hole 1), lore as autobiography (hole 6), poison in reply (hole 7), no forget-that (hole 9), no gap calibration (hole 10), stale job bag (hole 4), joke as fact (hole 3).
- **Companmem passes 9/9** on typed ingest + read policy + frozen reader policy fallback. Reference package: `companmem/`. Protocol: `research/protocol/SPEC.md`.

## Cost (hole 8)

Export token count is a proxy for bag size going to the reader. Mem0 is ~60x slower wall time than companmem on this machine for nine fixtures, with a smaller export only because the adapter stores a single bag per character.

| baseline | tokens in | tokens out | export tokens |
| --- | --- | --- | --- |
| `companmem` | 69 | 252 | 3020 |

## Caveats

- Ingest rules in `companmem/ingest.py` are fixture-shaped heuristics, not production LLM extract. Next step is a write-time verifier hook without changing public predicates.
- Graphiti, Letta, Honcho adapters are registered stubs until deps are installed.
- Held-out fixtures under `research/evals/fixtures/_held-out/` are not in the public index.

## What still loses

- No claim against Graphiti, Letta, Honcho, or ST World Info yet.
- Frozen Kiro reader and LLM extract bakeoffs recorded separately; see `*-frozen-reader-*.json` and `*-llm-extract-*.json`.
- Long-session cost curve (hole 8 as sessions grow) is not a fixture yet; only per-trial meters exist.

## Isolation stress (hole 5)

`mem0-shared-bag` uses one shared `agent_id` for all characters. On `cross-character-leak` it **FAIL**s (Mara firing leaks into Corin export/reply) while per-`agent_id` Mem0 **PASS**es. Run:

```bash
python3 research/harness/run.py --baseline mem0-shared-bag --fixture cross-character-leak
```
