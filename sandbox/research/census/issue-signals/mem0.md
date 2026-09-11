# Mem0 issue signals

Slice I. Searched GitHub `repo:mem0ai/mem0` for memory, forget, leak, persona, character on 2026-09-11.

| source_url | user_symptom | hole | dimension | label | fixture_idea | steal_or_avoid |
| --- | --- | --- | --- | --- | --- | --- |
| https://github.com/mem0ai/mem0/issues/4956 | After v3 upgrade, ADD-only extraction keeps contradictory employer facts; retrieval returns stale Company A instead of Company B. | 4 | supersession | measured | User retcons job; old row still wins retrieve. FAIL_TO_PASS new fact in reply; PASS_TO_PASS old row invalidated not deleted. | Avoid ADD-only without supersession. Steal soft-invalidate with latest_only if Platform Dream lands in OSS. |
| https://github.com/mem0ai/mem0/issues/5428 | Truncated extraction JSON drops all facts when max_tokens hit mid-parse. | 9 | write_policy | measured | Forget-that then extract truncates; revoked fact reappears from partial write. | Avoid unbounded extract output without salvage parse. |
| https://github.com/mem0ai/mem0/issues/7283 | Contributor wants faithfulness check before memory write (pluggable verification). | 7 | poisoning | inferred | Planted joke-as-fact should be rejected at write, not filtered at read. | Steal write-time verifier hook; separate from store. |
| https://github.com/mem0ai/mem0/issues/7260 | Server endpoints that call LLM have no rate limiting. | 8 | cost_shape | measured | Cost meter should fail run when extract+search per turn exceeds budget. | Meter LLM calls per turn in harness. |

Search note. 1076 issues matched broad query. Rows above are highest-signal for companion holes, not infra-only bugs.
