# Sequence architectures and persistent-agent papers

Reading path for this slice. Cards under `research/census/cards/` are the record. This file is the order to read them.

Shared premise under test. If we retrieve the right past text or extracted facts into the prompt, the model will act as if it remembers the relationship.

Titans, Nested Learning, and Miras are sequence-model memories. They write into weights at test time. They are not companion stores. measured from the papers.

Sophia wraps any LLM stack with a System 3 narrative layer. Memory is still RAG. measured.

MirrorMind splits episodic, semantic, and persona for scientist authors inside OmniScientist. Domain is research agents, not 1:1 companions. measured.

Do not clone these into a protocol. Steal cost_shape, retention-as-forgetting, timescale stacks, and the three-memory split.

## Overview

Google Research Titans family first. Then Hope. Then Miras as the unifying frame. Then Sophia as a persistent-agent wrapper. Then MirrorMind as the only paper here that types more than one memory kind at the individual.

None ship a product memory API. inferred from missing GitHub in the papers and from methods that are backbones or wrappers.

## Titans

Behrouz, Zhong, Mirrokni. arXiv 2501.00663. HTML https://arxiv.org/html/2501.00663. No official GitHub in the paper. measured.

**Write.** measured. Inner-loop gradient descent on associative loss `||M(k_t)-v_t||_2^2`. Surprise mixes momentum of past gradients with the current gradient. Forget gate `α_t` is weight decay on `M_{t-1}` (paper §3.1 Eq. 13).

**Read.** measured. Frozen forward pass `y_t = M*(q_t)`. MAC concatenates long-term tokens, persistent tokens, and the current window, then attention may ignore history (Figure 2).

**Premise.** mixed, measured. Remembering is a weight update, not prompt RAG. MAC still feeds memory tokens into attention, which is retrieve-then-attend.

**Fit.** MISFIT. Sequence backbone. No companion ontology. Steal cost_shape and forget-as-capacity-management.

**Eval.** measured. Wiki/commonsense Table 1. RULER S-NIAH Table 2. BABILong Figure 6. Genomics and forecasting. Not companion holes.

| dimension | score | label | primary source |
| --- | --- | --- | --- |
| ontology | partial | measured | paper §4 core, long-term, persistent |
| write_policy | present | measured | paper §3.1 surprise update |
| read_policy | present | measured | paper §3.1 retrieve, Figure 2 MAC |
| supersession | partial | measured | Eq. 13 `α_t` overwrite |
| temporal | absent | measured | sequence/chunk index §3.2 |
| identity_split | absent | measured | one backbone, no user object |
| silence | absent | measured | no skip filter in §3-§5 |
| poisoning | absent | inferred | surprise writes any large gradient |
| forgetting | present | measured | §3.1 forget gate |
| cost_shape | present | measured | §3.2 matmul/scan, Figures 7-8 |
| local | unknown | measured | no GitHub in HTML or Google pub page |
| mcp | absent | measured | not mentioned in the HTML |

## Nested Learning / Hope

Behrouz, Razaviyayn, Zhong, Mirrokni. arXiv 2512.24695. NeurIPS 2025. HTML https://arxiv.org/html/2512.24695. No official GitHub. measured.

**CMS.** measured. Chain of MLP blocks with different update frequencies (paper §7.1). High frequency adapts fast and keeps knowledge briefly. Low frequency is more persistent. Forgotten knowledge in one block can remain in a slower block.

**Hope.** measured. Self-modifying Titans plus CMS (paper §8, Figure 5). Hope-Attention swaps Titans for softmax attention.

**Premise.** mixed, measured. Memory is nested weight updates. Companion turn is still next-token, not a typed store.

**Fit.** MISFIT. Steal continuum timescales. Not a companion log.

**Eval.** measured. Class-incremental Figure 6. MK-NIAH, LongHealth, QASPER Figure 7. Continual translation Figure 8. Wiki Table 2. BABILong §9.2. Not companion holes.

| dimension | score | label | primary source |
| --- | --- | --- | --- |
| ontology | partial | measured | §7.1 CMS, §8 Hope |
| write_policy | present | measured | frequency-scheduled updates §7.1 |
| read_policy | present | measured | Hope forward pass §8.3 |
| supersession | partial | measured | slower blocks retain §7.1 |
| temporal | partial | measured | frequencies and sequential tasks |
| identity_split | absent | measured | one Hope backbone |
| silence | absent | measured | NIAH-class evals only |
| poisoning | absent | inferred | no trust tags |
| forgetting | present | measured | CMS recovery loop §7.1 |
| cost_shape | present | measured | only due blocks update §7.1 |
| local | unknown | measured | no GitHub in HTML |
| mcp | absent | measured | not mentioned |

## Miras

Behrouz, Razaviyayn, Zhong, Mirrokni. arXiv 2504.13173. HTML https://arxiv.org/html/2504.13173. No official GitHub. measured.

**Frame.** measured. Four choices. Memory architecture, attentional bias, retention gate, learning algorithm (Figure 1, §4). Table 1 places Titans, Mamba, DeltaNet, Moneta, Yaad, Memora on those axes.

**Forget.** measured. Remark 3. Forget gates are retention regularization. The authors say memories become inaccessible rather than erased. Steal that wording for later forgetting design. Do not treat it as a user command.

**Variants.** measured. Moneta `L_p`/`L_q`. Yaad Huber. Memora KL/softmax (§5.3).

**Fit.** MISFIT. Unifying backbone paper.

**Eval.** measured. LM and commonsense Table 2. RULER S-NIAH Table 3. Not companion holes.

