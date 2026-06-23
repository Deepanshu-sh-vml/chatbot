"""Pydantic models for API request/response."""

from typing import Optional, List, Any
from pydantic import BaseModel, Field


class TicketRequest(BaseModel):
    """Request body for /api/ticket endpoint."""
    ticket_text: str = Field(..., min_length=1, description="Raw ticket text")


class Stage1Output(BaseModel):
    """Stage 1 classification output."""
    category: str
    confidence: float
    reason: str


class Stage2Output(BaseModel):
    """Stage 2 extraction output."""
    name: Optional[str] = None
    order_id: Optional[str] = None
    product: Optional[str] = None
    issue_summary: Optional[str] = None
    urgency: Optional[str] = None


class Stage3Output(BaseModel):
    """Stage 3 grounding output."""
    behavior: str
    reply_text: str
    citations: List[str]


class Stage4Output(BaseModel):
    """Stage 4 critique output."""
    issues_found: List[str]
    final_reply: str


class PipelineResponse(BaseModel):
    """Full pipeline response."""
    ticket_id: str
    raw_ticket: str
    stage1_classification: Optional[dict] = None
    stage2_extraction: Optional[dict] = None
    stage3_grounded: Optional[dict] = None
    stage4_critique: Optional[dict] = None
    final_reply: str = ""
    timestamp: str


class ManualModeResponse(BaseModel):
    """Response when running in ManualClient mode (no API key)."""
    mode: str = "manual"
    assembled_prompt: str
    message: str = "No LLM key set. Run this prompt manually and resubmit, or set GEMINI_API_KEY."
    stage: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    mode: str  # "manual" or "openai"


class PolicyResponse(BaseModel):
    """Policy passages response."""
    passages: str


class TestTicket(BaseModel):
    """A test ticket from test_set.json."""
    id: int
    raw_ticket: str
    expected_category: str
    expected_behavior: str
    is_ambiguous: bool = False


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    stage: Optional[int] = None
    detail: Optional[str] = None