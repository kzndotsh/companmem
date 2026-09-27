"""Adapter protocol and supporting types.

All memory system adapters implement the Adapter Protocol: a single run()
method that receives a World and an Artifacts instance and returns AdapterMetrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from harness.artifacts import Artifacts
from harness.world import World


@dataclass
class AdapterMetrics:
    """Token counts reported by an adapter after a trial."""

    tokens_in: int
    tokens_out: int
    memory_tokens: int = field(default=0)  # tokens specifically from retrieved memory


class AdapterNotReadyError(RuntimeError):
    """Raised when an adapter cannot run due to a missing dependency or misconfigured env.

    Produces TrialStatus.SKIPPED in the runner — distinct from NotImplementedError
    (stub not yet written → TrialStatus.INFRA_ERROR).
    """


class Adapter(Protocol):
    """Structural protocol all adapters must satisfy."""

    def run(self, world: World, artifacts: Artifacts) -> AdapterMetrics:
        """Execute the adapter against the given world, writing outputs to artifacts."""
        ...
