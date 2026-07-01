"""
Stage 2 ADK Agent: Information Extraction
"""

from src.schemas import Stage1Output, Stage2Output
from .base import build_agent, load_prompt_content, run_agent


class ExtractAgent:
    """ADK Agent for Stage 2: Information Extraction"""

    def __init__(self):
        self.instruction = load_prompt_content("stage2_extract.v1.md")
        self.agent = build_agent(
            name="info_extractor",
            instruction=self.instruction,
            output_schema=Stage2Output,
        )

    async def extract(self, ticket_text: str, stage1_output: Stage1Output) -> Stage2Output:
        """
        Extract structured information from a support ticket.

        Args:
            ticket_text: Raw support ticket content
            stage1_output: Classification result from Stage 1

        Returns:
            Stage2Output: Extracted information (name, order_id, product, issue_summary, urgency)
        """
        try:
            input_data = f"{ticket_text}\n\nClassification: {stage1_output.category}"
            return await run_agent(self.agent, input_data, Stage2Output)
        except Exception as e:
            raise RuntimeError(f"Stage 2 extraction failed: {e}")

    def health_check(self) -> bool:
        """Check if agent is ready."""
        return self.agent is not None
