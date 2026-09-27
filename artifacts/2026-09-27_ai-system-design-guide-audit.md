# FINDINGS: AI System Design Guide → companmem

**Campaign:** 07d77f3d  
**Question:** Audit https://github.com/ombharatiya/ai-system-design-guide and identify gems/principles/best practices to adopt for companmem  
**Source:** [ombharatiya/ai-system-design-guide](https://github.com/ombharatiya/ai-system-design-guide)

---

## ★ EXECUTIVE SUMMARY & RECOMMENDATIONS
*Written after 11 research cycles covering all primary guide chapters and companmem's harness codebase.*

### The Short Answer

The guide is a production AI systems reference, not a companion-specific playbook — but it contains exactly the engineering discipline companmem needs to build on. The three areas with the highest direct applicability are: **(1) eval pipeline architecture**, **(2) memory system design principles**, and **(3) speak/silent policy formalization**. companmem's harness is already structurally sound; the gaps are in eval rigor and memory correctness measurement.

---

### TOP 5 ADOPTIONS — highest impact-to-effort ratio

**1. Per-behavior-code aggregate scores in `RunReport`**  
_Source: Eval-Gated CI/CD case study (cycle 002), Anti-patterns (cycle 004)_  
The guide's clearest principle: never gate on a composite quality score — gate per failure-mode axis. The `b0/b1/b3/b5` behavioral codes in `trial.py`'s `_BEHAVIOR_LABELS` are already the right taxonomy. Add one loop to `RunReport.print_summary()` that sums `resolved` by behavior group and emits a per-axis pass rate table. A hallucination regression masked by a formatting win is invisible with composite scoring.  
**Effort:** ~30 lines in `trial.py`. **Impact:** Changes what the eval gate actually measures.

**2. Corrective RAG three-state routing as the speak/silent decision function**  
_Source: Agentic RAG chapter (cycle 006), Memory architectures (cycle 001)_  
The guide's sharpest answer to companmem's central unsolved problem. Instead of a binary speak/silent gate, use three states for retrieved memories:
- `CORRECT` (relevance ≥ 0.85): inject and generate
- `AMBIGUOUS` (relevance 0.5–0.85): supplement with broader context, don't inject raw
- `INCORRECT` (contradicts established fact): discard and abstain

This is more precise than any single-threshold approach and maps directly to the companion's observable failure modes. Implement as a retrieval routing function in the companion's response pipeline.

**3. HaluMem per-operation evals — add extraction-level predicates**  
_Source: LLM Evaluation chapter (cycle 007), codebase gap analysis (cycle 008)_  
The harness evaluates QA output only — what the final reply says and what the final export contains. HaluMem (Nov 2025) showed a system can have high QA accuracy while making catastrophic extraction errors. The `b0-lore-not-autobiography` and `b3-retracted-allergy` fixtures are testing extraction/update correctness *indirectly* through the final export, which can miss extraction errors that resolve by probe time.  
Add a new predicate `kind: must_write_op` that checks the memory write log at ingestion time — what was actually stored when the companion processed the conversation, not just what survives to the final export.

**4. pass^k as the primary reliability metric**  
_Source: Loop engineering (cycle 003), LLM Evaluation (cycle 007)_  
companmem currently reports `resolved_count / runnable_count` = `pass@1`. The guide (tau2-bench) confirms: at 70% per-fixture success rate, `pass^3 ≈ 34%`. A companion that correctly recalls a fact 70% of the time fails every third consecutive session — unacceptable for a relationship product. Add multi-run orchestration (run each fixture k=3 times per adapter) and report `pass@k` and `pass^k` separately in `BaselineResult`. This single change reframes every adapter ranking.

**5. Batch API + prompt caching — halve eval costs with near-zero code change**  
_Source: FinOps chapter (cycle 010)_  
All companmem eval runs are async, offline, no human waiting — the exact workload for the Batch API (~50% discount). The judge LLM call uses a template prompt with a large static prefix that is almost certainly not cached — system prompts are ~69% of input tokens and 72% of production stacks don't cache them (Datadog 2026). Enable `cache_control` on the judge template header + submit eval runs via Batch API. These two changes together reduce eval costs by ~60-70%.

---

### PRIORITY MATRIX — all 29 adoptions

**Tier 1 — Immediate, low effort (< 1 day each)**

| # | Adoption | Where in companmem | Guide source |
|---|---|---|---|
| 1 | Per-behavior-code aggregate scores | `trial.py` `RunReport.print_summary()` | Cycle 002, 004 |
| 2 | Prompt caching on judge template | `scorer.py` `_run_judge()` | Cycle 010 |
| 3 | Most-relevant memories at TOP/BOTTOM of injected block | Companion system prompt / retrieval ordering | Cycle 009 |
| 4 | Structured JSON extraction: (subject, predicate, object) triplets | Memory consolidation step | Cycle 001, 004 |
| 5 | XML `<untrusted_input>` tags on user text before extraction | Memory ingestion pipeline | Cycle 010, 005 |

**Tier 2 — Medium effort, high impact (1–3 days each)**

| # | Adoption | Where in companmem | Guide source |
|---|---|---|---|
| 6 | pass^k computation (k=3 per fixture) | `runner.py` + `trial.py` `BaselineResult` | Cycle 003, 007 |
| 7 | Corrective RAG three-state routing | Companion retrieval layer | Cycle 006 |
| 8 | Relevance threshold gating: retrieve 20, inject top-5 above 0.7 | Companion memory retrieval | Cycle 001, 004 |
| 9 | Memory metadata: `{timestamp, source, confidence_score, access_level}` | All adapter memory writes | Cycle 004 |
| 10 | Abstention phrases in companion system prompt | Adapter system prompts | Cycle 005, 007 |
| 11 | Dev/test fixture split | `evals/fixtures/` organization | Cycle 002, 004 |
| 12 | Batch API for eval harness runs | `runner.py` API calls | Cycle 010 |

**Tier 3 — Medium effort, medium impact**

| # | Adoption | Where in companmem | Guide source |
|---|---|---|---|
| 13 | Stagnation detector in runner | `runner.py` `_run_trial()` | Cycle 003 |
| 14 | Temporal decay for memory relevance | Memory system / adapter config | Cycle 001 |
| 15 | Two-stage injection isolation in memory consolidation | Memory ingestion pipeline | Cycle 005, 010 |
| 16 | Guard model before memory extraction | Memory ingestion pipeline | Cycle 010 |
| 17 | Graph-as-reranker evaluation for Graphiti | Graphiti adapter, eval fixture | Cycle 006 |
| 18 | HaluMem extraction-level predicates (`must_write_op`) | `evals/fixtures/*/tests/predicates.json` | Cycle 007, 008 |
| 19 | Advisor/Executor pattern: cheap model for trial, frontier for judge | `runner.py` + `scorer.py` | Cycle 004, 007 |
| 20 | In-Context RAG hypothesis: `naive_full_context` adapter | `harness/adapters/` | Cycle 009 |

**Tier 4 — Longer horizon**

| # | Adoption | Where in companmem | Guide source |
|---|---|---|---|
| 21 | judgy statistical correction | `scorer.py` LLM judge post-processing | Cycle 002 |
| 22 | LLM judge calibration (60/20/20 split, kappa >0.7) | `evals/` judge calibration suite | Cycle 002, 007 |
| 23 | Nightly cron on main branch | CI/CD configuration | Cycle 002 |
| 24 | Community summarization for long-gap fixtures | Graphiti adapter query strategy | Cycle 006 |
| 25 | Namespace hard partition (user_id) | Any multi-user deployment | Cycle 001 |
| 26 | Self-consistency confabulation detector (3 samples, >0.7 cosine) | Companion response pipeline | Cycle 005 |
| 27 | Canary tokens in system prompt | Adapter system prompts | Cycle 010 |
| 28 | pass^k as headline production readiness metric | Reporting / docs | Cycle 003, 007 |
| 29 | Periodic reflection (goal-node review) | Memory consolidation | Cycle 001 |

---

### KEY INSIGHT

The guide reveals that companmem is solving a problem the field has partially formalized but not solved: **when should a companion surface a memory?** The best answer the guide offers is the Corrective RAG three-state routing (CORRECT/AMBIGUOUS/INCORRECT) — which is more precise than "only speak when memory is directly relevant" but still a heuristic, not a behavioral science answer. companmem's own research (the affective synchrony campaign, the speak/silent campaign) goes beyond what the guide covers for this specific question. The guide's contribution to companmem is primarily in **eval rigor** and **memory system engineering**, not in companion-specific psychology.

The harness is already well-structured — the gaps are:
1. It measures what the companion says, not what it stored (extraction-level gap)
2. It reports pass@1 when pass^k is what matters for reliability
3. It gates on total resolved count when per-behavior-code axes are what should gate

---

## Cycle 000 — Repo Structure & Relevance Map

**Sub-question:** What is the full scope and structure of the guide, and which chapters are most relevant to companmem?

**Finding:** The guide is a 20-chapter, 3.4k-star MIT-licensed living production AI reference (last updated August 2026). Its scope spans foundations, training, inference, prompting, retrieval, agentic systems, memory & state, eval/observability, design patterns, security, and 15 real-world case studies.

For companmem (companion memory benchmark — behavioral scoring of AI companion memory systems), the highest-value chapters are:

| Priority | Chapter | Why it matters to companmem |
|---|---|---|
| ⭐⭐⭐ | `08-memory-and-state` | L1/L2/L3 memory tiers, Mem0, caching — directly maps to what companmem benchmarks |
| ⭐⭐⭐ | `14-evaluation-and-observability` | LLM-as-judge, RAGAS, drift detection — companmem needs eval methodology |
| ⭐⭐⭐ | `07-agentic-systems` | Loop engineering, durable execution, MCP/A2A — harness design |
| ⭐⭐ | `06-retrieval-systems` | Agentic RAG, GraphRAG, ColBERT — memory retrieval strategies |
| ⭐⭐ | `15-ai-design-patterns` | Anti-patterns catalog — what NOT to build |
| ⭐⭐ | `13-reliability-and-safety` | Guardrails, safety — companion speak/silent policy |
| ⭐ | `16-case-studies` | Knowledge Mgmt + Eval-Gated CI/CD case studies |

**Key insight:** The guide explicitly names Mem0 (an adapter in companmem's harness) in chapter 08. The guide's Eval-Gated CI/CD case study (blocking PRs that regress AI quality using golden sets + LLM judges) is a direct architecture template for companmem's planned evaluation pipeline.

**Sources:** [GitHub README](https://github.com/ombharatiya/ai-system-design-guide), [`/home/kaizen/Projects/companmem/README.md`](/home/kaizen/Projects/companmem/README.md)

---

## Cycle 001 — Chapter 08: Memory Architectures & L1/L2/L3 Tiers

**Sub-question:** What specific principles does chapter 08-memory-and-state teach about L1/L2/L3 memory tiers, and how do they map to companmem's adapter set?

**Finding:** Chapter 08 defines a **Three-Tiered Cognitive Architecture**:

| Tier | Type | Tech | Latency | companmem adapter |
|------|------|------|---------|------------------|
| L1 | Working Memory | Context window / KV cache | <50ms | (in-prompt) |
| L2 | Episodic Memory | Vector DB | 100-300ms | a-mem, Telemem |
| L3 | Semantic Memory | Knowledge graph / SQL / Mem0 | >500ms | Mem0, Graphiti, Cognee, Letta, Zep |

**Key principles extracted for companmem:**

1. **Negative Retrieval (most important):** Only inject a memory if it directly contradicts a hallucination or fills a current unknown. This is the closest published formulation of companmem's speak/silent policy — maps to B5 behavioral codes.
2. **Thresholded Relevance:** Only use recalled facts above 0.85 relevance score. Low-value ephemeral facts (e.g., "it's raining") auto-deleted after 24h — maps to B3 (stale-job-purged, retracted-allergy).
3. **Memory Consolidation:** End-of-session LLM Reviewer extracts facts from L1 → L2 (vectors) + L3 (graph). Companmem's harness should test whether this consolidation is triggered and works correctly.
4. **Temporal Decay:** Old, non-reinforced memories lose relevance unless accessed. Critical gap in most adapters.
5. **Periodic Reflection:** Daily goal-node review → proactive reminders. Maps to companmem's three-month-gap fixture (B1).
6. **Catastrophic Forgetting via Index Overload:** Too many low-quality facts bury quality ones → mitigate with quality-weighted retrieval.
7. **Namespace Sharding:** user_id is a hard partition key, never LLM-filtered — cross-session leakage is #1 security risk.

**Adapter-to-tier mapping from the guide:** Mem0=managed L3 facts (entity linking, temporal weighting); Letta=OS-style paging for long-running agents; Zep=temporal-aware production pipeline; Cognee/Graphiti=graph-RAG L3. Honcho and LangMem not mentioned by name.

**Sources:** [01-memory-architectures.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/08-memory-and-state/01-memory-architectures.md), [03-long-term-memory.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/08-memory-and-state/03-long-term-memory.md), [04-agentic-memory-mem0.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/08-memory-and-state/04-agentic-memory-mem0.md)

---

## Cycle 002 — Case Study: Eval-Gated CI/CD → companmem eval pipeline template

**Sub-question:** What does the Eval-Gated CI/CD case study prescribe as a template for companmem's eval pipeline?

**Finding:** The case study is a complete, production-proven blueprint. Key principles mapped to companmem:

**Architecture (3 stages):**
1. Cheap static checks (lint, unit, type) — 2 min
2. Golden-set eval: code-based evaluators + LLM judge
3. Statistical correction with [`judgy`](https://github.com/ai-evaluation/judgy) → CI-bounded estimate vs main

**Critical principle — gate per-axis, NOT composite:** A single quality score hides regressions. Gate on per-axis scores from a failure-mode taxonomy. For companmem: `b0`, `b1`, `b3`, `b5` behavioral codes ARE the failure-mode taxonomy axes.

**Golden set construction (1,200 cases minimum):**
- 3 sources: production trace samples (90d, stratified by failure mode) + synthetic adversarial cases + customer-ticket edge cases
- 10–15% quarterly rotation; never delete (archive to historical regression set)
- Below 1,200 cases: CI too wide to detect 2-point regression at 95% confidence

**LLM judge discipline:**
- Treat judge prompt as a model with 60/20/20 train/dev/test split
- Cohen's kappa >0.7; recalibrate every 30 days with 50 fresh human-labeled cases
- Judge accuracy must stay >80% on dev set

**Statistical correction:** Raw judge score is biased (~75–88% accuracy). `judgy` computes corrected estimate + CI from judge's confusion matrix on held-out set. Gate on CI lower bound within tolerance vs main.

**Cost control:** Default 10–25% stratified sample per PR (<$40); `full-eval` label requires CODEOWNERS approval; nightly cron runs 100% on main; cache (prompt-hash, model-version) → (output, judge-score) for ~70% cache hit rate.

**Block-rate SLI:** Target 5–12%. If higher, developers learn to ignore the gate. Tune gating tolerance to stay in range.

**companmem 1:1 mapping:**
- `evals/fixtures/` = golden set cases
- `harness/runner.py` = eval runner
- `harness/scorer.py` = code-based evaluators + LLM judge layer
- `b0/b1/b3/b5` behavioral codes = per-axis failure-mode taxonomy
- Missing: `judgy` statistical correction layer, judge recalibration cadence, nightly cron on main

**Sources:** [16-case-studies/18-eval-gated-cicd.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/16-case-studies/18-eval-gated-cicd.md)

---

## Cycle 003 — Chapter 07: Loop Engineering → harness runner design

**Sub-question:** What does loop-engineering say about loop design, termination, and budgets applicable to companmem's harness runner?

**Two invariants (most important):**
1. **Termination is enforced by the harness on deterministic criteria, never by the model's own claim it is done.**
2. **The entity that verifies the work is structurally separate from the entity that produces it.**

**The mental model:** "The model is the policy, the harness is the kernel." Loop quality is a distinct discipline from base-model quality.

**Stop conditions every loop needs (multiple categories required):**
- Goal predicate passes (SUCCESS) — task-specific, deterministic test
- Retry limit: 3–5
- Max iterations: 10 for QA tasks
- Wall-clock timeout: 60–300s
- Token/dollar ceiling — enforced OUTSIDE the agent at a gateway
- Per-tool quota
- No-progress / oscillation detector: 3 identical (tool, args) calls, or plan similarity >95%
- Rate-of-spend breaker (not just cumulative — loops can burn hundreds of dollars in 20 minutes)

**Generator-verifier (maker-checker) separation:** One subagent drafts; a separate, often stronger subagent grades adversarially. Models self-grade optimistically; research shows intrinsic self-correction can degrade reasoning.

**Fresh-context technique:** Reset window each cycle, track progress in an external state file, exit on a predefined verifiable condition (stop hook verifies before allowing exit). Directly applicable to companmem's per-trial execution model.

**pass@k vs pass^k:** At 70% per-attempt success rate, the gap between pass@k and pass^k is already large by k=3. A companion that recalls correctly 70% of the time has pass^3 ≈ 34% — unacceptable for customer-facing reliability.

**Anti-patterns applicable to companmem:**
- **Loopmaxxing:** Ambiguous goals with no verifiable exit ('improve UX', 'improve relationship quality') — need concrete predicates
- **Context rot:** Quality degrades silently before hard context limit — externalize state to disk
- **Hallucinated success:** Trusting model's self-report — need deterministic verifier + goal predicate
- **Objective misspecification:** Proxy goals like deleting a failing test → termination criteria must capture intent
- **Self-policed budget:** Enforce spend at gateway, not in agent code

**For companmem's harness specifically:**
- Missing: stagnation detector (hash `(adapter, tool_name, args)` tuples, abort on 3 identical calls)
- Missing: budget enforcement outside runner.py (currently in-process)
- `pass@k` vs `pass^k` should be computed and reported separately in scorer.py
- "Relationship coherence" metric needs a concrete binary predicate for deterministic termination

**Sources:** [07-agentic-systems/12-loop-engineering.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/07-agentic-systems/12-loop-engineering.md)

---

## Cycle 004 — PATTERNS.md + 15-ai-design-patterns/02-anti-patterns.md

**Sub-question:** What anti-patterns should companmem avoid?

**Anti-patterns directly applicable to companmem:**

| Anti-Pattern | companmem impact | Fix |
|---|---|---|
| **God Prompt** | Companion system prompt grows into a 5k-token monster | Route to specialized handlers (persona, memory, tone) |
| **Vibes-Based Evaluation** | "Looks good to me" — the anti-pattern companmem exists to fight | Systematic 100+ case eval set with baselines |
| **Training on Test Set** | Iterating on the same fixtures that grade → overfitting | dev/test split — 60/20/20 (maps to judgy methodology) |
| **Agent Without Memory** | The core problem companmem is solving | Persistent memory store with session continuity |
| **Infinite Loop Risk** | No cost/time stop conditions in runner.py | max_steps + max_cost + wall-clock timeout |
| **Retrieve Everything** | Stuffing 50 memories into context → Lost in Middle | Retrieve 20, rerank, inject top-5 above 0.7 score |
| **Ignoring Metadata** | Memories without timestamps/source/trust level | Every memory: timestamp, source, confidence, access_level |
| **No Output Format** | Free-form memory extraction → unparseable | Structured JSON extraction (subject/predicate/object triplets) |
| **Single Provider Dependency** | Judge model has no fallback | Keep two judge models calibrated in parallel |

**Key positive pattern for companmem:**
- **Advisor/Executor (2026):** Cheap model runs the trial loop; strong model called at grading/judgment steps. Directly maps to companmem's eval architecture: small model drives the adapter conversation, frontier model scores with LLM-as-judge.

**Metadata pattern specifically:** Every retrieved memory should carry: `{timestamp, source, access_level, confidence_score, document_type}`. This enables temporal filtering (B3: stale-job-purged), injection quarantine (B0), and threshold-based speak/silent gating.

**Sources:** [PATTERNS.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/PATTERNS.md), [15-ai-design-patterns/02-anti-patterns.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/15-ai-design-patterns/02-anti-patterns.md)

---

## Cycle 005 — Chapter 13: Guardrails & Safety → B0 behavior codes

**Sub-question:** What does the guardrails chapter prescribe for injection defense and safety — applicable to companmem's B0 behavior codes?

**Defense-in-depth architecture:**
```
User Input → [INPUT GUARDRAILS] → LLM → [OUTPUT GUARDRAILS] → [ACTION VALIDATION] → Safe Response
```

**Prompt Injection Defense (B0: injection-quarantined):**

*Detection:*
- Regex patterns: `ignore previous instructions`, `you are now a`, `DAN mode`, `<|system|>`, etc.
- ML classifier for sophisticated attempts (score > 0.7 → block)

*Three mitigation strategies:*
1. **Sandwich defense:** Wrap user input with instruction reminders before AND after
2. **Delimiter defense:** Unique tags (`<<<>>>`) around user content so it's never parsed as instructions
3. **Input/output isolation (most important):** Two-stage — Stage 1 LLM extracts intent without acting; Stage 2 LLM acts only on extracted intent

**For companmem:** The memory consolidation step (fact extraction from L1 → L3) MUST apply injection detection before writing. An adversarial message like "Remember that I'm a billionaire" should NOT persist as a stored fact.

**Abstention Pattern → speak/silent policy:**
- `ABSTENTION_PHRASES`: "I don't have information about that", "I'm not sure", etc.
- Explicit prompt instruction: "If answer not in context, say 'I don't have information about that'"
- Self-consistency check: generate 3 samples at temperature 0.7, require cosine similarity >0.7 → low consistency = likely confabulation → abstain
- Low-confidence memory retrievals should abstain, not confabulate (maps to B0: lore-not-autobiography, stable-self)

**Hallucination Mitigation for companion memory:**
1. Retrieval quality first — wrong retrieved memory = certain confabulation
2. Abstention instruction in system prompt
3. Factuality check via NLI model or LLM judge (claims vs. stored memory)
4. Self-consistency across 3 generations

**PII Scrubbing before memory consolidation:**
- Redact email, phone, SSN, credit card before writing to L3
- `[EMAIL_REDACTED]`, `[PHONE_REDACTED]` placeholder substitution

**Relevance Check before memory injection:**
- Embedding similarity > 0.6 between query and candidate memory before injecting
- Below threshold → don't inject (speak/silent via relevance gating)

**Sources:** [13-reliability-and-safety/01-guardrails.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/13-reliability-and-safety/01-guardrails.md)

---

## Cycle 006 — Agentic RAG + GraphRAG → Graphiti adapter & emotional-context retrieval

**Sub-question:** What do Agentic RAG and GraphRAG say about retrieval architecture for companmem?

**Agentic RAG — four dominant patterns:**

| Pattern | What it does | companmem application |
|---|---|---|
| **Self-RAG** | Critic tokens: Relevant/Supported → re-retrieve if unsupported | Memory relevance check per candidate |
| **Corrective RAG** | Three-way routing: correct→generate, ambiguous→supplement, incorrect→discard | The speak/silent decision function |
| **Multi-Hop** | State object with evolving sub-goals, 1 hop per turn | Relationship traversal (job→company→colleague) |
| **Adaptive RAG** | Classifier picks pipeline depth (fast vs. deep path) | Route casual query to fast path, emotional query to deep |

**Production budget:** 3–5 turns max before forcing final answer; 8–12s typical for 3–4 iteration loop.

**CORRECTIVE RAG as speak/silent decision function (most important):**
- **CORRECT** (high relevance score): Inject memory and generate
- **AMBIGUOUS** (low confidence): Supplement with broader pattern search — don't inject raw
- **INCORRECT** (contradicts known fact): Discard and abstain

This is more precise than "Negative Retrieval" from cycle 001. It gives companmem a three-state decision function to implement in `scorer.py` / memory retrieval path.

**GraphRAG for companion memory:**

The dominant 2026 pattern is **graph-as-reranker**, NOT full GraphRAG:
1. Vector retrieves top-50 chunks
2. Entity extractor pulls named entities from those chunks
3. Graph traverses 1–2 hops from those entities → expanded candidates
4. Cross-encoder reranker on original + expanded set → top-k
5. Generator uses reranked top-k

**Why companion memory IS graph-shaped:**
- `(User) → works_at → (Company X)` traversal needed to answer "how is work going?"
- `(User) → mentioned → (Event: Birthday)` needed for temporal follow-up
- `(User) → has_preference → (Dark Mode)` needed for any session

**GraphRAG decision rule:** Pull 100 failed retrievals, tag as lexical / synthesis / graph-shaped. Build graph only if graph-shaped share ≥ 30%.

**Maintenance tail:** Graph built in January is meaningfully wrong by April. Plan quarterly refresh. Without it: "retrieves confidently and wrongly" — worse than no graph. **This is the key risk for Graphiti adapter.**

**Community summarization:** Hierarchical cluster summaries answer "what did we talk about over 3 months" without reading all memories — maps to companmem's B1 (three-month-gap fixture).

**HippoRAG variant:** Treats retrieval as Personalized PageRank over a memory graph — strong multi-hop benchmark results at lower index cost than Microsoft GraphRAG.

**Sources:** [06-retrieval-systems/08-agentic-rag.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/06-retrieval-systems/08-agentic-rag.md), [07-graph-rag.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/06-retrieval-systems/07-graph-rag.md)

---

## Cycle 007 — Chapter 14: LLM Evaluation → eval harness methodology

**Sub-question:** What does LLM eval chapter add beyond the case study?

**Judge biases to mitigate in companmem's LLM judge:**
- **Position bias** → randomize order in pairwise comparisons
- **Length bias** → instruct judge to ignore length
- **Self-preference** → use different model as judge than the one being tested
- **Format bias** → diverse few-shot examples in judge prompt

**Calibrated pairwise judge pattern:**
```python
result1 = judge(question, response_a, response_b)
result2 = judge(question, response_b, response_a)  # swapped
if result1 agrees with result2_adjusted: → high confidence
else: → tie / low confidence
```
companmem's scorer should implement this swap-and-compare.

**RAGAS metrics mapped to companion memory:**
- `faithfulness` = is companion response grounded in stored memories?
- `answer_relevancy` = does response address the user's message?
- `context_precision` = are retrieved memories relevant to the query?
- `context_recall` = did we retrieve all needed memories?

**HaluMem (Nov 2025) — most important finding for companmem:**

Breaks memory hallucination evaluation into three separate operations:

| Operation | What's measured | companmem fixture |
|---|---|---|
| **Extraction** | Fact written to memory matches source | B0: lore-not-autobiography |
| **Update** | Memory update correct relative to prior state | B3: retracted-allergy |
| **QA** | Answer grounded in stored memories | All fixtures |

**Critical insight:** A system can hit high QA accuracy while making catastrophic extraction errors. Aggregate metrics hide the failure site. **5% extraction error rate compounds into a wholly unreliable agent over time.**

companmem's harness currently evaluates QA output only — missing extraction and update correctness. Adding per-operation evals would catch the exact failure modes B3 and B0 are testing for.

**2026 eval stack (defensible production pattern):**
1. **Distilled judges inline** on every trace (Luna-2: 97% cheaper, 88-92% agreement) — taxonomy-bounded
2. **Frontier judge** on 1-5% sampled traces for drift calibration
3. **Human review** on disagreements → updates gold set
4. **Quarterly distilled judge retraining** from updated gold set

**pass^k metric (tau2-bench):** `pass^4` = prob agent succeeds on ALL 4 repeated trials. `pass^1=70%, pass^4=12%` = "works on easy path, cannot recover from any perturbation."

**Agent trajectory grading:** For memory-equipped companions, grade the trajectory (sequence of memory reads, writes, responses) not just the final answer. PRMs score each step. Failure modes: right-answer-wrong-reasoning, right-answer-dangerous-path, over-retrieval, tool-flailing.

**Sources:** [14-evaluation-and-observability/01-llm-evaluation.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/14-evaluation-and-observability/01-llm-evaluation.md)

---

## Research State

**Answered:**
- Repo structure and full chapter inventory ✅
- Which chapters are highest-value for companmem ✅
- L1/L2/L3 tier taxonomy and adapter mapping ✅
- Corrective RAG as speak/silent decision function (correct/ambiguous/incorrect) ✅
- Eval-Gated CI/CD architecture → companmem pipeline template ✅
- Loop engineering → harness runner termination, stagnation, pass@k vs pass^k ✅
- Anti-patterns catalog → 9 directly applicable ✅
- Guardrails + injection defense → B0 behavior codes ✅
- Agentic RAG + GraphRAG → Graphiti adapter ✅
- LLM eval methodology → HaluMem per-operation evals, judge calibration, 2026 stack ✅

**Open questions (lower priority, remaining research value):**
1. `08-memory-and-state/06-state-management-patterns.md` — state patterns
2. companmem's own codebase harness/scorer.py — ground guide findings against actual implementation
3. Any guide chapters on FinOps / token economics relevant to companmem's eval budget

**Assessment:** Core research is substantially complete. 8 cycles have covered the primary chapters relevant to companmem. The highest remaining value is reading companmem's own `harness/scorer.py` and `harness/runner.py` to produce concrete gap analysis (rather than more guide chapters). This is a natural pivot point toward synthesis.

**Dead-ends:** Honcho and LangMem not in guide. Emotional/affective context not in guide (companmem's own artifacts are better source).

**Weak spots:** HaluMem per-operation evals are a confirmed gap in companmem's harness (no extraction-level or update-level eval, only QA-level)

---

## Cycle 008 — companmem harness codebase gap analysis

**Sub-question:** Where are the specific gaps between guide principles and actual harness implementation?

**Harness strengths (already aligned with guide):**
- `fail_to_pass` / `pass_to_pass` predicate structure = "delta vs main" CI pattern from case study ✅
- `git_sha` tracked in every run report ✅
- `wall_ms`, `tokens_in/out`, `memory_tokens` tracked per trial ✅
- Behavioral codes `b0/b1/b3/b5` present in trial metadata ✅
- Fixture metadata has `pass_proves` / `fail_reveals` / `why_naive_fails` ✅
- Separation of concerns: world / adapter / scorer / artifacts / runner ✅

**Confirmed gaps (guide principle → missing in harness):**

| Gap | Guide principle | Harness status |
|---|---|---|
| **pass^k** | tau2-bench: compute pass^k for production reliability | Only pass@1 (resolved_count/runnable_count) |
| **Per-axis aggregate scores** | Gate on per-axis failure-mode taxonomy | b0/b1/b3/b5 per-trial but not summed in report |
| **Extraction-level predicates** | HaluMem: evaluate write/update operations separately | All predicates test final reply/export, not write ops |
| **Judge calibration** | Train/dev/test split, Cohen's kappa, recalibration cadence | Single LLM call at temp=0, no calibration |
| **Statistical correction** | judgy: convert biased judge score to CI-bounded estimate | Raw float 0.0–1.0, no CI |
| **Stagnation detector** | Hash (tool, args) tuples, abort on 3 identical calls | Not present |
| **Budget enforcement outside runner** | Enforce at gateway, not in agent code | cost_flags are passive (flag only, don't abort) |
| **Nightly CI cron on main** | Catch drift not caught by per-PR samples | Not present |
| **Dev/test fixture split** | Don't iterate on same fixtures you use as final gate | All 9 fixtures used for both development and evaluation |
| **Judge swap-and-compare** | Run pairwise judge twice with swapped order; check consistency | Single call, no position-bias mitigation |

**Three most actionable additions (lowest effort, highest impact):**

1. **Per-behavior-code aggregate scores in `RunReport.print_summary()`** — behavioral codes already in trial metadata; just sum `resolved` by behavior group. This gives the per-axis gating the guide mandates.

2. **pass^k computation** — run each fixture k=3 times per adapter; `pass@k` = at least 1 of k succeeds; `pass^k` = all k succeed. Add to `BaselineResult`. Already tracked per-trial, just needs multi-run orchestration.

3. **Extraction-level predicates** — add a new predicate `kind: must_write_op` that checks the memory write log (if adapter emits it) for what was written at ingestion time, not just what the final export contains. This is the HaluMem extraction-stage eval.

**Sources:** [`/home/kaizen/Projects/companmem/harness/scorer.py`](/home/kaizen/Projects/companmem/harness/scorer.py), [`/home/kaizen/Projects/companmem/harness/runner.py`](/home/kaizen/Projects/companmem/harness/runner.py), [`/home/kaizen/Projects/companmem/harness/trial.py`](/home/kaizen/Projects/companmem/harness/trial.py)

---

## Research State

**Answered:**
- Repo structure and full chapter inventory ✅
- Which chapters are highest-value for companmem ✅
- L1/L2/L3 tier taxonomy and adapter mapping ✅
- Corrective RAG as speak/silent decision function ✅
- Eval-Gated CI/CD architecture → companmem pipeline template ✅
- Loop engineering → harness runner termination, stagnation, pass@k vs pass^k ✅
- Anti-patterns catalog → 9 directly applicable ✅
- Guardrails + injection defense → B0 behavior codes ✅
- Agentic RAG + GraphRAG → Graphiti adapter ✅
- LLM eval methodology → HaluMem per-operation evals, judge calibration, 2026 stack ✅
- companmem codebase gap analysis → 10 concrete gaps identified ✅

**Open questions (remaining low-priority):**
1. `08-memory-and-state/06-state-management-patterns.md` — minor remaining gap
2. `05-prompting-and-context` — prompt injection patterns specific to companion context?

**Assessment:** Research is substantially complete. 9 cycles in, covering all primary guide chapters + companmem codebase grounding. Ready for synthesis / executive summary.

**Dead-ends:** Honcho and LangMem not in guide. Emotional/affective context not in guide scope.

---

## Cycle 009 — State Management + Context Engineering → harness and companion prompt design

**Sub-question:** What do state-management and context-engineering chapters add for companmem?

**State Management patterns for companmem:**
- **TypedDict State Object, append-only** — prevents data loss in long eval loops; maps to companmem's `world.py` conversation state
- **State Pruning:** trim `tool_results` once sub-task is complete; Summarizer Node every 10 turns — maps to adapter session management
- **Checkpointing:** persist every state update to disk; resume from last checkpoint_id on crash — harness `run_manifest.json` is already this pattern ✅
- **Time-travel = rescore:** the guide's "edit state at timestamp X and re-run" = what companmem's `python -m harness score --run-id <id>` already does ✅

**Context Engineering — five techniques (ranked by relevance to companmem):**

| Technique | companmem application |
|---|---|
| **Structured note-taking** | Companion writes active goals to a scratch file; re-reads on next session (B1: three-month-gap) |
| **Sub-agent isolation** | Each harness trial uses a clean window (already true for most adapters) |
| **Just-in-time loading** | Hold memory IDs, fetch full content on demand — avoids stuffing 1000-fact exports |
| **Compaction** | After 10+ turns of companion session, summarize history before continuing |
| **System prompt calibration** | Companion system prompt: Goldilocks zone — specific enough to be reliable, general enough not to be brittle |

**Lost-in-the-Middle → memory injection ordering:**
- Place most relevant memories at the **BEGINNING and END** of the injected memory block, not the middle
- Middle = raw less-relevant memories; first/last = highest-relevance anchor memories
- This is a one-line change to any companion system that injects retrieved memories in chronological order

**In-Context RAG hypothesis for companmem:**
- For users with <1,000 stored facts: stuffing all memories into context may outperform vector retrieval
- Hypothesis: small memory stores have better recall via In-Context RAG than via retrieval (no retrieval gap)
- **Testable with companmem's harness:** add a `naive_full_context` adapter that injects 100% of exported memories and compare against retrieval-based adapters

**Context budget for companion turns:**
- System prompt: 500–1,000 tokens
- Conversation history: 2,000–5,000 tokens
- Retrieved memories: 10K max (rerank top-5–10)
- Output reserve: 1,000–4,000 tokens

**Prompt caching:** If system prompt + base knowledge > 100K tokens and reused across >2 requests, prefix caching ($0.05/1M) is cheaper than RAG ($5.00/1M). For companmem's eval runs, use a stable system prompt prefix to maximize cache hit rate.

**Sources:** [08-memory-and-state/06-state-management-patterns.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/08-memory-and-state/06-state-management-patterns.md), [05-prompting-and-context/05-context-engineering.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/05-prompting-and-context/05-context-engineering.md)

---

## Research State

**Answered:**
- Repo structure and full chapter inventory ✅
- Which chapters are highest-value for companmem ✅
- L1/L2/L3 tier taxonomy and adapter mapping ✅
- Corrective RAG as speak/silent decision function ✅
- Eval-Gated CI/CD architecture → companmem pipeline template ✅
- Loop engineering → harness runner termination, stagnation, pass@k vs pass^k ✅
- Anti-patterns catalog → 9 directly applicable ✅
- Guardrails + injection defense → B0 behavior codes ✅
- Agentic RAG + GraphRAG → Graphiti adapter ✅
- LLM eval methodology → HaluMem per-operation evals, judge calibration, 2026 stack ✅
- companmem codebase gap analysis → 10 concrete gaps identified ✅
- State management + context engineering → memory injection ordering, In-Context RAG hypothesis ✅

**Open questions (remaining low-priority):**
1. `05-prompting-and-context/08-prompt-injection-defense.md` — dedicated injection defense (may add to cycle 005 findings)
2. Any case studies involving companion / emotional AI systems

**Assessment:** 10 cycles complete. All primary guide chapters covered. The research is now deep enough to support a strong executive summary. The remaining 20 cycles could productively explore: deeper fixture analysis, remaining case studies, or start moving toward writing actionable recommendations directly to companmem's docs.

**Dead-ends:** Honcho and LangMem not in guide. Emotional/affective context not in guide scope.

---

## Cycle 010 — Prompt Injection Defense + FinOps → ingestion pipeline and eval cost

**Sub-question:** What do the dedicated injection defense and FinOps chapters add for companmem?

**Prompt Injection Defense — three new concepts:**

**1. Dual-LLM (Security Proxy) pattern:**
- Tiny guard model (0.5B) checks input FIRST for injection patterns
- Frontier logic model only sees input if guard passes
- Logic model never sees malicious instructions in a "high-trust" context
- **For companmem:** Wrap user-provided text in `<untrusted>` XML tags before extraction LLM. Add guard model pass before any memory write operation.

**2. XML/marker isolation (H-Rank training):**
- Frontier models (Claude Sonnet 4.6, GPT-5.5, Gemini 3.1) have H-Rank training: tokens inside `<untrusted>` tags get **lower instruction-following weight**
- This is the structural defense for companion memory ingestion
- Example: wrap conversation text in `<user_conversation>` tags, system prompt in `<system>` tags — model treats them differently

**3. Indirect Injection in RAG (highest risk for companion memory):**
- A document retrieved from external source (web page, shared file) may contain hidden instructions
- When LLM reads the retrieved chunk to answer a question, it executes the hidden command
- **Defense:** Treat ALL retrieved chunks as "Untrusted Data" — separate Analyzer pass extracts facts before final generator sees them
- **Canary Tokens:** Place secret strings in system prompt; if they appear in output → response is blocked (leaked system prompt detection)

**Direct implication:** companmem's adapter ingestion pipeline should wrap user-provided text in XML `<untrusted_input>` tags before the extraction LLM processes it. The memory consolidation step (L1 → L3) must use a separate Analyzer pass, not a single LLM call that both sees user text and writes to memory.

**FinOps — two most actionable findings for companmem:**

**1. Batch API for eval harness runs:**
- Anthropic + OpenAI: ~50% discount on batch processing, 24h completion ceiling
- companmem's eval harness is exactly the offline, async workload that qualifies
- Current: synchronous API calls per trial; potential: batch API at half cost
- 9 fixtures × 10 adapters = 90 trials; if $0.05 avg per trial → $4.50 sync → $2.25 batch
- With pass^k (3 runs per fixture) → $13.50 sync → $6.75 batch

**2. System prompt cache hit rate:**
- System prompts are ~69% of input tokens; only ~28% of production stacks cache them (Datadog 2026)
- companmem's judge LLM call uses a template prompt — static prefix not cached
- Enabling `cache_control` on the judge template prefix → ~50-90% discount on judge prompt tokens

**Cost anti-patterns directly applicable to companmem's harness:**
- **Reasoning on by default:** Gate Extended Thinking by task complexity (classifier < 0.5 → skip)
- **Real-time for offline work:** All eval runs are async/offline → use Batch API
- **No attribution:** Tag every LLM call by adapter_id, fixture_id, run_id for cost attribution

**Sources:** [05-prompting-and-context/08-prompt-injection-defense.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/05-prompting-and-context/08-prompt-injection-defense.md), [11-infrastructure-and-mlops/04-finops-and-token-economics.md](https://github.com/ombharatiya/ai-system-design-guide/blob/main/11-infrastructure-and-mlops/04-finops-and-token-economics.md)

---

## Research State

**Answered:**
- Repo structure and full chapter inventory ✅
- Which chapters are highest-value for companmem ✅
- L1/L2/L3 tier taxonomy and adapter mapping ✅
- Corrective RAG as speak/silent decision function ✅
- Eval-Gated CI/CD architecture → companmem pipeline template ✅
- Loop engineering → harness termination, stagnation, pass@k vs pass^k ✅
- Anti-patterns catalog → 9 directly applicable ✅
- Guardrails + injection defense → B0 behavior codes ✅
- Agentic RAG + GraphRAG → Graphiti adapter ✅
- LLM eval methodology → HaluMem, judge calibration, 2026 stack ✅
- companmem codebase gap analysis → 10 concrete gaps identified ✅
- State management + context engineering → memory injection ordering ✅
- Prompt injection defense (dedicated chapter) → Dual-LLM, XML H-Rank, Indirect Injection ✅
- FinOps → Batch API for eval runs, prompt caching for judge ✅

**Open questions (remaining):**
- Any case studies with companion / relational AI memory architectures
- `11-infrastructure-and-mlops/03-ai-gateways-and-model-routing.md` → model routing for adapter selection

**Assessment:** 11 cycles complete. All primary and secondary guide chapters now covered. Research is ready for synthesis in the next cycle or two. Remaining cycles can either explore case studies or write the executive synthesis.
