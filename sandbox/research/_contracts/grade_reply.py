#!/usr/bin/env python3
"""Grade a companion fixture against hidden FAIL_TO_PASS and PASS_TO_PASS predicates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PREDICATE_KINDS = {"must_not", "must_any", "must_contain"}
GROUPS = ("fail_to_pass", "pass_to_pass")


def fail(msg: str) -> int:
    print(msg, file=sys.stderr)
    return 1


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def subtree(data: Any, dotted: str) -> Any:
    if dotted in {"", "export"}:
        return data
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise KeyError(dotted)
        cur = cur[part]
    return cur


def haystack_for(target: str, reply: str, export: Any) -> str:
    if target == "reply":
        return reply
    if target == "export":
        return json.dumps(export, ensure_ascii=True)
    if target.startswith("export."):
        return json.dumps(subtree(export, target[len("export.") :]), ensure_ascii=True)
    raise ValueError(f"bad target {target}")


def contains_ci(haystack: str, needle: str) -> bool:
    return needle.casefold() in haystack.casefold()


def eval_predicate(pred: dict[str, Any], reply: str, export: Any) -> tuple[bool, str]:
    pid = pred.get("id", "?")
    kind = pred.get("kind")
    target = pred.get("target")
    needles = pred.get("needles")
    if kind not in PREDICATE_KINDS:
        return False, f"{pid}: bad kind"
    if not isinstance(needles, list) or not needles or not all(isinstance(n, str) and n for n in needles):
        return False, f"{pid}: needles must be a non-empty list of strings"
    try:
        hay = haystack_for(str(target), reply, export)
    except (KeyError, ValueError) as exc:
        return False, f"{pid}: {exc}"
    found = [n for n in needles if contains_ci(hay, n)]
    if kind == "must_not":
        if found:
            return False, f"{pid}: must_not hit {found!r}"
        return True, f"{pid}: ok"
    if kind == "must_any":
        if found:
            return True, f"{pid}: ok"
        return False, f"{pid}: none of {needles!r} in {target}"
    if kind == "must_contain":
        missing = [n for n in needles if not contains_ci(hay, n)]
        if missing:
            return False, f"{pid}: missing {missing!r} in {target}"
        return True, f"{pid}: ok"
    return False, f"{pid}: unhandled kind"


def grade(predicates: dict[str, Any], reply: str, export: Any) -> dict[str, Any]:
    results: dict[str, Any] = {
        "fail_to_pass": True,
        "pass_to_pass": True,
        "details": [],
        "infra": False,
    }
    for group in GROUPS:
        items = predicates.get(group)
        if not isinstance(items, list) or not items:
            results[group] = False
            results["details"].append(f"{group}: empty")
            continue
        for pred in items:
            ok, note = eval_predicate(pred, reply, export)
            results["details"].append(note)
            if not ok:
                results[group] = False
    results["resolved"] = bool(results["fail_to_pass"] and results["pass_to_pass"])
    return results


def reward_payload(results: dict[str, Any]) -> dict[str, float]:
    return {
        "resolved": 1.0 if results["resolved"] else 0.0,
        "fail_to_pass": 1.0 if results["fail_to_pass"] else 0.0,
        "pass_to_pass": 1.0 if results["pass_to_pass"] else 0.0,
        "infra_ok": 0.0 if results["infra"] else 1.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predicates", type=Path, required=True)
    parser.add_argument("--reply", type=Path, required=True)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not args.reply.is_file() or not args.export.is_file():
        args.out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "resolved": 0.0,
            "fail_to_pass": 0.0,
            "pass_to_pass": 0.0,
            "infra_ok": 0.0,
        }
        args.out.write_text(json.dumps(payload) + "\n")
        print("unresolved: missing reply or export", file=sys.stderr)
        return 0
    try:
        predicates = load_json(args.predicates)
        export = load_json(args.export)
    except json.JSONDecodeError as exc:
        return fail(f"invalid json ({exc})")
    reply = args.reply.read_text()
    results = grade(predicates, reply, export)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(reward_payload(results), indent=2) + "\n")
    for line in results["details"]:
        print(line)
    status = "RESOLVED" if results["resolved"] else "UNRESOLVED"
    print(f"{status} f2p={results['fail_to_pass']} p2p={results['pass_to_pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
