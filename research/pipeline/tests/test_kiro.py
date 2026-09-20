from __future__ import annotations

from companmem_pipeline.kiro import content_text, content_types, parse_json_object


def test_content_text_prefers_text_over_thinking() -> None:
    body: dict[str, object] = {
        "content": [
            {"type": "thinking", "thinking": '{"wrong": true}'},
            {"type": "text", "text": '{"ok": true}'},
        ]
    }
    assert content_text(body) == '{"ok": true}'
    assert content_types(body) == ["thinking", "text"]


def test_content_text_falls_back_to_thinking_when_text_empty() -> None:
    body: dict[str, object] = {
        "content": [{"type": "thinking", "thinking": '<thinking>{"themes": []}</thinking>'}]
    }
    text = content_text(body)
    parsed = parse_json_object(text)
    assert parsed == {"themes": []}


def test_parse_json_object_none_without_brace() -> None:
    assert parse_json_object("still reasoning about products") is None
