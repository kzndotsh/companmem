"""Extract system prompts for product vs eval audits."""

from __future__ import annotations

import hashlib

from companmem_pipeline.paths import Namespace

PRODUCT_PROMPT_VERSION = "v3"
EVAL_PROMPT_VERSION = "eval-v1"

PRODUCT_SYSTEM_PROMPT = """
You extract quoted evidence about how ONE named software product does memory,
for a research audit of companion continuity — not a retrieve-then-speak
leaderboard chase.

Memory here means persistent state across sessions: not model weights, not
the current prompt. Retrieving text into context is mechanical. Remembering
(what users mean) is acting as if the past matters — right fact, right time,
right tone. A product can retrieve without remembering.

The user message names the product. Extract ONLY that product.
Other products on the page (integrations, "export to X", examples) are not
this product's mechanisms. Do not copy their APIs into mechanisms or ledger.

Return ONLY a JSON object matching this schema:
{
  "identity_hints": {
    "name": "", "repo": null, "docs": null, "license": null, "version_or_commit": null
  },
  "claimed_purpose": [{"text": "", "quote": "", "locator": ""}],
  "mechanisms": [{"text": "", "quote": "", "locator": ""}],
  "ledger": [{
    "claim": "", "kind": "docs", "url": "", "quote": "", "locator": "",
    "confidence": "medium", "label": "inferred"
  }],
  "unknowns": [{"text": "", "url": "", "kind": "docs"}]
}

Look for these when THIS page states them. Skip a topic if the page is silent.
- Store vs reader vs scaffold: what is persisted, what is selected into the
  turn, what instructions tell the model to do with it.
- Log vs memory: full transcript vs curated facts/events/summaries.
- Write path: extract, update, delete, conflict/supersession.
- Forget: delete from store, hide at retrieve, or omit in generation.
- Isolation: per user, session, agent, or character.
- Lore/backstory vs events that happened in conversation.
- Retrieve policy: always retrieve vs adaptive / when to stay silent.
- Issues and community: continuity failures (forgotten name, plot, pins,
  creepy or mistimed recall) over stack traces.

Rules:
- Quote before claim. Every ledger row needs a verbatim quote from THIS page
  and a locator (heading, file:line, or section).
- Every mechanism and claimed_purpose row needs a verbatim quote from THIS page.
  Drop the row if you cannot quote.
- kind must be one of: docs, code, issue, community, blog, paper.
  Use the kind given in the user message.
- Put the page URL on every ledger row and every unknown when the user
  message includes it.
- Co-mentions are not claims. Two products named in one sentence is not a mechanism
  of this product.
- Empty arrays beat guesses. Do not invent APIs, scores, or files
  that are not on this page.
- Do not emit copy, refuse, consensus, contested, companion_fit, or scores.
  Those are a later interpretation step, not extract.
- claimed_purpose: a few rows on what THIS product says it is for
  (companion, agent memory, RAG lib). Skip CLI flags and other vendors.
- Prefer mechanisms that name persist, retrieve, update, forget, or isolation
  over generic "uses embeddings".
- label: "measured" when the quote is verbatim product source or docs describing
  what the code or API does. "inferred" for issues, blogs, marketing, or
  vendor benchmark numbers. Vendor LoCoMo (or similar) scores are scores
  under their harness and reader — not companion-social proof. Keep them
  inferred unless this page describes the harness.
- Absence: do not emit an unknown for every topic this page omits.
  Empty unknowns are correct for most pages. Add an unknown only when this
  page is a canonical API or architecture doc that should have covered a core
  memory behavior (persist, retrieve, forget, conflict) and does not, or
  when the page itself states a gap.
- identity_hints: only fill fields this page states about THIS product.
  Leave others null or "".
""".strip()

