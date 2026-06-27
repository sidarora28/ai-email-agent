#!/usr/bin/env bash
# One-shot runner for the Email Assistant.
#
#   bash run_all.sh             # full pipeline: embed -> classify -> draft -> dashboard
#   bash run_all.sh dashboard   # skip the agents, just open the dashboard (uses bundled data)
#
# Handles venv + deps automatically. Auto-unpacks the data bundle if it's in
# the repo root or ~/Downloads. Requires: python3.11+, and (for the agent steps)
# the `claude` CLI logged in.
set -e
cd "$(dirname "$0")"

# --- 1. venv + deps ---
if [ ! -d .venv ]; then
  echo "==> Creating virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate
echo "==> Installing dependencies (quiet)..."
pip install -q -r requirements.txt

# --- 2. make sure data is present (auto-unpack the bundle if needed) ---
if [ ! -f data/raw_emails.jsonl ]; then
  for b in ./email-assistant-data.tgz "$HOME/Downloads/email-assistant-data.tgz"; do
    if [ -f "$b" ]; then echo "==> Unpacking data bundle: $b"; tar -xzf "$b"; break; fi
  done
fi
if [ ! -f data/raw_emails.jsonl ]; then
  echo "ERROR: no data found. Put email-assistant-data.tgz in this folder or ~/Downloads, then re-run."
  exit 1
fi

# --- 3. run ---
MODE="${1:-full}"
if [ "$MODE" = "dashboard" ]; then
  echo "==> Launching dashboard with bundled data..."
  exec streamlit run m3-dashboard/app.py
fi

echo "==> M1: building voice profile..."
python m1-voice/build_embeddings.py
echo "==> M2: classifying inbound emails..."
python m2-classifier/classify.py
echo "==> M3: drafting + reviewing..."
python m3-dashboard/orchestrate.py
echo "==> Launching dashboard..."
streamlit run m3-dashboard/app.py
