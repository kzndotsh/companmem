"""Repo-rooted paths and env loading."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

PIPELINE_DIR = Path(__file__).resolve().parent.parent
ROOT = PIPELINE_DIR.parent.parent
PRODUCT_CACHE_DIR = ROOT / ".cache" / "by-product"
EVAL_CACHE_DIR = ROOT / ".cache" / "by-eval"
CACHE_DIR = PRODUCT_CACHE_DIR
LOGS_DIR = PRODUCT_CACHE_DIR / "logs"
EVAL_LOGS_DIR = EVAL_CACHE_DIR / "logs"
OUTPUT_DIR = ROOT / "research" / "output" / "by-product"
EVAL_OUTPUT_DIR = ROOT / "research" / "output" / "by-eval"
SCHEMA_PATH = PIPELINE_DIR / "audit.schema.json"
SYNTHESIS_SCHEMA_PATH = PIPELINE_DIR / "synthesis.schema.json"
MATRIX_SCHEMA_PATH = PIPELINE_DIR / "matrix.schema.json"
SEED_PATH = PIPELINE_DIR / "seed.json"

Namespace = Literal["product", "eval"]


@dataclass(frozen=True)
class NamespacePaths:
    kind: Namespace
    cache_dir: Path
    output_dir: Path
    logs_dir: Path


def namespace_paths(kind: Namespace = "product") -> NamespacePaths:
    if kind == "eval":
        return NamespacePaths(
            kind="eval",
            cache_dir=EVAL_CACHE_DIR,
            output_dir=EVAL_OUTPUT_DIR,
            logs_dir=EVAL_LOGS_DIR,
        )
    return NamespacePaths(
        kind="product",
        cache_dir=PRODUCT_CACHE_DIR,
        output_dir=OUTPUT_DIR,
        logs_dir=LOGS_DIR,
    )


def parse_namespace(value: str) -> Namespace:
    if value == "eval":
        return "eval"
    if value == "product":
        return "product"
    raise SystemExit(f"unknown namespace: {value!r} (use product or eval)")


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


def slug_cache(slug: str, *, namespace: Namespace = "product") -> Path:
    return namespace_paths(namespace).cache_dir / slug


def slug_output(slug: str, *, namespace: Namespace = "product") -> Path:
    return namespace_paths(namespace).output_dir / slug


def product_cache(slug: str) -> Path:
    return slug_cache(slug, namespace="product")


def product_output(slug: str) -> Path:
    return slug_output(slug, namespace="product")


def eval_cache(slug: str) -> Path:
    return slug_cache(slug, namespace="eval")


def eval_output(slug: str) -> Path:
    return slug_output(slug, namespace="eval")
