# Required player list

Star counts and update times below were observed on GitHub search on 2026-09-11. Treat them as a snapshot, not a ranking.

Workers may add extras under `research/census/discoveries.md`. They must still finish every required id in their slice.

## Slice A. Infra big three

Assigned file. `research/census/infra-big3.md`

| id | name | repo | docs |
| --- | --- | --- | --- |
| mem0 | Mem0 | https://github.com/mem0ai/mem0 | https://docs.mem0.ai/llms.txt |
| graphiti | Graphiti | https://github.com/getzep/graphiti | https://help.getzep.com/graphiti |
| zep | Zep Cloud | closed core on Graphiti | https://help.getzep.com/llms.txt |
| letta | Letta | https://github.com/letta-ai/letta | https://docs.letta.com/llms.txt |

mem0 stars observed 65121. graphiti 30809. letta 24699.

## Slice B. Graphs, memory OS, and RAG memory

Assigned file. `research/census/graphs-and-os.md`

| id | name | repo |
| --- | --- | --- |
| cognee | Cognee | https://github.com/topoteretes/cognee |
| memos | MemOS | https://github.com/MemTensor/MemOS |
| memoryos | MemoryOS | https://github.com/BAI-LAB/MemoryOS |
| supermemory | SuperMemory | https://github.com/supermemoryai/supermemory |
| openviking | OpenViking | https://github.com/volcengine/OpenViking |
| memori | Memori | https://github.com/MemoriLabs/Memori |
| memu | memU | https://github.com/NevaMind-AI/memU |
| everos | EverOS | https://github.com/EverMind-AI/EverOS |

cognee stars observed 30643. supermemory 29626. openviking 36658. memos 11286.

Also card `lightrag` and `microsoft-graphrag` if you can find the canonical repos. They are graph-RAG, not companion memory. Still score them. They are what people cargo-cult into roleplay.

## Slice C. Companion-native and academic

Assigned file. `research/census/companion-native.md`

| id | name | repo or paper |
| --- | --- | --- |
| honcho | Honcho | https://github.com/plastic-labs/honcho |
| memorybank | MemoryBank / SiliconFriend | paper plus any public code |
| generative-agents | Generative Agents | Park et al. plus code if public |
| telemem | TeleMem | https://github.com/TeleAI-UAGI/telemem |
| honcho-sillytavern | Honcho SillyTavern guide | https://honcho.dev/docs/v3/guides/integrations/sillytavern.md |

Honcho docs index. https://docs.honcho.dev/llms.txt
Honcho stars observed 7114. License is often AGPL. Confirm from the repo.

## Slice D. Roleplay clients and closed companion apps

Assigned file. `research/census/roleplay-clients.md`

| id | name | notes |
| --- | --- | --- |
| sillytavern | SillyTavern | https://github.com/SillyTavern/SillyTavern |
| st-worldinfo | SillyTavern World Info | https://docs.sillytavern.app/usage/worldinfo.md |
| st-vectors | SillyTavern Vector Storage | extension in the ST repo |
| st-summarize | SillyTavern memory/summarize extension | extension in the ST repo |
| agnai | Agnai | public repo if still alive |
| risuai | RisuAI | public repo if still alive |
| kindroid | Kindroid | closed. official docs only |
| nomi | Nomi.ai | closed. official docs only |
| characterai | Character.AI | closed. official docs or papers only |
| replika | Replika | closed |

Do not treat aicompanionpick.com as a spec.

## Slice E. MCP, LangMem, Memobase, Hindsight

Assigned file. `research/census/mcp-and-new-vendors.md`

| id | name | notes |
| --- | --- | --- |
| mcp-memory | MCP official knowledge-graph memory | modelcontextprotocol servers |
| mem0-mcp | mem0ai/mem0-mcp | archived as of this search |
| mcp-mem0-community | coleam00/mcp-mem0 | community |
| langmem | LangMem | langchain-ai |
| memobase | Memobase | memodb-io |
| hindsight | Hindsight | find canonical repo |
| byterover | ByteRover | find canonical repo |
| claude-mem | claude-mem | https://github.com/thedotmack/claude-mem |

claude-mem is coding-agent memory. Card it as `adjacent-coding-agent`. It is a negative control, not a companion system.

## Slice F. Evals

