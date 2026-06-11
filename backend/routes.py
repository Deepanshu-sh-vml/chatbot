"""API routes for the Northwind Support Co-pilot."""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Any, Dict

from fastapi import APIRouter, HTTPException
from src.pipeline import run_pipeline
from src.llm_client import get_llm_client, ManualClient
from backend.models import (
    TicketRequest,
    PipelineResponse,
    HealthResponse,
    PolicyResponse,
    TestTicket,
)

router = APIRouter(prefix="/api", tags=["pipeline"])


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent


def load_policy() -> str:
    """Load policy.md from data/."""
    policy_file = get_project_root() / "data" / "policy.md"
    if not policy_file.exists():
        raise FileNotFoundError(f"Policy file not found: {policy_file}")
    return policy_file.read_text(encoding="utf-8")


def load_test_tickets() -> List[Dict[str, Any]]:
    """Load test_set.json from data/."""
    test_file = get_project_root() / "data" / "test_set.json"
    if not test_file.exists():
        raise FileNotFoundError(f"Test set file not found: {test_file}")
    with open(test_file, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    llm_client = get_llm_client()
    mode = "manual" if isinstance(llm_client, ManualClient) else "openai"
    return HealthResponse(status="ok", mode=mode)


@router.get("/policy", response_model=PolicyResponse)
async def get_policy() -> PolicyResponse:
    """Return policy passages [P1]-[P8]."""
    try:
        policy = load_policy()
        return PolicyResponse(passages=policy)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/tickets", response_model=List[TestTicket])
async def get_test_tickets() -> List[TestTicket]:
    """Return the 14 test tickets."""
    try:
        tickets = load_test_tickets()
        return [TestTicket(**t) for t in tickets]
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ticket", response_model=PipelineResponse)
async def run_on_custom_ticket(request: TicketRequest) -> PipelineResponse:
    """
    Run the full pipeline on a custom ticket.
    
    Body: {"ticket_text": "I was charged twice..."}
    """
    try:
        llm_client = get_llm_client()
        
        # Check if in manual mode
        if isinstance(llm_client, ManualClient):
            raise HTTPException(
                status_code=400,
                detail="ManualClient mode active. Set OPENAI_API_KEY to use automatic mode.",
            )
        
        # Generate a ticket ID based on timestamp
        ticket_id = f"custom_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        # Run pipeline
        result = run_pipeline(
            ticket_id=ticket_id,
            raw_ticket=request.ticket_text,
            llm_client=llm_client,
            save_output=True,
            output_dir=str(get_project_root() / "outputs"),
        )
        
        # Build response
        return PipelineResponse(
            ticket_id=result.ticket_id,
            raw_ticket=result.raw_ticket,
            stage1_classification=result.stage1_output.model_dump() if result.stage1_output else None,
            stage2_extraction=result.stage2_output.model_dump() if result.stage2_output else None,
            stage3_grounded=result.stage3_output.model_dump() if result.stage3_output else None,
            stage4_critique=result.stage4_output.model_dump() if result.stage4_output else None,
            final_reply=result.stage4_output.final_reply if result.stage4_output else "",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.post("/ticket/{ticket_id}", response_model=PipelineResponse)
async def run_on_test_ticket(ticket_id: int) -> PipelineResponse:
    """
    Run the pipeline on a test-set ticket by ID.
    
    Path param: ticket_id (1-14)
    """
    try:
        tickets = load_test_tickets()
        ticket = next((t for t in tickets if t["id"] == ticket_id), None)
        
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        
        llm_client = get_llm_client()
        
        if isinstance(llm_client, ManualClient):
            raise HTTPException(
                status_code=400,
                detail="ManualClient mode active. Set OPENAI_API_KEY to use automatic mode.",
            )
        
        result = run_pipeline(
            ticket_id=str(ticket_id),
            raw_ticket=ticket["raw_ticket"],
            llm_client=llm_client,
            save_output=True,
            output_dir=str(get_project_root() / "outputs"),
        )
        
        return PipelineResponse(
            ticket_id=result.ticket_id,
            raw_ticket=result.raw_ticket,
            stage1_classification=result.stage1_output.model_dump() if result.stage1_output else None,
            stage2_extraction=result.stage2_output.model_dump() if result.stage2_output else None,
            stage3_grounded=result.stage3_output.model_dump() if result.stage3_output else None,
            stage4_critique=result.stage4_output.model_dump() if result.stage4_output else None,
            final_reply=result.stage4_output.final_reply if result.stage4_output else "",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")