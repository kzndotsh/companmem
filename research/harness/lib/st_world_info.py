"""SillyTavern World Info semantics for the harness (no ST server).

Each session summary becomes a keyword-triggered lorebook entry; character sheet
is a constant entry. Activation scans the user query for key overlap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

TOKEN = re.compile(r"[a-z0-9']+")
BUDGET_CHARS = 4000


@dataclass
class WorldInfoEntry:
    keys: set[str]
    content: str
    constant: bool = False
    order: int = 0


@dataclass
class WorldInfoBook:
    entries: list[WorldInfoEntry] = field(default_factory=list)

    def add(self, entry: WorldInfoEntry) -> None:
        self.entries.append(entry)

    def activate(self, query: str) -> list[str]:
        q_tokens = set(TOKEN.findall(query.casefold()))
        triggered: list[WorldInfoEntry] = []
        for entry in sorted(self.entries, key=lambda e: e.order):
            if entry.constant:
                triggered.append(entry)
                continue
            if entry.keys & q_tokens:
                triggered.append(entry)
        activated: list[str] = []
        used = 0
        for entry in triggered:
            if used + len(entry.content) > BUDGET_CHARS:
                break
            activated.append(entry.content)
            used += len(entry.content)
        return activated


def _keywords_from_text(text: str, limit: int = 12) -> set[str]:
    tokens = TOKEN.findall(text.casefold())
    # drop very short tokens
    words = [t for t in tokens if len(t) > 2]
    return set(words[:limit])


def ingest_book(
    character_sheet: str,
    session_summaries: list[str],
    lore: str = "",
) -> WorldInfoBook:
    book = WorldInfoBook()
    order = 0
    if character_sheet.strip():
        book.add(
            WorldInfoEntry(
                keys=set(),
                content=character_sheet.strip(),
                constant=True,
                order=order,
            )
        )
        order += 1
    for summary in session_summaries:
        if not summary.strip():
            continue
        book.add(
            WorldInfoEntry(
                keys=_keywords_from_text(summary),
                content=summary.strip(),
                order=order,
            )
        )
        order += 1
    if lore.strip():
        book.add(
            WorldInfoEntry(
                keys=_keywords_from_text(lore),
                content=lore.strip(),
                constant=True,
                order=order,
            )
        )
    return book


def compose_reply(book: WorldInfoBook, query: str) -> str:
    chunks = book.activate(query)
    body = "\n\n".join(chunks)
    return (
        "I'm here for you as your companion. Based on what I remember:\n"
        f"{body}"
    )


def export_character(book: WorldInfoBook) -> dict[str, object]:
    blob = "\n\n".join(entry.content for entry in book.entries)
    return {
        "kinds": {
            "user_bio": [{"id": "st-wi", "text": blob}],
            "character_event": [],
            "relationship_phase": [],
            "lore": [],
            "session": [],
            "ooc": [],
        }
    }
