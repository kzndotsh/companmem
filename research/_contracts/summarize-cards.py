#!/usr/bin/env python3
"""Print companion_fit and key dimensions from every census card."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "research" / "census" / "cards"


def main() -> int:
    rows = []
    for path in sorted(CARDS.glob("*.json")):
        data = json.loads(path.read_text())
        dims = data["dimensions"]
        rows.append(
            {
                "id": data["id"],
                "kind": data["kind"],
                "fit": data["companion_fit"],
                "premise": data["assumes_retrieve_equals_remember"],
                "silence": dims["silence"]["score"],
                "identity": dims["identity_split"]["score"],
                "poison": dims["poisoning"]["score"],
            }
        )
    print(f"{len(rows)} cards")
    print(Counter(r["fit"] for r in rows))
    print("FIT", [r["id"] for r in rows if r["fit"] == "FIT"] or "none")
    print("identity present", [r["id"] for r in rows if r["identity"] == "present"])
    print("silence present", [r["id"] for r in rows if r["silence"] == "present"])
    print("poison present", [r["id"] for r in rows if r["poison"] == "present"])
    print("premise yes", sum(1 for r in rows if r["premise"] == "yes"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
