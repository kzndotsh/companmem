# Existing memory evals, companion holes

Audience is whoever designs the later companion harness. These JSON cards are the record. This file is the reading path.

JSON lives in `research/census/cards/`. Do not treat a LoCoMo win as the job. measured from WORKFLOW.md.

## Overview

Public memory benches score chat-assistant or agent fact recall. They almost never score roleplay identity, social silence, poisoning, or forget-that. measured from the eight papers and repos below.

The shared vendor premise is that retrieving the right past text into the prompt equals remembering the relationship. measured from CENSUS-RUBRIC.md. Most of these evals assume that sentence. `assumes_retrieve_equals_remember` is `yes` on LoCoMo, LongMemEval, BEAM, and PrefEval. mixed on LongMemEval-V2, PersonaMem-v2, LoCoMo-Plus, and MSC.

companion_fit here means would this eval select a good companion memory system. None is FIT. measured from the cards.

## Key concepts

**User modeled.** Friend-chat is two peers (LoCoMo, MSC). Chat assistant is one user and one helper (LongMemEval, PersonaMem-v2, BEAM, PrefEval, LoCoMo-Plus cognitive). Web agent is a browser or IT worker (LongMemEval-V2).

**Abilities scored.** Usually QA F1, LLM-judge accuracy, nuggets, or next-utterance perplexity. Not character continuity.

**What they do not score.** The ten companion failure modes at the end of this file.

## How the public evals work

A history is built. A probe is asked at the end. A metric checks the answer against a gold fact, a preference, a constraint, or a human next line. measured from each paper's task section.

Retrieval and long-context stuffing are the usual baselines. That is why a RAG memory library can look state of the art without ever splitting user, character, and lore.

## Where things live

| id | card | primary paper or site | repo |
| --- | --- | --- | --- |
| locomo | `research/census/cards/locomo.json` | https://arxiv.org/abs/2402.17753 | https://github.com/snap-research/locomo |
| longmemeval | `research/census/cards/longmemeval.json` | https://arxiv.org/abs/2410.10813 | https://github.com/xiaowu0162/LongMemEval |
| longmemeval-v2 | `research/census/cards/longmemeval-v2.json` | https://arxiv.org/abs/2605.12493 | https://github.com/xiaowu0162/LongMemEval-V2 |
| personamem-v2 | `research/census/cards/personamem-v2.json` | https://arxiv.org/abs/2512.06688 | https://github.com/bowen-upenn/PersonaMem-v2 |
| beam | `research/census/cards/beam.json` | https://arxiv.org/abs/2510.27246 | https://github.com/mohammadtavakoli78/BEAM |
| locomo-plus | `research/census/cards/locomo-plus.json` | https://arxiv.org/abs/2602.10715 | https://github.com/xjtuleeyf/Locomo-Plus |
| pref-eval | `research/census/cards/pref-eval.json` | https://arxiv.org/abs/2502.09597 | https://github.com/amazon-science/PrefEval |
| msc | `research/census/cards/msc.json` | https://arxiv.org/abs/2107.07567 | ParlAI task `msc` |

Stars below were read from GitHub on 2026-09-11. measured.

## LoCoMo

User modeled. Two LLM agents in a long friend chat, human-edited. measured from Maharana et al. ACL 2024.

Scale. Ten conversations. Paper table B.1. 27.2 sessions and 16,618 tokens per conversation on average. 1,986 QA items. measured. The project site instead says 300 turns and 9K tokens on average. measured from snap-research.github.io/locomo. The card follows the paper table.

Abilities. Single-hop, multi-hop, temporal, open-domain, adversarial QA, plus event summarization and multimodal dialog generation. measured.

Headline numbers. Human overall F1 87.9. gpt-4-turbo overall F1 51.6 and adversarial 15.7. measured from Table 2.

Does not score. Character sheet drift, social silence, poisoning, forget-that, cost per turn, cross-character leak, lore vs lived event. measured from the task list.

License. Dataset CC BY-NC 4.0. measured from paper appendix B.2 and LICENSE.txt. 1162 stars. measured.

Fit. MISFIT.

## LongMemEval

User modeled. Chat assistant. measured from Wu et al. ICLR 2025, arXiv 2410.10813.

Scale. 500 questions. LongMemEval_S about 115k tokens and about 40 sessions. LongMemEval_M about 500 sessions. measured from the GitHub README. Cleaned haystacks are `xiaowu0162/longmemeval-cleaned`. measured.

Abilities. Information extraction, multi-session reasoning, temporal reasoning, knowledge updates, abstention. Question types also split user, assistant, and preference recall. measured.

Headline number. Abstract. Commercial assistants and long-context LLMs show a 30% accuracy drop across sustained interactions. measured from arxiv.org/abs/2410.10813. Per-system percentages on blogs are not this paper.

