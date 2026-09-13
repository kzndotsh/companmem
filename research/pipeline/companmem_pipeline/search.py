"""HTTP search backends for harvest discovery: Brave, then DuckDuckGo.

Snippets are discovery only. Harvest must fetch the landing page before extract.
"""

from __future__ import annotations

import os
import re
from urllib.parse import unquote, urlparse

import httpx

from companmem_pipeline.html import clean_html
from companmem_pipeline.httputil import USER_AGENT
from companmem_pipeline.paths import ROOT, load_dotenv

load_dotenv()


def _load_brave_key() -> str | None:
    key = os.environ.get("BRAVE_API_KEY", "")
    if key:
        return key
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("BRAVE_API_KEY="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val:
                    return val
    return None


BRAVE_API_KEY: str | None = _load_brave_key()

SearchHit = dict[str, str]


def _brave_search(query: str, count: int = 8) -> tuple[list[SearchHit], str | None]:
    if not BRAVE_API_KEY:
        return [], "no_brave_key"
    try:
        resp = httpx.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": count, "result_filter": "web,news"},
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": BRAVE_API_KEY,
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
        results: list[SearchHit] = []
        for row in (data.get("web") or {}).get("results") or []:
            results.append(
                {
                    "title": row.get("title", ""),
                    "url": row.get("url", ""),
                    "snippet": row.get("description", ""),
                    "source": "brave",
                }
            )
        for row in (data.get("news") or {}).get("results") or []:
            results.append(
                {
                    "title": row.get("title", ""),
                    "url": row.get("url", ""),
                    "snippet": row.get("description", ""),
                    "source": "brave_news",
                }
            )
        kept = results[:count]
        if not kept:
            return [], "brave_empty"
        return kept, None
    except httpx.HTTPStatusError as exc:
        return [], f"brave_http_{exc.response.status_code}"
    except (httpx.HTTPError, ValueError) as exc:
        return [], f"brave_error:{type(exc).__name__}"


def _ddg_search(query: str, count: int = 6) -> tuple[list[SearchHit], str | None]:
    try:
        resp = httpx.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": USER_AGENT},
            timeout=10.0,
            follow_redirects=True,
        )
        resp.raise_for_status()
        results: list[SearchHit] = []
        for match in re.finditer(
            r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?'
            r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
            resp.text,
            re.DOTALL,
        ):
            raw_url = match.group(1)
            title = re.sub(r"<[^>]+>", "", match.group(2)).strip()
            snippet = re.sub(r"<[^>]+>", "", match.group(3)).strip()
            url = raw_url
            uddg_match = re.search(r"[?&]uddg=([^&]+)", raw_url)
            if uddg_match:
                url = unquote(uddg_match.group(1))
            elif raw_url.startswith("//"):
                url = "https:" + raw_url
            if title and url:
                results.append(
                    {"title": title, "url": url, "snippet": snippet, "source": "ddg"}
                )
            if len(results) >= count:
                break
        if not results:
            return [], "ddg_empty"
        return results, None
    except httpx.HTTPStatusError as exc:
        return [], f"ddg_http_{exc.response.status_code}"
    except (httpx.HTTPError, ValueError) as exc:
        return [], f"ddg_error:{type(exc).__name__}"


def _dedup_results(results: list[SearchHit]) -> list[SearchHit]:
    seen_urls: set[str] = set()
    seen_snippets: set[str] = set()
    deduped: list[SearchHit] = []
    for row in results:
        url = row.get("url", "")
        snippet_key = row.get("snippet", "")[:60].lower()
        url_key = re.sub(r"\?.*$", "", url).rstrip("/").lower()
        if url_key and url_key in seen_urls:
            continue
        if snippet_key and snippet_key in seen_snippets:
            continue
        if url_key:
            seen_urls.add(url_key)
        if snippet_key:
            seen_snippets.add(snippet_key)
        deduped.append(row)
    return deduped


def web_search_stats(query: str, count: int = 8) -> tuple[list[SearchHit], dict[str, object]]:
    """Brave then DuckDuckGo. Stats explain empty results without logging the API key."""
    brave_hits, brave_error = _brave_search(query, count=count)
    ddg_count = count if not brave_hits else max(4, count - len(brave_hits))
    ddg_hits, ddg_error = _ddg_search(query, count=ddg_count)
    merged = _dedup_results([*brave_hits, *ddg_hits])[:count]
    stats: dict[str, object] = {
        "brave_key": bool(BRAVE_API_KEY),
        "brave_hits": len(brave_hits),
        "ddg_hits": len(ddg_hits),
        "merged_hits": len(merged),
        "brave_error": brave_error,
        "ddg_error": ddg_error,
    }
    return merged, stats


def web_search(query: str, count: int = 8) -> list[SearchHit]:
    """Brave if BRAVE_API_KEY is set, else DuckDuckGo. Returns hit dicts with urls."""
    hits, _stats = web_search_stats(query, count=count)
    return hits


def fetch_url_text(url: str, max_chars: int = 200_000) -> str | None:
    """Fetch a URL and return plaintext. None on failure. Not a search snippet."""
    try:
        resp = httpx.get(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
            timeout=30.0,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            return None
        content_type = resp.headers.get("content-type", "")
        body = resp.text
        if "html" in content_type or body.lstrip()[:100].startswith("<"):
            body = clean_html(body)
        return body[:max_chars]
    except httpx.HTTPError:
        return None


def host_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except ValueError:
        return ""
