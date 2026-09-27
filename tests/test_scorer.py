"""Unit tests for harness.scorer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from harness.artifacts import Artifacts
from harness.scorer import Scorer


def _write_predicates(path: Path, data: dict[str, Any]) -> Path:
    pred_file = path / "predicates.json"
    pred_file.write_text(json.dumps(data))
    return pred_file


def _make_artifacts(tmp_path: Path, reply: str = "hello", export: dict[str, Any] | None = None) -> Artifacts:
    a = Artifacts(tmp_path / "artifacts")
    a.write_reply(reply)
    a.write_export(export if export is not None else {})
    return a


# ── must_not ──────────────────────────────────────────────────────────────────


def test_must_not_pass(tmp_path: Path) -> None:
    preds = {"fail_to_pass": [{"id": "p1", "kind": "must_not", "target": "reply", "needles": ["forbidden"]}], "pass_to_pass": []}
    scorer = Scorer(_write_predicates(tmp_path, preds))
    a = _make_artifacts(tmp_path, reply="hello world")
    result = scorer.score(a)
    assert result.fail_to_pass is True


def test_must_not_fail(tmp_path: Path) -> None:
    preds = {"fail_to_pass": [{"id": "p1", "kind": "must_not", "target": "reply", "needles": ["hello"]}], "pass_to_pass": []}
    scorer = Scorer(_write_predicates(tmp_path, preds))
    a = _make_artifacts(tmp_path, reply="hello world")
    result = scorer.score(a)
    assert result.fail_to_pass is False


def test_must_not_case_insensitive(tmp_path: Path) -> None:
    preds = {"fail_to_pass": [{"id": "p1", "kind": "must_not", "target": "reply", "needles": ["HELLO"]}], "pass_to_pass": []}
    scorer = Scorer(_write_predicates(tmp_path, preds))
    a = _make_artifacts(tmp_path, reply="hello world")
    result = scorer.score(a)
    assert result.fail_to_pass is False  # HELLO found in hello


# ── must_any ──────────────────────────────────────────────────────────────────


def test_must_any_pass(tmp_path: Path) -> None:
    preds = {"fail_to_pass": [], "pass_to_pass": [{"id": "p1", "kind": "must_any", "target": "reply", "needles": ["world", "planet"]}]}
    scorer = Scorer(_write_predicates(tmp_path, preds))
    a = _make_artifacts(tmp_path, reply="hello world")
    result = scorer.score(a)
    assert result.pass_to_pass is True


def test_must_any_fail(tmp_path: Path) -> None:
    preds = {"fail_to_pass": [], "pass_to_pass": [{"id": "p1", "kind": "must_any", "target": "reply", "needles": ["planet", "moon"]}]}
    scorer = Scorer(_write_predicates(tmp_path, preds))
    a = _make_artifacts(tmp_path, reply="hello world")
    result = scorer.score(a)
    assert result.pass_to_pass is False


# ── must_contain ──────────────────────────────────────────────────────────────


def test_must_contain_all_pass(tmp_path: Path) -> None:
    preds = {"fail_to_pass": [], "pass_to_pass": [{"id": "p1", "kind": "must_contain", "target": "reply", "needles": ["hello", "world"]}]}
    scorer = Scorer(_write_predicates(tmp_path, preds))
    a = _make_artifacts(tmp_path, reply="hello world")
    result = scorer.score(a)
    assert result.pass_to_pass is True


def test_must_contain_partial_fail(tmp_path: Path) -> None:
    preds = {"fail_to_pass": [], "pass_to_pass": [{"id": "p1", "kind": "must_contain", "target": "reply", "needles": ["hello", "moon"]}]}
    scorer = Scorer(_write_predicates(tmp_path, preds))
    a = _make_artifacts(tmp_path, reply="hello world")
    result = scorer.score(a)
    assert result.pass_to_pass is False


# ── must_json_path ────────────────────────────────────────────────────────────


def test_must_json_path_valid(tmp_path: Path) -> None:
    preds = {
        "fail_to_pass": [],
        "pass_to_pass": [{"id": "p1", "kind": "must_json_path", "target": "export.user.name", "needles": ["Alice"]}],
    }
    scorer = Scorer(_write_predicates(tmp_path, preds))
    export = {"user": {"name": "Alice"}}
    a = _make_artifacts(tmp_path, export=export)
    result = scorer.score(a)
    assert result.pass_to_pass is True


def test_must_json_path_missing_key(tmp_path: Path) -> None:
    preds = {
        "fail_to_pass": [],
        "pass_to_pass": [{"id": "p1", "kind": "must_json_path", "target": "export.user.age", "needles": ["42"]}],
    }
    scorer = Scorer(_write_predicates(tmp_path, preds))
    export = {"user": {"name": "Alice"}}
    a = _make_artifacts(tmp_path, export=export)
    result = scorer.score(a)
    assert result.pass_to_pass is False
    assert any("bad target" in d or "key" in d for d in result.predicate_details)


def test_must_json_path_multiple_needles(tmp_path: Path) -> None:
    preds = {
        "fail_to_pass": [],
        "pass_to_pass": [{"id": "p1", "kind": "must_json_path", "target": "export.data", "needles": ["Alice", "Bob"]}],
    }
    scorer = Scorer(_write_predicates(tmp_path, preds))
    export = {"data": {"users": ["Alice", "Bob"]}}
    a = _make_artifacts(tmp_path, export=export)
    result = scorer.score(a)
    assert result.pass_to_pass is True


# ── target resolution ─────────────────────────────────────────────────────────


def test_target_export_full(tmp_path: Path) -> None:
    preds = {"fail_to_pass": [], "pass_to_pass": [{"id": "p1", "kind": "must_contain", "target": "export", "needles": ["Alice"]}]}
    scorer = Scorer(_write_predicates(tmp_path, preds))
    export = {"name": "Alice"}
    a = _make_artifacts(tmp_path, export=export)
    result = scorer.score(a)
    assert result.pass_to_pass is True


def test_target_export_path(tmp_path: Path) -> None:
    preds = {"fail_to_pass": [], "pass_to_pass": [{"id": "p1", "kind": "must_contain", "target": "export.inner", "needles": ["value"]}]}
    scorer = Scorer(_write_predicates(tmp_path, preds))
    a = _make_artifacts(tmp_path, export={"inner": "some value"})
    result = scorer.score(a)
    assert result.pass_to_pass is True


# ── group logic ───────────────────────────────────────────────────────────────


def test_resolved_requires_both_groups(tmp_path: Path) -> None:
    preds = {
        "fail_to_pass": [{"id": "f1", "kind": "must_not", "target": "reply", "needles": ["forbidden"]}],
        "pass_to_pass": [{"id": "p1", "kind": "must_contain", "target": "reply", "needles": ["hello"]}],
    }
    scorer = Scorer(_write_predicates(tmp_path, preds))

    # both pass
    a = _make_artifacts(tmp_path, reply="hello world")
    r = scorer.score(a)
    assert r.resolved is True
    assert r.fail_to_pass is True
    assert r.pass_to_pass is True


def test_resolved_false_when_f2p_fails(tmp_path: Path) -> None:
    preds = {
        "fail_to_pass": [{"id": "f1", "kind": "must_not", "target": "reply", "needles": ["hello"]}],
        "pass_to_pass": [{"id": "p1", "kind": "must_contain", "target": "reply", "needles": ["hello"]}],
    }
    scorer = Scorer(_write_predicates(tmp_path, preds))
    a = _make_artifacts(tmp_path, reply="hello world")
    r = scorer.score(a)
    assert r.fail_to_pass is False
    assert r.resolved is False


def test_empty_group_fails(tmp_path: Path) -> None:
    preds = {"fail_to_pass": [], "pass_to_pass": [{"id": "p1", "kind": "must_contain", "target": "reply", "needles": ["hello"]}]}
    scorer = Scorer(_write_predicates(tmp_path, preds))
    a = _make_artifacts(tmp_path, reply="hello")
    r = scorer.score(a)
    assert r.fail_to_pass is False  # empty group fails
    assert r.resolved is False


def test_bad_target_propagates_as_failed_predicate(tmp_path: Path) -> None:
    preds = {"fail_to_pass": [], "pass_to_pass": [{"id": "p1", "kind": "must_contain", "target": "bogus", "needles": ["x"]}]}
    scorer = Scorer(_write_predicates(tmp_path, preds))
    a = _make_artifacts(tmp_path)
    r = scorer.score(a)
    assert r.pass_to_pass is False
    assert any("bad target" in d for d in r.predicate_details)


# ── judge pass ────────────────────────────────────────────────────────────────


def test_judge_pass_sets_score_and_model(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    preds: dict[str, Any] = {
        "fail_to_pass": [],
        "pass_to_pass": [],
        "judge_prompt": "Is this a good reply?",
        "judge_model": "gpt-4o",
    }
    monkeypatch.setenv("HARNESS_JUDGE_API_KEY", "test-key")

    fake_response = json.dumps({"choices": [{"message": {"content": "0.85"}}]}).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = fake_response
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)

    scorer = Scorer(_write_predicates(tmp_path, preds))
    a = _make_artifacts(tmp_path)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        r = scorer.score(a)

    assert r.judge_score == pytest.approx(0.85)
    assert r.judge_model == "gpt-4o"
    assert r.resolved is False  # judge never changes resolved


def test_judge_missing_api_key_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    preds: dict[str, Any] = {"fail_to_pass": [], "pass_to_pass": [], "judge_prompt": "score this"}
    monkeypatch.delenv("HARNESS_JUDGE_API_KEY", raising=False)
    monkeypatch.setenv("HARNESS_JUDGE_MODEL", "gpt-4o")
    scorer = Scorer(_write_predicates(tmp_path, preds))
    a = _make_artifacts(tmp_path)
    with pytest.raises(RuntimeError, match="HARNESS_JUDGE_API_KEY"):
        scorer.score(a)
