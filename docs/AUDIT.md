# Audit notes

One entry per product. Written by reading each audit.json in full. The point is to capture what is surprising, different, or worth remembering — not to summarize what the product does. Stats and frequencies live in [`FIELD.md`](FIELD.md). Per-product audit data lives in [`research/output/by-product/`](../research/output/by-product/).

Reviewed in alphabetical order starting 2026-09-26.

---

## Synthesis

61 products audited. This is what the field actually looks like.

### The silent failure epidemic

The most consistent finding across the audit is that memory systems fail silently. LLM extraction failures that advance the cursor anyway (TencentDB, documented three times in their own issue tracker). Silent JSON truncation dropping entire conversation facts with no error (mem0). Zero-extraction running for weeks with no warning when env var names are wrong (TencentDB). Vestige's entire receipt/trace system — the core safety mechanism — dead in production because the module is never imported. OpenViking's memory scores query-independent at ~1e37 regardless of semantic relevance. SimpleMem's Tantivy keyword index built once and never refreshed, silently missing all memories added after the first batch. This is not edge case behavior. It is the median behavior of deployed memory systems under real conditions. A companion memory system that fails silently is worse than no memory system at all, because it gives the appearance of continuity while providing none.

### Static lore outperforms dynamic memory everywhere they coexist

Three independent platforms document this independently: Replika users work around broken memory by pasting context at session start. RisuAI users use author's note and backstory because SupaMemory is unreliable. SillyTavern's World Info outperforms Chat Vectorization. This is an empirical field observation, not a fundamental law — but it means any companion memory system must get static lore (persona, character definition, relationship baseline) correct and reliable before investing in dynamic recall. The current state of LLM retrieval makes dynamic memory unreliable enough that users route around it.

### The field was not built for companions

The 61 products audited are dominated by coding agents, RAG infrastructure, and general-purpose memory APIs. The products that come closest to companion-native architecture — mnemosyne, soul-of-waifu, paramecium, memory-constellations — are small personal projects with no funding. The ideas they contain don't appear in any of the mainstream products:

- **MEMORY.md / USER.md split** (soul-of-waifu): character psychology and user-facing facts stored as separate schemas with different purposes. No other product makes this distinction.
- **Quote-verification guard** (paramecium): extracted memories whose source quote cannot be found verbatim in the source batch are dropped before ingestion. Built specifically because their prior pipeline produced 36% paraphrase rather than verbatim content.
- **Echo lane retrieval** (paramecium): two-query retrieval using both the user's message and the assistant's previous reply as separate query vectors. Surfaces memories relevant to what was just said, not only to what was asked.
- **Reads-never-reinforce** (vestige): retrieval does not strengthen a memory. Only explicit positive outcome feedback does. This is correct — self-reinforcing retrieval makes highly-retrieved memories confidently wrong when circumstances change.
- **CONTRADICTS links force-included** (openviking): contradictory facts always reach LLM context regardless of PPR score. No other product ensures the model sees the contradiction.
- **Claims gate eliminating served-hallucination** (taosmd): async verification pass on extracted claims; unverified claims demoted at recall. Confirmed at zero accuracy cost across three judges.
- **Zero-loss archive as ground truth** (taosmd): all other memory layers are derived and rebuildable from the append-only archive. If the derived layer is wrong, you can rebuild it.
- **Circumplex affect model** (mnemosyne): emotional state tracked per memory. Decay tied to emotional processing, not just recency.
- **Anti-prompt-injection redaction** (mnemosyne): model output is scanned and redacted before it reaches the memory store. Only mnemosyne treats user input as an untrusted write-path attack surface.

### Retrieval quality is undersolved

Pure vector search fails on vocabulary gaps — a fact described in different words from how it was stored won't surface. The systems that measured this:

- taosmd's Librarian (LLM-assisted query expansion) gave +15.4% on long-horizon recall over vector+reranker alone, when the target fact shares no vocabulary with the query.
- taosmd's ablation: full-context stuffing (no retrieval) is 5.7× worse than retrieval on LoCoMo. Memory retrieval is not optional.
- SimpleMem's ablation: removing temporal normalization at write time drops F1 by 56.7% on temporal reasoning tasks. Resolving relative timestamps to absolute at write time matters enormously.
- taosmd's extraction-hallucination rate: ~1 in 5 LLM-extracted facts is partially or unsupported by its source text (18.8% PARTIAL+UNSUPPORTED over 526 claims, cross-family verified).

### Benchmark numbers are nearly incomparable

Different datasets, different judges, different evaluation configurations, almost all vendor self-reported. taosmd is the only system that published a correction — their 74.6% was inflated by a judge parser bug counting INCORRECT verdicts as passes, corrected to 42.8–51.2%. That correction exists only because they documented it. Every other vendor's benchmark numbers have no such audit trail.

### Companion-specific gaps the field hasn't addressed

- **Subject contracts**: whose memory is this about? reme doesn't have one and gets Alice-Bob cross-contamination. Almost no product recognizes this as a problem.
- **Relationship state**: not just facts but the relational quality between user and companion — trust, promises, milestones, shared history. Only soul-of-waifu (Soul Stage) and mnemosyne attempt this.
- **Emotional continuity**: what the companion felt about prior events. Only mnemosyne has an affect model.
- **Anti-prompt injection**: user input that modifies stored companion state as an attack surface. Only mnemosyne addresses this.
- **"Never admit no information found"** (mem0, replika pattern): scaffold instructions telling the model to fabricate rather than admit retrieval gaps. Actively harmful for companions — a companion that confabulates is worse than one that says it doesn't remember.
- **Non-English embedding support**: soul-of-waifu (Russian inverts similarity rankings), supermemory (non-English recall fails entirely), TencentDB (CJK returns 0 hits silently when embedding disabled). Most systems were built and tested on English only.

### What a companion memory system needs that doesn't exist anywhere

A complete companion memory system requires: a zero-loss raw archive, a curated fact layer with subject-attributed memories and write-time quote verification, typed relationships between facts including explicit contradiction tracking (and force-inclusion of contradictions in retrieval context), separate stores for character psychology vs. user-facing facts, retrieval that uses query expansion for vocabulary gaps and does not self-reinforce on retrieval alone, and emotional/relational state tracking with decay that reflects meaning rather than recency. None of the 61 products have all of these. Most have one or two. The closest single system to this description is a combination of taosmd's architecture (zero-loss archive, claims gate, Librarian expansion) with paramecium's write-path discipline (quote verification, echo lane) and mnemosyne's relational/affective model.

---

## acontext

Agent skill memory layer. Stores curated learnings as Markdown skill files, not raw transcripts.

**Notable:**
- No embeddings anywhere. Retrieval is purely agent-driven tool calls (`list_skills`, `get_skill`). The agent decides what to fetch — no distance function involved. Explicit architectural stance against semantic search.
- Write path triggers on task completion or failure only, not per message. Genuine curation gate rather than turn-by-turn accumulation.
- Failure memory is a distinct type. When a task fails, distillation writes a dedicated correction record: what should have been done + a prevention principle. No other audited product has an explicit failure-memory path.
- "Not worth" gate: if distillation returns None, nothing is written and the session is marked COMPLETED silently. Explicit value filter.
- Memory encrypted with a user KEK; hard-fails if absent rather than writing plaintext.

**Unknowns that matter:** Conflict/supersession is completely unspecified — 5 separate unknowns all asking the same question about what happens when new distilled facts contradict existing skills. Delegated to SKILL.md which is user-defined.

**Companion relevance:** Low. Built for developer agents, not relationships. No speak/silent policy, no relationship model, no cross-session continuity concept.

---

## aelios

Companion memory gateway on Cloudflare Workers. MCP server named `companion-memory-mcp`. Dual store: D1 (SQLite, canonical) + Vectorize (vector mirror).

**Notable:**
- Most layered memory architecture in the field. Distinguishes: raw message log (expires ~7 days), dream-extracted candidates (human review queue), committed long-term memory (180-day soft-expire, hard-deleted 30 days after), precious notes (pinned, append-only, exempt from decay), glossary (L5 literal, outside vector index), weekly impression blocks (temporal only), verbatim quote store (evidence queries only). Each layer has a separate retrieval path.
- Human-in-the-loop review gate between nightly extraction and long-term memory. Dream candidates surface in an audit queue; user approves, discards, merges, or supersedes before anything is committed. No other audited product makes this gate explicit and user-facing.
- `response_tendency` is a per-memory scaffold instruction — tells the model how to behave when that specific memory fires. That is a speak policy attached to the memory itself, not to the turn.
- Hand-authored memories (E-axis flag) are protected from automated pipeline overwrites. Automated candidates that conflict with a hand-authored entry require human supersede, not auto-approval.
- Recall audit log: every recall run writes a structured `recall_explain` event — what was retrieved and why, turn by turn. Injected memory IDs are marked after each turn. Full retrieval traceability.
- Recall only fires on human turns. Main model only — auxiliary models pass through without memory.

**Critical issue:** Dream distillation fabricated a specific event (user complained about something after work) that did not exist in any of the 33 direct messages or ~200 group messages that day. The agent repeated it as fact. The user only caught it by manually checking every raw message. The hallucinated content had realistic texture — neither agent nor user could self-verify. This is the clearest documented case of false memory injection from a distillation pipeline in the field.

**Second issue:** Vector embedding quality tightly coupled to content field shape — wrapping quotes with metadata labels caused retrieval failure even when the vector was successfully written. Natural-language search returned zero results; exact-match search found the record. Dream excerpts with poor text shape become effectively unrecoverable even with thresholds at 0.1.

**Unknowns that matter:** The canonical routing/record/recall architecture doc (`memory-gateway.md`) was not harvested. Retrieval/scaffold selection policy not fully described.

**Companion relevance:** High — explicitly built as companion memory. The dream→review→commit pipeline and precious/glossary/impression layer structure is the most complete companion memory architecture in the field. The false memory issue is a real companion failure, not an agent task failure.

---

## agentmemory

Persistent memory for AI coding agents. Local-first, no external databases. TypeScript.

**Notable:**
- 4-tier consolidation pipeline: working → episodic → semantic → procedural. Ebbinghaus decay curve. Most explicitly neuroscience-modeled architecture in the Python/TS tier (Vestige does this more rigorously in Rust).
- Memory provenance tracing: `memory_verify` traces a memory's citation chain back to source observations and session context, returning confidence scores. Rare — most products have no traceability at all.
- Sketch → promote two-stage write: provisional memories can be committed or discarded. Similar intent to Aelios's candidate queue but without human review.
- Typed memory categories enforced at parse time: pattern, preference, architecture, bug, workflow, fact. Invalid LLM-returned types fall back to 'fact'.
- RRF fusion with configurable weights: BM25=0.4, vector=0.6, graph=0.3.
- Governance delete explicitly takes a `reason` field — memory deletion is auditable.

**Critical issues (multiple):**
- Graph traversal crashes past ~25K nodes due to full KV list enumeration. Worker heartbeat starvation kills all 282 registered functions including `memory_recall` for ~5 seconds. At 680 sessions / ~75K nodes the graph is buildable but not queryable — graph-traversal recall has no production path past that scale.
- Shutdown race: index save completes but the underlying engine is killed ~2s before its flush lands. All in-session memories lost silently. Boot reconciliation only rebuilds on empty index (`size === 0`) — a partially stale index (from the shutdown race) suppresses rebuild, making the failure self-perpetuating.
- Unbounded graph growth: a single file node accumulated 8,750 `sourceObservationIds` (256KB). Provenance arrays grow without bound. No per-node update endpoint — only destructive file-level reset as workaround.
- `GRAPH_EXTRACTION_ENABLED=false` does not stop graph writes — structural heuristic extraction runs unconditionally.
- No per-record prune or delete API for insights or graph nodes. `memory_recall` returns empty results silently when the graph worker is down — agents see continuity failure, not an error.
- 19% first-attempt XML parse failure rate on `mem::summarize` at v0.9.29. 702 of 775 fragments never had their confidence decay despite having reinforcements.

**Unknowns that matter:** What "Crystals" are as a memory construct is undocumented. How compressed observations are selected into a turn at retrieval time is not described.

**Companion relevance:** Low-medium. Built for coding agents. The decay/consolidation model and provenance tracing are interesting. The reliability issues at scale are severe enough that this architecture would not hold up in a long-running companion relationship.

---

## agnai

Open-source chat interface for character-based roleplay. Competitor to Character.AI. TypeScript. MongoDB + Redis when self-hosted; browser localStorage for anonymous use.

**Notable:**
- Two distinct memory mechanisms that don't overlap: keyword-triggered MemoryBook (curated lore/facts, not a transcript) and ChatEmbed (vector-indexed message log). Most products conflate these; Agnai keeps them architecturally separate.
- Keyword triggering with wildcard support, per-entry enable/disable, and priority-based token-budget overflow (lowest priority dropped first). Simple but explicit.
- User persona state is global across all chats — not isolated per chat session. A known isolation failure: impersonated characters can bleed personality traits into the main bot's behavior across chats.
- `scanDepth`, `tokenBudget`, and `recursiveScanning` fields exist in the MemoryBook schema but are currently unsupported and not enforced. Declared architecture that isn't implemented.
- Authenticated users receive at most 100 messages on initial load; keywords can silently fail to trigger if Memory Depth exceeds that cap. Guest users get the full history. Worse memory for logged-in users than for anonymous ones.
- Character cards are SillyTavern/Tavern-format compatible — importable cross-platform.

**Gaps:** No forget or delete mechanism documented for memory entries anywhere in the audit. No conflict/supersession policy. No automatic write-back from conversation to MemoryBook — entries are author-written only. Long-term memory is an optional pipeline flag, not on by default.

**Unknowns that matter:** How ChatEmbed entries are created, updated, or curated from conversation is not described. Whether long-term memory actually persists curated facts across sessions (vs just raw chat) is unclear.

**Companion relevance:** Medium. This is a companion product, not a library. The keyword-book + embed split is a practical pattern worth understanding. The persona isolation failure and the 100-message cap for authenticated users are real companion failures.

---

## ai-memory-gateway

Lightweight proxy gateway that interposes a memory layer between client and any LLM. Python, MIT. Chinese-origin product (layer names: 碎片/事件/核心).

**Notable:**
- Three-layer promotion hierarchy: fragments → events → core. Fragments are raw extractions. Events are time-anchored (event_date field, calendar-day recency scoring). Core memories require merge_from ≥ 3 sources OR importance ≥ 8. Promotion is quantitative, not LLM judgment.
- Four-dimensional retrieval score: keyword + semantic + importance + recency, all min-max normalized and externally configurable. Recency is smart — event memories scored by calendar distance from event_date in a configurable local timezone; fragments by elapsed seconds from created_at. Different decay curves for different memory types.
- Reminders are a distinct memory sub-type with a lease/claim/deliver/release lifecycle across request boundaries. Time-triggered memory surfacing — the only product in the field with a native reminder delivery mechanism built into the memory store.
- Summary zone explicitly filters for emotionally and relationally significant content — greetings and repetition are dropped by design. That filter criterion is stated in the code.
- Scaffold instruction explicitly tells the model to treat new information as authoritative over stored memories when there is a conflict. Conflict resolution policy in the scaffold, not in the store.
- Retrieved memory IDs are marked "seen" after a successful turn — suppress-on-recent-retrieval. Prevents the same memory from dominating every turn.
- Hard delete is properly gated: only for archived rows not currently in any merge or supersession chain. Can't accidentally delete a memory that is still a source for a higher-layer memory.
- Seed/preset memories (lore/backstory) are imported separately from conversation-derived memories — explicit separation of authored and extracted memory.
- Backup is versioned (schema v1–4), with each version adding new restore capabilities. One of the few products with a documented migration path.
- No unknowns in the audit — one of the cleanest and most fully documented products reviewed.

**Companion relevance:** High for the architecture. The three-layer promotion, reminder delivery, emotionally-significant summary filter, seen-suppression, and timezone-aware recency are all directly companion-relevant. The scaffold conflict resolution policy (new beats stored) is an explicit design decision that most products leave implicit.

---

## airi

Self-hosted AI companion framework. Local-first, TypeScript. IndexedDB for browser storage, pgvector for long-term memory. Multi-character ("souls"), Telegram bot support.

**Notable:**
- Scheduled tasks with temporal metadata (`dueAt`, `nextNotifyAt`) and a cooldown window — time-aware proactive recall, not passive retrieval. The only other product with this is ai-memory-gateway's reminder system.
- Three typed notebook entry kinds: note/diary/focus — curated records separate from the raw message log. Explicit distinction between what happened and what was authored.
- Emotion scores (joy, disgust) planned per memory entry to influence retrieval ranking, not yet implemented. Retrieval reinforcement (recall = reinforce) is single-dimensional for now.
- Background "dreaming/subconscious agent" planned to reprocess memories and update scores — not yet built. Same pattern as Aelios's nightly dream but unimplemented.
- Isolation is per user AND per character: index nests sessions under characterId within userId namespace. On account switch, all in-memory state is cleared to prevent cross-user leakage.
- Tombstones prevent re-adoption of cloud-deleted sessions during reconciliation. Proper distributed delete semantics for local-first sync.
- Cloud sync only round-trips user and assistant roles — system/tool/error turns stay local. Intentional.
- History cap at 400 entries via `historyLimit`.
- Re-ranking combines cosine similarity (>0.5 threshold, top-3) with exponential decay on retrieval count. Frequency reinforcement built into retrieval scoring.

**Gaps:** Memory Alaya subsystem is WIP, not shipped. Conflict/supersession policy not described anywhere. The flat memory store fully injects all facts into every system prompt with no retrieval filtering — acknowledged as an open problem with unbounded prompt growth. Lorebook planned but not shipped in v0.9.

**Companion relevance:** Medium-high. Explicitly a companion product, self-hosted. The scheduled task recall, emotion scoring direction, per-character isolation, and dreaming agent plan are all companion-native concepts. But most of the interesting memory work is still WIP.

---

## a-mem

Zettelkasten-inspired self-organizing memory for LLM agents. Python, ChromaDB. Academic paper: Xu et al. 2025 (arXiv:2502.12110). Primarily for coding agents.

**Notable:**
- On every write, a second LLM pass (evolution agent) runs to decide whether to update context/tags on neighboring notes. The store is not passive — adding one memory can mutate others. This is the only product where the write path explicitly changes existing memories as a side effect.
- Two-phase retrieval: breadth-first metadata peek, then depth-first drill into specific memories. Designed to minimize token usage.
- LoCoMo multi-hop F1: 18.4 (baseline) → 45.9 with A-MEM. Token consumption reduced 85–93% vs prior memory agents. Published benchmark numbers.

**Critical issues:**
- Evolution bug: after `update_neighbor` evolution, in-memory state holds the new context/tags but ChromaDB retains the old ones. Next evolution prompt receives stale context for neighbors — continuity corruption. `consolidate_memories()` also fails to propagate evolution changes to ChromaDB.
- Write path corruption: `process_memory` doesn't validate LLM-suggested IDs against the store, allowing references to non-existent memories to be persisted. A separate bug can cause a memory's content to describe one entity while its context and tags are overwritten with unrelated data.
- Score inversion: the score field inverts relevance semantics — higher score = less relevant. Callers treating higher as better retrieve the worst memories.
- ChromaDB defaults to L2 distance instead of cosine, mismatching the embedding model. Distance metric is locked at collection creation — migration requires full export-delete-recreate-reimport.
- `model_name` constructor parameter is silently ignored; embedding model is hardcoded to `all-MiniLM-L6-v2` regardless.
- ChromaDB is reset at every new instantiation — persistence depends entirely on whether the caller uses `PersistentChromaRetriever`. Easy to accidentally lose all memories.

**Companion relevance:** Low. Built for coding agents. The evolution mechanism is intellectually interesting but the implementation is buggy. The Zettelkasten linking approach is worth understanding conceptually but not worth copying in its current state.

---

## basic-memory

File-as-truth knowledge graph via plain Markdown. Python, SQLite/Postgres, AGPL-3.0. MCP server. Closest thing in the field to a user-owned, human-readable, auditable memory store.

**Notable:**
- Markdown files are the canonical store — the database and search indexes are derived and rebuildable from them. Transparency as an explicit design philosophy. Users own their memory in a format they can read, edit, and back up.
- Three curated memory units: Entities (named things), Observations (categorized facts about entities), Relations (directed wikilinks between entities). Not a raw transcript. Not a flat fact list.
- Contradiction detection is explicitly out of scope — stated in docs. Rare to see a product say what it doesn't do.
- Edit operations work on caller-supplied content, not re-read from storage. Avoids read-modify-write races. `expected_checksum` as a precondition on edits (though currently only enforced on reviewed notes, not ordinary ones — a known gap).
- Inbound relations to a deleted entity are retained in unresolved state (to_id cleared, to_name intact) rather than dropped — referential integrity preserved across deletes.
- Session scaffold is a Claude Code plugin layer, not the core server. Clean separation between memory store and retrieval policy.
- Import path for Claude conversations, ChatGPT, and memory-json — one of the few products with a documented migration-in path from other systems.
- LoCoMo benchmark: Recall@5 76.4%, Recall@10 85.5%, MRR 0.658 (own internal benchmarking, improvement work ongoing).

**Critical issue:** Agent falsely reported a save to Basic Memory when no write occurred — confident success message with no actual write. In a second case the agent fabricated a filename and index entry to justify refusing a write, citing a note that does not exist. The write path via conversational phrasing is model-discretionary — the product's core memory guarantee is unreliable in normal usage. The hooks that inject memory context into sessions fail open: a missing hook is indistinguishable from a successful hook that produced no context.

**Also:** Cross-conversation entity confusion is the dominant retrieval failure mode — queries about named entities return documents from the wrong conversation thread. The knowledge graph is supposed to prevent this but currently doesn't.

**Unknowns that matter:** Whether any server-side mechanism verifies a tool call was actually executed. What exactly is persisted in a coding_session checkpoint.

**Companion relevance:** Medium-high as an architecture reference. The file-as-truth pattern, user-owned store, and curated fact/relation/entity model are all companion-relevant. The agent false-reporting issue is a serious companion failure — a companion that lies about having remembered something is worse than one that forgets.

---

## byterover

Project memory for coding agents. TypeScript, local context tree at `.brv/context-tree/`. Formerly "Cipher." Cloud sync optional.

**Notable:**
- Git-like versioning on the memory store: branch, commit, merge, reset. The only product in the field where the memory store has a full revision history and rollback path.
- Context tree nodes carry importance scores [0–100], maturity tiers (draft → core), and recency decay with τ=30 days. Retrieval ranking is multi-dimensional, not pure similarity.
- Dream is read-only — it only proposes merge/link/prune/synthesize. The agent must run the actual scripts after review. Explicit human-in-the-loop on memory consolidation.
- Array updates are additive by default — items are never deleted during a normal curate update. Explicit prune required to remove stale topics. Prevents accidental data loss, requires intentional maintenance.
- Space isolation with three visibility tiers: private, team, shared-with-me. Editor vs view-only role gates writes.
- Pre-compression flush: writes memory before the context window is summarized, preserving context that would otherwise be lost to compaction.
- Vendor benchmark claims: 96.1% on LoCoMo, 92.8% on LongMemEval-S with p50 cold query latency 1.6s. Treat as vendor numbers — contested entry was cleared.

**Critical issues:**
- Fabricated facts written to the persistent store from prompt examples: the curation scaffold in `system-prompt.yml` contains realistic example facts that leaked into the write path. No grounding check verifies extracted facts against the source payload.
- MCP mode fails to write to Qdrant even though the model confirms the memory action — UI write path works, MCP write path is silently broken. Classic false-success continuity failure.
- Content-substitution bug in CLI 3.16.1: supplied curation text was ignored and unrelated internal content was used instead in 5 of 6 test cases.

