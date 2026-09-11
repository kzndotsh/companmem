"""Kiro gateway client (Anthropic-compatible /v1/messages)."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

DEFAULT_URL = "http://127.0.0.1:9000"
DEFAULT_MODEL = "claude-sonnet-4.6"


def gateway_url() -> str:
    return os.environ.get("KIRO_GATEWAY_URL", DEFAULT_URL).rstrip("/")


def api_key() -> str:
    return os.environ.get("KIRO_GATEWAY_API_KEY", os.environ.get("PROXY_API_KEY", "")).strip()


def default_model() -> str:
    return os.environ.get("COMPANMEM_LLM_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def _headers() -> dict[str, str]:
    key = api_key()
    if not key:
        raise RuntimeError("KIRO_GATEWAY_API_KEY or PROXY_API_KEY is not set")
    return {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }


def _text_from_body(body: dict[str, Any]) -> str:
    parts = body.get("content", [])
    if not isinstance(parts, list):
        return ""
    return "".join(str(p.get("text", "")) for p in parts if p.get("type") == "text").strip()


def _extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if "```" in cleaned:
        for part in cleaned.split("```"):
            candidate = part.lstrip("json\n").strip()
            if candidate.startswith("{"):
                cleaned = candidate
                break
    if not cleaned.startswith("{"):
        start = cleaned.find("{")
        if start == -1:
            raise ValueError("no JSON object in model response")
        cleaned = cleaned[start:]
    depth = 0
    end_idx = 0
    for i, char in enumerate(cleaned):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        if depth == 0:
            end_idx = i + 1
            break
    if not end_idx:
        raise ValueError("unbalanced JSON in model response")
    parsed = json.loads(cleaned[:end_idx])
    if not isinstance(parsed, dict):
        raise ValueError("expected JSON object from model")
    return parsed


def messages(
    model: str,
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    timeout_sec: float = 120.0,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "thinking": {"type": "disabled"},
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    with httpx.Client(timeout=timeout_sec) as client:
        resp = client.post(f"{gateway_url()}/v1/messages", headers=_headers(), json=payload)
        resp.raise_for_status()
        body = resp.json()
    if not isinstance(body, dict):
        raise ValueError("invalid gateway response")
    return body


def chat_text(
    model: str,
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.2,
    max_tokens: int = 1024,
    timeout_sec: float = 120.0,
) -> str:
    body = messages(
        model,
        system_prompt,
        user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout_sec=timeout_sec,
    )
    return _text_from_body(body)


def chat_json(
    model: str,
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    timeout_sec: float = 120.0,
) -> dict[str, Any]:
    system = (
        system_prompt
        + "\n\nIMPORTANT: Output ONLY a JSON object. No markdown fences. No preamble. Start with { and end with }."
    )
    text = chat_text(
        model,
        system,
        user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout_sec=timeout_sec,
    )
    return _extract_json_object(text)
