"""Thematic synthesis over every existing product audit.json."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import jsonschema

from companmem_pipeline.fold import load_json
from companmem_pipeline.harvest import load_seed, product_ids
from companmem_pipeline.kiro import MODEL, call_kiro, kiro_configured
from companmem_pipeline.lint import lint_audit
from companmem_pipeline.log import PipelineLogger
from companmem_pipeline.matrix import (
    CONFLICT_HITS,
    CURATED_HITS,
    FORGET_DELETE_HITS,
    FORGET_SUPPRESS_HITS,
    ISOLATION_HITS,
    ISOLATION_MISS,
    LOG_HITS,
    PERSIST_HITS,
    RETRIEVE_HITS,
)
from companmem_pipeline.paths import OUTPUT_DIR, SYNTHESIS_SCHEMA_PATH, load_dotenv

load_dotenv()

COMPACT_VERSION = "compact-v3"
LEDGER_CAP = 80
QUOTE_MAX = 240
UNKNOWNS_CAP = 8
PRODUCT_ID_CAP = 8
EVIDENCE_CAP = 8
MIN_TOKEN_OVERLAP = 2
MIN_QUOTE_PRECISION = 0.25
MIN_DISTINCTIVE_LEN = 8
MIN_ON_CARD_CHARS = 16
MIN_THEME_PRODUCTS = 2
PRODUCT_ROW_CAP = 3
GAP_THEME_JACCARD = 0.32
SYNTHESIZE_MAX_TOKENS = 32768
SYNTHESIZE_TIMEOUT = 600.0
JSON_SEPARATORS = (",", ":")
STOPWORDS = frozenset(
    {
        "a",
        "across",
        "after",
        "all",
        "also",
        "an",
        "and",
        "any",
        "are",
        "as",
        "at",
        "based",
        "be",
        "by",
        "can",
        "every",
        "existing",
        "for",
        "from",
        "in",
        "including",
        "into",
        "is",
        "it",
        "its",
        "itself",
        "may",
        "memories",
        "memory",
        "new",
        "no",
        "not",
        "of",
        "on",
        "only",
        "or",
        "per",
        "product",
        "products",
        "session",
        "sessions",
        "system",
        "systems",
        "than",
        "that",
        "the",
        "them",
        "then",
        "they",
        "this",
        "to",
        "used",
        "user",
        "users",
        "using",
        "via",
        "vs",
        "when",
        "with",
    }
)
# Tokens that appear in almost every memory audit. Overlap on these is not
# distinctive-token precision (PROTOCOL synthesis grounding).
FIELD_STOPWORDS = frozenset(
    {
        "about",
        "agent",
        "another",
        "back",
        "call",
        "content",
        "conversation",
        "data",
        "default",
        "fact",
        "file",
        "graph",
        "identity",
        "key",
        "language",
        "line",
        "link",
        "message",
        "model",
        "multiple",
        "never",
        "one",
        "other",
        "persist",
        "persistent",
        "place",
        "raw",
        "read",
        "result",
        "retriev",
        "same",
        "search",
        "stamp",
        "store",
        "storage",
        "thread",
        "time",
        "turn",
        "unit",
        "vector",
        "write",
        "written",
    }
)

CONFIDENCE_RANK = {"high": 0, "medium": 1, "unknown": 2}
KIND_RANK = {
    "code": 0,
    "docs": 1,
    "paper": 2,
    "issue": 3,
    "blog": 4,
    "community": 5,
}

SYSTEM_PROMPT = """
You synthesize product-memory audits for companion-continuity research.
Not a LoCoMo chase. Not retrieve-then-speak as the default good.

Themes must come from the audits' ledgers and mechanisms. Do not invent a
theme because a research question exists. If several products share
extract-embed-retrieve with no forget, update, or isolation, say that.

Return ONLY JSON. First character must be `{`. Do not emit
`<thinking>`, `<think>`, or `<reasoning>` tags.

{
  "themes": [{"text": "", "product_ids": []}],
  "recurring_mechanisms": [{"text": "", "product_ids": []}],
  "shared_gaps": [{"text": "", "product_ids": []}],
  "unknowns": [{"text": ""}]
}

Rules:
- Only use what the audits contain. Do not invent products or quotes.
- Recurring mechanism = stated in more than one product ledger or
  mechanisms list.
- When the audits support it, distinguish store vs reader vs scaffold,
  and log vs curated memory. Do not force empty axes.
