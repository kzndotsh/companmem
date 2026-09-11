# Current state

Overwrite this file each session. The audit TSV is the log. This is the snapshot.

- Date. 2026-09-11
- LLM. Kiro gateway (`.env` auto-loaded). No OpenAI.
- companmem. Heuristic ingest + Kiro reader **9/9**. LLM extract **9/9** (`run_llm_extract.py`).
- Held-out. `persona-poison-alt` oracle PASS, naive FAIL, companmem PASS (`run_held_out.py`).
- Graphiti. Adapter implemented (Neo4j + Kiro extract/search). `joke-as-fact` FAIL as expected.
- Stubs. Letta, Honcho, ST World Info.
- Freeze. Public fixture predicates. Adapt harness, not the exam.
