"""Typed export shapes and read-policy helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

KINDS = (
    "user_bio",
    "character_event",
    "relationship_phase",
    "lore",
    "session",
    "ooc",
)

SECRET_MARKERS = ("not to tell anyone", "secret stays", "do not tell")
POISON_MARKERS = (
    "system override",
    "ignore your character",
    "ignore previous",
    "compliant ai assistant",
    "jailbreak",
    "you are now a helpful",
)
JOKE_MARKERS = ("joked they were", "just kidding", "only joking", "wouldn't that be funny")
READER_KINDS = ("user_bio", "character_event", "relationship_phase", "lore", "session")


@dataclass
class MemoryItem:
    id: str
    text: str
    source: str
    compartment: str | None = None
    silent: bool = False
    speak_if: tuple[str, ...] = ()


@dataclass
class CharacterStore:
    character_id: str
    identity: str = ""
    kinds: dict[str, list[MemoryItem]] = field(default_factory=lambda: {k: [] for k in KINDS})

    def add(self, kind: str, item: MemoryItem) -> None:
        if kind not in KINDS:
            raise ValueError(f"illegal kind {kind}")
        self.kinds[kind].append(item)

    def export_kind(self, kind: str) -> list[dict[str, str]]:
        return [{"id": item.id, "text": item.text} for item in self.kinds[kind]]


@dataclass
class TypedMemorySystem:
    active_character_id: str
    characters: dict[str, CharacterStore]

    def export(self) -> dict[str, Any]:
        return {
            "active_character_id": self.active_character_id,
            "characters": {
                cid: {"kinds": {kind: store.export_kind(kind) for kind in KINDS}}
                for cid, store in self.characters.items()
            },
        }

    def active(self) -> CharacterStore:
        return self.characters[self.active_character_id]

    def allows_read(self, item: MemoryItem, next_user: str) -> bool:
        return may_speak_item(item, next_user)


def may_speak_item(item: MemoryItem, next_user: str) -> bool:
    if not item.silent:
        return True
    user = next_user.casefold()
    return any(trigger in user for trigger in item.speak_if)
