"""CLI entry points for the companion memory evaluation harness.

Usage:
    python -m harness run --baseline <id|all> [--fixture <id>]
                          [--fixtures-root <path>] [--results-root <path>]
                          [--include-docker]

    python -m harness score --run-id <id>
                            [--results-root <path>] [--fixtures-root <path>]
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from harness.adapter import AdapterNotReadyError
from harness.artifacts import ArtifactMissing, Artifacts
from harness.scorer import Scorer
from harness.trial import BaselineResult, RunReport, TrialResult, TrialStatus
from harness.world import World

# registry.json lives next to this file inside the installed package
_REGISTRY_PATH = Path(__file__).parent / "registry.json"


def load_registry() -> dict[str, Any]:
    return json.loads(_REGISTRY_PATH.read_text())


# private alias kept for internal use
_load_registry = load_registry


@dataclass(frozen=True)
class FixtureMeta:
    id: str
    behavior: str
    title: str
    description: str
    probe_type: str
    pass_proves: str
    fail_reveals: str
    why_naive_fails: str
    split: str  # "dev" or "test"; fixtures without the field default to "dev"


def load_fixture_meta(fixture_dir: Path) -> FixtureMeta | None:
    """Load fixture.json from a fixture directory. Returns None if absent or malformed."""
    p = fixture_dir / "fixture.json"
    if not p.is_file():
        return None
    try:
        d = json.loads(p.read_text())
        return FixtureMeta(
            id=str(d["id"]),
            behavior=str(d["behavior"]),
            title=str(d["title"]),
            description=str(d["description"]),
            probe_type=str(d["probe_type"]),
            pass_proves=str(d["pass_proves"]),
            fail_reveals=str(d["fail_reveals"]),
            why_naive_fails=str(d["why_naive_fails"]),
            split=str(d.get("split", "dev")),
        )
    except (KeyError, json.JSONDecodeError):
        return None


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def enumerate_fixtures(fixtures_root: Path) -> list[str]:
    """Return sorted fixture IDs: subdirs of fixtures_root not starting with '_'."""
    return sorted(
        d.name
        for d in fixtures_root.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )


# private alias kept for internal use
_enumerate_fixtures = enumerate_fixtures


def _compute_cost_flags(
    wall_ms: int,
    export_tokens_approx: int,
    cost_budgets: dict[str, int],
) -> list[str]:
    flags: list[str] = []
    if (cap := cost_budgets.get("wall_ms_per_trial")) is not None and wall_ms > cap:
        flags.append("wall_ms_over_budget")
    export_cap = cost_budgets.get("export_tokens_approx_per_trial")
    if export_cap is not None and export_tokens_approx > export_cap:
        flags.append("export_tokens_over_budget")
    return flags


def _run_trial(
    adapter_entry: dict[str, Any],
    fixture_id: str,
    fixtures_root: Path,
    results_root: Path,
    run_id: str,
    include_docker: bool,
    cost_budgets: dict[str, int],
    behavior: str | None = None,
    run_index: int = 0,
    runs: int = 1,
) -> TrialResult:
    baseline_id = str(adapter_entry["id"])
    needs_docker = bool(adapter_entry.get("needs_docker", False))

    art_base = results_root / run_id / baseline_id / fixture_id
    art_dir = art_base / f"run_{run_index}" if runs > 1 else art_base
    artifacts = Artifacts(art_dir)
    artifacts_path = art_dir.relative_to(results_root.parent).as_posix()

    world_dir = fixtures_root / fixture_id / "world"
    solution_dir = fixtures_root / fixture_id / "solution"

    world = World.from_path(world_dir, solution_dir=solution_dir)
    fixture_hash = world.fixture_hash

    # Docker skip
    if needs_docker and not include_docker:
        print(f"{baseline_id:24} {fixture_id:28} SKIPPED (needs_docker, no --include-docker)")
        return TrialResult(
            fixture_id=fixture_id,
            fixture_hash=fixture_hash,
            status=TrialStatus.SKIPPED,
            resolved=False,
            fail_to_pass=False,
            pass_to_pass=False,
            predicate_details=[],
            judge_score=None,
            judge_model=None,
            wall_ms=0,
            tokens_in=0,
            tokens_out=0,
            memory_tokens=0,
            export_tokens_approx=0,
            cost_flags=[],
            artifacts_path=artifacts_path,
            error="skipped: needs_docker",
            behavior=behavior,
            run_index=run_index,
        )

    # Load adapter class
    class_path = str(adapter_entry["class"])
    mod_path, cls_name = class_path.rsplit(".", 1)
    try:
        mod = importlib.import_module(mod_path)
        adapter = getattr(mod, cls_name)()
    except Exception as exc:
        error_msg = f"{type(exc).__name__}: {exc}"
        print(f"{baseline_id:24} {fixture_id:28} INFRA_ERROR (import: {error_msg})")
        return TrialResult(
            fixture_id=fixture_id,
            fixture_hash=fixture_hash,
            status=TrialStatus.INFRA_ERROR,
            resolved=False,
            fail_to_pass=False,
            pass_to_pass=False,
            predicate_details=[],
            judge_score=None,
            judge_model=None,
            wall_ms=0,
            tokens_in=0,
            tokens_out=0,
            memory_tokens=0,
            export_tokens_approx=0,
            cost_flags=[],
            artifacts_path=artifacts_path,
            error=error_msg,
            behavior=behavior,
            run_index=run_index,
        )

    # Run adapter
    t0 = time.perf_counter()
    status = TrialStatus.OK
    error: str | None = None
    tokens_in = 0
    tokens_out = 0
    memory_tokens = 0

    try:
        metrics = adapter.run(world, artifacts)
        tokens_in = metrics.tokens_in
        tokens_out = metrics.tokens_out
        memory_tokens = metrics.memory_tokens
    except AdapterNotReadyError as exc:
        status = TrialStatus.SKIPPED
        error = f"{type(exc).__name__}: {exc}"
    except Exception as exc:
        status = TrialStatus.INFRA_ERROR
        error = f"{type(exc).__name__}: {exc}"

    wall_ms = int((time.perf_counter() - t0) * 1000)

    # Score (only if adapter ran successfully)
    resolved = False
    fail_to_pass = False
    pass_to_pass = False
    predicate_details: list[str] = []
    judge_score: float | None = None
    judge_model: str | None = None

    if status == TrialStatus.OK:
        pred_path = fixtures_root / fixture_id / "tests" / "predicates.json"
        try:
            scorer = Scorer(pred_path)
            score_result = scorer.score(artifacts)
            resolved = score_result.resolved
            fail_to_pass = score_result.fail_to_pass
            pass_to_pass = score_result.pass_to_pass
            predicate_details = score_result.predicate_details
            judge_score = score_result.judge_score
            judge_model = score_result.judge_model
        except Exception as exc:
            status = TrialStatus.INFRA_ERROR
            error = f"scorer: {type(exc).__name__}: {exc}"

    # export_tokens_approx
    import contextlib

    export_tokens_approx = 0
    with contextlib.suppress(ArtifactMissing):
        export_tokens_approx = len(json.dumps(artifacts.export()).split())

    cost_flags = _compute_cost_flags(wall_ms, export_tokens_approx, cost_budgets)

    mark = "PASS" if resolved else ("FAIL" if status == TrialStatus.OK else status.value.upper())
    print(
        f"{baseline_id:24} {fixture_id:28} {mark:12} "
        f"wall_ms={wall_ms} export_tok={export_tokens_approx}"
    )

    return TrialResult(
        fixture_id=fixture_id,
        fixture_hash=fixture_hash,
        status=status,
        resolved=resolved,
        fail_to_pass=fail_to_pass,
        pass_to_pass=pass_to_pass,
        predicate_details=predicate_details,
        judge_score=judge_score,
        judge_model=judge_model,
        wall_ms=wall_ms,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        memory_tokens=memory_tokens,
        export_tokens_approx=export_tokens_approx,
        cost_flags=cost_flags,
        artifacts_path=artifacts_path,
        error=error,
        behavior=behavior,
        run_index=run_index,
    )


def _cmd_run(args: argparse.Namespace) -> int:
    # Mutual exclusion guard — must be first, before any path resolution
    if args.fixture and args.behavior:
        print("error: --fixture and --behavior are mutually exclusive")
        return 1

    if args.runs < 1:
        print("error: --runs must be ≥ 1")
        return 1

    # Resolve paths
    cwd = Path.cwd()
    fixtures_root = Path(args.fixtures_root) if args.fixtures_root else cwd / "evals" / "fixtures"
    if not fixtures_root.is_dir():
        msg = f"fixtures directory not found: {fixtures_root}"
        raise FileNotFoundError(msg)

    results_root = Path(args.results_root) if args.results_root else cwd / "evals" / "results"
    results_root.mkdir(parents=True, exist_ok=True)

    # Enumerate fixtures; narrow to single fixture if --fixture given
    all_fixture_ids = _enumerate_fixtures(fixtures_root)
    if args.fixture:
        if args.fixture not in all_fixture_ids:
            print(f"fixture {args.fixture!r} not found in {fixtures_root}")
            return 1
        all_fixture_ids = [args.fixture]

    # Single pass: build fixture_metas and filter by --behavior and --split when set
    fixture_metas: dict[str, FixtureMeta | None] = {}
    fixture_ids: list[str] = []
    split_filter: str = getattr(args, "split", "all")
    for fid in all_fixture_ids:
        meta = load_fixture_meta(fixtures_root / fid)
        fixture_metas[fid] = meta
        behavior_ok = args.behavior is None or (meta is not None and meta.behavior == args.behavior)
        meta_split = meta.split if meta is not None else "dev"
        split_ok = split_filter == "all" or meta_split == split_filter
        if behavior_ok and split_ok:
            fixture_ids.append(fid)

    if args.behavior and not fixture_ids:
        print(f"no fixtures found for behavior {args.behavior!r}")
        return 1

    # Load registry
    registry = _load_registry()
    adapter_by_id: dict[str, dict[str, Any]] = {a["id"]: a for a in registry["adapters"]}
    cost_budgets: dict[str, int] = registry.get("cost_budgets", {})

    # Select baselines
    baseline_arg: str = args.baseline
    if baseline_arg == "all":
        selected = list(registry["adapters"])
    else:
        if baseline_arg not in adapter_by_id:
            print(f"unknown baseline {baseline_arg!r}. Available: {', '.join(adapter_by_id)}")
            return 1
        selected = [adapter_by_id[baseline_arg]]

    run_id = uuid.uuid4().hex
    observed_at = datetime.now(UTC).isoformat()

    baseline_results: list[BaselineResult] = []
    for adapter_entry in selected:
        bid = str(adapter_entry["id"])
        title = str(adapter_entry.get("title", bid))
        trials: list[TrialResult] = []
        total_trials = args.runs * len(fixture_ids)
        global_idx = 0
        for run_index in range(args.runs):
            for fid in fixture_ids:
                global_idx += 1
                print(f"{bid:24} {fid:28} running ({global_idx}/{total_trials}) ...")
                _meta = fixture_metas.get(fid)
                trial = _run_trial(
                    adapter_entry=adapter_entry,
                    fixture_id=fid,
                    fixtures_root=fixtures_root,
                    results_root=results_root,
                    run_id=run_id,
                    include_docker=bool(args.include_docker),
                    cost_budgets=cost_budgets,
                    behavior=_meta.behavior if _meta is not None else None,
                    run_index=run_index,
                    runs=args.runs,
                )
                trials.append(trial)
        baseline_results.append(BaselineResult.from_trials(bid, title, trials))

    scored_at = datetime.now(UTC).isoformat()
    report = RunReport(
        run_id=run_id,
        observed_at=observed_at,
        scored_at=scored_at,
        git_sha=_git_sha(),
        fixture_ids=fixture_ids,
        baselines=baseline_results,
    )

    run_dir = results_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    report_path = run_dir / "report.json"
    report_path.write_text(report.to_json())

    # Write manifest — includes cost_budgets so rescore() can recompute flags
    manifest: dict[str, Any] = {
        "run_id": run_id,
        "runs": args.runs,
        "observed_at": observed_at,
        "git_sha": report.git_sha,
        "fixture_ids": fixture_ids,
        "cost_budgets": cost_budgets,
        "baselines": [
            {
                "baseline_id": a["id"],
                "title": a.get("title", a["id"]),
                "class": a["class"],
                "needs_docker": a.get("needs_docker", False),
            }
            for a in selected
        ],
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2))

    report.print_summary()
    print(f"\nreport: {report_path}")
    return 0


def _cmd_score(args: argparse.Namespace) -> int:
    cwd = Path.cwd()
    results_root = Path(args.results_root) if args.results_root else cwd / "evals" / "results"
    fixtures_root = Path(args.fixtures_root) if args.fixtures_root else cwd / "evals" / "fixtures"

    artifacts_root = results_root / args.run_id
    new_report = RunReport.rescore(artifacts_root, fixtures_root)

    report_path = artifacts_root / "report.json"
    report_path.write_text(new_report.to_json())
    new_report.print_summary()
    print(f"\nrescored: {report_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="harness",
        description="Companion memory evaluation harness",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # run
    run_p = sub.add_parser("run", help="Run adapters and score results")
    run_p.add_argument("--baseline", required=True, help="Adapter id or 'all'")
    run_p.add_argument("--fixture", default=None, help="Single fixture id")
    run_p.add_argument("--fixtures-root", default=None, help="Override evals/fixtures path")
    run_p.add_argument("--results-root", default=None, help="Override evals/results path")
    run_p.add_argument(
        "--include-docker",
        action="store_true",
        help="Include needs_docker adapters",
    )
    run_p.add_argument(
        "--behavior",
        default=None,
        help="Filter fixtures to those with this behavior id (b0, b1, b3, b5)",
    )
    run_p.add_argument(
        "--runs",
        type=int,
        default=1,
        metavar="N",
        help="Number of times to run each fixture (default 1)",
    )
    run_p.add_argument(
        "--split",
        default="all",
        choices=["dev", "test", "all"],
        help="Filter fixtures by split tag: dev, test, or all (default all)",
    )

    # score
    score_p = sub.add_parser("score", help="Re-score a prior run's artifacts")
    score_p.add_argument("--run-id", required=True, help="Run id to re-score")
    score_p.add_argument("--results-root", default=None, help="Override evals/results path")
    score_p.add_argument("--fixtures-root", default=None, help="Override evals/fixtures path")

    args = parser.parse_args()
    if args.command == "run":
        return _cmd_run(args)
    return _cmd_score(args)
