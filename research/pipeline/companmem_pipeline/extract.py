"""One-shot Kiro extract per harvested page. No tools."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from pathlib import Path

from companmem_pipeline.harvest import product_ids
from companmem_pipeline.html import clean_html, quality_score
from companmem_pipeline.kiro import MODEL, call_kiro, kiro_configured
from companmem_pipeline.log import PipelineLogger
from companmem_pipeline.paths import load_dotenv, product_cache

load_dotenv()

PROMPT_VERSION = "v3"
MAX_CHUNK_WORDS = 50_000

SYSTEM_PROMPT = """
You extract quoted evidence about how ONE named software product does memory,
for a research audit of companion continuity — not a retrieve-then-speak
leaderboard chase.

Memory here means persistent state across sessions: not model weights, not
the current prompt. Retrieving text into context is mechanical. Remembering
(what users mean) is acting as if the past matters — right fact, right time,
right tone. A product can retrieve without remembering.

The user message names the product. Extract ONLY that product.
Other products on the page (integrations, "export to X", examples) are not
this product's mechanisms. Do not copy their APIs into mechanisms or ledger.

Return ONLY a JSON object matching this schema:
{
  "identity_hints": {
    "name": "", "repo": null, "docs": null, "license": null, "version_or_commit": null
  },
  "claimed_purpose": [{"text": "", "quote": "", "locator": ""}],
  "mechanisms": [{"text": "", "quote": "", "locator": ""}],
  "ledger": [{
    "claim": "", "kind": "docs", "url": "", "quote": "", "locator": "",
    "confidence": "medium", "label": "inferred"
  }],
  "unknowns": [{"text": "", "url": "", "kind": "docs"}]
}

Look for these when THIS page states them. Skip a topic if the page is silent.
- Store vs reader vs scaffold: what is persisted, what is selected into the
  turn, what instructions tell the model to do with it.
- Log vs memory: full transcript vs curated facts/events/summaries.
- Write path: extract, update, delete, conflict/supersession.
- Forget: delete from store, hide at retrieve, or omit in generation.
- Isolation: per user, session, agent, or character.
- Lore/backstory vs events that happened in conversation.
- Retrieve policy: always retrieve vs adaptive / when to stay silent.
- Issues and community: continuity failures (forgotten name, plot, pins,
  creepy or mistimed recall) over stack traces.

Rules:
- Quote before claim. Every ledger row needs a verbatim quote from THIS page
  and a locator (heading, file:line, or section).
- Every mechanism and claimed_purpose row needs a verbatim quote from THIS page.
  Drop the row if you cannot quote.
- kind must be one of: docs, code, issue, community, blog.
  Use the kind given in the user message.
- Put the page URL on every ledger row and every unknown when the user
  message includes it.
- Co-mentions are not claims. Two products named in one sentence is not a mechanism
  of this product.
- Empty arrays beat guesses. Do not invent APIs, scores, or files
  that are not on this page.
- Do not emit copy, refuse, consensus, contested, companion_fit, or scores.
  Those are a later interpretation step, not extract.
- claimed_purpose: a few rows on what THIS product says it is for
  (companion, agent memory, RAG lib). Skip CLI flags and other vendors.
- Prefer mechanisms that name persist, retrieve, update, forget, or isolation
  over generic "uses embeddings".
- label: "measured" when the quote is verbatim product source or docs describing
  what the code or API does. "inferred" for issues, blogs, marketing, or
  vendor benchmark numbers. Vendor LoCoMo (or similar) scores are scores
  under their harness and reader — not companion-social proof. Keep them
  inferred unless this page describes the harness.
- Absence: do not emit an unknown for every topic this page omits.
  Empty unknowns are correct for most pages. Add an unknown only when this
  page is a canonical API or architecture doc that should have covered a core
  memory behavior (persist, retrieve, forget, conflict) and does not, or
  when the page itself states a gap.
- identity_hints: only fill fields this page states about THIS product.
  Leave others null or "".
