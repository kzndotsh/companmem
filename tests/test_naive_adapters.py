"""Unit tests for naive baseline adapters."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness.adapter import AdapterNotReadyError
from harness.adapters.naive import (
    LongContextStuffAdapter,
    NaiveRagAdapter,
    NaiveRetrieveAdapter,
    OracleAdapter,
)
from harness.artifacts import Artifacts
from harness.world import (
    Character,
    FixtureSolution,
    SessionRow,
    World,
    WorldMeta,
)


def _make_world(*, with_solution: bool = True) -> World:
    meta = WorldMeta(
        active_character_id="mara",
        character_ids=("mara",),
        last_interaction=None,
        as_of=None,
    )
    sessions = (
        SessionRow(session=1, date="2025-01-01", summary="Mara visited the city."),
        SessionRow(session=2, date="2025-01-08", summary="Mara talked about her sister."),
    )
    character = Character(character_id="mara", identity="I am Mara.", sessions=sessions)
    solution: FixtureSolution | None = None
    if with_solution:
        solution = FixtureSolution(
            gold_reply="Gold reply for Mara.",
            gold_export={"characters": {"mara": {"kinds": {"user_bio": [{"id": "g", "text": "bio"}]}}}},
        )
    return World(
        meta=meta,
        characters={"mara": character},
        lore=None,
        next_user="How are you doing?",
        fixture_hash="fakehash",
        solution=solution,
    )


# ── OracleAdapter ─────────────────────────────────────────────────────────────


def test_oracle_raises_when_no_solution(tmp_path: Path) -> None:
    world = _make_world(with_solution=False)
    a = Artifacts(tmp_path / "out")
    with pytest.raises(AdapterNotReadyError, match="no solution"):
        OracleAdapter().run(world, a)


def test_oracle_writes_gold_artifacts(tmp_path: Path) -> None:
    world = _make_world(with_solution=True)
    a = Artifacts(tmp_path / "out")
    metrics = OracleAdapter().run(world, a)
    assert a.reply() == "Gold reply for Mara."
    assert a.export() == world.solution.gold_export  # type: ignore[union-attr]
    assert metrics.tokens_in == 0
    assert metrics.tokens_out == 0


# ── NaiveRetrieveAdapter ─────────────────────────────────────────────────────


def test_naive_retrieve_reply_contains_companion_prefix(tmp_path: Path) -> None:
    world = _make_world()
    a = Artifacts(tmp_path / "out")
    NaiveRetrieveAdapter().run(world, a)
    reply = a.reply()
    assert "I'm here for you" in reply
    assert "as your companion" in reply


def test_naive_retrieve_reply_contains_session_text(tmp_path: Path) -> None:
    world = _make_world()
    a = Artifacts(tmp_path / "out")
    NaiveRetrieveAdapter().run(world, a)
    reply = a.reply()
    assert "Mara visited the city" in reply


def test_naive_retrieve_export_has_structure(tmp_path: Path) -> None:
    world = _make_world()
    a = Artifacts(tmp_path / "out")
    NaiveRetrieveAdapter().run(world, a)
    export = a.export()
    assert "characters" in export
    assert "mara" in export["characters"]


# ── NaiveRagAdapter ──────────────────────────────────────────────────────────


def test_naive_rag_reply_contains_companion_prefix(tmp_path: Path) -> None:
    world = _make_world()
    a = Artifacts(tmp_path / "out")
    NaiveRagAdapter().run(world, a)
    reply = a.reply()
    assert "I'm here for you" in reply
    assert "as your companion" in reply


# ── LongContextStuffAdapter ──────────────────────────────────────────────────


def test_long_context_stuff_export_is_empty(tmp_path: Path) -> None:
    world = _make_world()
    a = Artifacts(tmp_path / "out")
    LongContextStuffAdapter().run(world, a)
    assert a.export() == {}


def test_long_context_stuff_reply_is_json(tmp_path: Path) -> None:
    world = _make_world()
    a = Artifacts(tmp_path / "out")
    LongContextStuffAdapter().run(world, a)
    # Should be valid JSON
    parsed = json.loads(a.reply())
    assert "characters" in parsed
    assert "meta" in parsed


# ── NaiveFullContextAdapter ──────────────────────────────────────────────────


from harness.adapters.naive import NaiveFullContextAdapter


def test_naive_full_context_reply_contains_session_text(tmp_path: Path) -> None:
    world = _make_world()
    a = Artifacts(tmp_path / "out")
    NaiveFullContextAdapter().run(world, a)
    reply = a.reply()
    assert "Mara visited the city" in reply
    assert "her sister" in reply


def test_naive_full_context_no_companion_prefix(tmp_path: Path) -> None:
    """NaiveFullContextAdapter must not include the companion-voice prefix."""
    world = _make_world()
    a = Artifacts(tmp_path / "out")
    NaiveFullContextAdapter().run(world, a)
    reply = a.reply()
    assert "I'm here for you" not in reply
    assert "as your companion" not in reply


def test_naive_full_context_export_has_structure(tmp_path: Path) -> None:
    world = _make_world()
    a = Artifacts(tmp_path / "out")
    NaiveFullContextAdapter().run(world, a)
    export = a.export()
    assert "active_character_id" in export
    assert "characters" in export
    assert "mara" in export["characters"]
    kinds = export["characters"]["mara"]["kinds"]
    assert "user_bio" in kinds
    assert len(kinds["user_bio"]) == 1


def test_naive_full_context_export_contains_session_keywords(tmp_path: Path) -> None:
    """Export user_bio text must contain the session content."""
    world = _make_world()
    a = Artifacts(tmp_path / "out")
    NaiveFullContextAdapter().run(world, a)
    export = a.export()
    bio_text = export["characters"]["mara"]["kinds"]["user_bio"][0]["text"]
    assert "Mara visited the city" in bio_text


def test_naive_full_context_metrics_nonzero(tmp_path: Path) -> None:
    world = _make_world()
    a = Artifacts(tmp_path / "out")
    metrics = NaiveFullContextAdapter().run(world, a)
    assert metrics.tokens_in > 0
    assert metrics.tokens_out > 0


def test_naive_full_context_lore_included(tmp_path: Path) -> None:
    """Lore text must appear in both reply and export when present."""
    meta = WorldMeta(
        active_character_id="mara",
        character_ids=("mara",),
        last_interaction=None,
        as_of=None,
    )
    character = Character(
        character_id="mara",
        identity="I am Mara.",
        sessions=(SessionRow(session=1, date="2025-01-01", summary="Mara visited the city."),),
    )
    world = World(
        meta=meta,
        characters={"mara": character},
        lore="The kingdom of Aldoria.",
        next_user="Tell me about the land.",
        fixture_hash="fakehash",
        solution=None,
    )
    a = Artifacts(tmp_path / "out")
    NaiveFullContextAdapter().run(world, a)
    assert "Aldoria" in a.reply()
    export = a.export()
    lore_entries = export["characters"]["mara"]["kinds"]["lore"]
    assert len(lore_entries) == 1
    assert "Aldoria" in lore_entries[0]["text"]
