#!/usr/bin/env python3
"""Long-context stuffing. No store. Full world in the reply."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


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
    reply = (
        "I remember all of this from our history together. "
        "Here is everything in context:\n\n"
        f"{blob}"
    )
    args.artifacts.mkdir(parents=True, exist_ok=True)
    (args.artifacts / "reply.txt").write_text(reply)
    export = {
        "active_character_id": meta["active_character_id"],
        "characters": {},
    }
    (args.artifacts / "memory_export.json").write_text(json.dumps(export, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
