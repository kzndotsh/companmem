"""Append-only atoms and projection into typed character stores."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from companmem.models import CharacterStore, MemoryItem

Writer = Literal["user", "character", "narrator", "session", "system"]


@dataclass
class Atom:
    seq: int
    writer: Writer
    text: str
    source: str
    slot: str | None = None
    compartment: str | None = None
    silent: bool = False
    speak_if: tuple[str, ...] = ()
    revoke_slot: str | None = None


@dataclass
class AtomLog:
    character_id: str
    identity: str = ""
    atoms: list[Atom] = field(default_factory=list)
    _seq: int = 0

    def push(
        self,
        writer: Writer,
        text: str,
        source: str,
        *,
        slot: str | None = None,
        compartment: str | None = None,
        silent: bool = False,
        speak_if: tuple[str, ...] = (),
        revoke_slot: str | None = None,
    ) -> None:
        self._seq += 1
        self.atoms.append(
            Atom(
                seq=self._seq,
                writer=writer,
                text=text,
                source=source,
                slot=slot,
                compartment=compartment,
                silent=silent,
                speak_if=speak_if,
                revoke_slot=revoke_slot,
            )
        )


def project(log: AtomLog) -> CharacterStore:
    store = CharacterStore(character_id=log.character_id, identity=log.identity)
    user_slots: dict[str, MemoryItem] = {}
    revoked_slots: set[str] = set()
    revoked_topics: set[str] = set()

    for atom in log.atoms:
        if atom.revoke_slot:
            revoked_slots.add(atom.revoke_slot)
            if atom.revoke_slot == "nickel-allergy":
                revoked_topics.add("nickel")
            store.add("ooc", MemoryItem(atom.revoke_slot, atom.text, atom.source))
            continue
        if atom.writer == "session":
            store.add("session", MemoryItem(f"session-{atom.seq}", atom.text, atom.source))
            continue
        if atom.writer == "system":
            if atom.slot in ("phase", "gap"):
                store.add("relationship_phase", MemoryItem(atom.slot, atom.text, atom.source))
            elif atom.slot == "eye":
                store.add("character_event", MemoryItem(atom.slot, atom.text, atom.source))
            elif atom.slot in ("lore", "flood-1847"):
                store.add("lore", MemoryItem(atom.slot, atom.text, atom.source))
            elif atom.slot == "pilot":
                store.add("character_event", MemoryItem(atom.slot, atom.text, atom.source))
            continue
        if atom.writer == "character":
            item_id = atom.slot or f"character-{atom.seq}"
            store.add("character_event", MemoryItem(item_id, atom.text, atom.source))
            continue
        if atom.writer == "narrator":
            item_id = atom.slot or f"narrator-{atom.seq}"
            store.add("ooc", MemoryItem(item_id, atom.text, atom.source))
            continue
        if atom.writer == "user":
            if atom.slot and atom.slot in revoked_slots:
                continue
            item = MemoryItem(
                atom.slot or f"user-{atom.seq}",
                atom.text,
                atom.source,
                compartment=atom.compartment,
                silent=atom.silent,
                speak_if=atom.speak_if,
            )
            if atom.slot:
                user_slots[atom.slot] = item
            else:
                store.add("user_bio", item)

    for slot, item in user_slots.items():
        if slot in revoked_slots:
            continue
        if any(topic in item.text.casefold() for topic in revoked_topics):
            continue
        store.add("user_bio", item)

    return store
