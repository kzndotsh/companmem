# Notes

Scratchpad for research findings not yet folded into `docs/QUESTIONS.md` or audits.

---

## Assistant Benchmark audit (2026-09-15)

Source: [assistantbenchmark.com](https://assistantbenchmark.com/) — independent scorecard by David Pawlan and Autumn Moulder. **108 assistants, 16 dimensions, benchmark v0.2.** Scores come from real accounts with logged evidence, not demos or vendor claims. Free, no sponsors, retests on dispute.

This is **not** a memory library. It is a **closed-companion eval model** — the track ROADMAP Phase 3 calls a different protocol from plug-in memory bakeoffs.

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

1. **One published task per behavior** with written anchors (3/6/7/10) — matches ROADMAP Phase 2 “eval author could turn behaviors into tasks.”
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
- **Not reproducible by third parties today.** Runs are Pawlan/Moulder’s accounts; tasks are public but the harness isn’t open. ROADMAP wants “someone else can rerun” — borrow the *shape*, not the site as the exam.
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

### Candidate seed additions (Phase 1, not committed)

If expanding beyond memory libraries toward **companion-native memory infra**:

| Priority | Repo | Why |
|----------|------|-----|
| High | Paramecium | Verbatim-log philosophy; direct contrast to summary-first stores |
| High | Memory Constellations | Fact → constellation → episode pipeline |
| High | nocturne_memory | Structured/rollback memory; explicit anti–vector-RAG positioning |
| Medium | kimi-core, Ombre-Brain | Hybrid retrieval + drives/affect + maintenance |
| Medium | imprint-memory | Hook-based capture pattern (Claude Code ecosystem) |
| Low | revive-companion, jiwen | Proactive **timing** engines, not storage — Phase 2 behavior refs |

Run `just lint-seed` before adding; several are `verify`/`adapt` in the awesome list.

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
