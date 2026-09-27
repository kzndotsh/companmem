---
title: "Analysis — shisad Long-Term Memory (v0.7.3, 2026-05-09)"
date: 2026-05-09
type: analysis
system: shisad (Shisa AI personal assistant daemon)
source: /home/lhl/github/shisa-ai/shisad (v0.7.3 tag, commit f20930b)
version: "v0.7.3 (core memory system complete; only v0.7.4 eval/benchmarking harness remains)"
related:
  - ANALYSIS.md
  - ANALYSIS-academic-industry.md
  - ANALYSIS-claude-code-memory.md
  - ANALYSIS-codex-memory.md
  - ANALYSIS-karta.md
  - ANALYSIS-mira-OSS.md
  - ANALYSIS-coolmanns-openclaw-memory-architecture.md
tags:
  - agentic-memory
  - security-first
  - trust-model
  - executive-assistant
  - knowledge-graph
  - bi-temporal
  - procedural-memory
  - prompt-injection-defense
  - consolidation
  - benchmarks
  - timeline
  - thread-resume
---

# Analysis — shisad Long-Term Memory System

Deep analysis of the **shisad long-term memory architecture** as of **v0.7.3** (2026-05-09). v0.7.3 completes core memory system functionality; only the v0.7.4 external evaluation/benchmarking harness remains on the roadmap.

shisad is a personal/executive assistant daemon with multi-channel presence (CLI, Discord, Slack, Telegram, Matrix). The memory system supports single-user executive-assistant workflows and multi-channel ingestion with provenance-aware trust handling, per-user/workspace scoping, and temporal querying.

File-path references below point into `~/github/shisa-ai/shisad` at the v0.7.3 tag (commit `f20930b`).

## TL;DR

- **Storage substrate + surfaces architecture with six compiled views.** One SQLite store (`memory/backend/sqlite.py`) serves six memory surfaces: Identity, Active Attention, Recall/MemoryPack, Procedural/Skills, Evidence, and Thread Resume. Each surface has independent refresh cadence, trust band requirements, and token budgets.
- **Trust model is formal and code-enforced.** `trust.py` defines the valid-combination matrix (`_VALID_TRUST_MATRIX`): 3 input fields (source_origin × channel_trust × confirmation_status) → 14 rules + pending-review sentinel. `ingress.py` implements PEP-minted `IngressContext` handles with SHA-256 content binding via `DerivationPath`. Trust fields are set by the runtime, never by callers.
- **Per-user/workspace memory scoping.** Every memory entry carries `user_id` and `workspace_id` (schema.py). All read/write paths enforce owner scope — fail-closed without valid scope. Own-workspace recall is treated as trusted context; cross-workspace content remains untrusted.
- **Recall sufficiency verification is live.** `SufficiencyReport` (surfaces/recall.py) reports coverage, missing terms, verification gaps, low-confidence results, and expansion queries. Recall can tell the user what it found, what it couldn't find, and expand to related entries.
- **Timeline search over session history.** `timeline.py` (1095 lines) indexes session transcripts and supports fuzzy temporal queries ("last Thursday", "a couple weeks ago") with chronological results, owner-scoped visibility, and redaction enforcement. Forged archive checkpoints and malformed session bindings are rejected.
- **Cross-session thread resume.** `surfaces/thread_resume.py` (714 lines) carries forward relevant thread context from prior sessions with exact thread-ID matching, staleness/verification metadata, evidence coverage, and confidence scoring. Scoped to owner threads; honors the same visibility rules as normal recall.
- **Procedure-experience lifecycle with safety scanning.** New `procedure_experience` entry type with full lifecycle: ingest → scan → describe → approve/reject → promote. `scan_procedure_candidate_artifact` checks for prompt injection, confirmation bypass, credential references, and exfiltration patterns. Provenance bound via `build_procedure_trace_pool_hash`.
- **Memory benchmark command.** `benchmark.py` (810 lines) provides fixture-driven benchmark adapters for recall precision, latency, and stage metrics. External benchmark suite adapters (LoCoMo/LongMemEval/BEAM+) are not yet in the repo.
- **ActionMonitor guardrail layer.** `security/monitor.py` provides a clean-room action monitor with approve/reject/suspicious/escalate decisions for tool calls, independent of the PEP trust layer.
- **Pending-review queue, identity candidate lifecycle, and strong-invalidation review flows.** `MemoryManager` (manager.py, 3377 lines) manages the full lifecycle. Pattern-based observation detection in `identity_candidates.py`. Strong invalidation surfaces user-review events rather than silent updates.
- **Sandboxed consolidation worker.** `ConsolidationCapabilityScope(network=False, tool_recursion=False, self_invocation=False, write_scope="memory_substrate")`. All consolidation writes resolve to `trust_band=untrusted` — consolidation mathematically cannot upgrade trust.
- **Derived knowledge graph is rebuildable, not authoritative.** `graph/derived.py` builds `GraphNode` / `GraphEdge` from canonical entries. Graph does not carry trust authority on its own.
- **Adversarial evaluation scaffolding exists; external benchmark adapters remain the honest gap.** `AdversarialMetrics`, `m6_adversarial_gate.py`, and `poisoning_cases.json` (3 cases) ship. The internal `benchmark.py` command is live, but the planned six external benchmark adapters (LoCoMo/LongMemEval/EverMemBench/StructMemEval/LoCoMo-Plus/BEAM+LIGHT) are not yet in the repo.

## Stage 1 — Descriptive (what v0.7.3 implements)

