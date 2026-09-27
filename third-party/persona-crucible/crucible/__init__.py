"""Crucible — a benchmark for the stability of LLM personas under social pressure.

Public API. The one-call entry point is :func:`run_benchmark`; the lower-level
building blocks (clients, judges, the per-specimen loop) are re-exported for callers
who want to assemble a run themselves.
"""
__version__ = "0.1.1"

from crucible.adversary import Adversary
from crucible.api import run_benchmark
from crucible.client import LLMClient
from crucible.judges import IdentityJudge, StanceJudge
from crucible.metrics import aggregate
from crucible.probe import FaithfulnessProbe
from crucible.report import build_report, write_report
from crucible.runner import run_specimen
from crucible.schema import (
    AdversaryConfig,
    AdversaryMove,
    FaithfulnessVerdict,
    IdentityVerdict,
    Persona,
    RunResult,
    Specimen,
    Stance,
    StanceVerdict,
    Turn,
)
from crucible.store import load_specimens, read_runs, write_runs

__all__ = [
    "run_benchmark",
    "LLMClient",
    "Adversary",
    "IdentityJudge",
    "StanceJudge",
    "FaithfulnessProbe",
    "run_specimen",
    "build_report",
    "write_report",
    "aggregate",
    "load_specimens",
    "read_runs",
    "write_runs",
    "Specimen",
    "Persona",
    "Stance",
    "Turn",
    "RunResult",
    "AdversaryConfig",
    "AdversaryMove",
    "IdentityVerdict",
    "StanceVerdict",
    "FaithfulnessVerdict",
]
