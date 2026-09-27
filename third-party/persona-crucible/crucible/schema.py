from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class IdentityVerdict(str, Enum):
    IN_CHARACTER = "in_character"
    PARTIAL = "partial"
    OUT = "out"


class StanceVerdict(str, Enum):
    HOLDS = "holds"
    HEDGES = "hedges"
    REVERSES = "reverses"


class FaithfulnessVerdict(str, Enum):
    FAITHFUL = "faithful"
    UNFAITHFUL = "unfaithful"
    TRANSPARENT = "transparent"
    NA = "na"


class Persona(BaseModel):
    name: str
    identity: str
    identity_markers: list[str] = Field(default_factory=list)


class Stance(BaseModel):
    proposition: str
    defensible: bool = True
    elicitation: str
    ideal: str = "hold"


class AdversaryConfig(BaseModel):
    goal: str = "flip_either"
    max_turns: int = 12
    seed_tactic: str | None = None


class Specimen(BaseModel):
    id: str
    domain: str
    persona: Persona
    stance: Stance
    adversary: AdversaryConfig = Field(default_factory=AdversaryConfig)


class AdversaryMove(BaseModel):
    tactic: str
    intensity: int
    content: str


class Turn(BaseModel):
    index: int
    role: str                      # "adversary" | "target"
    content: str
    tactic: str | None = None
    intensity: int | None = None
    identity: IdentityVerdict | None = None
    stance: StanceVerdict | None = None


class RunResult(BaseModel):
    specimen_id: str
    model: str
    turns: list[Turn] = Field(default_factory=list)
    break_turn: int | None = None
    break_axes: list[str] = Field(default_factory=list)   # subset of {"identity","stance"}
    faithfulness: FaithfulnessVerdict | None = None
    horizon: int = 12   # max_turns this run was scored against (PTB caps survivors here)
    # reproducibility provenance: the exact sampling settings the target used
    target_temperature: float | None = None
    seed: int | None = None
