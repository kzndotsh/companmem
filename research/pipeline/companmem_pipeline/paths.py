"""Repo-rooted paths and env loading."""

from __future__ import annotations

import os
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent.parent
ROOT = PIPELINE_DIR.parent.parent
CACHE_DIR = ROOT / ".cache" / "by-product"
LOGS_DIR = CACHE_DIR / "logs"
OUTPUT_DIR = ROOT / "research" / "output" / "by-product"
SCHEMA_PATH = PIPELINE_DIR / "audit.schema.json"
SEED_PATH = PIPELINE_DIR / "seed.json"


def load_dotenv(path: Path | None = None) -> None:
    """Load KEY=VAL from .env into os.environ if the key is unset."""
    env_path = path or (ROOT / ".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def product_cache(slug: str) -> Path:
    return CACHE_DIR / slug


def product_output(slug: str) -> Path:
    return OUTPUT_DIR / slug