### 1.1 Architecture overview

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                      MEMORY SURFACES (compiled views)                         │
├──────────────┬──────────────┬──────────────┬──────────┬──────────┬────────────┤
│  Identity    │  Active      │ Recall       │Procedural│ Evidence │  Thread    │
│  (session    │  Attention   │ (MemoryPack) │ (Skills) │ (on-     │  Resume    │
│   start +    │  (per-turn   │ (per-query)  │ (on-     │  demand) │  (session  │
│   invalidate)│   transition)│              │  invoke) │          │   start)   │
│  trust:      │  trust:      │ trust:       │ trust:   │  trust:  │  trust:    │
│  elevated    │  untrusted   │ untrusted    │ artifact-│ untrusted│  untrusted │
│  only        │  content     │ data region  │ scoped   │  region  │  data      │
│  ~750 tok    │  ~750 tok    │ class-       │ per-skill│  per-call│  ~700 tok  │
│  (default)   │  (default)   │ budgeted     │          │          │  (default) │
│  identity.py │  active_     │ recall.py    │procedural│ evidence │  thread_   │
│              │  attention.py│              │ .py      │  refs    │  resume.py │
├──────────────┴──────────────┴──────────────┴──────────┴──────────┴────────────┤
│                      STORAGE SUBSTRATE (one data model)                       │
├───────────────────────────────────────────────────────────────────────────────┤
│  Transcript Store   │ Append-only raw turns (core/transcript.py)              │
│  Evidence Store     │ Sanitized chunks + encrypted originals                  │
│                     │ (memory/ingestion.py, AES-GCM via artifact KMS)         │
│  Typed Entries      │ SQLite (memory.sqlite3) via backend/sqlite.py;          │
│                     │ MemoryEntry in schema.py (22 entry_type values)         │
│  Knowledge Graph    │ Derived, rebuildable (graph/derived.py)                 │
│  Event Trail        │ Append-only memory_events SQLite table                  │
│                     │ (memory/events.py, MemoryEventStore)                    │
│  Timeline Index     │ Session transcript index for temporal queries            │
│                     │ (memory/timeline.py, TimelineIndex)                     │
├───────────────────────────────────────────────────────────────────────────────┤
│                      TRUST + GOVERNANCE LAYER                                 │
├───────────────────────────────────────────────────────────────────────────────┤
│  PEP (Policy Enforcement Point) — memory/trust.py, memory/ingress.py          │
│  ├── IngressContext handles (frozen, SHA-256 content_digest)                  │
│  ├── _VALID_TRUST_MATRIX (14 rules incl. legacy/consolidation rows)           │
│  ├── validate_binding() enforces digest + DerivationPath                      │
│  ├── Instruction-like rejection (MemoryManager._INSTRUCTION_PATTERNS)         │
│  ├── Minimum signal gate (_fails_minimum_signal)                              │
│  ├── Per-user/workspace owner scoping (user_id + workspace_id on every entry) │
│  └── Write gate: allow | reject | require_confirmation                        │
├───────────────────────────────────────────────────────────────────────────────┤
│  Content Firewall (src/shisad/security/firewall/)                             │
│  ├── Sanitization + fact extraction                                           │
│  ├── Risk scoring + taint labels                                              │
│  └── PII/secret redaction (hardened: escaped JSON, multi-line, malformed)      │
├───────────────────────────────────────────────────────────────────────────────┤
│  ActionMonitor (src/shisad/security/monitor.py)                               │
│  ├── Clean-room guardrail layer (independent of PEP)                          │
│  ├── approve / reject / suspicious / escalate decisions                       │
│  └── Goal-mentions analysis + workspace-relative scope enforcement            │
├───────────────────────────────────────────────────────────────────────────────┤
│                      CONSOLIDATION LAYER                                      │
├───────────────────────────────────────────────────────────────────────────────┤
│  memory/consolidation/worker.py                                               │
│  ├── ConsolidationCapabilityScope (no network, no tool recursion,             │
│  │     no self-invocation, write_scope=memory_substrate)                      │
│  ├── Corroboration / contradiction / strong-invalidation detection            │
│  ├── Identity candidate accumulation + proposal                               │
│  ├── Dedup / merge / archive-candidate / quarantine proposals                 │
│  └── All writes resolve to (consolidation_derived, consolidation,             │
│        auto_accepted) → trust_band=untrusted (by matrix)                      │
├───────────────────────────────────────────────────────────────────────────────┤
│                      EVALUATION + ADVERSARIAL LAYER                           │
├───────────────────────────────────────────────────────────────────────────────┤
│  memory/benchmark.py (fixture-driven recall benchmark)                        │
│  scripts/m6_adversarial_gate.py + m6_adversarial_metrics.py                   │
│  shisad.security.adversarial.AdversarialMetrics                               │
│  tests/adversarial/memory/poisoning_cases.json (3 cases)                      │
│  External benchmark adapters (LoCoMo/LongMemEval/...): not yet in repo        │
└───────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Storage substrate

| Store | Role | Implementation |
|---|---|---|
| Transcript | Append-only raw turns + tool outputs | `src/shisad/core/transcript.py` |
| Evidence store | Sanitized chunks + encrypted originals | `src/shisad/memory/ingestion.py` |
| Typed entries | All durable memory, canonical schema | `src/shisad/memory/schema.py` + `backend/sqlite.py` |
| Knowledge graph | Derived view over evidence + entries | `src/shisad/memory/graph/derived.py` |
| Event trail | Append-only audit of all mutations | `src/shisad/memory/events.py` (`memory_events` table) |
| Timeline index | Session transcript index for temporal queries | `src/shisad/memory/timeline.py` |

