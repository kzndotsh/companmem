#!/usr/bin/env python3
"""Validate paper registry against PAPER-INGEST rules and census cards."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "research" / "papers" / "registry.json"
CARDS = ROOT / "research" / "census" / "cards"
REQUIRED = ROOT / "research" / "_contracts" / "paper-ids.txt"
LOCAL_MD = ROOT / "research" / "papers" / "arxiv"

BANDS = {"core", "adjacent", "out-of-scope"}
PREMISE = {"yes", "no", "mixed", "unknown", "n/a"}


def main() -> int:
    errors: list[str] = []
    if not REGISTRY.is_file():
        print(f"missing {REGISTRY}", file=sys.stderr)
        return 1
    data = json.loads(REGISTRY.read_text())
    papers = data.get("papers")
    if not isinstance(papers, list):
        print("registry.papers must be a list", file=sys.stderr)
        return 1
    required = {
        line.strip()
        for line in REQUIRED.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    seen: set[str] = set()
    for i, paper in enumerate(papers):
        loc = f"papers[{i}]"
        arxiv = paper.get("arxiv")
        if arxiv in seen:
            errors.append(f"{loc} duplicate {arxiv}")
        seen.add(arxiv)
        if paper.get("band") not in BANDS:
            errors.append(f"{loc} bad band")
        if paper.get("assumes_retrieve_equals_remember") not in PREMISE:
            errors.append(f"{loc} bad premise")
        card_id = paper.get("card_id")
        band = paper.get("band")
        if band == "core":
            if not card_id:
                errors.append(f"{loc} {arxiv} core missing card_id")
            else:
                path = CARDS / f"{card_id}.json"
                if not path.is_file():
                    errors.append(f"{loc} {arxiv} core card missing {path.relative_to(ROOT)}")
        else:
            if card_id:
                errors.append(f"{loc} {arxiv} {band} must have card_id null")
        if band == "out-of-scope" and paper.get("holes"):
            errors.append(f"{loc} {arxiv} out-of-scope must have empty holes")
        steal = paper.get("steal")
        why = paper.get("why_band")
        if not isinstance(steal, str) or not steal.strip():
            errors.append(f"{loc} steal empty")
        if not isinstance(why, str) or not why.strip():
            errors.append(f"{loc} why_band empty")
        md = LOCAL_MD / f"{arxiv}.md"
        if not md.is_file():
            errors.append(f"{loc} {arxiv} missing local extract {md}")
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
    cores = [p for p in papers if p["band"] == "core"]
    print(
        f"{len(papers)} papers, {len(cores)} core, "
        f"{sum(1 for p in papers if p['band']=='adjacent')} adjacent, "
        f"{sum(1 for p in papers if p['band']=='out-of-scope')} out-of-scope"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
