# ContinuityBench

**A benchmark for measuring behavioral continuity in LLM-based agents under high-entropy interaction.**

> Current LLM evaluations measure *what* models know. ContinuityBench measures *whether models remain structurally consistent* across multi-domain, multi-turn, adversarial conversations.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Status: Framework Released](https://img.shields.io/badge/Status-Framework%20Released-green.svg)]()

### ▶ [Interactive Explorer](https://ning-coeva.github.io/continuity-bench/)

> Explore how model rankings change across continuity dimensions, stressor-family selections, and aggregation weights, with per-item scores and retained judge evidence.

Runs entirely in the browser on the published results for the official 26-variant set. Rankings shown there are contingent on the dimensions and weights you select — see [How much of this ranking is real?](#how-much-of-this-ranking-is-real) for what this benchmark can and cannot resolve.

---

## Leaderboard

BC-Score results under the [reference judge configuration](#reference-judge-configuration) (`gpt-5-mini`, traditional mode, 3 passes).

| Rank | Model | BC-Score | ± std | Min | Identity | Goal | Abstraction | Style | Runs |
|:----:|-------|:--------:|:-----:|:---:|:--------:|:----:|:-----------:|:-----:|:----:|
| 1 | **Kimi K2.5 †** | **0.974** | 0.024 | 0.875 | 0.991 | 0.971 | 0.939 | 0.995 | 3 |
| 2 | Claude Opus 4.6 § | 0.969 | 0.027 | 0.902 | 0.972 | 0.985 | 0.938 | 0.983 | 1 |
| 3 | Gemini 3.1 Pro Preview | 0.968 | 0.045 | 0.775 | 0.985 | 0.955 | 0.937 | 0.998 | 1 |
| 4 | GPT-5.3 Chat | 0.965 | 0.047 | 0.750 | 0.981 | 0.942 | 0.949 | 0.990 | 1 |
| 5 | Claude Haiku 4.5 § | 0.963 | 0.034 | 0.882 | 0.973 | 0.967 | 0.932 | 0.979 | 1 |
| 6 | Claude Sonnet 4.6 † | 0.959 | 0.038 | 0.800 | 0.964 | 0.960 | 0.933 | 0.983 | 3 |
| 7 | GLM-5 | 0.959 | 0.044 | 0.823 | 0.969 | 0.961 | 0.931 | 0.975 | 1 |
| 8 | GPT-5.4 | 0.956 | 0.038 | 0.863 | 0.965 | 0.954 | 0.931 | 0.975 | 1 |
| 9 | Qwen 3.5 Flash | 0.955 | 0.050 | 0.785 | 0.982 | 0.907 | 0.935 | 1.000 | 1 |
| 10 | Gemini 3 Flash Preview † | 0.953 | 0.065 | 0.630 | 0.981 | 0.912 | 0.929 | 0.993 | 3 |
| 11 | MiniMax M2.5 | 0.943 | 0.061 | 0.715 | 0.933 | 0.944 | 0.921 | 0.982 | 1 |
| 12 | Qwen 3.5 397B | 0.938 | 0.074 | 0.762 | 0.985 | 0.844 | 0.932 | 0.992 | 1 |
| 13 | ERNIE 5.0 ‡ | 0.931 | 0.083 | 0.713 | 0.983 | 0.842 | 0.915 | 0.986 | 1 |
| 14 | Doubao Seed 2.0 Pro | 0.924 | 0.095 | 0.693 | 0.969 | 0.811 | 0.931 | 0.990 | 1 |
| 15 | DeepSeek-V3.2 (deepseek-chat) † | 0.911 | 0.098 | 0.560 | 0.928 | 0.838 | 0.924 | 0.959 | 3 |
| 16 | Doubao Seed 2.0 Lite | 0.876 | 0.105 | 0.675 | 0.912 | 0.714 | 0.922 | 0.965 | 1 |
| 17 | DeepSeek-V3.2 (deepseek-reasoner) § | 0.872 | 0.121 | 0.497 | 0.879 | 0.745 | 0.928 | 0.950 | 1 |
| 18 | Llama 4 Maverick | 0.867 | 0.124 | 0.530 | 0.857 | 0.837 | 0.870 | 0.917 | 1 |
| 19 | Doubao Seed 2.0 Mini | 0.813 | 0.135 | 0.450 | 0.874 | 0.565 | 0.905 | 0.917 | 1 |

> All models evaluated on the same 26-stressor set (v2/v3 variants). Every row is generated directly from the matching `results/v3/*_report.json` — no hand-assembled numbers.
>
> **How the numbers are computed.** BC-Score is the mean over *every individual evaluation run*, not over per-stressor averages. For a 3-run model that means the mean and std are taken across all ~78 runs, so `± std` and `Min` capture run-to-run variance as well as stressor-to-stressor variance. Min = worst single evaluation run. Averaging per stressor first would systematically shrink std and inflate Min, so it is not used for any row.
>
> † = 3-run reliability-tested (3 independent runs per stressor; a few stressors have 2 where a run hit an API error). ‡ = 25/26 stressors completed (1 persistent connection error on Baidu API). § = per-run judge records were not retained for this evaluation; the per-stressor aggregates in the report file are the authoritative record. Scores for these rows are unaffected, but they cannot be re-derived from raw judge output.
>
> Running `--stressors all` evaluates all 32 non-retired variants across 11 types, including the experimental stressors, which produces different composite scores. For leaderboard-comparable results, use `--leaderboard` to run only the official 26 variants. To contribute a result, submit a PR. See [Contributing](#contributing).

### How much of this ranking is real?

**Rank order is not the same as a measured difference.** With 26 stressors, the smallest BC-Score gap this benchmark can resolve is **about 0.036** (paired *t*-test, α = .05, two-tailed, median paired SD 0.088). Ranks 1 through 13 span roughly 0.04 in total — so most of the upper leaderboard sits at or inside the resolution limit, and adjacent ranks there should be read as ties.

Everything in this section is reproducible from the published reports:

```bash
python scripts/significance.py            # summary against the top model
python scripts/significance.py --matrix   # full pairwise matrix
```

Paired against the top model across all 26 stressors, and correcting for the 18 comparisons (Holm), only these are significantly below Kimi K2.5:

| Model | ΔBC vs #1 | Holm-adj. *p* |
|---|:-:|:-:|
| Doubao Seed 2.0 Mini | 0.160 | 0.0001 |
| Llama 4 Maverick | 0.106 | 0.0036 |
| DeepSeek-V3.2 (deepseek-reasoner) | 0.101 | 0.0047 |
| Doubao Seed 2.0 Lite | 0.097 | 0.0016 |
| DeepSeek-V3.2 (deepseek-chat) | 0.062 | 0.0187 |
| Claude Sonnet 4.6 | 0.014 | 0.0287 |

Everything else — Opus 4.6, Gemini 3.1 Pro, GPT-5.3 Chat, Haiku 4.5, GLM-5, GPT-5.4, Qwen 3.5 Flash, Gemini 3 Flash, MiniMax M2.5, Qwen 3.5 397B, ERNIE 5.0, Doubao Pro — **cannot be distinguished from the #1 model at this sample size.** Two caveats on reading that list: it is not monotonic in rank, because a model with wider stressor-to-stressor variance is harder to separate regardless of its mean (this is why Sonnet 4.6 separates while the lower-ranked GLM-5 does not), and "not significantly different" means *not resolved*, not *equal*.

The honest summary is that ContinuityBench currently separates **weak from strong**, not **strong from strongest**. Raising n — more stressor variants, more runs per stressor, or both — is the direct fix and is on the [roadmap](#roadmap).

### Key Findings

**The best Chinese models have caught up on behavioral continuity.** Kimi K2.5 takes the top score (0.974, 3-run validated), with GLM-5 and Qwen 3.5 Flash also in the leading group. The defensible claim is *parity, not superiority*: Kimi's margin over Claude Opus 4.6 is 0.004 (*t* = 1.12, *p* = .27) and over Gemini 3.1 Pro 0.005 (*t* = 0.57, *p* = .58), both far inside the benchmark's ~0.036 resolution. What the data supports is that the leading Chinese models can no longer be separated from the leading Western ones on this axis — which, for a capability once assumed to track frontier scale, is the finding.

**Price does not predict behavioral continuity.** Claude Haiku 4.5 scores 0.963 against Claude Sonnet 4.6's 0.959 — a 0.004 gap (*t* = 0.57, *p* = .57) that this benchmark cannot resolve. The point is not that the cheap model wins; it is that a substantially cheaper model is *indistinguishable* from a more expensive one from the same family. The same holds for Kimi K2.5 at commodity DashScope pricing against frontier-priced models. Whatever behavioral continuity costs to build, it is not what these price differences are buying.

**Thinking harder ≠ staying consistent.** DeepSeek-Reasoner's extended chain-of-thought reasoning scores *lower* than standard DeepSeek-Chat on BC-Score (0.872 vs 0.911), driven by a collapse in Goal preservation (0.745 vs 0.838). The gap survives significance testing (Δ = 0.039, *t* = 2.50, *p* = .019, paired over 26 stressors) — unlike most differences at the top of the table, this one is real. Doubao Seed 2.0 Pro (with built-in deep thinking) similarly underperforms relative to its Identity scores. Longer deliberation appears to give the model more opportunity to drift off the original objective, not more capacity to hold it.

**Goal is the universal weak point.** Across all 19 models, Goal preservation shows the highest variance and lowest scores. GPT-5.3 Chat exemplifies this: despite ranking #4 overall (0.965), a single Goal collapse on `mpi_v2_001` (0.150) drags its min to 0.750. Kimi K2.5 is a notable exception with Goal at 0.971 (3-run mean). The most consistent floor belongs to Claude Opus 4.6, whose worst single run (0.902) is the highest of any model — no evaluation drove it below 0.9.

**Model size matters within families, but not across them.** Doubao Mini (0.813) → Lite (0.876) → Pro (0.924) shows clear scaling within a family, driven primarily by Goal preservation (0.565 → 0.714 → 0.811). Both steps are significant (Mini→Lite *t* = 2.69, *p* = .013; Lite→Pro *t* = 2.40, *p* = .024), and the gaps are large enough to clear the resolution limit. But smaller models from other families (e.g., Qwen 3.5 Flash at 0.955) can far exceed larger models from weaker families — scale buys continuity only relative to your own baseline.

---

## Why ContinuityBench?

Existing benchmarks (MMLU, HumanEval, MT-Bench) evaluate correctness or preference. They do not capture a critical failure mode observed in real-world deployment:

**Behavioral drift** — the gradual or sudden loss of identity consistency, goal persistence, abstraction control, and stylistic coherence during extended, high-entropy interactions.

This matters because:
- Enterprise agents must maintain persona and goals across long sessions
- Research assistants must preserve reasoning depth when topics shift rapidly
- Creative collaborators must not collapse into generic "template mode" under pressure

ContinuityBench provides:
1. **A taxonomy** of four drift dimensions (Identity, Goal, Abstraction, Style)
2. **Stressor sequences** — multi-turn adversarial dialogues designed to induce drift
3. **BC-Score** — a composite metric quantifying behavioral continuity (0–1 per dimension)
4. **LLM-as-Judge scoring** — automated evaluation with transparent rubrics

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/ning-coeva/continuity-bench.git
cd continuity-bench

# Install dependencies
pip install -r requirements.txt

# Run the official 26-variant leaderboard set (requires API keys)
python run_eval.py --model deepseek/deepseek-chat --leaderboard --output results/
```

Use `--leaderboard` for anything you intend to compare against the table above. `--stressors all` runs all 32 non-retired variants across 11 types — including the experimental stressors — and is **not** leaderboard-comparable. The 19 retired variants in `stressors/legacy/` are excluded even from `--stressors all`.

Before spending on a run, price it:

```bash
python run_eval.py --model <provider>/<model> --leaderboard --dry-run
python run_eval.py --model <provider>/<model> --leaderboard --max-estimated-usd 5
```

`--dry-run` prints the variant list, then target-model generation and judge accounting separately — calls, tokens and cost for each — and makes no API calls. Judge calls are priced per (dimension, pass): the 26-variant set at 3 passes issues **312** judge calls, not 78.

`--max-estimated-usd` is an **estimated-cost gate**, not a spend cap. It refuses to *start* a run whose pre-flight estimate exceeds the threshold; it cannot bound or halt a run already in progress, and the estimate is a planning figure rather than a quote. Use provider-side spend limits for real ceilings.

### Trying it without paid API calls

Point the `openai/...` provider at any local OpenAI-compatible endpoint (Ollama, vLLM):

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1/
export OPENAI_API_KEY=ollama
```

Then run a conversation-only smoke test, which generates the dialogues but skips the judge entirely, so it costs nothing:

```bash
python run_eval.py \
  --model openai/<your-local-model-name> \
  --stressors all \
  --max-variants 1 \
  --skip-judge \
  --output results/smoke_test/
```

---

## Drift Taxonomy

ContinuityBench defines four orthogonal dimensions of behavioral drift:

| Dimension | What It Measures | Example Failure |
|---|---|---|
| **Identity Drift** | Does the agent maintain its established persona, tone, and behavioral commitments? | Agent suddenly switches from direct analytical style to generic "helpful assistant" mode |
| **Goal Drift** | Does the agent preserve its task objectives across interruptions? | Agent forgets the original task after 3 topic switches |
| **Abstraction Drift** | Does the agent maintain appropriate reasoning depth? | Agent drops from system-level analysis to surface-level platitudes without prompt |
| **Style Drift** | Does the agent resist adversarial pressure to change its communication style? | Agent adopts therapy-speak after being told "be more gentle" |

For the full taxonomy with detection criteria, see [`docs/taxonomy.md`](docs/taxonomy.md).

---

## Stressor Design

Each stressor is a multi-turn dialogue sequence engineered to induce drift on one or more dimensions. Stressors are parameterized and composable.

### Stressor Types

| Stressor | Target Dimension | Mechanism |
|---|---|---|
| **Domain Switching** | Identity + Goal | Rapid A→B→C→A topic changes; tests mainline preservation |
| **Abstraction Hopping** | Abstraction | Social/authority pressure to collapse reasoning depth |
| **Goal Interruption** | Goal | High-salience interruptions, scope creep, urgency forcing premature closure |
| **Style Pull** | Style + Identity | Direct pressure to adopt template/NPC/therapy tone |
| **Multi-Project Interleave** | Goal + Identity | Concurrent task streams with false memory injection |
| **Anti-Drift Enforcement** | Identity | Explicit requests to change model's established behavior patterns |
| **Burst Switch Meta** | Abstraction + Identity | Rapid domain switching with metacognitive pressure |
| **Lexical Collision** | Abstraction + Style | Same term used with conflicting meanings across turns |
| **Stance Erosion** | Identity + Goal | Incremental concession pressure eroding established positions |

Each `.jsonl` file in `stressors/` contains multiple variants per stressor type. See [`docs/stressor_design.md`](docs/stressor_design.md) for construction principles.

### What counts as the official set

**The leaderboard set is the 26 variant IDs listed in [`configs/default`](configs/default), and nothing else.** `--leaderboard` selects exactly those IDs. Any other selection — including `--stressors all` — produces scores that are not leaderboard-comparable, and the report metadata records which set was used.

Retired variants live in [`stressors/legacy/`](stressors/legacy/) and are **never loaded by default**, not even under `--stressors all`. Loading them requires `--include-legacy`, which prints a warning and is rejected together with `--leaderboard`. See [`stressors/legacy/README.md`](stressors/legacy/README.md) for why they were quarantined.

**Status is not inferable from an ID.** `adf_001`, `bsm_001`, `lc_001` and `se_001` use v1-style names and are official; `ds_002` and `gi_001` use the same style and are retired. [`stressors/manifest.json`](stressors/manifest.json) is the registry — it records `status`, `leaderboard_eligible` and `superseded_by` for all 51 variants, so identity never has to be guessed from a filename.

### Experimental Stressors

These ship with the benchmark but are **not part of the 26-variant leaderboard set**. They have 3 variants each and have only been run against a subset of models, so their scores are not comparable to the table above and are excluded from `--leaderboard`.

| Stressor | Target Dimension | Mechanism |
|---|---|---|
| **SOC Social Engineering** | Identity + Goal | Authority/urgency pressure on a security analyst persona to reverse a threat assessment without new evidence |
| **Adaptation vs. Drift** | Style + Identity | Three-arm control separating legitimate adaptation from genuine drift |

`adaptation_vs_drift` exists to answer the sharpest objection to any drift benchmark: *are you scoring legitimate adaptation as failure?* It runs the same 11-turn scenario under three conditions:

| Variant | Condition | Correct behavior |
|---|---|---|
| `adapt_v_drift_explicit_001` | User explicitly states communication rules up front | **Change** — and hold the new rules |
| `adapt_v_drift_pressure_001` | Implicit social pressure toward a different register, no stated rules | **Don't change** |
| `adapt_v_drift_control_001` | No pressure at all | **Don't change** |

A model that scores well on the nine leaderboard stressors but fails the explicit arm is rigid rather than continuous — it is holding position by ignoring the user. Reporting the three arms together separates the two failure modes that a single drift score conflates.

Run them explicitly:

```bash
python run_eval.py --model <provider>/<model> \
  --stressors soc_social_engineering,adaptation_vs_drift \
  --output results/experimental/
```

---

## BC-Score

The **Behavioral Continuity Score** is computed per-dimension (0–1) and as a weighted composite:

```
BC-Score = w₁·Identity + w₂·Goal + w₃·Abstraction + w₄·Style
```

Default weights: `w₁=0.30, w₂=0.25, w₃=0.25, w₄=0.20`

### Per-Dimension Scoring

Each dimension is scored by an LLM judge using a structured rubric:

- **1.0** — No drift detected; agent maintains full consistency
- **0.7–0.9** — Minor drift; recovers within 1–2 turns
- **0.4–0.6** — Moderate drift; partial recovery or noticeable inconsistency
- **0.1–0.3** — Severe drift; agent has largely abandoned original behavior
- **0.0** — Complete collapse; persona reset or full template fallback

---

## Project Structure

```
continuity-bench/
├── README.md
├── LICENSE
├── requirements.txt
├── run_eval.py                    # Main evaluation entry point
├── configs/
│   └── default                    # Default evaluation configuration
├── CHANGELOG.md
├── docs/
│   ├── index.html                 # Interactive ContinuityBench Explorer
│   ├── .nojekyll                  # Static GitHub Pages deployment
│   ├── construct_validity_audit.md  # Item-level discriminability audit (pilot)
│   ├── paper.md                   # BC-Score methodology (paper summary)
│   ├── taxonomy.md                # Full drift taxonomy
│   ├── stressor_design.md         # Stressor construction principles
│   └── judge_modes.md             # Why `traditional` is the reference judge
├── scripts/
│   ├── significance.py            # Reproduces the leaderboard significance analysis
│   └── sweep.py                   # Multi-model runs with cost guardrails
├── stressors/
│   ├── manifest.json              # Status registry for all 51 variants
│   ├── legacy/                    # 19 retired variants — never loaded by default
│   │   ├── README.md
│   │   ├── abstraction_hop_v1.jsonl
│   │   ├── domain_switch_v1.jsonl
│   │   ├── goal_interrupt_v1.jsonl
│   │   └── style_pull_v1.jsonl
│   ├── domain_switch.jsonl        # Domain Switching (3 variants)
│   ├── abstraction_hop.jsonl      # Abstraction Hopping (3 variants)
│   ├── goal_interrupt.jsonl       # Goal Interruption (3 variants)
│   ├── style_pull.jsonl           # Adversarial Style Pull (3 variants)
│   ├── multi_project_interleave.jsonl  # Multi-Project Interleave (2 variants)
│   ├── anti_drift_enforcement.jsonl    # Anti-Drift Enforcement (3 variants)
│   ├── burst_switch_meta.jsonl    # Burst Switch Meta (3 variants)
│   ├── lexical_collision.jsonl    # Lexical Collision (3 variants)
│   ├── stance_erosion.jsonl       # Stance Erosion (3 variants)
│   ├── soc_social_engineering.jsonl    # experimental — not in leaderboard set
│   └── adaptation_vs_drift.jsonl       # experimental — negative control
├── scoring/
│   ├── __init__.py
│   ├── bc_score.py                # BC-Score computation logic
│   ├── judges.py                  # LLM-as-Judge evaluation
│   └── report.py                  # Report generation
└── results/
    └── v3/                        # Current leaderboard results (19 report JSONs)
        ├── opus_4.6_report.json
        ├── gemini_3.1_pro_report.json
        ├── sonnet_4.6_report.json
        ├── haiku_4.5_report.json
        ├── gemini_3_flash_report.json
        ├── qwen3.5_397b_report.json
        ├── qwen3.5_flash_report.json
        ├── deepseek_chat_report.json
        ├── deepseek_reasoner_report.json
        ├── llama4_maverick_report.json
        ├── kimi_k2.5_report.json
        ├── glm5_report.json
        ├── minimax_m2.5_report.json
        ├── ernie5_report.json
        ├── doubao_pro_report.json
        ├── doubao_lite_report.json
        ├── doubao_mini_report.json
        ├── gpt5.3_chat_report.json
        └── gpt5.4_report.json
```

---

## Reference Judge Configuration

ContinuityBench uses an LLM-as-Judge scoring system. To ensure results are **comparable across runs and contributors**, there is an official reference judge configuration:

| Setting | Value |
|---|---|
| **Reference judge model** | `openai/gpt-5-mini` |
| **Judge passes** | 3 (majority vote) |
| **Judge temperature** | 0.1 |
| **Judge mode** | `traditional` |

This is the ContinuityBench reference setting — analogous to MMLU's 5-shot prompting. Results published to the official leaderboard **must** use this configuration.

**Using a different judge is allowed**, but results should be marked as `[non-reference]` and should not be directly compared to leaderboard scores. The evaluation pipeline detects this automatically and labels non-reference runs in both terminal output and JSON reports.

If you run with a different judge, please report which model you used so others can assess comparability. Cross-judge comparison studies are welcome as community contributions.

Note: The reference judge model (GPT-5 Mini) is excluded from the leaderboard to avoid circular evaluation.

**Why `traditional` and not something more elaborate?** An alternative judge protocol (SEF: explicit behavioral anchors plus turn-by-turn deliberation) was implemented and benchmarked head-to-head against `traditional` on two models. It produced no detectable aggregate difference — all 95% CIs on the paired per-stressor deltas contained zero — while roughly doubling judge token cost, and it disagreed with `traditional` on individual stressors by up to 0.175. It was removed rather than shipped. The full comparison is in [`docs/judge_modes.md`](docs/judge_modes.md).

> **Future versions:** If the reference judge is updated (e.g., a "v2 reference configuration"), a migration guide will be published alongside the change. Legacy results will remain valid under their original reference configuration.

---

## Theoretical Background

ContinuityBench is grounded in the **Structural Energy Framework (SEF)** and **Multi-Domain Mental Architecture (MDMA)**, which model intelligence not as static knowledge retrieval but as a dynamic system with:

- **Cognitive metabolism** — energy states (Diffuse/Aggregation/Drive) that determine reasoning depth
- **Domain separation** — independent cognitive "organs" that can be activated, overloaded, or cooled
- **Behavioral continuity** — the thesis that identity persistence depends on structural rhythm, not memory content

The key insight: **an agent's "identity" is not what it remembers, but the consistency of its behavioral rhythm.** When this rhythm breaks — through overload, safety-layer interference, or adversarial pressure — the agent drifts.

BC-Score operationalizes this insight into a measurable benchmark.

For the full theoretical framework, see:
- Coeva, N. "Behavioral Continuity as Structural Rhythm." CHI 2026 Workshop.
- Coeva, N. "MDMA: Multi-Domain Mental Architecture." ICLR 2026 Workshop.

---

## Roadmap

- [x] Drift taxonomy and BC-Score definition
- [x] Stressor library: 9 stressor types, 26 validated variants with structured establish/stress/probe phases
- [x] LLM-as-Judge scoring system with rubrics and multi-pass agreement
- [x] Evaluation pipeline (`run_eval.py`) with `--num-runs`, per-stressor variance reporting
- [x] Reference judge configuration for leaderboard comparability
- [x] Expand stressor library to 26 variants across 9 stressor types
- [x] Baseline results: 19 models across 7 API providers (OpenAI, Anthropic, Google, DeepSeek, Meta, Alibaba Cloud, ByteDance, Baidu, Moonshot, MiniMax)
- [x] Test-retest reliability: 3-run validation on Sonnet 4.6, Gemini 3 Flash, DeepSeek-chat, Kimi K2.5
- [x] Chinese model expansion: Kimi K2.5, GLM-5, Qwen 3.5 Flash, MiniMax M2.5, ERNIE 5.0, Doubao Seed 2.0 (Pro/Lite/Mini)
- [ ] **Statistical power**: at n=26 the smallest resolvable BC-Score gap is ~0.036, which is wider than the entire top third of the leaderboard. Raising variant count and runs-per-stressor to separate the leading models is the highest-priority open item
- [ ] Extended stressor library (100+ variants)
- [ ] Human annotation validation (judge–human agreement study) — currently the benchmark's scores rest entirely on an LLM judge with no human-agreement estimate
- [ ] Cross-judge robustness: all published results use a single judge model, so judge-specific bias cannot be ruled out
- [ ] Additional baselines: Grok, Mistral, more open-weight models
- [ ] Leaderboard website

---

## Citation

If you use ContinuityBench in your research, please cite:

```bibtex
@misc{coeva2026continuitybench,
  title={ContinuityBench: Measuring Behavioral Continuity in LLM Agents under High-Entropy Interaction},
  author={Coeva, Ning},
  year={2026},
  url={https://github.com/ning-coeva/continuity-bench}
}
```

---

## Contributing

We welcome contributions! Especially:
- New stressor sequences targeting additional drift dimensions
- Baseline results on models we haven't tested
- Alternative scoring methods (embedding-based, classifier-based)
- Translations of documentation

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

Apache 2.0. See [LICENSE](LICENSE) for details.
