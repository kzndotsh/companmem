"""ContinuityBench Scoring Module

Provides BC-Score computation, LLM-as-Judge evaluation, and report generation.
"""

from scoring.bc_score import BCScore, DimensionScore
from scoring.judges import JudgeSystem
from scoring.report import generate_report

__all__ = ["BCScore", "DimensionScore", "JudgeSystem", "generate_report"]
