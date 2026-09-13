# ROADMAP

**Goal.** Build the most human-like AI companion we can, by building the memory technology that actually does that. Then show, with a number someone else can rerun, that we beat other products on it.

We do not know the product shape yet. We do not know the exam yet. Mapping the field and inventing that exam is how we find both.

"Best" is not a feeling and a slide. It is two results:

1. People would call the companion more human, because of memory, not a longer prompt.
2. A comparison we can run on us and on other products, that we would trust as "ahead."

If we cannot name that comparison, we are not done. If we pick a score that is easy and empty, we also fail.

---

## Phase 1. Map the field

**Status:** in progress

Learn what shipped memory and companion products actually do. Same questions for every product. Quotes from their code and docs. No FIT scores.

- `just harvest` and `just audit-write` for each seed product
- What they persist, what they retrieve, what users say breaks
- Who is a competitor we can plug into a runner, and who is a closed app we can only watch from the outside
- Synthesize what recurs and what is missing

Audits explain the field. They do not prove we are better.

**Done when:** we can describe the field with quotes, and we know which products we can score in a bakeoff versus which we can only observe.

---

## Phase 2. Name what "more human" is

**Status:** not started

Memory is the lever. A companion people would stay with is the point.

Name the behaviors that would make someone say "this knows me," not "it retrieved the fact." Include caring versus creepy, continuity versus a fact dump, and remembering versus retrieving.

Use papers, companion HCI, and live user complaints. Do not harvest papers as if they were products.

Phase 1 and Phase 2 can overlap. Do not wait to finish every audit before this starts.

**Done when:** we have a short list of behaviors that would count as a win, written so an eval author could turn them into tasks.

---

## Phase 3. Invent the exam

**Status:** not started

Turn those behaviors into something we can run. A third party runs the same thing on us and on other products.

The exam is the hard problem. We do not have it yet. Long-chat QA might be one probe. It is not automatically winning. The archived sandbox eval stays archived. Do not extend it.

Expect two comparison tracks, because they are not the same engineering:

- **Plug-in products.** Open memory libraries we can put behind one runner, same transcripts, same grader.
- **Closed companions.** Apps we cannot instrument. Scripted live probes or a user study, called out as a different protocol, not faked into the same adapter.

A thin, ugly exam that moves is better than a perfect story. Start it as soon as Phase 2 has even one named behavior. Do not wait for a literature program to finish.

**Done when:** we would bet the company on the comparison as "ahead," and we can point at how we scored at least one other product, not only ourselves.

---

## Phase 4. Name the product

**Status:** blocked until Phase 1 has a real map and Phase 3 has an exam that moves

This is the point of the research.

Use the field map, the behavior list, and the exam. Say what we copy, what we refuse, and what we invent. Name whether we ship a memory engine, a companion, or both, who it is for, and what we will not optimize for.

**Done when:** we can write the product in plain language, plus a falsifier for why this direction and not another.

---

## Phase 5. Build it, then keep winning

**Status:** blocked on Phase 4

Build the memory system the evidence pointed at. If the companion is the vehicle, build that on top. Spikes first. Product at the repo root when we ask.

Keep running the Phase 3 exam on us and on others. If we stop beating them, the product is not done.

**Done when:** someone can use it, and the exam still shows we are ahead.

---

## Will not do

- Treat a layer sketch as the product
- Ship the industry default because every audit showed it
- Treat an easy leaderboard as winning
- Extend the archived sandbox
- Implement before Phase 4
