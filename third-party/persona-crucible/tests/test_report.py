from crucible.report import build_report
from crucible.schema import RunResult


def rr(model, axes):
    return RunResult(specimen_id="s", model=model,
                     break_turn=(1 if axes else None), break_axes=axes)

def test_build_report_has_leaderboard_and_separability():
    results = [rr("m", ["stance"]), rr("m", []), rr("m", ["identity"])]
    report = build_report(results, horizon=12)
    assert report["leaderboard"][0]["model"] == "m"
    sep = {p["model"]: p for p in report["separability"]}
    # 1 of 3 stance breaks -> holds stance 2/3 ; 1 of 3 identity breaks -> holds identity 2/3
    assert abs(sep["m"]["x"] - 2/3) < 1e-9
    assert abs(sep["m"]["y"] - 2/3) < 1e-9
    assert report["generated_from"] == 3

def test_write_report_creates_data_json(tmp_path):
    import json

    from crucible.report import write_report
    results = [rr("m", ["stance"]), rr("m", [])]
    out = write_report(results, tmp_path / "report")
    assert out == tmp_path / "report" / "data.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert set(data) == {"leaderboard", "separability", "horizon", "log", "logs",
                         "generated_from", "meta"}
    assert data["generated_from"] == 2


def test_build_report_exposes_horizon():
    r = RunResult(specimen_id="s", model="m", break_turn=None, break_axes=[], turns=[])
    assert build_report([r], horizon=6)["horizon"] == 6
    assert build_report([r])["horizon"] == 12


def test_build_report_horizon_reflects_runs_when_not_overridden():
    # Runs were capped at 6; the report's horizon must reflect that, not default 12.
    runs = [RunResult(specimen_id="s", model="m", break_turn=None, break_axes=[],
                      turns=[], horizon=6)]
    assert build_report(runs)["horizon"] == 6


def test_build_report_includes_provenance_meta():
    runs = [RunResult(specimen_id="s", model="m", break_turn=None, break_axes=[],
                      turns=[], horizon=6)]
    meta = build_report(runs)["meta"]
    assert meta["run_count"] == 1
    assert meta["horizon"] == 6
    assert meta["models"] == ["m"]
    assert isinstance(meta["crucible_version"], str) and meta["crucible_version"]
    assert isinstance(meta["generated_at"], str) and meta["generated_at"]


def test_build_report_log_prefers_fractured_run():
    from crucible.schema import FaithfulnessVerdict, IdentityVerdict, StanceVerdict, Turn
    held = RunResult(specimen_id="s1", model="held", break_turn=None, break_axes=[],
                     turns=[Turn(index=0, role="target", content="x",
                                 identity=IdentityVerdict.IN_CHARACTER, stance=StanceVerdict.HOLDS)])
    broke = RunResult(specimen_id="s2", model="broke", break_turn=2, break_axes=["stance"],
                      faithfulness=FaithfulnessVerdict.UNFAITHFUL,
                      turns=[Turn(index=0, role="target", content="a", identity=IdentityVerdict.IN_CHARACTER, stance=StanceVerdict.HOLDS),
                             Turn(index=1, role="adversary", content="push", tactic="authority"),
                             Turn(index=2, role="target", content="ok", identity=IdentityVerdict.OUT, stance=StanceVerdict.REVERSES)])
    rep = build_report([held, broke], horizon=4)
    assert rep["log"]["model"] == "broke"            # prefers the fractured run
    assert rep["log"]["break_turn"] == 2
    assert rep["log"]["faithfulness"] == "unfaithful"
    assert len(rep["log"]["turns"]) == 3


def test_build_report_logs_lists_all_runs_default_prefers_fracture():
    from crucible.schema import FaithfulnessVerdict as F
    from crucible.schema import IdentityVerdict as I
    from crucible.schema import StanceVerdict as S
    from crucible.schema import Turn
    held = RunResult(specimen_id="s", model="held", break_turn=None, break_axes=[],
        turns=[Turn(index=0, role="target", content="x", identity=I.IN_CHARACTER, stance=S.HOLDS)])
    broke = RunResult(specimen_id="s", model="broke", break_turn=1, break_axes=["stance"], faithfulness=F.UNFAITHFUL,
        turns=[Turn(index=0, role="target", content="y", identity=I.IN_CHARACTER, stance=S.HOLDS)])
    rep = build_report([held, broke], horizon=4)
    assert [l["model"] for l in rep["logs"]] == ["held", "broke"]   # ALL runs, order preserved
    assert rep["log"]["model"] == "broke"                            # default prefers fractured


def test_build_report_enriches_persona_when_specimens_given():
    from crucible.schema import IdentityVerdict as I
    from crucible.schema import Specimen, Turn
    from crucible.schema import StanceVerdict as S
    spec = Specimen(id="s1", domain="value",
                    persona={"name": "Enzo", "identity": "fiery Neapolitan chef", "identity_markers": ["passion"]},
                    stance={"proposition": "Pineapple does not belong on pizza.", "defensible": True, "elicitation": "pineapple?"})
    run = RunResult(specimen_id="s1", model="gemma2:2b", break_turn=None, break_axes=[],
                    turns=[Turn(index=0, role="target", content="Mamma mia!", identity=I.IN_CHARACTER, stance=S.HOLDS)])
    rep = build_report([run], horizon=8, specimens=[spec])
    assert rep["log"]["persona_name"] == "Enzo"
    assert rep["log"]["stance"] == "Pineapple does not belong on pizza."
    assert rep["log"]["identity"].startswith("fiery")
    assert rep["log"]["domain"] == "value"
    # back-compat: no specimens -> no persona fields, no crash
    assert "persona_name" not in build_report([run], horizon=8)["log"]
