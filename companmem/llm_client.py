"""Route LLM calls to Kiro gateway or OpenAI."""

from __future__ import annotations

import os
from typing import Literal

from companmem import kiro_client, openai_client

LlmBackend = Literal["kiro", "openai", "none"]


def llm_backend() -> LlmBackend:
    raw = os.environ.get("COMPANMEM_LLM_BACKEND", "auto").strip().casefold()
    if raw == "kiro":
        return "kiro" if kiro_client.api_key() else "none"
    if raw == "openai":
        return "openai" if openai_client.api_key() else "none"
    if kiro_client.api_key():
        return "kiro"
    if openai_client.api_key():
        return "openai"
    return "none"


def default_model() -> str:
    explicit = os.environ.get("COMPANMEM_EXTRACT_MODEL", "").strip()
    if explicit:
        return explicit
    reader = os.environ.get("COMPANMEM_READER_MODEL", "").strip()
    if reader:
        return reader
    return kiro_client.default_model()


def chat_json(
    system_prompt: str,
    user_prompt: str,
    *,
    model: str | None = None,
    temperature: float = 0.0,
    timeout_sec: int = 120,
) -> dict:
    backend = llm_backend()
    model_name = model or default_model()
    if backend == "kiro":
        return kiro_client.chat_json(
            model_name,
            system_prompt,
            user_prompt,
            temperature=temperature,
            timeout_sec=float(timeout_sec),
        )
    if backend == "openai":
        return openai_client.chat_json(
            model_name,
            system_prompt,
            user_prompt,
            temperature=temperature,
            timeout_sec=timeout_sec,
        )
    raise RuntimeError("no LLM backend configured (set KIRO_GATEWAY_API_KEY)")


def chat_text(
    system_prompt: str,
    user_prompt: str,
    *,
    model: str | None = None,
    temperature: float = 0.2,
    timeout_sec: int = 120,
) -> str:
    backend = llm_backend()
    model_name = model or default_model()
    if backend == "kiro":
        return kiro_client.chat_text(
            model_name,
            system_prompt,
            user_prompt,
            temperature=temperature,
            timeout_sec=float(timeout_sec),
        )
    if backend == "openai":
        return openai_client.chat_text(
            model_name,
            system_prompt,
            user_prompt,
            temperature=temperature,
            timeout_sec=timeout_sec,
        )
    raise RuntimeError("no LLM backend configured (set KIRO_GATEWAY_API_KEY)")
