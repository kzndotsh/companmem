#!/usr/bin/env python3
"""Merge baseline rows from overlay reports into a base harness report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def merge(base: dict, overlays: list[dict]) -> dict:
    by_id = {row["baseline_id"]: row for row in base.get("baselines", [])}
    for overlay in overlays:
        for row in overlay.get("baselines", []):
            by_id[row["baseline_id"]] = row
    merged = dict(base)
    merged["baselines"] = list(by_id.values())
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True, help="base report JSON")
    parser.add_argument("--overlay", type=Path, action="append", default=[], help="overlay report(s)")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    base_path = args.base if args.base.is_absolute() else ROOT / args.base
    base = json.loads(base_path.read_text())
    overlays = []
    for path in args.overlay:
        resolved = path if path.is_absolute() else ROOT / path
        overlays.append(json.loads(resolved.read_text()))
    out_path = args.out if args.out.is_absolute() else ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(merge(base, overlays), indent=2) + "\n")
    print(out_path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
