# companmem

Research on memory for realistic human and companion communication. Not another retrieve-then-speak RAG stack.

Most agent-memory products follow the same pipeline: extract facts, embed, retrieve, stuff into context, generate. That works for assistants. For companions it often falls short. Users care when something is recalled, how it is said, and whether the relationship still feels continuous after weeks. They do not usually judge the system on whether a fact was technically present in the prompt.

This repo is for figuring out what is missing, what the field might be getting wrong in parallel, and what would count as proof before we build anything at the root.

## What we're investigating

Memory is probably more than storage. We treat a complete system as having at least three layers:

| Layer | Role |
| --- | --- |
| Store | Persists state across sessions (facts, events, relationship history) |
| Reader | Decides what enters context this turn: selection, ordering, omission |
| Scaffold | System prompt, instructions, tools; tells the model how to use what it sees |

Retrieval can work and the interaction can still feel off: creepy timing, wrong intimacy, facts without relational knowing, lore mixed up with lived history. LoCoMo and similar benchmarks measure long-chat QA recall. They do not cover social timing, character consistency, or when silence is the right move.

First user, product goal, eval bar, and what to refuse to optimize for are still open. See [`docs/QUESTIONS.md`](docs/QUESTIONS.md).

## How we work

Research first. No product code at the repo root until groups of questions converge.

[`docs/QUESTIONS.md`](docs/QUESTIONS.md) is the source of truth. Questions are grouped by theme (definitions, human behavior, storage, evals, product scope). There is no fixed priority order yet. Answers are working notes with inline citations; we prefer primary sources (papers, specs, law) over blog posts. Each item gets a status tag: `settled`, `open`, or `deferred`. Settled answers need a stated falsifier. When an answer has downstream consequences, it can become an ADR in `docs/decisions/` (that directory does not exist yet).

Agent skills in [`.agents/skills/`](.agents/skills/) back this up: research, summarization, pressure-testing via `grill-with-docs`, ADR drafting, and [`companmem-research-gate`](.agents/skills/companmem-research-gate/SKILL.md), which enforces the gates above. Versions are pinned in [`skills-lock.json`](skills-lock.json).

## Repository layout

| Path | Purpose |
| --- | --- |
| [`docs/`](docs/) | Active research; start with `QUESTIONS.md` |
| [`research/`](research/) | Placeholder for future pipeline output (decisions, experiments) |
| [`sandbox/`](sandbox/) | Archived sprint 1: harness, eval fixtures, census, reference impl. Reference only. Do not extend in place. See [`sandbox/README.md`](sandbox/README.md). |
| [`.agents/skills/`](.agents/skills/) | Project agent skills, git-tracked |

## What this is not (yet)

- Not a shipped memory product or library
- Not a push for LoCoMo leaderboard scores alone
- Not a bet on one storage architecture (vector DB, graph, files, OS-style paging)

Sprint 1 in `sandbox/` built comparison harnesses and census work. That code stays for reference. It is not the active direction.

## Contributing / using agents

When working in this repo:

- Read `docs/QUESTIONS.md` before proposing architecture
- Cite sources; do not invent claims
- Do not commit unless asked
- Attach `companmem-research-gate` for research edits to `QUESTIONS.md`
