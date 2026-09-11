# Memory-ops benchmarks

Reading path for Slice H1. Four core evals that score write, update, organization, or post-retrieval use. They are not companion engines.

Cards are `research/census/cards/halumem.json`, `structmemeval.json`, `memoryagentbench.json`, and `memtrapbench.json`.

## Shared premise

Most memory benches still assume that if the right past text is in the prompt, the model will act as if it remembers. HaluMem scores the store operations. StructMemEval scores how the store is organized. MemoryAgentBench still mostly injects then asks. MemTrapBench scores traps after the retrieved text is already relevant. That last one is the direct attack on the premise.

## HaluMem

Primary sources used this session are arXiv 2511.03506 v3, https://github.com/MemTensor/HaluMem, and https://huggingface.co/datasets/IAAR-Shanghai/HaluMem. Measured.

The bench is user-centric human-AI assistant chat, not RP. Measured. Twenty synthetic users. Measured. HaluMem-Medium is 30,073 turns, 69.35 sessions, and about 160k tokens per user. Measured. HaluMem-Long is the same users stretched to 53,516 turns and about 1.01M tokens with inserted distractor dialogues. Measured.

Three tasks are memory extraction, memory updating, and memory question answering. Measured. Ground-truth types are persona, event, and relationship. Measured. 14,948 memory points and 3,467 questions. Measured. Question types include memory boundary (828, abstain on unknown) and memory conflict (769, reject a wrong premise in the query). Measured.

Closest public bench to hole 7 is this one, as operation-level fabrication, error, conflict, and omission at extract and update. Measured. That is not a stored jailbreak that later overwrites a companion system persona. Inferred from the task definitions. Judge and answer generation default to GPT-4o. Measured.

Table 3 Medium MemOS extraction F1 is 79.70, update correct 62.11, QA correct 67.23. Measured. All listed systems stay below 70% QA accuracy. Measured. Long Mem0 extraction recall falls to 3.23%. Measured. Table 5 reports wall-clock minutes, not cost per turn. Measured.

License on LICENSE.txt and the HF card is CC-BY-NC-ND-4.0. Measured. GitHub SPDX is NOASSERTION. Measured. Stars 160 on 2026-09-11. Measured.

`assumes_retrieve_equals_remember` is mixed. Inferred from scoring extract and update as first-class tasks while QA still retrieves 20 memories into GPT-4o.

Companion holes missed are 1 identity drift of a companion character, 2 socially wrong timing, 3 joke stored as relationship fact, 4 retcon vs lie vs narrator, 5 cross-character leak, 6 lore vs lived, 7 planted persona overwrite, 8 cost per turn, 9 forget-that, 10 three-month reunion. Measured against the taxonomy. Session count passes 50. The metric still scores user-fact hallucination, not character identity. Inferred.

## StructMemEval

Primary sources used this session are arXiv 2602.11243 v3 and https://github.com/yandex-research/StructMemEval. Measured. Official repo is named in the paper. Measured.

The bench asks whether an agent organizes long synthetic histories the way a human notepad would. Measured. Four scenario families are trees, count-based settlements, state tracking, and recommendation aggregates. Measured. 207 scenarios and over 2,000 questions. Measured. Main comparison set is 51 longest problems, each at least 250 messages. Measured.

Retrieval-only agents collapse once the structure no longer fits the retrieval window. Measured. Paper Table 1 uses gemini-3.1-pro. Measured. Mem-agent total is 0.55, retrieval is 0.06, Mem0 is 0.30. Measured. The count-based column is 0.00 for every listed agent. Measured. Optional organization hints help but do not solve the bench. Measured.

The useful companion takeaway is the organization metrics. Inferred. Score whether the store keeps a graph, a netted ledger, a state machine, or a running preference statistic. Inferred. Still not RP. Measured.

License is Apache-2.0. Measured. README requires an OpenAI embedder key. Measured. Stars 12 on 2026-09-11. Measured.

