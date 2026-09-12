"""Kiro Messages API client. Extract-only: no tools, thinking disabled."""

from __future__ import annotations

import json
import os
import time

import httpx

from companmem_pipeline.paths import load_dotenv

load_dotenv()

KIRO_URL = os.environ.get("KIRO_GATEWAY_URL", "http://127.0.0.1:9000")
KIRO_KEY = os.environ.get("KIRO_GATEWAY_API_KEY", os.environ.get("PROXY_API_KEY", ""))
MODEL = os.environ.get("EXTRACT_MODEL", "claude-sonnet-4.6")


def kiro_configured() -> bool:
    return bool(KIRO_KEY)


def parse_json_object(text_out: str) -> dict[str, object] | None:
    """Parse a JSON object from model text (fence strip + brace match)."""
    text_out = text_out.strip()
    if "```" in text_out:
        parts = text_out.split("```")
        for part in parts[1:]:
            candidate = part.lstrip("json\n").strip()
            if candidate.startswith("{"):
                text_out = candidate
                break
    if not text_out.startswith("{"):
        start_idx = text_out.find("{")
        if start_idx == -1:
            return None
        text_out = text_out[start_idx:]
    if text_out.startswith("{"):
        depth = 0
        end_idx = 0
        for i, char in enumerate(text_out):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            if depth == 0:
                end_idx = i + 1
                break
        if end_idx:
            text_out = text_out[:end_idx]
    try:
        parsed = json.loads(text_out)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def call_kiro(
    user_text: str,
    system: str,
    *,
    temperature: float = 0.1,
    max_tokens: int = 8192,
    timeout: float = 180.0,
    model: str | None = None,
) -> dict[str, object] | None:
    """POST {KIRO_GATEWAY_URL}/v1/messages. Returns parsed JSON or None."""
    if not KIRO_KEY:
        raise RuntimeError("Set KIRO_GATEWAY_API_KEY or PROXY_API_KEY")
    payload = {
        "model": model or MODEL,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "thinking": {"type": "disabled"},
        "messages": [{"role": "user", "content": user_text}],
        "system": system,
    }
    headers = {
        "x-api-key": KIRO_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    url = f"{KIRO_URL.rstrip('/')}/v1/messages"
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            resp = httpx.post(url, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            body = resp.json()
            text_out = "".join(
                part.get("text", "")
                for part in body.get("content", [])
                if part.get("type") == "text"
            )
            parsed = parse_json_object(text_out)
            if parsed is not None:
                return parsed
            last_error = ValueError("response was not a JSON object")
        except (httpx.HTTPStatusError, httpx.TimeoutException, json.JSONDecodeError) as exc:
            last_error = exc
        if attempt < 2:
            time.sleep(min(2**attempt, 8))
    if last_error is not None:
        print(f"kiro failed: {type(last_error).__name__}: {last_error}")
    return None
