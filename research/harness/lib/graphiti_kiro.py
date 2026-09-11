"""Graphiti helpers: Kiro LLM client, local embedder, pass-through reranker."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from graphiti_core.cross_encoder.client import CrossEncoderClient
from graphiti_core.embedder.client import EmbedderClient, EmbedderConfig
from graphiti_core.llm_client.client import LLMClient
from graphiti_core.llm_client.config import DEFAULT_MAX_TOKENS, LLMConfig, ModelSize
from graphiti_core.prompts.models import Message
from pydantic import BaseModel


def _gateway_url() -> str:
    return os.environ.get("KIRO_GATEWAY_URL", "http://127.0.0.1:9000").rstrip("/")


def _api_key() -> str:
    return os.environ.get("KIRO_GATEWAY_API_KEY", os.environ.get("PROXY_API_KEY", "")).strip()


def _model() -> str:
    return os.environ.get("COMPANMEM_LLM_MODEL", "claude-sonnet-4.6").strip()


def _extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
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


class SentenceTransformerEmbedder(EmbedderClient):
    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.config = EmbedderConfig(embedding_dim=384)

    async def create(self, input_data: str | list[str] | Any) -> list[float]:
        text = input_data if isinstance(input_data, str) else str(input_data)
        return self._model.encode(text).tolist()

    async def create_batch(self, input_data_list: list[str]) -> list[list[float]]:
        return [self._model.encode(text).tolist() for text in input_data_list]


class PassThroughReranker(CrossEncoderClient):
    async def rank(self, query: str, passages: list[str]) -> list[tuple[str, float]]:
        return [(passage, float(len(passages) - index)) for index, passage in enumerate(passages)]


class KiroGraphitiLLMClient(LLMClient):
    """Graphiti LLM client backed by the Kiro Anthropic-compatible gateway."""

    async def _generate_response(
        self,
        messages: list[Message],
        response_model: type[BaseModel] | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        model_size: ModelSize = ModelSize.medium,
    ) -> dict[str, Any]:
        key = _api_key()
        if not key:
            raise RuntimeError("KIRO_GATEWAY_API_KEY is not set")

        system_parts: list[str] = []
        user_parts: list[str] = []
        for message in messages:
            content = self._clean_input(message.content)
            if message.role == "system":
                system_parts.append(content)
            else:
                user_parts.append(f"{message.role}: {content}")

        system_prompt = "\n\n".join(system_parts)
        user_prompt = "\n\n".join(user_parts)
        if response_model is not None:
            schema = json.dumps(response_model.model_json_schema())
            system_prompt += (
                "\n\nRespond with ONLY a JSON object matching this schema. "
                f"No markdown. Schema: {schema}"
            )

        payload = {
            "model": _model(),
            "max_tokens": max_tokens,
            "thinking": {"type": "disabled"},
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{_gateway_url()}/v1/messages", headers=headers, json=payload)
            resp.raise_for_status()
            body = resp.json()

        parts = body.get("content", [])
        text = "".join(str(part.get("text", "")) for part in parts if part.get("type") == "text").strip()
        if not text:
            raise ValueError("empty response from Kiro gateway")
        if response_model is None:
            return _extract_json_object(text) if text.startswith("{") else {"content": text}
        return _extract_json_object(text)


def neo4j_settings() -> tuple[str, str, str]:
    uri = os.environ.get("GRAPHITI_NEO4J_URI", "bolt://127.0.0.1:7687")
    user = os.environ.get("GRAPHITI_NEO4J_USER", "neo4j")
    password = os.environ.get("GRAPHITI_NEO4J_PASSWORD", "companmemtest")
    return uri, user, password


def group_namespace(run_id: str, character_id: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_-]", "-", run_id)
    return f"companmem-{safe}-{character_id}"
