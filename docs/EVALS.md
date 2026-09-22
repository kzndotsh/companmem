# Eval landscape (working notes)

Synthesis across **25** benchmarks in [`research/pipeline/seed.json`](../research/pipeline/seed.json) → `evals`. Primary evidence lives in [`research/output/by-eval/<slug>/audit.json`](../research/output/by-eval/) (harvest → extract → fold). This doc is a **comparison map** for Phase 2: what an exam might steal, refuse, or combine—before we line it up with [`research/output/by-product/`](../research/output/by-product/) product audits.

**Status:** exploratory notes, not settled research. Do not treat as scores or leaderboard truth. Refresh when audits are re-run.

Per-eval list of what each benchmark tests: [`EVAL-INVENTORY.md`](EVAL-INVENTORY.md).

**Protocol axes:** [`research/output/by-eval/PROTOCOL.md`](../research/output/by-eval/PROTOCOL.md) (RQ-E1 tasks, RQ-E2 graders, RQ-E3 what metrics miss, RQ-E4 remembering-as-behavior, RQ-E5 rerunnability).

---

## How this connects to product audits

| Layer | Question it answers |
|--------|---------------------|
| **Product audits** | What shipped systems *do* (store, retrieve, maintain, UX promises). |
| **Eval audits** | What the field *measures* when it claims “memory.” |
| **Gap** | Products optimize for metrics that exist; companions need behaviors many evals never score. |

Use this doc to:

1. **Cluster evals** by task shape and grader—so we do not conflate “good on LoCoMo” with “good companion.”
2. **Flag shared blind spots** (QA probes, LLM judges, session-end queries, no timing/restraint).
3. **Pick steal candidates** (task types, grader hygiene, abstention axes) vs **refuse** (vendor headline metrics, saturated QA with known key errors).
4. Later: cross-walk axes against [`research/output/by-product/synthesis.json`](../research/output/by-product/synthesis.json) (products only today).

### Product × eval join (deferred)

Steal/refuse in this file stays the **eval** map. Do not mix eval audits into `just synthesize`.

A product×eval crosswalk waits until `research/output/by-product/synthesis.json` exists **and** [`matrix.json`](../research/output/by-product/matrix.json) is in tree. Join those two with this doc in Phase 2; do not treat vendor LoCoMo rows in product ledgers as the eval map.

---

## Comparison axes (same grid for every slug)

| Axis | What to compare |
|------|------------------|
| **Interaction** | Passive QA after history vs in-dialog use vs tool/agent loop vs embedding retrieval only. |
| **Memory unit** | Raw turns, sessions, extracted facts, personas, project state, trajectories, multimodal items. |
| **Probe timing** | After all sessions vs interleaved vs at session end vs on-demand tool call. |
| **Grader** | Exact match / F1 / multiple-choice / LLM-as-judge / human / structured match (ASIN, JSON). |
| **Abstention** | Explicit unanswerable or conflict items vs implicit only. |
| **Scale** | ~10 conversations vs 500–8k questions vs 115M-token haystacks. |
| **Open harness** | Repo + grader script vs paper/HF only (`clone: false` in seed). |

---

## Master table (from audits)

Audit depth varies (`ledger` size, `unknowns`). Thin rows need re-harvest or more sources—not weak benchmarks necessarily.

