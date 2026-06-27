"""classify.py — triage inbound emails with the Claude Code classifier agent.

For each inbound email it sends the agent prompt (.claude/agents/classifier.md)
+ your categories (categories.yaml) + the email to the `claude` CLI, parses the
returned JSON, validates it against schema.py, and writes data/classified.json.

    python m2-classifier/classify.py

Inbound source:
- By default reads cached real inbound emails from data/inbound_emails.json
  (so the demo runs offline / repeatably).
- On your Mac you can swap in a live Gmail pull (see fetch_inbound()).

If live classification fails, the dashboard falls back to
data/classified.fallback.json — so the stage demo never shows an empty screen.
"""

import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from schema import Classification, parse_classification  # noqa: E402

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / ".claude/agents/classifier.md"
CATEGORIES = ROOT / "m2-classifier/categories.yaml"
INBOUND = ROOT / "data/inbound_emails.json"
OUT = ROOT / "data/classified.json"
MODEL = os.getenv("CLASSIFY_MODEL", "claude-haiku-4-5-20251001")
# Agent calls are independent per email, so run them concurrently — this is the
# difference between a 3-minute wait and a live-demo-friendly few seconds.
WORKERS = int(os.getenv("CLASSIFY_WORKERS", "10"))


def agent_prompt() -> str:
    """The classifier agent body, minus YAML frontmatter."""
    text = AGENT.read_text()
    return re.sub(r"^---.*?---\s*", "", text, count=1, flags=re.DOTALL).strip()


def categories_text() -> str:
    data = yaml.safe_load(CATEGORIES.read_text()) or {}
    cats = data.get("categories", [])
    return "\n".join(f"- {c['name']}: {c.get('description','').strip()}" for c in cats)


def fetch_inbound() -> list:
    """Cached real inbound emails. On your Mac, replace with a live Gmail pull."""
    return json.loads(INBOUND.read_text())


def call_agent(prompt: str) -> dict:
    """Run the classifier agent via the Claude Code CLI and parse its JSON."""
    result = subprocess.run(
        ["claude", "-p", prompt, "--model", MODEL],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout.strip()
    match = re.search(r"\{.*\}", out, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON in agent output: {out[:200]}")
    return json.loads(match.group(0))


def classify_one(email: dict, base: str, cats: str) -> Classification:
    prompt = (
        f"{base}\n\nCATEGORIES:\n{cats}\n\n"
        f"EMAIL:\nFrom: {email.get('sender','')}\n"
        f"Subject: {email.get('subject','')}\n"
        f"Body: {email.get('body', email.get('snippet',''))}\n"
    )
    raw = call_agent(prompt)
    raw.update({
        "id": email.get("id"),
        "sender": email.get("sender"),
        "subject": email.get("subject"),
        "snippet": email.get("snippet", email.get("body", ""))[:160],
    })
    return parse_classification(raw)


def classify_emails(emails: list) -> list:
    """Classify emails concurrently. Returns Classification objects in order."""
    base = agent_prompt()
    cats = categories_text()
    results = [None] * len(emails)
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(classify_one, e, base, cats): i
                   for i, e in enumerate(emails)}
        for fut in as_completed(futures):
            i = futures[fut]
            c = fut.result()
            results[i] = c
            done += 1
            print(f"  [{done}/{len(emails)}] {c.category:16} {c.urgency.value:6} "
                  f"({c.confidence})  {(c.subject or '')[:40]}")
    return results


def main():
    print(f"Loading inbound emails ...")
    emails = fetch_inbound()
    print(f"  {len(emails)} emails to classify (model: {MODEL})\n")

    start = time.time()
    results = classify_emails(emails)
    elapsed = time.time() - start

    OUT.write_text(json.dumps([c.model_dump(mode="json") for c in results], indent=2))
    print(f"\nDone. Classified {len(results)} emails in {elapsed:.1f}s -> {OUT}")


if __name__ == "__main__":
    main()
