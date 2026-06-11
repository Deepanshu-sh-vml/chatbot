"""
Main pipeline orchestration: Stage 1 -> 2 -> 3 -> 4.
"""

import json
from pathlib import Path
from typing import Dict, Any

from src.schemas import (
    Stage1Output,
    Stage2Output,
    Stage3Output,
    Stage4Output,
)
from src.stages import run_stage
from src.llm_client import LLMClient


class PipelineResult:
    """Results from running the complete pipeline."""

    def __init__(self, ticket_id: str, raw_ticket: str):
        self.ticket_id = ticket_id
        self.raw_ticket = raw_ticket
        self.stage1_output: Stage1Output = None
        self.stage2_output: Stage2Output = None
        self.stage3_output: Stage3Output = None
        self.stage4_output: Stage4Output = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "ticket_id": self.ticket_id,
            "raw_ticket": self.raw_ticket,
            "stage1": self.stage1_output.dict() if self.stage1_output else None,
            "stage2": self.stage2_output.dict() if self.stage2_output else None,
            "stage3": self.stage3_output.dict() if self.stage3_output else None,
            "stage4": self.stage4_output.dict() if self.stage4_output else None,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


def run_pipeline(
    ticket_id: str,
    raw_ticket: str,
    llm_client: LLMClient,
    save_output: bool = True,
    output_dir: str = "outputs",
) -> PipelineResult:
    """
    Run the full 4-stage pipeline on a ticket.
    
    Args:
        ticket_id: Unique identifier for the ticket
        raw_ticket: Raw ticket text
        llm_client: LLM client to use
        save_output: Whether to save JSON output
        output_dir: Directory for output files
        
    Returns:
        PipelineResult with all stage outputs
    """
    result = PipelineResult(ticket_id, raw_ticket)
    
    try:
        # Stage 1: Classify
        print(f"\n[Stage 1] Classifying ticket {ticket_id}...")
        result.stage1_output = run_stage(1, raw_ticket, Stage1Output, llm_client)
        print(f"  -> Category: {result.stage1_output.category} "
              f"(confidence: {result.stage1_output.confidence})")

        # Stage 2: Extract
        print(f"\n[Stage 2] Extracting information...")
        stage2_input = f"{raw_ticket}\n\nClassification: {result.stage1_output.category}"
        result.stage2_output = run_stage(2, stage2_input, Stage2Output, llm_client)
        print(f"  -> Order ID: {result.stage2_output.order_id}, "
              f"Name: {result.stage2_output.name}")

        # Stage 3: Ground in policy
        print(f"\n[Stage 3] Grounding in policy...")
        stage3_input = (
            f"Ticket: {raw_ticket}\n\n"
            f"Category: {result.stage1_output.category}\n"
            f"Extracted info: {result.stage2_output.json()}"
        )
        result.stage3_output = run_stage(3, stage3_input, Stage3Output, llm_client)
        print(f"  -> Behavior: {result.stage3_output.behavior}")
        print(f"  -> Reply: {result.stage3_output.reply_text[:80]}...")
        print(f"  -> Citations: {result.stage3_output.citations}")

        # Stage 4: Critique
        print(f"\n[Stage 4] Critiquing draft...")
        stage4_input = (
            f"Original ticket: {raw_ticket}\n\n"
            f"Draft reply: {result.stage3_output.reply_text}\n\n"
            f"Citations: {result.stage3_output.citations}"
        )
        result.stage4_output = run_stage(4, stage4_input, Stage4Output, llm_client)
        print(f"  -> Issues found: {len(result.stage4_output.issues_found)}")
        if result.stage4_output.issues_found:
            for issue in result.stage4_output.issues_found:
                print(f"    - {issue}")

        # Save output
        if save_output:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            output_file = output_path / f"{ticket_id}_output.json"
            output_file.write_text(result.to_json())
            print(f"\n[Output] Saved to {output_file}")

    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}")
        raise

    return result
