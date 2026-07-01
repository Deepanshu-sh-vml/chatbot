"""
ADK Workflow: Orchestrates the 4-agent pipeline
"""

import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

from .classify_agent import ClassifyAgent
from .extract_agent import ExtractAgent
from .ground_agent import GroundAgent
from .critique_agent import CritiqueAgent

# Import the existing PipelineResult class to maintain compatibility
from src.pipeline import PipelineResult


class NorthwindSupportWorkflow:
    """
    ADK-based workflow that orchestrates all 4 agents.
    Maintains the same interface as the legacy run_pipeline function.
    """
    
    def __init__(self):
        """Initialize all 4 agents."""
        self.classify_agent = ClassifyAgent()
        self.extract_agent = ExtractAgent()
        self.ground_agent = GroundAgent()
        self.critique_agent = CritiqueAgent()
        
    async def run_pipeline(
        self,
        ticket_id: str,
        raw_ticket: str,
        save_output: bool = True,
        output_dir: str = "outputs",
    ) -> PipelineResult:
        """
        Run the complete ADK-based pipeline.
        
        Args:
            ticket_id: Unique identifier for the ticket
            raw_ticket: Raw support ticket content
            save_output: Whether to save results to disk
            output_dir: Directory to save output files
            
        Returns:
            PipelineResult: Same format as legacy pipeline for compatibility
        """
        result = PipelineResult(ticket_id, raw_ticket)
        
        try:
            # Stage 1: Classify
            print(f"\n[ADK Stage 1] Classifying ticket {ticket_id}...")
            start_time = time.time()
            result.stage1_output = await self.classify_agent.classify(raw_ticket)
            stage1_time = time.time() - start_time
            print(f"  -> Category: {result.stage1_output.category} "
                  f"(confidence: {result.stage1_output.confidence}) [{stage1_time:.2f}s]")

            # Stage 2: Extract
            print(f"\n[ADK Stage 2] Extracting information...")
            start_time = time.time()
            result.stage2_output = await self.extract_agent.extract(raw_ticket, result.stage1_output)
            stage2_time = time.time() - start_time
            print(f"  -> Order ID: {result.stage2_output.order_id}, "
                  f"Name: {result.stage2_output.name} [{stage2_time:.2f}s]")

            # Stage 3: Ground in policy
            print(f"\n[ADK Stage 3] Grounding in policy...")
            start_time = time.time()
            result.stage3_output = await self.ground_agent.ground(raw_ticket, result.stage1_output, result.stage2_output)
            stage3_time = time.time() - start_time
            print(f"  -> Behavior: {result.stage3_output.behavior} [{stage3_time:.2f}s]")
            print(f"  -> Reply: {result.stage3_output.reply_text[:50]}...")

            # Stage 4: Critique
            print(f"\n[ADK Stage 4] Critiquing draft...")
            start_time = time.time()
            result.stage4_output = await self.critique_agent.critique(raw_ticket, result.stage3_output)
            stage4_time = time.time() - start_time
            print(f"  -> Issues found: {len(result.stage4_output.issues_found)} [{stage4_time:.2f}s]")
            if result.stage4_output.issues_found:
                for issue in result.stage4_output.issues_found:
                    print(f"    - {issue}")

            # Save output (same as legacy pipeline)
            if save_output:
                output_path = Path(output_dir)
                output_path.mkdir(exist_ok=True)
                output_file = output_path / f"{ticket_id}_output.json"
                output_file.write_text(result.to_json())
                print(f"\n[ADK Output] Saved to {output_file}")

        except Exception as e:
            print(f"\n[ADK ERROR] Pipeline failed: {e}")
            raise

        return result
    
    def health_check(self) -> bool:
        """Check if all agents are ready."""
        return all([
            self.classify_agent.health_check(),
            self.extract_agent.health_check(),
            self.ground_agent.health_check(),
            self.critique_agent.health_check()
        ])


# For backward compatibility, create a function that matches the legacy interface
async def run_adk_pipeline(
    ticket_id: str,
    raw_ticket: str,
    save_output: bool = True,
    output_dir: str = "outputs",
) -> PipelineResult:
    """
    ADK pipeline function that matches the legacy run_pipeline interface.
    
    This function can be used as a drop-in replacement for the legacy pipeline.
    """
    workflow = NorthwindSupportWorkflow()
    return await workflow.run_pipeline(ticket_id, raw_ticket, save_output, output_dir)


# Global workflow instance (initialized on first use)
_workflow_instance: Optional[NorthwindSupportWorkflow] = None

def get_workflow() -> NorthwindSupportWorkflow:
    """Get or create the global workflow instance."""
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = NorthwindSupportWorkflow()
    return _workflow_instance
