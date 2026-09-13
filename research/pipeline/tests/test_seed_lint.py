"""Tests for seed.json lint rules."""

from __future__ import annotations

from companmem_pipeline.harvest import (
    load_seed,
    product_named_in_url_or_title,
    reddit_subreddit_prefix_collision,
)
from companmem_pipeline.seed_lint import lint_seed, lint_seed_structure


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
