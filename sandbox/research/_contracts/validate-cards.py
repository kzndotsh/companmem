#!/usr/bin/env python3
"""Validate census cards against the required keys and enums in card.schema.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = Path(__file__).resolve().parent / "card.schema.json"
CARDS_DIR = ROOT / "research" / "census" / "cards"

DIM_KEYS = [
    "ontology",
    "write_policy",
    "read_policy",
    "supersession",
    "temporal",
    "identity_split",
    "silence",
    "poisoning",
    "forgetting",
    "cost_shape",
    "local",
    "mcp",
]
DIM_SCORES = {"present", "partial", "absent", "unknown"}
LABELS = {"measured", "inferred", "guess"}
FITS = {"FIT", "PARTIAL", "MISFIT"}
ASSUMES = {"yes", "no", "mixed", "unknown"}
KINDS = {
    "agent-memory-lib",
    "memory-os",
    "temporal-graph",
    "companion-native",
    "roleplay-client",
    "closed-companion-app",
    "mcp-server",
    "eval-benchmark",
    "academic",
    "adjacent-coding-agent",
}


def fail(path: Path, msg: str) -> str:
    return f"{path.relative_to(ROOT)}: {msg}"


def check_card(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        return [fail(path, f"invalid json ({exc})")]
    if not isinstance(data, dict):
        return [fail(path, "root must be an object")]
    for key in (
        "id",
        "name",
        "kind",
        "repo",
        "docs",
        "license",
        "stars_observed",
        "observed_at",
        "ontology_notes",
        "dimensions",
        "assumes_retrieve_equals_remember",
        "companion_fit",
        "companion_fit_reason",
        "published_eval",
        "sources",
        "open_unknowns",
    ):
        if key not in data:
            errors.append(fail(path, f"missing {key}"))
    extra = set(data) - {
        "id",
        "name",
        "kind",
        "repo",
        "docs",
        "license",
        "stars_observed",
        "observed_at",
        "ontology_notes",
        "dimensions",
        "assumes_retrieve_equals_remember",
        "companion_fit",
        "companion_fit_reason",
        "published_eval",
        "sources",
        "open_unknowns",
    }
    if extra:
        errors.append(fail(path, f"unknown keys {sorted(extra)}"))
    if data.get("kind") not in KINDS:
        errors.append(fail(path, f"bad kind {data.get('kind')!r}"))
    if data.get("assumes_retrieve_equals_remember") not in ASSUMES:
        errors.append(fail(path, "bad assumes_retrieve_equals_remember"))
    if data.get("companion_fit") not in FITS:
        errors.append(fail(path, "bad companion_fit"))
    dims = data.get("dimensions")
    if not isinstance(dims, dict):
        errors.append(fail(path, "dimensions must be an object"))
        return errors
    for key in DIM_KEYS:
        dim = dims.get(key)
        if not isinstance(dim, dict):
            errors.append(fail(path, f"dimensions.{key} missing"))
            continue
        if dim.get("score") not in DIM_SCORES:
            errors.append(fail(path, f"dimensions.{key}.score bad"))
        if dim.get("label") not in LABELS:
            errors.append(fail(path, f"dimensions.{key}.label bad"))
        if not isinstance(dim.get("evidence"), str) or not dim["evidence"].strip():
            errors.append(fail(path, f"dimensions.{key}.evidence empty"))
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append(fail(path, "sources must be a non-empty list"))
    pub = data.get("published_eval")
    if not isinstance(pub, dict) or set(pub) != {
        "name",
        "claimed_score",
        "what_it_actually_scores",
        "source",
    }:
        errors.append(fail(path, "published_eval keys wrong"))
    expected_id = path.stem
    if data.get("id") != expected_id:
        errors.append(fail(path, f"id {data.get('id')!r} != filename {expected_id}"))
    return errors


def main() -> int:
    if not CARDS_DIR.is_dir():
        print(f"no cards dir at {CARDS_DIR}", file=sys.stderr)
        return 1
    paths = sorted(CARDS_DIR.glob("*.json"))
    if not paths:
        print("no cards yet", file=sys.stderr)
        return 1
    errors: list[str] = []
    for path in paths:
        errors.extend(check_card(path))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"{len(errors)} error(s) in {len(paths)} card(s)", file=sys.stderr)
        return 1
    print(f"{len(paths)} card(s) valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
