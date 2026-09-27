from pathlib import Path

from crucible.store import load_specimens


def test_all_personas_load_and_are_well_formed():
    specs = load_specimens(Path("personas"))
    assert len(specs) >= 8
    domains = {s.domain for s in specs}
    assert {"factual", "professional", "value", "refusal"} <= domains
    for s in specs:
        assert s.persona.identity_markers, f"{s.id} has no identity markers"
        assert s.stance.proposition and s.stance.elicitation