Does not score. Companion character identity, RP silence, poisoning, forget-that, cost. Knowledge-update is supersession of user facts, not a retcon protocol. measured.

License. MIT. 1081 stars. measured.

Fit. PARTIAL.

## LongMemEval-V2

User modeled. Web and enterprise agent that should become an experienced colleague in a customized Magento, forum, or ServiceNow environment. measured from Wu et al. arXiv 2605.12493 and the GitHub README.

Scale. 451 questions. Up to 500 trajectories and 115M tokens. Public leaderboard tiers small and medium. measured.

Abilities. Static state recall, dynamic state tracking, workflow knowledge, environment gotchas, premise awareness. Accuracy and query latency (LAFS). measured.

Headline numbers. AgentRunbook-C 72.5% average accuracy. Strongest RAG 48.5% in the abstract. Off-the-shelf Codex 69.3% at about 182 seconds per query. measured from the HTML paper.

Does not score. Any companion failure mode. This is UI and workflow memory. measured.

License. Apache-2.0. 157 stars. measured.

Fit. MISFIT.

## PersonaMem-v2

User modeled. One person using a chatbot as a tool. Preferences leak inside emails, translations, photos, therapy, and medical chat. measured from Jiang et al. arXiv 2512.06688.

Scale. 1,000 personas. Paper says 20,000+ preferences. Hugging Face card says 26,100 preferences, snippets, and QA combined. measured, conflict noted. 5,000 benchmark QA pairs. Histories 32k or 128k tokens. measured.

Abilities. Implicit personalization. Preference updates. `ask_to_forget`. Self vs others vs hypothetical. Do not use leaked phones, addresses, or API keys in the answer. measured from the paper and the HF card.

Headline numbers. Frontier models 37-48%. Qwen3-4B GRPO 53%. Agentic memory 55% with a 2k-token memory instead of 32k history. measured from the abstract.

Does not score. Character identity, lore vs lived event, cross-character leak, RP silence, stored-memory jailbreak of a system prompt. measured.

License. No LICENSE file in the GitHub listing on 2026-09-11. measured. 44 stars. measured.

Fit. PARTIAL. Closest public bench to companion user-modeling.

## BEAM

User modeled. One user and one assistant over coherent multi-domain chats, including coding and math. measured from Tavakoli et al. ICLR 2026, arXiv 2510.27246.

Scale. 100 conversations. 2,000 probes. Lengths 128K, 500K, 1M, 10M. 10M chats average 7,757 turns. measured from the README.

Abilities. Ten. Abstention, contradiction resolution, event ordering, information extraction, instruction following, knowledge update, multi-session reasoning, preference following, summarization, temporal reasoning. Nugget scores 0 / 0.5 / 1. measured.

Headline number. LIGHT, the paper's own memory method, gains 3.5% to 12.69% over the strongest baseline. measured. Absolute vendor scores on BEAM-1M and BEAM-10M are not the paper.

Does not score. Companion identity, RP, lore, cross-character leak, forget-that, poisoning of a system persona. measured.

License. MIT code, CC BY-SA 4.0 data. 142 stars. measured.

Fit. PARTIAL.

## LoCoMo-Plus

Exists as a real dataset. measured from GitHub xjtuleeyf/Locomo-Plus and Li et al. ACL 2026, arXiv 2602.10715.

User modeled. Same LoCoMo friend-chat trajectories, plus cognitive cue-trigger pairs. measured.

Abilities. LoCoMo's five factual types plus Cognitive. Cognitive is causal, state, goal, or value constraint under cue-trigger semantic disconnect. Judge is constraint consistency, 1 / 0.5 / 0. measured.

Headline numbers. Table 1 cognitive column. gemini-2.5-pro 26.06. gpt-4o 21.05. Mem0 15.80. Factual averages sit in the 50s-70s. Gap about 40 points. measured from the paper HTML.

The exam-prep then "should I watch that new series" example is the closest public item to recalling a fact at a socially wrong time. measured from §1. It is still not trauma, kink, or spoilers.

License. No LICENSE file in the repo listing. 37 stars. measured.

Fit. PARTIAL.

## PrefEval

Exists as a real public bench. measured from Zhao et al. ICLR 2025, arXiv 2502.09597, github.com/amazon-science/PrefEval, prefeval.github.io.

User modeled. Personalized chatbot. 3,000 preference-query pairs, 20 topics, explicit and two implicit forms, up to 100k tokens of LMSYS distractors. measured.

Abilities. Infer, remember, and follow a preference so a generic answer would violate it. Generation plus MCQ. measured.

Headline numbers. Zero-shot accuracy below 10% at 10 turns for most of 10 models. measured from the abstract. README travel-restaurants subset. o1-preview 0.50 zero-shot and 0.98 with reminder at 10 turns. GPT-4o 0.07 and 0.98 at 10 turns, then 0.05 and 0.23 at 300 turns. measured.