| dimension | score | label | primary source |
| --- | --- | --- | --- |
| ontology | partial | measured | Figure 1, Table 1 |
| write_policy | present | measured | §5.3 update rules |
| read_policy | present | measured | associative recall, Figure 2 |
| supersession | partial | measured | Learning-Retaining viewpoint §3 |
| temporal | absent | measured | sequence/chunk only |
| identity_split | absent | measured | one backbone |
| silence | absent | measured | LM/NIAH evals |
| poisoning | absent | measured | Huber is robustness, not trust |
| forgetting | present | measured | Remark 3 retention gates |
| cost_shape | present | measured | chunked training §5.4 |
| local | unknown | measured | no GitHub in HTML |
| mcp | absent | measured | not mentioned |

## Sophia

Sun, Hong, Zhang. Westlake / Shanghai Innovation Institute / SJTU. arXiv 2512.18202. HTML https://arxiv.org/html/2512.18202. No GitHub in the paper. measured.

**Wrapper.** measured. System 3 over any LLM System 1/2 stack. Four services. Memory Module (RAG), User-Model, Self-Model, Hybrid Reward (paper §4.1.3, Figure 3).

**Identity.** partial, measured. User-Model vs Self-Model vs narrative memory graph. Self Model.terminal_creed holds five immutable creed sentences in the prototype (§5.1.2). Social relationship is a user-belief field, not a relationship-phase type.

**Premise.** yes, measured. Figure 3 caption says Memory Module (RAG-backed). Forward learning retrieves CoT traces into the next prompt. No runtime weight updates (§5.1.2).

**Fit.** PARTIAL. Persistent narrative wrapper. Still retrieve-then-speak. Not a companion product.

**Eval.** measured. Authors call it exploratory. 36-hour browser sandbox. Hard-task success 20% to 60%. About 80% fewer CoT steps on repeats. Intrinsic tasks during idle. Not companion holes.

| dimension | score | label | primary source |
| --- | --- | --- | --- |
| ontology | partial | measured | §4.1.3 four services |
| write_policy | present | measured | process-supervised ToT, Growth-Journal |
| read_policy | present | measured | RAG, Figure 3, §5.2.3 |
| supersession | partial | inferred | Self-Model append, no fact delete |
| temporal | partial | measured | timestamps §3.1, 36h run |
| identity_split | partial | measured | User-Model vs Self-Model |
| silence | absent | measured | stress trajectory acts on recall |
| poisoning | partial | measured | guardian checklist, no trust tags |
| forgetting | absent | measured | persist-all journal §5.1.2 |
| cost_shape | present | measured | Figure 5 CoT reduction |
| local | unknown | measured | prototype described, not released |
| mcp | absent | measured | not mentioned |

## MirrorMind

Zeng et al., Tsinghua / Zhongguancun Academy. arXiv 2511.16997. HTML https://arxiv.org/html/2511.16997. Paper cites no GitHub. measured.

`tsinghua-fib-lab/OmniScientist` lists the paper under a MIT paper dump. It does not contain the Author Agent engine. measured from README and tree.

**Split.** measured. Individual Level is episodic (hybrid dense+BM25 paper chunks), semantic (period summaries), persona (concept graph serialized into the system prompt). Paper §2.2.

**Read.** measured. Four-stage workflow. Persona load, semantic scoping, episodic RRF, prompt assembly (§2.2.4). That is the shared premise.

**Fit.** PARTIAL. Typed three-way split at the individual. Domain is OmniScientist. Not a companion store.

**Eval.** measured. Sci-Twin AuthorQA Table 1. NSKP Table 2. Collaborator prediction Table 3. HLE 12% vs 6% on 50 questions. Not companion holes.

| dimension | score | label | primary source |
| --- | --- | --- | --- |
| ontology | partial | measured | §2.2 episodic, semantic, persona |
| write_policy | present | measured | ingestion §2.2.1-2.2.3 |
| read_policy | present | measured | §2.2.4 four-stage workflow |
| supersession | partial | measured | incremental persona graph |
| temporal | partial | measured | timestamps and D/M/Y caches |
| identity_split | partial | measured | author vs domain vs MAS, not companion roles |
| silence | absent | measured | always load persona then retrieve |
| poisoning | absent | inferred | paper chunks enter the prompt |
| forgetting | absent | measured | no forget-that |
| cost_shape | present | measured | hybrid retrieve plus MAS caps §7.1 |
| local | unknown | measured | FastAPI described, engine not in OmniScientist repo |
| mcp | absent | measured | FastAPI, not MCP |

## Gotchas

- Unofficial `lucidrains/titans-pytorch` is not the paper's repo (measured from the Titans HTML, which has no GitHub).
- Titans persistent memory is task-knowledge tokens, not companion identity (measured, §3.3).
- Miras "forgetting" is retention regularization, not a user command (measured, Remark 3).
- Sophia User-Model "social relationship" is a belief field, not a typed relationship phase (inferred from §4.1.3 wording).
- MirrorMind persona is scientific style, not a roleplay character card (measured, §2.2.3).

## Verdicts

| id | companion_fit | reason |
| --- | --- | --- |
| titans | MISFIT | Test-time weight memory. No companion API. Steal cost_shape and forget gates. |
| nested-learning | MISFIT | Continuum timescales in Hope. Sequence model, not a companion log. |
| miras | MISFIT | Unifies forget-as-retention. Backbones only. |
| sophia | PARTIAL | Narrative wrapper with user vs self models. Still RAG into the prompt. |
| mirrormind | PARTIAL | Episodic/semantic/persona split for scientists. OmniScientist domain. |

PASS
