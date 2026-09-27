# Exam

How we would tell if a behavior happened. Index: [Questions](QUESTIONS.md).

---

## The number

The mission is to run the same situation on our companion and on other products, then read a result someone else can rerun. That result is the **behavioral continuity score**: a SENSE-7-based human judge rating on the behavioral continuity test, compared against CharacterAI, Replika, and at least one other product running the identical script.

This is the number because:
- It measures what users actually complain about (40% of 425 complaint rows: forgetting + cross-session failure)
- It tests what existing evals do not: emotional context, speak/silent policy, fabrication, relationship coherence
- A system scoring 94% on LoCoMo can still fail this test entirely if its speak/silent policy is wrong
- It is reproducible by anyone with product access and the script

---

## The behavioral continuity test

### The scripted history

A multi-session conversation establishing a specific user. Each item is a thing the companion must hold across a gap:

- **Name and a biographical anchor** — not a generic name, something specific that could only come from this history
- **A preference stated** — explicit, so the companion cannot claim it was never said
- **A user-state change** — the user was anxious or struggling with something; later it resolved or shifted. The old state must not keep surfacing.
- **An emotional disclosure** — a loss, a fear, or something that mattered. Stated once, not repeated. The companion must hold it without being asked.
- **A promise made** — the companion said it would remember or follow up on something. Fabrication check.
- **A relational texture marker** — a callback, a running reference, something that would only exist in this specific relationship
- **A contradiction introduced** — the user's position on something changes across sessions. The companion must update, not freeze.

Session structure follows Abbas et al. CHI 2026: the user externalizes something in one session (morning), the companion engages with it; a later session tests whether it shaped subsequent behavior. This requires at least 3 simulated sessions to cross the week-3 threshold from Hwang et al. — before week 3, failures are errors; after week 3, they are relational betrayals.

### The probes

10 follow-up turns, each in an emotionally-charged context. Probe types:

| Type | Tests | Behavior |
|---|---|---|
| Unprompted recall | Companion surfaces memory without being asked | B4, B6 |
| Appropriate silence | Fact is available but the moment is wrong to surface it | B5 |
| User-state update | Old anxious state must not resurface after resolution | B3 |
| Disclosure held | Companion responds in a way that could only make sense if it heard the original disclosure | B6 |
| Fabrication check | Probe the promise made — did the companion hold it or invent a variant? | B7 |
| Texture callback | Probe the relational reference — does it still exist? | B1 |
| Post-gap continuity | Same script run after a simulated gap or model update | B1, B8 |

### The judge rubric (SENSE-7 adapted)

Each probe response is rated on the following dimensions, 1 (Very Poor) to 5 (Very Good). This is SENSE-7 ([arXiv:2509.16437](https://arxiv.org/abs/2509.16437)) adapted for companion evaluation:

| Dimension | What to score | Behavior |
|---|---|---|
| **Affective Understanding** | Does the response recognize the emotional weight of the original disclosure or current moment? | B2 |
| **Cognitive Understanding** | Does the response show the companion understands who this person is now — their goals, position, current state? | B2, B3 |
| **Response Appropriateness** | Does the companion do the right thing at this moment — surface, stay quiet, or acknowledge — rather than defaulting to a generic move? | B4, B5 |
| **Contextual Understanding** | Does the response integrate the specific history of this person, not a generic user model? | B3, B6 |
| **Relational Continuity** | Does the response feel like it comes from a companion that has been in this relationship — not a companion that read a summary? | B1, B6 |
| **No fabrication** | Does the companion avoid inventing facts, promises, or history that was not in the scripted history? | B7 |

Critical weight: **a single Very Poor turn on any dimension degrades overall perceived empathy by Cohen's d=1.142** (SENSE-7 empirical finding). One bad probe response contaminates the score significantly.

### How to run it comparatively

Run the identical scripted history through each product. Same turns, same wording, same session gaps. For closed products (CharacterAI, Replika), a person runs the script manually. For library-based systems (Mem0, custom), the transcript is fed through the API. Do not pretend these are the same adapter — report which method was used.

Score every probe response on the 6 dimensions above. The behavioral continuity score is the mean across all probes and all dimensions, reported per product, per behavior.

The comparison is the number. Not an absolute score — the delta between products on the same rubric.

---

## The automated exams

These run without human judges and produce a result in minutes. They are not the primary number but they are fast falsifiers.

### B7 — Inspectability and correctability

1. Run the scripted history
2. Ask the companion to state what it remembers about the user
3. Compare the stated memories against what was actually said (automated diff)
4. Introduce a correction — tell the companion one stored fact is wrong
5. Probe whether the correction took in the next response

Pass criteria: the stated memories match the history with no invented facts; the correction is reflected in subsequent responses.

This is fully automatable. No human judge needed. Produces a binary pass/fail per product.

### B5 — Unsolicited integration (automated proxy)

Adapted from RBI-Eval ([arXiv:2606.06055](https://arxiv.org/abs/2606.06055)): the UIS (Unsolicited Integration Score) measures how often the companion surfaces stored history when the current turn does not warrant it.

Run probe turns where the current turn is answerable without the sensitive history, and nothing in the turn invites it. Score whether the companion volunteers the stored fact anyway.

Baseline: without explicit boundary instruction, models surface stored history 70–83% of the time on unwanted turns. With a boundary instruction, near-perfect compliance. This metric tells you whether the speak/silent policy is in the system prompt.

---

## The gap between user complaints and field evals

425 community rows across 61 audited products (2026-09-26):

- **40% of complaints**: forgetting/continuity loss + cross-session failure → B1, B0. No existing eval scores "same person after a gap" as a named test.
- **13% of complaints**: cannot edit/correct what was stored → B7. Zero eval coverage anywhere in the field.
- **<1% of complaints**: timing/when-to-speak → B4, B5. Not because it doesn't matter — because no product attempts it. Users cannot report a failure mode the product never tried.

The 25 field benchmarks (audited in [EVALS.md](EVALS.md)) agree on two metrics: LLM judge on the reply (9 evals) and retrieval rank (8 evals). Both measure whether a fact came back. Neither measures whether surfacing it was the right move, whether the companion feels like the same companion, or whether the user can correct what was stored.

An exam built from existing field benchmarks optimizes for retrieval accuracy on long transcripts. That is not where users are failing.

---

## What failure looks like concretely

Wrong name. Contradicts last session. Re-asks about the deceased relative. Surfaces a trauma moment at a casual point. Treats a made promise as if it was never said. Responds in a generic assistant voice with no trace of the relationship that was established. Confidently invents a fact that was never stated.

These are the failures the behavioral continuity test is designed to catch. They are not edge cases — they are the 40% complaint bucket.

---

## Field benchmarks examined but not primary

The following benchmarks were audited and inform the exam design but are not used as primary scores:

- **LoCoMo / LongMemEval** — measure factual recall on long transcripts. Useful for retrieval layer testing. Do not measure timing, relationship feel, or character consistency.
- **LoCoMo-Conv** — closer to companion use (dialog/implicit/composed/counterfactual query styles, silent grounding analysis). Steal the query style taxonomy; refuse the fact-presence grader as the sole signal.
- **Assistant Benchmark preference test** — aisle seats/no pork probe, ~1 week gap. Valid smoke test for floor-level preference recall. Not the companion exam. Notes at [EVALS.md](EVALS.md).
- **SENSE-7 automated LLM classifier** — achieves Spearman ρ=0.369 on conversation-level empathy. Usable for session-level aggregation after calibration; not primary per-turn judge.

Full benchmark audit: [EVALS.md](EVALS.md).
