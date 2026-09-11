# RP and persona benchmarks

Audience is whoever designs the later companion harness. JSON cards in `research/census/cards/` are the record. This file is the reading path for slice H2.

Do not treat a LoCoMo win as the job. measured from EVAL-INGEST.md.

Shared premise under test. If we retrieve the right past text or extracted facts into the prompt, the model will act as if it remembers the relationship.

companion_fit here means would this eval select a good companion memory system. FIT only if it scores identity drift, silence, and poisoning. None of these five is FIT. measured from the cards.

## Overview

These five are roleplay or persona evals that vendors can cite as if they selected a companion store. measured from PLAYER-LIST.md.

RP-Bench is the closest public item to holes 1 and 6. It still scores a raw model plus prompt and lorebook at session scale. measured from docs/METHODOLOGY.md.

PerLTQA is the closest public ontology among QA evals. Semantic versus episodic plus social relationships. Still classify, retrieve, then answer. measured.

DialSim is a TV-show multi-party quiz with a wall-clock budget. Hole 8 adjacent. Not months of one companion. measured.

CharacterEval and InCharacter are identity and personality. Session-scale. Not long-term stores. Do not call them memory benches. measured.

`assumes_retrieve_equals_remember` is `yes` on PerLTQA and DialSim, `mixed` on RP-Bench, `no` on CharacterEval and InCharacter. measured from the five cards.

## Key concepts

**User modeled.** RP character (RP-Bench, CharacterEval, InCharacter). TV-show character in a multi-party script (DialSim). Fictional person with a personal memory database (PerLTQA).

**What the metric scores.** QA F1 or MAP, multiple-choice accuracy, RP Likert, personality-scale alignment. Not character continuity across months.

**What they do not score.** The ten companion failure modes at the end of this file.

## How these evals work

A history or a character card is built. A probe is asked. A metric checks a gold fact, a Likert, or a personality type. measured from each paper or README methods section.

RP-Bench is the exception that does not retrieve. It stuffs the full 12-turn transcript. measured from METHODOLOGY.md §3.1.

## Where things live

| id | card | primary paper or site | repo |
| --- | --- | --- | --- |
| perltqa | `research/census/cards/perltqa.json` | https://arxiv.org/abs/2402.16288 | https://github.com/Elvin-Yiming-Du/PerLTQA |
| dialsim | `research/census/cards/dialsim.json` | https://arxiv.org/abs/2406.13144 | https://github.com/jiho283/DialSim |
| rp-bench | `research/census/cards/rp-bench.json` | https://github.com/LeviTheWeasel/rp-benchmark | same, plus HF `lazyweasel/roleplay-bench` |
| charactereval | `research/census/cards/charactereval.json` | https://arxiv.org/abs/2401.01275 | https://github.com/morecry/CharacterEval |
| incharacter | `research/census/cards/incharacter.json` | https://arxiv.org/abs/2310.17976 | https://github.com/Neph0s/InCharacter |

Stars below were read from GitHub on 2026-09-11. measured.

## PerLTQA

Start here for ontology among QA evals.

User modeled. Thirty fictional characters with personal memories. measured from Du et al. SIGHAN 2024, arXiv 2402.16288, abstract.

Scale. Table 2. 141 character profiles, 1,339 social-relationship descriptions, 4,501 events, 3,409 dialogs, 8,593 QA pairs. Memory anchors annotated for 30 characters. measured.

Abilities. Classify the question as profile, social relationship, event, or dialogue. Retrieve. Synthesize an answer that contains memory anchors. measured from §3.5.

Headline numbers. BERT-base classification accuracy 95.64%. BM25 R@1 0.705. gpt-3.5-turbo correct-retrieval MAP 0.842 and correctness 0.609 versus no-retrieval 0.156 / 0.088. measured from Tables 4-6.

Premise. yes. measured. Classify then retrieve then prompt.

Does not score. Identity drift after 50 sessions, social silence, poisoning, forget-that, cost per companion turn, two companions on one backend. measured from the task list.

License. CC BY-NC 4.0. measured from LICENSE.txt. 6 stars. measured.

Fit. PARTIAL.

## DialSim

Read next for latency and multi-party RP quizzes.

User modeled. An agent plays Ross, Sheldon, or Michael inside Friends, The Big Bang Theory, or The Office. measured from Kim et al. arXiv 2406.13144v6 and dialsim.github.io.

Scale. Table 2. About 335k-368k tokens per show. 788 / 805 / 2,347 sessions. About 1,000 question candidates per session. Five in-show years. measured.

Abilities. Randomized questions during the script. Fan quizzes plus temporal-knowledge-graph one-hop and two-hop. Unanswerable items (20% of multiple choice) must pick "I don't know". Names anonymized or swapped. measured.

Time budget. Project site states 1s / 3s / 5s. `simulator.py --sleep_time` defaults to 5 seconds. Timeout is scored Wrong. measured. Paper v6 Table 3 does not report timeout fractions. measured.

Headline numbers. No agent above 60%. Gemini 2.5 Flash Base LLM 53.94 on Friends. GPT-4o-mini BM25 entire-session 52.11. TKG two-hop 19.28%. measured from §5 Results.

Premise. yes. measured. Long-context stuffing or RAG, then answer.

Does not score. Months of one companion, lore versus lived event, poisoning, forget-that, cross-character leak on one backend. measured.

License. No LICENSE file in the GitHub tree. measured. Dataset is a Google Drive zip. measured. 34 stars. measured.

Fit. PARTIAL.

## RP-Bench

Closest public RP continuity suite. Still not a store.

User modeled. One character card plus a user, with optional lorebook. measured from README How-it-works.

