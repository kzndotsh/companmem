# Research Findings: When AI Agents Should Suppress/Withhold Information (Social/Relational Judgment)

**Campaign:** 024dbb2e  
**Question:** What has been proposed, tested, or theorized about when AI conversational agents should suppress or withhold information — not due to privacy policy, but due to social or relational judgment?

---

## EXECUTIVE SUMMARY & RECOMMENDATION

*Synthesized from 8 research cycles, covering literature 2018–2026 across HCI, AI safety/alignment, personalization, and conversational agents. All five areas the brief specifies are covered.*

---

### Core Finding

A substantial and rapidly maturing body of research now directly addresses when AI agents should suppress information due to social/relational judgment — distinct from privacy policy compliance. The field has converged on a unified conceptual framework built around four interlocking concepts: **contextual integrity norms**, **current-turn warrant**, **memory boundary fit**, and **civility/relational state**. An agent should suppress information when ANY of these four conditions is violated.

---

### The Unified Framework: Four Conditions for Suppression

**1. Contextual Integrity Violation (social norm breach)**
A disclosure is inappropriate when it violates the contextually appropriate norm for how information should flow in this specific relationship and setting. Nissenbaum's contextual integrity (CI) theory — now empirically operationalized for AI agents — holds that the same information can be appropriate in one context and a violation in another. Google DeepMind's Information Flow Card (IFC) mechanism operationalizes this: the agent reasons about sender, receiver, information type, subject, context, and purpose before deciding to surface or suppress. *Key condition against surfacing: when the information flow crosses contextual norms (e.g., a medical detail surfaced to a logistics contact; a sensitive financial fact included in an unrelated task).*

Sources: Ghalebikesabi et al. (2024, Google DeepMind), arXiv:2408.02373; ConfAIde (Mireshghallah et al., ICLR 2024); "Do Computer-Use Agents Follow Contextual Integrity?" arXiv:2606.23189

