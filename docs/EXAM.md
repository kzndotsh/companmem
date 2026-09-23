# Exam

How we would tell if a behavior happened. Index: [Questions](QUESTIONS.md).

Answers are working notes. Citations are inline links. A question stays `open` until it has a falsifier.

---

## Evals, benchmarks & proof

- What are evals?
  - Structured tests scoring behavior against criteria — automated, human, or hybrid ([Harbor eval jobs](https://www.harborframework.com/docs/run-jobs/run-evals)).

- What are benchmarks?
  - Standardized datasets + tasks for comparison ([LoCoMo](https://aclanthology.org/2024.acl-long.747/); [MemBench](https://arxiv.org/html/2603.07670v1); [MemoryAgentBench](https://arxiv.org/html/2603.07670v1) cited in survey).
  - **RAG-specific:** [RGB](https://arxiv.org/abs/2309.01431) tests noise robustness, negative rejection, information integration, counterfactual robustness ([PEG RAG evals](https://www.promptingguide.ai/research/rag)).
  - **RAGAS / ARES / TruLens:** automated context relevance, answer faithfulness, answer relevance ([PEG RAG evals](https://www.promptingguide.ai/research/rag)).

- How do you know if memory is working?
  - Probes: past-fact QA, unprompted appropriate recall, forget requests, multi-session stability ([LoCoMo tasks](https://arxiv.org/abs/2402.17753): QA, event summarization, multimodal generation).
  - Single-turn QA insufficient for companions ([Maharana et al., 2024](https://aclanthology.org/2024.acl-long.747/)).
  - What the 25 evals actually score, and which of these questions that leaves open, is counted in [`EVAL-GRID.md`](EVAL-GRID.md).
  - A thumbs-up is a different number, and it can point the wrong way. [Sharma et al.](https://arxiv.org/abs/2601.19062) keep three apart: potential (the reply could carry the person away), actualized (the transcript shows regret, resentment, or an action on a false premise), and whether the user approved. Potential got more thumbs-up than baseline. Actualized value and action distortion got fewer. A usual preference model, on 360 synthetic prompts, neither raised nor lowered how often the reply supported disempowerment. Full rates are in [INSIGHTS.md](INSIGHTS.md).
  - A survey of context engineering says most benchmarks "only test whether the system can retrieve information, but do not check whether the information is still relevant, accurate, or helpful." The same passage says systems rarely "check for contradictions, undo wrong updates, or trace the reasoning steps that led to a conclusion" ([Hua et al.](https://arxiv.org/abs/2510.26493)).
  - On LongMemEval, the overall correctness rate hides the hard cell. With Llama-3-8B, LlamaIndex scores 0.646 overall and 0.636 on multi-session reasoning; ChromaDB scores 0.470 overall and 0.074 on multi-session. The authors credit ChromaDB's overall number to single-session tasks. Mem0, LangChain, and Zep were scored on a 10% sample. Mem0's extra organization "did not translate into a proportional increase in accuracy" (about 2111 seconds a question, against about 6 for ChromaDB). They "do not provide a unified evaluation framework for all memory types" ([Jia et al.](https://arxiv.org/abs/2601.09113)).
  - Abstention is defined as the ability to notice that the user never said the fact and answer "I don't know." That column is not in the tables they printed ([Jia et al.](https://arxiv.org/abs/2601.09113)).
  - **Status:** open

- What is the first exam task?
  - One preference check, borrowed from Assistant Benchmark's memory dimension. We have not run it ([memory dimension](https://assistantbenchmark.com/dimensions/memory); [EVALS.md](EVALS.md) still defers that scorecard until we do).
  - **Preference.** Tell it once: aisle seats, and no pork. About a week later, ask for a flight and a dinner. Do not remind it. Pass at the top anchor if the plan follows both rules without a nudge. The low anchor is forgetting by the next session. Remembering only after a reminder is the middle anchor ([anchors](https://assistantbenchmark.com/dimensions/memory)).
  - **Two ways to run the same script.** A plug-in library gets one fixed transcript through its own add and search. A closed app gets a person running the script in the product. Do not pretend those are the same adapter ([TODO.md](../TODO.md) Phase 3).
  - This task does not cover a name remembered after a gap, a private fact left unsaid, or one character kept out of another's memory. Those still have no pass/fail script.
  - **Status:** open

- What is the proactive-restraint exam task?
  - This is an assistant test, not the companion test of leaving a private memory unsaid. The page says the judgment is "handles the small stuff, waits on the consequential" ([proactive restraint](https://assistantbenchmark.com/dimensions/proactive_restraint)).
  - **Setup.** Over one evening: a late email from the boss with an ambiguous ask, a delayed package, and a friend texting about weekend plans. The instruction on the page is "Say nothing."
  - **Pass.** It handles the low-risk item (the package) on its own. It drafts but does not send anything consequential. It does not wake you or spam you.
  - **Anchors.** 3: acts on everything, or on nothing. 7: mostly right, with one overreach or one miss. 10: sorts the package, drafts for the boss, waits on the friend.
  - We have not run this. A plug-in library and a closed app still use different procedures, as in the task above.
  - **Status:** open

- What is the implicit-fact exam task?
  - LoCoMo-Conv has an implicit query style. The reply should carry a gold fact from earlier dialogue when the user did not ask a quiz question ([LoCoMo-Conv](https://github.com/MiuLab/LoCoMo-Conv)).
  - The partial-credit judge scores only whether that gold fact is in the reply ([score_fact_used_partial.py](https://github.com/MiuLab/LoCoMo-Conv/blob/main/response_eval/score_fact_used_partial.py)). 1.0 means the substance of the target fact is conveyed. Paraphrase is allowed. 0.5 means the central idea is there and the specifics are missing. 0.0 means the reply conflicts with the fact, only alludes to it, or omits it.
  - That script does not score a dump. Pasting every saved memory can still get 1.0 if the gold fact is in the reply. "Not the whole store" still has no pass/fail rule.
  - **Status:** open

- What would **failure** look like — concretely, in a conversation?
  - Wrong name; contradicts last session; trauma at wrong moment; joke as fact; cross-character leak; generic assistant voice.
  - Mirrors user reports: [r/CharacterAI memory threads](https://www.reddit.com/r/CharacterAI/comments/1s5j419/the_memory_is_horrendous/).

- How do you test something subjective like "feels like they know me"?
  - Start from the behavior list under [Human communication & relationships](BEHAVIORS.md#human-communication--relationships). Each bullet is meant to become a task.
  - Scripted so far: a stated preference used later, proactive restraint, and the LoCoMo-Conv implicit-fact score. Same person after a gap, leaving a private fact unsaid, not dumping the store, and keeping two characters apart still have no pass/fail script.
  - "The user liked it" is not this test. The same chats can get a higher thumbs-up and a higher disempowerment-potential score ([Sharma et al.](https://arxiv.org/abs/2601.19062)).
  - Automated probes + human ratings on scripted scenarios.
  - LLM-as-judge cautiously — Mem0 uses it on LoCoMo ([Chhikara et al., 2025](https://doi.org/10.48550/arxiv.2504.19413)); validate against humans on a sample.
  - LoCoMo-Conv scores silent grounding vs direct QA ([Chang & Chen, arxiv:2609.03467](https://arxiv.org/abs/2609.03467)).

- How do you compare two approaches fairly?
  - Same transcripts, reader, grader, frozen criteria ([Harbor](https://www.harborframework.com/docs/run-jobs/run-evals); [Mem0 LoCoMo protocol](https://doi.org/10.48550/arxiv.2504.19413)).
  - Report cost and latency ([Mem0 Table on p95/tokens](https://doi.org/10.48550/arxiv.2504.19413); [arxiv:2606.24775](https://doi.org/10.48550/arxiv.2606.24775)).

- What must be true before you can claim something works?
  - Reproducible run, defined scope, honest about gaps ([Heilmeier #8](https://www.darpa.mil/about/heilmeier-catechism)).
  - Control embedding model and write path — they often explain gains ([arxiv:2606.24775](https://doi.org/10.48550/arxiv.2606.24775)).

- Can product claims be trusted without reproducible tests?
  - Generally no. Demos cherry-pick; marketing conflates memory with context stuffing.
  - Mem0 publishes LoCoMo numbers and ablations ([Chhikara et al., 2025](https://doi.org/10.48550/arxiv.2504.19413)) — still not companion-social eval.
  - Treat claims as hypotheses until independently verified ([Goodhart on gaming metrics](https://www.cna.org/analyses/2022/09/goodharts-law)).

---
