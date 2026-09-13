from __future__ import annotations

import httpx

from companmem_pipeline.httputil import (
    decode_body,
    fetch_prose,
    format_arctic_thread,
    markdown_new_url,
    markdown_suffix_url,
    reddit_post_id,
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


def test_reddit_post_id_from_thread_and_short_url() -> None:
    assert (
        reddit_post_id(
            "https://www.reddit.com/r/AI_Agents/comments/1stf5gv/mem0_sufficient/"
        )
        == "1stf5gv"
    )
    assert reddit_post_id("https://old.reddit.com/r/test/comments/abc123") == "abc123"
    assert reddit_post_id("https://redd.it/1stf5gv") == "1stf5gv"
    assert reddit_post_id("https://www.reddit.com/r/AI_Agents/") is None
    assert reddit_post_id("https://example.com/comments/1stf5gv") is None


def test_format_arctic_thread_skips_automod() -> None:
    text = format_arctic_thread(
        {
            "title": "Mem0 sufficient for memory layer?",
            "selftext": "Recently, many people were talking about mem0.",
            "author": "alice",
            "subreddit": "AI_Agents",
        },
        [
            {"author": "AutoModerator", "body": "Please check the wiki."},
            {"author": "bob", "body": "I use mem0 for long-term memory."},
            {"author": "gone", "body": "[deleted]"},
        ],
    )
    assert text.startswith("# Mem0 sufficient for memory layer?")
    assert "r/AI_Agents" in text
    assert "talking about mem0" in text
    assert "u/bob" in text
    assert "AutoModerator" not in text
    assert "[deleted]" not in text


def test_fetch_prose_uses_arctic_shift_for_reddit() -> None:
    reset_markdown_new()
    posts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if request.method == "POST":
            posts.append(url)
            return httpx.Response(500)
        if "arctic-shift.photon-reddit.com" in url and "/api/posts/ids" in url:
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "1stf5gv",
                            "title": "Mem0 sufficient for memory layer?",
                            "selftext": "Recently, many people were talking about mem0.",
                            "author": "alice",
                            "subreddit": "AI_Agents",
                        }
                    ]
                },
            )
        if "arctic-shift.photon-reddit.com" in url and "/api/comments/search" in url:
            return httpx.Response(
                200,
                json={
                    "data": [
                        {"author": "AutoModerator", "body": "wiki", "id": "1"},
                        {
                            "author": "bob",
                            "body": "I use mem0 for long-term memory.",
                            "id": "2",
                        },
                    ]
                },
            )
        return httpx.Response(200, text=THIN_HTML, headers={"content-type": "text/html"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    thread = "https://www.reddit.com/r/AI_Agents/comments/1stf5gv/mem0_sufficient/"
    page = fetch_prose(client, thread)
    assert page is not None
    assert page.converter == "arctic_shift"
    assert page.url == thread
    assert "talking about mem0" in page.text
    assert "u/bob" in page.text
    assert "AutoModerator" not in page.text
    assert posts == []


def test_fetch_prose_falls_back_when_arctic_shift_misses() -> None:
    reset_markdown_new()

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "arctic-shift.photon-reddit.com" in url:
            return httpx.Response(200, json={"data": []})
        if request.method == "POST":
            return httpx.Response(500)
        return httpx.Response(
            200,
            text=GOOD_MARKDOWN,
            headers={"content-type": "text/markdown"},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    page = fetch_prose(client, "https://www.reddit.com/r/test/comments/abc123/x/")
    assert page is not None
    assert page.converter == "origin_markdown"
