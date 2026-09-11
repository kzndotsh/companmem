# Lifecycle papers

Reading path for slice G2. Cards under `research/census/cards/` are the record. This file is the order to read them.

Shared premise under test. If we retrieve the right past text or extracted facts into the prompt, the model will act as if it remembers the relationship.

Assigned ids. `mi-memory`, `memorylace`, `ai-hippocampus`. Observed 2026-09-11.

## Overview

These three papers sit on the Personal-AI and survey side of the friend list. None is a companion engine with typed writers and silence. measured from the papers and repos.

Mi-Memory is a Xiaomi Darwin Agent technical report. It names Structure, Expansion, Evolution, and Deployment, then still serves by selecting evidence and generating. measured.

MemoryLACE is a TUM and inovex paper. It puts merge, supersession, and contradiction on atomic notes. Writers stay relation labels on one bag. measured.

The AI Hippocampus is a TMLR survey. Card it as a map. companion_fit is MISFIT because it is not a system. measured.

## Key concepts

**Lifecycle is not companion ontology.** measured. L0/L1/L2/SM and merge/update/contradict type granularity or evidence relations. They do not type user bio, character autobiography, relationship phase, lore, or OOC.

**Gates bound policy search, not recall manners.** measured. Mi-Memory gates accept or roll back strategy artifacts. They do not skip a high-score trauma hit.

**Evals still miss the ten holes.** measured from GAP-MAP plus the paper tables. LoCoMo, PersonaMem-v2, LongMemEval, BEAM, and StructMemEval score assistant fact, preference, or structured-state QA. They do not score identity drift, social silence, joke-as-fact, typed retcon, or stored-text persona overwrite.

## How it works

### Mi-Memory

Start here if you want Personal-AI lifecycle language.

**Contract.** measured from arXiv HTML 2607.18975 §3.1 and Table 3. Four artifact families. Typed evidence payloads, diagnostic traces, strategy artifacts, gate and rollback records.

**Store.** measured from Table 4 and §4.2. MemStack holds L0 facts, L1 summaries, L2 profile and corrections, SM session memory. Expansion adds PerceptionFact and FusedEvent. LiteMem Appendix G maps those onto `user/profile.md`, `entity/ethan.md`, daily logs, and Git history.

**Loop.** measured from §3.1 and Eq. 2-4. Admit observation. Write with W. Retrieve with R_sem, R_lex, R_exp. Pack C under budget B. Generate a grounded in selected E. Corrections go through U. E2MEND mutates only schema-bounded strategy artifacts after a gate.

**Premise.** mixed, measured. Lifecycle and gates exist. The serving path is still retrieve then speak.

**Eval.** measured from §8.1, the homepage, and README Results. MemStack LoCoMo 93.59%, PersonaMem-V2 57.24%, LongMemEval 87.47% against a reproduced MemBrain on the EverMemOS harness. E2MEND offline LoCoMo 75.58% to 94.74%. LiteMem 90.81% transfer, 90.0% retention versus no-memory 65.83%. Those benches are friend-chat and assistant preference QA. inferred they still miss holes 1, 2, 4, 6, 7 from GAP-MAP, because the paper never names those probes.

**Repo.** measured. `Darwin-Agent/Mi-Memory` MIT, 28 stars on 2026-09-11. Tree is homepage, PDF, MemFuse PDF, LICENSE. Not a MemStack runtime.

**Fit.** PARTIAL. typed layers and rollback help. No companion kinds. No silence. Poisoning left to platform ACL in §8.2.

| dimension | score | label | primary source |
| --- | --- | --- | --- |
| ontology | partial | measured | Table 4, §4.2 |
| write_policy | present | measured | W in §4.2, MemSense/MemFuse §5 |
| read_policy | present | measured | Eq. 2-3, Table 20 |
| supersession | present | measured | Table 4 L1 links, U in §4.2, LiteMem Git §7.2 |
| temporal | present | measured | §4.2 order, LiteMem Eq. 8 |
| identity_split | partial | measured | Appendix G `user/` vs `entity/` |
| silence | absent | measured | Table 20 packing, no skip |
| poisoning | partial | measured | §8.2 platform-level poisoning gap |
| forgetting | partial | measured | Table 20 forget constraints, §9 propagation-complete forgetting |
| cost_shape | present | measured | Table 12 MemStack vs LiteMem |
| local | partial | measured | LICENSE MIT, LiteMem §7, repo README |
| mcp | absent | measured | repo tree, paper |

### MemoryLACE

Read next. Closest paper to hole 4 and hole 9 in this slice.

**Store.** measured from §III-A. `m_i = (x_i, tau_i, z_i, p_i, a_i, R_i)`. Sparse graph with directed supersession and symmetric merge and contradiction.

