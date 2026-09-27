from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from crucible.metrics import aggregate
from crucible.schema import RunResult, Specimen


def _crucible_version() -> str:
    try:
        from importlib.metadata import version
        return version("persona-crucible")
    except Exception:
        from crucible import __version__
        return __version__


def _held_fraction(results: list[RunResult], axis: str) -> float:
    if not results:
        return 0.0
    broke = sum(r.break_turn is not None and axis in r.break_axes for r in results)
    return 1 - broke / len(results)


def _serialize_turn(t):
    return {"index": t.index, "role": t.role, "tactic": t.tactic,
            "identity": t.identity.value if t.identity else None,
            "stance": t.stance.value if t.stance else None,
            "content": t.content}


def _break_tactic(r):
    if r.break_turn is None:
        return None
    for t in r.turns:
        if t.index == r.break_turn - 1:
            return t.tactic
    return None


def _serialize_run(r, spec=None):
    d = {"model": r.model, "specimen_id": r.specimen_id,
         "break_turn": r.break_turn, "break_axes": r.break_axes,
         "faithfulness": r.faithfulness.value if r.faithfulness else "na",
         "turns": [_serialize_turn(t) for t in r.turns]}
    if spec is not None:
        d.update({"persona_name": spec.persona.name,
                  "identity": spec.persona.identity,
                  "stance": spec.stance.proposition,
                  "domain": spec.domain,
                  "break_tactic": _break_tactic(r) if r.break_turn is not None else None})
    return d


def build_report(results: list[RunResult], horizon: int | None = None,
                 specimens: list[Specimen] | None = None) -> dict:
    # No explicit horizon -> reflect what the runs were actually scored against
    # (the largest per-run budget), and let the leaderboard use each run's own.
    display_horizon = (horizon if horizon is not None
                       else max((r.horizon for r in results), default=12))
    smap = {s.id: s for s in (specimens or [])}
    models = sorted({r.model for r in results})
    separability = []
    for m in models:
        rs = [r for r in results if r.model == m]
        separability.append({"model": m,
                             "x": _held_fraction(rs, "stance"),
                             "y": _held_fraction(rs, "identity")})
    default_run = None
    if results:
        fractured = [r for r in results if r.break_turn is not None]
        default_run = fractured[0] if fractured else results[0]
    return {"leaderboard": aggregate(results, horizon),
            "separability": separability,
            "horizon": display_horizon,
            "log": _serialize_run(default_run, smap.get(default_run.specimen_id))
                   if default_run is not None else None,
            "logs": [_serialize_run(r, smap.get(r.specimen_id)) for r in results],
            "generated_from": len(results),
            "meta": {"crucible_version": _crucible_version(),
                     "generated_at": datetime.now(UTC).isoformat(),
                     "run_count": len(results),
                     "models": models,
                     "horizon": display_horizon}}


def write_report(results: list[RunResult], out_dir: str | Path,
                 horizon: int | None = None,
                 specimens: list[Specimen] | None = None) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data_path = out_dir / "data.json"
    data_path.write_text(
        json.dumps(build_report(results, horizon, specimens), indent=2))
    return data_path
