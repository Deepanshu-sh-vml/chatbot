"""
Stage 3 ADK Agent: Policy Grounding
"""

from pathlib import Path

from src.schemas import Stage1Output, Stage2Output, Stage3Output
from .base import build_agent, load_prompt_content, run_agent


def load_policy_content() -> str:
    """Load policy content from data/policy.md"""
    root = Path(__file__).resolve().parent.parent.parent
    return (root / "data" / "policy.md").read_text(encoding="utf-8")


class GroundAgent:
    """ADK Agent for Stage 3: Policy Grounding"""

    def __init__(self):
        self.instruction = load_prompt_content("stage3_ground.v1.md")
        self.policy_content = load_policy_content()
        self.agent = build_agent(
            name="policy_grounder",
            instruction=self.instruction,
            output_schema=Stage3Output,
        )

    async def ground(self, ticket_text: str, stage1_output: Stage1Output, stage2_output: Stage2Output) -> Stage3Output:
        """
        Ground ticket in policy and draft response.

        Args:
            ticket_text: Raw support ticket content
            stage1_output: Classification result from Stage 1
            stage2_output: Extracted information from Stage 2

        Returns:
            Stage3Output: Grounding result with behavior, reply_text, citations
        """
        try:
            input_data = f"""Ticket: {ticket_text}

Category: {stage1_output.category}
Extracted info: {stage2_output.model_dump_json()}

Policy:
{self.policy_content}"""
            return await run_agent(self.agent, input_data, Stage3Output)
        except Exception as e:
            raise RuntimeError(f"Stage 3 grounding failed: {e}")

    def health_check(self) -> bool:
        """Check if agent is ready."""
        return self.agent is not None
