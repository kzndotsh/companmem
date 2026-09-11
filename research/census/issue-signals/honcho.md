# Honcho issue signals

Slice I. Searched GitHub `repo:plastic-labs/honcho` for memory, leak, persona, forget on 2026-09-11.

| source_url | user_symptom | hole | dimension | label | fixture_idea | steal_or_avoid |
| --- | --- | --- | --- | --- | --- | --- |
| https://github.com/plastic-labs/honcho/issues/817 | Deriver attributes AI agent Fred's instruction to human peer Rodrigo in multi-peer session. | 4 | identity_split | measured | Three writers: user, character, other agent; user_bio must not ingest agent speech. | Avoid extract-about-peer from others' messages. Speaker filter at write. |
| https://github.com/plastic-labs/honcho/issues/729 | Dreamer accumulates near-duplicate observations despite dedup guard. | 8 | cost_shape | inferred | Token/cost grows with duplicate derives; meter derives per turn. | Steal dedup at write; still need cost meter. |
| https://github.com/plastic-labs/honcho/issues/728 | Deriver marks work units processed when embedding save fails; silent data loss. | 9 | forgetting | measured | User forget-that; store reports success but embedding missing; fact leaks next turn. | Harness infra_ok=0 on silent write failure. |
| https://github.com/plastic-labs/honcho/issues/1105 | User peer card stays empty under Hermes auto-config despite agent-side observations. | 1 | identity_split | inferred | 50 sessions; user model empty while agent model full; identity drift. | Steal dual peer cards; user vs character autobiography split. |

Search note. 67 issues matched. #817 has fix PRs (#823, #943, #1108); symptom still defines hole 4 writer confusion.
