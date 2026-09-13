"""Harvest pages into .cache/by-product/<slug>/. No LLM."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

from companmem_pipeline.httputil import (
    fetch_prose,
    fetch_with_retry,
    get_client,
    jitter,
    page_exists,
    save_page,
)
from companmem_pipeline.log import PipelineLogger
from companmem_pipeline.paths import (
    SEED_PATH,
    load_dotenv,
    product_cache,
)
from companmem_pipeline.search import host_of, web_search_stats

load_dotenv()

DOCS_CAP = 20
ISSUES_CAP = 20
ISSUE_FETCH_CAP = 50
BLOG_CAP = 10
SEARCH_CAP = 10
COMMUNITY_CAP = 10
CODE_FILE_CAP = 30
CODE_DIR_QUOTA = 4
DOCS_DIR_QUOTA = 3
MAX_API_PAGES = 4
MIN_HIGH_PACKAGE_FILES = 3
CONTENT_SCAN_CHARS = 32_768
SKIPPED_RECORD_CAP = 50
MAX_FILE_CHARS = 200_000
SITEMAP_LOC_CAP = 200
SITEMAP_CHILD_CAP = 5

SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    "vendor",
    ".venv",
    "venv",
    "testdata",
    "fixtures",
    ".tox",
    "target",
}
SKIP_CODE_PARTS = SKIP_DIRS | {
    "examples",
    "docs",
    "sandbox",
    "website",
    "benchmarks",
    "evaluation",
    "integrations",
    "tests",
    "test",
    "__tests__",
    ".github",
    ".gitlab",
    ".circleci",
}
SRC_ROOTS = {"src", "lib", "core"}
SOURCE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".rb"}
SCHEMA_STEMS = {"models", "schema"}
ROLE_PARTS = {"models", "schema", "store", "crud", "memory", "representation"}
LOW_ROLE_PARTS = {
    "scripts",
    "migrations",
    "website",
    "telemetry",
    "prometheus",
    "sentry",
    "llm",
    "startup",
    "cache",
}
HIGH_CODE_PACKAGES = {
    "deriver",
    "dialectic",
    "dreamer",
    "crud",
    "memory",
    "representation",
}
INFRA_CODE_PACKAGES = {"llm", "startup", "cache", "telemetry", "prometheus", "sentry"}
DOCS_VERSION_RE = re.compile(r"/v(\d+)(?:/|$)", re.I)
API_ENDPOINT_RE = re.compile(r"/endpoint/([^/]+)(?:/([^/]+))?", re.I)
MEMORY_NAME_RE = re.compile(
    r"(?:^|[^a-z0-9])"
    r"(?:memor(?:y|ies)|forget(?:ting)?|recall|remember(?:ing)?|"
    r"world[-_]?info|lore|personas?|episod\w*|vectors?|embed(?:ding)?s?)"
    r"(?:[^a-z0-9]|$)",
    re.I,
)
LICENSE_RE = re.compile(r"^(?:LICENSE|COPYING)(?:\..+)?$", re.I)
README_RE = re.compile(r"^README(?:\..+)?$", re.I)
GENERIC_META_EXT = r"(?:\.(?:md|txt|rst|adoc))?"
GENERIC_CODE_NAME_RE = re.compile(
    r"^(LICENSE|COPYING|NOTICE|AUTHORS|PATENTS|CHANGELOG|CHANGES|"
    r"CODE_OF_CONDUCT|CONTRIBUTING|SECURITY|MAINTAINERS|FUNDING|"
    r"PULL_REQUEST_TEMPLATE|ISSUE_TEMPLATE)"
    rf"{GENERIC_META_EXT}$",
    re.I,
)
TEST_CODE_NAME_RE = re.compile(
    r"^(?:test_.+|.*_test\.py|.*\.(?:test|spec)\.(?:ts|tsx|js|jsx))$",
    re.I,
)
GENERIC_DOC_PATH_RE = re.compile(
    r"/(?:licen[cs]es?|changelog|contributing|code[-_]of[-_]conduct)(?:/|\.|$)",
    re.I,
)
GITHUB_CHROME_RE = re.compile(
    r"^/[^/]+/[^/]+/?(?:$|(?:issues|pulls|pull|tags|releases|actions|"
    r"pulse|projects|wiki|discussions|commits|graphs|network|settings|"
    r"packages|deployments|rules|checks|security|compare)(?:/|$))",
    re.I,
)
MD_LINK_RE = re.compile(
    r"\[[^\]]+\]\(\s*<?([^)\s>]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)"
)
SKIP_HREF_RE = re.compile(
    r"^(?:javascript:|data:)|[.](?:png|jpe?g|gif|svg|webp|ico|pdf)(?:\?|#|$)",
    re.I,
)
SITEMAP_LOC_RE = re.compile(
    r"<(?:[\w.-]+:)?loc>\s*([^<]+)\s*</(?:[\w.-]+:)?loc>",
    re.I,
)
ISSUE_BOT_RE = re.compile(
    r"\[bot\]$|^(?:dependabot|renovate|github-actions)(?:\[bot\])?$",
    re.I,
)
ISSUE_NOISE_RE = re.compile(
    r"^(chore|ci|build|style|refactor)(\(|:)|"
    r"^test\(|"
    r"\bbump .+ from\b|\bdependabot\b|\bduplicate of\b|"
    r"\btypo\b|\bflaky\b|\blockfile\b|\bbump deps\b",
    re.I,
)
ISSUE_UX_RE = re.compile(
    r"\bremember(?:s|ing|ed)?\b|\bforgot(?:ten)?\b|\bforget(?:s|ting)?\b|"
    r"\brecall(?:s|ed|ing)?\b|"
    r"\bmemor(?:y|ies)\b|lost context|context window|"
    r"\bpersonas?\b|\bcompanions?\b|personaliz\w*|\bprivacy\b|"
    r"hallucin\w*|"
    r"doesn['’]t know (?:me|my|who)|does not know (?:me|my|who)|"
    r"doesn['’]t remember|does not remember|"
    r"doesn['’]t persist|never remember|"
    r"\bmy name\b|user experience|\bux\b|"
    r"delete memor(?:y|ies)|"
    r"cross[- ]sessions?",
    re.I,
)
PRODUCT_TOKEN_STOP = {
    "cloud",
    "labs",
    "lab",
    "official",
    "community",
    "open",
    "microsoft",
}
PRODUCT_TOKEN_MIN = 3
DOCS_INDEX_NAMES = frozenset(
    {
        "llms.txt",
        "llms-full.txt",
        "index.html",
        "index.md",
        "readme.md",
    }
)
ISSUE_TECH_BUG_RE = re.compile(
    r"typeerror|nullpointer|stack trace|segfault|\boom\b|race condition|"
    r"dockerfile|migration fail|\b500 error\b|connection refused|\bpytest\b|"
    r"compile error|import error",
    re.I,
)
COMMUNITY_HOST_SUFFIXES = (
    "news.ycombinator.com",
    "ycombinator.com",
    "reddit.com",
    "producthunt.com",
    "stackoverflow.com",
    "stackexchange.com",
    "x.com",
    "twitter.com",
    "lobste.rs",
)
SEARCH_MIRROR_HOSTS = (
    "deepwiki.com",
    "deepwiki.dev",
    "sourcegraph.com",
)
GITHUB_BLOB_RE = re.compile(
    r"https?://(?:www\.)?github\.com/[^/]+/[^/]+/(?:blob|tree|raw)/",
    re.I,
)
ARXIV_RE = re.compile(
    r"https?://(?:www\.)?(?:arxiv\.org|export\.arxiv\.org)/",
    re.I,
)
FORGE_HOSTS = {"github.com", "gitlab.com", "bitbucket.org", "codeberg.org"}
LOGIN_PATH_RE = re.compile(
    r"(?:^|/)(?:login|signin|sign-up|signup|signout|billing)(?:/|\?|$)",
    re.I,
)
README_CODE_PATH_RE = re.compile(
    r"(?:^|[\s`\"'(])((?:src|lib|core)[/\\][A-Za-z0-9_./-]+\.(?:py|ts|tsx|js|jsx|go|rs|rb))",
    re.I,
)


def utc_date() -> str:
    return datetime.now(UTC).date().isoformat()


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def load_seed() -> dict[str, object]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def product_ids() -> list[str]:
    seed = load_seed()
    products = seed.get("products")
    if not isinstance(products, dict):
        raise SystemExit("seed.json missing products")
    return [str(slug) for slug in products]


def require_str_list(product: dict[str, object], key: str) -> list[str]:
    slug = str(product.get("id") or "unknown")
    if key not in product:
        raise SystemExit(f"{slug} missing {key} in seed.json")
    value = product[key]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SystemExit(f"{slug} {key} must be a list of strings")
    return [item.strip() for item in value if item.strip()]


def load_product(slug: str) -> dict[str, object]:
    seed = load_seed()
    products = seed["products"]
    if not isinstance(products, dict) or slug not in products:
        raise SystemExit(f"unknown product slug: {slug}")
    product = dict(products[slug])
    product["census_sources"] = []
    return product


def product_path_tokens(product: dict[str, object] | None) -> list[str]:
    """This product's own name/id, not a hardcoded census of siblings."""
    if not product:
        return []
    tokens: list[str] = []
    seen: set[str] = set()
    for key in ("id", "name"):
        raw = str(product.get(key) or "")
        for part in re.split(r"[^a-z0-9]+", raw.lower()):
            if len(part) < PRODUCT_TOKEN_MIN or part in seen or part in PRODUCT_TOKEN_STOP:
                continue
            seen.add(part)
            tokens.append(part)
    return tokens


