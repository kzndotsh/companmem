#!/usr/bin/env python3
"""Companmem reference implementation adapter (unit 7)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from companmem.session import run_turn


def run(world: Path, artifacts: Path) -> dict[str, int | float]:
    return run_turn(world, artifacts)
