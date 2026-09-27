"""CogneeAdapter stub — not yet implemented.

To implement: replace NotImplementedError with real logic.
A missing pip dependency should raise AdapterNotReadyError instead.
"""
from __future__ import annotations

from harness.adapters._base import AdapterMetrics, Artifacts, World


class CogneeAdapter:
    def run(self, world: World, artifacts: Artifacts) -> AdapterMetrics:
        raise NotImplementedError("CogneeAdapter not yet implemented")


__all__ = ["CogneeAdapter"]
