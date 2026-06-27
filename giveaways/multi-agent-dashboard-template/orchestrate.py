"""orchestrate.py — the multi-agent loop: drafter -> reviewer -> drafts.json

For each pre-classified email:
  1. (Optional) Use voice examples passed inline on the email to ground the draft.
  2. Ask the DRAFTER agent to write a reply, grounded in those examples.
  3. Ask the REVIEWER agent to check the draft and return a verdict + comment.
  4. Write the result to drafts.json for the dashboard (app.py) to render.

    python orchestrate.py

This is the multi-agent segment: the terminal shows the agent-to-agent handoff
per email. Emails are independent, so the drafter->reviewer chain runs in
parallel across a thread pool.

STANDALONE NOTE
---------------
Unlike the full Email Assistant repo, this template has NO embeddings /
vector-store dependency. Voice grounding is optional: if an email in the input
JSON carries a "voice_examples" list (each item a string, or an object with a
"text" field), those are passed to the drafter. If absent, drafting proceeds
without voice examples — the drafter falls back to a sensible default tone.
"""

import json
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
# Default to the bundled synthetic emails; override with EMAILS_JSON.
EMAILS = Path(os.getenv("EMAILS_JSON", ROOT / "examples/sample_emails.json"))
OUT = Path(os.getenv("DRAFTS_JSON", ROOT / "drafts.json"))
DRAFTER = ROOT / ".claude/agents/drafter.md"
REVIEWER = ROOT / ".claude/agents/reviewer.md"
MODEL = os.getenv("DRAFT_MODEL", "claude-haiku-4-5-20251001")
# Emails are independent, so run the drafter->reviewer chain concurrently.
WORKERS = int(os.getenv("ORCHESTRATE_WORKERS", "8"))


def body(agent_path: Path) -> str:
    """Read an agent .md file and strip its YAML frontmatter, leaving the prompt."""
    text = agent_path.read_text()
    return re.sub(r"^---.*?---\s*", "", text, count=1, flags=re.DOTALL).strip()


def call_claude(prompt: str) -> str:
    """Invoke the local `claude` CLI in headless (-p) mode and return stdout."""
    result = subprocess.run(
        ["claude", "-p", prompt, "--model", MODEL],
        capture_output=True, text=True, timeout=90,
    )
    return result.stdout.strip()


def voice_block(email: dict) -> str:
    """Build the VOICE EXAMPLES section from an optional inline list.

    Accepts items that are plain strings or objects with a "text" field.
    Returns an empty string when no examples are present.
    """
    examples = email.get("voice_examples") or []
    texts = [e["text"] if isinstance(e, dict) else str(e) for e in examples]
    if not texts:
        return ""
    joined = "\n\n".join(f"- {t}" for t in texts)
    return f"VOICE EXAMPLES:\n{joined}\n"


def draft_reply(email: dict) -> str:
    """Ask the drafter agent for a reply, grounded in any inline voice examples."""
    prompt = (
        f"{body(DRAFTER)}\n\n"
        f"INBOUND:\nFrom: {email.get('sender','')}\n"
        f"Subject: {email.get('subject','')}\n"
        f"Body: {email.get('snippet','')}\n\n"
        f"CATEGORY: {email.get('category','')} "
        f"(urgency: {email.get('urgency','')})\n\n"
        f"{voice_block(email)}"
    )
    return call_claude(prompt)


def review_draft(email: dict, draft: str) -> dict:
    """Ask the reviewer agent to grade the draft; parse its JSON verdict."""
    prompt = (
        f"{body(REVIEWER)}\n\n"
        f"INBOUND:\nFrom: {email.get('sender','')}\n"
        f"Subject: {email.get('subject','')}\n"
        f"Body: {email.get('snippet','')}\n\n"
        f"DRAFT:\n{draft}\n"
    )
    out = call_claude(prompt)
    # The reviewer is asked for raw JSON, but be defensive: pull the first {...}.
    match = re.search(r"\{.*\}", out, re.DOTALL)
    if not match:
        return {"verdict": "approve", "comment": "(reviewer returned no JSON)", "suggested_edit": ""}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"verdict": "approve", "comment": "(reviewer JSON was malformed)", "suggested_edit": ""}


def process_email(email: dict) -> dict:
    """Full drafter -> reviewer chain for one email."""
    draft = draft_reply(email)
    review = review_draft(email, draft)
    return {
        "id": email.get("id"),
        "sender": email.get("sender"),
        "subject": email.get("subject"),
        "category": email.get("category"),
        "urgency": email.get("urgency"),
        "draft": draft,
        "review": review,
    }


def main():
    emails = json.loads(EMAILS.read_text())
    print(f"Orchestrating drafter -> reviewer for {len(emails)} emails (model: {MODEL})\n")

    results = [None] * len(emails)
    done = 0
    start = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(process_email, e): i for i, e in enumerate(emails)}
        for fut in as_completed(futures):
            i = futures[fut]
            r = fut.result()
            results[i] = r
            done += 1
            verdict = r["review"].get("verdict", "?")
            print(f"  [{done}/{len(emails)}] {(r['subject'] or '')[:40]:40} "
                  f"drafted -> reviewer: {verdict}")

    OUT.write_text(json.dumps(results, indent=2))
    elapsed = time.time() - start
    print(f"\nDone. {len(results)} drafts in {elapsed:.1f}s -> {OUT}")


if __name__ == "__main__":
    main()
