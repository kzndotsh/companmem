#!/usr/bin/env python3
"""Validate harness registry and baseline entrypoints."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "research" / "harness" / "registry.json"
RUNNER = ROOT / "research" / "harness" / "run.py"
MODES = {"oracle", "script", "adapter"}


def main() -> int:
    errors: list[str] = []
    if not RUNNER.is_file():
        errors.append(f"missing {RUNNER.relative_to(ROOT)}")
    if not REGISTRY.is_file():
        errors.append(f"missing {REGISTRY.relative_to(ROOT)}")
        print("\n".join(errors), file=sys.stderr)
        return 1
    data = json.loads(REGISTRY.read_text())
    baselines = data.get("baselines")
    if not isinstance(baselines, list) or not baselines:
        errors.append("registry.baselines empty")
    seen: set[str] = set()
    for i, item in enumerate(baselines or []):
        loc = f"baselines[{i}]"
        bid = item.get("id")
        if bid in seen:
            errors.append(f"{loc} duplicate {bid}")
        seen.add(bid)
        if item.get("mode") not in MODES:
            errors.append(f"{loc} bad mode")
        if item.get("mode") == "script":
            script = ROOT / item.get("script", "")
            if not script.is_file():
                errors.append(f"{loc} missing script {script.relative_to(ROOT)}")
        if item.get("mode") == "adapter":
            adapter = ROOT / item.get("adapter", "")
            if not adapter.is_file():
                errors.append(f"{loc} missing adapter {adapter.relative_to(ROOT)}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"{len(baselines)} baselines registered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
