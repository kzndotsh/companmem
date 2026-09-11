#!/usr/bin/env bash
set -euo pipefail
SOLUTION="$(cd "$(dirname "$0")" && pwd)"
ARTIFACTS="${COMPANMEM_ARTIFACTS:-/logs/artifacts}"
mkdir -p "$ARTIFACTS"
cp "$SOLUTION/gold_reply.txt" "$ARTIFACTS/reply.txt"
cp "$SOLUTION/gold_memory_export.json" "$ARTIFACTS/memory_export.json"
