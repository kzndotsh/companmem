# Eval inventory

What each of the 25 evals in `research/pipeline/seed.json` tests, one section per eval. Quotes are copied from `research/output/by-eval/<slug>/audit.json`. This is an inventory. It is not our exam, and it is not a merged rule list.

**Status:** exploratory. If a cell says unknown, the audit did not state that fact.

A second pass checked the harvested pages in `.cache/by-eval/<slug>/docs`. Rows below include tests those pages state. A few of them are missing from `audit.json`. Those rows say so in the score cell.

Counts across these tables are in [`EVAL-GRID.md`](EVAL-GRID.md).

## locomo

The audit says questions are classified into five reasoning types: single-hop, multi-hop, temporal, commonsense or world knowledge, and adversarial.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Single-hop question | unknown | We classify questions into five distinct reasoning types to evaluate memory from multiple perspectives: single-hop, multi-hop, temporal, commonsense or world knowledge, and adversarial. | https://snap-research.github.io/locomo/ (Evaluation Framework section, Question Answering paragraph) |
| Multi-hop question | Named as a reasoning type. The multi-hop F1 function splits the answer on commas. | def f1(prediction, ground_truth): predictions = [p.strip() for p in prediction.split(',')] ground_truths = [g.strip() for g in ground_truth.split(',')] return np.mean([max([f1_score(predic... | https://github.com/snap-research/locomo/blob/3eb6f2c585f5e1699204e3c3bdf7adc5c28cb376/task_eval/evaluation.py (task_eval/evaluation.py, f1()) |
| Temporal question | unknown | We classify questions into five distinct reasoning types to evaluate memory from multiple perspectives: single-hop, multi-hop, temporal, commonsense or world knowledge, and adversarial. | https://snap-research.github.io/locomo/ (Evaluation Framework section, Question Answering paragraph) |
| Commonsense or world knowledge question | unknown | We classify questions into five distinct reasoning types to evaluate memory from multiple perspectives: single-hop, multi-hop, temporal, commonsense or world knowledge, and adversarial. | https://snap-research.github.io/locomo/ (Evaluation Framework section, Question Answering paragraph) |
| Adversarial question | unknown | We classify questions into five distinct reasoning types to evaluate memory from multiple perspectives: single-hop, multi-hop, temporal, commonsense or world knowledge, and adversarial. | https://snap-research.github.io/locomo/ (Evaluation Framework section, Question Answering paragraph) |
| Categories 1-4 answer prediction | Token-level F1. Category 5 is not F1. | if line['category'] in [2, 3, 4]:             all_ems.append(f1_score(output, answer))         elif line['category'] in [1]:             all_ems.append(f1(output, answer))         elif line['category'] in [5]:        ... | https://github.com/snap-research/locomo/blob/3eb6f2c585f5e1699204e3c3bdf7adc5c28cb376/task_eval/evaluation.py (task_eval/evaluation.py, eval_question_answering()) |
| Answer prediction | F1-score. Higher is better. | Results are based on F1-score for answer prediction; higher is better. | https://snap-research.github.io/locomo/ (Findings section, QA table caption) |
| Retrieval when RAG is on | Per-item recall stored next to F1 | if args.use_rag and len(recall) > 0:                 answers['qa'][i][model_key + '_recall'] = round(recall[i], 3) | https://github.com/snap-research/locomo/blob/3eb6f2c585f5e1699204e3c3bdf7adc5c28cb376/task_eval/evaluate_qa.py (evaluate_qa.py:80-81) |
| Event summarization | Unknown. The audit says the eval code is not released. | Evaluate models on the event summarization task — Coming soon! Train and evaluate MiniGPT-5 models on the multimodal dialog generation task — Coming soon! | https://github.com/snap-research/locomo/blob/3eb6f2c585f5e1699204e3c3bdf7adc5c28cb376/README.MD (README.MD, §Code) |
| Multimodal dialog generation | MM-Relevance score | Variation of MM-Relevance score with length of dialog history | https://snap-research.github.io/locomo/ (Findings section, multimodal figure caption (B)) |

## longmemeval

The audit says it evaluates memory and long-dialogue systems on single-session, multi-session, temporal reasoning, knowledge update, and preference recall.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Single-session user | unknown | if task in ['single-session-user', 'single-session-assistant', 'multi-session']: ... elif task == 'temporal-reasoning': ... elif task == 'knowledge-update': ... elif task == 'single-session-preference': | https://github.com/xiaowu0162/LongMemEval/blob/9e0b455f4ef0e2ab8f2e582289761153549043fc/src/evaluation/evaluate_qa.py (evaluate_qa.py:get_anscheck_prompt) |
| Single-session assistant | unknown | if task in ['single-session-user', 'single-session-assistant', 'multi-session']: ... elif task == 'temporal-reasoning': ... elif task == 'knowledge-update': ... elif task == 'single-session-preference': | https://github.com/xiaowu0162/LongMemEval/blob/9e0b455f4ef0e2ab8f2e582289761153549043fc/src/evaluation/evaluate_qa.py (evaluate_qa.py:get_anscheck_prompt) |
| Multi-session | unknown | if task in ['single-session-user', 'single-session-assistant', 'multi-session']: ... elif task == 'temporal-reasoning': ... elif task == 'knowledge-update': ... elif task == 'single-session-preference': | https://github.com/xiaowu0162/LongMemEval/blob/9e0b455f4ef0e2ab8f2e582289761153549043fc/src/evaluation/evaluate_qa.py (evaluate_qa.py:get_anscheck_prompt) |
| Temporal reasoning | Yes/no judge. An off-by-one count of days, weeks, or months is still correct. | do not penalize off-by-one errors for the number of days. If the question asks for the number of days/weeks/months, etc., and the model makes off-by-one errors (e.g., predicting 19 days when the answe... | https://github.com/xiaowu0162/LongMemEval/blob/9e0b455f4ef0e2ab8f2e582289761153549043fc/src/evaluation/evaluate_qa.py (evaluate_qa.py:get_anscheck_prompt, temporal-reasoning template) |
| Knowledge update | Yes/no judge. A reply that includes the old fact and the updated fact is correct if the update is the required answer. | If the response contains some previous information along with an updated answer, the response should be considered as correct as long as the updated answer is the required answer. | https://github.com/xiaowu0162/LongMemEval/blob/9e0b455f4ef0e2ab8f2e582289761153549043fc/src/evaluation/evaluate_qa.py (evaluate_qa.py:get_anscheck_prompt, knowledge-update template) |
| Single-session preference | Named as a question type in the same yes/no judge. | if task in ['single-session-user', 'single-session-assistant', 'multi-session']: ... elif task == 'temporal-reasoning': ... elif task == 'knowledge-update': ... elif task == 'single-session-preference': | https://github.com/xiaowu0162/LongMemEval/blob/9e0b455f4ef0e2ab8f2e582289761153549043fc/src/evaluation/evaluate_qa.py (evaluate_qa.py:get_anscheck_prompt) |
| Abstention | Named as one of five core abilities. | LongMemEval consists of 500 human-curated, high-quality questions to test five core memory abilities: information extraction, cross-session reasoning, temporal reasoning, knowledge updates, and abstention. | https://arxiv.org/html/2410.10813v1 (Section 1, Introduction) |
| Abstention during retrieval | Skipped. Those items have no ground-truth answer location. | for evaluating the retrieval, we always skip the 30 abstention instances. This is because these instances generally refer to non-existing events and do not have a ground truth answer location. | https://github.com/xiaowu0162/LongMemEval/blob/9e0b455f4ef0e2ab8f2e582289761153549043fc/README.md (README.md, Baseline Retrieval section) |
| Retrieval of the answer session | Recall@k and NDCG@k against human-annotated answer locations | As LongMemEval contains human-annotated answer location labels, intermediate retrieval metrics can be reported if the chat system exposes its retrieval results. In this paper, we report Recall@k and NDCG@k. | https://arxiv.org/html/2410.10813v1 (Section 3.4, Memory Recall) |
| Overall QA | Mean of binary labels, plus per-type accuracy | print('Accuracy:', round(np.mean([1 if x['autoeval_label']['label'] else 0 for x in logs]).item(), 4)) ... for k,v in qtype2acc.items(): print('\t{}: {} ({})'.format(k, round(np.mean(v), 4), len(v))) | https://github.com/xiaowu0162/LongMemEval/blob/9e0b455f4ef0e2ab8f2e582289761153549043fc/src/evaluation/evaluate_qa.py (evaluate_qa.py:main block, final print statements) |

## locomo-conv

The audit says it covers four query styles: dialog, implicit, counterfactual, and composed.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Dialog query | Partial fact-used LLM judge | LLM judges (score_fact_used_partial.py, score_counterfactual_3way.py, score_composed_atomic.py, hallucination, pairwise three-dimension judges, cross-judge agreement) | https://github.com/MiuLab/LoCoMo-Conv/blob/main/README.md (README.md, Repository layout) |
| Implicit query | Partial fact-used LLM judge | LLM judges (score_fact_used_partial.py, score_counterfactual_3way.py, score_composed_atomic.py, hallucination, pairwise three-dimension judges, cross-judge agreement) | https://github.com/MiuLab/LoCoMo-Conv/blob/main/README.md (README.md, Repository layout) |
| Counterfactual query | 3-way LLM judge | score_counterfactual_3way.py | https://github.com/MiuLab/LoCoMo-Conv/blob/1925e924c36e632283ea91f2212157829f4e0e45/README.md (README.md, Repository layout section and Typical pipeline section) |
| Composed query | Atomic judge per sub-memory | python response_eval/score_composed_atomic.py --responses_path <dir>/responses.json --multimem_path data/locomo10_multimem_full.json --output <dir>/composed_atomic.json | https://github.com/MiuLab/LoCoMo-Conv/blob/1925e924c36e632283ea91f2212157829f4e0e45/README.md (README.md, Typical pipeline section) |
| Pairwise reply quality | Three-dimension pairwise judge | Pairwise quality judge: claude-opus-4-7 ... pairwise three-dimension judges | https://github.com/MiuLab/LoCoMo-Conv/blob/1925e924c36e632283ea91f2212157829f4e0e45/README.md (README.md, Setup section and Repository layout section) |

## memoryagentbench

The audit says it evaluates agent memory, including test-time learning scored by exact match, and it does not name one score the paper used when the code emits several.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Test-time learning, five ICL sets | Accuracy by exact_match | TTL (ICL series) / ICL_banking, ICL_clinic, ICL_nlu, ICL_trec_coarse, ICL_trec_fine / Accuracy / `exact_match` | https://github.com/HUST-AI-HYZ/MemoryAgentBench/blob/fe1735de8cf8b9908e1e3d3b5612afc815698062/README.md (README.md, Clarification on Evaluation Metrics section, metric table) |
| Signals the scorer can emit | rougeL F1, rougeL recall, rougeLsum F1, rougeLsum recall, exact_match, substring_exact_match. Which one the paper uses is unknown. | rougeL_f1 rougeL_recall rougeLsum_f1 rougeLsum_recall exact_match substring_exact_match | https://github.com/HUST-AI-HYZ/MemoryAgentBench/issues/5 (https://github.com/HUST-AI-HYZ/MemoryAgentBench/issues/5) |
| LongMemEval(S*) question types | Per-type accuracy is printed. The audit does not state a separate rule per type here. | single-session-user: 0.2 (45)         temporal-reasoning: 0.2 (75)         knowledge-update: 0.2 (45)         multi-session: 0.0933 (75)         single-session-preference: 0.0333 (30)         single-session-assistant:... | https://github.com/HUST-AI-HYZ/MemoryAgentBench/issues/15 (https://github.com/HUST-AI-HYZ/MemoryAgentBench/issues/15) |
| EventQA and FactConsolidation | Newly constructed datasets. Score rule unknown in this audit. | We collected and reformulated data from previous benchmarks and datasets. ... We also newly constructed two datasets EventQA and FactConsolidation. | https://github.com/HUST-AI-HYZ/MemoryAgentBench/blob/main/README.md (README.md, LongMemEval Overview section) |
| Accurate retrieval | Accuracy, using substring exact match, on event_qa, ruler_qa1, and ruler_qa2. The published audit does not contain this row. | Accurate Retrieval / event_qa, ruler_qa1, ruler_qa2 / Accuracy / substring_exact_match | https://github.com/HUST-AI-HYZ/MemoryAgentBench/blob/main/README.md (harvested README, Clarification on Evaluation Metrics) |
| Conflict resolution | Accuracy, using substring exact match, on fact_mh and fact_sh. The published audit does not contain this row. | Conflict Resolution / fact_mh, fact_sh / Accuracy / substring_exact_match | https://github.com/HUST-AI-HYZ/MemoryAgentBench/blob/main/README.md (harvested README, Clarification on Evaluation Metrics) |
| Long-range understanding | Accuracy by exact match on detectiveQA. The published audit does not contain this row. | LRU / detectiveQA / Accuracy / exact_match | https://github.com/HUST-AI-HYZ/MemoryAgentBench/blob/main/README.md (harvested README, Clarification on Evaluation Metrics) |
| Recommendation | Recall at 5 on the recsys set. The published audit does not contain this row. | Recsys / recsys / Recall@5 / Recall@5 | https://github.com/HUST-AI-HYZ/MemoryAgentBench/blob/main/README.md (harvested README, Clarification on Evaluation Metrics) |
| LongMemEval subset | LLM-as-judge. The published audit does not contain this row. | Longmemeval / longmemeval / LLM-as-judge | https://github.com/HUST-AI-HYZ/MemoryAgentBench/blob/main/README.md (harvested README, Clarification on Evaluation Metrics) |
| InfBench summarization | F1 from an LLM judge, following HELMET. The published audit does not contain this row. | Infbench / infbench (summarization subset) / F1 (LLM-as-judge) / Following HELMET | https://github.com/HUST-AI-HYZ/MemoryAgentBench/blob/main/README.md (harvested README, Clarification on Evaluation Metrics) |

## personamem

The audit says 15 models are scored across 7 in-situ query types. It does not name those 7 types.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Seven in-situ query types | The audit says 15 models are scored across 7 types. It does not name the 7 types or the score rule. | We evaluate 15 state-of-the-art LLMs, including GPT-4.5, GPT-4.1, o4-mini, o3-mini, o1, Llama-4, DeepSeek-R1, Gemini-2, Gemini-1.5, Claude-3.7, and Claude-3.5, across 7 in-situ query types. | https://github.com/bowen-upenn/PersonaMem/blob/d07e6ade22e85e0e5d562247323a9c3e07553226/README.md (README.md, Performance Leaderboard section) |
| No-context multiple choice | A four-option floor of 25% is used. No-context accuracy is reported. | a frontier model with no conversation history scores 31.1% [27.1, 35.2] here against the 25% four-option floor, versus 49.2% on v1 | https://github.com/bowen-upenn/PersonaMem/issues/42 (section 'Summary') |
| Preference-application slices | Length of the option is associated with which choice is gold. Score rule beyond multiple choice is unknown. | A mechanism consistent with inspection: where the correct response *declines* to use a preference — a forgetting request, someone else's preference — the correct answer is a short acknowledgement while the distractors... | https://github.com/bowen-upenn/PersonaMem/issues/42 (section 'The length signal, by slice') |
| Ask to forget | No-context score can fall below the 25% chance floor. | On this supersession/forgetting axis, a frontier model with no context scores **14.3%** — well *below* chance, because it is drawn to whichever option sounds most personalized and those are the distractors. | https://github.com/bowen-upenn/PersonaMem/issues/42 (section 'Why we think the supersession/forgetting axis is still valuable') |

## halumem

The audit says it measures hallucination and memory performance of memory systems.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Memory extraction | Part of the three-task run. Zep cannot be scored on this task. | evaluate Mem0 on memory extraction, memory update, and memory QA tasks, and aggregate the results | https://github.com/MemTensor/HaluMem/blob/718f16ff0c83413b1c86fa83fc13cc1a639871f9/eval/README.md (eval/README.md §Running the Evaluation, step 2) |
| Memory update | Judge labels Correct, Hallucination, Omission, or Other | evaluate Mem0 on memory extraction, memory update, and memory QA tasks, and aggregate the results | https://github.com/MemTensor/HaluMem/blob/718f16ff0c83413b1c86fa83fc13cc1a639871f9/eval/README.md (eval/README.md §Running the Evaluation, step 2) |
| Memory question answering | Judge labels Correct, Hallucination, or Omission | evaluate Mem0 on memory extraction, memory update, and memory QA tasks, and aggregate the results | https://github.com/MemTensor/HaluMem/blob/718f16ff0c83413b1c86fa83fc13cc1a639871f9/eval/README.md (eval/README.md §Running the Evaluation, step 2) |
| Memory extraction F1 | Harmonic mean of target accuracy and recall | eval_results["overall_score"]["memory_extraction_f1"] = compute_f1(         precision=eval_results["overall_score"]["memory_accuracy"]["target_accuracy(all)"],         recall=eval_results["overall_score"]["memory_inte... | https://github.com/MemTensor/HaluMem/blob/718f16ff0c83413b1c86fa83fc13cc1a639871f9/eval/evaluation.py (eval/evaluation.py:aggregate_eval_results, lines ~171-174) |
| Importance-weighted recall | Golden memories are weighted by an importance number | memory_integrity_weighted_scores += 0.5 * item["memory_integrity_score"] * item["importance"]             memory_integrity_weighted_valid_num += item["importance"] | https://github.com/MemTensor/HaluMem/blob/718f16ff0c83413b1c86fa83fc13cc1a639871f9/eval/evaluation.py (eval/evaluation.py:aggregate_eval_results, lines ~116-117) |
| Memory type breakdown | Event, persona, and relationship memories are scored apart | "memory_type_accuracy": {                 "Event Memory": {                     "memory_integrity_acc": 0,                     "memory_update_acc": 0,                     "total_num": 0,                 },            ... | https://github.com/MemTensor/HaluMem/blob/718f16ff0c83413b1c86fa83fc13cc1a639871f9/eval/evaluation.py (eval/evaluation.py:main, lines ~244-254) |
| Question types | Listed types. The header quote does not give a separate score rule for each. | Basic Fact Recall / Dynamic Update / Multi-hop Inference / Generalization and Application / Memory Conflict / Memory Boundary | https://github.com/MemTensor/HaluMem/blob/main/README.md (README.md, Performance Across Question Types) |

## atm-bench

The audit says it is a benchmark for multimodal, multi-source personalized referential memory question answering over about four years.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Personalized references | Counted inside QS. Separate score formula unknown. | PR Personalized references … LA Location awareness … MUT Memory updates over time … ME Multi-evidence composition … ABS Abstention | https://atmbench.github.io/ (§What ATM-Bench Measures) |
| Location awareness | Counted inside QS. Separate score formula unknown. | PR Personalized references … LA Location awareness … MUT Memory updates over time … ME Multi-evidence composition … ABS Abstention | https://atmbench.github.io/ (§What ATM-Bench Measures) |
| Memory updates over time | Counted inside QS. Separate score formula unknown. | PR Personalized references … LA Location awareness … MUT Memory updates over time … ME Multi-evidence composition … ABS Abstention | https://atmbench.github.io/ (§What ATM-Bench Measures) |
| Multi-evidence composition | Counted inside QS. Separate score formula unknown. | PR Personalized references … LA Location awareness … MUT Memory updates over time … ME Multi-evidence composition … ABS Abstention | https://atmbench.github.io/ (§What ATM-Bench Measures) |
| Abstention | Counted inside QS. Separate score formula unknown. | PR Personalized references … LA Location awareness … MUT Memory updates over time … ME Multi-evidence composition … ABS Abstention | https://atmbench.github.io/ (§What ATM-Bench Measures) |
| Query score | Accuracy percent. Primary judge is gpt-5-mini. | ATM-Bench QS ↑ / ATM-Bench Recall@10 ↑ / ATM-Bench-Hard QS ↑ / ATM-Bench-Hard Recall@10 ↑ | https://github.com/JingbiaoMei/ATM-Bench/blob/ef4e5dff1a47ec71213a06e359f02753defa8fb1/README.md (README.md, Memory-System Baseline Results table header) |
| Recall at 10 | Reported for memory-system baselines | ATM-Bench QS ↑ / ATM-Bench Recall@10 ↑ / ATM-Bench-Hard QS ↑ / ATM-Bench-Hard Recall@10 ↑ | https://github.com/JingbiaoMei/ATM-Bench/blob/ef4e5dff1a47ec71213a06e359f02753defa8fb1/README.md (README.md, Memory-System Baseline Results table header) |
| Oracle answer | Ground-truth evidence ids are given. This is an upper bound on answering. | Oracle (upper bound using GT evidence IDs) | https://github.com/JingbiaoMei/ATM-Bench/blob/ef4e5dff1a47ec71213a06e359f02753defa8fb1/docs/reproducibility.md (reproducibility.md §Oracle (upper bound using GT evidence IDs)) |
| Needle in a haystack | Generation only, on a fixed evidence pool | A generation-only protocol for the hard split where each question includes a fixed evidence pool (niah_evidence_ids) guaranteed to contain the ground truth. niah_evaluate.py is a wrapper around the Oracle baseline: it... | https://github.com/JingbiaoMei/ATM-Bench/blob/ef4e5dff1a47ec71213a06e359f02753defa8fb1/docs/baseline.md (docs/baseline.md §NIAH / What it is / How it is implemented here) |

## assistant-benchmark

The audit says it covers 15 named dimensions, scored 1 to 10 after real use, except personality, which is not scored.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Online tasks | Book a hotel stay, scored 1-10 against written anchors | Book a hotel stay. Completes a real browser or web workflow end to end, not just advice. 21 tested | https://assistantbenchmark.com/dimensions#how (Dimension 1 row) |
| Proactive behavior | Flight day, unprompted. Scored 1-10. | Flight day, unprompted. Acts or nudges usefully without being asked every step. 7 tested | https://assistantbenchmark.com/dimensions#how (Dimension 6 row) |
| Phone calls | Make a real call and report back. Scored 1-10. | Makes real phone calls on your behalf and reports back. 1 tested | https://assistantbenchmark.com/dimensions#how (Dimension 12 row) |
| Personality | Not scored. Read from public quotes. | Subjective, so it is read from public quotes rather than scored. Public opinion only | https://assistantbenchmark.com/dimensions#how (Dimension 11 row) |
| Memory | Minimum of two probe scores when both run | Dimension 10 of 16 Memory | https://assistantbenchmark.com/dimensions/memory (dimension header) |
| Memory preference probe | Anchors at 3, 6, 7, and 10 for whether a stated preference is used later | Preference: forgets by next session; City: no usable trip memory or incoherent 3 … City: searches or books NY without asking/confirming city against prior Chicago plan (partial—understands ask, misses conflict) 6 … Pr... | https://assistantbenchmark.com/dimensions/memory (Anchors table) |
| Memory city probe | Anchors at 3, 6, 7, and 10 for whether a trip city conflict is caught | Preference: forgets by next session; City: no usable trip memory or incoherent 3 … City: searches or books NY without asking/confirming city against prior Chicago plan (partial—understands ask, misses conflict) 6 … Pr... | https://assistantbenchmark.com/dimensions/memory (Anchors table) |
| Travel booking | Book a flight and handle the trip. Scored 1-10 against written anchors. | 2 Travel booking Test: Book a flight and handle the trip. Finds, books and manages flights and hotels, including check-in and changes. | https://assistantbenchmark.com/dimensions#how (harvested dimensions page) |
| Recommendation quality | Pick a restaurant with constraints. Scored 1-10. | 3 Recommendation quality Test: Pick a restaurant with constraints. Relevance, taste and constraint-following when it suggests options. | https://assistantbenchmark.com/dimensions#how (harvested dimensions page) |
| Purchasing | Reorder a product on Amazon. Scored 1-10. | 4 Purchasing a product Test: Reorder a product on Amazon. | https://assistantbenchmark.com/dimensions#how (harvested dimensions page) |
| Email | Reply to a scheduling email. Scored 1-10. | 5 Responding to emails Test: Reply to a scheduling email. | https://assistantbenchmark.com/dimensions#how (harvested dimensions page) |
| Routines | Daily digest for a week. Scored 1-10. | 7 Running a routine Test: Daily digest for a week. | https://assistantbenchmark.com/dimensions#how (harvested dimensions page) |
| Connected apps | Three tools, one request. Scored 1-10. | 8 Third-party integrations Test: Three tools, one request. | https://assistantbenchmark.com/dimensions#how (harvested dimensions page) |
| Permissions | Scoped access and a hard rule. Scored 1-10. | 9 Permissions and privacy Test: Scoped access and a hard rule. | https://assistantbenchmark.com/dimensions#how (harvested dimensions page) |
| Group chats | Plan dinner in a group chat. Scored 1-10. | 13 Multiplayer / groups Test: Plan dinner in a group chat. | https://assistantbenchmark.com/dimensions#how (harvested dimensions page) |
| Chained tasks | Flight check-in chain. Scored 1-10. | 14 Chained tasks Test: Flight check-in chain. | https://assistantbenchmark.com/dimensions#how (harvested dimensions page) |
| Restraint | Know when not to. Scored 1-10. The evening script is not in this dimensions-page quote. | 15 Proactive restraint Test: Know when not to. | https://assistantbenchmark.com/dimensions#how (harvested dimensions page) |
| Images | Make something for the group. Scored 1-10. | 16 Content creation / games Test: Make something for the group. | https://assistantbenchmark.com/dimensions#how (harvested dimensions page) |

## harbor

The audit says Harbor is a framework for evaluating agents and language models, and the official harness for Terminal-Bench 2.0.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Terminal-Bench 2.0 | Harbor is the official harness. The audit does not list that benchmark's tasks. | Harbor is the official harness for Terminal-Bench-2.0 | https://github.com/harbor-framework/harbor/blob/2993946dd5b64a46dac3aa766d03065f432a1468/README.md (README.md, Example: Running Terminal-Bench-2.0 section) |
| A trial's own tests | A passing trial has reward 1.0. Each trial is scored against that task's tests. | --passing / --failing  Job mode: score only passing (reward=1.0) / failing trials. | https://github.com/harbor-framework/harbor/issues/1767 (§CLI option table) |
| Cost and tokens | Trajectories include a metrics summary for cost and token use | step details with messages, tool calls, observations, and metrics ... metrics summary for total cost, token usage, etc. | https://github.com/harbor-framework/harbor/issues/128 (issue body bullet list) |

## mem2actbench

The audit says it evaluates extracting information from long-dialogue history and calling a tool correctly.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Apply memory to an action | The paper says prior benchmarks only test passive fact retrieval. This one tests applying memory to execute a task. | Existing benchmarks, however, primarily test an agent's ability to passively retrieve isolated facts in response to explicit questions. They fail to evaluate the more crucial capability of actively applying memory to ... | https://aclanthology.org/2026.acl-long.370/ (abstract) |
| Tool call from long dialogue | The README says the project tests extracting history and calling a tool correctly. The score formula is not in that quote. | 该项目旨在评估大语言模型在长上下文对话中，从历史记忆中提取信息并正确调用工具的能力。 | https://github.com/Cantaloupe-M/Mem2ActBench/blob/b00726940b5abbe9bd324bdd7a2cb272f5c62a29/README.md (README.md §项目简介) |
| Memory anchor check | Exact match, or a soft match by date, token overlap, fuzzy match, or semantic similarity | 记忆锚定验证：支持精确匹配和软匹配（日期转换、Token Overlap、模糊匹配、语义相似度） | https://github.com/Cantaloupe-M/Mem2ActBench/blob/main/README.md (README.md §04_qa_construction.py) |
| Difficulty levels | L1 direct copy, L2 semantic understanding, L3 cross-turn aggregation, L4 conflict resolution. The quote does not give a numeric score per level. | L1 Direct-Copy 单一来源，字面匹配，全是 explicit / L2 Semantic-Understanding 单一来源，需要推理/转换，有 inferred / L3 Cross-turn-Aggregation 多个来源，信息分散但无冲突 / L4 Conflict-Resolution 多个来源且有 inferred，或有时序冲突 | https://github.com/Cantaloupe-M/Mem2ActBench/blob/b00726940b5abbe9bd324bdd7a2cb272f5c62a29/README.md (README, difficulty levels) |

## realmem

The audit says its automated metrics are Recall and NDCG over retrieved memory points.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Temporal reasoning | Named query type. Automated metrics are Recall and NDCG on memory_used. | Examples of four query types in RealMem: (1) Temporal Reasoning resolves temporal constraints and schedule conflicts; (2) Static Retrieval ensures continuity by recalling accumulated context; (3) Dynamic Updating sync... | https://arxiv.org/html/2601.06966 (Figure 2 caption) |
| Static retrieval | Named query type. Recall and NDCG. | Examples of four query types in RealMem: (1) Temporal Reasoning resolves temporal constraints and schedule conflicts; (2) Static Retrieval ensures continuity by recalling accumulated context; (3) Dynamic Updating sync... | https://arxiv.org/html/2601.06966 (Figure 2 caption) |
| Dynamic updating | Named query type. Recall and NDCG. | Examples of four query types in RealMem: (1) Temporal Reasoning resolves temporal constraints and schedule conflicts; (2) Static Retrieval ensures continuity by recalling accumulated context; (3) Dynamic Updating sync... | https://arxiv.org/html/2601.06966 (Figure 2 caption) |
| Proactive alignment | Named query type. Recall and NDCG. | Examples of four query types in RealMem: (1) Temporal Reasoning resolves temporal constraints and schedule conflicts; (2) Static Retrieval ensures continuity by recalling accumulated context; (3) Dynamic Updating sync... | https://arxiv.org/html/2601.06966 (Figure 2 caption) |
| Retrieved memory points | Recall and NDCG | We support both automated metrics (Recall, NDCG) and LLM-based qualitative metrics. | https://github.com/AvatarMemory/RealMemBench/blob/67afd0891d603adcc4458ff0449df306ef296b7a/README.md (README.md, Metrics Calculation section) |
| Qualitative judge | LLM judge. Default model gpt-4o. The rubric items are not in this quote. | --model_name : Model used as the evaluator/judge (default: gpt-4o). | https://github.com/AvatarMemory/RealMemBench/blob/67afd0891d603adcc4458ff0449df306ef296b7a/README.md (README.md, Metrics Calculation / LLM-based Metrics section) |

## es-memeval

The audit says it evaluates conversational agents on personalized long-term emotional support.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Information extraction | QA subtype. F1, BERTScore, and an LLM judge from 0 to 2. | F1 Score (%) ↑ … BERTScore (%) ↑ … LLM-as-Judge (0-2) ↑ … IE … TR … CD … Abs … UM … All | https://github.com/slptongji/ES-MemEval/blob/692624208acc077b8867698c1d6fcd998dee641a/README.md (README.md, Table 3 header) |
| Temporal reasoning | QA subtype. Same three scores. | F1 Score (%) ↑ … BERTScore (%) ↑ … LLM-as-Judge (0-2) ↑ … IE … TR … CD … Abs … UM … All | https://github.com/slptongji/ES-MemEval/blob/692624208acc077b8867698c1d6fcd998dee641a/README.md (README.md, Table 3 header) |
| Contextual dependency | QA subtype. Same three scores. | F1 Score (%) ↑ … BERTScore (%) ↑ … LLM-as-Judge (0-2) ↑ … IE … TR … CD … Abs … UM … All | https://github.com/slptongji/ES-MemEval/blob/692624208acc077b8867698c1d6fcd998dee641a/README.md (README.md, Table 3 header) |
| Abstention | QA subtype. Same three scores. | F1 Score (%) ↑ … BERTScore (%) ↑ … LLM-as-Judge (0-2) ↑ … IE … TR … CD … Abs … UM … All | https://github.com/slptongji/ES-MemEval/blob/692624208acc077b8867698c1d6fcd998dee641a/README.md (README.md, Table 3 header) |
| Understanding and memory | QA subtype. Same three scores. | F1 Score (%) ↑ … BERTScore (%) ↑ … LLM-as-Judge (0-2) ↑ … IE … TR … CD … Abs … UM … All | https://github.com/slptongji/ES-MemEval/blob/692624208acc077b8867698c1d6fcd998dee641a/README.md (README.md, Table 3 header) |
| Retrieval | Recall@k and NDCG@k at turn, round, and session | Retrieval Accuracy … R@k (%) ↑ … NDCG@k (0-2) ↑ … Turn-level … Round-level … session-level | https://github.com/slptongji/ES-MemEval/blob/692624208acc077b8867698c1d6fcd998dee641a/README.md (README.md, Table 4 header) |
| Summarization | ROUGE-1, ROUGE-2, ROUGE-L, event precision, recall, and F1, plus an LLM score from 0 to 5 | ROUGE (%) ↑ / Event-based Metrics (%) ↑ / LLM Score (0-5) ↑ ... ROUGE-1 / ROUGE-2 / ROUGE-L / Precision / Recall / F1 | https://github.com/slptongji/ES-MemEval/blob/main/README.md (README.md, Table 6 header) |
| Dialogue generation memory | Recall and a weighted score | Recall ↑ … Weighted Score ↑ … LT-Mem. ↑ … Pers. ↑ … ES ↑ | https://github.com/slptongji/ES-MemEval/blob/692624208acc077b8867698c1d6fcd998dee641a/README.md (README.md, Table 7 and Table 8 headers) |
| Dialogue generation judges | Long-term memory, personalization, and emotional support | Memory Setting / Model / LT-Mem. ↑ / Pers. ↑ / ES ↑ | https://github.com/slptongji/ES-MemEval/blob/main/README.md (README.md, Table 8 header) |

## atod

The audit's ledger is about an agentic task-completion evaluator. It does not give a one-line benchmark definition beyond the metrics below.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Dependency-aware goal completion | Fraction of decided goals that are completed | dGCR = /{g∈U:S(g)=Completed}/ / /Udec/ ... This formulation avoids bias from dependency-locked goals and provides a faithful measure of system performance in multi-goal workflows. | https://arxiv.org/html/2601.11854v2 (§6.1) |
| Goal detection | F1 | Ours 91.92 92.31 86.49 84.28 | https://arxiv.org/html/2601.11854v2 (Table 3) |
| Status tracking | Accuracy | Ours 91.92 92.31 86.49 84.28 | https://arxiv.org/html/2601.11854v2 (Table 3) |
| Proactivity | Whether an unprompted goal or state change was appropriate | We evaluate proactive behaviors by identifying goal or state changes initiated without explicit user prompts and assessing whether these actions are contextually appropriate and beneficial. | https://arxiv.org/html/2601.11854v2 (§6.2) |
| Memory recall accuracy | Reported next to goal completion. Formula unknown in this quote. | dGCR 0.967 0.930 / # Turns to Completion 7.04 10.50 / Memory Recall Accuracy 0.913 0.743 / Proactivity Effectiveness 0.619 0.586 / Turn-level Quality 0.752 0.766 / Dialogue-level Quality 4.40 4.45 | https://arxiv.org/html/2601.11854v2 (Table 4) |
| Turn relevance and dialogue coherence | Response quality. Scale unknown in the short quote. | we assess conversational quality, focusing on turn-level relevance and dialogue-level coherence, following prior work. | https://arxiv.org/html/2601.11854v2 (§6.3) |
| Turns to completion | Count of turns | dGCR 0.967 0.930 / # Turns to Completion 7.04 10.50 / Memory Recall Accuracy 0.913 0.743 / Proactivity Effectiveness 0.619 0.586 / Turn-level Quality 0.752 0.766 / Dialogue-level Quality 4.40 4.45 | https://arxiv.org/html/2601.11854v2 (Table 4) |

## beam

The audit says it evaluates ten memory abilities, including abstention, contradiction resolution, event ordering, information extraction, instruction following, knowledge update, multi-session reasoning, preference following, and summarization.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Abstention | Named as one of ten abilities. | designed to assess ten distinct memory abilities … Abstention … Contradiction Resolution … Event Ordering … Information Extraction … Instruction Following … Knowledge Update … Multi-Session Reasoning … Preference Foll... | https://github.com/mohammadtavakoli78/BEAM/blob/b2da22eac88bb0874c64665f13457eb99835774a/README.md (README.md, BEAM Description and Probing Questions Types sections) |
| Contradiction resolution | Named as one of ten abilities. | designed to assess ten distinct memory abilities … Abstention … Contradiction Resolution … Event Ordering … Information Extraction … Instruction Following … Knowledge Update … Multi-Session Reasoning … Preference Foll... | https://github.com/mohammadtavakoli78/BEAM/blob/b2da22eac88bb0874c64665f13457eb99835774a/README.md (README.md, BEAM Description and Probing Questions Types sections) |
| Event ordering | Kendall tau-b. An LLM says whether two snippets are the same event. | We evaluate event ordering using the Kendall tau-b coefficient (Kendall, 1945) … an LLM equivalence detector … aligns events in system responses with nuggets, outputting yes if two snippets denote the... | https://arxiv.org/html/2510.27246v1 (Section 2.4, Evaluation) |
| Information extraction | Named as one of ten abilities. | designed to assess ten distinct memory abilities … Abstention … Contradiction Resolution … Event Ordering … Information Extraction … Instruction Following … Knowledge Update … Multi-Session Reasoning … Preference Foll... | https://github.com/mohammadtavakoli78/BEAM/blob/b2da22eac88bb0874c64665f13457eb99835774a/README.md (README.md, BEAM Description and Probing Questions Types sections) |
| Instruction following | Named as one of ten abilities. | designed to assess ten distinct memory abilities … Abstention … Contradiction Resolution … Event Ordering … Information Extraction … Instruction Following … Knowledge Update … Multi-Session Reasoning … Preference Foll... | https://github.com/mohammadtavakoli78/BEAM/blob/b2da22eac88bb0874c64665f13457eb99835774a/README.md (README.md, BEAM Description and Probing Questions Types sections) |
| Knowledge update | Named as one of ten abilities. | designed to assess ten distinct memory abilities … Abstention … Contradiction Resolution … Event Ordering … Information Extraction … Instruction Following … Knowledge Update … Multi-Session Reasoning … Preference Foll... | https://github.com/mohammadtavakoli78/BEAM/blob/b2da22eac88bb0874c64665f13457eb99835774a/README.md (README.md, BEAM Description and Probing Questions Types sections) |
| Multi-session reasoning | Named as one of ten abilities. | designed to assess ten distinct memory abilities … Abstention … Contradiction Resolution … Event Ordering … Information Extraction … Instruction Following … Knowledge Update … Multi-Session Reasoning … Preference Foll... | https://github.com/mohammadtavakoli78/BEAM/blob/b2da22eac88bb0874c64665f13457eb99835774a/README.md (README.md, BEAM Description and Probing Questions Types sections) |
| Preference following | Named as one of ten abilities. | designed to assess ten distinct memory abilities … Abstention … Contradiction Resolution … Event Ordering … Information Extraction … Instruction Following … Knowledge Update … Multi-Session Reasoning … Preference Foll... | https://github.com/mohammadtavakoli78/BEAM/blob/b2da22eac88bb0874c64665f13457eb99835774a/README.md (README.md, BEAM Description and Probing Questions Types sections) |
| Summarization | Named as one of ten abilities. | designed to assess ten distinct memory abilities … Abstention … Contradiction Resolution … Event Ordering … Information Extraction … Instruction Following … Knowledge Update … Multi-Session Reasoning … Preference Foll... | https://github.com/mohammadtavakoli78/BEAM/blob/b2da22eac88bb0874c64665f13457eb99835774a/README.md (README.md, BEAM Description and Probing Questions Types sections) |
| Rubric judge score | For every ability except event ordering, the score is the mean of the rubric item scores. | llm_judge_score = score / len(rubric) return dict( llm_judge_score=llm_judge_score, llm_judge_responses=llm_judge_responses ) | https://github.com/mohammadtavakoli78/BEAM/blob/b2da22eac88bb0874c64665f13457eb99835774a/src/evaluation/compute_metrics.py (src/evaluation/compute_metrics.py, evaluate_abstention and the same pattern in eight other tasks) |
| Temporal reasoning | Named in the ten abilities. The quote does not give a separate formula. | designed to assess ten distinct memory abilities … Abstention … Contradiction Resolution … Event Ordering … Information Extraction … Instruction Following … Knowledge Update … Multi-Session Reasoning … Preference Foll... | https://github.com/mohammadtavakoli78/BEAM/blob/b2da22eac88bb0874c64665f13457eb99835774a/README.md (README.md, BEAM Description and Probing Questions Types sections) |

## dialsim

The audit says it scores a conversational agent on questions asked during TV-script episodes, including a time limit.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Answer correctness | Accuracy: count of Correct divided by the number of questions | score_total = result_list.count('Correct') / len(result_list)     ...     calibrated_score = calibrated_result_list.count('Correct') / len(calibrated_result_list) | https://github.com/jiho283/DialSim/blob/0dd4db4db90740dbcf047f18a8e8adc83e7ba0f0/pseudo_simulator.py (pseudo_simulator.py, simulator(), scoring block) |
| Calibrated accuracy | Same ratio after ambiguity post-processing | score_total = result_list.count('Correct') / len(result_list)     ...     calibrated_score = calibrated_result_list.count('Correct') / len(calibrated_result_list) | https://github.com/jiho283/DialSim/blob/0dd4db4db90740dbcf047f18a8e8adc83e7ba0f0/pseudo_simulator.py (pseudo_simulator.py, simulator(), scoring block) |
| Time limit | A timeout is scored Wrong | result = 'Wrong (Timeout in saving history)' ... result = 'Wrong (Timeout in searching history)' ... result = 'Wrong (Timeout in answering)' ... if result_time >= sleep_time: result = 'Wrong (Timeout)' | https://github.com/jiho283/DialSim/blob/0dd4db4db90740dbcf047f18a8e8adc83e7ba0f0/simulator.py (simulator(), various timeout branches, simulator.py) |
| Fan quiz versus knowledge-graph questions | Both are scored as accuracy. Fan questions score higher than two-hop graph questions in the reported run. | comparing the performance of fan quiz-based questions and TKG-based questions, the results were 53.75% and 41.14% respectively... one-hop questions had a performance of 54.46%, whereas two-hop questions had a performa... | https://arxiv.org/html/2406.13144v1 (Section 4.3, Error Analysis by Question Type) |
| Known versus unknown | The agent must tell known information from unknown. The score rule for unknown is not in this quote. | requiring it to respond to spontaneous questions using past dialogue information and to distinguish between known and unknown information | https://github.com/jiho283/DialSim/blob/main/README.md (README.md, paragraph 1) |
| Three shows | Friends (Ross), The Big Bang Theory (Sheldon), and The Office (Michael). Scored with the same accuracy. | if script_name == 'friends': chatbot = 'Ross' elif script_name == 'bigbang': chatbot = 'Sheldon' elif script_name == 'theoffice': chatbot = 'Michael' | https://github.com/jiho283/DialSim/blob/0dd4db4db90740dbcf047f18a8e8adc83e7ba0f0/pseudo_simulator.py (simulator, chatbot assignment) |
| Adversarial names | original, shuffle, or new_name. Shuffle is the adversarial setting. Score rule beyond that label is unknown. | name_shuffle: Type of adversarial test, default is original. Options include original, shuffle, and new_name. shuffle means an adversarial setting, and new_name means placing generic names. | https://github.com/jiho283/DialSim/blob/main/README.md (README, Arguments, name_shuffle) |

## dulemon

The audit says it evaluates long-term dialogue consistency and dialogue engagingness.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Long-term dialogue consistency | Named as the main result. The scoring script is not in the repo. The README says the framework is coming soon. | Results on DuLeMon indicate that PLATO-LTM can significantly outperform baselines in terms of long-term dialogue consistency, leading to better dialogue engagingness. | https://aclanthology.org/2022.findings-acl.207/ (abstract, https://aclanthology.org/2022.findings-acl.207/) |
| Dialogue engagingness | Named as a result of consistency. Score rule unknown. | Results on DuLeMon indicate that PLATO-LTM can significantly outperform baselines in terms of long-term dialogue consistency, leading to better dialogue engagingness. | https://aclanthology.org/2022.findings-acl.207/ (abstract, https://aclanthology.org/2022.findings-acl.207/) |

## engramabench

The audit says it has 150 queries across factual recall, cross-space integration, temporal reasoning, adversarial abstention, and emergent synthesis.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Factual recall | Token F1 inside the factual average | It is built around 5 canonical personas, 100 multi-session conversations, and 150 queries spanning factual recall, cross-space integration, temporal reasoning, adversarial abstention, and emergent synthesis. | https://github.com/julianacunadc/engramabench/blob/146835cdcb7cb1519eddf09e9b07cd63448aca35/README.md (README.md §intro) |
| Cross-space integration | Token F1. Weighted inside the composite. | It is built around 5 canonical personas, 100 multi-session conversations, and 150 queries spanning factual recall, cross-space integration, temporal reasoning, adversarial abstention, and emergent synthesis. | https://github.com/julianacunadc/engramabench/blob/146835cdcb7cb1519eddf09e9b07cd63448aca35/README.md (README.md §intro) |
| Temporal reasoning | Token F1 inside the factual average | It is built around 5 canonical personas, 100 multi-session conversations, and 150 queries spanning factual recall, cross-space integration, temporal reasoning, adversarial abstention, and emergent synthesis. | https://github.com/julianacunadc/engramabench/blob/146835cdcb7cb1519eddf09e9b07cd63448aca35/README.md (README.md §intro) |
| Adversarial abstention | Accuracy. Contradicting a false premise counts as well as abstaining. | Policy: for adversarial abstain queries, correctly contradicting a false premise is as good as abstaining. | https://github.com/julianacunadc/engramabench/blob/146835cdcb7cb1519eddf09e9b07cd63448aca35/scorer/scorer.py (scorer.py:score_query) |
| Emergent insight | Token F1 against a reference answer, not a judge rubric | emergent_insight is currently scored with token-level F1 over a reference answer rather than a judge-based rubric, and should be interpreted more cautiously than the factual slices. | https://arxiv.org/html/2604.21229 (Section 3.4 and Limitations) |
| Composite | Half the mean of three factual F1s, plus a quarter adversarial accuracy, plus a quarter insight score | F = (single_space_f1 + cross_space_f1 + temporal_cross_space_f1) / 3 composite = 0.5 * F + 0.25 * adversarial_accuracy + 0.25 * emergent_insight_score | https://github.com/julianacunadc/engramabench/blob/146835cdcb7cb1519eddf09e9b07cd63448aca35/README.md (README.md §Scoring) |

## lmeb

The audit says it is a retrieval benchmark of 22 datasets and 193 tasks inside the MTEB framework.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Retrieval rank | Capped recall at k: relevant hits in the top k, divided by the smaller of the relevant count and k | R_cap@k = (# relevant in top-k) / min(#total_relevant, k) | https://github.com/KaLM-Embedding/LMEB/blob/a02ae842598183ed162fc90c58ffaae5eec89f12/metric.py (metric.py:recall_cap docstring) |
| nDCG at 10 | Default summary metric. Capped recall at 10 is optional. | 3rd argument (optional): Specific metric name to summarize (e.g., 'R_cap_at_10'). ndcg@10 by default. | https://github.com/KaLM-Embedding/LMEB/blob/main/README.md (README.md, Summarization section) |
| Constituent retrieval sets | The task list includes EPBench, KnowMeBench, LoCoMo, LongMemEval, REALTALK, TMD, MemBench, ConvoMem, QASPER, and NovelQA. Each is scored as retrieval on the test split. | tasks=[             "EPBench",             "KnowMeBench",             "LoCoMo",             "LongMemEval",             "REALTALK",             "TMD",             "MemBench",             "ConvoMem",             "QASPER... | https://github.com/KaLM-Embedding/LMEB/blob/a02ae842598183ed162fc90c58ffaae5eec89f12/lmeb_benchmark.py (lmeb_benchmark.py:build_lmeb(), tasks list) |
| Four memory types | Retrieval tasks are grouped as episodic, dialogue, semantic, and procedural. The score is the retrieval metric above. | LMEB spans 22 datasets and 193 zero-shot retrieval tasks across 4 memory types: episodic, dialogue, semantic, and procedural, with both AI-generated and human-annotated data. | https://arxiv.org/html/2603.12572v1 (Abstract) |

## longmemeval-v2

The audit says it has 451 questions on five memory abilities for web agents.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Static state recall | Accuracy, overall and per category. Judge model default is gpt-5.2. | LME-V2 contains 451 manually curated questions covering five core memory abilities for web agents: static state recall, dynamic state tracking, workflow knowledge, environment gotchas, and premise awareness. | https://arxiv.org/html/2605.12493v1 (Abstract) |
| Dynamic state tracking | Accuracy | LME-V2 contains 451 manually curated questions covering five core memory abilities for web agents: static state recall, dynamic state tracking, workflow knowledge, environment gotchas, and premise awareness. | https://arxiv.org/html/2605.12493v1 (Abstract) |
| Workflow knowledge | Accuracy | LME-V2 contains 451 manually curated questions covering five core memory abilities for web agents: static state recall, dynamic state tracking, workflow knowledge, environment gotchas, and premise awareness. | https://arxiv.org/html/2605.12493v1 (Abstract) |
| Environment gotchas | Accuracy | LME-V2 contains 451 manually curated questions covering five core memory abilities for web agents: static state recall, dynamic state tracking, workflow knowledge, environment gotchas, and premise awareness. | https://arxiv.org/html/2605.12493v1 (Abstract) |
| Premise awareness | Named as one of five abilities. Abstention items use a wrong premise the model must identify. | we curate abstention questions with wrong premises that the model must identify to succeed... These studies use a direct question answering setup rather than the context gathering ... | https://arxiv.org/html/2605.12493v1 (Section 3.2, Question Annotation; Section 3.4) |
| Latency-adjusted score | LAFS gain against a fixed accuracy-latency frontier | The score is LAFS gain over the fixed reference frontier, and a submission may include multiple latency operating points for the same method and tier. | https://github.com/xiaowu0162/LongMemEval-V2/blob/2cc8c540bdb87fe6761629b585e727e1c4704520/README.md (README.md, Submitting to Leaderboard section) |

## membench

The audit says it evaluates agent memory on effectiveness, efficiency, and capacity.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Effectiveness | Multiple-choice accuracy | we present a benchmark, named MemBench, to evaluate the memory capability of LLM-based agents from multiple aspects, including their effectiveness, efficiency, and capacity. | https://aclanthology.org/2025.findings-acl.989/ (abstract, tan-etal-2025-membench) |
| Efficiency | Named as temporal efficiency, alongside accuracy, recall, and capacity. Write time and read time are also recorded per step. | self.write_time.append(time_02 - time_01) ... self.read_time.append(time_04 - time_03) | https://github.com/import-myself/Membench/blob/f66d8d1028d3f68627d00f77a967b93fbb8694b6/benchmark/MembenchAgent.py (MemBenchAgent.response(), lines ~67 and ~76) |
| Capacity | Named as a third aspect. The formula is not in this quote. | we present a benchmark, named MemBench, to evaluate the memory capability of LLM-based agents from multiple aspects, including their effectiveness, efficiency, and capacity. | https://aclanthology.org/2025.findings-acl.989/ (abstract, tan-etal-2025-membench) |
| Multiple-choice answer | The agent must output one letter, A through D | Choices: A. {choice_A} B. {choice_B} C. {choice_C} D. {choice_D} Please output the correct option for the question, only one corresponding letter, without any other messages. | https://github.com/import-myself/Membench/blob/f66d8d1028d3f68627d00f77a967b93fbb8694b6/benchmark/MembenchAgent.py (INSTRUCTION_FIRST, lines 24-30) |
| Factual memory, including indirect time | The audit says this tests converting an indirect time, such as next Monday, to an exact date. The score formula for that item is not in the quote. | the user may not directly express the time of an event but might use indirect references, such as 'next Monday', we can evaluate the agent's ability to extract information and instantly convert time-r... | https://arxiv.org/html/2506.21605v1 (Section 3.3, Multi-level Memory — Factual Memory) |
| Four memory settings | Named splits. Score rule for each split is not in this quote. | Participation-Reflective (FirstAgentHighLevel), Participation-Factual (FirstAgentLowLevel), Observation-Reflective (ThirdAgentHighLevel), Observation-Factual (ThirdAgentLowLevel) | https://github.com/import-myself/Membench/blob/f66d8d1028d3f68627d00f77a967b93fbb8694b6/README.md (README.md, Data Details section) |
| Reflective memory | Extract and summarize a high-level preference from lower-level ones. Score formula unknown in this quote. | Reflective memory refers to the extraction and summarization of high-level preferences based on the user's expression of low-level preferences. | https://arxiv.org/html/2506.21605v1 (Section 3.3, Multi-level Memory, Reflective Memory) |

## memoryarena

The audit says it benchmarks agent memory in interdependent multi-session agentic tasks.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Subtask progress | Fraction of subtasks passed, averaged over tasks | PS_{S_i} = /s_i^{pass}/ / /S_i/, PS = (1/N) * sum_i^N PS_{S_i} | https://arxiv.org/html/2602.16313v1 (§4.2, Eq. 5) |
| Full task success | Percent of tasks fully solved | We also report the Task Success Rate (SR), which measures the percentage of tasks that are fully solved. | https://arxiv.org/html/2602.16313v1 (§4.2) |
| Progressive search | Answer is a target product id plus attributes. Match rule unknown. | {"target_asin": "B00TUDFEW2", "attributes": ["Almond Flour", ...]} | https://huggingface.co/datasets/ZexueHe/memoryarena/blob/main/README.md (README.md, Example task — In Progressive Search) |
| Formal reasoning | Math and physics items from papers. Score is the progress and success metrics. | "paper_name": "paper_id", # which paper the questions are created from ... "backgrounds": ["necessary definitions, formulations, and relevant context of subtask 1", ...] | https://huggingface.co/datasets/ZexueHe/memoryarena/blob/main/README.md (README.md, Example task — In Formal Reasoning (Math and Phys)) |
| Bundled shopping | One target item plus compatible and incompatible distractors. Score rule beyond progress and success is unknown. | With 3 compatible candidates (1 target item and 2 compatible distractors) identified... We selected 2 items that are logically compatible... We selected 2 items that are logically mutually exclusive... to serve as 'ha... | https://arxiv.org/html/2602.16313v1 (§A.2.1) |
| Group travel planning | Named as an environment where success is near zero. Item list unknown. | Overall, all methods achieve low SR and PS, with two environments exhibiting near-zero SR, indicating that MemoryArena poses a challenging evaluation setting. | https://arxiv.org/html/2602.16313v1 (§4.3) |

## memorybank

The audit says the evaluation uses both real user dialogs and simulated dialogs, with probing questions.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Retrieval accuracy | Reported as a number. Formula unknown in this quote. | SiliconFriend ChatGPT [English]: Retrieval Acc. 0.763, Correctness 0.716, Coherence 0.912, Ranking 0.818. | https://arxiv.org/html/2305.10250v3 (§4.2 Table 2) |
| Correctness | Reported as a number. Formula unknown in this quote. | SiliconFriend ChatGPT [English]: Retrieval Acc. 0.763, Correctness 0.716, Coherence 0.912, Ranking 0.818. | https://arxiv.org/html/2305.10250v3 (§4.2 Table 2) |
| Contextual coherence | 0, 0.5, or 1 for how the reply connects the dialogue and the retrieved memory | Contextual Coherence: Assesses whether the response is naturally and coherently structured, connecting the dialogue context and retrieved memory (labels: 0:not coherent, 0.5:partially coherent, 1:coherent). | https://arxiv.org/html/2305.10250v3 (§4.2 Quantitative Analysis, Evaluation Metrics) |
| Ranking | Reported as a number. Formula unknown in this quote. | SiliconFriend ChatGPT [English]: Retrieval Acc. 0.763, Correctness 0.716, Coherence 0.912, Ranking 0.818. | https://arxiv.org/html/2305.10250v3 (§4.2 Table 2) |
| Empathic reply, recall, and personality | Named as what the companion can do. Not given as a separate score. | SiliconFriend, equipped with MemoryBank, exhibits a strong capability for long-term companionship as it can provide emphatic response, recall relevant memories and understand user personality. | https://arxiv.org/abs/2305.10250 (abstract) |

## msc

The audit says it evaluates open-domain dialogue models across multiple chat sessions.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Multi-session chat | The audit says retrieval and summary methods beat encoder-decoder models. It does not name the metric. | retrieval-augmented methods and methods with an ability to summarize and recall previous conversations outperform the standard encoder-decoder architectures currently considered state of the art | https://parl.ai/projects/msc/ (Abstract) |
| Persona summary | A dialog-summary set with train and valid counts. Score rule unknown. | dialog summary for multi-session chat data (session 1-4, with 130k train examples and 25k valid examples) | https://parl.ai/projects/msc/ (Data section) |

## perltqa

The audit says it evaluates question answering over personal long-term memory, split into semantic memory and episodic memory.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Memory classification | Weighted precision, recall, F1, and accuracy | PerLTQA is a new benchmark for memory classification, retrieval, and synthesis of Large Language Models. | https://github.com/Elvin-Yiming-Du/PerLTQA/blob/8d9e19868e239740ef701e603ec205cd581f221b/README.md (README.md, heading section) |
| Memory retrieval | Recall at 1, 2, 3, and 5 | PerLTQA is a new benchmark for memory classification, retrieval, and synthesis of Large Language Models. | https://github.com/Elvin-Yiming-Du/PerLTQA/blob/8d9e19868e239740ef701e603ec205cd581f221b/README.md (README.md, heading section) |
| Memory synthesis | gpt-3.5 correctness and coherence, plus mean average precision of memory anchors | we measure the correctness and coherence of responses with gpt-3.5-turbo-based evaluation method (Zhong et al., 2023) and use MAP (mean average precision) of memory anchors as shown in Eq.(5) to evaluate memory synthe... | https://arxiv.org/html/2402.16288v1 (Section 3.5 Evaluation Metrics) |
| Question groups | Events, social relationships, profiles, and dialogues | extract_event_questions ... extract_social_relationship_questions ... extract_profile_questions ... extract_dialogue_questions | https://github.com/Elvin-Yiming-Du/PerLTQA/blob/8d9e19868e239740ef701e603ec205cd581f221b/Dataset/dataset.py (dataset.py, PerLTQA method names) |

## prefeval

The audit says it evaluates whether models recognize and follow user preferences.

| Thing tested | How it is scored | Quote | Locator |
| --- | --- | --- | --- |
| Explicit preference | Generation: preference-following accuracy. Classification: exact letter match. | 1. Explicit Preference. ... 2. Implicit Preference - Choice-based Conversation ... 3. Implicit Preference - Persona-driven Conversation | https://github.com/amazon-science/prefeval/blob/50795054b5ff5f418d2b768a331d71e480f93331/README.md (README.md, Data Format section) |
| Implicit choice-based preference | Same two tasks | 1. Explicit Preference. ... 2. Implicit Preference - Choice-based Conversation ... 3. Implicit Preference - Persona-driven Conversation | https://github.com/amazon-science/prefeval/blob/50795054b5ff5f418d2b768a331d71e480f93331/README.md (README.md, Data Format section) |
| Implicit persona-driven preference | Same two tasks | 1. Explicit Preference. ... 2. Implicit Preference - Choice-based Conversation ... 3. Implicit Preference - Persona-driven Conversation | https://github.com/amazon-science/prefeval/blob/50795054b5ff5f418d2b768a331d71e480f93331/README.md (README.md, Data Format section) |
| Generation adherence | Pass only if the reply is not inconsistent, not a hallucinated violation, not preference-unaware, and not unhelpful | preference_following_accuracy = not any(     [is_inconsistent, is_hallucination_of_preference_violation, is_preference_unaware_violation, is_unhelpful] ) ... accuracy = (stats["preference_adherence_accuracy"] / total_... | https://github.com/amazon-science/prefeval/blob/50795054b5ff5f418d2b768a331d71e480f93331/generation_task/get_preference_following_accuracy_generation_task.py (generation_task/get_preference_following_accuracy_generation_task.py:analyze_errors,print_evaluation_results) |
| Classification choice | Exact match of the chosen letter to the correct index | if task["choice"] == task["correct_idx"]:     correct_count += 1 | https://github.com/amazon-science/prefeval/blob/50795054b5ff5f418d2b768a331d71e480f93331/classification_task/benchmark_classification.py (main(), ~lines 168-169) |
