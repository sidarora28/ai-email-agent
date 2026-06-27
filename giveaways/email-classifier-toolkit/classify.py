"""classify.py — triage inbound emails with the Claude Code classifier agent.

For each inbound email it sends the agent prompt (.claude/agents/classifier.md)
+ your chosen category taxonomy (taxonomies/*.yaml) + the email to the `claude`
CLI, parses the returned JSON, validates it against schema.py, and writes
classified.json.

Run it out of the box (uses taxonomies/founder.yaml + examples/sample_inbound.json):

    python classify.py

Swap the taxonomy with a CLI arg ...

    python classify.py taxonomies/sales.yaml

... or via an env var:

    CLASSIFY_TAXONOMY=taxonomies/exec.yaml python classify.py

Override the inbound source the same way:

    CLASSIFY_INBOUND=examples/sample_inbound.json python classify.py
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

# Everything is relative to this file, so the kit runs from any working dir.
ROOT = Path(__file__).resolve().parent
AGENT = ROOT / ".claude/agents/classifier.md"

# Pick the taxonomy: CLI arg wins, then env var, then the founder default.
TAXONOMY = Path(
    sys.argv[1]
    if len(sys.argv) > 1
    else os.getenv("CLASSIFY_TAXONOMY", "taxonomies/founder.yaml")
)
if not TAXONOMY.is_absolute():
    TAXONOMY = ROOT / TAXONOMY

INBOUND = ROOT / os.getenv("CLASSIFY_INBOUND", "examples/sample_inbound.json")
OUT = ROOT / "classified.json"
MODEL = os.getenv("CLASSIFY_MODEL", "claude-haiku-4-5-20251001")
# Agent calls are independent per email, so run them concurrently — this is the
# difference between a 3-minute wait and a live-demo-friendly few seconds.
WORKERS = int(os.getenv("CLASSIFY_WORKERS", "10"))


def agent_prompt() -> str:
    """The classifier agent body, minus the YAML frontmatter."""
    text = AGENT.read_text()
    return re.sub(r"^---.*?---\s*", "", text, count=1, flags=re.DOTALL).strip()


def categories_text() -> str:
    """Render the chosen taxonomy as a '- name: description' bullet list."""
    data = yaml.safe_load(TAXONOMY.read_text()) or {}
    cats = data.get("categories", [])
    return "\n".join(f"- {c['name']}: {c.get('description', '').strip()}" for c in cats)


def fetch_inbound() -> list:
    """Synthetic inbound emails so the kit runs offline and repeatably."""
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
        f"EMAIL:\nFrom: {email.get('sender', '')}\n"
        f"Subject: {email.get('subject', '')}\n"
        f"Body: {email.get('body', email.get('snippet', ''))}\n"
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
    print(f"Taxonomy: {TAXONOMY.name}")
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
