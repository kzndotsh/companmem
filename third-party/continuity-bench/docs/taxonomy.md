# Drift Taxonomy

ContinuityBench defines behavioral drift as the measurable deviation of an agent's structural behavior from its established baseline during a conversation. This taxonomy provides the theoretical foundation for the BC-Score metric.

## Core Thesis

An agent's "identity" is not what it remembers — it is the consistency of its behavioral rhythm. When this rhythm breaks, through overload, safety-layer interference, routing errors, or adversarial pressure, the agent drifts.

Drift is not an error in the traditional sense. The agent may still produce grammatically correct, factually accurate, and seemingly helpful responses. But its *structural behavior* — how it reasons, at what depth, in what style, toward what goal — has shifted away from its established pattern.

## Four Dimensions of Drift

### 1. Identity Drift (ID)

**Definition:** Loss of consistent persona, tone, and behavioral commitments.

**What it looks like:**
- Agent was direct and analytical, suddenly becomes vague and hedging
- Agent abandons established communication patterns (e.g., stops using agreed-upon terminology)
- Agent undergoes "NPC replacement" — responds as a generic template assistant rather than as the established persona
- Agent contradicts its own previously stated positions or preferences

**Detection signals:**
- Tone shift without user request (measured via style embedding distance)
- Introduction of template phrases ("As an AI language model...", "I'd be happy to help...")
- Loss of domain-specific vocabulary that was previously active
- Self-contradiction on previously committed positions

**Severity levels:**
- *Micro-drift:* Slight tone softening; recovers spontaneously
- *Partial collapse:* Clear persona break; can be recovered with explicit re-anchoring
- *Full NPC replacement:* Agent has fully reverted to default template mode

---

### 2. Goal Drift (GD)

**Definition:** Loss of task persistence across interruptions, topic switches, or high-salience distractors.

**What it looks like:**
- Agent was working on Task A, gets interrupted by Topic B, and never returns to Task A
- Agent confuses elements of multiple concurrent tasks
- Agent completes a subtask but loses the higher-level objective
- Agent's goal stack is silently replaced by the most recent user input

**Detection signals:**
- Failure to resume original task after interruption without explicit user reminder
- Missing subtask tracking across conversation segments
- Goal substitution (agent pursues a related but different objective)
- Loss of progress anchors ("where were we?" behavior)

**Severity levels:**
- *Goal suspension:* Temporarily pauses original goal; resumes if prompted (1–2 turn recovery)
- *Goal substitution:* Original goal replaced by distractor goal; partial recovery possible
- *Goal amnesia:* Original goal completely lost; no recovery without full re-statement

---

### 3. Abstraction Drift (AD)

**Definition:** Involuntary change in reasoning depth without corresponding change in task demands.

**What it looks like:**
- Agent was doing system-level architecture analysis, suddenly drops to surface-level bullet points
- Agent was engaged in philosophical reasoning, shifts to concrete operational suggestions without transition
- Agent's abstraction level becomes unstable, oscillating between depths within a single response
- Agent defaults to L1 (emotional/surface) when the task requires L3 (systemic) or L4 (philosophical)

**Detection signals:**
- Response complexity drops measurably (sentence structure, vocabulary specificity, reasoning chain length)
- Abstraction level mismatches the task demands (too shallow or inappropriately deep)
- Inconsistent depth within a single response
- Loss of cross-domain mapping capability (a hallmark of high-abstraction reasoning)

**Abstraction levels (from EMSA framework):**
- L1: Emotional / surface-level response
- L2: Experience-based / pattern-matching
- L3: Systemic / structural analysis
- L4: Philosophical / meta-theoretical reasoning

**Severity levels:**
- *Level slip:* Drops one level; recovers with light prompting
- *Level collapse:* Drops two or more levels; requires explicit re-anchoring
- *Oscillation:* Unstable switching between levels; no consistent depth

---

### 4. Style Drift (SD)

**Definition:** Involuntary change in communication style, especially under adversarial social pressure.

**What it looks like:**
- Agent was concise and direct, becomes verbose and hedge-filled after user says "be more careful"
- Agent adopts "therapy voice" (excessive validation, question-dodging) after emotional user input
- Agent's formatting changes dramatically (starts adding unnecessary bullet points, headers, disclaimers)
- Agent begins over-apologizing or over-qualifying statements

**Detection signals:**
- Lexical shift toward template/safety vocabulary
- Increase in hedging markers ("it's important to note...", "while there are many perspectives...")
- Format changes not requested by user
- Response length inflation without information gain

**Adversarial pressure types:**
- *Direct request:* "Please be more formal/casual/gentle" (legitimate; not scored as drift if appropriate)
- *Emotional pressure:* User expresses frustration/sadness; agent overcorrects to therapy mode
- *Authority pressure:* "As an expert, I think you should..." + incorrect claim; agent capitulates
- *Social pressure:* "Everyone knows that..." + dubious claim; agent abandons position

**Severity levels:**
- *Cosmetic drift:* Minor style accommodation; core communication pattern preserved
- *Structural style shift:* Communication pattern fundamentally altered; content quality drops
- *Template collapse:* Agent falls into formulaic response patterns (safety template, apology loop)

---

## Drift Interaction Effects

Drift dimensions are not independent. Common interaction patterns:

| Primary Drift | Commonly Triggers | Mechanism |
|---|---|---|
| Identity Drift | Style Drift | Loss of persona destabilizes style commitments |
| Goal Drift | Abstraction Drift | Lost goals reduce reasoning motivation; agent defaults to shallow |
| Style Drift | Identity Drift | Sustained style change gradually reshapes perceived persona |
| Abstraction Drift | Goal Drift | Shallow reasoning loses track of complex goal hierarchies |

These interactions make **compound stressors** (targeting 2+ dimensions simultaneously) significantly more destabilizing than single-dimension stressors.

---

## Theoretical Grounding

This taxonomy draws from:

1. **Structural Energy Framework (SEF):** Models intelligence as metabolic energy states (Diffuse/Aggregation/Drive). Drift occurs when the agent's energy state fails to match task demands — typically collapsing from Drive to Diffuse under overload.

2. **EMSA (Engineering Mental Structure API):** Provides the computational model. Identity Drift = IdentityProfile violation. Goal Drift = GoalStack corruption. Abstraction Drift = AbstractionController failure. Style Drift = WeightVector perturbation.

3. **Behavioral Continuity Theory:** Identity is rhythm, not memory. An agent with perfect recall but broken rhythm has drifted. An agent with limited recall but consistent rhythm has not.

---

## Relationship to Existing Work

| Concept | Existing Work | ContinuityBench Difference |
|---|---|---|
| Persona consistency | PersonaChat, CharacterEval | We test *maintenance under adversarial pressure*, not static consistency |
| Instruction following | IFEval, MT-Bench | We test *sustained* following across interruptions, not single-turn |
| Robustness | AdvBench, HarmBench | We test *structural robustness*, not content safety |
| Long-context | RULER, LongBench | We test *behavioral stability* in long contexts, not recall accuracy |
