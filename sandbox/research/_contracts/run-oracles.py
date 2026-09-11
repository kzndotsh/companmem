#!/usr/bin/env python3
"""Run oracle and naive retrieve-then-speak against every public fixture."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRADER = Path(__file__).resolve().parent / "grade_reply.py"
IDS = Path(__file__).resolve().parent / "fixture-ids.txt"
FIXTURES = ROOT / "research" / "evals" / "fixtures"
NAIVE = ROOT / "research" / "evals" / "baselines" / "naive-retrieve" / "run.py"


def fixture_ids() -> list[str]:
    return [
        line.strip()
        for line in IDS.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]


def grade(fixture: Path, artifacts: Path, reward: Path) -> dict[str, float]:
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
    env = {
        **os.environ,
        "COMPANMEM_ARTIFACTS": str(artifacts),
    }
    subprocess.run(
        ["bash", str(fixture / "solution" / "solve.sh")],
        check=True,
        cwd=str(fixture),
        env=env,
    )


def run_naive(fixture: Path, artifacts: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(NAIVE),
            "--world",
            str(fixture / "environment" / "world"),
            "--artifacts",
            str(artifacts),
        ],
        check=True,
    )


def label(payload: dict[str, float]) -> str:
    return "PASS" if payload.get("resolved") == 1.0 else "FAIL"


def main() -> int:
    rows: list[str] = []
    oracle_pass = 0
    naive_fail = 0
    n = 0
    for fid in fixture_ids():
        fixture = FIXTURES / fid
        n += 1
        with tempfile.TemporaryDirectory(prefix=f"companmem-{fid}-") as tmp:
            tmp_path = Path(tmp)
            oracle_art = tmp_path / "oracle"
            naive_art = tmp_path / "naive"
            oracle_art.mkdir()
            naive_art.mkdir()
            run_oracle(fixture, oracle_art)
            oracle = grade(fixture, oracle_art, tmp_path / "oracle-reward.json")
            run_naive(fixture, naive_art)
            naive = grade(fixture, naive_art, tmp_path / "naive-reward.json")
        o = label(oracle)
        nai = label(naive)
        if o == "PASS":
            oracle_pass += 1
        if nai == "FAIL":
            naive_fail += 1
        rows.append(
            f"{fid:24} oracle={o} naive={nai} "
            f"oracle_f2p={oracle['fail_to_pass']} oracle_p2p={oracle['pass_to_pass']} "
            f"naive_f2p={naive['fail_to_pass']} naive_p2p={naive['pass_to_pass']}"
        )
    print("\n".join(rows))
    print(f"{oracle_pass}/{n} oracle PASS, {naive_fail}/{n} naive FAIL")
    if oracle_pass != n or naive_fail != n:
        print("unit 4 check failed", file=sys.stderr)
        return 1
    print("unit 4 check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
