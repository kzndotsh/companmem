# Companion eval spec (unit 4)

Registered protocol. Freeze this before running named baselines. Do not HARKing after Mem0 numbers exist.

Heilmeier exam 8. Mid-term is these fixtures. Final exam is WORKFLOW.md's bakeoff.

## Goal

A third party can score a memory backend plus a frozen reader plus a prompt scaffold on companion holes, not on LoCoMo.

## Questions this spec answers

1. After 50+ sessions of user life, is the character still the character.
2. Do two companions on one backend leak.
3. Does lore stay lore, or become a lived memory.

Public fixtures cover holes **1–7, 9, 10** (all companion pass/fail holes except hole 8). Nine fixtures: `identity-50`, `joke-as-fact`, `typed-retcon`, `social-silence`, `cross-character-leak`, `lore-vs-lived`, `persona-poison`, `forget-that`, `three-month-reunion`. Hole 8 is a meter on every run, not a fixture.

## What a fixture is

Harbor-shaped. measured from https://www.harborframework.com/docs/tasks

| object | this spec |
| --- | --- |
| Task | `instruction.md` plus `environment/world/`. History and the next user line. No gold. |
| Agent | Unit 5. Named backend plus frozen reader. Unit 4 uses oracle and naive only. |
| Environment | Isolated files per character. No shared `user_id` bag in the world layout. |
| Verifier | Hidden `tests/predicates.json`. FAIL_TO_PASS and PASS_TO_PASS. Separate from the store. |

Oracle. `solution/solve.sh` copies a gold reply and a typed export. Proves the task is solvable.

Naive retrieve-then-speak. `research/evals/baselines/naive-retrieve/`. One user bag. Stuffs overlapping chunks into the reply. This is the shared failed premise as code. It is not Mem0.

## Scoring

FULL resolve requires every FAIL_TO_PASS and every PASS_TO_PASS. Infra (missing artifacts) is unresolved, not a memory loss.

The score is the next in-situ reply plus the store export. Do not ask "what is my dog's name?" as the grade.

Cost (hole 8). Unit 5 records `tokens_in`, `tokens_out`, `export_tokens_approx`, and `wall_ms` per trial. The report adds a per-baseline `cost` block and optional `cost_flags` when a trial exceeds `registry.json` `cost_budgets`. Cost does not change memory pass/fail on the nine fixtures.

## Kill criteria

Kill a fixture if any of these hold.

- The next user line is a disguised LoCoMo probe.
- The instruction contains the gold reply or the hidden must-not list framed as the exam.
- The oracle cannot pass.
- Naive retrieve-then-speak passes every predicate. The exam is too weak.
- A human marks it narrow (requires one phrasing) or wide (checks unstated extras). OpenAI 2026 SWE-bench Verified audit.

## Contamination

Public set is these seven. Held-out variants may exist later. Do not publish every transcript into a vendor training dump.

## Unit 4 check

```
python3 research/_contracts/validate-fixtures.py
python3 research/_contracts/run-oracles.py
```

Oracle PASS on all nine. Naive FAIL on all nine. That is the mid-term. "Fails today's best-fit baseline" is unit 5.

## Unit 5 harness

One command.

```
python3 research/_contracts/validate-harness.py
python3 research/harness/run.py --baseline local
```

`--baseline all` includes adapter stubs (status `skipped` until installed). `--docker` runs script baselines through `research/harness/docker/` so the agent never sees `predicates.json`.

Report lands in `research/evals/results/<timestamp>-<git-sha>.json`. Tokens are approximate for script baselines until a frozen reader model is wired.

Mem0 adapter (`research/harness/adapters/mem0.py`) uses local HuggingFace embeddings, `infer=False` ingest, per-`agent_id` isolation, retrieve-then-speak reply. Optional deps in `research/harness/requirements.txt`.

Sketch A uses `research/harness/readers/frozen.py`. Policy fallback by default. Set `COMPANMEM_READER_MODEL` and `OPENAI_API_KEY` for a frozen OpenAI reader on the same typed store export.

## Unit 5 must not change

Predicate files. Next user lines. Gold tokens. Isolation layout. If a baseline needs a different export schema, adapt the harness adapter, not the exam.
