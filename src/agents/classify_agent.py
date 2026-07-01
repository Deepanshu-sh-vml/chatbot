"""
Stage 1 ADK Agent: Ticket Classification
"""

from src.schemas import Stage1Output
from .base import build_agent, load_prompt_content, run_agent


class ClassifyAgent:
    """ADK Agent for Stage 1: Ticket Classification"""

    def __init__(self):
        self.instruction = load_prompt_content("stage1_classify.v1.md")
        self.agent = build_agent(
            name="ticket_classifier",
            instruction=self.instruction,
            output_schema=Stage1Output,
        )

    async def classify(self, ticket_text: str) -> Stage1Output:
        """
        Classify a support ticket.

        Args:
            ticket_text: Raw support ticket content

        Returns:
            Stage1Output: Classification result with category, confidence, reason
        """
        try:
            return await run_agent(self.agent, ticket_text, Stage1Output)
        except Exception as e:
            raise RuntimeError(f"Stage 1 classification failed: {e}")

    def health_check(self) -> bool:
        """Check if agent is ready."""
        return self.agent is not None
