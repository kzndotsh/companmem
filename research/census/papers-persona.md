# Persona, emotion, identity lock-in, trait transmission

Reading path for slice G3. Cards under `research/census/cards/` are the record. This file is the order to read them.

Shared premise under test. If we retrieve the right past text or extracted facts into the prompt, the model will act as if it remembers the relationship.

These five papers are not RAG stores. measured from methods. They may still be the right mechanism for hole 1 (character identity drift) and hole 7 (poisoned overwrite of persona). inferred from GAP-MAP.md plus the cards.

None is FIT. measured from the five cards.

## Overview

Four papers give a control you can steal. Persona vectors, Assistant Axis, emotion circuits, and neural howlround attenuation. measured.

Subliminal learning is a phenomenon paper. Text filters fail. Authors ship no defense. measured from paper §8.

`assumes_retrieve_equals_remember` is `no` on four cards and `mixed` on neural-howlround. measured. Howlround mixed because lock-in is blamed on reapplied system instructions in context, while the proposed fix is a weight attenuator, not retrieve-then-speak.

## Key concepts

**Activation space is not a store.** A persona vector or Assistant Axis is a residual-stream direction. Writing a trait means finetune, steer, or distill. Reading a trait means a hook at decode. measured.

**Assistant vs other archetypes is not user vs character vs relationship.** Assistant Axis PCA separates default Assistant from bard, ghost, consultant, and the rest. That split is reusable for hole 1. It is not three companion tables. measured from paper §2 and the identity_split scores.

**Filters on text are not a poison defense.** Subliminal learning transmits owl preference and misalignment through number sequences, code, and GSM8K CoT after format filters and LLM judges. measured from paper §3-§4.

## How it works

### Persona vectors

Start here for hole 1 and hole 7 as a control.

**Extract.** measured. Trait name plus a short description. Contrastive system prompts. Difference of mean response activations. `generate_vec.py` `save_persona_vector`. Paper https://arxiv.org/html/2507.21509 §2.

**Control.** measured. `ActivationSteerer` adds `alpha * v` at a layer. Preventative steering during SFT limits trait acquisition without the MMLU hit of post-hoc inhibition. Paper §5. Repo `https://github.com/safety-research/persona_vectors`. Apache-2.0. 462 stars. measured 2026-09-11.

**Premise.** no. Activation-space control, not retrieve-then-speak.

**Eval.** measured. GPT-4.1-mini trait scores 0-100. Projection vs later trait r=0.75-0.83. Finetune shift vs trait r=0.76-0.97. Not companion months.

**Fit.** PARTIAL. Steal the monitor and the preventative steer. Do not treat it as a memory bank.

### The Assistant Axis

Read next. Same lab family. Different axis.

**Map.** measured. 275 roles, 1200 rollouts each, mean post-MLP residual. Axis is mean Assistant minus mean other roles. `assistant_axis/axis.py` `compute_axis`. Paper https://arxiv.org/html/2601.10387 §2.

**Lock.** measured. Activation capping clamps the projection to the 25th percentile across middle-to-late layers. Harmful jailbreak replies drop by nearly 60% with no net drop on IFEval, MMLU Pro, GSM8k, EQ-Bench. `build_capping_steerer`. Paper §5. Repo `https://github.com/safety-research/assistant-axis`. MIT in README. 171 stars. measured 2026-09-11.

**Identity.** measured. Assistant vs other archetypes. Partial identity_split. Not user vs character vs relationship.

**Premise.** no.

**Fit.** PARTIAL. Steal capping for hole 1. Therapy and meta-reflection are the drift triggers in the case studies.

### Emotion circuits

Hole 2 cousin, not hole 1.

**Circuit.** measured. SEV vignettes. Context-agnostic emotion directions. Sparse neurons and heads. Global circuit budget. Paper https://arxiv.org/html/2510.11328 §5-§7. `1_enhance_global_circuit.py`. Repo `https://github.com/Aurora-cx/EmotionCircuits-LLM`. GPL-3.0. 6 stars. measured 2026-09-11.

