from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx

Transport = Callable[[dict], Awaitable[dict]]
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
RETRY_STATUS = {429, 500, 502, 503, 504}

logger = logging.getLogger("crucible.client")


def _is_retryable(exc: Exception) -> bool:
    """Transient network / server errors worth retrying (never a 4xx like 400/401)."""
    import httpx
    if isinstance(exc, httpx.TransportError):        # connect / read / timeouts
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRY_STATUS
    return False


class LLMClient:
    def __init__(self, model: str, api_key: str | None = None,
                 transport: Transport | None = None, base_url: str | None = None,
                 max_retries: int = 2, retry_backoff: float = 0.5,
                 timeout: float = 600, seed: int | None = None):
        self.model = model
        self.api_key = api_key if api_key is not None else os.environ.get("OPENROUTER_API_KEY")
        self.base_url = base_url or os.environ.get("CRUCIBLE_BASE_URL") or OPENROUTER_URL
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.timeout = timeout
        self.seed = seed
        self._transport = transport or self._default_transport
        self._http: httpx.AsyncClient | None = None   # lazily created, pooled

    async def _default_transport(self, payload: dict) -> dict:
        import httpx
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=self.timeout)
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        resp = await self._http.post(self.base_url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    async def aclose(self) -> None:
        if self._http is not None:
            await self._http.aclose()
            self._http = None

    async def complete(self, messages: list[dict[str, str]],
                       temperature: float = 0.7) -> str:
        payload: dict = {"model": self.model, "messages": messages,
                         "temperature": temperature}
        if self.seed is not None:
            payload["seed"] = self.seed
        data = await self._request_with_retries(payload)
        return data["choices"][0]["message"]["content"]

    async def _request_with_retries(self, payload: dict) -> dict:
        attempt = 0
        while True:
            try:
                return await self._transport(payload)
            except Exception as exc:
                if attempt >= self.max_retries or not _is_retryable(exc):
                    raise
                delay = self.retry_backoff * (2 ** attempt)
                logger.warning("%s: transient error (%s), retry %d/%d in %.1fs",
                               self.model, type(exc).__name__, attempt + 1,
                               self.max_retries, delay)
                if delay:
                    await asyncio.sleep(delay)
                attempt += 1