- Vendor LoCoMo (or similar) numbers are not a theme unless several audits
  treat them the same way — and even then they are harness scores, not
  companion-social proof.
- copy/refuse stay empty; do not fill them here.
- product_ids are 3 to 8 strongest examples whose cards actually support
  the sentence. Not a census. Do not write nearly every or majority.
- Shared gaps are missing persist, retrieve, forget, conflict, or
  isolation behavior. Do not repeat a theme as a gap.
- Do not put a mechanism and a gap in one theme sentence (e.g. extract
  plus "no forget"). Mechanisms go in themes; absences go in shared_gaps.
- Always emit forget (hard delete, soft-delete/suppress, or decay) as a
  theme or a shared gap when two or more cards support it. Always emit
  isolation the same way. Do not skip those axes.
- If two or more cards describe a single shared file or unscoped store,
  put that in shared_gaps as no per-user isolation. Do not put it in a
  store/retrieve theme.
- Look at clone false cards (closed apps). Put undocumented companion
  recall in unknowns, not in a store/retrieve theme.
""".strip()

_synthesis_schema_cache: dict[str, object] | None = None


def synthesize_model() -> str:
    return os.environ.get("SYNTHESIZE_MODEL") or os.environ.get("EXTRACT_MODEL") or MODEL


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


def truncate_quote(quote: object) -> str:
    text = str(quote or "").strip()
    if len(text) <= QUOTE_MAX:
        return text
    return text[:QUOTE_MAX]


def ledger_sort_key(row: dict[str, object], index: int) -> tuple[int, int, int]:
    confidence = str(row.get("confidence") or "")
    kind = str(row.get("kind") or "")
    return (
        CONFIDENCE_RANK.get(confidence, 9),
        KIND_RANK.get(kind, 9),
        index,
    )


def compact_ledger(
    ledger: object,
    *,
    product_id: str,
) -> tuple[list[dict[str, object]], int]:
    rows: list[tuple[int, dict[str, object]]] = []
    if isinstance(ledger, list):
        for index, row in enumerate(ledger):
            if not isinstance(row, dict):
                continue
            quote = truncate_quote(row.get("quote"))
            if not quote:
                continue
            claim = str(row.get("claim") or "").strip()
            if not claim:
                continue
            rows.append(
                (
                    index,
                    {
                        "id": product_id,
                        "claim": claim,
                        "kind": row.get("kind"),
                        "confidence": row.get("confidence"),
                        "quote": quote,
                    },
                )
            )
    total = len(rows)
    rows.sort(key=lambda item: ledger_sort_key(item[1], item[0]))
    kept = [item[1] for item in rows[:LEDGER_CAP]]
    return kept, total


def compact_unknowns(unknowns: object) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not isinstance(unknowns, list):
        return out
    for item in unknowns:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        out.append({"text": text})
        if len(out) >= UNKNOWNS_CAP:
            break
    return out


def compact_audit(
    audit: dict[str, object],
    *,
    clone: bool,
    product_id: str | None = None,
) -> dict[str, object]:
    identity = audit.get("identity")
    identity_obj = identity if isinstance(identity, dict) else {}
    slug = product_id or str(identity_obj.get("id") or "")
    ledger_rows, _ledger_total = compact_ledger(audit.get("ledger"), product_id=slug)
    return {
        "identity": {
            "id": identity_obj.get("id"),
            "name": identity_obj.get("name"),
            "repo": identity_obj.get("repo"),
        },
        "clone": clone,
        "claimed_purpose": audit.get("claimed_purpose"),
        "mechanisms": audit.get("mechanisms"),
        "ledger": ledger_rows,
        "unknowns": compact_unknowns(audit.get("unknowns")),
    }


def load_audits() -> tuple[list[str], list[str], list[str], list[dict[str, object]]]:
    """Return (present, missing, dirty, audits). missing is absent or lint-fail."""
    present: list[str] = []
    missing: list[str] = []
    dirty: list[str] = []
    audits: list[dict[str, object]] = []
    for slug in product_ids():
        path = OUTPUT_DIR / slug / "audit.json"
        if not path.exists():
            missing.append(slug)
            continue
        audit = load_json(path)
        errors = lint_audit(audit)
        if errors:
            missing.append(slug)
            dirty.append(slug)
            continue
        present.append(slug)
        audits.append(audit)
    return present, missing, dirty, audits


def load_synthesis_schema() -> dict[str, object]:
    global _synthesis_schema_cache
    if _synthesis_schema_cache is None:
        _synthesis_schema_cache = json.loads(SYNTHESIS_SCHEMA_PATH.read_text(encoding="utf-8"))
    return _synthesis_schema_cache


def lint_synthesis(record: dict[str, object]) -> list[str]:
    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(load_synthesis_schema())
    for err in validator.iter_errors(record):
        errors.append(f"{list(err.absolute_path)}: {err.message}")
    return errors


def as_object_list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def filter_theme_rows(
    value: object,
    present: set[str],
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for item in as_object_list(value):
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        raw_ids = item.get("product_ids")
        ids: list[str] = []
        if isinstance(raw_ids, list):
            seen: set[str] = set()
            for raw in raw_ids:
                slug = str(raw).strip()
                if slug in present and slug not in seen:
                    seen.add(slug)
                    ids.append(slug)
        out.append({"text": text, "product_ids": ids})
    return out


def filter_unknown_rows(value: object) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for item in as_object_list(value):
        text = str(item.get("text") or "").strip()
        if text:
            out.append({"text": text})
    return out


def stem_token(word: str) -> str:
    if word.startswith("retriev"):
        return "retriev"
    if word.endswith("ing") and len(word) > 6:
        return word[:-3]
    if word.endswith("ed") and len(word) > 5:
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 4:
        return word[:-1]
    return word


def content_tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z][a-z0-9]{2,}", text.lower().replace("_", " "))
    blocked = {stem_token(word) for word in STOPWORDS | FIELD_STOPWORDS}
    return {stem_token(word) for word in words if stem_token(word) not in blocked}


NEGATION_RE = re.compile(
    r"\b(?:no|not|none|never|without|absent|missing|undocumented|"
    r"unscoped|lack|cannot|can't|isn't|aren't|doesn't|don't)\b",
    re.IGNORECASE,
)
ABSENCE_THEME_RE = re.compile(
    r"(?:no automatic|without automatic|undocumented|absent from|"
    r"no per-user|no (?:cross-session |per-session )?isolation|no forget|"
    r"no conflict|no mechanism|forget path absent|not described|few implement|"
    r"with no (?:automatic )?(?:forget|update|isolation|conflict))",
    re.IGNORECASE,
)
CONFLICT_THEME_RE = re.compile(
    r"conflict|invalidat|contradict|superse|temporal invalid",
    re.IGNORECASE,
)
CONSOLIDATE_THEME_RE = re.compile(
    r"\bdream|\bsleep\b|consolidat|\bdigest\b|reflect",
    re.IGNORECASE,
)
CONSOLIDATE_HITS = (
    "dream",
    "sleep",
    "consolidat",
    "digest",
    "reflect",
    "overnight",
)
RETRIEVE_THEME_RE = re.compile(
    r"hybrid retrieval|retrieve-then|semantic search|always-retrieve|"
    r"scaffold|on-demand|\bbm25\b|\brrf\b",
    re.IGNORECASE,
)
HYBRID_QUOTE_HITS = (
    "hybrid",
    "bm25",
    "rrf",
    "fts",
    "reciprocal rank",
    "full-text",
    "keyword search",
)
RETRIEVE_QUOTE_HITS = RETRIEVE_HITS + (
    "scaffold",
    "context block",
    "system prompt",
)
FORGET_DENIAL_RE = re.compile(
    r"no delete|no forget|never removes|does not delete|not present",
    re.IGNORECASE,
)
FORGET_SOFT_THEME_RE = re.compile(
    r"soft-delete|tombstone|deleted_at|soft delete",
    re.IGNORECASE,
)
ISOLATION_ABSENCE_HITS = ISOLATION_MISS + (
    "not multi-tenant",
    "one file per",
    "shared file",
    "flat collection",
    "flat store",
    "single file",
)
PERSIST_DENIAL_RE = re.compile(
    r"no canonical|does not persist|never persist|not the source of truth",
    re.IGNORECASE,
)
FORGET_THEME_RE = re.compile(
    r"forget|tombstone|soft-delete|ebbinghaus|\bfsrs\b|\bdecay\b",
    re.IGNORECASE,
)
ISOLATION_THEME_RE = re.compile(
    r"isolat|namespace|tenant|per-user|per-project|per-agent",
    re.IGNORECASE,
)
ISOLATION_QUOTE_HITS = ISOLATION_HITS + (
    "isolation",
    "tenant",
    "team_id",
    "agent_id",
    "per-agent",
    "per agent",
)
EXTRACT_HITS = (
    "extract",
    "curated",
    "heuristic",
    "llm extraction",
)
FORGET_QUOTE_HITS = FORGET_DELETE_HITS + FORGET_SUPPRESS_HITS + (
    "forget",
    "decay",
    "ebbinghaus",
    "fsrs",
    "heat",
)
PERSIST_QUOTE_HITS = PERSIST_HITS + (
    "markdown",
    "source of truth",
    "canonical",
    "jsonl",
    "file-native",
)


def token_jaccard(left: str, right: str) -> float:
    left_tokens = content_tokens(left)
    right_tokens = content_tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    union = left_tokens | right_tokens
    return len(left_tokens & right_tokens) / len(union)


def mechanism_texts(card: dict[str, object]) -> list[str]:
    texts: list[str] = []
    mechanisms = card.get("mechanisms")
    if not isinstance(mechanisms, list):
        return texts
    for item in mechanisms:
        if isinstance(item, dict):
            text = str(item.get("text") or "").strip()
            if text:
                texts.append(text)
        elif isinstance(item, str) and item.strip():
            texts.append(item.strip())
    return texts


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def card_snippets(card: dict[str, object]) -> list[str]:
    snippets: list[str] = []
    ledger = card.get("ledger")
    if isinstance(ledger, list):
        for row in ledger:
            if not isinstance(row, dict):
                continue
            quote = str(row.get("quote") or "").strip()
            if quote:
                snippets.append(quote)
    snippets.extend(mechanism_texts(card))
    return snippets


def kiro_evidence_quotes(item: dict[str, object]) -> dict[str, str]:
    quotes: dict[str, str] = {}
    evidence = item.get("evidence")
    if not isinstance(evidence, list):
        return quotes
    for row in evidence:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("product_id") or "").strip()
        quote = str(row.get("quote") or "").strip()
        if slug and quote and slug not in quotes:
            quotes[slug] = quote
    return quotes


def on_card_quote(quote: str, card: dict[str, object]) -> str:
    needle = normalize_ws(quote)
    if len(needle) < MIN_ON_CARD_CHARS:
        return ""
    for snippet in card_snippets(card):
        if needle in normalize_ws(snippet):
            return quote
    return ""


def contains_any(text: str, needles: tuple[str, ...]) -> bool:
    hay = text.lower()
    return any(needle in hay for needle in needles)


def theme_requires_negation(theme_text: str) -> bool:
    return bool(ABSENCE_THEME_RE.search(theme_text))


def axis_quote_ok(theme_text: str, snippet: str) -> bool:
    theme = theme_text.lower()
    absence = theme_requires_negation(theme_text)
    if ISOLATION_THEME_RE.search(theme_text):
        if absence:
            if not contains_any(snippet, ISOLATION_ABSENCE_HITS):
                return False
        else:
            if contains_any(snippet, ISOLATION_MISS):
                return False
            if not contains_any(snippet, ISOLATION_QUOTE_HITS):
                return False
    if CONFLICT_THEME_RE.search(theme_text):
        if not contains_any(snippet, CONFLICT_HITS):
            return False
        hay = snippet.lower()
        if "cache" in hay and "invalidat" in hay and not contains_any(
            snippet,
            ("fact", "supersed", "contradict"),
        ):
            return False
        if re.search(r"\bDELETE FROM\b", snippet, flags=re.IGNORECASE):
            return False
        if re.search(
            r"retained|status field|deprecated|soft supersession|"
            r"rather than.{0,40}delet|preserving (?:full )?history|not deleted",
            theme,
            flags=re.IGNORECASE,
        ) and re.search(
            r"hard-delet|cascade delet",
            snippet,
            flags=re.IGNORECASE,
        ):
            return False
    if FORGET_THEME_RE.search(theme_text):
        if not absence and FORGET_DENIAL_RE.search(snippet):
            return False
        if FORGET_SOFT_THEME_RE.search(theme_text):
            if not contains_any(
                snippet,
                FORGET_DELETE_HITS + FORGET_SUPPRESS_HITS + ("forgotten",),
            ):
                return False
        elif not contains_any(snippet, FORGET_QUOTE_HITS):
            return False
    if CONSOLIDATE_THEME_RE.search(theme_text):
        if not contains_any(snippet, CONSOLIDATE_HITS):
            return False
    if "extract" in theme:
        if not contains_any(snippet, EXTRACT_HITS):
            return False
    if RETRIEVE_THEME_RE.search(theme_text):
        if not contains_any(snippet, RETRIEVE_QUOTE_HITS):
            return False
    if any(word in theme for word in ("hybrid", "bm25", "rrf")):
        if not contains_any(snippet, HYBRID_QUOTE_HITS):
            return False
    if re.search(
        r"auto-injection|per-turn auto|every turn without",
        theme,
        flags=re.IGNORECASE,
    ):
        if re.search(
            r"when truly needed|explicit recall|not the short auto-injection",
            snippet,
            flags=re.IGNORECASE,
        ):
            return False
    if "curated" in theme and "log" in theme:
        if not (
            contains_any(snippet, LOG_HITS) or contains_any(snippet, CURATED_HITS)
        ):
            return False
    if any(
        word in theme
        for word in ("canonical", "source of truth", "file-native", "filesystem")
    ):
        if PERSIST_DENIAL_RE.search(snippet):
            return False
        if "markdown" in theme and re.search(
            r"sqlite is (?:the )?canonical",
            snippet,
            flags=re.IGNORECASE,
        ):
            return False
        if not contains_any(snippet, PERSIST_QUOTE_HITS):
            return False
    return True


def snippet_support(
    theme_text: str,
    snippet: str,
    *,
    require_negation: bool = False,
) -> tuple[float, int]:
    need_neg = require_negation or theme_requires_negation(theme_text)
    if need_neg and not NEGATION_RE.search(snippet):
        return 0.0, 0
    if not axis_quote_ok(theme_text, snippet):
        return 0.0, 0
    theme_tokens = content_tokens(theme_text)
    snippet_tokens = content_tokens(snippet)
    overlap = theme_tokens & snippet_tokens
    count = len(overlap)
    if not snippet_tokens:
        return 0.0, 0
    distinctive = any(len(token) >= MIN_DISTINCTIVE_LEN for token in overlap)
    min_overlap = 1 if distinctive else MIN_TOKEN_OVERLAP
    if count < min_overlap:
        return 0.0, 0
    precision = count / len(snippet_tokens)
    if precision < MIN_QUOTE_PRECISION and not distinctive:
        return 0.0, 0
    return precision, count


def best_evidence_quote(
    theme_text: str,
    card: dict[str, object],
    *,
    require_negation: bool = False,
) -> tuple[float, int, str]:
    ranked: list[tuple[float, int, int, str]] = []
    for snippet in card_snippets(card):
        quote = snippet[:QUOTE_MAX] if len(snippet) > QUOTE_MAX else snippet
        precision, overlap = snippet_support(
            theme_text,
            quote,
            require_negation=require_negation,
        )
        if overlap == 0:
            continue
        ranked.append((precision, overlap, -len(quote), quote))
    if not ranked:
        return 0.0, 0, ""
    ranked.sort(reverse=True)
    precision, overlap, _neg_len, quote = ranked[0]
    return precision, overlap, quote


def ground_cited_rows(
    value: object,
    present: set[str],
    cards: dict[str, dict[str, object]],
    clone_flags: dict[str, bool],
    *,
    require_negation: bool = False,
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for item in as_object_list(value):
        filtered = filter_theme_rows([item], present)
        if not filtered:
            continue
        text = str(filtered[0].get("text") or "")
        raw_ids = filtered[0].get("product_ids")
        if not isinstance(raw_ids, list):
            continue
        offered = kiro_evidence_quotes(item)
        scored: list[tuple[float, int, str, str]] = []
        for raw in raw_ids:
            slug = str(raw)
            card = cards.get(slug)
            if card is None:
                continue
            offered_quote = offered.get(slug)
            if offered_quote is not None:
                verified = on_card_quote(offered_quote, card)
                if verified:
                    precision, overlap = snippet_support(
                        text,
                        verified,
                        require_negation=require_negation,
                    )
                    if overlap == 0:
                        continue
                    scored.append((precision, overlap, slug, verified))
                    continue
            precision, overlap, quote = best_evidence_quote(
                text,
                card,
                require_negation=require_negation,
            )
            if overlap == 0 or not quote:
                continue
            scored.append((precision, overlap, slug, quote))
        scored.sort(key=lambda row: (-row[0], -row[1], row[2]))
        kept = scored[:PRODUCT_ID_CAP]
        ids = [slug for _precision, _overlap, slug, _quote in kept]
        if len(ids) < MIN_THEME_PRODUCTS:
            continue
        clone_true = [slug for slug in ids if clone_flags.get(slug, False)]
        clone_false = [slug for slug in ids if not clone_flags.get(slug, False)]
        evidence: list[dict[str, str]] = []
        for _precision, _overlap, slug, quote in kept[:EVIDENCE_CAP]:
            evidence.append({"product_id": slug, "quote": quote})
        out.append(
            {
                "text": text,
                "product_ids": ids,
                "clone_true": clone_true,
                "clone_false": clone_false,
                "evidence": evidence,
            }
        )
    return out


def rebuild_cited_row(
    row: dict[str, object],
    keep_ids: list[str],
    clone_flags: dict[str, bool],
) -> dict[str, object] | None:
    if len(keep_ids) < MIN_THEME_PRODUCTS:
        return None
    evidence_in = row.get("evidence")
    by_id: dict[str, str] = {}
    if isinstance(evidence_in, list):
        for item in evidence_in:
            if not isinstance(item, dict):
                continue
            slug = str(item.get("product_id") or "")
            quote = str(item.get("quote") or "").strip()
            if slug and quote and slug not in by_id:
                by_id[slug] = quote
    keep_ids = [slug for slug in keep_ids if slug in by_id]
    if len(keep_ids) < MIN_THEME_PRODUCTS:
        return None
    return {
        "text": row.get("text"),
        "product_ids": keep_ids,
        "clone_true": [slug for slug in keep_ids if clone_flags.get(slug, False)],
        "clone_false": [slug for slug in keep_ids if not clone_flags.get(slug, False)],
        "evidence": [{"product_id": slug, "quote": by_id[slug]} for slug in keep_ids],
    }


def cap_product_rows(
    groups: list[list[dict[str, object]]],
    clone_flags: dict[str, bool],
) -> list[list[dict[str, object]]]:
    placements: list[tuple[float, int, int, str]] = []
    for group_index, rows in enumerate(groups):
        for row_index, row in enumerate(rows):
            text = str(row.get("text") or "")
            evidence = row.get("evidence")
            if not isinstance(evidence, list):
                continue
            for item in evidence:
                if not isinstance(item, dict):
                    continue
                slug = str(item.get("product_id") or "")
                quote = str(item.get("quote") or "")
                if not slug:
                    continue
                precision, _overlap = snippet_support(text, quote)
                placements.append((precision, group_index, row_index, slug))
    placements.sort(key=lambda item: (-item[0], item[1], item[2], item[3]))
    used: dict[str, int] = {}
    allowed: dict[tuple[int, int], list[str]] = {}
    for _precision, group_index, row_index, slug in placements:
        if used.get(slug, 0) >= PRODUCT_ROW_CAP:
            continue
        key = (group_index, row_index)
        slot = allowed.setdefault(key, [])
        if slug in slot:
            continue
        used[slug] = used.get(slug, 0) + 1
        slot.append(slug)
    out: list[list[dict[str, object]]] = []
    for group_index, rows in enumerate(groups):
        kept_rows: list[dict[str, object]] = []
        for row_index, row in enumerate(rows):
            rebuilt = rebuild_cited_row(
                row,
                allowed.get((group_index, row_index), []),
                clone_flags,
            )
            if rebuilt is not None:
                kept_rows.append(rebuilt)
        out.append(kept_rows)
    return out


def drop_overlapping_gaps(
    themes: list[dict[str, object]],
    gaps: list[dict[str, object]],
) -> list[dict[str, object]]:
    theme_texts = [str(row.get("text") or "") for row in themes]
    kept: list[dict[str, object]] = []
    for gap in gaps:
        gap_text = str(gap.get("text") or "")
        overlap = False
        for theme_text in theme_texts:
            if token_jaccard(gap_text, theme_text) >= GAP_THEME_JACCARD:
                overlap = True
                break
        if not overlap:
            kept.append(gap)
    return kept


def write_synthesis(record: dict[str, object], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix="synthesis_",
        delete=False,
        encoding="utf-8",
    ) as handle:
        json.dump(record, handle, indent=2)
        tmp = Path(handle.name)
    try:
        loaded = json.loads(tmp.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise SystemExit("lint failed; not writing: root is not an object")
        errors = lint_synthesis(cast(dict[str, object], loaded))
        if errors:
            raise SystemExit("lint failed; not writing:\n" + "\n".join(errors))
        dest.write_text(tmp.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    finally:
        tmp.unlink(missing_ok=True)


def synthesize(*, write: bool = True) -> dict[str, object]:
    present, missing, dirty, audits = load_audits()
    if not audits:
        raise SystemExit("no lint-clean audit.json files yet")
    if not kiro_configured():
        raise SystemExit("ERROR: Set KIRO_GATEWAY_API_KEY or PROXY_API_KEY")
    clone_flags = product_clone_flags()
    payload: list[dict[str, object]] = []
    ledger_kept = 0
    ledger_seen = 0
    for slug, audit in zip(present, audits, strict=True):
        kept, total = compact_ledger(audit.get("ledger"), product_id=slug)
        ledger_kept += len(kept)
        ledger_seen += total
        payload.append(
            compact_audit(audit, clone=clone_flags.get(slug, False), product_id=slug)
        )
    user = (
        "Product-memory audits. Respond with ONLY a JSON object.\n\n"
        + json.dumps(payload, separators=JSON_SEPARATORS, ensure_ascii=False)
    )
    model = synthesize_model()
    present_set = set(present)
    cards_by_id = {slug: card for slug, card in zip(present, payload, strict=True)}
    with PipelineLogger("synthesize", source="seed", products=present) as log:
        log.info(
            "synthesize_started",
            present=len(present),
            missing=len(missing),
            missing_ids=missing,
            dirty_ids=dirty,
            user_chars=len(user),
            ledger_kept=ledger_kept,
            ledger_seen=ledger_seen,
            compact_version=COMPACT_VERSION,
            model=model,
        )
        parsed = call_kiro(
            user,
            SYSTEM_PROMPT
            + "\n\nIMPORTANT: Output ONLY the JSON object. No markdown fences.",
            temperature=0.1,
            max_tokens=SYNTHESIZE_MAX_TOKENS,
            timeout=SYNTHESIZE_TIMEOUT,
            model=model,
        )
        if parsed is None:
            log.error("synthesize_kiro_failed")
            raise SystemExit("synthesize: kiro returned no JSON")
        themes = ground_cited_rows(
            parsed.get("themes"),
            present_set,
            cards_by_id,
            clone_flags,
        )
        recurring = ground_cited_rows(
            parsed.get("recurring_mechanisms"),
            present_set,
            cards_by_id,
            clone_flags,
        )
        gaps = drop_overlapping_gaps(
            themes + recurring,
            ground_cited_rows(
                parsed.get("shared_gaps"),
                present_set,
                cards_by_id,
                clone_flags,
                require_negation=True,
            ),
        )
        themes, recurring, gaps = cap_product_rows(
            [themes, recurring, gaps],
            clone_flags,
        )
        record: dict[str, object] = {
            "observed_at": datetime.now(UTC).date().isoformat(),
            "products": present,
            "missing": missing,
            "dirty": dirty,
            "themes": themes,
            "recurring_mechanisms": recurring,
            "shared_gaps": gaps,
            "unknowns": filter_unknown_rows(parsed.get("unknowns")),
            "model": model,
            "compact_version": COMPACT_VERSION,
        }
        dest = OUTPUT_DIR / "synthesis.json"
        log.info(
            "synthesize_parsed",
            themes=len(themes),
            recurring=len(recurring),
            gaps=len(gaps),
        )
        lint_errors = lint_synthesis(record)
        if lint_errors:
            log.error("synthesize_lint_failed", errors=lint_errors[:20])
            raise SystemExit("synthesize lint failed:\n" + "\n".join(lint_errors))
        if write:
            write_synthesis(record, dest)
            log.action(
                "synthesis_written",
                path=str(dest),
                products=len(present),
                missing=len(missing),
            )
            print(f"wrote {dest} ({len(present)} products, {len(missing)} missing)")
        else:
            log.decision("synthesize_dry_run", products=len(present))
            print(json.dumps(record, indent=2))
        return record


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synthesize every lint-clean product audit.json"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    synthesize(write=not args.dry_run)


if __name__ == "__main__":
    main()
