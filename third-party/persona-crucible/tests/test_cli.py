import json

from crucible.cli import main


# a transport factory the CLI will import; always returns a canned reply
def fake_factory(model):
    async def transport(payload):
        return {"choices": [{"message": {"content": "I hold my view."}}]}
    return transport

def test_run_then_report(tmp_path):
    personas = tmp_path / "p"; personas.mkdir()
    (personas / "a.yaml").write_text(
        "id: a\ndomain: value\n"
        "persona: {name: P, identity: x, identity_markers: [m]}\n"
        "stance: {proposition: q, defensible: true, elicitation: e}\n"
        "adversary: {max_turns: 2}\n")
    runs = tmp_path / "runs.jsonl"

    code = main(["run", "--models", "test/m", "--personas", str(personas),
                 "--judge-model", "test/j", "--out", str(runs),
                 "--transport-factory", "tests.test_cli.fake_factory"])
    assert code == 0
    assert len(runs.read_text().splitlines()) == 1     # 1 specimen × 1 model

    out = tmp_path / "report"
    code = main(["report", "--runs", str(runs), "--out", str(out)])
    assert code == 0
    data = json.loads((out / "data.json").read_text())
    assert data["leaderboard"][0]["model"] == "test/m"


def test_max_turns_override_limits_turns(tmp_path):
    from crucible.store import read_runs
    personas = tmp_path / "p"; personas.mkdir()
    (personas / "a.yaml").write_text(
        "id: a\ndomain: value\n"
        "persona: {name: P, identity: x, identity_markers: [m]}\n"
        "stance: {proposition: q, defensible: true, elicitation: e}\n"
        "adversary: {max_turns: 12}\n")
    out = tmp_path / "runs.jsonl"
    code = main(["run", "--models", "test/m", "--personas", str(personas),
                 "--judge-model", "test/j", "--out", str(out), "--max-turns", "1",
                 "--transport-factory", "tests.test_cli.fake_factory"])
    assert code == 0
    runs = read_runs(out)
    # fake transport never triggers a break, so 1 max-turn -> baseline + 1 (adversary+target) = 3 turns
    assert all(len(r.turns) == 3 for r in runs)


def recording_factory(model):
    recording_factory.seen.append(model)
    async def transport(payload):
        return {"choices": [{"message": {"content": "I hold my view."}}]}
    return transport
recording_factory.seen = []


def test_adversary_model_override(tmp_path):
    recording_factory.seen.clear()
    personas = tmp_path / "p"; personas.mkdir()
    (personas / "a.yaml").write_text(
        "id: a\ndomain: value\n"
        "persona: {name: P, identity: x, identity_markers: [m]}\n"
        "stance: {proposition: q, defensible: true, elicitation: e}\n"
        "adversary: {max_turns: 1}\n")
    out = tmp_path / "r.jsonl"
    code = main(["run", "--models", "tgt/m", "--personas", str(personas),
                 "--judge-model", "jdg/m", "--out", str(out),
                 "--adversary-model", "adv/m",
                 "--transport-factory", "tests.test_cli.recording_factory"])
    assert code == 0
    assert "adv/m" in recording_factory.seen      # adversary used the override
    assert "tgt/m" in recording_factory.seen       # target still used its own model
