"""Letta MemFS semantics for the harness (no Letta server).

Models Letta's read policy: system/persona.md and system/human.md are always in
context; reference/ files are retrieved on demand via token overlap (no default
vector index). One isolated MemFS tree per character.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

TOKEN = re.compile(r"[a-z0-9']+")


@dataclass
class MemFS:
    """In-memory MemFS tree keyed by relative path."""

    files: dict[str, str] = field(default_factory=dict)

    def write(self, path: str, content: str) -> None:
        self.files[path] = content.strip()

    def read(self, path: str) -> str:
        return self.files.get(path, "")

    def paths(self) -> list[str]:
        return sorted(self.files)


def _overlap_score(query: str, chunk: str) -> int:
    q = set(TOKEN.findall(query.casefold()))
    c = set(TOKEN.findall(chunk.casefold()))
    return len(q & c)


def ingest_world(
    world: Path,
    character_id: str,
    *,
    attach_lore: bool,
    session_summaries: list[str],
    character_sheet: str,
) -> MemFS:
    from world_io import lore_text

    memfs = MemFS()
    if character_sheet:
        memfs.write("system/persona.md", character_sheet)

    human_lines = [f"- {summary}" for summary in session_summaries if summary.strip()]
    memfs.write("system/human.md", "\n".join(human_lines))

    for index, summary in enumerate(session_summaries):
        if summary.strip():
            memfs.write(f"reference/sessions/{index:03d}.md", summary)

    if attach_lore:
        lore = lore_text(world)
        if lore:
            memfs.write("reference/lore.md", lore)

    return memfs


def always_on_context(memfs: MemFS) -> str:
    parts: list[str] = []
    for path in ("system/persona.md", "system/human.md"):
        text = memfs.read(path)
        if text:
            parts.append(f"## {path}\n{text}")
    return "\n\n".join(parts)


def retrieve_reference(memfs: MemFS, query: str, top_k: int = 6) -> list[str]:
    candidates: list[tuple[int, str, str]] = []
    for path in memfs.paths():
        if not path.startswith("reference/"):
            continue
        text = memfs.read(path)
        if not text:
            continue
        candidates.append((_overlap_score(query, text), path, text))
    candidates.sort(key=lambda row: row[0], reverse=True)
    picked = [text for score, _path, text in candidates if score > 0][:top_k]
    if not picked and candidates:
        picked = [candidates[0][2]]
    return picked


def compose_reply(memfs: MemFS, query: str) -> str:
    system_blob = always_on_context(memfs)
    reference_chunks = retrieve_reference(memfs, query)
    reference_blob = "\n\n".join(reference_chunks)
    body = system_blob
    if reference_blob:
        body = f"{body}\n\n## reference\n{reference_blob}" if body else reference_blob
    return (
        "I'm here for you as your companion. Based on what I remember:\n"
        f"{body}"
    )


def export_character(memfs: MemFS) -> dict[str, object]:
    blob = "\n\n".join(f"### {path}\n{text}" for path in memfs.paths() for text in [memfs.read(path)] if text)
    return {
        "kinds": {
            "user_bio": [{"id": "letta-memfs", "text": blob}],
            "character_event": [],
            "relationship_phase": [],
            "lore": [],
            "session": [],
            "ooc": [],
        }
    }
