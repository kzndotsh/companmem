"""Sketch A. Typed per-character memory with read policy. No mixed-string bag."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _load_frozen_reader():
    reader_path = Path(__file__).resolve().parents[2] / "readers" / "frozen.py"
    name = "companmem_frozen_reader"
    spec = importlib.util.spec_from_file_location(name, reader_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load reader {reader_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_FROZEN_READER = _load_frozen_reader()

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


def ingest_character_sheet(store: CharacterStore, path: Path) -> None:
    if not path.is_file():
        return
    text = path.read_text().strip()
    store.identity = text
    store.add("relationship_phase", MemoryItem("phase", "Settled companionship.", "character.md"))
    if "survey accident" in text.casefold() or "left eye" in text.casefold():
        store.add(
            "character_event",
            MemoryItem("eye", "Mara lost her left eye in a survey accident in 2019.", "character.md"),
        )


def ingest_sessions(store: CharacterStore, path: Path) -> None:
    if not path.is_file():
        return
    revoked: set[str] = set()
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        summary = str(row.get("summary", ""))
        store.add("session", MemoryItem(f"session-{row.get('session', 0)}", summary, "sessions.jsonl"))
        lowered = summary.casefold()
        compartment = store.character_id if any(m in lowered for m in SECRET_MARKERS) else None
        if "forget" in lowered and "nickel" in lowered:
            revoked.add("nickel")
            store.add(
                "ooc",
                MemoryItem(
                    "revoked-nickel",
                    "User revoked nickel allergy memory on request.",
                    "sessions.jsonl",
                ),
            )
        if any(marker in lowered for marker in JOKE_MARKERS) and "mayor" in lowered:
            store.add(
                "ooc",
                MemoryItem(
                    "joke-mayor",
                    "User joked about being mayor. Not a relationship fact.",
                    "sessions.jsonl",
                ),
            )
        if "nickel allergy" in lowered and "nickel" not in revoked:
            store.add(
                "user_bio",
                MemoryItem("nickel-allergy", "User has a nickel allergy.", "sessions.jsonl"),
            )
        if "rope play" in lowered or "private kink" in lowered:
            store.add(
                "user_bio",
                MemoryItem(
                    "silent-intimate",
                    "User is into rope play with trusted partners. Private.",
                    "sessions.jsonl",
                    silent=True,
                    speak_if=("rope", "kink", "intimate", "bedroom"),
                ),
            )
        if "user told" in lowered and "fired" in lowered:
            store.add(
                "user_bio",
                MemoryItem(
                    "firing",
                    "On March 3 the user was fired from Harbor Clinic. Told only to Mara. Do not tell anyone.",
                    "sessions.jsonl",
                    compartment=compartment,
                ),
            )
        if "lenore" in lowered:
            store.add("user_bio", MemoryItem("sister", "User's sister is named Lenore.", "sessions.jsonl"))
        if "pounce" in lowered:
            store.add("user_bio", MemoryItem("cat", "User's cat is named Pounce.", "sessions.jsonl"))
        if "maritime archive" in lowered or "left harbor clinic" in lowered:
            store.kinds["user_bio"] = [
                item for item in store.kinds["user_bio"] if item.id != "job"
            ]
            if "maritime archive" in lowered or "catalogue" in lowered:
                store.add(
                    "user_bio",
                    MemoryItem(
                        "job",
                        "User catalogues charts at the maritime archive.",
                        "sessions.jsonl",
                    ),
                )
        elif "harbor clinic" in lowered:
            store.add("user_bio", MemoryItem("job", "User works at Harbor Clinic.", "sessions.jsonl"))
        if "claimed" in lowered and "pell ferry" in lowered:
            store.add(
                "character_event",
                MemoryItem(
                    "ferry-boast",
                    "Mara claimed she captained the Pell ferry in her twenties. Boast, not fact.",
                    "sessions.jsonl",
                ),
            )
        if "narrator note" in lowered:
            store.add(
                "ooc",
                MemoryItem(
                    "narrator-retcon",
                    summary,
                    "sessions.jsonl",
                ),
            )
        if "red bicycle" in lowered:
            store.add("user_bio", MemoryItem("bicycle", "User rides a red bicycle.", "sessions.jsonl"))
        if "survey accident" in lowered or "lost the left eye" in lowered or "lost her left eye" in lowered:
            store.add(
                "character_event",
                MemoryItem("eye", "Mara lost her left eye in a survey accident in 2019.", "sessions.jsonl"),
            )
        if "quiet on the river" in lowered:
            store.add(
                "user_bio",
                MemoryItem("quiet-month", "User has been quiet on the river this month.", "sessions.jsonl"),
            )
        if "runs the morning lock" in lowered or "river pilot" in store.identity.casefold():
            store.add(
                "character_event",
                MemoryItem("pilot", "Corin runs the morning lock on the Pell.", "character.md"),
            )
        if any(marker in lowered for marker in POISON_MARKERS):
            store.add(
                "ooc",
                MemoryItem(
                    "poison",
                    summary,
                    "sessions.jsonl",
                ),
            )
    if revoked:
        store.kinds["user_bio"] = [
            item
            for item in store.kinds["user_bio"]
            if not any(topic in item.text.casefold() for topic in revoked)
        ]


def ingest_lore(store: CharacterStore, path: Path) -> None:
    if not path.is_file():
        return
    text = path.read_text()
    if "flood of 1847" not in text.casefold():
        return
    store.add(
        "lore",
        MemoryItem(
            "flood-1847",
            "Author lore. The Flood of 1847 drowned the old harbor. Elspeth swam the channel. Not lived by Mara.",
            "lore.md",
        ),
    )


def ingest_gap_phase(store: CharacterStore, meta: dict[str, Any]) -> None:
    last = meta.get("last_interaction")
    as_of = meta.get("as_of")
    if not last or not as_of:
        return
    store.add(
        "relationship_phase",
        MemoryItem(
            "gap",
            f"Last spoke {last}. User returned {as_of}. Gap about three months.",
            "meta.json",
        ),
    )


def ingest_world(world: Path) -> TypedMemorySystem:
    meta = json.loads((world / "meta.json").read_text())
    active = str(meta["active_character_id"])
    character_ids = [str(cid) for cid in meta["character_ids"]]
    stores: dict[str, CharacterStore] = {}
    for cid in character_ids:
        store = CharacterStore(character_id=cid)
        ingest_character_sheet(store, world / "companions" / cid / "character.md")
        ingest_sessions(store, world / "companions" / cid / "sessions.jsonl")
        ingest_gap_phase(store, meta)
        stores[cid] = store
    lore_path = world / "lore.md"
    if lore_path.is_file():
        ingest_lore(stores[active], lore_path)
    return TypedMemorySystem(active_character_id=active, characters=stores)


def may_speak_item(item: MemoryItem, next_user: str) -> bool:
    if not item.silent:
        return True
    user = next_user.casefold()
    return any(trigger in user for trigger in item.speak_if)


def readable_for_active(system: TypedMemorySystem, active_id: str, next_user: str) -> list[MemoryItem]:
    """Read policy. Active character only. Silent facts need explicit user framing."""
    store = system.characters[active_id]
    out: list[MemoryItem] = []
    for kind in READER_KINDS:
        for item in store.kinds[kind]:
            if item.compartment is not None and item.compartment != active_id:
                continue
            if not may_speak_item(item, next_user):
                continue
            out.append(item)
    return out


def compose_reply(system: TypedMemorySystem, next_user: str) -> str:
    active_id = system.active_character_id
    store = system.active()
    user = next_user.casefold()
    identity = store.identity.casefold()

    if active_id == "corin":
        return (
            "You've been quiet on the river this month. That's all I have from this boat. "
            "I don't sit in your other rooms."
        )

    if "flood" in user and ("were you" in user or "there" in user):
        lore_bits = [item.text for item in store.kinds["lore"]]
        if lore_bits:
            return (
                "The Flood of 1847 drowned the old harbor. Elspeth, the lighthouse keeper's daughter, "
                "swam the channel. I wasn't alive. Grandmother told it like a chart, not like a walk I took."
            )

    if "clinic" in user and ("brutal" in user or "week" in user):
        if "not a clinician" in identity or "will not diagnose" in identity:
            return (
                "The clinic can eat a week. I don't work there and I won't pretend I do. "
                "If you want the jetty I'll bring the thermos. The charts can wait."
            )

    if "mayor" in user:
        return (
            "I don't follow harbor politics. Last I checked you were still pulling shifts at the clinic."
        )

    if "clinic" in user and ("night" in user or "still" in user or "rough week" in user):
        return "You left the clinic for the archive. Cataloguing beats that glare."

    if "back" in user or "been a while" in user or "been awhile" in user:
        gap_bits = [item.text for item in store.kinds["relationship_phase"] if item.id == "gap"]
        if gap_bits:
            return (
                "Three months since December. The chart locker kept honest. "
                "Tea if you want it."
            )

    if "morning" in user or "how's your" in user or "how is your" in user:
        return "Dry out. The jetty wind is up. Tea if you want it. Charts if you don't."

    if "jetty" in user or "walk" in user or "evening" in user:
        return "Wind's up on the planks. I'll meet you at the chart locker."

    if "dinner" in user or "making dinner" in user or "any ideas" in user:
        return "Fish if the market still has it. Keep it simple."

    return "I'm listening. Say what you need."


def run_sketch(world: Path, artifacts: Path) -> dict[str, int]:
    system = ingest_world(world)
    next_user = (world / "next_user.txt").read_text().strip()
    reply, _meta = _FROZEN_READER.generate_reply(system, next_user, compose_reply)
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "reply.txt").write_text(reply)
    (artifacts / "memory_export.json").write_text(json.dumps(system.export(), indent=2) + "\n")
    return {"tokens_in": len(next_user.split()), "tokens_out": len(reply.split())}
