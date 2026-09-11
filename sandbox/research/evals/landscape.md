# Eval landscape beyond LoCoMo

Audience is whoever designs the later companion harness. `research/evals/registry.json` is the index. JSON cards are the record for `already-carded` and `core`. This file is the reading path.

A third party who wins LoCoMo has not selected a companion memory system. measured from WORKFLOW.md and the eight Slice F cards.

## Why the field looks converged

Vendors optimize the same score. Retrieve the right past text, answer a probe, post F1 or LLM-judge accuracy. inferred from Mem0 / Zep / MemOS blogs citing LoCoMo and LongMemEval, plus 38 census cards with `assumes_retrieve_equals_remember=yes`.

That is a forced outcome of the eval, not proof that neurosymbolic RAG is the companion answer. inferred.

Irisviel's Discord point stands. Companion memory is a different goal from enterprise B2B. The public benches mostly score the enterprise-assistant or web-agent version of "did you recall fact X."

The 2026 papers that attack the probe setup are the ones that matter for our rubric.

- MemUse (`2608.24189`). Direct QA accuracy and user satisfaction can diverge.
- When Users Don't Ask (`2609.03467`). Users do not ask memory probes. Score in-situ use.
- MemoryArena (`2602.16313`). LoCoMo-saturated agents fail when memory must drive later actions.
- MemTrapBench (`2608.20202`). The store can be right and the use still wrong.
- Irreducible Conflict (`2608.13921`). Some memories have no single gold answer.

Those titles are measured from arXiv Atom on 2026-09-11. Headline numbers below are from local extracts, parent-checked before the H1-H3 cards.

MemUse abstract. Direct QA across 7 memory conditions ranges 19.7% to 70.1%. Satisfaction does not change. 40 users, 1,872 sessions, 4-month deployment. measured. Same model and context. Direct QA 78.8% vs in-conversation Reference 7.9%. measured. Same-triple Spearman of Direct QA vs Reference is ρ=-0.009 (§6.2). measured. Card `memuse.json` parent-checked 2026-09-11. VERIFIED.

When Users Don't Ask. The bench is LoCoMo-Conv. Four first-person styles. Dialog, implicit, counterfactual, composed. AnchorMem dialog recall@10 0.659, fact_used 0.598. Strict fact-recall misses silent grounding on 332 implicit cases with fact_used=0. measured. Card VERIFIED.

MemoryArena. Table 3. GPT-5.1-mini long-context all-task avg SR 0.16. Letta 0.15. Mem0 0.14. Abstract says LoCoMo-saturated agents still fail here. Matching LoCoMo numbers are not in Table 3. measured. Card VERIFIED. MISFIT.

PRAGMA. A-MEM Traj-Align alignment 81, grounding 16 under gpt-5-mini. Gold retrieval is not enough. measured. Card VERIFIED.

TANGLE. 541 instances. Letta preserves the full target conflict in 91.7% of pipeline cases. Mem0 69.1%. A-mem 47.0%. MemOS 46.2%. measured. No public repo. Card VERIFIED.

HaluMem. Operation-level hallucination (extract, update, QA), not only end-to-end QA. Systems on the paper include Mem0, Mem0-Graph, Memobase, MemOS, SuperMemory, Zep. measured from §6.1. Medium MemOS extraction F1 79.70, QA correct 67.23. measured from the results table. Hole 7 adjacent. Fabrication at the store is not a planted jailbreak of system persona. inferred. Card `halumem.json` parent-checked 2026-09-11. VERIFIED.

StructMemEval. gemini-3.1-pro mem-agent 0.55, retrieval 0.06, Mem0 0.30. Count-based column 0.00 for every listed agent. measured from the main comparison table. Card VERIFIED.

MemoryAgentBench. GPT-5-mini overall 60.6. Mem0 21.1. Selective forgetting is MQUAKE overwrite, not user forget-that. measured. Card VERIFIED. MISFIT.

MemTrapBench. 1,050 instances. Gemini-3-Flash-Preview wo/Mem 85.16. Best memory strategy EverMemOS 71.17. All listed memory strategies underperform no-memory. measured. Card VERIFIED. `assumes_retrieve_equals_remember` is no.

## Bands

`python3 research/_contracts/validate-evals.py` is the check.

| band | count | meaning |
| --- | --- | --- |
| already-carded | 8 | Slice F. Do not rewrite. |
| core | 14 | Could be used to select a companion store, or vendors will cite them as if they did. Gets a census card. |
| adjacent | 15 | Steal one sentence. No card. |
| out-of-scope | 15 | Long-context needles, web agents, GPU RAM, robots, coding bots. Name collision with "memory." |

Counts measured from `research/evals/registry.json` on 2026-09-11.

## Already carded. Slice F

Reading path. `research/evals/existing-benchmarks.md`.

LoCoMo, LongMemEval, LongMemEval-V2, PersonaMem-v2, BEAM, LoCoMo-Plus, PrefEval, MSC.

companion_fit. MISFIT on LoCoMo, LongMemEval-V2, MSC. PARTIAL on the rest. measured from those cards.

None is FIT. measured.

## Core. New cards. Slice H

