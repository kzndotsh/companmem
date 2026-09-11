"""Unit tests for Graphiti Kiro JSON parsing."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "harness" / "lib"))

from graphiti_kiro import _parse_json_response, get_sentence_transformer_embedder


def test_parse_plain_json() -> None:
    parsed = _parse_json_response('{"nodes": [], "edges": []}')
    assert parsed == {"nodes": [], "edges": []}


def test_parse_markdown_fence() -> None:
    text = 'Here you go:\n```json\n{"ok": true}\n```\n'
    assert _parse_json_response(text) == {"ok": True}


def test_parse_preamble_and_trailing_junk() -> None:
    text = 'Sure! {"a": 1, "b": "hello"} end junk'
    assert _parse_json_response(text) == {"a": 1, "b": "hello"}


def test_parse_unbalanced_raises() -> None:
    with pytest.raises(ValueError, match="unbalanced JSON"):
        _parse_json_response('{"truncated": true')


def test_parse_invalid_json_raises() -> None:
    with pytest.raises(ValueError, match="invalid JSON"):
        _parse_json_response("{not json}")


def test_embedder_singleton() -> None:
    first = get_sentence_transformer_embedder()
    second = get_sentence_transformer_embedder()
    assert first is second
