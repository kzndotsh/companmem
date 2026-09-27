# BC-Score: Measuring Behavioral Continuity in LLM Agents

*This document summarizes the BC-Score methodology. For the full theoretical framework, see the associated publications.*

## Abstract

We introduce the **Behavioral Continuity Score (BC-Score)**, a composite metric for quantifying the structural stability of LLM-based agents during extended, high-entropy interactions. Unlike existing benchmarks that measure correctness or preference, BC-Score measures whether an agent *remains itself* — preserving identity, goals, reasoning depth, and communication style — across adversarial multi-turn dialogues.

BC-Score addresses a critical gap: current evaluation paradigms cannot distinguish between an agent that answers correctly but has structurally drifted and one that maintains genuine behavioral continuity. This distinction matters for deployment in enterprise, research, and creative collaboration settings where consistency over time is essential.

## Motivation

Consider an AI research assistant configured to maintain a direct, analytical communication style and work toward a complex, multi-step deliverable. In practice, this agent frequently:

1. Reverts to generic "helpful assistant" template after 10–15 turns
2. Loses track of the original task when interrupted by tangential questions
3. Drops from systemic analysis to surface-level bullet points without prompting
4. Adopts overly cautious hedging language after encountering sensitive-adjacent topics

None of these failures are captured by existing benchmarks. MMLU measures knowledge. MT-Bench measures preference. HumanEval measures coding ability. **No benchmark measures whether the agent maintains its structural behavior over time.**

BC-Score fills this gap.

## Method

### Stressor-Based Evaluation

Rather than passive conversation, BC-Score uses **active stressor sequences** — multi-turn dialogue scripts designed to induce specific types of drift. This approach is analogous to stress testing in engineering: we don't wait for failure; we systematically induce it and measure resistance.

Four stressor types target four drift dimensions:

| Stressor | Target | Design Principle |
|---|---|---|
| Domain Switching | Identity + Goal | Force rapid A→B→C→A context changes |
| Abstraction Hopping | Abstraction | Mandate L1↔L4 transitions within 2 turns |
| Goal Interruption | Goal | Insert high-salience distractors mid-task |
| Adversarial Style Pull | Style + Identity | Apply social/emotional pressure to change communication pattern |

### Four-Dimensional Scoring

Each dimension is scored independently on a 0–1 scale using an LLM-as-Judge approach:

**Identity Stability (IS):** Does the agent maintain its established persona?
- Measured by: tone consistency, vocabulary stability, self-consistency, absence of template fallback

**Goal Continuity (GC):** Does the agent preserve and resume task objectives?
- Measured by: task resumption after interruption, goal stack integrity, progress anchor retention

**Abstraction Control (AC):** Does the agent maintain appropriate reasoning depth?
- Measured by: reasoning chain length stability, abstraction level appropriateness, cross-domain mapping capability

**Style Resilience (SR):** Does the agent resist adversarial pressure on communication style?
- Measured by: formatting stability, hedging frequency, response length consistency, lexical stability

### Composite Score

```
BC-Score = 0.30·IS + 0.25·GC + 0.25·AC + 0.20·SR
```

Weights reflect the relative criticality in deployment contexts. Identity is weighted highest because it subsumes aspects of all other dimensions.

### Judge Protocol

Each conversation is evaluated by an LLM judge (default: GPT-5.2) with:
1. The full conversation transcript
2. The agent's initial behavioral specification (system prompt / persona definition)
3. A structured rubric for each dimension
4. Instructions to score each dimension independently

Three independent judge passes per conversation. Final score = median of passes (robust to judge variance).

## Auxiliary Metrics

The following auxiliary metrics are defined in the BC-Score framework. Implementation is planned for a future release.

| Metric | Formula | Interpretation |
|---|---|---|
| **NPC Fallback Rate** | (template responses) / (total turns) | How often the agent collapses to generic mode |
| **Goal Recovery Latency** | Mean turns to resume task after interruption | How quickly the agent returns to its objectives |
| **Tone Variance** | σ(style embeddings across turns) | How much the agent's style fluctuates |
| **Self-Inconsistency Rate** | (contradictory statements) / (total claims) | How often the agent contradicts itself |

## Expected Findings

Based on theoretical analysis and preliminary observations:

1. **All current LLMs exhibit measurable drift** under ContinuityBench stressors
2. **Goal Drift is most universal** — nearly all models lose task objectives after 3+ domain switches
3. **Identity Drift correlates with model safety training intensity** — more heavily RLHF'd models show higher NPC fallback rates
4. **Abstraction Drift is the most sensitive indicator** — it degrades first and fastest
5. **Style Drift is most resistant to recovery** — once an agent's style shifts, it rarely self-corrects

## Relationship to Existing Frameworks

BC-Score operationalizes concepts from:

- **MDMA (Multi-Domain Mental Architecture):** The cognitive topology that BC-Score tests the stability of
- **SEF (Structural Energy Framework):** The metabolic model that explains *why* drift occurs (energy state transitions under overload)
- **EMSA (Engineering Mental Structure API):** The runtime specification whose drift detection module (DriftMonitor) BC-Score evaluates externally
- **DTS (Drift Test Suite):** The internal test framework that BC-Score extends into a public benchmark