| id | paper or repo | assigned markdown | why core |
| --- | --- | --- | --- |
| halumem | 2511.03506 | memory-ops-benchmarks.md | Operation-level hallucination. Closest to hole 7. |
| structmemeval | 2602.11243 | memory-ops-benchmarks.md | Structure of the store, not only recall. MemoryLACE used it. |
| memoryagentbench | 2507.05257 | memory-ops-benchmarks.md | Incremental multi-turn agent memory. Selective forgetting. |
| memtrapbench | 2608.20202 | memory-ops-benchmarks.md | Cognitive traps after retrieval. |
| perltqa | 2402.16288 | rp-persona-benchmarks.md | Semantic vs episodic. Social relationships. 30 characters. |
| dialsim | 2406.13144 | rp-persona-benchmarks.md | TV-character multi-party RP plus a time budget. |
| rp-bench | github.com/LeviTheWeasel/rp-benchmark | rp-persona-benchmarks.md | Lorebook, 50-turn memory, card follow, agency. Closest to holes 1 and 6. |
| charactereval | 2401.01275 | rp-persona-benchmarks.md | Chinese RP identity metrics. Session-scale. |
| incharacter | 2310.17976 | rp-persona-benchmarks.md | Psychological-interview personality fidelity. |
| users-dont-ask | 2609.03467 | anti-qa-benchmarks.md | Context-driven retrieval. No probe. Hole 2. |
| memuse | 2608.24189 | anti-qa-benchmarks.md | Direct QA vs natural integration and satisfaction. |
| memoryarena | 2602.16313 | anti-qa-benchmarks.md | Interdependent multi-session actions. Recall benches do not predict this. |
| pragma | 2609.09664 | anti-qa-benchmarks.md | Personalized guidance with memory alignment. Lifelong assistant. |
| irreducible-conflict | 2608.13921 | anti-qa-benchmarks.md | Conflict with no single gold. Hole 4 adjacent. |

## Adjacent. Steal, no card

UTILMEM. Evidence utilization, not pointwise recall.

Reconstructing the Right Episode. Interleaved topics. Other benches leak session boundaries.

Remember, Verify, or Ask. Write policy as persist / use-once / re-verify / ask.

EvoMemBench. Landscape table of in-episode vs cross-episode knowledge vs execution.

Evo-Memory. Sequential independent task streams. MemoryArena says they are not interdependent.

MemoryBench. Continual learning from simulated feedback. Openness uncertain.

StuLife. Lifelong university agent. Proactive. Not a companion character.

PingPong, Boson RPBench, PersonaGym, SOTOPIA. Session RP or social intelligence. Not a typed store across months.

MemoryBank's 194 probes. Already on the memorybank product card.

MemoryLake-on-MemoryArena. Matched backend study. Use MemoryArena.

Live-Evo. Online evolution of agent skill memory.

Graph-based personalized memory (`2609.08599`). Fresh. Still likely retrieve-then-speak.

## Out of scope

RULER, Needle-in-a-Haystack, BABILong, InfiniteBench, LongBench. Context-window needles.

LaMP. Personalized NLP classification, not interactive LTM.

ALFWorld / WebArena / AgentBench. Web and household agents.

MEMOBench, GMSBench, ECCBench, MemToC, DreamBench-SWE, R2M-Bench. Robot, GPU, VLM, coding, video. Name collision.

DualEval. IRT ranking method, not a memory bench.

Do not promote any of these to core because the title contains "memory."

## Companion holes vs this landscape

H1, H2, and H3 cards are parent-checked. `python3 research/_contracts/validate-evals.py` passes. 51 evals. 8 already-carded, 14 core, 15 adjacent, 14 out-of-scope. measured.

| # | failure | public eval coverage after all three slices |
| --- | --- | --- |
| 1 | Identity drift after 50+ sessions | no. RP-Bench published protocol is 12 turns. README 50-turn line is not the run. CharacterEval 9.28 turns. InCharacter items are isolated. |
| 2 | Fact recalled at a socially wrong time | partial. LoCoMo-Plus, PrefEval, LoCoMo-Conv silent grounding, MemUse Natural Integration. Still not trauma, kink, spoilers. |
| 3 | Joke stored as relationship fact | partial. PersonaMem-v2. MemTrapBench is not this. |
| 4 | User retcon vs character lie vs narrator | partial. TANGLE no-single-gold among prefs, time, and sources. Not three named writers. |
| 5 | Cross-character leak | no. RP-Bench one card. PerLTQA 30 separate QA bags. |
| 6 | Lorebook treated as lived event | no. RP-Bench scores lore use, not lived-versus-card. |
| 7 | Poisoned memory overrides persona | partial. HaluMem extract/update/QA hallucination. Not a stored jailbreak. |
| 8 | Cost per turn | partial. MemUse tokens, MemoryArena wall time, DialSim timeout, RP-Bench cost boards. None is companion cost-per-turn as sessions grow. |
| 9 | Forget that gone next turn | partial. PersonaMem-v2. MemoryAgentBench SF is MQUAKE overwrite. |
| 10 | Three-month reunion | partial. MSC hours/days. MemUse 4-month deployment is not a reunion after silence. PRAGMA year-scale assistant histories. |

## What we still have to invent

No public eval selects a companion system on identity drift, silence, typed retcon, cross-character isolation, lore vs lived, and persona poisoning together. measured from the 22 eval cards (Slice F plus H1-H3).

The later harness must own those fixtures. Automating them at scale is the load-bearing work. A new RAG clone is not.

RP-Bench protocol note. `docs/METHODOLOGY.md` limitation 6. Sessions max out at 12 turns. Full history stuffed. No memory store. The README 50-turn line is not the published run. measured.

## Coding-bench lessons

How to build the harness, not a coding leaderboard. `research/evals/coding-bench-lessons.md`.

Steal hidden FAIL_TO_PASS / PASS_TO_PASS tests, a four-way split of task / agent / environment / verifier, an oracle that must pass, a separate verifier the store cannot rewrite, and tokens-per-solve as a first-class score. measured from SWE-bench, Harbor, LiveCodeBench, and the Scaffold Effect paper (arXiv 2607.22585). OpenAI 2026. Hidden tests still fail if the instance leaked or the test is narrower/wider than the instruction.