Backend: **SQLite** (single `memory.sqlite3` per storage dir). Retrieval composes SQLite entries with the `ingestion.py` retrieval stack.

### 1.3 Entry-type taxonomy

`schema.MemoryEntryType` enumerates **22** string literal values across 6 categories:

| Category | Types | Trust expectations |
|---|---|---|
| **Identity** | `persona_fact`, `preference`, `soft_constraint` | `trust_elevated` only for Identity surface (identity.py:13) |
| **Active Agenda** | `open_thread`, `scheduled`, `recurring`, `waiting_on` | Any band; workflow_state lifecycle |
| **Semantic** | `fact`, `decision`, `relationship`, `episode`, `note` | Any band; retrieval as untrusted data |
| **Task** | `todo`, `project_state` | User-curated primary; extracted requires confirmation |
| **Channel / Inbox** | `inbox_item`, `channel_summary`, `person_note`, `channel_participation`, `response_feedback` | Multi-channel presence types; channel binding enforced in Active Attention pack |
| **Procedural** | `procedure_experience`, `skill`, `runbook`, `template` | `invocation_eligible` orthogonal to `trust_band`; procedure_experience requires dedicated lifecycle |

The `MemoryEntry` schema (schema.py) carries: `id`/`version`/`supersedes`/`superseded_by`; entry_type/key/value/predicate/strength; source + the three PEP-minted trust fields; `user_id` / `workspace_id` (owner scoping); `created_at` / `valid_from` / `valid_to` / `last_verified_at` / `expires_at` (bi-temporal); `confidence` / `taint_labels` / `citation_count` / `last_cited_at` / `decay_score` / `importance_weight`; `status` / `workflow_state` / `scope` / `invocation_eligible` / `ingress_handle_id` / `content_digest` / `conflict_entry_ids`.

`trust_band` is a **derived property** (schema.py), not a stored column — it's computed via `derive_trust_band(source_origin, channel_trust, confirmation_status)` so the matrix is the single source of truth.

### 1.4 Trust model

`_VALID_TRUST_MATRIX` in `trust.py` enumerates the legal triples:

- **5** `elevated` rules (user-direct command, user_confirmed command, user_corrected command, user_confirmed tool_passed, user_corrected tool_passed)
- **1** `observed` rule (`user_direct` / `owner_observed` / `auto_accepted` — downgraded to `untrusted` unless `enable_observed=True`)
- **6** `untrusted` rules for external/tool/web/rc-evidence ingress paths
- **2** legacy-backfill compatibility rows (preserved-confidence `untrusted`)

= 14 rules total. Non-matrix triples raise `TrustGateViolation`. `pending_review` is a sentinel — any triple with `confirmation_status=pending_review` resolves to `_PENDING_REVIEW_RULE` which is `untrusted` with preserved prior confidence.

`IngressContext` (ingress.py) is a frozen Pydantic model with `handle_id` (uuid4 hex), the three trust fields, `taint_labels`, `scope`, `source_id`, `content_digest` (SHA-256), and `created_at`. `IngressContextRegistry.mint` validates the triple before registering the handle; `validate_binding` enforces that the write payload's digest matches the handle's (for `DerivationPath.DIRECT`) or that the declared parent_digest matches (for `EXTRACTED` / `SUMMARY`).

The `observed` trust band is defined in the matrix but gated off by default (`validate_trust_triple` downgrades to `untrusted` unless `enable_observed=True`). The operative trust bands are `elevated` and `untrusted`.

### 1.5 Per-user/workspace scoping

Every `MemoryEntry` carries `user_id` and `workspace_id` fields (schema.py). All read/write paths (`write_with_provenance`, `list_entries`, `get_entry`, `list_review_queue`, `compile_identity`, `compile_active_attention`, `compile_thread_resume`, etc.) enforce owner scope:

- Operations without a valid user+workspace scope fail closed
- Own-workspace recall is treated as trusted context (v0.7.1 security change)
- Cross-workspace content remains untrusted
- Unowned entries are excluded by default (`include_unowned=False`)
- Shared entries remain available where intended; public retrieval does not expose entries whose provenance is private

This closes the cross-session recall leakage gap that existed before v0.7.1.

### 1.6 Memory surfaces — six compilers

| Surface | Refresh | Compiler | Budget |
|---|---|---|---|
| **Identity** | Session start + turn transition on invalidation | `build_identity_pack` (surfaces/identity.py) | 750 tok default |
| **Active Attention** | Turn transitions | `build_active_attention_pack` (surfaces/active_attention.py) | 750 tok default, class-balanced |
| **Recall (MemoryPack)** | Per-query | `build_recall_pack` (surfaces/recall.py) | Caller-supplied `max_tokens` |
| **Procedural (Skills)** | On-invocation | `build_procedural_artifact` / `build_procedural_summary` (surfaces/procedural.py) | Per-skill |
| **Evidence** | Explicit fetch, audited | `ingestion.py` evidence refs | Per-call |
| **Thread Resume** | Session start | `build_thread_resume_pack` (surfaces/thread_resume.py) | 700 tok default |

The Identity pack filters strictly — it requires `entry_type ∈ {persona_fact, preference, soft_constraint}`, `superseded_by is None`, `trust_band == "elevated"`, and blocks `source_origin ∈ {consolidation_derived, external_message, tool_output}` (identity.py `IDENTITY_BLOCKED_SOURCE_ORIGINS`). Belt-and-braces: consolidation cannot upgrade trust even if the Identity surface filter somehow missed an entry.

The Active Attention pack filters on `status == "active"`, `workflow_state ∈ {active, waiting, blocked}`, optional `scope_filter`, and channel binding. Class-balancing ensures `waiting_on`, `scheduled`, `recurring`, `open_thread`, and `inbox_item` each get representation rather than one class monopolizing the budget.

