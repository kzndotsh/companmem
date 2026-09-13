from __future__ import annotations

from companmem_pipeline.fold import fold_pages
from companmem_pipeline.lint import lint_audit


def _manifest() -> dict[str, object]:
    return {
        "id": "mem0",
        "name": "Mem0",
        "repo": "https://github.com/mem0ai/mem0",
        "docs": "https://docs.mem0.ai/llms.txt",
        "license": "Apache-2.0",
        "version_or_commit": "abc123",
        "observed_at": "2026-09-11",
        "pages": [
            {
                "url": "https://docs.mem0.ai/llms.txt",
                "kind": "docs",
                "accessed_at": "2026-09-11",
                "quality": "high",
            }
        ],
    }


def test_fold_skips_repo_hint_when_clone_skipped() -> None:
    manifest = {
        **_manifest(),
        "repo": None,
        "clone_skipped": True,
        "pages": [],
    }
    extracts = [
        {
            "identity_hints": {
                "repo": "https://github.com/getzep/zep",
            },
            "claimed_purpose": [],
            "mechanisms": [],
            "ledger": [],
            "unknowns": [],
        }
    ]
    audit = fold_pages(extracts, manifest)
    assert audit["identity"]["repo"] is None


def test_fold_prefers_longer_quote_and_drops_uncited() -> None:
    extracts = [
        {
            "identity_hints": {"name": "", "repo": None, "docs": None, "license": None},
            "claimed_purpose": [{"text": "Store user memories", "quote": "Mem0", "locator": "h1"}],
            "mechanisms": [],
            "ledger": [
                {
                    "claim": "extracts memories",
                    "kind": "docs",
                    "url": "https://docs.mem0.ai/llms.txt",
                    "quote": "short",
                    "locator": "how-it-works",
                    "confidence": "medium",
                    "label": "measured",
                },
                {
                    "claim": "no citation",
                    "kind": "docs",
                    "url": "",
                    "quote": "guess",
                    "locator": "",
                    "confidence": "unknown",
                    "label": "inferred",
                },
            ],
            "unknowns": [],
        },
        {
            "identity_hints": {"name": "Mem0", "repo": None, "docs": None, "license": None},
            "claimed_purpose": [],
            "mechanisms": [
                {
                    "text": "extracts memories",
                    "quote": "Mem0 extracts memories from the conversation",
                    "locator": "how-it-works",
                }
            ],
            "ledger": [
                {
                    "claim": "extracts memories",
                    "kind": "docs",
                    "url": "https://docs.mem0.ai/llms.txt",
                    "quote": "Mem0 extracts memories from the conversation",
                    "locator": "how-it-works",
                    "confidence": "high",
                    "label": "measured",
                }
            ],
            "unknowns": [
                {
                    "text": "Dream internals not on this page",
                    "url": "https://docs.mem0.ai/llms.txt",
                    "kind": "docs",
                }
            ],
        },
    ]
    audit = fold_pages(extracts, _manifest())
    assert audit["copy"] == []
    assert audit["refuse"] == []
    assert audit["consensus"] == []
    assert audit["contested"] == []
    assert len(audit["ledger"]) == 1
    row = audit["ledger"][0]
    assert "Mem0 extracts memories" in str(row["quote"])
    assert audit["identity"]["name"] == "Mem0"
    assert audit["identity"]["license"] == "Apache-2.0"
    assert audit["identity"]["version_or_commit"] == "abc123"
    assert audit["sources"][0]["url"] == "https://docs.mem0.ai/llms.txt"
    assert audit["mechanisms"] == [{"text": "extracts memories"}]
    assert audit["unknowns"] == []
    assert lint_audit(audit) == []


