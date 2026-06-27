"""extract_emails.py — pull your SENT emails into data/raw_emails.jsonl

This is your voice corpus: the way *you* actually write replies.

Run this once on your own machine. It uses the Gmail API over OAuth, so the
first run opens a browser asking you to grant read-only access. The token is
then cached in data/auth/token.json and reused.

    python extract_emails.py

Output: one JSON object per line in data/raw_emails.jsonl
        {"id", "date", "to", "subject", "body"}
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
LIMIT = int(os.getenv("EXTRACT_LIMIT", "500"))
OUT_PATH = Path("data/raw_emails.jsonl")


def get_service():
    """Authenticate and return a Gmail API client."""
    creds = None
    if Path(TOKEN_PATH).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        Path(TOKEN_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(TOKEN_PATH).write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def extract_body(payload):
    """Walk the MIME tree and return the plaintext body."""
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        raw = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", "ignore")
        return raw
    for part in payload.get("parts", []):
        body = extract_body(part)
        if body:
            return body
    return ""


def clean(body):
    """Strip quoted reply chains and signatures so we keep only YOUR words."""
    lines = []
    for line in body.splitlines():
        if line.strip().startswith(">"):
            continue
        if re.match(r"^On .* wrote:$", line.strip()):
            break
        if line.strip() in ("--", "Sent from my iPhone"):
            break
        lines.append(line)
    return "\n".join(lines).strip()


def main():
    print("Connecting to Gmail...")
    service = get_service()

    print(f"Finding your last {LIMIT} sent emails...")
    ids, token = [], None
    while len(ids) < LIMIT:
        resp = service.users().messages().list(
            userId="me", labelIds=["SENT"], maxResults=min(500, LIMIT - len(ids)),
            pageToken=token,
        ).execute()
        ids.extend(m["id"] for m in resp.get("messages", []))
        token = resp.get("nextPageToken")
        if not token:
            break

    # Make sure data/ exists before we write to it.
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with OUT_PATH.open("w") as f:
        for i, mid in enumerate(ids[:LIMIT], 1):
            msg = service.users().messages().get(userId="me", id=mid, format="full").execute()
            headers = msg["payload"].get("headers", [])
            body = clean(extract_body(msg["payload"]))
            if len(body) < 20:          # skip one-liners / empty bodies
                continue
            record = {
                "id": mid,
                "date": header(headers, "Date"),
                "to": header(headers, "To"),
                "subject": header(headers, "Subject"),
                "body": body,
            }
            f.write(json.dumps(record) + "\n")
            written += 1
            if i % 50 == 0:
                print(f"  ...processed {i} / {len(ids[:LIMIT])}")

    print(f"Done. Wrote {written} sent emails to {OUT_PATH}")


if __name__ == "__main__":
    main()
