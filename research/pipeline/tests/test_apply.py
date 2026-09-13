from __future__ import annotations

from companmem_pipeline.apply import merge_audits


def test_merge_does_not_resurrect_repo_for_clone_skipped_products() -> None:
    existing = {
        "identity": {
            "id": "zep",
            "name": "Zep Cloud",
            "repo": "https://github.com/getzep/zep",
        },
        "claimed_purpose": [],
        "mechanisms": [],
        "ledger": [],
        "sources": [],
        "copy": [],
        "refuse": [],
        "consensus": [],
        "contested": [],
        "unknowns": [],
    }
    candidate = {
        "identity": {
            "id": "zep",
            "name": "Zep Cloud",
            "repo": None,
        },
        "claimed_purpose": [],
        "mechanisms": [],
        "ledger": [],
        "sources": [],
        "copy": [],
        "refuse": [],
        "consensus": [],
        "contested": [],
        "unknowns": [],
    }
    merged = merge_audits(existing, candidate, clone_skipped=True)
    assert merged["identity"]["repo"] is None


def test_merge_replaces_purpose_and_drops_off_source_ledger() -> None:
    existing = {
        "identity": {"id": "honcho", "name": "Honcho", "observed_at": "2026-09-11"},
        "claimed_purpose": [{"text": "Mem0 export helper"}],
        "mechanisms": [{"text": "OpenClaw daily notes"}],
        "ledger": [
            {
                "claim": "OpenClaw stores daily notes",
                "kind": "docs",
                "url": "https://docs.openclaw.ai/concepts/memory",
                "quote": "daily notes",
                "locator": "h1",
                "confidence": "high",
                "label": "inferred",
            },
            {
                "claim": "Honcho peers",
                "kind": "docs",
                "url": "https://docs.honcho.dev/v2/guides/architecture",
                "quote": "old short",
                "locator": "peers",
                "confidence": "medium",
                "label": "inferred",
            },
        ],
        "sources": [
            {
                "url": "https://docs.openclaw.ai/concepts/memory",
                "kind": "docs",
                "accessed_at": "2026-09-11",
                "quality": "high",
            }
        ],
        "copy": [{"text": "keep this"}],
        "refuse": [],
        "consensus": [],
        "contested": [],
        "unknowns": [{"text": "old gap", "url": "https://docs.openclaw.ai/concepts/memory"}],
    }
    candidate = {
        "identity": {
            "id": "honcho",
            "name": "Honcho",
            "repo": "https://github.com/plastic-labs/honcho",
            "observed_at": "2026-09-12",
        },
        "claimed_purpose": [{"text": "Companion-native memory"}],
        "mechanisms": [{"text": "async deriver"}],
        "ledger": [
            {
                "claim": "Honcho peers",
                "kind": "docs",
                "url": "https://docs.honcho.dev/v2/guides/architecture",
                "quote": "longer quote about peers",
                "locator": "peers",
                "confidence": "high",
                "label": "measured",
            }
        ],
        "sources": [
            {
                "url": "https://docs.honcho.dev/v2/guides/architecture",
                "kind": "docs",
                "accessed_at": "2026-09-12",
                "quality": "high",
            }
        ],
        "copy": [],
        "refuse": [],
        "consensus": [],
        "contested": [],
        "unknowns": [],
    }
    merged = merge_audits(existing, candidate)
    assert merged["claimed_purpose"] == candidate["claimed_purpose"]
    assert merged["mechanisms"] == candidate["mechanisms"]
    assert merged["unknowns"] == []
    assert merged["copy"] == [{"text": "keep this"}]
    urls = {str(row.get("url")) for row in merged["ledger"]}
    assert "https://docs.openclaw.ai/concepts/memory" not in urls
    assert merged["ledger"][0]["quote"] == "longer quote about peers"
    assert merged["sources"] == candidate["sources"]
