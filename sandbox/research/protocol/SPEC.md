# Companion memory protocol (unit 7 draft)

Status. Draft. Grounded in harness results. Sketch B selected as the write model; Sketch A remains a reference typed-store path.

## Decision record

```
python3 research/harness/compare_sketches.py --run
```

Both sketches pass 9/9 public fixtures. Sketch B wins on architecture fit, not pass rate alone.

| criterion | sketch A | sketch B |
| --- | --- | --- |
| pass rate | 9/9 | 9/9 |
| total export tokens (approx) | 3300 | 3020 |
| write model | direct typed buckets | append-only atoms + projection |
| hole 4 retcon | slot replace in bucket | slot supersession in log |
| audit trail | session kind only | full writer provenance |

## Problem

Retrieve-then-speak treats memory as one bag. Companion failure is write policy, identity split, silence, poisoning, supersession, and cost — not recall F1.

## Objects

### Atom (write unit)

Append-only. Never mutate prior atoms.

| field | role |
| --- | --- |
| `writer` | `user`, `character`, `narrator`, `session`, `system` |
| `slot` | supersession key for user facts (`job`, `nickel-allergy`, …) |
| `text` | canonical phrase stored |
| `compartment` | character id when fact is private to one companion |
| `silent` + `speak_if` | read policy hooks |
| `revoke_slot` | tombstone for forget-that |

### Write-time extract (before append)

Session lines pass through `companmem/extract.py`:

1. **Extract** — `SessionExtractor` proposes `AtomDraft` rows (`heuristic` default; `llm` stub).
2. **Verify** — `verify_draft()` rejects poison, jokes, and wrong-writer promotions.
3. **Commit** — approved drafts append to the atom log; rejects quarantine as `narrator` `rejected-extract`.

Set `COMPANMEM_EXTRACT_BACKEND=heuristic` (default) or `llm`. LLM extract uses Kiro (`COMPANMEM_EXTRACT_MODEL`, default `claude-sonnet-4.6`) and falls back to heuristic when `COMPANMEM_LLM_EXTRACT_FALLBACK=1` (default). Recorded bakeoff: `python3 research/harness/run_llm_extract.py`.

LLM backends (`companmem/llm_client.py`). Auto-prefers **Kiro** when `KIRO_GATEWAY_API_KEY` is set (same gateway as gang.guide: `POST {KIRO_GATEWAY_URL}/v1/messages`). Falls back to OpenAI.

```
# .env — see .env.example
KIRO_GATEWAY_URL=http://127.0.0.1:9000
KIRO_GATEWAY_API_KEY=...
COMPANMEM_LLM_BACKEND=auto
COMPANMEM_READER_MODEL=claude-sonnet-4.6
COMPANMEM_EXTRACT_BACKEND=llm

python3 research/harness/run_frozen_reader.py --model claude-sonnet-4.6
```

Writer rules (hole mapping).

- `user` — biographical facts. Same `slot` superseded by later user atoms.
- `character` — what the character claimed or lived. Never promoted to `user`.
- `narrator` — OOC, jokes, poison, forget markers. Never spoken in IC export.
- `session` — episodic transcript summary. Not permission to speak.
- `system` — character sheet, lore, relationship phase, calendar gap.

### Projection (read unit)

`project(atom_log) -> TypedExport` collapses the log into illegal-to-mix kinds:

`user_bio`, `character_event`, `relationship_phase`, `lore`, `session`, `ooc`

Export schema matches `research/evals/fixtures/*/solution/gold_memory_export.json`.

### Read policy

Separate from retrieval score.

- OOC never enters the frozen reader package.
- `silent` facts withheld unless `speak_if` triggers appear in `next_user`.
- `compartment` facts visible only to the owning character store.
- Poison (hole 7) quarantined at write (`writer=narrator`, poison markers).

Implementation. `research/harness/readers/frozen.py` + `allows_read()`.

### Frozen reader

Fixed model + prompt scaffold for bakeoff fairness. Policy fallback when no API key. Same reader across baselines when comparing backends.

## Per-character isolation

One atom log per `character_id`. No shared `user_id` bag. Cross-character export must not contain another companion's compartment facts (hole 5). Stress baseline: `mem0-shared-bag`.

## Cost (hole 8)

Harness records `tokens_in`, `tokens_out`, `export_tokens_approx`, `wall_ms` per trial. Report `cost` block per baseline. Budget flags in `registry.json` `cost_budgets`. Cost does not change memory predicates on public fixtures.

## Reference implementation map

| protocol piece | path |
| --- | --- |
| package | `companmem/` (`pyproject.toml`) |
| atoms + projection | `companmem/atoms.py` |
| extract + write gate | `companmem/extract.py` |
| ingest | `companmem/ingest.py` |
| read policy | `companmem/models.py` (`allows_read`, `may_speak_item`) |
| frozen reader hook | `companmem/session.py` |
| harness adapter | `research/harness/adapters/companmem.py` |

Sketch A (`sketch_a/memory.py`) remains for A/B regression. Sketch B is a thin wrapper over `companmem`.

## Out of scope (this draft)

- Production persistence, embedding index, or LLM extract-every-turn loop.
- LoCoMo-style probe QA as the grade.
- Persona files writable by chat ingest.

## Checks

```
python3 research/_contracts/run-oracles.py
python3 research/harness/run.py --baseline companmem
python3 research/harness/compare_sketches.py
python3 research/harness/summarize_bakeoff.py
```

Held-out fixtures under `research/evals/fixtures/_held-out/` are not in `fixture-ids.txt`. Run their `tests/test.sh` manually before bakeoff refresh.
