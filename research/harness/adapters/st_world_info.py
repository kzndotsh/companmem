#!/usr/bin/env python3
"""SillyTavern World Info adapter stub."""

from __future__ import annotations

from pathlib import Path


class AdapterNotReadyError(RuntimeError):
    pass


def run(world: Path, artifacts: Path) -> dict[str, int | float]:
    raise AdapterNotReadyError("st-world-info: adapter not implemented yet")
