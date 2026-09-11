#!/usr/bin/env python3
"""Honcho adapter stub."""

from __future__ import annotations

from pathlib import Path


class AdapterNotReadyError(RuntimeError):
    pass


def run(world: Path, artifacts: Path) -> dict[str, int | float]:
    raise AdapterNotReadyError("honcho: adapter not implemented yet")
