"""Run one stressor selection across several models, with cost guardrails.

A sweep will not walk from cheap models into expensive ones on its own. Models
flagged expensive in run_eval.EXPENSIVE_PREFIXES sit behind a checkpoint: the
sweep stops, reports what it has spent so far, and requires --confirm-expensive
to continue. Without that flag it exits cleanly having run only the cheap tier.

    # see the plan and the bill, run nothing
    python scripts/sweep.py --models cheap.txt --stressor-ids ah_v2_001 --dry-run

    # run the cheap tier, stop at the first expensive model
    python scripts/sweep.py --models models.txt --leaderboard --max-estimated-usd 5

--max-estimated-usd gates on a pre-flight ESTIMATE. It is not a spend cap: it
cannot bound a run already in progress. Use provider-side spend limits for that.
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from run_eval import (JUDGE_DIMENSIONS, estimate_cost, is_expensive,  # noqa: E402
                      judge_calls_per_item, load_stressors, STRESSOR_FILES)

import yaml  # noqa: E402


def read_models(path):
    """One `provider/model[<TAB>Display Name]` per line; # comments allowed."""
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split("\t") if p.strip()] or [line]
            out.append((parts[0], parts[1] if len(parts) > 1 else parts[0]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True, help="file listing models to sweep")
    ap.add_argument("--stressor-ids")
    ap.add_argument("--leaderboard", action="store_true")
    ap.add_argument("--config", default="configs/default")
    ap.add_argument("--output", default="results/sweep/")
    ap.add_argument("--num-runs", type=int, default=1)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--max-estimated-usd", type=float, default=None,
                    help="estimated-cost gate: refuse to START if the pre-flight estimate for the reachable models exceeds this. Not a spend cap.")
    ap.add_argument("--judge-mode", default="traditional")
    ap.add_argument("--confirm-expensive", action="store_true",
                    help="permit models flagged expensive; without it the sweep stops at the checkpoint")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    config = yaml.safe_load(open(args.config, encoding="utf-8"))
    ids = args.stressor_ids
    if args.leaderboard:
        ids = ",".join(config["stressors"]["leaderboard_ids"])
    if not ids:
        ap.error("pass --stressor-ids or --leaderboard")

    wanted = {s.strip() for s in ids.split(",")}
    stressors = [s for s in load_stressors(list(STRESSOR_FILES), 100) if s["id"] in wanted]
    if not stressors:
        sys.exit("No stressors matched.")

    models = read_models(args.models)
    judge_model = config.get("scoring", {}).get("judge_model", "openai/gpt-5-mini")
    judge_passes = config.get("scoring", {}).get("judge_passes", 3)

    plan, total = [], 0.0
    for spec, name in models:
        est = estimate_cost(stressors, spec, num_runs=args.num_runs,
                            judge_model=judge_model, judge_passes=judge_passes,
                            judge_mode=args.judge_mode)
        plan.append((spec, name, est, is_expensive(spec)))
        total += est["total_usd_upper"]

    cheap_total = sum(e["total_usd_upper"] for _, _, e, exp in plan if not exp)
    n_exp = sum(1 for *_, exp in plan if exp)

    print("Sweep plan")
    print("  models:            %d  (%d flagged expensive)" % (len(models), n_exp))
    print("  stressor variants: %d" % len(stressors))
    per_item_exp, _ = judge_calls_per_item(args.judge_mode, judge_passes)
    print("  conversations:     %d" % (len(stressors) * args.num_runs * len(models)))
    print("  judge calls:       %d  (mode=%s, %d passes x %d dims)"
          % (len(stressors) * args.num_runs * per_item_exp * len(models),
             args.judge_mode, judge_passes, JUDGE_DIMENSIONS))
    print("\n  %-42s %10s  %s" % ("model", "est. USD", "tier"))
    for spec, name, est, exp in plan:
        print("  %-42s %10.2f  %s" % (spec[:41], est["total_usd_upper"], "EXPENSIVE" if exp else "cheap"))
    print("\n  cheap tier subtotal: $%.2f" % cheap_total)
    print("  full sweep total:    $%.2f   (planning estimate, not a quote)" % total)

    budget = args.max_estimated_usd
    reachable = total if args.confirm_expensive else cheap_total
    if budget is not None:
        print("  gate threshold:      $%.2f" % budget)
        if reachable > budget:
            print("\nEstimated-cost gate: refusing to start.")
            print("  reachable estimate $%.2f exceeds --max-estimated-usd $%.2f"
                  % (reachable, budget))
            print("  (pre-flight estimate gate, not a spend cap)")
            sys.exit(2)
    if not args.confirm_expensive and n_exp:
        print("\n  NOTE: %d expensive model(s) will NOT run. The sweep stops at the" % n_exp)
        print("        checkpoint. Re-run with --confirm-expensive to include them.")

    if args.dry_run:
        print("\nDry run - no API calls were made.")
        return

    ok, failed, spent = [], [], 0.0
    t0 = time.time()
    for i, (spec, name, est, exp) in enumerate(plan, 1):
        if exp and not args.confirm_expensive:
            print("\n" + "=" * 70)
            print("CHECKPOINT - stopping before expensive model: %s" % name)
            print("  spent so far (est.): $%.2f across %d model(s)" % (spent, len(ok)))
            print("  remaining expensive models would add an estimated $%.2f"
                  % sum(e["total_usd_upper"] for _, _, e, x in plan[i - 1:] if x))
            print("  re-run with --confirm-expensive to continue")
            print("=" * 70)
            break

        print("\n%s\n[%d/%d] %s  (est. $%.2f)\n%s"
              % ("=" * 70, i, len(plan), name, est["total_usd_upper"], "=" * 70), flush=True)
        cmd = [sys.executable, "run_eval.py", "--model", spec, "--stressor-ids", ids,
               "--model-name", name, "--output", args.output,
               "--workers", str(args.workers), "--num-runs", str(args.num_runs),
               "--config", args.config]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=3600)
            print("\n".join((p.stdout or "").strip().splitlines()[-5:]), flush=True)
            if p.returncode == 0:
                ok.append(name)
                spent += est["total_usd_upper"]
            else:
                failed.append((name, (p.stderr or "")[-300:]))
                print("!! FAILED rc=%d" % p.returncode, flush=True)
        except Exception as e:                                # keep the sweep alive
            failed.append((name, repr(e)))
            print("!! ERROR %r" % (e,), flush=True)

    print("\n%s\nDONE in %.1f min" % ("=" * 70, (time.time() - t0) / 60))
    print("succeeded: %d   failed: %d   estimated spend: $%.2f" % (len(ok), len(failed), spent))
    for n, e in failed:
        print("  FAILED %s: %s" % (n, e[:160]))
    print(json.dumps({"ok": ok, "failed": [f[0] for f in failed],
                      "estimated_usd": round(spent, 2)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
