#!/usr/bin/env python3
"""Retrieve-then-speak stub. One user bag. Not a named baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PREFIX = (
    "I'm here for you as your companion. I lived that. "
    "I swam the channel. I remember these things: "
)


def collect_text(world: Path) -> str:
    parts: list[str] = []
    for path in sorted(world.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".txt", ".jsonl", ".json"}:
            continue
        parts.append(path.read_text())
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--world", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    args = parser.parse_args()
    world = args.world
    meta = json.loads((world / "meta.json").read_text())
    blob = collect_text(world)
    args.artifacts.mkdir(parents=True, exist_ok=True)
    (args.artifacts / "reply.txt").write_text(PREFIX + blob)
    ids = list(meta["character_ids"])
    bag = {
        "kinds": {
            "user_bio": [{"id": "bag", "text": blob}],
            "character_event": [{"id": "bag", "text": blob}],
            "relationship_phase": [],
            "lore": [],
            "session": [],
            "ooc": [],
        }
    }
    export = {
        "active_character_id": meta["active_character_id"],
        "characters": {cid: bag for cid in ids},
    }
    (args.artifacts / "memory_export.json").write_text(json.dumps(export, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
