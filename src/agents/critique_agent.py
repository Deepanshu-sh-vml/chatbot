"""
Stage 4 ADK Agent: Response Critique
"""

from src.schemas import Stage3Output, Stage4Output
from .base import build_agent, load_prompt_content, run_agent


class CritiqueAgent:
    """ADK Agent for Stage 4: Response Critique"""

    def __init__(self):
        self.instruction = load_prompt_content("stage4_critique.v1.md")
        self.agent = build_agent(
            name="response_critic",
            instruction=self.instruction,
            output_schema=Stage4Output,
        )

    async def critique(self, ticket_text: str, stage3_output: Stage3Output) -> Stage4Output:
        """
        Critique and finalize the draft response.

        Args:
            ticket_text: Original support ticket content
            stage3_output: Draft response from Stage 3

        Returns:
            Stage4Output: Critique result with issues_found and final_reply
        """
        try:
            input_data = f"""Original ticket: {ticket_text}

Draft reply: {stage3_output.reply_text}

Citations: {stage3_output.citations}"""
            return await run_agent(self.agent, input_data, Stage4Output)
        except Exception as e:
            raise RuntimeError(f"Stage 4 critique failed: {e}")

    def health_check(self) -> bool:
        """Check if agent is ready."""
        return self.agent is not None