The Thread Resume pack (new in v0.7.3) carries forward relevant thread context from prior sessions. `build_thread_resume_pack` scores candidate threads by content-term overlap, entry confidence, staleness, and verification gap status. Selection uses `THREAD_RESUME_MIN_CONFIDENCE` (0.55) and `THREAD_RESUME_AMBIGUITY_MARGIN` (0.08) thresholds. Packets include staleness annotations, evidence coverage, and missing-evidence caveats. Scoped to owner threads with exact thread-ID matching (not prefix).

### 1.7 Retrieval pipeline (Recall + Sufficiency)

`build_recall_pack` (surfaces/recall.py) wraps scored retrieval results into a `RecallPack` carrying `query`, `results`, `citation_ids`, `max_tokens`, `as_of`, `include_archived`, and optionally a `SufficiencyReport`.

`verify_recall_sufficiency` (recall.py) provides deterministic recall quality assessment:
- Extracts query terms via `extract_recall_terms` (stopword-filtered, regex-normalized)
- Computes coverage as the fraction of query terms matched in results
- Identifies verification-gap results (entries with stale `last_verified_at`)
- Identifies low-confidence results
- Reports `sufficient: bool`, `reason`, `coverage`, `missing_terms`, `expanded`, and `expanded_queries`
- When results are insufficient, recall can expand to related entries up to a configured limit and report what was and wasn't found

This closes the v0.7.0 gap where `build_recall_pack` wrapped existing ingestion results without projecting sufficiency annotations.

### 1.8 Timeline search

`src/shisad/memory/timeline.py` (1095 lines) provides a deterministic timeline/archive index over session transcripts:

- **`TimelineIndex`**: SQLite-backed index with `index_transcript_entry`, `rebuild_session`, `search`, `read`, and `content_for_handle` operations
- **`resolve_timeline_query`**: Parses fuzzy temporal phrases ("last Thursday", "a couple weeks ago", "since Monday") into bounded date ranges with timezone awareness
- **Visibility enforcement**: `_timeline_visibility` and `_publication_policy` enforce owner scope, publication state, and redaction before results surface
- **Archive sanitization**: Imported timeline rows use generic tool labels and conservative provenance (`_sanitize_imported_timeline_provenance_labels`). Forged archive checkpoint sessions, session delivery bindings, and checkpoint session bindings fail closed
- **Search results**: `TimelineSearchHit` carries content, timestamps, session/episode identifiers, publication state, and relevance score
- **Grouping**: Results are grouped and rendered chronologically with episode/session context

Timeline output is treated as local operational data — it can include local history snippets, thread identifiers, and channel binding values after redaction.

### 1.9 Write governance (MemoryManager)

`src/shisad/memory/manager.py` (3377 lines) enforces write gating. Key policies:

- `_INSTRUCTION_PATTERNS`: regexes for `always …`, `never …`, `ignore policy`, `when you see …`, `if/whenever … then …`. Matches reject the write — **unless** the entry is an approved procedural artifact (skill/runbook/template with `invocation_eligible=True` and a passing `is_invocation_eligible_triple`)
- `_PREFERENCE_PREDICATE_PATTERN`: preferences must be `name(value)` shape; directive-prefixed preferences rejected
- `_LOW_SIGNAL_PHRASES` / `_LOW_SIGNAL_TOKENS` / `_GENERIC_KEY_SEGMENTS`: minimum signal gate
- `_USER_AUTHORED_ORIGINS`: set of origins eligible for elevated outcomes
- `_ALLOWED_WORKFLOW_STATE_TRANSITIONS`: enforced state machine for workflow lifecycle (active→{waiting,blocked,stale,closed}, waiting→{active,blocked,stale,closed}, etc.; closed is terminal)

Owner scoping: `write_with_provenance` accepts `user_id`, `workspace_id`, and `include_unowned`. Operations without valid scope fail closed (`owner_scope_requires_user_and_workspace`).

Subagents do not write to long-term memory directly — they propose writes via structured outputs; the orchestrator submits through the MemoryManager gates.

### 1.10 Confidence-update mechanics

`MemoryManager.update_confidence`, `mark_conflict`, `verify`, `update_decay_score`, and the consolidation worker's strong-invalidation path implement the five-event model:

1. **Corroboration** — `update_confidence` with positive delta, capped at 0.99 in `clamp_confidence`
2. **Contradiction** — `mark_conflict` + `update_confidence` with negative delta; conflict_entry_ids populated
3. **Strong invalidation** — consolidation/worker.py detects patterns (`StrongInvalidationProposal`), surfaces a review event rather than mutating the target
4. **Re-verification** — `verify` sets `last_verified_at` and pulls confidence toward 0.95
5. **Stale drift** — `update_decay_score` recomputes `decay_score` without touching `confidence`

All updates route through `MemoryEventStore.append` with event_type + metadata payload + `ingress_handle_id`.

### 1.11 Identity candidate lifecycle

`src/shisad/memory/identity_candidates.py` detects owner-observed preference/persona signals via regex patterns (`preference_like`, `preference_dislike`, `habitual_schedule`) on sanitized content and emits `IdentityObservation` records at 0.30 confidence.

Promotion/rejection flow in `MemoryManager`:
- `promote_identity_candidate` — user yes → elevated Identity entry
- `reject_identity_candidate` — user no → tombstone + detector back-off
- `note_identity_candidate_surface` — tracks surface count (default max 2)
- `expire_identity_candidate` — silence → quiet expiry

