"""Kiro Messages API client. Extract-only: no tools, thinking disabled."""

from __future__ import annotations

import json
import os
import time

import httpx

from companmem_pipeline.log import emit_console
from companmem_pipeline.paths import load_dotenv

load_dotenv()

KIRO_URL = os.environ.get("KIRO_GATEWAY_URL", "http://127.0.0.1:9000")
MODEL = os.environ.get("EXTRACT_MODEL", "claude-sonnet-4.6")


def kiro_api_key() -> str:
    """Empty KIRO_GATEWAY_API_KEY falls through to PROXY_API_KEY."""
    return (
        os.environ.get("KIRO_GATEWAY_API_KEY") or os.environ.get("PROXY_API_KEY") or ""
    ).strip()


def kiro_configured() -> bool:
    return bool(kiro_api_key())


def content_text(body: dict[str, object]) -> str:
    """Visible reply text. Thinking-only 200s have no type=text block."""
    parts = body.get("content")
    if not isinstance(parts, list):
        return ""
    texts: list[str] = []
    thinking: list[str] = []
    for part in parts:
        if not isinstance(part, dict):
            continue
        kind = part.get("type")
        if kind == "text":
            texts.append(str(part.get("text") or ""))
        elif kind == "thinking":
            thinking.append(str(part.get("thinking") or part.get("text") or ""))
    joined = "".join(texts).strip()
    if joined:
        return joined
    return "".join(thinking)


def content_types(body: dict[str, object]) -> list[str]:
    parts = body.get("content")
    if not isinstance(parts, list):
        return []
    kinds: list[str] = []
    for part in parts:
        if isinstance(part, dict):
            kinds.append(str(part.get("type") or "unknown"))
    return kinds


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
    key = kiro_api_key()
    if not key:
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
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    url = f"{KIRO_URL.rstrip('/')}/v1/messages"
    chosen = model or MODEL
    last_error: Exception | None = None
    started = time.time()
    emit_console(
        "kiro",
        "",
        "info",
        "kiro_request",
        model=chosen,
        user_chars=len(user_text),
        timeout=timeout,
        temperature=temperature,
    )
    for attempt in range(3):
        emit_console("kiro", "", "info", "kiro_attempt", attempt=attempt + 1, attempts=3)
        try:
            resp = httpx.post(url, headers=headers, json=payload, timeout=timeout)
            emit_console(
                "kiro",
                "",
                "info",
                "kiro_response",
                attempt=attempt + 1,
                status=resp.status_code,
                elapsed=round(time.time() - started, 2),
            )
            resp.raise_for_status()
            body = resp.json()
            if not isinstance(body, dict):
                raise json.JSONDecodeError("root is not an object", str(body), 0)
            text_out = content_text(body)
            parsed = parse_json_object(text_out)
            if parsed is not None:
                emit_console(
                    "kiro",
                    "",
                    "info",
                    "kiro_ok",
                    attempt=attempt + 1,
                    elapsed=round(time.time() - started, 2),
                    reply_chars=len(text_out),
                    content_types=content_types(body),
                )
                return parsed
            last_error = ValueError("response was not a JSON object")
            emit_console(
                "kiro",
                "",
                "warn",
                "kiro_not_json",
                attempt=attempt + 1,
                reply_chars=len(text_out),
                preview=text_out[:120].replace("\n", " "),
                content_types=content_types(body),
                stop_reason=body.get("stop_reason"),
            )
            if "{" not in text_out:
                break
        except (httpx.HTTPStatusError, httpx.TimeoutException, json.JSONDecodeError) as exc:
            last_error = exc
            emit_console(
                "kiro",
                "",
                "warn",
                "kiro_http_error",
                attempt=attempt + 1,
                error_type=type(exc).__name__,
                error=str(exc)[:300],
            )
        if attempt < 2:
            time.sleep(min(2**attempt, 8))
    if last_error is not None:
        emit_console(
            "kiro",
            "",
            "error",
            "kiro_failed",
            error_type=type(last_error).__name__,
            error=str(last_error)[:300],
            elapsed=round(time.time() - started, 2),
        )
        print(f"kiro failed: {type(last_error).__name__}: {last_error}")
    return None
