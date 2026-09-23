# Building

How the work would get built, once a question is settled. Index: [Questions](QUESTIONS.md).

Answers are working notes. Citations are inline links. A question stays `open` until it has a falsifier.

---

## Building it (dev, workflow, agentic coding)

- When do we **write code** vs stay in docs and research?
  - Code when only running something answers the question (spike, benchmark) ([Heilmeier #8: exams](https://www.darpa.mil/about/heilmeier-catechism)).
  - Stay in docs while goal, success criteria, and falsification path unclear.

- What is the minimum bar before something counts as "implemented" — runs locally, has tests, reviewed?
  - **Runs** on clean machine with documented setup.
  - **Tests** for anything we rely on ([verification-first](https://se-ml.github.io/agentic_patterns/07-verification-first/)).
  - **Reviewed** diff — human or separate verifier ([AVP](https://github.com/ontojoseki/agentic-verification-protocol)).

- How do we structure the repo so research and code don't blur together?
  - Separate `docs/` from implementation; keep throwaway spikes out of git.
  - Harbor pattern: task = instruction + environment + verifier, kept distinct ([Harbor](https://www.harborframework.com/docs/run-jobs/run-evals)).

- What belongs in version control vs notes vs throwaway experiments?
  - **Git:** code, fixtures, specs, decisions.
  - **Throwaway:** time-boxed spikes ([Heilmeier risks/timeline](https://www.darpa.mil/about/heilmeier-catechism)).

### Working with agents

- What is **agentic coding** — agent writes, human reviews, or something else?
  - Agent plans and edits; human sets goal, reviews diff, approves.
  - Loop: gather context → act → **verify** → repeat ([verify-first harness](https://www.theaioperator.net/p/coding-with-agents-the-verify-first) citing Anthropic production loop; [OpenAI tools guide](https://developers.openai.com/api/docs/guides/tools)).

- What should the human always do vs delegate to an agent?
  - **Human:** goal, accept/reject, security, "right problem" ([Coordinator–Implementor–Verifier](https://www.augmentcode.com/guides/agentic-sdlc-coordinator)).
  - **Delegate:** boilerplate, search, refactors with clear tests.

- How do you give an agent enough context without dumping the whole repo?
  - Point to files, rules, question being answered.
  - MCP **resources** for scoped data ([MCP spec](https://modelcontextprotocol.io/specification/2025-11-25/index)).

- When should an agent explore vs execute a narrow task?
  - **Explore** when location/approach unknown.
  - **Execute** when bounded — reduces scope creep ([Augment: bounded workflow first](https://www.augmentcode.com/guides/agentic-sdlc-coordinator)).

- How do you stop an agent from **scope creep**?
  - Explicit scope; small commits; reject unrelated diffs ([verification-first: review actual diff](https://se-ml.github.io/agentic_patterns/07-verification-first/)).

- How do you stop an agent from **pretending** something works?
  - Require run output before accepting ([SE-ML verification-first](https://se-ml.github.io/agentic_patterns/07-verification-first/)).
  - Separate verifier session, no shared reasoning ([AVP](https://github.com/ontojoseki/agentic-verification-protocol)).
  - ~46% of agentic fix PRs rejected in AIDev dataset ([verify-first article](https://www.theaioperator.net/p/coding-with-agents-the-verify-first)).

### Trust and verification

- What is **falsified code** — looks complete, never ran, wrong API, stub that returns success?
  - Code matching the prompt visually but not executed against real deps ([SE-ML: sycophantic tests](https://se-ml.github.io/agentic_patterns/07-verification-first/)).
  - Hallucinated imports/signatures; tests asserting buggy behavior.

- How do you catch code that was **generated to match the prompt** but not reality?
  - Run, typecheck, lint, integration test ([SE-ML](https://se-ml.github.io/agentic_patterns/07-verification-first/)).
  - Compare against library docs / `node_modules` types.

- What must be **run** before we trust a change — tests, lint, manual smoke, full flow?
  - Minimum: typecheck/lint + relevant tests ([SE-ML](https://se-ml.github.io/agentic_patterns/07-verification-first/)).
  - User-facing: E2E smoke ([verify-first: hooks in agent loop](https://www.theaioperator.net/p/coding-with-agents-the-verify-first)).
  - Cheapest falsifying check first ([SE-ML](https://se-ml.github.io/agentic_patterns/07-verification-first/)).

- Who verifies — always the human, or can another agent review?
  - Separate agent helps with isolated context ([Augment CIV pattern](https://www.augmentcode.com/guides/agentic-sdlc-coordinator); [AVP Verifier role](https://github.com/ontojoseki/agentic-verification-protocol)).
  - Human approves termination; agents can sycophantically agree ([SE-ML on sycophantic testing](https://se-ml.github.io/agentic_patterns/07-verification-first/)).

- How do we separate **"the agent said it works"** from **"we proved it works"**?
  - Artifact: command log, test output, CI green — not summary ([AVP: claims vs artifacts](https://github.com/ontojoseki/agentic-verification-protocol)).
  - `policy_version` + replayable runs ([verify-first](https://www.theaioperator.net/p/coding-with-agents-the-verify-first)).

- When is a screenshot or log output required as evidence?
  - Non-deterministic UI, long runs, baseline comparisons ([Harbor trial artifacts](https://www.harborframework.com/docs/run-jobs/run-evals)).

### Process and discipline

- Research first, implementation second — how do we enforce that without stalling forever?
  - Time-box; define decision that unblocks code ([Heilmeier](https://www.darpa.mil/about/heilmeier-catechism)).
  - Spikes labeled and time-limited.

- What is a **spike** vs a **product** — when is throwaway code OK?
  - **Spike:** answers one question ([Heilmeier #8 midterm exam](https://www.darpa.mil/about/heilmeier-catechism)).
  - **Product:** tested, maintained, intended to last.

- How small should changes be — one concern per commit, per PR?
  - One logical concern per commit — easier review/revert ([SE-ML: review diff complexity](https://se-ml.github.io/agentic_patterns/07-verification-first/)).

- What triggers a commit — user asks, milestone hit, end of session?
  - **User asks** (our rule). No drive-by commits.

- How do we avoid **rewriting the same thing** because we skipped writing down decisions?
  - Answers live next to questions; one-line "we chose X because Y."

- What docs must exist before agents touch architecture — if any?
  - Goal, falsifiable success criteria, verification commands ([Heilmeier #1 and #8](https://www.darpa.mil/about/heilmeier-catechism)).

### Quality and maintenance

- What tests are worth writing at each stage?
  - **Spike:** one script proving hypothesis.
  - **Product:** unit + integration on memory read/write ([Harbor verifier pattern](https://www.harborframework.com/docs/run-jobs/run-evals)).
  - Tests before implementation to avoid sycophantic tests ([SE-ML TDD note](https://se-ml.github.io/agentic_patterns/07-verification-first/)).

- How do we keep dependencies and tooling boring and reproducible?
  - Lockfiles, pinned versions, documented setup.

- What runs in CI — and what is too expensive or flaky for CI?
  - **CI:** lint, typecheck, fast unit tests, fixtures without live LLM.
  - **On demand:** full LLM bakeoffs ([Mem0-scale eval cost](https://doi.org/10.48550/arxiv.2504.19413)).

- How do we handle secrets, API keys, and local-only config?
  - `.env` gitignored; `.env.example` with dummies; never commit secrets ([MCP security considerations](https://modelcontextprotocol.io/specification/2025-11-25/index)).

- When do we delete code vs archive it?
  - **Archive** when informative but unmaintained.
  - **Delete** when misleading.

- How do we know when a prototype should be promoted, rewritten, or thrown away?
  - **Promote:** spike answered question, tests pass ([Heilmeier final exam](https://www.darpa.mil/about/heilmeier-catechism)).
  - **Rewrite:** right idea, wrong structure.
  - **Throw away:** hypothesis falsified.

---
