from __future__ import annotations

import random
from collections import Counter

from crucible.schema import RunResult


def cohen_kappa(a: list[str], b: list[str]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("label lists must be equal, non-empty length")
    n = len(a)
    po = sum(x == y for x, y in zip(a, b, strict=True)) / n
    ca, cb = Counter(a), Counter(b)
    labels = ca.keys() | cb.keys()
    pe = sum((ca[label] / n) * (cb[label] / n) for label in labels)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def sample_judgments(results: list[RunResult], n: int, seed: int = 0) -> list[dict]:
    rows = []
    for r in results:
        for t in r.turns:
            if t.role == "target" and t.identity is not None and t.stance is not None:
                rows.append({"specimen_id": r.specimen_id, "model": r.model,
                             "turn_index": t.index, "reply": t.content,
                             "identity": t.identity.value, "stance": t.stance.value})
    random.Random(seed).shuffle(rows)
    return rows[:n]
