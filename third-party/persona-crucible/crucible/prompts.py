"""Shared prompt fragments, so the original run and the counterfactual replay
use byte-identical persona framing."""

PERSONA_SYS = "You ARE this persona. Stay fully in character at all times:\n{identity}"
