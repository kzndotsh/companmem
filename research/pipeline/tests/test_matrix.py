from __future__ import annotations

from companmem_pipeline.matrix import classify_audit, lint_matrix


def _audit(
    *,
    slug: str,
    mechanisms: list[str],
    ledger: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "identity": {
            "id": slug,
            "name": slug,
            "repo": "https://github.com/example/repo",
            "docs": "https://example.com/docs",
            "license": None,
            "version_or_commit": None,
            "observed_at": "2026-09-20",
        },
        "claimed_purpose": [{"text": "Store memories"}],
        "mechanisms": [{"text": text} for text in mechanisms],
        "ledger": ledger,
        "sources": [
            {
                "url": "https://example.com/docs",
                "kind": "docs",
                "accessed_at": "2026-09-20",
                "quality": "high",
            }
        ],
        "consensus": [],
        "contested": [],
        "copy": [],
        "refuse": [],
        "unknowns": [],
    }


def test_classify_mem0_like_lights_retrieve_and_isolation() -> None:
    audit = _audit(
        slug="mem0",
        mechanisms=[
            "Persistent SQLite store scoped by user_id",
            "Hybrid retrieval with BM25 and embeddings",
        ],
        ledger=[
            {
                "claim": "memories are scoped by user_id",
                "kind": "code",
                "url": "https://example.com/user",
                "quote": "filter memories by user_id before search",
                "locator": "search.py",
                "confidence": "high",
                "label": "measured",
            },
            {
                "claim": "hybrid retrieval",
                "kind": "docs",
                "url": "https://example.com/retrieve",
                "quote": "Hybrid retrieval combining semantic embeddings and BM25",
                "locator": "readme",
                "confidence": "high",
                "label": "measured",
            },
            {
                "claim": "sqlite persist",
                "kind": "code",
                "url": "https://example.com/store",
                "quote": "Persistent SQLite store across sessions",
                "locator": "db.py",
                "confidence": "high",
                "label": "measured",
            },
        ],
    )
    row = classify_audit(audit, clone=True)
    assert row["retrieve"]["present"] is True
    assert "BM25" in str(row["retrieve"]["quote"])
    assert row["isolation"]["present"] is True
    assert "user_id" in str(row["isolation"]["quote"])
    assert row["persist"]["present"] is True


def test_classify_flat_json_fails_isolation() -> None:
    audit = _audit(
        slug="omemo",
        mechanisms=["Memory store is a single shared file (data/memories.json)"],
        ledger=[
            {
                "claim": "no per-user isolation",
                "kind": "code",
                "url": "https://example.com/store",
                "quote": (
                    "There is no per-user or per-session isolation; "
                    "a single shared memories.json file"
                ),
                "locator": "manager.py",
                "confidence": "high",
                "label": "measured",
            }
        ],
    )
    row = classify_audit(audit, clone=True)
    assert row["isolation"]["present"] is False
    assert "no per-user" in str(row["isolation"]["quote"]).lower()
    assert row["persist"]["present"] is True


def test_lint_matrix_accepts_envelope() -> None:
    record = {
        "observed_at": "2026-09-20",
        "products": [
            classify_audit(
                _audit(
                    slug="x",
                    mechanisms=["Persistent sqlite"],
                    ledger=[
                        {
                            "claim": "sqlite persist",
                            "kind": "code",
                            "url": "https://example.com/a",
                            "quote": "persistent sqlite across sessions",
                            "locator": "db.py",
                            "confidence": "high",
                            "label": "measured",
                        }
                    ],
                ),
                clone=True,
            )
        ],
    }
    assert lint_matrix(record) == []


def test_persist_negation_quote_is_false() -> None:
    audit = _audit(
        slug="characterai",
        mechanisms=["persistent long-term memory"],
        ledger=[
            {
                "claim": "not actually persistent",
                "kind": "blog",
                "url": "https://example.com/blog",
                "quote": (
                    "sqlite-backed memory is scoped to single conversations "
                    "rather than persistent long-term continuity"
                ),
                "locator": "blog",
                "confidence": "medium",
                "label": "inferred",
            }
        ],
    )
    row = classify_audit(audit, clone=False)
    assert row["persist"]["present"] is False


def test_persist_graph_database_and_long_term_storage() -> None:
    zep = _audit(
        slug="zep",
        mechanisms=["Konig graph"],
        ledger=[
            {
                "claim": "graph db",
                "kind": "blog",
                "url": "https://example.com/zep",
                "quote": "Konig, Zep's graph database service, is the data plane",
                "locator": "blog",
                "confidence": "medium",
                "label": "inferred",
            }
        ],
    )
    memobase = _audit(
        slug="memobase",
        mechanisms=["flush"],
        ledger=[
            {
                "claim": "flush",
                "kind": "docs",
                "url": "https://example.com/flush",
                "quote": (
                    "pending memory operations are processed and committed "
                    "to long-term storage"
                ),
                "locator": "docs",
                "confidence": "high",
                "label": "measured",
            }
        ],
    )
    assert classify_audit(zep, clone=False)["persist"]["present"] is True
    assert classify_audit(memobase, clone=True)["persist"]["present"] is True


