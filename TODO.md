# TODO.md: companmem roadmap

Ideas that are not work yet live in [`IDEA.md`](IDEA.md). Docs live in [`docs/INDEX.md`](docs/INDEX.md).

The mission is to build the memory technology that makes the most human-like companion we can, then show it with a number someone else can rerun. We still do not know what we are shipping, and we still do not know what that number measures. An example in this file or in [`README.md`](README.md) is not the assignment. A single borrowed probe is not the exam.

The product decision is deliberately deferred to Phase 4. The hypothesis going in: a companion-first memory engine that solves the speak/silent problem the field hasn't touched, proved by a behavioral continuity benchmark that doesn't exist yet. Phase 3 either validates or revises that hypothesis.

## Pending

### Phase 2. Name what "more human" is

- [ ] Name the behaviors that would make someone say this knows me
- [ ] Write them so an eval author could turn them into tasks

Phase 1 and Phase 2 can overlap. Papers, companion HCI, and live complaints are sources. Do not harvest papers as if they were products.

Working list is in [`docs/BEHAVIORS.md`](docs/BEHAVIORS.md). Five behaviors are named. "Cannot edit/correct" and the speak/silent task still have no pass/fail script.

### Phase 3. Invent the exam

- [ ] Turn the Phase 2 behaviors into something a third party can run on us and on other products
- [ ] Keep plug-in products and closed apps on different protocols
- [ ] Run it once

Draft tasks and the failures they still miss are in [`docs/EXAM.md`](docs/EXAM.md). Nothing has been run. A borrowed probe is not the exam. A score that only checks whether something came back cannot close this phase.

The behavioral continuity test design is in EXAM.md: 20–30 turn scripted history establishing specific facts, 10 emotionally-charged follow-up prompts, human judge scoring recall appropriateness, fabrication, and relationship coherence. Run against CharacterAI, Replika, and the system under test.

Done when we would bet on that number as ahead, and we can point at a score for at least one other product.

### Phase 4. Name the product

Blocked until Phase 1 has a real map and Phase 3 has an exam that moves.

- [ ] Say what we copy, what we refuse, and what we invent
- [ ] Name whether we ship a memory engine, a companion, or both

Done when we can write the product in plain language, plus a falsifier for why this direction.

### Phase 5. Build it, then keep winning

Blocked on Phase 4. Product code at the repo root stays blocked until questions are settled and we ask.

- [ ] Build what the evidence pointed at
- [ ] Keep running the Phase 3 exam on us and on others

## Will not

- Treat a layer sketch as the product
- Ship the industry default because every audit showed it
- Treat an easy leaderboard as winning
- Treat a thumbs-up, or any user-approval rate, as the number we would bet on ([Sharma et al.](https://arxiv.org/abs/2601.19062))
- Implement before Phase 4

## Done

### Phase 1. Map the field ✓

- [x] Harvest and write an audit for each seed product — 61 products audited, per-product notes in [`docs/AUDIT.md`](docs/AUDIT.md)
- [x] Record what each product persists, what it retrieves, and what users say breaks — covered in AUDIT.md per-product entries and synthesis
- [x] Separate products we can score in a bakeoff from closed apps we can only watch — field map in [`docs/FIELD.md`](docs/FIELD.md)
- [x] Synthesize what recurs and what is missing — synthesis section at top of AUDIT.md, one-shot model analysis in [`docs/AUDIT-ANALYSIS.md`](docs/AUDIT-ANALYSIS.md)

Key findings: silent failure is the median behavior of deployed memory systems. Static lore outperforms dynamic memory on every platform that has both. Speaker misattribution is systemic. The benchmark that matters (behavioral continuity, emotional context recall) does not exist yet. No product in the field has an architecture that survives model updates with continuity intact.
