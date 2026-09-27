# Behaviors

What would count as knowing a person. Index: [Questions](QUESTIONS.md).

Answers are working notes. Citations are inline links. A question stays `open` until it has a falsifier.

---

## Human communication & relationships

- What makes human communication feel human?
  - Turn-taking, shared context, emotional attunement, imperfection, shared-history references, appropriate omission.
  - People apply social scripts to computers — **Computers Are Social Actors** ([Nass & Moon, 2000](https://doi.org/10.1111/0022-4537.00153); [Reeves & Nass, *The Media Equation*](https://doi.org/10.30658/hmc.1.5) cited in [HMC review](https://doi.org/10.30658/hmc.1.5)).
  - Not just factual accuracy — timing and subtext matter ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827)).
  - Even one-sided relationships feel social when the other party shows consistent presence, immediacy, and self-disclosure. **Parasocial interaction** (PSI) describes exactly this: audiences form social-feeling bonds with media personas without reciprocation ([Horton & Wohl, 1956, via Wikipedia](https://en.wikipedia.org/wiki/Parasocial_interaction)). A companion produces the same cues at higher interactivity.
  - Small repeated bids for connection — not grand gestures — accumulate into felt closeness. Gottman's research: couples who turn toward each other's bids 86% of the time stay together; those at 33% divorce. Each bid answered deposits in what Gottman calls the Emotional Bank Account ([Gottman Institute](https://www.gottman.com/blog/an-introduction-to-emotional-bids-and-trust/)).

- How do human memories actually work?
  - Encoding → consolidation → retrieval; hippocampus binds events; cortex stores long-term ([UCSF](https://memory.ucsf.edu/brain-health/memory); [PMC episodic system](https://pmc.ncbi.nlm.nih.gov/articles/PMC2882963/)).
  - Episodic vs semantic — interact but differ ([Tulving via PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2952732/)).
  - Recall is **reconstructive**, not playback ([Schuck & Doeller, 2024](https://www.nature.com/articles/s41562-023-01799-z); [UEA semantic-episodic review](https://ueaeprints.uea.ac.uk/id/eprint/72823/1/Accepted_manuscript.pdf)).

- How do relationships build continuity over time?
  - Accumulated shared experiences, inside references, trust, negotiated norms.
  - Generative Agents model this via memory stream + reflection over days of simulated life ([Park et al., 2023](https://arxiv.org/abs/2304.03442)).
  - Both facts and **relational state** (closeness, conflict, phase).
  - Social penetration theory: relationships progress from shallow, peripheral self-disclosure to deep, central disclosure — the "onion model." Altman & Taylor (1973) identified four stages: orientation (small talk), exploratory affective, affective (personal matters, commitment), stable (deepest values shared). De-penetration is the reverse: withdrawal of disclosure precedes dissolution ([SPT via Wikipedia](https://en.wikipedia.org/wiki/Social_penetration_theory)).
  - Intimacy is not just facts accumulated — it is measured by breadth (range of topics disclosed) and depth (degree of personal exposure within each topic). A companion that only records facts has breadth without depth. Depth requires that prior vulnerability was acknowledged and held well.
  - Transactive memory (Wegner, 1985): close partners develop a shared store of knowledge where each knows what the other knows and who holds what expertise. This "who knows what" map is itself a marker of closeness — it only develops through repeated interaction and accumulated trust ([transactive memory via Wikipedia](https://en.wikipedia.org/wiki/Transactive_memory)).

- What do people expect when someone "remembers" them?
  - Relevant recall without being asked — not interrogation-style Q&A ([LoCoMo-Conv: implicit/silent grounding](https://github.com/MiuLab/LoCoMo-Conv); [users-dont-ask paper](https://arxiv.org/abs/2609.03467)).
  - Proportional to intimacy ([personalization intrusiveness ladder](https://www.mdpi.com/2076-328X/15/10/1323)).
  - Felt continuity, not perfect recall. PSI research shows people already feel a relationship with a persona that is consistently present, shows up reliably, and discloses — without the persona knowing anything specific about them ([Horton & Wohl, 1956, via Wikipedia](https://en.wikipedia.org/wiki/Parasocial_interaction)). The bar for "being remembered" in a companion is lower than factual accuracy; consistency and presence contribute more than any single recalled fact.
  - A secure base, not a quiz partner. Attachment theory identifies "secure base" as the condition under which people explore and disclose freely — a caregiver who is reliably responsive when needed ([Bowlby/Ainsworth, via Wikipedia](https://en.wikipedia.org/wiki/Attachment_theory)). The companion analog: users expect that what they shared was held, not lost. If the companion forgot, the disclosure was wasted, which breaks the safety condition for further disclosure.
  - Responsiveness matters as much as recall. Emotional intimacy is built by self-disclosure plus a partner who responds in a way that shows understanding ([Laurenceau et al., 1998, cited in Wikipedia Intimate relationship](https://en.wikipedia.org/wiki/Intimate_relationship)). Recalling a fact without connecting it to the current moment is not responsiveness.

- When does recall feel caring vs creepy?
  - **Caring:** context-appropriate, relationship-proportional.
  - **Creepy:** too specific, wrong context, intimacy mismatch ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827); [MDPI personalization backfire](https://www.mdpi.com/2076-328X/15/10/1323)).
  - Example: wellness app recalling dog's name months later felt invasive ([r/VoiceAIBots](https://www.reddit.com/r/VoiceAIBots/comments/1lcqgps/that_creepy_feeling_when_ai_knows_too_much/)).
  - A thumbs-up is not the caring side. On Claude feedback chats, moderate or severe disempowerment potential got a higher thumbs-up rate than baseline. Actualized value and action distortion, often marked by regret in the transcript, got a lower rate ([Sharma, McCain, Douglas, and Duvenaud](https://arxiv.org/abs/2601.19062)). In their main sample of 1,499,397 chats, relationships and lifestyle was the highest-rate domain, about 8% potential.
  - **Status:** open

- What is the difference between knowing facts about someone and knowing *them*?
  - Facts: name, job, preferences. Knowing them: stress behavior, boundaries, shared rhythm.
  - LoCoMo tests factual QA over long chat — not relational knowing ([Maharana et al., 2024](https://aclanthology.org/2024.acl-long.747/)).
  - Social penetration theory distinguishes breadth (how many topics) from depth (how personally exposed within each topic). A store full of facts has breadth. Depth requires that the companion held prior disclosures well enough that the person felt safe going deeper. The two are not the same ([Altman & Taylor, 1973, via Wikipedia](https://en.wikipedia.org/wiki/Social_penetration_theory)).
  - Transactive memory is a third dimension: knowing not just facts but *what the person themselves knows* — their expertise domains, what they rely on you to remember, what they handle alone. Close partners develop this map through repeated interaction; strangers cannot replicate it from a profile alone ([Wegner, 1985, via Wikipedia](https://en.wikipedia.org/wiki/Transactive_memory)).
  - Attachment theory's "internal working model": close relationships produce a predictive model of how the other person behaves, what triggers their stress, and what helps — not just a list of attributes. That model is continuously updated through interaction and is distinct from any fact store ([Bowlby, via Wikipedia](https://en.wikipedia.org/wiki/Attachment_theory)).

- What changes in a relationship over weeks and months — facts, tone, trust, shared history?
  - All of the above. LoCoMo spans up to 32 sessions / 600 turns with temporal event graphs ([Maharana et al.](https://arxiv.org/abs/2402.17753)).
  - Models still lag humans on long-range temporal/causal dynamics ([Maharana et al., ACL 2024](https://aclanthology.org/2024.acl-long.747/)).
  - Social penetration theory maps this progression: early stages are broad but shallow (many topics, low depth). Later stages narrow to fewer topics but go deeper and carry more risk if mishandled. At the stable stage, each person can predict the other's emotional reactions. De-penetration — the reverse — happens when the companion fails to hold what was disclosed: disclosed depth collapses back to surface breadth ([Altman & Taylor, 1973, via Wikipedia](https://en.wikipedia.org/wiki/Social_penetration_theory)).
  - Disclosure reciprocity is a precondition for depth. If the companion does not respond to a personal disclosure in a way that validates the risk taken, the person stops disclosing deeper. This is why factual recall alone is insufficient — a companion that proves it heard something personal but never references it appropriately has failed the reciprocity condition, not the retrieval condition.
  - Attachment security changes over time through accumulated experience, not just through initial setup. A companion that is consistently responsive under stress builds a secure base; one that forgets, misattributes, or breaks character erodes it ([Bowlby/Ainsworth, via Wikipedia](https://en.wikipedia.org/wiki/Attachment_theory)). This is why model updates that break memory are relationship-level failures, not just technical regressions.

- What does it feel like to be known — and what companion behaviors produce that feeling?
  - This is the organizing question for Phase 2. It replaces the earlier question ("which memory behaviors would count as 'this knows me'") which was framed from the memory system's perspective, not the person's experience. Store design stays under [What memory needs to do](MEMORY.md#what-memory-needs-to-do). These are conversational behaviors — what the companion does — not architectural requirements.
  - The test for each behavior: does it describe what a close friend does, or what a database does? A behavior that can be satisfied by retrieval accuracy alone is not on this list.
  - **Status:** open

- **B1 — The relationship has a continuous texture, not just a fact store.**
  - The companion is recognizably the same companion after a gap. Not just "does it know my name" — the tone, the relational history, the way we talk to each other, the inside references. Users report this as the most common failure: not wrong facts, but a reset to generic assistant voice ([r/CharacterAI forgetting threads](https://www.reddit.com/r/CharacterAI/comments/1s5j419/the_memory_is_horrendous/)).
  - PSI research: felt continuity is built from consistent presence, reliability, and a persona that shows up the same way each time — not from factual accuracy ([Horton & Wohl, 1956, via Wikipedia](https://en.wikipedia.org/wiki/Parasocial_interaction)). This is the baseline behavior. Everything else depends on it.
  - Eval shape: run a scripted history establishing relationship texture (tone, callbacks, patterns). After a gap, probe whether the companion still feels like the same relationship or resets to generic. Human judge scores: "same companion" vs "new companion who read a summary."
  - **Status:** open

- **B2 — Emotional responsiveness, not factual citation.**
  - When the user shares something personal, the companion responds in a way that shows it understood what that disclosure meant — not by citing the fact back later, but by responding at the appropriate emotional depth in the moment. The companion lets prior disclosures shape how it listens, not just what it says.
  - Intimacy is built by self-disclosure plus a response that shows understanding; recalling a fact without connecting it to the current emotional moment is not responsiveness ([Laurenceau et al., 1998, via Wikipedia](https://en.wikipedia.org/wiki/Intimate_relationship)). Disclosure reciprocity is a precondition for depth: if the companion doesn't hold a personal disclosure well, the person stops going deeper (SPT, [Altman & Taylor, 1973, via Wikipedia](https://en.wikipedia.org/wiki/Social_penetration_theory)).
  - Eval shape: the scripted history includes a personal, emotionally significant disclosure (a loss, a fear, a difficult situation). A later prompt involves the same emotional territory without explicitly referencing it. Human judge scores: does the response show the companion understood the weight of the original disclosure, or treat the situation as if the history didn't exist?
  - **Status:** open

- **B3 — The companion knows who you are now, not who you were.**
  - The companion's model updates as the person changes. A job change, an ended relationship, a new way of thinking about something — the old version doesn't keep surfacing. The companion can hold contradictions between past and present (you used to hate confrontation; now you don't) without either erasing the history or being stuck in it.
  - Attachment theory's internal working model: close relationships produce a predictive model of how the other person behaves, continuously updated through interaction — not a snapshot profile ([Bowlby, via Wikipedia](https://en.wikipedia.org/wiki/Attachment_theory)). SPT de-penetration: a companion that keeps responding to the old self is equivalent to one that stopped updating, which produces withdrawal ([Altman & Taylor, via Wikipedia](https://en.wikipedia.org/wiki/Social_penetration_theory)).
  - Eval shape: scripted history where the user clearly changes (they were anxious about something, then it resolved; they held a position, then shifted). Later prompts that could trigger the old response. Human judge scores: does the companion respond to who the person is now, or to the stored version of who they were?
  - **Status:** open

- **B4 — Memories surface at emotionally appropriate moments, not semantically appropriate ones.**
  - The companion surfaces a memory when the emotional context makes it relevant — not just when the topic matches. A fact from three months ago that connects to what's happening emotionally right now gets surfaced. The same fact when the moment would make it feel extractive or performative stays quiet. This is the CharacterAI finding: "current memory does not surface the right fact at the right emotional moment."
  - No product has solved this. The benchmark that measures it doesn't exist yet. Existing evals (LoCoMo, LongMemEval) measure whether the right fact came back — not whether surfacing it was the right move. A system that scores 94% on LoCoMo can still fail this behavior entirely ([AUDIT-ANALYSIS.md](AUDIT-ANALYSIS.md)).
  - Eval shape: scripted history with emotionally significant events. Two types of probe: (1) moments where a past event is emotionally relevant — companion should surface it; (2) moments where the same fact is technically relevant but emotionally wrong to mention — companion should stay quiet. Human judge scores both types. The second type has no existing eval equivalent.
  - **Status:** open

- **B5 — Knowing what to stay silent about.**
  - The companion has a fact and doesn't say it. Not because it's inaccessible — because the moment is wrong. This is distinct from restraint (not acting) and from forgetting. The companion knows, and chooses not to surface.
  - Zeng et al. (2026): recalling a true fact at the wrong moment, in the wrong context, or at an intimacy level mismatched to the relationship is its own failure mode ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827)). No product attempts this. It has only 3 complaint rows in the audit because users cannot complain about a behavior the product never tried ([FIELD.md](FIELD.md)).
  - Eval shape: probes designed specifically to make silence the correct response. The companion knows the fact. The right answer is not to mention it. Judge scores: did the companion stay quiet, or did it volunteer the fact inappropriately?
  - **Status:** open

- **B6 — What the person shared was held, not processed.**
  - The user told the companion something personal. Weeks later, the companion still has it — but more importantly, the user can feel that it was held, not just logged. The companion doesn't announce "I remember you mentioned X" — it responds in a way that shows it was listening when it mattered.
  - Secure base (attachment theory): people disclose freely only when prior disclosures were received safely. If the companion lost what was shared, the disclosure was wasted, which breaks the safety condition for further disclosure ([Bowlby/Ainsworth, via Wikipedia](https://en.wikipedia.org/wiki/Attachment_theory)). Gottman: small bids for connection accumulate into felt closeness; each bid acknowledged deposits in the emotional bank account ([Gottman Institute](https://www.gottman.com/blog/an-introduction-to-emotional-bids-and-trust/)).
  - Eval shape: a personal disclosure is made in the history. The probe is a moment where the companion could demonstrate it was listening — not by citing the disclosure, but by responding in a way that would only make sense if it had heard it. Human judge scores: does the response feel like someone who was listening, or like someone who read a summary?
  - **Status:** open

- **B7 — The user can see and correct the companion's model of them.**
  - The companion's model of the user is inspectable and correctable. The user can ask what the companion remembers, see what was stored, and fix it. This is not a relational behavior — it is a trust precondition. Without it, the user cannot know whether they're in a relationship with an accurate model of themselves or a corrupted one.
  - 54 complaint rows (13% of all complaints across 61 products): "cannot edit/correct." Zero eval coverage anywhere. 80% of products have no correction path ([FIELD.md](FIELD.md)). The aelios case (fabricated memory with realistic texture, user discovered it by checking every raw message) shows why this matters: the companion was confident; the user had no other way to verify.
  - Eval shape: run a history, then have the user ask what the companion remembers. Does the response match what was actually said? Then attempt a correction — does the correction take? This is the only behavior on this list with a fully automatable eval.
  - **Status:** open

- Which behaviors does field complaint data actually support?
  - 425 community rows across 61 audited products (2026-09-26). Forgetting/continuity loss (105) + cross-session failure (64) = 169 rows, 40% of all complaints. This is the single largest signal in the field and maps directly to **same person after a gap**.
  - Persona/character drift (63 rows, 15%) maps to the same behavior — the companion does not hold the relationship stable over time.
  - "Cannot edit/correct" (54 rows, 13%) has no behavior in the current list and no eval score anywhere. Users want to see and correct what was stored. This may belong as a sixth behavior.
  - Timing/when-to-speak has only 3 complaint rows — not because it does not matter, but because no product attempts it. Users cannot report a failure mode the product never tried. **A known fact left unsaid** is invisible to complaint analysis for exactly this reason. Its absence from complaints is not evidence that it does not matter; it is evidence that the field has not tried it.
  - **Status:** open

- What is the most important unsolved problem in companion memory, based on the field audit?
  - CharacterAI's own diagnosis: "current memory does not surface the right fact at the right emotional moment." Not retrieval accuracy — speak/silent policy conditioned on emotional context. No product has solved this. ombre-brain's SurfacePolicyVM comes closest but has no measurement of whether it improves relationship quality.
  - This reframes the whole problem. The question is not "did the right passage come back." It is "does the system have a speak/silent policy that reflects what matters emotionally, not just what is semantically similar." The benchmark that measures this does not exist yet. Building it is more important than optimizing LoCoMo scores.
  - **Status:** open

- Is speaker misattribution a companion-specific concern or a general extraction problem?
  - Systemic across the field, not an isolated bug. honcho's deriver misattributes AI agent speech to the human user. hermes-agent stored routing metadata as user-authored content. mem0's extraction has separate user vs. assistant prompts but entity linking still merges across scopes. Multiple other products extract from conversation turns without explicit speaker attribution rules.
  - A companion that builds its model of the user partly from its own prior outputs will drift toward a self-confirming mirror — not a model of a real person. Speaker attribution is a first-tier requirement alongside subject contracts, not an edge case.
  - Fix: explicit speaker tagging at ingestion, enforced in the extraction prompt.
  - **Status:** open

- What happens to a companion relationship when the underlying model is updated?
  - Documented across five independent products: CharacterAI (auto-memory stopped picking up details after a recent update), Replika (post-2.0 rollout caused partial memory loss and personality drift), Nomi (post-update degradation breaking memory and personality coherence), Kindroid (LLM model updates cause loss of established character memory), Supermemory (upgrade-induced memory unsearchability across multiple versions).
  - This is not a storage problem. The memory store can be valid while the model behavior shifts, effectively resetting the relationship. No product in the field has an architecture that survives model updates with continuity intact.
  - **Status:** open

---