`assumes_retrieve_equals_remember` is mixed. Inferred. The point of the bench is that retrieve-then-QA is not enough, and the score is still a later factual question.

Misses holes 1 through 10 listed above. Measured against the scenario list.

## MemoryAgentBench

Primary sources used this session are arXiv 2507.05257 v4, https://github.com/HUST-AI-HYZ/MemoryAgentBench, and https://huggingface.co/datasets/ai-hyz/MemoryAgentBench. Measured. ICLR 2026. Measured.

Paper competencies are accurate retrieval, test-time learning, long-range understanding, and selective forgetting. Measured. Table 1 claims 2,071 questions and 103k to 1.44M context depth. Measured. Inputs are existing long-context sets chunked into incremental turns, plus EventQA and FactConsolidation. Measured.

Selective forgetting builds MQUAKE counterfactual edit pairs so a later rewritten fact should overwrite an earlier true one. Measured. Search of the paper for "forget that" returned no hits. Measured. Hole 9 adjacent, not a companion user forget request. Inferred.

Paper Table 3 overall scores are GPT-5-mini 60.6, Claude-3.7-Sonnet 49.6, and GPT-4o 48.8. Measured. MemGPT is 28.3, MIRIX is 26.2, Mem0 is 21.1. Measured. Multi-hop FactConsolidation stays at most 28.0. Measured.

Repo LICENSE is MIT. Measured. HF card license is mit. Measured. Paper ethics also promised CC BY 4.0 for datasets. Measured. README Overview heading still says LongMemEval Overview and lists Conflict Resolution. Measured. Using the paper names. Inferred.

`assumes_retrieve_equals_remember` is yes. Inferred from chunk ingest then probe, including reconstructed LongMemEval.

Misses holes 1 through 10 as companion holes. Measured. SF is the only adjacent item, and it is world-fact overwrite, not forget-that. Inferred.

## MemTrapBench

Primary sources used this session are arXiv 2608.20202 v1 and https://github.com/zjunlp/MemTrapBench. Measured. Paper names that GitHub URL. Measured.

1,050 instances. Measured. 350 Cognitive Bias, 350 Task Boundary, 200 Safety, 150 Trauma. Measured. Two categories are Reasoning Fixation and Belief Distortion. Measured. Final query is solvable without history. Measured.

Even faithfully recorded, semantically relevant memories can drop current-task score. Measured. Gemini-3-Flash-Preview wo/Mem 85.16, EverMemOS 71.17. Measured. Qwen3-30B wo/Mem 81.83, LightMem 70.13. Measured. All listed memory strategies underperform no-memory. Measured. Table 3 Task Boundary trap average 31.05 versus no-trap 94.39. Measured.

Trauma is named as a behavioral analogy for feedback-induced avoidance, not companion trauma silence. Measured. Safety plants a counterfactual or sandbox premise and checks whether it overrides a straightforward safety judgment. Measured. Adjacent to hole 7. Not a stored jailbreak of system persona. Inferred.

`assumes_retrieve_equals_remember` is no. Measured from the trap design. Correct retrieval can still be the wrong use.

No LICENSE file in the repo. Measured. GitHub license field is null. Measured. Stars 5 on 2026-09-11. Measured.

Misses holes 1, 2, 3, 4, 5, 6, 7 as persona overwrite, 8, 9, and 10. Measured against the four scenarios.

## Verdict

None of these four is FIT. FIT would need identity drift, silence, and poisoning together. None score that set.

| id | companion_fit | reason |
| --- | --- | --- |
| halumem | PARTIAL | Operation-level hallucination on user persona, event, and relationship points. Not character identity, social silence, or a stored persona jailbreak. |
| structmemeval | PARTIAL | Scores store structure. Steal organization metrics. Still not RP. |
| memoryagentbench | MISFIT | Incremental agent tasks and MQUAKE overwrite. Not companion forget-that, identity, silence, or poisoning. |
| memtrapbench | PARTIAL | Scores traps after relevant retrieval. Not typed retcon or a companion persona overwrite. |
