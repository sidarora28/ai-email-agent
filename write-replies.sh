#!/usr/bin/env bash
# STEP 3 — writer drafts each reply in Sid's voice, reviewer checks it
set -e; cd "$(dirname "$0")"; source .venv/bin/activate 2>/dev/null || true
export PYTHONWARNINGS=ignore ANONYMIZED_TELEMETRY=False GRPC_VERBOSITY=NONE TOKENIZERS_PARALLELISM=false
python m3_engine/engine.py
