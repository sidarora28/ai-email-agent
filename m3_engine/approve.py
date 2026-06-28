"""approve.py — Segment 4: review a draft, approve it into Gmail Drafts.

    python m3_engine/approve.py        # list the drafts with their numbers
    python m3_engine/approve.py 2      # review draft #2 only — approve / skip / edit

Approve drafts one at a time, by number. On approve it creates a DRAFT in your
Gmail (drafts.create) — it is NEVER sent. You hit send yourself.

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


def list_drafts(drafts):
    print(f"\n{BOLD}✅  STEP 4 — Review & approve{RESET}  {DIM}{len(drafts)} drafts · "
          f"approve one at a time → Gmail Drafts (never sent){RESET}\n")
    for i, r in enumerate(drafts, 1):
        print(f"  {BOLD}{i}{RESET}  to {r.get('sender','')}  {DIM}re: {r.get('subject','')}{RESET}")
    print(f"\n{DIM}Approve one:{RESET} python m3_engine/approve.py <number>\n")


def approve_one(drafts, n):
    if n < 1 or n > len(drafts):
        print(f"{YELLOW}No draft #{n}. There are {len(drafts)} drafts (1–{len(drafts)}).{RESET}\n")
        return
    r = drafts[n - 1]
    print(f"\n{'─'*70}\n{BOLD}{n}/{len(drafts)}  to {r.get('sender','')}{RESET}")
    print(f"{DIM}re: {r.get('subject','')}{RESET}\n{r['draft']}\n")
    choice = input(f"{BOLD}approve / skip / edit  [a/s/e]:{RESET} ").strip().lower()
    if choice == "e":
        r["draft"] = edit(r["draft"])
        choice = "a"
    if choice == "a":
        svc = service()
        make_draft(svc, email_addr(r.get("sender", "")), r.get("subject", ""), r["draft"])
        print(f"   {GREEN}✓ added to your Gmail Drafts — review and send it yourself.{RESET}\n")
    else:
        print(f"   {YELLOW}↷ skipped{RESET}\n")


def main():
    records = json.loads(RECORDS.read_text())
    drafts = [r for r in records if r.get("status") == "drafted" and r.get("draft")]
    if len(sys.argv) > 1:
        approve_one(drafts, int(sys.argv[1]))
    else:
        list_drafts(drafts)


if __name__ == "__main__":
    main()
