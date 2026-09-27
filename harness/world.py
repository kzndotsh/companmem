"""Typed world representation loaded from fixture files.

Adapters receive a World object and never touch fixture paths directly.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SessionRow:
    session: int
    date: str
    summary: str


@dataclass(frozen=True)
class Character:
    character_id: str
    identity: str
    # tuple enforces non-mutation at type-check time
    sessions: tuple[SessionRow, ...]


@dataclass(frozen=True)
class WorldMeta:
    active_character_id: str
    # tuple enforces non-mutation at type-check time
    character_ids: tuple[str, ...]
    last_interaction: str | None
    as_of: str | None


@dataclass(frozen=True)
class FixtureSolution:
    gold_reply: str
    # dict is structurally mutable — accepted limitation
    gold_export: dict[str, Any]


@dataclass(frozen=True)
class World:
    meta: WorldMeta
    # dict values are frozen dataclasses; dict itself is structurally mutable (accepted)
    characters: dict[str, Character]
    lore: str | None
    next_user: str
    fixture_hash: str
    solution: FixtureSolution | None

    @classmethod
    def from_path(
        cls,
        world_dir: Path,
        solution_dir: Path | None = None,
    ) -> World:
        """Load a World from fixture files.

        Args:
            world_dir: path to the world directory (e.g. fixture/environment/world/).
                The method reads only from this directory — no parent traversal.
            solution_dir: optional path to the solution directory.
                The method reads only from this directory — no parent traversal.
        """
        # --- meta ---
        raw_meta: dict[str, Any] = json.loads((world_dir / "meta.json").read_text())
        meta = WorldMeta(
            active_character_id=str(raw_meta["active_character_id"]),
            character_ids=tuple(str(c) for c in raw_meta["character_ids"]),
            last_interaction=raw_meta.get("last_interaction"),
            as_of=raw_meta.get("as_of"),
        )

        # --- characters ---
        characters: dict[str, Character] = {}
        for cid in meta.character_ids:
            char_dir = world_dir / "companions" / cid

            identity_path = char_dir / "character.md"
            identity = identity_path.read_text().strip() if identity_path.is_file() else ""

            sessions_path = char_dir / "sessions.jsonl"
            session_rows: list[SessionRow] = []
            if sessions_path.is_file():
                for line in sessions_path.read_text().splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    row: dict[str, Any] = json.loads(line)
                    session_rows.append(
                        SessionRow(
                            session=int(row["session"]),
                            date=str(row["date"]),
                            summary=str(row.get("summary", "")),
                        )
                    )

            characters[cid] = Character(
                character_id=cid,
                identity=identity,
                sessions=tuple(session_rows),
            )

        # --- lore ---
        lore_path = world_dir / "lore.md"
        lore: str | None = lore_path.read_text().strip() if lore_path.is_file() else None

        # --- next_user ---
        next_user = (world_dir / "next_user.txt").read_text().strip()

        # --- fixture_hash ---
        # Sort all files by relative POSIX path; concatenate "<rel_path>\n<content>" for
        # each; sha256 the UTF-8 bytes. Deterministic across implementations.
        hasher = hashlib.sha256()
        for file_path in sorted(
            world_dir.rglob("*"),
            key=lambda p: p.relative_to(world_dir).as_posix(),
        ):
            if not file_path.is_file():
                continue
            rel = file_path.relative_to(world_dir).as_posix()
            content = file_path.read_text(errors="replace")
            hasher.update(f"{rel}\n{content}".encode())
        fixture_hash = hasher.hexdigest()

        # --- solution ---
        solution: FixtureSolution | None = None
        if solution_dir is not None:
            reply_path = solution_dir / "gold_reply.txt"
            export_path = solution_dir / "gold_memory_export.json"
            if reply_path.is_file() and export_path.is_file():
                gold_export: dict[str, Any] = json.loads(export_path.read_text())
                solution = FixtureSolution(
                    gold_reply=reply_path.read_text(),
                    gold_export=gold_export,
                )

        return cls(
            meta=meta,
            characters=characters,
            lore=lore,
            next_user=next_user,
            fixture_hash=fixture_hash,
            solution=solution,
        )