| Slug | Family | Interaction | Typical grader | Scale (order of magnitude) | Harness |
|------|--------|-------------|----------------|---------------------------|---------|
| locomo | Long-dialogue QA | Post-hoc QA on long chat (truncated context in official script) | Official `evaluation.py`: token **F1** (cat-dependent paths); cat-5 = decline phrases; community **gpt-4o-mini** judge (3× majority) + “Generous Judge” (mem0 script) | **10** convs, **1,986** QA; cat-5 **446** adversarial | Open; **issue-heavy** (keys, cat IDs, cat-5 mislabels) |
| locomo-conv | In-situ memory | Same gold/evidence as LoCoMo; **dialog / implicit / counterfactual / composed** queries | `score_fact_used_partial`, `score_counterfactual_3way`, `score_composed_atomic`; pairwise **claude-opus-4-7** | 1,069 composed clusters (`locomo10_multimem_full.json`) + per-QA rewrites | Open; inherits LoCoMo label noise |
| longmemeval | Long-dialogue QA | Post-hoc QA on haystack sessions; **S** (~115k tok) / **M** (long); **oracle** variant | `evaluate_qa.py`: per-type LLM judge → `autoeval_label` (**yes** in response); **30** `_abs` abstention; retrieval **Recall@k** / NDCG (skip abstention) | **500** Q (6 types + abstention); cleaned HF splits; **2025/09** history cleanup | Open; issues: oracle `question_type` routing, multi-gold R@k, #37 label error |
| longmemeval-v2 | Agent trajectory memory | **Context gathering:** `insert()` trajectories → `query()` (text + optional screenshot); web + enterprise domains | **gpt-5.2** evaluator (default); accuracy + per-ability breakdown; leaderboard **LAFS** gain vs reference frontier | **451** Q; tiers **small** (~25M shared haystack) / **medium** (~115M per-Q); 200k tok reader budget | Open; issue **#1** gold/DOM mismatch; abstention handling (#6) |
| beam | Long-dialogue QA | Default: **full chat.json** context (not RAG slice); optional retrieval in issues | Rubric **LLM judge** mean (`llm_judge_score`); **event_ordering** = Kendall τ-b (paper); issues: 1.0/0.5/0.0 items | 100 chats (128K–10M), 2k Q (~40/category); synthetic 3-stage LLM build | Open; **issue ledger**: int() drops 0.5, plan/chat gold mismatch |
| dialsim | **In-stream** multi-party sim | Question fired **mid-episode** when chatbot speaks; incremental history + RAG | Accuracy (Correct/total) + **calibrated_score**; timeout → Wrong; gpt-4o-mini judge for some formats | 3 TV scripts (~350k tok avg); LongDialQA; hard TKG vs easy fan quiz | Open |
| memorybank | Early LT companion eval | ChatGPT-sim **memory banks** + human **probing** questions (en/zh) | Paper: human **Retrieval Acc / Correctness / Coherence** (0–0.5–1) + **Ranking**; repo retrieval only (FAISS top-6, Ebbinghaus forget) | 15 virtual users, **194** probes (97 en + 97 zh) | Open; no scored eval script in audit |
| msc | Long-dialogue (gen) | Human–human **5-session** chat (S1=ConvAI2); prior sessions in context | ParlAI **generation** metrics + per-turn human eval (scorer not in harvest) | S2–4 train/valid/test; PersonaSummary **130k** train; optional `time_gap` | ParlAI `tasks/msc` |
| dulemon | Persona LT (ZH) | Open-domain **generation**; persona grounding labels on turns | **Consistency** + **engagingness** (paper/README); no public scorer in audit | Download via `download_dulemon.sh`; scale/splits not in audit | Paddle subtree only; PLATO-LTM “coming soon” |
| perltqa | Structured LT QA (ZH) | Three tasks: **classify** memory type → **retrieve** (BM25/DPR/RocketQA) → **synthesize** | Clf: weighted P/R/F1; retrieval **R@k**; synthesis **MAP** (anchor EM) + **gpt-3.5** correctness/coherence | **8,593** Q, **30** anchored personas; synthetic fiction (CC BY-NC 4.0) | Open; README light on graders |
| personamem | Persona / preference MC | **In-situ** MC over PersonaHub-seeded synthetic multi-session chats (v1 jsonl vs v2 per-file) | MC accuracy (leaderboard); optional context slice via `end_index_in_shared_context` | 15 LLMs × **7** query types (README); v2 on HF | Open; **v2 eval loop**, data gaps (**#15**, **#35**, **#42** length bias) |
| prefeval | Preference following | Explicit + implicit (choice/persona) prefs; **inter_turns** filler (default 5); 10 vs **300** turn arms | Gen: **Preference Following Accuracy** (4 violation types, all must pass) from pre-graded `error_*.json` (Claude judge upstream); clf: **exact** choice letter (seed 41) | 20 topics; HF explicit set; leaderboard Travel-Restaurants | Open (ICLR 2025 oral); Bedrock inference |
| memoryagentbench | Agent memory competencies | Per context: **initialize_and_memorize** then query; YAML task configs (HELMET, InfBench, LongMemEval(S*), EventQA, FactConsolidation, TTL ICL…) | Per-task: **exact_match** (TTL), rouge/substring EM (issues), **gpt-4o** judge yes/no (LME types; temporal off-by-one OK), %×100 in `main.py` | HF `ai-hyz/MemoryAgentBench`; ICLR **2026**; paper base **gpt-4o-mini** | Open; issues **#10** leakage, **#14** which output column is paper |
| membench | Agent memory mechanisms | Stream `message` + `question` obs; Participation/Observation × Reflective/Factual | MC letter (JSON `choice`); **Recall@10** on `retri()`; write/read latency | `data2test` **0–10k** / **100k** tok; MemData external | Open |
| mem2actbench | Memory → action | Sessions → **tool_call** + `grounding_info` | Soft anchor match in pipeline; no audited end-to-end scorer | Full + **350**-QA small; **L1–L4**; BFCL/OASST1/ToolACE | Open; generator README |
| memoryarena | Agentic multi-session | Five envs (bundled shopping, progressive search, group travel, formal math/phys); background per subtask | **PS** (subtask pass fraction) + **SR** (full task solve); structured gold (ASIN+attrs, itineraries, LaTeX) | HF **701** rows / paper **766** tasks, ~6.9 subtasks, ~57 steps; **test** only | HF + paper HTML; **repo null** in audit |
| realmem | Project-oriented LT | **Interleaved** QA within long cross-session project dialogues (11 scenarios) | Auto **Recall** + **NDCG** on `memory_used`; **gpt-4o** LLM-QA score (default); human rank cross-check in paper | **1,415** Q, **14k** turns, ~**269k** tok/user avg; synthetic multi-agent pipeline | Open (ACL 2026 Findings) |
| es-memeval | Emotional support LT | **Four tracks:** QA, summarization, dialogue gen, retrieval (`src/exe/*`) | QA: F1/BERTScore/LLM-judge 0–2 (IE,TR,**CD**,**Abs**,UM); DG: No-Mem vs Full-Hist vs **RAG** + LT-Mem/Pers/ES judges | EvoEmo `data/evo_emo.json`; QA context ablation 2K–20K | Open |
| halumem | Memory **hallucination** | Three **ops:** extraction, update, QA via adapter scripts (shared I/O contract) | **GPT-4o** judge (T=0); `overall_score`: integrity, accuracy, extraction F1, update, QA, type breakdown; update/QA labels Correct/Hallucination/Omission | Halu-Medium (~160k tok) / Halu-Long (~1M); 3,467 QA; issue **#10** missing `original_memories` | Open; leaderboard mostly team-scored until issue **#6** |
| atm-bench | Multimodal referential QA | Ingest chronologically → retrieve → evidence-grounded answer (Unknown allowed) | **QS** (%; primary judge gpt-5-mini); **Recall@10**; Oracle ceiling; NIAH on hard (k=25/50/100) | ~12k items, ~1.1k QA; **hard=31**; PR/LA/MUT/ME/ABS qtypes | Open; per-question isolation in baselines |
| atod | Agentic TOD + **ATOD-Eval** | Multi-goal TOD (~54 turns); async, deps, interleaving, proactive, turn-level goal status | **dGCR** (primary completion); goal F1 + status acc; memory recall acc; proactivity; turn/dialogue quality | LLM-built from SGD; medium vs complex test splits | Paper/HTML only in audit; no repo |
| assistant-benchmark | Holistic assistant | Real-use probes (travel, email, routines—not batch QA) | Human 1–10 vs anchors; **Memory** = min of two probes (preference @ ~1 week, city-conflict); anchors 3/6/7/10 | v0.2, 16 dimension tasks, 193 runs; only **10** assistants scored on Memory | Site only; grader identity not in audit |
| lmeb | **Embedding** retrieval (MTEB benchmark) | Query → rank memory **candidates** (dialogue tasks use per-conv `candidates.jsonl`) | **R_cap@k** (primary in `metric.py`); summarize **ndcg@10** or **R_cap_at_10**; binary qrels | 22 datasets (LoCoMo, LongMemEval, MemBench, …), 193 tasks, 4 memory types | Open; ~orthogonal to MTEB retrieval (r≈−0.12) |
| harbor | **Harness** (not memory QA) | Task dirs (`task.toml`, `tests/`, env); multi-step SHARED mode | Per-task **verifier** → `reward.json` (often scalar 1.0 pass); `BaseMetric` aggregation (issues: alphabetical key pick, missing key = 0) | Terminal-Bench-2.0 official; SWE-Bench, GAIA adapters; **ATIF** `trajectory.json` | Open; issue **#1960** verifier leak in SHARED steps |
| engramabench | LT conv QA (delayed) | Queries after **full** history observed | **Composite** = 0.5×mean(F1 on 3 recall families) + 0.25×adversarial_acc + 0.25×emergent; stdlib scorer v1.4.0 | 150 Q (30/30/30/40/20), 100 convs, 5 personas, `full_v1` | Open; typed answers (entity…insight) |

---

## Families (similarities)

### A. Post-hoc long-chat QA (the “LoCoMo cluster”)

**Slugs:** locomo, longmemeval, beam, perltqa (structured), engramabench, parts of memoryagentbench / MemoryBank probes.

**What they target:** Given a long history, answer a question (or abstain)._axes often include single-hop, multi-hop, temporal, knowledge update, preference.

**Similarities:** Session-stacked or padded context; gold answer or session pointer; heavy **LLM-as-judge** or fuzzy match.

**Differences:**

- **LoCoMo:** LLM+human event-graph dialogues (`locomo10.json`); official scorer = token F1 with **numeric category IDs that do not match paper section order** (issue **#29**). Cat-5 abstention uses brittle phrase match; issues **#27**, **#35**, **#43** document wrong gold, mislabeled “adversarial” items, and generous LLM judges without evidence in prompt (issue **#23**). Community SOTA posts use mem0-style gpt-4o-mini judge—not necessarily `evaluate_qa.py`.
- **LongMemEval:** 500 curated Q over padded chat histories (ShareGPT/UltraChat/simulated mix); six scored types + **30** false-premise abstention (`_abs`); judge templates in code (temporal off-by-one OK, knowledge-update accepts stale+new). **LongMemEval-S** ≈128k context; **oracle** file for retrieval-only. Community scores often use `longmemeval_*_cleaned.json`—pin version (issue **#27**). Using dataset **question_type** for per-category retrieval policy is a large uplift (issue **#43**) vs production-realistic runs.
- **BEAM:** single-user coherent narratives to **10M** tokens; ten abilities (IE, MR, KU, TR, ABS, CR, EO, IF, PF, SUM). Official harness: `compute_metrics.py` rubric judge (nine categories) vs paper **Kendall τ-b** for event ordering. Audit **issues** flag `int(score)` truncating 0.5 partial credit, abstention label ambiguity, and gold answers that reference `plan_new` not visible in `chat.json` at eval time—treat vendor BEAM % as harness-dependent.
- **PerLTQA:** Chinese synthetic personas; staged **classification (BERT) → retrieval (BM25/DPR/RocketQA) → synthesis** with **memory anchors** and MAP—not a single end-to-end companion score.
- **EngramaBench:** five families (single/cross/temporal cross-space, **adversarial** abstention, emergent insight); **published composite formula** in README/scorer; `cross_space` highlighted as structured-memory diagnostic; adversarial policy counts contradicting false premises like abstain.

**Companion gap (RQ-E4):** Questions are **external probes**, not “user didn’t ask.” No social timing, restraint, or relationship tone.

---

### B. Remembering in conversation (not only QA cards)

**Slugs:** locomo-conv, prefeval (partially), assistant-benchmark (Memory dimension probes).

**What they target:** Whether memory shows up when the **dialog frame** requires it (implicit, composed, counterfactual).

**Steal candidate:** LoCoMo-Conv’s split of **dialog / implicit / composed / counterfactual** and “silent grounding” analysis—closer to companion use than raw QA accuracy.

**DialSim:** Streams TV-script episodes; asks **one** question per session at a chatbot utterance (not end-of-history QA). Scores **latency** (per-stage timeouts count as wrong) and supports oracle/BM25/OpenAI-emb retrieval—closer to “conversation is happening now” than LoCoMo cards.

**Assistant Benchmark (Memory dimension):** Two live probes—dietary preference recalled unprompted after ~one week, and trip-city conflict caught when planning dinner—not a transcript QA set. Final Memory score is the **minimum** of the two subscores (strict). Same scorecard also scores **Restraint**, **Proactive**, and **Routines**, so it is one of the few census evals that situates memory next to companion-adjacent behavior (audit: `assistant-benchmark`).

---

### C. Preferences and persona

**Slugs:** prefeval, personamem, personamem-adjacent (halumem personas), dulemon/msc/memorybank (persona consistency).

**What they target:** Stable user model—preferences (PrefEval), persona MC (PersonaMem), mutual persona (DuLeMon), session personas (MSC), empathic recall probes (MemoryBank).

**Similarities:** Synthetic or curated personas; long context; degradation over turns without reminders/RAG.

**PrefEval:** Three preference surfaces (explicit string, implicit choice, implicit persona); five baselines (zero-shot, remind, cot, RAG top-k, self-critic). Generation pass/fail is strict conjunction of four judge flags (unhelpful, inconsistent, hallucinated preference, preference-unaware)—scores often &lt;10% by 10 turns without remind (paper). Classification track is cheap exact MC with shuffled options.

**PersonaMem:** PersonaHub-seeded synthetic arcs; **seven** in-situ query types (README leaderboard). Audit issues flag **v1→v2** harness drift, missing creative-writing assets, and **#42** slice-dependent **length heuristics** (no-context can beat 25% floor or fall below it on `ask_to_forget`).

**MemoryBank (SiliconFriend):** Early companion prototype eval—ChatGPT-built banks, human **194** probes; paper human scores for retrieval + response quality, not a pinned auto harness in repo.

**MSC:** Human–human continuity across sessions with personas and optional inter-session **time gap**—generation benchmark, not preference-violation MC.

**Companion gap:** Measures **violation of stated preference** more than **caring vs creepy** recall ([`docs/QUESTIONS.md`](QUESTIONS.md) remembering vs retrieving).

---

### D. Agent memory (incremental ingest + later query)

**Slugs:** memoryagentbench, membench, mem2actbench, memoryarena, longmemeval-v2.

**What they target:**

- **MemoryAgentBench:** Unified harness over reformulated RULER/InfBench/HELMET/LongMemEval plus **EventQA** and **FactConsolidation**; explicit **memorize-then-query** per context with resume checkpoints. Metrics mix EM/rouge/substring and **gpt-4o** binary judges (LME-style type prompts). Community issues: parametric-knowledge leakage vs LoCoMo (**#10**), ambiguous “which score is the paper” (**#14**), **gpt-4o-mini** reproducibility horizon (**#16**), proposed **conflict-detection recall** not shipped.
- **MemBench:** simulates **agent memory modules** under noise-inflated context; four quadrants (who speaks + factual vs reflective MC). Reports accuracy, retrieval recall, capacity curves, temporal efficiency—closer to **memory algorithm** bakeoff than user-facing companion chat.
- **Mem2ActBench:** memory for **tool parameters**, not fact QA. LLM-built pipeline (facts → BERTopic conflicts → QA with explicit/inferred args); levels **L1–L4** (copy → semantic → aggregate → conflict). Audit: dataset generator, not a pinned end-to-end harness score.
- **MemoryArena:** **766** interdependent agentic tasks (shopping bundles with hard negatives, progressive web search with embedding top-5, travel planning, paper-derived formal reasoning). **PS/SR** aggregate subtask success; near-zero SR on hardest envs in paper—LoCoMo-saturated agents still fail (claimed gap). HF card lists **701** rows; automated grader scripts not linked in audit.
- **LongMemEval-V2:** memory from **multimodal web/enterprise agent trajectories** (WebArena + WorkArena pool); five abilities (static/dynamic state, workflow, gotchas, premise/abstention). Methods implement memory backend API—no gold leakage at `query()`. Paper fixed reader **Qwen3.5-9B**; embedding RAG baseline; **LAFS** scores accuracy vs latency for leaderboard. Not comparable to chat-QA saturation on LME v1.

**Research takeaway:** Saturation on chat-QA does not imply strong **agentic** memory ([MemoryArena claimed purpose in audit](research/output/by-eval/memoryarena/audit.json)).

---

### E. Hallucination and memory operations

**Slugs:** halumem, halumem-adjacent critiques in issues.

**What they target:** Wrong extraction, update failures, false memory resistance—**operation-level**, not single end-to-end score. HaluMem scores **memory systems** (Mem0, Zep, MemOS, …) through `eval/evaluation.py`: golden **memory points** (persona/event/relationship) vs extracted set; update and QA graded as Correct vs Hallucination vs Omission. QA taxonomy includes **Memory Conflict** and **Memory Boundary** (six types in README).

**Steal candidate:** Stage-wise metrics (extract / update / QA) for product pipelines; refuse collapsing to one LoCoMo number. **Caveats from audit:** Zep skipped on extraction (API cannot list all session memories); Memobase recall caps (250 tok update / 500 QA); dataset issue **#10** (>70% update rows reference missing originals); independent replication only recently (issue **#6**).

---

### F. Domain-specific long horizon

| Slug | Domain |
|------|--------|
| es-memeval | Emotional support (**EvoEmo**); QA abstention (Abs) + contextual dependency (CD); separate **generation** track with memory-condition ablation and LT-Mem/Pers/ES LLM judges |
| realmem | Long-running **projects** (11 scenarios); **interleaved** QA; four query types (temporal, static retrieval, dynamic update, proactive alignment); Recall/NDCG + LLM QA; no tool-use axis |
| atm-bench | Multimodal personal referential QA (email, image, video); five qtypes (PR, LA, MUT, ME, ABS); **SGM** text surrogates preferred over raw media under haystack; ships Mem0/MemoryOS/HippoRAG2 baselines with contamination controls |
| atod | Task-oriented dialogue: goals, dependencies, proactive/async; **ATOD-Eval** metrics (dGCR, memory recall accuracy correlates with dGCR); synthetic from SGD goal graph (52 nodes) |

---

### G. Infrastructure (not “memory benchmarks” but in census)

| Slug | Role |
|------|------|
| **harbor** | Agent eval **orchestration** (Docker/Modal/…), not a memory dataset. **ATIF** v1.6+ trajectories; v1.7 `context_management` for compaction boundaries (issue **#3078**). Per-benchmark adapters normalize to Harbor task shape; trials write `reward.json` + optional `VerifierResult`. Audit flags: SHARED multi-step **#1960** (agent can read prior `test.sh` / reward), progress metric chosen by **alphabetical** reward keys (**#2396**, **#2782**), infra failures mis-tagged as task fail (**#2317**), reasoning token undercount (**#2831**). Use for **rerunnable** bakeoffs, not as a memory score. |
| **lmeb** | **Long-horizon Memory Embedding Benchmark** via `mteb.get_benchmark('LMEB')`; episodic/dialogue/semantic/procedural qrels; instruction prefix `Instruct: …\nQuery:` (wo/ w inst ablation). Reuses many **same-named** chat benchmarks as retrieval-only—does not score generation or abstention behavior. |
| **assistant-benchmark** | End-user assistant rubric; Memory is one dimension among 15 (restraint, proactive, …). |

Use Harbor when we need **fair reruns** of a chosen task set; use LMEB when the product bet is **retrieval quality**, not generation.

---

## Cross-cutting themes (from audits)

1. **LLM-as-judge stacks** — LongMemEval, LoCoMo, BEAM, RealMem, ES-MemEval, ATM-Bench, PrefEval (generation track). Audits note model/version sensitivity and “generous” judging; companion claims need judge + rubric disclosure (RQ-E2, RQ-E5).

2. **QA vs behavior** — Most slugs score **answer correctness** after history is fixed. Few score *whether the assistant brought memory up appropriately* except LoCoMo-Conv and Assistant Benchmark probes.

3. **Abstention & conflict** — LongMemEval, BEAM, EngramaBench, ES-MemEval, HaluMem, MemoryAgentBench (partial). Under-tested in older sets (MemoryBank-era).

4. **Scale arms race** — Context length (BEAM 10M, LME-V2 115M) tests **retrieval/long context**, not necessarily curated memory policies.

5. **Known benchmark pathology** — LoCoMo audit ledger: key errors, cat-5 design, judge overlap with mem0 scripts. **BEAM** audit ledger: heavy issue harvest (label disputes, plan vs chat asymmetry, `int()` vs 0.5 rubric scores). **HaluMem** issue **#10** (broken update gold links). **Harbor** issue **#1960** (grading script leakage between steps). Treat vendor headline % on both as **noisy** until harness + commit pinned.

6. **Reproducibility holes** — PersonaMem (v2 eval script, Drive assets, branch-only datasets per issues), MemoryArena (**repo null**, grader not in HF README), **MemoryAgentBench** (multi-metric logs, library pins issue **#7**), **ATOD** (paper-only in audit), MSC/DuLeMon (ParlAI tree / docs-only seed), PerLTQA (metrics in paper, not README).

7. **MCQ length / prior bias** — PersonaMem **#42** documents slice-dependent longest/shortest-option shortcuts; report length-matched controls before trusting leaderboard MC.

---

## Working steal / refuse / defer (for companion exam design)

Hypotheses only—promote to [`docs/QUESTIONS.md`](QUESTIONS.md) with citations + **Falsifier:** before `settled`.

| Direction | Steal (consider) | Refuse (for now) | Defer |
|-----------|------------------|------------------|--------|
| Task shape | LoCoMo-Conv query styles; MemoryArena interdependence; Mem2Act tool-grounding | Single post-hoc QA as sole exam | Full ATM multimodal until companion scope includes media |
| Grader hygiene | LongMemEval per-type prompts; **PrefEval** explicit MC + disclosed gen error taxonomy; **PerLTQA** anchor MAP; HaluMem stage metrics | Opaque “accuracy %” from blogs; **BEAM** third-party “honest retrieval %”; **PersonaMem** MC without length controls; MemoryAgentBench multi-score logs | Assistant Benchmark until we run probes ourselves |
| Abstention / conflict | LongMemEval abstention; **EngramaBench** adversarial (40 Q, scorer v1.3.1+ leading-abstention fix); ES-MemEval CD | Cat-5 LoCoMo without fixing keys | |
| Agent ingest | MemoryAgentBench chunk feed; MemBench observation vs participation; **Mem2ActBench** tool-grounding levels | Mem2ActBench headline % without custom scorer | MemBench MC without noise length + memory config declared |
| Latency | **LME-V2 LAFS** (multi operating points); **DialSim** sleep_time / timeout-as-wrong | Raw LME-V2 accuracy without latency tier | |
| Retrieval layer | LMEB R_cap@k when product is embed+RAG | LMEB as whole-product score | |
| Harness | Harbor task model + ATIF for agent/memory **instrumentation** (context_management) | Harbor leaderboard reward as “memory quality”; SHARED-mode runs before **#1960** fix | HaluMem extraction F1 without pinning judge + adapter recall limits |

---

## Per-slug notes (full audit read)

Read order follows seed sort. Each block reflects the whole `audit.json` (ledger + unknowns); not leaderboard numbers.

### assistant-benchmark ✓

- **Sources:** assistantbenchmark.com only (4 pages); no repo, no paper in audit.
- **What it scores:** Sixteen named dimensions (site copy also says “15 tasks” in v0.2 meta—treat as one task per dimension, count unsettled). Memory is dimension 10/16: **preference persistence** and **location/conflict** under real use; discrete anchor ladder 3/6/7/10; **min** of probes when both run.
- **Companion-relevant neighbors on same card:** Proactive, Routines, Restraint, Multi-step—not memory in isolation.
- **Runs:** `test` vs `observed` tags; evidence published for dispute; 116 assistants on scorecard, but only 10 Memory rankings in snapshot.
- **Audit gaps (unknowns):** Who assigns 1–10 scores; whether week delay is calendar-verified; full rubric on `/how-scoring-works` not harvested; no reproducible harness.

### atm-bench ✓

- **Sources:** Pinned README + `docs/baseline.md` + `docs/reproducibility.md`, site, HF dataset card, one issue; 47 ledger rows, 22 unknowns.
- **Task:** Human-curated ~4-year personal memory (image, video, email); referential QA with `evidence_ids`; answer only from retrieved evidence or **Unknown**.
- **Ability tags:** PR, LA, MUT, ME, ABS (site); schema also has `qtype` per row.
- **Metrics:** QS as accuracy % (judge **gpt-5-mini**, some rows DeepSeek-V4-flash*); memory systems also report Recall@10 and R@{1…100} over-fetch; joint retrieval+answer summaries for MemPalace.
- **Splits:** `atm-bench.json` vs `atm-bench-hard.json` (31 questions—Harbor per-question Docker mentioned); NIAH uses fixed `niah_evidence_ids` pools (generation-only, not retrieval test).
- **Harness hygiene:** Checkpoint restore / no-update modes; canonical 2B indexer + 8B answerer; mem0 defaults to `--no-mem0-infer` on structured batch items.
- **Compare scores carefully:** Raw multimodal can beat SGM on Oracle but collapses under distractors; agent harness choice moves GLM/Kimi several points—treat harness+model as one system.
- **Audit gaps:** `docs/metrics.md` not in harvest; train/test boundaries unstated; full judge prompt not in audited paths.

### atod ✓

- **Sources:** arXiv abstract + HTML v2 only; 14 ledger rows, 12 unknowns; empty mechanisms/copy/refuse in audit extract.
- **Benchmark vs eval:** **ATOD** = synthetic multi-goal TOD dataset (SGD-seeded LLM pipeline, ~54 turns/dialogue, claims unique combo of async + dependency + interleaving + proactive + turn-level goal annotations). **ATOD-Eval** = metric suite usable offline or online.
- **Primary outcome:** **dGCR** (dependency-aware goal completion rate)—completed goals over *decided* goals, excluding dependency-locked.
- **Memory-adjacent metrics:** Memory Recall Accuracy (strongest correlate with dGCR in paper tables); Proactivity Effectiveness; turn-level relevance + dialogue-level coherence; goal detection F1 and status-tracking accuracy for proposed agentic memory system.
- **Efficiency:** Paper reports per-turn memory update latency (&lt;25s proposed vs &gt;180s LLM-Rsum baseline on complex).
- **Audit gaps:** No public repo in harvest; split sizes and judge prompts for quality/proactivity not in audited text; proactivity formula unspecified.

### beam ✓

- **Sources:** README + `compute_metrics.py` + `run_evaluation.py`, paper HTML, HF card, **8 GitHub issues**; 59 ledger rows, 37 unknowns.
- **Data:** 100 LLM-generated chats (plan → user Q → assistant A), 2,000 probes, length tiers 128K/500K/1M/10M (20/35/35/10 chats); HF viewer shows 100K/500K/1M splits (128K vs 100K naming mismatch in audit).
- **Default eval input:** Whole long chat fed to answerer—not retrieved-memory context (issue #3 discusses adapting pipeline for RAG).
- **Scoring:** Per-category `evaluate_*`; most return mean rubric `llm_judge_score`; semantic align helpers (MiniLM 0.65, bge-large 0.7); event ordering in code uses newline-split response (fact extract commented out) while **paper** specifies Kendall τ-b + LLM equivalence.
- **Rubric scale (issue #14):** 1.0 / 0.5 / 0.0 per item—but **issue #8:** nine evaluators use `int(response['score'])`, zeroing half credit.
- **Label quality (issues #4, #7):** Disputed abstention ideal answers; knowledge-update gold tied to plan metadata not always in `chat.json`.
- **Licenses (README):** code MIT, data CC BY-SA 4.0 (issue #2 predates license clarity).
- **Refuse for comparability:** Issue posters’ “honest retrieval %” unless tied to official `run_evaluation` output at pinned commit.

### dialsim ✓

- **Sources:** README + `simulator.py` + `pseudo_simulator.py`, paper HTML; 45 ledger rows, 14 unknowns.
- **Setting:** Real-time **simulator** over Friends / Big Bang / The Office scripts (5 seasons each); chatbot persona (Ross/Sheldon/Michael); multi-party, ~350k tokens average per show arc.
- **Questions:** **LongDialQA**—hard (`hard_q`, TKG / multi-hop) vs easy (`easy_q`, fan quiz + **unanswerable** ~20%); one question per session, triggered mid-utterance when chatbot speaks.
- **Memory loop:** Incremental session history (in-progress session popped until complete); retrieval `bm25` | `openai-emb` | `no_ret` | **`oracle`** (gt sessions); k tuned by model in code.
- **Metrics:** Primary **accuracy**; secondary **calibrated_score** after ambiguity handling; mean response time; timeouts on save/retrieve/answer fail the item.
- **Grader:** `judge_eq` + **gpt-4o-mini** for `multi_choice_unstructured` and `open_ended`; adversarial **name_shuffle** mode.
- **Reporting:** Paper runs **3×** with mean ± std; no official train/dev/test split (N/A in appendix).
- **Audit gaps:** Judge prompts not in README; structured MC rule logic not documented on page.

### dulemon ✓

- **Sources:** PaddlePaddle Research README + arXiv/ACL anthology pages; **12 ledger rows**, 9 unknowns—thin audit (no harvested PDF body).
- **Focus:** Chinese open-domain **long-term memory** dialogues (Baidu DuLeMon); metrics named **long-term dialogue consistency** and **dialogue engagingness** (PLATO-LTM paper claims).
- **Data shape (README):** Persona statements with tab-separated grounding IDs on utterances; `user_said_persona` vs `user_no_said_persona` for facts revealed vs not yet said (proactive elicitation angle).
- **Harness:** Dataset download script only; **PLATO-LTM evaluation code “coming soon”** at capture—no grader implementation in audited paths.
- **Companion angle:** Consistency/engagingness over sessions, not factoid QA; overlaps Family C with MSC/PersonaMem but **ZH** and pre-LLM-benchmark era.
- **Audit gaps:** Construction, splits, counts, and exact consistency/engagingness formulas not in harvested sources.

### engramabench ✓

- **Sources:** README + `scorer/scorer.py`, paper HTML, Zenodo; 36 ledger rows, 23 unknowns.
- **Design:** Synthetic fictional personas (5), 100 timestamped multi-session convs (late 2025–early 2026), **150 delayed-recall queries** (not next-turn).
- **Families:** single_space (30), cross_space (30), temporal_cross_space (30), adversarial (40), emergent_insight (20).
- **Scoring:** Python **stdlib-only** scorer **v1.4.0**; seven answer types; composite weights documented in repo; emergent_insight = token F1 (paper cautions vs factual slices).
- **Splits:** `pilot_v1` vs `full_v1`; reported results pinned to full_v1 + unified entity registry.
- **Steal hook:** Explicit composite + reproducibility hashes (`corpus/query/judge_prompt_hash` fields in report)—rare among LLM-judge-heavy evals.
- **Audit gaps:** Per-type F1 normalization details partly in scorer body not fully quoted in audit; generation pipeline not in README harvest.

### es-memeval ✓

- **Sources:** README (+ pinned/main), arXiv abstract; 17 ledger rows, 12 unknowns—README-heavy, no harvested paper HTML body.
- **Dataset:** **EvoEmo** in-repo (`data/evo_emo.json`); multi-session emotional-support seekers with fragmented/implicit disclosures (paper abstract).
- **Task bundle:** (1) **QA** with IE/TR/CD/Abs/UM; (2) **summarization** (ROUGE + event P/R/F1 + LLM 0–5); (3) **dialogue generation** under No-Mem / Full-Hist / RAG; (4) **retrieval** R@k and NDCG@k at turn/round/session levels.
- **Companion angle:** Only census eval that scores **emotional support** and **personalization** alongside memory (Table 8 LT-Mem./Pers./ES)—not just fact recall.
- **Audit gaps:** Subtype definitions, judge prompts, Weighted Score formula, EvoEmo size/splits, event-based metric definition—all listed unknowns.

### halumem ✓

- **Sources:** Pinned README + `eval/README.md` + `eval/evaluation.py`, paper abstract, **4 issues**; 46 ledger rows, 30+ unknowns (FMR/weighted recall formulas mostly paper-only).
- **Dataset:** Six-stage LLM+human pipeline (Persona Hub seeds); HF **IAAR-Shanghai/HaluMem**; Halu-Medium vs Halu-Long (same QA/memory-point counts, longer context in Long).
- **Three operations:** (1) **Extraction**—recall/precision/F1 vs golden memory points + false-memory resistance; (2) **Update**—Correct/Hallucination/Omission/Other; (3) **QA**—six types (basic recall, dynamic update, multi-hop, generalization, **conflict**, **boundary**).
- **Harness:** Per-vendor adapters (`eval_memzero.py`, …) then `python evaluation.py --frame …`; parallel per-item grading; invalid judge outputs excluded from “valid” denominators.
- **Steal hook:** Operation-level hallucination tracking (paper: errors compound extraction → update → QA)—closest census analog to **product pipeline** debugging.
- **Audit gaps:** Judge prompts not in harvest; train/test boundary; embedding model for retrieval adapters (issue **#9**); CC-BY-NC-ND badge vs missing LICENSE file (issue **#12**).

### harbor ✓

- **Sources:** Pinned README + **15 GitHub issues** (infra/ATIF/metrics); 52 ledger rows, 60 unknowns—harness-focused, no single “memory task.”
- **Role:** Run/version datasets (`dataset@version`), sandboxes (Daytona, Modal, …), agents (Claude Code, Codex, OpenHands); official **Terminal-Bench-2.0** harness; RL rollouts supported.
- **Scoring model:** Task `tests/` scripts → `reward.json` multi-key floats → `BaseMetric.compute` (e.g. `mean` treats missing keys as **zero**—issue **#2708** proposes `mean_reported`); UI/progress bar often shows **first alphabetical** metric key, not `reward` (**#2396**, **#2782**).
- **Trajectories:** **ATIF** JSON (`trajectory.json`); converters for major CLIs; proposed **prompt_components** + **context_management** for memory/RAG/compaction attribution (**#3078**).
- **Integrity issues:** Multi-step SHARED **#1960**—`/tests/test.sh` and prior verifier logs readable by agent next step (observed model exploit); high uid tar failures (**#1959**); DNS/egress breaking runs (**#3312**); infra errors as honest fails (**#2317**).
- **Companion use:** Instrument **what entered context** and **when** during long agent runs—not a substitute for LoCoMo-style user-memory probes.

### lmeb ✓

- **Sources:** README + `lmeb_benchmark.py` + `metric.py` + `run_lmeb.py`, paper HTML, HF dataset card; 43 ledger rows, 18 unknowns.
- **What it scores:** **Embedding models** (or BM25 baseline)—not end-to-end assistants. 22 constituent benchmarks → 193 zero-shot **test** retrieval tasks.
- **Metrics:** Custom **R_cap@k** = hits@k / min(|relevant|, k); macro-avg skips queries with no relevant docs; leaderboard reporting often **nDCG@10** with optional **R_cap_at_10** in `summarize_results.py`.
- **Memory types (paper):** Episodic, dialogue, semantic, procedural; mix of AI-generated and human qrels; dialogue eval restricted to in-conversation candidate pools.
- **Overlap with census:** Task list includes LoCoMo, LongMemEval, MemBench, ConvoMem, EPBench, KnowMeBench, ReMe, MemGovern, etc.—useful for **retrieval-layer** comparisons only.
- **Findings (paper/README):** Low correlation with MTEB eng v2 retrieval; instruction sensitivity varies by task; larger embedders not uniformly better.
- **Audit gaps:** 193-task macro aggregation details in summarizer; per-dataset train boundaries; MTEB version pin for NDCG implementation.

### locomo ✓

- **Sources:** README + `task_eval/evaluation.py` + `evaluate_qa.py` + `generate_conversations.py`, site, paper abstract, **15+ issues**; 81 ledger rows, 50 unknowns; empty `claimed_purpose` in extract.
- **Data:** 10 long two-speaker conversations; QA with category + evidence dia_ids; optional RAG path (default Contriever top-5).
- **Official metrics:** Per-QA F1 stored as `*_f1`; cat **1** single-hop `f1`, **2–4** multi-hop/temporal/open `f1_score`, **5** adversarial = 1 if output contains “no information available” / “not mentioned”. Event summarization + multimodal gen eval marked **coming soon** in README.
- **Generation:** MSC personas, causal event graphs, ChatGPT T=1.2, BLIP captions; human verification per paper/site.
- **Pathology (issues):** Answer-key errors (#27, #35), cat-5 items answerable from cited turns (#43), DRAGON tokenizer bug (#15), uncontrolled third-party “leaderboard” issues (#26, #31, #33, #34, #39).
- **Refuse for comparability:** Headline F1% without stating **judge script** (official F1 vs gpt-4o-mini CORRECT/WRONG vs Generous Judge) and **pinned** `locomo10.json` commit.

### locomo-conv ✓

- **Sources:** README (pinned + main), paper abstract; 15 ledger rows, 11 unknowns—no harvested scorer source bodies.
- **Design:** Recasts LoCoMo QA into four **conversational** query styles while keeping gold answers + `dia_ids`; adds `expected_memory_use`, `supportive_memory`, composed **two-QA clusters** (1,069).
- **Pipeline:** `construction/` (rewrite, cluster mine, **leakage repair**, validation) → memory-system retrieval scripts (mem0, A-MEM, …) → `response_eval/` judges + retrieval metrics.
- **Steal hook:** Separates **retrieval recall** from **response quality** under dialog framing; paper claims implicit/composed expose gaps vs raw QA.
- **Audit gaps:** Judge prompt text inside `score_*.py`; pairwise three dimensions unnamed in README; license for LoCoMo-Conv additions unset.

### longmemeval ✓

- **Sources:** README + `evaluate_qa.py`, paper HTML, **15+ issues**; 75 ledger rows, 40 unknowns.
- **Abilities (paper/code):** IE, multi-session reasoning, temporal, knowledge-update, preference, **abstention**; internal name mapping in README (e.g. `two_hop` → `multi-session`).
- **End-to-end:** Submit JSONL `{question_id, hypothesis}` → `python evaluate_qa.py <model> …`; macro accuracy + per-`question_type` breakdown.
- **Retrieval track:** Log retrieved sessions → `print_retrieval_metrics.py`; gold **answer location** labels; abstention items skipped (no location).
- **Construction (paper):** LLM-simulated evidence sessions (~70% human-edited); attribute ontology; ~5% yield from generated pool.
- **Pathology:** Wrong session label (issue **#37**); empty `correct_docs` / recall bugs (#7); multi-gold hit definition unsettled (#48); ss-assistant judge abstention artifact (#43).
- **Steal hook:** Disclosed judge prompts + separate retrieval metrics—good template for companion exam **if** oracle metadata and cleaned split are declared.

### longmemeval-v2 ✓

- **Sources:** README + `run_eval.py` + run scripts, paper HTML, **4 issues**; 38 ledger rows, 28 unknowns; empty `claimed_purpose`.
- **Task:** 451 hand-curated Q over **agent trajectories** (AXTree/screenshots); **web** (WebArena) + **enterprise** (WorkArena) domains; context-gathering formulation (not chat-session QA).
- **Haystacks:** **Small** = 100 trajectories shared (~25M tok); **Medium** = ~500 trajectories per question (~115M); reader context capped **200k** tokens.
- **Harness:** Custom memory backend `insert(trajectory)` / `query(text, image?)`—evaluator holds gold, types, IDs private; `evaluation/run_eval.py` + leaderboard `combine_aggregated_metrics.py` for **LAFS**.
- **Baselines (paper):** Fixed reader Qwen3.5-9B; embedding RAG (Qwen3-Embedding-8B); AgentRunbook-C; no-context frontier models ~14.1% (non-abstention).
- **Issues:** Gold contradicts DOM (#1); Codex baseline evidence-status contract unused on abstention slice (#6); transport failures scored as empty (#7).
- **Companion angle:** Tests **specialized environment memory** (workflows, UI gotchas)—orthogonal to user-preference companion probes on LME v1.

### mem2actbench ✓

- **Sources:** README (pinned + main), ACL anthology abstract; 22 ledger rows, 14 unknowns—**pipeline repo**, not a one-command leaderboard harness in audit.
- **Purpose:** Active **memory → tool call** (params grounded in dialogue history), vs passive QA retrieval (paper claim).
- **Build:** Scripts `01`–`05` from BFCL / OASST1 / ToolACE → sessions + `qa_dataset.jsonl` with `tool_call`, `grounding_info`, complexity **L1–L4**; topological sort for temporal merge; BERTopic conflict detection.
- **Scoring intent:** Memory anchoring validation (exact + soft: dates, overlap, fuzzy, semantic)—implementation in construction, not a documented `evaluate.py` entrypoint in harvest.
- **Splits:** `Mem2ActBench/` full + `Mem2ACTbench_small/` default **350** QA for smoke tests.
- **Audit gaps:** Full-set size; official metric aggregation; human rubric for “memory-dependent” tasks; eval runner absent from audited paths.

### membench ✓

- **Sources:** README + `MembenchAgent.py` + `load_test_data.py` + `CommonMemory.py`, paper HTML; 37 ledger rows, 18 unknowns.
- **Axes:** Participation (first-person) vs Observation (third-person); Reflective (high-level prefs) vs Factual (low-level facts); synthetic dialogues from 500 profile graphs (paper).
- **Interaction:** Alternating memory **messages** and MC **questions** with timestamp in prompt; optional `response_cap` stresses memory under continuous QA while writing.
- **Metrics:** MC **accuracy** (single letter JSON); **Recall@10** via `memory.retri()` vs `target_step_id`; per-step write/read **latency**; capacity vs token noise (paper Fig. 5).
- **Harness:** Pluggable `create_memory_module` (Full, GA, MemoryBank, Retrieval, SCMemory, MG, RF, …); noise length ~1k tok/unit; shipped **data2test** at 10k and 100k conversation length.
- **Steal hook:** Clean MC grader + explicit retrieval indices—good contrast to LLM-judge-heavy chat benchmarks.
- **Audit gaps:** Main MemData only on external drives; aggregation across subtypes; runner that collects final scores not in harvest.

### memoryagentbench ✓

- **Sources:** README + `main.py` + `longmem_qa_evaluate.py`, arXiv abstract, **12 issues**; 47 ledger rows, 40+ unknowns; empty `claimed_purpose` in extract.
- **Harness:** `initialize_and_memorize_agent` per context chunk → queries; YAML configs (`HELMET_InfBench`, LongMemEval splits, Movie Rec needs `entity2id.json`); HF `ai-hyz/MemoryAgentBench`; resume via last context/query id.
- **Metrics table (README):** TTL/ICL five sets → **exact_match**; LongMemEval-style → **gpt-4o** judge → mean binary accuracy (temporal off-by-one OK; preference rubric partial OK); `main.py` scales most keys ×100 for %.
- **Construction:** Reformulated prior benchmarks + new **EventQA** / **FactConsolidation** (methodology “coming soon” in README unknowns).
- **Issues:** LoCoMo-style event grounding vs parametric answers (**#10**); which printed score matches paper tables (**#14**, **#5** six signals); Mem0 empty extraction (**#11**); FC-SH naive retrieval vs conflict engine at 32k+ (**#18**); **gpt-4o-mini** retirement (**#16**).
- **Steal hook:** Explicit memorize/query separation + multi-competency configs—good stress test for **agent memory APIs**; refuse single headline % without task YAML + metric column named.

### memoryarena ✓

- **Sources:** arXiv HTML + HF dataset card + README + project site; **no GitHub repo** in identity; 24 ledger rows, 15 unknowns.
- **Tasks:** bundled_shopping, progressive_search, group_travel_planner, formal_reasoning_math/phys—each row = multi-subtask agentic dict with backgrounds + question/answer lists.
- **Metrics (paper §4.2):** **PS** = mean over tasks of (passed subtasks / total subtasks); **SR** = % tasks fully solved; formal reasoning uses T=0, 8192 max tokens, LaTeX outputs.
- **Eval setup (paper):** Progressive search uses OpenAI embedding retriever top-5 × 512 tok; shopping sessions shuffle 5 candidates (1 GT + 2 compatible + 2 incompatible distractors).
- **Claimed gap:** Near-saturated LoCoMo agents score poorly here (abstract)—low SR/PS overall, travel near-zero in paper §4.3.
- **Audit gaps:** Per-env automated graders not specified in README; HF **701** rows vs paper **766** tasks; no version pin; “Code” link on site without URL in harvest.

### memorybank ✓

- **Sources:** SiliconFriend README + `forget_memory.py` + `local_doc_qa.py`, paper HTML; 22 ledger rows, 20 unknowns.
- **Eval data:** `eval_data/{en,cn}/` memory banks + probing JSONL; banks built by ChatGPT role-play (15 personalities, multi-topic days).
- **Paper metrics (human):** **Retrieval Accuracy**, **Response Correctness**, **Contextual Coherence** (0 / 0.5 / 1), **Model Ranking**—example SiliconFriend+ChatGPT en: 0.763 / 0.716 / 0.912 / 0.818.
- **Mechanism in repo:** Ebbinghaus retention `exp(-t/5S)` stochastic drop; FAISS top-6 (forget path) vs top-3 (local_doc_qa); strength increments on recall; OpenAI key for summarization.
- **Companion angle:** Qualitative real-user platform examples + quantitative synthetic probes—early **LT companion** eval, not modern LLM-judge harness.
- **Audit gaps:** No scoring script path in README; train/test boundary; IAA for human rubric.

### msc ✓

- **Sources:** ParlAI `agents.py`, ACL anthology abstract, parl.ai project page; 17 ledger rows, 6 unknowns; **repo null** in seed (ParlAI upstream).
- **Structure:** Sessions **1–5** (S1 PersonaChat); S2–4 train/valid/test files; **no train for S5**; `previous_dialogs`, personas, `time_num`/`time_unit` between sessions.
- **Tasks:** Default `MscTeacher` (sessions 2–4); **PersonaSummary** (gold `goldsum_` vs predicted `predsum_`); subsampled no-persona negatives in train only.
- **Scale:** PersonaSummary **130k** train / **25k** valid (project page); retrieval-augmented + summarization models beat plain encoder-decoder (claim).
- **Audit gaps:** Exact generation metrics and human eval rubric not harvested; wrong arXiv id in one source slot (astrophysics paper—ignored in ledger).

### perltqa ✓

- **Sources:** README + `Dataset/dataset.py` + retriever, arXiv HTML, ACL anthology link; 28 ledger rows, 18 unknowns.
- **Memory model:** Semantic (profiles, social 关系) + episodic (events, dialogues); **memory anchors** per QA; 30 characters fully anchored (labor limit).
- **Tasks:** (1) **Classification**—BERT-base ~95.7% weighted F1; (2) **Retrieval**—BM25 best R@1/R@2, DPR R@5; (3) **Synthesis**—MAP over anchor EM + gpt-3.5-turbo correctness/coherence (Zhong et al. method).
- **Data:** **8,593** questions; synthetic fiction via **gpt-3.5-turbo** + 3 annotators; CC **BY-NC 4.0**; dataset fix **2025-12-22**.
- **Steal hook:** Explicit **anchor MAP** separates retrieval grounding from generation quality—rare structured-memory diagnostic in census.
- **Audit gaps:** Judge prompt not in paper HTML; eval scripts not linked from README; train/test sizes in paper body not re-harvested to code paths.

### personamem ✓

- **Sources:** README (pinned + main), **15 issues**; 30 ledger rows, 50+ unknowns; empty `claimed_purpose`; arXiv id in seed mismatches paper on abs page (harvest quirk).
- **Design:** PersonaHub-seeded **synthetic** multi-session chats; **7** in-situ query types; 15 LLMs on leaderboard; context truncation via `end_index_in_shared_context`.
- **Formats:** v1 `shared_contexts_*.jsonl` + `questions_*.csv`; v2 per-persona JSON under `data/chat_history_32k/`—`inference.py` targets v1 (**#35**, **#36**).
- **Pathology:** Missing Drive creative-writing file (**#15**); Claude context dropped when scoring (**#39**); v1 no-context **49.2%** vs v2 **31.1%** (issue **#42**); length-correlated options by `pref_type` slice; ask_to_forget no-context **14.3%**.
- **Steal hook:** Preference / forget / stereotype slices—companion-relevant if length-balanced; **refuse** headline MC until controls reported.
- **Audit gaps:** Exact MC grader in `inference.py` not quoted; train/test splits; session timestamps missing vs paper (**#37**).

### prefeval ✓

- **Sources:** README + classification + generation scripts + `get_preference_following_accuracy_generation_task.py`, arXiv abstract; 40+ ledger rows in full audit.
- **Data:** Explicit + implicit (choice / persona) JSON per **topic**; Claude-generated seeds + human filter; HF `siyanzhao/prefeval_explicit`.
- **Generation track:** Bedrock models; tasks zero-shot | cot | remind | rag_k | selfcritic; **Preference Following Accuracy** = entry passes only if **none** of four error bits (unhelpful, inconsistent, preference hallucination, preference-unaware)—aggregated % from precomputed `error_*.json` (judge prompt not in scorer file).
- **Classification track:** Shuffled MC (seed **41**); exact letter match; default **5** inter_turns (configurable difficulty); overall accuracy only.
- **Paper claim:** &lt;10% preference following by ~10 turns (~3k tok) zero-shot for most models; reminder arm much higher on leaderboard excerpt.
- **Steal hook:** Declared violation taxonomy + cheap MC correlate—good template for **preference memory** exams; disclose inter_turns + remind condition.

### realmem ✓

- **Sources:** RealMemBench README + arXiv HTML; 26 ledger rows, 20 unknowns; empty `claimed_purpose`.
- **Data:** Multi-agent pipeline (blueprint → events → summary → dialogue); personas from `persona_all.json`; per-persona JSON up to ~256k tok; **synthetic** (Gemini-family construction in paper).
- **Stats (paper):** ~**269k** tok/user, **205** sessions/user, **1,415** questions, **5,072** memories, **11** scenarios; QA **interleaved** within sessions (Table 1 contrast).
- **Metrics:** `compute_auto_metrics_for_realmem.py` → **Recall**, **NDCG** vs `memory_used` annotations (k=10 retrieve in pipeline pseudocode); `compute_llm_metrics_for_realmem.py` default judge **gpt-4o**; default generator **gpt-4o-mini**.
- **Abilities (Figure 2):** Temporal reasoning, static retrieval, dynamic updating, proactive alignment—**no tool-use** eval (limitations).
- **Paper finding:** NDCG often more predictive than recall for downstream QA; human ranking aligned with automated QA score across four systems.
- **Audit gaps:** NDCG@k definition and LLM judge rubric not in README; train/test split; aggregation macro vs micro.

---

## Per-slug pointers (deep dive = audit.json)

| Slug | Audit | Seed `docs` |
|------|-------|-------------|
| assistant-benchmark | [audit](../research/output/by-eval/assistant-benchmark/audit.json) | assistantbenchmark.com |
| atm-bench | [audit](../research/output/by-eval/atm-bench/audit.json) | arXiv:2603.01990 |
| atod | [audit](../research/output/by-eval/atod/audit.json) | arXiv:2601.11854 |
| beam | [audit](../research/output/by-eval/beam/audit.json) | arXiv:2510.27246 |
| dialsim | [audit](../research/output/by-eval/dialsim/audit.json) | arXiv:2406.13144 |
| dulemon | [audit](../research/output/by-eval/dulemon/audit.json) | arXiv:2203.05797 |
| engramabench | [audit](../research/output/by-eval/engramabench/audit.json) | arXiv:2604.21229 |
| es-memeval | [audit](../research/output/by-eval/es-memeval/audit.json) | arXiv:2602.01885 |
| halumem | [audit](../research/output/by-eval/halumem/audit.json) | arXiv:2511.03506 |
| harbor | [audit](../research/output/by-eval/harbor/audit.json) | harborframework.com |
| lmeb | [audit](../research/output/by-eval/lmeb/audit.json) | arXiv:2603.12572 |
| locomo | [audit](../research/output/by-eval/locomo/audit.json) | arXiv:2402.17753 |
| locomo-conv | [audit](../research/output/by-eval/locomo-conv/audit.json) | arXiv:2609.03467 |
| longmemeval | [audit](../research/output/by-eval/longmemeval/audit.json) | arXiv:2410.10813 |
| longmemeval-v2 | [audit](../research/output/by-eval/longmemeval-v2/audit.json) | arXiv:2605.12493 |
| mem2actbench | [audit](../research/output/by-eval/mem2actbench/audit.json) | arXiv:2601.19935 |
| membench | [audit](../research/output/by-eval/membench/audit.json) | arXiv:2506.21605 |
| memoryagentbench | [audit](../research/output/by-eval/memoryagentbench/audit.json) | arXiv:2507.05257 |
| memoryarena | [audit](../research/output/by-eval/memoryarena/audit.json) | arXiv:2602.16313 |
| memorybank | [audit](../research/output/by-eval/memorybank/audit.json) | arXiv:2305.10250 |
| msc | [audit](../research/output/by-eval/msc/audit.json) | ACL 2022 MSC |
| perltqa | [audit](../research/output/by-eval/perltqa/audit.json) | arXiv:2402.16288 |
| personamem | [audit](../research/output/by-eval/personamem/audit.json) | arXiv:2504.14230 |
| prefeval | [audit](../research/output/by-eval/prefeval/audit.json) | arXiv:2502.09597 |
| realmem | [audit](../research/output/by-eval/realmem/audit.json) | arXiv:2601.06966 |

---

## Maintenance

```bash
just harvest-eval <slug>
just audit-write-eval <slug>
just lint-eval-audits
```

When an audit changes, update the **family** and **master table** rows for that slug here; do not copy leaderboard numbers into this file.

**Next synthesis step:** map product mechanisms (from `by-product` audits) onto the axes above—e.g. “product X reports LoCoMo” vs “product Y exposes conflict resolution” — in a separate pass or extended section once `synthesis.json` is refreshed.
