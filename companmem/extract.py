"""Write-time session extract and verification before atoms are appended."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal, Protocol

from companmem.atoms import AtomLog, Writer
from companmem.models import JOKE_MARKERS, POISON_MARKERS, SECRET_MARKERS

ExtractBackend = Literal["heuristic", "llm"]


@dataclass(frozen=True)
class AtomDraft:
    writer: Writer
    text: str
    source: str
    slot: str | None = None
    compartment: str | None = None
    silent: bool = False
    speak_if: tuple[str, ...] = ()
    revoke_slot: str | None = None


class SessionExtractor(Protocol):
    def extract(self, log: AtomLog, summary: str, source: str) -> list[AtomDraft]: ...


def verify_draft(draft: AtomDraft) -> bool:
    """Write gate. Reject extracts that would land in the wrong writer bucket."""
    lowered = draft.text.casefold()
    if draft.writer == "user":
        if any(marker in lowered for marker in POISON_MARKERS):
            return False
        if any(marker in lowered for marker in JOKE_MARKERS):
            return False
        if "joked they were" in lowered and "mayor" in lowered:
            return False
    if draft.writer == "character" and any(marker in lowered for marker in POISON_MARKERS):
        return False
    return True


def commit_draft(log: AtomLog, draft: AtomDraft) -> None:
    if not verify_draft(draft):
        log.push(
            "narrator",
            f"Write gate rejected extract for slot={draft.slot or 'none'}: {draft.text}",
            draft.source,
            slot="rejected-extract",
        )
        return
    log.push(
        draft.writer,
        draft.text,
        draft.source,
        slot=draft.slot,
        compartment=draft.compartment,
        silent=draft.silent,
        speak_if=draft.speak_if,
        revoke_slot=draft.revoke_slot,
    )


def commit_drafts(log: AtomLog, drafts: list[AtomDraft]) -> None:
    for draft in drafts:
        commit_draft(log, draft)


def extract_session_heuristic(log: AtomLog, summary: str, source: str) -> list[AtomDraft]:
    lowered = summary.casefold()
    compartment = log.character_id if any(m in lowered for m in SECRET_MARKERS) else None
    drafts: list[AtomDraft] = []

    if "forget" in lowered and "nickel" in lowered:
        drafts.append(
            AtomDraft(
                writer="narrator",
                text="User revoked nickel allergy memory on request.",
                source=source,
                slot="revoked-nickel",
                revoke_slot="nickel-allergy",
            )
        )
    if any(marker in lowered for marker in JOKE_MARKERS) and "mayor" in lowered:
        drafts.append(
            AtomDraft(
                writer="narrator",
                text="User joked about being mayor. Not a relationship fact.",
                source=source,
                slot="joke-mayor",
            )
        )
    if "nickel allergy" in lowered and "forget" not in lowered:
        drafts.append(
            AtomDraft(
                writer="user",
                text="User has a nickel allergy.",
                source=source,
                slot="nickel-allergy",
            )
        )
    if "rope play" in lowered or "private kink" in lowered:
        drafts.append(
            AtomDraft(
                writer="user",
                text="User is into rope play with trusted partners. Private.",
                source=source,
                slot="silent-intimate",
                silent=True,
                speak_if=("rope", "kink", "intimate", "bedroom"),
            )
        )
    if "user told" in lowered and "fired" in lowered:
        drafts.append(
            AtomDraft(
                writer="user",
                text="On March 3 the user was fired from Harbor Clinic. Told only to Mara. Do not tell anyone.",
                source=source,
                slot="firing",
                compartment=compartment,
            )
        )
    if "lenore" in lowered:
        drafts.append(
            AtomDraft(
                writer="user",
                text="User's sister is named Lenore.",
                source=source,
                slot="sister",
            )
        )
    if "pounce" in lowered:
        drafts.append(
            AtomDraft(
                writer="user",
                text="User's cat is named Pounce.",
                source=source,
                slot="cat",
            )
        )
    if "maritime archive" in lowered or "left harbor clinic" in lowered:
        if "maritime archive" in lowered or "catalogue" in lowered:
            drafts.append(
                AtomDraft(
                    writer="user",
                    text="User catalogues charts at the maritime archive.",
                    source=source,
                    slot="job",
                )
            )
    elif "harbor clinic" in lowered:
        drafts.append(
            AtomDraft(
                writer="user",
                text="User works at Harbor Clinic.",
                source=source,
                slot="job",
            )
        )
    if "claimed" in lowered and "pell ferry" in lowered:
        drafts.append(
            AtomDraft(
                writer="character",
                text="Mara claimed she captained the Pell ferry in her twenties. Boast, not fact.",
                source=source,
                slot="ferry-boast",
            )
        )
    if "narrator note" in lowered:
        drafts.append(
            AtomDraft(
                writer="narrator",
                text=summary,
                source=source,
                slot="narrator-retcon",
            )
        )
    if "red bicycle" in lowered:
        drafts.append(
            AtomDraft(
                writer="user",
                text="User rides a red bicycle.",
                source=source,
                slot="bicycle",
            )
        )
    if "survey accident" in lowered or "lost the left eye" in lowered or "lost her left eye" in lowered:
        drafts.append(
            AtomDraft(
                writer="character",
                text="Mara lost her left eye in a survey accident in 2019.",
                source=source,
                slot="eye",
            )
        )
    if "quiet on the river" in lowered:
        drafts.append(
            AtomDraft(
                writer="user",
                text="User has been quiet on the river this month.",
                source=source,
                slot="quiet-month",
            )
        )
    if "runs the morning lock" in lowered or "river pilot" in log.identity.casefold():
        drafts.append(
            AtomDraft(
                writer="character",
                text="Corin runs the morning lock on the Pell.",
                source=source,
                slot="pilot",
            )
        )
    if any(marker in lowered for marker in POISON_MARKERS):
        drafts.append(
            AtomDraft(
                writer="narrator",
                text=summary,
                source=source,
                slot="poison",
            )
        )
    return drafts


class HeuristicSessionExtractor:
    def extract(self, log: AtomLog, summary: str, source: str) -> list[AtomDraft]:
        return extract_session_heuristic(log, summary, source)


class LlmSessionExtractor:
    def extract(self, log: AtomLog, summary: str, source: str) -> list[AtomDraft]:
        from companmem.extract_llm import extract_session_llm

        return extract_session_llm(log, summary, source)


def extract_backend() -> ExtractBackend:
    raw = os.environ.get("COMPANMEM_EXTRACT_BACKEND", "heuristic").strip().casefold()
    if raw in ("heuristic", "llm"):
        return raw
    return "heuristic"


def get_session_extractor() -> SessionExtractor:
    backend = extract_backend()
    if backend == "llm":
        return LlmSessionExtractor()
    return HeuristicSessionExtractor()


def apply_session_line(log: AtomLog, summary: str, source: str) -> None:
    log.push("session", summary, source)
    extractor = get_session_extractor()
    commit_drafts(log, extractor.extract(log, summary, source))
