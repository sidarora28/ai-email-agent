"""approve.py — Segment 4: review each draft, approve it into Gmail Drafts.

Shows each reviewed draft. You approve / skip / edit. On approve it creates a
DRAFT in your Gmail (drafts.create) — it is NEVER sent. You hit send yourself.

    python m3_engine/approve.py

Needs a write scope (gmail.compose) — first run re-auths in the browser. Uses a
separate token (token_compose.json) so your read-only fetch token is untouched.
"""

import base64
import json
import os
import subprocess
import sys
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "data/records.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]   # create drafts, NOT send
CREDS = os.getenv("GMAIL_CREDENTIALS_PATH", "data/auth/credentials.json")
TOKEN = "data/auth/token_compose.json"
BOLD, DIM, GREEN, YELLOW, RESET = "\033[1m", "\033[2m", "\033[32m", "\033[33m", "\033[0m"


def service():
    creds = None
    if Path(TOKEN).exists():
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = InstalledAppFlow.from_client_secrets_file(CREDS, SCOPES).run_local_server(port=0)
        Path(TOKEN).write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def email_addr(sender):
    import re
    m = re.search(r"<([^>]+)>", sender or "")
    return m.group(1) if m else (sender or "").strip()


def edit(text):
    """Open the draft in $EDITOR for quick tweaks; return the edited text."""
    import tempfile
    editor = os.getenv("EDITOR", "nano")
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as f:
        f.write(text)
        path = f.name
    subprocess.run([editor, path])
    return Path(path).read_text().strip()


def make_draft(svc, to, subject, body):
    msg = EmailMessage()
    msg["To"] = to
    msg["Subject"] = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    msg.set_content(body)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return svc.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()


def main():
    records = json.loads(RECORDS.read_text())
    drafts = [r for r in records if r.get("status") == "drafted" and r.get("draft")]
    print(f"\n{BOLD}✅  STEP 4 — Review & approve{RESET}  {DIM}{len(drafts)} drafts · "
          f"approve → Gmail Drafts (never sent){RESET}\n")
    svc = service()

    approved = 0
    for i, r in enumerate(drafts, 1):
        print(f"{'─'*70}\n{BOLD}{i}/{len(drafts)}  to {r.get('sender','')}{RESET}")
        print(f"{DIM}re: {r.get('subject','')}{RESET}\n{r['draft']}\n")
        choice = input(f"{BOLD}approve / skip / edit  [a/s/e]:{RESET} ").strip().lower()
        if choice == "e":
            r["draft"] = edit(r["draft"])
            choice = "a"
        if choice == "a":
            make_draft(svc, email_addr(r.get("sender", "")), r.get("subject", ""), r["draft"])
            approved += 1
            print(f"   {GREEN}✓ added to your Gmail Drafts{RESET}\n")
        else:
            print(f"   {YELLOW}↷ skipped{RESET}\n")

    print(f"{'─'*70}\n{BOLD}Done.{RESET} {approved} draft(s) in your Gmail Drafts — "
          f"review and send them yourself.\n")


if __name__ == "__main__":
    main()
