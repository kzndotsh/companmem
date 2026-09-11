# companmem

Find the missing secret sauce for **agent memory that feels like a real relationship** — not a search box stapled to a chat window.

## The actual goal

**Memory ≠ context.** Context is what fits in the active window this turn. Memory is what persists across weeks and months of sessions: who you are to each other, what changed, what was a joke, what must never be said unprompted, and what got revoked.

Almost every product in this space (Mem0, Zep/Graphiti, Letta, Honcho, RAG bags, vector stores) converges on the same move: **extract facts → embed → retrieve → stuff the prompt**. Vendors benchmark that loop on LoCoMo and LongMemEval. Companion users still report the same failures after months: wrong voice, creepy recall timing, jokes turned into lore, poisoned writes, cross-character leaks, no sense of time away.

This repo exists because **claims without automated evals are hearsay**. The program:

1. **Census** every serious player (papers, products, MCP servers) with a companion-memory rubric.
2. **Audit** existing benchmarks for what they actually score — and what they miss.
3. **Run the same transcripts** through named baselines and candidate designs in one harness.
4. **Score companion-specific holes** that retrieval QA never touches: write policy, read policy, ontology, isolation, poisoning, forget-that, reunion gaps, cost per turn.
5. **Simulate long arcs** (fixtures today; multi-month simulation is the direction) and measure drift, hallucination, and latency — memory has to feel instant, not "hold on while I search."

The north star is not a leaderboard number on someone else's bench. It is a **reproducible bakeoff** — `git sha`, dated artifact, same command for Mem0, Graphiti, naive RAG, and our design — where the winner still feels like the same person after a three-month gap without leaking another character's secrets.

LoCoMo stays in the census as a **baseline others optimize**. Beating it does not mean you solved companion memory. Mem0 can look fine on LoCoMo and score 2/9 here.

## What we test (nine public holes)

Identity drift, social silence, joke-as-fact, retcon/supersession, cross-character isolation, lore vs lived experience, persona poisoning, forget-that, reunion gap calibration, plus cost meters. See [`research/evals/SPEC.md`](research/evals/SPEC.md).

## Failed premise under test

> If we retrieve the right past text into the prompt, the model will act as if it remembers the relationship.

Most of the field assumes that sentence. This repo is built to break it — or prove a design that doesn't.

## Current score

| Layer | Result |
| --- | --- |
| Public fixtures (9) | **companmem 9/9** |
| Oracle solvability | 9/9 PASS |
| Naive retrieve-then-speak | 0/9 (expected) |
| Mem0 (per-`agent_id`) | 2/9 |
| Kiro frozen reader | 9/9 |
| Kiro LLM extract (no fallback) | 9/9 |

Latest numbers and matrix: [`research/evals/BAKEOFF.md`](research/evals/BAKEOFF.md).

## Quick start

```bash
# Python 3.11+
pip install httpx
pip install -r research/harness/requirements.txt   # mem0, graphiti, etc. as needed

cp .env.example .env                             # Kiro gateway (no OpenAI required)

# Unit 4 — fixtures are solvable, naive baseline fails
python3 research/_contracts/run-oracles.py

# Full local bakeoff
python3 research/harness/run.py --baseline local
python3 research/harness/summarize_bakeoff.py
python3 research/harness/write_bakeoff.py

# Extract / reader bakeoffs (gateway must be up)
python3 research/harness/run_frozen_reader.py
python3 research/harness/run_llm_extract.py

# Held-out fixture (not in public index)
python3 research/harness/run_held_out.py

# Package tests
python3 tests/test_extract.py
```

### LLM backend

Defaults to the **Kiro gateway** (same env as the gang.guide pipeline): set `KIRO_GATEWAY_URL` and `KIRO_GATEWAY_API_KEY` in `.env`. Heuristic ingest works without a gateway; frozen reader and LLM extract need it.

```bash
COMPANMEM_EXTRACT_BACKEND=heuristic   # default — fast, deterministic ingest
COMPANMEM_EXTRACT_BACKEND=llm         # Kiro extract + write gate
```

### Optional: Graphiti baseline

```bash
docker compose -f research/harness/docker/neo4j-compose.yml up -d
python3 research/harness/run.py --baseline graphiti
```

## Repository layout

```
companmem/              Reference implementation (typed atoms, ingest, read policy)
research/
  _contracts/           Fixture schemas, grader, oracle runner, validators
  census/               Player cards, gap map, paper slices
  evals/
    fixtures/           Nine public fixtures + held-out persona-poison-alt
    baselines/          naive-retrieve, naive-rag, long-context-stuff
    BAKEOFF.md          Generated scoreboard
  harness/              run.py, adapters (mem0, graphiti, companmem, …), readers
  papers/               registry.json, vendored arxiv extracts
  protocol/SPEC.md      Memory protocol (unit 7)
tests/                  Write-gate and extract tests
WORKFLOW.md             Program playbook and unit order
CURRENT_STATE.md        Session snapshot (overwrite each session)
```

## Memory model (sketch)

Records are typed, not chunks:

| Kind | Example |
| --- | --- |
| `user_bio` | User works at the clinic |
| `character_event` | Mara lost her eye in a survey accident |
| `relationship_phase` | Settled companionship; three-month gap |
| `lore` | Flood of 1847 (author-canonical) |
| `session` | Working memory for this turn |
| `ooc` | Jailbreak text, revocations — never IC recall |

**Read policy ≠ retrieval score.** Silent facts stay stored but do not surface unless the user frames the topic. OOC is quarantined. Per-character compartments prevent cross-leak.

Implementation: append-only atoms → read-time projection → frozen reader. See [`research/protocol/SPEC.md`](research/protocol/SPEC.md).

## Baselines

| ID | Status |
| --- | --- |
| `naive-retrieve`, `naive-rag`, `long-context-stuff` | Local scripts |
| `mem0`, `mem0-shared-bag` | HuggingFace embedder, per-`agent_id` isolation |
| `companmem`, `companmem-sketch-a/b` | Typed memory sketches |
| `graphiti` | Neo4j + Kiro episode extract |
| `letta`, `honcho`, `st-world-info` | Stubs — see [`research/harness/adapters/README.md`](research/harness/adapters/README.md) |

Registry: [`research/harness/registry.json`](research/harness/registry.json).

## Contributing

Public fixture **predicates are frozen**. If a design fails a hole, fix ingest/read policy or the harness — not the exam.

1. Read [`WORKFLOW.md`](WORKFLOW.md) for unit order.
2. Run `python3 research/_contracts/run-oracles.py` before and after changes.
3. Refresh bakeoff: `run.py --baseline local` → `write_bakeoff.py`.

## License

Not specified yet. Census cards cite upstream licenses per player.
