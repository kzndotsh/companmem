"""Structured JSONL logging for pipeline steps."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime

from companmem_pipeline.paths import LOGS_DIR


class PipelineLogger:
    """JSONL logger. One file per run at .cache/by-product/logs/{step}_{slug}_{run_id}.jsonl."""

    def __init__(self, step: str, source: str = "", **metadata: object) -> None:
        self.step = step
        self.source = source
        self.start_time = time.time()
        self.run_id = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        safe_source = source.replace("/", "_").replace(":", "_") if source else "global"
        self.log_path = LOGS_DIR / f"{step}_{safe_source}_{self.run_id}.jsonl"
        self._file = self.log_path.open("w", encoding="utf-8")
        self.counts = {
            "info": 0,
            "warn": 0,
            "error": 0,
            "decisions": 0,
            "actions": 0,
        }
        self._write("info", "run_started", **metadata)

    def _ts(self) -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")

    def _elapsed(self) -> float:
        return round(time.time() - self.start_time, 2)

    def _write(self, level: str, event: str, **data: object) -> None:
        entry: dict[str, object] = {
            "ts": self._ts(),
            "elapsed": self._elapsed(),
            "level": level,
            "event": event,
            "run_id": self.run_id,
            "step": self.step,
            "source": self.source,
        }
        entry.update({k: v for k, v in data.items() if v is not None})
        self._file.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self._file.flush()

    def debug(self, event: str, **data: object) -> None:
        self._write("debug", event, **data)

    def info(self, event: str, **data: object) -> None:
        self.counts["info"] += 1
        self._write("info", event, **data)

    def warn(self, event: str, **data: object) -> None:
        self.counts["warn"] += 1
        self._write("warn", event, **data)

    def error(self, event: str, **data: object) -> None:
        self.counts["error"] += 1
        self._write("error", event, **data)

    def decision(self, event: str, **data: object) -> None:
        self.counts["decisions"] += 1
        self._write("info", event, **data)

    def action(self, event: str, **data: object) -> None:
        self.counts["actions"] += 1
        self._write("info", event, **data)

    def close(self) -> None:
        self._write("info", "run_completed", counts=self.counts)
        self._file.close()
        total = sum(self.counts.values())
        print(f"Log: {self.log_path.name} ({total} entries, {self._elapsed():.1f}s)")

    def __enter__(self) -> PipelineLogger:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> None:
        self.close()
