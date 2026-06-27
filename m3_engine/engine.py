"""engine.py — M3: the runtime pipeline.

Reads M2's classified.json, keeps only reply-worthy emails, and for each runs:
  drafter (voice + knowledge + connectors + principles)
    -> reviewer (voice match + groundedness vs FULL knowledge + principles)
    -> one revise loop
and writes everything to data/records.json for the dashboard.

    python m3_engine/engine.py

Runs sequentially (one email at a time) — spawning many `claude` CLIs at once
overwhelms a laptop. A handful of seed emails takes a couple of minutes.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from retrieve import retrieve_voice, retrieve_knowledge  # noqa: E402
from connectors import CONNECTORS  # noqa: E402

load_dotenv()

CLASSIFIED = ROOT / "data/classified.json"
RECORDS = ROOT / "data/records.json"
PRINCIPLES = ROOT / "principles.md"
VOICE_PROFILE = ROOT / "data/voice_profile.md"
KNOWLEDGE_DIR = ROOT / "knowledge"
DRAFTER = ROOT / ".claude/agents/drafter.md"
REVIEWER = ROOT / ".claude/agents/reviewer.md"
DRAFT_MODEL = os.getenv("DRAFT_MODEL", "claude-opus-4-8")            # confirmed on this CLI
REVIEW_MODEL = os.getenv("REVIEW_MODEL", "claude-haiku-4-5-20251001")  # fast review


def body(path):
    return re.sub(r"^---.*?---\s*", "", path.read_text(), count=1, flags=re.DOTALL).strip()


def full_knowledge():
    return "\n\n".join(f"### {p.name}\n{p.read_text()}" for p in sorted(KNOWLEDGE_DIR.glob("*.md")))


def claude(prompt, model, timeout=180):
    res = subprocess.run(
        ["claude", "-p", "--model", model],
        input=prompt, capture_output=True, text=True, timeout=timeout,
    )
    if res.returncode != 0:
        raise RuntimeError(f"claude failed: {res.stderr[:200]}")
    return res.stdout.strip()


def incoming_block(email):
    """Full context for the drafter/reviewer: prior thread + the latest message."""
    parts = []
    if email.get("thread"):
        parts.append(f"EARLIER IN THIS THREAD:\n{email['thread']}\n")
    parts.append(
        f"LATEST MESSAGE:\nFrom: {email.get('sender','')}\n"
        f"Subject: {email.get('subject','')}\n"
        f"Body: {email.get('body') or email.get('snippet','')}"
    )
    return "\n".join(parts)


def run_connectors(email):
    """Run the connectors this category cares about (stubbed -> degrade safely)."""
    results = {}
    for tool in email.get("tools") or []:
        fn = CONNECTORS.get(tool)
        if fn:
            try:
                results[tool] = fn(email.get("sender", ""))
            except Exception as e:
                results[tool] = {"available": False, "reason": str(e)[:80]}
    return results


def draft_reply(email, voice_ex, knowledge, connectors, principles, profile, feedback=""):
    voice = profile + "\n\nEXAMPLE REPLIES:\n" + "\n---\n".join(v["text"] for v in voice_ex)
    know = "\n".join(f"- ({k['meta'].get('source','')}) {k['text']}" for k in knowledge)
    prompt = (
        f"{body(DRAFTER)}\n\n"
        f"INCOMING:\n{incoming_block(email)}\n\n"
        f"CATEGORY: {email.get('category')} | INTENT: {email.get('intent')} | "
        f"DEFAULT ACTION: {email.get('default_action')}\n\n"
        f"VOICE:\n{voice}\n\n"
        f"KNOWLEDGE (only facts you may use):\n{know}\n\n"
        f"CONNECTORS: {json.dumps(connectors)}\n\n"
        f"PRINCIPLES:\n{principles}\n"
    )
    if feedback:
        prompt += f"\nThe reviewer asked you to revise: {feedback}\nRewrite the reply.\n"
    return claude(prompt, DRAFT_MODEL)


def review_draft(email, draft, knowledge_full, closest, connectors, principles):
    prompt = (
        f"{body(REVIEWER)}\n\n"
        f"INCOMING:\n{incoming_block(email)}\n\n"
        f"DRAFT:\n{draft}\n\n"
        f"FULL KNOWLEDGE:\n{knowledge_full}\n\n"
        f"CLOSEST REAL REPLY:\n{closest}\n\n"
        f"CONNECTORS: {json.dumps(connectors)}\n\n"
        f"PRINCIPLES:\n{principles}\n"
    )
    out = claude(prompt, REVIEW_MODEL)
    m = re.search(r"\{.*\}", out, re.DOTALL)
    return json.loads(m.group(0)) if m else {
        "verdict": "revise", "grounded": False, "voice_match": False,
        "comment": "reviewer returned no JSON", "issues": ["parse error"], "suggested_edit": "",
    }


def main():
    classified = json.loads(CLASSIFIED.read_text())
    worklist = [e for e in classified if e.get("reply_needed") and not e.get("needs_human")]
    print(f"{len(classified)} classified · {len(worklist)} reply-worthy → drafting\n")

    principles = body(PRINCIPLES)
    profile = VOICE_PROFILE.read_text() if VOICE_PROFILE.exists() else ""
    knowledge_full = full_knowledge()

    records = []
    for i, email in enumerate(worklist, 1):
        subj = (email.get("subject") or "")[:40]
        print(f"[{i}/{len(worklist)}] {subj}")
        query = f"{email.get('subject','')} {email.get('body') or email.get('snippet','')}"
        voice_ex = retrieve_voice(query, 3)
        knowledge = retrieve_knowledge(query, 4)
        connectors = run_connectors(email)

        print("    drafter ...")
        draft = draft_reply(email, voice_ex, knowledge, connectors, principles, profile)

        if draft.startswith("NO_DRAFT"):
            print(f"    no draft — {draft}")
            records.append({**email, "status": "insufficient_info",
                            "draft": "", "review": {"comment": draft}})
            continue

        closest = voice_ex[0]["text"] if voice_ex else ""
        print("    reviewer ...")
        review = review_draft(email, draft, knowledge_full, closest, connectors, principles)

        if review.get("verdict") == "revise":
            print(f"    revise — {review.get('comment','')[:60]}")
            draft = draft_reply(email, voice_ex, knowledge, connectors, principles,
                                profile, feedback=review.get("comment", ""))
            review = review_draft(email, draft, knowledge_full, closest, connectors, principles)

        print(f"    {review.get('verdict','?')} (grounded={review.get('grounded')}, "
              f"voice={review.get('voice_match')})\n")
        records.append({**email, "status": "drafted", "draft": draft, "review": review})

    RECORDS.write_text(json.dumps(records, indent=2))
    drafted = sum(1 for r in records if r["status"] == "drafted")
    print(f"Done -> {RECORDS}  ({drafted} drafted, {len(records)-drafted} insufficient)")


if __name__ == "__main__":
    main()