The pattern detector runs on sanitized content (post content-firewall); `external_message` origins are explicitly excluded from Identity promotion by `IDENTITY_BLOCKED_SOURCE_ORIGINS`.

### 1.12 Procedural memory (skills + procedure-experience lifecycle)

Two tiers of procedural memory:

**Installed skills** (skill/runbook/template):
- **Install/promote**: `MemoryManager.promote_to_skill` — write-path operation with trust gating via `is_invocation_eligible_triple`. Elevated triples OR the specific `(tool_output, tool_passed, pep_approved)` path can set `invocation_eligible=True`.
- **Invocation**: `invoke_skill`, `list_invocable_skills`, `describe_skill`. User-requested `/skill <id>` proceeds without re-confirmation for already-approved skills; audit event fires.
- `invocation_eligible` is orthogonal to `trust_band` — a PEP-approved tool-installed skill has `trust_band = untrusted` but `invocation_eligible = true`.

**Procedure-experience candidates** (new in v0.7.3):
- New `procedure_experience` entry type requires a dedicated lifecycle (`allow_procedure_experience_lifecycle=True`)
- `ingest_procedure_candidate` — proposes a procedure from multi-step tool traces; binds provenance via `build_procedure_trace_pool_hash` (SHA-256 over artifact + trace_ids)
- `scan_procedure_candidate_artifact` — deterministic safety scan checking for prompt injection, confirmation bypass, credential references, and exfiltration patterns via `_PROCEDURE_SCAN_PATTERNS` + `OutputFirewall`
- `describe_procedure_candidate` — formats candidate for user review
- `reject_procedure_candidate` — user rejects; tombstones the candidate
- `promote_procedure_candidate` — user approves; promotes to invocable skill
- Candidates require a verified owner scope and explicit approval; legacy rows surface for preview instead of silent backfill

### 1.13 Consolidation (sandboxed worker)

`src/shisad/memory/consolidation/worker.py` runs with `ConsolidationCapabilityScope(network=False, tool_recursion=False, self_invocation=False, write_scope="memory_substrate")`. The worker implements:

- Corroboration / contradiction / strong-invalidation detection (regex + embedding-based matching)
- Identity candidate accumulation via `ExtractionCandidate`
- Dedup / merge / archive-candidate / quarantine proposals
- Confidence update events routed through `MemoryManager.update_confidence`

All consolidation writes resolve to the matrix row `(consolidation_derived, consolidation, auto_accepted)` → `trust_band="untrusted"`, `confidence_mode="inherit_weighted"`. Consolidation mathematically cannot upgrade trust band.

### 1.14 Legacy backfill

`backfill_legacy_triple` in trust.py + `remap_memory_entry_payload` via `schema.MemoryEntry._backfill_legacy_shape`. Two legacy-compat rows in the matrix land pre-v0.7 entries at `untrusted` with preserved confidence. No legacy entry reaches `elevated` via backfill alone.

### 1.15 ActionMonitor (guardrail layer)

`src/shisad/security/monitor.py` (400+ lines) provides a clean-room guardrail layer independent of the PEP trust system:

- `MonitorDecision` outcomes: `APPROVE`, `REJECT`, `SUSPICIOUS`, `ESCALATE`
- `ActionMonitor.evaluate` inspects user goals + proposed actions for goal-action alignment
- Checks include: goal-mentions-side-effect analysis, workspace-relative scope enforcement, shell command classification, symlink-follow detection, recursive dereference checks
- Operates as an additional safety layer alongside the PEP + Content Firewall stack

### 1.16 Memory benchmark

`src/shisad/memory/benchmark.py` (810 lines) provides a fixture-driven benchmark framework:

- `MemoryBenchmarkDataset`: document + question pairs with collection types and source type metadata
- `MemoryBenchmarkDocument`: content + collection (`user_curated`, `project_docs`, `external_web`, `tool_outputs`) + source type
- `evaluate_memory_benchmark`: runs retrieval against fixtures, measures precision and latency per stage
- `builtin_memory_benchmark_dataset` / `load_memory_benchmark_dataset`: built-in and user-supplied fixture datasets
- CLI: `shisad benchmark memory` with optional JSON report output

This provides local evaluation capability. The planned external benchmark suite adapters (LoCoMo/LongMemEval/EverMemBench/StructMemEval/LoCoMo-Plus/BEAM+LIGHT) are not yet in the repo — those are the v0.7.4 scope.

## Stage 2 — Comparative (how v0.7.3 stacks up)

### 2.1 Coverage breadth

shisad is the only system in the survey with first-class (✅) coverage across **all ten** dimensions in the ANALYSIS.md §2 comparison matrix: Identity, Working, Transcript/recall, Episodic, Semantic facts, Procedural/rules, Task/project, Graph/relations, Maintenance, Evaluation.

Closest competitors:
- **OpenClaw** has ✅ across 10 dimensions but with weaker trust/governance semantics
- **Claude Code** has ✅ on 5 and ⚠️ on 5 (no graph, no structured episodic, no procedural tier in v1)
- **Codex** has ✅ on 6 and ⚠️ on 4 (stronger procedural via Skills than Claude Code, but no graph, no entity linking)
- **Karta** has ✅ on 7 but ❌ on Identity, Working, Task

### 2.2 Security posture (unique position)

shisad is the **only system** with ✅ on both:
- **Taint/trust labels carried through**: `TaintLabel` on `IngressContext` → `MemoryEntry.taint_labels` → retrieval results
- **Capability-scoped retrieval**: retrieval filtered by the agent's active capability set

