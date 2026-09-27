"""Mem0Adapter stub — not yet implemented.

To implement: replace NotImplementedError with real logic.
A missing pip dependency should raise AdapterNotReadyError instead.
"""
from __future__ import annotations

from harness.adapters._base import AdapterMetrics, Artifacts, World


class Mem0Adapter:
    def run(self, world: World, artifacts: Artifacts) -> AdapterMetrics:
        raise NotImplementedError("Mem0Adapter not yet implemented")


__all__ = ["Mem0Adapter"]
