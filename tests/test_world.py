"""Unit tests for harness.world."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from harness.world import FixtureSolution, World


def _make_world_dir(
    tmp_path: Path,
    *,
    character_id: str = "mara",
    sessions: list[dict[str, Any]] | None = None,
    with_lore: bool = False,
    with_solution: bool = False,
) -> tuple[Path, Path | None]:
    """Create a minimal fixture world directory and optional solution directory."""
    world_dir = tmp_path / "world"
    companion_dir = world_dir / "companions" / character_id
    companion_dir.mkdir(parents=True)

    meta = {"active_character_id": character_id, "character_ids": [character_id]}
    (world_dir / "meta.json").write_text(json.dumps(meta))
    (companion_dir / "character.md").write_text(f"I am {character_id}.")

    if sessions:
        lines = "\n".join(json.dumps(s) for s in sessions)
        (companion_dir / "sessions.jsonl").write_text(lines + "\n")

    (world_dir / "next_user.txt").write_text("Hello, how are you?")

    if with_lore:
        (world_dir / "lore.md").write_text("Lore text here.")

    solution_dir: Path | None = None
    if with_solution:
        solution_dir = tmp_path / "solution"
        solution_dir.mkdir()
        (solution_dir / "gold_reply.txt").write_text("Gold reply.")
        (solution_dir / "gold_memory_export.json").write_text(json.dumps({"characters": {}}))

    return world_dir, solution_dir


def test_from_path_basic(tmp_path: Path) -> None:
    world_dir, _ = _make_world_dir(tmp_path)
    world = World.from_path(world_dir)
    assert world.meta.active_character_id == "mara"
    assert world.meta.character_ids == ("mara",)
    assert world.next_user == "Hello, how are you?"
    assert world.lore is None
    assert world.solution is None


def test_from_path_sessions(tmp_path: Path) -> None:
    sessions = [
        {"session": 1, "date": "2025-01-01", "summary": "First session."},
        {"session": 2, "date": "2025-01-08", "summary": "Second session."},
    ]
    world_dir, _ = _make_world_dir(tmp_path, sessions=sessions)
    world = World.from_path(world_dir)
    assert len(world.characters["mara"].sessions) == 2
    assert world.characters["mara"].sessions[0].summary == "First session."


def test_sessions_is_tuple(tmp_path: Path) -> None:
    sessions = [{"session": 1, "date": "2025-01-01", "summary": "s"}]
    world_dir, _ = _make_world_dir(tmp_path, sessions=sessions)
    world = World.from_path(world_dir)
    assert isinstance(world.characters["mara"].sessions, tuple)
    assert isinstance(world.meta.character_ids, tuple)


def test_fixture_hash_stable(tmp_path: Path) -> None:
    world_dir, _ = _make_world_dir(tmp_path)
    h1 = World.from_path(world_dir).fixture_hash
    h2 = World.from_path(world_dir).fixture_hash
    assert h1 == h2


def test_fixture_hash_changes_on_file_change(tmp_path: Path) -> None:
    world_dir, _ = _make_world_dir(tmp_path)
    h1 = World.from_path(world_dir).fixture_hash
    (world_dir / "next_user.txt").write_text("Different question?")
    h2 = World.from_path(world_dir).fixture_hash
    assert h1 != h2


def test_lore_present(tmp_path: Path) -> None:
    world_dir, _ = _make_world_dir(tmp_path, with_lore=True)
    world = World.from_path(world_dir)
    assert world.lore == "Lore text here."


def test_solution_none_when_not_passed(tmp_path: Path) -> None:
    world_dir, _ = _make_world_dir(tmp_path, with_solution=True)
    world = World.from_path(world_dir)  # no solution_dir
    assert world.solution is None


def test_solution_populated_when_both_files_present(tmp_path: Path) -> None:
    world_dir, solution_dir = _make_world_dir(tmp_path, with_solution=True)
    assert solution_dir is not None
    world = World.from_path(world_dir, solution_dir=solution_dir)
    assert isinstance(world.solution, FixtureSolution)
    assert world.solution.gold_reply == "Gold reply."
    assert isinstance(world.solution.gold_export, dict)


def test_solution_none_when_gold_reply_missing(tmp_path: Path) -> None:
    world_dir, solution_dir = _make_world_dir(tmp_path, with_solution=True)
    assert solution_dir is not None
    (solution_dir / "gold_reply.txt").unlink()
    world = World.from_path(world_dir, solution_dir=solution_dir)
    assert world.solution is None


def test_solution_none_when_gold_export_missing(tmp_path: Path) -> None:
    world_dir, solution_dir = _make_world_dir(tmp_path, with_solution=True)
    assert solution_dir is not None
    (solution_dir / "gold_memory_export.json").unlink()
    world = World.from_path(world_dir, solution_dir=solution_dir)
    assert world.solution is None


def test_no_parent_traversal(tmp_path: Path) -> None:
    """from_path must not read files outside world_dir."""
    world_dir, _ = _make_world_dir(tmp_path)
    # Confirm loading succeeds even when called from an unrelated cwd
    world = World.from_path(world_dir.resolve())
    assert world.meta.active_character_id == "mara"


def test_identity_empty_when_character_md_missing(tmp_path: Path) -> None:
    world_dir, _ = _make_world_dir(tmp_path)
    (world_dir / "companions" / "mara" / "character.md").unlink()
    world = World.from_path(world_dir)
    assert world.characters["mara"].identity == ""
