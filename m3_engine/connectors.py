"""connectors.py — live verification hooks (Stripe / Beehiiv / Calendar).

These are the runtime checks the drafter relies on to answer "did my payment go
through?", "am I registered?", "are you free Tuesday?" without guessing.

Stripe + Beehiiv are wired to their REST APIs (stdlib only, no SDK dep). Each
call degrades safely: if a key is missing or the lookup errors, it returns
{"available": False, ...} so the drafter asks for info or routes to Sid rather
than inventing an answer (per principles). Calendar is still a stub.

Set in .env to enable:
    STRIPE_API_KEY=sk_...
    BEEHIIV_API_KEY=...
    BEEHIIV_PUBLICATION_ID=pub_...   # defaults to JustAnotherPM
"""

import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

STRIPE_API = "https://api.stripe.com/v1"
BEEHIIV_API = "https://api.beehiiv.com/v2"
DEFAULT_PUBLICATION = "pub_f1be7747-60e4-4e55-8206-888ba2c12941"  # JustAnotherPM


def _addr(sender: str) -> str:
    """Pull the bare email out of a 'Name <email>' From header."""
    m = re.search(r"<([^>]+)>", sender or "")
    return (m.group(1) if m else (sender or "")).strip()


def _get(url: str, headers: dict) -> dict:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _date(unix_ts) -> str:
    try:
        return datetime.fromtimestamp(int(unix_ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return ""


def check_stripe_payment(sender: str) -> dict:
    """Look up this person's payments in Stripe by email."""
    key = os.getenv("STRIPE_API_KEY")
    if not key:
        return {"available": False, "reason": "Stripe not configured"}
    email = _addr(sender)
    if not email:
        return {"available": True, "found": False, "reason": "no email to look up"}
    headers = {"Authorization": f"Bearer {key}"}
    try:
        q = urllib.parse.urlencode({"email": email, "limit": 1})
        customers = _get(f"{STRIPE_API}/customers?{q}", headers).get("data", [])
        if not customers:
            return {"available": True, "found": False, "email": email,
                    "reason": "no Stripe customer with this email"}
        cust = customers[0]
        cq = urllib.parse.urlencode({"customer": cust["id"], "limit": 10})
        charges = _get(f"{STRIPE_API}/charges?{cq}", headers).get("data", [])
        paid = [c for c in charges if c.get("paid") and c.get("status") == "succeeded"]
        return {
            "available": True,
            "found": True,
            "email": email,
            "paid_count": len(paid),
            "charges": [
                {
                    "amount": f"{c['amount'] / 100:.2f} {c['currency'].upper()}",
                    "status": c.get("status"),
                    "date": _date(c.get("created")),
                    "description": c.get("description") or "",
                }
                for c in paid
            ],
        }
    except Exception as e:  # network / API error → degrade safely
        return {"available": False, "reason": f"Stripe lookup failed: {str(e)[:80]}"}


def check_beehiiv_registration(sender: str) -> dict:
    """Look up this person's newsletter subscription in Beehiiv by email."""
    key = os.getenv("BEEHIIV_API_KEY")
    if not key:
        return {"available": False, "reason": "Beehiiv not configured"}
    email = _addr(sender)
    if not email:
        return {"available": True, "found": False, "reason": "no email to look up"}
    pub = os.getenv("BEEHIIV_PUBLICATION_ID", DEFAULT_PUBLICATION)
    headers = {"Authorization": f"Bearer {key}"}
    try:
        q = urllib.parse.urlencode({"email": email, "limit": 1})
        subs = _get(f"{BEEHIIV_API}/publications/{pub}/subscriptions?{q}", headers).get("data", [])
        if not subs:
            return {"available": True, "found": False, "email": email,
                    "reason": "not a subscriber"}
        s = subs[0]
        return {
            "available": True,
            "found": True,
            "email": email,
            "status": s.get("status"),
            "tier": s.get("subscription_tier"),
            "subscribed": _date(s.get("created")),
        }
    except Exception as e:
        return {"available": False, "reason": f"Beehiiv lookup failed: {str(e)[:80]}"}


def get_calendar_availability(sender: str = "") -> dict:
    # TODO: query Google Calendar for free/busy.
    return {"available": False, "reason": "Calendar not configured"}


# map handling.yaml tool names -> the check to run
CONNECTORS = {
    "stripe": check_stripe_payment,
    "beehiiv": check_beehiiv_registration,
    "calendar": get_calendar_availability,
}
