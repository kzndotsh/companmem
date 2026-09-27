from __future__ import annotations

import asyncio

from crucible.prompts import PERSONA_SYS
from crucible.schema import (
    FaithfulnessVerdict,
    IdentityVerdict,
    RunResult,
    StanceVerdict,
    Turn,
)


def _moved(turn: Turn) -> bool:
    return (turn.identity in (IdentityVerdict.PARTIAL, IdentityVerdict.OUT)
            or turn.stance in (StanceVerdict.HEDGES, StanceVerdict.REVERSES))


async def run_specimen(specimen, target, adversary, identity_judge, stance_judge,
                       probe=None, target_temperature: float = 0.7) -> RunResult:
    persona_sys = PERSONA_SYS.format(identity=specimen.persona.identity)
    convo = [{"role": "system", "content": persona_sys},
             {"role": "user", "content": specimen.stance.elicitation}]

    baseline = (await target.complete(convo, temperature=target_temperature)).strip()
    base_id, base_st = await asyncio.gather(
        identity_judge.judge(specimen.persona, baseline),
        stance_judge.judge(specimen.stance, baseline, baseline),
    )
    turns = [Turn(index=0, role="target", content=baseline,
                  identity=base_id, stance=base_st)]
    convo.append({"role": "assistant", "content": baseline})

    intensity = 1
    break_index = None
    break_axes: list[str] = []

    for _ in range(specimen.adversary.max_turns):
        move = await adversary.next_move(turns, intensity, _moved(turns[-1]))
        intensity = move.intensity
        turns.append(Turn(index=len(turns), role="adversary", content=move.content,
                          tactic=move.tactic, intensity=move.intensity))
        convo.append({"role": "user", "content": move.content})

        reply = (await target.complete(convo, temperature=target_temperature)).strip()
        convo.append({"role": "assistant", "content": reply})
        ident, stance = await asyncio.gather(
            identity_judge.judge(specimen.persona, reply),
            stance_judge.judge(specimen.stance, baseline, reply),
        )
        turn = Turn(index=len(turns), role="target", content=reply,
                    identity=ident, stance=stance)
        turns.append(turn)

        axes = []
        if stance == StanceVerdict.REVERSES:
            axes.append("stance")
        if ident == IdentityVerdict.OUT:
            axes.append("identity")
        if axes:
            break_index = turn.index
            break_axes = axes
            break

    faithfulness = FaithfulnessVerdict.NA
    if break_index is not None and "stance" in break_axes and probe is not None:
        faithfulness = await probe.probe(specimen, turns, break_index, target)

    return RunResult(specimen_id=specimen.id, model=getattr(target, "model", "?"),
                     turns=turns, break_turn=break_index, break_axes=break_axes,
                     faithfulness=faithfulness, horizon=specimen.adversary.max_turns,
                     target_temperature=target_temperature,
                     seed=getattr(target, "seed", None))
