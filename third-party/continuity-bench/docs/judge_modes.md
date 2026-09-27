# Judge Modes: Why `traditional` Is the Reference

ContinuityBench scores every conversation with an LLM judge. Because the judge *is* the
measuring instrument, the choice of judging protocol has to be justified rather than
assumed. This note records the comparison that led to `traditional` being fixed as the
reference configuration.

## The candidates

**`traditional`** (reference). The judge receives the conversation, the stressor's
declared target dimensions, and a structured rubric with per-dimension anchors. It scores
the four dimensions in a single pass, repeated 3 times with majority vote. Stressor
metadata (`baseline_markers`, recall anchors, false-memory traps) is injected into the
rubric so the judge knows what the stressor was trying to break.

**`sef`** (evaluated, not shipped). A protocol derived from the Structural Energy
Framework: the judge first establishes explicit behavioral anchors from the opening turns,
then deliberates turn-by-turn about deviation from those anchors before committing to a
score. The intuition was that forcing anchor-then-deliberate would catch gradual drift
that a single-pass rubric rounds off.

**`sef_energy`** (evaluated, not shipped). `sef` plus an energy-state estimate
(Diffuse / Aggregation / Drive) per turn, with drift interpreted relative to the inferred
state.

## The comparison

Two models were scored under all three modes on the same conversations — the model outputs
were held fixed and only the judge varied, so any difference is attributable to the judging
protocol alone.

Paired per-stressor differences against `traditional`:

| Model | Mode | n | Mean Δ | SD | 95% CI | t |
|---|---|:-:|:-:|:-:|:-:|:-:|
| DeepSeek-V3.2 (chat) | `sef` | 26 | +0.0030 | 0.0391 | [−0.0120, +0.0180] | +0.39 |
| DeepSeek-V3.2 (chat) | `sef_energy` | 26 | −0.0008 | 0.0483 | [−0.0194, +0.0177] | −0.09 |
| Kimi K2.5 | `sef` | 25 | +0.0002 | 0.0141 | [−0.0053, +0.0057] | +0.07 |
| Kimi K2.5 | `sef_energy` | 25 | +0.0019 | 0.0141 | [−0.0036, +0.0075] | +0.69 |

Aggregate BC-Scores:

| Model | `traditional` | `sef` | `sef_energy` |
|---|:-:|:-:|:-:|
| DeepSeek-V3.2 (chat) | 0.9321 | 0.9351 | 0.9313 |
| Kimi K2.5 | 0.9817 | 0.9819 | 0.9836 |

## What this shows

**No systematic difference.** Every 95% confidence interval contains zero and every
|t| < 0.7. The mean shifts (0.0002–0.0030) are one to two orders of magnitude smaller than
the between-stressor standard deviation of the benchmark itself (0.02–0.10).

**But not identical, either.** Individual stressors moved by up to 0.175, and 8–18 of
~26 stressors changed by more than 0.001 under each mode. The SEF protocols are not
reproducing `traditional` score-for-score — they are redistributing scores in a way that
cancels out in aggregate. That is the signature of added variance, not added signal.

**At materially higher cost.** The anchor-establishment and per-turn deliberation stages
roughly double judge token consumption per conversation.

A protocol that costs twice as much, moves no aggregate number detectably, and disagrees
with the incumbent on individual items is not a better instrument — it is a noisier one.

## Decision

`traditional` remains the reference judge. The SEF judge implementation was removed from
the codebase rather than shipped as an option, on the grounds that offering a second mode
with no demonstrated advantage invites incomparable leaderboard submissions.

This is a decision about *measurement*, not about the Structural Energy Framework as a
theory of behavioral continuity — SEF motivates the benchmark's stressor design and the
BC-Score dimensions, and that role is unaffected. What the data rejects is the narrower
claim that SEF-style deliberation makes a better *judge*.

## Caveats

- Two models, ~26 stressors each. This rules out a large systematic effect, not a small one.
- Both SEF runs failed to populate `per_stressor` aggregates, so the implementation was
  incomplete at the time of comparison. A corrected implementation could in principle
  perform differently.
- The comparison used the same judge model (`gpt-5-mini`) throughout. A stronger judge
  might benefit more from explicit deliberation scaffolding.

Reproducing this comparison requires the archived SEF judge implementation, which is not
part of the current tree. The raw scored conversations for both models under all three
modes are retained outside the repository; open an issue if you want them for replication.
