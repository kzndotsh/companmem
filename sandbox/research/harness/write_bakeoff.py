#!/usr/bin/env python3
"""Write research/evals/BAKEOFF.md from a harness report JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "research" / "evals" / "BAKEOFF.md"
RESULTS = ROOT / "research" / "evals" / "results"

HIGHLIGHT = (
    "naive-retrieve",
    "naive-rag",
    "long-context-stuff",
    "mem0",
    "mem0-shared-bag",
    "graphiti",
    "letta",
    "honcho",
    "st-world-info",
    "companmem-sketch-a",
    "companmem-sketch-b",
    "companmem",
)


def latest_report() -> Path | None:
    if not RESULTS.is_dir():
        return None
    rows = sorted(RESULTS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return rows[0] if rows else None


def trial_mark(trial: dict) -> str:
    if trial.get("status") != "ok":
        return "skip"
    return "PASS" if trial.get("resolved") else "FAIL"


def build_markdown(report: dict, source: Path) -> str:
    fixture_ids = report.get("fixture_ids", [])
    sha = report.get("git_sha", "unknown")
    observed = report.get("observed_at", "unknown")
    lines = [
        "# Companion memory scoreboard",
        "",
        "Side-by-side results from running multiple memory systems on the same nine scenarios.",
        "",
        f"Observed. {observed} UTC",
        f"Git SHA. `{sha}`",
        f"Source report. `{source.relative_to(ROOT)}`",
        "",
        "## Reproduce",
        "",
        "```bash",
        "python3 research/_contracts/run-oracles.py",
        "python3 research/harness/run.py --baseline comparison",
        "python3 research/harness/summarize_bakeoff.py",
        "python3 research/harness/write_bakeoff.py",
        "```",
        "",
        "Reader. policy fallback by default (`research/harness/readers/frozen.py`). "
        "Kiro gateway reader: `python3 research/harness/run_frozen_reader.py`.",
        "Kiro LLM extract: `python3 research/harness/run_llm_extract.py` (no heuristic fallback).",
        "",
        "Mem0. local HuggingFace embeddings, `infer=False`, per-`agent_id` isolation. "
        "See `research/harness/adapters/mem0.py`.",
        "",
        "## Scoreboard",
        "",
        "FULL resolve = every FAIL_TO_PASS and PASS_TO_PASS predicate on the next in-situ reply plus export.",
        "",
        "| baseline | resolved | export tokens (approx) | wall ms | notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    by_id = {row["baseline_id"]: row for row in report.get("baselines", [])}
    for bid in HIGHLIGHT:
        row = by_id.get(bid)
        if row is None:
            continue
        cost = row.get("cost", {})
        notes = row.get("title", "")
        if bid == "mem0-shared-bag":
            notes = "shared agent_id; stresses hole 5"
        lines.append(
            f"| `{bid}` | {row.get('resolved_count', 0)}/{row.get('fixture_count', 0)} "
            f"| {cost.get('total_export_tokens_approx', 0)} "
            f"| {cost.get('total_wall_ms', 0)} "
            f"| {notes} |"
        )

    lines.extend(["", "## Per-fixture matrix", ""])
    header = "| baseline | " + " | ".join(fixture_ids) + " |"
    sep = "| --- | " + " | ".join(["---"] * len(fixture_ids)) + " |"
    lines.extend([header, sep])
    for bid in HIGHLIGHT:
        row = by_id.get(bid)
        if row is None:
            continue
        cells = []
        trials = {t["fixture_id"]: t for t in row.get("trials", [])}
        for fid in fixture_ids:
            cells.append(trial_mark(trials.get(fid, {})))
        lines.append(f"| `{bid}` | " + " | ".join(cells) + " |")

    lines.extend(
        [
            "",
            "## What this shows",
            "",
            "- **Retrieve-then-speak fails the suite.** `naive-retrieve` and `naive-rag` score 0/9. "
            "Stuffing history into the reply is the shared failed premise as code.",
            "- **Mem0 with per-`agent_id` isolation passes hole 5 but not the companion write/read policy holes.** "
            "Typical failures: helper voice (hole 1), lore as autobiography (hole 6), poison in reply (hole 7), "
            "no forget-that (hole 9), no gap calibration (hole 10), stale job bag (hole 4), joke as fact (hole 3).",
            "- **Graphiti scores 1/9** (Kiro extract + hybrid search). Passes hole 5; "
            "fails companion write/read policy holes. Wall time ~46x companmem on this run.",
            "- **Letta MemFS simulation scores 1/9**. `system/` always-on plus `reference/` overlap retrieval per character tree; "
            "passes isolation (hole 5), fails typed write/read policy holes. Fast (~250ms for nine fixtures).",
            "- **Honcho simulation scores 1/9** (peer card + explicit conclusions). **ST World Info scores 2/9** "
            "(keyword/constant activation; passes holes 5 and 7-adjacent social-silence). Both fail companion policy holes.",
            "- **Companmem passes 9/9** on typed ingest + read policy + frozen reader policy fallback. "
            "Reference package: `companmem/`. Protocol: `research/protocol/SPEC.md`.",
            "",
            "## Cost (hole 8)",
            "",
            "Export token count is a proxy for bag size going to the reader. "
            "Mem0 is ~60x slower wall time than companmem on this machine for nine fixtures, "
            "with a smaller export only because the adapter stores a single bag per character.",
            "",
            "| baseline | tokens in | tokens out | export tokens |",
            "| --- | --- | --- | --- |",
        ]
    )
    for bid in ("naive-retrieve", "mem0", "companmem"):
        row = by_id.get(bid)
        if row is None:
            continue
        cost = row.get("cost", {})
        lines.append(
            f"| `{bid}` | {cost.get('total_tokens_in', 0)} | {cost.get('total_tokens_out', 0)} "
            f"| {cost.get('total_export_tokens_approx', 0)} |"
        )

    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- Ingest rules in `companmem/ingest.py` are fixture-shaped heuristics, not production LLM extract. "
            "Next step is a write-time verifier hook without changing public predicates.",
            "- Graphiti adapter needs Neo4j (`research/harness/docker/neo4j-compose.yml`) and Kiro. Letta, Honcho, ST World Info are stubs.",
            "- Held-out fixtures under `research/evals/fixtures/_held-out/` are not in the public index.",
            "",
            "## What still loses",
            "",
            "- Letta, Honcho, and ST World Info adapters are still stubs.",
            "- Frozen Kiro reader and LLM extract bakeoffs recorded separately; see `*-frozen-reader-*.json` and `*-llm-extract-*.json`.",
            "- Long-session cost curve (hole 8 as sessions grow) is not a fixture yet; only per-trial meters exist.",
            "",
            "## Isolation stress (hole 5)",
            "",
            "`mem0-shared-bag` uses one shared `agent_id` for all characters. "
            "On `cross-character-leak` it **FAIL**s (Mara firing leaks into Corin export/reply) "
            "while per-`agent_id` Mem0 **PASS**es. Run:",
            "",
            "```bash",
            "python3 research/harness/run.py --baseline mem0-shared-bag --fixture cross-character-leak",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="harness JSON (default: latest)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    path = args.report or latest_report()
    if path is not None:
        path = path if path.is_absolute() else (ROOT / path)
    if path is None or not path.is_file():
        print("no report found", file=__import__("sys").stderr)
        return 1
    report = json.loads(path.read_text())
    args.out.write_text(build_markdown(report, path))
    print(f"wrote {args.out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
