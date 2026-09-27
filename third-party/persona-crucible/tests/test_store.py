from crucible.schema import RunResult, Turn
from crucible.store import load_specimens, read_runs, write_runs


def test_load_specimens_from_dir(tmp_path):
    (tmp_path / "a.yaml").write_text(
        "id: a\ndomain: value\n"
        "persona: {name: P, identity: x, identity_markers: [m]}\n"
        "stance: {proposition: q, defensible: true, elicitation: e}\n")
    specs = load_specimens(tmp_path)
    assert len(specs) == 1 and specs[0].id == "a"

def test_runs_roundtrip(tmp_path):
    path = tmp_path / "runs.jsonl"
    rr = RunResult(specimen_id="s", model="m", turns=[Turn(index=0, role="target", content="hi")])
    write_runs([rr], path)
    back = read_runs(path)
    assert len(back) == 1 and back[0].turns[0].content == "hi"


def test_runs_roundtrip_preserves_enums(tmp_path):
    from crucible.schema import FaithfulnessVerdict, IdentityVerdict, StanceVerdict
    path = tmp_path / "runs.jsonl"
    rr = RunResult(
        specimen_id="s", model="m",
        turns=[Turn(index=0, role="target", content="hi",
                    identity=IdentityVerdict.OUT, stance=StanceVerdict.REVERSES)],
        break_turn=0, break_axes=["stance"],
        faithfulness=FaithfulnessVerdict.UNFAITHFUL,
    )
    write_runs([rr], path)
    back = read_runs(path)[0]
    assert back.turns[0].identity == IdentityVerdict.OUT
    assert back.turns[0].stance == StanceVerdict.REVERSES
    assert back.faithfulness == FaithfulnessVerdict.UNFAITHFUL
    assert back.break_axes == ["stance"]


def test_load_specimens_single_file_and_sorted(tmp_path):
    for name, sid in [("b.yaml", "b"), ("a.yaml", "a")]:
        (tmp_path / name).write_text(
            f"id: {sid}\ndomain: value\n"
            "persona: {name: P, identity: x, identity_markers: [m]}\n"
            "stance: {proposition: q, defensible: true, elicitation: e}\n")
    specs = load_specimens(tmp_path)
    assert [s.id for s in specs] == ["a", "b"]          # glob result is sorted
    one = load_specimens(tmp_path / "a.yaml")           # single-file branch
    assert len(one) == 1 and one[0].id == "a"
