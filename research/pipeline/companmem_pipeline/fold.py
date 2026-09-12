"""Fold per-page extracts into one candidate.json."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from companmem_pipeline.harvest import product_ids
from companmem_pipeline.log import PipelineLogger
from companmem_pipeline.paths import product_cache

CONFIDENCE_RANK = {"high": 3, "medium": 2, "unknown": 1}
PAGE_ABSENCE_RE = re.compile(
    r"not (?:described|stated|shown|mentioned|documented|defined|present|"
    r"covered|specified|addressed|determinable).{0,80}this (?:page|file)|"
    r"not on this (?:page|file)|"
    r"no memory mechanisms.{0,80}this (?:page|file)|"
    r"this (?:page|file) (?:contains|defines) (?:no|only)|"
    r"this file",
    re.I,
)


def normalize_claim(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def ledger_key(row: dict[str, object]) -> str:
    locator = str(row.get("locator") or "").strip()
    kind = str(row.get("kind") or "")
    if locator:
        return f"{kind}::{locator}"
    return f"claim::{normalize_claim(str(row.get('claim') or ''))}"


def quote_len(row: dict[str, object]) -> int:
    return len(str(row.get("quote") or ""))


def has_citation(row: dict[str, object]) -> bool:
    url = str(row.get("url") or "").strip()
    locator = str(row.get("locator") or "").strip()
    return bool(url or locator)


def empty_audit(identity: dict[str, object]) -> dict[str, object]:
    return {
        "identity": identity,
        "claimed_purpose": [],
        "mechanisms": [],
        "ledger": [],
        "sources": [],
        "consensus": [],
        "contested": [],
        "copy": [],
        "refuse": [],
        "unknowns": [],
    }


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def ledger_matches(item: dict[str, object], ledger: list[dict[str, object]]) -> bool:
    """True if this summary is backed by a ledger quote or overlapping claim text."""
    text = normalize_claim(str(item.get("text") or ""))
    if not text:
        return False
    item_quote = normalize_claim(str(item.get("quote") or ""))
    for row in ledger:
        if item_quote and item_quote == normalize_claim(str(row.get("quote") or "")):
            return True
        claim = normalize_claim(str(row.get("claim") or ""))
        if text in claim or claim in text:
            return True
    return False


def cited_summaries(
    items: list[dict[str, object]],
    ledger: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Keep unique summary texts that match the ledger. Do not emit claim_ids."""
    out: list[dict[str, object]] = []
    seen: set[str] = set()
    for item in items:
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        key = normalize_claim(text)
        if key in seen:
            continue
        if not ledger_matches(item, ledger):
            continue
        seen.add(key)
        out.append({"text": text})
    return out


def is_page_absence(text: str) -> bool:
    return bool(PAGE_ABSENCE_RE.search(text))