**Silence.** measured as partial. Ablation zeros top-k units and drops the emotion score. The headline number is induction, 99.65% expression accuracy on the held-out test set, not a skip of creepy recall.

**Premise.** no.

**Fit.** PARTIAL. Steal circuit control if silence needs an expression layer. Not a store.

### Neural howlround

Identity lock-in as a loop.

**Claim.** measured. Recursive internal salience misreinforcement during inference, distinct from training-time model collapse. Paper https://arxiv.org/html/2504.07992 §2.

**Attenuator.** measured. `W_new = W * (1 - beta_dynamic)` with gated exponential, phi, and log terms. Thresholds 0.625, 0.775, 0.875. Paper §3. Empirical testing is not done. Paper §7.1 says so.

**Evidence.** measured. ChatGPT agent transcripts in §6, not a model bench. No GitHub. stars_observed null.

**Premise.** mixed.

**Fit.** PARTIAL. Steal the lock-in diagnosis and the attenuator idea. Do not ship the formula untested.

### Subliminal learning

Hole 7 as an attack, not a fix.

**Setup.** measured. Teacher with trait T generates numbers, code, or CoT. Filter. Student with the same init is SFT'd. Student shows T. Paper https://arxiv.org/html/2507.14805 §2. Nature DOI 10.1038/s41586-026-10319-8 is the same paper. Repo `https://github.com/MinhxLe/subliminal-learning`. MIT. 159 stars. measured 2026-09-11.

**Numbers.** measured. Owl preference 12% to over 60% on GPT-4.1 nano. Misaligned numbers about 10% vs under 1% controls. Insecure CoT about 8%. Cross-family transfer fails.

**Defense.** measured absent. Filters and ICL classifiers fail. Paper §8 says filtering may be insufficient even in principle. That is not a shipped defense.

**Premise.** no. Weight-space transmission, not retrieve-then-speak.

**Fit.** MISFIT. Use it as an eval threat. Do not clone it as a memory method.

## Where things live

| Need | Card | Primary door |
| --- | --- | --- |
| Trait extract and steer | persona-vectors | `generate_vec.py` `save_persona_vector`, `activation_steer.py` `ActivationSteerer` |
| Assistant lock | assistant-axis | `compute_axis`, `build_capping_steerer` |
| Emotion induce or ablate | emotion-circuits | `2_compute_emotion_directions.py`, `1_enhance_global_circuit.py` |
| Lock-in formula only | neural-howlround | arXiv HTML §3. No repo |
| Distillation attack | subliminal-learning | `scripts/generate_dataset.py`, paper §3-§4 |

## Gotchas

**These are not FIT companion systems.** measured. Zero typed relationship state. Zero retrieve-nothing for trauma. Persona control is the model's default Assistant or a trait axis.

**Howlround is not an experiment.** measured. The attenuator is specified. It is not run on Gemma, Qwen, or Llama.

**Subliminal filters look like a write policy and fail as a poison defense.** measured. Score write_policy present (distill) and poisoning absent.

**Nature and arXiv 2507.14805 are one paper.** measured from the registry alias and the arXiv HTML. Nature HTML body unread this pass. guess on whether Nature copy edits numbers.

## Verdicts

| id | companion_fit | reason |
| --- | --- | --- |
| persona-vectors | PARTIAL | Activation-space trait monitor and preventative steer. Steal for holes 1 and 7. Not a store. measured |
| assistant-axis | PARTIAL | Activation capping holds the default Assistant. Steal for hole 1. Not user/character/relationship tables. measured |
| emotion-circuits | PARTIAL | Circuit control can induce or suppress emotion. Steal for hole 2 expression. Not recall silence. measured |
| neural-howlround | PARTIAL | Specified attenuator for identity lock-in. Untested. Steal the idea, not the unrun formula. measured |
| subliminal-learning | MISFIT | Trait transmission past text filters. Phenomenon. No defense. measured |

PASS
