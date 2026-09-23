---
name: companmem-research-gate
description: Enforces the companmem research workflow on docs/QUESTIONS.md — cited answers, status tags (settled/open/deferred), falsifiability before promotion, and ADR drafting only when settled. Use when editing QUESTIONS.md, answering research questions, tagging items, promoting answers to decisions, or any companmem research work.
---

# Companmem Research Gate

Research-first project. **Source of truth:** `docs/QUESTIONS.md`.

The mission is to build the memory technology that makes the most human-like companion we can, then show it with a number someone else can rerun. We still do not know what we are shipping, and we still do not know what that number measures. The field map exists so we do not copy everyone else's extract-and-search pipeline. The missing piece is a number we would bet the company on. We get it by running the same situation on our companion and on other products, then reading a result someone else can run again. That number is what tells us the product. An example in `TODO.md` or `README.md` is not the assignment. A single borrowed probe is not the exam.

Do not implement product code or expand scope beyond documentation unless the user explicitly asks.

## Hard gates

Apply in order. Do not skip a gate.

| Gate | Allowed | Blocked until |
|------|---------|---------------|
| **Explore** | Read sources, draft answer bullets, add citations | — |
| **Tag** | Mark status on a question block | At least one answer bullet exists |
| **Settle** | Set status to `settled` | Cited + falsifiable (see below) |
| **Decide** | Draft an ADR | Status is `settled` and user agrees |
| **Defer** | Set status to `deferred` | User confirms it has no downstream effect right now |

<HARD-GATE>
Do **not** draft an ADR, write a product spec, or propose implementation for a question whose status is `open` or `deferred`.
</HARD-GATE>

## Vocabulary (use in docs)

| Term | Meaning |
|------|---------|
| **Question** | Something we do not know yet |
| **Claim** | A statement we believe, stated in plain language |
| **Evidence** | Source or observation that supports or falsifies a claim |
| **Answered** | Position stated with at least one source or observation |
| **Cited** | Source is linked; we know what it actually measured |
| **Falsifiable** | We can name a test or counterexample that would change our mind |

## Status tags

Every answered question block must end with a status line:

```markdown
**Status:** open | settled | deferred
```

| Status | When to use |
|--------|-------------|
| `open` | Default. Still gathering evidence or wording |
| `settled` | Answered, cited, falsifiable; ready for ADR if needed |
| `deferred` | No downstream effect right now; revisit later |

Before setting `settled`, verify all three:

1. **Answered** — plain-language position exists
2. **Cited** — inline link to a primary source (paper, spec, law) when one exists; blog posts only when no primary source is available
3. **Falsifiable** — add a one-line **Falsifier:** naming what would change the answer

Example:

```markdown
- What is memory?
  - In AI systems: persistent state across sessions — not weights, not just the current prompt ([Pathak, 2025](https://ninadpathak.com/blog/context-windows-vs-memory/)).
  - **Falsifier:** A system with no cross-session state that users still describe as "remembering" would break this definition.
  - **Status:** settled
```

## Workflow by intent

### Answer an open question

1. Read the question and existing bullets in `docs/QUESTIONS.md`
2. Use `research` or `evidence-driven-research` for landscape / options work
3. Use `research-summarizer` when the user provides a paper or long article
4. Draft answer bullets with inline citations (match existing style)
5. Add **Falsifier:** if aiming for `settled`; otherwise tag **Status:** open
6. Tell the user what changed and what remains open

### Pressure-test before settling

Before changing **Status:** to `settled`, offer `/grill-with-docs` on that section unless the user already pressure-tested it in this session.

### Promote to decision

When status is `settled` and the answer has product or architecture consequences:

1. Confirm with the user that an ADR is warranted
2. Invoke `adr-drafting`
3. Default ADR location: `docs/decisions/` (create if missing; use `0001-slug.md` numbering)
4. Link the ADR back to the question section in `QUESTIONS.md`

## Editing rules

- Prefer revising existing bullets over adding parallel conflicting answers
- When new evidence contradicts a `settled` item, downgrade to `open` and note what changed
- Do not invent citations — if no source exists, say so and keep status `open`
- Match `QUESTIONS.md` tone: concise bullets, inline markdown links, no priority ordering across sections
- Do not create new top-level doc files unless the user asks (except ADRs after the Decide gate)

## Companion skills

| Phase | Skill |
|-------|-------|
| Find sources | `research`, `evidence-driven-research` |
| Summarize a provided doc | `research-summarizer` |
| Pressure-test | `grill-with-docs` |
| Record decision | `adr-drafting` |

## Anti-patterns

- Jumping from a question to code or architecture without a `settled` answer
- Tagging `settled` without **Falsifier:**
- Citing a secondary blog when a primary paper or spec exists
- Adding answers that do not change what we would build, measure, or refuse to do
- Treating trivia as urgent — use `deferred` instead
