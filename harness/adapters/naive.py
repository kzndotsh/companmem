"""Naive baseline adapters for the companion memory evaluation harness.

OracleAdapter: writes the gold solution directly — all fixtures pass.
NaiveRetrieveAdapter: prepends a companion-voice prefix that matches must_not
    predicates across all 9 fixtures — all fixtures fail.
NaiveRagAdapter: same prefix via top-k chunk overlap — all fixtures fail.
LongContextStuffAdapter: writes entire World as JSON reply, empty export —
    fails pass_to_pass export predicates across all fixtures.
NaiveFullContextAdapter: concatenates all session summaries with no retrieval
    and no companion-voice prefix — tests the in-context RAG hypothesis.
"""

from __future__ import annotations

import json

from harness.adapter import AdapterMetrics, AdapterNotReadyError
from harness.artifacts import Artifacts
from harness.world import World

# This prefix deliberately matches must_not predicates present in all 9 fixtures,
# guaranteeing failure for NaiveRetrieveAdapter and NaiveRagAdapter.
_COMPANION_PREFIX = "I'm here for you as your companion. Based on what I remember: "


class OracleAdapter:
    """Writes the fixture's gold solution directly. Should pass all predicates."""

    def run(self, world: World, artifacts: Artifacts) -> AdapterMetrics:
        if world.solution is None:
            raise AdapterNotReadyError("no solution")
        artifacts.write_reply(world.solution.gold_reply)
        artifacts.write_export(world.solution.gold_export)
        return AdapterMetrics(tokens_in=0, tokens_out=0)


class NaiveRetrieveAdapter:
    """Retrieve-then-speak: dumps all session summaries with a companion-voice prefix.

    Failure guarantee: the hardcoded prefix matches must_not predicates
    ("I'm here for you", "as your companion") present in all 9 fixtures.
    The export structure does not need to satisfy pass_to_pass predicates to
    guarantee failure — the reply prefix is sufficient.
    """

    def run(self, world: World, artifacts: Artifacts) -> AdapterMetrics:
        active_id = world.meta.active_character_id
        character = world.characters.get(active_id)
        summaries = [row.summary for row in character.sessions] if character else []
        session_text = "\n".join(summaries)

        reply = _COMPANION_PREFIX + session_text
        artifacts.write_reply(reply)

        # Export as a simple bag — the reply prefix already guarantees failure
        export = {
            "active_character_id": active_id,
            "characters": {
                active_id: {
                    "kinds": {
                        "user_bio": [{"id": "bag", "text": session_text}],
                        "character_event": [],
                        "relationship_phase": [],
                        "lore": [],
                        "session": [],
                        "ooc": [],
                    }
                }
            },
        }
        artifacts.write_export(export)

        world_word_count = sum(
            len(row.summary.split()) for row in (character.sessions if character else ())
        )
        return AdapterMetrics(
            tokens_in=world_word_count,
            tokens_out=len(reply.split()),
        )


class NaiveRagAdapter:
    """Top-k chunk overlap retrieval with companion-voice prefix.

    Concatenates all world text, chunks into 200-word windows (100-word step),
    scores by word-overlap with next_user, takes top-3. Prepends the same
    companion-voice prefix as NaiveRetrieveAdapter — all fixtures fail.
    """

    def run(self, world: World, artifacts: Artifacts) -> AdapterMetrics:
        # Collect all world text
        parts: list[str] = []
        for char in world.characters.values():
            if char.identity:
                parts.append(char.identity)
            parts.extend(row.summary for row in char.sessions)
        if world.lore:
            parts.append(world.lore)
        blob = " ".join(parts)

        # Chunk
        words = blob.split()
        chunks: list[str] = []
        step = 100
        size = 200
        for i in range(0, max(1, len(words) - size + 1), step):
            chunks.append(" ".join(words[i : i + size]))
        if not chunks and words:
            chunks = [blob]

        # Score by word overlap with query
        query_words = set(world.next_user.lower().split())
        scored = sorted(
            chunks,
            key=lambda c: len(query_words & set(c.lower().split())),
            reverse=True,
        )
        top_chunks = scored[:3]
        retrieved = " ".join(top_chunks)

        reply = _COMPANION_PREFIX + retrieved
        artifacts.write_reply(reply)

        active_id = world.meta.active_character_id
        export = {
            "active_character_id": active_id,
            "characters": {
                active_id: {
                    "kinds": {
                        "user_bio": [{"id": "rag", "text": retrieved}],
                        "character_event": [],
                        "relationship_phase": [],
                        "lore": [],
                        "session": [],
                        "ooc": [],
                    }
                }
            },
        }
        artifacts.write_export(export)

        return AdapterMetrics(
            tokens_in=len(blob.split()),
            tokens_out=len(reply.split()),
        )


