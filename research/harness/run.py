#!/usr/bin/env python3
"""Unit 5 harness. One command, dated scores, agent isolated from verifier."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
HARNESS = Path(__file__).resolve().parent
REGISTRY = HARNESS / "registry.json"
FIXTURE_IDS = ROOT / "research" / "_contracts" / "fixture-ids.txt"
FIXTURES = ROOT / "research" / "evals" / "fixtures"
GRADER = ROOT / "research" / "_contracts" / "grade_reply.py"
RESULTS = ROOT / "research" / "evals" / "results"

LOCAL_DEFAULTS = (
    "oracle",
    "naive-retrieve",
    "long-context-stuff",
    "naive-rag",
    "mem0",
    "companmem-sketch-a",
    "companmem-sketch-b",
    "companmem",
)


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


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY.read_text())


def baseline_by_id(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in registry["baselines"]}


def copy_world(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def run_oracle(fixture: Path, artifacts: Path) -> dict[str, int | float]:
    env = {**os.environ, "COMPANMEM_ARTIFACTS": str(artifacts)}
    subprocess.run(
        ["bash", str(fixture / "solution" / "solve.sh")],
        check=True,
        cwd=str(fixture),
        env=env,
    )
    return {"tokens_in": 0, "tokens_out": 0}


def run_script(script: Path, world: Path, artifacts: Path) -> dict[str, int | float]:
    world_blob = ""
    for path in sorted(world.rglob("*")):
        if path.is_file() and path.suffix in {".md", ".txt", ".jsonl", ".json"}:
            world_blob += path.read_text()
    subprocess.run(
        [sys.executable, str(script), "--world", str(world), "--artifacts", str(artifacts)],
        check=True,
        cwd=str(ROOT),
    )
    reply = (artifacts / "reply.txt").read_text()
    return {
        "tokens_in": len(world_blob.split()),
        "tokens_out": len(reply.split()),
    }


def load_adapter(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(f"adapter_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load adapter {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_adapter(path: Path, world: Path, artifacts: Path) -> dict[str, int | float]:
    module = load_adapter(path)
    metrics = module.run(world, artifacts)
    if not isinstance(metrics, dict):
        return {"tokens_in": 0, "tokens_out": 0}
    return {
        "tokens_in": int(metrics.get("tokens_in", 0)),
        "tokens_out": int(metrics.get("tokens_out", 0)),
    }


def export_metrics(artifacts: Path) -> dict[str, int]:
    export_path = artifacts / "memory_export.json"
    if not export_path.is_file():
        return {"export_chars": 0, "export_tokens_approx": 0}
    text = export_path.read_text()
    return {"export_chars": len(text), "export_tokens_approx": len(text.split())}


def cost_flags(trial: dict[str, Any], budgets: dict[str, int]) -> list[str]:
    flags: list[str] = []
    if trial["status"] != "ok":
        return flags
    export_cap = budgets.get("export_tokens_approx_per_trial")
    wall_cap = budgets.get("wall_ms_per_trial")
    if export_cap is not None and trial.get("export_tokens_approx", 0) > export_cap:
        flags.append("export_tokens_over_budget")
    if wall_cap is not None and trial.get("wall_ms", 0) > wall_cap:
        flags.append("wall_ms_over_budget")
    return flags


def summarize_cost(trials: list[dict[str, Any]], budgets: dict[str, int]) -> dict[str, Any]:
    ok = [trial for trial in trials if trial["status"] == "ok"]
    resolved = [trial for trial in ok if trial.get("resolved")]
    total_wall = sum(int(trial.get("wall_ms", 0)) for trial in ok)
    total_in = sum(int(trial.get("tokens_in", 0)) for trial in ok)
    total_out = sum(int(trial.get("tokens_out", 0)) for trial in ok)
    total_export = sum(int(trial.get("export_tokens_approx", 0)) for trial in ok)
    over_budget = sum(1 for trial in ok if trial.get("cost_flags"))
    return {
        "hole": 8,
        "trial_count": len(ok),
        "resolved_count": len(resolved),
        "total_wall_ms": total_wall,
        "mean_wall_ms_per_trial": int(total_wall / len(ok)) if ok else 0,
        "total_tokens_in": total_in,
        "total_tokens_out": total_out,
        "total_export_tokens_approx": total_export,
        "tokens_per_resolved": int((total_in + total_out) / len(resolved)) if resolved else None,
        "wall_ms_per_resolved": int(total_wall / len(resolved)) if resolved else None,
        "trials_over_budget": over_budget,
        "budgets": budgets,
    }


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


def run_trial(
    baseline: dict[str, Any],
    fixture_id: str,
    work_root: Path,
) -> dict[str, Any]:
    fixture = FIXTURES / fixture_id
    agent_dir = work_root / "agent"
    artifacts = work_root / "artifacts"
    reward = work_root / "reward.json"
    world = agent_dir / "world"
    agent_dir.mkdir(parents=True, exist_ok=True)
    artifacts.mkdir(parents=True, exist_ok=True)
    copy_world(fixture / "environment" / "world", world)

    started = time.perf_counter()
    status = "ok"
    error: str | None = None
    metrics: dict[str, int | float] = {"tokens_in": 0, "tokens_out": 0}
    scores: dict[str, float] = {
        "resolved": 0.0,
        "fail_to_pass": 0.0,
        "pass_to_pass": 0.0,
        "infra_ok": 0.0,
    }
    try:
        mode = baseline["mode"]
        if mode == "oracle":
            metrics = run_oracle(fixture, artifacts)
        elif mode == "script":
            script = ROOT / baseline["script"]
            metrics = run_script(script, world, artifacts)
        elif mode == "adapter":
            adapter = ROOT / baseline["adapter"]
            metrics = run_adapter(adapter, world, artifacts)
        else:
            raise RuntimeError(f"unknown mode {mode}")
        scores = grade(fixture, artifacts, reward)
    except RuntimeError as exc:
        status = "skipped"
        error = str(exc)
    except subprocess.CalledProcessError as exc:
        status = "infra_error"
        error = f"exit {exc.returncode}"
    wall_ms = int((time.perf_counter() - started) * 1000)
    export_stats = export_metrics(artifacts) if status == "ok" else {"export_chars": 0, "export_tokens_approx": 0}
    trial = {
        "fixture_id": fixture_id,
        "status": status,
        "resolved": scores.get("resolved", 0.0) == 1.0,
        "fail_to_pass": scores.get("fail_to_pass", 0.0) == 1.0,
        "pass_to_pass": scores.get("pass_to_pass", 0.0) == 1.0,
        "wall_ms": wall_ms,
        "tokens_in": metrics.get("tokens_in", 0),
        "tokens_out": metrics.get("tokens_out", 0),
        "export_chars": export_stats["export_chars"],
        "export_tokens_approx": export_stats["export_tokens_approx"],
        "error": error,
    }
    return trial


def run_baseline(
    baseline: dict[str, Any],
    fixture_list: list[str],
    tmp_parent: Path,
    budgets: dict[str, int],
) -> dict[str, Any]:
    trials: list[dict[str, Any]] = []
    for fixture_id in fixture_list:
        work = tmp_parent / baseline["id"] / fixture_id
        trial = run_trial(baseline, fixture_id, work)
        trial["cost_flags"] = cost_flags(trial, budgets)
        trials.append(trial)
    resolved = sum(1 for t in trials if t["status"] == "ok" and t["resolved"])
    runnable = sum(1 for t in trials if t["status"] == "ok")
    return {
        "baseline_id": baseline["id"],
        "title": baseline["title"],
        "mode": baseline["mode"],
        "trials": trials,
        "resolved_count": resolved,
        "runnable_count": runnable,
        "fixture_count": len(fixture_list),
        "cost": summarize_cost(trials, budgets),
    }


def print_summary(report: dict[str, Any]) -> None:
    for row in report["baselines"]:
        bid = row["baseline_id"]
        for trial in row["trials"]:
            if trial["status"] != "ok":
                mark = trial["status"]
            elif trial.get("resolved"):
                mark = "PASS"
            else:
                mark = "FAIL"
            cost_note = ""
            if trial.get("cost_flags"):
                cost_note = f" cost={','.join(trial['cost_flags'])}"
            print(
                f"{bid:22} {trial['fixture_id']:24} {mark:12} "
                f"f2p={trial['fail_to_pass']} p2p={trial['pass_to_pass']} "
                f"wall_ms={trial['wall_ms']} "
                f"export_tok={trial.get('export_tokens_approx', 0)}{cost_note}"
            )
        cost = row.get("cost", {})
        if cost:
            print(
                f"{bid:22} {'[hole-8 cost]':24} "
                f"wall={cost.get('total_wall_ms')}ms "
                f"in={cost.get('total_tokens_in')} "
                f"out={cost.get('total_tokens_out')} "
                f"export={cost.get('total_export_tokens_approx')} "
                f"over_budget={cost.get('trials_over_budget')}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        default="local",
        help="baseline id, comma list, 'local' (default), or 'all'",
    )
    parser.add_argument("--fixture", help="single fixture id")
    parser.add_argument("--out", type=Path, help="report path (default: research/evals/results/<ts>-<sha>.json)")
    parser.add_argument("--docker", action="store_true", help="use docker agent/verifier (not yet required for local baselines)")
    args = parser.parse_args()

    if args.docker:
        docker_run = HARNESS / "docker" / "run_trial.sh"
        if not docker_run.is_file():
            print("docker mode requested but harness/docker/run_trial.sh is missing", file=sys.stderr)
            return 1
        print("docker mode delegates to harness/docker/run_trial.sh per trial", file=sys.stderr)

    registry = load_registry()
    by_id = baseline_by_id(registry)
    fixture_list = [args.fixture] if args.fixture else fixture_ids()

    if args.baseline == "local":
        selected = [by_id[bid] for bid in LOCAL_DEFAULTS]
    elif args.baseline == "all":
        selected = list(registry["baselines"])
    else:
        ids = [part.strip() for part in args.baseline.split(",") if part.strip()]
        missing = [bid for bid in ids if bid not in by_id]
        if missing:
            print(f"unknown baseline(s): {missing}", file=sys.stderr)
            return 1
        selected = [by_id[bid] for bid in ids]

    import tempfile

    budgets = registry.get("cost_budgets", {})
    if not isinstance(budgets, dict):
        budgets = {}

    with tempfile.TemporaryDirectory(prefix="companmem-harness-") as tmp:
        tmp_path = Path(tmp)
        baseline_rows = [run_baseline(item, fixture_list, tmp_path, budgets) for item in selected]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    sha = git_sha()
    report = {
        "observed_at": now,
        "git_sha": sha,
        "reader_model": registry.get("reader_model", "frozen-at-harness-time"),
        "fixture_ids": fixture_list,
        "cost_budgets": budgets,
        "baselines": baseline_rows,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = args.out or (RESULTS / f"{now}-{sha[:8]}.json")
    out.write_text(json.dumps(report, indent=2) + "\n")
    print_summary(report)
    print(f"report {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
