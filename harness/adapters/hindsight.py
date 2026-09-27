"""HindsightAdapter stub — not yet implemented.

To implement: replace NotImplementedError with real logic.
A missing pip dependency should raise AdapterNotReadyError instead.
"""
from __future__ import annotations

from harness.adapters._base import AdapterMetrics, Artifacts, World


class HindsightAdapter:
    def run(self, world: World, artifacts: Artifacts) -> AdapterMetrics:
        raise NotImplementedError("HindsightAdapter not yet implemented")


__all__ = ["HindsightAdapter"]