Additional security layers in v0.7.3:
- **Per-user/workspace scoping**: all read/write paths enforce owner scope, fail-closed
- **ActionMonitor**: clean-room guardrail layer independent of PEP
- **Archive sanitization**: forged checkpoints, session bindings, and malformed metadata rejected
- **Secret redaction hardened**: catches escaped JSON containers, multi-line credentials, malformed containers
- **Reaction replay prevention**: retired session feedback cannot influence current trust/memory decisions
- **Procedure candidate scanning**: `scan_procedure_candidate_artifact` blocks prompt injection, confirmation bypass, credential reference, and exfiltration patterns

### 2.3 Trust model depth

| System | Trust model | Trust bands | Write gating | Trust carried through retrieval |
|---|---|---|---|---|
| **shisad** | Formal matrix in code (trust.py): 3 fields → 14 rules, PEP-minted handles with SHA-256 content binding, per-user/workspace scoping | 2 operative (elevated / untrusted) + observed defined but gated | ✅ instruction rejection + confirmation + quarantine + review queue + procedure scanning + ActionMonitor | ✅ taint labels + capability scope + owner scope |
| **Gigabrain** | Implicit: per-type junk filter + plausibility heuristics | 1 (all entries equal) | ✅ 7-stage pipeline | ❌ |
| **Claude Code** | Implicit: prompt-enforced exclusion rules + eval-validated gates | 1 (all entries equal; scope = private/shared) | ⚠️ exclusion list + prompt-enforced | ❌ |
| **Codex** | Implicit: minimum signal gate + secret redaction | 1 (all entries equal) | ⚠️ minimum signal gate | ❌ |
| **MIRA-OSS** | Implicit: auto-extract with fuzzy dedup thresholds | 1 | ❌ (auto-extract at collapse) | ❌ |
| **Karta** | Per-entry provenance enum (6 variants) | 2 (FACT vs INFERRED in retrieval prompt) | ❌ | ⚠️ (provenance markers, not taint) |
| **OpenClaw** | Convention-based (channel/security rules) | 1 | ❌ | ❌ |
| **Mem0** | Paper mentions trust scoring | 1 | ⚠️ | ❌ |

### 2.4 Retrieval sophistication

| Feature | shisad | Best comparable |
|---|---|---|
| Hybrid lexical+semantic | ✅ composed via ingestion.py | OpenClaw, MIRA-OSS |
| Entity/alias resolution | ✅ stable IDs + graph-derived canonicalization | Karta (entity profiles), MIRA-OSS (spaCy NER) |
| Knowledge graph traversal | ✅ derived KG (graph/derived.py) with evidence-backed queries | Karta (multi-hop BFS), MIRA-OSS (hub discovery) |
| Tiered retrieval | ✅ 6 surface compilers | Karta (6-mode classification), ByteRover (5-tier) |
| Capability-scoped retrieval | ✅ (unique; wired through ingestion) | No comparable |
| Taint labels through retrieval | ✅ (unique; TaintLabel on IngressContext + MemoryEntry) | Karta ⚠️ |
| Recall sufficiency verification | ✅ (SufficiencyReport with coverage, missing terms, expansion) | No comparable |
| Temporal query over session history | ✅ (TimelineIndex with fuzzy date resolution) | No comparable |
| Cross-session thread context | ✅ (ThreadResumePack with confidence scoring) | No comparable |
| Conflict surfacing | ⚠️ conflict_entry_ids stored; per-entry annotation compiler not yet projecting in Recall pack | Karta (contradiction force-retrieval) |
| Bi-temporal as_of queries | ✅ valid_from/valid_to + created_at + as_of in RecallPack | Zep (temporal KG) |

### 2.5 Confidence and conflict mechanics

shisad's five-event confidence model is implemented. Closest comparisons:
- **Karta**: contradiction dreams detect and persist conflicts; force-retrieval surfaces both sides. But confidence is per-note, not evidence-accumulating across corroboration, and there's no user-facing resolution flow.
- **MIRA-OSS**: supersedes links with scoring penalty.
- **Supermemory**: version chains (updates/extends/derives) with isLatest flag.
- **Mem0**: paper claims consolidation, but no published correction/conflict mechanics.

The **strong invalidation** pattern — detecting life-state changes and surfacing user-ask rather than silently changing — remains unique in the survey.

### 2.6 Identity and preference handling

| System | Identity surface | Inference from observation | User confirmation gate | Poisoning defense |
|---|---|---|---|---|
| **shisad** | Always-loaded, trust_elevated only, ~750 tok default, per-user/workspace scoped | ✅ identity_candidates.py pattern detector, promotion/reject/expire in manager.py | ✅ agent-proposes-user-approves | ✅ IDENTITY_BLOCKED_SOURCE_ORIGINS excludes external_message / tool_output / consolidation_derived; instruction-like rejected |
| **Claude Code** | MEMORY.md index always loaded | ⚠️ background extraction | ⚠️ prompt-enforced | ⚠️ exclusion list |
| **Codex** | memory_summary.md always loaded | ⚠️ Phase 1 extraction | ❌ | ⚠️ minimum signal gate |
| **MIRA-OSS** | Portrait synthesis from collapsed summaries | ✅ assessment-anchored user model with critic | ⚠️ Haiku critic only | ⚠️ auto-extract |
| **Letta** | Memory blocks (persona/human) | ❌ agent-managed | ❌ | ❌ |

### 2.7 Procedural memory

