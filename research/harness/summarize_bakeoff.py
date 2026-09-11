#!/usr/bin/env python3
"""Print a bakeoff scoreboard from a harness report JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_report(path: Path) -> dict:
    return json.loads(path.read_text())


def latest_report(results_dir: Path) -> Path | None:
    if not results_dir.is_dir():
        return None
    rows = sorted(results_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return rows[0] if rows else None


def print_board(report: dict) -> None:
    fixture_ids = report.get("fixture_ids", [])
    print(f"bakeoff @ {report.get('observed_at')} {report.get('git_sha')}")
    header = f"{'baseline':22} " + " ".join(f"{fid[:8]:>8}" for fid in fixture_ids) + "  resolved  cost_export"
    print(header)
    for row in report.get("baselines", []):
        bid = row["baseline_id"]
        marks: list[str] = []
        for fid in fixture_ids:
            trial = next((t for t in row.get("trials", []) if t["fixture_id"] == fid), None)
            if trial is None:
                marks.append("     ?  ")
            elif trial.get("status") != "ok":
                marks.append("   skip ")
            elif trial.get("resolved"):
                marks.append("    PASS")
            else:
                marks.append("    FAIL")
        cost = row.get("cost", {})
        print(
            f"{bid:22} "
            + " ".join(marks)
            + f"  {row.get('resolved_count', 0)}/{row.get('fixture_count', 0):<8}"
            + f"  {cost.get('total_export_tokens_approx', 0)}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="harness JSON (default: latest)")
    args = parser.parse_args()
    path = args.report or latest_report(ROOT / "research" / "evals" / "results")
    if path is None or not path.is_file():
        print("no report found", file=__import__("sys").stderr)
        return 1
    print_board(load_report(path))
    print(f"source {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
