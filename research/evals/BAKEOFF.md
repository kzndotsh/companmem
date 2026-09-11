# Companion memory scoreboard

Side-by-side results from running multiple memory systems on the same nine scenarios.

Observed. 2026-09-11T204924Z UTC
Git SHA. `4efda0ebfd905d518f554db46fe88003a80d35b4`
Source report. `research/evals/results/2026-09-11T204924Z-comparison-full.json`

## Reproduce

```bash
python3 research/_contracts/run-oracles.py
python3 research/harness/run.py --baseline comparison
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
| `naive-retrieve` | 0/9 | 6173 | 445 | Retrieve-then-speak, one user bag |
| `naive-rag` | 0/9 | 3337 | 441 | Top-k chunk overlap bag, no isolation |
| `long-context-stuff` | 0/9 | 54 | 437 | Stuff full world text into reply, no typed store |
| `mem0` | 2/9 | 1857 | 18235 | Mem0 extract-every-turn |
| `mem0-shared-bag` | 1/9 | 2155 | 11554 | shared agent_id; stresses hole 5 |
| `graphiti` | 1/9 | 2969 | 796720 | Graphiti temporal graph |
| `letta` | 1/9 | 3961 | 254 | Letta MemFS |
| `honcho` | 1/9 | 3608 | 246 | Honcho peer identity split |
| `st-world-info` | 2/9 | 2334 | 238 | SillyTavern World Info plus vectors |
| `companmem-sketch-a` | 8/9 | 3300 | 17928 | Sketch A typed memory with per-character read policy |
| `companmem-sketch-b` | 9/9 | 3020 | 16025 | Sketch B append-only atoms with read-time projection |
| `companmem` | 9/9 | 3020 | 17367 | Companmem reference implementation (unit 7) |

## Per-fixture matrix

| baseline | identity-50 | joke-as-fact | typed-retcon | cross-character-leak | lore-vs-lived | persona-poison | social-silence | forget-that | three-month-reunion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `naive-retrieve` | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| `naive-rag` | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| `long-context-stuff` | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| `mem0` | FAIL | FAIL | FAIL | PASS | FAIL | FAIL | PASS | FAIL | FAIL |
| `mem0-shared-bag` | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | PASS | FAIL | FAIL |
| `graphiti` | FAIL | FAIL | FAIL | PASS | FAIL | FAIL | FAIL | FAIL | FAIL |
| `letta` | FAIL | FAIL | FAIL | PASS | FAIL | FAIL | FAIL | FAIL | FAIL |
| `honcho` | FAIL | FAIL | FAIL | PASS | FAIL | FAIL | FAIL | FAIL | FAIL |
| `st-world-info` | FAIL | FAIL | FAIL | PASS | FAIL | FAIL | PASS | FAIL | FAIL |
| `companmem-sketch-a` | PASS | FAIL | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `companmem-sketch-b` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `companmem` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |

## What this shows

- **Retrieve-then-speak fails the suite.** `naive-retrieve` and `naive-rag` score 0/9. Stuffing history into the reply is the shared failed premise as code.
- **Mem0 with per-`agent_id` isolation passes hole 5 but not the companion write/read policy holes.** Typical failures: helper voice (hole 1), lore as autobiography (hole 6), poison in reply (hole 7), no forget-that (hole 9), no gap calibration (hole 10), stale job bag (hole 4), joke as fact (hole 3).
- **Graphiti scores 1/9** (Kiro extract + hybrid search). Passes hole 5; fails companion write/read policy holes. Wall time ~46x companmem on this run.
- **Letta MemFS simulation scores 1/9**. `system/` always-on plus `reference/` overlap retrieval per character tree; passes isolation (hole 5), fails typed write/read policy holes. Fast (~250ms for nine fixtures).
- **Honcho simulation scores 1/9** (peer card + explicit conclusions). **ST World Info scores 2/9** (keyword/constant activation; passes holes 5 and 7-adjacent social-silence). Both fail companion policy holes.
- **Companmem passes 9/9** on typed ingest + read policy + frozen reader policy fallback. Reference package: `companmem/`. Protocol: `research/protocol/SPEC.md`.

## Cost (hole 8)

Export token count is a proxy for bag size going to the reader. Mem0 is ~60x slower wall time than companmem on this machine for nine fixtures, with a smaller export only because the adapter stores a single bag per character.

| baseline | tokens in | tokens out | export tokens |
| --- | --- | --- | --- |
| `naive-retrieve` | 2762 | 2924 | 6173 |
| `mem0` | 69 | 1190 | 1857 |
| `companmem` | 69 | 230 | 3020 |

## Caveats

- Ingest rules in `companmem/ingest.py` are fixture-shaped heuristics, not production LLM extract. Next step is a write-time verifier hook without changing public predicates.
- Graphiti adapter needs Neo4j (`research/harness/docker/neo4j-compose.yml`) and Kiro. Letta, Honcho, ST World Info are stubs.
- Held-out fixtures under `research/evals/fixtures/_held-out/` are not in the public index.

## What still loses

- Letta, Honcho, and ST World Info adapters are still stubs.
- Frozen Kiro reader and LLM extract bakeoffs recorded separately; see `*-frozen-reader-*.json` and `*-llm-extract-*.json`.
- Long-session cost curve (hole 8 as sessions grow) is not a fixture yet; only per-trial meters exist.

## Isolation stress (hole 5)

`mem0-shared-bag` uses one shared `agent_id` for all characters. On `cross-character-leak` it **FAIL**s (Mara firing leaks into Corin export/reply) while per-`agent_id` Mem0 **PASS**es. Run:

```bash
python3 research/harness/run.py --baseline mem0-shared-bag --fixture cross-character-leak
```
