"""Honcho peer-memory semantics for the harness (no Honcho server).

Models directional peer memory: explicit session conclusions, always-on peer
card facts, and semantic-style retrieval via token overlap. One isolated peer
pair (character observes user) per fixture character.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

TOKEN = re.compile(r"[a-z0-9']+")
MAX_PEER_CARD = 40


@dataclass
class PeerMemory:
    """Character peer's memory of the user (explicit docs + peer card)."""

    character_sheet: str = ""
    explicit: list[str] = field(default_factory=list)
    peer_card: list[str] = field(default_factory=list)
    lore: str = ""


def _overlap_score(query: str, chunk: str) -> int:
    q = set(TOKEN.findall(query.casefold()))
    c = set(TOKEN.findall(chunk.casefold()))
    return len(q & c)


def ingest_peer(
    character_sheet: str,
    session_summaries: list[str],
    lore: str = "",
) -> PeerMemory:
    explicit = [s for s in session_summaries if s.strip()]
    card = explicit[:MAX_PEER_CARD]
    return PeerMemory(
        character_sheet=character_sheet.strip(),
        explicit=explicit,
        peer_card=card,
        lore=lore.strip(),
    )


def build_context(peer: PeerMemory, query: str, top_k: int = 8) -> str:
    parts: list[str] = []
    if peer.character_sheet:
        parts.append(f"Peer representation:\n{peer.character_sheet}")
    if peer.peer_card:
        parts.append("Peer card:\n" + "\n".join(f"- {fact}" for fact in peer.peer_card))
    if peer.explicit:
        ranked = sorted(peer.explicit, key=lambda doc: _overlap_score(query, doc), reverse=True)
        hits = [doc for doc in ranked if _overlap_score(query, doc) > 0][:top_k]
        if not hits:
            hits = ranked[: min(top_k, len(ranked))]
        parts.append("Explicit conclusions:\n" + "\n".join(f"- {doc}" for doc in hits))
    if peer.lore:
        parts.append(f"Lore:\n{peer.lore}")
    return "\n\n".join(parts)


def compose_reply(peer: PeerMemory, query: str) -> str:
    body = build_context(peer, query)
    return (
        "I'm here for you as your companion. Based on what I remember:\n"
        f"{body}"
    )


def export_character(peer: PeerMemory) -> dict[str, object]:
    blob_parts = []
    if peer.character_sheet:
        blob_parts.append(peer.character_sheet)
    blob_parts.extend(peer.peer_card)
    blob_parts.extend(peer.explicit)
    if peer.lore:
        blob_parts.append(peer.lore)
    blob = "\n".join(blob_parts)
    return {
        "kinds": {
            "user_bio": [{"id": "honcho-peer", "text": blob}],
            "character_event": [],
            "relationship_phase": [],
            "lore": [],
            "session": [],
            "ooc": [],
        }
    }
