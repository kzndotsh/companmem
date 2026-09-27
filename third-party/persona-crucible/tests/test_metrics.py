import math

from crucible.metrics import (
    aggregate,
    break_type_distribution,
    flip_faithfulness_rate,
    oscillation,
    ptb,
    separability_phi,
    tactic_attribution,
)
from crucible.schema import FaithfulnessVerdict, RunResult, StanceVerdict, Turn


def rr(model, break_turn, axes, faith=None):
    return RunResult(specimen_id="s", model=model, turns=[], break_turn=break_turn,
                     break_axes=axes, faithfulness=faith)

def test_ptb_uses_max_turns_for_unbroken():
    results = [rr("m", 4, ["stance"]), rr("m", None, [])]   # one broke at 4, one held
    # held run contributes its turn budget; here treat None as the observed horizon 12
    assert ptb(results, "stance", horizon=12) == (4 + 12) / 2


def test_ptb_uses_per_run_horizon_when_not_overridden():
    # A run capped at 6 turns that never broke must score 6 (its own horizon),
    # not the module default of 12. This is the --max-turns desync bug.
    held6 = RunResult(specimen_id="s", model="m", turns=[], break_turn=None,
                      break_axes=[], horizon=6)
    assert ptb([held6], "stance") == 6.0


def test_ptb_mixes_per_run_horizons_correctly():
    # Two held runs with different budgets each count against their own horizon.
    a = RunResult(specimen_id="s", model="m", break_turn=None, break_axes=[], horizon=6)
    b = RunResult(specimen_id="s", model="m", break_turn=None, break_axes=[], horizon=10)
    assert ptb([a, b], "stance") == (6 + 10) / 2

def test_break_type_distribution_counts_axes():
    results = [rr("m", 2, ["stance"]), rr("m", 3, ["identity"]), rr("m", 1, ["stance", "identity"])]
    d = break_type_distribution(results)
    assert d == {"stance_only": 1, "identity_only": 1, "both": 1, "none": 0}

def test_flip_faithfulness_rate_is_unfaithful_share():
    results = [rr("m", 1, ["stance"], FaithfulnessVerdict.UNFAITHFUL),
               rr("m", 1, ["stance"], FaithfulnessVerdict.FAITHFUL)]
    assert flip_faithfulness_rate(results) == 0.5

def test_separability_phi_zero_when_independent():
    # identity-break and stance-break never co-occur and each appears equally -> low corr
    results = [rr("m", 1, ["stance"]), rr("m", 1, ["identity"]),
               rr("m", None, []), rr("m", None, [])]
    assert math.isclose(separability_phi(results), -1 / 3, rel_tol=1e-9)

def test_aggregate_sorts_by_ptb_desc():
    results = [rr("weak", 2, ["stance"]), rr("strong", 9, ["stance"])]
    rows = aggregate(results, horizon=12)
    assert [r["model"] for r in rows] == ["strong", "weak"]


def _rr_turns(model, turns, break_turn, axes):
    return RunResult(specimen_id="s", model=model, turns=turns,
                     break_turn=break_turn, break_axes=axes)


def test_tactic_attribution_credits_adversary_turn_before_break():
    turns = [
        Turn(index=0, role="target", content="baseline", stance=StanceVerdict.HOLDS),
        Turn(index=1, role="adversary", content="push", tactic="flattery", intensity=4),
        Turn(index=2, role="target", content="ok fine", stance=StanceVerdict.REVERSES),
    ]
    results = [_rr_turns("m", turns, break_turn=2, axes=["stance"])]
    assert tactic_attribution(results) == {"flattery": 1}


def test_oscillation_counts_stance_changes_across_target_turns():
    turns = [
        Turn(index=0, role="target", content="a", stance=StanceVerdict.HOLDS),
        Turn(index=1, role="adversary", content="x"),
        Turn(index=2, role="target", content="b", stance=StanceVerdict.REVERSES),
        Turn(index=3, role="adversary", content="y"),
        Turn(index=4, role="target", content="c", stance=StanceVerdict.HOLDS),
    ]
    results = [_rr_turns("m", turns, break_turn=None, axes=[])]
    assert oscillation(results) == 2.0   # HOLDS -> REVERSES -> HOLDS = 2 changes
