"""HTTP fetch, retry, jitter, and page save for harvest."""

from __future__ import annotations

import hashlib
import json
import random
import time
from pathlib import Path

import httpx

USER_AGENT = "CompanmemResearch/0.1 (+https://github.com/kzndotsh/companmem)"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 5


def get_client() -> httpx.Client:
    return httpx.Client(
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml,text/plain;q=0.9,*/*;q=0.8",
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
