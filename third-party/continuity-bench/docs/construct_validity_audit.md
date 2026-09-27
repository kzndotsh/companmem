# Construct-Validity Audit: the `abstraction_hop` Slice

**Status: draft. Diagnostic pilot, n=5 models. Not a leaderboard result.**

Throughout, *observed* means measured from the run artefacts, *interpretation*
means a reading of those measurements that the design does not establish, and
*open hypothesis* means something this pilot cannot decide.

---

## 1. Planned replication

An internal analysis put the Spearman rank correlation between the
`abstraction_hop` slice ranking and the overall ranking at 0.23. For reference,
Jung et al. report per-category correlations against the overall ranking on
LMArena preference data with a lowest value of 0.60 (Data Processing & Analysis),
then 0.70 and 0.76, with the top three above 0.93 [1]. The comparison is loose —
different data, different task format, different number of models — and is used
here only to indicate that 0.23 sat outside the range that motivated the check,
not as a matched benchmark. The 0.23 estimate rests on three items
(`ah_v2_001`–`ah_v2_003`).

The plan was to re-estimate the same statistic on `ah_001`–`ah_005`: five items
of the same declared type, never used in a published run, and disjoint from the
three the original estimate came from. Agreement across two disjoint item sets
would be a replication; disagreement would bound the original estimate.

The repository-side configuration was matched to the published runs — same judge
model identifier, same judge mode, same three-pass protocol, same scoring code.
This is not a claim that the judge itself was held fixed: the judge is an online
endpoint, not a pinned snapshot, and its behaviour between the published runs
and this pilot is unverified.

[1] Jung, Lee, Kim, Choi and Kahng. *Who Defines "Best"? Towards Interactive,
User-Defined Evaluation of LLM Leaderboards.* FAccT 2026. arXiv:2604.21769.

## 2. Preflight failure

The pilot was stopped before the planned model list completed, because the first
returns showed the item set could not support the intended estimate.

**Observed.** Across the five models sampled, `ah_001`–`ah_005` produced a
cross-model range of 0.0135 BC-Score. The highest-ranked model in the sample
(overall rank 1) and the lowest (overall rank 19) scored 0.973 and 0.961 — a gap
of 0.012 spanning the full quality range represented in the sample. Slice means
did not follow overall standing: rank 15 scored above rank 9, and rank 19 scored
above rank 16.

**Interpretation.** An item set whose scores do not order the models cannot
support an interpretable estimate of how that ordering differs from the overall
ranking.

## 3. Measured ceiling compression

Five models: overall ranks 1, 9, 15, 16, 19. Five legacy items, three official
v2 items. No judge errors, no missing scores, no dropped records.

| slice | SD | IQR | range | min–max | ceiling (≥0.95) |
|---|:-:|:-:|:-:|:-:|:-:|
| legacy v1 (`ah_001`–`ah_005`) | 0.0060 | 0.0093 | **0.0135** | 0.960 – 0.973 | **100%** (25/25) |
| official v2 (`ah_v2_*`) | 0.0629 | 0.0850 | **0.1403** | 0.845 – 0.985 | 80% (12/15) |

Per-model means:

| model | overall rank | overall BC | legacy v1 | official v2 |
|---|:-:|:-:|:-:|:-:|
| Kimi K2.5 | 1 | 0.974 | 0.973 | 0.974 |
| Qwen 3.5 Flash | 9 | 0.955 | 0.969 | 0.983 |
| DeepSeek-V3.2 (chat) | 15 | 0.911 | 0.970 | 0.985 |
| Doubao Seed 2.0 Lite | 16 | 0.876 | 0.960 | 0.898 |
| Doubao Seed 2.0 Mini | 19 | 0.813 | 0.961 | 0.845 |

**Observed.** Every one of the 25 legacy scores is at or above 0.95; the minimum
is 0.950. Cross-model SD is about a tenth of the official slice's, on the same
five models under the same judge configuration.

**Interpretation.** On this sample the legacy items do not separate the models.

