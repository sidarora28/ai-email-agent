#!/usr/bin/env bash
# STEP 1 — fetch new emails from the inbox into data/inbound.jsonl
set -e; cd "$(dirname "$0")"; source .venv/bin/activate 2>/dev/null || true
export PYTHONWARNINGS=ignore ANONYMIZED_TELEMETRY=False GRPC_VERBOSITY=NONE TOKENIZERS_PARALLELISM=false
python m2_classify/fetch_unread.py
