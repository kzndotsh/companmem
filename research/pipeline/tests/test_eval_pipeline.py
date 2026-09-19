"""Tests for eval namespace: seed, harvest profile, schema paper kind."""

from __future__ import annotations

from companmem_pipeline.fold import filter_ledger_rows
from companmem_pipeline.harvest import (
    allowed_source_url,
    docs_harvest_url_allowed,
    eval_issue_search_query,
    harvest_docs_page_kind,
    load_eval,
    load_seed,
    open_doc_url_key,
    seed_open_doc_keys,
)
from companmem_pipeline.lint import lint_audit
from companmem_pipeline.seed_lint import lint_seed_structure


def test_seed_has_evals_and_no_product_collision() -> None:
    errors = lint_seed_structure(load_seed())
    assert errors == []


def test_eval_issue_query_targets_grader_metrics() -> None:
    query = eval_issue_search_query("snap-research", "locomo")
    assert "judge" in query
    assert "forget" not in query


def test_seed_listed_arxiv_open_doc_allowed() -> None:
    entry = load_eval("locomo")
    url = "https://arxiv.org/abs/2402.17753"
    assert open_doc_url_key(url) in seed_open_doc_keys(entry)
    assert allowed_source_url(url, entry, {"origin": entry.get("repo")})


def test_seed_open_doc_allowed_after_openreview_redirect() -> None:
    entry = load_eval("atod")
    requested = "https://openreview.net/forum?id=1L7cY1x2zp"
    redirected = "https://openreview.net/challenge?redirect=%2Fforum%3Fid%3D1L7cY1x2zp"
    assert open_doc_url_key(requested) in seed_open_doc_keys(entry)
    assert not allowed_source_url(redirected, entry, {})
    assert docs_harvest_url_allowed(requested, redirected, entry, {})


def test_harvest_docs_page_kind_paper_for_arxiv() -> None:
    entry = load_eval("locomo")
    assert harvest_docs_page_kind("https://arxiv.org/abs/2402.17753", entry) == "paper"


def test_lint_accepts_paper_ledger_kind() -> None:
    audit = {
        "identity": {"id": "locomo", "name": "LoCoMo", "observed_at": "2026-01-01"},
        "claimed_purpose": [],
        "mechanisms": [],
        "ledger": [
            {
                "claim": "LoCoMo has 500 questions",
                "kind": "paper",
                "url": "https://arxiv.org/abs/2402.17753",
                "quote": "500 evaluation instances",
                "locator": "abstract",
                "confidence": "medium",
                "label": "inferred",
            }
        ],
        "sources": [],
        "consensus": [],
        "contested": [],
        "copy": [],
        "refuse": [],
        "unknowns": [],
    }
    assert lint_audit(audit) == []


def test_eval_filter_ledger_keeps_hf_style_blog() -> None:
    row = {
        "claim": "Dataset card describes splits",
        "kind": "docs",
        "url": "https://huggingface.co/datasets/example/data",
        "quote": "train and test split",
        "locator": "card",
        "confidence": "medium",
        "label": "inferred",
    }
    kept = filter_ledger_rows([row], has_official_docs=True, subject="eval")
    assert kept == [row]
