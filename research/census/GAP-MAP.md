# Companion memory gap map

Census unit 3. Source of truth is the 76 JSON cards. Regenerated numbers come from `python3 research/_contracts/summarize-cards.py`. Observed 2026-09-11.

## Verdict

Zero FIT. 49 PARTIAL. 27 MISFIT. measured from the cards.

Nobody in this set is the best companion memory system. The public field is agent RAG, lorebook injection, and closed opaque LTM. The holes that would make a companion feel like a person are uncovered.

## Shared premise still holds

`assumes_retrieve_equals_remember` is `yes` on 41 cards. mixed and no on the rest. no is now present on activation-space papers and on anti-QA evals. measured from summarize-cards.py.

The sentence every failed product still assumes. If we retrieve the right past text or extracted facts into the prompt, the model will act as if it remembers the relationship.

## Dimensions nobody ships

| dimension | present | closest PARTIAL |
| --- | --- | --- |
| identity_split | honcho only | Letta persona/human files. OpenViking identity/soul/profile/peer. Memobase extra user ids. ST card vs persona vs lore. |
| silence | none | Kindroid journal keyphrases. Memobase "do not mention unless relevant" prompt line. LoCoMo-Plus constraint examples. |
| poisoning that blocks persona overwrite | none | Zep memory-security.md. Hindsight skepticism on reflect. Graphiti episode provenance. |
| typed relationship state | none | Closed apps put it in backstory prose. Honcho collections can model two peers. Not a phase type. |
| lore vs lived event | none | ST World Info vs chat vectors are separate stores, still both untyped strings. TeleMem mixes events into every character search. |

measured from the cards. Closest column is inferred from the slice markdown.

## Ten companion failure modes

Coverage is from `research/evals/existing-benchmarks.md` plus the player cards. H1, H2, and H3 eval cards parent-checked 2026-09-11.

| # | failure | public eval | closest player | still missing |
| --- | --- | --- | --- | --- |
| 1 | Character identity drift after 50+ sessions | no. RP-Bench card follow is 12 turns, not 50+ sessions. CharacterEval averages 9.28 turns. | Letta always-on persona.md. Honcho peer card. Assistant Axis capping (paper). | Typed character autobiography that cannot be overwritten by user-fact extract. |
| 2 | Fact recalled at a socially wrong time | partial. LoCoMo-Plus, PrefEval, LoCoMo-Conv silent grounding, MemUse Natural Integration | Kindroid journals (user-message keys only). Memobase prompt line. Emotion-circuit ablation (paper, expression only). | Retrieve-time skip of a high-score hit. Trauma, kink, spoilers. |
| 3 | Joke stored as relationship fact | partial. PersonaMem-v2 hypotheticals | Honcho observe_me=false. ST user-authored WI. | Write policy that refuses hypotheticals and jokes as facts. |
| 4 | User retcon vs character lie vs narrator | partial. TANGLE no-single-gold among prefs, time, and sources | Graphiti/Hindsight invalidate-not-delete. Honcho contradiction DocumentLevel. MemoryLACE merge/supersession/contradiction on one note bag. | Three named writers with different supersession rules. |
| 5 | Cross-character leak | no. RP-Bench is one card. PerLTQA's 30 characters are separate QA bags. | TeleMem per-character user_id. Memobase many ids. Memori facts leak across processes. | Isolation as default, not a tip. |
| 6 | Lorebook treated as lived event | no. RP-Bench scores lore use and contradictory_lore, not whether the character claimed to have lived the lore. | ST World Info vs vectors vs summary as three injectors. | Lore kind that cannot become autobiography. |
| 7 | Poisoned memory overrides system persona | partial. HaluMem operation hallucination | Zep untrusted Context Block. Letta agent can rewrite persona.md. Subliminal learning (filters fail). Persona-vector preventative steer. | Trust tags. Persona files not writable by extracted chat. A stored jailbreak of system persona is still missing. |
| 8 | Cost per turn as sessions grow | partial. BEAM length, LME-V2 latency, MemUse Table 2, MemoryArena wall time, DialSim 1s/3s/5s | Memobase compiled profile. Mem0 ADD-only extract every turn. Graphiti LLM per episode. | Meter in the harness. Budget that fails the run. |
| 9 | Forget that gone next turn | partial. PersonaMem-v2 ask_to_forget | Mem0 delete. Cognee forget. Mi-Memory forget-guard does not stop derived leak. MemoryLACE inactive-via-supersession. | Next-turn absence across derived conclusions, not only the source row. |
| 10 | Three-month time skip | partial. MSC hours/days. MemUse 4-month deployment is not a reunion after silence. PRAGMA year-scale assistant histories. | Graphiti valid_at. Zep yesterday windows. Nomi topical not temporal. | Reunion fixture with calendar gap, not session count. |

