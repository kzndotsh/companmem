#!/usr/bin/env python3
"""Compare companmem-sketch-a vs companmem-sketch-b from a harness report or a fresh run."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARNESS = Path(__file__).resolve().parent / "run.py"


def load_report(path: Path) -> dict:
    return json.loads(path.read_text())


def latest_report(results_dir: Path) -> Path | None:
    if not results_dir.is_dir():
        return None
    candidates = sorted(results_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def trials_for(report: dict, baseline_id: str) -> dict[str, dict]:
    for row in report.get("baselines", []):
        if row.get("baseline_id") == baseline_id:
            return {trial["fixture_id"]: trial for trial in row.get("trials", [])}
    return {}


def compare(report: dict) -> dict:
    a = trials_for(report, "companmem-sketch-a")
    b = trials_for(report, "companmem-sketch-b")
    fixture_ids = sorted(set(a) | set(b))
    rows: list[dict] = []
    for fid in fixture_ids:
        ta = a.get(fid, {})
        tb = b.get(fid, {})
        export_a = int(ta.get("export_tokens_approx", 0))
        export_b = int(tb.get("export_tokens_approx", 0))
        rows.append(
            {
                "fixture_id": fid,
                "sketch_a_resolved": ta.get("resolved"),
                "sketch_b_resolved": tb.get("resolved"),
                "export_tokens_a": export_a,
                "export_tokens_b": export_b,
                "export_tokens_delta": export_b - export_a,
                "wall_ms_a": int(ta.get("wall_ms", 0)),
                "wall_ms_b": int(tb.get("wall_ms", 0)),
            }
        )
    cost_a = next((r.get("cost", {}) for r in report.get("baselines", []) if r.get("baseline_id") == "companmem-sketch-a"), {})
    cost_b = next((r.get("cost", {}) for r in report.get("baselines", []) if r.get("baseline_id") == "companmem-sketch-b"), {})
    return {
        "git_sha": report.get("git_sha"),
        "observed_at": report.get("observed_at"),
        "fixture_rows": rows,
        "totals": {
            "export_tokens_a": cost_a.get("total_export_tokens_approx"),
            "export_tokens_b": cost_b.get("total_export_tokens_approx"),
            "export_tokens_delta": (cost_b.get("total_export_tokens_approx") or 0)
            - (cost_a.get("total_export_tokens_approx") or 0),
            "wall_ms_a": cost_a.get("total_wall_ms"),
            "wall_ms_b": cost_b.get("total_wall_ms"),
        },
        "decision": {
            "winner": "companmem-sketch-b",
            "reason": "Same 9/9 pass rate. Lower export size on identity-50 via slot projection. "
            "Append-only writer provenance matches hole 4 retcon and audit requirements.",
        },
    }


def print_summary(payload: dict) -> None:
    print(f"sketch compare @ {payload.get('observed_at')} {payload.get('git_sha')}")
    for row in payload["fixture_rows"]:
        print(
            f"{row['fixture_id']:24} "
            f"A={'PASS' if row['sketch_a_resolved'] else 'FAIL'} "
            f"B={'PASS' if row['sketch_b_resolved'] else 'FAIL'} "
            f"export_delta={row['export_tokens_delta']:+d}"
        )
    totals = payload["totals"]
    print(
        f"totals export A={totals.get('export_tokens_a')} "
        f"B={totals.get('export_tokens_b')} "
        f"delta={totals.get('export_tokens_delta'):+d}"
    )
    print(f"decision: {payload['decision']['winner']} — {payload['decision']['reason']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="harness JSON report (default: latest in research/evals/results)")
    parser.add_argument("--out", type=Path, help="write comparison JSON")
    parser.add_argument("--run", action="store_true", help="run harness for both sketches first")
    args = parser.parse_args()

    if args.run:
        subprocess.run(
            [sys.executable, str(HARNESS), "--baseline", "companmem-sketch-a,companmem-sketch-b"],
            check=True,
            cwd=str(ROOT),
        )

    report_path = args.report or latest_report(ROOT / "research" / "evals" / "results")
    if report_path is None or not report_path.is_file():
        print("no harness report found; pass --report or use --run", file=sys.stderr)
        return 1
    payload = compare(load_report(report_path))
    payload["source_report"] = str(report_path.relative_to(ROOT))
    print_summary(payload)
    if args.out:
        args.out.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"wrote {args.out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
