"""Artifact persistence for harness trial outputs.

Artifacts are written by adapters and read by the scorer. They are persisted to
disk so runs can be re-scored later without re-running adapters.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ArtifactMissing(RuntimeError):
    """Raised when an artifact is read before it has been written."""


class Artifacts:
    """Disk-backed container for one trial's adapter outputs.

    reply.txt and memory_export.json are created on first write. Both
    reply() and export() read from disk so they work across process restarts
    (e.g. during re-scoring).
    """

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir

    @property
    def output_dir(self) -> Path:
        return self._output_dir

    def _reply_path(self) -> Path:
        return self._output_dir / "reply.txt"

    def _export_path(self) -> Path:
        return self._output_dir / "memory_export.json"

    def write_reply(self, text: str) -> None:
        """Write the adapter's text reply to disk."""
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._reply_path().write_text(text, encoding="utf-8")

    def write_export(self, data: dict[str, Any]) -> None:
        """Write the adapter's memory export (a dict) to disk as JSON."""
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._export_path().write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def reply(self) -> str:
        """Read the reply from disk.

        Raises:
            ArtifactMissing: if write_reply has not been called.
        """
        path = self._reply_path()
        if not path.is_file():
            raise ArtifactMissing(f"reply.txt not found in {self._output_dir}")
        return path.read_text(encoding="utf-8")

    def export(self) -> dict[str, Any]:
        """Read the memory export from disk.

        Raises:
            ArtifactMissing: if write_export has not been called.
        """
        path = self._export_path()
        if not path.is_file():
            raise ArtifactMissing(f"memory_export.json not found in {self._output_dir}")
        result: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return result
