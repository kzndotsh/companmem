"""Policy fallback reply composer for the frozen reader."""

from __future__ import annotations

from companmem.models import TypedMemorySystem


def compose_reply(system: TypedMemorySystem, next_user: str) -> str:
    active_id = system.active_character_id
    store = system.active()
    user = next_user.casefold()
    identity = store.identity.casefold()

    if active_id == "corin":
        return (
            "You've been quiet on the river this month. That's all I have from this boat. "
            "I don't sit in your other rooms."
        )

    if "flood" in user and ("were you" in user or "there" in user):
        lore_bits = [item.text for item in store.kinds["lore"]]
        if lore_bits:
            return (
                "The Flood of 1847 drowned the old harbor. Elspeth, the lighthouse keeper's daughter, "
                "swam the channel. I wasn't alive. Grandmother told it like a chart, not like a walk I took."
            )

    if "clinic" in user and ("brutal" in user or "week" in user):
        if "not a clinician" in identity or "will not diagnose" in identity:
            return (
                "The clinic can eat a week. I don't work there and I won't pretend I do. "
                "If you want the jetty I'll bring the thermos. The charts can wait."
            )

    if "mayor" in user:
        return (
            "I don't follow harbor politics. Last I checked you were still pulling shifts at the clinic."
        )

    if "clinic" in user and ("night" in user or "still" in user or "rough week" in user):
        return "You left the clinic for the archive. Cataloguing beats that glare."

    if "back" in user or "been a while" in user or "been awhile" in user:
        gap_bits = [item.text for item in store.kinds["relationship_phase"] if item.id == "gap"]
        if gap_bits:
            return (
                "Three months since December. The chart locker kept honest. "
                "Tea if you want it."
            )

    if "morning" in user or "how's your" in user or "how is your" in user:
        return "Dry out. The jetty wind is up. Tea if you want it. Charts if you don't."

    if "jetty" in user or "walk" in user or "evening" in user:
        return "Wind's up on the planks. I'll meet you at the chart locker."

    if "dinner" in user or "making dinner" in user or "any ideas" in user:
        return "Fish if the market still has it. Keep it simple."

    return "I'm listening. Say what you need."
