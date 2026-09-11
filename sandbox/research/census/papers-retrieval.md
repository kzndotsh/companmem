# Retrieval papers

Reading path for Slice G retrieval cards. JSON under `research/census/cards/` is the record. This file is the order to read them. measured from the brief.

Shared premise under test. If we retrieve the right past text or extracted facts into the prompt, the model will act as if it remembers the relationship. measured from CENSUS-RUBRIC.md.

None of these four is FIT. FIT needs typed user vs character vs relationship, silence, and a poisoning block. measured from the rubric and the cards.

Do not clone HippoRAG PPR, A-MEM note evolution, MEM1 IS XML, or MemGPT core/recall/archival into a later engine. Census only. measured from PAPER-INGEST.md.

## Verdict table

| id | companion_fit | one-line reason |
| --- | --- | --- |
| hipporag | MISFIT | Multi-hop passage RAG. No companion types, silence, or poisoning controls. measured. |
| a-mem | MISFIT | LoCoMo agent RAG with evolving notes. Still retrieve-then-generate. LoCoMo does not score identity, silence, or poisoning. measured. |
| mem1 | MISFIT | Web and multi-hop QA agent with a learned prompt summary. Not a companion store. measured. |
| memgpt | PARTIAL | Historical chat agent with user/persona working context. Silence absent. Agent can poison persona. Current Letta is MemFS. Do not implement the tiers. measured. |

## Overview

All four still remember by putting text in the next prompt. measured from methods sections.

HippoRAG and A-MEM retrieve then generate. measured. MEM1 searches the environment, writes a compact IS, then speaks. measured. That is still retrieve-then-generate, inferred from the shared premise sentence. MemGPT pages recall or archival into main context, which the paper calls virtual context. measured. `assumes_retrieve_equals_remember` is yes on all four, measured from each methods section.

Current Letta is MemFS. The memgpt card is historical. measured from PAPER-INGEST.md and the letta product card.

## Key concepts

**Open KG is not ontology.** HippoRAG noun phrases are extraction units. They are not user bio, character autobiography, or relationship state. measured from paper §2.3.

**Note metadata is not identity split.** A-MEM keywords, tags, and context are LLM labels on one note bag. measured from MemoryNote.

**Discard is not silence.** MEM1 drops prior observations to bound tokens. That is not a social skip of a high-score memory. measured from paper §3.1.

**Working context is two blobs.** MemGPT stores user facts and persona in one writeable block. measured from paper §2.1. Relationship is not a type. measured.

## How it works

### HippoRAG

Start here if you need the hippocampal-index story.

**Loop.** measured. Offline OpenIE builds a schemaless KG. Online query NER links to nodes. `HippoRAG.rank_docs` and `run_pagerank_igraph_chunk` in `src/hipporag.py` on the `legacy` branch run Personalized PageRank and return passages. `HippoRAG.retrieve` and `run_ppr` on current main are HippoRAG 2.

**Premise.** yes, measured. Ranked passages go to a QA reader.

**Eval.** measured. 2Wiki R@5 89.1 versus ColBERTv2 68.2 (Table 2). Multi-hop passage recall and QA F1. Not companion identity.

**Fit.** MISFIT. measured.

**Repo note.** measured. `OSU-NLP-Group/HippoRAG` main is HippoRAG 2. Paper 2405.14831 is v1 on `legacy`. MIT. 3999 stars on 2026-09-11.

### A-MEM

Read next. It is the LoCoMo memory paper in this slice. measured from paper §4.

**Loop.** measured. `AgenticMemorySystem.add_note` builds a `MemoryNote`, links neighbors, and may evolve their context. `search` / `HybridRetriever.retrieve` returns top-k into the agent prompt. Production code is `WujiangXu/A-mem-sys` `agentic_memory/memory_system.py`. Benchmark code is `WujiangXu/A-mem` `memory_layer.py`.

**Premise.** yes, measured. Retrieved notes are the remember path.

**Eval.** measured. GPT-4o-mini temporal F1 45.85 on LoCoMo versus MemGPT 25.52 (Table 1). DialSim F1 3.45 (Table 2). LoCoMo is two-speaker friend-chat fact QA. It does not score companion identity, silence, or poisoning. measured from the locomo card and Maharana et al.

**Fit.** MISFIT. measured.

**Repo note.** measured. A-mem 963 stars, A-mem-sys 394 stars, both MIT.

### MEM1

Read for constant-size working memory, not for a store. measured from paper §3.

**Loop.** measured. Paper Algorithm 1 keeps only the latest internal state, query, and info. `Mem1/train/rollout/llm_agent/generation_think.py` `_extract_think_and_response` pulls the think span. Issue 10 says training truncation may not match that paper claim, measured from the issue thread. That discrepancy is an open unknown, measured from the card.

**Premise.** yes, measured. The agent still acts from whatever text remains in the prompt.

**Eval.** measured. 16-objective HotpotQA+NQ EM 1.97 versus Qwen2.5-14B-Instruct 0.567, with about 3.7x lower peak tokens (Table 1). WebShop reward 70.87 (Table 2). Multi-hop QA and web shopping, not companion identity.

**Fit.** MISFIT. measured.

**Repo note.** measured. Official repo is `MIT-MI/MEM1` (paper HTML). MIT. 335 stars. Project site has no llms.txt (404, measured).

### MemGPT

Read last, and only as history. measured from PAPER-INGEST.md.

**Loop.** measured. Working context plus FIFO queue in the prompt. Recall and archival outside. Functions `core_memory_append`, `core_memory_replace`, `archival_memory_search`, `conversation_search` on `letta-ai/letta` archive `letta/functions/function_sets/base.py`. Paper released code at https://research.memgpt.ai. That site has no llms.txt (404, measured).

**Premise.** yes, measured. Virtual context is retrieve or page, then generate.

**Eval.** measured. DMR on MSC, GPT-4 Turbo 93.4% (Table 2). Session-6 fact probe about sessions 1-5. Not identity drift, silence, or poisoning.

**Fit.** PARTIAL. Closest of the four to a long-lived chat person. Still no silence. The agent can write a jailbreak into working context. Current Letta is MemFS. Do not implement core/recall/archival. measured from PAPER-INGEST.md and the letta card.

**Repo note.** measured. `letta-ai/letta` Apache-2.0, 24699 stars. Same tree as the product card. This card describes 2023 MemGPT, not MemFS.

## Gotchas

HippoRAG GitHub README is HippoRAG 2. Mixing v2 delete APIs into the v1 card would be a miss. measured.

A-MEM "wins LoCoMo" in ranking tables. That bench is fact QA on simulated friend chat. measured.

MEM1 paper and training code may disagree on how IS is stored. measured from issue 10.

MemGPT numbers in later vendor blogs are not this paper's DMR table. Use Table 2. measured.

## Worker report

PASS. Four valid academic cards. Primary sources named for every non-unknown dimension. Markdown labels measured/inferred/guess in the same sentence as each claim. measured after validate-cards.py.
