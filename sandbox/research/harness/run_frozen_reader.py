#!/usr/bin/env python3
"""Run companmem with a frozen LLM reader (Kiro gateway) across public fixtures."""

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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from companmem.env import load_dotenv

load_dotenv()
FIXTURE_IDS = ROOT / "research" / "_contracts" / "fixture-ids.txt"
FIXTURES = ROOT / "research" / "evals" / "fixtures"
GRADER = ROOT / "research" / "_contracts" / "grade_reply.py"
RESULTS = ROOT / "research" / "evals" / "results"
ADAPTER = HARNESS / "adapters" / "companmem.py"


def fixture_ids() -> list[str]:
    return [
        line.strip()
        for line in FIXTURE_IDS.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]


def git_sha() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def load_adapter():
    import importlib.util

    spec = importlib.util.spec_from_file_location("companmem_adapter", ADAPTER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ADAPTER}")
    module = importlib.util.module_from_spec(spec)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    spec.loader.exec_module(module)
    return module


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        default=os.environ.get("COMPANMEM_READER_MODEL", "claude-sonnet-4.6"),
        help="Kiro gateway model for frozen reader",
    )
    parser.add_argument("--out", type=Path, help="report JSON path")
    args = parser.parse_args()

    from companmem.llm_client import llm_backend

    if llm_backend() == "none":
        print(
            "KIRO_GATEWAY_API_KEY is required (copy .env.example → .env or export it)",
            file=sys.stderr,
        )
        return 1

    os.environ.setdefault("COMPANMEM_READER_MODEL", args.model)
    adapter = load_adapter()
    trials: list[dict] = []
    resolved = 0

    for fid in fixture_ids():
        fixture = FIXTURES / fid
        with tempfile.TemporaryDirectory(prefix=f"frozen-{fid}-") as tmp:
            artifacts = Path(tmp)
            world = fixture / "environment" / "world"
            metrics = adapter.run(world, artifacts)
            scores = grade(fixture, artifacts, artifacts / "reward.json")
            ok = scores.get("resolved") == 1.0
            if ok:
                resolved += 1
            trials.append(
                {
                    "fixture_id": fid,
                    "status": "ok",
                    "resolved": ok,
                    "fail_to_pass": scores.get("fail_to_pass") == 1.0,
                    "pass_to_pass": scores.get("pass_to_pass") == 1.0,
                    "tokens_in": metrics.get("tokens_in", 0),
                    "tokens_out": metrics.get("tokens_out", 0),
                }
            )
            mark = "PASS" if ok else "FAIL"
            print(f"{fid:24} {mark} in={metrics.get('tokens_in')} out={metrics.get('tokens_out')}")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    report = {
        "observed_at": now,
        "git_sha": git_sha(),
        "reader_model": os.environ.get("COMPANMEM_READER_MODEL", args.model),
        "llm_backend": llm_backend(),
        "extract_backend": os.environ.get("COMPANMEM_EXTRACT_BACKEND", "heuristic"),
        "baseline_id": "companmem-frozen-reader",
        "resolved_count": resolved,
        "fixture_count": len(fixture_ids()),
        "trials": trials,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = args.out or (RESULTS / f"{now}-frozen-reader-{args.model.replace('/', '_')}.json")
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"{resolved}/{len(trials)} PASS")
    print(f"report {out.relative_to(ROOT)}")
    return 0 if resolved == len(trials) else 1


if __name__ == "__main__":
    raise SystemExit(main())
