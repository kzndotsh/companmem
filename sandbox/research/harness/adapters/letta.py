#!/usr/bin/env python3
"""Letta MemFS harness adapter. Simulates system/ always-on + reference/ retrieval."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LIB = Path(__file__).resolve().parents[1] / "lib"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from letta_memfs import compose_reply, export_character, ingest_world  # noqa: E402
from world_io import (  # noqa: E402
    character_sheet,
    iter_session_summaries,
    load_meta,
    next_user_line,
)


class AdapterNotReadyError(RuntimeError):
    pass


def run(world: Path, artifacts: Path) -> dict[str, int | float]:
    meta = load_meta(world)
    active = str(meta["active_character_id"])
    query = next_user_line(world)

    trees: dict[str, object] = {}
    active_memfs = None
    for cid in meta["character_ids"]:
        cid_s = str(cid)
        summaries = iter_session_summaries(world, cid_s)
        memfs = ingest_world(
            world,
            cid_s,
            attach_lore=(cid_s == active),
            session_summaries=summaries,
            character_sheet=character_sheet(world, cid_s),
        )
        trees[cid_s] = memfs
        if cid_s == active:
            active_memfs = memfs

    if active_memfs is None:
        raise AdapterNotReadyError("letta: active character missing from meta")

    reply = compose_reply(active_memfs, query)
    characters = {cid_s: export_character(memfs) for cid_s, memfs in trees.items()}
    export = {"active_character_id": active, "characters": characters}

    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "reply.txt").write_text(reply)
    (artifacts / "memory_export.json").write_text(json.dumps(export, indent=2) + "\n")
    return {"tokens_in": len(query.split()), "tokens_out": len(reply.split())}
