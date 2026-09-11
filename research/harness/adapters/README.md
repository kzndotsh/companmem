# Harness adapters

| id | status | install |
| --- | --- | --- |
| `mem0` | implemented | `pip install mem0ai sentence-transformers` |
| `mem0-shared-bag` | implemented | same as mem0 |
| `companmem` / sketches | implemented | `pip install httpx` (Kiro in `.env`) |
| `graphiti` | implemented | `pip install graphiti-core sentence-transformers`; Neo4j via `docker compose -f research/harness/docker/neo4j-compose.yml up -d`; Kiro in `.env` |
| `letta` | stub | Letta server + `letta-client` |
| `honcho` | stub | Honcho API key + SDK |
| `st-world-info` | stub | SillyTavern World Info semantics TBD |

Stubs raise `AdapterNotReadyError` so `run.py` skips them unless explicitly requested.

Named external baselines are tracked in `research/harness/registry.json`. Implement adapters without changing public fixture predicates.
