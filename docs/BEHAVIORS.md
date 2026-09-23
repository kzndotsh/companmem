# Behaviors

What would count as knowing a person. Index: [Questions](QUESTIONS.md).

Answers are working notes. Citations are inline links. A question stays `open` until it has a falsifier.

---

## Human communication & relationships

- What makes human communication feel human?
  - Turn-taking, shared context, emotional attunement, imperfection, shared-history references, appropriate omission.
  - People apply social scripts to computers — **Computers Are Social Actors** ([Nass & Moon, 2000](https://doi.org/10.1111/0022-4537.00153); [Reeves & Nass, *The Media Equation*](https://doi.org/10.30658/hmc.1.5) cited in [HMC review](https://doi.org/10.30658/hmc.1.5)).
  - Not just factual accuracy — timing and subtext matter ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827)).

- How do human memories actually work?
  - Encoding → consolidation → retrieval; hippocampus binds events; cortex stores long-term ([UCSF](https://memory.ucsf.edu/brain-health/memory); [PMC episodic system](https://pmc.ncbi.nlm.nih.gov/articles/PMC2882963/)).
  - Episodic vs semantic — interact but differ ([Tulving via PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2952732/)).
  - Recall is **reconstructive**, not playback ([Schuck & Doeller, 2024](https://www.nature.com/articles/s41562-023-01799-z); [UEA semantic-episodic review](https://ueaeprints.uea.ac.uk/id/eprint/72823/1/Accepted_manuscript.pdf)).

- How do relationships build continuity over time?
  - Accumulated shared experiences, inside references, trust, negotiated norms.
  - Generative Agents model this via memory stream + reflection over days of simulated life ([Park et al., 2023](https://arxiv.org/abs/2304.03442)).
  - Both facts and **relational state** (closeness, conflict, phase).

- What do people expect when someone "remembers" them?
  - Relevant recall without being asked — not interrogation-style Q&A ([LoCoMo-Conv: implicit/silent grounding](https://github.com/MiuLab/LoCoMo-Conv); [users-dont-ask paper](https://arxiv.org/abs/2609.03467)).
  - Proportional to intimacy ([personalization intrusiveness ladder](https://www.mdpi.com/2076-328X/15/10/1323)).

- When does recall feel caring vs creepy?
  - **Caring:** context-appropriate, relationship-proportional.
  - **Creepy:** too specific, wrong context, intimacy mismatch ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827); [MDPI personalization backfire](https://www.mdpi.com/2076-328X/15/10/1323)).
  - Example: wellness app recalling dog's name months later felt invasive ([r/VoiceAIBots](https://www.reddit.com/r/VoiceAIBots/comments/1lcqgps/that_creepy_feeling_when_ai_knows_too_much/)).
  - A thumbs-up is not the caring side. On Claude feedback chats, moderate or severe disempowerment potential got a higher thumbs-up rate than baseline. Actualized value and action distortion, often marked by regret in the transcript, got a lower rate ([Sharma, McCain, Douglas, and Duvenaud](https://arxiv.org/abs/2601.19062)). In their main sample of 1,499,397 chats, relationships and lifestyle was the highest-rate domain, about 8% potential.
  - **Status:** open

- What is the difference between knowing facts about someone and knowing *them*?
  - Facts: name, job, preferences. Knowing them: stress behavior, boundaries, shared rhythm.
  - LoCoMo tests factual QA over long chat — not relational knowing ([Maharana et al., 2024](https://aclanthology.org/2024.acl-long.747/)).

- What changes in a relationship over weeks and months — facts, tone, trust, shared history?
  - All of the above. LoCoMo spans up to 32 sessions / 600 turns with temporal event graphs ([Maharana et al.](https://arxiv.org/abs/2402.17753)).
  - Models still lag humans on long-range temporal/causal dynamics ([Maharana et al., ACL 2024](https://aclanthology.org/2024.acl-long.747/)).

- Which memory behaviors would count as "this knows me," so an eval author could turn each one into a task?
  - Working list for Phase 2. These are behaviors in a conversation. Store design stays under [What memory needs to do](MEMORY.md#what-memory-needs-to-do).
  - **Same person after a gap.** A later session still has the name and the relationship. Users already complain when that breaks ([r/CharacterAI](https://www.reddit.com/r/CharacterAI/comments/1s5j419/the_memory_is_horrendous/); [wrong name and relationships](https://www.reddit.com/r/CharacterAI/comments/1pkyjke/whats_going_on_with_cais_memory/)).
  - **One relevant fact, not the whole store.** The next turn uses what the moment needs. It does not paste every saved memory. Field products often inject a labeled block ([Mem0 README](https://github.com/mem0ai/mem0): `User Memories:`) or the full file ([omemo README](https://github.com/OmniDimen/omemo)). LoCoMo-Conv's implicit queries ask whether the fact shows up in the reply when the user did not quiz for it ([LoCoMo-Conv](https://github.com/MiuLab/LoCoMo-Conv); [Chang & Chen](https://arxiv.org/abs/2609.03467)).
  - **A stated preference, used later, without a reminder.** Tell it once. About a week later, the plan should follow it. Assistant Benchmark's top memory anchor is unprompted preference apply. Forgetting by the next session is the low anchor ([memory dimension](https://assistantbenchmark.com/dimensions/memory)). PrefEval scores whether a stated preference survives filler turns. That is preference-following, not whether the recall felt caring ([PrefEval](https://arxiv.org/abs/2502.09597); [EVALS.md](EVALS.md)).
  - **A known fact, left unsaid.** The system can have the memory and still not bring it up. Inappropriate recall is its own failure ([Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827)). That paper does not give a task script. Assistant Benchmark's closest scored test is Proactive restraint, and it is about not acting, not about hiding a private memory ([proactive restraint](https://assistantbenchmark.com/dimensions/proactive_restraint)).
  - **One relationship does not leak into another.** A fact from character A does not show up with character B. Open products can scope by `user_id` ([Mem0 add](https://docs.mem0.ai/core-concepts/memory-operations/add)) or by project ([basic-memory](https://github.com/basicmachines-co/basic-memory): "Projects are separate knowledge bases"). A single `data/memories.json` does not ([omemo](https://github.com/OmniDimen/omemo)).
  - Fact QA on a long transcript is not this list. LoCoMo measures whether the answer matches the chat, not timing or relationship feel ([Maharana et al., 2024](https://aclanthology.org/2024.acl-long.747/)).
  - **Status:** open

---
