# companmem

Research on memory for realistic human and companion communication. Not another retrieve-then-speak RAG stack.

Most agent-memory products follow the same pipeline: extract facts, embed, retrieve, stuff into context, generate. That works for assistants. For companions it often falls short. Users care when something is recalled, how it is said, and whether the relationship still feels continuous after weeks. They do not usually judge the system on whether a fact was technically present in the prompt.

This repo is for figuring out what memory has to be for a companion to feel human, what the field is getting wrong, and what would count as proof, before we pick a product shape.

## What we're investigating

A companion that people would call human-like, through memory, not through a bigger prompt. We do not yet know the architecture.

Retrieval can work and the interaction can still feel off. Long-chat QA recall is not the same as a relationship that holds. Path: [`ROADMAP.md`](ROADMAP.md).

## How we work

Research first. No product code at the repo root until groups of questions converge.

[`docs/QUESTIONS.md`](docs/QUESTIONS.md) is the source of truth. Questions are grouped by theme (definitions, human behavior, storage, evals, product scope). There is no fixed priority order yet. Answers are working notes with inline citations; we prefer primary sources (papers, specs, law) over blog posts. Each item gets a status tag: `settled`, `open`, or `deferred`. Settled answers need a stated falsifier. When an answer has downstream consequences, it can become an ADR in `docs/decisions/` (that directory does not exist yet).

Agent skills in [`.agents/skills/`](.agents/skills/) back this up: research, summarization, pressure-testing via `grill-with-docs`, ADR drafting, and [`companmem-research-gate`](.agents/skills/companmem-research-gate/SKILL.md), which enforces the gates above. Versions are pinned in [`skills-lock.json`](skills-lock.json).

## Repository layout

| Path | Purpose |
| --- | --- |
| [`ROADMAP.md`](ROADMAP.md) | Human-like companion via memory, plus an exam we can win |
| [`docs/`](docs/) | Active research; start with `QUESTIONS.md` |
| [`research/pipeline/`](research/pipeline/) | Harvest / extract / fold / apply |
| [`research/output/`](research/output/) | Product `audit.json` records; see `by-product/PROTOCOL.md` |
| [`.agents/skills/`](.agents/skills/) | Project agent skills, git-tracked |

## What this is not (yet)

- Not a shipped memory product or library
- Not a push for LoCoMo leaderboard scores alone
- Not a bet on one storage architecture (vector DB, graph, files, OS-style paging)

## Contributing / using agents

When working in this repo:

- Read `docs/QUESTIONS.md` before proposing architecture
- Cite sources; do not invent claims
- Do not commit unless asked
- Attach `companmem-research-gate` for research edits to `QUESTIONS.md`