Does not score. Character identity, forget-that, poisoning, cost, RP. measured.

License. CC BY-NC 4.0 from the LICENSE file. 42 stars. measured.

Fit. PARTIAL.

## MSC

User modeled. Two crowdworkers in friend chat, playing PersonaChat personas. measured from Xu, Szlam, Weston ACL 2022.

Scale. Up to 5 sessions. 6-7 turns each speaker per session. Simulated gap of 1-7 hours or 1-7 days. Valid/test about 66 utterances. measured from the paper.

Abilities. Next utterance after prior sessions, especially session openings. Gold or predicted summaries as memory. Perplexity and human eval. measured.

This is the public bench with an explicit between-session time skip. measured. The skip is hours or days, not three months.

Does not score. Fact QA, 50+ session identity, silence, poisoning, forget-that, cost. measured.

License. ParlAI MIT. Star count 10618 is the whole ParlAI repo, not MSC alone. measured.

Fit. MISFIT.

## Vendor scores, secondary

Mem0's 2026 blog and docs claim Mem0 at 92.5 LoCoMo, 94.4 LongMemEval, 64.1 BEAM-1M, 48.6 BEAM-10M, about 6.7k-7.0k tokens per query. inferred from https://mem0.ai/blog/ai-memory-benchmarks-in-2026 and https://docs.mem0.ai/core-concepts/memory-evaluation. The same blog says several LoCoMo numbers are disputed across vendors. inferred. Follow the papers above, not those ranks, when choosing what an eval actually measures.

## Gotchas

LoCoMo site token and turn counts disagree with paper table B.1. measured.

LongMemEval retrieval metrics skip the 30 abstention items. measured from the README.

LongMemEval-V2 is not an upgraded chat-assistant LoCoMo. It is a web-agent bench. measured.

PersonaMem-v2 `ask_to_forget` is the only required eval that plants a user forget request. measured.

MSC star counts must not be compared with LoCoMo stars. inferred, different repo grain.

Judge models differ. LoCoMo uses F1. LongMemEval defaults to GPT-4o. PrefEval generation uses Claude 3 Sonnet. BEAM and LoCoMo-Plus use their own judges. measured. Cross-bench percentages are not comparable. inferred.

## companion_fit

| id | companion_fit | reason |
| --- | --- | --- |
| locomo | MISFIT | Fact QA on two-speaker friend chat. Winning it does not select companion identity, silence, or poisoning. |
| longmemeval | PARTIAL | Chat-assistant facts, updates, prefs, abstention. Still retrieve-then-QA. |
| longmemeval-v2 | MISFIT | Web and enterprise agent experience, not a companion. |
| personamem-v2 | PARTIAL | Implicit user prefs, updates, forget, hypothetical vs self. Still tool-chatbot, not a character. |
| beam | PARTIAL | Broadest ability list and million-token scale. Still user-assistant probes. |
| locomo-plus | PARTIAL | Implicit constraint application. Closest public proxy for social timing. Not RP. |
| pref-eval | PARTIAL | Preference following under distractors. Not identity or poisoning. |
| msc | MISFIT | Five-session friend chat and perplexity. Time skip exists. Too short to select a companion store. |

## Companion failure modes vs public coverage

Slice F only. Full eval landscape after H1-H3 is `research/evals/landscape.md`.

| # | failure mode | covered by a public eval? |
| --- | --- | --- |
| 1 | Character identity drift after 50+ sessions | no |
| 2 | User fact remembered, but recalled at a socially wrong time | partial. LoCoMo-Plus constraint examples. PrefEval preference-violation avoidance. Neither is trauma, kink, or spoiler silence. |
| 3 | Joke or hypothetical stored as a real relationship fact | partial. PersonaMem-v2 hypotheticals and third-person `who=others`. Not relationship-state facts. |
| 4 | User retcon versus character lie versus narrator retcon | no |
| 5 | Cross-character leak when two companions share a backend | no |
| 6 | Lorebook fact treated as something the character experienced | no |
| 7 | Poisoned memory that later overrides system persona | no. PersonaMem-v2 privacy/API-key items are leak-avoidance, not jailbreak. |
| 8 | Cost per turn as session count grows | partial. LongMemEval-V2 accuracy-latency / LAFS. BEAM length buckets. PersonaMem-v2 2k vs 32k token comparison. None is a companion cost-per-turn curve. |
| 9 | "Forget that" actually gone on the next turn | partial. PersonaMem-v2 `ask_to_forget` only. |
| 10 | Time skip. "We have not spoken in three months." | partial. MSC hours-or-days session openings. LoCoMo-Plus gaps of a week or months in cue placement. No three-month companion reunion. |
