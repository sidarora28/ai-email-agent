#!/usr/bin/env bash
# STEP 4 — review each draft and approve it into your Gmail Drafts (never sends)
set -e; cd "$(dirname "$0")"; source .venv/bin/activate 2>/dev/null || true
export PYTHONWARNINGS=ignore ANONYMIZED_TELEMETRY=False GRPC_VERBOSITY=NONE
python m3_engine/approve.py
