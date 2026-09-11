# Graphiti issue signals

Slice I. Searched GitHub `repo:getzep/graphiti` for memory, forget, invalidate on 2026-09-11.

| source_url | user_symptom | hole | dimension | label | fixture_idea | steal_or_avoid |
| --- | --- | --- | --- | --- | --- | --- |
| https://github.com/getzep/graphiti/issues/1876 | add_episode writes to cloned DB per group_id but search reads configured DB; episodes exist but get_episodes returns empty with no error. | 5 | identity_split | measured | Two companions as group_ids; B's read path misses A's write DB. Silent empty retrieve. | Avoid read/write scope mismatch. Harness must assert non-empty when write succeeded. |
| https://github.com/getzep/graphiti/issues/1602 | RFC for salience-based fact filtering and multi-tier memory. | 2 | silence | inferred | High-salience trauma fact retrieved every turn; need skip-at-read policy. | Steal salience tier idea; read policy still separate from score. |
| https://github.com/getzep/graphiti/issues/1863 | User asks whether graphiti supports durable memory across sessions. | 10 | temporal | inferred | Three-month reunion after silence; episodes need valid_at and gap-aware opening. | Steal valid_at windows; reunion fixture still missing in public evals. |
| https://github.com/getzep/graphiti/issues/1506 | FalkorDB edge fulltext search times out on broad queries. | 8 | cost_shape | measured | Wall-time budget fails run when graph search exceeds N seconds. | Meter retrieve latency per turn. |

Search note. 135 issues matched. #1876 is open with PR #1878; strong cross-character isolation analog.
