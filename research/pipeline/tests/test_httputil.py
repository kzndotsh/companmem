from __future__ import annotations

import httpx

from companmem_pipeline.httputil import (
    decode_body,
    fetch_prose,
    markdown_new_url,
    markdown_suffix_url,
    reset_markdown_new,
    unwrap_markdown_new,
)

THIN_HTML = "<html><body><div id='app'></div></body></html>"
GOOD_MARKDOWN = "# Title\n\n" + "This paragraph has enough words to pass the quality gate. " * 8
MDNEW_ENVELOPE = (
    "Title: Example\n\nURL Source: https://example.com/docs\n\nMarkdown Content:\n"
    + GOOD_MARKDOWN
)


def test_markdown_new_url_prepends() -> None:
    assert markdown_new_url("https://mem0.ai/blog") == "https://markdown.new/https://mem0.ai/blog"


def test_markdown_suffix_url_appends_md() -> None:
    assert markdown_suffix_url("https://docs.example.com/guide/") == (
        "https://docs.example.com/guide.md"
    )
    assert markdown_suffix_url("https://docs.example.com/guide?x=1") == (
        "https://docs.example.com/guide.md?x=1"
    )
    assert markdown_suffix_url("https://docs.example.com/llms.txt") is None
    assert markdown_suffix_url("https://docs.example.com/guide.md") is None
    assert markdown_suffix_url("https://example.com/") is None


def test_decode_body_keeps_origin_markdown() -> None:
    text, conv = decode_body("text/markdown; charset=utf-8", GOOD_MARKDOWN)
    assert conv == "origin_markdown"
    assert text == GOOD_MARKDOWN


def test_decode_body_strips_html() -> None:
    text, conv = decode_body("text/html", "<h1>About Us</h1><p>Hello there friend.</p>")
    assert conv == "clean_html"
    assert "About Us" in text
    assert "<h1>" not in text


def test_decode_body_plain_text() -> None:
    text, conv = decode_body("text/plain", "# llms.txt\n\n- /docs")
    assert conv == "origin_text"
    assert text.startswith("# llms.txt")


def test_unwrap_markdown_new_drops_envelope() -> None:
    assert unwrap_markdown_new(MDNEW_ENVELOPE) == GOOD_MARKDOWN


def test_fetch_prose_uses_origin_markdown_without_proxy() -> None:
    reset_markdown_new()
    posts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            posts.append(str(request.url))
            return httpx.Response(500)
        return httpx.Response(
            200,
            text=GOOD_MARKDOWN,
            headers={"content-type": "text/markdown; charset=utf-8"},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    page = fetch_prose(client, "https://example.com/docs")
    assert page is not None
    assert page.converter == "origin_markdown"
    assert page.url == "https://example.com/docs"
    assert posts == []


def test_fetch_prose_prefers_md_suffix_over_markdown_new() -> None:
    reset_markdown_new()
    posts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            posts.append(str(request.url))
            return httpx.Response(500)
        path = request.url.path
        if path.endswith(".md"):
            return httpx.Response(
                200,
                text=GOOD_MARKDOWN,
                headers={"content-type": "text/plain"},
            )
        return httpx.Response(200, text=THIN_HTML, headers={"content-type": "text/html"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    page = fetch_prose(client, "https://example.com/guide")
    assert page is not None
    assert page.converter == "origin_markdown"
    assert page.url == "https://example.com/guide.md"
    assert posts == []


def test_fetch_prose_falls_back_when_html_is_thin() -> None:
    reset_markdown_new()

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            assert str(request.url) == "https://markdown.new/"
            return httpx.Response(
                200,
                text=MDNEW_ENVELOPE,
                headers={"content-type": "text/markdown; charset=utf-8"},
            )
        if request.url.path.endswith(".md"):
            return httpx.Response(404)
        return httpx.Response(200, text=THIN_HTML, headers={"content-type": "text/html"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    page = fetch_prose(client, "https://example.com/app")
    assert page is not None
    assert page.converter == "markdown_new"
    assert page.url == "https://example.com/app"
    assert page.text == GOOD_MARKDOWN
    assert "URL Source" not in page.text


def test_fetch_prose_keeps_origin_url_when_origin_fails() -> None:
    reset_markdown_new()

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return httpx.Response(
                200,
                text=GOOD_MARKDOWN,
                headers={"content-type": "text/markdown"},
            )
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    page = fetch_prose(client, "https://example.com/missing")
    assert page is not None
    assert page.converter == "markdown_new"
    assert page.url == "https://example.com/missing"


def test_fetch_prose_skips_markdown_new_after_429() -> None:
    reset_markdown_new()
    posts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal posts
        if request.method == "POST":
            posts += 1
            return httpx.Response(429)
        return httpx.Response(200, text=THIN_HTML, headers={"content-type": "text/html"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    first = fetch_prose(client, "https://example.com/a")
    second = fetch_prose(client, "https://example.com/b")
    assert first is not None
    assert first.converter == "clean_html"
    assert second is not None
    assert second.converter == "clean_html"
    assert posts == 1
