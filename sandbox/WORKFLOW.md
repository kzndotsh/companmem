# Companion memory program workflow

This is the playbook for this repo. It is not the memory protocol. The protocol does not exist until an eval says a design beats named baselines.

## Done for this framing pass

A reviewer can point at files that name the predicate, the player list, the census rubric, and the unit order below.

## Done for the whole program

A third party can clone this repo, run the eval harness against Mem0, Graphiti, Letta, Honcho, SillyTavern World Info plus vectors, naive RAG, and long-context stuffing, then run our system on the same transcripts. Our system wins on the companion suite, not only on LoCoMo. Cost per turn and poisoning resistance are first-class scores. The claim "best" is that run, dated, with the commit SHA.

If we cannot lose that bakeoff, we do not get to claim we won it.

## Scope

This session. Frame, census, then a multi-phase build plan. No memory engine.

The program after operator go. Eval fixtures and harness first. Then two or three architecture sketches on the same harness. Then one protocol and a reference implementation.

Rough size. Census is about 30 players. Deep code audit of about 8. Eval design is the long pole. Full program is weeks, not an afternoon.

## Rigor

High. The one-way door is locking an architecture and then calling it the best. Reversible steps (census notes, fixture drafts) stay cheap.

## Shared failed premise

If we retrieve the right past text or extracted facts into the prompt, the model will act as if it remembers the relationship.

Agent-memory vendors optimize that premise against LoCoMo and LongMemEval. Companion users fail on write policy, identity split, silence, poisoning, and cost. The public benches barely score those.

## Domain shape, before any engine

A companion memory record is not a chunk.

Minimum kinds the later types must make illegal to mix.

- User biographical fact, with provenance and supersession.
- Character autobiographical event, what the character lived.
- Relationship state, a phase, not a factoid.
- World or lore, author-canonical, not episodic.
- Session working memory.
- OOC or meta instruction, never mixed into IC recall.

Read policy is its own object. Retrieval score is not permission to speak.

## Unit order

1. Frame. This file, the rubric, the player list. Check. Files exist.
2. Census. JSON cards plus slice markdown, citations to primary sources. Check. Schema-valid cards for every required id, or an explicit `unknown` with a reason.
3. Gap map. Which companion failure modes have zero current coverage. Check. A table that names the hole and the player closest to it.
4. Eval spec. Transcript fixtures, pass predicates, cost meters, poisoning cases. Check. `python3 research/_contracts/run-oracles.py` shows oracle PASS and naive FAIL on every public fixture. Named-baseline fail is unit 5.
5. Harness that runs the named baselines. Check. `python3 research/harness/run.py` writes `research/evals/results/<timestamp>-<sha>.json`. Local baselines run without Docker. `--docker` uses `research/harness/docker/` for agent/verifier split.
6. Architecture sketches, two or three, on that harness. Check. `python3 research/harness/compare_sketches.py` — sketch B selected (see `research/harness/sketch-comparison.json`).
7. Protocol spec and reference implementation against the losing sketches. Check. `companmem/` package + `research/protocol/SPEC.md`.
8. Public bakeoff writeup. Check. `research/evals/BAKEOFF.md` from `python3 research/harness/write_bakeoff.py`. Refresh after each `run.py --baseline local`.

Do not start unit 7 because a design feels revolutionary.

## Fan-out seams

Census slices A-F are independent. Each worker writes its own files. They do not edit `research/_contracts/`.

**Issue mining (slice I, optional).** GitHub issues, discussions, and public feedback on census players. Protocol in `research/census/issue-mining.md`. Output lands in `research/census/issue-signals/`. Use this to sharpen fixtures for holes 2, 7, 8, 9, and 10. Does not replace the harness.

## What this is not

A girlfriend app. A Mem0 clone with better marketing. A claim that we already have the best system on the planet. We do not. The repo is empty of an engine.
