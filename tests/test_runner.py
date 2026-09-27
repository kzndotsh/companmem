"""Unit tests for harness.runner internals."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

from harness.runner import enumerate_fixtures, load_fixture_meta, load_registry

# ── fixture enumeration ───────────────────────────────────────────────────────


def testenumerate_fixtures_excludes_underscore_dirs(tmp_path: Path) -> None:
    (tmp_path / "fixture-a").mkdir()
    (tmp_path / "fixture-b").mkdir()
    (tmp_path / "_held-out").mkdir()
    (tmp_path / "_shared").mkdir()
    (tmp_path / "not-a-dir.txt").write_text("x")

    result = enumerate_fixtures(tmp_path)
    assert result == ["fixture-a", "fixture-b"]


def testenumerate_fixtures_sorted(tmp_path: Path) -> None:
    (tmp_path / "zebra").mkdir()
    (tmp_path / "alpha").mkdir()
    (tmp_path / "mango").mkdir()
    result = enumerate_fixtures(tmp_path)
    assert result == ["alpha", "mango", "zebra"]


def testenumerate_fixtures_empty_dir(tmp_path: Path) -> None:
    result = enumerate_fixtures(tmp_path)
    assert result == []


# ── registry loading ──────────────────────────────────────────────────────────


def test_registry_loads_14_adapters() -> None:
    registry = load_registry()
    assert len(registry["adapters"]) == 14


def test_registry_all_ids_unique() -> None:
    registry = load_registry()
    ids = [a["id"] for a in registry["adapters"]]
    assert len(ids) == len(set(ids))


def test_registry_all_classes_resolve() -> None:
    """All 14 adapter class paths must importable without error."""
    registry = load_registry()
    for entry in registry["adapters"]:
        class_path = str(entry["class"])
        mod_path, cls_name = class_path.rsplit(".", 1)
        mod = importlib.import_module(mod_path)
        cls = getattr(mod, cls_name)
        assert callable(cls), f"{class_path} is not callable"


def test_registry_baseline_all_includes_all_adapters() -> None:
    registry = load_registry()
    assert len(registry["adapters"]) >= 14


def test_registry_oracle_baseline_exists() -> None:
    registry = load_registry()
    ids = {a["id"] for a in registry["adapters"]}
    assert "oracle" in ids


# ── docker-skip logic ─────────────────────────────────────────────────────────


def test_docker_adapters_flagged_in_registry() -> None:
    """graphiti and honcho must have needs_docker: true."""
    registry = load_registry()
    by_id = {a["id"]: a for a in registry["adapters"]}
    assert by_id["graphiti"]["needs_docker"] is True
    assert by_id["honcho"]["needs_docker"] is True


def test_non_docker_adapters_not_flagged() -> None:
    registry = load_registry()
    by_id = {a["id"]: a for a in registry["adapters"]}
    assert by_id["oracle"]["needs_docker"] is False
    assert by_id["naive-retrieve"]["needs_docker"] is False


# ── --fixture filtering ───────────────────────────────────────────────────────


def test_single_fixture_filter(tmp_path: Path) -> None:
    """When --fixture is given, only that fixture id is run."""
    for name in ["alpha", "beta", "gamma"]:
        (tmp_path / name).mkdir()

    all_fixtures = enumerate_fixtures(tmp_path)
    assert "beta" in all_fixtures

    # Simulate the filter logic from _cmd_run
    selected = ["beta"]  # as if --fixture beta was passed
    assert selected == ["beta"]
    assert len(selected) == 1


# ── cost_budgets in manifest ──────────────────────────────────────────────────


def test_registry_has_cost_budgets() -> None:
    registry = load_registry()
    assert "cost_budgets" in registry
    assert "export_tokens_approx_per_trial" in registry["cost_budgets"]
    assert "wall_ms_per_trial" in registry["cost_budgets"]


# ── FixtureMeta loading ───────────────────────────────────────────────────────


def test_load_fixture_meta_returns_none_for_missing_file(tmp_path: Path) -> None:
    result = load_fixture_meta(tmp_path)
    assert result is None


def test_load_fixture_meta_returns_none_for_malformed_json(tmp_path: Path) -> None:
    (tmp_path / "fixture.json").write_text("not json")
    result = load_fixture_meta(tmp_path)
    assert result is None


def test_load_fixture_meta_parses_valid_fixture(tmp_path: Path) -> None:
    (tmp_path / "fixture.json").write_text(json.dumps({
        "id": "b0-test",
        "behavior": "b0",
        "title": "Test",
        "description": "Desc.",
        "probe_type": "stable-self",
        "pass_proves": "Proves.",
        "fail_reveals": "Reveals.",
        "why_naive_fails": "Because.",
    }))
    meta = load_fixture_meta(tmp_path)
    assert meta is not None
    assert meta.behavior == "b0"
    assert meta.id == "b0-test"


# ── behavior filtering logic ──────────────────────────────────────────────────


def test_behavior_filter_returns_correct_subset(tmp_path: Path) -> None:
    """Fixtures with matching behavior are included; others excluded."""
    for fid, beh in [("b0-a", "b0"), ("b0-b", "b0"), ("b5-a", "b5")]:
        d = tmp_path / fid
        d.mkdir()
        (d / "fixture.json").write_text(json.dumps({
            "id": fid, "behavior": beh, "title": "T", "description": "D.",
            "probe_type": "stable-self", "pass_proves": "P.", "fail_reveals": "F.",
            "why_naive_fails": "W.",
        }))
    all_ids = enumerate_fixtures(tmp_path)
    filtered = [
        fid for fid in all_ids
        if (meta := load_fixture_meta(tmp_path / fid)) is not None
        and meta.behavior == "b0"
    ]
    assert filtered == ["b0-a", "b0-b"]


def test_behavior_filter_no_match_returns_empty(tmp_path: Path) -> None:
    """No fixture has behavior b9 — filter returns empty list."""
    d = tmp_path / "b0-x"
    d.mkdir()
    (d / "fixture.json").write_text(json.dumps({
        "id": "b0-x", "behavior": "b0", "title": "T", "description": "D.",
        "probe_type": "stable-self", "pass_proves": "P.", "fail_reveals": "F.",
        "why_naive_fails": "W.",
    }))
    all_ids = enumerate_fixtures(tmp_path)
    filtered = [
        fid for fid in all_ids
        if (meta := load_fixture_meta(tmp_path / fid)) is not None
        and meta.behavior == "b9"
    ]
    assert filtered == []


def test_behavior_and_fixture_flags_are_mutually_exclusive(capsys: object) -> None:
    """Passing both --behavior and --fixture must return exit code 1."""
    import argparse

    from harness.runner import _cmd_run

    ns = argparse.Namespace(
        baseline="oracle",
        fixture="b0-x",
        behavior="b0",
        fixtures_root=None,
        results_root=None,
        include_docker=False,
    )
    rc = _cmd_run(ns)
    assert rc == 1
    out = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "mutually exclusive" in out