def product_mentioned(text: str, product: dict[str, object]) -> bool:
    """True when the thread names this product as a token, not a substring."""
    blob = text.lower()
    for key in ("name", "id"):
        raw = str(product.get(key) or "").strip().lower()
        if len(raw) < PRODUCT_TOKEN_MIN:
            continue
        if re.search(rf"(?:^|[^a-z0-9]){re.escape(raw)}(?:[^a-z0-9]|$)", blob):
            return True
    return False


def product_named_in_url_or_title(url: str, title: str, product: dict[str, object]) -> bool:
    """True when the page is about this product, not a sibling that mentions it in a snippet."""
    return product_mentioned(url, product) or product_mentioned(title, product)


def community_confirm_queries(host: str, product: dict[str, object]) -> list[str]:
    """Stricter follow-up search: title or product-hunt slug, not 'mentions Mem0 somewhere'."""
    name = str(product.get("name") or product["id"])
    slug = str(product.get("id") or "").strip()
    host = host.lower().removeprefix("www.")
    queries = [f'site:{host} intitle:"{name}"']
    if host.endswith("producthunt.com") and slug:
        queries.append(f"site:{host}/products/{slug}")
    return queries


def is_memory_path(rel: str, product: dict[str, object] | None = None) -> bool:
    if MEMORY_NAME_RE.search(rel):
        return True
    lowered = rel.lower()
    for token in product_path_tokens(product):
        if re.search(rf"(?:^|[^a-z0-9]){re.escape(token)}(?:[^a-z0-9]|$)", lowered):
            return True
    return False


def skip_url(url: str, prefixes: list[str]) -> bool:
    return any(url.startswith(p) for p in prefixes)


def normalize_url(url: str) -> str:
    return re.sub(r"[#?].*$", "", url).rstrip("/")


