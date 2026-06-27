"""orchestrate.py — the multi-agent loop: drafter -> reviewer -> drafts.json

For each classified email:
  1. Retrieve Sid's most similar past replies (M1 voice profile).
  2. Ask the DRAFTER agent to write a reply in Sid's voice, grounded in those.
  3. Ask the REVIEWER agent to check the draft and return a verdict + comment.
  4. Write the result to data/drafts.json for the dashboard to render.

    python m3-dashboard/orchestrate.py

This is a LIVE segment: the terminal shows the agent-to-agent handoff per email.
"""

import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "m1-voice"))
from retrieve import retrieve_similar  # noqa: E402

load_dotenv()

CLASSIFIED = ROOT / "data/classified.json"
OUT = ROOT / "data/drafts.json"
DRAFTER = ROOT / ".claude/agents/drafter.md"
REVIEWER = ROOT / ".claude/agents/reviewer.md"
MODEL = os.getenv("DRAFT_MODEL", "claude-haiku-4-5-20251001")
VOICE_K = int(os.getenv("VOICE_K", "3"))
# Emails are independent, so run the drafter->reviewer chain concurrently.
WORKERS = int(os.getenv("ORCHESTRATE_WORKERS", "8"))


def body(agent_path: Path) -> str:
    text = agent_path.read_text()
    return re.sub(r"^---.*?---\s*", "", text, count=1, flags=re.DOTALL).strip()


def call_claude(prompt: str) -> str:
    result = subprocess.run(
        ["claude", "-p", prompt, "--model", MODEL],
        capture_output=True, text=True, timeout=90,
    )
    return result.stdout.strip()


def draft_reply(email: dict, voice_examples: list) -> str:
    examples = "\n\n".join(f"- {e['text']}" for e in voice_examples)
    prompt = (
        f"{body(DRAFTER)}\n\n"
        f"INBOUND:\nFrom: {email.get('sender','')}\n"
        f"Subject: {email.get('subject','')}\n"
        f"Body: {email.get('snippet','')}\n\n"
        f"CATEGORY: {email.get('category','')} "
        f"(suggested: {email.get('suggested_action','')})\n\n"
        f"VOICE EXAMPLES:\n{examples}\n"
    )
    return call_claude(prompt)


def review_draft(email: dict, draft: str) -> dict:
    prompt = (
        f"{body(REVIEWER)}\n\n"
        f"INBOUND:\nFrom: {email.get('sender','')}\n"
        f"Subject: {email.get('subject','')}\n"
        f"Body: {email.get('snippet','')}\n\n"
        f"DRAFT:\n{draft}\n"
    )
    out = call_claude(prompt)
    match = re.search(r"\{.*\}", out, re.DOTALL)
    if not match:
        return {"verdict": "approve", "comment": "(reviewer returned no JSON)", "suggested_edit": ""}
    return json.loads(match.group(0))


def process_email(email: dict) -> dict:
    """Full drafter -> reviewer chain for one email."""
    voice = retrieve_similar(email.get("snippet", ""), VOICE_K)
    draft = draft_reply(email, voice)
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
    emails = json.loads(CLASSIFIED.read_text())
    print(f"Orchestrating drafter -> reviewer for {len(emails)} emails (model: {MODEL})\n")

    # warm the embedding model once so concurrent threads don't all load it
    retrieve_similar("warmup", 1)

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
