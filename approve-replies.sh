#!/usr/bin/env bash
# STEP 4 — review and approve drafts into your Gmail Drafts, one at a time (never sends).
#   bash approve-replies.sh        list the drafts with their numbers
#   bash approve-replies.sh 2      approve draft 2 only
set -e; cd "$(dirname "$0")"; source .venv/bin/activate 2>/dev/null || true
export PYTHONWARNINGS=ignore ANONYMIZED_TELEMETRY=False GRPC_VERBOSITY=NONE
python m3_engine/approve.py "$@"
