"""Lint audit.json against schema and citation rules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import jsonschema

from companmem_pipeline.paths import OUTPUT_DIR, SCHEMA_PATH

_schema_cache: dict[str, object] | None = None


def load_schema() -> dict[str, object]:
    global _schema_cache
    if _schema_cache is None:
        _schema_cache = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return _schema_cache


class LintError(Exception):
    """Audit failed lint."""


def lint_audit(audit: dict[str, object]) -> list[str]:
    """Return a list of error strings. Empty means pass."""
    errors: list[str] = []
    schema = load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    for err in validator.iter_errors(audit):
        errors.append(f"{list(err.absolute_path)}: {err.message}")
    ledger = audit.get("ledger")
    if isinstance(ledger, list):
        for i, row in enumerate(ledger):
            if not isinstance(row, dict):
                errors.append(f"ledger[{i}]: not an object")
                continue
            url = str(row.get("url") or "").strip()
            locator = str(row.get("locator") or "").strip()
            if not url and not locator:
                errors.append(f"ledger[{i}]: needs url or locator")
            if not str(row.get("quote") or "").strip():
                errors.append(f"ledger[{i}]: empty quote")
    for field in ("copy", "refuse", "consensus", "contested"):
        if field in audit and not isinstance(audit[field], list):
            errors.append(f"{field}: must be an array")
    return errors


def lint_path(path: Path) -> list[str]:
    try:
        audit = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON ({exc})"]
    if not isinstance(audit, dict):
        return [f"{path}: root is not an object"]
    return [f"{path}: {msg}" for msg in lint_audit(audit)]


def lint_all() -> int:
    paths = sorted(OUTPUT_DIR.glob("*/audit.json"))
    if not paths:
        print("no audit.json files")
        return 0
    failed = 0
    for path in paths:
        errors = lint_path(path)
        if errors:
            failed += 1
            print(f"FAIL {path}")
            for err in errors:
                print(f"  {err}")
        else:
            print(f"ok {path}")
    return 1 if failed else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint product audit.json files")
    parser.add_argument("--path", help="Single audit.json path")
    args = parser.parse_args()
    if args.path:
        errors = lint_path(Path(args.path))
        if errors:
            for err in errors:
                print(err)
            raise SystemExit(1)
        print(f"ok {args.path}")
        return
    raise SystemExit(lint_all())


if __name__ == "__main__":
    main()
