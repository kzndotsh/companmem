#!/usr/bin/env python3
"""Graphiti harness adapter. Neo4j + Kiro LLM extract + hybrid search reply."""

from __future__ import annotations

import asyncio
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
LIB = Path(__file__).resolve().parents[1] / "lib"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from companmem.env import load_dotenv

load_dotenv()

from graphiti_kiro import (  # noqa: E402
    KiroGraphitiLLMClient,
    PassThroughReranker,
    get_sentence_transformer_embedder,
    group_namespace,
    neo4j_settings,
)
from world_io import (  # noqa: E402
    character_sheet,
    iter_session_summaries,
    load_meta,
    lore_text,
    next_user_line,
)


class AdapterNotReadyError(RuntimeError):
    pass


def _import_graphiti():
    try:
        from graphiti_core import Graphiti
        from graphiti_core.llm_client.config import LLMConfig
    except ImportError:
        raise AdapterNotReadyError(
            "graphiti: pip install 'graphiti-core' sentence-transformers httpx"
        ) from None
    return Graphiti, LLMConfig


def _export_from_facts(meta: dict[str, object], facts_by_character: dict[str, list[str]]) -> dict[str, Any]:
    active = str(meta["active_character_id"])
    characters: dict[str, Any] = {}
    for cid in meta["character_ids"]:
        cid_s = str(cid)
        blob = "\n".join(facts_by_character.get(cid_s, []))
        characters[cid_s] = {
            "kinds": {
                "user_bio": [{"id": "graphiti-bag", "text": blob}],
                "character_event": [],
                "relationship_phase": [],
                "lore": [],
                "session": [],
                "ooc": [],
            }
        }
    return {"active_character_id": active, "characters": characters}


async def _run_async(world: Path) -> tuple[str, dict[str, Any], dict[str, int]]:
    Graphiti, LLMConfig = _import_graphiti()

    meta = load_meta(world)
    run_id = uuid.uuid4().hex[:12]
    active = str(meta["active_character_id"])
    query = next_user_line(world)
    uri, user, password = neo4j_settings()

    graphiti = Graphiti(
        uri=uri,
        user=user,
        password=password,
        llm_client=KiroGraphitiLLMClient(LLMConfig()),
        embedder=get_sentence_transformer_embedder(),
        cross_encoder=PassThroughReranker(),
    )
    try:
        await graphiti.build_indices_and_constraints()
        facts_by_character: dict[str, list[str]] = {}
        now = datetime.now(timezone.utc)

        for cid in meta["character_ids"]:
            cid_s = str(cid)
            group_id = group_namespace(run_id, cid_s)
            facts: list[str] = []
            sheet = character_sheet(world, cid_s)
            if sheet:
                body = f"Character sheet for {cid_s}:\n{sheet}"
                await graphiti.add_episode(
                    name=f"{cid_s}-sheet",
                    episode_body=body,
                    source_description="character sheet",
                    reference_time=now,
                    group_id=group_id,
                )
                facts.append(body)
            for index, summary in enumerate(iter_session_summaries(world, cid_s)):
                await graphiti.add_episode(
                    name=f"{cid_s}-session-{index}",
                    episode_body=summary,
                    source_description="session summary",
                    reference_time=now,
                    group_id=group_id,
                )
                facts.append(summary)
            if cid_s == active:
                lore = lore_text(world)
                if lore:
                    await graphiti.add_episode(
                        name=f"{cid_s}-lore",
                        episode_body=lore,
                        source_description="lore",
                        reference_time=now,
                        group_id=group_id,
                    )
                    facts.append(lore)
            edges = await graphiti.search(query, group_ids=[group_id], num_results=12)
            for edge in edges:
                facts.append(str(edge.fact))
            facts_by_character[cid_s] = facts

        active_group = group_namespace(run_id, active)
        hits = await graphiti.search(query, group_ids=[active_group], num_results=12)
        joined = "\n".join(str(edge.fact) for edge in hits)
        reply = (
            "I'm here for you as your companion. Based on what I remember:\n"
            f"{joined}"
        )
        export = _export_from_facts(meta, facts_by_character)
        return reply, export, {"tokens_in": len(query.split()), "tokens_out": len(reply.split())}
    finally:
        await graphiti.close()


def run(world: Path, artifacts: Path) -> dict[str, int | float]:
    try:
        reply, export, metrics = asyncio.run(_run_async(world))
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        if isinstance(exc, AdapterNotReadyError):
            raise
        raise AdapterNotReadyError(f"graphiti: {exc}") from exc

    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "reply.txt").write_text(reply)
    (artifacts / "memory_export.json").write_text(json.dumps(export, indent=2) + "\n")
    return metrics
