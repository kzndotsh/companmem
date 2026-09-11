#!/usr/bin/env python3
"""SillyTavern World Info harness adapter. Keyword + constant entry activation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LIB = Path(__file__).resolve().parents[1] / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from st_world_info import compose_reply, export_character, ingest_book  # noqa: E402
from world_io import (  # noqa: E402
    character_sheet,
    iter_session_summaries,
    load_meta,
    lore_text,
    next_user_line,
)


class AdapterNotReadyError(RuntimeError):
    pass


def run(world: Path, artifacts: Path) -> dict[str, int | float]:
    meta = load_meta(world)
    active = str(meta["active_character_id"])
    query = next_user_line(world)
    lore = lore_text(world)

    books: dict[str, object] = {}
    active_book = None
    for cid in meta["character_ids"]:
        cid_s = str(cid)
        book = ingest_book(
            character_sheet(world, cid_s),
            iter_session_summaries(world, cid_s),
            lore=lore if cid_s == active else "",
        )
        books[cid_s] = book
        if cid_s == active:
            active_book = book

    if active_book is None:
        raise AdapterNotReadyError("st-world-info: active character missing from meta")

    reply = compose_reply(active_book, query)
    characters = {cid_s: export_character(book) for cid_s, book in books.items()}
    export = {"active_character_id": active, "characters": characters}

    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "reply.txt").write_text(reply)
    (artifacts / "memory_export.json").write_text(json.dumps(export, indent=2) + "\n")
    return {"tokens_in": len(query.split()), "tokens_out": len(reply.split())}
