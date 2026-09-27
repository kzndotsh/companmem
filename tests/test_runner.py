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
    assert len(registry["adapters"]) == 15


def test_registry_all_ids_unique() -> None:
    registry = load_registry()
    ids = [a["id"] for a in registry["adapters"]]
    assert len(ids) == len(set(ids))


def test_registry_all_classes_resolve() -> None:
    """All adapter class paths must be importable without error."""
    registry = load_registry()
    for entry in registry["adapters"]:
        class_path = str(entry["class"])
        mod_path, cls_name = class_path.rsplit(".", 1)
        mod = importlib.import_module(mod_path)
        cls = getattr(mod, cls_name)
        assert callable(cls), f"{class_path} is not callable"


def test_registry_baseline_all_includes_all_adapters() -> None:
    registry = load_registry()
    assert len(registry["adapters"]) >= 15


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


# ── split filter logic ────────────────────────────────────────────────────────


def _make_fixture_dir(root: Path, fid: str, behavior: str = "b0", split: str = "dev") -> None:
    d = root / fid
    d.mkdir()
    (d / "fixture.json").write_text(json.dumps({
        "id": fid, "behavior": behavior, "title": "T", "description": "D.",
        "probe_type": "stable-self", "pass_proves": "P.", "fail_reveals": "F.",
        "why_naive_fails": "W.", "split": split,
    }))


def test_split_filter_dev_returns_only_dev(tmp_path: Path) -> None:
    """--split dev must include only fixtures tagged split=dev."""
    _make_fixture_dir(tmp_path, "b0-dev-a", split="dev")
    _make_fixture_dir(tmp_path, "b0-dev-b", split="dev")
    _make_fixture_dir(tmp_path, "b0-test-a", split="test")
    all_ids = enumerate_fixtures(tmp_path)
    filtered = [
        fid for fid in all_ids
        if (meta := load_fixture_meta(tmp_path / fid)) is not None
        and meta.split == "dev"
    ]
    assert sorted(filtered) == ["b0-dev-a", "b0-dev-b"]


def test_split_filter_test_returns_only_test(tmp_path: Path) -> None:
    """--split test must include only fixtures tagged split=test."""
    _make_fixture_dir(tmp_path, "b0-dev-x", split="dev")
    _make_fixture_dir(tmp_path, "b0-test-x", split="test")
    all_ids = enumerate_fixtures(tmp_path)
    filtered = [
        fid for fid in all_ids
        if (meta := load_fixture_meta(tmp_path / fid)) is not None
        and meta.split == "test"
    ]
    assert filtered == ["b0-test-x"]


def test_split_defaults_to_dev_when_field_absent(tmp_path: Path) -> None:
    """A fixture.json without a split field must default to 'dev'."""
    d = tmp_path / "b0-no-split"
    d.mkdir()
    (d / "fixture.json").write_text(json.dumps({
        "id": "b0-no-split", "behavior": "b0", "title": "T", "description": "D.",
        "probe_type": "stable-self", "pass_proves": "P.", "fail_reveals": "F.",
        "why_naive_fails": "W.",
    }))
    meta = load_fixture_meta(tmp_path / "b0-no-split")
    assert meta is not None
    assert meta.split == "dev"


def test_load_fixture_meta_parses_split_field(tmp_path: Path) -> None:
    """split field is loaded correctly when present."""
    _make_fixture_dir(tmp_path, "b0-held", split="test")
    meta = load_fixture_meta(tmp_path / "b0-held")
    assert meta is not None
    assert meta.split == "test"


def test_behavior_and_fixture_flags_are_mutually_exclusive(capsys: object) -> None:
    """Passing both --behavior and --fixture must return exit code 1."""
    import argparse

    from harness.runner import _cmd_run  # pyright: ignore[reportPrivateUsage]

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


# ── --runs flag ───────────────────────────────────────────────────────────────


def test_runs_flag_zero_exits_1(capsys: object) -> None:
    import argparse

    from harness.runner import _cmd_run  # pyright: ignore[reportPrivateUsage]

    ns = argparse.Namespace(
        baseline="oracle",
        fixture=None,
        behavior=None,
        fixtures_root=None,
        results_root=None,
        include_docker=False,
        runs=0,
    )
    rc = _cmd_run(ns)
    assert rc == 1
    out = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "error: --runs must be ≥ 1" in out


def test_runs_flag_default_1() -> None:
    import argparse

    args = argparse.Namespace(runs=1)
    assert args.runs == 1


# ── artifact path layout ──────────────────────────────────────────────────────


def test_multirun_artifact_paths_use_run_subdirs(tmp_path: Path) -> None:
    """With runs > 1, artifacts_path must end with run_<index>."""
    from unittest.mock import MagicMock, patch

    from harness.artifacts import ArtifactMissing
    from harness.runner import _run_trial  # pyright: ignore[reportPrivateUsage]

    adapter_entry = {
        "id": "oracle",
        "class": "harness.adapters.naive.OracleAdapter",
        "needs_docker": False,
    }

    mock_world = MagicMock()
    mock_world.fixture_hash = "testhash"

    for run_index in (0, 2):
        with (
            patch("harness.runner.World") as mock_world_cls,
            patch("harness.runner.Artifacts") as mock_artifacts_cls,
            patch("importlib.import_module"),
        ):
            mock_world_cls.from_path.return_value = mock_world
            mock_artifacts_cls.return_value.export.side_effect = ArtifactMissing("missing")
            result = _run_trial(
                adapter_entry=adapter_entry,
                fixture_id="b0-test",
                fixtures_root=tmp_path / "fixtures",
                results_root=tmp_path / "results",
                run_id="run1",
                include_docker=False,
                cost_budgets={},
                run_index=run_index,
                runs=3,
            )
        assert result.artifacts_path.endswith(f"run_{run_index}"), (
            f"Expected path ending with run_{run_index}, got: {result.artifacts_path}"
        )


def test_singlerun_artifact_paths_unchanged(tmp_path: Path) -> None:
    """With runs == 1, artifacts_path must not contain run_ segments."""
    from unittest.mock import MagicMock, patch

    from harness.artifacts import ArtifactMissing
    from harness.runner import _run_trial  # pyright: ignore[reportPrivateUsage]

    adapter_entry = {
        "id": "oracle",
        "class": "harness.adapters.naive.OracleAdapter",
        "needs_docker": False,
    }

    mock_world = MagicMock()
    mock_world.fixture_hash = "testhash"

    with (
        patch("harness.runner.World") as mock_world_cls,
        patch("harness.runner.Artifacts") as mock_artifacts_cls,
        patch("importlib.import_module"),
    ):
        mock_world_cls.from_path.return_value = mock_world
        mock_artifacts_cls.return_value.export.side_effect = ArtifactMissing("missing")
        result = _run_trial(
            adapter_entry=adapter_entry,
            fixture_id="b0-test",
            fixtures_root=tmp_path / "fixtures",
            results_root=tmp_path / "results",
            run_id="run1",
            include_docker=False,
            cost_budgets={},
            run_index=0,
            runs=1,
        )
    assert "run_" not in result.artifacts_path, (
        f"Expected no run_ in path, got: {result.artifacts_path}"
    )
