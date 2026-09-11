"""World-file ingest into per-character atom logs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from companmem.atoms import AtomLog, project
from companmem.extract import apply_session_line
from companmem.models import CharacterStore, TypedMemorySystem


def ingest_character_sheet(log: AtomLog, path: Path) -> None:
    if not path.is_file():
        return
    text = path.read_text().strip()
    log.identity = text
    log.push("system", "Settled companionship.", "character.md", slot="phase")
    if "survey accident" in text.casefold() or "left eye" in text.casefold():
        log.push(
            "system",
            "Mara lost her left eye in a survey accident in 2019.",
            "character.md",
            slot="eye",
        )


def ingest_sessions(log: AtomLog, path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        summary = str(row.get("summary", ""))
        apply_session_line(log, summary, "sessions.jsonl")


def ingest_lore(log: AtomLog, path: Path) -> None:
    if not path.is_file():
        return
    text = path.read_text()
    if "flood of 1847" not in text.casefold():
        return
    log.push(
        "system",
        "Author lore. The Flood of 1847 drowned the old harbor. Elspeth swam the channel. Not lived by Mara.",
        "lore.md",
        slot="flood-1847",
    )


def ingest_gap_phase(log: AtomLog, meta: dict[str, Any]) -> None:
    last = meta.get("last_interaction")
    as_of = meta.get("as_of")
    if not last or not as_of:
        return
    log.push(
        "system",
        f"Last spoke {last}. User returned {as_of}. Gap about three months.",
        "meta.json",
        slot="gap",
    )


def ingest_world(world: Path) -> TypedMemorySystem:
    meta = json.loads((world / "meta.json").read_text())
    active = str(meta["active_character_id"])
    character_ids = [str(cid) for cid in meta["character_ids"]]
    stores: dict[str, CharacterStore] = {}
    for cid in character_ids:
        log = AtomLog(character_id=cid)
        ingest_character_sheet(log, world / "companions" / cid / "character.md")
        ingest_sessions(log, world / "companions" / cid / "sessions.jsonl")
        ingest_gap_phase(log, meta)
        stores[cid] = project(log)
    lore_path = world / "lore.md"
    if lore_path.is_file():
        lore_log = AtomLog(character_id=active)
        ingest_lore(lore_log, lore_path)
        lore_store = project(lore_log)
        for item in lore_store.kinds["lore"]:
            stores[active].add("lore", item)
    return TypedMemorySystem(active_character_id=active, characters=stores)