def page_slug(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_")[:80] or "index"
    path = re.sub(r"[^A-Za-z0-9._-]", "_", path)
    digest = hashlib.sha256(url.encode()).hexdigest()[:8]
    return f"{path}_{digest}"


def github_owner_repo(url: str) -> tuple[str, str] | None:
    if not url:
        return None
    match = re.search(
        r"(?:^|[@/])(?:www\.)?github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$",
        url.strip(),
    )
    if not match:
        return None
    return match.group(1), match.group(2).removesuffix(".git")


def is_generic_code_name(name: str) -> bool:
    return bool(GENERIC_CODE_NAME_RE.match(name))


def is_test_code_name(name: str) -> bool:
    return bool(TEST_CODE_NAME_RE.match(name))


def is_github_chrome_url(url: str) -> bool:
    if host_of(url) != "github.com":
        return False
    if GITHUB_BLOB_RE.match(url):
        return False
    return bool(GITHUB_CHROME_RE.search(urlparse(url).path))


def is_generic_docs_url(url: str) -> bool:
    if is_github_chrome_url(url):
        return True
    path = urlparse(url).path
    return bool(GENERIC_DOC_PATH_RE.search(path))


def is_marketing_home(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.path.strip("/") == "" and not parsed.query


def is_community_thread(url: str) -> bool:
    """True for a post/issue thread, not a profile or section index."""
    host = host_of(url)
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    parts = [p for p in path.split("/") if p]
    if host in {"news.ycombinator.com", "ycombinator.com"}:
        return "item" in path.lower() or "id=" in parsed.query
    if host.endswith("reddit.com"):
        return "/comments/" in path.lower()
    if host.endswith("stackoverflow.com") or host.endswith("stackexchange.com"):
        return "/questions/" in path.lower()
    if host.endswith("producthunt.com"):
        return "/posts/" in path.lower() or "/products/" in path.lower()
    if host in {"x.com", "twitter.com"}:
        return len(parts) >= 3 and parts[1].lower() == "status"
    if host.endswith("lobste.rs"):
        return len(parts) >= 2 and parts[0] == "s"
    if "discourse" in host or host.startswith("forum."):
        return "/t/" in path.lower()
    return True


def docs_path_version(url: str) -> int | None:
    match = DOCS_VERSION_RE.search(urlparse(url).path)
    if not match:
        return None
    return int(match.group(1))


def docs_kind(url: str) -> str:
    path = urlparse(url).path.lower()
    if "llms" in path and path.endswith(".txt"):
        return "index"
    if "/endpoint/" in path:
        return "api_endpoint"
    if "api-reference" in path or "/reference/" in path:
        return "api"
    if is_memory_path(path):
        return "memory"
    if any(
        token in path
        for token in (
            "concept",
            "guide",
            "architecture",
            "overview",
            "introduction",
            "documentation",
            "tutorial",
        )
    ):
        return "concepts"
    return "other"


def docs_dir_key(url: str) -> str:
    parts = [p for p in urlparse(url).path.lower().split("/") if p]
    if not parts:
        return "."
    if parts[-1].endswith(".txt"):
        return "index"
    if len(parts) >= 4:
        return "/".join(parts[:4])
    if len(parts) > 1:
        return "/".join(parts[:-1])
    return parts[0]


def api_resource_key(url: str) -> str | None:
    match = API_ENDPOINT_RE.search(urlparse(url).path)
    if not match:
        return None
    return match.group(1).lower()


def api_page_sort(url: str) -> tuple[int, str]:
    name = urlparse(url).path.rstrip("/").rsplit("/", 1)[-1].lower()
    if any(token in name for token in ("intro", "overview", "index")):
        return (0, name)
    if name.startswith(("get-", "list-", "get_", "list_")) or name in {"get", "list"}:
        return (1, name)
    return (2, name)


def docs_sort_key(url: str, product: dict[str, object] | None, from_llms: set[str]) -> tuple:
    path = urlparse(url).path.lower()
    kind = docs_kind(url)
    wave = {
        "index": 0,
        "concepts": 0,
        "memory": 0,
        "other": 1,
        "api": 2,
        "api_endpoint": 2,
    }[kind]
    llms_boost = 0 if normalize_url(url) in from_llms else 1
    mem = 0 if is_memory_path(path, product) else 1
    return (wave, llms_boost, mem, len(path), url)


@dataclass
class DocsSelection:
    urls: list[str]
    signaled: int
    must_open: list[str]
    skipped: list[dict[str, str]]
    skipped_total: int = 0

    def as_dict(self) -> dict[str, object]:
        return {
            "signaled": self.signaled,
            "kept": len(self.urls),
            "must_open": self.must_open,
            "skipped": self.skipped,
            "skipped_total": self.skipped_total,
        }


def select_docs_urls(
    urls: list[str],
    product: dict[str, object] | None = None,
    *,
    from_llms: set[str] | None = None,
    already: set[str] | None = None,
    cap: int = DOCS_CAP,
    skip_home: bool = False,
) -> DocsSelection:
    """Rank docs URLs: newest version, collapse API verbs, prefer guides over CRUD."""
    llms = {normalize_url(item) for item in (from_llms or set())}
    seen_already = already or set()
    candidates: list[str] = []
    seen: set[str] = set()
    for url in urls:
        key = normalize_url(url)
        if not url or key in seen or key in seen_already:
            continue
        if skip_home and is_marketing_home(url):
            continue
        seen.add(key)
        candidates.append(url)

    numbered = [v for u in candidates if (v := docs_path_version(u)) is not None]
    max_v = max(numbered) if numbered else None
    skipped: list[dict[str, str]] = []
    filtered: list[str] = []
    for url in candidates:
        ver = docs_path_version(url)
        if max_v is not None and ver is not None and ver < max_v:
            skipped.append({"path": url, "reason": "old_version"})
            continue
        filtered.append(url)

    by_resource: dict[str, list[str]] = {}
    non_api: list[str] = []
    for url in filtered:
        resource = api_resource_key(url)
        if resource and docs_kind(url) == "api_endpoint":
            by_resource.setdefault(resource, []).append(url)
        else:
            non_api.append(url)
    collapsed_api: list[str] = []
    for group in by_resource.values():
        winner = min(group, key=lambda item: (api_page_sort(item), item))
        collapsed_api.append(winner)
        for url in group:
            if url != winner:
                skipped.append({"path": url, "reason": "api_collapse"})
    collapsed_api.sort(key=lambda item: (api_page_sort(item), item))
    for url in collapsed_api[MAX_API_PAGES:]:
        skipped.append({"path": url, "reason": "api_cap"})
    collapsed_api = collapsed_api[:MAX_API_PAGES]
    pool = non_api + collapsed_api

    must = [url for url in pool if docs_kind(url) == "index"]
    rest = [url for url in pool if url not in must]
    rest.sort(key=lambda item: docs_sort_key(item, product, llms))
    by_dir: dict[str, list[str]] = {}
    for url in rest:
        by_dir.setdefault(docs_dir_key(url), []).append(url)

    kept: list[str] = []
    seen_kept: set[str] = set()
    for url in must:
        key = normalize_url(url)
        if key in seen_kept:
            continue
        kept.append(url)
        seen_kept.add(key)
        if len(kept) >= cap:
            break

    def dir_wave(key: str) -> int:
        return docs_sort_key(by_dir[key][0], product, llms)[0]

    for wave in (0, 1, 2):
        wave_dirs = [key for key in by_dir if dir_wave(key) == wave]
        round_idx = 0
        while len(kept) < cap and wave_dirs:
            added = False
            if round_idx >= DOCS_DIR_QUOTA:
                break
            for key in sorted(wave_dirs):
                files = by_dir[key]
                if round_idx >= len(files):
                    continue
                url = files[round_idx]
                norm = normalize_url(url)
                if norm in seen_kept:
                    continue
                kept.append(url)
                seen_kept.add(norm)
                added = True
                if len(kept) >= cap:
                    break
            if not added:
                break
            round_idx += 1
        if len(kept) >= cap:
            break

    skipped_urls = {row["path"] for row in skipped}
    for url in pool:
        if normalize_url(url) not in seen_kept and url not in skipped_urls:
            skipped.append({"path": url, "reason": "cap"})

    must_open = [url for url in kept if docs_kind(url) == "index"]
    return DocsSelection(
        urls=kept,
        signaled=len(candidates),
        must_open=must_open,
        skipped=skipped[:SKIPPED_RECORD_CAP],
        skipped_total=len(skipped),
    )


def parse_sitemap_locs(xml_text: str) -> list[str]:
    return [
        html.unescape(loc.strip())
        for loc in SITEMAP_LOC_RE.findall(xml_text)
        if loc.strip()
    ]


def sitemap_index_urls(docs_url: str) -> list[str]:
    parsed = urlparse(docs_url)
    if not parsed.scheme or not parsed.netloc:
        return []
    if host_of(docs_url) in FORGE_HOSTS:
        return []
    root = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path.rsplit("/", 1)[0] if "/" in parsed.path.strip("/") else ""
    nested = f"{root}{path}" if path else root
    candidates = [
        f"{root}/sitemap.xml",
        f"{root}/sitemap_index.xml",
        f"{root}/sitemap-index.xml",
        f"{nested}/sitemap.xml",
        f"{root}/docs/sitemap.xml",
        f"{root}/robots.txt",
    ]
    seen: set[str] = set()
    out: list[str] = []
    for url in candidates:
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def parse_robots_sitemaps(text: str) -> list[str]:
    urls: list[str] = []
    for line in text.splitlines():
        if line.lower().startswith("sitemap:"):
            loc = line.split(":", 1)[1].strip()
            if loc.startswith("http"):
                urls.append(loc)
    return urls


def collect_sitemap_locs(
    client: httpx.Client,
    docs_url: str,
    log: PipelineLogger,
) -> list[str]:
    """Follow robots.txt and sitemap.xml on the docs host. First-party only."""
    found: list[str] = []
    child_sitemaps: list[str] = []
    for candidate in sitemap_index_urls(docs_url):
        resp = fetch_with_retry(client, candidate)
        jitter()
        if resp is None:
            continue
        body = resp.text
        if candidate.endswith("robots.txt"):
            child_sitemaps.extend(parse_robots_sitemaps(body))
            continue
        ctype = resp.headers.get("content-type", "")
        if "gzip" in ctype or candidate.endswith(".gz"):
            continue
        locs = parse_sitemap_locs(body)
        if "sitemapindex" in body[:500].lower() or "<sitemap>" in body[:800].lower():
            child_sitemaps.extend(locs)
        else:
            found.extend(locs)
        log.info("sitemap_read", url=str(resp.url), locs=len(locs))
    for child in child_sitemaps[:SITEMAP_CHILD_CAP]:
        if not child.startswith("http") or child.endswith(".gz"):
            continue
        resp = fetch_with_retry(client, child)
        jitter()
        if resp is None:
            continue
        found.extend(parse_sitemap_locs(resp.text))
    seen: set[str] = set()
    unique: list[str] = []
    for url in found:
        key = normalize_url(url)
        if key in seen:
            continue
        seen.add(key)
        unique.append(url)
        if len(unique) >= SITEMAP_LOC_CAP:
            break
    return unique


def is_noisy_issue(item: dict[str, object]) -> bool:
    title = str(item.get("title") or "")
    user = ""
    raw_user = item.get("user")
    if isinstance(raw_user, dict):
        user = str(raw_user.get("login") or "")
    if ISSUE_BOT_RE.search(user):
        return True
    if ISSUE_NOISE_RE.search(title):
        return True
    labels: list[str] = []
    raw_labels = item.get("labels") or []
    if isinstance(raw_labels, list):
        for lab in raw_labels:
            if isinstance(lab, dict):
                labels.append(str(lab.get("name") or "").lower())
            elif isinstance(lab, str):
                labels.append(lab.lower())
    if any(name in {"dependencies", "ci", "infra", "duplicate"} for name in labels):
        if not ISSUE_UX_RE.search(title):
            return True
    return False


def issue_sort_key(item: dict[str, object]) -> tuple[int, int, int, int]:
    title = str(item.get("title") or "")
    body = str(item.get("body") or "")[:4000]
    blob = f"{title}\n{body}"
    ux = 0 if ISSUE_UX_RE.search(blob) else 1
    tech = 0 if not ISSUE_TECH_BUG_RE.search(blob) else 1
    reactions = 0
    raw_react = item.get("reactions")
    if isinstance(raw_react, dict):
        reactions = int(raw_react.get("total_count") or 0)
    comments = int(item.get("comments") or 0)
    return (ux, tech, -reactions, -comments)


def is_community_host(host: str) -> bool:
    host = host.lower().removeprefix("www.")
    if "discourse" in host or host.startswith("forum."):
        return True
    return any(host == suffix or host.endswith("." + suffix) for suffix in COMMUNITY_HOST_SUFFIXES)


def community_search_queries(name: str) -> list[str]:
    return [
        f"site:news.ycombinator.com {name} memory",
        f"site:reddit.com {name} memory",
        f"site:producthunt.com {name}",
        f"site:stackoverflow.com {name} memory",
        f"{name} memory reddit",
        f'{name} memory "hacker news"',
        f"{name} memory forum",
    ]


def has_listed_docs(product: dict[str, object]) -> bool:
    listed = product.get("open_docs")
    if not isinstance(listed, list):
        return False
    return any(isinstance(item, str) and item.strip() for item in listed)


def search_queries(product: dict[str, object]) -> list[str]:
    """Claim-shaped web queries. Wikipedia only for closed products. Not forums."""
    name = str(product.get("name") or product["id"])
    queries = [
        f'{name} "doesn\'t remember" OR "does not remember"',
        f'{name} "lost context" OR forget',
        f"{name} LoCoMo",
        f"{name} graph memory OR vector memory",
        f"{name} companion memory",
    ]
    docs = product.get("docs")
    if isinstance(docs, str) and docs:
        host = host_of(docs)
        if host and host not in FORGE_HOSTS:
            prefix = docs_host_path_prefix(product) or ""
            queries.append(f"site:{host}{prefix} forget OR memory OR companion")
    if not product.get("clone"):
        queries.append(f"site:en.wikipedia.org {name}")
    return queries


def is_search_mirror_host(host: str) -> bool:
    host = host.lower().removeprefix("www.")
    if host.endswith(".github.io"):
        return True
    return any(host == suffix or host.endswith("." + suffix) for suffix in SEARCH_MIRROR_HOSTS)


def search_url_skip_reason(
    url: str,
    prefixes: list[str],
    *,
    skip_home: bool = False,
) -> str | None:
    """Why this URL is not a search landing page. None means fetch it."""
    if not url:
        return "empty"
    if not url.startswith(("http://", "https://")):
        return "not_http"
    if skip_url(url, prefixes):
        return "skip_prefix"
    if GITHUB_BLOB_RE.match(url):
        return "github_blob"
    if ARXIV_RE.match(url):
        return "arxiv"
    if LOGIN_PATH_RE.search(urlparse(url).path):
        return "login"
    host = host_of(url)
    if not host:
        return "no_host"
    if is_community_host(host):
        return "community_host"
    if host in FORGE_HOSTS:
        return "forge"
    if is_search_mirror_host(host):
        return "mirror"
    if is_generic_docs_url(url):
        return "generic_docs"
    if skip_home and is_marketing_home(url):
        return "marketing_home"
    return None


def is_search_url(url: str, prefixes: list[str], *, skip_home: bool = False) -> bool:
    """True for a fetchable search landing page. Community and forge stay other lanes."""
    return search_url_skip_reason(url, prefixes, skip_home=skip_home) is None


def community_url_skip_reason(
    url: str,
    prefixes: list[str],
    seed_urls: set[str],
) -> str | None:
    if not url:
        return "empty"
    if skip_url(url, prefixes):
        return "skip_prefix"
    if GITHUB_BLOB_RE.match(url):
        return "github_blob"
    if ARXIV_RE.match(url):
        return "arxiv"
    if LOGIN_PATH_RE.search(urlparse(url).path):
        return "login"
    if not is_community_host(host_of(url)):
        return "not_community_host"
    if normalize_url(url) not in seed_urls and not is_community_thread(url):
        return "not_thread"
    return None


def select_search_urls(
    urls: list[str],
    product: dict[str, object],
    repo_meta: dict[str, object],
    already: set[str],
    *,
    cap: int = SEARCH_CAP,
) -> tuple[list[str], bool]:
    """Dedupe search hits. First-party extras first. Cap without filling docs."""
    prefixes = [str(p) for p in (product.get("skip_url_prefixes") or [])]
    skip_home = has_listed_docs(product)
    seen: set[str] = set()
    first_party: list[str] = []
    third_party: list[str] = []
    for url in urls:
        key = normalize_url(url)
        if key in seen or key in already:
            continue
        reason = search_url_skip_reason(url, prefixes, skip_home=skip_home)
        if reason:
            continue
        if sibling_on_shared_host(url, product, repo_meta):
            continue
        seen.add(key)
        if allowed_source_url(url, product, repo_meta):
            first_party.append(url)
        else:
            third_party.append(url)
    unique = first_party + third_party
    return unique[:cap], len(unique) > cap


def search_page_meta(
    url: str,
    product: dict[str, object],
    repo_meta: dict[str, object],
) -> tuple[str, str]:
    """ledger kind and quality. Third-party stays discovery until a first-party page."""
    if allowed_source_url(url, product, repo_meta):
        path = urlparse(url).path.lower()
        host = host_of(url)
        if "/blog" in path or host.startswith("blog."):
            return "blog", "high"
        return "docs", "high"
    return "blog", "medium"


def run_git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=300,
    )


def write_unavailable(lane_dir: Path, reason: str) -> None:
    lane_dir.mkdir(parents=True, exist_ok=True)
    (lane_dir / "unavailable.json").write_text(
        json.dumps({"reason": reason, "observed_at": utc_date()}, indent=2),
        encoding="utf-8",
    )


def detect_license(repo_dir: Path) -> str | None:
    for path in repo_dir.iterdir():
        if path.is_file() and LICENSE_RE.match(path.name):
            head = path.read_text(encoding="utf-8", errors="replace")[:4000].lower()
            if "gnu affero" in head:
                return "AGPL-3.0"
            if "apache license" in head and "2.0" in head:
                return "Apache-2.0"
            if "mit license" in head:
                return "MIT"
            if "gnu general public license" in head and "version 3" in head:
                return "GPL-3.0"
            return path.name
    return None


def public_https_repo(origin: object, seed_repo: object) -> str | None:
    pair = github_owner_repo(str(origin or "")) or github_owner_repo(str(seed_repo or ""))
    if pair:
        return f"https://github.com/{pair[0]}/{pair[1]}"
    if isinstance(seed_repo, str) and seed_repo.startswith("http"):
        return seed_repo.rstrip("/")
    return None


@dataclass
class CodeCandidate:
    path: Path
    rel: str
    must: bool
    path_hit: bool
    content_hits: int
    role: int
    reasons: list[str] = field(default_factory=list)

    def sort_key(self) -> tuple[int, int, int, int, int, str]:
        return (
            0 if self.must else 1,
            self.role,
            0 if self.path_hit else 1,
            -min(self.content_hits, 20),
            len(Path(self.rel).parts),
            self.rel.lower(),
        )


@dataclass
class CodeSelection:
    files: list[Path]
    eligible: int
    signaled: int
    must_open: list[str]
    skipped: list[dict[str, str]]
    skipped_total: int = 0

    def as_dict(self) -> dict[str, object]:
        return {
            "eligible": self.eligible,
            "signaled": self.signaled,
            "kept": len(self.files),
            "must_open": self.must_open,
            "skipped": self.skipped,
            "skipped_total": self.skipped_total,
        }


def _code_dir_key(rel: str) -> str:
    """Quota bucket: src/deriver/*, including nested trees, share one cap."""
    parts = Path(rel).parts
    if len(parts) == 1:
        return "."
    if parts[0].lower() in SRC_ROOTS:
        if len(parts) == 2:
            return parts[0]
        return f"{parts[0]}/{parts[1]}"
    parent = Path(rel).parent.as_posix()
    return "." if parent == "." else parent


def _package_leaf(key: str) -> str:
    return Path(key).name.lower()


def _is_high_code_package(key: str) -> bool:
    leaf = _package_leaf(key)
    return leaf in HIGH_CODE_PACKAGES or any(name in leaf for name in HIGH_CODE_PACKAGES)


def _is_infra_code_package(key: str) -> bool:
    parts = [p.lower() for p in Path(key).parts]
    return any(part in INFRA_CODE_PACKAGES or part in LOW_ROLE_PARTS for part in parts)


def _is_package_module(rel: Path) -> bool:
    return len(rel.parts) >= 2 and path_stem(rel) == rel.parts[-2].lower()


def path_stem(rel: Path) -> str:
    return rel.stem.lower()


def code_role(rel: Path) -> int:
    parts = [p.lower() for p in rel.parts]
    name = rel.name
    stem = rel.stem.lower()
    if "tests" in parts or "test" in parts or is_test_code_name(name):
        return 5
    if any(part in LOW_ROLE_PARTS for part in parts) or any(
        "cli" in part or part.startswith("mock") for part in parts
    ):
        return 4
    if rel.suffix.lower() not in SOURCE_EXTS:
        return 3
    if stem in SCHEMA_STEMS or any(
        part in ROLE_PARTS or "store" in part or "memory" in part for part in parts
    ):
        return 0
    if _is_package_module(rel):
        return 0
    if parts and parts[0] in SRC_ROOTS:
        return 1
    return 3


def _is_schema_file(rel: Path) -> bool:
    if not rel.parts or rel.parts[0].lower() not in SRC_ROOTS:
        return False
    return rel.stem.lower() in SCHEMA_STEMS


def _eligible_code_file(path: Path, repo_dir: Path) -> Path | None:
    if not path.is_file():
        return None
    try:
        repo_root = repo_dir.resolve()
        resolved = path.resolve()
        rel = resolved.relative_to(repo_root)
    except (ValueError, OSError):
        return None
    if any(part in SKIP_CODE_PARTS for part in rel.parts):
        return None
    if is_test_code_name(resolved.name):
        return None
    if is_generic_code_name(resolved.name):
        return None
    is_root_readme = len(rel.parts) == 1 and README_RE.match(resolved.name)
    if not is_root_readme and resolved.suffix.lower() not in SOURCE_EXTS:
        return None
    try:
        if path.stat().st_size > MAX_FILE_CHARS:
            return None
    except OSError:
        return None
    return resolved


def content_memory_hits(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:CONTENT_SCAN_CHARS]
    except OSError:
        return 0
    return len(MEMORY_NAME_RE.findall(text))


def readme_named_paths(repo_dir: Path, readme: Path) -> list[Path]:
    try:
        text = readme.read_text(encoding="utf-8", errors="replace")[:MAX_FILE_CHARS]
    except OSError:
        return []
    found: list[Path] = []
    seen: set[Path] = set()
    hrefs = list(MD_LINK_RE.findall(text))
    hrefs.extend(README_CODE_PATH_RE.findall(text))
    repo_root = repo_dir.resolve()
    for href in hrefs:
        href = href.strip().split("#", 1)[0]
        if not href or href.startswith(("http://", "https://", "mailto:", "javascript:")):
            continue
        target = (readme.parent / href).resolve()
        try:
            target.relative_to(repo_root)
        except ValueError:
            continue
        if target in seen or not target.is_file():
            continue
        picked = _eligible_code_file(target, repo_dir)
        if picked is None:
            continue
        seen.add(picked)
        found.append(picked)
    return found


def select_code_inventory(
    repo_dir: Path,
    product: dict[str, object] | None = None,
) -> CodeSelection:
    """Score src files by path, content, and role. Cap per directory. Record misses."""
    repo_root = repo_dir.resolve()
    readmes: list[Path] = []
    eligible_paths: list[Path] = []
    for path in repo_dir.rglob("*"):
        picked = _eligible_code_file(path, repo_dir)
        if picked is None:
            continue
        rel = picked.relative_to(repo_root)
        if len(rel.parts) == 1 and README_RE.match(picked.name):
            readmes.append(picked)
            continue
        eligible_paths.append(picked)

    must_paths: set[Path] = set(readmes)
    for readme in readmes:
        must_paths.update(readme_named_paths(repo_dir, readme))
    for path in eligible_paths:
        if _is_schema_file(path.relative_to(repo_root)):
            must_paths.add(path)

    by_path: dict[Path, CodeCandidate] = {}
    for path in eligible_paths:
        rel_path = path.relative_to(repo_root)
        rel = rel_path.as_posix()
        path_hit = is_memory_path(rel, product)
        hits = content_memory_hits(path)
        must = path in must_paths
        signaled = must or path_hit or hits > 0
        if not signaled:
            continue
        reasons: list[str] = []
        if must:
            reasons.append("must")
        if path_hit:
            reasons.append("path")
        if hits:
            reasons.append("content")
        by_path[path] = CodeCandidate(
            path=path,
            rel=rel,
            must=must,
            path_hit=path_hit,
            content_hits=hits,
            role=code_role(rel_path),
            reasons=reasons,
        )

    signaled_dirs = {_code_dir_key(c.rel) for c in by_path.values()}
    for path in eligible_paths:
        if path in by_path:
            continue
        rel_path = path.relative_to(repo_root)
        if not _is_package_module(rel_path):
            continue
        dir_key = _code_dir_key(rel_path.as_posix())
        if dir_key not in signaled_dirs:
            continue
        by_path[path] = CodeCandidate(
            path=path,
            rel=rel_path.as_posix(),
            must=False,
            path_hit=False,
            content_hits=0,
            role=0,
            reasons=["package_root"],
        )

    for readme in readmes:
        rel = readme.relative_to(repo_root).as_posix()
        by_path[readme] = CodeCandidate(
            path=readme,
            rel=rel,
            must=True,
            path_hit=False,
            content_hits=0,
            role=0,
            reasons=["must"],
        )

    ranked = sorted(by_path.values(), key=lambda c: c.sort_key())
    must_kept: list[CodeCandidate] = []
    rest: list[CodeCandidate] = []
    for cand in ranked:
        if cand.must:
            must_kept.append(cand)
        else:
            rest.append(cand)

    by_dir: dict[str, list[CodeCandidate]] = {}
    for cand in rest:
        by_dir.setdefault(_code_dir_key(cand.rel), []).append(cand)

    def dir_wave(key: str) -> int:
        if key == ".":
            return 2
        parts = [p.lower() for p in Path(key).parts]
        if any(
            part in LOW_ROLE_PARTS or "cli" in part or part.startswith("mock") for part in parts
        ):
            return 1
        if _is_high_code_package(key) or any(
            part in HIGH_CODE_PACKAGES or "store" in part for part in parts
        ):
            return 0
        first = parts[0] if parts else ""
        if first in SRC_ROOTS:
            return 0
        return 2

    kept: list[CodeCandidate] = []
    seen: set[Path] = set()
    for cand in must_kept:
        if cand.path in seen:
            continue
        kept.append(cand)
        seen.add(cand.path)
        if len(kept) >= CODE_FILE_CAP:
            break

    for wave in (0, 1, 2):
        wave_dirs = [key for key in by_dir if dir_wave(key) == wave]
        round_idx = 0
        while len(kept) < CODE_FILE_CAP and wave_dirs:
            added = False
            if round_idx >= CODE_DIR_QUOTA:
                break
            for key in sorted(wave_dirs):
                files = by_dir[key]
                if round_idx >= len(files):
                    continue
                cand = files[round_idx]
                if cand.path in seen:
                    continue
                kept.append(cand)
                seen.add(cand.path)
                added = True
                if len(kept) >= CODE_FILE_CAP:
                    break
            if not added:
                break
            round_idx += 1
        if len(kept) >= CODE_FILE_CAP:
            break

    for key, files in by_dir.items():
        if not _is_high_code_package(key):
            continue
        have = sum(1 for cand in kept if _code_dir_key(cand.rel) == key)
        while have < MIN_HIGH_PACKAGE_FILES and have < len(files) and len(kept) >= CODE_FILE_CAP:
            next_file = next((cand for cand in files if cand.path not in seen), None)
            if next_file is None:
                break
            victims = [
                cand
                for cand in kept
                if not cand.must
                and _is_infra_code_package(_code_dir_key(cand.rel))
            ]
            if not victims:
                victims = [
                    cand
                    for cand in kept
                    if not cand.must and not _is_high_code_package(_code_dir_key(cand.rel))
                ]
            if not victims:
                break
            victim = sorted(victims, key=lambda cand: cand.sort_key(), reverse=True)[0]
            kept.remove(victim)
            seen.discard(victim.path)
            kept.append(next_file)
            seen.add(next_file.path)
            have += 1

    skipped: list[dict[str, str]] = []
    for cand in ranked:
        if cand.path in seen:
            continue
        key = _code_dir_key(cand.rel)
        rest_files = by_dir.get(key, [])
        try:
            idx = rest_files.index(cand)
        except ValueError:
            idx = 0
        reason = "quota" if idx >= CODE_DIR_QUOTA else "cap"
        skipped.append({"path": cand.rel, "reason": reason})

    must_open = sorted({c.rel for c in kept if c.must})
    skipped_rows = skipped[:SKIPPED_RECORD_CAP]
    return CodeSelection(
        files=[c.path for c in kept],
        eligible=len(eligible_paths) + len(readmes),
        signaled=len(by_path),
        must_open=must_open,
        skipped=skipped_rows,
        skipped_total=len(skipped),
    )


def select_code_files(
    repo_dir: Path,
    product: dict[str, object] | None = None,
) -> list[Path]:
    """Listed seed paths when open_code is set. Ranker is not the harvest path."""
    if product is not None and "open_code" in product:
        return select_listed_code_files(repo_dir, require_str_list(product, "open_code")).files
    return select_code_inventory(repo_dir, product).files


def select_listed_code_files(repo_dir: Path, listed: list[str]) -> CodeSelection:
    """Fetch exactly the seed paths. Missing paths are skipped, not ranked around."""
    repo_root = repo_dir.resolve()
    files: list[Path] = []
    skipped: list[dict[str, str]] = []
    seen: set[Path] = set()
    for rel in listed:
        target = (repo_dir / rel).resolve()
        try:
            target.relative_to(repo_root)
        except ValueError:
            skipped.append({"path": rel, "reason": "outside_repo"})
            continue
        if not target.is_file():
            skipped.append({"path": rel, "reason": "missing"})
            continue
        if target in seen:
            continue
        seen.add(target)
        files.append(target)
    return CodeSelection(
        files=files,
        eligible=len(listed),
        signaled=len(listed),
        must_open=list(listed),
        skipped=skipped[:SKIPPED_RECORD_CAP],
        skipped_total=len(skipped),
    )


def print_code_inventory(repo_dir: Path) -> None:
    """Print source files so a human can fill open_code. No ranking."""
    repo_root = repo_dir.resolve()
    for path in sorted(repo_dir.rglob("*")):
        picked = _eligible_code_file(path, repo_dir)
        if picked is None:
            continue
        print(picked.relative_to(repo_root).as_posix())


def harvest_repo(
    cache: Path,
    product: dict[str, object],
    log: PipelineLogger,
    *,
    force: bool,
    inventory: bool = False,
) -> dict[str, object]:
    repo_url = product.get("repo")
    clone = bool(product.get("clone"))
    repo_dir = cache / "repo"
    result: dict[str, object] = {
        "lane": "repo",
        "truncated": False,
        "pages": [],
        "sha": None,
        "origin": None,
        "license": None,
        "skipped": False,
    }
    if not clone or not repo_url:
        write_unavailable(repo_dir, "closed_or_no_public_repo")
        result["skipped"] = True
        log.info("repo_skipped", reason="closed_or_no_public_repo")
        return result

    git_dir = repo_dir / ".git"
    if git_dir.exists() and not force:
        log.info("repo_clone_skipped", path=str(repo_dir))
    else:
        if repo_dir.exists() and force:
            shutil.rmtree(repo_dir)
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        proc = run_git(
            ["clone", "--depth", "1", "--single-branch", str(repo_url), str(repo_dir)]
        )
        if proc.returncode != 0:
            write_unavailable(repo_dir, proc.stderr[-500:] or "git_clone_failed")
            log.error("repo_clone_failed", stderr=proc.stderr[-300:])
            result["skipped"] = True
            return result
        log.action("repo_cloned", url=repo_url)

    sha_proc = run_git(["rev-parse", "HEAD"], cwd=repo_dir)
    origin_proc = run_git(["remote", "get-url", "origin"], cwd=repo_dir)
    sha = sha_proc.stdout.strip() or None
    origin = origin_proc.stdout.strip() or str(repo_url)
    result["sha"] = sha
    result["origin"] = origin
    result["license"] = detect_license(repo_dir)
    if inventory:
        print_code_inventory(repo_dir)
        return result

    listed = require_str_list(product, "open_code")
    files = select_listed_code_files(repo_dir, listed)
    result["truncated"] = False
    result["code_selection"] = files.as_dict()
    owner_repo = github_owner_repo(origin) or github_owner_repo(str(repo_url))
    pages: list[dict[str, object]] = []
    code_root = cache / "code"
    repo_root = repo_dir.resolve()
    for path in files.files:
        rel = path.relative_to(repo_root).as_posix()
        slug = re.sub(r"[^A-Za-z0-9._-]", "_", rel)[:80]
        page_dir = code_root / slug
        if owner_repo and sha:
            blob_url = f"https://github.com/{owner_repo[0]}/{owner_repo[1]}/blob/{sha}/{rel}"
        else:
            blob_url = f"file:{rel}"
        if force or not page_exists(page_dir):
            text = path.read_text(encoding="utf-8", errors="replace")[:MAX_FILE_CHARS]
            save_page(
                page_dir,
                blob_url,
                text,
                {"relpath": rel, "sha": sha, "kind": "code"},
            )
        pages.append(
            {
                "id": f"code_{slug}",
                "lane": "code",
                "kind": "code",
                "url": blob_url,
                "path": str(page_dir.relative_to(cache) / "content.txt"),
                "quality": "high",
                "score_as_prose": False,
                "accessed_at": utc_date(),
            }
        )
    result["pages"] = pages
    for row in files.skipped:
        log.info("code_skipped", path=row.get("path"), reason=row.get("reason"))
    for page in pages:
        log.info("code_kept", path=page.get("path"), url=page.get("url"))
    log.info(
        "repo_pages",
        count=len(pages),
        truncated=result["truncated"],
        sha=sha,
        eligible=files.eligible,
        signaled=files.signaled,
        skipped=len(files.skipped),
    )
    return result


def parse_llms_links(text: str, base_url: str) -> list[str]:
    urls: list[str] = []
    for href in MD_LINK_RE.findall(text):
        href = href.strip()
        if href.startswith("#") or href.startswith("mailto:") or SKIP_HREF_RE.search(href):
            continue
        abs_url = urljoin(base_url, href)
        if abs_url.startswith("http"):
            urls.append(abs_url)
    return urls


def prefer_llms_full(docs_url: str) -> list[str]:
    candidates: list[str] = []
    if docs_url.endswith("llms.txt"):
        candidates.append(docs_url.replace("llms.txt", "llms-full.txt"))
        candidates.append(docs_url)
    else:
        parsed = urlparse(docs_url)
        root = f"{parsed.scheme}://{parsed.netloc}"
        base = docs_url.rstrip("/")
        candidates.extend(
            [
                f"{base}/llms-full.txt",
                f"{base}/llms.txt",
                f"{root}/llms-full.txt",
                f"{root}/llms.txt",
                docs_url,
            ]
        )
    # preserve order, unique
    seen: set[str] = set()
    out: list[str] = []
    for url in candidates:
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def harvest_docs(
    cache: Path,
    product: dict[str, object],
    repo_meta: dict[str, object],
    already: set[str],
    log: PipelineLogger,
    client: httpx.Client,
    *,
    force: bool,
) -> dict[str, object]:
    prefixes = [str(p) for p in (product.get("skip_url_prefixes") or [])]
    result: dict[str, object] = {"lane": "docs", "truncated": False, "pages": []}
    pages: list[dict[str, object]] = []
    listed = require_str_list(product, "open_docs")
    if not listed:
        log.info("docs_skipped", reason="empty_open_docs")
        result["docs_selection"] = {
            "signaled": 0,
            "kept": 0,
            "must_open": [],
            "skipped": [],
            "skipped_total": 0,
        }
        return result

    seen_local: set[str] = set()
    unique: list[str] = []
    skipped: list[dict[str, str]] = []
    for url in listed:
        key = normalize_url(url)
        if key in seen_local:
            skipped.append({"path": url, "reason": "dup"})
            log.info("docs_skipped", url=url, reason="dup")
            continue
        if key in already:
            skipped.append({"path": url, "reason": "already"})
            log.info("docs_skipped", url=url, reason="already")
            continue
        if skip_url(url, prefixes):
            skipped.append({"path": url, "reason": "skip_prefix"})
            log.info("docs_skipped", url=url, reason="skip_prefix")
            continue
        seen_local.add(key)
        unique.append(url)
    result["docs_selection"] = {
        "signaled": len(listed),
        "kept": len(unique),
        "must_open": list(listed),
        "skipped": skipped[:SKIPPED_RECORD_CAP],
        "skipped_total": len(skipped),
    }

    docs_root = cache / "docs"
    for url in unique:
        slug = page_slug(url)
        page_dir = docs_root / slug
        final_url = url
        converter: str | None = None
        if force or not page_exists(page_dir):
            page = fetch_prose(client, url)
            jitter()
            if page is None:
                log.warn("docs_fetch_failed", url=url)
                continue
            final_url = page.url
            if not allowed_source_url(final_url, product, repo_meta):
                log.warn("docs_skipped_off_product", url=final_url)
                continue
            if is_generic_docs_url(final_url):
                log.info("docs_skipped", url=final_url, reason="generic_docs")
                continue
            converter = page.converter
            save_page(
                page_dir,
                final_url,
                page.text[:MAX_FILE_CHARS],
                {"kind": "docs", "converter": converter},
            )
        else:
            final_url = (page_dir / "url.txt").read_text(encoding="utf-8").strip()
            if not allowed_source_url(final_url, product, repo_meta):
                log.warn("docs_skipped_off_product", url=final_url)
                continue
            if is_generic_docs_url(final_url):
                log.info("docs_skipped", url=final_url, reason="generic_docs")
                continue
        already.add(normalize_url(final_url))
        log.info("docs_kept", url=final_url, converter=converter)
        pages.append(
            {
                "id": f"docs_{slug}",
                "lane": "docs",
                "kind": "docs",
                "url": final_url,
                "path": str(page_dir.relative_to(cache) / "content.txt"),
                "quality": "high",
                "score_as_prose": True,
                "accessed_at": utc_date(),
            }
        )
    result["pages"] = pages
    log.info("docs_pages", count=len(pages), truncated=result["truncated"])
    return result


def harvest_issues(
    cache: Path,
    product: dict[str, object],
    repo_meta: dict[str, object],
    log: PipelineLogger,
    *,
    force: bool,
) -> dict[str, object]:
    result: dict[str, object] = {"lane": "issues", "truncated": False, "pages": []}
    origin = repo_meta.get("origin") or product.get("repo")
    pair = github_owner_repo(str(origin) if origin else "")
    if not pair:
        pair = github_owner_repo(str(product.get("repo") or ""))
    if not pair:
        write_unavailable(cache / "issues", "no_github_repo")
        log.info("issues_skipped", reason="no_github_repo")
        return result
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        write_unavailable(cache / "issues", "missing_GITHUB_TOKEN")
        log.warn("issues_skipped", reason="missing_GITHUB_TOKEN")
        return result

    owner, repo = pair
    query = (
        f"repo:{owner}/{repo} is:issue "
        "(memory OR forget OR forgot OR remember OR persona OR recall)"
    )
    url = "https://api.github.com/search/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "CompanmemResearch/0.1",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    try:
        resp = httpx.get(
            url,
            params={"q": query, "per_page": ISSUE_FETCH_CAP, "sort": "updated"},
            headers=headers,
            timeout=30.0,
        )
        if resp.status_code != 200:
            write_unavailable(cache / "issues", f"github_search_{resp.status_code}")
            log.error("issues_search_failed", status=resp.status_code)
            return result
        payload = resp.json()
    except httpx.HTTPError as exc:
        write_unavailable(cache / "issues", str(exc))
        log.error("issues_search_failed", error=str(exc))
        return result

    raw_items = [item for item in (payload.get("items") or []) if isinstance(item, dict)]
    ranked: list[dict[str, object]] = []
    noisy = 0
    for item in raw_items:
        if is_noisy_issue(item):
            noisy += 1
            log.info(
                "issues_skipped",
                url=item.get("html_url"),
                number=item.get("number"),
                title=str(item.get("title") or "")[:120],
                reason="noisy",
            )
            continue
        ranked.append(item)
    ranked.sort(key=issue_sort_key)
    total = int(payload.get("total_count") or 0)
    if total > ISSUES_CAP or len(ranked) > ISSUES_CAP:
        result["truncated"] = True
    pages: list[dict[str, object]] = []
    issues_root = cache / "issues"
    for item in ranked[:ISSUES_CAP]:
        html_url = str(item.get("html_url") or "")
        number = item.get("number")
        slug = str(number) if number is not None else page_slug(html_url)
        page_dir = issues_root / slug
        body = item.get("body") or ""
        title = item.get("title") or ""
        text = f"# {title}\n\n{body}\n"
        if force or not page_exists(page_dir):
            save_page(
                page_dir,
                html_url,
                text[:MAX_FILE_CHARS],
                {"kind": "issue", "number": number, "state": item.get("state")},
            )
        log.info("issues_kept", url=html_url, number=number, title=str(title)[:120])
        pages.append(
            {
                "id": f"issue_{slug}",
                "lane": "issues",
                "kind": "issue",
                "url": html_url,
                "path": str(page_dir.relative_to(cache) / "content.txt"),
                "quality": "medium",
                "score_as_prose": False,
                "accessed_at": utc_date(),
            }
        )
    result["pages"] = pages
    log.info(
        "issues_pages",
        count=len(pages),
        truncated=result["truncated"],
        fetched=len(raw_items),
        kept=len(pages),
        noisy=noisy,
        total_count=total,
    )
    return result


def first_party_hosts(product: dict[str, object], repo_meta: dict[str, object]) -> set[str]:
    """Product docs/marketing hosts. github.com is handled separately by repo path."""
    hosts: set[str] = set()
    docs = product.get("docs")
    if isinstance(docs, str) and docs:
        host = host_of(docs)
        if host and host not in FORGE_HOSTS:
            hosts.add(host)
            if host.startswith("docs."):
                hosts.add(host.removeprefix("docs."))
            if host.startswith("help."):
                hosts.add(host.removeprefix("help."))
    name = str(product.get("name") or product.get("id") or "").lower().replace(" ", "")
    extra = {
        "docs.mem0.ai",
        "mem0.ai",
        "help.getzep.com",
        "getzep.com",
        "docs.letta.com",
        "letta.com",
        "docs.honcho.dev",
        "honcho.dev",
        "plasticlabs.ai",
    }
    for extra_host in extra:
        stem = extra_host.replace("-", "").replace(".", "")
        if name and name in stem:
            hosts.add(extra_host)
    hosts.discard("")
    hosts.discard("github.com")
    return hosts


def docs_host_path_prefix(product: dict[str, object]) -> str | None:
    """Path under the docs host that is this product. None means the whole host."""
    docs = product.get("docs")
    if not isinstance(docs, str) or not docs:
        return None
    path = urlparse(docs).path.rstrip("/")
    if not path:
        return None
    name = path.rsplit("/", 1)[-1].lower()
    if name in DOCS_INDEX_NAMES:
        path = path[: -len(name)].rstrip("/")
    if not path:
        return None
    return path.lower()


def path_under_docs_prefix(path: str, prefix: str) -> bool:
    path = path.lower().rstrip("/") or "/"
    prefix = prefix.lower().rstrip("/")
    return path == prefix or path.startswith(prefix + "/") or path.startswith(prefix + ".")


def allowed_source_url(
    url: str,
    product: dict[str, object],
    repo_meta: dict[str, object],
) -> bool:
    """True if this URL is this product (docs host or this GitHub repo), not a sibling vendor."""
    parsed = urlparse(url)
    host = host_of(url)
    path = parsed.path
    if host in {"discord.com", "discord.gg"}:
        return False
    if LOGIN_PATH_RE.search(path):
        return False
    pair = github_owner_repo(str(repo_meta.get("origin") or "")) or github_owner_repo(
        str(product.get("repo") or "")
    )
    if host == "github.com":
        if not pair:
            return False
        prefix = f"/{pair[0]}/{pair[1]}".lower()
        return path.lower().startswith(prefix)
    if host not in first_party_hosts(product, repo_meta):
        return False
    prefix = docs_host_path_prefix(product)
    if not prefix:
        return True
    docs = product.get("docs")
    docs_host = host_of(str(docs)) if isinstance(docs, str) else ""
    if host == docs_host:
        return path_under_docs_prefix(path, prefix)
    if host.startswith("docs.") or host.startswith("help."):
        return True
    blob = path.lower()
    return any(
        re.search(rf"(?:^|[^a-z0-9]){re.escape(token)}(?:[^a-z0-9]|$)", blob)
        for token in product_path_tokens(product)
    )


def sibling_on_shared_host(
    url: str,
    product: dict[str, object],
    repo_meta: dict[str, object],
) -> bool:
    """True for another product's pages on this product's docs/marketing host."""
    host = host_of(url)
    if not host or host == "github.com":
        return False
    if host not in first_party_hosts(product, repo_meta):
        return False
    return not allowed_source_url(url, product, repo_meta)


def blog_seed_urls(product: dict[str, object]) -> list[str]:
    """First-party blog seeds. Do not treat GitHub profiles or github.blog as product blogs."""
    prefixes = [str(p) for p in (product.get("skip_url_prefixes") or [])]
    candidates: list[str] = []
    for src in product.get("census_sources") or []:
        if not isinstance(src, str):
            continue
        if GITHUB_BLOB_RE.match(src) or ARXIV_RE.match(src):
            continue
        if skip_url(src, prefixes):
            continue
        if "/blog" in src or "blog." in src or "medium.com" in src:
            if host_of(src) in FORGE_HOSTS or host_of(src) == "github.blog":
                continue
            candidates.append(src)
    docs = product.get("docs")
    if isinstance(docs, str) and docs:
        host = host_of(docs)
        if host and host not in FORGE_HOSTS:
            parsed = urlparse(docs)
            blog_host = host
            if host.startswith("docs.") or host.startswith("help."):
                blog_host = host.split(".", 1)[1]
            candidates.append(f"{parsed.scheme}://{blog_host}/blog")
            candidates.append(f"{parsed.scheme}://blog.{blog_host}/")
    seen: set[str] = set()
    unique: list[str] = []
    prefix = docs_host_path_prefix(product)
    for url in candidates:
        key = normalize_url(url)
        if key in seen:
            continue
        if prefix and not product_mentioned(url, product):
            continue
        seen.add(key)
        unique.append(url)
    return unique


def harvest_blog(
    cache: Path,
    product: dict[str, object],
    already: set[str],
    log: PipelineLogger,
    client: httpx.Client,
    *,
    force: bool,
) -> dict[str, object]:
    result: dict[str, object] = {"lane": "blog", "truncated": False, "pages": []}
    seeds = blog_seed_urls(product)
    log.info("blog_seeds", count=len(seeds), urls=seeds)
    unique: list[str] = []
    seen: set[str] = set()
    skipped: dict[str, int] = {}
    for url in seeds:
        key = normalize_url(url)
        if key in seen:
            skipped["dup"] = skipped.get("dup", 0) + 1
            log.info("blog_skipped", url=url, reason="dup")
            continue
        if key in already:
            skipped["already"] = skipped.get("already", 0) + 1
            log.info("blog_skipped", url=url, reason="already")
            continue
        seen.add(key)
        unique.append(url)
    if len(unique) > BLOG_CAP:
        result["truncated"] = True
        for url in unique[BLOG_CAP:]:
            skipped["cap"] = skipped.get("cap", 0) + 1
            log.info("blog_skipped", url=url, reason="cap")
        unique = unique[:BLOG_CAP]
    if not unique:
        log.info("blog_skipped", reason="no_seeds", skipped_by=skipped)
        return result

    pages: list[dict[str, object]] = []
    blog_root = cache / "blog"
    for url in unique:
        slug = page_slug(url)
        page_dir = blog_root / slug
        if force or not page_exists(page_dir):
            page = fetch_prose(client, url)
            jitter()
            if page is None:
                skipped["fetch_failed"] = skipped.get("fetch_failed", 0) + 1
                log.info("blog_skipped", url=url, reason="fetch_failed")
                continue
            save_page(
                page_dir,
                page.url,
                page.text[:MAX_FILE_CHARS],
                {"kind": "blog", "converter": page.converter},
            )
            final_url = page.url
            log.info("blog_kept", url=final_url, converter=page.converter)
        else:
            final_url = (page_dir / "url.txt").read_text(encoding="utf-8").strip()
            log.info("blog_kept", url=final_url)
        already.add(normalize_url(final_url))
        pages.append(
            {
                "id": f"blog_{slug}",
                "lane": "blog",
                "kind": "blog",
                "url": final_url,
                "path": str(page_dir.relative_to(cache) / "content.txt"),
                "quality": "medium",
                "score_as_prose": True,
                "accessed_at": utc_date(),
            }
        )
    result["pages"] = pages
    log.info(
        "blog_pages",
        count=len(pages),
        truncated=result["truncated"],
        skipped_by=skipped,
    )
    return result


def harvest_search(
    cache: Path,
    product: dict[str, object],
    repo_meta: dict[str, object],
    already: set[str],
    log: PipelineLogger,
    client: httpx.Client,
    *,
    force: bool,
) -> dict[str, object]:
    result: dict[str, object] = {"lane": "search", "truncated": False, "pages": []}
    prefixes = [str(p) for p in (product.get("skip_url_prefixes") or [])]
    skip_home = has_listed_docs(product)
    skipped: dict[str, int] = {}
    candidates: list[str] = []
    seen: set[str] = set()
    found = 0
    queries = search_queries(product)
    log.info("search_queries", queries=queries, skip_home=skip_home)
    for query in queries:
        hits, stats = web_search_stats(query, count=8)
        log.info("search_query", query=query, **stats)
        for hit in hits:
            found += 1
            url = hit.get("url") or ""
            title = (hit.get("title") or "")[:120]
            source = hit.get("source") or ""
            log.info("search_hit", url=url, title=title, engine=source, query=query)
            blob = f"{hit.get('title') or ''} {hit.get('snippet') or ''} {url}"
            if not url:
                skipped["empty"] = skipped.get("empty", 0) + 1
                log.info("search_skipped", url=url, reason="empty", query=query)
                continue
            if not allowed_source_url(url, product, repo_meta) and not product_mentioned(
                blob, product
            ):
                skipped["product_not_in_snippet"] = skipped.get("product_not_in_snippet", 0) + 1
                log.info("search_skipped", url=url, reason="product_not_in_snippet", query=query)
                continue
            reason = search_url_skip_reason(url, prefixes, skip_home=skip_home)
            if reason:
                skipped[reason] = skipped.get(reason, 0) + 1
                log.info("search_skipped", url=url, reason=reason, query=query)
                continue
            if sibling_on_shared_host(url, product, repo_meta):
                skipped["sibling_host"] = skipped.get("sibling_host", 0) + 1
                log.info("search_skipped", url=url, reason="sibling_host", query=query)
                continue
            key = normalize_url(url)
            if key in already:
                skipped["already"] = skipped.get("already", 0) + 1
                log.info("search_skipped", url=url, reason="already", query=query)
                continue
            if key in seen:
                skipped["dup"] = skipped.get("dup", 0) + 1
                log.info("search_skipped", url=url, reason="dup", query=query)
                continue
            seen.add(key)
            candidates.append(url)

    first_party = [
        url for url in candidates if allowed_source_url(url, product, repo_meta)
    ]
    third_party = [
        url for url in candidates if not allowed_source_url(url, product, repo_meta)
    ]
    unique = first_party + third_party
    if len(unique) > SEARCH_CAP:
        result["truncated"] = True
        for url in unique[SEARCH_CAP:]:
            skipped["cap"] = skipped.get("cap", 0) + 1
            log.info("search_skipped", url=url, reason="cap")
        unique = unique[:SEARCH_CAP]
    if not unique:
        log.info(
            "search_skipped",
            reason="no_hits",
            found=found,
            skipped_by=skipped,
        )
        return result

    pages: list[dict[str, object]] = []
    root = cache / "search"
    for url in unique:
        slug = page_slug(url)
        page_dir = root / slug
        converter: str | None = None
        if force or not page_exists(page_dir):
            page = fetch_prose(client, url)
            jitter()
            if page is None:
                skipped["fetch_failed"] = skipped.get("fetch_failed", 0) + 1
                log.info("search_skipped", url=url, reason="fetch_failed")
                continue
            final_url = page.url
            reason = search_url_skip_reason(final_url, prefixes, skip_home=skip_home)
            if reason:
                skipped[f"redirect_{reason}"] = skipped.get(f"redirect_{reason}", 0) + 1
                log.info("search_skipped", url=final_url, reason=reason, via="redirect")
                continue
            if sibling_on_shared_host(final_url, product, repo_meta):
                skipped["redirect_sibling_host"] = skipped.get("redirect_sibling_host", 0) + 1
                log.info("search_skipped", url=final_url, reason="sibling_host", via="redirect")
                continue
            body = page.text
            first_party_page = allowed_source_url(final_url, product, repo_meta)
            if not first_party_page and not product_mentioned(body, product):
                skipped["product_not_in_body"] = skipped.get("product_not_in_body", 0) + 1
                log.info("search_skipped", url=final_url, reason="product_not_in_body")
                continue
            kind, quality = search_page_meta(final_url, product, repo_meta)
            converter = page.converter
            save_page(
                page_dir,
                final_url,
                body[:MAX_FILE_CHARS],
                {"kind": kind, "converter": converter},
            )
        else:
            final_url = (page_dir / "url.txt").read_text(encoding="utf-8").strip()
            body = (page_dir / "content.txt").read_text(encoding="utf-8", errors="replace")
            first_party_page = allowed_source_url(final_url, product, repo_meta)
            if sibling_on_shared_host(final_url, product, repo_meta):
                skipped["sibling_host"] = skipped.get("sibling_host", 0) + 1
                log.info("search_skipped", url=final_url, reason="sibling_host")
                continue
            if not first_party_page and not product_mentioned(body, product):
                skipped["product_not_in_body"] = skipped.get("product_not_in_body", 0) + 1
                log.info("search_skipped", url=final_url, reason="product_not_in_body")
                continue
            kind, quality = search_page_meta(final_url, product, repo_meta)
        already.add(normalize_url(final_url))
        log.info("search_kept", url=final_url, kind=kind, quality=quality, converter=converter)
        pages.append(
            {
                "id": f"search_{slug}",
                "lane": "search",
                "kind": kind,
                "url": final_url,
                "path": str(page_dir.relative_to(cache) / "content.txt"),
                "quality": quality,
                "score_as_prose": True,
                "accessed_at": utc_date(),
            }
        )
    result["pages"] = pages
    log.info(
        "search_pages",
        count=len(pages),
        found=found,
        truncated=result["truncated"],
        skipped_by=skipped,
    )
    return result


def harvest_community(
    cache: Path,
    product: dict[str, object],
    already: set[str],
    log: PipelineLogger,
    client: httpx.Client,
    *,
    force: bool,
) -> dict[str, object]:
    result: dict[str, object] = {"lane": "community", "truncated": False, "pages": []}
    name = str(product.get("name") or product["id"])
    prefixes = [str(p) for p in (product.get("skip_url_prefixes") or [])]
    seed_urls: set[str] = set()
    candidates: list[str] = []
    skipped: dict[str, int] = {}
    found = 0
    for url in product.get("community") or []:
        if isinstance(url, str) and url:
            candidates.append(url)
            seed_urls.add(normalize_url(url))
            log.info("community_seed", url=url)
    queries = community_search_queries(name)
    log.info("community_queries", queries=queries)
    incidental_hosts: set[str] = set()
    for query in queries:
        hits, stats = web_search_stats(query, count=6)
        log.info("community_query", query=query, **stats)
        for hit in hits:
            found += 1
            url = hit.get("url") or ""
            title = (hit.get("title") or "")[:120]
            source = hit.get("source") or ""
            log.info("community_hit", url=url, title=title, engine=source, query=query)
            blob = f"{hit.get('title') or ''} {hit.get('snippet') or ''} {url}"
            if not product_mentioned(blob, product):
                skipped["product_not_in_snippet"] = skipped.get("product_not_in_snippet", 0) + 1
                log.info("community_skipped", url=url, reason="product_not_in_snippet", query=query)
                continue
            reason = community_url_skip_reason(url, prefixes, seed_urls)
            if reason:
                skipped[reason] = skipped.get(reason, 0) + 1
                log.info("community_skipped", url=url, reason=reason, query=query)
                continue
            if product_named_in_url_or_title(url, title, product):
                candidates.append(url)
                continue
            incidental_hosts.add(host_of(url))
            skipped["incidental_mention"] = skipped.get("incidental_mention", 0) + 1
            log.info("community_skipped", url=url, reason="incidental_mention", query=query)
    for host in sorted(h for h in incidental_hosts if h):
        for query in community_confirm_queries(host, product):
            hits, stats = web_search_stats(query, count=6)
            log.info("community_confirm", host=host, query=query, **stats)
            for hit in hits:
                found += 1
                url = hit.get("url") or ""
                title = (hit.get("title") or "")[:120]
                if not product_named_in_url_or_title(url, title, product):
                    skipped["confirm_not_named"] = skipped.get("confirm_not_named", 0) + 1
                    log.info("community_skipped", url=url, reason="confirm_not_named", query=query)
                    continue
                reason = community_url_skip_reason(url, prefixes, seed_urls)
                if reason:
                    skipped[reason] = skipped.get(reason, 0) + 1
                    log.info("community_skipped", url=url, reason=reason, query=query)
                    continue
                candidates.append(url)
                log.info("community_adjusted", url=url, title=title, via=query)

    unique: list[str] = []
    seen: set[str] = set()
    for url in candidates:
        reason = community_url_skip_reason(url, prefixes, seed_urls)
        if reason:
            skipped[reason] = skipped.get(reason, 0) + 1
            log.info("community_skipped", url=url, reason=reason)
            continue
        key = normalize_url(url)
        if key in seen:
            skipped["dup"] = skipped.get("dup", 0) + 1
            log.info("community_skipped", url=url, reason="dup")
            continue
        if key in already:
            skipped["already"] = skipped.get("already", 0) + 1
            log.info("community_skipped", url=url, reason="already")
            continue
        seen.add(key)
        unique.append(url)
    if len(unique) > COMMUNITY_CAP:
        result["truncated"] = True
        for url in unique[COMMUNITY_CAP:]:
            skipped["cap"] = skipped.get("cap", 0) + 1
            log.info("community_skipped", url=url, reason="cap")
        unique = unique[:COMMUNITY_CAP]
    if not unique:
        log.info(
            "community_skipped",
            reason="no_hits",
            found=found,
            skipped_by=skipped,
        )
        return result

    pages: list[dict[str, object]] = []
    root = cache / "community"
    for url in unique:
        slug = page_slug(url)
        page_dir = root / slug
        converter: str | None = None
        if force or not page_exists(page_dir):
            page = fetch_prose(client, url)
            jitter()
            if page is None:
                skipped["fetch_failed"] = skipped.get("fetch_failed", 0) + 1
                log.info("community_skipped", url=url, reason="fetch_failed")
                continue
            body = page.text
            if not product_mentioned(body, product):
                skipped["product_not_in_body"] = skipped.get("product_not_in_body", 0) + 1
                log.info("community_skipped", url=page.url, reason="product_not_in_body")
                continue
            converter = page.converter
            save_page(
                page_dir,
                page.url,
                body[:MAX_FILE_CHARS],
                {"kind": "community", "converter": converter},
            )
            final_url = page.url
        else:
            final_url = (page_dir / "url.txt").read_text(encoding="utf-8").strip()
            body = (page_dir / "content.txt").read_text(encoding="utf-8", errors="replace")
            if not product_mentioned(body, product):
                skipped["product_not_in_body"] = skipped.get("product_not_in_body", 0) + 1
                log.info("community_skipped", url=final_url, reason="product_not_in_body")
                continue
        already.add(normalize_url(final_url))
        log.info("community_kept", url=final_url, converter=converter)
        pages.append(
            {
                "id": f"community_{slug}",
                "lane": "community",
                "kind": "community",
                "url": final_url,
                "path": str(page_dir.relative_to(cache) / "content.txt"),
                "quality": "medium",
                "score_as_prose": True,
                "accessed_at": utc_date(),
            }
        )
    result["pages"] = pages
    log.info(
        "community_pages",
        count=len(pages),
        found=found,
        truncated=result["truncated"],
        skipped_by=skipped,
    )
    return result


def write_manifest(
    cache: Path,
    product: dict[str, object],
    lanes: dict[str, dict[str, object]],
    repo_meta: dict[str, object],
) -> dict[str, object]:
    pages: list[dict[str, object]] = []
    truncated: dict[str, bool] = {}
    for name, lane in lanes.items():
        truncated[name] = bool(lane.get("truncated"))
        pages.extend(list(lane.get("pages") or []))
    manifest = {
        "id": product["id"],
        "name": product["name"],
        "repo": public_https_repo(repo_meta.get("origin"), product.get("repo")),
        "docs": product.get("docs"),
        "license": repo_meta.get("license"),
        "version_or_commit": repo_meta.get("sha"),
        "clone_skipped": bool(repo_meta.get("skipped")),
        "observed_at": utc_date(),
        "accessed_at": utc_now(),
        "truncated": truncated,
        "pages": pages,
    }
    selection = repo_meta.get("code_selection")
    if isinstance(selection, dict):
        manifest["code_selection"] = selection
    docs_lane = lanes.get("docs") or {}
    docs_sel = docs_lane.get("docs_selection")
    if isinstance(docs_sel, dict):
        manifest["docs_selection"] = docs_sel
    (cache / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def harvest(
    slug: str,
    *,
    force: bool = False,
    inventory: bool = False,
) -> dict[str, object] | None:
    product = load_product(slug)
    cache = product_cache(slug)
    cache.mkdir(parents=True, exist_ok=True)
    if inventory:
        with PipelineLogger("harvest", source=slug, inventory=True) as log:
            harvest_repo(cache, product, log, force=force, inventory=True)
        return None
    already: set[str] = set()
    with PipelineLogger("harvest", source=slug, force=force) as log:
        log.info("harvest_started", slug=slug)
        client = get_client()
        try:
            log.info("lane_start", lane="repo")
            repo_meta = harvest_repo(cache, product, log, force=force)
            log.info("lane_start", lane="docs")
            docs = harvest_docs(cache, product, repo_meta, already, log, client, force=force)
            log.info("lane_start", lane="issues")
            issues = harvest_issues(cache, product, repo_meta, log, force=force)
            log.info("lane_start", lane="blog")
            blog = harvest_blog(cache, product, already, log, client, force=force)
            log.info("lane_start", lane="search")
            search = harvest_search(
                cache, product, repo_meta, already, log, client, force=force
            )
            log.info("lane_start", lane="community")
            community = harvest_community(cache, product, already, log, client, force=force)
        finally:
            client.close()
        lanes = {
            "repo": repo_meta,
            "docs": docs,
            "issues": issues,
            "blog": blog,
            "search": search,
            "community": community,
        }
        manifest = write_manifest(cache, product, lanes, repo_meta)
        log.action("manifest_written", pages=len(manifest["pages"]))
        print(f"harvest {slug}: {len(manifest['pages'])} pages")
        return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Harvest product pages into .cache/")
    parser.add_argument("--slug")
    parser.add_argument("--all", action="store_true", help="Every product in seed.json")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--inventory",
        action="store_true",
        help="Clone if needed and print source paths. Do not rank or fetch.",
    )
    args = parser.parse_args()
    if args.all:
        for slug in product_ids():
            harvest(slug, force=args.force, inventory=args.inventory)
        return
    if not args.slug:
        raise SystemExit("pass --slug <id> or --all")
    harvest(args.slug, force=args.force, inventory=args.inventory)


if __name__ == "__main__":
    main()
