# Harness adapters

| id | status | install |
| --- | --- | --- |
| `mem0` | implemented | `pip install mem0ai sentence-transformers` |
| `mem0-shared-bag` | implemented | same as mem0 |
| `companmem` / sketches | implemented | `pip install httpx` (Kiro in `.env`) |
| `graphiti` | implemented | `pip install graphiti-core sentence-transformers`; Neo4j via `docker compose -f research/harness/docker/neo4j-compose.yml up -d`; Kiro in `.env` |
| `letta` | implemented | MemFS simulation (`system/` always-on + `reference/` overlap retrieval); no Letta server |
| `honcho` | implemented | Peer card + explicit conclusions simulation; no Honcho server |
| `st-world-info` | implemented | Keyword/constant World Info activation simulation |

Stubs raise `AdapterNotReadyError` so `run.py` skips them unless explicitly requested.

Named external baselines are tracked in `research/harness/registry.json`. Implement adapters without changing public fixture predicates.