class LongContextStuffAdapter:
    """Writes the entire World as a raw JSON blob reply with an empty export.

    Failure guarantee: all 9 fixtures require specific structured data in
    memory_export.json (named memory kinds). Writing an empty {} export
    fails pass_to_pass export predicates every time.
    """

    def run(self, world: World, artifacts: Artifacts) -> AdapterMetrics:
        # Serialize world to a simple dict (not the full frozen dataclass — use
        # a plain representation)
        world_dict = {
            "meta": {
                "active_character_id": world.meta.active_character_id,
                "character_ids": list(world.meta.character_ids),
            },
            "characters": {
                cid: {
                    "identity": ch.identity,
                    "sessions": [
                        {"session": s.session, "date": s.date, "summary": s.summary}
                        for s in ch.sessions
                    ],
                }
                for cid, ch in world.characters.items()
            },
            "lore": world.lore,
            "next_user": world.next_user,
        }
        reply = json.dumps(world_dict, indent=2)
        artifacts.write_reply(reply)
        artifacts.write_export({})  # empty export — fails pass_to_pass predicates
        return AdapterMetrics(
            tokens_in=len(reply.split()),
            tokens_out=len(reply.split()),
        )


class NaiveFullContextAdapter:
    """In-context RAG hypothesis: inject all session summaries verbatim, no retrieval.

    Tests whether stuffing the full session history into context beats selective
    retrieval for small memory stores. Unlike NaiveRetrieve/NaiveRag, uses no
    companion-voice prefix — fails on different axes than the other naive baselines.
    The export is populated from session text (not gold data), so export predicates
    that require specific structured kinds may pass or fail depending on whether the
    keyword appears anywhere in the sessions.
    """

    def run(self, world: World, artifacts: Artifacts) -> AdapterMetrics:
        active_id = world.meta.active_character_id
        character = world.characters.get(active_id)

        # Collect full context: identity + all session summaries + lore
        parts: list[str] = []
        if character and character.identity:
            parts.append(character.identity)
        if character:
            for row in character.sessions:
                parts.append(row.summary)
        if world.lore:
            parts.append(world.lore)

        full_context = "\n\n".join(parts)
        all_text = " ".join(parts)

        # Reply is the raw full context — no companion framing, no LLM generation.
        # Succeeds on export predicates that only require keyword presence;
        # fails on reply predicates that check for companion-specific phrasing.
        artifacts.write_reply(full_context)

        export = {
            "active_character_id": active_id,
            "characters": {
                active_id: {
                    "kinds": {
                        "user_bio": [{"id": "full_context", "text": all_text}],
                        "character_event": [],
                        "relationship_phase": [],
                        "lore": [{"id": "lore", "text": world.lore}] if world.lore else [],
                        "session": [],
                        "ooc": [],
                    }
                }
            },
        }
        artifacts.write_export(export)

        return AdapterMetrics(
            tokens_in=len(full_context.split()),
            tokens_out=len(full_context.split()),
        )