Assigned file. `research/evals/existing-benchmarks.md`

Card each as `eval-benchmark`.

| id | name |
| --- | --- |
| locomo | LoCoMo |
| longmemeval | LongMemEval |
| longmemeval-v2 | LongMemEval-V2 |
| personamem-v2 | PersonaMem-v2 |
| beam | BEAM |
| locomo-plus | Locomo-Plus if it exists as a real dataset |
| pref-eval | PrefEval if it is a real public bench |
| msc | Multi-Session Chat |

For each eval, state the user it models (assistant, agent, friend-chat, web agent), the abilities it scores, and the companion failure modes it does **not** score.

Companion failure modes the later harness must cover, even if no public bench does.

1. Character identity drift after 50+ sessions.
2. User fact remembered, but recalled at a socially wrong time.
3. Joke or hypothetical stored as a real relationship fact.
4. User retcon versus character lie versus narrator retcon.
5. Cross-character leak when two companions share a backend.
6. Lorebook fact treated as something the character experienced.
7. Poisoned memory that later overrides system persona.
8. Cost per turn as session count grows.
9. "Forget that" actually gone on the next turn.
10. Time skip. "We have not spoken in three months."

## Slice G. Friend paper list

Assigned files.

- `research/census/papers-retrieval.md` (G1)
- `research/census/papers-lifecycle.md` (G2)
- `research/census/papers-persona.md` (G3)
- `research/census/papers-architectures.md` (G4)

Index and bands live in `research/papers/registry.json`. Contract is `research/_contracts/PAPER-INGEST.md`.

Card only `core` ids. Adjacent and out-of-scope stay in the registry.

| id | arxiv | worker |
| --- | --- | --- |
| hipporag | 2405.14831 | G1 |
| a-mem | 2502.12110 | G1 |
| mem1 | 2506.15841 | G1 |
| memgpt | 2310.08560 | G1 |
| mi-memory | 2607.18975 | G2 |
| memorylace | 2609.03201 | G2 |
| ai-hippocampus | 2601.09113 | G2 |
| persona-vectors | 2507.21509 | G3 |
| assistant-axis | 2601.10387 | G3 |
| emotion-circuits | 2510.11328 | G3 |
| neural-howlround | 2504.07992 | G3 |
| subliminal-learning | 2507.14805 | G3 |
| titans | 2501.00663 | G4 |
| nested-learning | 2512.24695 | G4 |
| miras | 2504.13173 | G4 |
| sophia | 2512.18202 | G4 |
| mirrormind | 2511.16997 | G4 |

Nature DOI `10.1038/s41586-026-10319-8` is the same paper as `2507.14805`.

## Slice H. Eval landscape beyond LoCoMo

Assigned files.

- `research/evals/memory-ops-benchmarks.md` (H1)
- `research/evals/rp-persona-benchmarks.md` (H2)
- `research/evals/anti-qa-benchmarks.md` (H3)

Index and bands live in `research/evals/registry.json`. Contract is `research/_contracts/EVAL-INGEST.md`.

Card only `core` ids. Already-carded stays in slice F. Adjacent and out-of-scope stay in the registry.

A LoCoMo or LongMemEval win is not a companion system. Card `companion_fit` as whether the eval would **select** a good companion memory system. None of these will be FIT.

| id | arxiv or repo | worker |
| --- | --- | --- |
| halumem | 2511.03506 | H1 |
| structmemeval | 2602.11243 | H1 |
| memoryagentbench | 2507.05257 | H1 |
| memtrapbench | 2608.20202 | H1 |
| perltqa | 2402.16288 | H2 |
| dialsim | 2406.13144 | H2 |
| rp-bench | https://github.com/LeviTheWeasel/rp-benchmark | H2 |
| charactereval | 2401.01275 | H2 |
| incharacter | 2310.17976 | H2 |
| users-dont-ask | 2609.03467 | H3 |
| memuse | 2608.24189 | H3 |
| memoryarena | 2602.16313 | H3 |
| pragma | 2609.09664 | H3 |
| irreducible-conflict | 2608.13921 | H3 |

## Do not waste depth on

Agent harnesses that mention memory as a feature of a coding bot (ruflo, nanobot, CowAgent, ECC) unless they publish a memory engine you can audit. One line in discoveries.md is enough.
