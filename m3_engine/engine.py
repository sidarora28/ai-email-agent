"""engine.py — M3: the runtime pipeline, built for a live demo.

Reads M2's classified.json, keeps only reply-worthy emails, and for each:
  drafter (voice + knowledge + connectors + principles)  -- STREAMS to screen
    -> reviewer (voice match + groundedness vs FULL knowledge + principles)
    -> one revise loop
then writes everything to data/records.json.

    python m3_engine/engine.py

Sequential, with the draft streaming token-by-token so an audience watches the
reply get written. Terminal is kept clean (warnings/telemetry silenced).
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from retrieve import retrieve_voice, retrieve_knowledge  # noqa: E402  (sets quiet env)
from connectors import CONNECTORS  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

load_dotenv()

CLASSIFIED = ROOT / "data/classified.json"
RECORDS = ROOT / "data/records.json"
PRINCIPLES = ROOT / "principles.md"
VOICE_PROFILE = ROOT / "data/voice_profile.md"
KNOWLEDGE_DIR = ROOT / "knowledge"
DRAFTER = ROOT / ".claude/agents/drafter.md"
REVIEWER = ROOT / ".claude/agents/reviewer.md"
DRAFT_MODEL = os.getenv("DRAFT_MODEL", "claude-opus-4-8")
REVIEW_MODEL = os.getenv("REVIEW_MODEL", "claude-haiku-4-5-20251001")

DIM, BOLD, GREEN, YELLOW, BLUE, RESET = (
    "\033[2m", "\033[1m", "\033[32m", "\033[33m", "\033[36m", "\033[0m")


def body(path):
    return re.sub(r"^---.*?---\s*", "", path.read_text(), count=1, flags=re.DOTALL).strip()


def full_knowledge():
    return "\n\n".join(f"### {p.name}\n{p.read_text()}" for p in sorted(KNOWLEDGE_DIR.glob("*.md")))


def name_of(sender):
    return re.sub(r"\s*<.*?>", "", sender or "").strip() or sender


def claude(prompt, model, timeout=180):
    res = subprocess.run(["claude", "-p", "--model", model],
                         input=prompt, capture_output=True, text=True, timeout=timeout)
    if res.returncode != 0:
        raise RuntimeError(f"claude failed: {res.stderr[:200]}")
    return res.stdout.strip()


def stream_claude(prompt, model, prefix="      "):
    """Run the drafter and print its output live, so the reply writes on screen."""
    proc = subprocess.Popen(["claude", "-p", "--model", model],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
    proc.stdin.write(prompt)
    proc.stdin.close()
    chunks = []
    for line in proc.stdout:
        sys.stdout.write(prefix + line)
        sys.stdout.flush()
        chunks.append(line)
    proc.wait()
    text = "".join(chunks).strip()
    if proc.returncode != 0:
        raise RuntimeError(text or "claude call failed")
    return text


def incoming_block(email):
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
    results = {}
    for tool in email.get("tools") or []:
        fn = CONNECTORS.get(tool)
        if fn:
            try:
                results[tool] = fn(email.get("sender", ""))
            except Exception as e:
                results[tool] = {"available": False, "reason": str(e)[:80]}
    return results


def draft_prompt(email, voice_ex, knowledge, connectors, principles, profile, feedback=""):
    voice = profile + "\n\nEXAMPLE REPLIES:\n" + "\n---\n".join(v["text"] for v in voice_ex)
    know = "\n".join(f"- ({k['meta'].get('source','')}) {k['text']}" for k in knowledge)
    p = (
        f"{body(DRAFTER)}\n\nINCOMING:\n{incoming_block(email)}\n\n"
        f"CATEGORY: {email.get('category')} | INTENT: {email.get('intent')} | "
        f"DEFAULT ACTION: {email.get('default_action')}\n\n"
        f"VOICE:\n{voice}\n\nKNOWLEDGE (only facts you may use):\n{know}\n\n"
        f"CONNECTORS: {json.dumps(connectors)}\n\nPRINCIPLES:\n{principles}\n"
    )
    if feedback:
        p += f"\nThe reviewer asked you to revise: {feedback}\nRewrite the reply.\n"
    return p


def review_prompt(email, draft, knowledge_full, closest, connectors, principles):
    return (
        f"{body(REVIEWER)}\n\nINCOMING:\n{incoming_block(email)}\n\nDRAFT:\n{draft}\n\n"
        f"FULL KNOWLEDGE:\n{knowledge_full}\n\nCLOSEST REAL REPLY:\n{closest}\n\n"
        f"CONNECTORS: {json.dumps(connectors)}\n\nPRINCIPLES:\n{principles}\n"
    )


def review(prompt):
    out = claude(prompt, REVIEW_MODEL)
    m = re.search(r"\{.*\}", out, re.DOTALL)
    return json.loads(m.group(0)) if m else {
        "verdict": "revise", "grounded": False, "voice_match": False,
        "comment": "reviewer returned no JSON", "issues": ["parse error"], "suggested_edit": ""}


def main():
    classified = json.loads(CLASSIFIED.read_text())
    worklist = [e for e in classified if e.get("reply_needed") and not e.get("needs_human")]
    skipped = [e for e in classified if not (e.get("reply_needed") and not e.get("needs_human"))]

    print(f"\n{BOLD}✍️  STEP 3 — Write replies{RESET}")
    print(f"{DIM}    {len(worklist)} to draft · a WRITER drafts in Sid's voice, "
          f"a REVIEWER checks each one{RESET}\n")

    principles = body(PRINCIPLES)
    profile = VOICE_PROFILE.read_text() if VOICE_PROFILE.exists() else ""
    knowledge_full = full_knowledge()

    records = []
    for i, email in enumerate(worklist, 1):
        print(f"{BLUE}{'─'*70}{RESET}")
        print(f"📨  {BOLD}{name_of(email.get('sender'))}{RESET} — \"{email.get('subject','')}\"")
        print(f"{DIM}    {email.get('category')} · {email.get('intent')}{RESET}\n")

        try:
            query = f"{email.get('subject','')} {email.get('body') or email.get('snippet','')}"
            voice_ex = retrieve_voice(query, 3)
            knowledge = retrieve_knowledge(query, 4)
            connectors = run_connectors(email)

            print(f"   ✍️  {BOLD}WRITER{RESET} {DIM}drafting in your voice, grounded in your facts:{RESET}\n")
            draft = stream_claude(
                draft_prompt(email, voice_ex, knowledge, connectors, principles, profile),
                DRAFT_MODEL)

            if draft.startswith("NO_DRAFT"):
                print(f"\n   {YELLOW}⚠️  no draft — {draft}{RESET}\n")
                records.append({**email, "status": "insufficient_info", "draft": "",
                                "review": {"comment": draft}})
                continue

            closest = voice_ex[0]["text"] if voice_ex else ""
            print(f"\n\n   🔍  {BOLD}REVIEWER{RESET} {DIM}checking voice · grounding · principles …{RESET}")
            rev = review(review_prompt(email, draft, knowledge_full, closest, connectors, principles))

            if rev.get("verdict") == "revise":
                print(f"   {YELLOW}↻ revise: {rev.get('comment','')[:70]}{RESET}\n")
                draft = stream_claude(
                    draft_prompt(email, voice_ex, knowledge, connectors, principles,
                                 profile, feedback=rev.get("comment", "")), DRAFT_MODEL)
                rev = review(review_prompt(email, draft, knowledge_full, closest, connectors, principles))
        except Exception as e:
            msg = (str(e).splitlines() or ["claude error"])[-1][:120]
            print(f"\n   {YELLOW}⚠️  skipped — {msg}{RESET}\n")
            records.append({**email, "status": "error", "draft": "", "review": {"comment": msg}})
            continue

        tick = f"{GREEN}✓{RESET}" if rev.get("verdict") == "approve" else f"{YELLOW}↻{RESET}"
        g = f"{GREEN}✓{RESET}" if rev.get("grounded") else f"{YELLOW}✗{RESET}"
        v = f"{GREEN}✓{RESET}" if rev.get("voice_match") else f"{YELLOW}✗{RESET}"
        print(f"   {tick} {rev.get('verdict','').upper()}   grounded {g}  voice {v}   "
              f"{DIM}{rev.get('comment','')[:60]}{RESET}\n")
        records.append({**email, "status": "drafted", "draft": draft, "review": rev})
        time.sleep(0.3)

    RECORDS.write_text(json.dumps(records, indent=2))
    drafted = sum(1 for r in records if r["status"] == "drafted")
    print(f"{BLUE}{'─'*70}{RESET}")
    print(f"{BOLD}Done.{RESET} {drafted} drafts ready for review  {DIM}→ {RECORDS}{RESET}\n")


if __name__ == "__main__":
    main()
