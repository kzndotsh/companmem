# companmem

Research on memory for realistic human and companion communication. Not another retrieve-then-speak RAG stack.

The mission is to build the memory technology that makes the most human-like companion we can, then show it with a number someone else can rerun. We still do not know what we are shipping, and we still do not know what that number measures. The field map exists so we do not copy everyone else's extract-and-search pipeline. The missing piece is a number we would bet the company on. We get it by running the same situation on our companion and on other products, then reading a result someone else can run again. That number is what tells us the product. Path: [`TODO.md`](TODO.md). Docs: [`docs/INDEX.md`](docs/INDEX.md).

Most agent-memory products follow the same pipeline: extract facts, embed, retrieve, stuff into context, generate. That pipeline is what the field map is here to keep us from copying. Examples of how a companion can still feel wrong, such as timing, wording, or a relationship that fades after weeks, are examples. They are not the mission.

## How we work

Research first. No product code at the repo root until groups of questions converge.

[`docs/QUESTIONS.md`](docs/QUESTIONS.md) is the index. The question docs are the source of truth. There is no fixed priority order yet. Answers are working notes with inline citations. We prefer primary sources (papers, specs, law) over blog posts. Each item gets a status tag: `settled`, `open`, or `deferred`. Settled answers need a stated falsifier. When an answer has downstream consequences, it can become an ADR in `docs/decisions/` (that directory does not exist yet).

Agent skills in [`.agents/skills/`](.agents/skills/) back this up: research, summarization, pressure-testing via `grill-with-docs`, ADR drafting, and [`companmem-research-gate`](.agents/skills/companmem-research-gate/SKILL.md), which enforces the gates above. Versions are pinned in [`skills-lock.json`](skills-lock.json).

## Repository layout

| Path | Purpose |
| --- | --- |
| [`TODO.md`](TODO.md) | Roadmap. Pending and done |
| [`IDEA.md`](IDEA.md) | Not work yet |
| [`docs/INDEX.md`](docs/INDEX.md) | Which doc owns what |
| [`research/pipeline/`](research/pipeline/) | Harvest / extract / fold / apply |
| [`research/output/`](research/output/) | Product `audit.json` records; see `by-product/PROTOCOL.md` |
| [`.agents/skills/`](.agents/skills/) | Project agent skills, git-tracked |

## What this is not (yet)

- Not a shipped memory product or library
- Not a push for LoCoMo leaderboard scores alone
- Not a bet on one storage architecture (vector DB, graph, files, OS-style paging)
- Not a bet on user approval. A thumbs-up can rise on the failure ([Sharma et al.](https://arxiv.org/abs/2601.19062))

## Contributing / using agents

When working in this repo:

- Read [`docs/QUESTIONS.md`](docs/QUESTIONS.md) before proposing architecture
- Cite sources; do not invent claims
- Do not commit unless asked
- Attach `companmem-research-gate` for edits to the question docs
