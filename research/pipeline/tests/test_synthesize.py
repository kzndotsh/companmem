from __future__ import annotations

import json
from pathlib import Path

import pytest

import companmem_pipeline.synthesize as synth
from companmem_pipeline.kiro import kiro_api_key, kiro_configured
from companmem_pipeline.lint import lint_audit
from companmem_pipeline.synthesize import (
    COMPACT_VERSION,
    LEDGER_CAP,
    PRODUCT_ID_CAP,
    PRODUCT_ROW_CAP,
    QUOTE_MAX,
    UNKNOWNS_CAP,
    cap_product_rows,
    compact_audit,
    compact_ledger,
    compact_unknowns,
    drop_overlapping_gaps,
    filter_theme_rows,
    ground_cited_rows,
    lint_synthesis,
    load_audits,
    product_clone_flags,
    snippet_support,
    truncate_quote,
)


def _valid_audit(*, slug: str = "mem0") -> dict[str, object]:
    return {
        "identity": {
            "id": slug,
            "name": slug,
            "repo": "https://github.com/example/repo",
            "docs": "https://example.com/docs",
            "license": None,
            "version_or_commit": None,
            "observed_at": "2026-09-11",
        },
        "claimed_purpose": [{"text": "Store memories"}],
        "mechanisms": [{"text": "Extract then retrieve"}],
        "ledger": [
            {
                "claim": "Extracts facts each turn",
                "kind": "docs",
                "url": "https://example.com/how",
                "quote": "Mem0 extracts facts",
                "locator": "How it works",
                "confidence": "high",
                "label": "measured",
            }
        ],
        "sources": [
            {
                "url": "https://example.com/docs",
                "kind": "docs",
                "accessed_at": "2026-09-11",
                "quality": "high",
            }
        ],
        "consensus": [],
        "contested": [],
        "copy": [],
        "refuse": [],
        "unknowns": [
            {
                "text": "Platform internals not in OSS",
                "url": "https://example.com/docs",
                "kind": "docs",
            }
        ],
    }


def test_truncate_quote_caps_length() -> None:
    long_quote = "x" * (QUOTE_MAX + 40)
    assert len(truncate_quote(long_quote)) == QUOTE_MAX


def test_compact_audit_ranks_high_code_before_late_issue() -> None:
    audit = _valid_audit()
    long_quote = "later issue evidence " + ("n" * QUOTE_MAX)
    audit["ledger"] = [
        {
            "claim": "late issue",
            "kind": "issue",
            "url": "https://example.com/issue/1",
            "quote": long_quote,
            "locator": "body",
            "confidence": "medium",
            "label": "inferred",
        },
        {
            "claim": "code high",
            "kind": "code",
            "url": "https://example.com/blob",
            "quote": "def remember():",
            "locator": "remember.py",
            "confidence": "high",
            "label": "measured",
        },
    ]
    audit["unknowns"] = [
        {"text": f"gap {i}", "url": "https://example.com/u", "kind": "docs"}
        for i in range(20)
    ]
    card = compact_audit(audit, clone=True, product_id="mem0")
    assert card["clone"] is True
    ledger = card["ledger"]
    assert isinstance(ledger, list)
    assert ledger[0]["claim"] == "code high"
    assert ledger[0]["id"] == "mem0"
    assert "url" not in ledger[0]
    assert "locator" not in ledger[0]
    assert len(str(ledger[1]["quote"])) == QUOTE_MAX
    unknowns = card["unknowns"]
    assert isinstance(unknowns, list)
    assert len(unknowns) == UNKNOWNS_CAP
    assert list(unknowns[0].keys()) == ["text"]


def test_compact_ledger_caps_after_rank() -> None:
    rows: list[dict[str, object]] = []
    for i in range(LEDGER_CAP + 5):
        rows.append(
            {
                "claim": f"issue {i}",
                "kind": "issue",
                "confidence": "medium",
                "quote": f"q{i}",
            }
        )
    rows.append(
        {
            "claim": "code high",
            "kind": "code",
            "confidence": "high",
            "quote": "src",
        }
    )
    kept, total = compact_ledger(rows, product_id="x")
    assert total == LEDGER_CAP + 6
    assert len(kept) == LEDGER_CAP
    assert kept[0]["claim"] == "code high"


def test_compact_unknowns_caps_and_drops_url() -> None:
    items = [{"text": f"u{i}", "url": "https://example.com"} for i in range(12)]
    out = compact_unknowns(items)
    assert len(out) == UNKNOWNS_CAP
    assert out[0] == {"text": "u0"}