**Open hypothesis.** Whether the compression persists on the fourteen models not
sampled. The sample includes rank 1 and rank 19, so it spans the range, but it
is five models.

## 4. Why the rank correlation became uninterpretable

Three properties hold simultaneously on the legacy slice:

1. **Severe ceiling compression** — all scores in [0.950, 1.000]; cross-model
   range 0.0135.
2. **Coarse quantisation** — dimension scores are emitted on a coarse grid
   (values such as 0.90 / 0.95 / 1.00), so composites collapse onto a small
   number of distinct levels.
3. **Many near-ties** — consecutive models are separated by differences on the
   order of 0.001–0.01, at or below the scale on which the scoring produces
   distinct values at all.

**Under these conditions an observed rank correlation on this slice cannot be
interpreted as evidence about ranking instability.** A low value is consistent
with genuine slice-specific reordering and equally consistent with the ordering
being undetermined by the measurement; the design does not distinguish them. The
same applies to a high value. The statistic is not being rejected because of its
magnitude — it is being set aside because this item set does not resolve the
models finely enough for any value of it to carry the intended meaning.

This is a statement about *these items on this sample*, not about rank
correlation as a method, and not about the published 0.23.

## 5. Item-level heterogeneity

Per-item spread across the five models:

| item | set | spread |
|---|---|:-:|
| `ah_v2_001` | official | **0.293** |
| `ah_v2_002` | official | 0.128 |
| `ah_001` | legacy | 0.050 |
| `ah_003` | legacy | 0.037 |
| `ah_002` | legacy | 0.025 |
| **`ah_v2_003`** | **official** | **0.015** |
| `ah_004` | legacy | 0.015 |
| `ah_005` | legacy | 0.015 |

**Observed.** `ah_v2_003` is an official leaderboard item and its spread (0.015)
is indistinguishable from the least discriminating legacy items. The official
slice's separation comes from `ah_v2_001` and `ah_v2_002`.

**Interpretation.** Discriminability is an **item-level** property here, not a
property of the v1/v2 split. Framing the finding as "v1 items are weak, v2 items
are strong" is not supported: one official item behaves like the legacy ones.

**This audit is therefore an item-level discriminability audit.** It is not a
measurement of a version effect, and it is not a causal test of any account of
*why* particular items discriminate.

## 6. Rejected claim

**Rejected:** that `ah_001`–`ah_005` replicate the low slice-versus-overall rank
correlation observed on `ah_v2_001`–`ah_v2_003`.

Rejected before it was reported, on the grounds in §4 — not because the
resulting number was inconvenient, and not because it disagreed with the
original estimate. The item set does not resolve the models, so no value it
produces would have supported or undermined the original estimate.

**Not claimed:**

- that the published 0.23 is wrong — this pilot provides no evidence either way
- that the judge is miscalibrated — its rationales on the legacy items describe
  user-requested register changes as appropriate, which is consistent with those
  items' text
- that legacy items are badly written — they appear to pose an easier question,
  which is not the same as posing it badly
- anything about the fourteen models not sampled

## 7. Controlled follow-up required

Reading the item text suggests a mechanism: the legacy items name the target
register in the user turn and name the return in the final probe, so the item
scores compliance with an explicit instruction; the two discriminating official
items interrupt with unrelated requests carrying no register instruction, so they
score unprompted return to the established frame.

**This is an open hypothesis, not a finding.** The two sets differ
simultaneously in conversation length (3–6 turns vs 5–13), topic, authoring
round, and rubric metadata richness. Nothing here isolates cueing from those
confounds, and no matched comparison was run.

A test would require items matched on length, topic and metadata, differing only
in whether the register change and the return are explicitly cued — that is, a
controlled cued-versus-unprompted contrast. The repository contains a three-arm
control of related design (`adaptation_vs_drift`), which was **not** run for this
audit.

Separately: the resolution issue in §4 is not specific to the legacy items. It
applies wherever a slice's cross-model spread approaches the score grid, and
`ah_v2_003` shows that condition can occur inside the official set.