def fold_page_absence_unknowns(
    items: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Keep a page-local absence only when the same stem appears on two or more URLs."""
    kept: list[dict[str, object]] = []
    by_stem: dict[str, list[dict[str, object]]] = {}
    for item in items:
        text = str(item.get("text") or "")
        if is_page_absence(text):
            by_stem.setdefault(normalize_claim(text), []).append(item)
        else:
            kept.append(item)
    for rows in by_stem.values():
        urls = {str(row.get("url") or "") for row in rows}
        if len(urls) >= 2:
            kept.extend(rows)
    return kept


def fold_pages(extracts: list[dict[str, object]], manifest: dict[str, object]) -> dict[str, object]:
    identity = {
        "id": str(manifest.get("id") or ""),
        "name": str(manifest.get("name") or ""),
        "repo": manifest.get("repo"),
        "docs": manifest.get("docs"),
        "license": manifest.get("license"),
        "version_or_commit": manifest.get("version_or_commit"),
        "observed_at": str(manifest.get("observed_at") or ""),
    }
    ledger_by_key: dict[str, dict[str, object]] = {}
    purposes: list[dict[str, object]] = []
    mechanisms: list[dict[str, object]] = []
    unknowns: list[dict[str, object]] = []
    sources_by_url: dict[str, dict[str, object]] = {}

    for page in manifest.get("pages") or []:
        if not isinstance(page, dict):
            continue
        url = str(page.get("url") or "").strip()
        if not url:
            continue
        sources_by_url[url] = {
            "url": url,
            "kind": page.get("kind") or "docs",
            "accessed_at": page.get("accessed_at") or manifest.get("observed_at"),
            "quality": page.get("quality") or "medium",
        }

    for extract in extracts:
        hints = extract.get("identity_hints")
        if isinstance(hints, dict):
            for field in ("name", "repo", "docs", "license", "version_or_commit"):
                if identity.get(field) in (None, "") and hints.get(field):
                    identity[field] = hints[field]
        for item in extract.get("claimed_purpose") or []:
            if isinstance(item, dict):
                purposes.append(item)
        for item in extract.get("mechanisms") or []:
            if isinstance(item, dict):
                mechanisms.append(item)
        for item in extract.get("unknowns") or []:
            if not isinstance(item, dict) or not item.get("text"):
                continue
            url = str(item.get("url") or "").strip()
            if not url:
                continue
            kind = str(item.get("kind") or "")
            if kind not in {"docs", "code", "issue", "community", "blog"}:
                kind = "docs"
            locator = str(item.get("locator") or "").strip()
            row: dict[str, object] = {
                "text": str(item["text"]),
                "url": url,
                "kind": kind,
            }
            if locator:
                row["locator"] = locator
            unknowns.append(row)
        for row in extract.get("ledger") or []:
            if not isinstance(row, dict) or not has_citation(row):
                continue
            key = ledger_key(row)
            existing = ledger_by_key.get(key)
            if existing is None or quote_len(row) > quote_len(existing):
                ledger_by_key[key] = dict(row)

    ledger = list(ledger_by_key.values())
    audit = empty_audit(identity)
    audit["ledger"] = ledger
    audit["claimed_purpose"] = cited_summaries(purposes, ledger)
    audit["mechanisms"] = cited_summaries(mechanisms, ledger)
    seen_unknown: set[str] = set()
    unique_unknowns: list[dict[str, object]] = []
    for item in unknowns:
        text = str(item.get("text") or "")
        url = str(item.get("url") or "")
        key = f"{url}::{normalize_claim(text)}"
        if not text or not url or key in seen_unknown:
            continue
        seen_unknown.add(key)
        unique_unknowns.append(item)
    audit["unknowns"] = fold_page_absence_unknowns(unique_unknowns)
    audit["sources"] = list(sources_by_url.values())
    audit["copy"] = []
    audit["refuse"] = []
    audit["consensus"] = []
    audit["contested"] = []
    return audit


def load_extracts(cache: Path, manifest: dict[str, object]) -> list[dict[str, object]]:
    extract_root = cache / "extract"
    if not extract_root.exists():
        return []
    pages_by_id: dict[str, dict[str, object]] = {}
    for page in manifest.get("pages") or []:
        if isinstance(page, dict) and page.get("id"):
            pages_by_id[str(page["id"])] = page
    extracts: list[dict[str, object]] = []
    for path in sorted(extract_root.glob("*/extract.json")):
        page = pages_by_id.get(path.parent.name)
        if page is None:
            continue
        extract = load_json(path)
        page_url = str(page.get("url") or "")
        page_kind = str(page.get("kind") or "docs")
        rows = extract.get("unknowns")
        if isinstance(rows, list):
            stamped: list[object] = []
            for item in rows:
                if not isinstance(item, dict):
                    continue
                if not item.get("url") and page_url:
                    item["url"] = page_url
                if not item.get("kind"):
                    item["kind"] = page_kind
                stamped.append(item)
            extract["unknowns"] = stamped
        extracts.append(extract)
    return extracts


def fold(slug: str) -> dict[str, object]:
    cache = product_cache(slug)
    manifest_path = cache / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"missing manifest: {manifest_path}")
    manifest = load_json(manifest_path)
    extracts = load_extracts(cache, manifest)
    with PipelineLogger("fold", source=slug, extracts=len(extracts)) as log:
        candidate = fold_pages(extracts, manifest)
        out = cache / "candidate.json"
        out.write_text(json.dumps(candidate, indent=2), encoding="utf-8")
        log.action(
            "candidate_written",
            ledger=len(candidate["ledger"]),
            sources=len(candidate["sources"]),
        )
        print(
            f"fold {slug}: {len(candidate['ledger'])} ledger rows, "
            f"{len(candidate['sources'])} sources"
        )
        return candidate


def main() -> None:
    parser = argparse.ArgumentParser(description="Fold extracts into candidate.json")
    parser.add_argument("--slug")
    parser.add_argument("--all", action="store_true", help="Every product in seed.json")
    args = parser.parse_args()
    if args.all:
        for slug in product_ids():
            cache = product_cache(slug)
            if not (cache / "extract").exists():
                print(f"fold {slug}: skip (no extracts)")
                continue
            fold(slug)
        return
    if not args.slug:
        raise SystemExit("pass --slug <id> or --all")
    fold(args.slug)


if __name__ == "__main__":
    main()
