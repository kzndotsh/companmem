"""Turn runner: ingest world, project store, frozen reader reply."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from companmem.ingest import ingest_world
from companmem.reply import compose_reply


def _load_frozen_reader():
    reader_path = Path(__file__).resolve().parents[1] / "research" / "harness" / "readers" / "frozen.py"
    name = "companmem_frozen_reader"
    spec = importlib.util.spec_from_file_location(name, reader_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load reader {reader_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_FROZEN_READER = _load_frozen_reader()


def run_turn(world: Path, artifacts: Path) -> dict[str, int]:
    system = ingest_world(world)
    next_user = (world / "next_user.txt").read_text().strip()
    reply, _meta = _FROZEN_READER.generate_reply(system, next_user, compose_reply)
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "reply.txt").write_text(reply)
    (artifacts / "memory_export.json").write_text(json.dumps(system.export(), indent=2) + "\n")
    return {"tokens_in": len(next_user.split()), "tokens_out": len(reply.split())}
