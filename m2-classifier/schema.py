"""schema.py — the typed shape of a classified email.

Every classification the agent produces is validated against this. If the
agent returns malformed JSON, validation fails loudly instead of silently
feeding garbage into the dashboard.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Urgency(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Classification(BaseModel):
    """One classified email."""

    category: str = Field(..., description="One of the categories in categories.yaml")
    urgency: Urgency = Field(..., description="high / medium / low")
    suggested_action: str = Field(..., description="Short next step, e.g. 'reply', 'archive'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="0.0-1.0 model confidence")

    # carried through from the source email so the dashboard can render it
    id: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None
    snippet: Optional[str] = None


def parse_classification(data: dict) -> Classification:
    """Validate a raw dict (e.g. parsed agent JSON) into a Classification."""
    return Classification(**data)
