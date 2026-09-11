#!/usr/bin/env python3
"""Sketch B adapter. Append-only atoms with read-time projection."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_memory():
    path = Path(__file__).resolve().parents[1] / "sketches" / "sketch_b" / "memory.py"
    name = "companmem_sketch_b_memory"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run(world: Path, artifacts: Path) -> dict[str, int | float]:
    memory = _load_memory()
    return memory.run_sketch(world, artifacts)
