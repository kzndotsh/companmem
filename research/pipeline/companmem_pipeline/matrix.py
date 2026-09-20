"""Same persist/retrieve/forget/conflict/isolation axis for every product audit."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import jsonschema

from companmem_pipeline.fold import load_json
from companmem_pipeline.harvest import load_seed, product_ids
from companmem_pipeline.lint import lint_audit
from companmem_pipeline.paths import MATRIX_SCHEMA_PATH, OUTPUT_DIR, load_dotenv

load_dotenv()

QUOTE_MAX = 240
FORGET_QUOTE_JACCARD = 0.5

PERSIST_STORE = (
    "sqlite",
    "postgres",
    "jsonl",
    "memories.json",
    "json file",
    "json files",
    "vector store",
    "vector database",
    "graph database",
    "qdrant",
    "chromadb",
    "create table",
    "long-term storage",
    "neo4j",
    "json.dump",
)
PERSIST_SESSION = (
    "across session",
    "across sessions",
    "cross-session",
    "cross session",
)
PERSIST_NEGATE = (
    "rather than persist",
    "rather than persistent",
    "not persist",
    "no persist",
    "without persist",
    "rather than long-term",
)
PERSIST_HITS = PERSIST_STORE + PERSIST_SESSION
RETRIEVE_HITS = (
    "retriev",
    "recall",
    "bm25",
    "vector search",
    "hybrid retrieval",
    "semantic search",
)
SEARCH_CALL_RE = re.compile(r"\bsearch\s*\(", re.IGNORECASE)
FORGET_DELETE_HITS = (
    "hard-delet",
    "hard delete",
    "hard delet",
    "delete_all",
    "wipe",
    "drop the row",
    "permanently deleted",
)
FORGET_SUPPRESS_HITS = (
    "soft-delete",
    "soft delete",
    "deleted_at",
    "expiration_date",
    "valid_until",
    "hidden from search",
    "hidden from retrieval",
    "is_active",
)
CONFLICT_STRONG = (
    "supersed",
    "invalid_at",
    "invalidat",
    "conflict resol",
    "update existing",
    "add/update/delete",
)
CONFLICT_HITS = CONFLICT_STRONG + ("contradict",)
ISOLATION_HITS = (
    "user_id",
    "group_id",
    "bank_id",
    "namespace",
    "tenant_id",
    "data isolation",
    "scoped to user",
    "per-user",
    "per user",
    "per-project",
    "per project",
    "project_id",
    "memory_session_id",
    "usermemory",
    "scopedmemory",
)
ISOLATION_MISS = (
    "no per-user",
    "no isolation",
    "single shared",
    "single flat",
    "globally shared",
    "no namespace",
)
LOG_HITS = (
    "transcript",
    "conversation_log",
    "message log",
    "append-only",
    "raw session",
    "jsonl session",
)
CURATED_HITS = (
    "curated",
    "structured fact",
    "entity edge",
    "extracted fact",
    "memory card",
)

KIND_RANK = {"code": 0, "docs": 1, "paper": 2, "issue": 3, "blog": 4, "community": 5}

QuoteOk = Callable[[str], bool]


def product_clone_flags() -> dict[str, bool]:
    seed = load_seed()
    products = seed.get("products")
    if not isinstance(products, dict):
        raise SystemExit("seed.json missing products")
    flags: dict[str, bool] = {}
    for slug, entry in products.items():
        if isinstance(entry, dict):
            flags[str(slug)] = bool(entry.get("clone"))
        else:
            flags[str(slug)] = False
    return flags


def blob_text(audit: dict[str, object]) -> str:
    parts: list[str] = []
    for field in ("mechanisms", "claimed_purpose"):
        rows = audit.get(field)
        if not isinstance(rows, list):
            continue
        for item in rows:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or ""))
    ledger = audit.get("ledger")
    if isinstance(ledger, list):
        for row in ledger:
            if isinstance(row, dict):
                parts.append(str(row.get("claim") or ""))
                parts.append(str(row.get("quote") or ""))
    return " ".join(parts).lower()


def contains_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def empty_axis() -> dict[str, object]:
    return {"present": False, "quote": "", "url": ""}


def persist_quote_ok(quote: str) -> bool:
    q = quote.lower()
    if contains_any(q, PERSIST_NEGATE):
        return False
    return contains_any(q, PERSIST_STORE) or contains_any(q, PERSIST_SESSION)


def retrieve_quote_ok(quote: str) -> bool:
    q = quote.lower()
    if contains_any(q, RETRIEVE_HITS):
        return True
    return SEARCH_CALL_RE.search(quote) is not None


def conflict_quote_ok(quote: str) -> bool:
    q = quote.lower()
    if contains_any(q, CONFLICT_STRONG):
        return True
    if "contradict" not in q:
        return False
    return contains_any(q, ("invalidat", "supersed", "update existing", "add/update"))


def axis_quote(
    audit: dict[str, object],
    needles: tuple[str, ...],
    *,
    quote_ok: QuoteOk | None = None,
    extra_match: Callable[[str], bool] | None = None,
) -> tuple[str, str]:
    ledger = audit.get("ledger")
    if not isinstance(ledger, list):
        return "", ""
    ranked: list[tuple[int, int, int, str, str]] = []
    for index, row in enumerate(ledger):
        if not isinstance(row, dict):
            continue
        quote = str(row.get("quote") or "").strip()
        if not quote:
            continue
        q = quote.lower()
        hit = contains_any(q, needles)
        if extra_match is not None and extra_match(quote):
            hit = True
        if not hit:
            continue
        if quote_ok is not None and not quote_ok(quote):
            continue
        kind = str(row.get("kind") or "")
        score = sum(1 for needle in needles if needle in q)
        if extra_match is not None and extra_match(quote):
            score = max(score, 1)
        ranked.append(
            (
                -score,
                KIND_RANK.get(kind, 9),
                index,
                quote[:QUOTE_MAX],
                str(row.get("url") or ""),
            )
        )
    if not ranked:
        return "", ""
    ranked.sort()
    _score, _kind, _index, quote, url = ranked[0]
    return quote, url


def quoted_axis(
    audit: dict[str, object],
    needles: tuple[str, ...],
    *,
    quote_ok: QuoteOk | None = None,
    extra_match: Callable[[str], bool] | None = None,
) -> dict[str, object]:
    quote, url = axis_quote(
        audit,
        needles,
        quote_ok=quote_ok,
        extra_match=extra_match,
    )
    if not quote:
        return empty_axis()
    return {"present": True, "quote": quote, "url": url}


def token_set(text: str) -> set[str]:
    return {part for part in re.split(r"[^\w]+", text.lower()) if part}


def quotes_same_evidence(left: dict[str, object], right: dict[str, object]) -> bool:
    left_url = str(left.get("url") or "")
    right_url = str(right.get("url") or "")
    if left_url and left_url == right_url:
        return True
    left_quote = str(left.get("quote") or "")
    right_quote = str(right.get("quote") or "")
    if left_quote.strip() == right_quote.strip():
        return True
    left_tokens = token_set(left_quote)
    right_tokens = token_set(right_quote)
    if not left_tokens or not right_tokens:
        return False
    overlap = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    return overlap / union >= FORGET_QUOTE_JACCARD


def forget_axes(audit: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    delete = quoted_axis(audit, FORGET_DELETE_HITS)
    suppress = quoted_axis(audit, FORGET_SUPPRESS_HITS)
    if delete["present"] and suppress["present"] and quotes_same_evidence(delete, suppress):
        suppress_q = str(suppress.get("quote") or "").lower()
        if contains_any(suppress_q, FORGET_SUPPRESS_HITS):
            delete = empty_axis()
        else:
            suppress = empty_axis()
    return delete, suppress


def isolation_hit_quote_ok(quote: str) -> bool:
    return not contains_any(quote.lower(), ISOLATION_MISS)


def isolation_axis(audit: dict[str, object]) -> dict[str, object]:
    hit = quoted_axis(audit, ISOLATION_HITS, quote_ok=isolation_hit_quote_ok)
    if hit["present"]:
        return hit
    miss_quote, miss_url = axis_quote(audit, ISOLATION_MISS)
    if miss_quote:
        return {"present": False, "quote": miss_quote, "url": miss_url}
    return empty_axis()


def log_vs_curated(blob: str) -> str:
    has_log = contains_any(blob, LOG_HITS)
    has_curated = contains_any(blob, CURATED_HITS)
    if has_log and has_curated:
        return "both"
    if has_log:
        return "log"
    if has_curated:
        return "curated"
    return "unknown"


def classify_audit(audit: dict[str, object], *, clone: bool) -> dict[str, object]:
    identity = audit.get("identity")
    identity_obj = identity if isinstance(identity, dict) else {}
    slug = str(identity_obj.get("id") or "")
    blob = blob_text(audit)
    forget_delete, forget_suppress = forget_axes(audit)
    return {
        "id": slug,
        "clone": clone,
        "persist": quoted_axis(audit, PERSIST_HITS, quote_ok=persist_quote_ok),
        "retrieve": quoted_axis(
            audit,
            RETRIEVE_HITS,
            quote_ok=retrieve_quote_ok,
            extra_match=lambda quote: SEARCH_CALL_RE.search(quote) is not None,
        ),
        "forget_delete": forget_delete,
        "forget_suppress": forget_suppress,
        "conflict_or_supersession": quoted_axis(
            audit,
            CONFLICT_HITS,
            quote_ok=conflict_quote_ok,
        ),
        "isolation": isolation_axis(audit),
        "log_vs_curated": log_vs_curated(blob),
    }


def load_clean_audits() -> tuple[list[str], list[dict[str, object]]]:
    present: list[str] = []
    audits: list[dict[str, object]] = []
    for slug in product_ids():
        path = OUTPUT_DIR / slug / "audit.json"
        if not path.exists():
            continue
        audit = load_json(path)
        if lint_audit(audit):
            continue
        present.append(slug)
        audits.append(audit)
    return present, audits


def build_matrix() -> dict[str, object]:
    clone_flags = product_clone_flags()
    _present, audits = load_clean_audits()
    rows: list[dict[str, object]] = []
    for audit in audits:
        identity = audit.get("identity")
        slug = str(identity.get("id") or "") if isinstance(identity, dict) else ""
        rows.append(classify_audit(audit, clone=clone_flags.get(slug, False)))
    rows.sort(key=lambda row: str(row.get("id") or ""))
    return {
        "observed_at": datetime.now(UTC).date().isoformat(),
        "products": rows,
    }


def lint_matrix(record: dict[str, object]) -> list[str]:
    schema = json.loads(MATRIX_SCHEMA_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(schema)
    for err in validator.iter_errors(record):
        errors.append(f"{list(err.absolute_path)}: {err.message}")
    return errors


def write_matrix(record: dict[str, object], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix="matrix_",
        delete=False,
        encoding="utf-8",
    ) as handle:
        json.dump(record, handle, indent=2)
        tmp = Path(handle.name)
    try:
        loaded = json.loads(tmp.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise SystemExit("matrix lint failed; not writing: root is not an object")
        errors = lint_matrix(cast(dict[str, object], loaded))
        if errors:
            raise SystemExit("matrix lint failed:\n" + "\n".join(errors))
        dest.write_text(tmp.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    finally:
        tmp.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Write persist/retrieve/forget field matrix")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    record = build_matrix()
    errors = lint_matrix(record)
    if errors:
        raise SystemExit("matrix lint failed:\n" + "\n".join(errors))
    dest = OUTPUT_DIR / "matrix.json"
    if args.dry_run:
        print(json.dumps(record, indent=2))
        return
    write_matrix(record, dest)
    products = record["products"]
    count = len(products) if isinstance(products, list) else 0
    print(f"wrote {dest} ({count} products)")


if __name__ == "__main__":
    main()
