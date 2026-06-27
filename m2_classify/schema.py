"""schema.py — the typed result of classifying one incoming email (M2).

Every classification is validated against this before it flows to M3, so a
malformed agent response fails loudly instead of poisoning the pipeline.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Urgency(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Classification(BaseModel):
    category: str = Field(..., description="One of the M1 categories, or 'uncertain'")
    confidence: float = Field(..., ge=0.0, le=1.0)
    intent: str = Field(..., description="One line: what the sender actually wants")
    urgency: Urgency = Field(...)
    needs_human: bool = Field(..., description="True → route to Sid, don't auto-draft")
    reply_needed: bool = Field(..., description="False → automated / no-reply mail")

    # carried through from the source email for the dashboard / drafter
    id: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None
    snippet: Optional[str] = None       # short, for display
    body: Optional[str] = None          # FULL incoming message — the drafter reads this
    thread: Optional[str] = None        # prior conversation context (what came before)

    # attached from the category handling map (R3.3)
    default_action: Optional[str] = None
    tools: Optional[list] = None


def parse_classification(data: dict) -> Classification:
    return Classification(**data)
