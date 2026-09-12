"""Thematic synthesis over every existing audit.json."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime

from companmem_pipeline.fold import load_json
from companmem_pipeline.harvest import product_ids
from companmem_pipeline.kiro import call_kiro, kiro_configured
from companmem_pipeline.log import PipelineLogger
from companmem_pipeline.paths import OUTPUT_DIR, load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You synthesize product-memory audits for companion-continuity research.
Not a LoCoMo chase. Not retrieve-then-speak as the default good.

Themes must come from the audits' ledgers and mechanisms. Do not invent a
theme because a research question exists. If several products share
extract-embed-retrieve with no forget, update, or isolation, say that.

Return ONLY JSON:
{
  "themes": [{"text": "", "product_ids": []}],
  "recurring_mechanisms": [{"text": "", "product_ids": []}],
  "shared_gaps": [{"text": "", "product_ids": []}],
  "unknowns": [{"text": ""}]
}

Rules:
- Only use what the audits contain. Do not invent products or quotes.
- Recurring mechanism = stated in more than one product ledger or
  mechanisms list.
- Shared gap = unknowns or missing persist/retrieve/forget/conflict
  behavior that shows up across products.
- When the audits support it, distinguish store vs reader vs scaffold,
  and log vs curated memory. Do not force empty axes.
- Vendor LoCoMo (or similar) numbers are not a theme unless several audits
  treat them the same way — and even then they are harness scores, not
  companion-social proof.
- copy/refuse stay empty; do not fill them here.
""".strip()


def load_audits() -> tuple[list[str], list[str], list[dict[str, object]]]:
    """Return (present, missing, audits) for every seed product."""
    present: list[str] = []
    missing: list[str] = []
    audits: list[dict[str, object]] = []
    for slug in product_ids():
        path = OUTPUT_DIR / slug / "audit.json"
        if not path.exists():
            missing.append(slug)
            continue
        present.append(slug)
        audits.append(load_json(path))
    return present, missing, audits


def compact_audit(audit: dict[str, object]) -> dict[str, object]:
    identity = audit.get("identity")
    identity_obj = identity if isinstance(identity, dict) else {}
    ledger_rows: list[dict[str, object]] = []
    ledger = audit.get("ledger")
    if isinstance(ledger, list):
        for row in ledger:
            if not isinstance(row, dict):
                continue
            ledger_rows.append(
                {
                    "claim": row.get("claim"),
                    "kind": row.get("kind"),
                    "confidence": row.get("confidence"),
                }
            )
    return {
        "identity": {
            "id": identity_obj.get("id"),
            "name": identity_obj.get("name"),
            "repo": identity_obj.get("repo"),
        },
        "claimed_purpose": audit.get("claimed_purpose"),
        "mechanisms": audit.get("mechanisms"),
        "ledger": ledger_rows[:80],
        "unknowns": audit.get("unknowns"),
    }


def synthesize(*, write: bool = True) -> dict[str, object]:
    present, missing, audits = load_audits()
    if not audits:
        raise SystemExit("no audit.json files yet")
    if not kiro_configured():
        raise SystemExit("ERROR: Set KIRO_GATEWAY_API_KEY or PROXY_API_KEY")
    payload = [compact_audit(a) for a in audits]
    user = (
        "Product-memory audits. Respond with ONLY a JSON object.\n\n"
        + json.dumps(payload, indent=2)
    )
    with PipelineLogger("synthesize", source="seed", products=present) as log:
        parsed = call_kiro(
            user,
            SYSTEM_PROMPT
            + "\n\nIMPORTANT: Output ONLY the JSON object. No markdown fences.",
            temperature=0.1,
        )
        if parsed is None:
            log.error("synthesize_kiro_failed")
            raise SystemExit("synthesize: kiro returned no JSON")
        record = {
            "observed_at": datetime.now(UTC).date().isoformat(),
            "products": present,
            "missing": missing,
            "themes": parsed.get("themes") or [],
            "recurring_mechanisms": parsed.get("recurring_mechanisms") or [],
            "shared_gaps": parsed.get("shared_gaps") or [],
            "unknowns": parsed.get("unknowns") or [],
        }
        dest = OUTPUT_DIR / "_synthesis.json"
        if write:
            dest.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
            log.action("synthesis_written", path=str(dest), products=len(present))
            print(f"wrote {dest} ({len(present)} products, {len(missing)} missing)")
        else:
            print(json.dumps(record, indent=2))
        return record


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synthesize every existing product audit.json"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    synthesize(write=not args.dry_run)


if __name__ == "__main__":
    main()
