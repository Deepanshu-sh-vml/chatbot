"""API routes for the Northwind Support Co-pilot."""

import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Any, Dict

from fastapi import APIRouter, HTTPException
from src.pipeline import run_pipeline
from src.llm_client import get_llm_client, ManualClient

# ADK Pipeline imports (only imported if ADK is enabled)
try:
    from src.agents.workflow import run_adk_pipeline, get_workflow
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    print("Warning: ADK not available. Install google-adk to enable ADK pipeline mode.")

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
        data = json.load(f)
        # Handle nested structure: {"tickets": [...]}
        if isinstance(data, dict) and "tickets" in data:
            return data["tickets"]
        return data


def use_adk_pipeline() -> bool:
    """Check if ADK pipeline should be used based on environment variable."""
    return (
        ADK_AVAILABLE and 
        os.getenv("USE_ADK_PIPELINE", "false").lower() in ("true", "1", "yes")
    )


def is_simple_greeting(text: str) -> bool:
    """Check if the message is a simple greeting that doesn't need full pipeline."""
    text_lower = text.lower().strip()
    
    # Simple greetings
    greetings = [
        "hi", "hello", "hey", "hii", "hiii", "hello there", "hi there",
        "good morning", "good afternoon", "good evening", "good day",
        "greetings", "howdy", "what's up", "sup", "hlo", "hllo"
    ]
    
    # Check if the entire message is just a greeting (with optional punctuation)
    cleaned_text = text_lower.rstrip('!.?').strip()
    
    return cleaned_text in greetings or any(
        cleaned_text == greeting for greeting in greetings
    )


def create_greeting_response(ticket_id: str, raw_ticket: str) -> PipelineResponse:
    """Create a greeting response without running the full pipeline."""
    greeting_reply = "Hello! Welcome to Northwind Support. How can I assist you today? Feel free to describe your issue or question."
    
    return PipelineResponse(
        ticket_id=ticket_id,
        raw_ticket=raw_ticket,
        stage1_classification={"category": "greeting", "confidence": 1.0, "reason": "Simple greeting detected"},
        stage2_extraction={"name": None, "order_id": None, "product": None, "issue_summary": "Greeting", "urgency": "low"},
        stage3_grounded={"behavior": "grounded_reply", "reply_text": greeting_reply, "citations": []},
        stage4_critique={"issues_found": [], "final_reply": greeting_reply},
        final_reply=greeting_reply,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


async def run_pipeline_dual_mode(ticket_id: str, raw_ticket: str, save_output: bool = True, output_dir: str = "outputs"):
    """
    Run either legacy or ADK pipeline based on configuration.
    
    Returns the same PipelineResult format for compatibility.
    """
    if use_adk_pipeline():
        # Use ADK pipeline
        print(f"[DUAL MODE] Using ADK pipeline for ticket {ticket_id}")
        return await run_adk_pipeline(
            ticket_id=ticket_id,
            raw_ticket=raw_ticket,
            save_output=save_output,
            output_dir=output_dir
        )
    else:
        # Use legacy pipeline
        print(f"[DUAL MODE] Using legacy pipeline for ticket {ticket_id}")
        llm_client = get_llm_client()
        
        # Check if in manual mode
        if isinstance(llm_client, ManualClient):
            raise HTTPException(
                status_code=400,
                detail="ManualClient mode active. Set GEMINI_API_KEY to use automatic mode.",
            )
        
        return run_pipeline(
            ticket_id=ticket_id,
            raw_ticket=raw_ticket,
            llm_client=llm_client,
            save_output=save_output,
            output_dir=output_dir
        )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    llm_client = get_llm_client()
    
    # Determine LLM mode
    if isinstance(llm_client, ManualClient):
        llm_mode = "manual"
    else:
        llm_mode = "gemini"
    
    # Determine pipeline mode
    if use_adk_pipeline():
        pipeline_mode = "adk"
        # Check ADK workflow health if available
        try:
            workflow = get_workflow()
            adk_healthy = workflow.health_check()
            mode = f"{llm_mode}+{pipeline_mode}" if adk_healthy else f"{llm_mode}+{pipeline_mode}(unhealthy)"
        except Exception:
            mode = f"{llm_mode}+{pipeline_mode}(error)"
    else:
        pipeline_mode = "legacy"
        mode = f"{llm_mode}+{pipeline_mode}"
    
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
        # Generate a ticket ID based on timestamp
        ticket_id = f"custom_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        # Check for simple greetings first
        if is_simple_greeting(request.ticket_text):
            print(f"[GREETING] Detected simple greeting for ticket {ticket_id}")
            return create_greeting_response(ticket_id, request.ticket_text)
        
        # Run pipeline (dual mode: legacy or ADK based on environment)
        result = await run_pipeline_dual_mode(
            ticket_id=ticket_id,
            raw_ticket=request.ticket_text,
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
        
        # Check for simple greetings first
        if is_simple_greeting(ticket["raw_ticket"]):
            print(f"[GREETING] Detected simple greeting for test ticket {ticket_id}")
            return create_greeting_response(str(ticket_id), ticket["raw_ticket"])
        
        # Run pipeline (dual mode: legacy or ADK based on environment)
        result = await run_pipeline_dual_mode(
            ticket_id=str(ticket_id),
            raw_ticket=ticket["raw_ticket"],
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