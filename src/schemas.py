"""
Pydantic models for each stage's JSON output.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


class CategoryEnum(str, Enum):
    """Valid ticket categories."""
    billing = "billing"
    account = "account"
    technical = "technical"
    other = "other"


class Stage1Output(BaseModel):
    """Stage 1: Classify output."""
    category: CategoryEnum = Field(..., description="One of: billing, account, technical, other")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence 0.0-1.0")
    reason: str = Field(..., description="Brief explanation of classification")


class UrgencyEnum(str, Enum):
    """Urgency levels."""
    low = "low"
    medium = "medium"
    high = "high"


class Stage2Output(BaseModel):
    """Stage 2: Extract information."""
    name: Optional[str] = Field(None, description="Customer name or None")
    order_id: Optional[str] = Field(None, description="Order ID or None")
    product: Optional[str] = Field(None, description="Product mentioned or None")
    issue_summary: Optional[str] = Field(None, description="Issue in <= 15 words or None")
    urgency: Optional[UrgencyEnum] = Field(None, description="Urgency level or None")


class BehaviorEnum(str, Enum):
    """Stage 3 behavior options."""
    grounded_reply = "grounded_reply"
    grounded_denial = "grounded_denial"
    escalate = "escalate"


class Stage3Output(BaseModel):
    """Stage 3: Ground in policy."""
    behavior: BehaviorEnum = Field(..., description="One of: grounded_reply, grounded_denial, escalate")
    reply_text: str = Field(..., description="Reply text, <= 120 words")
    citations: List[str] = Field(default_factory=list, description="List of [P#] citations")


class Stage4Output(BaseModel):
    """Stage 4: Critique the draft."""
    issues_found: List[str] = Field(default_factory=list, description="List of issues or empty")
    final_reply: str = Field(..., description="Final reviewed reply")


class TestCase(BaseModel):
    """A test ticket case."""
    id: int
    raw_ticket: str
    expected_category: CategoryEnum
    expected_fields: dict  # extracted fields expected
    expected_behavior: BehaviorEnum
    is_ambiguous: bool = False
    notes: str = ""
