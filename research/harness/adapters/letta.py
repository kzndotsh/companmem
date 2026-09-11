#!/usr/bin/env python3
"""Letta adapter stub."""

from __future__ import annotations

from pathlib import Path


class AdapterNotReadyError(RuntimeError):
    pass


def run(world: Path, artifacts: Path) -> dict[str, int | float]:
    raise AdapterNotReadyError("letta: adapter not implemented yet")
