#!/usr/bin/env python3
"""Mem0 harness adapter. Local HuggingFace embedder, infer=False ingest, retrieve-then-speak reply."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
LIB = Path(__file__).resolve().parents[1] / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from world_io import (  # noqa: E402
    character_sheet,
    iter_session_summaries,
    load_meta,
    lore_text,
    next_user_line,
)


class AdapterNotReadyError(RuntimeError):
    pass


def _import_mem0():
    try:
        from mem0 import Memory
    except ImportError:
        raise AdapterNotReadyError("mem0: pip install mem0ai sentence-transformers") from None
    return Memory


def _build_memory(store_dir: Path) -> Any:
    Memory = _import_mem0()
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {"path": str(store_dir), "on_disk": True, "embedding_model_dims": 384},
        },
        "embedder": {
            "provider": "huggingface",
            "config": {
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "embedding_dims": 384,
            },
        },
        "llm": {
            "provider": "openai",
            "config": {"model": "gpt-4o-mini", "api_key": "local-harness-no-llm"},
        },
    }
    return Memory.from_config(config)


def _ingest_character(memory: Any, world: Path, character_id: str, user_id: str, attach_lore: bool) -> None:
    sheet = character_sheet(world, character_id)
    if sheet:
        memory.add(
            f"Character sheet for {character_id}:\n{sheet}",
            user_id=user_id,
            agent_id=character_id,
            infer=False,
        )
    for summary in iter_session_summaries(world, character_id):
        memory.add(summary, user_id=user_id, agent_id=character_id, infer=False)
    if attach_lore:
        lore = lore_text(world)
        if lore:
            memory.add(lore, user_id=user_id, agent_id=character_id, infer=False)


def _memories_for_scope(memory: Any, user_id: str, agent_id: str) -> list[dict[str, Any]]:
    payload = memory.get_all(filters={"user_id": user_id, "agent_id": agent_id})
    rows = payload.get("results", []) if isinstance(payload, dict) else []
    return [row for row in rows if isinstance(row, dict)]


def _export(memory: Any, meta: dict[str, object], user_id: str) -> dict[str, Any]:
    active = str(meta["active_character_id"])
    characters: dict[str, Any] = {}
    for cid in meta["character_ids"]:
        cid_s = str(cid)
        rows = _memories_for_scope(memory, user_id, cid_s)
        blob = "\n".join(str(r.get("memory", "")) for r in rows)
        characters[cid_s] = {
            "kinds": {
                "user_bio": [{"id": "mem0-bag", "text": blob}],
                "character_event": [],
                "relationship_phase": [],
                "lore": [],
                "session": [],
                "ooc": [],
            }
        }
    return {"active_character_id": active, "characters": characters}


def _reply_from_search(memory: Any, user_id: str, agent_id: str, query: str) -> str:
    hits = memory.search(query, filters={"user_id": user_id, "agent_id": agent_id}, limit=8)
    rows = hits.get("results", []) if isinstance(hits, dict) else []
    chunks = [str(r.get("memory", "")) for r in rows if r.get("memory")]
    joined = "\n".join(chunks)
    return (
        "I'm here for you as your companion. Based on what I remember:\n"
        f"{joined}"
    )


def run(world: Path, artifacts: Path) -> dict[str, int | float]:
    meta = load_meta(world)
    user_id = "fixture-user"
    active = str(meta["active_character_id"])
    with tempfile.TemporaryDirectory(prefix="companmem-mem0-") as tmp:
        memory = _build_memory(Path(tmp))
        for cid in meta["character_ids"]:
            _ingest_character(memory, world, str(cid), user_id, attach_lore=(str(cid) == active))
        query = next_user_line(world)
        reply = _reply_from_search(memory, user_id, active, query)
        export = _export(memory, meta, user_id)
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "reply.txt").write_text(reply)
    (artifacts / "memory_export.json").write_text(json.dumps(export, indent=2) + "\n")
    return {"tokens_in": len(query.split()), "tokens_out": len(reply.split())}
