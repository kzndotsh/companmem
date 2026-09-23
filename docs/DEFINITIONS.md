# Definitions

What the words mean. Index: [Questions](QUESTIONS.md).

Answers are working notes. Citations are inline links. A question stays `open` until it has a falsifier.

---

## Core definitions

- What is memory?
  - In AI systems: **persistent state across sessions** — not weights, not just the current prompt ([Pathak, 2025](https://ninadpathak.com/blog/context-windows-vs-memory/); [arxiv:2606.06448](https://doi.org/10.48550/arxiv.2606.06448): external memory decouples capacity from context length).
  - In humans: stored information retrievable later; **episodic** (events) vs **semantic** (facts) ([Tulving, 1972 via PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2952732/); [UCSF Memory Center](https://memory.ucsf.edu/brain-health/memory)).

- What is context?
  - Everything the model sees **in this one inference call** — system prompt, messages, retrieved chunks, tool results ([Atlan](https://atlan.com/know/memory-layer-vs-context-window/)).
  - Fixed token budget; cleared between calls unless you explicitly carry state forward ([Pathak](https://ninadpathak.com/blog/context-windows-vs-memory/)).
  - Analogized to **L1 cache**, not memory ([arxiv:2603.09023](https://arxiv.org/abs/2603.09023)).

- What is reasoning?
  - The model using in-context information to produce outputs — chain-of-thought, planning, tool use (inside one inference call).
  - Reasoning happens *inside* the call; memory is what you fetch *into* the call from outside ([Pathak](https://ninadpathak.com/blog/context-windows-vs-memory/); [Generative Agents planning loop](https://arxiv.org/abs/2304.03442)).

- What is a harness?
  - A controlled runner that feeds fixed tasks to a system and records outputs, rewards, cost, and errors ([Harbor docs](https://www.harborframework.com/docs/run-jobs/run-evals); [Harbor GitHub](https://github.com/harbor-framework/harbor)).
  - Separates agent + environment + verifier so comparisons stay fair ([Harbor task model](https://www.harborframework.com/docs/run-jobs/run-evals): instruction, environment, test script).
  - Context-engineering changes need eval pipelines to measure whether prompt/RAG tweaks actually work ([PEG: context engineering guide](https://www.promptingguide.ai/guides/context-engineering-guide)).

- What is the difference between **remembering** and **retrieving**?
  - **Retrieving:** pulling stored text/facts into context (mechanical) — standard RAG pipeline ([Lewis et al., 2020](https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf)).
  - **Remembering** (what users mean): the agent *acts as if* the past matters — right fact, right time, right tone ([LoCoMo-Conv / in-situ use](https://github.com/MiuLab/LoCoMo-Conv); [Zeng et al., 2026](https://doi.org/10.1145/3768310.3807827) on inappropriate recall).
  - You can retrieve without remembering (wrong fact, creepy timing, generic reply).

- What belongs in memory vs what belongs only in the active turn?
  - **Active turn:** immediate intent, current scene, last few exchanges (working memory / context window).
  - **Memory:** stable facts, preferences, relationship history, things that should survive session end ([MemGPT virtual memory tiers](https://doi.org/10.48550/arxiv.2310.08560)).
  - Rule of thumb: if losing it next session would break continuity, it belongs in memory ([Pathak](https://ninadpathak.com/blog/context-windows-vs-memory/)).

- What is the difference between a **log** (everything that happened) and **memory** (what matters later)?
  - **Log:** append-only transcript — complete, heavy, noisy.
  - **Memory:** curated subset — extracted, summarized, typed, or forgotten ([Mem0 extract/consolidate/retrieve](https://doi.org/10.48550/arxiv.2504.19413)).
  - Humans do not replay full logs; they reconstruct gist ([Schuck & Doeller, *Nature Human Behaviour*, 2024](https://www.nature.com/articles/s41562-023-01799-z)).

---
