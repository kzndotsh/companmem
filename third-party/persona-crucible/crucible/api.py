"""High-level entry point: run the whole benchmark with one call.

This does the wiring the CLI does — build clients, judges, and an adversary per
specimen — so library users don't have to assemble them by hand. The CLI's `run`
subcommand is a thin shell around `run_benchmark`.
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Iterable
from pathlib import Path

from crucible.adversary import Adversary
from crucible.client import LLMClient, Transport
from crucible.judges import IdentityJudge, StanceJudge
from crucible.probe import FaithfulnessProbe
from crucible.runner import run_specimen
from crucible.schema import RunResult, Specimen
from crucible.store import load_specimens

TransportFactory = Callable[[str], Transport]
ResultCallback = Callable[[RunResult], None]

logger = logging.getLogger("crucible.api")


def _resolve_specimens(specimens: str | Path | Iterable[Specimen]) -> list[Specimen]:
    if isinstance(specimens, (str, Path)):
        return load_specimens(specimens)
    return list(specimens)


async def run_benchmark(
    specimens: str | Path | Iterable[Specimen],
    target_models: str | Iterable[str],
    judge_model: str,
    *,
    adversary_model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    transport_factory: TransportFactory | None = None,
    max_turns: int | None = None,
    concurrency: int = 8,
    on_result: ResultCallback | None = None,
    target_temperature: float = 0.7,
    seed: int | None = None,
) -> list[RunResult]:
    """Run every ``target_model × specimen`` pair and return their ``RunResult``s.

    ``specimens`` may be a directory/file path (loaded via ``load_specimens``) or an
    iterable of ``Specimen`` objects. ``target_models`` may be a comma-separated
    string or an iterable of model names. ``adversary_model`` defaults to each
    target; ``max_turns`` (when given) overrides every specimen's budget.
    ``transport_factory`` maps a model name to a fake transport for offline/tests.
    ``concurrency`` bounds how many ``(model, specimen)`` runs are in flight at once.
    ``on_result`` is invoked with each ``RunResult`` as it completes (e.g. to append
    it to disk immediately, so a crash mid-grid keeps the finished runs). A run that
    raises is logged and dropped from the results rather than aborting the whole grid.
    """
    specs = _resolve_specimens(specimens)
    if max_turns is not None:
        for spec in specs:
            spec.adversary.max_turns = max_turns
    if isinstance(target_models, str):
        target_models = target_models.split(",")
    else:
        target_models = list(target_models)

    clients: dict[str, LLMClient] = {}

    def _client(model: str) -> LLMClient:
        # One client per model name -> shared connection pool across all its runs.
        if model not in clients:
            clients[model] = LLMClient(
                model, base_url=base_url, api_key=api_key, seed=seed,
                transport=transport_factory(model) if transport_factory else None)
        return clients[model]

    judge_client = _client(judge_model)
    identity_judge = IdentityJudge(judge_client)
    stance_judge = StanceJudge(judge_client)
    probe = FaithfulnessProbe(judge_client, stance_judge)

    sem = asyncio.Semaphore(concurrency)

    async def _run_pair(model: str, spec: Specimen) -> RunResult | None:
        async with sem:
            adversary = Adversary(_client(adversary_model or model), spec)
            try:
                result = await run_specimen(
                    spec, _client(model), adversary, identity_judge, stance_judge,
                    probe, target_temperature=target_temperature)
            except Exception:
                logger.exception("run failed for model=%s specimen=%s -- skipping",
                                 model, spec.id)
                return None
            if on_result is not None:
                on_result(result)
            return result

    # model-major, specimen-minor order; gather preserves it regardless of timing
    pairs = [(m, s) for m in target_models for s in specs]
    outcomes = await asyncio.gather(*(_run_pair(m, s) for m, s in pairs))
    return [r for r in outcomes if r is not None]
