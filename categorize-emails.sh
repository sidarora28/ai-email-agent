#!/usr/bin/env bash
# STEP 2 — sort the fetched emails into Sid's categories
set -e; cd "$(dirname "$0")"; source .venv/bin/activate 2>/dev/null || true
export PYTHONWARNINGS=ignore ANONYMIZED_TELEMETRY=False GRPC_VERBOSITY=NONE TOKENIZERS_PARALLELISM=false
python m2_classify/classify.py
