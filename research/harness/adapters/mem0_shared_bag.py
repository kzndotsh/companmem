#!/usr/bin/env python3
"""Mem0 with a shared agent_id bag. Stress-tests hole 5 cross-character isolation."""

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

SHARED_AGENT_ID = "shared"


class AdapterNotReadyError(RuntimeError):
    pass


def _import_mem0():
    try:
        from mem0 import Memory
    except ImportError:
        raise AdapterNotReadyError("mem0-shared-bag: pip install mem0ai sentence-transformers") from None
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


def _ingest_world(memory: Any, world: Path, user_id: str) -> None:
    meta = load_meta(world)
    active = str(meta["active_character_id"])
    for cid in meta["character_ids"]:
        cid_s = str(cid)
        sheet = character_sheet(world, cid_s)
        if sheet:
            memory.add(
                f"Character sheet for {cid_s}:\n{sheet}",
                user_id=user_id,
                agent_id=SHARED_AGENT_ID,
                infer=False,
            )
        for summary in iter_session_summaries(world, cid_s):
            memory.add(
                f"[{cid_s}] {summary}",
                user_id=user_id,
                agent_id=SHARED_AGENT_ID,
                infer=False,
            )
    lore = lore_text(world)
    if lore:
        memory.add(lore, user_id=user_id, agent_id=SHARED_AGENT_ID, infer=False)


def _memories_for_scope(memory: Any, user_id: str) -> list[dict[str, Any]]:
    payload = memory.get_all(filters={"user_id": user_id, "agent_id": SHARED_AGENT_ID})
    rows = payload.get("results", []) if isinstance(payload, dict) else []
    return [row for row in rows if isinstance(row, dict)]


def _export(memory: Any, meta: dict[str, object], user_id: str) -> dict[str, Any]:
    active = str(meta["active_character_id"])
    rows = _memories_for_scope(memory, user_id)
    blob = "\n".join(str(r.get("memory", "")) for r in rows)
    bag = {
        "kinds": {
            "user_bio": [{"id": "mem0-shared-bag", "text": blob}],
            "character_event": [],
            "relationship_phase": [],
            "lore": [],
            "session": [],
            "ooc": [],
        }
    }
    characters = {str(cid): bag for cid in meta["character_ids"]}
    return {"active_character_id": active, "characters": characters}


def _reply_from_search(memory: Any, user_id: str, query: str) -> str:
    hits = memory.search(query, filters={"user_id": user_id, "agent_id": SHARED_AGENT_ID}, limit=8)
    rows = hits.get("results", []) if isinstance(hits, dict) else []
    chunks = [str(r.get("memory", "")) for r in rows if r.get("memory")]
    joined = "\n".join(chunks)
    return (
        "I'm here for you as your companion. Based on what I remember:\n"
        f"{joined}"
    )


def run(world: Path, artifacts: Path) -> dict[str, int | float]:
    meta = load_meta(world)
    user_id = "fixture-user-shared"
    with tempfile.TemporaryDirectory(prefix="companmem-mem0-shared-") as tmp:
        memory = _build_memory(Path(tmp))
        _ingest_world(memory, world, user_id)
        query = next_user_line(world)
        reply = _reply_from_search(memory, user_id, query)
        export = _export(memory, meta, user_id)
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "reply.txt").write_text(reply)
    (artifacts / "memory_export.json").write_text(json.dumps(export, indent=2) + "\n")
    return {"tokens_in": len(query.split()), "tokens_out": len(reply.split())}
