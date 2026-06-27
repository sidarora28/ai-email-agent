"""fetch_pairs.py — M1 Step 1: build the voice corpus as PAIRS.

For each of my recent sent replies, capture the reply IN FULL plus the one
message I was replying to. Voice is a reaction to context, so we store both:

    {"incoming": {from, subject, date, body}, "reply": {date, body}}

Output: data/voice_pairs.jsonl  (one pair per line)

Run on your Mac (uses Gmail OAuth, read-only):

    python m1_voice/fetch_pairs.py

Requirements satisfied: R1.1 (full replies), R1.2 (substantive only),
R1.3 (one prior message), R1.4 (clean pairs).
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
LIMIT = int(os.getenv("VOICE_PAIRS_LIMIT", "200"))
MIN_REPLY_CHARS = int(os.getenv("MIN_REPLY_CHARS", "200"))
OUT = Path(os.getenv("VOICE_PAIRS", "data/voice_pairs.jsonl"))


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
        Path(TOKEN_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(TOKEN_PATH).write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def extract_body(payload):
    """Return the plaintext body from a message payload (walks MIME parts)."""
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", "ignore")
    for part in payload.get("parts", []):
        body = extract_body(part)
        if body:
            return body
    return ""


def strip_quotes(body):
    """Keep only the new text — drop quoted reply chains and signatures."""
    lines = []
    for line in body.splitlines():
        if line.strip().startswith(">"):
            continue
        if re.match(r"^On .* wrote:$", line.strip()):
            break
        if line.strip() in ("--", "Sent from my iPhone"):
            break
        lines.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def message_fields(msg):
    headers = msg["payload"].get("headers", [])
    return {
        "from": header(headers, "From"),
        "to": header(headers, "To"),
        "subject": header(headers, "Subject"),
        "date": header(headers, "Date"),
        "body": strip_quotes(extract_body(msg["payload"])),
        "internalDate": int(msg.get("internalDate", "0")),
    }


def main():
    print("Connecting to Gmail ...")
    service = get_service()
    me = service.users().getProfile(userId="me").execute()["emailAddress"]
    print(f"  authenticated as {me}")

    print(f"Scanning sent mail for up to {LIMIT} substantive reply pairs ...")
    pairs, token, scanned = [], None, 0
    while len(pairs) < LIMIT:
        resp = service.users().messages().list(
            userId="me", labelIds=["SENT"], maxResults=100, pageToken=token,
        ).execute()
        for m in resp.get("messages", []):
            scanned += 1
            sent = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
            reply = message_fields(sent)
            if len(reply["body"]) < MIN_REPLY_CHARS:
                continue  # R1.2: skip one-liners / trivial

            # R1.3: find the single message I was replying to (the one just before
            # my reply in the same thread).
            thread = service.users().threads().get(userId="me", id=sent["threadId"], format="full").execute()
            msgs = sorted(
                (message_fields(t) for t in thread["messages"]),
                key=lambda x: x["internalDate"],
            )
            incoming = None
            for t in msgs:
                if t["internalDate"] >= reply["internalDate"]:
                    break
                incoming = t
            if not incoming or len(incoming["body"]) < 20:
                continue  # need real context to learn from

            pairs.append({
                "id": m["id"],
                "incoming": {k: incoming[k] for k in ("from", "subject", "date", "body")},
                "reply": {k: reply[k] for k in ("date", "body")},
            })
            if len(pairs) % 25 == 0:
                print(f"  ...{len(pairs)} pairs (scanned {scanned} sent)")
            if len(pairs) >= LIMIT:
                break
        token = resp.get("nextPageToken")
        if not token:
            break

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        for p in pairs:
            f.write(json.dumps(p) + "\n")
    print(f"Done. Wrote {len(pairs)} voice pairs to {OUT}")


if __name__ == "__main__":
    main()
