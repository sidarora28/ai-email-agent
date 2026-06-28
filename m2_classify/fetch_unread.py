"""fetch_unread.py — pull recent unread inbox emails to classify.

Writes data/inbound.jsonl (one {id, sender, subject, body} per line) so
classify.py has something to run on. M3 will build its fetch on top of this.

    python m2_classify/fetch_unread.py            # default 15 most-recent unread
    INBOUND_LIMIT=30 python m2_classify/fetch_unread.py
"""

import base64
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "data/auth/credentials.json")
TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "data/auth/token.json")
LIMIT = int(os.getenv("INBOUND_LIMIT", "15"))
QUERY = os.getenv("INBOUND_QUERY", "in:inbox is:unread")
OUT = Path("data/inbound.jsonl")


def get_service():
    creds = None
    if Path(TOKEN_PATH).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        Path(TOKEN_PATH).write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def extract_body(payload):
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", "ignore")
    for part in payload.get("parts", []):
        b = extract_body(part)
        if b:
            return b
    return ""


def strip_quotes(body):
    lines = []
    for line in body.splitlines():
        if line.strip().startswith(">"):
            continue
        if re.match(r"^On .* wrote:$", line.strip()):
            break
        lines.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def name_of(sender):
    import re as _re
    return _re.sub(r"\s*<.*?>", "", sender or "").strip() or sender


def main():
    service = get_service()
    print("\n\033[1m📥  STEP 1 — Fetch new emails\033[0m")
    print(f"\033[2m    pulling inbox ({QUERY})…\033[0m\n")
    resp = service.users().messages().list(
        userId="me", q=QUERY, maxResults=LIMIT,
    ).execute()
    ids = [m["id"] for m in resp.get("messages", [])]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with OUT.open("w") as f:
        for mid in ids:
            msg = service.users().messages().get(userId="me", id=mid, format="full").execute()
            h = msg["payload"].get("headers", [])

            # full thread context: everything before this message in the thread
            thread = service.users().threads().get(
                userId="me", id=msg["threadId"], format="full").execute()
            prior = []
            for t in sorted(thread["messages"], key=lambda x: int(x.get("internalDate", "0"))):
                if t["id"] == mid:
                    break
                th = t["payload"].get("headers", [])
                tb = strip_quotes(extract_body(t["payload"]))
                if tb:
                    prior.append(f"{header(th, 'From')}: {tb}")

            sender, subject = header(h, "From"), header(h, "Subject")
            f.write(json.dumps({
                "id": mid,
                "sender": sender,
                "subject": subject,
                "body": strip_quotes(extract_body(msg["payload"])),
                "thread": "\n\n".join(prior),   # prior messages in the conversation
            }) + "\n")
            rows.append((name_of(sender), subject))

    for nm, subj in rows:
        print(f"   • \033[1m{nm[:22]:22}\033[0m {(subj or '')[:46]}")
    print(f"\n\033[32m✓\033[0m {len(rows)} emails fetched  \033[2m→ data/inbound.jsonl\033[0m\n")


if __name__ == "__main__":
    main()
