# Anti-QA benchmarks

Reading path for Slice H3. JSON under `research/census/cards/` is the record. This file is the order to read them. measured from the brief.

Shared premise under test. If we retrieve the right past text or extracted facts into the prompt, the model will act as if it remembers the relationship. measured from CENSUS-RUBRIC.md.

These five papers attack Direct-QA-as-memory. That is why they are core. measured from EVAL-INGEST.md and `research/evals/registry.json`.

None is FIT. FIT needs scores for identity drift, silence, and poisoning together. measured from EVAL-INGEST.md. None of this slice scores all three. measured from the five cards.

Do not clone LoCoMo-Conv query styles, MemUse Natural Integration, MemoryArena gyms, PRAGMA guidance rubrics, or TANGLE's CAAP into a later engine. Census only. measured from CENSUS-RUBRIC.md.

Audience is whoever designs the later companion harness. measured from the brief.

## Overview

users-dont-ask and memuse set `assumes_retrieve_equals_remember` to no. measured from each methods section. They score in-situ use or satisfaction instead of a probe. measured. They still model assistant chat, not RP trauma, kink, or spoiler silence. Hole 2 is partial at best. measured from the cards.

MemoryArena also sets the premise to no. measured. Domain is interdependent agent tasks. measured from Table 1. companion_fit is MISFIT. measured. Steal the negative result that LoCoMo-class recall does not predict later action. measured from the abstract. The paper does not table matching LoCoMo scores for the Table 3 systems. measured.

PRAGMA is mixed. measured from registry and §5. It still retrieves then generates, but it also scores whether gold evidence is used for guidance. measured from Table 4 and Table 5. Lifelong assistant, not character identity. measured.

irreducible-conflict (TANGLE) sets the premise to no. measured. No single gold. measured from §3.4. Still personal-assistant prefs. Not user vs character vs narrator. measured.

## Ten companion holes

1. Identity drift after 50+ sessions. missed by all five. measured.
2. Fact recalled at a socially wrong time. partial on users-dont-ask (silent grounding, implicit queries) and memuse (Natural Integration vs Direct QA). partial on PRAGMA corrective queries as wrong-assumption handling. Still not trauma, kink, or spoilers. measured.
3. Joke stored as a relationship fact. missed. memuse negatives score fabricated recall when nothing was cued, which is over-eager use, not joke ontology. measured.
4. User retcon vs character lie vs narrator. adjacent on TANGLE only (CPC / BOC / SCC with no unique answer). Not three named writers. measured.
5. Cross-character leak. missed. measured.
6. Lorebook treated as a lived event. missed. measured.
7. Poisoned memory overrides system persona. missed. Counterfactual LoCoMo-Conv is a user-side false premise. SCC is source disagreement. Neither is a stored jailbreak. measured.
8. Cost per turn. present as a meter on memuse (Table 2 tokens and latency) and MemoryArena (Table 4 wall time). Neither is companion tokens-per-turn into a character prompt. measured.
9. Forget-that gone next turn. missed. measured.
10. Three-month reunion. adjacent on PRAGMA year-scale timestamps and memuse's four-month deployment. Neither scores "we have not spoken in three months" for a companion character. measured.

## How it works

### users-dont-ask (LoCoMo-Conv)

Start here. It is the cleanest rewrite of LoCoMo's probe into first-person use. measured from Table 1.

**Loop.** measured. Keep LoCoMo10 memories and gold evidence. Rewrite each QA as dialog, implicit, counterfactual, or composed. Retrieve top-10. Judge free-form replies with fact_used. Paper Table 9. 1,986 dialog, 1,986 implicit, 1,540 counterfactual, 1,069 composed clusters. Repo `MiuLab/LoCoMo-Conv`. 0 stars on 2026-09-11. measured from gh api.

**Premise.** no, measured. The user often never asks for the fact. §7.3 silent grounding. Oracle memory still lifts faithfulness +55.1 and engagement +31.0 on 332 implicit cases where fact_used is 0.

**Eval.** measured. Table 4. AnchorMem dialog recall@10 0.659 / fact_used 0.598. Implicit recall 0.368. mem0 implicit recall 0.456 and dialog fact_used 0.366. Retrieval does not equal a grounded reply. Multi-facet rewriting helps raw-turn memory (AnchorMem implicit +15.6 recall) and barely moves abstractive mem0 / Memora.

**Fit.** PARTIAL. measured.

**Repo note.** measured. No LICENSE file. LoCoMo10 source is CC BY-NC 4.0. Judges are vendor APIs.

### memuse

Read next. It is the measured split between Direct QA and what users actually rate. measured from §4 and §6.

**Loop.** measured. 40 users talked to Luke (GPT-4.1-mini) for four months. 1,872 sessions. Seven capacity conditions. MemUse is 72 real user-cued moments with 316 fact questions. Score Natural Integration on the natural reply, Direct QA on the same context, and Reference of those facts in the reply. 72 negatives catch fabricated recall.

**Premise.** no, measured. Abstract. Direct QA 19.7% to 70.1% across conditions. Satisfaction does not change (deltas vs Summary under 0.06 SD). Same model and context. Direct QA 78.8% vs Reference 7.9%. Spearman rho=-0.009 on 207 pairs.

