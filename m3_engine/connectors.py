"""connectors.py — live verification hooks (Stripe / Beehiiv / Calendar).

These are the runtime checks the drafter relies on to answer "did my payment go
through?", "am I registered?", "are you free Tuesday?" without guessing.

STATUS: stubbed. Each returns {"available": False} so the engine degrades safely
— if a needed check isn't wired, the draft asks for info or routes to Sid rather
than inventing an answer (per principles). Wire your API keys here to enable.
"""

import os


def check_stripe_payment(email: str) -> dict:
    # TODO: query Stripe for a payment from this email.
    if not os.getenv("STRIPE_API_KEY"):
        return {"available": False, "reason": "Stripe not configured"}
    return {"available": False, "reason": "not implemented"}


def check_beehiiv_registration(email: str) -> dict:
    # TODO: query Beehiiv for this subscriber / whether a confirmation was sent.
    if not os.getenv("BEEHIIV_API_KEY"):
        return {"available": False, "reason": "Beehiiv not configured"}
    return {"available": False, "reason": "not implemented"}


def get_calendar_availability() -> dict:
    # TODO: query Google Calendar for free/busy.
    return {"available": False, "reason": "Calendar not configured"}


# map handling.yaml tool names -> the check to run
CONNECTORS = {
    "stripe": check_stripe_payment,
    "beehiiv": check_beehiiv_registration,
    "calendar": lambda email=None: get_calendar_availability(),
}