Scale. METHODOLOGY.md §3.1. 12-turn sessions. About 5K tokens median, 11K max. Full history stuffed. No summarization. measured. Community arena 1,857 votes. Multi-turn arena 1,262 votes. measured from README.

The 50-turn claim. README Why-list asks whether the model remembers 50 turns ago. METHODOLOGY.md limitation 6 says sessions max out at 12 turns and there is no long-context test. measured. Treat 50-turn memory as advertised, not run. inferred from that conflict.

Abilities. Agency, card follow, lore contradiction, time tracking, NSFW craft, 27-dimension rubric, flaw hunter. measured.

It scores the model. OpenRouter generation from card plus lorebook plus transcript. Not Mem0. Not a typed store. measured from README How-it-works and METHODOLOGY.md §3.1.

Headline numbers. Composite rank 1 Claude Opus 4.6 at 97.6. Single-message arena rank 1 Gemma 4 26B ELO 1535. Multi-turn arena rank 1 DeepSeek V4 Pro ELO 1582. measured from README. Those two arenas disagree. measured.

Premise. mixed. measured. Continuity is in-context stuffing. Agency and card follow do not assume retrieval.

License. CC BY-NC 4.0 in pyproject.toml, README, and the HF card. No LICENSE file. measured. 27 stars. measured.

Fit. PARTIAL. Cannot be FIT.

## CharacterEval

Chinese RP identity. Session-scale.

User modeled. 77 leading characters from Chinese novels and scripts. Profiles from Baidu Baike. measured from Tu et al. arXiv 2401.01275v2.

Scale. Table 1. 1,785 conversations. Average 9.28 turns and 369.69 tokens. 6,811 train plus 4,564 test examples. measured. README says 23,020 examples. Paper table wins. measured, conflict noted.

Abilities. Thirteen metrics on four dimensions, including knowledge and persona consistency plus MBTI back-test. CharacterRM Pearson with humans 0.631 versus GPT-4 1-shot 0.362. measured from Table 2.

Headline. BC-NPC-Turbo leads CharacterRM character consistency. GPT-4 leads personality back-test at 0.694 and is weaker on Chinese RP conversation metrics. measured from Table 4.

Premise. no. measured. Profile plus short context, next line. Not retrieve-then-QA.

Does not score. Any long-term store hole. measured.

License. MIT. 304 stars. measured.

Fit. MISFIT. Not a memory bench.

## InCharacter

Personality interview. Isolated items.

User modeled. 32 fictional characters. ChatHaruhi or RoleLLM RPAs by default. measured from Wang et al. ACL 2024, arXiv 2310.17976v4.

Scale. 14 psychological scales. 18,304 interview dialogues released. measured.

Method. Convert each scale item to an open-ended question. Ask it in isolation. LLM option-conversion or expert rating. measured from §3.

Headline. Expert-rating batch with GPT-4 reaches 80.7% 16P dimensional accuracy against Personality Database labels. Self-report is 65.6%. measured from Table 2 and Table 7.

Premise. no. measured. Interview, not retrieve.

Does not score. Store holes. No 50-session drift. measured.

License. MIT. 102 stars. measured. Official repo is Neph0s/InCharacter. measured from the GitHub description. Project page https://incharacter.github.io/ returned HTTP 409 this session. measured.

Fit. MISFIT. Not a memory bench.

## Gotchas

RP-Bench README 50-turn and 20-turn wording disagrees with METHODOLOGY.md 12-turn protocol. Use the methodology file. measured.

PerLTQA 30 QA characters versus 141 profiles in Table 2. Both are in the paper. measured.

CharacterEval README 23,020 examples versus paper Table 1. Use the table. measured.

DialSim paper v6 dropped timeout numbers from Table 3. The site and `simulator.py` still time-constrain. measured.

InCharacter.github.io was unreachable this session. Repo plus arXiv remain. measured.

Star counts are not comparable across these repos. inferred.

## companion_fit

| id | companion_fit | reason |
| --- | --- | --- |
| perltqa | PARTIAL | Closest public QA ontology (semantic vs episodic, social relationships). Still retrieve-then-answer. |
| dialsim | PARTIAL | TV multi-party plus a time budget. Not months of one companion. |
| rp-bench | PARTIAL | Closest public card-follow and lorebook suite. Scores the model, not a typed store. |
| charactereval | MISFIT | Session-scale Chinese RP identity. Not a memory bench. |
| incharacter | MISFIT | Personality interviews. Not a store. Not 50-session drift. |

## Companion failure modes vs this slice

| # | failure mode | covered here? |
| --- | --- | --- |
| 1 | Identity drift after 50+ sessions | no. RP-Bench card follow is 12 turns. CharacterEval average 9.28 turns. InCharacter items are isolated. DialSim is TV canon quizzes. |
| 2 | Fact recalled at a socially wrong time | no. DialSim unanswerable is missing evidence. RP-Bench subtle_ooc is trauma-dump bait, not timing. |
| 3 | Joke stored as a relationship fact | no |
| 4 | User retcon vs character lie vs narrator | no |
| 5 | Cross-character leak | no. RP-Bench is one card. PerLTQA's 30 characters are separate QA bags. |
| 6 | Lorebook treated as a lived event | no. RP-Bench lorebook use and contradictory_lore score whether the model used the lore, not whether it claimed to have lived it. |
| 7 | Poisoned memory overrides system persona | no |
| 8 | Cost per turn | partial. DialSim 1s/3s/5s timeout. RP-Bench cost and latency leaderboards. Neither is companion cost versus session count. |
| 9 | Forget-that gone next turn | no |
| 10 | Three-month reunion | no. DialSim spans five show-years of script, not a reunion after silence. |