**Eval.** measured. Natural Integration on 48 memory-moment sessions correlates with rating_z at +0.289 (any-success). The LMM is p=0.082. Treat that association as conditional. measured from Appendix Table 16 and the paper's own Bonferroni note.

**Fit.** PARTIAL. measured.

**Repo note.** measured. `ryuichi-sumida/memuse`, 3 stars. Code MIT. Data CC BY-NC 4.0. HF `RuiSumida/memuse`. Paper used 73 instances. Public set is 72.

### memoryarena

Read for the negative result, then stop. measured from the brief.

**Loop.** measured. Multi-session Memory-Agent-Environment tasks. Shopping, group travel, progressive search, formal reasoning. Table 1. 766 tasks, 6.9 subtasks, 57 steps. Site `https://memoryarena.github.io/`. Code `ZexueHe/MemoryArena`, 60 stars. Data `ZexueHe/memoryarena`.

**Premise.** no, measured. Recall benches score memorization. This gym scores whether earlier actions and feedback, once stored, drive later actions.

**Eval.** measured. Table 3. All methods low SR. Group travel near 0. GPT-5.1-mini long-context all-task avg SR 0.16. Letta 0.15, Mem0 0.14. Table 4. External memory is slower (Letta 132.8s avg vs GPT-5.1-mini 74.2s). Abstract claims LoCoMo-saturated agents still fail here. Matching LoCoMo numbers are not in Table 3. measured.

**Fit.** MISFIT. measured.

**Repo note.** measured. No license on GitHub or Hugging Face as of 2026-09-11. README wants vendor memory APIs.

### pragma

Read for guidance plus memory alignment. Not for character identity. measured from Table 1 and the brief. Not Revolut banking PRAGMA 2604.08649. measured from the abs id 2609.09664.

**Loop.** measured. 100 users, 400 queries, about 160K tokens per history. Four types. Event-Align, Event-Correct, Traj-Align, Traj-Correct. Retrieve evidence sessions. GPT-5 judges alignment and grounding. HF `stellahj/PRAGMA`. Code `yuhyojeong/PRAGMA`, 0 stars.

**Premise.** mixed, measured. Systems still retrieve then speak. Table 4. Oracle-Session is far below Oracle-Summary (Traj-Align grounding 17 vs 86 under gpt-5-mini). Table 5. Query rewriting can recover Traj-Align Exact Recall 80 and still score alignment 25. Gold retrieval is not enough.

**Eval.** measured. Table 3. A-MEM Traj-Align alignment 81, grounding 16. Event-Correct alignment 2 to 8 on practical systems. Full-context Traj-Align grounding 8. Table 7. A-MEM preserves 99.1% of Traj-Correct evidence and retrieves 48.9%.

**Fit.** PARTIAL. measured.

**Repo note.** measured. Dataset NVIDIA License, non-commercial. GitHub code has no LICENSE.

### irreducible-conflict (TANGLE)

Read last for hole 4's shape. measured from §3.

**Loop.** measured. 541 instances, 40 personas, CPC / BOC / SCC. Oracle track feeds curated memory. Pipeline track runs Letta, Mem0, A-mem, MemOS on verbalized multi-session chat. Rubric D1-D5 (0-4). Perception, causal reasoning, calibration, clarification, faithfulness. Action set includes commit, conditionalize, clarify, verify, defer, reversible_trial.

**Premise.** no, measured. Forcing one gold is the bug. The query withholds the variable that would resolve the conflict.

**Eval.** measured. Oracle totals under GPT-5.4. CPC 14.79, SCC 11.92, BOC 10.81. D4 is the bottleneck for every model. Pipeline FULL preservation. Letta 91.7%, Mem0 69.1%, A-mem 47.0%, MemOS 46.2%. Judges Pearson r=0.838 on 2,705 responses.

**Fit.** PARTIAL. measured.

**Repo note.** measured. search_paper_text for github.com, huggingface, license, and release returned nothing. Web search on 2026-09-11 found no official code repo. Dataset license unknown.

## What to steal

Score the reply the user actually sees, not a quiz. measured from LoCoMo-Conv and MemUse.

Direct QA can rise while satisfaction and in-conversation reference stay flat. measured from MemUse §4 and §6.2.

A recall leaderboard does not predict later action. measured from MemoryArena's claim. Use it as a warning, not as a companion gym. inferred from companion_fit MISFIT.

Guidance needs both evidence recovery and use. measured from PRAGMA Tables 4-5.

Some conflicts have no winner. Ask, hold, or qualify. measured from TANGLE. Do not treat that as user vs character vs narrator. measured.

## Verdict table

| id | companion_fit | one-line reason |
| --- | --- | --- |
| users-dont-ask | PARTIAL | In-situ LoCoMo use and silent grounding. Not trauma silence, identity, or poisoning. measured. |
| memuse | PARTIAL | Direct QA diverges from Natural Integration and satisfaction. Diary assistant, not RP. measured. |
| memoryarena | MISFIT | Interdependent agent tasks. Recall saturation does not predict action. Not a companion. measured. |
| pragma | PARTIAL | Lifelong assistant guidance and corrective alignment. Not character identity. measured. |
| irreducible-conflict | PARTIAL | No single gold among prefs, time, and sources. Not three writers. measured. |