def test_filter_theme_rows_drops_unknown_ids() -> None:
    filtered = filter_theme_rows(
        [
            {"text": "RAG only", "product_ids": ["mem0", "ghost", "mem0"]},
            {"text": "   ", "product_ids": ["mem0"]},
            "skip",
        ],
        {"mem0"},
    )
    assert filtered == [{"text": "RAG only", "product_ids": ["mem0"]}]


def test_product_clone_flags_reads_seed() -> None:
    flags = product_clone_flags()
    assert flags["mem0"] is True
    assert flags["zep"] is False


def test_load_audits_skips_missing_and_dirty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    good_dir = tmp_path / "good"
    bad_dir = tmp_path / "bad"
    good_dir.mkdir()
    bad_dir.mkdir()
    good = _valid_audit(slug="good")
    good["identity"]["id"] = "good"
    (good_dir / "audit.json").write_text(json.dumps(good), encoding="utf-8")
    dirty = _valid_audit(slug="bad")
    dirty["identity"]["id"] = "bad"
    del dirty["ledger"]
    (bad_dir / "audit.json").write_text(json.dumps(dirty), encoding="utf-8")
    assert lint_audit(dirty)

    monkeypatch.setattr(synth, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(synth, "product_ids", lambda: ["good", "bad", "gone"])
    present, missing, dirty_ids, audits = load_audits()
    assert present == ["good"]
    assert missing == ["bad", "gone"]
    assert dirty_ids == ["bad"]
    assert len(audits) == 1


def test_lint_synthesis_accepts_envelope() -> None:
    record = {
        "observed_at": "2026-09-20",
        "products": ["mem0", "zep"],
        "missing": [],
        "dirty": [],
        "themes": [
            {
                "text": "extract-embed-retrieve",
                "product_ids": ["mem0", "zep"],
                "clone_true": ["mem0"],
                "clone_false": ["zep"],
                "evidence": [
                    {"product_id": "mem0", "quote": "Mem0 extracts facts"},
                    {"product_id": "zep", "quote": "Zep retrieves facts"},
                ],
            }
        ],
        "recurring_mechanisms": [],
        "shared_gaps": [],
        "unknowns": [{"text": "forget APIs sparse"}],
        "model": "claude-sonnet-4.6",
        "compact_version": COMPACT_VERSION,
    }
    assert lint_synthesis(record) == []


def _extract_card(slug: str, *, clone: bool) -> dict[str, object]:
    return {
        "identity": {"id": slug, "name": slug, "repo": None},
        "clone": clone,
        "claimed_purpose": [{"text": "Store memories"}],
        "mechanisms": [{"text": "Extract then retrieve facts"}],
        "ledger": [
            {
                "id": slug,
                "claim": "Extracts facts each turn",
                "kind": "docs",
                "confidence": "high",
                "quote": f"{slug} extracts facts each turn",
            }
        ],
        "unknowns": [],
    }


def test_ground_cited_rows_drops_unsupported_caps_and_splits_clone() -> None:
    cards = {
        "mem0": _extract_card("mem0", clone=True),
        "zep": _extract_card("zep", clone=False),
        "unrelated": {
            "identity": {"id": "unrelated", "name": "unrelated", "repo": None},
            "clone": True,
            "claimed_purpose": [],
            "mechanisms": [{"text": "Graph edges only"}],
            "ledger": [
                {
                    "id": "unrelated",
                    "claim": "Stores graph edges",
                    "kind": "docs",
                    "confidence": "high",
                    "quote": "Stores graph edges",
                }
            ],
            "unknowns": [],
        },
    }
    extras = [f"zz{i}" for i in range(PRODUCT_ID_CAP - 1)]
    for slug in extras:
        cards[slug] = _extract_card(slug, clone=True)
    clone_flags = {slug: bool(card["clone"]) for slug, card in cards.items()}
    grounded = ground_cited_rows(
        [
            {
                "text": "extracts facts each turn",
                "product_ids": ["unrelated", "mem0", "ghost", "zep", *extras],
            },
            {
                "text": "isolation conflict forget",
                "product_ids": ["mem0", "zep"],
            },
            {
                "text": "extracts facts each turn",
                "product_ids": ["mem0"],
            },
        ],
        set(cards),
        cards,
        clone_flags,
    )
    assert len(grounded) == 1
    row = grounded[0]
    assert "unrelated" not in row["product_ids"]
    assert "ghost" not in row["product_ids"]
    assert len(row["product_ids"]) == PRODUCT_ID_CAP
    assert "mem0" in row["clone_true"]
    assert "zep" in row["clone_false"]
    evidence = row["evidence"]
    assert len(evidence) == len(row["product_ids"])
    assert evidence[0]["quote"]
    assert evidence[0]["product_id"] in row["product_ids"]


def test_cap_product_rows_limits_repeat_ids() -> None:
    quote = "mem0 extracts facts each turn"
    flags = {"mem0": True, "zep": False}
    rows = [
        {
            "text": "extracts facts each turn",
            "product_ids": ["mem0", "zep"],
            "clone_true": ["mem0"],
            "clone_false": ["zep"],
            "evidence": [
                {"product_id": "mem0", "quote": quote},
                {"product_id": "zep", "quote": "zep extracts facts each turn"},
            ],
        }
        for _ in range(11)
    ]
    capped_themes, _recurring, _gaps = cap_product_rows([rows, [], []], flags)
    mem0_count = sum(1 for row in capped_themes if "mem0" in row["product_ids"])
    assert mem0_count <= PRODUCT_ROW_CAP
    assert mem0_count >= 1


def test_drop_overlapping_gaps_drops_theme_echo() -> None:
    themes = [{"text": "extract embed retrieve"}]
    gaps = [
        {"text": "extract embed retrieve with no forget"},
        {"text": "no isolation or conflict resolution"},
    ]
    kept = drop_overlapping_gaps(themes, gaps)
    assert kept == [{"text": "no isolation or conflict resolution"}]


def _card(*, slug: str, clone: bool, quote: str, mechanism: str = "") -> dict[str, object]:
    mechanisms = [{"text": mechanism}] if mechanism else []
    return {
        "identity": {"id": slug, "name": slug, "repo": None},
        "clone": clone,
        "claimed_purpose": [],
        "mechanisms": mechanisms,
        "ledger": [
            {
                "id": slug,
                "claim": quote,
                "kind": "docs",
                "confidence": "high",
                "quote": quote,
            }
        ],
        "unknowns": [],
    }


def test_ground_drops_on_card_quote_that_does_not_support_theme() -> None:
    theme = (
        "LLM-driven write pipelines pass raw conversation through an "
        "extraction step before any curated-memory write occurs"
    )
    support_quote = (
        "The extraction model produces structured facts from each "
        "conversation turn before the curated store write"
    )
    telemem_quote = (
        "False stores each non-system message's content verbatim, with no LLM call"
    )
    cards = {
        "telemem": _card(slug="telemem", clone=True, quote=telemem_quote),
        "mem0": _card(slug="mem0", clone=True, quote=support_quote),
        "zep": _card(slug="zep", clone=False, quote=support_quote),
    }
    clone_flags = {"telemem": True, "mem0": True, "zep": False}
    grounded = ground_cited_rows(
        [
            {
                "text": theme,
                "product_ids": ["telemem", "mem0", "zep"],
                "evidence": [
                    {"product_id": "telemem", "quote": telemem_quote},
                    {"product_id": "mem0", "quote": support_quote},
                    {"product_id": "zep", "quote": support_quote},
                ],
            }
        ],
        set(cards),
        cards,
        clone_flags,
    )
    assert len(grounded) == 1
    ids = grounded[0]["product_ids"]
    assert "telemem" not in ids
    assert ids == ["mem0", "zep"]
    quotes = {row["product_id"]: row["quote"] for row in grounded[0]["evidence"]}
    assert quotes["mem0"] == support_quote


def test_ground_on_card_unsupported_does_not_fallback() -> None:
    theme = "Write-time deduplication skips exact hashes before persist"
    hash_quote = "mem_hash = hashlib.md5(text.encode()); skip exact duplicates"
    tag_quote = (
        "Identifying the most salient keywords and creating categorical tags"
    )
    cards = {
        "mem0": _card(
            slug="mem0",
            clone=True,
            quote=tag_quote,
            mechanism=hash_quote,
        ),
        "zep": _card(slug="zep", clone=False, quote=hash_quote),
    }
    grounded = ground_cited_rows(
        [
            {
                "text": theme,
                "product_ids": ["mem0", "zep"],
                "evidence": [{"product_id": "mem0", "quote": tag_quote}],
            }
        ],
        set(cards),
        cards,
        {"mem0": True, "zep": False},
    )
    assert grounded == []


def test_ground_invented_quote_falls_back_to_card_snippet() -> None:
    theme = "Write-time deduplication skips exact hashes before persist"
    hash_quote = "skip exact hashes before persist write-time"
    cards = {
        "mem0": _card(slug="mem0", clone=True, quote=hash_quote),
        "zep": _card(slug="zep", clone=False, quote=hash_quote),
    }
    grounded = ground_cited_rows(
        [
            {
                "text": theme,
                "product_ids": ["mem0", "zep"],
                "evidence": [{"product_id": "mem0", "quote": "not present on this card"}],
            }
        ],
        set(cards),
        cards,
        {"mem0": True, "zep": False},
    )
    assert len(grounded) == 1
    quotes = {row["product_id"]: row["quote"] for row in grounded[0]["evidence"]}
    assert quotes["mem0"] == hash_quote


def test_snippet_support_rejects_generic_field_overlap() -> None:
    isolation = (
        "Per-namespace or per-project isolation enforced at write and retrieve "
        "time: every memory write is tagged with an identity key (user_id, "
        "agent_id, namespace, group_id, project_id) and retrieval is filtered "
        "to that key, so one tenant's memories never leak into another's results."
    )
    extraction = (
        "LLM-driven curated extraction: raw conversation turns are processed "
        "by a language model before any fact reaches the persistent store."
    )
    conflict = (
        "Temporal invalidation as conflict resolution: when a newer fact "
        "contradicts an older one, the older fact is retired in place."
    )
    gap = (
        "No conflict or supersession policy when two independently extracted "
        "facts about the same subject contradict each other."
    )
    misses = [
        (
            isolation,
            "Memory defragmentation via triggered events to the sleep-time agent",
        ),
        (
            isolation,
            "Shared memory: multiple agents read and write the same memory store",
        ),
        (
            extraction,
            "Persistent memory that survives across conversations and sessions",
        ),
        (conflict, "Supermemory infers a fact you never stated in one place"),
        (gap, "This is for iOS at least, I'm not sure about other systems."),
    ]
    for theme, quote in misses:
        assert snippet_support(theme, quote) == (0.0, 0)
    kiwi = (
        "Private project content never flows into global chats or another "
        "project. No setup needed — isolation is automatic."
    )
    precision, overlap = snippet_support(isolation, kiwi)
    assert overlap >= 2
    assert precision > 0.0
    extract_theme = (
        "Extract-embed-retrieve is the dominant write-read pattern: raw "
        "messages are processed to produce curated facts"
    )
    tenant_quote = (
        "Multi-tenant isolation: each tenant's memories are stored and "
        "retrieved independently via tenant_id."
    )
    assert snippet_support(extract_theme, tenant_quote) == (0.0, 0)
    isolation_gap = (
        "No per-user or per-session isolation: the store is a single flat "
        "collection with no namespace"
    )
    assert snippet_support(
        isolation_gap,
        "Isolation: memory scoped per user, agent, conversation",
        require_negation=True,
    ) == (0.0, 0)
    omemo = (
        "Memory store is a single shared file (data/memories.json); "
        "no per-user or per-session isolation is described"
    )
    gap_precision, gap_overlap = snippet_support(
        isolation_gap,
        omemo,
        require_negation=True,
    )
    assert gap_overlap >= 2
    assert gap_precision > 0.0
    conflict = (
        "Temporal invalidation (soft supersession) rather than hard deletion"
    )
    assert snippet_support(
        conflict,
        "Undo clears that stamp — and un-forgets a declined memory — bringing it back.",
    ) == (0.0, 0)
    version = (
        "Per-record version chain: updates create a new row linked via "
        "supersedes_id or migrated_to"
    )
    assert snippet_support(version, "DEFAULT_CAUSAL_LINK_WEIGHT = 1.0") == (0.0, 0)
    no_forget = (
        "Extract-embed-retrieve with no automatic forget or update: "
        "ingestion produces curated records"
    )
    assert snippet_support(
        no_forget,
        'The agent can call "manage_memory" to create, update, and delete memories by ID',
    ) == (0.0, 0)
    isolation_axes = (
        "Multi-dimensional isolation axes (user, agent, session, project, "
        "namespace): most products scope memory along at least two axes"
    )
    assert snippet_support(
        isolation_axes,
        "Evict old messages beyond the most recent 10 for this scope.",
    ) == (0.0, 0)
    hybrid = (
        "Hybrid retrieval: semantic vector search combined with BM25 "
        "keyword search, fused via Reciprocal Rank Fusion"
    )
    assert snippet_support(
        hybrid,
        "# Redact secrets before storage from secret_filter import redact_secrets",
    ) == (0.0, 0)
    iso_precision, iso_overlap = snippet_support(
        isolation_axes,
        "group_id filtering used for multi-user data isolation",
    )
    assert iso_overlap >= 1
    assert iso_precision > 0.0
    dreaming = (
        "Background or asynchronous consolidation (variously called dreaming, "
        "sleep, digest, or reflect) runs off the hot path"
    )
    assert snippet_support(
        dreaming,
        "Cognee stores ingested data in a graph structure that is searchable.",
    ) == (0.0, 0)
    dream_precision, dream_overlap = snippet_support(
        dreaming,
        "Honcho supports Dreaming: autonomous background consolidation "
        "to continuously improve memory.",
    )
    assert dream_overlap >= 1
    assert dream_precision > 0.0
    retrieve_then = (
        "Retrieve-then-prompt as the universal scaffold pattern — retrieved "
        "memory is assembled into a text block"
    )
    assert snippet_support(
        retrieve_then,
        "Khoj can keep your files and folders synced using the Khoj Desktop",
    ) == (0.0, 0)
    extract_write = (
        "LLM-driven extraction of curated facts from raw conversation turns"
    )
    assert snippet_support(
        extract_write,
        "The write path for conversation recording distinguishes external user inputs",
    ) == (0.0, 0)
    hybrid_sleep = (
        "Hybrid retrieval combining dense vector search, BM25/FTS keyword "
        "search, and graph traversal"
    )
    assert snippet_support(
        hybrid_sleep,
        "Mnemosyne includes a sleep consolidation architecture component, "
        "suggesting offline or async memory consolidation separate from live retrieval",
    ) == (0.0, 0)
    scaffold = (
        "Retrieval is scaffold-injected into the model turn rather than "
        "passively returning records"
    )
    assert snippet_support(
        scaffold,
        "if is_agent_memory: return AGENT_MEMORY_EXTRACTION_PROMPT",
    ) == (0.0, 0)
    isolation_gap = (
        "No cross-session isolation for companion products operating a "
        "single global store"
    )
    assert snippet_support(
        isolation_gap,
        "Context isolation is not authentication. Closing grants no "
        "implementation authorization.",
        require_negation=True,
    ) == (0.0, 0)
    omemo_precision, omemo_overlap = snippet_support(
        isolation_gap,
        "Memory store is a single shared file (data/memories.json); "
        "no per-user or per-session isolation is described",
        require_negation=True,
    )
    assert omemo_overlap >= 1
    assert omemo_precision > 0.0
    soft_forget = (
        "Soft-delete (status flag, deleted_at timestamp) as the primary "
        "forget mechanism"
    )
    assert snippet_support(
        soft_forget,
        "No delete or forget operation is present in this file; the backfill "
        "only writes, never removes records.",
    ) == (0.0, 0)
    soft_conflict = (
        "Soft supersession via status or deprecated flag — the old fact row "
        "is retained in the store with a status field"
    )
    assert snippet_support(
        soft_conflict,
        "The old fact row is retained, then the FK cascade deletes "
        "superseded observation history",
    ) == (0.0, 0)
    contradiction = (
        "Contradiction detection as a named write-path operation: products "
        "compare new facts against existing stored facts"
    )
    assert snippet_support(
        contradiction,
        "After a write, the peer's cache entry is explicitly invalidated "
        "to enforce a read-through pattern.",
    ) == (0.0, 0)
    rather_than_deleted = (
        "when a fact changes, the old record is marked superseded or retired "
        "with a chain pointer rather than being deleted, preserving full history"
    )
    assert snippet_support(
        rather_than_deleted,
        "Delete a superseded or contradicted observation. DELETE FROM "
        "memory_units WHERE id = $1",
    ) == (0.0, 0)
    extract_write = (
        "LLM-driven fact extraction on the write path: raw conversation "
        "messages are passed to a language model"
    )
    assert snippet_support(
        extract_write,
        "await check_embedding_sanity() await llm_sanity_check()",
    ) == (0.0, 0)
    file_native = (
        "File-native or Markdown-backed persistence: memory is stored as "
        "human-readable Markdown files as the canonical source of truth"
    )
    assert snippet_support(
        file_native,
        "SQLite is the canonical store; Markdown, full-text indexes, and "
        "optional graph stores are rebuildable projections",
    ) == (0.0, 0)


def test_filter_theme_rows_clears_ids_not_in_present() -> None:
    filtered = filter_theme_rows(
        [{"text": "x", "product_ids": ["ghost"]}],
        {"mem0"},
    )
    assert filtered == [{"text": "x", "product_ids": []}]


def test_kiro_api_key_empty_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KIRO_GATEWAY_API_KEY", "")
    monkeypatch.setenv("PROXY_API_KEY", "proxy-secret")
    assert kiro_api_key() == "proxy-secret"
    assert kiro_configured() is True
