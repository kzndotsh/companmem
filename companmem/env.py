"""Load project `.env` into os.environ (setdefault — does not override shell exports)."""

from __future__ import annotations

import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_LOADED = False


def load_dotenv(path: Path | None = None) -> None:
    global _LOADED
    if _LOADED:
        return
    env_path = path or (_ROOT / ".env")
    if not env_path.is_file():
        _LOADED = True
        return
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)
    _LOADED = True
