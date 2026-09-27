"""Unit tests for harness.trial."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from harness.trial import BaselineResult, RunReport, TrialResult, TrialStatus


def _make_trial(
    fixture_id: str = "f1",
    status: TrialStatus = TrialStatus.OK,
    resolved: bool = True,
    tokens_in: int = 10,
    tokens_out: int = 5,
    run_index: int = 0,
    behavior: str | None = None,
) -> TrialResult:
    return TrialResult(
        fixture_id=fixture_id,
        fixture_hash="abc",
        status=status,
        resolved=resolved,
        fail_to_pass=resolved,
        pass_to_pass=resolved,
        predicate_details=[],
        judge_score=None,
        judge_model=None,
        wall_ms=100,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        memory_tokens=0,
        export_tokens_approx=0,
        cost_flags=[],
        artifacts_path="results/run/base/f1",
        error=None,
        run_index=run_index,
        behavior=behavior,
    )


def _make_report(trials: list[TrialResult] | None = None) -> RunReport:
    if trials is None:
        trials = [_make_trial()]
    bl = BaselineResult.from_trials("oracle", "Oracle", trials)
    return RunReport(
        run_id="abc123",
        observed_at="2025-01-01T00:00:00+00:00",
        scored_at="2025-01-01T00:01:00+00:00",
        git_sha="deadbeef",
        fixture_ids=["f1"],
        baselines=[bl],
    )


# ── TrialStatus serialization ─────────────────────────────────────────────────


def test_trial_status_serializes_as_string() -> None:
    t = _make_trial()
    d = t.to_dict()
    assert d["status"] == "ok"
    assert isinstance(d["status"], str)


def test_trial_status_infra_error_string() -> None:
    t = _make_trial(status=TrialStatus.INFRA_ERROR, resolved=False)
    assert t.to_dict()["status"] == "infra_error"


# ── RunReport serialization ───────────────────────────────────────────────────


def test_run_report_to_json_round_trips() -> None:
    report = _make_report()
    raw = report.to_json()
    parsed = json.loads(raw)
    assert parsed["run_id"] == "abc123"
    assert parsed["baselines"][0]["baseline_id"] == "oracle"
    assert parsed["baselines"][0]["trials"][0]["status"] == "ok"


# ── BaselineResult.from_trials aggregation ───────────────────────────────────


def test_from_trials_all_ok_resolved() -> None:
    trials = [_make_trial("f1", TrialStatus.OK, True), _make_trial("f2", TrialStatus.OK, True)]
    bl = BaselineResult.from_trials("b", "B", trials)
    assert bl.fixture_count == 2
    assert bl.runnable_count == 2
    assert bl.resolved_count == 2


def test_from_trials_mixed_status() -> None:
    trials = [
        _make_trial("f1", TrialStatus.OK, resolved=True, tokens_in=10, tokens_out=5),
        _make_trial("f2", TrialStatus.SKIPPED, resolved=False, tokens_in=0, tokens_out=0),
        _make_trial("f3", TrialStatus.INFRA_ERROR, resolved=False, tokens_in=0, tokens_out=0),
    ]
    bl = BaselineResult.from_trials("b", "B", trials)
    # fixture_count includes all trials
    assert bl.fixture_count == 3
    # runnable_count: only OK
    assert bl.runnable_count == 1
    # resolved_count: only OK and resolved
    assert bl.resolved_count == 1
    # token sums: only OK trials
    assert bl.total_tokens_in == 10
    assert bl.total_tokens_out == 5


def test_from_trials_tokens_per_resolved_none_when_no_resolved() -> None:
    trials = [_make_trial("f1", TrialStatus.OK, resolved=False)]
    bl = BaselineResult.from_trials("b", "B", trials)
    assert bl.tokens_per_resolved is None


def test_from_trials_tokens_per_resolved_computed() -> None:
    trials = [_make_trial("f1", TrialStatus.OK, resolved=True, tokens_in=100, tokens_out=50)]
    bl = BaselineResult.from_trials("b", "B", trials)
    assert bl.tokens_per_resolved == 150  # (100+50) // 1


# ── rescore() SKIPPED/INFRA_ERROR guard ─────────────────────────────────────


def test_rescore_carries_forward_non_ok_trials(tmp_path: Path) -> None:
    """rescore() must not call scorer.score() on SKIPPED or INFRA_ERROR trials."""
    artifacts_root = tmp_path / "results" / "run1"
    artifacts_root.mkdir(parents=True)

    skipped = _make_trial("f1", TrialStatus.SKIPPED, resolved=False)
    infra = _make_trial("f2", TrialStatus.INFRA_ERROR, resolved=False)
    bl = BaselineResult.from_trials("oracle", "Oracle", [skipped, infra])
    report = RunReport(
        run_id="run1",
        observed_at="2025-01-01T00:00:00+00:00",
        scored_at="2025-01-01T00:01:00+00:00",
        git_sha="abc",
        fixture_ids=["f1", "f2"],
        baselines=[bl],
    )
    (artifacts_root / "report.json").write_text(report.to_json())
    manifest: dict[str, Any] = {
        "run_id": "run1",
        "observed_at": "2025-01-01T00:00:00+00:00",
        "git_sha": "abc",
        "fixture_ids": ["f1", "f2"],
        "cost_budgets": {},
        "baselines": [{"baseline_id": "oracle", "title": "Oracle", "class": "harness.adapters.naive.OracleAdapter", "needs_docker": False}],
    }
    (artifacts_root / "run_manifest.json").write_text(json.dumps(manifest))

    fixtures_root = tmp_path / "fixtures"
    fixtures_root.mkdir()

    new_report = RunReport.rescore(artifacts_root, fixtures_root)

    # Both trials carried forward, status unchanged
    new_trials = new_report.baselines[0].trials
    assert len(new_trials) == 2
    statuses = {t.fixture_id: t.status for t in new_trials}
    assert statuses["f1"] == TrialStatus.SKIPPED
    assert statuses["f2"] == TrialStatus.INFRA_ERROR


def test_rescore_missing_manifest_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        RunReport.rescore(tmp_path, tmp_path)


def test_rescore_malformed_manifest_raises(tmp_path: Path) -> None:
    (tmp_path / "run_manifest.json").write_text("not json")
    (tmp_path / "report.json").write_text(json.dumps({"baselines": [], "fixture_ids": [], "observed_at": "", "git_sha": ""}))
    with pytest.raises(ValueError):
        RunReport.rescore(tmp_path, tmp_path)


def test_rescore_missing_report_raises(tmp_path: Path) -> None:
    (tmp_path / "run_manifest.json").write_text(json.dumps({"run_id": "x", "baselines": [], "fixture_ids": []}))
    with pytest.raises(FileNotFoundError):
        RunReport.rescore(tmp_path, tmp_path)


# ── run_index serialization ───────────────────────────────────────────────────


def test_run_index_default_zero() -> None:
    t = _make_trial()
    assert t.run_index == 0
    assert t.to_dict()["run_index"] == 0


def test_run_index_serializes() -> None:
    t = _make_trial(run_index=2)
    d = t.to_dict()
    assert d["run_index"] == 2
    t2 = TrialResult.from_dict(d)
    assert t2.run_index == 2


def test_from_dict_missing_run_index_defaults_zero() -> None:
    t = _make_trial()
    d = t.to_dict()
    del d["run_index"]
    t2 = TrialResult.from_dict(d)
    assert t2.run_index == 0


# ── resolved_by_behavior ─────────────────────────────────────────────────────


def test_resolved_by_behavior_all_pass() -> None:
    trials = [_make_trial(f"b0-{i}", resolved=True, behavior="b0") for i in range(4)]
    bl = BaselineResult.from_trials("base", "Base", trials)
    assert bl.resolved_by_behavior == {"b0": [4, 4]}


def test_resolved_by_behavior_partial() -> None:
    trials = [
        _make_trial("b0-0", resolved=True, behavior="b0"),
        _make_trial("b0-1", resolved=True, behavior="b0"),
        _make_trial("b0-2", resolved=False, behavior="b0"),
    ]
    bl = BaselineResult.from_trials("base", "Base", trials)
    assert bl.resolved_by_behavior == {"b0": [2, 3]}


def test_resolved_by_behavior_excludes_none_behavior() -> None:
    trials = [
        _make_trial("f1", resolved=True, behavior=None),
        _make_trial("f2", resolved=True, behavior=None),
    ]
    bl = BaselineResult.from_trials("base", "Base", trials)
    assert bl.resolved_by_behavior == {}


def test_resolved_by_behavior_none_trial_before_behavior_trial() -> None:
    """A behavior=None trial arriving before a behavior='b0' trial must not shadow it."""
    trials = [
        _make_trial("f1", status=TrialStatus.SKIPPED, resolved=False, behavior=None, run_index=0),
        _make_trial("f1", resolved=True, behavior="b0", run_index=1),
    ]
    bl = BaselineResult.from_trials("base", "Base", trials)
    assert "b0" in bl.resolved_by_behavior
    assert bl.resolved_by_behavior["b0"] == [1, 1]


# ── pass@k / pass^k ──────────────────────────────────────────────────────────


def test_pass_at_k_none_when_n1() -> None:
    trials = [_make_trial("f1", resolved=True, behavior="b0")]
    bl = BaselineResult.from_trials("base", "Base", trials)
    assert bl.pass_at_k is None
    assert bl.pass_k is None


def test_pass_at_k_computed_n3() -> None:
    # 3 fixtures × 3 runs; fixtures f1 and f2 resolve all 3 runs; f3 fails all
    trials: list[TrialResult] = []
    for fid, resolves in [("f1", True), ("f2", True), ("f3", False)]:
        for ri in range(3):
            trials.append(_make_trial(fid, resolved=resolves, behavior="b0", run_index=ri))
    bl = BaselineResult.from_trials("base", "Base", trials)
    assert bl.pass_at_k == pytest.approx(2 / 3)
    assert bl.pass_k == pytest.approx(2 / 3)


def test_pass_at_k_partial_resolve() -> None:
    # 1 fixture × 2 runs; run 0 resolves, run 1 does not
    trials = [
        _make_trial("f1", resolved=True, behavior="b0", run_index=0),
        _make_trial("f1", resolved=False, behavior="b0", run_index=1),
    ]
    bl = BaselineResult.from_trials("base", "Base", trials)
    assert bl.pass_at_k == pytest.approx(1.0)
    assert bl.pass_k == pytest.approx(0.0)


def test_infra_error_within_multirun_excluded_from_denominator_when_all_error() -> None:
    # 1 fixture × 2 runs, both INFRA_ERROR → denom == 0 → both None
    trials = [
        _make_trial("f1", status=TrialStatus.INFRA_ERROR, resolved=False, run_index=0),
        _make_trial("f1", status=TrialStatus.INFRA_ERROR, resolved=False, run_index=1),
    ]
    bl = BaselineResult.from_trials("base", "Base", trials)
    assert bl.pass_at_k is None
    assert bl.pass_k is None


# ── to_dict emits new fields ──────────────────────────────────────────────────


def test_to_dict_emits_three_new_fields() -> None:
    bl = BaselineResult.from_trials("b", "B", [_make_trial()])
    d = bl.to_dict()
    assert "resolved_by_behavior" in d
    assert "pass_at_k" in d
    assert "pass_k" in d


# ── rescore() multi-run keying ────────────────────────────────────────────────


def test_rescore_multirun_keying(tmp_path: Path) -> None:
    """rescore() on a 9-fixture × 3-run report must return 27 trials."""
    from unittest.mock import MagicMock, patch

    from harness.trial import RunReport

    artifacts_root = tmp_path / "results" / "run1"
    artifacts_root.mkdir(parents=True)
    fixtures_root = tmp_path / "fixtures"
    fixtures_root.mkdir()

    fixture_ids = [f"f{i}" for i in range(9)]

    # Build a report with 27 trials (9 fixtures × 3 run_index values)
    trials: list[TrialResult] = []
    for fid in fixture_ids:
        for ri in range(3):
            art_path = f"results/run1/oracle/{fid}/run_{ri}"
            trials.append(TrialResult(
                fixture_id=fid,
                fixture_hash="abc",
                status=TrialStatus.OK,
                resolved=True,
                fail_to_pass=True,
                pass_to_pass=True,
                predicate_details=[],
                judge_score=None,
                judge_model=None,
                wall_ms=10,
                tokens_in=1,
                tokens_out=1,
                memory_tokens=0,
                export_tokens_approx=0,
                cost_flags=[],
                artifacts_path=art_path,
                error=None,
                behavior="b0",
                run_index=ri,
            ))

    bl = BaselineResult.from_trials("oracle", "Oracle", trials)
    report = RunReport(
        run_id="run1",
        observed_at="2025-01-01T00:00:00+00:00",
        scored_at="2025-01-01T00:01:00+00:00",
        git_sha="abc",
        fixture_ids=fixture_ids,
        baselines=[bl],
    )
    (artifacts_root / "report.json").write_text(report.to_json())
    manifest: dict[str, Any] = {
        "run_id": "run1",
        "runs": 3,
        "observed_at": "2025-01-01T00:00:00+00:00",
        "git_sha": "abc",
        "fixture_ids": fixture_ids,
        "cost_budgets": {},
        "baselines": [{"baseline_id": "oracle", "title": "Oracle",
                       "class": "harness.adapters.naive.OracleAdapter", "needs_docker": False}],
    }
    (artifacts_root / "run_manifest.json").write_text(json.dumps(manifest))

    # Patch Scorer so no real artifact files are needed
    mock_result = MagicMock()
    mock_result.resolved = True
    mock_result.fail_to_pass = True
    mock_result.pass_to_pass = True
    mock_result.predicate_details = []
    mock_result.judge_score = None
    mock_result.judge_model = None

    with patch("harness.trial.Scorer") as mock_scorer_cls:
        mock_scorer_cls.return_value.score.return_value = mock_result
        new_report = RunReport.rescore(artifacts_root, fixtures_root)

    assert len(new_report.baselines) == 1
    assert len(new_report.baselines[0].trials) == 27
