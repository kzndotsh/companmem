from __future__ import annotations

from companmem_pipeline.extract import normalize_extract


def test_normalize_drops_mechanisms_without_quotes() -> None:
    parsed = {
        "claimed_purpose": [{"text": "remembers users", "quote": "", "locator": "h1"}],
        "mechanisms": [
            {"text": "vector store", "quote": "pgvector", "locator": "storage"},
            {"text": "no quote", "quote": "", "locator": "x"},
        ],
        "ledger": [],
        "unknowns": [],
    }
    out = normalize_extract(parsed, kind="docs", url="https://docs.honcho.dev/")
    assert out["claimed_purpose"] == []
    assert out["mechanisms"] == [
        {"text": "vector store", "quote": "pgvector", "locator": "storage"}
    ]


def test_normalize_label_code_measured_issue_inferred() -> None:
    parsed = {
        "ledger": [
            {
                "claim": "stores messages",
                "kind": "code",
                "url": "https://github.com/plastic-labs/honcho/blob/sha/src/models.py",
                "quote": "class Message",
                "locator": "models.py:1",
                "confidence": "medium",
                "label": "inferred",
            }
        ]
    }
    code = normalize_extract(
        parsed,
        kind="code",
        url="https://github.com/plastic-labs/honcho/blob/sha/src/models.py",
    )
    assert code["ledger"][0]["label"] == "measured"

    parsed["ledger"][0]["label"] = "measured"
    issue = normalize_extract(
        parsed,
        kind="issue",
        url="https://github.com/plastic-labs/honcho/issues/1",
    )
    assert issue["ledger"][0]["label"] == "inferred"
