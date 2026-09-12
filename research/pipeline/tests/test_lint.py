from __future__ import annotations

from companmem_pipeline.lint import lint_audit


def _valid_audit() -> dict[str, object]:
    return {
        "identity": {
            "id": "mem0",
            "name": "Mem0",
            "repo": "https://github.com/mem0ai/mem0",
            "docs": "https://docs.mem0.ai/llms.txt",
            "license": None,
            "version_or_commit": None,
            "observed_at": "2026-09-11",
        },
        "claimed_purpose": [{"text": "Store memories"}],
        "mechanisms": [],
        "ledger": [
            {
                "claim": "Extracts facts each turn",
                "kind": "docs",
                "url": "https://docs.mem0.ai/core-concepts/how-it-works.md",
                "quote": "Mem0 extracts facts",
                "locator": "How it works",
                "confidence": "high",
                "label": "measured",
            }
        ],
        "sources": [
            {
                "url": "https://docs.mem0.ai/llms.txt",
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
                "text": "Platform Dream internals not in OSS",
                "url": "https://docs.mem0.ai/llms.txt",
                "kind": "docs",
            }
        ],
    }


def test_lint_accepts_cited_ledger() -> None:
    assert lint_audit(_valid_audit()) == []


def test_lint_requires_url_or_locator() -> None:
    audit = _valid_audit()
    audit["ledger"] = [
        {
            "claim": "uncited",
            "kind": "docs",
            "url": None,
            "quote": "something",
            "locator": None,
            "confidence": "unknown",
            "label": "unknown",
        }
    ]
    errors = lint_audit(audit)
    assert any("url or locator" in e or "url" in e.lower() for e in errors)


def test_lint_rejects_extra_top_level_field() -> None:
    audit = _valid_audit()
    audit["companion_fit"] = "PARTIAL"
    errors = lint_audit(audit)
    assert errors
