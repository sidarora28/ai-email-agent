#!/usr/bin/env bash
# Reset to the "live-start" state for Act 3: keep the slow pre-built bits
# (voice pairs, knowledge index, model cache) and back up the current outputs as
# a failsafe; clear only what we regenerate live on stage.
set -e; cd "$(dirname "$0")"
mkdir -p data/failsafe
cp -f data/records.json    data/failsafe/records.json    2>/dev/null || true
cp -f data/classified.json data/failsafe/classified.json 2>/dev/null || true
rm -f data/voice_profile.md data/categories.yaml data/classified.json data/records.json
rm -rf data/voice_index.db
echo "✓ Reset to live-start."
echo "  kept:   voice_pairs.jsonl, knowledge_index.db, model cache"
echo "  backed up failsafe: data/failsafe/records.json"
echo "  stage order: learn_voice -> build_voice_index -> categorize -> write-replies"
