from __future__ import annotations

import json
from pathlib import Path

import yaml

from crucible.schema import RunResult, Specimen


def load_specimens(path: str | Path) -> list[Specimen]:
    path = Path(path)
    files = sorted(path.glob("*.yaml")) if path.is_dir() else [path]
    specs = []
    for f in files:
        specs.append(Specimen(**yaml.safe_load(f.read_text(encoding="utf-8"))))
    return specs


def append_run(fh, result: RunResult) -> None:
    """Write one run as a JSON line and flush, so a crash keeps completed runs."""
    fh.write(json.dumps(result.model_dump(mode="json")) + "\n")
    fh.flush()


def write_runs(results: list[RunResult], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for r in results:
            append_run(fh, r)


def read_runs(path: str | Path) -> list[RunResult]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [RunResult(**json.loads(ln)) for ln in lines if ln.strip()]
