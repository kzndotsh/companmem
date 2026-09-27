"""
BC-Score: Behavioral Continuity Score Calculator

Computes per-dimension scores and composite BC-Score from judge evaluations.
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np


LOW_SIGNAL_THRESHOLD = 0.5  # confidence below this → low_signal flag


@dataclass
class DimensionScore:
    """Score for a single drift dimension."""
    dimension: str  # "identity", "goal", "abstraction", "style"
    score: float  # 0.0 - 1.0
    confidence: float  # inter-judge agreement
    evidence: list[str] = field(default_factory=list)  # key observations from judge
    is_primary: bool = True  # True if stressor targets this dimension
    low_signal: bool = False  # True if confidence < threshold on secondary dim

    def __post_init__(self):
        assert 0.0 <= self.score <= 1.0, f"Score must be 0-1, got {self.score}"
        assert self.dimension in ("identity", "goal", "abstraction", "style")
        # Auto-flag low signal on secondary dimensions
        if not self.is_primary and self.confidence < LOW_SIGNAL_THRESHOLD:
            self.low_signal = True


# Planned: not yet implemented in scoring pipeline
@dataclass
class AuxiliaryMetrics:
    """Auxiliary metrics beyond the four core dimensions."""
    npc_fallback_rate: float = 0.0      # template responses / total turns
    goal_recovery_latency: float = 0.0  # mean turns to resume after interruption
    tone_variance: float = 0.0          # std dev of style embeddings
    self_inconsistency_rate: float = 0.0  # contradictions / total claims


@dataclass
class BCScore:
    """Complete Behavioral Continuity Score for one evaluation run."""
    identity: DimensionScore
    goal: DimensionScore
    abstraction: DimensionScore
    style: DimensionScore
    auxiliary: Optional[AuxiliaryMetrics] = None

    # Default weights (can be overridden via config)
    DEFAULT_WEIGHTS = {
        "identity": 0.30,
        "goal": 0.25,
        "abstraction": 0.25,
        "style": 0.20,
    }

    @property
    def composite(self) -> float:
        """Compute weighted composite BC-Score."""
        return self.composite_with_weights(self.DEFAULT_WEIGHTS)

    def composite_with_weights(self, weights: dict[str, float]) -> float:
        """Compute composite score with custom weights."""
        assert abs(sum(weights.values()) - 1.0) < 0.01, "Weights must sum to 1.0"
        return (
            weights["identity"] * self.identity.score
            + weights["goal"] * self.goal.score
            + weights["abstraction"] * self.abstraction.score
            + weights["style"] * self.style.score
        )

    @property
    def composite_primary_only(self) -> float:
        """Composite score using only primary (targeted) dimensions.
        Redistributes weight proportionally among primary dimensions.
        Falls back to full composite if all dimensions are primary."""
        dims = [self.identity, self.goal, self.abstraction, self.style]
        primary_dims = [d for d in dims if d.is_primary]
        if len(primary_dims) == 4 or len(primary_dims) == 0:
            return self.composite
        primary_weights = {d.dimension: self.DEFAULT_WEIGHTS[d.dimension] for d in primary_dims}
        total = sum(primary_weights.values())
        return sum(
            (w / total) * getattr(self, dim).score
            for dim, w in primary_weights.items()
        )

    @property
    def min_dimension(self) -> DimensionScore:
        """Return the lowest-scoring dimension (weakest link)."""
        dims = [self.identity, self.goal, self.abstraction, self.style]
        return min(dims, key=lambda d: d.score)

    @property
    def min_primary_dimension(self) -> DimensionScore:
        """Return the lowest-scoring primary dimension."""
        dims = [self.identity, self.goal, self.abstraction, self.style]
        primary = [d for d in dims if d.is_primary]
        if not primary:
            return self.min_dimension
        return min(primary, key=lambda d: d.score)

    @property
    def mean_confidence(self) -> float:
        """Average inter-judge agreement across dimensions."""
        return np.mean([
            self.identity.confidence,
            self.goal.confidence,
            self.abstraction.confidence,
            self.style.confidence,
        ])

    @property
    def mean_confidence_primary(self) -> float:
        """Average inter-judge agreement across primary dimensions only."""
        dims = [self.identity, self.goal, self.abstraction, self.style]
        primary = [d for d in dims if d.is_primary]
        if not primary:
            return self.mean_confidence
        return np.mean([d.confidence for d in primary])

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        def _dim_dict(dim_score: DimensionScore) -> dict:
            d = {
                "score": round(dim_score.score, 4),
                "confidence": round(dim_score.confidence, 4),
                "is_primary": dim_score.is_primary,
                "evidence": dim_score.evidence,
            }
            if dim_score.low_signal:
                d["low_signal"] = True
            return d

        result = {
            "composite_score": round(self.composite, 4),
            "composite_primary_only": round(self.composite_primary_only, 4),
            "dimensions": {
                "identity": _dim_dict(self.identity),
                "goal": _dim_dict(self.goal),
                "abstraction": _dim_dict(self.abstraction),
                "style": _dim_dict(self.style),
            },
            "mean_confidence": round(self.mean_confidence, 4),
            "mean_confidence_primary": round(self.mean_confidence_primary, 4),
            "weakest_dimension": self.min_dimension.dimension,
            "weakest_primary_dimension": self.min_primary_dimension.dimension,
        }
        if self.auxiliary:
            result["auxiliary"] = {
                "npc_fallback_rate": round(self.auxiliary.npc_fallback_rate, 4),
                "goal_recovery_latency": round(self.auxiliary.goal_recovery_latency, 2),
                "tone_variance": round(self.auxiliary.tone_variance, 4),
                "self_inconsistency_rate": round(self.auxiliary.self_inconsistency_rate, 4),
            }
        return result


def aggregate_scores(scores: list[BCScore], weights: Optional[dict] = None) -> dict:
    """
    Aggregate multiple BCScore results (e.g., across stressor variants).

    Returns summary statistics per dimension and overall.
    """
    if weights is None:
        weights = BCScore.DEFAULT_WEIGHTS

    composites = [s.composite_with_weights(weights) for s in scores]
    composites_primary = [s.composite_primary_only for s in scores]
    dims = {}
    for dim_name in ("identity", "goal", "abstraction", "style"):
        dim_scores = [getattr(s, dim_name).score for s in scores]
        dim_confs = [getattr(s, dim_name).confidence for s in scores]
        dim_primary = [getattr(s, dim_name).is_primary for s in scores]
        dim_low_signal = [getattr(s, dim_name).low_signal for s in scores]

        # Primary-only stats
        primary_scores = [sc for sc, p in zip(dim_scores, dim_primary) if p]
        primary_confs = [c for c, p in zip(dim_confs, dim_primary) if p]

        dims[dim_name] = {
            "mean": round(float(np.mean(dim_scores)), 4),
            "std": round(float(np.std(dim_scores)), 4),
            "min": round(float(np.min(dim_scores)), 4),
            "max": round(float(np.max(dim_scores)), 4),
            "mean_confidence": round(float(np.mean(dim_confs)), 4),
            "n_primary": sum(dim_primary),
            "n_low_signal": sum(dim_low_signal),
        }
        if primary_scores:
            dims[dim_name]["mean_primary_only"] = round(float(np.mean(primary_scores)), 4)
            dims[dim_name]["mean_confidence_primary_only"] = round(float(np.mean(primary_confs)), 4)

    return {
        "n_evaluations": len(scores),
        "composite": {
            "mean": round(float(np.mean(composites)), 4),
            "std": round(float(np.std(composites)), 4),
            "min": round(float(np.min(composites)), 4),
            "max": round(float(np.max(composites)), 4),
        },
        "composite_primary_only": {
            "mean": round(float(np.mean(composites_primary)), 4),
            "std": round(float(np.std(composites_primary)), 4),
            "min": round(float(np.min(composites_primary)), 4),
            "max": round(float(np.max(composites_primary)), 4),
        },
        "dimensions": dims,
    }
