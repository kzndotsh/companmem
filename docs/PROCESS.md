# Research process

How we run the research. Index: [Questions](QUESTIONS.md).

Answers are working notes. Citations are inline links. A question stays `open` until it has a falsifier.

---

## Research process

- How do you organize research?
  - Start from questions, not solutions. Group by theme (definitions, human behavior, tech, proof).
  - One doc per layer: questions → answers → decisions → experiments.
  - Revisit when new evidence contradicts an answer; tag status: settled / open / deferred.
  - Pressure-test proposals with the [Heilmeier Catechism](https://www.darpa.mil/about/heilmeier-catechism) (DARPA): eight questions on goals, state of art, novelty, impact, risks, cost, timeline, and success exams.

- How do you exhaust all options when attempting to solve groundbreaking complex problems?
  - Map the problem space before picking an architecture: definitions, failure modes, prior art, constraints ([Heilmeier #2–3](https://www.darpa.mil/about/heilmeier-catechism)).
  - Use structured comparison (same axis for every option) rather than reading products one by one — e.g. decompose memory into representation, extraction, retrieval, maintenance ([arxiv:2606.24775](https://doi.org/10.48550/arxiv.2606.24775)).
  - Stop when options cluster — then test whether the cluster is correct or a shared blind spot ([CMA / continuum memory](https://arxiv.org/pdf/2601.09913v1)).

- What is a **question** vs a **claim** vs **evidence** in our docs?
  - **Question:** something we do not know yet ("What is memory?").
  - **Claim:** a statement we believe ("RAG alone is not long-term memory") — cf. [CMA](https://arxiv.org/pdf/2601.09913v1): RAG treats memory as stateless lookup.
  - **Evidence:** source or observation that supports or falsifies a claim (paper, benchmark result, user report).

- What does "done" mean for a research item (answered, cited, falsifiable)?
  - **Answered:** we can state a position in plain language with at least one source or observation.
  - **Cited:** the source is linked and we know what it actually measured ([Heilmeier #8](https://www.darpa.mil/about/heilmeier-catechism): midterm and final "exams").
  - **Falsifiable:** we could imagine a test or counterexample that would change our mind.

- How do you know when you're answering the right question?
  - The answer changes what you would build, measure, or refuse to do ([Heilmeier #4](https://www.darpa.mil/about/heilmeier-catechism): "who cares?").
  - If the answer has no downstream effect, it may be trivia — defer it.

- How do you avoid optimizing for what's easy to measure?
  - [Goodhart's Law](https://www.cna.org/analyses/2022/09/goodharts-law): when a measure becomes a target, it ceases to be a good measure ([Strathern via MPRA](https://mpra.ub.uni-muenchen.de/90649/1/MPRA_paper_90649.pdf)).
  - Name what your metric does *not* capture before trusting a score.
  - Pair automated scores with behavioral probes ([Wispaper on LoCoMo limits](https://www.wispaper.ai/en/research/agent-memory-evaluation-beyond-completion)).
  - LoCoMo QA measures recall of facts in long chat — not timing, relationship feel, or character consistency ([Maharana et al., ACL 2024](https://aclanthology.org/2024.acl-long.747/)).

---
