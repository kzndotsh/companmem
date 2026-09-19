"""Tests for seed.json lint rules."""

from __future__ import annotations

from pathlib import Path

from companmem_pipeline.harvest import (
    load_seed,
    product_named_in_url_or_title,
    reddit_subreddit_prefix_collision,
)
from companmem_pipeline.seed_lint import (
    lint_open_code_paths,
    lint_seed,
    lint_seed_structure,
)

def test_lint_seed_structure_passes() -> None:
    assert lint_seed_structure(load_seed()) == []


def test_zep_open_docs_skip_graphiti_paths() -> None:
    seed = load_seed()
    products = seed["products"]
    assert isinstance(products, dict)
    zep = products["zep"]
    assert isinstance(zep, dict)
    for url in zep["open_docs"]:
        assert "/graphiti" not in url


def test_reddit_subreddit_prefix_collision_blocks_zepbound() -> None:
    zep = {"id": "zep", "name": "Zep Cloud"}
    assert reddit_subreddit_prefix_collision("zepbound", zep)
    assert not reddit_subreddit_prefix_collision("zep", zep)
    assert not reddit_subreddit_prefix_collision("zep_cloud", zep)
    assert not product_named_in_url_or_title(
        "https://www.reddit.com/r/Zepbound/comments/abc/on_zep_cloud_9/",
        "On Zep Cloud 9",
        zep,
    )
    assert product_named_in_url_or_title(
        "https://www.reddit.com/r/zep/comments/abc/review/",
        "Zep Cloud memory review",
        zep,
    )


def test_lint_seed_offline() -> None:
    assert lint_seed(check_urls=False) == []


def test_lint_open_code_paths_for_cached_clones() -> None:
    seed = load_seed()
    errors = lint_open_code_paths(seed)
    assert errors == []


def test_lint_open_code_detects_missing_path(tmp_path: Path) -> None:
    repo = tmp_path / "demo" / "repo"
    repo.mkdir(parents=True)
    (repo / ".git").mkdir()
    (repo / "README.md").write_text("# demo", encoding="utf-8")
    seed = {
        "products": {
            "demo": {
                "id": "demo",
                "clone": True,
                "open_code": ["README.md", "missing.py"],
            }
        }
    }
    errors = lint_open_code_paths(seed, cache_dir=tmp_path)
    assert any("missing.py" in err for err in errors)


def test_lint_open_code_detects_empty_path(tmp_path: Path) -> None:
    repo = tmp_path / "demo" / "repo"
    repo.mkdir(parents=True)
    (repo / ".git").mkdir()
    (repo / "README.md").write_text("# demo", encoding="utf-8")
    (repo / "empty.py").write_bytes(b"")
    seed = {
        "products": {
            "demo": {
                "id": "demo",
                "clone": True,
                "open_code": ["README.md", "empty.py"],
            }
        }
    }
    errors = lint_open_code_paths(seed, cache_dir=tmp_path)
    assert any("empty.py" in err and "empty" in err for err in errors)


def test_evals_required_and_collision_guard() -> None:
    seed = load_seed()
    assert "evals" in seed
    assert isinstance(seed["evals"], dict)
    assert "locomo" in seed["evals"]
    bad = {
        "products": {"dup": {"id": "dup", "name": "Dup", "repo": "", "docs": "", "clone": False, "community": [], "skip_url_prefixes": [], "open_code": [], "open_docs": ["https://example.com/a"]}},
        "evals": {"dup": {"id": "dup", "name": "Dup", "repo": "", "docs": "", "clone": False, "community": [], "skip_url_prefixes": [], "open_code": [], "open_docs": ["https://example.com/b"]}},
    }
    assert any("both products and evals" in err for err in lint_seed_structure(bad))


def test_clone_true_requires_nonempty_open_code() -> None:
    seed = {
        "evals": {},
        "products": {
            "bad": {
                "id": "bad",
                "name": "Bad",
                "repo": "https://github.com/example/bad",
                "docs": "https://example.com/docs",
                "clone": True,
                "community": [],
                "skip_url_prefixes": [],
                "open_code": [],
                "open_docs": ["https://example.com/docs"],
            }
        }
    }
    assert any("open_code is empty" in err for err in lint_seed_structure(seed))
