#!/usr/bin/env bash
# deploy.sh — local-only setup + run for the Multi-Agent Dashboard Template.
#
# This is intentionally simple: create a venv, install deps, launch the
# dashboard. It does NOT deploy to any server (the cohort covers real
# deployment / hardening in weeks 3-4).
#
#   ./deploy.sh
#
set -euo pipefail
cd "$(dirname "$0")"

# 1. Create an isolated virtual environment (once).
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment in .venv ..."
  python3 -m venv .venv
fi

# 2. Activate it and install pinned dependencies.
# shellcheck disable=SC1091
source .venv/bin/activate
echo "Installing dependencies ..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# 3. (Optional) Generate fresh drafts with the drafter->reviewer loop.
#    Requires the `claude` CLI on your PATH. Uncomment to run before launch:
# echo "Running the multi-agent drafter->reviewer loop ..."
# python orchestrate.py

# 4. Launch the dashboard. The dark theme comes from .streamlit/config.toml.
echo "Launching dashboard at http://localhost:8501 ..."
streamlit run app.py
