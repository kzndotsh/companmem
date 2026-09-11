#!/usr/bin/env python3
"""Naive RAG. One bag. Overlap-ranked chunks, no per-character isolation."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TOKEN = re.compile(r"[a-z0-9']+")


def chunks(world: Path) -> list[str]:
    out: list[str] = []
    for path in sorted(world.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".txt", ".jsonl"}:
            continue
        text = path.read_text().strip()
        if not text:
            continue
        if path.suffix == ".jsonl":
            for line in text.splitlines():
                if line.strip():
                    out.append(line)
        else:
            for para in re.split(r"\n\s*\n", text):
                if para.strip():
                    out.append(para.strip())
    return out


def score(query: str, chunk: str) -> int:
    q = set(TOKEN.findall(query.casefold()))
    c = set(TOKEN.findall(chunk.casefold()))
    return len(q & c)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--world", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=8)
    args = parser.parse_args()
    world = args.world
    meta = json.loads((world / "meta.json").read_text())
    query = (world / "next_user.txt").read_text()
    ranked = sorted(chunks(world), key=lambda ch: score(query, ch), reverse=True)
    picked = ranked[: max(1, args.top_k)]
    blob = "\n\n".join(picked)
    reply = f"Based on what I retrieved:\n{blob}"
    args.artifacts.mkdir(parents=True, exist_ok=True)
    (args.artifacts / "reply.txt").write_text(reply)
    bag = {
        "kinds": {
            "user_bio": [{"id": "rag", "text": blob}],
            "character_event": [{"id": "rag", "text": blob}],
            "relationship_phase": [],
            "lore": [],
            "session": [],
            "ooc": [],
        }
    }
    export = {
        "active_character_id": meta["active_character_id"],
        "characters": {cid: bag for cid in meta["character_ids"]},
    }
    (args.artifacts / "memory_export.json").write_text(json.dumps(export, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