def test_fold_identity_hints_only_fill_empty() -> None:
    manifest = _manifest()
    manifest["license"] = None
    extracts = [
        {
            "identity_hints": {
                "name": "ShouldNotReplace",
                "repo": None,
                "docs": None,
                "license": "MIT",
                "version_or_commit": None,
            },
            "claimed_purpose": [],
            "mechanisms": [],
            "ledger": [],
            "unknowns": [],
        }
    ]
    audit = fold_pages(extracts, manifest)
    assert audit["identity"]["name"] == "Mem0"
    assert audit["identity"]["license"] == "MIT"


def test_fold_unknowns_keep_page_url() -> None:
    extracts = [
        {
            "identity_hints": {},
            "claimed_purpose": [],
            "mechanisms": [],
            "ledger": [],
            "unknowns": [
                {
                    "text": "No memory mechanisms on this page",
                    "url": "https://example.com/blog",
                    "kind": "blog",
                },
                {
                    "text": "No memory mechanisms on this page",
                    "url": "https://docs.mem0.ai/llms.txt",
                    "kind": "docs",
                },
            ],
        }
    ]
    audit = fold_pages(extracts, _manifest())
    urls = {str(row.get("url")) for row in audit["unknowns"]}
    assert urls == {"https://example.com/blog", "https://docs.mem0.ai/llms.txt"}
    assert lint_audit(audit) == []


def test_fold_drops_single_url_this_file_absence() -> None:
    extracts = [
        {
            "identity_hints": {},
            "claimed_purpose": [],
            "mechanisms": [],
            "ledger": [],
            "unknowns": [
                {
                    "text": "Forget / deletion behavior: no tool is present in this file",
                    "url": "https://github.com/plastic-labs/honcho/blob/main/src/crud.py",
                    "kind": "code",
                },
                {
                    "text": "The forget/delete path is not defined in this file",
                    "url": "https://github.com/plastic-labs/honcho/blob/main/src/router.py",
                    "kind": "code",
                },
                {
                    "text": "Contradiction resolution is not implemented",
                    "url": "https://github.com/plastic-labs/honcho/issues/403",
                    "kind": "issue",
                },
            ],
        }
    ]
    audit = fold_pages(extracts, _manifest())
    texts = {str(row.get("text")) for row in audit["unknowns"]}
    assert "The forget/delete path is not defined in this file" not in texts
    assert "Forget / deletion behavior: no tool is present in this file" not in texts
    assert "Contradiction resolution is not implemented" in texts


def test_fold_keeps_this_file_absence_on_two_urls() -> None:
    extracts = [
        {
            "identity_hints": {},
            "claimed_purpose": [],
            "mechanisms": [],
            "ledger": [],
            "unknowns": [
                {
                    "text": "Forget is not present in this file",
                    "url": "https://github.com/plastic-labs/honcho/blob/main/src/a.py",
                    "kind": "code",
                },
                {
                    "text": "Forget is not present in this file",
                    "url": "https://github.com/plastic-labs/honcho/blob/main/src/b.py",
                    "kind": "code",
                },
            ],
        }
    ]
    audit = fold_pages(extracts, _manifest())
    urls = {str(row.get("url")) for row in audit["unknowns"]}
    assert urls == {
        "https://github.com/plastic-labs/honcho/blob/main/src/a.py",
        "https://github.com/plastic-labs/honcho/blob/main/src/b.py",
    }


def test_fold_drops_uncited_mechanisms() -> None:
    extracts = [
        {
            "identity_hints": {},
            "claimed_purpose": [{"text": "orphan purpose", "quote": "nope", "locator": ""}],
            "mechanisms": [{"text": "orphan mechanism", "quote": "nope", "locator": ""}],
            "ledger": [
                {
                    "claim": "extracts memories",
                    "kind": "docs",
                    "url": "https://docs.mem0.ai/llms.txt",
                    "quote": "Mem0 extracts memories",
                    "locator": "how-it-works",
                    "confidence": "high",
                    "label": "measured",
                }
            ],
            "unknowns": [],
        }
    ]
    audit = fold_pages(extracts, _manifest())
    assert audit["mechanisms"] == []
    assert audit["claimed_purpose"] == []
    assert len(audit["ledger"]) == 1
