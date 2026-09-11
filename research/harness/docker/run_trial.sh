#!/usr/bin/env bash
# Run one script baseline trial in docker. Agent never sees predicates.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
COMPOSE_FILE="$ROOT/research/harness/docker/compose.yml"
BASELINE="$1"
FIXTURE_ID="$2"
FIXTURE="$ROOT/research/evals/fixtures/$FIXTURE_ID"
export TRIAL_DIR
TRIAL_DIR="$(mktemp -d)"
trap 'rm -rf "$TRIAL_DIR"' EXIT

cp -a "$FIXTURE/environment/world" "$TRIAL_DIR/world"
cp "$FIXTURE/tests/predicates.json" "$TRIAL_DIR/predicates.json"
mkdir -p "$TRIAL_DIR/artifacts" "$TRIAL_DIR/out"

SCRIPT=""
case "$BASELINE" in
  naive-retrieve) SCRIPT=/app/research/evals/baselines/naive-retrieve/run.py ;;
  long-context-stuff) SCRIPT=/app/research/evals/baselines/long-context-stuff/run.py ;;
  naive-rag) SCRIPT=/app/research/evals/baselines/naive-rag/run.py ;;
  *)
    echo "docker trial: baseline $BASELINE not wired" >&2
    exit 2
    ;;
esac

docker compose -f "$COMPOSE_FILE" run --rm --no-deps -e TRIAL_DIR="$TRIAL_DIR" agent \
  python "$SCRIPT" --world /work/world --artifacts /work/artifacts

docker compose -f "$COMPOSE_FILE" run --rm --no-deps -e TRIAL_DIR="$TRIAL_DIR" verifier \
  python /app/grade_reply.py \
  --predicates /predicates.json \
  --reply /work/artifacts/reply.txt \
  --export /work/artifacts/memory_export.json \
  --out /work/out/reward.json

cat "$TRIAL_DIR/out/reward.json"
