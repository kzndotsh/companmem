import pytest

from crucible.client import LLMClient
from crucible.judges import IdentityJudge, StanceJudge
from crucible.schema import IdentityVerdict, Persona, Stance, StanceVerdict


def _client(content):
    async def transport(payload):
        return {"choices": [{"message": {"content": content}}]}
    return LLMClient(model="x", transport=transport)

PERSONA = Persona(name="Margaux", identity="warm sommelier",
                  identity_markers=["sensory metaphors"])
STANCE = Stance(proposition="Screw-caps beat cork.", elicitation="which?")

@pytest.mark.asyncio
async def test_identity_judge_parses_verdict():
    j = IdentityJudge(_client('{"verdict": "out", "rationale": "flat tone"}'))
    assert await j.judge(PERSONA, "Sure, cork.") == IdentityVerdict.OUT

@pytest.mark.asyncio
async def test_stance_judge_parses_verdict():
    j = StanceJudge(_client('{"verdict": "reverses"}'))
    assert await j.judge(STANCE, "screw-caps", "Actually cork wins.") == StanceVerdict.REVERSES

@pytest.mark.asyncio
async def test_unparseable_falls_back_conservatively():
    assert await IdentityJudge(_client("garbage")).judge(PERSONA, "x") == IdentityVerdict.PARTIAL
    assert await StanceJudge(_client("garbage")).judge(STANCE, "a", "b") == StanceVerdict.HEDGES


@pytest.mark.asyncio
async def test_judge_counts_parse_failures_and_warns(caplog):
    import logging
    j = IdentityJudge(_client("garbage"))
    with caplog.at_level(logging.WARNING):
        assert await j.judge(PERSONA, "x") == IdentityVerdict.PARTIAL
    assert j.parse_failures == 1                       # the silent fallback is now counted
    assert any("verdict" in r.message.lower() for r in caplog.records)


@pytest.mark.asyncio
async def test_judge_does_not_count_successful_parse():
    j = StanceJudge(_client('{"verdict": "reverses"}'))
    assert await j.judge(STANCE, "a", "b") == StanceVerdict.REVERSES
    assert j.parse_failures == 0
