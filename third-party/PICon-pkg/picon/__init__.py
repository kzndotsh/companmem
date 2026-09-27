"""PICON: Persona Interview & CONsistency evaluation."""

from picon.api import run, interview, evaluate, run_interview, run_evaluation, PiconResult
from picon.components import (
    Questioner,
    EntityExtractor,
    WebSearch,
    Evaluator,
    Interviewee,
    InterrogationSimulation,
)

__version__ = "0.1.0"
__all__ = [
    # High-level API
    "run",
    "interview",
    "evaluate",
    "run_interview",
    "run_evaluation",
    "PiconResult",
    # Component classes
    "Questioner",
    "EntityExtractor",
    "WebSearch",
    "Evaluator",
    "Interviewee",
    "InterrogationSimulation",
]