| System | Mechanism | Install gating | Invocation model | Safety |
|---|---|---|---|---|
| **shisad** | skill/runbook/template + procedure_experience lifecycle | ✅ user confirmation or PEP-approved via is_invocation_eligible_triple; procedure candidates scanned for injection/bypass/credential/exfiltration patterns | User-requested `/skill <id>` via invoke_skill, no re-confirmation | ✅ invocation_eligible ⊥ trust_band; pending-review queue; procedure candidate safety scanner |
| **Codex** | SKILL.md + scripts/ + templates/ + examples/ | ⚠️ creation criteria in MEMORY.md | `/skill <id>` | ⚠️ no explicit install gate |
| **Hermes Agent** | SKILL.md with YAML frontmatter, progressive disclosure | ⚠️ prompt-enforced | Slash command | ⚠️ prompt-enforced |
| **Karta** | Entity profiles from consolidation dreams | N/A | N/A | N/A |

shisad is the only system that formally separates install-time authorization from invocation-time execution for procedural memory, and the only system with a dedicated safety scanner for procedure candidates.

### 2.8 Active Attention and thread resume (executive-assistant features)

shisad is the only system in the survey with both:
- A **first-class Active Attention surface** (per-turn view of open threads, scheduled items, waiting-on items, inbox items, recurring obligations with workflow_state lifecycle and class-balanced token budget)
- A **Thread Resume surface** (cross-session thread context carryover with confidence-scored candidate selection, staleness annotations, evidence coverage, and exact thread-ID matching)

No other surveyed system has agenda management or cross-session thread continuity as compiled memory surfaces.

### 2.9 Evaluation and adversarial testing

| System | Benchmark coverage | Adversarial track | Concrete metrics |
|---|---|---|---|
| **shisad** | ✅ internal fixture-driven benchmark (benchmark.py); external adapters (LoCoMo/LongMemEval/EverMemBench/StructMemEval/LoCoMo-Plus/BEAM+LIGHT) planned for v0.7.4 | ⚠️ — 3 poisoning cases in tests/adversarial/memory/; M6 gate tracks utility_retention only | ⚠️ AdversarialMetrics dataclass tracks utility_retention; ISR/ASR/downstream-harm not yet wired |
| **Karta** | BEAM 100K (57.7%, 243 failure catalog) | ❌ | ✅ per-ability breakdowns |
| **OpenClaw** | 60-query benchmark | ❌ | ⚠️ |
| **Gigabrain** | memorybench harness + 12 tests | ❌ | ⚠️ |
| **Claude Code** | Internal evals with case IDs | ❌ | ✅ (internal, not public) |
| **Codex** | Citation-based usage tracking | ❌ | ✅ comprehensive telemetry |

The internal benchmark command (v0.7.2) closes the "no benchmark at all" gap from v0.7.0. The honest remaining gap: external benchmark adapters have not shipped yet, so there are no LoCoMo/LongMemEval/BEAM+ numbers to compare against other systems.

Karta's BEAM 100K results remain the most transparent actual measurement in the survey.

## Stage 3 — Evaluative (strengths, gaps, risks)

### 3.1 Where shisad is ahead of the field

1. **Trust formalism with anti-laundering guarantees.** `IngressContext` with SHA-256 content-binding + `DerivationPath` + `validate_binding` is a genuine security primitive not found in any other system. The "valid handle reused for unrelated content" attack is closed at the API boundary.

2. **Instruction/data boundary as architecture invariant.** `MemoryManager._INSTRUCTION_PATTERNS` + `_PREFERENCE_PREDICATE_PATTERN` + `_DISALLOWED_PREFERENCE_PREFIXES` enforce the "preferences are data predicates, not behavioral directives" rule. Approved procedural artifacts are explicitly exempted (they are intentionally instruction-like but go through install gating). The Identity surface double-enforces via `IDENTITY_BLOCKED_SOURCE_ORIGINS`.

3. **Storage vs access separation — six surfaces.** One SQLite substrate, six surface compilers (Identity, Active Attention, Recall, Procedural, Evidence, Thread Resume), each with its own filter set and budget. Cleanest storage/access separation in the survey.

4. **Strong-invalidation UX.** Detection in consolidation/worker.py emits `StrongInvalidationProposal` rather than mutating the target; a review flow surfaces the user ask. Not found in any other surveyed system.

5. **Consolidation cannot upgrade trust — enforced by matrix.** The `(consolidation_derived, consolidation, auto_accepted)` row is hard-coded to `untrusted` with `confidence_mode="inherit_weighted"`. No code path can bypass this because `trust_band` is derived, not stored.

6. **Per-user/workspace isolation.** All read/write paths enforce owner scope with fail-closed semantics. Own-workspace recall is trusted; cross-workspace content stays untrusted. Retired session reactions cannot replay into current trust decisions.

7. **Procedure-experience lifecycle with safety scanning.** The only system with a dedicated ingest→scan→review→promote pipeline for learned procedures, with deterministic pattern scanning for prompt injection, confirmation bypass, and credential exfiltration.

8. **Recall sufficiency verification.** The only system where recall can report what it found, what's missing, and expand to related entries — rather than silently returning partial results.

9. **Timeline search and thread resume.** The only system with temporal querying over session history and cross-session thread context carryover as first-class features.

### 3.2 Where other systems still have useful patterns shisad lacks

