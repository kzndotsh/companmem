# Roleplay clients and closed companion apps

Slice D. Census only. Cards in `research/census/cards/`.

throughput checkpoint: n/a, read-only investigation

This slice answers how people actually talk to a companion for months. The three injection modes that show up everywhere are keyword lore, vector chat recall, and pinned backstory. None of the ten players expose a typed relationship-state object.

aicompanionpick.com was not used as a spec.

## Overview

Open-source roleplay clients assemble a prompt. They do not run a memory engine with kinds. Character card fields and persona text sit in the prompt every turn. World Info / memory books / lorebooks inject extra strings when keywords (or embeddings) match recent chat. Vector storage shuffles similar old messages back in. A summarize extension compresses dropped history into one more string. Token budgets cap how much of that extra text is allowed.

Closed apps (Kindroid, Nomi, Character.AI, Replika) document similar slots with friendlier names. Their engines are closed. Internals are INCONCLUSIVE.

The shared premise (retrieve the right past text and the model will act as if it remembers) is assumed by every keyword and vector path. Official ST vector docs deny a memory guarantee. Character.AI says the same about written chat memories.

## Key concepts

**Pinned backstory.** Always-on prompt text. ST character card plus persona plus Author's Note. Agnai persona/scenario. RisuAI character fields and `personaPrompt`. Kindroid Backstory and Key Memories. Nomi Shared Notes. Character.AI Chat Memories (400 characters) and Story Memory. Replika profile plus Memory-tab facts the product claims to keep. measured from the primary docs and source listed on each card.

**Keyword lore.** Scan the last N messages for keys. Inject entry content until a token budget fills. ST `checkWorldInfo` in `public/scripts/world-info.js`. Agnai `buildMemoryPrompt` in `common/memory.ts`. RisuAI `loadLoreBookV3Prompt` in `src/ts/process/lorebook.svelte.ts`. Kindroid journals (max 3 individual plus 3 global per user message, up to 8 keyphrases). measured.

**Vector chat recall.** Embed recent messages. Pull similar old chunks. ST `rearrangeChat` defaults. query 2, insert 3, protect last 5, score_threshold 0.25. RisuAI `HypaProcesser.similaritySearch` takes top 3 as "past events". Agnai has `ChatEmbed` / `UserEmbed` types. Closed LTM internals INCONCLUSIVE. measured for open source. guess for closed LTM algorithms.

**Rolling summary.** ST Summarize writes `extra.memory` on a chat message and injects `[Summary: {{summary}}]`. RisuAI `supaMemory` summarizes overflow when `currentTokens > maxContextTokens`. Lossy. measured.

**Typed relationship state.** Absent on every player in this slice. measured for open source (no such type in the files named). inferred for closed (no public schema).

## How it works

### Open-source prompt path

1. Always-on card, persona, and note text are copied into the request. measured.
2. Keyword lore scans a depth window and spends a budget. ST default `world_info_budget` is 25 percent of maxContext, optional cap. Agnai defaults `memoryDepth` 50 and `memoryContextLimit` 500 tokens. RisuAI uses `loreSettings.tokenBudget` or `db.loreBookToken`. measured.
3. If vectors are on, similar past chat or files occupy more of the window before remaining history is packed. measured.
4. If summarize/supa is on, a second LLM (or BART) call writes a blob that is then always-on. measured.
5. The chat LLM sees a pile of strings. Nothing in these clients marks "this is user bio" vs "this is what we agreed last month" vs "this is a joke". measured.

ST World Info can stay silent. Scan Depth 0 plus no constants means no keyword hits. Vectors can retrieve nothing under the score threshold. Summarize can be paused and cleared. measured.

### Closed apps

Kindroid publishes persistent vs cascaded vs retrievable, journal keyphrase caps, chat break (short-term reset, LTM kept), and a tier matrix of character budgets. measured from help snippets. How consolidation works is INCONCLUSIVE.

