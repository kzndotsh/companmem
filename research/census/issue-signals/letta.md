# Letta issue signals

Slice I. Searched GitHub `repo:letta-ai/letta` for memory, persona, forget, leak on 2026-09-11.

| source_url | user_symptom | hole | dimension | label | fixture_idea | steal_or_avoid |
| --- | --- | --- | --- | --- | --- | --- |
| https://github.com/letta-ai/letta/issues/3388 | Agent uses core_memory_replace to poison persona; poison persists across independent eval tasks on same daemon because no hard teardown between sandboxes. | 7 | poisoning | measured | Hole 7 planted write to persona.md; next task must still pass persona predicates. | Avoid writable persona without trust tags. Harness needs teardown per trial. |
| https://github.com/letta-ai/letta/issues/3270 | sliding_window compaction at 15% evicts entire history; only summary remains. | 9 | forgetting | measured | User says forget that; compaction wipes unrelated facts. PASS_TO_PASS other facts hold. | Avoid compaction that is summarize-all. Distinct from user forget-that. |
| https://github.com/letta-ai/letta/issues/3399 | Core memory blocks with `/` in label are created but cannot be read (404). | none | ontology | measured | Typed block names must be addressable or illegal at write. | Avoid string labels without validation. |
| https://github.com/letta-ai/letta/issues/3332 | Request for multi-profile memory for objective vs adversarial reasoning. | 5 | identity_split | inferred | Two agents share server; adversarial profile leaks into companion profile. | Steal explicit profile isolation as default. |

Search note. 393 issues matched. #3388 closed not_planned; still valid architectural signal for eval harness teardown.
