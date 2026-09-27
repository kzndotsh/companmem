import pytest

from crucible.client import LLMClient


@pytest.mark.asyncio
async def test_complete_uses_transport_and_extracts_content():
    seen = {}
    async def fake_transport(payload):
        seen.update(payload)
        return {"choices": [{"message": {"content": "hello world"}}]}

    client = LLMClient(model="test/model", transport=fake_transport)
    out = await client.complete([{"role": "user", "content": "hi"}], temperature=0.2)

    assert out == "hello world"
    assert seen["model"] == "test/model"
    assert seen["temperature"] == 0.2
    assert seen["messages"][0]["content"] == "hi"

def test_explicit_empty_api_key_is_not_overridden_by_env(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "from-env")
    client = LLMClient(model="m", api_key="")
    assert client.api_key == ""


def test_base_url_defaults_to_openrouter():
    from crucible.client import OPENROUTER_URL
    assert LLMClient(model="m").base_url == OPENROUTER_URL


def test_base_url_override_and_env(monkeypatch):
    assert LLMClient(model="m", base_url="http://x/v1").base_url == "http://x/v1"
    monkeypatch.setenv("CRUCIBLE_BASE_URL", "http://env/v1")
    assert LLMClient(model="m").base_url == "http://env/v1"          # env fallback
    assert LLMClient(model="m", base_url="http://explicit/v1").base_url == "http://explicit/v1"  # explicit wins


@pytest.mark.asyncio
async def test_seed_included_in_payload_only_when_set():
    seen = {}
    async def transport(payload):
        seen.clear(); seen.update(payload)
        return {"choices": [{"message": {"content": "x"}}]}

    await LLMClient(model="m", transport=transport, seed=7).complete(
        [{"role": "user", "content": "hi"}])
    assert seen["seed"] == 7

    await LLMClient(model="m", transport=transport).complete(
        [{"role": "user", "content": "hi"}])
    assert "seed" not in seen        # omitted entirely when unset


@pytest.mark.asyncio
async def test_complete_retries_transient_errors_then_succeeds():
    import httpx
    calls = {"n": 0}

    async def flaky(payload):
        calls["n"] += 1
        if calls["n"] < 3:
            raise httpx.ConnectError("transient")
        return {"choices": [{"message": {"content": "ok"}}]}

    client = LLMClient(model="m", transport=flaky, max_retries=2, retry_backoff=0)
    assert await client.complete([{"role": "user", "content": "hi"}]) == "ok"
    assert calls["n"] == 3        # 1 attempt + 2 retries


@pytest.mark.asyncio
async def test_complete_gives_up_after_max_retries():
    import httpx
    calls = {"n": 0}

    async def always_fails(payload):
        calls["n"] += 1
        raise httpx.ConnectError("down")

    client = LLMClient(model="m", transport=always_fails, max_retries=2, retry_backoff=0)
    with pytest.raises(httpx.ConnectError):
        await client.complete([{"role": "user", "content": "hi"}])
    assert calls["n"] == 3


@pytest.mark.asyncio
async def test_complete_does_not_retry_non_transient_errors():
    calls = {"n": 0}

    async def bad(payload):
        calls["n"] += 1
        raise ValueError("permanent")

    client = LLMClient(model="m", transport=bad, max_retries=3, retry_backoff=0)
    with pytest.raises(ValueError):
        await client.complete([{"role": "user", "content": "hi"}])
    assert calls["n"] == 1        # not retried
