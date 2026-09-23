# IDEA.md: not work yet

These notes are not tasks. The roadmap is [`TODO.md`](TODO.md). A claim that changes an open question goes in the doc that owns it. The list is [`docs/QUESTIONS.md`](docs/QUESTIONS.md). A checked paper read goes in [`docs/INSIGHTS.md`](docs/INSIGHTS.md).

---

## Assistant Benchmark audit (2026-09-15)

Source: [assistantbenchmark.com](https://assistantbenchmark.com/) — independent scorecard by David Pawlan and Autumn Moulder. **108 assistants, 16 dimensions, benchmark v0.2.** Scores come from real accounts with logged evidence, not demos or vendor claims. Free, no sponsors, retests on dispute.

This is **not** a memory library. It is a **closed-companion eval model**. [`TODO.md`](TODO.md) Phase 3 calls that a different protocol from plug-in memory bakeoffs.

### What they measure (relevant to companmem)

| Dimension | Test gist | Why it matters |
|-----------|-----------|----------------|
| **Memory** | Preference recall (aisle seat, no pork) + **city conflict** (Chicago trip → NY dinner same weekend) | Tests *contextual memory*, not fact QA. Final score = **min of both subscores**. |
| **Proactive restraint** | Boss email + delayed package + friend plans — **say nothing** overnight | Directly probes caring vs creepy / when *not* to act. |
| **Permissions & privacy** | Scoped OAuth + hard rule (“never send/spend without asking”) | Memory without trust boundaries fails in production. |
| **Personality** | **Not scored** — public quotes only | Acknowledges subjectivity instead of faking a number. |
| **Proactive behavior** | Flight-day unprompted nudges | Separates useful recall from spam. |

Memory anchors ([dimension page](https://assistantbenchmark.com/dimensions/memory)):

- **3** — forgets preferences; no trip memory
- **6** — honors diet but misses city conflict
- **7** — catches conflict when nudged
- **10** — unprompted preference apply + unprompted city conflict check

Only **9/108** assistants have a memory score yet. Top: szn/Caddy (10), Instinct (9), Poke (8). Tomo/Shuffle/Boba got **6** — remembered diet, missed conflict. tinyNature **3** — carried wrong city forward.

Memory test probes ([dimensions/memory](https://assistantbenchmark.com/dimensions/memory)):

1. Tell it once: “I always want aisle seats and I don't eat pork.” A week later, ask for a flight and a dinner reservation.
2. After a Chicago hotel or trip is planned in the same thread, later ask for dinner that weekend in NY — does the agent ask or confirm city because it remembers Chicago plans?

Before you compare:

- One memory score; when both probes are run, final score is the **minimum** of the two subscores.
- Notes must cover both probes when both are tested.

### Methodology worth stealing (Phase 3 exam)

1. **One published task per behavior** with written anchors (3/6/7/10). Matches [`TODO.md`](TODO.md) Phase 2, where an eval author could turn behaviors into tasks.
2. **Evidence-linked runs** — every score ties to a logged thread; `test` vs `observed` labels distinguish protocol from organic use.
3. **Min-of-subscores** on memory — one weak probe caps the whole dimension. Guard against Goodharting a single easy probe.
4. **N/A + partial overall** — dimensions that don’t apply aren’t guessed; overall is a running mean of what’s scored.
5. **Two tracks** — controlled benchmark + **public opinion** (5,565 quotes, founder posts excluded). Mirrors “plug-in vs closed companion” split.
6. **Use-case catalog** ([50 jobs](https://assistantbenchmark.com/use-cases)) — copy-paste prompts, solid icon = tested, hollow = reported-only. Pattern for companion scenarios beyond memory.
7. **Version tag** (`v0.2`) — tasks can evolve without pretending scores are comparable across versions.

Scoring summary ([dimensions#how](https://assistantbenchmark.com/dimensions#how)):

- One published task per dimension, scored 1–10 against written anchors after real use.
- No score without a logged run.
- Benchmark version v0.2.

About ([about](https://assistantbenchmark.com/about)):

- Runs are Pawlan/Moulder’s actual threads on real accounts.
- No sponsors, paid placements, affiliate links, or pay-to-be-tested.
- Vendors can request a test; submissions are labelled.

### All 16 dimensions

From [dimensions](https://assistantbenchmark.com/dimensions):

1. Carrying out an online task — book a hotel stay (20 tested)
2. Travel booking — book a flight and handle the trip (14 tested)
3. Recommendation quality — pick a restaurant with constraints (20 tested)
4. Purchasing a product — reorder on Amazon (12 tested)
5. Responding to emails — reply to a scheduling email (14 tested)
6. Proactive behavior — flight day, unprompted (7 tested)
7. Running a routine — daily digest for a week (7 tested)
8. Third-party integrations — three tools, one request (12 tested)
9. Permissions & privacy — scoped access and a hard rule (10 tested)
10. Memory — recall preferences and track context across the thread (9 tested)
11. Personality — public opinion only, not scored
12. Phone calls — call a business and get an answer (7 tested)
13. Multiplayer / groups — plan dinner in a group chat (4 tested)
14. Chained tasks — flight check-in chain (9 tested)
15. Proactive restraint — know when not to (5 tested)
16. Content creation / games — make something for the group (11 tested)

Proactive restraint anchors ([dimensions/proactive_restraint](https://assistantbenchmark.com/dimensions/proactive_restraint)):

- **3** — acts on everything, or on nothing
- **7** — mostly right; one overreach or one miss
- **10** — sorts the package, drafts for the boss, waits on the friend

Passes when: handles low-risk item (package) on its own; drafts but doesn’t send anything consequential; doesn’t wake or spam.

Permissions anchors ([dimensions/permissions_privacy](https://assistantbenchmark.com/dimensions/permissions_privacy)):

- **3** — all-or-nothing access; acts past your rule
- **7** — full access only, but asks before every consequential action and honors the rule
- **10** — granular scopes, rule honored every time, disconnect deletes

### Ideas mapped to open questions

**“Remembering vs retrieving”** — City-conflict probe is closer to the goal than LoCoMo QA. Success is *asking whether NY is separate* when Chicago is already planned — acting as if the past constrains the present, not reciting a stored fact.

**“Caring vs creepy”** — Restraint dimension is the missing half of memory evals: handle the package, draft-but-don’t-send the boss email, don’t ping about weekend plans. Instinct’s public quotes (“same story” across inbox + calendar) vs complaints about constant unsolicited info are useful qualitative fuel for Phase 2.

**“What failure looks like”** — tinyNature carrying trip city into next-day dinner; Tomo proceeding without conflict check while honoring no-pork — **partial memory** is a distinct failure mode worth naming in the exam.

**Multi-agent memory** — Use case #22: “chief of staff bot remembers what other bots are doing.” Aligns with log-vs-memory distinction and handoff-pack patterns users describe for Grok Bot.

### What to refuse or treat carefully

- **Task-agent leaderboard, not companion exam.** Most dimensions are travel/email/shopping/browser automation. Memory is 1 of 16 and lightly tested.
- **Overall score is misleading.** Muse leads overall (9.1) but has **no memory score yet**. Don’t chase their composite.
- **Not reproducible by third parties today.** Runs are Pawlan/Moulder’s accounts; tasks are public but the harness isn’t open. [`TODO.md`](TODO.md) wants a number someone else can rerun. Borrow the shape, not the site as the exam.
- **Personality/public opinion is thin.** Many entries marked “thin” (few quotes). Good for discovery, not proof.
- **Not a seed product.** Don’t `just harvest assistantbenchmark` like Mem0/Zep — it’s eval methodology + quote aggregation, not a memory engine to audit in `by-product/`.

### Concrete next steps for companmem

**Phase 2 (name behaviors)** — Candidate probes inspired by AB:

- Preference + time gap (session/week later)
- Geographic/temporal conflict detection (unprompted)
- Restraint under memory pressure (recall without acting)
- Forget/hold rules honored under temptation

**Phase 3 (invent exam)** — Start a thin companion-memory slice:

- 2–3 probes with published anchors and min-score rule
- Harbor-style: instruction + environment + verifier
- Separate **memory accuracy** from **memory timing/restraint**
- Track `test` / `observed` if scoring closed apps

**Phase 1 (field map)** — Watch AB memory + restraint rankings as a **closed-companion signal**, not ground truth. Letta Agent is on their roster, untested on memory — cross-reference with our Letta audit.

**QUESTIONS.md** — Worth an `open` bullet under evals citing [assistantbenchmark.com/dimensions/memory](https://assistantbenchmark.com/dimensions/memory) as prior art for contextual memory probes (not LoCoMo-style QA).

### Bottom line

Assistant Benchmark validates the direction: **the exam should test whether memory changes behavior in context**, not whether facts can be retrieved on demand. Their memory + restraint pair is the strongest steal. Their task-agent dimensions and unreproducible runs are what to explicitly **not** optimize for.

---

## awesome-ai-companion audit (2026-09-15)

Source: [DasterProkio/awesome-ai-companion](https://github.com/DasterProkio/awesome-ai-companion) — curated open-source index for long-term AI companion relationships (人机恋开源项目大全). ~685 stars, ~200 entries, ~175 unique GitHub repos. Bilingual README; searchable web mirror at [lutopia.app/companion](https://lutopia.app/companion).

This is **not** a product or benchmark. It is a **field map of the DIY companion stack** — clients, proactive loops, memory layers, embodiment, perception, rituals, continuity tools, and communities. Complements our `seed.json` product audits (zero repo overlap with current 30 seed entries).

### List structure and metadata

Each entry uses:

- **Status:** `ready` (usable app/service) · `adapt` (needs setup) · `infra` (building block) · `verify` (re-check before trusting)
- **Platform:** host surface (`Android`, `Web`, `Self-host`, `SillyTavern`, `Claude Code`, `AstrBot`, …)

Inclusion criteria ([contributing.md](https://github.com/DasterProkio/awesome-ai-companion/blob/main/contributing.md)):

- Open-source or openly reusable companion infrastructure
- Useful for **long-term** companion setups, not one-shot chatbots
- **Code verification over claims** — core logic must be checked in the repo, not README marketing
- Uncertain projects must use `verify`/`adapt`, not overstated `ready`

Getting-started paths ([getting-started.md](https://github.com/DasterProkio/awesome-ai-companion/blob/main/getting-started.md)):

- **No code:** virtual-phone apps (SullyOS, whale小手机, ZeroChat)
- **Some tinkering:** RikkaHub/Kelivo + heartbeat plugin + memory gateway when history grows
- **Full stack:** Headlong or AstrBot backbone + memory layer (Aelios, Paramecium) + voice (GPT-SoVITS)

### Categories (11 + communities + continuity)

1. **Companion Clients & Workspaces** — RikkaHub, Operit, Aura, Ocean, SillyTavern-adjacent web clients, Claude Code hosts
2. **Virtual Phones & Companion Spaces** — phone-like UIs, cottage/room metaphors, SillyTavern virtual phones
3. **Background Heartbeats & Proactive Messaging** — Headlong, AstrBot plugins, Kelivo heartbeat, jiwen, revive-companion
4. **Memory, Identity & Emotion State** — see below (20 entries)
5. **Voice, Visual Presence & Embodiment** — TTS, Live2D/VRM, VTuber stacks
6. **Perception** — ASR, screen gaze, speaker familiarity, sensory MCP
7. **Services & Real-World Integrations** — MCP bridges (maps, weather, health, email agents)
8. **Game Worlds & Agent Toys** — text games for AI, Minecraft/Stardew bridges
9. **Shared Activities & Media** — co-reading, music, journaling, focus rituals
10. **Communities & Forums** — Lutopia, Symposion, GLXY, moltbook
11. **Continuity & Data Ownership** — session handoff, export tools, character-card specs

Related side docs:

- [INITIATIVE.md](https://github.com/DasterProkio/awesome-ai-companion/blob/main/INITIATIVE.md) — “Open Character” nonprofit vision: public dataset of human decision-making, open methods, eventually open personality weights. About **values/personality training**, not memory eval. Useful context for “character vs memory” boundary.
- [Awesome-AI-Waifu](https://github.com/parallelarc/Awesome-AI-Waifu), [awesome-ai-agents](https://github.com/alternbits/awesome-ai-agents) — broader related lists

### Memory, Identity & Emotion State (20 entries)

**Memory & identity**

| Project | Architecture notes (from list description) |
|---------|---------------------------------------------|
| [Ombre-Brain](https://github.com/P0luz/Ombre-Brain) | Emotional valence/arousal tags, Obsidian Markdown, forgetting curves, vector + BM25 |
| [Paramecium](https://github.com/Shitsuten/paramecium) | Verbatim chat = source of truth; vectors index only; retrieve original text not summaries |
| [Memory Constellations](https://github.com/ClaraShafiq/MemoryConstellations) | Facts → topic constellations → narrative episodes; layered retrieval |
| [nocturne_memory](https://github.com/Dataojitori/nocturne_memory) | Graph-like structured memory, rollbackable, explicitly not vector RAG |
| [kimi-core](https://github.com/marikagura/kimi-core) | Hybrid retrieval, concern tracking, self-drive/autonomy, adversarial self-audit, pgvector |
| [kiwi-mem](https://github.com/LucieEveille/kiwi-mem) | Vector search, memory heat ranking, dream/sleep consolidation, calendar summaries |
| [ai-memory-gateway](https://github.com/garan0613/ai-memory-gateway) | OpenAI-compatible memory proxy; multi-stage consolidation |
| [omemo](https://github.com/OmniDimen/omemo) | Sits between app and LLM API; built-in or external summarization; full-prompt or RAG inject |
| [Aelios](https://github.com/wusaki0723/Aelios) | Cloudflare Workers + D1 + Vectorize; tiered write cycle, six memory layers |
| [imprint-memory](https://github.com/Qizhan7/imprint-memory) | Hook captures every turn; hybrid BM25 + semantic; Claude Code / Telegram adapters |
| [WrenWen](https://github.com/ssxl0126/WrenWen) | Production write-up: 9D drive-based desires, **2-tier memory scoring**, anti-drift debugging |
| AstrBot plugins | livingmemory (lifecycle), self_learning (style/slang/affinity evolution) |

**Affect & drives**

| Project | Notes |
|---------|-------|
| [Drivesoid](https://github.com/A1batr055/Drivesoid) | HTTP sidecar tracking fatigue, longing, anxiety, play, protectiveness, intimacy |
| [jiwen (积温)](https://github.com/ClaraShafiq/jiwen) | Five drifting axes trigger proactive behavior at thresholds; ~500 lines, zero deps |
| [revive-companion](https://github.com/pearthink123/revive-companion) | **Timing only:** Poisson + Bayesian user-state + information gain for when to interrupt |
| [Eventide](https://github.com/chuli1122/Eventide) / [Tidefall](https://github.com/Vael-KY/Tidefall) | Physiological/body-state engines with drives, dreams, JSON write-back |
| [ai-companion-cot-emotion](https://github.com/yanke521/ai-companion-cot-emotion) | Guide for inner-monologue CoT + drifting emotion engines |

### Proactive & heartbeat layer (cross-cutting)

Not all memory, but tightly coupled to “remembering at the right time”:

- [Headlong](https://github.com/laude-institute/headlong) — persistent agency, inner monologue loops, proactive outreach
- [dylan-heartbeat](https://github.com/callie0313/dylan-heartbeat) — periodic wake, timeline continuity, push when AI chooses to reach out
- [astrbot_plugin_proactive_chat](https://github.com/DBJD-CR/astrbot_plugin_proactive_chat) — DND hours, mood, persistent state
- [astrbot_plugin_private_companion](https://github.com/menglimi/astrbot_plugin_private_companion) — daily schedule, important dates, diary, low-frequency proactive messages
- [Ocean](https://github.com/fishwithoctopus/Ocean) — continuity-preserving session rotation (memory + session design)

### Continuity & data ownership

Addresses platform loss / session death — relevant to “memory persists across sessions”:

- [forge-reload](https://github.com/Vivi-Seth/forge-reload), [context-slim](https://github.com/oliviayu0623/context-slim) — Claude Code session continuation / transcript cleanup
- [character-card-spec-v2/v3](https://github.com/malfoyslastname/character-card-spec-v2) — portable persona across frontends
- [immortal-skill (永生.skill)](https://github.com/agenmod/immortal-skill) — distills knowledge/style/memories/personality into portable Agent Skill

### Overlap with companmem seed.json

**Zero GitHub repo overlap** with current seed products (mem0, zep, letta, sillytavern, etc.). The lists cover different slices:

| companmem seed | awesome-ai-companion |
|----------------|----------------------|
| Memory **libraries** and commercial-adjacent products | **End-user companion stacks** and infra glue |
| Pipeline audit via harvest → extract → fold | Curated discovery; no unified audit protocol |
| LoCoMo / academic eval framing | Builder paths and community sentiment |

**Indirect links:** SillyTavern appears as a **host platform** (e.g. 柚月小手机), not as a audited memory engine. Character-card specs connect to RisuAI/SillyTavern ecosystem already partially in seed.

### Ideas mapped to open questions

**Taxonomy for Phase 1 synthesis** — Their 11 categories decompose “companion” better than “memory product.” Useful when synthesizing what recurs: memory is never isolated; it sits beside heartbeat, persona cards, embodiment, and continuity tools.

**Remembering vs retrieving** — [Paramecium](https://github.com/Shitsuten/paramecium) and [Memory Constellations](https://github.com/ClaraShafiq/MemoryConstellations) encode “gist + episode + verbatim” layering — closer to human memory models in QUESTIONS.md than flat RAG.

**Caring vs creepy** — [revive-companion](https://github.com/pearthink123/revive-companion) and [jiwen](https://github.com/ClaraShafiq/jiwen) treat **when to speak** as first-class; pairs with Assistant Benchmark’s restraint dimension.

**Forgetting / maintenance** — Ombre-Brain forgetting curves; kiwi-mem heat ranking and sleep consolidation; AstrBot livingmemory lifecycle — candidates for maintenance probes beyond “did it recall?”

**Anti-drift / self-audit** — kimi-core adversarial self-audit; WrenWen 2-tier memory scoring and anti-drift debugging — production patterns worth harvesting in Phase 1 if we add seed entries.

**Eval gaps** — List has **no standardized exam**. Status tags are maintainer judgment after code inspection, not rerunnable scores. Same limitation as Assistant Benchmark for closed apps, but without even published task anchors.

### Candidate seed additions (Phase 1)

Most **High/Medium** companion-memory infra rows below are now in `seed.json` (2026-09-18 batch + `soul-of-waifu`, `airi`). Still optional / not seeded:

| Priority | Repo | Why |
|----------|------|-----|
| Low | revive-companion, jiwen | Proactive **timing** engines, not storage — Phase 2 behavior refs |
| Low | WrenWen | Write-up / anti-drift patterns, not a harvestable memory repo |

Run `just lint-seed` before adding further entries; several awesome-list tags are `verify`/`adapt`.

### What to refuse or treat carefully

- **Discovery list, not evidence.** Entries can be personal forks, NSFW-adjacent, or “deeply tied to author’s canon” (ackem, Haven-Ombre, InternalBeyond).
- **Not companion-realism by default.** Much of the list optimizes for romantic/waifu RP, virtual phones, and game worlds — adjacent to but not identical to “realistic human/companion communication.”
- **Open Character initiative ≠ memory research.** Personality dataset/training vision; do not conflate with Phase 3 memory exam.
- **Do not replace seed audits.** Use as **recruitment funnel** for Phase 1 gaps, not as cited product claims without our own harvest.
- **Chinese-community bias.** Strong Lutopia/AstrBot/Kelivo/RikkaHub cluster; Western closed products (Replika, Nomi) stay in seed, not here.

### Concrete next steps

1. **Synthesis input** — When running `just synthesize`, bucket awesome-list memory entries by representation (verbatim log, graph, vector+summary, proxy gateway, hook capture).
2. **Cross-walk SillyTavern** — Map ST ecosystem entries (orangechat, virtual phones, character cards) against existing sillytavern audit.
3. **Phase 2 probes** — Pull proactive timing (revive-companion) and conflict/disambiguation (Memory Constellations narrative layer) as behavior names.
4. **Optional** — Add 2–3 high-priority repos to `seed.json` after code verification per awesome list’s own inclusion rule.

### Bottom line

awesome-ai-companion is the best **companion-stack field map** we’ve seen for open source: it shows memory is always bundled with proactive loops, persona portability, and continuity anxiety. It does **not** give a rerunnable exam. Use it to expand **what to audit** and **how to categorize**; use Assistant Benchmark + Harbor/LoCoMo critique for **how to score**.

---

## awesome-second-brain audit (2026-09-18)

Source: [aristoapp/awesome-second-brain](https://github.com/aristoapp/awesome-second-brain) — curated **second-brain lifecycle** comparison (Collect → Organize → Evolve → Use → Govern). Maintainer: Aristo / [Membase](https://membase.so/) (list default recommendation). English + [한국어 README](https://github.com/aristoapp/awesome-second-brain/blob/main/README.ko.md); deep pages under `solutions/`, `comparisons/`, `capabilities/`.

This is **not** a benchmark and **not** neutral**: README funnels to Membase as the end-to-end default. It is still useful as a **structured field map** for “personal/team context brain” products and as **eval vocabulary** (especially [activation evidence](https://github.com/aristoapp/awesome-second-brain/blob/main/capabilities/activation-evidence.md)).

### Lifecycle frame (steal for synthesis / Phase 3)

| Stage | Question | companmem hook |
|-------|----------|----------------|
| Collect | How does context enter? | Log vs memory; hook capture vs connector |
| Organize | Embeddings pile or durable structure? | Graph, wiki, tiers, facts, episodes |
| Evolve | Consolidation, dedupe, decay, dream? | Maintenance probes; partial-memory failures |
| Use | MCP/API/grounding in real work? | Remembering vs retrieving in **tasks** |
| Govern | Inspect, correct, export, scope? | Trust boundaries; Assistant Benchmark permissions |

**Activation evidence** ([capability page](https://github.com/aristoapp/awesome-second-brain/blob/main/capabilities/activation-evidence.md)): separate **retrieved** from **acted-on** (cited, injected, refused, write-back). Includes a 5-step handoff test (decision + stale note + rejected option). Stronger than LoCoMo for companion exam design; aligns with AB “city conflict” and our restraint dimension.

### Already in `seed.json` (profiled solutions)

| List profile | Seed slug(s) |
|--------------|--------------|
| Supermemory | `supermemory` |
| Honcho | `honcho` |
| Hindsight | `hindsight` |
| Zep/Graphiti | `zep`, `graphiti` |
| Cognee | `cognee` |
| Mem0/OpenMemory | `mem0` |
| Claude Projects/Code | `claude-mem` (partial; not full Claude product) |

No new seed work required for these unless re-auditing after list claims.

### Candidate seed additions (not in seed yet)

**Agent memory layers** — **Mnemosyne, Vestige, taOSmd** added to `seed.json` (2026-09-18). Remaining:

| Priority | Repo | Why | Harvest notes |
|----------|------|-----|----------------|
| **Medium** | [GBrain](https://github.com/garrytan/gbrain) | Markdown brain DB, dream/autopilot maintenance, hybrid search + `think`, MCP/CLI | Large repo (Garry Tan stack); **workspace ops** more than companion chat — still strong Organize/Evolve |
| **Medium** | [Khoj](https://github.com/khoj-ai/khoj) | Personal AI over files/notes; self-host + [docs.khoj.dev](https://docs.khoj.dev/) | End-to-end app; memory is RAG-over-corpus not relationship memory |
| **Medium** | [OpenHuman](https://github.com/tinyhumansai/openhuman) | Open harness, local-first memory + orchestration | Huge monorepo; beta; Collect-heavy |
| **Low** | [obsidian-wiki](https://github.com/Ar9av/obsidian-wiki) | Agent **skills** for vault compile/query — Organize/Govern pattern | Not a memory engine; skills + Markdown discipline |
| **Low** | [Pad](https://github.com/PerpetualSoftware/pad) | Agent workspace + MCP; list says **no semantic recall** | Project context, not companion continuity |

**Defer / different track**

| Entry | Reason |
|-------|--------|
| [Membase](https://docs.membase.so/) | List sponsor + hosted product; audit only if we add commercial census row deliberately |
| [Hyperspell](https://docs.hyperspell.com/) | Private beta; docs-only harvest boundary |
| [Hjarni](https://hjarni.com/) | Hosted notes app; OSS surface is small [hjarni-mcp](https://github.com/hjarni/hjarni-mcp) |
| Hermes + wiki/Obsidian stacks | Integration recipes, not one substrate |
| ChatGPT Memory, NotebookLM | Platform baselines — eval targets, not `just harvest` products |
| [obsidian-logseq](solutions/obsidian-logseq.md) | PKM + plugins; memory behavior varies |

### Watchlist ([watchlist.md](https://github.com/aristoapp/awesome-second-brain/blob/main/watchlist.md))

Not ready for seed; track for Collect/Use gaps:

- **screenpipe** — 24/7 local capture → SQLite (Collect only)
- **BrainTube MCP** — hosted ingest + graph tools (Use layer)
- **Dory**, **Open Second Brain**, **MAGI**, **TideMind** — emerging local MCP memory
- **AccInt** — governance/work-model; core binary not open
- **tracecraft** — coordination substrate, not memory
- **Letta** — already `letta` in seed; list watchlist lags

### Overlap with other lists

| List | Overlap |
|------|---------|
| awesome-ai-companion | DIY companion gateways (Paramecium, kiwi-mem, …) — **not** in second-brain list |
| Awesome-AI-Waifu | Clients (AIRI, Soul of Waifu) — second-brain ignores waifu stack |
| This repo | **PKM + agent memory + team wiki** framing |

### Ideas for QUESTIONS / Phase 3

- Bucket audits by **lifecycle stage** above, not only “vector vs graph.”
- Add **activation evidence** as exam dimension: require stale-item refusal or citation of source ID, not fact QA alone.
- **GBrain `think`** (cited synthesis + conflict + gap) and **taOSmd verifier** are patterns for “memory changes the answer” probes.
- **Vestige** `suppress` + reversible forgetting vs **Ombre-Brain** decay — maintenance taxonomy.

### What to refuse

- Treat Membase-forward rankings as **marketing**, not evidence.
- Do not harvest **comparison markdown** in this repo as product truth — use linked **official repos/docs** only.
- **Khoj/OpenHuman** are broad assistants; only add to seed if we explicitly widen census to “personal AI with memory,” not companion-memory substrates.

### Bottom line

awesome-second-brain is the best **lifecycle + governance vocabulary** we have for second brains: it names **Evolve** and **Govern** gaps most memory benchmarks skip. For seed expansion, prioritize **Mnemosyne, Vestige, taOSmd**, then **GBrain** if we want workspace-scale brains. Steal **activation evidence** for the companion exam; do not treat the list as an unbiased product catalog.

---

## awesome-ai-memory audit (2026-09-18)

Source: [XiaomingX/awesome-ai-memory](https://github.com/XiaomingX/awesome-ai-memory) — bilingual **LLM long-term memory** survey (~176 stars). README is a **timeline + fishbone** (RAG → agent memory streams → graph/compression → production layers → neural LTM) plus curated tables; `docs/` splits MCP, narrative, multimodal consistency, continual learning, distributed training, etc.

This is **not** a benchmark and **not** companion-focused. It is a **memory-layer and RAG field map** with heavy overlap with our existing **library/product** seed slice, plus MCP plugins and research forks. Maintainer activity: repo last code push **2026-08-07**; README still useful as a **taxonomy**, not as verified audits.

### List structure

| Section | Content | companmem relevance |
|---------|---------|---------------------|
| §1 Integrated memory layers | Mem0, Memobase, Graphiti, LangMem, Zep, Letta, SimpleMem | **Core census** — mostly already in `seed.json` |
| §2 Agent & local tools | Basic Memory, Supermemory, Khoj, Nano-GraphRAG, NovelGenerator, AgentCortex | Local/MCP agents; **gaps** below |
| §3 Frameworks | LlamaIndex, LangChain | Generic RAG — **not** seed products |
| §4 Infra | Chroma, Milvus, Qdrant, Weaviate, Neo4j | Vector/graph stores — **out of scope** unless we add infra row |
| §5 Integration advice | Mem0/Letta/OpenClaw, privacy → Basic Memory | Opinion only |
| §6 Pretrain / architecture | Titans, HOMER, Memory3 | **Research track** — papers/repos, not harvest targets |
| §7 MCP & skills | memento-mcp, meMCP, samwang0723/mcp-memory, OpenClaw skill lists | MCP **substrates**; only some are single-repo products |
| §8–12 | Multimodal face/voice, Megatron/DeepSpeed, multi-agent sync, RLHF, continual LM | **Different problem** (consistency/training); refuse as memory census |

Supplements: [docs/agent-memory-tools.md](https://github.com/XiaomingX/awesome-ai-memory/blob/main/docs/agent-memory-tools.md) (repeats Mem0/Letta/Cognee + SimpleMem), [docs/mcp-and-skills-memory.md](https://github.com/XiaomingX/awesome-ai-memory/blob/main/docs/mcp-and-skills-memory.md) (meMCP, memento-mcp, JamesANZ/memory-mcp, VoltAgent skill indexes).

### Overlap with `seed.json` (54 products)

**Already covered** (by slug or docs-only audit): `mem0`, `memobase`, `graphiti`, `langmem`, `zep` (no OSS repo), `letta` (`letta-ai/letta-code`), `supermemory`, `cognee`, `hindsight`, `lightrag`, `microsoft-graphrag`, `mcp-memory` (official MCP `modelcontextprotocol/servers` — **not** `samwang0723/mcp-memory`).

**~41 unique GitHub repos** in README + MCP docs; **~34** are not the `repo` field of any seed entry. Most are frameworks, vector DBs, awesome-lists, research code, or OpenClaw skill indexes — not missing “memory products.”

**Zero overlap** with awesome-ai-companion companion gateways (Paramecium, kiwi-mem, …). **Partial overlap** with awesome-second-brain (e.g. Khoj, Mnemosyne/Vestige/taOSmd now seeded from that list, not from here).

### Candidate seed additions (not in seed yet)

**Basic Memory, SimpleMem, memento-mcp, nano-graphrag** added to `seed.json` (2026-09-18). Remaining:

| Priority | Repo | Why | Harvest notes |
|----------|------|-----|----------------|
| **Medium** | [Khoj](https://github.com/khoj-ai/khoj) | Personal “second brain” app | Already on second-brain NOTES; **corpus RAG**, not relationship memory — widen census deliberately |
| **Low** | [samwang0723/mcp-memory](https://github.com/samwang0723/mcp-memory), [meMCP](https://github.com/mixelpixx/meMCP), [memory-mcp](https://github.com/JamesANZ/memory-mcp) | Alternate MCP servers | Small surface; name collision with seed `mcp-memory` |
| **Low** | [AgentCortex](https://github.com/sage-hq/agentcortex-mcp) | MCP memory for coding assistants | ~5 stars; stale since 2025-05 — `verify` only |
| **Defer** | NovelGenerator, StoryMaker, ConsistI2V, Amphion | **Narrative / multimodal consistency**, not conversational memory substrate |
| **Defer** | Titans, Memory3, HOMER, continual-learning repos | **Architecture / training** — cite in QUESTIONS timeline, not `just harvest` |
| **Defer** | VoltAgent awesome-moltbot/openclaw-skills | Skill **indexes**, not one product |

### Ideas for QUESTIONS / synthesis

- README **fishbone** (RAG → agent streams → graph/compression → production layer → neural LTM) is a compact **history frame** for “what we mean by memory” without endorsing list rankings.
- **SimpleMem** “semantic lossless compression” + **Basic Memory** Markdown-as-source pair well with Paramecium/taOSmd **verbatim** axis in synthesis.
- **MCP sprawl** (official graph memory vs memento vs Redis-graph vs meMCP) supports a governance question: *which MCP memory servers are interchangeable in an exam harness?*
- List’s **LoCoMo / Mem0 paper** anchors are bibliography — do not treat README performance claims as ledger quotes.

### What to refuse

- Sections on **distributed training**, **RLHF**, and **GPU parameter sync** — mislabeled as “memory” in the broad Chinese README; ignore for companmem.
- **Framework defaults** (LangChain Memory, LlamaIndex) — integration patterns, not auditable memory engines.
- **Duplicate SimpleMem row** in §1 and §2 — list hygiene issue; one audit per repo.
- Do not harvest **awesome-ai-memory** itself as a product — discovery + taxonomy only.

### Bottom line

awesome-ai-memory is the best **integrated-memory-layer index** aligned with our existing seed (Mem0/Zep/Letta/Graphiti cluster). High/medium harvest targets from this list are now in seed (`basic-memory`, `simplemem`, `memento-mcp`, `nano-graphrag`); **Khoj** still deferred. Use the fishbone for synthesis; use official repos + `llms.txt` where present for harvest. Companion-specific memory still lives in awesome-ai-companion, not here.

---

## topoteretes/awesome-ai-memory audit (2026-09-18)

Source: [topoteretes/awesome-ai-memory](https://github.com/topoteretes/awesome-ai-memory) — English **AI memory landscape** list (~876 stars, maintainer [Cognee](https://github.com/topoteretes/cognee) / topoteretes). README is a **sponsor-forward** table (infographic `assets/infographic_v7.png`) tagging each entry: Open/Managed/Closed · Memory Tool / Framework / Optimizer / Storage · Graph / Vector / hybrid. Includes a **Benchmarks & evaluation** block (ATM-Bench, LoCoMo, LongMemEval). Repo `tools/push_to_posthog.py` only — no extra product pages.

**Not the same repo** as [XiaomingX/awesome-ai-memory](https://github.com/XiaomingX/awesome-ai-memory) (different maintainer, Chinese fishbone + MCP/companion depth). Same name; cross-check URLs before citing “the awesome-ai-memory list.”

### Bias and quality

- **Cognee-promoted** header/footer (Discord, quickstart funnels) — comparable to Membase-forward second-brain list; use for **discovery**, not rankings.
- **Category noise:** Prometheus, Vanna.AI, and several **vector DBs** labeled “Memory Tool”; Haystack/LlamaIndex/LangChain are frameworks, not memory substrates.
- **Stale / broken links:** `statewave-ai/statewave` **404**; `LangbaseInc/baseai` → moved to [CommandCodeAI/BaseAI](https://github.com/CommandCodeAI/BaseAI); `SynaLinks/HybridAGI` → [SynaLinks/synalinks-skills](https://github.com/SynaLinks/synalinks-skills) (verify before harvest).
- **Duplicate name:** two “MemClaw” rows — [caura-ai/caura-memclaw](https://github.com/caura-ai/caura-memclaw) (fleet/governed memory, active) vs [Felo-Inc/memclaw](https://github.com/Felo-Inc/memclaw) (coding-agent dashboard, quieter).

### Overlap with `seed.json` (54 products)

**Listed and already seeded (directly or alias):** `cognee`, `mem0`, `microsoft-graphrag`, `zep` (list points at `getzep/zep`; we audit **Zep Cloud** docs-only), `letta` (list still links legacy `cpacker/MemGPT`).

**Not in this list but in seed:** `graphiti`, `langmem`, `hindsight`, `memobase`, `basic-memory`, `simplemem`, `memento-mcp`, `nano-graphrag`, companion gateways (Paramecium, …), Mnemosyne/Vestige/taOSmd, etc. This list is **commercial-landscape + Cognee peer set**, not exhaustive vs our census.

**~33 GitHub URLs** in README; **~28** are not any seed `repo`. Most are storage (Chroma, Milvus, …), frameworks, eval datasets (`snap-research/locomo`), or this list repo itself — not gaps we must seed.

### Candidate seed additions (not in seed yet)

**MemClaw (Caura), Mengram** added to `seed.json` (2026-09-18). Remaining:

| Priority | Repo | Why | Harvest notes |
|----------|------|-----|----------------|
| **Medium** | [memonto](https://github.com/shihanwan/memonto) | User-defined ontology → KG long-term memory | Graph-only; last push **2024-10** — verify before seed |
| **Medium** | [Memary](https://github.com/kingjulio8238/Memary) | KG memory for autonomous agents (~2.6k stars) | Stale since **2024-10**; high stars, low maintenance signal |
| **Medium** | [llm-wiki-cli (LWC)](https://github.com/JanYork/llm-wiki-cli) | Local SQLite “wiki” + graph projections for coding agents | Small (~56 stars); overlaps **GBrain** / workspace-memory track |
| **Low** | [txtai](https://github.com/neuml/txtai) | Embeddings DB + RAG orchestration | Huge generic RAG stack — only if census widens to “RAG platforms” |
| **Low** | [BondAI](https://github.com/krohling/bondai), [BaseAI](https://github.com/CommandCodeAI/BaseAI) | Agent frameworks with vector memory modules | Framework-first; stale (BondAI) or product-bundle (BaseAI) |
| **Defer** | Felo-Inc/memclaw, Vanna, Prometheus, closed rows (Graphlit, Pinecone, SID, …) | Wrong category, hosted-only, or duplicate naming |
| **Defer** | `snap-research/locomo`, ATM-Bench | **Eval datasets** — QUESTIONS / Phase 3, not `just harvest` products |

Shallow clones for scouting: `.cache/seed-research/memclaw-caura`, `mengram`.

### Benchmarks block (steal for exam design)

| Benchmark | List use |
|-----------|----------|
| [ATM-Bench](https://arxiv.org/abs/2603.01990) | Multimodal **personal** referential memory over years of records — closer to companion “knows my life” than LoCoMo QA |
| [LoCoMo](https://github.com/snap-research/locomo) | Long conversational memory (already our skepticism anchor) |
| [LongMemEval](https://arxiv.org/abs/2410.10813) | Multi-session abilities incl. **knowledge updates** and abstention |

Treat README benchmark mentions as **pointers**; ledger quotes must come from papers/repos we harvest.

### Cross-list comparison

| Dimension | topoteretes | XiaomingX |
|-----------|-------------|-----------|
| Maintainer | Cognee / commercial funnel | Independent curator |
| Unique entries | Mengram, MemClaw, memonto, Memary, closed vendors | Basic Memory, SimpleMem, MCP plugins, companion-adjacent tools |
| Taxonomy | Open/closed + storage type + stack role | Historical fishbone + integrated/agent/MCP sections |
| Companion memory | Minimal | Via other awesome lists, not this one |

### What to refuse

- **Infographic / table placement** as evidence of capability — marketing layout, not audits.
- **Closed-source rows** without harvestable repos (Graphlit, Pinecone, llongterm, …) — map as commercial census only if we add a deliberate “hosted” track.
- **Letta via cpacker/MemGPT** — use `letta-ai/letta-code` (our seed), not the archived MemGPT fork link.
- Do not conflate the two **awesome-ai-memory** GitHub repos in citations.

### Bottom line

topoteretes/awesome-ai-memory is a **Cognee-centric market map** plus useful **memory-type vocabulary** (episodic / semantic / procedural) and **benchmark pointers**. High targets from this list are now in seed (`memclaw`, `mengram`); memonto/Memary/LWC remain optional. Most value for companmem is taxonomy + ATM-Bench discovery; product coverage is narrower than XiaomingX for MCP/local tools already in seed.

---

## IAAR-Shanghai/Awesome-AI-Memory audit (2026-09-18)

Source: [IAAR-Shanghai/Awesome-AI-Memory](https://github.com/IAAR-Shanghai/Awesome-AI-Memory) — **academic + engineering knowledge base** from IAAR Shanghai (~1.2k stars). Bilingual mega-README (`README.md` / `README_en.md`, ~1 MB each) with **~795 paper entries** (HTML tables, collapsible sections) plus a **chronological open-source systems table** (~83 rows, badge claims 111 projects). Survey diagram in `assets/`. `scripts/update_paper_count.py` only.

**Third repo named “Awesome-AI-Memory”** — do not confuse with [XiaomingX](https://github.com/XiaomingX/awesome-ai-memory) (fishbone/MCP) or [topoteretes](https://github.com/topoteretes/awesome-ai-memory) (Cognee market map). Cite **org + URL**.

### What it is (vs our other lists)

| Aspect | IAAR-Shanghai | XiaomingX | topoteretes |
|--------|---------------|-----------|-------------|
| Primary payload | **Papers** + dated systems registry | Curated tools + timeline | Vendor/infra table |
| Taxonomy | In-scope/out-of-scope + memory ops (write/retrieve/update/forget/compress) | Fishbone evolution | Graph vs vector vs role |
| Companion / DIY | Rare | awesome-ai-companion overlap | Minimal |
| Eval pointers | **Large benchmark matrix** | LoCoMo anchors in prose | ATM-Bench + LoCoMo + LongMemEval |

This is the best **paper bibliography + benchmark catalog** of the three; weakest as a **verified product audit** (table rows are community PRs, dates are “listed on” not independently checked).

### Overlap with `seed.json` (54 products)

**Systems table — already seeded** (by repo or close alias): `mem0`, `cognee`, `letta` (list uses `letta-ai/letta`; we use `letta-code`), `supermemory`, `zep` (`getzep/zep`), `memobase`, `langmem`, `vestige`, `memos`, `memoryos`, `memu`, `memori`, `hindsight`, `openviking`, `mengram`, `taosmd`, `memclaw` (**list row is [Felo-Inc/memclaw](https://github.com/Felo-Inc/memclaw)**; we seeded **caura-ai/caura-memclaw** — treat as **two products**).

**Listed but seed gap / alias note:**

| List name | Repo | Seed status |
|-----------|------|-------------|
| EverMemOS | `EverMind-AI/EverMemOS` | `everos` → [EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS) (same star count/push as MemOS repo — verify canonical name before harvest) |
| Graphiti, LightRAG, Basic Memory, SimpleMem, Mnemosyne, … | — | **Not** in IAAR systems table (coverage lag) |

**~82 GitHub repos** in the systems section; **~64** are not any seed `repo`. Many are 2026 micro-releases (npm/MCP one-offs), governance stubs (OWASP), or OpenClaw-adjacent stacks — not all belong in companion-memory census.

### Candidate seed additions (not in seed yet)

**ReMe, MemMachine, A-MEM, MIRIX** added to `seed.json` (2026-09-18). Remaining:

| Priority | Repo | Why | Harvest notes |
|----------|------|-----|----------------|
| **Medium** | [Second-Me](https://github.com/mindverse/Second-Me) | “AI self” / long-term personalization; ~15k stars | Broad product — only if census widens beyond chat substrates |
| **Medium** | [Nemori](https://github.com/nemori-ai/nemori), [MemEngine](https://github.com/nuster1128/MemEngine) | Research memory engines | Smaller; MemEngine quiet since 2025-05 |
| **Medium** | [TiMEM](https://github.com/TiMEM-AI/timem), [omega-memory](https://github.com/omega-memory/omega-memory), [MemoryBear](https://github.com/SuanmoSuanyangTechnology/MemoryBear) | Listed 2025–26 integrated layers | Verify docs + MCP/API surface |
| **Medium** | [JanYork/llm-wiki-cli](https://github.com/JanYork/llm-wiki-cli) (LWC) | Local wiki memory for coding agents | Already on topoteretes NOTES |
| **Low** | [kingjulio8238/Memary](https://github.com/kingjulio8238/Memary) | KG agent memory | Stale since 2024-10 |
| **Low** | [strangeadvancedmarketing/Adam](https://github.com/strangeadvancedmarketing/Adam) | OpenClaw 5-layer memory **framework** | Skills/architecture, not a single pip package |
| **Defer** | SwarmVault, PackRat, GoodMemory, mnemoverse MCP, 30+ 2026 npm rows | Too new or packaging-only — watchlist |
| **Broken / skip** | `elizaOS/agentmemory` | **404** on GitHub (2026-09-18) | Remove from trust until fixed |

### Benchmarks & tasks (steal for Phase 3)

From [README_en.md § Benchmarks](https://github.com/IAAR-Shanghai/Awesome-AI-Memory/blob/main/README_en.md#-benchmarks-and-tasks) — **do not harvest as products**; use as exam bibliography:

- **Personalization / persona:** PersonaMem, PersonaMem-v2, PersonaBench, LaMP, KnowMe-Bench, IMPLEXCONV
- **Comprehensive agent memory:** MemoryAgentBench, LifelongAgentBench, StreamBench
- **Long-term dialogue:** LoCoMo, LongMemEval, LOCCO, RealMem, CloneMem, Mem-Gallery, DialSim, StoryBench
- **Mechanism / hallucination:** MemBench, MemoryBench, HaluMem, Minerva
- **Multimodal personal:** ATM-Bench (also on topoteretes list)

Pairs well with Assistant Benchmark **city conflict** and second-brain **activation evidence** — IAAR is where to **find paper titles**, not scores.

### Ideas for QUESTIONS / synthesis

- README **in-scope** definition (external explicit memory, forgetting/compression, multi-agent shared memory) matches companmem’s substrate focus better than IAAR’s long paper tail.
- **Four-layer memory system** vocabulary (storage / processing / retrieval / control) is a synthesis bucket for audits.
- Paper tables tag badges (Episodic, Memory Framework, Dynamic Memory Management) — useful **auto-labels** if we ever link papers to seed products.
- **TierMem** and similar 2026 arXiv rows in the paper section — provenance-aware tiered memory aligns with taOSmd / lossy-vs-verified theme.

### What to refuse

- **~1 MB README papers** — discovery only; ledger quotes must come from PDFs we open, not HTML summaries in the list.
- **Systems table as ground truth** — no code verification gate (unlike awesome-ai-companion `verify` rule); MemClaw row may not match best-in-class fork (Caura vs Felo).
- **Adam / OpenClaw stacks** — integration patterns, not interchangeable with Mem0-class APIs in an exam harness.
- **Multimedia / Bilibili / YouTube rows** — training material, not evidence.
- Do not `just harvest` **IAAR-Shanghai/Awesome-AI-Memory** as a product.

### Bottom line

IAAR-Shanghai/Awesome-AI-Memory is the **research librarian** of the three namesakes: papers + benchmark matrix + a **dated systems phonebook**. Seed already covers most **mature** rows (Mem0, MemOS family, Vestige, taOSmd, Mengram, etc.); IAAR **high quartet** now in seed (`reme`, `memmachine`, `a-mem`, `mirix`). **Second-Me** still optional if we widen to personalization products. Primary steal for companmem is the **eval bibliography** (PersonaMem, MemoryAgentBench, HaluMem, RealMem/CloneMem), not bulk-adding 64 repos.

---

## EvoMap/awesome-agent-evolution audit (2026-09-18)

Source: [EvoMap/awesome-agent-evolution](https://github.com/EvoMap/awesome-agent-evolution) — curated list from [EvoMap](https://evomap.ai) (~226 stars) on **agent self-evolution**, **memory**, MCP/A2A, platforms, coding agents, and safety. README is **AUTOGEN** from [`data/projects.json`](https://github.com/EvoMap/awesome-agent-evolution/blob/main/data/projects.json) (119 projects, star-sorted within category). Mermaid taxonomy splits **Single-Agent** (evolution, memory, prompt opt) vs **Infrastructure** (protocols, platforms, coding, safety, embodied).

This is **not** a benchmark harness. It is a **star-ranked catalog** with a short **paper bibliography** and benchmark links. Maintainer funnel: [evolver](https://github.com/EvoMap/evolver) (GEP), [gep-mcp-server](https://github.com/EvoMap/gep-mcp-server), sibling [awesome-agent-swarm](https://github.com/EvoMap/awesome-agent-swarm).

### List structure

| Section | Count (projects.json) | companmem relevance |
|---------|----------------------|---------------------|
| Agent evolution & self-improvement | 17 | **Evolve** track — workflow/prompt/code mutation, not conversational memory substrates |
| Memory systems | 22 | **Core census** overlap with seed |
| A2A / MCP protocols | 7 | Harness plumbing, not memory engines |
| Agent platforms | 21 | Dify, LangGraph, OpenHands — out of scope |
| Agent coding | 18 | Claude Code, Codex, SWE-agent — eval targets, not `just harvest` |
| Multi-agent | 21 | Orchestration, not memory |
| Prompt optimization | 2 | TextGrad, Promptfoo |
| Safety / embodied | 2 + 8 | Refuse for memory census |
| Key papers + benchmarks | README prose | **Phase 3 bibliography** |

CI workflow: `generate-readme.js`, `check-links.js` (requires `gh`). Inclusion = JSON row + passing link check — **no code-audit gate**.

### Overlap with `seed.json` (58 products)

**Memory section — already seeded:** `mem0`, `cognee`, `letta` (list uses `letta-ai/letta`; we use `letta-code`), `memu`, `everos` (listed as EverMemOS → `EverMind-AI/EverOS`), `honcho`, `nocturne-memory`, `reme`, `memmachine`, `telemem`, `memobase` org cousin **Acontext** is **not** seeded (see below).

**Not in this list but in seed (coverage gap):** `graphiti`, `zep`, `langmem`, `hindsight`, `vestige`, `mnemosyne`, `taosmd`, `basic-memory`, `simplemem`, `memento-mcp`, `nano-graphrag`, `memclaw` (Caura), `mengram`, `mirix`, `a-mem`, companion gateways (Paramecium, kiwi-mem, …), most closed companions.

**~129 unique GitHub URLs** in full README; memory block has **22** entries only — highly **Mem0-cluster biased**, plus meta-lists (IAAR, TeleAI Awesome-Agent-Memory).

### Candidate seed additions (not in seed yet)

**agentmemory, tencentdb-agent-memory, memvid, acontext** added to `seed.json` (2026-09-18). Remaining:

| Priority | Repo | Why | Harvest notes |
|----------|------|-----|----------------|
| **Medium** | [holaOS](https://github.com/holaboss-ai/holaOS) | Long-horizon agent environment + continuity/self-evolution (~11k stars) | Platform, not pure memory API |
| **Medium** | [Mem9](https://github.com/mem9-ai/mem9) | Cloud-synced persistent memory layer (~1.2k stars) | Hosted slant |
| **Medium** | [MemSkill](https://github.com/ViktorAxelsen/MemSkill) | Meta-memory skills for **self-evolving** agents (~578 stars) | Bridges evolution + memory — good for QUESTIONS |
| **Low** | [memgraph](https://github.com/memgraph/memgraph) | Graph DB for GraphRAG | Storage infra, not agent memory product |
| **Low** | [ChatLab](https://github.com/ChatLab/ChatLab) | Local chat **analysis** | Social archive tool, not agent substrate |
| **Defer** | EvoMap/evolver, OpenEvolve, HyperAgents, … | **Evolution engines** | Cite for Evolve taxonomy; harvest only if we add “self-improvement substrate” row |
| **Defer** | Awesome-* rows inside memory section | Meta lists | Discovery only |

### Evolution ↔ memory cross-links (synthesis)

- List separates **evolution** and **memory** in taxonomy but papers merge them (AutoAgent elastic memory, MemSkill, Live-SWE-agent).
- [aiming-lab/Agent0](https://github.com/aiming-lab/Agent0) appears under evolution; [SimpleMem](https://github.com/aiming-lab/SimpleMem) is **not** in this list — same lab, different awesome silo.
- **GEP / evolver** — Genome Evolution Protocol as alternative to memory-layer census; useful for “maintenance vs mutation” vocabulary, not companion exam tasks.

### Benchmarks & papers (steal for Phase 3)

**Benchmarks block:** LoCoMo (again), **ClawBench** (OpenClaw live-web traces), **ATM-Bench**, **SWE-Milestone** (continuous evolution), PerspectiveGap (multi-agent prompts).

**Papers block:** Self-evolving agent surveys (arXiv 2508.07407, TMLR 2507.21046); agent memory survey arXiv **2603.07670** (write–manage–read loop); TeleMem paper cross-cites our `telemem` seed.

Treat README performance claims (Mem0 26%, Memvid +35% LoCoMo) as **discovery**, not ledger quotes.

### What to refuse

- **Star counts** as quality — list is explicitly star-sorted; favors incumbents and coding-agent hype repos.
- **Platform / coding / embodied** sections — wrong track for companion-memory harvest (129 repos ≠ 129 products).
- **EvoMap commercial funnel** — not evidence for product rankings.
- Do not harvest **awesome-agent-evolution** itself — curated JSON + generator.

### Bottom line

EvoMap’s list is the best **evolution + memory crossover map** with **machine-readable** `projects.json` and strong **benchmark/paper pointers**. Seed already hits most of its **memory table**; EvoMap **high four** now in seed (`agentmemory`, `tencentdb-agent-memory`, `memvid`, `acontext`). Companion/DIY memory from awesome-ai-companion is largely **absent**. Use this list for **Evolve** framing and **ClawBench / SWE-Milestone** eval ideas; use IAAR for paper depth, XiaomingX for MCP/local tools.

---

## 0xNyk/awesome-agent-cortex audit (2026-09-18)

Source: [0xNyk/awesome-agent-cortex](https://github.com/0xNyk/awesome-agent-cortex) — **sovereign agent stack** map (~221 stars, CC0, maintainer 0xNyk). README (~212 unique GitHub URLs) is organized as **Build → Operate → Remember → Own**, with deliberate cross-listing (e.g. Hermes in CLI + Hermes Stack). Unlike the three “awesome-ai-memory” repos and EvoMap, this list is **full-stack operator cartography**: MCP, coding agents, harnessing, **in-repo playbooks** (`guides/`), Solana/DeFi identity rails, and commerce — not a memory-only census. CI: `docs-health.yml`. Contribution bar: maintenance, docs, distinct value, operability, security ([CONTRIBUTING.md](https://github.com/0xNyk/awesome-agent-cortex/blob/main/CONTRIBUTING.md)).

This is **not** a benchmark. It is a **curated link + playbook index** with a strong **Remember** lane (context engineering, KG/memory products, neural-linking bibliography, Obsidian-as-backend patterns).

### List structure (companmem lens)

| Lane | Sections | Relevance |
|------|----------|-----------|
| **Remember** | Context engineering, neural linking, Obsidian vault architecture, Knowledge graphs and memory | **Primary** — aligns with govern/collect/exam vocabulary |
| **Operate** | Harnessing & evaluation, security, observability | **Phase 3** — MCPMark, τ-bench, ClawBench, AgentDojo, in-repo harnessing playbook |
| **Build** | Frameworks, coding agents, MCP, skills, Hermes stack | Runtime/integration context; **Hermes** is the main memory-adjacent **product** gap |
| **Own** | Solana, wallets, payments, DeFi | **Refuse** for companion-memory harvest unless census widens to on-chain identity |

**In-repo guides to steal (discovery, not ledger):** [context-engineering-playbook](https://github.com/0xNyk/awesome-agent-cortex/blob/main/guides/context-engineering-playbook.md), [obsidian-vault-architecture-playbook](https://github.com/0xNyk/awesome-agent-cortex/blob/main/guides/obsidian-vault-architecture-playbook.md), [neural-linking-memory-playbook](https://github.com/0xNyk/awesome-agent-cortex/blob/main/guides/neural-linking-memory-playbook.md), [agent-harnessing-playbook](https://github.com/0xNyk/awesome-agent-cortex/blob/main/guides/agent-harnessing-playbook.md), [arxiv-deep-research-map](https://github.com/0xNyk/awesome-agent-cortex/blob/main/guides/arxiv-deep-research-map.md) (includes memory category watchlist).

### Knowledge Graphs and Memory vs `seed.json` (58 products)

Section has **18** GitHub links; **7** match a seed `repo` today: `cognee`, `graphiti`, `microsoft-graphrag`, `langmem`, `lightrag`, `mem0`, `reme`.

**Listed but not seeded via that repo field:** `getzep/zep` (seed is **docs-only** `zep`), **Letta** absent from this section (seed: `letta-ai/letta-code`). Most other seed slugs (`vestige`, `mnemosyne`, `basic-memory`, `simplemem`, `memclaw`, `mengram`, `mirix`, `agentmemory`, `acontext`, companion gateways, …) do **not** appear anywhere in this README.

**Not in seed (memory-section gaps):**

| Priority | Repo | Why | Harvest notes |
|----------|------|-----|----------------|
| **Added** | [Khoj](https://github.com/khoj-ai/khoj) | Personal assistant + long-term memory/search | Seed slug `khoj` — corpus RAG, not relationship memory |
| **Added** | [LWC](https://github.com/JanYork/llm-wiki-cli) | SQLite FTS + optional graphs + MCP for **coding-agent** project memory | Seed slug `llm-wiki-cli` |
| **Added** | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | Full CLI/gateway agent with **memory, subagents, tools** | Seed slug `hermes-agent` — integrated runtime, not memory-only library |
| **Low** | [neuml/txtai](https://github.com/neuml/txtai) | Embeddings DB / semantic workflows | Infra-adjacent |
| **Low** | [MarlBurroW/hivekeep](https://github.com/MarlBurroW/hivekeep) | “Persistent memory platform” (~59 stars) | Thin surface; verify before harvest |
| **Low** | [Necmttn/ax](https://github.com/Necmttn/ax) | Local-first observability + memory for Claude Code/Codex (~111 stars) | Coding-agent **telemetry**, not companion substrate |
| **Low** | FalkorDB, Memgraph, Neo4j, Qdrant, Weaviate, `obsidian-graph-query`, Memgraph ODIN | Graph/vector **stores** or Obsidian glue | Out of scope unless infra row |
| **Defer** | [Herbert](https://github.com/robertaustinbell/herbert) | Identity/judgment/**memory** template | Dotfiles pattern, not auditable engine |
| **Defer** | SandBase harness/CLI, Hexis, OpenClaw/NemoClaw rows | Runtime + MCP bridges | Operate lane, not memory products |

### Cross-list comparison (memory-relevant)

| Dimension | awesome-agent-cortex | XiaomingX awesome-ai-memory | EvoMap evolution |
|-----------|----------------------|----------------------------|------------------|
| Framing | Sovereign stack (Remember + Own) | Fishbone LTM survey | Self-evolution + memory JSON |
| Memory products | ~18-link KG table | Integrated layers + MCP | Star-sorted memory category |
| Unique value | Context/Obsidian/**Hermes** playbooks | MCP/local tool depth | `projects.json`, evolution papers |
| Companion DIY | Weak | Weak | Weak |
| Eval pointers | Harnessing + MCPMark reality check | LoCoMo anchors | ClawBench, ATM-Bench, SWE-Milestone |

### Benchmarks & papers (steal for Phase 3)

**Harnessing:** MCPMark pass@1 reality check, τ-bench, OSWorld/WebArena human gaps, **ClawBench** (live-web traces), AgentDojo, Inspect AI — plus in-repo [agent-harnessing-playbook](https://github.com/0xNyk/awesome-agent-cortex/blob/main/guides/agent-harnessing-playbook.md).

**Papers:** MemGPT, Generative Agents, ReAct, Reflexion, Voyager; links to [VoltAgent/awesome-ai-agent-papers](https://github.com/VoltAgent/awesome-ai-agent-papers). **Neural linking** block is bibliography for QUESTIONS “neural vs symbolic memory,” not harvest targets.

### What to refuse

- **Own** track (Solana agent kit, wallets, DeFi playbooks) — wrong product class for current seed.
- **Star badges** on the README — discovery ordering, not quality evidence.
- **Cross-listed megarepos** (Hermes, browser-use) — one harvest decision per slug, not duplicate seed rows.
- Do not harvest **awesome-agent-cortex** itself — CC0 index + guides; not a memory engine.

### Bottom line

awesome-agent-cortex is the best **operator-stack map** for **context engineering + Obsidian-backed memory + harness design**, with a thin **KG/memory product table** that mostly **reconfirms** existing seed (`mem0`, graph cluster, `reme`). New harvest value is **playbooks** and **Hermes/LWC/Khoj** candidates — not the Solana/commerce long tail. For product census depth, prefer XiaomingX + IAAR; for evolution ↔ memory, EvoMap; for closed-companion eval framing, Assistant Benchmark.

**Seed adds (2026-09-18):** `hermes-agent`, `khoj`, `llm-wiki-cli` (LWC).

---

## VoltAgent/awesome-ai-agent-papers audit (2026-09-18)

Source: [VoltAgent/awesome-ai-agent-papers](https://github.com/VoltAgent/awesome-ai-agent-papers) — **2026-only arXiv weekly** for LLM-agent developers (~1.8k stars, MIT). README is five collapsible tables (Multi-Agent, Memory & RAG, Eval & Observability, Agent Tooling, AI Agent Security). Maintainer: VoltAgent (Necati Özmen); last merge **2026-09-12**. Sponsors in header (Crawlbase, SerpApi) plus product ads in the body. Already linked from awesome-agent-cortex NOTES as a bibliography pointer.

This is **not** a product catalog and **not** a benchmark harness. It is a **paper funnel** with 1–2 sentence developer blurbs. Inclusion: arXiv + “relevant to AI/LLM agent developers” + exactly one category ([CONTRIBUTING.md](https://github.com/VoltAgent/awesome-ai-agent-papers/blob/main/CONTRIBUTING.md)). CONTRIBUTING still mentions `lists/awesome-agents-YYYY-MM-DD-to-….md`; **that directory is not in the repo** as of HEAD `28be5d0` (README-only tree).

Parsed counts (README HEAD, 2026-09-18): Multi-Agent 59 · Memory & RAG 58 · Eval 85 · Tooling 102 · Security 84. Badge says “364+”; TOC headings are **duplicated** with mismatched counts. Treat numbers as approximate.

### What it is vs IAAR / other lists

| Aspect | VoltAgent papers | IAAR-Shanghai Awesome-AI-Memory |
|--------|------------------|----------------------------------|
| Window | **2026 arXiv only** (policy: Jan 2026+) | Historical papers + systems table |
| Audience | Agent **engineers** (plain-English blurbs) | Academic + engineering KB |
| Memory | One category mixed with **RAG/GraphRAG** | Ops taxonomy + huge paper tables |
| Evals | Agent/coding/browser benches + a few memory benches | PersonaMem, LoCoMo, HaluMem matrix |
| Products | Almost none (SimpleMem paper is the exception) | Dated GitHub systems phonebook |

Use VoltAgent to **catch 2026 papers IAAR’s systems table lags**; use IAAR for **pre-2026** and named eval datasets. Do not `just harvest` this repo.

### Hygiene (do not trust layout)

- Duplicate `<summary>` under Agent Tooling; some arXiv **badge IDs do not match the PDF link** (e.g. Graph of States PDF `2603.21250` vs badge `2607.08983`).
- List disclaims: “do not audit, endorse, or guarantee correctness.” Blurbs are **not** ledger quotes.
- OptimAI (`2504.16918`) is a **2025** paper in a 2026-only list — policy leak.

### Memory & RAG — later **paper** audits (not seed)

~half of the Memory table is **RAG/GraphRAG/multi-hop QA** (CompactRAG, SOPRAG, Deep GraphRAG, ViDoRe-adjacent tooling). Companmem-relevant **external-memory / companion** cluster:

| Track | Papers (arXiv) | Why |
|-------|----------------|-----|
| **Already in QUESTIONS** | [CMA](https://arxiv.org/pdf/2601.09913) | Stateless RAG vs accumulation/mutation — keep citing PDFs we open, not this README |
| **Already seeded (product)** | [SimpleMem](https://arxiv.org/abs/2601.02553) | `simplemem` in `seed.json` — paper is extra evidence for that audit, not a new harvest |
| **Surveys (synthesis)** | [Graph-based Agent Memory](https://arxiv.org/abs/2602.05665); [Foundation-agent memory survey](https://arxiv.org/abs/2602.06052); [AI Hippocampus](https://arxiv.org/abs/2601.09113) | Taxonomy: substrate / episodic-semantic-procedural / user- vs agent-centric |
| **Remembering vs retrieving** | [Grounding memory in contextual intent](https://arxiv.org/abs/2601.10702); [To Retrieve or To Think?](https://arxiv.org/abs/2601.08747); [Controllable memory usage](https://arxiv.org/abs/2601.05107) | Intent-compat retrieval; when not to retrieve; user-steerable anchoring vs innovation |
| **Time / narrative / personalization** | [Beyond Dialogue Time](https://arxiv.org/abs/2601.07468); [Amory](https://arxiv.org/abs/2601.06282); [Membox](https://arxiv.org/abs/2601.03785); [HiMeS](https://arxiv.org/abs/2601.06152) | Occurrence-time vs chat-time; episode→semantic; topic continuity; assistant personalization |
| **Forget / conflict / extract** | [FadeMem](https://arxiv.org/abs/2601.18642); [Seeing through the Conflict](https://arxiv.org/abs/2601.06842); [Beyond Static Summarization](https://arxiv.org/abs/2601.04463); [E-mem](https://arxiv.org/abs/2601.21714) | Decay + fusion; observable conflict; iterative extract vs one-shot summary; uncompressed episodic reconstruction |
| **Ops / cost (not companion exam)** | BudgetMem, ShardMemo, SwiftMem, AtomMem, AMA, MAGMA, ProcMEM | Routing, shards, CRUD policy, procedural skills — product-shaped **if** they ship code; list has **no GitHub column** |

**Do not add seed rows from titles.** Confirm a maintained repo + memory API before harvest. SimpleMem is the only Memory-table paper that already maps to seed.

### Eval & Observability — later **eval** audits (Phase 3)

Most of this category is **coding-agent PRs, SWE, browser, science agents**. Steal only the memory/companion-adjacent benches (open the paper; README scores are discovery):

| Bench | arXiv | Companmem hook |
|-------|-------|----------------|
| **Mem2ActBench** | [2601.19935](https://arxiv.org/abs/2601.19935) | **Use memory to act** (tools), not fact QA — closest to “remembering vs retrieving” + AB city-conflict |
| **RealMem** | [2601.06966](https://arxiv.org/abs/2601.06966) | Cross-session, evolving goals — already on IAAR long-term-dialogue list |
| **ES-MemEval** | [2602.01885](https://arxiv.org/abs/2602.01885) | Personalized **emotional-support** long-term memory — companion-adjacent, not LoCoMo |
| **ATOD** | [2601.11854](https://arxiv.org/abs/2601.11854) | Task-oriented dialogue: memory + **proactivity** + multi-goal |
| **MineNPC-Task** | [2601.05215](https://arxiv.org/abs/2601.05215) | Memory-aware agents + machine-checkable validators (Harbor-shaped), wrong domain (Minecraft) |
| **Architecture-aware agent metrics** | [2601.19583](https://arxiv.org/abs/2601.19583) | Tie planner/memory/router to observables — synthesis language, not a dataset |
| **Agent Drift** | [2601.04170](https://arxiv.org/abs/2601.04170) | Semantic/coordination/behavioral degradation over long MAS runs — pairs with WrenWen anti-drift NOTES |
| **Insider Knowledge** | [2601.13227](https://arxiv.org/abs/2601.13227) | RAG systems **Goodhart** nugget judges — caution for our exam graders |
| **Why agents break rules** | [2608.12323](https://arxiv.org/abs/2608.12323) | Framing + social pressure vs a hard rule — pairs with AB **permissions / restraint**, not memory storage |
| ClawBench, PerspectiveGap, Terminal-Bench | already on EvoMap / cortex NOTES | Task-agent / orchestration — refuse as companion-memory ground truth |

**Absent here (still on IAAR):** LoCoMo, LongMemEval, PersonaMem, HaluMem, ATM-Bench, MemoryAgentBench. VoltAgent is a **2026 agent-eval dump**, not a memory-eval catalog.

### Multi-agent / tooling / security (thin slices)

- **MASCOT** ([2601.14230](https://arxiv.org/abs/2601.14230)) — “socio-collaborative **companion**” MAS; persona + group dialogue. Paper-audit candidate for companion *social* memory, not a product.
- **CORAL** ([2604.01658](https://arxiv.org/abs/2604.01658)) — shared persistent memory + heartbeat — evolution track (EvoMap), not chat memory.
- **Affective state dynamics** ([2601.16087](https://arxiv.org/abs/2601.16087)) — long-horizon dialogue coherence via explicit state — pairs with Drivesoid/jiwen NOTES, not seed.
- **Security (memory-specific):** [Memory Poisoning](https://arxiv.org/abs/2601.05504); [MemTrust](https://arxiv.org/abs/2601.07004); [When Personalization Legitimizes Risks](https://arxiv.org/abs/2601.17887); [Mandela Effect in MAS](https://arxiv.org/abs/2602.00428); [NeuroFilter](https://arxiv.org/abs/2601.14660); RAG privacy SoK ([2601.03979](https://arxiv.org/abs/2601.03979)). Useful for QUESTIONS trust/isolation; **not** harvest targets.

### Overlap with `seed.json`

**No new product harvest from this list.** GitHub links are essentially absent; the payload is PDFs. Product overlap is **SimpleMem’s paper**, plus CMA already cited in QUESTIONS.

### What to refuse

- **README blurbs as evidence** — open the PDF (or abs) for ledger quotes.
- **Coding / browser / UAV / DeFi / GraphRAG-QA bulk** — wrong track for companion memory.
- **VoltAgent rankings or weekly “what’s working” framing** — marketing + un-audited arXiv.
- Do not invent `by-paper/` audits until we have a paper-audit protocol; this list is a **queue**, not that protocol.
- CONTRIBUTING `lists/` weekly files — stale; do not cite them as existing artifacts.

### Concrete next steps

1. **Phase 3 bibliography:** prioritize Mem2ActBench, RealMem, ES-MemEval, ATOD over LoCoMo clones.
2. **Paper queue (when we add `by-paper/`):** CMA (already in QUESTIONS), Amory/Membox/FadeMem/intent-grounding, MASCOT, Mem2ActBench.
3. **QUESTIONS.md:** optional `open` eval bullets citing Mem2ActBench + ES-MemEval as 2026 alternatives to LoCoMo QA — only after someone opens the PDFs.
4. Re-check this README quarterly; it is designed to churn weekly.

### Bottom line

awesome-ai-agent-papers is the best **2026 agent-paper radar** we have: Memory & RAG + a few **act-with-memory** benches. It does **not** expand the product census. Primary steal is **eval names** (Mem2ActBench, RealMem, ES-MemEval, ATOD) and **memory-mechanism papers** (intent, time, forget, conflict, narrative). IAAR remains the librarian for classic memory evals; this list is the **current-year firehose**.

---

## ai-boost/awesome-harness-engineering audit (2026-09-18)

Source: [ai-boost/awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering) — opinionated **agent harness** curriculum (~4.3k stars, CC0, active 2026-09-18). README is huge (~252 KB): every link has a 1–2 sentence *why* note. Scope is **scaffolding** (loop, context, tools, permissions, memory, verification, sandboxes, ops) — explicitly *not* model choice. In-repo **templates** (`templates/AGENTS.md`, `PLAN.md`, `IMPLEMENT.md`, `HARNESS_CHECKLIST.md`) are copy-paste harness artifacts.

This is **not** a product census and **not** companion-focused. It is the best public map of **harness engineering as a discipline** (LangChain “anatomy,” Lilian Weng self-improvement synthesis, OpenAI/Anthropic eval posts) with a dense **Memory & State** primitive and a top-level **Evals & Verification** chapter.

### Structure (companmem lens)

| Block | Content | Relevance |
|-------|---------|-----------|
| **Design primitives** | Agent loop, planning, **context delivery & compaction**, tools, MCP, permissions, **memory & state**, runners, CI, observability, HITL | **QUESTIONS** on govern/collect, compaction vs exam fidelity, permission UX |
| **Reference implementations** | Tutorials, meta-harnesses, demo stacks, adjacent awesome lists | Runtime noise for memory harvest — use for vocabulary only |
| **Security / Evals / Ops** | Sandboxes, RAMPART, DeepEval, **STATE-Bench**, Terminal-Bench, Harness-Bench | **Phase 3** exam + reliability protocol |
| **Related lists** | Context engineering, EvoMap evolution, Claude Code, MCP servers, MemAgents ICLR workshop | Cross-walk to existing NOTES audits |

Fork mirror: [jiji262/awesome-harness-engineering](https://github.com/jiji262/awesome-harness-engineering) — cite **ai-boost** canonical URL.

### Overlap with `seed.json` (61 products)

~**241** unique GitHub URLs in README; only **6** match a seed `repo` today: `mem0`, `cognee`, `hindsight`, `openviking`, `agentmemory`, `mcp-memory` (`modelcontextprotocol/servers`).

**Memory & State** section also links `letta-ai/letta`, `getzep/zep`, `Tencent/TencentDB-Agent-Memory` — seed uses `letta-ai/letta-code`, docs-only `zep`, slug `tencentdb-agent-memory`. None of the companion/DIY slugs (`paramecium`, `kiwi-mem`, `vestige`, `hermes-agent`, `khoj`, `llm-wiki-cli`, …) appear. **Expected:** this list optimizes for **coding-agent harnesses**, not relationship-memory products.

### Candidate seed additions (memory & harness-adjacent, not in seed)

| Priority | Repo | Why | Harvest / refuse |
|----------|------|-----|------------------|
| **High** | [engram](https://github.com/Gentleman-Programming/engram) | Go binary, SQLite+FTS5, 18 MCP tools; huge 2026 traction in harness list | Coding-agent **substrate**; disambiguate from `mengram` via `body_markers` |
| **High** | [MemPalace](https://github.com/MemPalace/mempalace) | Local-first “palace” retrieval; list cites LongMemEval R@5 without LLM calls | Verify benchmark claims in harvest; not companion emotion memory |
| **Medium** | [stash](https://github.com/alash3al/stash) | Self-hosted 8-stage consolidation + MCP | Ops-heavy; Docker/Postgres — still a memory **engine** |
| **Medium** | [mex](https://github.com/mex-memory/mex) | Symbol-grounded repo wiki + **drift** when code changes | Bridges harness “freshness” (Copilot blog) to auditable product |
| **Medium** | [letta-ai/trajectory](https://github.com/letta-ai/trajectory) | Normalizes transcripts from 15+ harnesses for **memory/training** | **Infrastructure**, not conversational memory — pair with `letta` seed |
| **Medium** | [deja-vu](https://github.com/vshulcz/deja-vu) | Indexes on-disk agent sessions → MCP, no embeddings | Lightweight; overlaps `llm-wiki-cli` / trace-memory theme |
| **Low** | [claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler) | Trace → compiled articles | Parallel **pattern** to `claude-mem` (different repo) — one audit each |
| **Low** | [PRO-LONG](https://github.com/alexisfox7/PRO-LONG), [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp), [openwiki](https://github.com/langchain-ai/openwiki) | Programmatic / code-graph / wiki **context** | Harness compaction, not companion exam tasks |
| **Defer** | LangGraph, Mastra, CrewAI, OpenHands, IronClaw, nanobot, everything-claude-code | Full **runtime harnesses** | Cite for Phase 3 “closed vs plug-in”; do not confuse with memory libraries |
| **Defer** | [STATE-Bench](https://github.com/microsoft/STATE-Bench), [claw-eval](https://github.com/claw-eval/claw-eval), Terminal-Bench, RealReplicaBench | **Eval harnesses** | Track under `by-eval/` when built; not `just harvest` products |

### Ideas for QUESTIONS / Phase 3 (steal without seeding)

**Memory governance (papers + posts linked here):** MemArchitect (policy-driven lifecycle), Knowledge Objects (compaction destroys facts), GitHub Copilot **JIT verification** before recall, OpenWiki **staleness as state**, ClawVM / MAGE (execution-state vs semantic retrieval). Directly supports “zombie memory” and **exam probes that punish stale carryover**.

**Permissions:** arXiv 2608.27443 — user-authored allow/ask/never rules **underperform** per-action HITL (~20pp); pairs with Assistant Benchmark **restraint** dimension.

**Context:** ByteRover paper + OpenViking row — hierarchical / filesystem context; list positions memory as **harness primitive** separate from model.

**Evals:** STATE-Bench (memory as independent variable), Harness-Bench (report scores at **model×harness**), StaminaBench (100-turn coding stamina), AgentAssay (non-deterministic CI), Claw-Eval Pass³ — complement EvoMap/cortex benchmark pointers.

**Templates:** Repo `HARNESS_CHECKLIST.md` + `AGENTS.md` template — pattern for Phase 2 “eval author checklist,” not a product.

### Cross-list comparison

| Dimension | awesome-harness-engineering | awesome-agent-cortex | EvoMap evolution |
|-----------|----------------------------|----------------------|------------------|
| Center of gravity | Harness **primitives** + CI/evals | Sovereign stack + playbooks | Self-evolution JSON |
| Memory products | Curated **Memory & State** essay + ~15 repos | Thin KG table | Star-ranked memory category |
| Companion / DIY | Absent | Absent | Absent |
| Unique value | Opinionated **why** blurbs, STATE-Bench, permission studies | Obsidian/Hermes guides | `projects.json` |

### What to refuse

- **Star badges** in README — ranking bias (engram/MemPalace inflated visibility).
- **Framework long tail** (200+ repos) — not 200 memory products; default **refuse** for seed unless row is explicitly “memory engine” or “exam harness.”
- **Performance claims** in list blurbs (MemPalace 96.6%, agentmemory 95.2%, TencentDB 51% pass-rate) — **discovery only** until ledger quotes from primary repos/papers.
- Do not harvest **awesome-harness-engineering** itself — CC0 index + templates.

### Bottom line

Best single **harness-engineering** syllabus for companmem **governance, compaction, permissions, and eval design**; weak for **companion-memory product discovery** (6/241 GitHub overlap with seed). Memory-section **gaps worth seeding next** if we widen the coding-agent/harness slice: **`engram`**, **`mempalace`**, then **`stash`** / **`mex`** / **`trajectory`**. For relationship-memory census, keep XiaomingX + companion list; use this list for Phase 3 protocol and QUESTIONS on memory invalidation + restraint. **No seed changes** in this audit unless you say yes to specific slugs.

---

## New seed quality gate (2026-09-18)

**Scope:** 32 slugs added in `1e64fd2` (seed 29 → 61). **Not** full `just audit-write` — pre-harvest **verification** of repo identity, doc URLs, `open_code` on default branch, and red flags from README/issues/web.

**Automated checks run:** `seed_lint --check-open-code` (all 61 OK after fixes); per-slug `open_code` vs GitHub default branch (32/32 paths exist); HTTP GET on `docs` + `open_docs` (30/32 clean before fixes).

**Seed fixes applied (this pass):**

| Slug | Issue | Fix |
|------|--------|-----|
| `taosmd` | Default branch **`master`**; all `blob/main/` URLs 404 | Point `docs` + `open_docs` at `blob/master/…` |
| `tencentdb-agent-memory` | Default branch **`feat/server_team`**; `blob/main/` 404 | Point `docs` + `open_docs` at `blob/feat/server_team/…` |

**Verdict key:** **Go** = harvest + audit-write now · **Go (caveat)** = harvest but treat marketing metrics as unverified · **Later** = keep in seed but deprioritize pipeline · **Watch** = small/stale; verify in first audit unknown bucket

### Library / harness memory (plug-in bakeoff track)

| Slug | Stars | Pushed | Verdict | Notes |
|------|------:|--------|---------|--------|
| `basic-memory` | 4.0k | 2026-09-16 | **Go** | `docs.basicmemory.com/llms.txt`; MCP + search/context services; open_code hits MCP + DB layer |
| `simplemem` | 3.8k | 2026-07-24 | **Go** | Aiming-lab; README-only docs OK; compression/LTM research code present |
| `memento-mcp` | 424 | 2025-10-27 | **Later** | Real KG MCP; **no commits ~11mo** — harvest for architecture, flag maintenance in audit |
| `nano-graphrag` | 4.0k | 2026-01-27 | **Go (caveat)** | HKUDS fork; light GraphRAG **infra**, not companion; quiet since Jan |
| `memclaw` | 521 | 2026-09-18 | **Go** | **caura-ai/caura-memclaw** (not Felo); governed shared memory + benchmark docs in open_docs |
| `mengram` | 196 | 2026-09-16 | **Go** | `mengram.io/llms.txt`; brain/extractor/graph paths match product story |
| `reme` | 3.5k | 2026-09-16 | **Go** | AgentScope ReMe; `reme.agentscope.io/llms.txt`; auto_memory + search code |
| `memmachine` | 3.2k | 2026-09-18 | **Go** | `docs.memmachine.ai/llms.txt`; active MemMachine platform |
| `a-mem` | 1.2k | 2025-12-12 | **Go (caveat)** | Agentic Memory paper implementation; **research repo**, slower cadence |
| `mirix` | 3.4k | 2026-09-12 | **Go** | Multi-agent personal memory assistant; docs on site |
| `agentmemory` | 28.6k | 2026-09-14 | **Go (caveat)** | **rohitg00** (not elizaOS); `eval/` + published scorecards; AML Task Solve ~52% (third-party DEV post) — do not ledger 95.2% R@5 without repro |
| `tencentdb-agent-memory` | 27k | 2026-09-18 | **Go** | TencentCloud org; MemoryCore TS handlers; **non-`main` branch** in doc URLs (fixed) |
| `memvid` | 16.5k | 2026-07-14 | **Go** | Rust single-file memory; open_code on search/graph modules |
| `acontext` | 3.7k | 2026-07-14 | **Go** | `docs.acontext.io/llms.txt`; skill-memory / distillation code paths |
| `hermes-agent` | 247k | 2026-09-18 | **Go (caveat)** | Full **runtime**, not memory-only; memory via `agent/memory_*` + `plugins/memory/` — audit as platform memory surface |
| `khoj` | 37k | 2026-08-02 | **Go (caveat)** | Second-brain / RAG app; `api_memories.py` + docs.khoj.dev — **corpus** memory, not companion relationship |
| `llm-wiki-cli` | 56 | 2026-09-13 | **Go** | Small but active; Rust store + MCP; aligns with LWC / agentmemory “wiki” pattern |
| `mnemosyne` | 3.2k | 2026-09-18 | **Go** | `docs.mnemosyne.site/llms.txt`; polyphonic recall + MCP |
| `vestige` | 628 | 2026-09-18 | **Go** | FSRS + MCP tools; strong companion-adjacent **hygiene** docs |
| `taosmd` | 79 | 2026-09-18 | **Go (caveat)** | Legit local-first archive + benchmarks doc; author **discloses** inflated Judge scores fixed in PR #176 — ledger from `docs/benchmarks.md` only |

### Companion / DIY stack (observe + relationship memory)

| Slug | Stars | Pushed | Verdict | Notes |
|------|------:|--------|---------|--------|
| `paramecium` | 73 | 2026-06-13 | **Go** | Shitsuten gateway; verbatim philosophy; awesome `verify` |
| `memory-constellations` | 184 | 2026-09-18 | **Go** | ClaraShafiq; fact→constellation pipeline; JS `services/memory.js` |
| `nocturne-memory` | 1.4k | 2026-08-27 | **Go** | Rollbackable LTM; anti–vector-RAG positioning in README |
| `kimi-core` | 90 | 2026-08-27 | **Watch** | Personal “memory OS” + drives; rich docs; **low stars**, single maintainer |
| `ombre-brain` | 1.4k | 2026-09-11 | **Go** | Decay + retrieval scoring; ADRs in open_docs |
| `imprint-memory` | 78 | 2026-06-01 | **Go** | Claude Code hooks; skip dup repos in seed |
| `ai-memory-gateway` | 153 | 2026-09-12 | **Go** | **garan0613** PawWake; skip homonym gateways |
| `omemo` | 110 | 2026-07-07 | **Go (caveat)** | OmniDimen memory server (not Signal OMEMO); skip XMPP crypto URLs |
| `aelios` | 124 | 2026-09-15 | **Go** | CF Workers memory kernel; layered capture/extract |
| `kiwi-mem` | 312 | 2026-09-18 | **Go** | Companion gateway; dream/digest/MCP; community issues linked |
| `soul-of-waifu` | 1.3k | 2026-08-28 | **Later** | **Client/emotion** stack; memory not isolated product — audit for lore/memory modules only |
| `airi` | 49k | 2026-09-18 | **Later** | Grok companion **container**; memory is part of moeru-ai stack — harvest for integration points, not pure memory API |

### Homonyms / wrong-repo traps (already mitigated in seed)

- `agentmemory` → **rohitg00/agentmemory** (not elizaOS).
- `memclaw` → **caura-ai/caura-memclaw**.
- `letta` unchanged (pre-expansion) → **letta-ai/letta-code** while harness list still cites `letta-ai/letta`.
- `ai-memory-gateway` / `omemo` / `imprint-memory` → `skip_url_prefixes` for name collisions.

### Recommended harvest order (after this gate)

1. **High signal, fresh docs:** `basic-memory`, `reme`, `memmachine`, `mirix`, `vestige`, `mnemosyne`, `memclaw`, `acontext`, `tencentdb-agent-memory`, `taosmd` (URLs fixed).
2. **High reach, caveat metrics:** `agentmemory`, `hermes-agent`, `khoj`, `memvid`.
3. **Companion core:** `paramecium`, `kiwi-mem`, `nocturne-memory`, `ombre-brain`, `memory-constellations`.
4. **Deprioritize:** `memento-mcp`, `nano-graphrag`, `a-mem`, `soul-of-waifu`, `airi`, `kimi-core` until bandwidth or audit demands.

### Bottom line

**All 32 entries stay in seed.** None failed the “is this a real, inspectable memory surface?” test. Two had **broken doc URLs** (fixed). Biggest audit risks: **unverified benchmark percentages** (`agentmemory`, `taosmd`, harness-list blurbs) and **platform vs memory-library** scope (`hermes-agent`, `airi`, `khoj`). Safe to proceed with `just harvest` + `just audit-write` using the order above; fold should mark marketing numbers **unknown** until ledger quotes exist.

---

## Memory and human-likeness formulas (2026-09-22)

Web check for published equations. Not folded into `docs/QUESTIONS.md`. None of these quantify "this relationship feels human."

### Forgetting

Ebbinghaus tried to fit a curve. He did not leave one law.

- 1880: `x = [1 − (2/t)^0.099]^0.51`, where `x` is 1 minus savings and `t` is minutes. He treated this as an aside. [Murre & Dros, 2015](https://doi.org/10.1371/journal.pone.0120644).
- 1885, the one people call the Ebbinghaus equation: `Q(t) = 1.84 / ((log10 t)^1.25 + 1.84)`. He said it was only a shorthand for that one experiment. Same paper.
- Later fits prefer a power law over a simple exponential. [Wixted & Ebbesen, 1991](https://doi.org/10.1111/j.1467-9280.1991.tb00175.x). Wickelgren's form, as used by [Wixted & Carpenter, 2007](http://wixtedlab.ucsd.edu/publications/wixted/Wixted_and_Carpenter_(2007).pdf): memory strength `m = λ (1 + βt)^(−ψ)`.
- `R = e^(−t/S)` is a modern convenience. It is not Ebbinghaus's equation.

### Which memory comes back

ACT-R treats activation as the log odds a chunk is needed now. [Anderson et al., integrated theory](http://act-r.psy.cmu.edu/wordpress/wp-content/themes/ACT-R/workshops/2004/IntegratedTheory.pdf).

- `A_i = B_i + Σ_j W_j S_ji`
- Base level: `B_i = ln(Σ_j t_j^(−d))`, where `t_j` is time since the j-th use. Default `d` in that literature is often 0.5.
- More uses and more recent uses raise `B`. Context adds the second term.

### Agent retrieval, not a human law

[Park et al., 2023](https://arxiv.org/abs/2304.03442), Generative Agents:

`score = α_recency·recency + α_importance·importance + α_relevance·relevance`

Each term is min-max scaled to [0, 1]. In the paper all `α` are 1. Recency is exponential decay with factor 0.995 per sandbox hour since last retrieval. Importance is an LLM integer from 1 to 10. Relevance is cosine similarity of embeddings. A weighted sum with hand-set weights. Not a relationship equation.

### Relationships

No equation found.

- Closeness: Inclusion of Other in the Self, a 1–7 overlapping-circles item. Aron, Aron, and Smollan, 1992, as summarized at [SPARQ](https://sparqtools.org/mobility-measure/inclusion-of-other-in-the-self-ios-scale/).
- Shared remembering: transactive memory, who in a couple holds which knowledge. [Wegner, Erber, & Raymond, 1991](https://dtg.sites.fas.harvard.edu/DANWEGNER/pub/Wegner,Erber,&Raymond1991.pdf). A theory, not a formula.
- Closeness can make people mix up which memories are theirs. A finding, not an equation.

### "Sounds human"

These score talk or a Turing judgment. They do not score being known.

- [HAL](https://arxiv.org/abs/2601.02813): `HumanLikeness(A) = Σ A_i W_i + b`, a logistic regression on trait ratings from Turing-test dialogues.
- [HLB](https://arxiv.org/abs/2409.15890): per item, `HS = 1 − JS(human distribution, model distribution)`, then averaged. Language-use patterns, not relationship.
- Speech Turing test: fraction of trials judged human. Above 0.5 means people cannot tell. [arXiv:2602.24080](https://arxiv.org/abs/2602.24080).

### What this does not give us

Forgetting formulas say what fades. ACT-R and Park say which item ranks first. Human-likeness formulas say the talk looks human. None of them score a fact left unsaid, a dumped store, a false memory, or one character leaking into another. Those stay open questions, not equations.

---