**Writers.** measured from §III-B1. Speaker attribution is preserved as stated inside the restatement. z_i is entities, keywords, topics, locations. R_i is merge, supersession, contradiction. Not three named writers.

**Write.** measured from §III-B. 20-turn windows, overlap 2. g picks one of merge, update, contradict, no_action. Default linked-merge keeps both texts. Compact-merge drops originals. Default does not delete.

**Read.** measured from §III-C. Search active set A. Expand L(A_q) along supersession lineages (cap 80) and one-hop contradictions (cap 4). Pack 64 memories. Generate from lifecycle-ordered units.

**Premise.** mixed, measured. Relations change what is packed. The companion still speaks from retrieved units.

**Eval.** measured from Tables I-III. BEAM 100K overall 45.4% (Qwen3.5-4B) and 51.9% (Qwen3.5-9B). Hindsight 40.1% and 50.3%. StructMemEval overall 52.08% with state 100 and tree 100, count 0, recsys 8.33. Runtime 7 h 31 min versus Hindsight 22 h 30 min. BEAM scores ten assistant abilities. StructMemEval scores structured state. Neither scores companion silence or typed retcon.

**Repo.** measured. No official GitHub on 2026-09-11. license null. stars_observed null.

**Fit.** PARTIAL. Steal the relation set. Do not treat relation labels as companion writers.

| dimension | score | label | primary source |
| --- | --- | --- | --- |
| ontology | partial | measured | §III-A |
| write_policy | present | measured | §III-B, g and R |
| read_policy | present | measured | §III-C, R_hybrid and L(A_q) |
| supersession | present | measured | §III-B3 |
| temporal | present | measured | tau_i, Table IV ablation |
| identity_split | absent | measured | §III-B1 speaker attribution in x_i |
| silence | absent | measured | §III-C |
| poisoning | partial | measured | p_i turn ids, no trust tag |
| forgetting | partial | measured | inactive via supersession, no forget-that |
| cost_shape | present | measured | Table II |
| local | unknown | measured | no repo |
| mcp | absent | measured | paper HTML |

### The AI Hippocampus

Read last. Use it as a map.

**Covered families.** measured from §1 and Figure 1.

Implicit. Parametric Transformer memory. FFN key-value memories. Knowledge neurons. Hopfield-style association. ROME and MEMIT editing. Unlearning in §2.2.

Explicit. External RAG over text, vectors, and graphs. Long-context indexes in §3.

Agentic. STM as context-window thoughts (CoT, ToT, ReAct, Reflexion). LTM as facts, trajectories, user feedback, dialogues and personalization, including MemoryBank/SiliconFriend in §4.1.2. Multi-agent shared stores (A-MEM, DAMCS, IoA) in §4.2.

Multimodal. Video, navigation, embodied agents in §5.

**Ignored companion holes.** measured from §7 plus GAP-MAP. Future work is internals, long context versus RAG, dynamic adaptation, multimodal tokens. No axis for character drift, silence, joke-as-fact, user retcon versus character lie versus narrator, cross-character leak, lore versus lived event, stored-text persona overwrite, or three-month reunion.

**Repo.** measured. `bigai-nlco/LLM-Memory-Survey` MIT, 40 stars. LICENSE, empty README.md, memory.png. §7 says they do not ship a unified eval or an integrating platform.

**Premise.** yes, measured. Explicit and agentic sections describe retrieve then generate. The survey does not reject that sentence.

**Fit.** MISFIT. Survey, not an engine.

| dimension | score | label | primary source |
| --- | --- | --- | --- |
| ontology | absent | measured | §1 Figure 1 |
| write_policy | absent | measured | §7 no platform |
| read_policy | absent | measured | §3 RAG, §4.1 recall-then-act |
| supersession | absent | measured | §2.2 reviews others' editing |
| temporal | absent | measured | §4.4 metric list only |
| identity_split | absent | measured | §4.1.2 one-user assistants |
| silence | absent | measured | §7 |
| poisoning | absent | measured | §2.2 parametric unlearning only |
| forgetting | absent | measured | literature review, no engine |
| cost_shape | absent | measured | §4.4.2 general latency talk |
| local | absent | measured | GitHub tree |
| mcp | absent | measured | paper and repo |

## Verdicts

| id | companion_fit | reason |
| --- | --- | --- |
| mi-memory | PARTIAL | Personal-AI lifecycle with gates. Still retrieve then speak. Evals miss companion holes. measured. |
| memorylace | PARTIAL | Merge, supersession, contradiction on one note bag. Not typed writers. measured. |
| ai-hippocampus | MISFIT | TMLR survey map. No engine. Ignores silence and typed companion kinds. measured. |

No FIT. These three papers leave companion kinds, silence as permission, and poisoning blocks uncovered. inferred from these cards plus GAP-MAP.

PASS