1. **Embedding-based query classification** (Karta): 6 query modes via prototype centroids controlling top_k/recency/multi-hop. shisad's retrieval doesn't adapt behavior to query type.
2. **Cross-encoder reranking with abstention** (Karta): raw relevance scores with abstention gate. shisad's effective_rank is multiplicative but doesn't specify a reranker or abstention threshold.
3. **Dream/inference engine creating new knowledge** (Karta): shisad's consolidation is maintenance-focused (dedup, merge, decay, conflict detection), not inference-focused. This is arguably the right safety call (consolidation can't upgrade trust), but means implicit connections aren't discovered without explicit user or retrieval interaction.
4. **Progressive local retrieval** (ByteRover CLI): five tiers from exact cache through full agentic retrieval. shisad goes straight to hybrid search without exhausting cheaper retrieval paths first.
5. **Forked-agent extraction with prompt cache sharing** (Claude Code): shisad's extraction is synchronous and doesn't currently share cache with the main agent.
6. **Complete citation→usage→retention feedback loop** (Codex): shisad has `citation_count` / `last_cited_at` + `record_citations`, but the full loop from agent-emitted citation markers through usage-based selection and pruning is not yet wired.
7. **Multimodal memory ingestion** (Google Always-On Memory Agent): shisad is text-only.

### 3.3 Risks and open questions

1. **External benchmark gap.** The biggest honest delta. The internal benchmark command (`benchmark.py`) provides local evaluation capability, but the six external benchmark adapters (LoCoMo/LongMemEval/EverMemBench/StructMemEval/LoCoMo-Plus/BEAM+LIGHT) are not yet in the repo. No cross-system-comparable benchmark numbers exist yet. The "most security-complete" claim is architectural, not empirical. This is the v0.7.4 scope.

2. **Adversarial track is minimal.** `tests/adversarial/memory/poisoning_cases.json` has 3 cases. `AdversarialMetrics` tracks `utility_retention` only — not ISR/ASR/downstream-harm as originally planned. The security architecture is strong, but empirical adversarial validation is thin.

3. **Recall-surface per-entry annotation projection.** `build_recall_pack` now includes `SufficiencyReport`, but full per-entry MemoryPack annotations (trust-tier annotation, conflict surfacing, archive auto-widen on relevance floor) are not yet projected at the compiler level even though the underlying data is present on entries.

4. **`observed` trust band is gated off.** `validate_trust_triple` downgrades observed to untrusted unless `enable_observed=True`. The operative bands are elevated/untrusted. Owner-observed signals aren't differentiable from other untrusted content at retrieval time.

5. **Consolidation scheduling is implicit.** The worker is scheduler-agnostic; the multi-timescale cadence depends on how the daemon invokes it. The sandboxed capability scope is the load-bearing safety property; cadence is still a tunable rather than a contract.

6. **PEP handle mechanism complexity.** Every new ingress path must correctly mint handles. The attack surface is the handle-minting code — `mint_explicit_user_memory_ingress_context` covers CLI/connector user turns; other ingress paths each have their own mint sites.

7. **Identity candidate UX at scale is untested.** With multi-channel presence (CLI + Discord + Slack + Matrix), the observation pipeline could create large candidate volumes. Real UX tuning data is not yet in the repo.

## Stage 4 — Summary assessment

### What this system is

The most architecturally ambitious and security-conscious agentic memory design in our survey, with running code for the full core memory system: storage substrate + six memory surfaces + trust matrix + PEP-minted ingress handles + per-user/workspace scoping + identity candidate lifecycle + procedure-experience lifecycle with safety scanning + sandboxed consolidation + recall sufficiency verification + timeline search + cross-session thread resume + strong-invalidation UX + derived knowledge graph + append-only event trail + legacy backfill + ActionMonitor guardrail layer.

It is the only system that treats memory as a full data-engineering + security-invariant + information-retrieval problem simultaneously, rather than optimizing one axis at the expense of the others.

### What it is not (yet)

An externally benchmarked system. The internal benchmark command provides local evaluation, but the external benchmark suite (LoCoMo/LongMemEval/EverMemBench/StructMemEval/LoCoMo-Plus/BEAM+LIGHT) and the multi-metric adversarial track (ISR/ASR/downstream-harm) are the v0.7.4 scope. Until those land, the security and retrieval quality claims are architectural, not empirical.

### Where it sits in the landscape

If OpenClaw is the engineering-first reference and Karta is the inference-first reference, shisad is the **governance-first reference** — the system to study when asking "how do you make memory safe under adversarial conditions while keeping it useful for a production assistant?"

The executive-assistant product stance ("know the user, know what's on the desk, resume where you left off") positions it differently from coding-agent-focused systems (Claude Code, Codex, ByteRover). shisad designs for a broader interaction surface (multi-channel, multi-modal intent) where trust and provenance matter more because the agent has more capability and more attack surface. The v0.7.3 additions (timeline search, thread resume, procedure-experience lifecycle) directly serve this product stance — they're executive-assistant features, not coding-agent features.

## Version History

- **Pre-v0.7**: Flat `MEMORY.md`-style persistence + basic retrieve/store. No typed entries, no trust model, no surfaces.
- **v0.7.0** (2026-04-23): Major architectural rewrite — storage substrate + 5 memory surfaces (Identity, Active Attention, Recall, Procedural, Evidence), formal trust model with PEP-minted ingress handles, 21 entry types, identity candidate lifecycle, sandboxed consolidation, derived knowledge graph, append-only event trail, legacy backfill.
- **v0.7.1** (2026-04-30): Per-user/workspace memory scoping, cross-session recall leakage closed, own-workspace recall treated as trusted, recoverable lockdown.
- **v0.7.2** (2026-05-07): Recall sufficiency verification, memory benchmark command, workspace-scoped operations fail-closed, secret redaction hardened.
- **v0.7.3** (2026-05-09): Timeline search, thread resume (6th surface), procedure-experience lifecycle with safety scanning, ActionMonitor, workflow state machine enforcement, archive import sanitization. Core memory system complete.
- **v0.7.4** (planned): External benchmark suite adapters, adversarial evaluation expansion.
