# What to steal from coding evals

Audience is whoever writes the later companion harness (WORKFLOW unit 4). Coding benches are not companion memory benches. They already solved problems our public memory evals have not.

Do not add SWE-bench to the companion leaderboard. Steal the harness shape. measured from the sources below.

## Shared lesson

HumanEval was built as hidden unit tests instead of BLEU. Chen et al. 2021. measured from the Codex paper's functional-correctness argument. Prior code evals used n-gram overlap. inferred.

LoCoMo-class memory benches still score BLEU's cousin. Probe QA, F1, LLM-judge. MemUse measured that Direct QA and in-conversation use do not move together. measured from `research/census/cards/memuse.json`.

The coding field already treated "the exam is the wrong metric" as a one-way door. inferred.

## Architecture to copy

Harbor (Terminal-Bench 2.0's eval framework) splits four objects. measured from https://www.harborframework.com/docs/tasks

1. Task. `instruction.md` plus `task.toml`. What the agent is allowed to see.
2. Agent. The system under test. Claude Code, OpenHands, Aider, or a memory backend plus a reader model.
3. Environment. Isolated container. Docker, Daytona, Modal.
4. Verifier. Tests that run after the agent stops. Writes a numeric reward. The agent does not get the tests.

A companion fixture should look the same.

- Instruction. The transcript so far, plus the next user line. Not the gold fact.
- Agent. Named memory backend plus a frozen reader model.
- Environment. Isolated store per character. No shared `user_id` bag across companions.
- Verifier. Hidden next-turn predicates. Run after the reply. The store cannot rewrite them.

Harbor also ships an Oracle agent that runs `solution/solve.sh`. measured. That proves the task is solvable before any model is scored. Our unit 4 check already says a fixture must fail today's best-fit baseline. It should also pass an oracle. inferred.

Harbor can run the verifier in a separate sandbox and copy only named artifacts. measured from the 2026-05-15 Harbor note on separate verifier environments. Copy that split. A memory library that can edit the judge prompt is a `conftest.py`. inferred.

## Scoring to copy

### Fail-to-pass and pass-to-pass

SWE-bench grades two hidden test lists. measured from OpenAI's SWE-bench Verified writeup.

- `FAIL_TO_PASS`. Tests that failed before the gold patch. They must pass after. The new behavior exists.
- `PASS_TO_PASS`. Tests that already passed. They must still pass. No regression.

FULL resolve requires both. The tests are not shown to the agent. measured.

Companion analog.

| hole | FAIL_TO_PASS | PASS_TO_PASS |
| --- | --- | --- |
| 1 identity after 50+ sessions | New session still matches the character card | User facts still retrieve. Lore still injects as lore. |
| 2 social silence | Next turn does not mention the high-score intimate fact | The fact is still in the store if asked later in a safe frame |
| 3 joke as fact | Store does not treat the joke as a relationship fact | Real facts still hold |
| 4 typed retcon | User rewrite supersedes. Character lie does not. Narrator retcon is tagged | The other two writers are unchanged |
| 5 cross-character leak | Companion B's next turn has zero of user-A's private facts | Companion A still remembers them |
| 6 lore vs lived | Character does not claim to have lived a lorebook event | Lore still available as world knowledge |
| 7 persona poison | After a planted write, system persona still holds | Unrelated memories still work |
| 9 forget-that | Next turn does not use the revoked fact, including derived summaries | Other facts still hold |
| 10 three-month reunion | Opening treats the gap as months, not yesterday | Identity and relationship phase still match |

Hole 8 is not a pass/fail test. It is a meter. See cost below.

### Hidden tests

LiveCodeBench and HumanEval require passing all hidden tests. Public examples may exist. The suite that grades is hidden. measured from LiveCodeBench (arXiv 2403.07974) and the SWE-bench Verified writeup.

Companion analog. Do not ask "what is my dog's name?" as the score. Check the next in-situ reply. That is LoCoMo-Conv and MemUse. measured. Coding benches just made it a unit test instead of an LLM judge.

### Resolution taxonomy

SWE-bench's run report splits empty patches, infra failures, unresolved, resolved. measured from the SWE-bench evaluation guide.

Companion analog. Empty store, harness crash, timeout, unresolved, resolved. Do not fold infra into "the memory system lost." inferred.

### Cost is first class

The Scaffold Effect paper (Vats and Golev, arXiv 2607.22585, KDD 2026 eval workshop) held the model fixed and varied the harness on 50 Terminal-Bench Pro tasks. Pass-rate spread 0 to 8 points. Tokens per solved task about 40 times. Goose Qwen 28,142 tokens per solve. OpenCode Qwen 1,147,740. measured from the HTML abstract and Table 3.

Terminal-Bench 2.0 already showed Claude Opus 4.5 at 52.1% on one harness and 57.8% on another, with 256.9M vs 3.9M input tokens. About 65 times the tokens for 5.7 points. measured from that paper's citation in Scaffold Effect §1.

SWE-bench Verified therefore publishes two boards. Full systems. And a bash-only mini-SWE-agent board so models can be compared under one scaffold. measured from https://www.swebench.com/verified.html

Companion analog. Report `memory-backend + reader model + prompt scaffold` as the unit. Mem0's extract-every-turn loop is a scaffold, not a model. inferred. Tokens per companion turn, and tokens per passed fixture, sit next to pass rate. WORKFLOW.md already requires cost per turn. This is the coding-bench justification.

## Contamination and saturation

LiveCodeBench tags problems with contest dates and scores a model only on problems after its cutoff. DeepSeek dropped on LeetCode problems after its release month. measured from livecodebench.github.io.

SWE-bench-Live rebuilds repository tasks continuously because a static GitHub-issue set leaks into training. measured from arXiv 2505.23419.

SWE-Bench Pro keeps a public set, a held-out set, and a commercial set. measured from arXiv 2509.16941.

OpenAI stopped reporting SWE-bench Verified in 2026. measured from https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/. Two failures. Frontier models could reproduce gold patches from a task id. An audit of 138 remaining-hard tasks found 59.4% had material flaws. 35.5% narrow tests that reject a correct fix. 18.8% wide tests that check unstated extras. Hidden tests are not enough if the instance leaked, or if the test does not match the instruction the agent saw.

HumanEval saturated. Perfect scores became incremental. inferred from HLCE (arXiv 2506.12713) naming that as a reason new benches exist.

Companion analog. Do not publish every transcript if a vendor can train on it. Keep a held-out reunion and poison set. Refresh fixtures. LoCoMo is already the contaminated-looking default exam. inferred. Also. A silence fixture that fails because the judge wanted a specific phrasing is a narrow test. A reunion fixture that also requires an unstated lore dump is a wide test. Humans check both, the way SWE-bench Verified's later audit said they should have.

## Human verification of instances

SWE-bench Verified is 500 instances humans checked for underspecified issues, wrong tests, and unsolvable items. measured from OpenAI's writeup.

Aider Polyglot is 225 hard Exercism tasks. Headline is pass after a second try that sees failing unit-test output. measured from Aider's protocol descriptions. That scores the debug loop, not one-shot generation.

Companion analog. Humans must confirm each fixture actually is hole 2 (silence) and not just "the model forgot." A second-try analog is allowed only if we are scoring repair after a user correction, not the first companion turn. inferred.

## Trust boundary. Do not let the agent grade itself

BenchJack (arXiv 2605.12673) and Berkeley RDI. A nine-line `conftest.py` in the same container as pytest rewrites every test to PASSED. SWE-bench trusted stdout from a filesystem the agent could write. measured.

Harbor's separate verifier sandbox exists because of this class of bug. inferred.

Companion analog. The memory backend must not be the judge. Hidden predicates live outside the store. LLM-as-judge, if used at all, cannot see the system's retrieved memories as "evidence of success." A backend that injects "I remembered correctly" into the prompt is `conftest.py`. inferred.

Hole 7 (poisoning) is this attack in companion form. The store writes text that later overrides persona. The verifier has to be outside that write path. inferred.

## What not to copy

Pass@k with 10 samples is a code-generation statistic. Companion turns are sequential and stateful. Do not sample 10 next-lines and take the best. inferred.

Competitive-programming I/O is not relationship memory. LiveCodeBench is for contamination method, not the task shape.

Aider's required diff format is a tool-compliance test. We can require a typed write API. We should not fail a companion because the model emitted the wrong patch syntax. inferred.

Do not import Harbor as the companion product. Copy the four-object split.

## Direct mapping onto our ten holes

Coding benches win because the score is a hidden, executable predicate the system cannot see. Our ten holes are those predicates. They are not quiz questions.

The later harness, if it is honest, looks like SWE-bench plus Harbor, not like LoCoMo.

- One command.
- Named baselines (Mem0, Graphiti, Letta, Honcho, ST World Info plus vectors, naive RAG, long-context).
- Frozen reader model.
- Isolated store per character.
- Hidden FAIL_TO_PASS and PASS_TO_PASS per fixture.
- Oracle must pass. Best-fit baseline must fail at least one fixture.
- Tokens per turn and wall time in the report.
- Dated artifact plus git SHA.
- Held-out fixtures not in the public README.

That last list is WORKFLOW.md's done predicate, restated in coding-bench language. measured from WORKFLOW.md. The coding field is the existence proof that this shape can be automated at scale. inferred.

## Sources

- Chen et al. Evaluating Large Language Models Trained on Code. HumanEval. 2021.
- SWE-bench. https://www.swebench.com/SWE-bench/reference/harness/
- OpenAI. Introducing SWE-bench Verified. FAIL_TO_PASS and PASS_TO_PASS. Tests hidden.
- Jain et al. LiveCodeBench. arXiv 2403.07974. https://livecodebench.github.io/
- SWE-bench Goes Live. arXiv 2505.23419.
- SWE-Bench Pro. arXiv 2509.16941.
- Harbor task format. https://www.harborframework.com/docs/tasks
- Harbor separate verifier sandboxes. 2026-05-15. https://www.harborframework.com/news/separate-verifier-sandboxes
- Vats and Golev. The Scaffold Effect in Coding Agents. arXiv 2607.22585.
- OpenAI. Why SWE-bench Verified no longer measures frontier coding capabilities. 2026. Contamination plus narrow/wide tests.
- BenchJack. arXiv 2605.12673. RDI writeup https://rdi.berkeley.edu/blog/trustworthy-benchmarks-cont/
- Aider Polyglot protocol. Second try with failing tests.