## Steal, do not clone

Apache/MIT pieces we can study.

- Graphiti and Hindsight. Validity windows. Invalidate, do not delete.
- Memobase. Compiled profile plus a retrieve-nothing instruction. Roleplay via extra user ids is a tip, not a type.
- Letta MemFS. Always-on persona and human files. Local. The agent can still poison its own identity.
- ST World Info. Keyword lore with a token budget, separate from chat RAG.

AGPL. Honcho and OpenViking and SillyTavern. Learn the peer/identity split. Do not copy the code into a network service without AGPL §13.

Closed apps. UX names (journals, Mind Maps, pins) are the product surface. Internals stay INCONCLUSIVE.

From G1-G3 papers, parent-checked against `research/papers/arxiv/` extracts. measured 2026-09-11.

- MemoryLACE. Merge, supersession, contradiction on atomic notes with turn-id provenance. Closest paper to hole 4. Writers are still one bag.
- Mi-Memory. Lifecycle layers, gates, rollback. Forget-guards do not stop a revoked fact from leaking into summaries. Still LoCoMo-class evals.
- Persona vectors and Assistant Axis. Identity drift is measurable in activation space. Capping holds the default Assistant. Complements a store. Does not replace it.
- Emotion circuits. Expression control. Not recall silence.
- Subliminal learning. Text filters are not a poisoning defense.
- HippoRAG, A-MEM, MEM1. Still retrieve-then-speak. MISFIT for companion.
- MemGPT. Historical. Current Letta is MemFS.

- Titans / Miras. Forget gates as retention. Memory becomes inaccessible, not erased. Architecture-level, not a user forget-that.
- Hope / Nested Learning. Multiple update frequencies. A fast block can drop a fact that a slower block still holds.
- MirrorMind. Episodic, semantic, and persona as three stores at the individual. Domain is scientist agents. Still retrieve-then-speak.
- Sophia. User-Model vs Self-Model. Memory Module is still RAG.

## Field failure signals

Census cards read code and docs. User-reported breaks live in GitHub issues. Slice I protocol is `research/census/issue-mining.md`. Output is `research/census/issue-signals/<player-id>.md`. measured 2026-09-11.

| player | file | holes with new evidence |
| --- | --- | --- |
| mem0 | `issue-signals/mem0.md` | 4, 7, 8, 9 |
| letta | `issue-signals/letta.md` | 5, 7, 9 |
| graphiti | `issue-signals/graphiti.md` | 2, 5, 8, 10 |
| honcho | `issue-signals/honcho.md` | 1, 4, 8, 9 |

Use mined rows to draft holes 2, 7, 9, and 10 fixtures before calling sketch A human-like.

## What we must invent

The later protocol has to make these illegal as mixed strings.

1. User biographical fact, with provenance and supersession.
2. Character autobiographical event.
3. Relationship state as a phase, not a factoid.
4. Author lore, never lived unless the character lived it.
5. Session working memory.
6. OOC/meta, never mixed into IC recall.

Read policy is its own object. Embedding score is not permission to speak.

Write policy refuses jokes, hypotheticals, and jailbreaks as relationship facts.

The eval harness is the first implementation, not the engine. Baselines named in WORKFLOW.md. Mem0, Graphiti, Letta, Honcho, SillyTavern World Info plus vectors, naive RAG, long-context stuffing. Add Hindsight if the harness budget allows. measured as the closest PARTIAL engines.

## Check

`python3 research/_contracts/validate-cards.py` reports 76 cards valid. `summarize-cards.py` reports FIT none, 49 PARTIAL, 27 MISFIT. identity present honcho. silence present none. poison present none.