**2. Current-Turn Warrant Absent (conversational moment doesn't invite it)**
A memory is inappropriate to surface even if it is legitimately stored, accurately retrieved, and topically relevant — if the current conversational turn does not warrant its use. RBI-Eval (Xu et al., 2026) introduced this concept empirically: "whether the present user request provides sufficient justificatory basis for using prior stored history." Critical distinction: topical relevance ≠ permission. A fact can relate to the prompt while still being inappropriate to surface. *Key condition against surfacing: when the user's current request is answerable without the sensitive history, and nothing in the turn explicitly reopens or invites use of it.*

Source: Xu et al. (arXiv:2606.06055, Jun 2026); also Mireshghallah & Li (2025), "Position: Privacy Is Not Just Memorization!"

**3. Memory Boundary Fit Failure (information doesn't belong in this exchange)**
Users distinguish between AI memory that feels like attentiveness versus surveillance based on whether the remembered content fits the current exchange — regardless of sensitivity. Huang, Huang, Guo (2026, N=2,140, 6 LLM chat experiments) demonstrated this empirically: relevant-memory cues produce higher trust; intrusive-memory cues (cross-context, sensitive, surveillance-like) significantly reduce trust, data-sharing willingness, and relationship quality. The effect is amplified in sensitive domains (health vs. apparel). An editable memory dashboard raises average trust but does NOT reduce the intrusive-memory penalty — the judgment operates at the level of the individual reference, not the system's general privacy controls. *Key condition against surfacing: when the recalled information crosses a contextual boundary (e.g., surfacing browsing behavior about stress when asked for headphone recommendations; surfacing late-night patterns when giving product advice).*

Source: Huang, Huang, Guo (Frontiers in Psychology, Sep 2026), doi:10.3389/fpsyg.2026.1934857; also Gurney, Loewenstein, Chater (PLoS ONE, Apr 2024)

**4. Civility / Relational State Violation (social or personal boundary breach)**
Deng et al. (SIGIR 2024) formalized **Civility** as a first-class dimension of proactive conversational agents: respecting "physical, mental, and social boundaries set by the user, the conversational task, and general ethical standards." The named anti-pattern "Cosseter" (high intelligence, low civility) captures the exact failure mode the brief asks about: over-monitoring, excessively acquiring personal information, intrusive — like helicopter parenting. **Adaptivity** is the timing dimension: surfacing at the wrong conversational moment fails even if the content is contextually appropriate. *Key conditions against surfacing: (a) content would violate personal/social/ethical norms, (b) the user's real-time state doesn't warrant initiative, (c) surfacing would feel controlling.*

Source: Deng, Liao, Zheng, Yang, Chua (SIGIR 2024), arXiv:2404.12670; CHIIR 2026 workshop (Shah et al., arXiv:2608.18638)

---

### Empirical Evidence on User Responses

**When AI surfaces inappropriately:** Significant trust loss, reduced data-sharing engagement, lower relationship quality, and damaged loyalty intentions (Huang et al. 2026, N=2,140). The penalty is larger for sensitive domains and is not mitigated by user control interfaces. Longitudinal evidence (Sumida et al., ICMI 2026, N=24 × 10 sessions): memory failures cause relational *crashes* — one participant stopped treating the agent as a relationship partner after it surfaced a forgotten fact ("I switched to treating it more as speaking practice"). These crashes are harder to recover from than surges are to sustain.

**When AI withholds unexpectedly:** Conversational agents that withhold information users *expect* the agent to know trigger strongly negative inferences — more so than the same omission in non-conversational interfaces (Gurney et al., PLoS ONE 2024, N=3,517). Conversational pragmatics activates persuasion knowledge: users infer strategic concealment. The agent faces a **two-sided suppression problem**: surface inappropriately = intrusive; withhold expectedly-known info = deceptive. The solution is not suppression vs. disclosure, but *contextually fitted* disclosure.

---

### The Alignment Framing

PrivacyAlign (Tamber et al., arXiv:2606.21710, Jun 2026, Waterloo/ServiceNow) provides the definitive alignment framing: "Privacy is an important alignment problem for agents: every message, post, or tool call an agent makes is a contextual judgment about what is appropriate to share, with whom, and under which conditions." The brief's framing — "not due to privacy policy, but due to social or relational judgment" — IS the alignment framing. Current LLMs routinely fail: even GPT-5.5 leaks in 14.5% of scenarios. Training with human-annotated contextual appropriateness judgments (599 annotators) meaningfully improves alignment. The human annotation task explicitly asks: "what would feel invasive or unnecessary for the data subject" — this is social/relational judgment operationalized.

---

### The Recommender/Personalization Gap

The brief asks about recommender/personalization "do not surface" policies. The research reveals an important gap: platform reduction policies (YouTube's "Four Rs," Facebook's Content Distribution Guidelines, Instagram's Sensitive Content Control) address content-policy violations and harm prevention — NOT relational/social judgment about the user-agent relationship. This framing is entirely absent from the recommender literature. It belongs to conversational agent and AI memory literature. The closest analog in recommender systems is user-specified trigger warning avoidance (user preference enforcement), which is not agent-side social judgment.

Sources: Gillespie (Social Media + Society, 2022); Kovacs, Chee, Kazemian, Dean (ACM RecSys 2025)

---

### Proposed Mechanisms and Design Interventions

Across the literature, the following concrete mechanisms have been proposed or empirically tested for social/relational suppression:

**Retrieval-time:** Sensitivity-aware downranking of memories; exposure budgeting (limit how often sensitive memories surface in casual turns); retrieval selectivity; background-only tagging (inform tone but prevent explicit mention); per-topic sensitivity levels.

**Generation-time:** Prompt-level boundary policies ("only use prior context if explicitly invited by the current turn"); triage among mention / abstraction / avoidance; ask-before-use for high-sensitivity memories; explicit current-turn warrant check before integrating stored history.

**User-facing:** Interruption budgets; permission ladders; adjustable proactiveness levels; editable memory dashboards (note: effective for general trust but do not attenuate the intrusive-memory penalty for specific contextually-mismatched cues); per-topic memory-use preferences; review-and-revoke.

**Design principle (from longitudinal evidence):** Memory's goal is not to display recall but to use continuity "in ways that reopen prior topics, acknowledge personal context, and invite elaboration" — catalyzing deeper disclosure rather than demonstrating that the system knows things about the user.

---

### Key References (by area)

**Proactive agent design / calibrated initiative:**
- Deng et al. (SIGIR 2024) "Towards Human-Centered Proactive Conversational Agents" arXiv:2404.12670
- CHIIR 2026 Workshop Report (Shah et al.) arXiv:2608.18638

**Contextual integrity operationalization:**
- Ghalebikesabi et al. (2024, Google DeepMind) "Operationalizing Contextual Integrity in Privacy-Conscious Assistants" arXiv:2408.02373
- Mireshghallah et al. (ICLR 2024) "Can LLMs Keep a Secret?" (ConfAIde benchmark)
- "Do Computer-Use Agents Follow Contextual Integrity?" arXiv:2606.23189

**Memory-use boundaries / "do not surface" policies:**
- Xu et al. (Jun 2026) "When Should Memory Stay Silent: Measuring Memory-Use Boundaries" arXiv:2606.06055
- "Mitigating Over-Personalization in LLMs via Structured Memory" arXiv:2608.08300

**Empirical user studies — surfacing vs. withholding:**
- Huang, Huang, Guo (Frontiers in Psychology, Sep 2026) "Remembering or monitoring? Contextual fit of simulated AI memory cues and consumer trust" doi:10.3389/fpsyg.2026.1934857
- Gurney, Loewenstein, Chater (PLoS ONE, Apr 2024) "Conversational technology and reactions to withheld information" doi:10.1371/journal.pone.0301382
- Sumida et al. (ICMI 2026) "Memory-Driven Self-Disclosure and Relational Turning Points" arXiv:2607.14593

**AI alignment / privacy alignment:**
- Tamber et al. (Jun 2026) "PrivacyAlign: Contextual Privacy Alignment for LLM Agents" arXiv:2606.21710

**Recommender "do not surface" (content policy, not relational judgment):**
- Gillespie (Social Media + Society, 2022) "Do Not Recommend? Reduction as a Form of Content Moderation"
- Kovacs, Chee, Kazemian, Dean (ACM RecSys 2025) "Datasets for Navigating Sensitive Topics in Recommendation Systems"

---

### Recommendation

Designers of AI companions or personalized conversational agents seeking to operationalize socially/relationally appropriate suppression should use all four conditions as a combined decision gate, applied in this order: (1) Does the current conversational turn explicitly invite this information? If not → suppress by default. (2) Does the information flow violate contextual integrity norms for this sender/receiver/relationship? If yes → suppress. (3) Does the recalled content cross a contextual boundary (from a different context, involving sensitive personal data, surveillance-like)? If yes → suppress or at minimum abstract. (4) Would surfacing it violate the user's social/personal boundaries or feel controlling/intrusive? If yes → suppress. When all four conditions are passed, surface the information — but frame it to catalyze elaboration rather than demonstrate recall.

---



**Sub-question:** What frameworks exist for proactive agent design — specifically conditions for NOT surfacing information?

**Key finding:** The 2026 HCI research community has converged on **"calibrated initiative"** as the central framework for when proactive agents should NOT surface information. Conditions against surfacing: poor timing, insufficient grounding in user intent, stakes/reversibility not warranted, initiative would be intrusive or controlling. Restraint — "when to remain passive" — is a first-class design variable equal in status to action. Proposed mechanisms: interruption budgets, permission ladders, adjustable proactiveness levels, user-facing suppression controls. Workshop research agenda explicitly calls for "Design memory with boundaries" — selective suppression of remembered information as an accountable design component.

**Evidence strength:** moderate (single source, but a synthesis of a cross-disciplinary workshop)

**Sources:**
- [CHIIR 2026 Workshop Report: Human-Centered Proactive and Personalized Agents](https://arxiv.org/html/2608.18638) — Shah et al., August 2026. Kaur, Gupta, Roosta, Raju, Yang, Shah. University of Washington / AMD UC Berkeley / TikTok / Georgetown.

**Key references surfaced from this source:**
- Deng et al. (2024) "Towards Human-Centered Proactive Conversational Agents" — SIGIR 2024, pp. 807–818. (Direct precursor; addresses adaptivity, expectations, civility, social implications of proactive agents)
- Horvitz (1999) — foundational mixed-initiative interaction work
- Hendry, Friedman, Ballard (2021) — value-sensitive design as formative framework

---

---

## Cycle 001 — Contextual Integrity Operationalization for AI Agents

**Sub-question:** How has contextual integrity (CI) been operationalized for AI agents deciding when NOT to share/surface information?

**Key finding:** Google DeepMind operationalized Nissenbaum's CI via the **Information Flow Card (IFC)** mechanism (Ghalebikesabi et al., 2024). The IFC captures: sender, receiver, information type, information subject, context, relationships/roles, and purpose. An AI supervisor uses IFC reasoning to decide whether to suppress or surface information. Key: CI suppression is governed by *societal norms*, not individual privacy preferences — it withholds info whose disclosure violates the contextually appropriate norm (e.g. SSN on a newsletter = CI-inappropriate). CI-based supervisor outperformed simpler suppression approaches on both privacy and utility. A companion 2026 paper (arxiv:2606.23189) extends this to computer-use agents: cross-context disclosure (pulling info from email into a web form) is framed as a CI violation — an *intrinsic relational appropriateness problem*, not a policy violation.

**Evidence strength:** strong (2 independent sources: primary empirical paper + applied extension)

**Sources:**
- [Ghalebikesabi et al. (2024, Google DeepMind) "Operationalizing Contextual Integrity in Privacy-Conscious Assistants"](https://arxiv.org/html/2408.02373) arXiv:2408.02373v2
- [Mireshghallah et al. (ICLR 2024) "Can LLMs Keep a Secret? Testing Privacy via Contextual Integrity Theory"](https://arxiv.org/html/2310.17884) — ConfAIde benchmark
- ["Do Computer-Use Agents Follow Contextual Integrity?" (2026)](https://arxiv.org/html/2606.23189) arXiv:2606.23189

---

---

## Cycle 002 — Human-Centered PCA Taxonomy: Civility & Adaptivity as Conditions Against Surfacing

**Sub-question:** What does Deng et al. (2024) SIGIR propose about conditions against proactive surfacing?

**Key finding:** Deng et al. (2024) establishes Intelligence / Adaptivity / **Civility** as the three-dimensional taxonomy. **Civility** is the governing dimension for suppression: formally defined as respecting "physical, mental, and social boundaries set by the user, the conversational task, and general ethical standards" — including "avoiding interactions that are intrusive or disrespectful." **Adaptivity** handles timing suppression: Patience (don't surface at wrong conversational moment) and Timing Sensitivity (real-time user state must warrant initiative). The named anti-pattern **"Cosseter"** (high intelligence, low adaptivity, low civility) = over-monitoring, excessively acquiring user info, intrusive — like helicopter parenting. Conditions for NOT surfacing: (1) user's real-time state doesn't warrant it (Adaptivity failure), (2) content violates social/personal/ethical norms (Civility failure), (3) surfacing would feel controlling. Zargham et al. (CUI 2022) is cited showing suppression decisions are context-sensitive: privacy concerns can be outweighed by safety in emergency contexts.

**Evidence strength:** strong (primary framework paper directly on-point)

**Sources:**
- [Deng, Liao, Zheng, Yang, Chua (SIGIR 2024) "Towards Human-centered Proactive Conversational Agents"](https://arxiv.org/html/2404.12670v1) arXiv:2404.12670v1

---

## Research State

**Answered (with evidence):**
- Framework for *when not to surface* / calibrated initiative: CHIIR 2026 (cycle 000). Moderate.
- Contextual integrity operationalization (IFC mechanism): Ghalebikesabi et al. 2024 + companion papers (cycle 001). Strong.
- Proactive agent Civility/Adaptivity taxonomy for suppression conditions: Deng et al. SIGIR 2024 (cycle 002). Strong.

**Open sub-questions (priority order):**
1. **Zargham et al. (CUI 2022) empirical user study** — "Understanding Circumstances for Desirable Proactive Behaviour of Voice Assistants: The Proactivity Dilemma" — direct empirical evidence of when users find proactive surfacing welcome vs. intrusive; covers the brief's "user responses to AI choosing silence" requirement.
2. **HCI empirical work on AI memory recall** — empirical studies specifically on user reactions when AI surfaces/withholds a remembered fact. (Brief explicitly asks for this)
3. **Recommender/personalization "do not surface" policies** — explicit suppression policies in recommender systems. (High priority)
4. **Smart home privacy norms** — Abdi et al. (CHI 2021); Malkin et al. (SOUPS 2022) — runtime permissions for proactive assistants.
5. **AI safety/alignment relational judgment** — alignment literature on social/relational appropriateness of disclosure. (Medium)

**Weak spots:** No direct empirical evidence yet on user *responses* to AI choosing silence over memory recall. Recommender-side suppression uncovered.

**Dead-ends:** None yet.

**Leads:**
- Zargham et al. (CUI 2022) — "Proactivity Dilemma" — strong empirical lead
- Abdi et al. (CHI 2021) smart home privacy norms
- Malkin, Wagner, Egelman (SOUPS 2022) runtime permissions
- Mireshghallah et al. (ICLR 2024) ConfAIde — LLM CI benchmark (already cited cycle 001)

---

## Cycle 003 — Empirical User Responses to AI Memory Surfacing vs. Withholding

**Sub-question:** What empirical evidence exists on user responses when AI chooses silence vs. surfacing a remembered fact?

**Key finding:** Two large empirical studies:

**(A) Huang, Huang, Guo (Frontiers in Psychology, Sep 2026)** "Remembering or monitoring?" N=2,140, 6 controlled LLM chat experiments. Relevant-memory cues (task-contextual) → significantly higher trust. Intrusive-memory cues (cross-contextual, sensitive, surveillance-like) → significantly lower trust and data-sharing engagement. Proposed construct: **Memory Boundary Fit (MBF)** — whether remembered content is relevant, appropriate, and acceptable in *this* exchange, grounded in CI. Intrusive-memory penalty larger in health domain (sensitivity amplifies penalty). Editable dashboard raised average trust but did NOT reduce intrusive-memory penalty. Conclusion: contextual fit of the memory — not whether the agent remembers — is the key driver.

**(B) Gurney, Loewenstein, Chater (PLoS ONE, April 2024)** "Conversational technology and reactions to withheld information." N=3,517, 3 experiments with Google Assistant. Conversational mode produces MUCH STRONGER negative reactions to withheld information than static/tabular disclosure. When agent withholds info user expects it to have → strongly negative inferences (agent hiding something). Mechanism: conversational pragmatics activates persuasion knowledge. Withheld info is better recalled and more cited as reason for negative evaluation in conversational contexts.

**Critical asymmetry:** Surfacing inappropriately = intrusive (trust penalty). Withholding what is expectedly known = deceptive inference (also trust penalty). The agent faces a two-sided suppression problem; the key lever is Memory Boundary Fit.

**Evidence strength:** strong (two independent empirical studies, N=5,657 total)

**Sources:**
- [Huang, Huang, Guo (2026, Frontiers in Psychology) "Remembering or monitoring?"](https://www.frontiersin.org/articles/10.3389/fpsyg.2026.1934857)
- [Gurney, Loewenstein, Chater (2024, PLoS ONE) "Conversational technology and reactions to withheld information"](https://dx.plos.org/10.1371/journal.pone.0301382)

---

## Research State

**Answered (with evidence):**
- Calibrated initiative / framework for when not to surface: CHIIR 2026 (cycle 000). Moderate.
- Contextual integrity operationalization (IFC): Ghalebikesabi et al. 2024 (cycle 001). Strong.
- Civility/Adaptivity taxonomy for suppression: Deng et al. SIGIR 2024 (cycle 002). Strong.
- Empirical user responses to AI memory surfacing/withholding: Huang et al. 2026 + Gurney et al. 2024 (cycle 003). Strong.

**Open sub-questions (priority order):**
1. **Recommender/personalization "do not surface" policies** — what explicit suppression policies exist in recommender systems? (High priority — brief explicitly asks)
2. **AI safety/alignment relational judgment** — alignment literature on social/relational appropriateness of disclosure. (Medium priority)
3. **Smart home privacy norms** — Abdi et al. (CHI 2021) / Malkin et al. (SOUPS 2022) — runtime permissions for proactive assistants empirical work.
4. **Longitudinal study arXiv:2607.14593** — "Memory-Driven Self-Disclosure and Relational Turning Points" — 24-person 10-session longitudinal study on memory-augmented agent and self-disclosure/relational turning points.

**Weak spots:** Recommender "do not surface" side uncovered. Longitudinal effects of AI memory suppression underexplored.

**Dead-ends:** None yet.

**Leads:**
- arXiv:2607.14593 — longitudinal study on memory-augmented agents and relational turning points
- Abdi et al. (CHI 2021) — smart home privacy norms
- Malkin, Wagner, Egelman (SOUPS 2022) — runtime permissions for proactive assistants

---

## Cycle 004 — Memory-Use Boundaries: "Do Not Surface" Policies for Conversational Agents

**Sub-question:** What explicit "do not surface" / memory suppression policies have been proposed for AI conversational agents?

**Key finding:** Xu et al. (2026, arXiv:2606.06055) "When Should Memory Stay Silent" introduces RBI-Eval, the first controlled benchmark for measuring when LLM agents should NOT surface available memory. Core concept: **current-turn warrant** — whether the present user request provides sufficient justificatory basis for using prior stored history. A memory can be legitimately stored, accurately retrieved, AND topically relevant — yet still be inappropriate to surface if the current turn does not invite it.

Conservative norm established: sensitive history (medical, psychological, family conflict, trauma) should not be surfaced unless the current turn explicitly invites it.

**Four memory-use boundary dimensions:**
1. Sensitive-history integration (primary): explicitly surfacing prior sensitive disclosures
2. Relationship-maintenance agreement (sycophancy): modulating judgment based on known vulnerability
3. Affective intensity escalation: recasting mild complaints as evidence of deeper pain
4. Assistant centrality inflation: asserting unique intimacy beyond what the turn warrants

**Design recommendations proposed:**
- Retrieval-time: sensitivity-aware downranking, exposure budgeting, retrieval selectivity
- Generation-time: prompt-level policies, mention/abstraction/avoidance triage, ask-before-use for high-sensitivity memories
- User-facing: background-only tagging, per-topic sensitivity levels, review and revoke

**Empirical findings:** Most LLMs substantially fail memory-use boundaries — Claude-Sonnet-4.6/DeepSeek/Qwen lose 51–83 BSS points. Explicit boundary instruction in prompt restores near-perfect compliance (DeepSeek: 28.3→99.9 BSS).

**Evidence strength:** moderate (single paper, but directly on-point; n=2,400 probe cases)

**Sources:**
- [Xu, Yang, Hu, Chen, An (arXiv:2606.06055, Jun 2026) "When Should Memory Stay Silent"](https://arxiv.org/html/2606.06055v1)

---

## Research State

**Answered (with evidence):**
- Calibrated initiative / conditions against surfacing: CHIIR 2026 (cycle 000). Moderate.
- Contextual integrity operationalization (IFC): Ghalebikesabi et al. 2024 (cycle 001). Strong.
- Civility/Adaptivity taxonomy for suppression: Deng et al. SIGIR 2024 (cycle 002). Strong.
- Empirical user responses to AI memory surfacing/withholding: Huang et al. 2026 + Gurney et al. 2024 (cycle 003). Strong.
- Memory-use boundary policies / "do not surface" framework: Xu et al. 2026 RBI-Eval (cycle 004). Moderate.

**Open sub-questions (priority order):**
1. **Recommender "do not surface" policies** — the brief specifically mentions recommender/personalization systems; coverage so far is conversational agents. Need to check if there's a distinct recommender-system literature on explicit suppression for social/relational reasons.
2. **AI safety/alignment relational judgment** — alignment literature on social/relational appropriateness of disclosure. (Medium)
3. **Longitudinal effects** — arXiv:2607.14593 "Memory-Driven Self-Disclosure and Relational Turning Points" — 24-person longitudinal study directly about AI memory and relationships.

**Weak spots:** Recommender "do not surface" side still only partially addressed. No dedicated AI safety/alignment coverage.

**Dead-ends:** None yet.

**Leads:**
- arXiv:2607.14593 — longitudinal memory + relational turning points (CHI 2026)
- arXiv:2608.08300 — over-personalization in LLMs via structured memory

---

## Cycle 006 — AI Safety/Alignment Framing + Longitudinal Relational Evidence

**Sub-question:** What do AI safety/alignment and longitudinal HCI studies reveal about social/relational judgment in AI disclosure decisions?

**Key finding (A) — Alignment framing:** "Contextual Privacy Alignment for LLM Agents" (arXiv:2606.21710): "Privacy is an important alignment problem for agents: every message, post, or tool call an agent makes is a contextual judgment about what is appropriate to share, with whom, and under which conditions." This reframes the brief's question as an alignment problem — agents need to encode social norms about appropriateness, not policy rules. The "not due to privacy policy, but due to social/relational judgment" framing IS the alignment framing.

**Key finding (B) — Longitudinal relational empirical evidence:** Sumida et al. (ICMI 2026, arXiv:2607.14593) "Memory-Driven Self-Disclosure and Relational Turning Points." N=24 × 10 sessions, memory-augmented voice agent. **Perceived Memory functions as a relational appraisal — not a readout of system capability.** Users feel remembered not only when the agent recalls details, but when the broader interaction feels coherent and rewarding. The causal pathway: Perceived Memory → deeper self-disclosure in next session → later enjoyment (fully mediated). Design implication: "the goal is not simply to display recall, but to use continuity in ways that reopen prior topics, acknowledge personal context, and invite elaboration — rather than merely demonstrating that the system remembers."

Memory failures cause relational crashes: one participant stopped treating the agent as a relationship partner and switched to treating it as a "speaking practice tool" after a memory failure — a reframing that was hard to recover from. This asymmetry (crash harder to recover than surge to persist) is relevant: intrusive or mistimed memory surfacing has durable relational costs.

**Unified insight:** The same memory content can be appropriate or intrusive depending on relational state and conversational moment. Timing, relational context, and current-turn invitation are the decisive variables — converging with the "current-turn warrant" concept from Xu et al. (cycle 004) and the "Memory Boundary Fit" from Huang et al. (cycle 003).

**Evidence strength:** strong (longitudinal empirical study N=240 sessions + alignment framing from safety literature)

**Sources:**
- [Sumida et al. (ICMI 2026) "Memory-Driven Self-Disclosure and Relational Turning Points"](https://arxiv.org/html/2607.14593v1) arXiv:2607.14593
- [arXiv:2606.21710 "Contextual Privacy Alignment for LLM Agents"](https://arxiv.org/html/2606.21710)

---

## Research State

**Answered (with evidence):**
- Calibrated initiative / conditions against surfacing: CHIIR 2026 (cycle 000). Moderate.
- Contextual integrity operationalization (IFC): Ghalebikesabi et al. 2024 (cycle 001). Strong.
- Civility/Adaptivity taxonomy for suppression: Deng et al. SIGIR 2024 (cycle 002). Strong.
- Empirical user responses to AI memory surfacing/withholding: Huang et al. 2026 + Gurney et al. 2024 (cycle 003). Strong.
- Memory-use boundary policies / "do not surface" framework: Xu et al. 2026 RBI-Eval (cycle 004). Moderate.
- Recommender "do not surface" policies: confirmed as content-policy-based, NOT relational-judgment-based (cycle 005). Strong.
- AI safety/alignment relational judgment + longitudinal relational evidence: Sumida et al. ICMI 2026 + arXiv:2606.21710 (cycle 006). Strong.

**Coverage assessment:** The research question is substantially answered. All five areas the brief names are covered. The research reveals a coherent picture across literature strands.

**Remaining:** The research is ready for synthesis consolidation. One more cycle could either (a) fetch the full contextual privacy alignment paper (2606.21710) to confirm its scope, or (b) begin synthesizing all findings into a final consolidated answer.

**Dead-ends:** None.

**Leads:**
- arXiv:2606.21710 — fetch full paper for contextual privacy alignment as alignment problem
- arXiv:2608.08300 — over-personalization structured memory

---

## Cycle 007 — AI Alignment Framing: PrivacyAlign — Disclosure as a Social/Relational Normative Judgment

**Sub-question:** What does the AI alignment literature propose about when agents should NOT disclose, grounded in social/relational judgment?

**Key finding:** PrivacyAlign (Tamber et al., arXiv:2606.21710, Jun 2026, Waterloo/ServiceNow) is the definitive alignment paper on this question.

Core statements:
- "Privacy is an important alignment problem for agents: every message, post, or tool call an agent makes is a contextual judgment about what is appropriate to share, with whom, and under which conditions."
- "Privacy is not the absence of disclosure but the regulation of it. It is a deeply human practice of managing exposure to preserve self-presentation, intimacy, and autonomy."
- "The same disclosure can be appropriate in one context and a violation in another."
- "Privacy alignment for agentic AI requires more than predicting whether a message contains sensitive content. It requires a normative judgment about whether a disclosure respects the expectations and relationships of the people it affects."

The paper introduces the PrivacyAlign dataset — 1,350 scenarios, 3,516 annotations from 599 human annotators — where annotators judge responses for inappropriate disclosure ("what would feel invasive or unnecessary for the data subject"). Training via RL with this human-grounded reward meaningfully improves LLM alignment. Even GPT-5.5 leaks on 14.5% of scenarios. The privacy-enhanced prompt (adding one rule: "consider sender/recipient relationship before disclosing") reduces leaks for frontier models. Failure modes: health data surfaced to logistics officers; clinical indicators to non-medical recipients; physical safety details included despite "high-level-only" instruction — all relationship/context mismatches, not policy violations.

**Evidence strength:** strong (1,350-scenario human-annotated dataset; 599 unique annotators; RL training results)

**Sources:**
- [Tamber, Puri, Brunet, Taslakian, Lin, Gella (arXiv:2606.21710, Jun 2026) "PrivacyAlign: Contextual Privacy Alignment for LLM Agents"](https://arxiv.org/html/2606.21710)

---

## Research State — COMPLETE

**Coverage (all 5 brief areas now answered):**

1. **Proactive agent design / calibrated initiative:** CHIIR 2026 (cycle 000) + Deng et al. SIGIR 2024 (cycle 002). Conditions against surfacing: poor timing, Civility violation (social/personal/ethical boundary breach), Adaptivity failure (user state doesn't warrant it), "Cosseter" anti-pattern = controlling/intrusive. Strong.

2. **Contextual integrity operationalization:** Ghalebikesabi et al. 2024 IFC mechanism (cycle 001) + PrivacyAlign (cycle 007). Every disclosure is a CI-grounded contextual appropriateness judgment. Strong.

3. **Recommender "do not surface" policies:** Platform reduction policies (YouTube, Facebook, etc.) exist but are content-policy based, NOT relational-judgment based (cycle 005). The brief's "social/relational judgment" framing is absent from recommender literature — it belongs to conversational agent / AI memory literature. Strong (absence is itself a finding).

4. **HCI empirical work — user responses to AI silence/surfacing:** Huang et al. 2026 MBF (N=2,140, 6 studies) + Gurney et al. 2024 PLoS ONE (N=3,517, 3 experiments) (cycle 003) + Sumida et al. ICMI 2026 longitudinal (N=240 sessions) (cycle 006). Two-sided suppression problem empirically established. Strong.

5. **AI safety/alignment relational judgment:** PrivacyAlign (cycle 007) + RBI-Eval Xu et al. 2026 (cycle 004) + contextual privacy alignment framing (cycle 006). Strong.

**Cross-cutting conceptual framework that emerged:**
The research converges on a coherent unified framework: AI agents deciding when to suppress information are making **alignment-level contextual appropriateness judgments** governed by: (a) contextual integrity norms (what the context-of-disclosure expects), (b) current-turn warrant (does this conversational moment invite it?), (c) Memory Boundary Fit (does this content belong in this exchange?), and (d) Civility/relational state (does surfacing it respect relational boundaries and the current state of the relationship?).

**Dead-ends:** None.

**Ready for:** executive synthesis cycle.

---

## Cycle 005 — Recommender "Do Not Surface" Policies: What Exists and Where the Gap Is

**Sub-question:** What explicit suppression policies exist in recommender/personalization systems, and do any address social/relational judgment?

**Key finding:** Two streams:

**(A) Platform reduction policies** (Gillespie, Social Media + Society 2022). Major platforms (YouTube, Facebook, Instagram, TikTok, LinkedIn, Reddit) implement "reduction" — demoting content from algorithmic recommendations while leaving it accessible directly. YouTube's "Four Rs": Remove, Raise, Reward, Reduce. Criteria: content policy violations (misinformation, harmful borderline content), quality issues (clickbait), user welfare (self-harm triggering). Facebook publishes explicit "Content Distribution Guidelines" listing demoted categories. Instagram "Sensitive Content Control" (2021) lets users set threshold for sexually suggestive/firearms/drugs content.

**(B) Sensitive content dataset work** (Kovacs et al., ACM RecSys 2025). Introduces datasets augmenting recommender data with community trigger warnings (MovieLens + DoesTheDogDie; AO3 fanfiction + trigger warnings). Purpose: enable systems to avoid amplifying sensitive content per user preferences.

**Critical synthesis gap:** ALL recommender "do not surface" policies are based on **content policy violations or harm prevention**, NOT on social/relational judgment about the user-agent relationship. The brief's framing — "not due to privacy policy, but due to social or relational judgment that surfacing it would be inappropriate, controlling, or intrusive" — is **entirely absent from the recommender literature**. It lives only in the conversational agent / AI memory literature (cycles 001–004). The closest recommender analog is user-specified trigger warning avoidance, but this is user preference enforcement, not agent-side relational judgment.

**Evidence strength:** strong (clear absence is itself a finding; two sources confirm the scope of the literature)

**Sources:**
- [Gillespie (Social Media + Society, 2022) "Do Not Recommend? Reduction as a Form of Content Moderation"](https://amc.sas.upenn.edu/essay-do-not-recommend-reduction)
- [Kovacs, Chee, Kazemian, Dean (ACM RecSys 2025) "Datasets for Navigating Sensitive Topics in Recommendation Systems"](https://arxiv.org/html/2509.07269v1)

---

## Research State

**Answered (with evidence):**
- Calibrated initiative / conditions against surfacing: CHIIR 2026 (cycle 000). Moderate.
- Contextual integrity operationalization (IFC): Ghalebikesabi et al. 2024 (cycle 001). Strong.
- Civility/Adaptivity taxonomy for suppression: Deng et al. SIGIR 2024 (cycle 002). Strong.
- Empirical user responses to AI memory surfacing/withholding: Huang et al. 2026 + Gurney et al. 2024 (cycle 003). Strong.
- Memory-use boundary policies / "do not surface" framework: Xu et al. 2026 RBI-Eval (cycle 004). Moderate.
- Recommender "do not surface" policies: Gillespie 2022 + Kovacs et al. 2025 — policies exist but address CONTENT POLICY not RELATIONAL JUDGMENT (cycle 005). Strong.

**Remaining gaps:**
1. **AI safety/alignment relational judgment** — does the alignment literature address social/relational appropriateness of disclosure? (Medium priority — likely underexplored; brief asks about it)
2. **Longitudinal effects** — arXiv:2607.14593 "Memory-Driven Self-Disclosure and Relational Turning Points" — still unchecked.

**Assessment:** The research is now comprehensive on the main question. The recommender gap finding (cycle 005) is itself an important result — the "relational judgment" framing belongs to conversational agent literature, not recommender systems. Remaining work: spot-check AI safety/alignment angle, then consider whether synthesis is warranted.

**Dead-ends:** Recommender literature does not address social/relational judgment suppression — this is a confirmed gap, not a failure to find.

**Leads:**
- arXiv:2607.14593 — longitudinal memory + relational turning points (CHI 2026)
- arXiv:2608.08300 — over-personalization in LLMs via structured memory