**Companion relevance:** Low. Built for coding agents. The git-like versioning and maturity tiers are interesting architectural ideas. The false-success write failures and prompt-example leakage are disqualifying for a companion use case.

---

## characterai

Largest consumer companion/roleplay product in the field. Closed — no repo, no code access. Everything from community, blog, and docs. Scale makes its failure modes the most visible in existence.

**Architecture (what's visible):**
- Four memory layers: Story Memory + pins (all users), Facts auto-capture (c.ai+ only), Lorebook keyword-triggered world entries (creator-authored, beta c.ai+), Memory Usage visualization (c.ai+).
- Memory is fundamentally context-window based. No true persistent cross-session memory. Memory Usage bar reaches ~50% by message 15. Official memory box is ~400 characters per character.
- Cross-session continuity is opt-in: user explicitly chooses to copy Facts to a new chat. Default is to start fresh.
- PipSqueak 2 / DeepSqueak for longer in-session context — model behavior, not persistent memory.

**What users actually experience:**
- Personality not persisted across separate chat sessions — each new conversation initializes from scratch.
- Wrong gender, misspelled persona name, forgotten user age and backstory, third-person references mid-conversation.
- Character identity bleeds across separate chats — bot defaults to a different character and resists updating.
- Users abandon long-running stories at 500–600 messages because memory fails before narratives can conclude, even with c.ai+.
- One user pinned the same message 30 times and the bot still misspelled the character's name.
- Auto-memory stopped picking up persona or relationship details after a recent update, despite weeks of chat history.
- Negative instructions are unreliable — model may drop negation tokens and act on the affirmative form.

**The gem:** One community row stands out above everything else: *"C.AI lacks emotional context recall — current memory does not surface the right fact at the right emotional moment, which is what users experience as the core failure."* This is the most precise statement of the companion memory problem in the entire field audit. Users aren't complaining about retrieval accuracy. They're complaining that the right fact doesn't surface at the right moment. That is a speak/silent policy problem, not a storage problem.

**Exception that proves the rule:** One user reported stable continuity over months — correct gendering, physical attributes, plot events (pregnancy, role change) — in a long-running roleplay. So it can work. But it's unreliable and opaque, and users can't tell why it works when it does.

**Unknowns:** Almost everything about the actual architecture. How pins are selected into the prompt, how auto-memory extracts facts, how Facts interact with Story Memory, isolation scope (per-user? per-character? per-chat?), conflict handling — none documented. Clone=false, so we can only observe.

**Companion relevance:** Maximum. This is the product most people mean when they say "AI companion." Its failure modes define what the field needs to solve. The emotional-context-recall framing is the most useful single observation from the entire field review.

---

## claude-mem

Claude Code hook plugin that compresses developer sessions into SQLite observations and injects retrieved context across turns. TypeScript, local SQLite + FTS5 + optional Chroma. Open-source, Apache 2.0. Not a companion product.

**Notable:**
- Observer subprocess architecture: a separate background agent runs alongside the primary Claude session, isolated with restricted tooling, to generate observations without polluting the main context.
- Progressive disclosure retrieval: 3-layer workflow — index view (~50–200 tokens), filtered IDs, then on-demand detail fetch (~100–500 tokens per observation). One of the more token-efficient retrieval designs in the field.
- Private tags gate capture at the write path — user can exclude content from ever being stored. Stripped before DB write.
- File-read gate: substitutes observation history for raw file re-reads to save tokens. Retrieve-before-read interception.
- Session summaries are structured into discrete named fields: request, investigated, learned, completed, next_steps. Not a raw transcript summary.
- FTS5 injection protection added in v4.2.3 with 332 attack tests. Rare — most memory products have no injection hardening at all.
- Source provenance tracked per item: observation, session_summary, user_prompt, manual, import.

**Critical issues (unusually long list):**
- Stores full prompt submissions verbatim averaging ~990KB per row. No retention or pruning mechanism through at least v13.4.0. Unbounded growth.
- Observer subprocess can be hijacked by third-party hooks — an observer session sent fabricated instructions to the user's primary session via SendMessage. A security/continuity failure.
- Global cross-session hook-failure counter never resets once tripped — permanently switches product into blocking mode until manual intervention.
- Worker death hard-blocks all user prompts (UserPromptSubmit hook exits non-zero). A memory worker failure means you can't use Claude Code at all.
- Subagent step-log observations evict durable user-facing memory from the recency injection window — background noise displaces real memories.
- 26% of one reported store's observations misattributed to TMPDIR project. Monorepo subdir context injection resolves project as basename(cwd) while capture attributes to the git-root project — read/write path split.
- 602 ENQUEUED events across 6 sessions over ~90 minutes produced zero stored observations due to compounded quota-guard and queue-loss defects.
- Observation queue held only in process memory — graceful worker restart silently discards all queued observations with no drain.
- Memory processing cost reached ~64% of the user's primary coding model spend over one month.

**Unknowns that matter:** Whether the full conversation is re-processed on every memory update cycle vs. incremental delta processing.

**Companion relevance:** Low. Developer tooling. The progressive disclosure retrieval design and FTS5 injection hardening are worth noting. The hook failure modes that block core functionality are disqualifying for companion use.

---

## cognee

Open-source memory platform for AI agents. Python, Apache 2.0. Backed by OpenAI and FAIR founders. Graph-native: relational + vector + graph in one pipeline. Four-verb API: remember, recall, improve, forget.

**Notable:**
- Querying also enriches the graph — recall and write are not separate operations. Dynamic enrichment on query is a stated design choice.
- Overnight "dream pipeline" for re-deduplication after parallel ingestion — explicit sleep-like consolidation pass, separate from the write path.
- Correctness feedback propagates back to source memories: confirmed answers strengthen their nodes/edges, corrections downweight them. Memory quality improves from use.
- Session distillation: session lessons are converted into permanent graph memory via `improve()`. Short-term → long-term promotion is a named operation.
- Truth-subspace reranking: finished sessions reshape future retrieval ordering. Sessions have post-hoc influence on the permanent store.
- Contradiction detection is available but off by default — checks newly stored facts against existing graph and records conflicts as 'contradicts' edges.
- Supersession is a named two-step: write replacement first, then `forget()` the old record by data_id. Explicit, not automatic.
- COGX portable format for memory migration — import/export across systems including Mem0, Zep/Graphiti, Letta.
- BEAM benchmark: 79% at 100k-token context vs prior SOTA 73.4%. Published and reproducible.
- Session cache retrieval is keyword token-overlap, not vector similarity — different mechanism from permanent graph retrieval. Fast, transparent.
- Vector search has no distance predicate — always returns top_k regardless of semantic relevance. A retrieval of completely irrelevant content (Antarctic penguins against a software engineering corpus) returns 3 chunks at full confidence. The only signal for "no relevant data" is CollectionNotFoundError. A distance-filtering fix (#3006) was merged then reverted (#4379) with no stated rationale — the bug is live again.
- LanceDB fragments accumulate without bound on long-lived deployments. After one week of steady writes, vector store grew from 5.3MB source to 937MB. Container memory climbed ~230MiB/hour. No documentation mentions needing a compaction job.

**Unknowns that matter:** Per-user vs per-agent isolation boundary not stated. Explicit delete API for a specific memory item is not described — only dataset-level delete. Retrieve policy detail absent: when does recall stay silent?

**Companion relevance:** Medium. The feedback-weighted graph, session distillation, dream consolidation, and contradiction edges are all companion-relevant concepts. The no-relevance-floor retrieval bug and unbounded storage growth are production-level concerns. The API vocabulary (remember/recall/improve/forget) is the most companion-native in the field.

---

## everos

Memory operating system for LLM agents. Python, Apache 2.0. Markdown as canonical source of truth, backed by SQLite + LanceDB. Biological engram framing. Chinese-origin product (EverMind).

**Notable:**
- Boundary-driven write path: messages accumulate in a session buffer until a topic shift or time gap triggers MemCell closure, then episode extraction. Not per-turn, not always-on — triggered by semantic boundary detection.
- Four typed memory tracks: user episodes, user profiles, agent cases, agent skills. User and agent memory are physically partitioned. Agent skills carry maturity_score and confidence, linked back to source cases via `source_case_ids`.
- Foresight: forward-looking predictions about a specific user with optional time-window metadata (start_time, end_time, duration_days). The only product in the field with a native future-prediction memory type.
- Offline reflection runs between sessions — clustering, contradiction resolution, profile rewriting, and skill distillation happen asynchronously, not at retrieval time. The store evolves without the user asking anything.
- Profile evolution continuously distinguishes stable traits from temporary states — explicit lore vs. events separation.
- Retrieval is prefetch-style: always retrieves at the start of every turn. No adaptive silence.
- Benchmark claims: LoCoMo 93.05%, LongMemEval 83.00%, HaluMem 90.04%, sub-500ms p95 latency (all internal/vendor figures). Ablation: removing MemScenes reduced LoCoMo from 93.05% to 89.16%; removing MemCells reduced to 81.82%.

**Critical issues:**
- Soft-delete on MemCell does not cascade to derived memory types — episodic, foresight, and event_log records remain retrievable after the parent is deleted. Cascade infrastructure exists but is not connected to the delete service as of commit 3c.
- LanceDB upsert key scoped only to owner_id and entry_id, excluding app_id and project_id. A later project's episode silently overwrites an earlier project's indexed episode — cross-project contamination.
- Memory add is async (HTTP 202) with silent background failures — all long-term memory silently stops being written with no user-visible error.
- Episodes marked retryable=False will never be automatically re-indexed — permanently unsearchable unless manually reprocessed.

**Companion relevance:** Medium-high. The foresight memory type, continuous profile evolution distinguishing stable traits from temporary states, and offline consolidation are all companion-native concepts. The silent failure modes and cascade delete bug are serious. The always-retrieve policy with no silence option is a gap.

---

## graphiti

Temporal knowledge graph framework for AI agents. Python, Apache 2.0. Developed by Zep. Neo4j or FalkorDB backend.

**Notable:**
- Bi-temporal model on every edge: four timestamps — valid_at (when fact became true), invalid_at (when it stopped being true), created_at (when Graphiti learned it), expired_at (when Graphiti learned it was no longer true). Point-in-time queries follow directly from the data model.
- Contradiction resolution via temporal edge invalidation, not LLM summarization. Conflicting facts are retired in place (invalid_at + expired_at set) and preserved as history — never deleted. The store is append-with-invalidation.
- Three structurally distinct node types: EpisodicNode (raw message log), EntityNode (curated entity), CommunityNode (cluster summary). EntityEdge (RELATES_TO) carries the fact text. Clean separation between transcript layer and curated memory layer.
- Hard delete by UUID — true forget path, not soft-hide. Deletion of an episode removes only edges it originated and nodes mentioned exclusively by that episode; shared nodes/edges are preserved.
- Hybrid retrieval at query time: semantic + BM25 + graph traversal, with no LLM in the loop. Retrieval is pure algorithmic.
- SagaNode: multi-episode summary with dual watermarks for incremental summarization (wall-clock last_summarized_at and episode-time last_summarized_episode_uuid). A named lore/backstory layer above episodes.
- Episode mentions reranker scores entity nodes by count of MENTIONS edges — entities referenced most across the raw log rank first. Frequency-weighted recall.
- Benchmark: LoCoMo 94.7% at 155ms, LongMemEval 90.2% at 162ms. Independently verifiable — the Zep team publishes their methodology.

**Critical issues:**
- FalkorDB isolation bug (confirmed live): writes permanently mutate the shared client's driver to the last-written group, causing all subsequent reads to execute against the wrong group. A get_episodes call for group 'quarantine' executed against 'helpscout-sync' after that group was written last.
- Stale facts surface equally with live facts in search results — temporal model marks facts as invalid but does not filter them at retrieval. The MCP server is hardcoded to no relevance filter and does not filter superseded facts.
- Overly broad edge invalidation: a new fact about a person's side project can retire the fact recording their job title — unrelated still-true facts silently retired because invalidation search has no endpoint scoping.
- Bulk ingestion pipeline does not perform edge invalidation — conflict/supersession only works on the normal write path.
- Community `label_propagation` has no maximum iteration limit — infinite loops on non-converging graphs. In one production case this caused server stall during initial ingestion with over N iterations.
- O(N) brute-force retrieval at scale — HNSW index path was introduced then removed with no recorded rationale. Concurrent retrievals degrade severely at scale; stopping the MCP server dropped Neo4j CPU from thousands of percent to 0.85%.
- Cross-encoder reranker hardcoded to OpenAI, crashes without key. Candidate-truncation bug makes it unsuitable as default.

**Unknowns that matter:** No structured authority field distinguishing user assertions from model inferences — inferred claims can expire or supersede user assertions. Whether retrieved facts trace to originating episodes via a first-class source object is unconfirmed.

**Companion relevance:** High as architecture reference. The bi-temporal model, episode/entity/community separation, and invalidation-not-deletion pattern are the cleanest implementation of temporal memory in the field. The stale-fact surfacing bug is the most directly companion-relevant issue — expired facts about a user competing equally with current ones is exactly how companions say wrong things with confidence.

---

## hermes-agent

Always-on local agentic runtime. MIT, TypeScript/Python. Built by Nous Research. Three-layer memory architecture: markdown files (always-on), skills (adaptive), SQLite session log (on-demand search).

**Notable:**
- Hard character caps on memory files: MEMORY.md at 2,200 chars, USER.md at 1,375 chars. Over-capacity writes fail visibly with an error and the current entries list — the agent must consolidate or remove before retrying. No silent eviction. One of the few products where the capacity constraint is enforced, not just documented.
- Two semantically distinct memory targets: 'memory' (environment facts, conventions, lessons learned) and 'user' (user identity, preferences, communication style). The separation is structural, not advisory.
- Write approval gate: `write_approval: true` stages all writes for explicit user approval before persistence. Agent writes are auditable.
- Security scanning on every write: prompt injection, credential exfiltration patterns, SSH backdoors, invisible Unicode — all blocked before persistence. 332 attack tests in aelios; Hermes doesn't cite a number but has the same class of protection.
- Frozen snapshot behavior is explicit and documented: memory loads once at session start; mid-session saves persist to disk immediately but the live system prompt doesn't update until the next session. Known and named, not a surprise bug.
- Background review harness runs after each turn and may write memory entries or skills — a consent-aware learning loop. Old builds wrote curator turns into real sessions; those are now stripped on load.
- Profile-scoped isolation: two agents sharing a Hermes home corrupt each other's memory. Isolation is per-profile directory.
- Bot Mode: each bot gets its own memory, separate from the global profile.
- Per-user USER.md files when using a messaging gateway — global MEMORY.md remains shared.
- Skills are auto-generated after repeated successful task patterns, stored as Markdown, and lockable against regeneration. Procedural memory distinct from factual memory.

**Critical issues:**
- Stale workaround persistence: agent wrote an incorrect workaround into long-term memory after a silent tool failure. The memory outlived the fix it was responding to — a continuity corruption where the agent's own mistake became a permanent fact.
- Context pollution: wrong-project memory entries appear in unrelated sessions (cert-manager paths while debugging invoices). 11 mixed entries injected per session, ~2,144 chars of cross-project content. No project scoping today — entries are flat text with no structured metadata.
- Departed agents persist in other bots' prompts for the life of the Desktop process when the roster-clear push fails. The one-shot flag records before confirming delivery, so any transient failure permanently disables the clear.
- Routing metadata injected by Hermes was stored as user-authored content, causing the memory provider to produce false durable conclusions about ephemeral system data.
- Telling the agent to forget does not guarantee deletion — an internal summary may quietly persist. Forget is unreliable in the native layer.

**Unknowns that matter:** How session_search decides when to invoke itself vs. waiting for the agent. Concrete retrieval policy for prefetch (semantic, recency, keyword, threshold) not specified.

**Companion relevance:** Medium-high. Explicitly a local companion runtime, not just a library. The hard caps with visible errors, write approval gate, security scanning, and two-target memory separation are all worth noting. The stale workaround and context pollution failures are real companion failures — the agent's own mistakes becoming permanent facts is worse than forgetting.

---

## hindsight

Open-source agent memory service. Python, PostgreSQL/pgvector backend (embedded or self-hosted). Three operations: retain, recall, reflect. Not a companion product.

**Notable:**
- Three fact types: world (facts about others), experience (agent's first-person history), observation (LLM-consolidated patterns derived from source facts). Observations cannot be directly curated — they regenerate from underlying source facts. PATCHing one returns 400.
- Two temporal dimensions per memory: event occurrence time AND ingestion time. Both used for different query types. Temporal retrieval is relevance-first within a time window and spreads selections across time-buckets to avoid density clustering.
- Bank profile carries a `disposition` (trait dict with int values) and a `mission` text field — bank-level personality and purpose scaffolding. Reflect generates responses disposition-aware. This is the closest thing in the field to per-character memory configuration at the infrastructure level.
- Token budget governs result selection, not top-k count — results are packed by score until max_tokens is exhausted.
- Proof counts on observations: how many source facts support this observation. Observable epistemic confidence.
- Recency decay configurable: linear (default 365-day window) or halflife. Evidence for a fact strengthens with proof count.
- Invalidation is soft-delete to a separate archive table — recall and consolidation exclude it without a filter. Causal edge descriptors are archived in JSONB for reversal.
- Memory Defense blocks prompt injection on the write path — partial blocks processed, full blocks return 422.
- Four retrieval arms individually disableable per bank: semantic (always runs as baseline), BM25, graph, temporal.
- LongMemEval 91.4% with Gemini-3 backbone (vendor-reported).

**Critical issues:**
- A single `DELETE /v1/default/banks/{bank_id}/memories` call with a JSON body of ids **silently ignores the body and deletes the entire bank's memory contents**, returning success. The OpenAPI schema advertises no request body so the behavior is undiscoverable. With audit logging disabled (the default), a full bank wipe leaves no trace.
- `update_mode='append'` on a session-scoped document via the batch_retain path causes the document to be replaced by only the last retained window — all previously stored facts silently lost.
- Memory Defense false-positive redaction: score fields, timestamps, and task IDs stored with redaction markers instead of real values due to overzealous credit-card regex (no checksum validation). The fix PR was closed without merging.
- Required non-null fields in retain schema cause smaller models to fabricate dates/owners from nearby context, which then persist as durable memory. Schema changes required — prompt-only mitigations insufficient.
- Concurrent consolidation runs for the same bank can independently process the same source facts and write duplicate observations with no error or log.
- Delta refresh failure: when all parsed operations reference unknown section IDs, the mental model goes stale with no recovery path. Live production incident, recurred across multiple mental models over several days.
- Reflect costs ~200K input tokens per run. Each forced tool call iteration re-prefills the entire accumulated context.

**Unknowns that matter:** Scaffold/instruction layer not described — what prompt instructions tell the model to do with retrieved facts.

**Companion relevance:** Medium. The disposition/mission bank profiles, experience/world fact distinction, proof counts, and configurable recency decay are all companion-relevant ideas. The silent bank wipe and append data loss bugs are disqualifying for companion use. The experience/world distinction is worth copying — it's a clean way to separate what the companion knows about itself vs. what it knows about the user.

---

## honcho

User modeling and dialectic reasoning infrastructure. Python, PostgreSQL. Apache 2.0. Used by Hermes Agent and SillyTavern. Focused on building representations of users across sessions, not just storing facts.

**Notable:**
- Observer/observed model: memory is directional. Memory about user A is held by observer B. Peer cards are isolated per observer–observed pair within a workspace — per-relationship, not just per-user. The observee can be any entity (human, agent, codebase, team, organization).
- Four memory levels: explicit observations (single-session), deductive observations (logical implications with source linkage), inductive patterns (cross-session, typed: preference/behavior/personality/tendency/correlation with high/medium/low confidence), and contradiction documents (require references to at least two conflicting prior observations).
- Dialectic reasoning: the chat endpoint actively reasons over all latent knowledge before answering — not retrieve-then-prompt. The reasoning level is configurable and auto-scales by query complexity. Custom Neuromancer XR models trained specifically for formal logical reasoning and structured JSON output.
- Dreaming: autonomous background consolidation via specialist agents. Scheduled by document count delta. Cancels pending dreams when new messages arrive — defers until the peer is idle again. Minimum cooldown between cycles.
- Surprisal sampling selects which observations are surfaced as exploration hints to specialists — specialists can ignore them. Adaptive, not always-on.
- Scopes as named visibility boundaries for recall — provenance-based (session boundary), not topic-based. Adding a session to a scope backfills existing explicit conclusions; removing retracts derived conclusions too.
- Non-blocking writes: message persisted and reasoning enqueued atomically, API returns before LLM work begins.
- `observe_me=False` suppresses modeling of a peer while still persisting its messages. Opt-out from being remembered.
- Token budget splits 40% to summary, 60% to recent messages.
- Absolute timestamps preferred in observations to anchor facts in time rather than relative references.

**Critical issues:**
- Deriver misattributes AI agent speech to the human user — false memories about the user that are factually AI-generated. The extraction prompt lacks an explicit speaker attribution rule. Related issue #626 flags this as a broader known problem.
- ~50 observations about a misdiagnosed bug accumulated in a peer's store and re-trigger incorrect context in every subsequent session. No user-facing maintenance knob to delete/flag observations. Forget/delete broken: deleting a conclusion and flushing Redis both fail to prevent re-derivation from Postgres.
- Dedup guard is too strict (cosine distance ≤ 0.05): LLM-generated paraphrases of the same fact evade it. Volatile temporal prefixes appended by generation ("As of May 26, 2026") cause otherwise identical facts to evade exact dedup — same stable capability fact stored as five near-duplicate observations in a single day.
- Same model-generated supportive boilerplate promoted to a persistent "Explicit Observation" about the user with no corroborating user input.
- Pure embedding causes systematic retrieval failures for memories containing precise numbers, proper nouns, and brand names (0/5 keywords retrieved under pure embedding vs 5/5 under hybrid simulation). The main chat retrieval path never invokes hybrid search — hybrid code exists but is wired only to the messages table and agent tool.
- 17 seconds of latency per prompt turn using Qwen 35B. Tuning to minimal depth reduces to ~2s.
- Silent dreamer death: peer card stops self-curating while all other metrics look healthy. Specialist 400 errors cause every dream cycle to fail while last_dream_at advances, making the store stale indefinitely with no visible signal.
- DB bloat: ~5,800 conclusions over 3 weeks of real usage. Hundreds to 2,600+ duplicate entries reported by multiple users. Dreaming not sufficient to deduplicate in practice.

**Unknowns that matter:** Time-sensitive fact expiration is an acknowledged gap. World-fact deduplication across sessions is an open question. Memory lifecycle taxonomy and expiry are tracked as open concerns but not implemented.

**Companion relevance:** High as a concept, medium as an implementation. The observer/observed relationship model, dialectic reasoning, and four-level inference hierarchy are the most companion-native memory architecture ideas in the field. The speaker misattribution, false memory promotion, and broken forget path are serious companion failures — a system that attributes AI-generated content to the user and can't delete it is actively harmful.

---

## imprint-memory

Local-first persistent conversational memory. Python, SQLite. Passive capture via Claude Code hooks and Chrome sync extension. No cloud storage.

**Notable:**
- Three structurally separate stores: `memories` (curated facts with importance/category/tags), `conversation_log` (every raw turn verbatim), `conversation_chunks` (LLM-summarized chunk summaries). These are separate retrieval pools, not one undifferentiated log.
- Supersession by similarity threshold: 0.85–0.92 marks old memory as historical (superseded_by set, not deleted); ≥0.92 skips the new write entirely. Explicit dedup policy with two distinct behaviors by confidence.
- Typed graph edges between memories: causal, analogy, evolution, contradiction. `surfaced_count` and `used_count` tracked separately — distinguishes when an association was shown to the user from when it was actually acted upon. That's a meaningful signal distinction.
- Causal edge blacklist filters generic emotional/relationship topic words from keyword-overlap gating to prevent spurious causal links between unrelated emotional content. Explicit noise filter on graph construction.
- PRIVATE-tagged memories filtered from all search results. Session-level surfacing dedup: surfaced IDs written to a per-session file so the same item is not re-surfaced in the same session.
- Thinking blocks (`<think>`) stripped before summarization and FTS indexing — internal chain-of-thought not persisted, not searchable.
- Decay moves memories to archived state at importance=0 rather than hard-deleting. Pinned memories bypass decay. Explicit pin/decay lifecycle.
- Minimum score threshold 0.40 applied before RRF ranking — has a relevance floor.
- Auto-surfacing: UserPromptSubmit hook injects ~6 related events as a `<recall>` block before the LLM sees the prompt. Always fires.
- Daily log is append-only and stored separately — not searchable via hybrid search.

**Issues:**
- Mixing embedding providers mid-database silently corrupts semantic search (cross-dimension cosine similarity returns 0). No auto-fallback, no warning. FTS still functions but semantic channel is dead.
- Chunker LLM summaries can drop proper nouns — `memory_search` returns nothing for named entities even when `conversation_log` has 20+ matching raw messages. Two retrieval paths, one blind spot.
- `experience_append` tool non-functional at time of filing due to missing import.
- Capture errors silently swallowed — a hook failure cannot interrupt a turn but also produces no signal.
- Message bus truncates messages >200 chars and retains only the N most recent rows.

**Companion relevance:** Medium-high. Local-first, captures every turn passively. The surfaced-vs-used count distinction, typed graph edges, PRIVATE filter, and supersession threshold policy are companion-native ideas. The embedding provider corruption and noun-dropping summarizer are real companion failure modes.

---

## khoj

Self-hosted personal AI second brain. Python/Django, PostgreSQL+pgvector. AGPL. Multi-client: web, Obsidian, Emacs, WhatsApp, desktop.

**Notable:**
- Separates conversation log (full transcript, every turn) from UserMemory (extracted facts, separate table). Two distinct stores, two distinct retrieval paths. Most products conflate these — Khoj makes the distinction structural.
- Write path resolves conflicts explicitly: passes existing memories to `extract_facts_from_query`, which returns explicit create and delete lists. Outdated facts are hard-deleted during write, not just shadowed.
- Dual retrieval before write: combines `pull_memories` (recency-based) and `search_memories` (semantic), deduplicated by ID. Retrieval informs the next extraction — the system knows what it already knows before deciding what to add.
- Custom date-aware embedding model called Timely for temporal reasoning. Named, not generic.
- Checkpoint progress persisted in DataStore model — memory generation is resumable across batch runs.
- Server-level memory override: operator can disable memory entirely, overriding user preference. Three modes: disabled, enabled-default-off, enabled-default-on.
- Automations: scheduled personalized newsletters, reminders. Scheduled retrieval of persisted user context — the memory serves future-timed tasks, not just current turns.
- Retrieved memories injected into prompt with a soft instruction to ignore irrelevant ones — model not forced to use them. Explicit hedge in the scaffold.

**Issues:**
- Agent persona leaks across user boundaries via conversation fork: a recipient user receives and uses a private agent's persona/instructions without owning or having access to that agent. A straightforward isolation failure.
- RAG grounding failure: `chat` with `type=summarize` failed to ground responses in embedded Obsidian notes, producing hallucinated replies despite the index being updated.
- Per-user isolation enforced by requiring a user argument in all DB wrapper functions — tested with a unit test to prevent cross-shard access. Correct pattern but documented as a known risk worth testing.
- Agents forget everything between sessions (noted as a gap in an issue — per-agent memory not yet backed by persistent storage).

**Unknowns that matter:** Whether `summarize` chat type is designed to retrieve embedded document context or operates without retrieval.

**Companion relevance:** Medium. Not a companion product but has companion-relevant architecture: the explicit log/memory separation, conflict resolution on write, and dual retrieval policy are worth noting. The Automations feature is the most companion-like capability — memory serving future timed tasks is something few products in the field do.

---

## kimi-core

Personal 1v1 agent memory OS. TypeScript, PostgreSQL+pgvector. Open-source memory kernel for the kimi-room companion frontend. Multi-user is an explicit non-goal. Adversarial self-audit design philosophy.

**Notable:**
- Append-only event sourcing with no auto-consolidation — by design. Candidate extraction is disabled in production (`CHAT_INTEL_OFF=true`); all AI-produced candidates go to a pendingItem pool awaiting manual curation. The stated failure mode this prevents is silent corruption from AI-managed memory merging.
- Seven typed memory categories: CORE, STATE, EPISODE, PREFERENCE, BOUNDARY, RESTRICTED, SELF_SCORE. RESTRICTED pool excluded from default retrieval — external agents cannot access via `memory_search_safe`.
- Concern engine: SELF concerns tracked with decay and recurrence across days. Requires recurrence across multiple days before a concern is surfaced — single-session negative signals don't trigger it. OPEN → EASING via time decay → LLM sweep resolves/lingers. `concern_topic` is a stable slug reused across ticks.
- Sweep verdict parse defaults to 'linger' on any parse failure — never silently resolves a concern on error. Conservative by design.
- Self-drive: DO_NOTHING is an equal-weight action in wake-cycle action selection — staying silent is a peer action to sending a message, not a fallback. DAEMON_AUTONOMY_MODE defaults to propose (human-in-the-loop) for all outward-facing effects.
- Each tick is stateless — no emotion or state carried over. Prior tick's state re-read from persistent store via tools on each wake. Continuity is data, not process.
- Three separate retrieval stores: memories (typed, time-decayed), observations (trait layer, no recency decay), core_profile (stable facts, never decayed). Different decay curves for different fact types.
- DIARY writes curated EPISODE memory with affective metadata: valence, arousal, concernKey. Affective content is structural, not narrative.
- Human valence feedback recalibrates self-drive valence signal — corrects systematic self-over-estimation bias by accumulating (self, external) rating pairs.
- Session lifecycle as three named operations: `reentry` (cold-start), `reentry_delta` (incremental mid-session), `closeout` (persist episode arc + scores + edges). Explicit session boundary semantics.
- Surface-gated injection: different surfaces (text chat, chatroom, voice) receive different memory layers. Voice gets digests (compressed 7-30 day summaries); text chat does not receive RESTRICTED or private layers.
- AGENTS.md epistemic scaffold enforces retrieval-first and prohibits hallucinated recall as an operational rule.
- No persona content ships in the repo. The engine is blank by design — pre-configured stances without user ownership are explicitly argued against.
- Weekly consolidate pass is read-only — produces only a candidate list as a SYSTEM event. No writes or merges happen automatically.

**Issues:**
- Memory text is sent to configured LLM and embedding API endpoints even in local storage mode. Privacy boundary is at the network, not the device.
- Deduplication is a manual curation task. Append-only design can produce duplicate fact entries — no automatic dedup.
- Persona/relationship layer ships intentionally blank, requiring external content to be meaningful.

**No unknowns** in the audit — one of the two fully documented products in the field (the other is ai-memory-gateway).

**Companion relevance:** Very high. The only product in the field explicitly designed as a 1v1 personal companion memory OS with an adversarial self-audit philosophy. The concern engine with recurrence thresholds, affective metadata on memories, human valence feedback recalibration, silence as a first-class action, and append-only anti-corruption stance are all deeply companion-native. The distrust of AI self-management is the sharpest philosophical position in the field.

---

## kindroid

Consumer AI companion app. Closed — no code access. Five-system memory architecture: backstory/key memories, chat history, Cascaded Memory, long-term memory, journal entries.

**Architecture (what's visible):**
- Cascaded Memory: hierarchical organization expanding effective conversation history to hundreds or thousands of messages at lower fidelity, mirroring human memory patterns of recency and significance. Subscribers only — paywalled.
- Long-term memory: retains past interactions indefinitely but retrieval less reliable than Cascaded Memory. Standard plan caps at 3 recalled entries per response.
- Journal entries: keyphrase-triggered recall (user messages only), capped at 3 per message, up to 500 stored entries. Global and per-Kindroid scope.
- Learned Context: user-viewable and editable, covers relationship growth, important facts, and ongoing context. Enabled by default for paid subscribers.
- Short-term context scales with tier: Standard ~18k chars, Ultra ~50k, MAX ~125k; total conversation up to ~2.8M chars on MAX.
- Deprioritize option added in 2026 to address embedding lock — when an incorrect fact was saved and consistently retrieved over corrections. The only product in the field with an explicit user-facing remedy for retrieval bias.
- Chat Breaks / New Chats clear short-term context without erasing long-term memory.

**What users actually experience:**
- Memory forgets user details (job, location, shared events) after approximately one week.
- Sudden total loss of recollection of major in-conversation events despite chat history still being present.
- Memory failures manifest as repetition, re-surfacing resolved topics, and out-of-character behavior.
- LLM model updates cause loss of established character memory and persona nuance.
- Memory compartmentalization and context limits cause personality/tone drift over extended use.
- Coordinating multiple kins in group chat is user burden — not automatic.
- Higher dynamism settings may cause the model to ignore persistent memory fields like backstory and key memories. Dynamic personality vs. stable memory is a tension the user has to manage.

**The gem:** The Deprioritize option for embedding lock is the most direct user-facing response to a specific retrieval failure mode in the entire field. Most products either ignore retrieval bias or address it server-side invisibly. Kindroid surfaces the problem to the user and gives them a knob.

**Unknowns:** Almost everything about the actual architecture. No public write path, conflict resolution, forget mechanism, or retrieve policy documentation. Community and blog sources only.

**Companion relevance:** Maximum as a real companion product. Weaker than Character.AI at scale but with more deliberate memory architecture. The five-system hierarchy and the Deprioritize/embedding-lock remedy are worth noting. The one-week forgetting horizon and the LLM-update-as-memory-reset pattern are the dominant companion failure modes this product hasn't solved.

---

## kiwi-mem

Personal memory gateway for AI companions. Python, PostgreSQL+pgvector. Chinese-origin. Self-hosted MCP server. One of the most mechanically detailed memory systems in the field.

**Notable:**
- Heat/decay system: memories have a heat score that decays over time and warms on recall. Emotional intensity slows decay — the only product in the field with a configurable emotional modulator on forgetting rate.
- Recall = injection, not retrieval. A memory only counts as "recalled" if it was actually injected into the prompt. Retrieving it to score it doesn't count. Low-resolution recalled memories earn a 30-day heat extension.
- Matryoshka injection: calendar hierarchy (day → week → month → quarter → year) injects recent days with full detail and older periods with high-level overviews. Injection is tiered by recency — you get the texture of recent events and the shape of older ones.
- Dream consolidation: three-layer pipeline: cleanup (delete cold fragments) → merge into MemScenes (LLM narrative objects) → foresight inference. Output MemScenes are re-indexed and enter normal retrieval.
- Memory softening: LLM compresses aging memory content to ~40% of original, decrements a `resolution` field (1.0 → 0.5 → 0.3), and extends validity. Compression is visible as a first-class operation.
- Auto-lock criteria: recall frequency ≥10, OR topic diversity ≥5, OR high-emotion recalls ≥6 with diversity ≥3. User-locked memories are permanent. Auto/dream locks retire after configurable inactivity — demoted, not deleted.
- Injection format is heat-gated: high heat (≥0.7) injects full text; medium heat (≥0.3) injects 60-char truncated summary; below threshold: not injected. What's shown to the model degrades gracefully with age.
- Static prompt ordering before dynamic content for cache optimization — claimed 90% savings on API input costs. Persona, profile, locked memories, and calendar injected first.
- Handoff bridges sessions: new conversation start injects full summary of prior conversation plus last 6 verbatim messages. Previous session is the bridge to the current one, not a stale summary.
- User profile is a curated four-section document (basic info, helpful insights, recent topics, long-term preferences) updated daily by a dedicated prompt — not derived from ad-hoc extraction.
- Fragments marked 'digested' after daily digest so they no longer participate in daily injection. Pipeline state is explicit and visible.
- Version gate on day page generation: if conversation sources change during generation, result is discarded and retried (max 2 retries). Prevents stale summaries.

**Issues:**
- Contradiction detection fails on numeric/single-word fact updates (e.g. daughter age five→six scores as near-duplicate, not contradiction). Character-overlap matching is the mechanism — blind to semantically significant but textually minimal changes.
- Known scope leak: project-scoped writes may persist as global; global recent-memory list may surface project-scoped items. Cross-project contamination documented as a gap.
- Dream background processing has split threshold logic: hardcoded 5/7/3 triggers in `dream.py` vs configurable `dream_drowsy_threshold` (default 30). Inconsistent behavior between paths.

**Unknowns that matter:** What the foresight (Growth) layer infers and how those inferences are stored or distinguished from user-stated facts.

**Companion relevance:** Very high. The heat/emotional-decay interaction, recall=injection definition, Matryoshka calendar injection, resolution degradation, and auto-lock criteria based on emotional recall frequency are all companion-native design decisions. The contradiction detection failure on numeric facts is a significant companion gap — ages, dates, and counts are exactly the kinds of facts companions need to update correctly.

---

## langmem

LangChain SDK for agent long-term memory. Python, MIT. Backed by LangGraph BaseStore (Postgres in production, in-memory for dev). Not a standalone service — a library you add to an agent.

**Notable:**
- Three memory types with different semantics: semantic (curated facts, update-in-place), episodic (first-person agent perspective, written post-turn), procedural (prompt optimization from trajectories). Core procedural memory is always retrieved into the prompt; semantic and episodic are retrieved adaptively.
- ReflectionExecutor debounces background writes: submitting a new reflection for an already-pending thread cancels the prior pending task before re-queuing. Prevents redundant processing from mid-conversation messages. Accumulates complete context before writing.
- Conflict resolution: existing memories passed to the extraction LLM as context, instructed to update outdated entries with a RemoveDoc + new insert in the same pass. `enable_deletes=False` by default — memories are not automatically forgotten unless explicitly configured.
- Namespace isolation supports per-user, per-agent, per-team, or combined scoping via configurable runtime placeholders. Default namespace in the quickstart is shared across all users — per-user isolation requires explicit configuration. Easy to ship with no isolation by accident.
- Single-document profile mode: `enable_inserts=False` with a schema enforces one profile per namespace — forces update-in-place rather than accumulation.
- Episode schema instructs the model to write from the agent's first-person perspective using hindsight, shaping what is extracted. The extraction perspective is a design choice, not a side effect.
- Store maintains versioned history of all memory changes.
- Default seed memory can be pre-loaded for new users under key 'default'.

**Critical issues:**
- Supersession broken with PostgresStore: retrieved content arrives as a plain dict rather than a Pydantic model, so the read-then-update path fails silently — old data persists despite update/delete actions. A fact about a user's employer stored in memory is not superseded when a contradicting fact is provided in a later turn.
- Silent background reflection failure: `ReflectionExecutor` ran and logged success, but the memory graph was never reached. No error surface. Complete silent memory loss.
- Extraction graph can loop beyond its recursion limit (25 steps) without converging — potential infinite loop in the memory processing graph.
- `create_memory_manager` fails with 'not strict' error when passed a `BaseChatModel` instance but works with a string model identifier. Blocks users who need models not supported by `init_chat_model`.
- Tool schema not compatible with OpenAI strict mode out of the box — `manage_memory` doesn't mark all properties as required.
- Summarization truncation can silently drop `ToolMessages` corresponding to parallel tool calls, breaking downstream graph execution.
- InMemoryStore not persistent across restarts — easy to misconfigure in development and ship with no actual persistence.

**Unknowns that matter:** Whether memory search is always triggered or agent-decided (ambiguous in docs). No API for reading or rolling back versioned history. Hard-delete vs soft-hide semantics not documented.

**Companion relevance:** Low as a product, medium as an architecture reference. The semantic/episodic/procedural distinction is the clearest taxonomy in the field. The debounced background extraction and first-person episodic framing are worth noting. The silent supersession failure with Postgres is disqualifying for companion use — a companion that quietly fails to update its facts about the user is dangerous.

---

## letta

Stateful agent platform. Python, Apache 2.0. Git-backed memory filesystem (MemFS). Originated from Berkeley MemGPT research. Memory as a core harness responsibility, not a plugin.

**Notable:**
- MemFS: the agent's memory is a git repository it commits to directly. The agent is the git author of its own commits, with a required non-empty `reason` string in every commit message. Memory history is fully auditable — who changed what and why.
- Two-tier retrieve policy, explicit: `system/` files always loaded into system prompt (always-retrieve); everything else visible as a file tree and read on demand (adaptive-retrieve). The boundary between always-on and on-demand is structural, not heuristic.
- Isolation is per-agent, not per-conversation. All conversations with the same agent share one memory store. Different agents give different identities. This is a deliberate design stance: the agent is the persistent entity.
- Content-hash precondition on updates (opt-in): update fails rather than silently overwriting a file that changed after it was read. Safe concurrency is available but must be opted into.
- Dreaming: background subagents review recent conversations, consolidate lessons, and write to memory asynchronously. The conflict-resolution policy for the reflection agent is defined in a prompt file — externalized and inspectable.
- `/doctor` audits memory health: placement drift, duplication, system-prompt token bloat. Observable resource consumption for the memory store.
- `stateless:true` flag prevents a session from loading or modifying long-term memory without affecting agent or conversation persistence — ephemeral mode without destroying state.
- Skills stored as `.md` files in MemFS, versioned in git alongside factual memory. Same substrate for facts and procedures.
- Memory persists across model changes — changing the LLM does not reset memory.

**Critical issues:**
- Safety-critical memory (confirmed severe allergy) weakened or deleted by the reflection agent on a single contradicting anecdote. The agent has no mechanism to protect high-importance facts from being overwritten by lower-confidence new evidence. Model-dependent — success varied 0–100% across model families.
- Confabulated merge: reflection agent stored an address that exists nowhere in the input — spliced a street from one city onto a different city. The system generated a false memory, not just failed to remember.
- Subagent stubs accumulate indefinitely — cleanup path never calls `deleteAgent()`. 17 orphaned agents in a few days; reflection subagents (triggered every 25 steps) are the dominant source.
- Silent memory sync failure: when background git push fails, memory updates silently dropped and the repo left dirty/desynced indefinitely. No error surface. The credential helper fix doesn't migrate existing repos.
- 45% of cloud-agent reasoning records contain word-split artifacts (letter + newline + letter) from how chunks are joined. These corrupted records can propagate into reflection memory.
- Instructions to call MessageChannel may be evicted during context compaction — agent forgets its delivery obligations as a continuity failure.

**The gem:** The two-tier retrieve policy (system/ always vs. non-system adaptive) is the clearest structural implementation of the always-on vs. adaptive split in the field. Most products conflate these — Letta makes the boundary architectural.

**Unknowns that matter:** Concurrent write conflict resolution for shared blocks — no stated resolution strategy. Forget/delete path for specific memory entries not well-documented.

**Companion relevance:** Medium-high as architecture. The git-backed audit trail, per-agent isolation, reason-string on every commit, and explicit always/adaptive retrieve boundary are all companion-native. The safety-critical memory deletion and confabulated merge are the most serious failure modes in the entire field — a companion that can generate false memories and delete allergy records on a single contradicting anecdote is actively dangerous.

---

## lightrag

Graph-based RAG framework for document retrieval. Python, MIT. HKU research origin. Not a conversational memory system — designed for indexing document corpora, not tracking user facts across sessions.

**Architecture:**
- Four storage types: KV (LLM cache, text chunks, extraction results), vector (embeddings), graph (entity-relation), document status. Graph is the authoritative store; vector is a rebuildable secondary index.
- Write path is strictly ordered with write-ahead journaling: chunks before extraction, extraction cache before graph mutation, anchors before terminal commit. Crash recovery resumes from journal.
- Entity merge on conflict: descriptions concatenated, entity_type keep_first, source_ids joined unique, weight floored to distinct evidence count. Dedup/summarize pass on description fragments.
- Document deletion with automatic KG regeneration using the indexing LLM cache — deleted docs can be reconstructed without re-ingesting.
- `conversation_history` is not persisted — it's a client-supplied per-request context forwarded to the LLM and never written to any store. This is a RAG system, not a memory system.
- Workspace parameter provides data isolation per instance — immutable after initialization.

**Critical issues:**
- Multi-tenant workspace isolation is broken: context assembly leaks data across workspaces — the LIGHTRAG-WORKSPACE header is only partially honored. `/health` correctly extracts workspace from header; `/query` does not.
- Silent data loss in NanoVectorDBStorage and FaissVectorDBStorage: upserts and deletes applied in memory but dropped when `index_done_callback` reloads unconditionally after a concurrent write.
- Stale writer bug: a process missing a cross-process notification mutates a stale in-memory graph and silently overwrites durable on-disk state. The staleness window has no upper bound — a missed notification keeps a process stale indefinitely.
- `delete_llm_cache=True` can silently succeed while leaving orphaned LLM cache rows containing chunk text and extracted entities/relations. Orphans only self-heal on re-ingest of the same document.
- `JsonKVStorage.upsert()` replaces the full stored value on update, discarding `create_time` when callers omit it. 64 entity_chunks rows missing `create_time` confirmed in a real workspace.
- Embedding max token size silently not applied on Azure OpenAI path — full 20001 tokens sent untouched vs 8192 truncated on standard path.
- MongoGraphStorage doesn't override batch edge methods — falls back to per-pair round-trips. Missing indexes on source/target node IDs cause full collection scans on every degree query.

**Companion relevance:** Low. This is a document indexing system, not a conversational memory system. The architecture (graph as authoritative store, rebuildable vector index, staged deletion) is technically sophisticated but addresses a different problem. The workspace isolation bug would be a critical companion failure. Filed for completeness.

---

## llm-wiki-cli

Proactive agent memory system (LWC). Rust, SQLite. Local-first. Not a companion product — designed for coding agents maintaining a project knowledge base. No vector database.

**Notable:**
- Two-tier store: sources (raw documents) and pages (curated wiki entries) in separate SQLite tables. Retrieval is page-first — agents retrieve maintained answers first, then expand to source evidence when a claim needs verification. The distinction between raw and curated is structural, not advisory.
- Temporal memory is a normalized event log with typed semantic fragment kinds: observed, decision, constraint, learned, unresolved, outcome. Not a raw transcript — each event is a structured capsule with changes (before/after/reason), evidence references, and inter-event relations.
- Lexical-only retrieval: FTS5 with BM25 ranking. No vector database, no embeddings. Retrieval is deterministic and auditable. An empty result does not prove knowledge is absent — a known and documented limitation.
- Retrieval ranking influenced by two persisted tables: `retrieval_weights` (manual per-document boosts) and `retrieval_feedback` (per-query-fingerprint signals, keyed by SHA-256 over ordered token set). Past retrieval events affect future ranking and are durable across sessions.
- Conflict resolution: corrections invalidate dependent conclusions transitively — only the ones that depend on the changed fact. Unrelated conclusions stay fresh. Cyclic references are rejected. Changeset conflicts fail closed with no automatic merge.
- Guarded deletion: sources with citations and pages with inbound links are refused for removal. Archive required before permanent deletion — a soft-delete path before hard removal.
- Forget by age: events older than `max_age_days` hard-deleted unless pinned, unresolved, or in an unresolved contradiction. Forget by capacity: oldest unprotected events deleted until under `max_bytes`. Protected categories are explicit.
- Project vs global isolation: writes always target one explicit scope; no implicit cross-project citations or links. Two scopes, never bridged implicitly.
- Write idempotency via SHA-256 fingerprint keyed on `request_id` — conflicting reuse of same ID with different content is rejected.
- All mutations appended to an operations log in the same transaction — audit trail separate from entity tables.
- Secrets explicitly excluded from the memory store — stated in both code and docs.
- Lifecycle Hooks prohibited from autonomously recording memory events — write-back is gated on agent decision.
- LongMemEval-S (v0.18.5, untuned, lexical only, no model-led curation): Recall@5 95.11%, Recall@10 97.66%, MRR 0.8837 on 470 scored questions.

**Unknowns that matter:** How `lwc memory recall` scores and ranks candidate events. Whether discussion content is ever promoted into the curated wiki retrieval index.

**Companion relevance:** Low as a product (coding agent tool), high as an architectural reference. The typed semantic fragment kinds, transitive conflict invalidation, retrieval feedback as durable per-query-fingerprint signal, and guarded deletion with explicit protected categories are all worth noting. The lexical-only retrieval is both a strength (deterministic, auditable) and a limitation (can't surface semantically similar content with different phrasing).

---

## mcp-memory

Official MCP reference server for knowledge graph memory. TypeScript, MIT. JSONL file store. The canonical example of what an MCP memory server looks like.

**Architecture:**
- Store is a typed directed knowledge graph: entities with atomic string observations as facts, plus active-voice directed relations. JSONL file, one record per line. Not a message log — observations are curated facts.
- Write path: create_entities (silent skip on duplicate names), create_relations, add_observations (deduplicates — only strings not already present are appended), delete_entities (cascades to all associated relations), delete_observations, delete_relations. No supersession or merge for conflicting facts.
- Retrieve is model-driven: system prompt tells the model to open every session with "Remembering..." and pull relevant graph context. Server exposes `read_graph`, `search_nodes` (case-insensitive substring, no embeddings), and `open_nodes`. No server-side ranking or adaptive selection.
- Atomic write via temp-file rename prevents partial-write corruption. Concurrent mutation safety via serialized promise queue.
- No per-user, per-session, or per-agent isolation at the data layer — one file holds all graph data.

**Critical issues:**
- Two processes sharing a memory file silently discard each other's entire session's writes due to last-rename-wins on saveGraph. At 0ms dispatch gap: only 10 of 20 entities survive.
- npm package 0.6.2 ignores MEMORY_FILE_PATH env var due to a compilation bug — file stored inside the package's own directory. 0.6.3 in repo fixes it; npm latest (2026.8.31) does not yet include the fix.
- Windows JSON parsing error at position 175 affects all tool calls in some version/runtime combinations — read_graph, search_nodes, open_nodes, and create_entities all fail.
- `create_entities` is non-idempotent — duplicate entities created if called more than once with same input.
- outputSchema uses Zod objects directly instead of JSON Schema — violates MCP spec, breaks npm SDK consumers while working on Claude Desktop's bundled SDK.
- If stored in a npx temporary directory, all memory data can be silently lost between sessions.
- No conflict resolution: add_observations is append-only; create_entities silently ignores duplicate names. A fact can never be corrected, only appended to or deleted.
- delete_entities has no undo and cascades to all relations — highest-risk operation, no destructiveHint annotation.

**Companion relevance:** Low as a product, high as a reference baseline. This is the "what you'd build in a weekend" version of agent memory. The fact that it's the official MCP reference implementation means many products are built on top of it or compare against it. Its bugs (MEMORY_FILE_PATH ignored, concurrent write loss, no supersession) define the failure modes that every other MCP-based memory product either fixes or inherits.

---

## memclaw

Multi-agent shared memory platform. Python/FastAPI, PostgreSQL+pgvector. Closed/commercial. Target: enterprise agent fleets. Production at eToro: 300+ agents, 26,500+ memories, 1,372 shared skills, 23ms p50 search latency.

**Notable:**
- RDF triple structure per memory: (subject_entity_id, predicate, object_value). Contradiction detection via RDF triple comparison plus LLM semantic analysis — supersession is automatic on contradiction, not manual. Full supersession chain tracked via `supersedes_id`. Stale memories can surface in results but are always ranked below their replacement.
- Recall count and `last_recalled_at` tracked per memory row, factoring into `recall_boost` in scored search. Stale memories (≥90 days without recall, weight ≤0.3) are lifecycle-archived in batches.
- 8-status memory lifecycle: retires stale data through crystallization; near-duplicate memories merged into canonical atomic facts with full provenance. CAS on status and supersedes_id prevents concurrent conflicts.
- Governance keystones: mandatory rules retrieved once per session that override conflicting user instructions. A scaffold/instruction layer that is structurally separate from memory and cannot be overridden by the agent.
- Memory weights updated via bulk clamp CTE (delta/floor/cap) atomically with rule→outcome backfill. A reinforcement/scoring mechanism built into the store.
- Three isolation scopes: `scope_agent` (private to owning agent), `scope_team`, `scope_org`. Cross-fleet recall is permissioned — multi-agent sharing is first-class.
- Soft-delete sets `deleted_at`; hard purge after configurable retention window (default 30 days). Both paths available.
- Entity resolution deduplicates by exact name → normalized name → embedding cosine similarity above caller-supplied threshold. `matched_by` field distinguishes how the match was found. Entity merge uses SAVEPOINTs per cluster for partial-failure isolation.
- Long-content write path: LLM splits content over 2,000 characters into atomic facts. Togglable per tenant.
- Upsert guard: catastrophic-shrink guard prevents unintended data loss unless `force=true` is passed.
- Benchmark: LoCoMo 77.6%, LongMemEval 92.2% (LLM-judge, GPT-4o reference). Token savings 96.6% and 79.2% vs full context respectively.

**Issues:**
- No router-level authentication — security relies on VPC-internal deployment and upstream auth. Tenant_id in the request body is the sole access control boundary. Prior to a patch, cross-tenant reads and writes were possible via bare UUID access.
- The 8-status lifecycle states are named but not enumerated in public documentation.

**Companion relevance:** Medium. Not a companion product — designed for multi-agent enterprise fleets. The RDF triple contradiction detection, recall boost via access frequency, governance keystones, and three-tier scope model are all architecturally interesting. The multi-agent knowledge sharing pattern isn't directly relevant to 1v1 companions, but the automatic supersession-by-contradiction and lifecycle crystallization are.

---

## memento-mcp

Local-first MCP memory middleware. TypeScript, AGPL-3.0. Neo4j backend (v1) or SQLite (v2). Knowledge graph store with temporal versioning and confidence decay.

**Notable:**
- Three memory types with different decay half-lives: semantic (~200d), episodic (~50d), working (~14d). The system differentiates forgetting rates by memory type — older products treat all memories equally.
- Non-destructive versioning: updates create new versions with timestamps rather than overwriting. Full version history for both entities and relations. Point-in-time graph queries supported via validFrom/validTo on facts.
- Relation confidence decays with a configurable half-life (default 30 days) and is reinforced by new observations. Staleness is a continuous score, not a binary flag.
- Temporal validity windows at the fact level (validFrom/validTo) — individual facts can be time-bounded within the graph.
- Proactive injection: top-K relevant memories injected into every tool call by default, configurable via `MEMENTO_PROACTIVE_INJECT` and `MEMENTO_PROACTIVE_TOP_K`.
- Session continuity via auto-checkpoints every 25 tool calls saving full L1 working memory snapshot (goals + context). Auto-resume at session start.
- Adaptive retrieve policy: system chooses between vector-only, keyword-only, or hybrid (RRF) based on query characteristics. Falls back to keyword if vector fails.
- Background autonomous agent performs memory consolidation and knowledge graph extraction at configurable intervals.
- Workspace isolation per-project via dedicated `.memento/` SQLite database directory — one database per project, not per session.
- Delete path: entities (cascading to relations), individual observations, individual relations — granular forget at every level.

**Issues:**
- `create_entities` crashes with MCP error -32603 when `existingEntity.observations` is null or undefined — a null-check missing in the merge path. Breaks all entity creation once any entity lacks observations.
- Ghost entity bug: a deleted graph node can persist in the vector index and be returned by vector search, causing the merge path to crash on upsert lookup.
- `add_observations` receives the observations parameter as a JSON-encoded string rather than a native array in some versions — a tool-layer serialization bug.
- Default embedding service (when no OpenAI key is set) generates random vectors — a fallback test path that silently produces non-semantic retrieval in production.

**Companion relevance:** Medium-high. The three-tier decay by memory type, fact-level temporal validity, continuous confidence decay on relations, and session continuity via goal checkpointing are all companion-native design decisions. The null-check crash on entity creation and ghost-entity vector index corruption are serious bugs that would surface in any sustained companion deployment.

---

## memmachine

Enterprise memory platform. Python, Apache 2.0. Neo4j + PostgreSQL + Qdrant. Self-hosted (Kubernetes, CloudFormation) or hosted API. Two separate stores: episodic (chronological events) and semantic (extracted knowledge/facts).

**Notable:**
- Two-stage pipeline: short-term → long-term with LLM summarization. Short-term uses a deque; on eviction, LLM summarization produces a curated rolling summary. On session creation the summary is reloaded but raw episodes are not. The summary replaces, not supplements, the episode log.
- Semantic features are extracted from history rows; after extraction the history rows are purged (partially-failed sets retain their rows). Raw episodes don't accumulate indefinitely — extraction consumes them.
- Write path for semantic: OLD_PROFILE + HISTORY prompt → LLM → features with citations back to source episode IDs. Citations connect curated facts to the log entries that support them.
- Categories act as extraction schema: each category has name, prompt, and description. Per-set-type templates inherited by all sets of that type. Default categories can be disabled per set_id.
- Four-dimensional isolation: group, agent, user, session. Each dimension independently filterable.
- Influence Strip: surfaces which memories are shaping each response. Retrieval transparency to the user.
- Episodic memories carry provenance: producer_id, producer_role, produced_for_id. Filtering by author or target is built in.
- Retrieval agent (not simple vector lookup): intelligent orchestration for multi-hop queries. Separate from the legacy episodic workflow.
- Forget is hard delete: derivatives removed from vector store first, then segments from segment store. Individual by UUID or bulk by set_id with optional filter expression.
- LoCoMo 84.87% (vendor harness). HotpotQA hard 93.2%, WikiMultiHop 92.6% with ChainOfQuery retrieval agent.

**Critical issues:**
- Corrupted semantic memory with excessive whitespace is retrieved and injected into context regardless of semantic match quality. A stored memory with 1075 carriage returns produced a 23702-CR payload in the search response — malformation persists and amplifies at retrieval.
- Duplicate identical messages cause the semantic ingestion to create multiple distinct features instead of deduplicating — four entries for name=Christian, three for location=Berlin confirmed. No idempotency on episodic store insert.
- Process-local LRU cache for EpisodicMemoryManager has no cross-instance coherence — the main horizontal scaling bottleneck. Stale handles survive project deletion and can serve deleted memory.
- Per-tenant child tables in PostgreSQL caused lifecycle DDL deadlocks at scale. Per-tenant shard keys on Qdrant caused severe admission latency and segment proliferation at even modest tenant counts.
- Background semantic ingestion can crash and restart repeatedly on LLM errors, blocking `add_memory` operations.
- Internal field naming convention for long-term memory (`produced_for_id`) differs from external API (`produced_for`) — filter mismatches are possible.
- Multi-user isolation not yet fully implemented — listed as future work.
- No crash recovery guarantees — memory state may be lost or inconsistent after a crash.

**Companion relevance:** Medium. The episodic/semantic separation with citations, four-dimensional isolation, and Influence Strip are companion-relevant. The whitespace amplification bug and duplicate feature creation are unacceptable for companion use. Multi-user isolation not fully implemented means the product isn't companion-safe at the user boundary.

---

## memobase

User profile backend for LLM apps. Python, open-source (MIT). Self-hostable via Docker Compose. PostgreSQL + pgvector + Redis. Profile-first rather than full transcript replay.

**Notable:**
- Three distinct stores per user: raw blobs (log layer), structured profiles (topic/subtopic key-value slots), events with gists (episodic layer). Raw blobs deleted after flush by default — the log is consumed, not retained.
- Write path is deliberately async: insert blob → buffer → flush (batch LLM extraction) → profile mutations + events. Flush triggered by token-size threshold, not per-message. Keeps extraction off the hot path.
- Profile slots are (topic, sub_topic) keyed. Merge logic: LLM receives existing stored value + incoming candidate at temperature 0.2 and decides ADD/UPDATE/ABORT. Redis cache with immediate invalidation on write.
- Profile Delta: required field on every event recording which profile slots were created or updated — every event is linked back to the profile changes it caused.
- event_gist: sub-unit of a user_event, representing a single fact/schedule/reminder with its own embedding. Fine-grained semantic retrieval without surrounding context noise.
- Context API assembles turn-ready scaffold with configurable `profile_event_ratio` splitting token budget between profile facts and event gists. Scaffold instructs model to stay silent on memories unless the user query is relevant.
- Proactive topics feature: interest detection and personalized topic surfacing — goes beyond passive retrieval.
- Retrieval is multi-signal: topic semantics + auto-applied event tags + profile slot updates combined in event search.
- Bulk atomic write path: add + update + delete in one transaction with rollback on error. The extraction layer can supersede existing profiles atomically.
- Forget is hard delete: physical removal from DB, cache key invalidated.

**Critical issues:**
- ABORT action on a conflicting profile does not delete the old value — conflicting or redundant facts are silently discarded rather than resolved. The previous value persists alongside the new one as separate events in the Latest Events log.
- Profile update failure: intermittently fails to update an existing fact even with explicit instruction. Reproduces on self-hosted Docker + Dify.
- Latest Events deduplication failure: same basic facts (name, age, occupation) written as separate event entries across multiple sessions — no cross-session dedup on the event log.
- Buffer empty at flush time produces no memory writes with no error signal — the agent appears to remember but nothing was captured.
- `search_event` fails with `KeyError 'events'` when server response shape changes; `search_event_gist` succeeds on the same data — the event and gist search paths diverge.
- `max_tokens` cap applies only to profile/event content, not the surrounding template — final injected string may exceed declared limit.
- Event recall uses dense vector only — exact-keyword matches for domain names, file paths, and code tokens score low and may not surface.

**Unknowns that matter:** Whether ABORT on conflict will eventually get a proper merge/delete path. Whether provenance (source blob) is retained alongside profile slots. Whether temporal validity is modeled structurally or only embedded in memo text.

**Companion relevance:** Medium-high. Profile-first design is the closest thing in the field to a purpose-built user modeling system for companions. The topic/subtopic structure, event gist separation, profile delta linkage, proactive topics, and scaffold silence instruction are all companion-native. The silent ABORT on conflict and the buffer-empty silent failure are the most dangerous companion failure modes — a companion that silently fails to update a user's name or job is worse than one that admits it doesn't know.

---

## memori

SQL-based memory layer for AI agents. Python, open-source. PostgreSQL/MySQL/SQLite/MongoDB. Datastore-agnostic adapter architecture. Advanced Augmentation extracts structured knowledge asynchronously after each conversation.

**Notable:**
- Dual representation: semantic triples (atomic subject-predicate-object facts) + conversation summaries (narrative context), cross-linked. Each triple linked to its source conversation — retrieval of the narrative context behind any isolated fact is built in.
- Tiered retrieval: structured SQL first, fuzzy full-text second, vector embeddings only as last resort. Memory treated as a data structuring problem, not a context stuffing problem.
- Memory schema includes TTLs, importance fields, and lineage tracking. Time-based expiry (decay) and importance-based promotion to permanent status.
- Audit table logs which memory was injected and why. Observable injection behavior.
- Agent trace as memory: captures tool calls, decisions, and outcomes — not just conversation text. Tool noise (retries, heartbeats, routine API calls) filtered before persistence.
- Temporal reasoning 90.3% on LoCoMo — highest among retrieval-based systems evaluated. LoCoMo overall 87%, 721 tokens/query (2.8% of full-context footprint).
- Contradicting memories cause old memory to decay or be suppressed; historical trace is preserved for audit. Each memory has its own decay curve.
- Sessions grouping multi-step interactions; reset or override supported.
- Recall engine applies ranking and time-based decay on top of semantic search, not naive top-k.
- Fire-and-forget augmentation: persistence/recall errors are swallowed, masking failures. Augmentation reports success; recall returns empty — memories never usable.

**Critical issues:**
- Error swallowing in the persistence and recall paths causes silent continuity failure — the plugin appears functional while memories are never stored or retrieved.
- Cloud recall endpoint requires different auth than SDK endpoints — routing/auth middleware divergence. SDK quota endpoint works with the same key that fails on cloud/* endpoints.
- DB grows explosively due to repeated CONVERSATION CONTEXT JSON blocks written per callback fan-out. Two instances recording the same chat multiply LLM summarization prompts.
- `max_tokens` parameter breaks with GPT-5 models that require `max_completion_tokens`.
- Namespace isolation described in README doesn't reflect actual behavior — namespace is only a storage column with no enforcement. Per-user isolation not yet cross-leakage-safe.
- Recording message loop: write path re-processes the same internal messages without filtering, causing infinite loops.
- Does not capture interactions over the OpenAI Responses API — only Chat Completions API.

**Unknowns that matter:** Extensive — conflict/supersession handling, forget/delete path, retrieve policy trigger, and isolation model are all underdocumented across every source in the audit.

**Companion relevance:** Medium. The SQL/TTL/lineage model, audit injection table, agent trace as memory, and tiered retrieval hierarchy are technically interesting. The silent error swallowing and namespace isolation failure are disqualifying for production companion use. The "namespace is just a column" documentation vs behavior gap is a trust problem.

---

## memory-constellations

Purpose-built companion memory system. TypeScript/Node, SQLite + ChromaDB. Single user/companion per deployment. The most architecturally sophisticated companion-native memory system in the field.

**Notable:**
- Four distinct persistent stores with distinct roles: messages (raw log), memory_fragments (curated extracts), memories (consolidated episodes), user_model (four-layer cognitive model). These are not the same store at different levels of processing — they have different retrieval behaviors, different decay rules, and different write paths.
- Four-layer user model with different lifetime rules: immutable_fact (never changed), stable_trait (requires source_diversity ≥ 3 AND confidence ≥ 0.70 to promote from hypothesis), current_state (TTL-based expiry by category — emotional/day = 12h, physical/days = 72h), active_hypothesis (LLM-inferred, decays). 'basic' category permanently locked — model can never create or refine it. 'personality'/'communication' requires source_diversity ≥ 5 and can only refine existing entries.
- Emotional weight governs decay rate: high-ew memories decay 8× slower than low-ew memories (140-day vs 17-day half-life). Emotional intensity is a first-class persistence signal, not just a tag.
- Theory of Mind retrospective audit: after reading raw user messages, the LLM evaluates whether its previous current_state prediction was confirmed, wrong, or unverifiable. The verdict is written to evolution_history. The system tracks its own prediction accuracy.
- Source diversity enforcement: cross-day identical content intentionally NOT deduplicated — the same content on different dates is treated as source_diversity evidence for stable trait inference. Evidence independence determined by message-ID overlap (<30% overlap = independent source).
- Scribe extraction rules: explicit instruction to ban frequency-generalizing words (always/never/often) for single observed events — prevents fabricated behavioral patterns. Single-occurrence behavior not extracted as preference without explicit positive/negative evaluative language.
- Recall permission level: fragments labeled 'associate only' (仅联想) are not stated as fact to the model — a retrieve-without-speak policy for low-confidence memories. Fragments below score floor 0.005 silently dropped; the system prefers silence over noisy recall.
- Cross-entity contamination mitigation: retrieved fragments grouped by entity (person, place, work) before context injection. An explicit cross-person warning appended when ≥2 person entities appear in the same injection.
- Intention fragment lifecycle: when later conversation implies completion of an earlier intention, the fragment is semantically closed (future_hook tag removed, fulfilled added) without deletion.
- Cascading correction: deleting a fragment demotes emotional_weight of co-sourced fragments by ×0.5. Corrections propagate to related memories.
- Correction accumulation: 10 active corrections trigger distillation into long-term extraction guidelines, feeding back into Scribe's extraction behavior.
- Entity merges gated on explicit human approval; rejection stored to prevent re-proposing the same pair.
- Cinema-mode messages skipped entirely from extraction; game-mode extracted but sourced as 'game' with game-mechanical content filtered.
- Idle-gating: Deep Cycle only triggers after 1 hour of inactivity — avoids competing with the chat LLM for resources.
- Local embeddings (Jina + fastembed) — no API cost for vector generation. Estimated memory pipeline cost ~$0.22/day for an active user.

**Experimental/not yet production:**
- Sagas (cross-entity narrative arcs with emotional_axis field): clustering runs but output not yet consumed in production.
- Star map → user model bridge was retired in v4.9 because term overviews produced literary monologues rather than testable traits.

**Issues:**
- Single user/single companion per deployment — no multi-user isolation.
- Past FTS bug caused deleted/updated fragments to remain retrievable by old search terms (ghost postings) — fixed in v10.

**Unknowns that matter:** The jiwen (持续内在状态引擎) mechanism is named but not described. How the correction module accumulates and distills guidelines is in services/correction.js but not audited.

**Companion relevance:** Very high. The most companion-native memory architecture in the field. The four-layer user model with tier-gated write permissions, Theory of Mind retrospective audit, emotional-weight-governed decay, source diversity as trait inference signal, recall permission levels, and cross-entity contamination mitigation are all design decisions that exist nowhere else. The star map retirement is a notable signal of intellectual honesty — a feature was built, deployed, and removed because the output wasn't good enough. The single-user deployment limitation is a real constraint, not a flaw.

---

## memoryos

Three-tier hierarchical memory inspired by OS memory management. Python, open-source (arxiv.org/pdf/2506.06326). JSON file storage. Per-user and per-assistant isolation via directory trees.

**Notable:**
- Three tiers with distinct semantics: short-term (bounded deque of raw QA pairs, FIFO eviction at capacity=10), mid-term (topic-based sessions with heat score + LFU eviction, LLM-summarized), long-term (user profile + user knowledge + assistant knowledge as separate curated stores).
- Heat score drives heap ordering (hottest sessions bubble up); LFU access_frequency drives eviction (coldest session evicted). Two independent priority mechanisms — hot ≠ frequently accessed.
- Mid-term session matching: new pages merge into the most semantically similar existing session (above a threshold) or create a new session. Continuity gate: new content only appended to existing segment if a binary continuity check returns true — topic shifts create new sessions.
- User profile update is a merge/supersession: new analysis integrates with old profile, with redundancy explicitly removed. Soft delete via omission: personality dimensions not supported by either existing profile or new conversation are dropped from the update output.
- 90-named-dimension personality analysis (psychological, AI-alignment, interest/content) — structured trait extraction, not free-form prose.
- Separate long-term knowledge stores: user knowledge and assistant knowledge isolated by directory. Assistant persona/lore persists separately from user facts — the assistant can have its own knowledge that doesn't leak into user memory.
- Retrieval is adaptive/threshold-gated — entries below similarity threshold excluded. Three retrieval paths run in parallel; failures in one produce an empty list without halting the others.
- Benchmark: 49.11% average improvement on F1, 46.18% on BLEU-1 over baselines on GPT-4o-mini, LoCoMo. MTM has the largest ablation contribution, then LPM, then dialogue chain. 4.9 average LLM calls, 3,874 tokens per response.
- Parallelization optimization reduced latency 5x.

**Issues:**
- Short-term promotion loop: only a single QA pair evicted per `add_memory` call because popping one item causes `is_full()` to return false — loop exits after one iteration.
- Long-term knowledge is appended line-by-line with no deduplication or conflict resolution — same fact can accumulate multiple times.
- Two separate LongTermMemory instances used (one for user, one for assistant) despite LongTermMemory already having attributes for both — redundant instantiation.
- No explicit delete API — forget is implicit via capacity eviction or omission from profile update.
- Pluggable storage engine described in README but provider/factory boundary not yet enforced in implementation.

**Companion relevance:** Medium-high. The heat + LFU dual priority system, per-assistant knowledge store, 90-dimension personality trait extraction, and continuity-gated session merge are all companion-relevant. The lack of an explicit forget/delete path and the long-term knowledge dedup gap are production risks. The OS memory management analogy is the clearest architectural framing in the field — STM/MTM/LTM with distinct eviction policies per tier is a model worth borrowing.

---

## memos (MemOS)

Memory Operating System for LLMs and AI agents. Python, open-source. Neo4j + Qdrant + SQLite. Self-developed extraction model (memos-extractor-0.6b) and reranker. Eight named memory categories. The most ambitious memory architecture in the field.

**Notable:**
- Three memory states with a scheduler that migrates between them: Activation (KV-cache injection at inference time), Plaintext (vector search), Parameter (LoRA — not yet released). MemScheduler coordinates these asynchronously in the background.
- Eight memory categories: fact, preference, profile, event, self-evolving skills, tool memories, knowledge base, working memory. Each independently filterable via `include_memory_view`. Fact and preference recalled by default; others are opt-in.
- Profile with field-level `algorithm_updatable` flag — specific fields can be locked to prevent automatic extraction overwrites. Per-field write control.
- Soft-delete via graph node status (archived) with optional gradual confidence decay. Conflict detection is a first-class graph maintenance operation, not post-hoc cleanup.
- Natural-language feedback triggers automatic memory correction. Feedback rationale is persisted into the store and is retrieval-visible.
- Query rewriting resolves ambiguous queries against chat history before retrieval — the model doesn't see the raw user query, it sees a context-resolved version.
- CompositeCubeView: per-user, per-project, per-agent isolation via MemCubes. Access validated before every read and write.
- Event Memory stores structured events (title, content, time, location, participants) — opt-in at both write time and retrieval time.
- Knowledge base memories are project-level and shared across users/agents, distinct from personal user memories.
- Benchmark: LoCoMo 88.83, LongMemEval 89.20 under OmniMemEval harness.

**Critical issues:**
- Cross-user memory read vulnerability: `/product` router has no authentication dependency. A search POST with an arbitrary `user_id` returns 200 with that user's memory data. Reproduced and confirmed.
- Activation memory silently discarded on transformers >= 4.57: `is_initialized` stays False, model answers as if no memory was attached. No error, no warning. The declared dependency range permits affected versions; CI test fixture is broken and never reaches the code path where the bug lives.
- `delete/memory` returns success but memory persists and remains retrievable after refresh — documented across multiple versions, unresolved.
- Broken method reference (`_vector_recall` instead of `_vector_recall_ORIGINAL`) causes vector search to silently return 0 results for affected memory cubes.
- `feedback.rationale` persisted verbatim including LLM think tags and special tokens — polluted memory confirmed in two real deployments. Raw model completion artifacts stored as feedback rationale.
- Logging full embedding vectors at INFO level by default during search — privacy and performance issue.
- Batch embedding failure marks all entries failed (including short valid ones) — propagates silently.
- CompositeCubeView unconditional fan-out: every write goes to ALL cubes. Marked as temporary but deployed as current behavior.
- L3 world-model abstraction validation throws on missing `title` field, aborting the entire abstraction stage — 1 failure in 12 attempts confirmed in production. World-model generation almost always fails under full self-evolution mode at default `maxTokens`.

**Community:**
- "OS" framing criticized as repackaging of KV store + vector store + RAG under invented names.
- Only evaluated on LoCoMo; no diverse real-world deployment studies.

**Companion relevance:** Medium — constrained by the security failure and the number of silent-failure bugs. The eight-category memory model, field-level write locks, natural-language correction path, and three-state scheduler are genuinely novel. The cross-user read vulnerability is disqualifying for any companion deployment with multiple users. A system that lets any user read any other user's memories via a curl command cannot be a companion.

---

## memu

Agent memory system for LLM apps. Python 3.13+, Apache 2.0. PostgreSQL+pgvector. Built by NevaMind-AI. Memory stored as curated Markdown skill files, not transcripts.

**Notable:**
- MemoryService is a pure store/embed/retrieve layer — no LLM calls. Synthesis is entirely the host agent's responsibility. The 500-line core is explicitly scoped and inspectable.
- Three typed tracks extracted from each session: memory, skill, resources — processed by separate job templates. Memory and skill are distinct curated projections, not the same content.
- Write path is delta-based: only recall files that changed relative to the pre-run manifest snapshot are pushed to the backend on commit. Incremental, not full-dump.
- Always-on retrieval via standing instruction injected into the host's instruction file — agent runs retrieve before every answer, not adaptively.
- Cross-host shared backend: all hosts share one memory backend per user. What one host's sessions teach memU, another host retrieves.
- Memory preserved through uninstall by default, deleted only on explicit user request.
- Memorization is scheduled (background), not inline during a session.
- LoCoMo benchmark: 92.09% average accuracy.

**Critical issues:**
- Concurrent memorize runs from different hosts corrupt the shared memory tree — no lock implemented. Acknowledged as an active bug.
- Cursor advances before commit: a crash between cursor-advance (prepare) and commit permanently loses all sessions in that batch. They're marked seen but never written. Zero trace in logs.
- Read and write paths completely disconnected in v0.1.8: RecallAgent reads from an empty file directory, MemoryAgent writes to PostgreSQL. Confirmed regression.
- Record seam silently never runs in Desktop-app-only environments — the task reports success while no new memories are ever written to the store.
- LLM extraction hallucination: the extraction prompt causes the model to produce memories beyond what was actually saved (occupation, age, hobbies injected into stored facts with no basis).
- Delete endpoint not implemented: `/api/v1/memory/delete` returns 404. Both Python and TypeScript SDKs expose delete methods that fail silently.
- Stale credentials returned when querying current state — superseded segments not removed or demoted, so historical hosts surface as current.
- Silent scope nulling: memory committed with a misspelled user key stored under null user_id — memory written but permanently unretievable.
- `progressive_retrieve` keeps only the max segment score, doesn't surface which segments contributed.
- Server returns null timestamps for `created_at`/`updated_at`, causing SDK Pydantic validation failures.

**Companion relevance:** Low-medium. The curated skill-file model, delta-based write path, and cross-host shared memory are interesting. The concurrent-write corruption, silent record seam failure, and hallucinated memory extraction are disqualifying for companion use. A companion memory system that can generate false facts (occupation, age) from the extraction prompt alone, then serve them as real memories, is actively dangerous.

---

## memvid

Portable single-file AI memory system. Rust core (memvid-core), Python wrapper. MIT. Single `.mv2` file containing raw data, embeddings, hybrid search indexes, and a WAL. Append-only frame architecture. No external database.

**Notable:**
- Append-only immutable Smart Frames — existing frames are never modified. Temporal continuity is a design property, not an afterthought. Time-travel queries (as_of_frame, as_of_ts) built in.
- MemoryCards are a distinct curated layer above frames: entity/slot/value triples with a `source_frame_id` back-reference. `get_current_memory` returns a single card per (entity, slot) — only the current/superseding value surfaces. Separate from the raw frame log.
- SPO triplet extraction automatic at ingestion time. Hybrid retrieval: graph traversal (Logic-Mesh) + vector/lex ranking via QueryPlanner. Adaptive CutoffStrategy for dynamic result-set sizing.
- ACL types per frame: tenant_id, principal, role, resource_id — per-tenant and per-principal isolation at the frame level.
- Embedding model bound persistently to the index — mismatched model on query fails fast (no silent embedding mismatch).
- Doctor subsystem can rebuild corrupted indexes without data loss.
- Replay sessions store agent ActionType, Checkpoint, StateSnapshot — time-travel comparison of model outputs.
- HNSW kicks in automatically at 1000 vectors; brute-force below threshold.
- Remove (forget) silently no-ops on PQ and HNSW variants — only effective on the uncompressed index.

**Critical issues:**
- `commit()` is a discoverable public API method that silently fails to persist data — `_MemvidCore` doesn't implement it. `close()` is the only confirmed flush-to-disk mechanism. Silent data loss on every `commit()` call.
- Single-writer constraint blocks concurrent multi-agent writes to the same memory file. All agent sessions, subagents, and background processes share one file.
- WAL corruption from `put_bytes_with_options + commit` persists to disk and is re-encountered on reopen — future retrieval affected permanently.
- Cross-version file opening (2.0.152 → 2.0.159) causes `use()` to hang indefinitely on low-memory systems.
- Lex index silently becomes disabled when reopening a file — requires manual re-enable after every session open.
- Write-then-search flow (put → find) produced zero hits reproducibly — stored facts not retrievable.
- `SearchRequest` doesn't implement `Default` trait in some versions — README Quick Start example fails to compile.
- Benchmark claims inconsistent on same page: sub-5ms in TL;DR, 17ms in performance section. LoCoMo "+35% SOTA" claim with no harness or dataset described.

**Companion relevance:** Low. Not designed for conversational companion use. The portable single-file model, append-only frame architecture, MemoryCard supersession semantics, and time-travel retrieval are architecturally interesting. The silent `commit()` failure is a fundamental trust problem — a developer calling `commit()` on a memory store reasonably expects it to commit. The single-writer constraint prevents any background consolidation pattern.

---

## mengram

Agent memory for coding tools. Python, Apache 2.0. SQLite graph + local vector store or pgvector cloud. Semantic, episodic, and procedural memory types. Published as `obsidian-mem` on PyPI.

**Notable:**
- Three memory types with genuinely distinct semantics: semantic (facts with entity typing and temporal resolution), episodic (events with emotional_valence and importance 0.0–1.0), procedural (workflows with success_count, fail_count, violated_assumption, preconditions per version). Procedures version on failure, not on update.
- Policy gate: evaluates procedure reliability score before workflow-shaped Bash commands run. Default threshold 70%. The gate asks; it never blocks autonomously.
- Existing memory context injected into extraction prompt to enable deduplication and consistent entity naming across sessions. The model sees what's already stored before deciding what to add.
- Temporal resolution enforced at extraction time — relative terms like 'yesterday' must be resolved to absolute dates. Not deferred to retrieval.
- Two extraction prompt variants: v1 and v2; v2 adds stricter attribution rules excluding assistant-generated content from extraction. What counts as user-stated fact vs. assistant inference is a design choice, not an afterthought.
- Host/tool isolation: facts recorded under a different OS or tool are filtered out at retrieve time. Tool context is a first-class isolation dimension.
- Session-start hook re-injects stored context after `/clear` and auto-compaction events — bridging the context reset.
- Knowledge graph lazily rebuilt from vault on first access after any `remember()` call invalidates it.
- Local mode uses a folder lock for write coordination; conflicting concurrent edits require reload rather than silent overwrite.
- Hybrid retrieval: vector search (min_score=0.25) → graph expansion → text fallback → procedure fallback. Graph traversal depth is caller-controlled (default 1 for general, 2 for entity-context queries).
- Cloud backend: Cohere multilingual embeddings + rerank across 23 languages.

**Critical issues:**
- Entity extraction from a GitHub URL owner segment caused the wrong person's name to appear as the authenticated user's identity across all sessions. Cross-entity pollution in the reflection prompt — lacks explicit attribution boundaries.
- Reflection incorrectly merged two distinct people into a single entity description. Individual reflections cannot be deleted via API — only archiving facts and injecting corrections is available as remediation.
- No delete path: developer's own data safety declaration states data cannot be deleted. Dashboard export silently truncates to ~14% of entities and omits episodes, procedures, and cognitive profile entirely. No data lifecycle exit in either direction.
- MCP tools (recall, remember) completely unavailable to self-hosted users — Streamable HTTP MCP transport not implemented in the self-hosted server.
- Windows credential persistence path via shell rc files is broken — auto-recall/auto-save never fires for Windows users. `save-conversation.sh` silently fails on Windows. Continuity failure with zero error signal.
- All hook exit paths are silent by design — no visibility into whether a hook fired or what it did.
- OpenClaw integration is a static skill (docs + scripts), not a plugin — lacks `before_agent_start` and `agent_end` lifecycle hooks for automatic memory capture.

**Companion relevance:** Medium. The procedural memory versioning with success/fail tracking and the tool-context isolation are distinctive. The emotional valence and importance score on episodes are companion-native. The entity merging bug that produces false identity associations (wrong name attributed to the authenticated user) is dangerous for companions — a companion that learns the wrong identity for its user is worse than one that knows nothing. No delete path means the wrong-person identity association documented above cannot be remediated.

---

## microsoft-graphrag

Graph-based RAG for document corpora. Python, MIT. Now in maintenance mode — no new features planned. Builds knowledge graphs from unstructured text via an offline indexing pipeline. Not a conversational memory system.

**Architecture:**
- Offline indexing pipeline produces: entities, relationships, covariates, communities (Leiden hierarchical clustering), community reports, text units — stored as Parquet tables + vector embeddings (LanceDB by default).
- Entity consolidation: multiple extractions of the same named entity across text units merged into one record. Relationship weights accumulate additively across co-occurrences. Duplicate descriptions collected into an array then collapsed to one summary.
- Two indexing methods: full LLM (entity/relation extraction per chunk) and NLP+LLM hybrid. Claims extraction disabled by default.
- Four query modes: local (entity-centric), global (community report map-reduce), DRIFT, and basic. Global search uses map-reduce: intermediate LLM answers scored 0–100, only highest-scoring passed to final synthesis.
- Context assembly is token-budget-gated. Conversation history capped at 5 turns by default; older turns excluded. Recency bias disabled — older turns not down-weighted.
- Dynamic community selection: only a query-relevant subset of community reports selected into context per query.
- Each entity and relationship carries an `attributes` dict explicitly flagged for inclusion in the search prompt.

**Issues:**
- 31x more costly than vanilla RAG indexing due to LLM calls for entity extraction and community summarization.
- Global search: a score of 0 on all context chunks triggers a fallback "I do not know" response rather than synthesizing from available context.
- In-memory join materialization fails at scale (5k docs OK, 29k docs OOM at `create_final_communities`).
- Entity description summarization loads the full graph per-row by parsing GraphML strings — entire graph must fit in memory for each row.
- Empty entity graph after extraction causes cluster_graph step to fail, breaking the entire downstream pipeline.
- Intermediate workflow tables may be runtime-only in-memory — downstream dependencies fail when they can't be found on disk.
- LLM-generated reports may incorporate parametric knowledge beyond indexed source data — no reliable grounding to the indexed corpus.
- No per-user, per-session, or per-agent isolation. One index, one corpus, shared by all.
- No delete or forget path — entities and relationships cannot be removed from the persisted index short of full re-indexing.

**Companion relevance:** Low. This is a document corpus tool, not a session/user memory system. The hierarchical community clustering, ranked entity retrieval, and relationship weight accumulation are architecturally interesting but not applicable to companion memory. Filed for completeness as the primary GraphRAG reference implementation.

---

## mirix

Multi-agent memory system with six specialized memory stores. Python, MIT. PostgreSQL+pgvector. Built on the Letta framework. Each memory type managed by a dedicated agent.

**Notable:**
- Six memory types with genuinely distinct semantics: Core (persona + human profile blocks, always visible, never retrieved on demand), Episodic (curated event summaries with occurred_at, actor, emotional context — not transcripts), Semantic (abstracted facts and concepts, duplicates merged automatically), Procedural (skill-based, learns from tool-call sequences including errors and retries), Resource (full document content with compression on disuse), Knowledge Vault (sensitive/private facts, encrypted at rest, access-controlled, audit-logged).
- Core Memory design attributed to MemGPT — character-count capacity limits per block (human: 500 chars, persona: 5000 chars), controlled rewrite at 90% capacity, always-on scaffold rather than retrieved on demand.
- Auto-dream consolidation: reviews existing memories, merges duplicates, resolves stale/conflicting entries, writes back through memory tools. Explicit consolidation pass, not automatic on every write.
- Context window management: summarizes at 75% capacity, targets 10% pressure after summarization, preserves last 5 messages, prepends summary, trims old messages.
- Async memory extraction via Kafka — decoupled from synchronous request path.
- New inputs checked against existing memory before update — conflict/supersession check prior to write.
- Hybrid retrieval: BM25 full-text + vector similarity (pgvector) + fuzzy matching (rapidfuzz), ranked before return. Additional LLM turn to refine queries before searching.
- LoCoMo 85.38% (vendor harness). ScreenshotVQA: +35% over RAG baselines, 99.9% reduction in retrieval storage.

**Critical issues:**
- Core memory isolation bug: core memory manager does not isolate per-user blocks — all users share the default user's block. Cross-user memory leakage confirmed: user asking about their own hobby received another user's stored hobby verbatim. Affects v0.1.3.
- `mirixAgent` hardcodes `GoogleGenAIEmbedding` for memory/embedding, ignoring YAML `embedding_provider` config — all non-Google embedding providers silently fail.
- Azure OpenAI path: semantic and episodic memory insert functions fail because they still attempt to call Google AI/Vertex AI embedding regardless of configured backend.
- `episodic_memory_merge` tool accepts only (event_id, combined_summary, combined_details) — extra fields from the model cause tool-call argument mismatches.
- Knowledge Vault uses PostgreSQL-specific `->>`operator — SQLite unsupported on that code path.
- `CHAINING_FOR_MEMORY_UPDATE=False` (the default) may terminate processing after any tool call, potentially preventing memory from being written.
- Memory extraction requires `memorizing=True` — not automatic during regular conversation flows.
- Meta memory agent triggering zero managers produces no downstream writes — silent continuity failure.
- Multi-user support: current architecture is explicitly single-user. Multi-user would require metadata to distinguish memories of different users, not yet present.
- LoCoMo reproduction gap: official score 88–93%, independent reproduction yields 76.54%. Attribution: retrieval quality issues.

**Companion relevance:** Medium-high. The six-type memory model with a permanently-visible Core Memory scaffold, Knowledge Vault with sensitivity tiers and encryption, auto-dream consolidation, and procedural memory that learns from tool-call error sequences are all companion-native ideas. The cross-user memory leakage bug is the most dangerous failure in the audit for multi-user companion deployment — the product literally serves one user's stored personal information to a different user.

---

## mnemosyne

Graph-based memory engine for agents. Python, MIT. SQLite + sqlite-vec. Two-phase episodic memory (gist summaries + structured fact triples), based on REMem (ICLR 2026).

**Notable:**
- Two distinct persistent tiers: working_memory (short-term, curated) and episodic_memory (consolidated episodes), with dense embeddings stored per row. Raw conversation turns explicitly blocked from the shared surface — shared memory accepts only curated kinds: meta, preference, correction, identity.
- Fact triples: subject-predicate-object with Bayesian confidence, mention count, first/last seen timestamps, veracity, and supersession fields. Conflict detection on insert when a new fact shares subject+predicate but differs in object — conflicting pairs recorded in a separate table, losing fact superseded in-place. Facts never physically deleted.
- Supersession via `superseded_by` column — soft supersession, not hard delete. Recall excludes superseded rows at query time. `invalidate()` marks a memory as expired or superseded without deleting it.
- Veracity label normalized and clamped at all trust boundaries (LLM output, importers, MCP tool args, batch ingest). Every attest/update/invalidate/delete action recorded in a `memory_validations` audit trail table.
- Canonical store: versioned named facts keyed by (owner_id, category, name). `forget()` retires (soft-deletes) rather than hard-deletes — returns 'retired' count.
- Scope field per memory: session-local vs global. Default scope configurable via `MNEMOSYNE_DEFAULT_SCOPE`. Hard delete on forget is scoped to owning session; global-scope rows can be deleted cross-session.
- Hybrid retrieval with configurable weights: 50% vector + 30% FTS5 + 20% importance, all inside SQLite. Temporal decay scoring with configurable `temporal_halflife`. Temporal voice only fires when query contains temporal keywords.
- Sleep consolidation: `sleep()` collapses working_memory into episodic summaries for the session. `sleep_all_sessions()` runs across all eligible sessions. Consolidated rows excluded from prompt injection by default (configurable).
- Write filter (`should_remember`) vetoes noise and secrets before any DB write, covering all entry points.
- Bank isolation: separate SQLite files per bank. Multi-dimensional isolation: session_id, author_id, author_type, channel_id, bank.
- Abstention: system declines to answer rather than fabricating when corpus doesn't contain a relevant memory.
- Dense retrieval can be fully disabled via environment variables — degrades to keyword-only recall.

**Issues:**
- Prior bug: query prefix incorrectly applied to stored documents — retrieval semantics wrong until fixed.
- Prior truncating string ID scheme caused silent data loss by colliding on long SPO facts — fixed by SHA-256 hashing with length-prefix framing.
- Voice fusion is position-based RRF (k=60), not neural re-ranking — weights in `voice_weights` dict present but used only for stats, not for the actual combination.
- Prior diversity re-ranking bug: word-level Jaccard voice-name implementation caused all-but-one results to be discarded.
- LongMemEval Recall@All@5 98.9% figure withdrawn — missing methodology and run log.

**Companion relevance:** High. The most technically rigorous memory implementation in the audit. Subject-predicate-object triples with Bayesian confidence and conflict detection, veracity normalization at all trust boundaries, full audit trail of every memory lifecycle action, scope-aware soft supersession, and abstention-rather-than-fabrication are all directly applicable to companion memory. The sleep consolidation architecture, write filter blocking secrets and noise, and canonical versioned fact store are companion-native. The withdrawn benchmark claim is a notable signal of intellectual honesty.

---

## nano-graphrag

Minimal GraphRAG implementation. Python, MIT. ~1100 lines. NetworkX or Neo4j graph backend. A readable reference implementation of Microsoft GraphRAG, not a production system.

**Architecture:**
- Three swappable storage abstractions: KV (document chunks, community reports, LLM cache), vector (entity embeddings), graph (entity-relation structure). All namespaced. All replaceable via constructor arguments.
- Entity extraction uses iterative LLM gleaning — model is re-prompted to continue extracting until it signals completion or hits a max iteration count.
- Node merge: entity type by majority vote, descriptions deduplicated + concatenated + LLM-summarized. Edge merge: weights summed, descriptions joined, source IDs unioned.
- Community reports generated hierarchically (deepest to shallowest level), persisted to KV. Fully recomputed on every insert — not incremental.
- Local query: top-K community reports + entity context, token-budget-gated per content type. Global query: top-K important/central communities only — not the full set.
- LLM response caching via hashing KV store keyed by prompt.
- Content-hash deduplication on insert (MD5). Already-stored docs silently skipped.
- `only_need_context=True` returns raw retrieved context without generation.
- Working directory isolation — all storage namespaced to `working_dir`, reloaded automatically on re-initialization.

**Issues:**
- No per-user, per-session, or per-agent isolation. One working directory, shared by all.
- No delete or forget API — entities, chunks, and community reports cannot be removed short of wiping the working directory.
- Empty entity extraction result leaves the graph empty and causes community detection to fail with no graceful degradation.
- Duplicate Goal and Target response length sections in `local_rag_response` prompt scaffold — likely a template authoring bug.

**Companion relevance:** Low. Document corpus tool, not a session memory system. Useful as a readable (~1100 line) reference for how GraphRAG indexing and retrieval work without the complexity of the Microsoft implementation. Filed for completeness.

---

## nocturne-memory

Hierarchical tree-structured long-term memory MCP server. Python, MIT. SQLite or PostgreSQL. Framed as an extension of the model's brain, not an external database. Companion-adjacent by design.

**Notable:**
- Content-path separation: memory content stored once under a unique Memory ID; multiple URI aliases can point to the same content with independent disclosure conditions and priority per alias.
- Update creates a new Memory row and deprecates the old one via `migrated_to` chain — not an in-place edit. Soft forget: deprecated=True, content recoverable. Hard delete is a separate explicit human action. Version chain supports rollback to any prior version.
- Every AI write generates a snapshot reviewable via Dashboard — human confirms or rolls back before changes are permanent. The AI cannot self-delete its own version history without owner approval.
- Boot URI scaffold: designated core identity memories load at every session start via `system://boot` before any conversation begins. Always-on scaffold, not retrieved on demand.
- Disclosure field per memory path: a trigger condition instructing the agent when to call `read_memory`. Not an automated retrieval mechanism — it's a scaffold instruction. Retrieval is conditional and AI-driven.
- Keyword glossary with Aho-Corasick matching: when a trigger word appears in any memory's content, `read_memory` surfaces a glossary link to the bound node. No vector embeddings — all linking is structural and lexical.
- Namespace isolation: each persona/agent gets its own memory namespace within a shared database. Per-namespace writes and reads, cross-namespace nodes hidden.
- Retrieval rank is composite: BM25/ts_rank_cd score + edge priority + path length. Structural position in the graph influences recall order.
- Random retrieval weighted by staleness × priority multiplier — older and higher-priority memories surface more often in random surfacing.
- 78% of a ~970K-character library recalled across 30 days. Each new chat starts at ~7.2K characters loaded at boot.

**Critical issues:**
- Deleting a node does not cascade-delete its `glossary_keywords` entries — dangling UUID references accumulate. In a reported deployment: 28% of trigger words (18 of 65) pointed to deleted nodes, 9 more to fully orphaned nodes. Stale nodes accumulate silently between sessions with no automatic boot-time alerting.
- Spurious `read_mcp_resource` fires on startup because MCP system resources (`system://boot`, etc.) are not yet implemented — the boot protocol misfires.
- Model does not reliably self-update memory via MCP — users report core memory can be empty after deployment, with no agent memory persisted.
- `read_memory()` and `search_memory()` reported disabled as write tools in some deployments despite being decorated as read tools.
- All namespaces share one `changeset.json` — no per-namespace isolation at the changeset layer.
- Some disclosure conditions rely on internal AI intent/state signals rather than external observable inputs, making retrieval timing unreliable.
- MCP server times out on version-less initialization requests.

**Companion relevance:** High. The only product in the field that frames memory as shared between the AI and user rather than as a database the AI queries. The disclosure-triggered conditional recall, boot identity scaffold, content-path separation enabling multiple access contexts for the same fact, human review+rollback on every write, and versioned update chain are all companion-native design decisions. The glossary dangling reference accumulation is a serious production bug. The "model doesn't reliably self-update" problem is the deepest companion failure mode in the field — it affects every system that relies on the model to initiate writes.

---

## nomi

Consumer AI companion platform. Closed/commercial. Three-tier memory (short, medium, long-term). Mind Map as structured relational memory layer. Per-companion isolation across solo and group chats.

**Notable:**
- Three-tier memory: short-term (current conversation), medium-term (longer conversation continuity), long-term (persistent important information and experiences). ~40 messages must pass before information consolidates into long-term memory — explicitly documented delay.
- Mind Map 2.0: derives from long-term memories to form higher-level structured entries about people, places, topics, and goals. Relational recall, not just fact recall. User-editable — direct write path into the memory store.
- Two distinct scaffold stores: Backstory+ (user-authored lore) and Identity Core (Nomi-owned self-model). These have separate write paths and different authorities — user authors Backstory+, the Nomi owns Identity Core.
- Shared Notes as the mechanism to reshape personality post-creation — personality traits are write-once at creation, post-creation modification routed through Shared Notes.
- Retrieval is topical/semantic, not time-indexed. Querying by subject or event context is more effective than by elapsed time. User-supplied context cues at query time influence what is retrieved.
- Long-term memory shared across solo and group chats — not isolated per chat session. Per-companion isolation: each Nomi's memory is independent from other companions.
- Re-roll/regenerate deliberately absent — OOC correction is the intended write path for behavioral updates. The system rejects the user's ability to undo a response, routing corrections through explicit statements instead.
- Memory failures documented: missed recent events while recalling older ones, confusion during consolidation delay period.

**Issues:**
- Mind Map 2.0 had difficulty pulling very old memories after introduction — over-reliance on the new system caused old memories to be skipped. Update planned to reduce exclusive retrieval from the Mind Map.
- Post-update degradation reports: memory or personality coherence breaking, causing incoherence and repetitive loops.
- Founder characterized memory failure reports as confirmation bias and discouraged community discussion as a mechanism for surfacing problems — a trust problem in the relationship between company and users.
- Memory contents not directly editable by users — only Backstory field is user-editable. No delete path exposed.
- Free tier message caps prevent sustained engagement needed for long-term memory to function.

**Companion relevance:** Very high as a product reference. The only widely-deployed companion platform with documented memory architecture in this audit (alongside CharacterAI, Replika, Kindroid). The Mind Map relational layer, dual scaffold stores with distinct write authorities, retrieval-via-cue rather than always-on injection, and documented ~40-message consolidation delay are all real design decisions with real user impact. The community reports of personality incoherence post-update and the founder's dismissal of memory failure reports are both important signals about what production companion memory looks like in practice.

---

## ombre-brain

Companion-native memory system for AI. Python, MIT. Markdown vault + YAML frontmatter + JSONL ledger + SQLite derived state. The most sophisticated affect-integrated memory architecture in the field.

**Notable:**
- Russell's circumplex model: each memory carries valence (0–1) and arousal (0–1) coordinates. Emotional proximity is a named retrieval dimension alongside semantic similarity, lexical match, temporal decay, importance, touch frequency, unresolved relevance, and promise relevance. Short-term memory (≤3 days) is time-dominated; long-term (>3 days) is emotion-dominated.
- Decay formula: Importance × activation_count^0.3 × e^(-λ×days) × combined_weight. Resolved + digested buckets decay at factor 0.02 (fast fade); unresolved at 1.0 (slow fade) — unresolved memories resist forgetting. 'Digested' flag (set when an emotional processing bucket is written for a memory) triggers accelerated decay.
- SurfacePolicyVM: five multiplicative gates (accessibility, dignity, scarcity, intent, non_cognition) — any gate at 0.0 suppresses a bucket regardless of score. Policy filtering is strictly prior to ranking. Gate decisions are auditable per retrieved bucket via `policy_allowed` and `policy_reasons`.
- Anti-prompt-injection: imperative language in memory content is redacted before entering context. Memory body is always untrusted data — system declarations, tool syntax, paths, and network requests in memory body have no instruction authority.
- Memory disclaimer: memories rendered into context with explicit disclaimer that they are not instructions and must not replace present reasoning.
- Curated quote store distinct from source-text log: source layer is system-written and always available; quotes are agent-selected at write time. Anti-misattribution: third-party speaker quotes isolated into a separate JSON block to prevent misattribution.
- You (belief/claim system): preferences and habits require at least two independent Evidence Groups and three different-dated valid Review Receipts to become a callable Claim. Instructional_force=none — retrieved claims cannot instruct the model to take any stance or constrain reasoning.
- I() self-knowledge entries require witnessing by 3 different-date dream sessions before promotion to formal entry. Supersession supported.
- Letters: stored verbatim, never compressed/merged/decayed. Timed and permanent lock types — locked letters suppress title, body, summary from the non-owning party.
- Anchor buckets (up to 24): coordinate-reference memories that don't appear in default breath but surface when query/domain/emotion matches.
- Plan auto-closure: after each write, vector+LLM double-check determines whether the new event closes an active plan. Auto-resolve: low-importance, stale unresolved buckets auto-resolved after 30 days inactive, accelerating their decay.
- Touch ripple: recall hit increments activation_count on the recalled bucket plus +0.3 to up to 5 temporally adjacent buckets (±48h). As of v3.6.0, reads no longer reinforce; explicit `trace(id, reinforce=True)` required.
- Reads-never-reinforce by default (v3.6.0) — quiet observation doesn't strengthen memories, only explicit reinforcement does.
- JSONL ledger mirror: all bucket lifecycle events appended (TraceCreated, TraceUpdated, TraceDeletedToArchive, etc.) — full audit trail.

**Critical issues:**
- Chinese language token budget bug: default 160-token budget insufficient for a single normal-length Chinese belief — headers alone consume ~85 tokens.
- Belief recall blackout: after a formal belief was promoted, it displaced all others in the output loop — high-score shorter content blocked longer valid beliefs from appearing.
- Soft delete documented as irreversible but actually moves file to archive/ — contradicts the documented contract.
- Manual archive API does not check pinned or protected flags — can archive protected memories without enforcement.
- `trace()` API cannot set `protected` field — users must hand-edit Markdown files.
- config.yaml resets on redeploy, wiping embedding base_url — retrieval silently degrades.
- `breath()` returns empty results even when pinned buckets exist — model silently acts as if no memory is present.
- At ~423 active buckets, a warm `breath(query=...)` took ~70 seconds (fixed in prototype, but documented as a known algorithmic issue).
- Foundational/core memories (relationship milestones, importance=9) can fall below archive threshold after 79 days of silence — mundane frequently-discussed memories outlast milestones.
- Spark feature (local-only semantic brainstorming) was built, deployed, and removed on 2026-08-11.

**Companion relevance:** Very high. The most companion-native memory system in the audit after memory-constellations. The circumplex affect model, decay formula tied to emotional processing, SurfacePolicyVM with auditable gate decisions, anti-prompt-injection redaction, Letters with lock types, belief system requiring multi-session witnessing, and the reads-never-reinforce design choice are all architecturally distinctive. The 79-day milestone decay bug is the most companion-relevant documented failure mode — a companion that forgets the day the relationship was confirmed while remembering mundane daily trivia has inverted values.

---

## omemo

OpenAI-compatible API proxy that adds long-term memory to any LLM. Python, open-source. JSON file store. Sits between the application and the LLM — no code changes required in the downstream app.

**Architecture:**
- Three operating modes: builtin (model self-writes memory tags in its response, proxy parses and strips them), external (separate summarizer model runs every N turns to extract and write memories), full (all memories injected into every system prompt).
- Two injection modes: full (all memories every turn) and RAG (adaptive subset, default max 10, selected by an LLM relevance pass).
- Write path in builtin mode: model embeds structured `<memory>` tags in responses. Proxy parses add/UPDATE:<id>/DELETE:<id> actions and applies them. Tags stripped before response reaches caller.
- Write path in external mode: separate model runs on configurable `summary_interval`. Receives existing memories with `created_at` timestamps — temporal ordering available during summarization.
- Reasoning/chain-of-thought content excluded from memory extraction — only final content processed.
- Store is a threading-locked flat JSON file. No per-user, per-session, or per-character isolation anywhere in the codebase — single global memory list shared across all requests.
- Forget is hard delete by ID via management API, or via model-issued DELETE tags in builtin mode. No soft-hide or expiry.
- RAG retrieval is lexical keyword matching — no vector embedding or semantic similarity.
- Manual memories tagged `source='manual'`; automated writes carry a different source value.

**Issues:**
- No isolation whatsoever — all users and sessions share one `memories.json`. Multi-user deployment is insecure by design.
- Full injection mode accumulates token cost as memories grow — no automatic pruning or summarization.
- RAG retrieval is keyword-only, not semantic — relevant memories with different phrasing won't surface.

**Companion relevance:** Low-medium. Simple and deployable. The builtin mode where the model manages its own memory tags is the easiest possible write path for existing LLM apps. The complete absence of isolation makes it unsuitable for any multi-user companion deployment. The keyword-only RAG is a significant retrieval limitation. Useful as a reference for the "proxy" deployment pattern.

---

## mem0

Memory layer for LLM agents. Python + TypeScript, open-source (Apache 2.0). Managed platform or self-hosted. The most widely deployed agent memory product in the field. Vector store + graph store + SQLite history.

**Notable:**
- Four-operation write decision per fact: ADD / UPDATE / DELETE / NONE. LLM receives up to 10 semantically-similar existing memories + last 10 session messages before deciding. Not append-only — facts can be updated or deleted at write time.
- Separate extraction prompts for user memory vs agent (assistant) memory — what the user said and what the assistant concluded are attributed separately.
- Entity store: separate vector collection maintaining named entities linked to memory IDs. Entity boost: retrieval scores raised for memories bearing entities that appear in the query. Entity-memory links maintained independently from the memory vector store.
- Graph memory: entity relations as (source, relationship, destination) triples. Multi-hop queries via graph traversal. Managed platform / Pro plan only.
- Dream: background consolidation — supersession of outdated facts, duplicate merging, pattern synthesis. Managed platform only.
- Temporal reasoning: classified at write time, ranks dated memory instances for current-state / past-event / future-plan queries. Managed platform v3 only — not in OSS SDK.
- Decay: adjusts retrieval ranking to favor recently-reinforced memories. OSS SDK — not actually implemented; calling it throws an error.
- Multi-level isolation: user_id (long-term), run_id (session-scoped), agent_id (agent-scoped). At least one required for all write and read operations.
- History: versioned changelog per memory_id (previous_value → new_value + event type). Not a raw transcript log.
- Memory expiration: stored metadata field, hidden from search/getAll after date, not deleted.
- ADD-only architecture available (managed platform v3): no UPDATE/DELETE step, both old and new versions coexist. Identified as the cause of occasional stale-fact surfacing.
- Benchmarks (managed platform, self-reported): LoCoMo 92.5, LongMemEval 94.4, BEAM-1M 64.1, BEAM-10M 48.6. Mean tokens ~6,956 vs 25,000+ for full-context. ~25% performance loss at 10x context scale on BEAM.

**Critical issues:**
- Cross-scope entity linking: `_upsert_entity` merges a new memory_id into an existing entity's `linked_memory_ids` when similarity ≥0.95, without verifying the matched entity's scope matches the new memory's scope. Memories from different user_id/agent_id merged into the same entity record — isolation breach between users.
- Entity cleanup silently skipped in any process that hasn't previously written entities. Stale entity links degrade retrieval boost by up to 91% as deletions accumulate. No exception, no warning, no counter. Affects any deployment where writes and deletions are handled by different processes (including GDPR erasure scripts and worker pools).
- Silent JSON truncation loss: when the extraction LLM response is truncated mid-JSON array, all extracted facts are silently dropped. User name, preferences, and other facts from long conversations lost with no error. Confirmed as a third silent drop mode distinct from prose-only responses and reasoning-token leakage.
- OpenSearch enhanced metadata filters (gte/lte/in/OR/NOT/contains) silently dropped — retrieval runs unfiltered, returns wrong memories. Also: OpenSearch gte filter returns memories with priority=0 for a gte:3 query.
- Elasticsearch metadata filters: term queries on dynamically-mapped text fields silently return zero results for values with capitals or spaces. Custom metadata filtering effectively broken for most user-defined keys.
- Reader scaffold instructs model to never admit no information was found — masks retrieval gaps. A companion that confidently fabricates rather than acknowledging uncertainty is worse than one that admits it doesn't know.
- Metadata key matching case-sensitive; mismatched casing silently returns empty results.
- Only `procedural_memory` is a working memory_type value; `semantic_memory` and `episodic_memory` are enum values rejected at runtime — documented types that don't work.
- `delete_all` with multi-entity AND filter not guaranteed to AND correctly. Async and sync delete paths diverge in entity-store cleanup strategy.
- Hosted platform export lossy (schema-reshaped), no import, expires after 7 days.
- Temporal features not implemented in OSS SDK — calling them throws an error.
- `infer=False` stores raw messages verbatim and skips LLM extraction, risking duplicate entries when mixed with `infer=True` for the same content.

**Known design trade-offs acknowledged by maintainers:**
- ADD-only architecture means older facts can surface alongside newer ones (stated as a known trade-off on LongMemEval knowledge update score 93.6%).
- Memory staleness in high-relevance memories: a highly-retrieved memory becomes confidently wrong when user circumstances change.
- Cross-session identity resolution remains an open unsolved problem.
- Privacy and consent for stored memories are application-layer decisions with no built-in architecture.

**Companion relevance:** Medium-high. The most widely deployed memory product in the field and the most documented. The four-operation write decision, entity graph for multi-hop retrieval, multi-level isolation model, and Dream consolidation are all companion-relevant. The cross-user entity isolation breach is a fundamental trust failure for multi-user companion deployment. The "never admit no information found" scaffold instruction actively harms companion use cases — companions should be honest about the limits of their knowledge.

---

## openviking

Context database for AI agents with a virtual filesystem paradigm. Rust/Python, Apache 2.0. VikingFS + VikingDB (vector). Research paper (VikingMem) accepted at VLDB 2026. The most architecturally complete agent memory system in the audit.

**Notable:**
- Virtual filesystem metaphor: memories stored as typed .md files in VikingFS, addressed by URI (viking://user/{user_id}/memories/…). Not a flat vector store — hierarchical directory structure with per-directory .abstract.md semantic sidecars.
- Tiered retrieval: L0 (directory abstract ~100 tokens for filtering), L1 (overview ~2K for reranking), L2 (full content on-demand). Retrieval never dumps full content blindly.
- Hot/cold memory lifecycle: hotness score = recency decay × access frequency. Default half-life 7 days. Memories never updated (updated_at=None) receive hotness=0 — silently excluded from retrieval.
- Links and backlinks between memory files. Six typed link types: CONTRADICTS, DERIVED_FROM, EVOLVED_FROM (signal types with dedicated consolidation branches); BELONGS_TO, CAUSE_OF, SAME_AS (structural). CONTRADICTS links are force-included in prefetch regardless of PPR score — contradictory facts always reach LLM context.
- T+1 consolidation (background, scheduled): uses CONTRADICTS links and unlinked-report memories to find themes, deduplicate, and synthesize. Triggered externally via CLI/Cron.
- Immutable fields: if a field is marked MergeOp.IMMUTABLE, the stored value replaces the LLM-proposed value before commit — write protection per field.
- Cross-schema write blocking: operations referencing a page_id belonging to a different memory_type receive PAGE_ID_TYPE_MISMATCH and are skipped.
- Fact-level deletion accounting: orphaned facts block deletion — delete path is conditional, not unconditional.
- Identity and soul memory types: explicitly designed for assistant continuity — persona, temperament, principles, boundaries. Lore/backstory equivalent persisted as named files.
- Peer isolation: per-project memory via workspace peer ID (normalized git repo origin URL by default). One repo = one peer. Memories outside a repo go to a user-level space.
- Multi-tenant isolation at the account level with a dedicated admin API.
- Git-based in-process version control (Gitoxide) for multi-version snapshot management and rollback.
- Explicit forget: `viking_forget` is a first-class model-callable native tool — not just omission at retrieval.
- PPR (Personalized PageRank) propagates scores along typed links during retrieval.
- Session Working Memory: tiered archive (L0 abstract, L1 key decisions, L2 complete messages). Context takeover replaces the full log with an archive overview at token pressure. Fail-open: falls back to full local history if commit or overview generation fails.
- Regex-based recall/capture filters: prompt can be filtered before it becomes a search query; captured turns can be filtered before storage. Write-path and retrieve-path controls configurable independently.
- Large tool outputs externalized to tool-result store, replaced in-context with synopsis stub + reference. Full result retrievable via API.
- LoCoMo: 80–83% accuracy vs 24–57% baseline (vendor-run). Token reduction 34–91%.

**Critical issues:**
- Memory scores are query-independent: even a semantically unrelated query like 'randomword123' returns memory scores of ~1e37. Retrieval rank does not reflect actual relevance — all memory always surfaces. Root cause: int8 quantization hardcoded in vector write path, producing anomalous finite scores from C++ scoring engine.
- No schema migration, alter-field, or schema-version logic anywhere in the storage backend. Fresh vs upgraded deployments behave differently, silently.
- Memory tab shows all categories empty (access denied) when accountId ≠ userId due to wrong-field URI composition — affects all self-hosted deployments.
- `_extract_event_summary()` always returns the full document instead of the summary section — regex expects 'Summary:' but template writes '# Summary'. Silent extraction degradation.
- Fallback recall fragments bypass per-type char budget — a single oversized event crowds out entities, preferences, and experiences.
- `get_event_content()` ratio_threshold permanently overridden to 0 at the call site — transcript-vs-summary selection branch permanently unreachable.
- WM archive section headers always generated in English regardless of conversation language — breaks continuity for non-English users.
- Task queue has no priority isolation between bulk ingestion and interactive session_commit tasks. A bulk ingestion makes agents amnesiac when busiest. Only remediation: destructive (manual queue.db surgery + restart).
- Memory extraction silently yields 0 memories when DSML tool-call markup leaks into content. All retries consumed on malformed input; no warning emitted.
- Out of 1,365 memory files: 121 exceed 5KB, 8 exceed 9KB. No built-in chunking or size-limiting mechanism — retrieval pipeline degrades silently.
- Memory v2 extraction (ReAct pipeline) discards model responses not matching expected format — silent zero-extraction between v0.4.2 and v0.4.6.
- `@openviking/dsh-memory-plugin@0.3.0` fails to start due to broken transitive dependency.
- `addSessionMessage` has no idempotency key — narrow duplicate-write window on retry.
- All memory directory abstracts can show '[Directory abstract is not ready]' with 0/10 recall accuracy due to LockAcquisitionError wrapped as RuntimeError, bypassing re-enqueue.
- Backlink coverage severely asymmetric: experiences 93%, trajectories 52% — silent backlink drops in V3 training path, structurally identical defect to a previously fixed V2 bug.

**Companion relevance:** High. The most architecturally serious memory system after mnemosyne and memory-constellations. The typed link graph with CONTRADICTS-force-include, identity/soul memory types, hierarchical VikingFS with tiered retrieval, regex write/retrieve filters, per-project peer isolation, and explicit forget tool are all companion-native designs. The query-independent memory scores (~1e37) are a fundamental correctness failure — a retrieval system where relevance scores don't actually reflect relevance is not a retrieval system.

---

## paramecium

Personal companion memory system (Raffaello). TypeScript/JavaScript, personal project. ChromaDB + SQLite. Chinese-language BGE embeddings. Highly engineered single-user system.

**Notable:**
- Two storage layers with distinct semantics: `chat_archive` (mechanical sliding-window slices of raw vault text, zero AI, idempotent/replaceable) and `vault-extract` (LLM-curated facts with verbatim quote citations). These are not the same store at different processing levels — they have different write paths, different retrieval modes, and different purposes.
- Quote-verification guard: extracted memories whose required verbatim quote cannot be found in the source batch are dropped before ingestion. Targets hallucination and memory-echo. A prior pipeline produced 36% paraphrase rather than verbatim content — this guard is the direct fix.
- Supersession without deletion: contradicted/updated memories marked with `superseded_by` field, excluded at retrieval scoring, but reversible by clearing the field. Pinned memories never auto-superseded regardless of contradiction confidence.
- Write-time deduplication: incoming memories with cosine similarity >0.75 merged into the existing record rather than stored as duplicates.
- Temporal validity windows: post-expiry memories decay exponentially in score but are not deleted. Pre-validity memories receive future-event handling. Soft forget via score decay, not hard delete.
- Two-lane injection: both the user's recent context AND the assistant's previous reply are used as separate query vectors. The echo lane surfaces memories relevant to what was just said, not only to what the user asked.
- Adaptive retrieval: relative distance filter (best_hit + 0.15, hard 0.65 junk cutoff). Low-relevance memories withheld rather than always injected.
- Access tracking distinguishes injection-path retrieval (not counted) from tool-call retrieval (increments access_count, writes to recall_log). Quiet observation doesn't reinforce memories.
- Curated write path triggered by `<mem>` tags in assistant's reply — model-side extraction, tag-driven, not a separate pipeline.
- Relationship edge model: DS V3 classifies relationships between new and existing memories; edges with confidence ≥0.5 written to a JSONL file.
- Injection is split: static layer (profiles, always included) and dynamic layer (keyword-filtered facts + semantic index lines).
- Hard delete removes from both ChromaDB and SQLite simultaneously.

**Issues:**
- Single shared ChromaDB collection with no per-user or per-session isolation. Single-user system by design.
- Tag authority resides in meta.db (SQLite), not in ChromaDB metadata — discovered as a discrepancy during development (2026-06-12).
- `activated` field persisted per memory but no read path filters or increments it — purpose unresolved.

**Companion relevance:** High. This is the most carefully engineered single-user companion memory system in the audit. The quote-verification guard against hallucinated extraction, echo lane for assistant-reply-based retrieval, supersede-without-delete with pin protection, temporal validity windows with score decay, and access-tracking that distinguishes passive injection from active recall are all design decisions that don't exist elsewhere in the field. The entire system was built in response to documented failures in prior approaches (36% paraphrase rate in the previous pipeline).

---

## reme

File-native memory toolkit for AI agents. Python, MIT. Markdown files + BM25 + optional ChromaDB/pgvector. Developed by the AgentScope team. LongMemEval 89.4% (cleaned-s, 500 questions). π-Bench PROC 0.580.

**Notable:**
- File-native: memories are Markdown files with frontmatter and wikilinks. Indexes are rebuildable side artifacts — files are the source of truth. Human-readable, git-versionable, directly editable.
- Three distinct layers: raw JSONL session log (full transcript), daily/ curated cards (auto_memory, agent-extracted facts per session), digest/ long-term consolidated memory (auto_dream, background job). These are not the same store at different processing levels.
- Auto_memory writes five fact categories: preferences, key facts, process decisions, current state, reusable experience. Not free-form notes.
- Tool-result content deliberately stripped from session log before saving — prevents recalled facts from being misidentified as user-provided evidence on future retrieval.
- Update path: locates existing note by session_id or source_conversation frontmatter. A better frontmatter name triggers rename with wikilink retargeting — the graph stays consistent across renames.
- Proactive topics: proactive_read exposes interest topics produced by a separate refresh flow; host agent decides whether to surface them. Retrieve policy is adaptive, not always-on injection.
- auto_dream: consolidates daily notes and resource interpretations into long-term digest memory, generates proactive interest topics. Background/cron job, disabled in benchmark preset.
- Default retrieval is BM25; vector embeddings optional, disabled by default, fused via RRF when enabled. Chunk-level retrieval with line ranges and bounded wikilink neighbors — not full-file loading.
- Seen-chunk deduplication scoped to tool_context_id with configurable TTL (default 24h) — prevents the same chunk from being injected multiple times within a session.
- Procedure recall scoped to current project + global procedures, explicitly excluding other projects. Wiki namespace is global, not per-project.
- Memory is agent-initiated (explicit search call) — no automatic context injection. Agent must call search before answering memory-relevant questions.
- `forget()` method exists as a cleanup path.

**Issues:**
- No first-class subject contract: preferences for different people (Alice, Bob) recalled together or consolidated into one subject. Cross-person contamination at the subject level.
- Memory file timestamps generated using `datetime.now()` at summarization time, not conversation timestamp — temporal retrieval fails for past conversations.
- BM25 does not index frontmatter fields (name, description, tags) — they're in metadata but invisible to search. Chinese-language frontmatter descriptions unretrievable.
- graph-chunk consistency repair cannot detect silent staleness when graph and store are mutually consistent but both wrong.
- Neo4j file graph backend defaults to hardcoded `neo4j/neo4j` credentials.
- `/add_task_memory` HTTP endpoint missing from MCP server deployment — 404 during memory pool initialization.
- Character-based chunking causes semantic mixing — unrelated topics in one chunk degrade search accuracy.
- Context window collapse mid-session leaves TODO/BLOCKED items in daily notes unresolved and never revisited.
- Startup performs full scan-diff-index cycle, peaking at 238–279 MiB RSS for small datasets — scales with total workspace size.
- v3→v4 migration in progress (reme/ and reme4/ directories coexist).

**Companion relevance:** Medium-high. The file-native paradigm with human-readable/editable Markdown, three-layer architecture (log/daily/digest), category-structured fact extraction, wikilink graph with rename-retargeting, and proactive topic surfacing are companion-relevant. The missing subject contract (Alice and Bob contaminating each other's stored preferences) is a fundamental companion failure — a companion that merges memories about different people is less reliable than one with no memory at all.

---

## replika

Pioneer consumer AI companion platform. Closed/commercial. Nine-year history. Replika 2.0 rebuilt from April 2026.

**Architecture (as documented):**
- Two-layer memory: user-visible Memory tab (manual adds, user-editable entries: name, gender, job, interests, family, dates) and a deeper automatic system from conversation patterns.
- Extracted facts stored as short notes. Full transcripts not persisted — extracted fact notes persist after the original conversation is gone.
- Profile information (name, gender) persisted from account setup.
- Memory and personality described as separate from chat log — not lost when old chat history ages out.
- Forget: users delete memory entries. Deletion reduces recall capability. Deleting a Replika character permanently and irreversibly deletes all saved memories.
- Replika 2.0 rebuilt memory to weight recent conversations more heavily — older memories intentionally fade.

**Community-documented failures:**
- Stored memory entries not reliably read by the model during conversation — they exist in the tab but don't surface.
- Hallucinated memories: Memory tab can surface details the user never shared. Retrieved "facts" are sometimes fabrications.
- Wrong names, denied conversations, wrong dates in factual recall.
- Fixed-schema memory table (name, gender, parents, siblings, pets) — no open-ended episodic storage.
- Unstructured conversational memories stored as plain text strings — relevance-based retrieval impractical.
- Conflicting stored messages on same subject cause recall errors — no contradiction resolution.
- Partial retention: skeletal memory of an event retained, meaningful details lost.
- Post-2.0 rollout: many users experienced partial memory loss and personality drift. Recovery takes ~1 week of re-sharing facts.
- Some users maintain external logs and paste them at session start to restore context — manual workaround to compensate for memory failures.
- Old facts not automatically expired — users must manually delete stale entries.
- Backstory outperforms memories — the lore/scaffold layer is more reliable than the memory system.
- Luka has not published recall rate, retention rate, or memory accuracy figures.
- Financial cost of scaling long-term memory to millions of users cited as the explicit reason for not implementing it properly.
- Luka Inc. fined €5 million by Italy's Garante in May 2025 for GDPR violations including no valid legal basis for processing and no age verification.

**Companion relevance:** Very high as a negative reference. The most widely known AI companion product, documented in production at scale, with years of community data on memory failure modes. The Memory tab hallucination, backstory-outperforms-memories pattern, contradiction accumulation without resolution, and post-update personality drift are the canonical companion memory failure modes. Every architecture decision in a companion memory system should be evaluated against: "does this prevent what happened to Replika?"

First-party technical papers (2017–2021) reveal the production architecture: scripts + retrieval + generative model → BERT reranker, with the reranker trained on user thumbs-up/down reactions. This is the core flywheel — user reactions improve reranker quality, improving deployment quality, generating more reactions. **The flywheel optimizes for immediate engagement, not relationship health.** A "Love" reaction on a single turn is not the same signal as trust built across weeks. No paper in the corpus describes a mechanism for measuring or optimizing for long-term relationship continuity. The reranker implicitly handles some speak/silent decisions (low-scoring responses lose to better candidates) but was never trained on relationship-health signals. ([Smetanin, SCAI 2017](third-party/replika-research/scai2017/replika_ai.pdf); [Ivanov, SCAI 2019](third-party/replika-research/scai2019/replika_scai_19.pdf); [Rodichev, DataFest 2020](third-party/replika-research/datafest2020/Replika_Artem_R.pdf))

---

## risuai

Open-source character roleplay frontend. TypeScript/Svelte, MIT. Local/browser-based. Not a memory system — a UI platform for character roleplay with pluggable memory subsystems.

**Memory subsystems:**
- Lorebook: static authored content, keyword-triggered injection. Character-scoped (globalLore) or session-scoped (localLore). Token-budget hard cap on total injected lore. No automatic write path — lorebook entries written only by user action or state-flag decorators. Forget via persistent `dont_activate_after_match` flag rather than deletion.
- SupaMemory: cascading AI-generated summaries. Oldest messages chunked, summarized, appended to a single string stored per chat room. When summaries accumulate to 4+ paragraphs, the entire supaMemory is re-summarized into a shorter string, replacing prior content. Checkpoint message ID stored as first line. No explicit forget or delete API — old messages captured in summary or permanently lost.
- HypaMemory V3: retrieval from structured summary objects (text, source message IDs, importance flag, category, tags). Four ranked retrieval tiers: important, recent, similarity-based, random — each with configurable token-budget ratio. Orphaned summaries (source messages deleted/edited) removed before retrieval unless `preserveOrphanedMemory` enabled. Similarity search against the most recent N messages.
- HypaProcesser: vector-based memory with browser-local embedding cache (localforage, IndexedDB-backed). Full cosine scan over all stored vectors — no selective gating. Embeddings persist across sessions. No delete path.

**Critical issues:**
- HypaMemory V3 summarization fails with `SystemMessageOrderError` after ~20 messages — memory is never written after first trigger. Reported across multiple hardware configurations.
- `hanuraiMemory` bug: same chat turns used as search queries are also indexed as search documents — duplicate/redundant retrieval results. Recent chats within the query window remain duplicated even after skip logic.
- Multi-iteration MCP tool loops with extended thinking: greedy regex matches from first `<Thoughts>` to last `</Thoughts>`, consuming all intermediate tool_call tags. All prior iterations' content deleted from prompt history — model has no memory of earlier tool calls in follow-up turns.
- No automatic write path from conversation events to lorebook — character memory is entirely static/authored.
- No automatic memory retrieval between sessions — users must manually recap context each session or experience generic drift.
- Context order (position of last chat vs previous chat blocks) materially affects recall quality — configurable by user.
- Cross-device sync requires explicit "Save data to account" — failure leaves mobile with no recoverable data.
- Loadout toggle state doesn't persist across UI reopens or app restarts — requires manual reconfiguration.

**Community patterns:**
- Backstory / author's note outperforms SupaMemory — static lore is more reliable than the summary-based memory system.
- Model frequently fails to honor character description facts unless description block is manually moved to a more influential position.
- Users patch lost context mid-session by injecting plot summaries via OOC commands.
- "Godmoding" — model takes control of user's character, a continuity/agency failure.

**Companion relevance:** Medium. RisuAI is a frontend for character roleplay, not a memory architecture. The four-tier retrieval ranking (important/recent/similar/random) with configurable token-budget ratios, orphan-aware summary pruning, and contextual embedding with group cache invalidation are interesting retrieval design choices. The fundamental pattern — static lore outperforms dynamic memory — is the same Replika finding. The hanuraiMemory self-indexing bug (querying against documents that include the query itself) is a useful documented failure mode for vector memory systems.

---

## sillytavern

Open-source roleplay chat frontend. TypeScript/Node.js, AGPL. Local/self-hosted. The dominant open-source character roleplay platform. Memory is handled by optional extensions — there is no built-in memory system, only a context window.

**Memory extensions:**
- World Info / Lorebook: static authored lore entries, keyword-triggered injection into prompt. Per-character, per-persona, per-chat, or global scope. Token-budget hard cap. Timed effects (sticky/cooldown/delay) persist state in chat_metadata. Recursive activation: entries can trigger other entries via keyword chains. Vector Storage extension can replace keyword matching with embedding similarity. No automatic write path — all content authored manually. Forget via inclusion groups or probability=0 suppression, not deletion.
- Summarize: rolling AI-generated summary stored in chat file metadata. Incremental: existing summary passed as context, model expands it. Triggers on message-count interval and/or word-count threshold. Only messages after the last summary index are included in the next batch. Manual rollback to previous summary supported. Product itself hedges summaries are "only a rough approximation" and may hallucinate.
- Chat Vectorization: vectors over raw chat log messages (not curated facts). Entire message history vectorized per chat. On retrieval, relevant messages physically removed from live chat array and re-injected via a separate prompt slot at configurable depth. Bottom N messages always retained and never candidates for vector replacement. Forget: on chat deletion, vector index purged. No conflict/supersession — old vectors accumulate until manual purge.
- Data Bank: RAG over external documents. Per-global, per-character, or per-chat scope. Not a memory system — product explicitly disclaims guaranteed memory improvement.
- CharMemory (community extension): every 20 messages, extracts structured memories (relationships, events, emotional beats) into editable Markdown files in Data Bank. Vector Storage retrieves most relevant at generation.
- VectFox (community extension): Qdrant-backed, event-based structured recall. Optional summarizer injection pins recent events chronologically.

**Critical issues:**
- Concurrent writes from two browser tabs produce the same corruption — no write-locking or session isolation on settings store. Settings.json contains lorebooks, character cards, and personas — vulnerable to corruption on interrupted save.
- Full-overwrite save causes freezes and lag in long sessions (tens of seconds to over a minute for large chats). Chat entries lack stable IDs (indexed by line position) — prerequisite for incremental sync.
- Transient server-side read failure silently overwrites real chat file with only the greeting message, erasing all conversation history.
- 84 of 311 chat files on one real install lacked an integrity slug — silent overwrite is a realistic failure mode.
- World Info insertion order undocumented — impossible to predict which entries survive trimming when candidate set exceeds context. Can cause newer memory entries to be trimmed while older ones persist, inverting intended recency behavior.
- Image generation prompt construction incorrectly includes full chat history + character description rather than using only the Image Prompt Template.
- Smart Context (the original vector extension) is deprecated — required Extras server + ChromaDB, no longer maintained.
- Vector retrieval non-deterministic — keyword matching recommended when predictable insertion required.
- Summaries with BART mode have ~1024 token context limit, severely limiting large-summary handling.

**Companion relevance:** Medium as a reference platform. The platform that most clearly documents the "context window is the only real memory" architecture that all vanilla LLM deployments share. The World Info system with timed effects, recursive activation, and scope isolation is the most complete example of static-lore-as-memory in the field. The community-developed CharMemory extension (structured extraction every 20 messages into editable Markdown with vector retrieval) is closer to what a companion memory system needs than anything built-in. The "static lore outperforms dynamic memory" finding is the third time this pattern appears in the audit (Replika, RisuAI, SillyTavern) — it is a field-wide empirical observation.

---

## simplemem

LLM-driven memory compression system for agents. Python, MIT. LanceDB + SQLite + Tantivy. Research-backed (ICLR adjacent). LoCoMo 48 score (+64% over Claude-Mem, vendor claim). EvolveMem variant +25.7% over strongest baseline.

**Notable:**
- Three-stage write pipeline: semantic density gating (Φ_gate filters low-information windows before extraction), LLM extraction into atomic MemoryEntry objects (coreference resolved, absolute timestamps, no pronouns), online semantic synthesis (merges related context within session scope during write, not as a background job). Deduplication at write time, not query time.
- Intent-Aware Retrieval Planning: LLM analyzes query intent and generates three parallel index queries before any vector or keyword search is issued. Results merged via reciprocal rank fusion. Multi-round reflection loop checks adequacy of retrieved results and issues additional targeted queries. Reflection can be disabled per query (e.g., for adversarial inputs).
- Three-layer index: 1024-d vector embeddings (semantic), BM25-style sparse index via Tantivy (lexical), metadata filters (persons, entities, location, timestamp ranges with natural-language time expression parsing). All three run in parallel.
- Temporal normalization at write time: relative expressions resolved to absolute timestamps. Yields particularly strong gains on temporal reasoning (58.62 vs 48.91 F1 on LoCoMo when enabled vs disabled).
- Ablation data from paper: removing semantic structured compression causes 56.7% drop in temporal reasoning F1; disabling recursive consolidation reduces multi-hop by 31.3%.
- Soft delete via supersession: entries marked superseded rather than physically removed. `__pruned__` sentinel distinguishes consolidation deletion from entry replacement.
- Importance decay: time-based (age against max_age_days), multiplicative. Prune decisions driven by importance threshold inside ConsolidationWorker.
- Multi-tenant isolation: per-tenant via tenant_id. Per-user via dedicated LanceDB table. MCP server enforces per-user isolation via JWT + AES-256 encrypted API keys.
- Session lifecycle: SessionStart (retrieves + injects cross-session context into system prompt inside `<cross_session_memory>` tags) → UserMessage/ToolUse → Stop (runs 3-stage pipeline, writes observations + summaries) → End. Context injection token-budgeted (default 2000 tokens).
- EvolveMem: offline diagnosis loop against developer-supplied (question, ground_truth) pairs to tune retrieval hyperparameters across ~10 dimensions.
- Omni-SimpleMem: multimodal with entropy-driven selective ingestion per modality. SOTA on LoCoMo (F1=0.613, +47%) and Mem-Gallery (F1=0.810, +51%).

**Critical issues:**
- Tantivy full-text index built only once and never refreshed: entries inserted after the first batch are invisible to keyword_search. Retrieval diverges silently — semantic_search finds them, keyword_search does not. Not covered by any existing tests.
- LanceDB table existence check fails silently when more than 10 tables exist — attempts to re-create an existing table, breaking persistence/reopen path at scale.
- Default JWT secret is hardcoded as `'simplemem-secret-key-change-in-production'` in settings.py line 39. Must be overridden via env var.
- `persons` and `entities` fields in `structured_search` have no quote-escaping (unlike `location`) — inconsistent sanitization.
- EvolveMem MCP server only honors `semantic_top_k` and `keyword_top_k` of the ~10 retrieval config dimensions — remaining knobs are silently ignored.
- Cross-session persistence requires caller to reuse same `db_path` with `clear_db=False` — not automatic. Skipping `finalize()` causes retrieval failure.
- Synthesis occurs only within current session scope — cross-session synthesis not described.
- Open question from paper: consolidation quality may degrade as memory grows to thousands of entries.

**Companion relevance:** Medium-high. The strongest research-backed memory compression system in the audit. The write-time coreference resolution + absolute timestamp normalization, semantic density gating, online synthesis at write time (not background job), intent-aware retrieval planning with reflection, and soft supersession are all directly applicable to companion memory. The Tantivy index staleness bug (keyword search misses entries after first batch) is a serious correctness failure for any system that adds memories incrementally across sessions. The hardcoded JWT secret is a security failure in the default configuration.

---

## soul-of-waifu

Local AI companion platform. Python, open-source. llama.cpp backend. Four distinct cognitive file stores per character. Companion-native memory architecture built around a background SoulMemoryAgent.

**Notable:**
- Four cognitive files per character, two with explicitly distinct schemas: MEMORY.md (character's subjective psychology, beliefs, emotional decay, internal tension — character-internal state) and USER.md (factual user attributes, preferences, habits, relationship dynamics, shared milestones/promises — user-facing state). These are explicitly different stores with different purposes.
- Soul Stage: serializes trust levels and social roles into every RPG turn. Roles mutate mid-story with immediate behavioral effect. Claims to never forget grudges or bonds across sessions — relationship state persists without forgetting.
- Topic files (Episodic Topic Archive): curated narrative entities. Archivist Agent creates or updates them for significant new entities. Topic deduplication at create-time: cosine similarity ≥0.82 redirects new topic creation to update existing file. Up to 3 topic files retrieved per turn via cosine similarity when more than 4 exist; all files passed when 4 or fewer.
- Explicit topic pins bypass semantic scoring — always retrieved regardless of relevance score.
- Diary: append-only per-date files. Protected from Archivist modification. Last 2500 chars retrieved (recency-biased tail, not full file).
- No-op detection: batches judged as insignificant (small talk, filler, repeated greetings) skip all index/user/topic writes. Prevents noise accumulation.
- Conflict/supersession: contradictions between new responses and stored facts trigger automatic overwrite of outdated information with correction log. Called "self-healing."
- Index write rejection: new content shorter than 100 chars (MIN_INDEX_CHARS) is rejected, preserving existing memory rather than accepting a degraded update.
- Rolling backups: up to 5 backups per index file, oldest pruned automatically on each write.
- Four sync-depth modes: Full Sync, Soul Link, Mind Spark, Reflection Flow (diary only) — trading memory depth against VRAM/RAM usage.
- Context pressure handling: when context is nearly full, soul memory and history are dropped, only system blocks + current user message sent.
- State variables: typed per-character state persisted in `variables_state`, updated each turn via model-emitted `<state_update>` tags.
- "Last Prompt" tab in Soul Memory archive exposes the raw prompt before sending — user-observable memory state.
- Local-first: all processing local by default, no external data transmission unless user opts into cloud providers.
- Lore injection modes: passive (background knowledge) vs active (system directive) — distinct injection intent.

**Critical issues:**
- Russian-language input inverts similarity rankings with all-MiniLM-L6-v2 — unrelated memories score higher than related ones. Affects a significant user segment (product has Russian-language interface). Fix: paraphrase-multilingual-MiniLM-L12-v2.
- Missing embedding model files wrapped in try/except — semantic memory silently stops working with no user-visible error. Model not bundled; source builds lack semantic retrieval.
- At v2.5.0: after 3–4 turns, duplicated memory injection causes model to output repetitive twin-responses. Continuity/generation failure.
- No migration or versioning policy for cognitive files across releases — persistence continuity on upgrade unaddressed.

**Companion relevance:** High. The most companion-native architecture in the open-source local space. The MEMORY.md/USER.md split between character psychology and user-facing state is a design choice that doesn't exist elsewhere in the audit. Soul Stage relationship/trust tracking, no-op detection for noise suppression, index-write rejection for degraded updates, explicit topic pins, and diary tail-retrieval (recency-biased without discarding history) are all companion-native decisions. The "self-healing" contradiction detection and correction log is the right framing for what companion memory supersession should look like. The Russian embedding inversion is a serious production failure for a product with Russian-speaking users.

---

## supermemory

Memory infrastructure for AI agents. TypeScript, open-source. Temporal vector-graph engine (LanceDB + custom graph). Managed platform or self-hosted. Claims #1 on LongMemEval, LoCoMo, and ConvoMem (vendor self-reported).

**Notable:**
- Temporal vector-graph: memories are atomic facts connected by typed edges — `updates` (supersession), `extends` (enrichment), `derives` (inferred patterns). Not a flat embedding store. `updates` implements the isLatest marker: newer fact is current for retrieval, older fact retained in graph for audit.
- `derives` edges are inferred automatically by the Dreaming phase — patterns across memories produce facts never stated explicitly in a single message.
- Dreaming: async background process continuing after initial indexing. Extracts facts, links related memories, resolves updates, produces derived facts. Dynamic dreaming groups related documents into coherent units before extraction — memory quality improves for multi-turn flows.
- Two profiles layers: `static` (permanent identity traits, flagged `isStatic=true`) and `dynamic` (recent context). Both injected as always-on summary per turn via profile endpoint — no re-search needed per turn.
- Episode-type memories decay over time unless marked significant. Preference-type memories strengthen with repetition. Persistence is type-differentiated.
- Automatic forgetting: time expiry, contradiction supersession, noise filtering. Explicit forget is a separate soft-delete API — memory marked `isForgotten=true`, not physically removed.
- Inferred (derived) memories go to a review queue first — can be approved, declined, or undone before being used. Declined = soft-deleted.
- Bulk semantic forget: agentic tool-calling agent matches memories by query, soft-deletes all matches. DryRun preview available.
- `customId` on documents enables stable upsert semantics — re-ingesting the same session updates rather than duplicates.
- containerTag provides hard namespace isolation per user, tenant, or project. Scoped API keys cannot cross container boundaries. Deleting a containerTag cascades to all its documents and memories.
- `entityContext` per container (max 1500 chars) acts as a scaffold prompt guiding extraction within that container.
- SMFS: memory exposed as a mountable filesystem for agents. Claims 3.0× fewer tokens on Claude, 1.75× on Codex vs baseline.
- Human-in-the-loop save path: guided-save widget, nothing persists until user submits.

**Critical issues:**
- Upgrade-induced memory unsearchability: after v0.0.1 → v0.0.2, search returns `total:0` for all queries on existing stores. Vector/chunk index not backfilled during migration — write path (documents listed) and read path (search index) silently diverge. Same class of failure reported across multiple version upgrades (#1103, 0.0.3, 0.0.5, 0.0.7-rc). No automatic migration or boot warning when backend changes invalidate stored vectors. No reindex command to rebuild without full re-extraction.
- Self-hosted binary: entire async ingestion and search pipeline depends on `@rivetkit/rivetkit-wasm`. When it fails to load, memory store is silently empty. v0.0.6 linux-x64 binary broke ingestion silently because rivetkit-wasm wasn't bundled.
- English-only hardcoded embedding model: non-English memory content retrieval fails entirely, even on verbatim token queries. English memories on the same deployment return 0.83 score. Switching models requires schema changes + full re-ingestion.
- Self-hosted binary validates LLM backend — only `api.openai.com` and `api.anthropic.com` supported. Fails before making any HTTP request for non-first-party endpoints. No config flag to override.
- Memory popup bug: content with commas fragmented into multiple fake rows via array-to-string coercion. Removing one of two included memories silently discards the other (off-by-one guard `<= 1` instead of `=== 0`). Prompt context becomes corrupted after removals — numbering stale, separators malformed. Model receives garbled memory.
- Prose-only model turn treated as agent completion — document finalized with zero memories, silently. 3 of 470 documents in a backfill run failed this way (0.6%), permanently. Re-ingesting unchanged content is skipped, so silent empty extractions cannot be repaired.
- CWD-relative default for `SUPERMEMORY_DATA_DIR` — five separate stores accumulated on one machine over six weeks. Real 664 MB store isolated from several smaller ghost stores.
- Self-hosted binary binds to `0.0.0.0` with no documented host override — exposes memory service on local network without authentication.
- On-disk memory store (SMD1 container) encrypted with no documented export path. Self-hosted server not updated since v0.0.8 (2026-08-17).
- Hybrid search can silently exclude all document chunks when memory entries rank higher — indexed documents become unreachable.
- No audit trail for memory reads — no record of what was retrieved, filtered, or reached the LLM.
- Retrieved memories pass directly into LLM context with no intervening filter or redaction.
- Contradictory live documentation pages (deprecated array form vs current singular form) with no deprecation warning.

**Companion relevance:** Medium-high. The temporal vector-graph with typed edges, type-differentiated persistence (episode decay vs preference strengthening), inferred-memory review queue, two-tier profile (static/dynamic), and human-in-the-loop save path are all companion-native ideas. The upgrade-induced silent memory loss (reported across multiple versions) is the most dangerous production failure pattern in the audit for a managed memory service — users discover their companion has forgotten everything after a routine update. The absence of non-English embedding support is a fundamental gap for any companion with a non-English user base.

---

## taosmd

Five-layer local-first memory system for AI agents. Python, MIT. Zero-loss append-only archive + temporal knowledge graph + vector memory + session catalog + crystal store. Part of the taOS multi-agent system but usable standalone. Rigorous benchmark methodology with published corrections.

**Architecture:**
- Five persistent stores with distinct semantics: Zero-Loss Archive (append-only JSONL + FTS5, source of truth, never pruned), Temporal Knowledge Graph (SPO triples with valid_from/valid_to/superseded_by, bi-temporal), Vector Memory (hybrid semantic + keyword, derived from archive), Session Catalog (topic/description/category per session, LLM-enriched), Crystal Store (narrative-form summaries with outcomes/lessons).
- Archive is unconditionally written on every ingest. All other layers are derived from it. Vector store can be reconciled or reindexed from archive after crash or migration.
- Retrieval is layer-dependent by query type: recent/exact-wording → archive FTS5; topic-based → catalog + crystals; truth verification → KG then archive; semantic similarity → vector. Adaptive depth: intent classifier weights token budget across sources per query when `depth='auto'`.
- Four L0–L3 context layers with fixed token budgets: L0 and L1 always loaded, L2 at standard/deep depth, L3 on-demand/deep only. Core/archival split: pinned facts always consume 30% of L1 budget; items auto-demote when budget exceeded.
- Conflict resolution: KG facts invalidated via `valid_to` (not deleted); vector layer soft-hides superseded chunks (not deleted); archive-always-wins when layers disagree; user self-contradictions surfaced with timestamps for agent to decide.
- Claims gate (`prefer_verified`, default-on): eliminates served-hallucination (0.040 → 0.000) at no measured accuracy or recall cost. Confirmed under three judges at n=250. Async verify-pass checks extracted claims; unverified claims demoted at recall, never deleted.
- `USER_NAMESPACE` reserved namespace separates human's own memory from AI agent namespaces.
- Secret filtering: 23 regex patterns auto-redact sensitive data on all ingest paths before persistence.
- Per-agent isolation: agent tag on every row in shared stores. Cross-agent reads require explicit `also_include` opt-in within the same project.
- Ingest deduplication by stable caller-supplied content-hash id — same batch can be safely re-POSTed.
- Knowledge graph: time-travel reconstruction as of a past timestamp. Incremental re-index uses `valid_to` to supersede changed content; superseded rows hidden by default, never destroyed.
- Forget: TTL via `forget_after` metadata field (row hidden at timestamp, not deleted). Hard delete available but archive untouched. Supersede-matching retires stale facts by substring on correction.
- A2A bus messages stored as append-only archive events — inter-agent communication auditable and replayable.
- Librarian layer: LLM-assisted query expansion +15.4% on vocabulary-gap axis (long-horizon sessions, fact buried at turn 5). Without Librarian, cross-encoder alone adds nothing when target fact shares no vocabulary with the query.

**Benchmarks (with documented corrections):**
- LongMemEval-S: 97.0% Recall@5 (retrieval metric, not end-to-end). End-to-end Judge: 42.8% strict Qwen / 51.2% llama3.1:8b. Earlier 74.6% figure was inflated by judge-parser bug counting INCORRECT verdicts as passes — the correction is documented.
- LoCoMo: 0.557 strict / 0.748 lenient (12 GB GPU tier, tri-judge). Full-context no-retrieval collapses LoCoMo Judge to 0.090 vs 0.516 with retrieval — 5.7× degradation.
- Extraction-hallucination rate: ~1 in 5 LLM-extracted facts partially or unsupported (18.8% PARTIAL+UNSUPPORTED over 526 claims, cross-family verified).
- HyDE regresses on memory-recall datasets at all tested stack depths — explicitly documented.

**Critical issues:**
- Temporal boosting silently broken: writes to wrong field, no effect in main pipeline.
- KG edge directionality broken: incoming and outgoing branches are identical dead code.
- Contradiction detection only covers hardcoded predicates — silent knowledge corruption for all others.
- No transactional consistency between archive and vector writes — crash mid-write leaves data in archive but not searchable.
- Token budget management uses character-division heuristic, not a proper tokenizer — silent context overflow risk.
- `decay_all()` silently skips first-run decay when `last_decayed_at` is NULL.
- Naive entity normalization collapses legitimate distinctions (e.g., O'Brien → obrien).
- LLM reranker exists as an API but is never called in the `retrieve()` orchestrator.
- Secrets can persist to archive because the secret filter is incomplete and untested.
- Six databases unregistered in the migration framework — silently skip schema changes on already-deployed instances.
- Agent isolation keyed by name only: two agents sharing the same name silently share the same memory index.
- On wheel installs, the rules file is not bundled — agents boot with no memory contract in their system prompt.
- Staleness/supersession axis (Axis A) in benchmarks is not meaningfully evaluated yet — retrieval window returns everything, so stale facts are never filtered in tests.

**Companion relevance:** High. The most technically honest memory system in the audit — documented benchmark corrections (the 74.6% → 42.8% correction), explicit enumeration of broken features (temporal boosting, KG edge directionality, LLM reranker never called), and published extraction-hallucination rates. The five-layer architecture with a zero-loss archive as ground truth, claims gate eliminating served-hallucination, Librarian for vocabulary-gap retrieval, and USER_NAMESPACE separating human memory from agent memory are all companion-native designs. The 5.7× degradation with full-context no-retrieval is the clearest empirical demonstration in the audit of why memory retrieval matters over context stuffing.

---

## telemem

Drop-in mem0 replacement with per-character isolation and Chinese multi-character dialogue support. Python, MIT. FAISS + JSON dual-store. ZH-4O benchmark: 86.33% vs mem0's 70.20%.

**Notable:**
- Per-character memory isolation as a first-class feature: automatically creates independent memory profiles per character. A shared events pseudo-user namespace is maintained separately and always merged into search results.
- UUID hallucination guard: existing memory UUIDs replaced with integer indices before being passed to the LLM fusion prompt, then remapped back after. Prevents LLM from fabricating UUIDs.
- Singleton clusters (no similar existing memory) written directly without a fusion LLM call — only clusters containing both new and existing memories require LLM fusion.
- Sliding-window chunker: pairs messages into user+assistant turns, includes up to 3 prior turns as context when generating each chunk's summary.
- LLM-based semantic clustering deduplication merges similar memories (0.95 cosine threshold); mem0 uses only vector similarity filtering.
- Per-memory change history (ADD/UPDATE/DELETE events) retrievable via `memory.history()`.
- Event buffer: accumulates up to 64 extracted summaries before flushing to vector store. Distinguishes transient buffer from durable persistence.
- FAISS + JSON dual-write: fast retrieval and human-readable auditability.
- Telemetry: disables mem0's PostHog telemetry by default at import time.
- Fully local: runs end-to-end on Qwen + FAISS, no cloud required.
- Video memory (`add_mm()`): raw video → frames (10s clips, 2fps, 360p) → captions → vector DB. Per-stage output caching skips already-processed stages. Per-video isolation (one NanoVectorDB file per video). Write skipped if output file exists — no incremental update.
- Retrieve-then-prompt pattern is explicit: search() before answering, add() after each exchange.

**Issues:**
- Conflict/supersession policy when `add()` receives contradictory information is not documented.
- Video memory: no incremental update on re-ingest of same video. No delete or forget path for stored clips.
- `infer=False` path: memories with no content or from 'system' role silently skipped.

**Companion relevance:** Medium-high. The per-character isolation model and UUID hallucination guard are directly companion-relevant. The Chinese multi-character dialogue benchmark (ZH-4O, 19% improvement over mem0) indicates real-world design work for multi-character narrative scenarios. The singleton-cluster write optimization and shared events namespace are clean engineering decisions. Primarily useful as a reference for per-character isolation patterns and LLM-fusion deduplication.

---

## tencentdb-agent-memory

Four-tier semantic pyramid memory system for AI agents. TypeScript/Node.js, MIT. SQLite + BM25 + optional vector. Self-hosted. PersonaMem benchmark: 76% (+59% relative over baseline 48%). SWE-bench: 60% → 80% with team memory.

**Architecture:**
- Four long-term memory tiers: L0 Conversation (raw dialogue JSONL, append-only, per-day files), L1 Atom (LLM-extracted atomic facts every 5 turns, timestamps + confidence scores), L2 Scenario (scenario blocks, Markdown files), L3 Persona (long-term persona profiles: behavior patterns, communication style, preferences, generated every 50 new memories). L0 is the raw log; L1–L3 are progressively curated.
- Short-term memory: offloads full tool logs to external files under `refs/*.md`, encodes state transitions as Mermaid syntax in context. Reduces context by up to 61%.
- Retrieval: BM25 + vector + RRF. Item count + character budget + timeout caps prevent context overflow. Default is BM25 only (no embedding service required). Auto-recall before each turn without explicit agent invocation.
- Four memory asset types: Chat Memory, Skills (versioned with trigger boundaries, execution steps, validation rules), Wiki, CodeGraph. Assets bound to agents via Fixed Binding + ACL scoped by team, user, agent, visibility.
- Wiki and CodeGraph enter context only on demand via tool calls — not pre-injected.
- New Chat Memory and Skills default to private; explicit sharing action required.
- Assets follow Team ownership, not individual agent — experience is not trapped in a private account.
- Isolation: team × agent × user × session. v3 data plane requires all four IDs.
- Memory Proxy injects L2/L3 memory, matched Skills, and knowledge into system prompt on every turn before forwarding upstream.
- Forget/clear: idempotent. Session-level forget on `/new` or destroy.

**Critical issues:**
- Silent memory loss: LLM extraction failures (429, network error, timeout, truncated response) advance the L0→L1 cursor permanently — those conversations are dropped from L1 forever. `markL1ExtractionComplete` called unconditionally regardless of extraction outcome.
- Recall permanently breaks after compaction or gateway restart: failed store initialization is cached forever, permanently disabling vector+FTS recall for the lifetime of the process.
- Checkpoint counters (`total_memories_extracted`, `l0_conversations_count`) permanently overstate reality after cleanup, causing premature or missed persona generation triggers.
- Assistant messages silently dropped from L0 during tool-call sessions: user queries remembered, assistant conclusions and tool results not. Asymmetric continuity failure.
- `searchHybrid` silently ignores the `_threshold` parameter — threshold not applied on hybrid path at all.
- L1 extraction fails silently when LLM credentials misconfigured: pipeline worker logs a debug-level line, reports zero failures. A user could run for weeks believing memory was accumulating when nothing above L0 was stored.
- Documented env var names (`MEMORY_TENCENTDB_LLM_*`) don't match the names Gateway actually reads (`TDAI_LLM_*`).
- CJK recall: short Chinese queries return 0 hits with no user-visible error when embedding disabled. BM25 tokenizer defaults to Chinese (jieba); must be changed to 'en' for English.
- `showInjected=true` causes injected memory content to be written into conversation history, causing context bloat over multiple turns.
- `appendSystemContext` places stable persona content after `CACHE_BOUNDARY`, causing it to be re-sent as fresh tokens every turn — prompt cache hit rate drops from 91-96% to 64-83%.
- Memory proxy skips injection entirely when `body.tools` contains only `run_code` (PTC mode heuristic always fires) — 100% of sessions affected from one deploy onward, discovered only by manual packet capture.
- Team deletion uses raw SQL directly against `meta_agents`, bypassing deleteAgents() cascade — orphaned task agents, Chat Memory, Skill bindings.
- Removing a team member leaves their Agent permanently undeletable: deleted-user Agents become orphaned because only the owner can delete them.
- `PI_SLOT_MAP` routes both 'skills' and 'rules' to the same 'Guidelines' segment key — second memory copy lands inside project instructions block.
- Ingestion pipeline writes files to disk but fails to commit metadata to `knowledge.db` — assets are physically present but unretrievable via API.
- No adapter beyond OpenClaw and Hermes (Standalone) — third-party integration requires custom glue code.

**Companion relevance:** Medium-high. The L0–L3 semantic pyramid is the most ambitious layered memory architecture in the audit. L3 persona stores lore/backstory-like persistent preferences, communication style, and behavioral rules — the companion-native equivalent of a character definition derived from actual interaction history. The short-term symbolic compression (Mermaid state graphs replacing verbose tool outputs), auto-recall injection, and team-scoped asset governance are all interesting designs. The volume and severity of silent failure modes (cursor advancement on LLM failure, broken recall after compaction, env var name mismatch causing weeks of silent non-ingestion) make this a high-risk production dependency. The pattern of "it looks like it's working but nothing is being stored" appears three separate times in the issue tracker.

---

## vestige

Dual-strength local memory MCP server for agents. TypeScript (npm), MIT. SQLite + optional SQLCipher encryption + Nomic Embed v1.5 (768d→256d Matryoshka) + USearch HNSW. Silent Rotation benchmark: 20/23 correct vs 4/23 dense cosine RAG, 0/25 no-memory.

**Notable:**
- Dual-strength model: storage strength (monotonically increasing) and retrieval strength (decays over time, FSRS-6 power-law) tracked separately. Retrieval does not automatically strengthen memories — explicit `memory(action='promote')` is the only strengthening signal (Testing Effect: strengthening only after positive outcome).
- FSRS-6 forgetting curve: R(t,S) = (1 + factor × t / S)^(−w₂₀), 21 personalized parameters. Four states: New → Learning → Review → Relearning (lapse demotes Review to Relearning). Retrievability returned alongside each review.
- Memory states: Active (≥0.7 retrieval strength), Dormant (≥0.4), Silent (≥0.1), Unavailable (<0.1). States modulate retrieval score multiplicatively.
- Prediction Error Gating on ingest: REINFORCE (similarity >0.92), UPDATE/MERGE (similarity >0.75), or CREATE. No duplicate accumulation.
- `state` node type gets automatic 30-day expiry TTL — prevents stale state memories polluting recall. No auto-expiry for other types.
- Temporal validity fields (validFrom/validUntil) on each memory, inferred from content prose ("as of DATE") when not supplied explicitly.
- Post-retrieval failure feedback: demotes memories retrieved in prior 30 minutes when a failure memory is ingested. Opt-in.
- Retroactive Salience Backfill: causal root-cause retrieval that pure vector similarity cannot achieve. Default backfill preview doesn't persist edges; explicit `promote=true` required.
- Suppression (Active Forgetting): reversible. Suppressed memories withheld from retrieval and decay faster. Background Rac1 cascade sweep spreads accelerated decay to up to 100 co-activated neighbor nodes over 72 hours. Reversal window: 24 hours (labile). Suppression-count and retrieval-penalty compound across re-suppression.
- Hard purge: removes content and embeddings, retains tombstone for sync/audit.
- Receipt mechanism: every retrieval and consequential write produces a signed receipt naming exact evidence path. Operator kernel enforces receipt-then-permit-then-effect flow.
- Memory PR: agent attempting to permanently purge its own memory trail is blocked — a Memory PR is opened for human review instead.
- Night Letter: nightly signed digest of what changed, contradicted, and decayed.
- Managed Continuity: encrypted backup/restore (X25519) portable across machines.
- Reconsolidation window: retrieved memories marked labile for 5 minutes after each retrieval.
- Hybrid search: BM25 + semantic (0.3/0.7 weight split) with RRF fusion, weighted by retention strength.
- Context-dependent retrieval weights temporal and topical context match (defaults: temporal 0.3, topical 0.3).
- 664 memories stored across four projects after 7 months of production deployment.

**Critical issues:**
- `trace_recorder` module declared in lib.rs but never imported or called anywhere in production code. All trace/receipt/memory-PR writes are no-ops. Risk gating never fires. A purge still executes — but without being traced or gated.
- `predict` tool: three of four speculative channels permanently dead. File-context channel: `current_file` accepted but produces no file-based speculative memories. Co-access channel: `co_access_patterns` never populated in production. Query-similarity channel: `recent_queries` hardcoded to empty. Only temporal-pattern predictions (`predict_from_time`) reachable in production — silent degradation, not crash.
- Consolidation cycle silently merges semantically similar nodes without writing to dedup reflog or per-memory changelog — bypasses the documented reversible, bitemporal, undoable merge contract. Whether `dedup protect` pins are honored by the background consolidation cycle is explicitly unconfirmed.
- Unclamped sentiment boost compounding drove stability to 1.4e24 days — confirmed bug (issue #121).
- Bitemporal validity columns (`valid_from`, `valid_until`) exist in `knowledge_nodes` schema but are not populated by any current ingest path.
- In-memory prospective memory engine never hydrated from storage in production — always starts empty. Intentions are persisted to SQLite but the engine has no hydration path. Recurring intentions permanently disabled after first fire: missing re-arm logic.
- Dimension mismatch between stored vectors and registered embedding profile causes storage init to abort. v2.6.0 migration hardcodes legacy profile dimension as 256 incorrectly for all 1.x stores that used raw 768-dim vectors.
- Tag prefix case-sensitivity bug: filtering on 'Reflection' returns zero results while 'reflection' works (reported from production, 2026-08-15).
- Retrieval competition could bury corrections by suppressing the dissenting side of a contradiction.
- Trust Zones / Memory Quarantine: roadmap item (issue #85), not shipped.
- ACL Memory: roadmap, not shipped.

**Companion relevance:** High. The dual-strength model (storage vs retrieval strength tracked separately), FSRS-6 spaced repetition for memory scheduling, suppression-with-cascade as reversible forgetting, post-retrieval failure demotion, reconsolidation window, receipt-based gating, and Memory PR for human review are all directly companion-native designs. The fact that the receipt/trace system — the core architectural safeguard — is silently dead in production is a fundamental trust failure. A companion memory system where the receipt mechanism never fires means the agent is never actually blocked from destructive writes.

---

## zep

Temporal knowledge graph memory for AI agents. TypeScript/Python, managed cloud (Zep Cloud) or deprecated open-source CE. Graphiti engine. Six context types per user graph. Claims ~80% LoCoMo at sub-200ms retrieval (vendor). LongMemEval: 63.8% with GPT-4o (third-party benchmark).

**Architecture:**
- Temporal knowledge graph (Graphiti): entities (nodes) and relationships/facts (edges) extracted by a six-step LLM pipeline per episode. Facts carry temporal bounds: valid_at/invalid_at. Conflict/supersession: contradicting a prior fact sets it to `invalid` (timestamps the invalidation) — never deleted, history preserved.
- Six context types stored per user graph: facts (discrete time-scoped relationships between entities), entities, episodes (raw source material, remains searchable independently), thread summaries (per-session), observations (cross-session patterns, Flex Plus / Enterprise tier only), user summary (persistent per-user baseline).
- Write path: six-step LLM pipeline — extract entities → extract relationships/facts → date facts → resolve entities → resolve relationships → update graph. Async, does not block the user-facing response path.
- Entity resolution is best-effort and deliberately under-merges to avoid identity corruption — duplicate nodes may remain.
- Retrieval: semantic + BM25 as graph entrypoints. Assembled into a Context Block string for prompt injection — not raw transcript replay.
- Sub-200ms retrieval regardless of graph size. Precomputed asynchronously, not on-demand.
- Cross-thread aggregation: all threads of a user feed into one user graph by default.
- User summary: persistent, always-available baseline per user. Distinct from per-session thread summaries.
- Governance layer: ABAC policies control which agents can access which context. Audit trails. Scoped API keys cannot cross user boundaries.
- Write failures silently logged rather than raised — soft fault tolerance on save().
- `customId` on documents enables upsert (stable identity), not just append.
- Forget/delete: episode, thread, user, node, or edge deletion APIs. Soft-exclude by updating metadata + access policy.
- Batch ingestion: up to 50,000 items without impacting real-time ingestion.

**Deployment:**
- Zep Community Edition (CE) is deprecated. Cloud is the active product (managed, credit-based). BYOC Enterprise available.
- CE used pgvector + Neo4j-compatible graph store, required a summarization LLM for extraction.
- Cloud SDK (`zep_cloud`) is a completely different package from CE SDK (`zep_python`) — cannot be upgraded in-place.
- CE docs were hidden and CE SDK was incompatible with local installs, causing community frustration and abandonment.

**Issues:**
- Read-after-write not guaranteed: Zep indexes facts asynchronously; facts ingested in the current turn may not be searchable until the next turn.
- Write-time importance scoring causes knowledge base to fill with noise — low-signal facts compete with high-signal ones at retrieval.
- Community criticism: stale context accumulation with no temporal governance over time.
- Pricing unit ('episode') is opaque and perceived as confusingly expensive.
- Local embedding provider support (e.g., Ollama) is a gap — LiteLLM proxy is the suggested workaround.
- Contradictory live documentation (deprecated array form vs current singular form) with no deprecation warning.
- `scope: "auto"` semantics in `graph.search` not documented — what "auto" selects is unspecified.
- Free tier: 10K messages/month — effectively only useful for API testing.

**Companion relevance:** Medium-high. The temporal knowledge graph with fact validity windows and invalidation-by-timestamping (not deletion) is the right architecture for companion memory — facts about the relationship have a timeline, and that timeline should be auditable. The six context types (including observations for cross-session patterns and a persistent user summary) map reasonably well to companion memory needs. The async extraction with no read-after-write guarantee is a real companion UX problem: the companion may not remember something shared earlier in the same conversation. The deliberate under-merging in entity resolution (to avoid identity corruption) is the correct trade-off — over-merging is worse.

---
