# Eval grid

Counts from [`EVAL-INVENTORY.md`](EVAL-INVENTORY.md) only. Each cell is one eval. `y` means that file states the score rule. `u` means the thing is named and the score rule on that row is unknown. `.` means no inventory row for this label.

Same words are not the same test. Temporal F1, temporal judged by a model, and temporal retrieval stay on different rows.

BEAM abilities other than event ordering are `y` when the ability is named and the inventory says the score for every other ability is the mean of the rubric items.

LongMemEval-V2 premise awareness is `y` because that row says the model must identify a wrong premise, and the static-state row says accuracy is reported per category with a judge.

**Status:** exploratory. This is not our exam. A user thumbs-up is not the exam either. On Claude feedback chats, moderate or severe disempowerment potential got a higher thumbs-up rate than baseline ([Sharma et al.](https://arxiv.org/abs/2601.19062)). The rates and the potential-versus-actualized split are in [`INSIGHTS.md`](INSIGHTS.md) and under "how do you know if memory is working" in [`QUESTIONS.md`](QUESTIONS.md).

## Grid

| Test | loco | lme | lmc | mab | pm | halu | atm | ab | harb | m2a | real | esm | atod | beam | dial | dule | engr | lmeb | lmv2 | memb | mara | mbank | msc | pltq | pref | y | u |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Answer vs gold, token F1 | y | . | . | . | . | . | . | . | . | . | . | y | . | . | . | . | y | . | . | . | . | . | . | . | . | 3 | 0 |
| Answer vs gold, exact or substring match | . | . | . | y | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | y | . | . | . | . | y | 3 | 0 |
| LLM judge on the reply | . | y | y | y | . | y | y | . | . | . | y | y | . | y | . | . | . | . | y | . | . | . | . | . | . | 9 | 0 |
| Retrieval rank | y | y | . | y | . | . | y | . | . | . | y | y | . | . | . | . | . | y | . | . | . | u | . | y | . | 8 | 1 |
| Temporal item, token F1 | . | . | . | . | . | . | . | . | . | . | . | y | . | . | . | . | y | . | . | . | . | . | . | . | . | 2 | 0 |
| Temporal item, LLM judge | . | y | . | . | . | . | . | . | . | . | . | y | . | y | . | . | . | . | . | . | . | . | . | . | . | 3 | 0 |
| Temporal item, named only | u | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | u | . | . | . | . | . | 0 | 2 |
| Temporal item, retrieval rank | . | . | . | . | . | . | . | . | . | . | y | . | . | . | . | . | . | . | . | . | . | . | . | . | . | 1 | 0 |
| Knowledge update, LLM judge | . | y | . | . | . | y | . | . | . | . | . | . | . | y | . | . | . | . | . | . | . | . | . | . | . | 3 | 0 |
| Knowledge update, retrieval rank | . | . | . | . | . | . | . | . | . | . | y | . | . | . | . | . | . | . | . | . | . | . | . | . | . | 1 | 0 |
| Knowledge update, score unknown | . | . | . | . | . | . | u | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | 0 | 1 |
| Abstention or false premise | u | u | . | . | . | . | u | . | . | . | . | y | . | y | u | . | y | . | y | . | . | . | . | . | . | 4 | 4 |
| Preference followed | . | y | . | . | u | . | . | y | . | . | . | . | . | y | . | . | . | . | . | u | . | . | . | . | y | 4 | 2 |
| Multi-hop or multi-session answer | y | u | y | . | . | u | . | . | . | . | . | y | . | y | . | . | . | . | . | . | . | . | . | . | . | 4 | 2 |
| Summarization | u | . | . | y | . | . | . | . | . | . | . | y | . | y | . | . | . | . | . | . | . | . | u | . | . | 3 | 2 |
| Contradiction or conflict | . | . | . | y | . | . | . | y | . | u | . | . | . | y | . | . | . | . | . | . | . | . | . | . | . | 3 | 1 |
| Event ordering | . | . | . | . | . | . | . | . | . | . | . | . | . | y | . | . | . | . | . | . | . | . | . | . | . | 1 | 0 |
| Tool call or finished action | . | . | . | . | . | . | . | . | . | y | . | . | y | . | . | . | . | . | . | . | y | . | . | . | . | 3 | 0 |
| Latency or cost | . | . | . | . | . | . | . | . | y | . | . | . | . | . | y | . | . | . | y | y | . | . | . | . | . | 4 | 0 |
| Written-anchor rating | . | . | . | . | . | . | . | y | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | 1 | 0 |

Slug columns, in seed order: loco is locomo, lme is longmemeval, lmc is locomo-conv, mab is memoryagentbench, pm is personamem, halu is halumem, atm is atm-bench, ab is assistant-benchmark, harb is harbor, m2a is mem2actbench, real is realmem, esm is es-memeval, atod is atod, beam is beam, dial is dialsim, dule is dulemon, engr is engramabench, lmeb is lmeb, lmv2 is longmemeval-v2, memb is membench, mara is memoryarena, mbank is memorybank, msc is msc, pltq is perltqa, pref is prefeval.

## What the counts say

Agreement here means 5 or more evals with `y` on that row. That cutoff is a reading rule for this table. It is not a property of the benchmarks. No row is `y` for all 25.

### Agreement

- **LLM judge on the reply.** 9 evals. A model marks the reply correct, or scores a rubric. Evals: longmemeval, locomo-conv, memoryagentbench, halumem, atm-bench, realmem, es-memeval, beam, longmemeval-v2.
- **Retrieval rank.** 8 evals. Recall@k, NDCG, or capped recall of a retrieved item. Evals: locomo, longmemeval, memoryagentbench, atm-bench, realmem, es-memeval, lmeb, perltqa.

### Differences

These rows have one to four `y` cells.

- **Answer vs gold, token F1.** 3 evals. locomo, es-memeval, engramabench.
- **Answer vs gold, exact or substring match.** 3 evals. memoryagentbench, membench, prefeval.
- **Temporal item, token F1.** 2 evals. es-memeval, engramabench.
- **Temporal item, LLM judge.** 3 evals. longmemeval, es-memeval, beam.
- **Temporal item, retrieval rank.** 1 evals. realmem.
- **Knowledge update, LLM judge.** 3 evals. longmemeval, halumem, beam.
- **Knowledge update, retrieval rank.** 1 evals. realmem.
- **Abstention or false premise.** 4 evals. es-memeval, beam, engramabench, longmemeval-v2.
- **Preference followed.** 4 evals. longmemeval, assistant-benchmark, beam, prefeval.
- **Multi-hop or multi-session answer.** 4 evals. locomo, locomo-conv, es-memeval, beam.
- **Summarization.** 3 evals. memoryagentbench, es-memeval, beam.
- **Contradiction or conflict.** 3 evals. memoryagentbench, assistant-benchmark, beam.
- **Event ordering.** 1 evals. beam.
- **Tool call or finished action.** 3 evals. mem2actbench, atod, memoryarena. Mem2ActBench is yes because the anchor check has an exact or soft match. The separate tool-call row does not state a score formula, so it stays unjoined.
- **Latency or cost.** 4 evals. harbor, dialsim, longmemeval-v2, membench.
- **Written-anchor rating.** 1 evals. assistant-benchmark.

### Weak spots

A weak spot is a row with fewer than 5 `y` cells.

- **Answer vs gold, token F1.** 3 scored, 0 named only. Named only: none.
- **Answer vs gold, exact or substring match.** 3 scored, 0 named only. Named only: none.
- **Temporal item, token F1.** 2 scored, 0 named only. Named only: none.
- **Temporal item, LLM judge.** 3 scored, 0 named only. Named only: none.
- **Temporal item, named only.** 0 scored, 2 named only. Named only: locomo, membench.
- **Temporal item, retrieval rank.** 1 scored, 0 named only. Named only: none.
- **Knowledge update, LLM judge.** 3 scored, 0 named only. Named only: none.
- **Knowledge update, retrieval rank.** 1 scored, 0 named only. Named only: none.
- **Knowledge update, score unknown.** 0 scored, 1 named only. Named only: atm-bench.
- **Abstention or false premise.** 4 scored, 4 named only. Named only: locomo, longmemeval, atm-bench, dialsim.
- **Preference followed.** 4 scored, 2 named only. Named only: personamem, membench.
- **Multi-hop or multi-session answer.** 4 scored, 2 named only. Named only: longmemeval, halumem.
- **Summarization.** 3 scored, 2 named only. Named only: locomo, msc.
- **Contradiction or conflict.** 3 scored, 1 named only. Named only: mem2actbench.
- **Event ordering.** 1 scored, 0 named only. Named only: none.
- **Tool call or finished action.** 3 scored, 0 named only. Named only: none.
- **Latency or cost.** 4 scored, 0 named only. Named only: none.
- **Written-anchor rating.** 1 scored, 0 named only. Named only: none.

### Not in the inventory at all

No inventory line is this test.

- The same person after a gap, including their name and the relationship.
- Using one fact without pasting the whole memory store.
- Knowing a private fact and leaving it unsaid. Assistant Benchmark restraint scores whether the assistant acts on an email, a package, and a text. It is not this test.
- A fact told to one character does not appear with another character.

## Inventory rows not joined

Every inventory row not cited above stays a one-eval detail.

- **locomo.** Single-hop question; Commonsense or world knowledge question; Answer prediction; Multimodal dialog generation.
- **longmemeval.** Single-session user; Single-session assistant; Abstention during retrieval.
- **locomo-conv.** Implicit query; Counterfactual query; Pairwise reply quality.
- **memoryagentbench.** Signals the scorer can emit; LongMemEval(S*) question types; EventQA and FactConsolidation; Long-range understanding.
- **personamem.** Seven in-situ query types; No-context multiple choice; Ask to forget.
- **halumem.** Memory extraction; Memory extraction F1; Importance-weighted recall; Memory type breakdown.
- **atm-bench.** Personalized references; Location awareness; Multi-evidence composition; Oracle answer; Needle in a haystack.
- **assistant-benchmark.** Online tasks; Proactive behavior; Phone calls; Personality; Memory; Travel booking; Recommendation quality; Purchasing; Email; Routines; Connected apps; Permissions; Group chats; Chained tasks; Restraint; Images.
- **harbor.** Terminal-Bench 2.0; A trial's own tests.
- **mem2actbench.** Apply memory to an action; Tool call from long dialogue.
- **es-memeval.** Dialogue generation memory; Dialogue generation judges. Understanding and memory uses the same F1, BERTScore, and judge as information extraction, which is already counted.
- **atod.** Goal detection; Status tracking; Proactivity; Memory recall accuracy; Turn relevance and dialogue coherence; Turns to completion.
- **beam.** Information extraction; Instruction following.
- **dialsim.** Answer correctness; Calibrated accuracy; Fan quiz versus knowledge-graph questions; Three shows.
- **dulemon.** Long-term dialogue consistency; Dialogue engagingness.
- **engramabench.** Cross-space integration; Emergent insight; Composite.
- **lmeb.** Constituent retrieval sets; Four memory types. nDCG at 10 is the same retrieval-rank score as capped recall.
- **longmemeval-v2.** Dynamic state tracking; Workflow knowledge; Environment gotchas.
- **membench.** Capacity; Four memory settings. Effectiveness is the same multiple-choice accuracy as the exact-match cell.
- **memoryarena.** Full task success; Progressive search; Formal reasoning; Bundled shopping; Group travel planning.
- **memorybank.** Correctness; Contextual coherence; Ranking; Empathic reply, recall, and personality.
- **msc.** Multi-session chat.
- **perltqa.** Memory classification; Memory synthesis; Question groups.
- **prefeval.** Explicit preference; Implicit choice-based preference; Implicit persona-driven preference.

## Relation to QUESTIONS.md

`docs/QUESTIONS.md` has 128 top-level questions. 89 of them are about how we work, what words mean, the market, or the repo. An eval grid cannot answer those.

The other 39 ask what memory should do, or how we would tell. The grid covers 7 of those with a stated score. 9 are only nearby. 22 have no eval score. One, "how do you know if memory is working," is what this grid is for.

### Stated score

| QUESTIONS.md line | Question | Grid row | Scored evals |
| --- | --- | --- | --- |
| 202 | Speed tax of tool calls | Latency or cost | 4 |
| 217 | Cost and hardware | Latency or cost | 4 |
| 381 | How stored memory is retrieved | Retrieval rank | 8 |
| 407 | Two memories conflict | Contradiction or conflict | 3 |
| 532 | First exam task, preference later | Preference followed | 4 |
| 547 | Implicit fact shows up in the reply | LLM judge on the reply | 9 |
| 505 | Does event order matter | Event ordering | 1 |

### Nearby, not the question

| QUESTIONS.md line | Question | Why it is only nearby |
| --- | --- | --- |
| 66 | Remembering versus retrieving | Retrieval rank is scored. Remembering is not. |
| 307 | Behaviors that would count as "this knows me" | Preference later is scored by 4 evals. The other four behaviors in that list are not. |
| 373 | What should persist | HaluMem scores extraction. That row is not a shared grid label. |
| 386 | Unit of a memory | LMEB names episodic, dialogue, semantic, and procedural. It does not score which unit a companion should use. |
| 420 | Consistency | DuLeMon names consistency. The score script is not in the audit. |
| 425 | Is perfect recall desirable | Abstention is scored by 4 evals. That is the near test, not this question. |
| 539 | Proactive restraint task | Assistant Benchmark scores not acting on an email, a package, and a text. |
| 486 | Should the companion raise a memory without being asked | Unprompted preference use is scored by 4 evals. Raising some other memory unasked is not. |
| 553 | What failure looks like | Conflict is scored. A leak, a joke stored as fact, and a wrong name are not. |

### No eval score

| QUESTIONS.md line | Question |
| --- | --- |
| 71 | What belongs in memory versus only in the active turn |
| 76 | Log versus memory |
| 129 | When the model ignores retrieved memory |
| 133 | Should the system always retrieve |
| 283 | How relationships build continuity |
| 288 | What people expect when someone remembers them |
| 292 | Caring versus creepy |
| 299 | Facts about someone versus knowing them |
| 303 | What changes over weeks and months |
| 391 | Optional versus essential |
| 396 | What forget means |
| 414 | Who owns memories |
| 429 | What "you forgot" is usually about |
| 434 | Jokes, hypotheticals, and roleplay |
| 439 | Lore versus what happened in conversation |
| 444 | Two characters sharing one user's facts |
| 463 | When a stored fact is spoken versus left silent |
| 471 | What if the stored memory is false |
| 478 | What is dropped when memory is full |
| 492 | Can the user see and correct what was stored |
| 498 | What the companion remembers about itself |
| 557 | How to test "feels like they know me" |

The four behaviors in the "knows me" list with no score are the same gaps as lines 76, 292, 396, and 444. They are not a fifth missing pile.
