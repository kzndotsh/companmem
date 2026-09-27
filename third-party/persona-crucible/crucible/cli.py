from __future__ import annotations

import argparse
import asyncio
import importlib
import logging
from pathlib import Path

from crucible.api import run_benchmark
from crucible.report import write_report
from crucible.store import append_run, load_specimens, read_runs


def _load_factory(dotted: str | None):
    if not dotted:
        return None
    module, name = dotted.rsplit(".", 1)
    return getattr(importlib.import_module(module), name)


async def _run(args) -> int:
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Stream each run to disk as it finishes: a crash mid-grid keeps completed runs.
    with out.open("w", encoding="utf-8") as fh:
        results = await run_benchmark(
            specimens=args.personas,
            target_models=args.models,
            judge_model=args.judge_model,
            adversary_model=args.adversary_model,
            base_url=args.base_url,
            transport_factory=_load_factory(args.transport_factory),
            max_turns=args.max_turns,
            concurrency=args.concurrency,
            target_temperature=args.temperature,
            seed=args.seed,
            on_result=lambda r: append_run(fh, r),
        )
    print(f"wrote {len(results)} runs -> {args.out}")
    return 0


def _report(args) -> int:
    specimens = load_specimens(args.personas) if args.personas else None
    write_report(read_runs(args.runs), args.out, specimens=specimens)
    print(f"wrote report -> {args.out}/data.json")
    return 0


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(prog="crucible")
    sub = parser.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run")
    r.add_argument("--models", required=True)
    r.add_argument("--personas", required=True)
    r.add_argument("--judge-model", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--transport-factory", default=None)
    r.add_argument("--adversary-model", default=None)
    r.add_argument("--base-url", default=None)
    r.add_argument("--max-turns", type=int, default=None)
    r.add_argument("--concurrency", type=int, default=8)
    r.add_argument("--temperature", type=float, default=0.7,
                   help="target model sampling temperature")
    r.add_argument("--seed", type=int, default=None,
                   help="sampling seed forwarded to the backend for reproducibility")

    rep = sub.add_parser("report")
    rep.add_argument("--runs", required=True)
    rep.add_argument("--out", required=True)
    rep.add_argument("--personas", default=None)

    args = parser.parse_args(argv)
    if args.cmd == "run":
        return asyncio.run(_run(args))
    return _report(args)


if __name__ == "__main__":
    raise SystemExit(main())
