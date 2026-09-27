# companmem

Research on memory for realistic human and companion communication.

## Why this exists

This started from direct frustration with AI companion apps — the slopping memory, the reset personalities, the sense that the AI never actually learned anything about you. The natural question was: why are there 60+ memory products competing in this space without anyone clearly winning? The answer the field audit gave back: the problem isn't solved. Most products are just database CRUD with memory branding. Nobody has a proper speak/silent policy. Forget is missing from 80% of products. The benchmark that would tell you whether a companion actually knows you doesn't exist yet.

The observation that matters: coding assistants work well partly because the context problem for code is well-specified — what files are open, what's the diff, what tests failed. The context problem for a companion relationship is completely unspecified. Nobody has written the equivalent of "what does a relationship harness need to track." That's what this project is building toward.

The specific failure the field hasn't solved: surfacing the right memory at the right emotional moment — not when the topic matches, but when the emotional context calls for it. No product has a speak/silent policy that reflects this. The benchmark that would measure it doesn't exist. Building that benchmark is what unlocks the product decision.

## The mission

Build the memory technology that makes a companion feel like it actually knows you — continuously, over months, not just within a session. The field map exists so we don't copy the extract-embed-retrieve pipeline everyone else already built.

The real test is not a benchmark score. It's someone using the companion over months and noticing, unprompted, that it remembered something at exactly the right moment. It's a relationship that feels continuous. A number can't fully capture that — but we need one anyway, because without an external check you drift toward optimizing your own intuitions. The number is a compass during build, not the destination.

The working compass: a behavioral continuity test run against the best products in the field on the same scripted history. Human judge scores relationship coherence, appropriate recall, and fabrication. Not LoCoMo — that measures whether the right fact came back, not whether surfacing it was the right move.

Path: [`TODO.md`](TODO.md). Docs: [`docs/INDEX.md`](docs/INDEX.md).

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
