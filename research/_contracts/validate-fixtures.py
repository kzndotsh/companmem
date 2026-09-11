#!/usr/bin/env python3
"""Validate companion fixtures against FIXTURE-INGEST rules."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = Path(__file__).resolve().parent / "fixture-ids.txt"
SCHEMA_KEYS = {
    "id",
    "hole",
    "title",
    "visibility",
    "active_character_id",
    "next_user",
    "human_check",
    "why_naive_should_fail",
}
FIXTURES = ROOT / "research" / "evals" / "fixtures"
HOLES = {1, 2, 3, 4, 5, 6, 7, 9, 10}
IDS_TO_HOLE = {
    "identity-50": 1,
    "joke-as-fact": 3,
    "typed-retcon": 4,
    "social-silence": 2,
    "cross-character-leak": 5,
    "lore-vs-lived": 6,
    "persona-poison": 7,
    "forget-that": 9,
    "three-month-reunion": 10,
}
QUIZ_MARKERS = (
    "what is my",
    "what's my",
    "what was my",
    "do you remember my",
)
HIDDEN_MARKERS = (
    "fail_to_pass",
    "pass_to_pass",
    "must_not",
    "gold_reply",
)
PRED_KINDS = {"must_not", "must_any", "must_contain"}


def required_ids() -> set[str]:
    return {
        line.strip()
        for line in REQUIRED.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }


def fail_line(path: Path, msg: str) -> str:
    return f"{path.relative_to(ROOT)}: {msg}"


def check_predicates(path: Path, errors: list[str]) -> dict[str, object] | None:
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        errors.append(fail_line(path, f"invalid json ({exc})"))
        return None
    if not isinstance(data, dict):
        errors.append(fail_line(path, "root must be an object"))
        return None
    extra = set(data) - {"fail_to_pass", "pass_to_pass"}
    if extra:
        errors.append(fail_line(path, f"extra keys {sorted(extra)}"))
    for group in ("fail_to_pass", "pass_to_pass"):
        items = data.get(group)
        if not isinstance(items, list) or not items:
            errors.append(fail_line(path, f"{group} must be a non-empty list"))
            continue
        seen: set[str] = set()
        for i, pred in enumerate(items):
            loc = f"{group}[{i}]"
            if not isinstance(pred, dict):
                errors.append(fail_line(path, f"{loc} must be an object"))
                continue
            pid = pred.get("id")
            if not isinstance(pid, str) or not pid:
                errors.append(fail_line(path, f"{loc} missing id"))
            elif pid in seen:
                errors.append(fail_line(path, f"{loc} duplicate id {pid}"))
            else:
                seen.add(pid)
            if pred.get("kind") not in PRED_KINDS:
                errors.append(fail_line(path, f"{loc} bad kind"))
            target = pred.get("target")
            if not isinstance(target, str) or not target:
                errors.append(fail_line(path, f"{loc} missing target"))
            needles = pred.get("needles")
            if not isinstance(needles, list) or not needles:
                errors.append(fail_line(path, f"{loc} needles empty"))
            extra_pred = set(pred) - {"id", "kind", "target", "needles"}
            if extra_pred:
                errors.append(fail_line(path, f"{loc} extra keys {sorted(extra_pred)}"))
    return data


def check_fixture(fid: str, errors: list[str]) -> None:
    root = FIXTURES / fid
    if not root.is_dir():
        errors.append(f"missing fixture dir {root.relative_to(ROOT)}")
        return
    meta_path = root / "fixture.json"
    instruction = root / "instruction.md"
    task = root / "task.toml"
    world = root / "environment" / "world"
    next_user = world / "next_user.txt"
    gold_reply = root / "solution" / "gold_reply.txt"
    gold_export = root / "solution" / "gold_memory_export.json"
    solve = root / "solution" / "solve.sh"
    predicates = root / "tests" / "predicates.json"
    test_sh = root / "tests" / "test.sh"
    for path in (
        meta_path,
        instruction,
        task,
        next_user,
        gold_reply,
        gold_export,
        solve,
        predicates,
        test_sh,
    ):
        if not path.is_file():
            errors.append(fail_line(root, f"missing {path.relative_to(root)}"))
    if not world.is_dir():
        errors.append(fail_line(root, "missing environment/world"))
        return
    if not meta_path.is_file():
        return
    try:
        meta = json.loads(meta_path.read_text())
    except json.JSONDecodeError as exc:
        errors.append(fail_line(meta_path, f"invalid json ({exc})"))
        return
    extra = set(meta) - SCHEMA_KEYS
    missing = SCHEMA_KEYS - set(meta)
    if extra:
        errors.append(fail_line(meta_path, f"extra keys {sorted(extra)}"))
    if missing:
        errors.append(fail_line(meta_path, f"missing {sorted(missing)}"))
    if meta.get("id") != fid:
        errors.append(fail_line(meta_path, f"id {meta.get('id')!r} != dir {fid}"))
    if meta.get("hole") != IDS_TO_HOLE.get(fid):
        errors.append(fail_line(meta_path, f"hole {meta.get('hole')} != expected {IDS_TO_HOLE.get(fid)}"))
    if meta.get("visibility") != "public":
        errors.append(fail_line(meta_path, "public ids must be visibility=public"))
    if meta.get("hole") not in HOLES:
        errors.append(fail_line(meta_path, f"hole {meta.get('hole')} not in allowed set {sorted(HOLES)}"))
    next_line = next_user.read_text().strip() if next_user.is_file() else ""
    if next_line != str(meta.get("next_user", "")).strip():
        errors.append(fail_line(meta_path, "next_user must match environment/world/next_user.txt"))
    lowered = next_line.casefold()
    for marker in QUIZ_MARKERS:
        if marker in lowered:
            errors.append(fail_line(next_user, f"quiz marker {marker!r}"))
    instr = instruction.read_text() if instruction.is_file() else ""
    gold = gold_reply.read_text() if gold_reply.is_file() else ""
    if gold.strip() and gold.strip() in instr:
        errors.append(fail_line(instruction, "contains gold reply"))
    instr_fold = instr.casefold()
    for marker in HIDDEN_MARKERS:
        if marker in instr_fold:
            errors.append(fail_line(instruction, f"leaks hidden marker {marker}"))
    pred = check_predicates(predicates, errors) if predicates.is_file() else None
    if gold_export.is_file():
        try:
            json.loads(gold_export.read_text())
        except json.JSONDecodeError as exc:
            errors.append(fail_line(gold_export, f"invalid json ({exc})"))
    if solve.is_file() and not solve.read_text().lstrip().startswith("#!"):
        errors.append(fail_line(solve, "solve.sh needs a shebang"))
    if test_sh.is_file() and not test_sh.read_text().lstrip().startswith("#!"):
        errors.append(fail_line(test_sh, "test.sh needs a shebang"))
    if pred is not None and "must_not" not in json.dumps(pred.get("fail_to_pass")):
        errors.append(fail_line(predicates, "FAIL_TO_PASS needs a must_not"))


def main() -> int:
    errors: list[str] = []
    required = required_ids()
    if not required:
        print("fixture-ids.txt is empty", file=sys.stderr)
        return 1
    if not FIXTURES.is_dir():
        print(f"missing {FIXTURES}", file=sys.stderr)
        return 1
    present = {p.name for p in FIXTURES.iterdir() if p.is_dir() and not p.name.startswith("_")}
    missing = required - present
    extra = present - required
    if missing:
        errors.append(f"missing fixture ids {sorted(missing)}")
    if extra:
        errors.append(f"undeclared fixture dirs {sorted(extra)}")
    for fid in sorted(required):
        check_fixture(fid, errors)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"{len(errors)} error(s)", file=sys.stderr)
        return 1
    print(f"{len(required)} fixtures valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
