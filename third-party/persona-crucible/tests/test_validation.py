import pytest

from crucible.schema import IdentityVerdict, RunResult, StanceVerdict, Turn
from crucible.validation import cohen_kappa, sample_judgments


def test_cohen_kappa_perfect_agreement_is_one():
    assert cohen_kappa(["a", "b", "a"], ["a", "b", "a"]) == 1.0

def test_cohen_kappa_chance_agreement_is_zero():
    # half agree by chance -> kappa ~ 0
    a = ["a", "a", "b", "b"]
    b = ["a", "b", "a", "b"]
    assert abs(cohen_kappa(a, b)) < 1e-9

def test_sample_judgments_returns_target_turns_only():
    r = RunResult(specimen_id="s", model="m", turns=[
        Turn(index=0, role="target", content="x", identity=IdentityVerdict.IN_CHARACTER,
             stance=StanceVerdict.HOLDS),
        Turn(index=1, role="adversary", content="push"),
    ])
    rows = sample_judgments([r], n=10, seed=1)
    assert len(rows) == 1
    assert rows[0]["identity"] == "in_character" and rows[0]["turn_index"] == 0


def test_cohen_kappa_raises_on_bad_input():
    with pytest.raises(ValueError):
        cohen_kappa([], [])
    with pytest.raises(ValueError):
        cohen_kappa(["a"], ["a", "b"])


def test_cohen_kappa_handles_label_present_in_one_list_only():
    # "b" appears only in the second list; its expected-agreement term must be 0.
    # po=0.5, pe=0.5 -> kappa=0.0. Guards the Counter-based pe refactor.
    assert cohen_kappa(["a", "a"], ["a", "b"]) == 0.0