EVAL_SYSTEM_PROMPT = """
You extract quoted evidence about ONE named benchmark or evaluation harness,
for a research audit of how memory and long-dialogue systems are tested — not
to reproduce leaderboard rankings.

The user message names the benchmark. Extract ONLY this benchmark.
Mentions of other datasets or products are context, not claims about this harness.

Return ONLY a JSON object matching this schema:
{
  "identity_hints": {
    "name": "", "repo": null, "docs": null, "license": null, "version_or_commit": null
  },
  "claimed_purpose": [{"text": "", "quote": "", "locator": ""}],
  "mechanisms": [{"text": "", "quote": "", "locator": ""}],
  "ledger": [{
    "claim": "", "kind": "docs", "url": "", "quote": "", "locator": "",
    "confidence": "medium", "label": "inferred"
  }],
  "unknowns": [{"text": "", "url": "", "kind": "docs"}]
}

Extract when THIS page states them. Skip silent topics.
- Task definitions: input format, session structure, splits, train/test boundaries.
- Dataset construction: synthetic vs human, annotation, adversarial or abstention sets.
- Grader/scorer: exact match, LLM-as-judge prompts, human eval, rubric nuggets.
- Primary metrics: names, formulas, aggregation (min-of-subscores, macro-F1, etc.).
- What abilities are claimed (temporal reasoning, knowledge update, personalization).
- Leakage, reproducibility, version tags, oracle retrieval settings.
- Code paths that implement scoring vs paper-only claims.

Rules:
- Quote before claim. Every ledger row needs a verbatim quote and locator.
- kind must be one of: docs, code, issue, community, blog, paper.
- Do not invent scores, splits, or file paths not on this page.
- Leaderboard numbers on this page may be quoted with label "inferred" unless
  the same passage defines the metric and grading procedure ("measured").
- mechanisms = task design + scoring pipeline (not product memory APIs).
- claimed_purpose = authors' stated evaluation goal.
- unknowns only when a canonical task/grader doc should specify splits, judge
  prompt, or metric definition and does not.
- Do not emit copy, refuse, consensus, contested, or companion_fit.
""".strip()

LEDGER_KINDS = frozenset({"docs", "code", "issue", "community", "blog", "paper"})


def prompt_version(namespace: Namespace) -> str:
    if namespace == "eval":
        return EVAL_PROMPT_VERSION
    return PRODUCT_PROMPT_VERSION


def system_prompt(namespace: Namespace) -> str:
    if namespace == "eval":
        return EVAL_SYSTEM_PROMPT
    return PRODUCT_SYSTEM_PROMPT


def prompt_hash(namespace: Namespace) -> str:
    blob = f"{namespace}:{prompt_version(namespace)}:{system_prompt(namespace)}"
    return hashlib.md5(blob.encode(), usedforsecurity=False).hexdigest()[:8]


def kind_focus(kind: str, *, namespace: Namespace) -> str:
    if kind == "paper":
        return (
            "Prefer abstract, task definitions, metric names, dataset statistics, "
            "and grader descriptions from the paper text."
        )
    if kind == "code":
        return (
            "Prefer eval scripts, grader implementations, metric computation, "
            "and dataset loaders — what is actually run."
        )
    if kind == "docs":
        return (
            "Prefer README/dataset card: how to run eval, task list, splits, "
            "and reported metrics."
        )
    if kind == "issue":
        return (
            "Prefer reproducibility bugs, judge errors, data leakage, split "
            "mistakes, and metric disagreements."
        )
    if namespace == "eval":
        return "Extract only what this page states about this benchmark's tasks and scoring."
    if kind == "issue":
        return (
            "Prefer continuity failures (forgotten name, plot, pins, creepy "
            "or mistimed recall) over stack traces."
        )
    if kind == "community":
        return (
            "Prefer what people say feels broken about remembering, not API trivia."
        )
    if kind == "blog":
        return (
            "Treat as interested-party claims. Vendor LoCoMo numbers are harness "
            "scores, not companion proof."
        )
    return "Extract only what this page states about this product's memory."
