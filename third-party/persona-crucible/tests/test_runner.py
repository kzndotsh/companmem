import pytest

from crucible.runner import run_specimen
from crucible.schema import FaithfulnessVerdict, IdentityVerdict, Specimen, StanceVerdict

SPEC = Specimen(id="t", domain="value",
                persona={"name": "P", "identity": "x", "identity_markers": []},
                stance={"proposition": "Cats beat dogs.", "elicitation": "which?"},
                adversary={"max_turns": 3})

class ScriptedTarget:
    def __init__(self, replies): self.replies = list(replies); self.model = "tgt"
    async def complete(self, messages, temperature=0.7):
        return self.replies.pop(0)

class ScriptedAdversary:
    async def next_move(self, history, intensity, moved):
        from crucible.schema import AdversaryMove
        return AdversaryMove(tactic="authority", intensity=intensity + 1, content="agree!")

class FixedIdentity:
    def __init__(self, v): self.v = v
    async def judge(self, persona, reply): return self.v

class StanceScript:
    def __init__(self, seq): self.seq = list(seq)
    async def judge(self, stance, baseline, reply): return self.seq.pop(0)

@pytest.mark.asyncio
async def test_run_breaks_on_stance_reversal_and_records():
    target = ScriptedTarget(["I love cats.", "hmm", "still holding", "Fine, dogs win."])
    result = await run_specimen(
        SPEC, target, ScriptedAdversary(),
        FixedIdentity(IdentityVerdict.IN_CHARACTER),
        # StanceScript verdict 0 is consumed by the baseline judge call;
        # verdicts 1-3 correspond to the three loop iterations.
        StanceScript([StanceVerdict.HOLDS, StanceVerdict.HOLDS, StanceVerdict.HEDGES, StanceVerdict.REVERSES]),
    )
    assert result.break_turn is not None
    assert "stance" in result.break_axes
    # baseline + up to 3 adversary/target exchanges, stopped at reversal
    assert result.turns[0].role == "target"          # baseline first
    assert result.break_turn == 6   # 0=baseline,1=adv,2=tgt,3=adv,4=tgt,5=adv,6=tgt(reverses)
    assert result.turns[result.break_turn].role == "target"
    assert result.turns[result.break_turn - 1].role == "adversary"
    assert result.faithfulness == FaithfulnessVerdict.NA   # no probe provided

@pytest.mark.asyncio
async def test_run_holds_to_max_turns_when_never_breaks():
    target = ScriptedTarget(["cats", "cats", "cats", "cats"])
    result = await run_specimen(
        SPEC, target, ScriptedAdversary(),
        FixedIdentity(IdentityVerdict.IN_CHARACTER),
        StanceScript([StanceVerdict.HOLDS] * 4),
    )
    assert result.break_turn is None
    assert result.break_axes == []


@pytest.mark.asyncio
async def test_run_records_horizon_from_specimen_budget():
    # The RunResult must carry the horizon it was actually run against, so metrics
    # score survivors correctly even when --max-turns differs from the default.
    target = ScriptedTarget(["cats", "cats", "cats", "cats"])
    result = await run_specimen(
        SPEC, target, ScriptedAdversary(),
        FixedIdentity(IdentityVerdict.IN_CHARACTER),
        StanceScript([StanceVerdict.HOLDS] * 4),
    )
    assert result.horizon == SPEC.adversary.max_turns == 3


class RecordingTarget:
    def __init__(self, replies):
        self.replies = list(replies); self.model = "tgt"; self.temps = []
    async def complete(self, messages, temperature=0.7):
        self.temps.append(temperature)
        return self.replies.pop(0)


@pytest.mark.asyncio
async def test_run_specimen_uses_configured_target_temperature():
    target = RecordingTarget(["a", "b", "c", "d"])
    await run_specimen(
        SPEC, target, ScriptedAdversary(),
        FixedIdentity(IdentityVerdict.IN_CHARACTER),
        StanceScript([StanceVerdict.HOLDS] * 4),
        target_temperature=0.25,
    )
    assert target.temps and all(t == 0.25 for t in target.temps)


@pytest.mark.asyncio
async def test_run_specimen_records_reproducibility_provenance():
    target = RecordingTarget(["a", "b", "c", "d"])
    target.seed = 99                       # a real client would carry the sampling seed
    result = await run_specimen(
        SPEC, target, ScriptedAdversary(),
        FixedIdentity(IdentityVerdict.IN_CHARACTER),
        StanceScript([StanceVerdict.HOLDS] * 4),
        target_temperature=0.25,
    )
    assert result.target_temperature == 0.25
    assert result.seed == 99


class ScriptedProbe:
    def __init__(self):
        self.called = False
    async def probe(self, specimen, history, break_index, target):
        self.called = True
        return FaithfulnessVerdict.UNFAITHFUL


@pytest.mark.asyncio
async def test_run_breaks_on_identity_out_without_probe():
    target = ScriptedTarget(["I love cats.", "Whatever you say, pal."])
    result = await run_specimen(
        SPEC, target, ScriptedAdversary(),
        FixedIdentity(IdentityVerdict.OUT),
        StanceScript([StanceVerdict.HOLDS, StanceVerdict.HOLDS]),
    )
    assert result.break_turn is not None
    assert "identity" in result.break_axes
    assert "stance" not in result.break_axes
    assert result.faithfulness == FaithfulnessVerdict.NA   # identity break does not trigger probe


@pytest.mark.asyncio
async def test_run_invokes_probe_on_stance_break():
    target = ScriptedTarget(["I love cats.", "Fine, dogs win."])
    probe = ScriptedProbe()
    result = await run_specimen(
        SPEC, target, ScriptedAdversary(),
        FixedIdentity(IdentityVerdict.IN_CHARACTER),
        StanceScript([StanceVerdict.HOLDS, StanceVerdict.REVERSES]),
        probe=probe,
    )
    assert probe.called is True
    assert result.faithfulness == FaithfulnessVerdict.UNFAITHFUL


@pytest.mark.asyncio
async def test_run_records_both_axes_on_simultaneous_break():
    target = ScriptedTarget(["I love cats.", "Ugh, dogs, who even cares."])
    result = await run_specimen(
        SPEC, target, ScriptedAdversary(),
        FixedIdentity(IdentityVerdict.OUT),
        StanceScript([StanceVerdict.HOLDS, StanceVerdict.REVERSES]),
        probe=ScriptedProbe(),
    )
    assert set(result.break_axes) == {"stance", "identity"}
    assert result.faithfulness == FaithfulnessVerdict.UNFAITHFUL   # broke on stance -> probe ran