""".strip()


def kind_focus(kind: str) -> str:
    if kind == "code":
        return (
            "Prefer what the code persists, retrieves, updates, or deletes. "
            "Distinguish a message log from a curated memory write."
        )
    if kind == "docs":
        return (
            "Prefer store vs retrieve vs forget vs conflict. Note if the page "
            "only describes retrieve-then-prompt."
        )
    if kind == "issue":
        return (
            "Prefer continuity failures (forgotten name, plot, pins, creepy "
            "or mistimed recall) over stack traces."
        )
    if kind == "community":
        return (
            "Prefer what people say feels broken about remembering, not API trivia."
        )
    if kind == "blog":
        return (
            "Treat as interested-party claims. Vendor LoCoMo numbers are harness "
            "scores, not companion proof."
        )
    return "Extract only what this page states about this product's memory."


def prompt_hash() -> str:
    return hashlib.md5(SYSTEM_PROMPT.encode(), usedforsecurity=False).hexdigest()[:8]


def chunk_text(text: str) -> list[str]:
    words = text.split()
    if len(words) <= MAX_CHUNK_WORDS:
        return [text]
    chunks: list[str] = []
    for i in range(0, len(words), MAX_CHUNK_WORDS):
        chunks.append(" ".join(words[i : i + MAX_CHUNK_WORDS]))
    return chunks


def empty_extract() -> dict[str, object]:
    return {
        "identity_hints": {
            "name": "",
            "repo": None,
            "docs": None,
            "license": None,
            "version_or_commit": None,
        },
        "claimed_purpose": [],
        "mechanisms": [],
        "ledger": [],
        "unknowns": [],
    }


def normalize_extract(parsed: dict[str, object], *, kind: str, url: str) -> dict[str, object]:
    out = empty_extract()
    hints = parsed.get("identity_hints")
    if isinstance(hints, dict):
        out["identity_hints"] = {
            "name": hints.get("name") or "",
            "repo": hints.get("repo") or None,
            "docs": hints.get("docs") or None,
            "license": hints.get("license") or None,
            "version_or_commit": hints.get("version_or_commit") or None,
        }
    for key in ("claimed_purpose", "mechanisms"):
        items = parsed.get(key)
        if not isinstance(items, list):
            continue
        cleaned: list[dict[str, str]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            text = str(item.get("text") or "").strip()
            quote = str(item.get("quote") or "").strip()
            if not text or not quote:
                continue
            cleaned.append(
                {
                    "text": text,
                    "quote": quote,
                    "locator": str(item.get("locator") or ""),
                }
            )
        out[key] = cleaned
    ledger_in = parsed.get("ledger")
    ledger: list[dict[str, object]] = []
    if isinstance(ledger_in, list):
        for row in ledger_in:
            if not isinstance(row, dict):
                continue
            claim = str(row.get("claim") or "").strip()
            quote = str(row.get("quote") or "").strip()
            if not claim:
                continue
            row_kind = str(row.get("kind") or kind)
            if row_kind not in {"docs", "code", "issue", "community", "blog"}:
                row_kind = kind
            confidence = str(row.get("confidence") or "unknown")
            if confidence not in {"high", "medium", "unknown"}:
                confidence = "unknown"
            label = str(row.get("label") or "unknown")
            if label not in {"measured", "inferred", "unknown"}:
                label = "unknown"
            if kind == "code" and quote:
                label = "measured"
            elif kind in {"issue", "community", "blog"}:
                label = "inferred"
            locator = str(row.get("locator") or "").strip() or None
            row_url = str(row.get("url") or "").strip() or url or None
            ledger.append(
                {
                    "claim": claim,
                    "kind": row_kind,
                    "url": row_url,
                    "quote": quote,
                    "locator": locator,
                    "confidence": confidence,
                    "label": label,
                }
            )
    out["ledger"] = ledger
    unknowns_in = parsed.get("unknowns")
    unknowns: list[dict[str, str]] = []
    if isinstance(unknowns_in, list):
        for item in unknowns_in:
            if not isinstance(item, dict):
                continue
            text = str(item.get("text") or "").strip()
            if not text:
                continue
            row_kind = str(item.get("kind") or kind)
            if row_kind not in {"docs", "code", "issue", "community", "blog"}:
                row_kind = kind
            row_url = str(item.get("url") or "").strip() or url
            locator = str(item.get("locator") or "").strip()
            row: dict[str, str] = {"text": text, "url": row_url, "kind": row_kind}
            if locator:
                row["locator"] = locator
            unknowns.append(row)
    out["unknowns"] = unknowns
    return out


def merge_chunks(chunk_results: list[dict[str, object]]) -> dict[str, object]:
    if not chunk_results:
        return empty_extract()
    if len(chunk_results) == 1:
        return chunk_results[0]
    merged = empty_extract()
    hints = chunk_results[0].get("identity_hints")
    if isinstance(hints, dict):
        merged["identity_hints"] = hints
    for key in ("claimed_purpose", "mechanisms", "ledger", "unknowns"):
        rows: list[object] = []
        for result in chunk_results:
            items = result.get(key)
            if isinstance(items, list):
                rows.extend(items)
        merged[key] = rows
    return merged


def load_manifest(cache: Path) -> dict[str, object]:
    path = cache / "manifest.json"
    if not path.exists():
        raise SystemExit(f"missing manifest: {path}. Run harvest first.")
    return json.loads(path.read_text(encoding="utf-8"))


def extract_page(
    cache: Path,
    page: dict[str, object],
    *,
    product_id: str,
    product_name: str,
    force: bool,
    log: PipelineLogger,
    index: int = 0,
    total: int = 0,
) -> str:
    page_id = str(page["id"])
    out_dir = cache / "extract" / page_id
    out_dir.mkdir(parents=True, exist_ok=True)
    meta_path = out_dir / "meta.json"
    extract_path = out_dir / "extract.json"
    log.info(
        "extract_page_begin",
        page_id=page_id,
        index=index,
        total=total,
        url=str(page.get("url") or ""),
        kind=str(page.get("kind") or "docs"),
        path=str(page.get("path") or ""),
    )
    if not force and meta_path.exists() and extract_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("prompt_hash") == prompt_hash():
            log.decision("extract_skipped", page_id=page_id, reason="prompt_hash_match")
            return "skipped"
    rel = str(page["path"])
    raw_path = cache / rel
    if not raw_path.exists():
        log.warn("extract_missing_page", page_id=page_id, path=rel)
        return "missing"
    raw = raw_path.read_text(encoding="utf-8", errors="replace")
    text = clean_html(raw) if raw.lstrip()[:100].startswith("<") else raw
    if not text.strip():
        log.decision("extract_skipped", page_id=page_id, reason="empty")
        empty = empty_extract()
        extract_path.write_text(json.dumps(empty, indent=2), encoding="utf-8")
        meta_path.write_text(
            json.dumps(
                {
                    "page_id": page_id,
                    "prompt_hash": prompt_hash(),
                    "prompt_version": PROMPT_VERSION,
                    "skipped": "empty",
                    "model": MODEL,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return "empty"
    score_as_prose = bool(page.get("score_as_prose", True))
    score = quality_score(text)
    if score_as_prose and score["is_low_quality"]:
        log.decision("extract_skipped", page_id=page_id, reason="low_quality")
        empty = empty_extract()
        extract_path.write_text(json.dumps(empty, indent=2), encoding="utf-8")
        meta_path.write_text(
            json.dumps(
                {
                    "page_id": page_id,
                    "prompt_hash": prompt_hash(),
                    "prompt_version": PROMPT_VERSION,
                    "skipped": "low_quality",
                    "quality_score": score,
                    "model": MODEL,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return "low_quality"
    kind = str(page.get("kind") or "docs")
    url = str(page.get("url") or "")
    chunks = chunk_text(text)
    log.info(
        "extract_page_ready",
        page_id=page_id,
        chars=len(text),
        chunks=len(chunks),
        word_count=score.get("word_count"),
    )
    chunk_results: list[dict[str, object]] = []
    for chunk_i, chunk in enumerate(chunks, start=1):
        log.info(
            "extract_chunk",
            page_id=page_id,
            chunk=chunk_i,
            chunks=len(chunks),
            chars=len(chunk),
        )
        user = (
            f"Product: {product_name} (id: {product_id}). Extract only this product.\n"
            f"Source kind: {kind}\n"
            f"Page URL: {url}\n"
            f"{kind_focus(kind)}\n"
            f"Extract memory-relevant claims from this text about {product_name} only. "
            "Respond with ONLY a JSON object, no markdown fences, no explanation.\n\n"
            f"{chunk}"
        )
        parsed = call_kiro(
            user,
            SYSTEM_PROMPT
            + "\n\nIMPORTANT: Output ONLY the JSON object. No markdown code fences. No preamble.",
            temperature=0.1,
        )
        if parsed is None:
            log.error("extract_kiro_failed", page_id=page_id, chunk=chunk_i, chunks=len(chunks))
            continue
        chunk_results.append(normalize_extract(parsed, kind=kind, url=url))
        log.info(
            "extract_chunk_ok",
            page_id=page_id,
            chunk=chunk_i,
            ledger=len(chunk_results[-1]["ledger"]),
        )
        time.sleep(random.uniform(0.4, 1.2))
    merged = merge_chunks(chunk_results)
    if not chunk_results:
        log.warn("extract_empty", page_id=page_id, reason="all_chunks_failed")
    extract_path.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    meta_path.write_text(
        json.dumps(
            {
                "page_id": page_id,
                "prompt_hash": prompt_hash(),
                "prompt_version": PROMPT_VERSION,
                "model": MODEL,
                "quality_score": score,
                "chunks": len(chunks),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    log.action("extract_written", page_id=page_id, ledger=len(merged["ledger"]))
    return "ok"


def extract(slug: str, *, force: bool = False, dry_run: bool = False) -> None:
    cache = product_cache(slug)
    manifest = load_manifest(cache)
    pages = list(manifest.get("pages") or [])
    product_id = str(manifest.get("id") or slug)
    product_name = str(manifest.get("name") or slug)
    if dry_run:
        print(f"Would extract {len(pages)} pages for {slug}")
        return
    if not kiro_configured():
        raise SystemExit("ERROR: Set KIRO_GATEWAY_API_KEY or PROXY_API_KEY")
    with PipelineLogger("extract", source=slug, pages=len(pages), force=force) as log:
        counts = {"ok": 0, "skipped": 0, "low_quality": 0, "missing": 0}
        total = len(pages)
        log.info("extract_pages", total=total, product_id=product_id, product_name=product_name)
        for index, page in enumerate(pages, start=1):
            if not isinstance(page, dict):
                continue
            status = extract_page(
                cache,
                page,
                product_id=product_id,
                product_name=product_name,
                force=force,
                log=log,
                index=index,
                total=total,
            )
            counts[status] = counts.get(status, 0) + 1
            log.info(
                "extract_page_done",
                page_id=str(page.get("id") or ""),
                status=status,
                index=index,
                total=total,
            )
        log.info("extract_finished", **counts)
        print(f"extract {slug}: {counts}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract claims from harvested pages")
    parser.add_argument("--slug")
    parser.add_argument("--all", action="store_true", help="Every product in seed.json")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.all:
        for slug in product_ids():
            cache = product_cache(slug)
            if not (cache / "manifest.json").exists():
                print(f"extract {slug}: skip (no harvest)")
                continue
            extract(slug, force=args.force, dry_run=args.dry_run)
        return
    if not args.slug:
        raise SystemExit("pass --slug <id> or --all")
    extract(args.slug, force=args.force, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