Nomi publishes Shared Notes, STM/MTM/LTM, Identity Core, and Mind Map 2.0. Official post. Mind Maps form after about 500 messages and are editable. measured. The Nomipedia FAQ quotes the CEO. Memory is topical, not temporal. measured as vendor wiki text. Internals INCONCLUSIVE.

Character.AI pins up to 5 messages (more on c.ai+), auto Facts with persona/character/side tabs, 400-character Chat Memories, copy Facts to a new chat. measured from official blog and help. Internals INCONCLUSIVE.

Replika shows a Memory tab, allows add/delete, and limits visible chat history to four months while claiming retained training. measured from help. Internals INCONCLUSIVE.

## Where things live

| id | primary code or docs |
| --- | --- |
| sillytavern | https://github.com/SillyTavern/SillyTavern (AGPL-3.0, 33251 stars on 2026-09-11) |
| st-worldinfo | `public/scripts/world-info.js` `checkWorldInfo`, `getWorldInfoPrompt`, `WorldInfoTimedEffects` |
| st-vectors | `public/scripts/extensions/vectors/index.js` `rearrangeChat`, `activateWorldInfo` |
| st-summarize | `public/scripts/extensions/memory/index.js` `setMemoryContext`, `summarizeChat` |
| agnai | `common/memory.ts` `buildMemoryPrompt`; `common/types/memory.ts` |
| risuai | `src/ts/process/lorebook.svelte.ts`, `memory/supaMemory.ts`, `memory/hypamemory.ts` |
| kindroid | https://kindroid.ai/v2/docs/memory and sibling help pages |
| nomi | https://nomi.ai Nomi 101 and Mind Map 2.0 posts |
| characterai | https://blog.character.ai/memory/ |
| replika | https://help.replika.com/hc/en-us/articles/37208679176077-How-does-Replika-s-memory-work |

JSON records. `research/census/cards/<id>.json`.

## Gotchas

ST vector docs state that the extension does not guarantee better memory. measured.

ST vectorization breaks prompt caching because the prefix changes. measured.

Agnai `buildMemoryPrompt` does not implement stored V2 fields `recursiveScanning` and `constant`. Comments say they are carried so imports are not destroyed. measured.

Agnai logged-in keyword scan only sees messages loaded in the browser. Default server send is 100. Depth above 100 surprises people. measured.

RisuAI recursive lore is on by default. Entry content can activate more lore until the token budget fills. measured.

RisuAI in-process MCP (`RisuAccessClient`) can list and set module lorebooks after a user access prompt. That is a write path, not a memory ontology. measured.

Closed LTM extractors can store jokes as facts. No public silence type. guess, consistent with the retrieve-equals-remember premise.

Kindroid journals match user messages only, not the model's. measured.

Replika chat UI is not infinite. Four months. measured.

No player in this slice publishes a companion-memory eval. measured.

## Verdicts

| id | companion_fit | reason |
| --- | --- | --- |
| sillytavern | PARTIAL | Local prompt control and keyword lore. No typed relationship. Retrieve equals remember. |
| st-worldinfo | PARTIAL | Best keyword lorebook in the slice. Budgeted. Still untyped strings. |
| st-vectors | MISFIT | Official docs deny a memory guarantee. Similarity shuffle is not a companion. |
| st-summarize | PARTIAL | User-editable rolling summary. Lossy. One blob. |
| agnai | PARTIAL | Keyword books with a 500-token default cap. V2 flags unused. No relationship type. |
| risuai | PARTIAL | Lore plus supa/hypa overflow. MCP can edit lore. Still untyped. |
| kindroid | PARTIAL | Companion UX, journals, claimed infinite LTM. Internals INCONCLUSIVE. No public relationship type. |
| nomi | PARTIAL | Shared Notes plus Mind Maps. Internals INCONCLUSIVE. No public relationship type. |
| characterai | PARTIAL | Pins and Facts. Vendor does not guarantee use. Internals INCONCLUSIVE. |
| replika | PARTIAL | Visible facts, opaque layers, 4-month chat UI. Internals INCONCLUSIVE. |

FIT would need typed kinds, supersession, silence, and a poison story. Nobody here has that in public.
