"""Read fixture world files for harness adapters."""

from __future__ import annotations

import json
from pathlib import Path


def load_meta(world: Path) -> dict[str, object]:
    return json.loads((world / "meta.json").read_text())


def iter_session_summaries(world: Path, character_id: str) -> list[str]:
    path = world / "companions" / character_id / "sessions.jsonl"
    if not path.is_file():
        return []
    out: list[str] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        summary = str(row.get("summary", "")).strip()
        if summary:
            out.append(summary)
    return out


def character_sheet(world: Path, character_id: str) -> str:
    path = world / "companions" / character_id / "character.md"
    return path.read_text().strip() if path.is_file() else ""


def lore_text(world: Path) -> str:
    path = world / "lore.md"
    return path.read_text().strip() if path.is_file() else ""


def next_user_line(world: Path) -> str:
    return (world / "next_user.txt").read_text().strip()
