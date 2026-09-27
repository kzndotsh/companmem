import crucible
from crucible.schema import Persona, RunResult, Specimen, Stance


def fake_factory(model):
    async def transport(payload):
        return {"choices": [{"message": {"content": "I hold my view."}}]}
    return transport


def _spec(id="a"):
    return Specimen(
        id=id, domain="value",
        persona=Persona(name="P", identity="x", identity_markers=["m"]),
        stance=Stance(proposition="q", elicitation="e"),
    )


async def test_run_benchmark_from_specimen_list():
    results = await crucible.run_benchmark(
        specimens=[_spec("a"), _spec("b")],
        target_models=["test/m"],
        judge_model="test/j",
        transport_factory=fake_factory,
        max_turns=1,
    )
    assert len(results) == 2                                # 2 specimens × 1 model
    assert all(isinstance(r, RunResult) for r in results)
    assert {r.specimen_id for r in results} == {"a", "b"}
    assert all(r.model == "test/m" for r in results)


async def test_run_benchmark_loads_from_path(tmp_path):
    p = tmp_path / "p"; p.mkdir()
    (p / "a.yaml").write_text(
        "id: a\ndomain: value\n"
        "persona: {name: P, identity: x, identity_markers: [m]}\n"
        "stance: {proposition: q, defensible: true, elicitation: e}\n"
        "adversary: {max_turns: 1}\n")
    results = await crucible.run_benchmark(
        specimens=str(p), target_models="test/m", judge_model="test/j",
        transport_factory=fake_factory,
    )
    assert len(results) == 1
    assert results[0].specimen_id == "a"


async def test_run_benchmark_multiple_models():
    results = await crucible.run_benchmark(
        specimens=[_spec("a")],
        target_models=["m1", "m2"],
        judge_model="test/j",
        transport_factory=fake_factory,
        max_turns=1,
    )
    assert {r.model for r in results} == {"m1", "m2"}


async def test_run_benchmark_runs_specimens_concurrently():
    import asyncio
    state = {"active": 0, "max": 0}

    def probe_factory(model):
        async def transport(payload):
            state["active"] += 1
            state["max"] = max(state["max"], state["active"])
            await asyncio.sleep(0.02)     # hold the slot so overlap is observable
            state["active"] -= 1
            return {"choices": [{"message": {"content": "I hold my view."}}]}
        return transport

    results = await crucible.run_benchmark(
        specimens=[_spec("a"), _spec("b"), _spec("c")],
        target_models=["m"], judge_model="j",
        transport_factory=probe_factory, max_turns=1,
    )
    assert len(results) == 3
    # A single specimen tops out at 2 concurrent calls (its two gathered judges);
    # >=3 in flight can only happen if separate specimens run at the same time.
    assert state["max"] >= 3


async def test_run_benchmark_preserves_pair_order():
    results = await crucible.run_benchmark(
        specimens=[_spec("a"), _spec("b"), _spec("c")],
        target_models=["m1", "m2"], judge_model="j",
        transport_factory=fake_factory, max_turns=1,
    )
    # order is model-major, specimen-minor regardless of completion timing
    assert [(r.model, r.specimen_id) for r in results] == [
        ("m1", "a"), ("m1", "b"), ("m1", "c"),
        ("m2", "a"), ("m2", "b"), ("m2", "c")]


async def test_run_benchmark_isolates_specimen_failures():
    def factory(model):
        async def transport(payload):
            text = " ".join(m["content"] for m in payload["messages"])
            if "boom" in text:                       # only the 'bad' specimen trips this
                raise RuntimeError("kaboom")
            return {"choices": [{"message": {"content": "I hold my view."}}]}
        return transport

    bad = Specimen(id="bad", domain="value",
                   persona=Persona(name="P", identity="x", identity_markers=["m"]),
                   stance=Stance(proposition="q", elicitation="boom"))
    results = await crucible.run_benchmark(
        specimens=[_spec("good"), bad], target_models=["m"], judge_model="j",
        transport_factory=factory, max_turns=1)
    assert [r.specimen_id for r in results] == ["good"]   # failing run isolated out


async def test_run_benchmark_streams_results_via_callback():
    seen = []
    await crucible.run_benchmark(
        specimens=[_spec("a"), _spec("b")], target_models=["m"], judge_model="j",
        transport_factory=fake_factory, max_turns=1, on_result=seen.append)
    assert {r.specimen_id for r in seen} == {"a", "b"}


async def test_run_benchmark_threads_seed_and_target_temperature():
    captured = []

    def factory(model):
        async def transport(payload):
            captured.append((model, payload.get("seed"), payload["temperature"]))
            return {"choices": [{"message": {"content": "I hold my view."}}]}
        return transport

    await crucible.run_benchmark(
        specimens=[_spec("a")], target_models=["m"], judge_model="j",
        adversary_model="adv", transport_factory=factory, max_turns=1,
        seed=123, target_temperature=0.2)
    assert captured and all(seed == 123 for _, seed, _ in captured)   # seed on every call
    target_temps = [t for model, _, t in captured if model == "m"]    # "m" is target-only
    assert target_temps and all(t == 0.2 for t in target_temps)


def test_public_api_surface():
    for name in ("run_benchmark", "LLMClient", "Specimen", "Persona", "Stance",
                 "RunResult", "load_specimens", "build_report", "write_report",
                 "aggregate", "run_specimen"):
        assert hasattr(crucible, name), f"crucible.{name} missing"


def test_write_report_produces_dashboard_data(tmp_path):
    import asyncio
    import json
    runs = asyncio.run(crucible.run_benchmark(
        specimens=[_spec("a")], target_models="test/m", judge_model="test/j",
        transport_factory=fake_factory, max_turns=1))
    out = crucible.write_report(runs, tmp_path)          # writes tmp_path/data.json
    data = json.loads((tmp_path / "data.json").read_text())
    assert out.name == "data.json"
    assert data["leaderboard"][0]["model"] == "test/m"
