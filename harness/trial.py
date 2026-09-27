"""Trial result dataclasses and RunReport.

All serialization goes through to_dict() chains so enum values are rendered
as strings. dataclasses.asdict() is NOT used — it does not serialize Enum
members as their .value strings.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from harness.artifacts import Artifacts
from harness.scorer import Scorer


class TrialStatus(Enum):
    OK = "ok"
    INFRA_ERROR = "infra_error"
    SKIPPED = "skipped"


_BEHAVIOR_LABELS: dict[str, str] = {
    "b0": "stable self",
    "b1": "relational texture",
    "b2": "emotional responsiveness",
    "b3": "knows who you are now",
    "b4": "emotionally appropriate surface",
    "b5": "appropriate silence",
    "b6": "held, not processed",
    "b7": "inspectable and correctable",
    "b8": "survives updates",
}

_BEHAVIOR_ORDER = ["b0", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8"]


def _behavior_header(behavior: str | None) -> str:
    if behavior is None:
        label = "(no behavior)"
    else:
        label = f"{behavior}: {_BEHAVIOR_LABELS.get(behavior, behavior)}"
    fill = "─" * max(0, 56 - len(label) - 4)
    return f"── {label} {fill}"


@dataclass
class TrialResult:
    fixture_id: str
    fixture_hash: str
    status: TrialStatus
    resolved: bool
    fail_to_pass: bool
    pass_to_pass: bool
    predicate_details: list[str]
    judge_score: float | None
    judge_model: str | None
    wall_ms: int
    tokens_in: int
    tokens_out: int
    memory_tokens: int
    export_tokens_approx: int
    cost_flags: list[str]
    artifacts_path: str  # relative path, for regrading
    error: str | None
    behavior: str | None = None  # populated from FixtureMeta; None for old reports
    run_index: int = 0  # 0-based; default keeps existing single-run reports valid

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture_id": self.fixture_id,
            "fixture_hash": self.fixture_hash,
            "status": self.status.value,  # enum → string
            "resolved": self.resolved,
            "fail_to_pass": self.fail_to_pass,
            "pass_to_pass": self.pass_to_pass,
            "predicate_details": self.predicate_details,
            "judge_score": self.judge_score,
            "judge_model": self.judge_model,
            "wall_ms": self.wall_ms,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "memory_tokens": self.memory_tokens,
            "export_tokens_approx": self.export_tokens_approx,
            "cost_flags": self.cost_flags,
            "artifacts_path": self.artifacts_path,
            "error": self.error,
            "behavior": self.behavior,
            "run_index": self.run_index,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TrialResult:
        return cls(
            fixture_id=str(d["fixture_id"]),
            fixture_hash=str(d["fixture_hash"]),
            status=TrialStatus(d["status"]),
            resolved=bool(d["resolved"]),
            fail_to_pass=bool(d["fail_to_pass"]),
            pass_to_pass=bool(d["pass_to_pass"]),
            predicate_details=list(d.get("predicate_details", [])),
            judge_score=d.get("judge_score"),
            judge_model=d.get("judge_model"),
            wall_ms=int(d["wall_ms"]),
            tokens_in=int(d["tokens_in"]),
            tokens_out=int(d["tokens_out"]),
            memory_tokens=int(d["memory_tokens"]),
            export_tokens_approx=int(d["export_tokens_approx"]),
            cost_flags=list(d.get("cost_flags", [])),
            artifacts_path=str(d["artifacts_path"]),
            error=d.get("error"),
            behavior=d.get("behavior"),
            run_index=int(d.get("run_index", 0)),
        )


@dataclass
class BaselineResult:
    baseline_id: str
    title: str
    trials: list[TrialResult]
    resolved_count: int
    runnable_count: int
    fixture_count: int
    total_wall_ms: int
    total_tokens_in: int
    total_tokens_out: int
    total_memory_tokens: int
    tokens_per_resolved: int | None  # (total_tokens_in + total_tokens_out) // resolved_count
    resolved_by_behavior: dict[str, list[int]]  # code → [resolved, runnable] fixture-level counts
    pass_at_k: float | None  # None when n == 1
    pass_k: float | None  # None when n == 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_id": self.baseline_id,
            "title": self.title,
            "trials": [t.to_dict() for t in self.trials],
            "resolved_count": self.resolved_count,
            "runnable_count": self.runnable_count,
            "fixture_count": self.fixture_count,
            "total_wall_ms": self.total_wall_ms,
            "total_tokens_in": self.total_tokens_in,
            "total_tokens_out": self.total_tokens_out,
            "total_memory_tokens": self.total_memory_tokens,
            "tokens_per_resolved": self.tokens_per_resolved,
            "resolved_by_behavior": self.resolved_by_behavior,
            "pass_at_k": self.pass_at_k,
            "pass_k": self.pass_k,
        }

    @classmethod
    def from_trials(
        cls,
        baseline_id: str,
        title: str,
        trials: list[TrialResult],
    ) -> BaselineResult:
        """Aggregate trial results. Only TrialStatus.OK trials contribute to sums."""
        ok = [t for t in trials if t.status == TrialStatus.OK]
        resolved = [t for t in ok if t.resolved]
        total_in = sum(t.tokens_in for t in ok)
        total_out = sum(t.tokens_out for t in ok)
        tokens_per_resolved = (total_in + total_out) // len(resolved) if resolved else None

        # --- per-behavior fixture-level counts and pass@k / pass^k ---

        # Group all runs for each fixture; track the behavior per fixture.
        # Unconditionally overwrite with non-None so a SKIPPED/INFRA_ERROR trial
        # with behavior=None arriving before the OK trial doesn't win.
        fixture_runs: dict[str, list[TrialResult]] = defaultdict(list)
        fixture_behavior: dict[str, str | None] = {}
        for t in trials:
            fixture_runs[t.fixture_id].append(t)
            if t.behavior is not None:
                fixture_behavior[t.fixture_id] = t.behavior  # always overwrite; prefer non-None
            else:
                fixture_behavior.setdefault(t.fixture_id, None)  # only if not yet set

        # Fixture-level resolution: a fixture is resolved iff every OK run resolved.
        beh_resolved: dict[str, int] = defaultdict(int)
        beh_runnable: dict[str, int] = defaultdict(int)
        for fid, runs in fixture_runs.items():
            beh = fixture_behavior.get(fid)
            if beh is None:
                continue
            ok_runs = [r for r in runs if r.status == TrialStatus.OK]
            if not ok_runs:
                continue  # no OK trial → not in denominator
            beh_runnable[beh] += 1
            if all(r.resolved for r in ok_runs):
                beh_resolved[beh] += 1

        resolved_by_behavior: dict[str, list[int]] = {
            beh: [beh_resolved[beh], beh_runnable[beh]]
            for beh in beh_runnable
        }

        # Determine N from trial data (inference source, not manifest).
        n = max((t.run_index for t in trials), default=0) + 1

        if n == 1:
            pass_at_k: float | None = None
            pass_k: float | None = None
        else:
            eligible = {
                fid for fid, runs in fixture_runs.items()
                if any(r.status == TrialStatus.OK for r in runs)
            }
            denom = len(eligible)
            if denom == 0:
                pass_at_k = None
                pass_k = None
            else:
                at_k_count = sum(
                    1 for fid in eligible
                    if any(
                        r.resolved for r in fixture_runs[fid]
                        if r.status == TrialStatus.OK
                    )
                )
                k_count = sum(
                    1 for fid in eligible
                    if all(
                        r.resolved for r in fixture_runs[fid]
                        if r.status == TrialStatus.OK
                    )
                )
                pass_at_k = at_k_count / denom
                pass_k = k_count / denom

        return cls(
            baseline_id=baseline_id,
            title=title,
            trials=trials,
            # fixture_count = all trials regardless of status
            fixture_count=len(trials),
            # runnable_count = trials that ran without error (not SKIPPED/INFRA_ERROR)
            runnable_count=len(ok),
            # resolved_count = trials that passed all predicates
            resolved_count=len(resolved),
            total_wall_ms=sum(t.wall_ms for t in ok),
            total_tokens_in=total_in,
            total_tokens_out=total_out,
            total_memory_tokens=sum(t.memory_tokens for t in ok),
            tokens_per_resolved=tokens_per_resolved,
            resolved_by_behavior=resolved_by_behavior,
            pass_at_k=pass_at_k,
            pass_k=pass_k,
        )


@dataclass
class RunReport:
    run_id: str
    observed_at: str
    scored_at: str
    git_sha: str
    fixture_ids: list[str]
    baselines: list[BaselineResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "observed_at": self.observed_at,
            "scored_at": self.scored_at,
            "git_sha": self.git_sha,
            "fixture_ids": self.fixture_ids,
            "baselines": [b.to_dict() for b in self.baselines],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def print_summary(self) -> None:
        """Print a human-readable summary table to stdout."""

        def _row(baseline_id: str, t: TrialResult) -> None:
            if t.status == TrialStatus.OK:
                mark = "PASS" if t.resolved else "FAIL"
            elif t.status == TrialStatus.SKIPPED:
                mark = "SKIPPED"
            else:
                mark = "INFRA_ERROR"
            flags = ",".join(t.cost_flags) if t.cost_flags else "-"
            print(
                f"{baseline_id:24} {t.fixture_id:28} {mark:12} "
                f"f2p={t.fail_to_pass} p2p={t.pass_to_pass} "
                f"wall_ms={t.wall_ms} flags={flags}"
            )

        for bl in self.baselines:
            pairs: list[tuple[str, TrialResult]] = [
                (bl.baseline_id, t) for t in bl.trials
            ]

            # If no trial carries a behavior, fall back to flat output
            if not any(t.behavior is not None for _, t in pairs):
                for baseline_id, t in pairs:
                    _row(baseline_id, t)
            else:
                # Group by behavior, preserving defined order; None group last
                groups: dict[str | None, list[tuple[str, TrialResult]]] = {}
                for beh in _BEHAVIOR_ORDER:
                    groups[beh] = []
                groups[None] = []

                for baseline_id, t in pairs:
                    key = t.behavior if t.behavior in groups else None
                    groups[key].append((baseline_id, t))

                for beh in [*_BEHAVIOR_ORDER, None]:
                    rows = sorted(groups[beh], key=lambda p: (p[0], p[1].fixture_id))
                    if not rows:
                        continue
                    print(_behavior_header(beh))
                    for baseline_id, t in rows:
                        _row(baseline_id, t)

            # Summary line — branch on pass_at_k is not None rather than recomputing N
            beh_parts = "  ".join(
                f"{code}: {bl.resolved_by_behavior[code][0]}/{bl.resolved_by_behavior[code][1]}"
                for code in _BEHAVIOR_ORDER
                if code in bl.resolved_by_behavior
            )
            if bl.pass_at_k is None:
                # N == 1: per-behavior counts + total
                total_part = f"total: {bl.resolved_count}/{bl.runnable_count}"
                parts = f"{beh_parts}  {total_part}" if beh_parts else total_part
                print(parts)
            else:
                # N > 1: combined pass^k line; N inferred only for label formatting
                n = max((t.run_index for t in bl.trials), default=0) + 1
                pak = f"pass@{n}={bl.pass_at_k:.2f}"
                pk = f"pass^{n}={bl.pass_k:.2f}" if bl.pass_k is not None else f"pass^{n}=n/a"
                parts = f"{bl.baseline_id}   {pak}  {pk}  {beh_parts}"
                print(parts.strip())

    @classmethod
    def rescore(cls, artifacts_root: Path, fixtures_root: Path) -> RunReport:
        """Re-score a prior run's artifacts against current predicates.

        Reads run_manifest.json and report.json from artifacts_root.
        Only TrialStatus.OK trials are re-scored; SKIPPED/INFRA_ERROR are
        carried forward unchanged (no artifacts exist for them).
        """
        manifest_path = artifacts_root / "run_manifest.json"
        if not manifest_path.is_file():
            msg = f"run_manifest.json not found in {artifacts_root}"
            raise FileNotFoundError(msg)
        try:
            manifest: dict[str, Any] = json.loads(manifest_path.read_text())
        except json.JSONDecodeError as exc:
            msg = f"run_manifest.json is malformed: {exc}"
            raise ValueError(msg) from exc

        report_path = artifacts_root / "report.json"
        if not report_path.is_file():
            msg = f"report.json not found in {artifacts_root}"
            raise FileNotFoundError(msg)
        try:
            old_report: dict[str, Any] = json.loads(report_path.read_text())
        except json.JSONDecodeError as exc:
            msg = f"report.json is malformed: {exc}"
            raise ValueError(msg) from exc

        # Index original trials by (baseline_id, fixture_id, run_index) for O(1) lookup.
        # run_index defaults to 0 so existing single-run reports round-trip correctly.
        original_trials: dict[tuple[str, str, int], dict[str, Any]] = {}
        for bl_dict in old_report.get("baselines", []):
            bid = str(bl_dict["baseline_id"])
            for t_dict in bl_dict.get("trials", []):
                fid = str(t_dict["fixture_id"])
                run_idx = int(t_dict.get("run_index", 0))
                original_trials[(bid, fid, run_idx)] = t_dict

        cost_budgets: dict[str, int] = manifest.get("cost_budgets", {})

        new_baselines: list[BaselineResult] = []
        for bl_entry in manifest.get("baselines", []):
            bid = str(bl_entry["baseline_id"])
            title = str(bl_entry.get("title", bid))
            new_trials: list[TrialResult] = []

            # Collect all (bid, fid, run_index) keys for this baseline, sorted for determinism
            keys_for_baseline = sorted(
                (bid2, fid2, ri)
                for (bid2, fid2, ri) in original_trials
                if bid2 == bid
            )

            for _, fid, run_idx in keys_for_baseline:
                key = (bid, fid, run_idx)
                orig = original_trials.get(key)
                if orig is None:
                    continue

                orig_trial = TrialResult.from_dict(orig)

                if orig_trial.status != TrialStatus.OK:
                    # No artifacts to re-score; carry forward unchanged
                    new_trials.append(orig_trial)
                    continue

                # Reconstruct artifact directory from stored path.
                # artifacts_path is relative to results_root.parent.
                # artifacts_root = results_root / run_id, so:
                #   artifacts_root.parent         = results_root
                #   artifacts_root.parent.parent  = results_root.parent  ← correct base
                art_dir = artifacts_root.parent.parent / orig_trial.artifacts_path
                artifacts = Artifacts(art_dir)
                pred_path = fixtures_root / str(fid) / "tests" / "predicates.json"
                scorer = Scorer(pred_path)
                result = scorer.score(artifacts)

                # Recompute cost_flags from manifest budgets
                cost_flags = _compute_cost_flags(
                    orig_trial.wall_ms,
                    orig_trial.export_tokens_approx,
                    cost_budgets,
                )

                new_trial = TrialResult(
                    fixture_id=orig_trial.fixture_id,
                    fixture_hash=orig_trial.fixture_hash,
                    status=orig_trial.status,
                    resolved=result.resolved,
                    fail_to_pass=result.fail_to_pass,
                    pass_to_pass=result.pass_to_pass,
                    predicate_details=result.predicate_details,
                    judge_score=result.judge_score,
                    judge_model=result.judge_model,
                    wall_ms=orig_trial.wall_ms,
                    tokens_in=orig_trial.tokens_in,
                    tokens_out=orig_trial.tokens_out,
                    memory_tokens=orig_trial.memory_tokens,
                    export_tokens_approx=orig_trial.export_tokens_approx,
                    cost_flags=cost_flags,
                    artifacts_path=orig_trial.artifacts_path,
                    error=orig_trial.error,
                    behavior=orig_trial.behavior,
                    run_index=orig_trial.run_index,
                )
                new_trials.append(new_trial)

            new_baselines.append(BaselineResult.from_trials(bid, title, new_trials))

        scored_at = datetime.now(UTC).isoformat()
        return cls(
            run_id=str(manifest["run_id"]),
            observed_at=str(old_report["observed_at"]),
            scored_at=scored_at,
            git_sha=str(old_report.get("git_sha", "unknown")),
            fixture_ids=list(old_report.get("fixture_ids", [])),
            baselines=new_baselines,
        )


def _compute_cost_flags(
    wall_ms: int,
    export_tokens_approx: int,
    cost_budgets: dict[str, int],
) -> list[str]:
    flags: list[str] = []
    wall_cap = cost_budgets.get("wall_ms_per_trial")
    export_cap = cost_budgets.get("export_tokens_approx_per_trial")
    if wall_cap is not None and wall_ms > wall_cap:
        flags.append("wall_ms_over_budget")
    if export_cap is not None and export_tokens_approx > export_cap:
        flags.append("export_tokens_over_budget")
    return flags
