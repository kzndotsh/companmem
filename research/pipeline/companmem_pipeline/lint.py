"""Lint audit.json against schema and citation rules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import jsonschema

from companmem_pipeline.log import PipelineLogger
from companmem_pipeline.paths import EVAL_OUTPUT_DIR, OUTPUT_DIR, SCHEMA_PATH

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


def lint_eval_all() -> int:
    paths = sorted(EVAL_OUTPUT_DIR.glob("*/audit.json"))
    if not paths:
        print("no eval audit.json files")
        return 0
    failed = 0
    with PipelineLogger("lint", source="eval", files=len(paths)) as log:
        log.info("lint_started", files=len(paths), namespace="eval")
        for path in paths:
            errors = lint_path(path)
            if errors:
                failed += 1
                log.error(
                    "lint_fail",
                    path=str(path),
                    error_count=len(errors),
                    errors=errors[:20],
                )
                print(f"FAIL {path}")
                for err in errors:
                    print(f"  {err}")
            else:
                log.info("lint_ok", path=str(path))
                print(f"ok {path}")
        log.info("lint_finished", ok=len(paths) - failed, failed=failed)
    return 1 if failed else 0


def lint_all() -> int:
    paths = sorted(OUTPUT_DIR.glob("*/audit.json"))
    if not paths:
        print("no audit.json files")
        return 0
    failed = 0
    with PipelineLogger("lint", source="seed", files=len(paths)) as log:
        log.info("lint_started", files=len(paths))
        for path in paths:
            errors = lint_path(path)
            if errors:
                failed += 1
                log.error(
                    "lint_fail",
                    path=str(path),
                    error_count=len(errors),
                    errors=errors[:20],
                )
                print(f"FAIL {path}")
                for err in errors:
                    print(f"  {err}")
            else:
                log.info("lint_ok", path=str(path))
                print(f"ok {path}")
        log.info("lint_finished", ok=len(paths) - failed, failed=failed)
    return 1 if failed else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint audit.json files")
    parser.add_argument("--path", help="Single audit.json path")
    parser.add_argument(
        "--namespace",
        choices=("product", "eval"),
        default="product",
        help="Glob audits under by-product (default) or by-eval",
    )
    args = parser.parse_args()
    if args.path:
        path = Path(args.path)
        with PipelineLogger("lint", source=path.stem) as log:
            errors = lint_path(path)
            if errors:
                log.error("lint_fail", path=str(path), errors=errors[:20])
                for err in errors:
                    print(err)
                raise SystemExit(1)
            log.info("lint_ok", path=str(path))
            print(f"ok {args.path}")
        return
    if args.namespace == "eval":
        raise SystemExit(lint_eval_all())
    raise SystemExit(lint_all())


if __name__ == "__main__":
    main()
