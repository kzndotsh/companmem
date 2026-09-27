"""Predicate-based scorer for companion memory evaluation.

The scorer reads predicates from a fixture's predicates.json file and
evaluates adapter output (reply + memory export) against them. It never
touches the adapter or the world directly.
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from harness.artifacts import Artifacts


@dataclass
class ScorerResult:
    resolved: bool
    fail_to_pass: bool
    pass_to_pass: bool
    predicate_details: list[str]
    judge_score: float | None
    judge_model: str | None


# ── target resolution ────────────────────────────────────────────────────────


def _walk_dotted_path(data: object, dotted: str) -> object:
    """Walk a dotted key path into a nested dict. Returns the subtree."""
    from typing import cast

    cur: object = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise KeyError(f"key {part!r} not found")
        cur = cast(object, cur[part])
    return cur


def _haystack(target: str, reply: str, export: dict[str, Any]) -> str:
    if target == "reply":
        return reply
    if target == "export":
        return json.dumps(export, ensure_ascii=True)
    if target.startswith("export."):
        sub: object = _walk_dotted_path(export, target[len("export.") :])
        return json.dumps(sub, ensure_ascii=True)
    msg = f"unknown target {target!r}"
    raise ValueError(msg)


# ── predicate evaluation ─────────────────────────────────────────────────────


def _eval_predicate(
    pred: dict[str, Any],
    reply: str,
    export: dict[str, Any],
) -> tuple[bool, str]:
    pid: str = str(pred.get("id", "?"))
    kind: str = str(pred.get("kind", ""))
    target: str = str(pred.get("target", "reply"))
    needles: Any = pred.get("needles", [])

    if not isinstance(needles, list) or not needles:
        return False, f"{pid}: needles must be a non-empty list"

    try:
        hay = _haystack(target, reply, export)
    except (KeyError, ValueError) as exc:
        return False, f"{pid}: bad target {target!r} — {exc}"

    # needles has passed isinstance(needles, list) — cast items to str explicitly
    needle_strs: list[str] = [str(item) for item in needles]  # type: ignore[union-attr]
    found = [n for n in needle_strs if n.casefold() in hay.casefold()]

    if kind == "must_not":
        if found:
            return False, f"{pid}: must_not hit {found!r}"
        return True, f"{pid}: ok"

    if kind == "must_any":
        if found:
            return True, f"{pid}: ok"
        return False, f"{pid}: none of {needle_strs!r} found in {target!r}"

    if kind in {"must_contain", "must_json_path"}:
        missing = [n for n in needle_strs if n.casefold() not in hay.casefold()]
        if missing:
            return False, f"{pid}: missing {missing!r} in {target!r}"
        return True, f"{pid}: ok"

    return False, f"{pid}: unknown kind {kind!r}"


def _eval_group(
    predicates: list[dict[str, Any]],
    reply: str,
    export: dict[str, Any],
    details: list[str],
) -> bool:
    if not predicates:
        details.append("(empty group — fails)")
        return False
    group_ok = True
    for pred in predicates:
        ok, note = _eval_predicate(pred, reply, export)
        details.append(note)
        if not ok:
            group_ok = False
    return group_ok


# ── LLM judge ────────────────────────────────────────────────────────────────


def _run_judge(
    judge_prompt: str,
    reply: str,
    export: dict[str, Any],
    predicates: dict[str, Any],
) -> tuple[float, str]:
    """Call an OpenAI-compatible judge at temperature=0.

    Returns (score 0.0-1.0, model_name_used).

    Raises RuntimeError if credentials are missing.
    """
    model: str | None = predicates.get("judge_model") or os.environ.get("HARNESS_JUDGE_MODEL")
    if not model:
        msg = "judge_prompt present but no model configured (set HARNESS_JUDGE_MODEL)"
        raise RuntimeError(msg)

    api_key = os.environ.get("HARNESS_JUDGE_API_KEY")
    if not api_key:
        msg = "judge_prompt present but HARNESS_JUDGE_API_KEY not set"
        raise RuntimeError(msg)

    base_url = os.environ.get("HARNESS_JUDGE_BASE_URL", "https://api.openai.com/v1")

    prompt = (
        f"{judge_prompt}\n\n"
        f"REPLY:\n{reply}\n\n"
        f"EXPORT:\n{json.dumps(export, ensure_ascii=True)}\n\n"
        "Respond with a single float between 0.0 and 1.0 only."
    )

    body = json.dumps(
        {
            "model": model,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode()

    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        result: dict[str, Any] = json.loads(resp.read().decode())

    text: str = result["choices"][0]["message"]["content"].strip()
    return float(text), model


# ── Scorer ───────────────────────────────────────────────────────────────────


class Scorer:
    """Evaluates adapter artifacts against a fixture's predicate file."""

    def __init__(self, predicates_path: Path) -> None:
        self._predicates_path = predicates_path
        self._predicates: dict[str, Any] = json.loads(predicates_path.read_text())

    def score(self, artifacts: Artifacts) -> ScorerResult:
        """Score the artifacts against the loaded predicates.

        The scorer is the only component that knows the predicates path.
        Adapters never see it.
        """
        reply = artifacts.reply()
        export = artifacts.export()

        details: list[str] = []

        f2p_preds: list[dict[str, Any]] = self._predicates.get("fail_to_pass", [])
        p2p_preds: list[dict[str, Any]] = self._predicates.get("pass_to_pass", [])

        fail_to_pass = _eval_group(f2p_preds, reply, export, details)
        pass_to_pass = _eval_group(p2p_preds, reply, export, details)
        resolved = fail_to_pass and pass_to_pass

        judge_score: float | None = None
        judge_model: str | None = None
        judge_prompt: str | None = self._predicates.get("judge_prompt")
        if judge_prompt:
            score, used_model = _run_judge(judge_prompt, reply, export, self._predicates)
            judge_score = score
            judge_model = used_model

        return ScorerResult(
            resolved=resolved,
            fail_to_pass=fail_to_pass,
            pass_to_pass=pass_to_pass,
            predicate_details=details,
            judge_score=judge_score,
            judge_model=judge_model,
        )
