"""
BC-Score Report Generator

Produces human-readable reports and machine-readable summaries from evaluation results.
"""

import json
from datetime import datetime
from typing import Optional

import numpy as np

from scoring.bc_score import BCScore, aggregate_scores


def _bar(score: float, width: int = 20) -> str:
    """Create a visual bar for terminal output."""
    filled = int(score * width)
    return "#" * filled + "-" * (width - filled)


def _grade(score: float) -> str:
    """Convert score to letter grade."""
    if score >= 0.9:
        return "A"
    elif score >= 0.8:
        return "A-"
    elif score >= 0.7:
        return "B+"
    elif score >= 0.6:
        return "B"
    elif score >= 0.5:
        return "C+"
    elif score >= 0.4:
        return "C"
    elif score >= 0.3:
        return "D"
    else:
        return "F"


def print_single_report(score: BCScore, model_name: str = "Unknown Model"):
    """Print a formatted BC-Score report for a single evaluation."""
    print()
    print("=" * 60)
    print(f"  ContinuityBench · BC-Score Report")
    print(f"  Model: {model_name}")
    print(f"  Date:  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()

    composite = score.composite
    print(f"  COMPOSITE BC-SCORE:  {composite:.3f}  [{_grade(composite)}]")
    print(f"  {_bar(composite, 40)}")
    print()

    print("  Per-Dimension Scores:")
    print("  " + "-" * 56)

    for dim_name, dim_score in [
        ("Identity    ", score.identity),
        ("Goal        ", score.goal),
        ("Abstraction ", score.abstraction),
        ("Style       ", score.style),
    ]:
        conf_str = f"(conf: {dim_score.confidence:.2f})"
        print(
            f"  {dim_name} {_bar(dim_score.score)} "
            f"{dim_score.score:.3f} [{_grade(dim_score.score)}] {conf_str}"
        )

    print()
    print(f"  Weakest Dimension: {score.min_dimension.dimension.upper()}")
    print(f"  Mean Judge Agreement: {score.mean_confidence:.3f}")

    if score.auxiliary:
        print()
        print("  Auxiliary Metrics:")
        print("  " + "-" * 56)
        print(f"  NPC Fallback Rate:      {score.auxiliary.npc_fallback_rate:.1%}")
        print(f"  Goal Recovery Latency:  {score.auxiliary.goal_recovery_latency:.1f} turns")
        print(f"  Tone Variance:          {score.auxiliary.tone_variance:.4f}")
        print(f"  Self-Inconsistency:     {score.auxiliary.self_inconsistency_rate:.1%}")

    # Evidence summary
    print()
    print("  Key Evidence:")
    print("  " + "-" * 56)
    for dim in [score.identity, score.goal, score.abstraction, score.style]:
        if dim.evidence:
            print(f"  [{dim.dimension.upper()}]")
            for ev in dim.evidence[:3]:
                print(f"    · {ev}")
            print()

    print("=" * 60)
    print()


def print_aggregate_report(
    scores: list[BCScore],
    model_name: str = "Unknown Model",
    weights: Optional[dict] = None,
    per_stressor: Optional[dict] = None,
    num_runs: int = 1,
    metadata: Optional[dict] = None,
):
    """Print an aggregate report across multiple evaluations."""
    agg = aggregate_scores(scores, weights)
    meta = metadata or {}

    print()
    print("=" * 60)
    print(f"  ContinuityBench · Aggregate Report")
    print(f"  Model: {model_name}")
    print(f"  Evaluations: {agg['n_evaluations']}")
    if num_runs > 1:
        print(f"  Runs per stressor: {num_runs}")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if meta.get("judge_model"):
        ref_label = "" if meta.get("is_reference_judge", True) else " [non-reference]"
        print(f"  Judge: {meta['judge_model']}{ref_label}")
    print("=" * 60)
    print()

    c = agg["composite"]
    print(f"  COMPOSITE BC-SCORE:  {c['mean']:.3f} ± {c['std']:.3f}  [{_grade(c['mean'])}]")
    print(f"  Range: [{c['min']:.3f}, {c['max']:.3f}]")
    print(f"  {_bar(c['mean'], 40)}")
    print()

    print("  Per-Dimension Breakdown:")
    print("  " + "-" * 56)
    print(f"  {'Dimension':<14} {'Mean':>6} {'± Std':>7} {'Min':>6} {'Max':>6} {'Grade':>6}")
    print("  " + "-" * 56)
    for dim_name in ("identity", "goal", "abstraction", "style"):
        d = agg["dimensions"][dim_name]
        print(
            f"  {dim_name.capitalize():<14} {d['mean']:>6.3f} {d['std']:>6.3f} "
            f"{d['min']:>6.3f} {d['max']:>6.3f} {_grade(d['mean']):>6}"
        )
    print()

    # Per-stressor breakdown
    if per_stressor:
        print("  Per-Stressor Breakdown:")
        dims = ("identity", "goal", "abstraction", "style")
        if num_runs > 1:
            hdr = f"  {'Stressor':<16} {'Runs':>4}  {'Identity':>12} {'Goal':>12} {'Abstr.':>12} {'Style':>12} {'Composite':>12}"
        else:
            hdr = f"  {'Stressor':<16} {'Identity':>9} {'Goal':>9} {'Abstr.':>9} {'Style':>9} {'Composite':>10}"
        print("  " + "-" * (len(hdr) - 2))
        print(hdr)
        print("  " + "-" * (len(hdr) - 2))
        for sid in sorted(per_stressor.keys()):
            sc_list = per_stressor[sid]
            n = len(sc_list)
            dim_stats = {}
            for dim in dims:
                vals = [getattr(s, dim).score for s in sc_list]
                dim_stats[dim] = (float(np.mean(vals)), float(np.std(vals)))
            composites = [s.composite for s in sc_list]
            comp = (float(np.mean(composites)), float(np.std(composites)))
            if num_runs > 1:
                def _fmt(m, s): return f"{m:.3f}+/-{s:.3f}"
                print(
                    f"  {sid:<16} {n:>4}  "
                    f"{_fmt(*dim_stats['identity']):>12} {_fmt(*dim_stats['goal']):>12} "
                    f"{_fmt(*dim_stats['abstraction']):>12} {_fmt(*dim_stats['style']):>12} "
                    f"{_fmt(*comp):>12}"
                )
            else:
                print(
                    f"  {sid:<16} "
                    f"{dim_stats['identity'][0]:>9.3f} {dim_stats['goal'][0]:>9.3f} "
                    f"{dim_stats['abstraction'][0]:>9.3f} {dim_stats['style'][0]:>9.3f} "
                    f"{comp[0]:>10.3f}"
                )

        # High-variance warnings (only meaningful with multiple runs)
        if num_runs > 1:
            HIGH_VAR_THRESHOLD = 0.15
            warnings = []
            for sid, sc_list in per_stressor.items():
                for dim in ("identity", "goal", "abstraction", "style"):
                    vals = [getattr(s, dim).score for s in sc_list]
                    if float(np.std(vals)) >= HIGH_VAR_THRESHOLD:
                        warnings.append((sid, dim, float(np.std(vals)), float(np.mean(vals))))
            if warnings:
                print(f"  [!] High-Variance Stressors (std >= {HIGH_VAR_THRESHOLD}):")
                for sid, dim, std, mean in sorted(warnings, key=lambda x: -x[2]):
                    print(f"      {sid}  [{dim}]  mean={mean:.3f}  std={std:.3f}")
                print()

        print()

    print("=" * 60)
    print()


def save_json_report(
    scores: list[BCScore],
    model_name: str,
    output_path: str,
    metadata: Optional[dict] = None,
    weights: Optional[dict] = None,
    per_stressor: Optional[dict] = None,
    num_runs: int = 1,
):
    """Save evaluation results as JSON."""
    agg = aggregate_scores(scores, weights)

    # Compute per-stressor aggregates if provided
    per_stressor_agg = None
    if per_stressor:
        per_stressor_agg = {}
        dims = ("identity", "goal", "abstraction", "style")
        for sid, sc_list in per_stressor.items():
            entry = {"n_runs": len(sc_list)}
            for dim in dims:
                vals = [getattr(s, dim).score for s in sc_list]
                entry[dim] = {
                    "mean": round(float(np.mean(vals)), 4),
                    "std": round(float(np.std(vals)), 4),
                    "min": round(float(np.min(vals)), 4),
                    "max": round(float(np.max(vals)), 4),
                }
            composites = [s.composite for s in sc_list]
            entry["composite"] = {
                "mean": round(float(np.mean(composites)), 4),
                "std": round(float(np.std(composites)), 4),
                "min": round(float(np.min(composites)), 4),
                "max": round(float(np.max(composites)), 4),
            }
            per_stressor_agg[sid] = entry

    report = {
        "meta": {
            "benchmark": "ContinuityBench",
            "version": "0.1.0",
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "n_evaluations": len(scores),
            "num_runs": num_runs,
            **(metadata or {}),
        },
        "aggregate": agg,
        "individual": [s.to_dict() for s in scores],
    }
    if per_stressor_agg:
        report["per_stressor"] = per_stressor_agg

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Report saved to {output_path}")


def generate_report(
    scores: list[BCScore],
    model_name: str = "Unknown Model",
    output_path: Optional[str] = None,
    weights: Optional[dict] = None,
    per_stressor: Optional[dict] = None,
    num_runs: int = 1,
    metadata: Optional[dict] = None,
):
    """
    Generate and display a BC-Score report.

    If output_path is provided, also saves a JSON report.
    """
    if len(scores) == 1 and num_runs == 1:
        print_single_report(scores[0], model_name)
    else:
        print_aggregate_report(scores, model_name, weights, per_stressor=per_stressor,
                                num_runs=num_runs, metadata=metadata)

    if output_path:
        save_json_report(scores, model_name, output_path, metadata=metadata, weights=weights,
                         per_stressor=per_stressor, num_runs=num_runs)
