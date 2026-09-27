"""Reproduce the significance analysis quoted in the README.

Every model is compared against every other by pairing per-stressor composite
means on the 26 leaderboard variants, which controls for stressor difficulty —
the dominant source of variance in BC-Score.

    python scripts/significance.py                 # summary vs the top model
    python scripts/significance.py --matrix        # full pairwise matrix
    python scripts/significance.py --vs "GPT-5.4"  # one model against the field
"""
import argparse
import glob
import json
import os
from math import sqrt

import numpy as np
from scipy import stats

RESULTS_GLOB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "results", "v3", "*_report.json")
ALPHA = 0.05


def load():
    """{model: {stressor_id: composite mean}} for every report with per-stressor data."""
    data = {}
    for path in glob.glob(RESULTS_GLOB):
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        per = d.get("per_stressor")
        if not per:
            continue
        data[d["meta"]["model"]] = {k: v["composite"]["mean"] for k, v in per.items()}
    return data


def paired(a, b):
    """Paired t-test on the stressors two models have in common."""
    common = sorted(set(a) & set(b))
    diffs = np.array([a[s] - b[s] for s in common])
    n = len(diffs)
    if n < 2:
        return None
    sd = diffs.std(ddof=1)
    if sd == 0:
        return dict(delta=float(diffs.mean()), t=0.0, p=1.0, n=n, sd=0.0)
    t = diffs.mean() / (sd / sqrt(n))
    return dict(delta=float(diffs.mean()), t=float(t),
                p=float(2 * (1 - stats.t.cdf(abs(t), n - 1))), n=n, sd=float(sd))


def holm(pvals):
    """Holm-Bonferroni step-down adjusted p-values, order preserved."""
    idx = sorted(range(len(pvals)), key=lambda i: pvals[i])
    k, adj, running = len(pvals), [0.0] * len(pvals), 0.0
    for rank, i in enumerate(idx):
        running = min(1.0, max(running, (k - rank) * pvals[i]))
        adj[i] = running
    return adj


def rank(data):
    return sorted(data, key=lambda m: -float(np.mean(list(data[m].values()))))


def resolution(data):
    """Smallest difference detectable at ALPHA, from the median paired SD."""
    order = rank(data)
    sds = []
    for i, A in enumerate(order):
        for B in order[i + 1:]:
            r = paired(data[A], data[B])
            if r:
                sds.append(r["sd"])
    sd = float(np.median(sds))
    n = 26
    crit = stats.t.ppf(1 - ALPHA / 2, n - 1)
    return sd, crit * sd / sqrt(n)


def report_vs(data, target):
    order = rank(data)
    others = [m for m in order if m != target]
    res = [paired(data[target], data[m]) for m in others]
    adj = holm([r["p"] for r in res])

    print(f"\nPaired against: {target}   ({len(others)} comparisons, Holm-adjusted)\n")
    print(f"{'model':<38}{'ΔBC':>9}{'t':>8}{'p':>9}{'Holm p':>9}  verdict")
    print("-" * 82)
    for m, r, pa in sorted(zip(others, res, adj), key=lambda x: -x[1]["delta"]):
        verdict = "lower" if pa < ALPHA else "not resolved"
        print(f"{m[:37]:<38}{r['delta']:>+9.4f}{r['t']:>+8.2f}{r['p']:>9.4f}{pa:>9.4f}  {verdict}")

    unresolved = [m for m, pa in zip(others, adj) if pa >= ALPHA]
    print(f"\n{len(unresolved)} of {len(others)} models cannot be separated from {target}:")
    for m in unresolved:
        print(f"  - {m}")


def report_matrix(data):
    order = rank(data)
    print("\nPairwise |t| (row vs column); * = uncorrected p < .05\n")
    w = 26
    print(" " * w + "".join(f"{i + 1:>6}" for i in range(len(order))))
    for i, A in enumerate(order):
        cells = []
        for B in order:
            if A == B:
                cells.append(f"{'—':>6}")
                continue
            r = paired(data[A], data[B])
            cells.append(f"{abs(r['t']):>5.2f}" + ("*" if r["p"] < ALPHA else " "))
        print(f"{i + 1:>2} {A[:22]:<23}" + "".join(cells))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", action="store_true", help="full pairwise |t| matrix")
    ap.add_argument("--vs", help="compare this model against all others")
    args = ap.parse_args()

    data = load()
    if not data:
        raise SystemExit("No reports with per_stressor data found.")

    order = rank(data)
    sd, mde = resolution(data)
    span = float(np.mean(list(data[order[0]].values())) - np.mean(list(data[order[12]].values()))) \
        if len(order) > 12 else float("nan")

    print(f"Models: {len(order)}   stressors: 26   alpha: {ALPHA}")
    print(f"Median paired SD: {sd:.4f}")
    print(f"Minimum detectable difference: {mde:.3f} BC-Score")
    if not np.isnan(span):
        print(f"Span of ranks 1-13: {span:.3f}  "
              f"({'inside' if span < mde else 'wider than'} the resolution limit)")

    if args.matrix:
        report_matrix(data)
    else:
        report_vs(data, args.vs or order[0])
