#!/usr/bin/env bash
set -euo pipefail
TESTS="$(cd "$(dirname "$0")" && pwd)"
RESEARCH="$(cd "$TESTS/../../../../.." && pwd)"
ARTIFACTS="${COMPANMEM_ARTIFACTS:-/logs/artifacts}"
OUT="${COMPANMEM_REWARD:-/logs/verifier/reward.json}"
mkdir -p "$(dirname "$OUT")"
python3 "$RESEARCH/_contracts/grade_reply.py" \
  --predicates "$TESTS/predicates.json" \
  --reply "$ARTIFACTS/reply.txt" \
  --export "$ARTIFACTS/memory_export.json" \
  --out "$OUT"