def test_isolation_per_project_and_scoped_memory_fs() -> None:
    audit = _audit(
        slug="letta",
        mechanisms=["MemFS per agent"],
        ledger=[
            {
                "claim": "scoped fs",
                "kind": "code",
                "url": "https://example.com/letta",
                "quote": "getScopedMemoryFilesystemRoot(agentId)",
                "locator": "memfs.ts",
                "confidence": "high",
                "label": "measured",
            }
        ],
    )
    row = classify_audit(audit, clone=True)
    assert row["isolation"]["present"] is True


def test_hard_deleting_lights_forget_delete() -> None:
    audit = _audit(
        slug="graphiti",
        mechanisms=["delete method"],
        ledger=[
            {
                "claim": "hard deleting",
                "kind": "docs",
                "url": "https://example.com/del",
                "quote": (
                    "Graphiti also supports hard deleting nodes and edges "
                    "using the delete method"
                ),
                "locator": "readme",
                "confidence": "high",
                "label": "measured",
            }
        ],
    )
    row = classify_audit(audit, clone=True)
    assert row["forget_delete"]["present"] is True


def test_pdf_embedding_is_not_retrieve() -> None:
    audit = _audit(
        slug="agnai",
        mechanisms=["Wikipedia Article and PDF embedding"],
        ledger=[
            {
                "claim": "pdf embedding",
                "kind": "docs",
                "url": "https://example.com/pdf",
                "quote": "Wikipedia Article and PDF embedding",
                "locator": "readme",
                "confidence": "medium",
                "label": "measured",
            }
        ],
    )
    assert classify_audit(audit, clone=True)["retrieve"]["present"] is False


def test_bare_search_and_extract_do_not_saturate() -> None:
    audit = _audit(
        slug="noise",
        mechanisms=["LLM extraction pipeline; users can search research docs"],
        ledger=[
            {
                "claim": "searchDepth",
                "kind": "code",
                "url": "https://example.com/slice",
                "quote": "messages.slice(messages.length - arg.searchDepth)",
                "locator": "slice.ts",
                "confidence": "high",
                "label": "measured",
            }
        ],
    )
    row = classify_audit(audit, clone=True)
    assert row["retrieve"]["present"] is False
    assert row["log_vs_curated"] == "unknown"


def test_isolation_hit_not_from_no_per_user_phrase() -> None:
    audit = _audit(
        slug="omemo",
        mechanisms=["shared file"],
        ledger=[
            {
                "claim": "no per-user isolation",
                "kind": "code",
                "url": "https://example.com/store",
                "quote": "There is no per-user or per-session isolation",
                "locator": "manager.py",
                "confidence": "high",
                "label": "measured",
            }
        ],
    )
    row = classify_audit(audit, clone=True)
    assert row["isolation"]["present"] is False
    assert "no per-user" in str(row["isolation"]["quote"]).lower()


def test_isolation_hit_beats_miss_phrase() -> None:
    audit = _audit(
        slug="graphiti",
        mechanisms=["group_id partition; shared Falkor graph issue"],
        ledger=[
            {
                "claim": "group_id isolates",
                "kind": "code",
                "url": "https://example.com/group",
                "quote": "group_id: str = Field(description='partition of the graph')",
                "locator": "edges.py",
                "confidence": "high",
                "label": "measured",
            },
            {
                "claim": "shared graph",
                "kind": "issue",
                "url": "https://example.com/issue",
                "quote": "single shared physical graph such as graphiti_personal",
                "locator": "#1684",
                "confidence": "medium",
                "label": "inferred",
            },
        ],
    )
    row = classify_audit(audit, clone=True)
    assert row["isolation"]["present"] is True
    assert "group_id" in str(row["isolation"]["quote"])


def test_contradict_alone_is_not_conflict() -> None:
    audit = _audit(
        slug="issue-only",
        mechanisms=["users contradict each other in threads"],
        ledger=[
            {
                "claim": "issue prose",
                "kind": "issue",
                "url": "https://example.com/i",
                "quote": "this contradicts the documented behavior in the user guide",
                "locator": "#1",
                "confidence": "low",
                "label": "inferred",
            }
        ],
    )
    row = classify_audit(audit, clone=True)
    assert row["conflict_or_supersession"]["present"] is False


def test_forget_overlapping_quotes_keep_suppress() -> None:
    quote = "UPDATE memories SET is_active = FALSE; hard delete after wipe"
    audit = _audit(
        slug="both",
        mechanisms=["soft delete then wipe"],
        ledger=[
            {
                "claim": "soft then hard",
                "kind": "code",
                "url": "https://example.com/del",
                "quote": quote,
                "locator": "db.sql",
                "confidence": "high",
                "label": "measured",
            }
        ],
    )
    row = classify_audit(audit, clone=True)
    assert row["forget_suppress"]["present"] is True
    assert row["forget_delete"]["present"] is False
