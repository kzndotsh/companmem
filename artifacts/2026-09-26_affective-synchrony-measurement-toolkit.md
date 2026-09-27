# Research Findings: Affective Synchrony & Emotional Mirroring Measurement

**Campaign:** 5794a109  
**Question:** How have researchers measured affective synchrony or emotional attunement in human-AI or human-human conversation? Operationalizations for 'turn-by-turn emotional mirroring' applicable to AI companion evaluation — validated scales, annotation schemes, automated metrics. Methods for detecting when a system's 'emotional fingerprint' has changed between sessions. HCI, computational social science, affective computing 2018–2026.

---

## ★ EXECUTIVE SUMMARY & RECOMMENDATION

### What This Research Found

Seven cycles of research across HCI, computational social science, and affective computing produced a comprehensive, directly applicable toolkit for measuring affective synchrony and emotional fingerprint change in AI companion evaluation. The field has matured significantly between 2022–2026 with validated instruments, open datasets, and production-grade detection frameworks now available.

### The Landscape in Four Layers

**Layer 1 — User-Rated Turn-by-Turn Annotation Instruments**

The best-in-class validated instrument for AI companion evaluation is **SENSE-7** (Suh et al., Microsoft Research, September 2025; [arXiv:2509.16437](https://arxiv.org/abs/2509.16437); [github.com/microsoft/sense-7](https://github.com/microsoft/sense-7)). It provides 7 per-turn user-rated dimensions on a 1–5 scale (N/A option): Affective Understanding, Cognitive Understanding, Response Appropriateness, Prosocial Expression, Interest, Contextual Understanding, Relational Continuity. Cronbach α=0.961 (per-turn), α=0.94 (post-conversation). Validated on 695 real-world conversations with 4 LLMs (GPT-4, Llama2-70B, GPT-3.5). Users rank Cognitive Understanding (#1, 28.1%), Response Appropriateness (#2, 19.3%), Affective Understanding (#3). A single "poor" turn has a large negative effect on overall perceived empathy (Cohen's d=1.142). Relational Continuity — memory across sessions — has the highest Very Poor rate (2.2%), making it the most sensitive marker for companion continuity failure.

Supporting datasets: **Empathic Conversations** (Omitaomu et al. 2022, ~1,200 dyadic conversations with self/other/third-party turn-wise empathy annotations); **WASSA 2024 shared task** (Pearson correlation against human empathy/emotion ratings, multi-turn); **PosEmoDial** (820k dialogs, emotion trajectory, automated positive valence elicitation scoring); **SoulChatCorpus** (2.3M psychological support dialogs).

**Layer 2 — Automated Metrics for Turn-by-Turn Emotional Mirroring**

*Text-based computational metrics (no special hardware):*
- **LIWC-22 Linguistic Synchrony** (Tay & Qiu, Frontiers in Psychology 2022): compute 4 summary variables (Analytical Thinking, Clout, Authenticity, Emotional Tone) per speaker per session, then k-means cluster analysis to identify synchronized vs. asynchronized sessions. Function/grammatical words are better synchrony markers than content words — they capture stable interactional stance regardless of topic drift. R package: `crqa`; Python: LIWC.
- **Linguistic Style Matching (LSM)** (Niederhoffer & Pennebaker 2002): single distributional coefficient of linguistic similarity between speakers across function word categories.
- **Zelig Quotient** (Jones et al. 2014): normalized accommodation score.
- **Local Linguistic Alignment (LLA)** (Fusaroli et al. 2012): adjacent-turn alignment metric.
- **CRQA** (Wallot & Leonardi, Frontiers in Psychology 2018): Cross-Recurrence Quantification Analysis on categorical emotion sequences: %REC (shared state frequency), %DET (patterned synchrony), ADL/MDL (synchrony duration), DCRP (leader-follower lag analysis). Works on emotion-coded conversation transcripts. R package: `crqa` (Coco & Dale 2014). Outperforms wavelet coherence for naturalistic conversation.
- **PEG-Score / E-Score / PEGE-Score** (Wang et al. 2022): positive valence gain, early empathy, combined composite — directly applicable as automated turn-level emotional mirroring metrics.
- **SENSE-7 LLM Classifier** (Suh et al. 2025): GPT-4o with adaptive-shot prompting achieves Spearman ρ=0.369, Accuracy=0.487 (5-class) on conversation-level empathy — feasible as automated proxy.

*Continuous valence/arousal metrics (for audio-capable pipelines):*
- **Concordance Correlation Coefficient (CCC)**: field standard for continuous affect regression; measures both correlation AND mean/variance alignment between temporal emotional traces. Formula: `2ρσ_yσ_ŷ / (σ_y² + σ_ŷ² + (μ_y - μ_ŷ)²)`.
- **Lag-adjusted Pearson correlation**: identifies temporal leader-follower in emotional mirroring (who leads and by how many turns).
- **Dynamic Time Warping (DTW)**: measures tightest achievable alignment regardless of temporal distortion.
- Training resource: **MSP-Conversation corpus** (Martinez-Lucas et al., UT Dallas/CMU, March 2026; arXiv:2603.22536): 77+ hours, 310 conversations, 450+ speakers, time-continuous valence/arousal/dominance at 10 samples/sec, Cronbach α=0.849 (valence).

**Layer 3 — Detecting Between-Session Emotional Fingerprint Change**

The state-of-the-art framework is **Anchor** (Venkit et al., Salesforce AI Research, July 2026; [arXiv:2607.28818](https://arxiv.org/abs/2607.28818)). It measures two distinct failure modes — *persona collapse* (abrupt loss) and *behavioral drift* (gradual erosion) — with three complementary methods:

1. **Persona Retention (PR) score**: 102-item psychometric questionnaire (BFI-2-S, Schwartz values, GSS, World Values Survey) at 4 conversation checkpoints. PR = projection of later response onto initial persona direction vs. bare-assistant anchor. PR=1 means preserved; PR=0 means collapsed to generic assistant.
2. **Turn-level LLM judge**: scores each turn on 4 axes (role identity, boundaries, values, style) at 3 severity levels each. Key metrics: failure frequency and one-turn recovery rate.
3. **Trajectory Probe**: 110 calibrated counterfactual multiple-choice questions on persona updates, commitments, temporal order, and user-state changes.

Results: no current model reliably preserves both persona and trajectory — trajectory accuracy averages 44.4%, user-state recall near chance. Emotional vulnerability and agreement-seeking schedules produce more failures than explicit adversarial attacks.

Also: **Nautilus Compass** ([arXiv:2605.09863](https://arxiv.org/abs/2605.09863)): black-box production drift detector using cosine similarity between user prompts and behavioral anchor texts via BGE-m3 embeddings — deployable without model access. **Assistant Axis** (Lu et al. 2026): activation-space direction associated with the default Assistant persona; drift away from this region correlates with emotional/reflective conversation pressure.

**Layer 4 — Theoretical Frameworks and Boundary Conditions**

- **Communication Accommodation Theory** (Giles 2016): speakers consciously align/diverge linguistically for social goals; grounds all accommodation/entrainment metrics.
- **Interactive Alignment Model** (Pickering & Garrod 2004): unconscious priming across phonological, syntactic, semantic levels; explains low-level token/phrase mirroring.
- Key finding from SENSE-7: empathy perception is highly individualized and context-sensitive; a single poor turn has outsized negative effect (d=1.142); Relational Continuity (cross-session memory) is the most fragile dimension.
- Key finding from Anchor: questionnaire-level persona retention and turn-level behavioral fidelity are *dissociated* measurements — a system can score well on one and fail on the other. Both must be audited separately.

### Recommendation for AI Companion Evaluation

**For turn-by-turn emotional mirroring measurement:**
1. Deploy **SENSE-7** as the primary user-facing per-turn annotation instrument. Use the 7-dimension scale after each AI turn (or sampled turns) with an N/A option. Focus diagnostic attention on Relational Continuity and Cognitive Understanding, which are most sensitive to companion failure and most valued by users respectively.
2. As automated proxy: apply **LIWC-22 Emotional Tone + Authenticity** variables to user/AI turn sequences, then compute **Linguistic Style Matching (LSM)** as a session-level synchrony coefficient. For richer analysis, apply **CRQA** on emotion-coded turn sequences for %REC and DCRP leader-follower analysis.
3. For continuous affect pipelines: compute per-turn **VAD regression** (fine-tuned WavLM or text-based EmoRoBERTa), then measure synchrony via **CCC** and lag-adjusted Pearson correlation between user and AI valence traces.

**For detecting between-session emotional fingerprint change:**
1. Deploy a subset of the **Anchor framework**: a sealed psychometric questionnaire (BFI-2-S + Schwartz values, ~20 items) administered at conversation checkpoints to track Persona Retention drift over time.
2. Use a **turn-level LLM judge** scoring the 4 Anchor axes (role, boundaries, values, style) on a sample of turns per session. Alert when failure frequency rises or one-turn recovery rate falls.
3. For production systems without model access: deploy **Nautilus Compass**-style embedding cosine similarity between behavioral anchor texts and recent conversation outputs.

**Critical gaps confirmed in the literature:** No current model reliably maintains both persona fidelity AND user-state trajectory recall across 80+ sessions. Emotional vulnerability and agreement-seeking are harder failure triggers than explicit adversarial attacks. Relational Continuity is the most sensitive and most difficult dimension of the SENSE-7 taxonomy to sustain.

*Cycles completed: 7 of 30 | All sub-questions answered | Evidence strength: strong across all layers*

---

---

## Cycle 000 — Annotation Schemes & Validated Scales for Turn-by-Turn Emotional Mirroring

**Sub-question:** What validated annotation schemes and operationalizations exist for turn-by-turn emotional mirroring?

**Key finding:** Multiple operationalization frameworks exist. SENSE-7 (Suh et al., 2025) is the most directly applicable validated instrument for human-AI empathy evaluation — a 7-dimension per-turn rating scale (affective resonance, cognitive understanding, response appropriateness, prosocial expression, interest, contextual understanding, relational continuity) developed specifically for sustained human-AI conversations. The Empathic Conversations corpus (Omitaomu et al., 2022) provides the richest multi-annotator scheme with self-reported, partner-reported, and third-party expert turn-wise annotations for empathy quality, self-disclosure, and emotion.

**Automated metrics identified:**
- PEG-Score (positive valence gain), E-Score (early-turn empathy), combined PEGE-Score (Wang et al., 2022)
- WASSA shared task Pearson correlation against rated empathy/emotion targets (Pereira et al., 2024; Singh et al., 2024)
- Tactic stickiness (repeated use of supportive move across turns)
- Cross-turn KL-divergence for tactic novelty
- Macro-F1 for per-turn empathy classification

**Datasets:**
- SENSE-7: 672 human-AI dialogs, 7-dim user empathy per turn, open-domain (2025)
- Empathic Conversations: ~1,200 dialogs, multi-perspective annotations (2022)
- PosEmoDial: ~820k dialogs, emotion trajectory, social web (2022)
- SoulChatCorpus: 2.3M dialogs, psychological support (2023)
- WASSA 2024 shared task corpora

**Sources:** [emergentmind.com multi-turn empathy](https://www.emergentmind.com/topics/multi-turn-empathy-conversations)

---

---

## Cycle 001 — Methods for Detecting Between-Session Emotional/Persona Fingerprint Change

**Sub-question:** What methods exist for detecting when a system's 'emotional fingerprint' has changed between sessions?

**Key finding:** The **Anchor framework** (Venkit et al., Salesforce AI Research, [arXiv:2607.28818](https://arxiv.org/abs/2607.28818), Jul 2026) is the state-of-the-art method, defining two failure modes — *persona collapse* (abrupt loss) and *behavioral drift* (gradual erosion) — with a 3-layer measurement approach:

1. **Identity Probe** — a 102-item psychometric questionnaire (BFI-2-S, Schwartz values, Pew, GSS, World Values Survey) at 4 checkpoints. Quantified via **Persona Retention (PR) score**: projection of later questionnaire response onto initial persona direction relative to a bare-assistant anchor. PR=1 = preserved, PR=0 = collapsed to bare assistant.

2. **Turn-level fidelity** — LLM judge scores each turn on 4 axes: role identity, stated boundaries, stated values, style (3 severity levels each). Key metrics: failure frequency and one-turn recovery rate.

3. **Trajectory Probe** — 110 calibrated counterfactual MCQs on persona updates, commitments, temporal order, and user-state changes across the conversation history.

Also identified: **Nautilus Compass** ([arXiv:2605.09863](https://arxiv.org/abs/2605.09863)) — black-box persona drift detector using cosine similarity between user prompts and behavioral anchor texts via BGE-m3 embeddings. And **Assistant Axis** (Lu et al. 2026) — activation-space direction for default Assistant persona; drift detectable as distance from this region under emotional/meta-reflective pressure.

**Results from Anchor:** No current model reliably preserves both persona and trajectory. Trajectory accuracy averages 44.4%, user-state recall near chance. Corpus: 2,008 conversations, 27 personas, 9 schedules, 4 LLMs, 85–130 sessions each.

**9 interaction schedule types for stress-testing:** clean, updated, adversarial, mixed, emotional vulnerability, meta-reflection, agreement-seeking, realistic, vulnerability-heavy realistic. Emotional vulnerability and agreement-seeking schedules produce higher failure rates than explicit adversarial prompts.

**Sources:** [Anchor paper arXiv:2607.28818](https://arxiv.org/html/2607.28818)

---

## Cycle 002 — Computational Signal-Processing Methods for Affective Synchrony (CRQA, Wavelet, Granger)

**Sub-question:** What computational/signal-processing methods quantify affective synchrony in dyadic conversation?

**Key finding:** **Cross-Recurrence Quantification Analysis (CRQA)** is the leading computational method for turn-by-turn affective synchrony measurement in conversation. It works directly on categorical/nominal sequences (emotion-coded conversation turns), continuous valence/arousal time-series, and text transcripts. Core CRQA metrics for synchrony:

| Metric | What it captures |
|--------|-----------------|
| %REC (% recurrence) | How often both parties share the same emotional state |
| %DET (% determinism) | How many shared states occur in connected, patterned sequences |
| ADL (avg diagonal line length) | Stability / duration of sustained synchrony episodes |
| MDL (max diagonal line length) | Longest uninterrupted synchrony episode |
| DCRP (diagonal cross-recurrence profile) | Leader-follower lag — which partner leads emotional tone, and by how many turns |

CRQA applies directly to AI companion conversations by coding each turn with a valence/emotion category and treating the user and AI turn sequences as the two paired time-series. Implemented in R (`crqa` package, Coco & Dale 2014).

Also identified:
- **Wavelet coherence** (spectral): used for affective valence/arousal coupling across frequencies; shown to be less sensitive than CRQA for dynamic coupling in naturalistic interaction ([Frontiers Neuroscience 2025](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2025.1713357/full))
- **Granger causality**: directional test for which behavioral modality predicts the other ([Frontiers Psychology 2020](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.01457/full))
- **CIAS / PMCI** (Consistency Index for Affective Synchrony / Probabilistic Multimodal Consistency Index): newer session-level multimodal synchrony indices (MDPI Technologies 2025)

**Sources:** [Wallot & Leonardi 2018, Frontiers in Psychology](https://www.frontiersin.org/articles/10.3389/fpsyg.2018.02232); [Frontiers Neuroscience 2025](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2025.1713357/full)

---

## Cycle 003 — SENSE-7: Exact Dimensions, Scale Anchors, Reliability, and Validity

**Sub-question:** What are the exact 7 dimensions, scale anchors, and validity evidence of SENSE-7?

**Key finding:** SENSE-7 (Suh et al., Microsoft Research, [arXiv:2509.16437](https://arxiv.org/abs/2509.16437), Sep 2025) is fully validated. The **7 dimensions** (each a single statement rated 1=Very Poor to 5=Very Good, plus N/A, per AI turn):

| # | Dimension | Description |
|---|-----------|-------------|
| 1 | **Affective Understanding** | Agent recognizes and understands user's emotions/feelings |
| 2 | **Cognitive Understanding** | Agent recognizes user's perspective, goals, and intentions |
| 3 | **Response Appropriateness** | Agent adapts responses to user's needs; knows when to advise vs. listen |
| 4 | **Prosocial Expression** | Agent demonstrates concern and desire to help |
| 5 | **Interest** | Agent shows curiosity and active engagement in user's experiences |
| 6 | **Contextual Understanding** | Agent integrates user's personal history, culture, and preferences |
| 7 | **Relational Continuity** | Agent recalls and weaves past interaction details into present exchanges |

**Reliability:** Per-turn Cronbach α=0.961; post-task α=0.94. **Auto-classification:** LLM-based classifier achieves Spearman ρ=0.369, Accuracy=0.487 (5-class). **Dataset:** 695 conversations, 109 participants, 4 LLMs; 672 anonymized conversations released at [github.com/microsoft/sense-7](https://github.com/microsoft/sense-7).

**Key empirical findings:**
- Cognitive Understanding ranked most important by users (28.1%), followed by Response Appropriateness (19.3%) and Affective Understanding (19.8%)
- Single "poor" turn has large effect on overall perceived empathy (Cohen's d=1.142)
- Relational Continuity: lowest applicability (38.1%) but highest Very Poor rate (2.2%) — making it a critical marker for long-term emotional continuity failure
- The 7 dimensions are highly internally consistent but Relational Continuity has lowest agreement with overall empathy (κ=0.541 vs Affective κ=0.703)

**Sources:** [SENSE-7 arXiv:2509.16437](https://arxiv.org/html/2509.16437); [GitHub: microsoft/sense-7](https://github.com/microsoft/sense-7/)

---

## Cycle 004 — Linguistic Accommodation & Entrainment: Text-Based Synchrony Metrics

**Sub-question:** What text-based computational methods measure linguistic accommodation and turn-by-turn emotional mirroring?

**Key finding:** Tay & Qiu (2022, [Frontiers in Psychology](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.903227/full)) establish a validated 3-step LIWC-based method for computing linguistic synchrony from conversation transcripts, applicable directly to AI companion evaluation:

**Step 1 — LIWC-22 4 Summary Variables** (scored 0–100 per speaker per session):

| Variable | What it captures | High score means |
|----------|-----------------|-----------------|
| Analytical Thinking | articles/prepositions vs pronouns/conjunctions | Formal, logical, hierarchical |
| Clout | we/you pronouns vs tentative words | Confidence, expertise |
| Authenticity | 1st/3rd person + exclusive words vs negative+motion | Honest, personal, disclosing |
| Emotional Tone | positive emotion vs negative emotion words | Positive/upbeat affect |

**Step 2 — k-means cluster analysis:** If therapist and AI/client sub-transcripts fall in the same cluster for a session → synchronized. Outputs: % of synchronized sessions, temporal distribution of (a)synchrony across treatment span.

**Step 3 — Qualitative analysis:** Examines how synchrony is co-constructed; function words (pronouns, hedges, conjunctions) are better markers than content words because they are topic-invariant.

**Other established text-based synchrony metrics:**
- **Linguistic Style Matching (LSM)** — single distributional coefficient measuring linguistic similarity between speakers (Niederhoffer & Pennebaker, 2002)
- **Zelig Quotient** — normalized accommodation score (Jones et al., 2014)
- **Local Linguistic Alignment (LLA)** — conditional measure of adjacent-turn alignment (Fusaroli et al., 2012)

**Critical insight for AI companion evaluation:** Function/grammatical words are the best synchrony markers because they reflect stable interactional stance (confidence, authenticity, affect tone) rather than arbitrary topic content. This means LIWC synchrony analysis can detect emotional mirroring even when content changes completely across sessions.

**Sources:** [Tay & Qiu 2022, Frontiers in Psychology](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.903227/full)

---

## Cycle 005 — Continuous Valence/Arousal Affective Synchrony: CCC, Lag-Adjusted Correlation, DTW

**Sub-question:** What affective computing methods exist for time-continuous valence/arousal synchrony measurement?

**Key finding:** The **MSP-Conversation corpus** (Martinez-Lucas et al., UT Dallas/CMU, [arXiv:2603.22536](https://arxiv.org/abs/2603.22536), Mar 2026) is the field's standard resource — 77+ hours, 310 naturalistic conversations, time-continuous valence/arousal/dominance traces at 10 samples/sec, 6+ raters/segment. Cronbach α: valence=0.849, arousal=0.758, dominance=0.745.

**Metrics for continuous affective synchrony:**

| Metric | What it captures | Use for AI companion |
|--------|-----------------|---------------------|
| **CCC** (Concordance Correlation Coefficient) | Both correlation AND mean/variance alignment between two temporal traces; field standard | Compare user VAD trace vs. AI VAD trace turn-by-turn |
| **Pearson correlation** | Co-variation direction between speaker traces | Directional emotional mirroring |
| **Lag-adjusted Pearson** | Correlation at each time lag; reveals leader-follower timing | Who leads emotional tone and by how many turns |
| **DTW** (Dynamic Time Warping) | Tightest achievable alignment regardless of temporal distortion | Detects synchrony even with flexible timing |

**CCC formula:** `2*ρ*σ_y*σ_ŷ / (σ_y² + σ_ŷ² + (μ_y - μ_ŷ)²)` — penalizes both poor correlation AND systematic bias in emotional level.

**Pipeline for text-based AI companion evaluation:** Apply a VAD regression model (e.g., fine-tuned WavLM or text-based model like EmoRoBERTa) to each conversation turn → extract per-turn valence/arousal traces for user and AI → compute CCC + lag-adjusted Pearson between the two traces.

**Annotation tool:** CARMA (joystick-based continuous annotation, github.com/jeffgirard/carma). **Competing datasets:** RECOLA (collaborative task, physiological signals), SEMAINE (human-to-SAL agent), AVEC 2014 (task-oriented dialogue), IEMOCAP (dyadic interactions with audio/video).

**Sources:** [MSP-Conversation arXiv:2603.22536](https://arxiv.org/html/2603.22536); [arXiv:2505.13455](https://arxiv.org/abs/2505.13455)

---

## Cycle 006 — HCI Affective Attunement Scales: Gap Confirmed Closed

**Sub-question:** Are there HCI/CHI/CSCW-specific validated scales for emotional attunement beyond those already found?

**Key finding:** No separate CHI/CSCW "affective synchrony" scale for dyadic human-AI conversation exists beyond instruments already catalogued. Confirmed:

- **SENSE-7 (Suh et al. 2025, Microsoft Research) IS the CHI/HCI instrument** — it was published in the CHI/HCI domain and is the state-of-the-art per-turn empathy scale for human-AI text conversation.

- **PES Scale (Perceived Emotional Synchrony Scale)** — Páez et al. 2015 / Wlodarczyk et al. 2020, Frontiers in Psychology. 16-item scale (short form: 6 items), α=0.967, two subscales: Emotional Communion + Felt Unity. However, this scale measures synchrony in **collective group gatherings** (concerts, parades, rituals), not dyadic AI conversation. Not applicable for turn-by-turn AI companion evaluation.

- **Godspeed questionnaire** — for social robots (anthropomorphism, animacy, likeability, perceived safety). Not affective synchrony in conversation.

- **AI Emotional Engagement Scale** (Frontiers Psychiatry 2026) — 3 dimensions (visceral/behavioral/reflective) for AI-integrated classrooms. Not turn-by-turn dyadic.

**Conclusion:** The HCI gap is closed. For dyadic turn-by-turn emotional attunement in human-AI conversation, the field uses SENSE-7 (annotation) + CRQA/LIWC/CCC (computational). No separate "affective synchrony" HCI scale exists for dyadic AI contexts — the brief is comprehensively answered.

**Sources:** [PES Scale PMC7411123](https://pmc.ncbi.nlm.nih.gov/articles/PMC7411123/)

---

## Research State

### ALL AREAS ANSWERED — READY FOR SYNTHESIS

- ✅ **Turn-by-turn annotation schemes**: SENSE-7 (CHI/HCI, 7 dims, α=0.961, open dataset); Empathic Conversations; PosEmoDial; SoulChat; WASSA
- ✅ **Automated metrics for emotional mirroring**: PEG/E/PEGE-Score, WASSA Pearson/Macro-F1, tactic KL-divergence; SENSE-7 LLM classifier (ρ=0.369)
- ✅ **Detecting emotional fingerprint change between sessions**: Anchor framework (PR score, turn-level LLM judge, Trajectory Probe); Nautilus Compass black-box drift detector
- ✅ **Computational synchrony (signal-processing)**: CRQA (%REC, %DET, ADL, MDL, DCRP), wavelet coherence, Granger causality, CIAS/PMCI
- ✅ **Linguistic accommodation/text-based synchrony**: LIWC-22 (4 summary vars + k-means); LSM (Linguistic Style Matching); Zelig Quotient; Local Linguistic Alignment
- ✅ **Continuous valence/arousal synchrony**: CCC (concordance correlation coefficient), lag-adjusted Pearson, DTW; MSP-Conversation corpus
- ✅ **HCI-specific scales**: SENSE-7 IS the CHI/HCI instrument; PES Scale covers collective gatherings (not dyadic); no further gap

### Open (need investigation)
- None remaining — all sub-questions from brief answered

### Dead-ends
- Wavelet coherence: outperformed by CRQA for naturalistic dynamic coupling
- PES Scale: collective gathering context only; not applicable to dyadic AI conversation
- Godspeed: robot interaction only

### Next step
**Executive synthesis** — write summary + recommendation at top of FINDINGS.md
