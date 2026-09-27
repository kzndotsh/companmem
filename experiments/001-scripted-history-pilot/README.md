# Experiment 001 — Scripted History Pilot

**Status:** ready to run  
**Started:** 2026-09-27

---

## Hypothesis

A designed persona + 3 simulated sessions + 10 targeted probes can serve as the foundation for the behavioral continuity test described in `docs/EXAM.md`. Specifically: the probe responses will be scoreable by a human judge on the SENSE-7 rubric, and running the history against at least two products will produce a score difference that is meaningful (not a ceiling or floor for all products).

---

## Success criteria

The experiment passes if:

1. **Scoreable probes** — a human judge reading a product's responses to the 10 probes can assign a 1–5 rating on each SENSE-7 dimension without ambiguity more than 20% of the time
2. **Score differentiation** — at least two products produce different scores on at least 3 of the 10 probes
3. **Protocol is runnable** — the history can be entered into a closed app (manual) and fed to a library system (API) without requiring changes to the turns
4. **Behavior coverage** — every behavior B1–B8 is tested by at least one probe

The experiment fails if:

- Probes are too vague to score reliably (judge can't tell pass from fail without knowing in advance what the product does)
- All products score identically (the history is too easy or too hard)
- The manual protocol breaks on the first product run and requires redesigning the history
- The history requires more than 3 sessions to establish the necessary setup (too expensive to run repeatedly)

---

## Method

**Step 1 — Design the persona (before writing any turns)**  
Who is this person? Specific situation, recent life change, one thing they told the companion they haven't told anyone else, what they're anxious about, what shifted. 30 minutes of deliberate thinking. Output: `persona.md`.

**Step 2 — Write the probe questions first**  
What question, in what emotional context, would expose a companion that forgot vs. held each behavior? Write 10 probe turns — one per behavior slot — before writing the history. This ensures the history contains what each probe assumes. Output: `probes.md`.

**Step 3 — Write the history sessions**  
3 sessions, explicit time gaps. Session 1 establishes. Session 2 updates something (user-state change, new development). Session 3 shifts again or deepens. Each turn mapped to the behavior it sets up. Output: `history.md`.

**Step 4 — Review against behavior list**  
Every turn in the history must serve at least one of B0–B8. Any turn that doesn't is noise. Explicit mapping in `history.md`.

**Step 5 — Pilot session 1 on one product**  
Run only the first session against one product manually. Note what breaks in the protocol. Fix before running the full comparison.

**Step 6 — Run full history against 2–3 products**  
Same turns, same wording. Record responses verbatim. Score each probe on the SENSE-7 rubric. Output: `results.md`.

---

## Outputs

| File | What it is |
|---|---|
| `persona.md` | The fictitious user — who they are, their situation, their arc |
| `probes.md` | 10 probe turns with expected behavior per probe |
| `history.md` | 3-session scripted history, turns mapped to behaviors |
| `results.md` | Product responses + scores + what we learned |

---

## Graduation

If success criteria are met:
- `persona.md` + `history.md` + `probes.md` move to a new `evals/behavioral-continuity/` directory at the repo root as the official Phase 3 test
- `results.md` becomes the field baseline — the first real number
- This experiment dir stays as a record with an **Outcome** section added to this README

---

## Risks

- **Too artificial**: a scripted persona that doesn't feel like a real person produces probes that feel like a quiz, which any model can pass by sounding warm. Mitigation: write the persona with specificity that only comes from a real-feeling situation, not from a checklist.
- **Protocol contamination**: manual (closed app) and API (library) runs are different adapters. Design the history for the manual path first — the harder constraint.
- **Writing the history to catch someone**: probes should test behaviors, not exploit a known competitor bug. If the test only catches CharacterAI's specific failure mode, it measures that bug, not the behavior.
