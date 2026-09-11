#!/usr/bin/env python3
"""Run oracle, naive, and companmem against held-out fixtures (not in public index)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARNESS = Path(__file__).resolve().parent
HELD_OUT = ROOT / "research" / "evals" / "fixtures" / "_held-out"
GRADER = ROOT / "research" / "_contracts" / "grade_reply.py"
NAIVE = ROOT / "research" / "evals" / "baselines" / "naive-retrieve" / "run.py"
RESULTS = ROOT / "research" / "evals" / "results"
ADAPTER = HARNESS / "adapters" / "companmem.py"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from companmem.env import load_dotenv

load_dotenv()


def fixture_ids() -> list[str]:
    if not HELD_OUT.is_dir():
        return []
    return sorted(
        path.name
        for path in HELD_OUT.iterdir()
        if path.is_dir() and (path / "tests" / "predicates.json").is_file()
    )


def grade(fixture: Path, artifacts: Path, reward: Path) -> dict:
    subprocess.run(
        [
            sys.executable,
            str(GRADER),
            "--predicates",
            str(fixture / "tests" / "predicates.json"),
            "--reply",
            str(artifacts / "reply.txt"),
            "--export",
            str(artifacts / "memory_export.json"),
            "--out",
            str(reward),
        ],
        check=True,
        cwd=str(fixture),
        stdout=subprocess.DEVNULL,
    )
    return json.loads(reward.read_text())


def run_oracle(fixture: Path, artifacts: Path) -> None:
    env = {**os.environ, "COMPANMEM_ARTIFACTS": str(artifacts)}
    subprocess.run(
        ["bash", str(fixture / "solution" / "solve.sh")],
        check=True,
        cwd=str(fixture),
        env=env,
    )


def run_naive(world: Path, artifacts: Path) -> None:
    subprocess.run(
        [sys.executable, str(NAIVE), "--world", str(world), "--artifacts", str(artifacts)],
        check=True,
        cwd=str(ROOT),
    )


def load_adapter():
    import importlib.util

    spec = importlib.util.spec_from_file_location("companmem_adapter", ADAPTER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ADAPTER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", help="single held-out fixture id")
    parser.add_argument("--out", type=Path, help="report JSON path")
    args = parser.parse_args()

    ids = [args.fixture] if args.fixture else fixture_ids()
    if not ids:
        print("no held-out fixtures found", file=sys.stderr)
        return 1

    adapter = load_adapter()
    rows: list[dict] = []

    for fid in ids:
        fixture = HELD_OUT / fid
        world = fixture / "environment" / "world"
        with tempfile.TemporaryDirectory(prefix=f"held-{fid}-") as tmp:
            tmp_path = Path(tmp)
            oracle_art = tmp_path / "oracle"
            naive_art = tmp_path / "naive"
            companmem_art = tmp_path / "companmem"
            for art in (oracle_art, naive_art, companmem_art):
                art.mkdir()

            run_oracle(fixture, oracle_art)
            oracle = grade(fixture, oracle_art, tmp_path / "oracle-reward.json")

            run_naive(world, naive_art)
            naive = grade(fixture, naive_art, tmp_path / "naive-reward.json")

            adapter.run(world, companmem_art)
            companmem = grade(fixture, companmem_art, tmp_path / "companmem-reward.json")

        def mark(payload: dict) -> str:
            return "PASS" if payload.get("resolved") == 1.0 else "FAIL"

        print(
            f"{fid:24} oracle={mark(oracle)} naive={mark(naive)} companmem={mark(companmem)}"
        )
        rows.append(
            {
                "fixture_id": fid,
                "oracle": oracle,
                "naive": naive,
                "companmem": companmem,
            }
        )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    report = {
        "observed_at": now,
        "baseline_id": "held-out",
        "fixtures": rows,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = args.out or (RESULTS / f"{now}-held-out.json")
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"report {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
