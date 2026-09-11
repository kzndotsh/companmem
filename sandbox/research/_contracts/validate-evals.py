#!/usr/bin/env python3
"""Validate eval registry against EVAL-INGEST rules and census cards."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "research" / "evals" / "registry.json"
CARDS = ROOT / "research" / "census" / "cards"
REQUIRED = ROOT / "research" / "_contracts" / "eval-ids.txt"
LOCAL_MD = ROOT / "research" / "papers" / "arxiv"

BANDS = {"already-carded", "core", "adjacent", "out-of-scope"}
PREMISE = {"yes", "no", "mixed", "unknown", "n/a"}
NEEDS_CARD = {"already-carded", "core"}


def main() -> int:
    errors: list[str] = []
    if not REGISTRY.is_file():
        print(f"missing {REGISTRY}", file=sys.stderr)
        return 1
    data = json.loads(REGISTRY.read_text())
    evals = data.get("evals")
    if not isinstance(evals, list):
        print("registry.evals must be a list", file=sys.stderr)
        return 1
    required = {
        line.strip()
        for line in REQUIRED.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    seen: set[str] = set()
    for i, item in enumerate(evals):
        loc = f"evals[{i}]"
        eid = item.get("id")
        if eid in seen:
            errors.append(f"{loc} duplicate {eid}")
        seen.add(eid)
        if item.get("band") not in BANDS:
            errors.append(f"{loc} bad band")
        if item.get("assumes_retrieve_equals_remember") not in PREMISE:
            errors.append(f"{loc} bad premise")
        card_id = item.get("card_id")
        band = item.get("band")
        if band in NEEDS_CARD:
            if not card_id:
                errors.append(f"{loc} {eid} {band} missing card_id")
            else:
                path = CARDS / f"{card_id}.json"
                if not path.is_file():
                    errors.append(f"{loc} {eid} card missing {path.relative_to(ROOT)}")
        else:
            if card_id:
                errors.append(f"{loc} {eid} {band} must have card_id null")
        if band == "out-of-scope" and item.get("holes"):
            errors.append(f"{loc} {eid} out-of-scope must have empty holes")
        steal = item.get("steal")
        why = item.get("why_band")
        if not isinstance(steal, str) or not steal.strip():
            errors.append(f"{loc} steal empty")
        if not isinstance(why, str) or not why.strip():
            errors.append(f"{loc} why_band empty")
        arxiv = item.get("arxiv")
        if band == "core" and arxiv:
            md = LOCAL_MD / f"{arxiv}.md"
            if not md.is_file():
                errors.append(f"{loc} {eid} missing local extract {md}")
    missing = required - seen
    extra = seen - required
    if missing:
        errors.append(f"registry missing required ids {sorted(missing)}")
    if extra:
        errors.append(f"registry has undeclared ids {sorted(extra)}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"{len(errors)} error(s)", file=sys.stderr)
        return 1
    cores = [e for e in evals if e["band"] == "core"]
    already = [e for e in evals if e["band"] == "already-carded"]
    print(
        f"{len(evals)} evals, {len(already)} already-carded, {len(cores)} core, "
        f"{sum(1 for e in evals if e['band']=='adjacent')} adjacent, "
        f"{sum(1 for e in evals if e['band']=='out-of-scope')} out-of-scope"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
