"""HTTP fetch, retry, jitter, and page save for harvest."""

from __future__ import annotations

import hashlib
import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse, urlunparse

import httpx

from companmem_pipeline.html import clean_html, quality_score
from companmem_pipeline.log import emit_console

USER_AGENT = "CompanmemResearch/0.1 (+https://github.com/kzndotsh/companmem)"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 5
MARKDOWN_NEW_ENDPOINT = "https://markdown.new/"
Converter = Literal["origin_markdown", "origin_text", "clean_html", "markdown_new"]

_markdown_new_disabled = False


@dataclass(frozen=True)
class FetchedText:
    url: str
    text: str
    converter: Converter


def reset_markdown_new() -> None:
    """Tests only. harvest-all keeps a 429 disable across slugs."""
    global _markdown_new_disabled
    _markdown_new_disabled = False


def markdown_new_url(url: str) -> str:
    """GET form. Prefer POST so origin query strings are not parsed as converter options."""
    return MARKDOWN_NEW_ENDPOINT + url


def markdown_suffix_url(url: str) -> str | None:
    """Same path with `.md` appended. None if the URL already has a file extension."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    if not path:
        return None
    last = path.rsplit("/", 1)[-1]
    if "." in last:
        return None
    return urlunparse(parsed._replace(path=path + ".md"))


def get_client() -> httpx.Client:
    return httpx.Client(
        headers={
            "User-Agent": USER_AGENT,
            "Accept": (
                "text/markdown, text/html;q=0.9, application/xhtml+xml;q=0.9, "
                "application/xml;q=0.8, text/plain;q=0.8, */*;q=0.1"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
        timeout=DEFAULT_TIMEOUT,
        follow_redirects=True,
    )


def jitter(low: float = 0.4, high: float = 1.2) -> None:
    time.sleep(random.uniform(low, high))


def fetch_with_retry(client: httpx.Client, url: str) -> httpx.Response | None:
    """GET with backoff on 429/503. None on permanent failure."""
    for attempt in range(MAX_RETRIES):
        try:
            resp = client.get(url)
            if resp.status_code == 200:
                return resp
            if resp.status_code in (429, 503):
                wait = min(2**attempt, 16)
                if resp.status_code == 429:
                    wait = max(wait, 15 * (attempt + 1))
                time.sleep(wait)
                continue
            if 400 <= resp.status_code < 500:
                return None
            resp.raise_for_status()
        except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError):
            if attempt >= MAX_RETRIES - 1:
                return None
            time.sleep(min(2**attempt, 16))
    return None


def decode_body(content_type: str, body: str) -> tuple[str, Converter]:
    """Turn an origin response into stored prose. Does not call markdown.new."""
    ctype = content_type.lower()
    if "markdown" in ctype:
        return body, "origin_markdown"
    if "html" in ctype or body.lstrip()[:80].startswith("<"):
        return clean_html(body), "clean_html"
    return body, "origin_text"


def unwrap_markdown_new(text: str) -> str:
    marker = "\nMarkdown Content:"
    idx = text.find(marker)
    if idx == -1:
        return text
    rest = text[idx + len(marker) :].lstrip("\r\n")
    return rest if rest else text


def _is_markdown_new_error(resp: httpx.Response) -> bool:
    ctype = resp.headers.get("content-type", "").lower()
    if "json" in ctype:
        return True
    head = resp.text.lstrip()[:400]
    return head.startswith("{") and '"success"' in head


def fetch_markdown_new(client: httpx.Client, url: str) -> str | None:
    """One origin URL through markdown.new. None on failure or daily 429."""
    global _markdown_new_disabled
    if _markdown_new_disabled:
        emit_console("httputil", url, "info", "markdown_new_skipped", reason="disabled")
        return None
    for attempt in range(MAX_RETRIES):
        try:
            resp = client.post(
                MARKDOWN_NEW_ENDPOINT,
                json={"url": url, "method": "auto", "retain_images": False},
            )
            if resp.status_code == 200:
                if _is_markdown_new_error(resp):
                    return None
                return unwrap_markdown_new(resp.text)
            if resp.status_code == 429:
                _markdown_new_disabled = True
                emit_console("httputil", url, "warn", "markdown_new_disabled", status=429)
                return None
            if resp.status_code == 503:
                time.sleep(min(2**attempt, 16))
                continue
            if 400 <= resp.status_code < 500:
                return None
            resp.raise_for_status()
        except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError):
            if attempt >= MAX_RETRIES - 1:
                return None
            time.sleep(min(2**attempt, 16))
    return None


def _from_response(resp: httpx.Response) -> FetchedText:
    text, conv = decode_body(resp.headers.get("content-type", ""), resp.text)
    final = str(resp.url)
    if conv == "origin_text" and urlparse(final).path.lower().endswith(".md"):
        conv = "origin_markdown"
    return FetchedText(url=final, text=text, converter=conv)


def _thin_html(page: FetchedText) -> bool:
    return page.converter == "clean_html" and bool(quality_score(page.text)["is_low_quality"])


def fetch_prose(client: httpx.Client, url: str) -> FetchedText | None:
    """Origin markdown, else `{url}.md`, else local HTML strip, else markdown.new."""
    emit_console("httputil", url, "info", "fetch_prose_start")
    resp = fetch_with_retry(client, url)
    origin: FetchedText | None = None
    if resp is not None:
        origin = _from_response(resp)
        thin = _thin_html(origin)
        emit_console(
            "httputil",
            origin.url,
            "info",
            "fetch_prose_origin",
            converter=origin.converter,
            chars=len(origin.text),
            thin_html=thin,
            status=resp.status_code,
        )
        if not thin:
            return origin
        emit_console("httputil", origin.url, "info", "fetch_prose_origin_thin")
    else:
        emit_console("httputil", url, "warn", "fetch_prose_origin_failed")
    suffix = markdown_suffix_url(url)
    if suffix:
        emit_console("httputil", suffix, "info", "fetch_prose_md_suffix")
        md_resp = fetch_with_retry(client, suffix)
        if md_resp is not None:
            md_page = _from_response(md_resp)
            thin = _thin_html(md_page)
            emit_console(
                "httputil",
                md_page.url,
                "info",
                "fetch_prose_md_suffix_ok",
                converter=md_page.converter,
                chars=len(md_page.text),
                thin_html=thin,
            )
            if not thin:
                return md_page
        else:
            emit_console("httputil", suffix, "info", "fetch_prose_md_suffix_miss")
    requested = origin.url if origin is not None else url
    emit_console("httputil", requested, "info", "fetch_prose_markdown_new")
    md = fetch_markdown_new(client, requested)
    if md:
        emit_console(
            "httputil",
            requested,
            "info",
            "fetch_prose_markdown_new_ok",
            chars=len(md),
        )
        return FetchedText(url=requested, text=md, converter="markdown_new")
    emit_console(
        "httputil",
        requested,
        "warn",
        "fetch_prose_done",
        converter=origin.converter if origin is not None else None,
        ok=origin is not None,
    )
    return origin


def save_page(
    page_dir: Path,
    url: str,
    content: str,
    metadata: dict[str, object] | None = None,
) -> None:
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "url.txt").write_text(url + "\n", encoding="utf-8")
    (page_dir / "content.txt").write_text(content, encoding="utf-8")
    if metadata:
        (page_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2),
            encoding="utf-8",
        )


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def page_exists(page_dir: Path) -> bool:
    return (page_dir / "content.txt").exists()
