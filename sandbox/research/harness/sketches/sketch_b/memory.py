"""Sketch B. Thin wrapper over the companmem reference package."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from companmem.session import run_turn


def run_sketch(world: Path, artifacts: Path) -> dict[str, int]:
    return run_turn(world, artifacts)
