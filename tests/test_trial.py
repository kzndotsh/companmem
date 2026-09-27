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
