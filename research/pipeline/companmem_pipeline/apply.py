"""Apply candidate.json to research/output/by-product/<slug>/audit.json.

Lint a temp copy, then write. Replace ledger, claimed_purpose, mechanisms,
unknowns, and sources from the candidate so a prompt/harvest rerun does not
keep stale rows. Do not wipe filled copy/refuse/consensus/contested with empty
fold output.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from companmem_pipeline.harvest import product_ids
from companmem_pipeline.lint import lint_audit
from companmem_pipeline.log import PipelineLogger
from companmem_pipeline.paths import product_cache, product_output

INTERPRETATION_FIELDS = ("copy", "refuse", "consensus", "contested")


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def object_rows(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def identity_dict(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return dict(value)
    return {}


def merge_text_lists(
    existing: list[dict[str, object]],
    incoming: list[dict[str, object]],
) -> list[dict[str, object]]:
    if existing and not incoming:
        return existing
    seen: set[str] = set()
    out: list[dict[str, object]] = []
    for item in existing + incoming:
        text = str(item.get("text") or "").strip().lower()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(item)
    return out


def merge_audits(
    existing: dict[str, object] | None,
    candidate: dict[str, object],
) -> dict[str, object]:
    if existing is None:
        return candidate
    merged = dict(candidate)
    identity = identity_dict(candidate.get("identity"))
    existing_identity = identity_dict(existing.get("identity"))
    for field, value in existing_identity.items():
        if identity.get(field) in (None, "") and value not in (None, ""):
            identity[field] = value
    merged["identity"] = identity
    merged["ledger"] = object_rows(candidate.get("ledger"))
    merged["claimed_purpose"] = object_rows(candidate.get("claimed_purpose"))
    merged["mechanisms"] = object_rows(candidate.get("mechanisms"))
    merged["unknowns"] = object_rows(candidate.get("unknowns"))
    for field in INTERPRETATION_FIELDS:
        existing_rows = object_rows(existing.get(field))
        incoming_rows = object_rows(candidate.get(field))
        if existing_rows and not incoming_rows:
            merged[field] = existing_rows
        else:
            merged[field] = merge_text_lists(existing_rows, incoming_rows)
    merged["sources"] = object_rows(candidate.get("sources"))
    return merged


def summarize(audit: dict[str, object]) -> str:
    identity = identity_dict(audit.get("identity"))
    return (
        f"{identity.get('id')} ledger={len(object_rows(audit.get('ledger')))} "
        f"sources={len(object_rows(audit.get('sources')))} "
        f"copy={len(object_rows(audit.get('copy')))} "
        f"refuse={len(object_rows(audit.get('refuse')))}"
    )


def write_if_linted(audit: dict[str, object], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix="audit_",
        delete=False,
        encoding="utf-8",
    ) as handle:
        json.dump(audit, handle, indent=2)
        tmp = Path(handle.name)
    try:
        errors = lint_audit(json.loads(tmp.read_text(encoding="utf-8")))
        if errors:
            raise SystemExit("lint failed; not writing:\n" + "\n".join(errors))
        dest.write_text(tmp.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    finally:
        tmp.unlink(missing_ok=True)


def apply_slug(slug: str, *, write: bool) -> dict[str, object]:
    cache = product_cache(slug)
    candidate_path = cache / "candidate.json"
    if not candidate_path.exists():
        raise SystemExit(f"missing candidate: {candidate_path}. Run fold first.")
    candidate = load_json(candidate_path)
    dest = product_output(slug) / "audit.json"
    existing = load_json(dest) if dest.exists() else None
    merged = merge_audits(existing, candidate)
    with PipelineLogger("apply", source=slug, write=write) as log:
        log.info(
            "apply_started",
            dest=str(dest),
            exists=dest.exists(),
            candidate=str(candidate_path),
        )
        print(("WRITE " if write else "DRY-RUN ") + summarize(merged))
        if existing is not None:
            log.info("existing_summary", summary=summarize(existing))
            for field in INTERPRETATION_FIELDS:
                kept = object_rows(merged.get(field))
                incoming = object_rows(candidate.get(field))
                existing_rows = object_rows(existing.get(field))
                log.info(
                    "apply_interpretation",
                    field=field,
                    existing=len(existing_rows),
                    incoming=len(incoming),
                    merged=len(kept),
                    preserved=bool(existing_rows and not incoming),
                )
        log.info(
            "apply_merged",
            summary=summarize(merged),
            purpose=len(object_rows(merged.get("claimed_purpose"))),
            mechanisms=len(object_rows(merged.get("mechanisms"))),
            unknowns=len(object_rows(merged.get("unknowns"))),
        )
        errors = lint_audit(merged)
        if errors:
            log.error("lint_failed", error_count=len(errors), errors=errors[:20])
            raise SystemExit("lint failed on merged audit:\n" + "\n".join(errors))
        log.info("lint_ok", dest=str(dest))
        if write:
            write_if_linted(merged, dest)
            log.action("audit_written", path=str(dest), summary=summarize(merged))
            print(f"wrote {dest}")
        else:
            log.decision("apply_dry_run", path=str(dest), summary=summarize(merged))
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply candidate.json to audit.json")
    parser.add_argument("--slug")
    parser.add_argument("--all", action="store_true", help="Every product in seed.json")
    parser.add_argument("--write", action="store_true", help="Lint then write audit.json")
    args = parser.parse_args()
    if args.all:
        for slug in product_ids():
            candidate = product_cache(slug) / "candidate.json"
            if not candidate.exists():
                print(f"apply {slug}: skip (no candidate)")
                continue
            apply_slug(slug, write=args.write)
        return
    if not args.slug:
        raise SystemExit("pass --slug <id> or --all")
    apply_slug(args.slug, write=args.write)


if __name__ == "__main__":
    main()
