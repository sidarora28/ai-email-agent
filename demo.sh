#!/usr/bin/env bash
# Live demo runner — triage the inbox and draft+review replies, streamed on screen.
#
#   bash demo.sh           # use the emails already in data/inbound.jsonl
#   bash demo.sh --live    # first pull fresh unread inbox (audience emails)
#
# Keeps the terminal clean for a projector (no warnings / telemetry noise).
set -e
cd "$(dirname "$0")"
source .venv/bin/activate 2>/dev/null || true

export PYTHONWARNINGS=ignore
export ANONYMIZED_TELEMETRY=False
export GRPC_VERBOSITY=NONE
export TOKENIZERS_PARALLELISM=false

if [ "$1" = "--live" ]; then
  python m2_classify/fetch_unread.py
fi

python m2_classify/classify.py
python m3_engine/engine.py
