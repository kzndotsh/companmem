"""Structured JSONL logging for pipeline steps. Echoes the same events to stderr."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import UTC, datetime
from typing import TextIO

from companmem_pipeline.paths import LOGS_DIR, Namespace, namespace_paths

_REDACT_NAMES = {
    "token",
    "api_key",
    "apikey",
    "password",
    "authorization",
    "github_token",
    "brave_api_key",
    "proxy_api_key",
    "kiro_gateway_api_key",
    "x-api-key",
    "x-subscription-token",
}
_CONSOLE_VALUE_CHARS = 300


def console_enabled() -> bool:
    return os.environ.get("COMPANMEM_LOG_CONSOLE", "1") not in {"0", "false", "no"}


def _is_sensitive(name: str, value: object) -> bool:
    n = name.lower().replace("-", "_")
    if n in _REDACT_NAMES:
        return True
    if "token" in n and isinstance(value, str) and len(value) > 12:
        return True
    return False


def _short(value: object) -> str:
    if isinstance(value, str):
        text = value.replace("\n", " ")
    else:
        try:
            text = json.dumps(value, ensure_ascii=False, default=str)
        except TypeError:
            text = str(value)
    if len(text) > _CONSOLE_VALUE_CHARS:
        return text[: _CONSOLE_VALUE_CHARS - 3] + "..."
    return text


def emit_console(
    step: str,
    source: str,
    level: str,
    event: str,
    *,
    elapsed: float | None = None,
    file: TextIO | None = None,
    **data: object,
) -> None:
    """One-line progress on stderr. No secrets. Always flushed."""
    if not console_enabled():
        return
    parts = [datetime.now(UTC).isoformat(timespec="seconds"), step]
    if source:
        parts.append(source)
    parts.append(level.upper())
    parts.append(event)
    if elapsed is not None:
        parts.append(f"elapsed={elapsed}")
    for key, value in data.items():
        if value is None or _is_sensitive(key, value):
            continue
        parts.append(f"{key}={_short(value)}")
    print(" ".join(parts), file=file or sys.stderr, flush=True)


class PipelineLogger:
    """JSONL logger. One file per run at .cache/by-product/logs/{step}_{slug}_{run_id}.jsonl."""

    def __init__(
        self,
        step: str,
        source: str = "",
        *,
        namespace: Namespace = "product",
        **metadata: object,
    ) -> None:
        self.step = step
        self.source = source
        self.start_time = time.time()
        self.run_id = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        logs_dir = namespace_paths(namespace).logs_dir
        logs_dir.mkdir(parents=True, exist_ok=True)
        safe_source = source.replace("/", "_").replace(":", "_") if source else "global"
        self.log_path = logs_dir / f"{step}_{safe_source}_{self.run_id}.jsonl"
        self._file = self.log_path.open("w", encoding="utf-8")
        self.counts = {
            "info": 0,
            "warn": 0,
            "error": 0,
            "decisions": 0,
            "actions": 0,
        }
        emit_console(
            self.step,
            self.source,
            "info",
            "log_file",
            path=str(self.log_path),
        )
        self._write("info", "run_started", **metadata)

    def _ts(self) -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")

    def _elapsed(self) -> float:
        return round(time.time() - self.start_time, 2)

    def _write(self, level: str, event: str, **data: object) -> None:
        safe = {k: v for k, v in data.items() if v is not None and not _is_sensitive(k, v)}
        entry: dict[str, object] = {
            "ts": self._ts(),
            "elapsed": self._elapsed(),
            "level": level,
            "event": event,
            "run_id": self.run_id,
            "step": self.step,
            "source": self.source,
        }
        if "source" in safe:
            safe.setdefault("hit_source", safe.pop("source"))
        for key in ("step", "level", "event", "elapsed", "ts", "run_id"):
            safe.pop(key, None)
        entry.update(safe)
        self._file.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
        self._file.flush()
        emit_console(
            self.step,
            self.source,
            level,
            event,
            elapsed=self._elapsed(),
            **safe,
        )

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
        if exc is not None:
            self.error("run_failed", error_type=type(exc).__name__, error=str(exc)[:500])
        self.close()
