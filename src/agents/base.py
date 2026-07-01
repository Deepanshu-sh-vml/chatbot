"""
Shared base utilities for ADK agents.

Centralizes:
- Model name resolution from environment variables
- API key resolution from environment variables
- generate_content_config (temperature, max tokens, JSON schema)
- Agent execution via ADK Runner
"""

import os
import json
import uuid
from pathlib import Path
from typing import Type

from pydantic import BaseModel
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types


# ---------------------------------------------------------------------------
# Configuration (all reference environment variables)
# ---------------------------------------------------------------------------

def get_model_name() -> str:
    """Model name from env. Falls back to GEMINI_MODEL, then a safe default."""
    return os.getenv("ADK_MODEL") or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def get_api_key() -> str:
    """API key from env. Supports GEMINI_API_KEY or GOOGLE_API_KEY."""
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")


def get_temperature() -> float:
    return float(os.getenv("ADK_TEMPERATURE", "0.3"))


def get_max_tokens() -> int:
    return int(os.getenv("ADK_MAX_TOKENS", "3000"))


def _ensure_api_key_env() -> None:
    """
    Ensure google-genai can find the API key.

    google-genai reads GOOGLE_API_KEY natively; mirror GEMINI_API_KEY into it
    if only the latter is set.
    """
    key = get_api_key()
    if key and not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = key


# ---------------------------------------------------------------------------
# Prompt loading
# ---------------------------------------------------------------------------

def load_prompt_content(prompt_file: str) -> str:
    """Load prompt content from prompts/ directory."""
    root = Path(__file__).resolve().parent.parent.parent
    return (root / "prompts" / prompt_file).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Agent construction
# ---------------------------------------------------------------------------

def build_agent(name: str, instruction: str, output_schema: Type[BaseModel]) -> Agent:
    """
    Build an ADK Agent configured for structured JSON output.

    Model name and API key are resolved from environment variables.
    """
    _ensure_api_key_env()

    config = types.GenerateContentConfig(
        temperature=get_temperature(),
        max_output_tokens=get_max_tokens(),
    )

    return Agent(
        name=name,
        model=get_model_name(),
        instruction=instruction,
        output_schema=output_schema,
        generate_content_config=config,
    )


# ---------------------------------------------------------------------------
# Agent execution
# ---------------------------------------------------------------------------

async def run_agent(agent: Agent, input_text: str, output_schema: Type[BaseModel]) -> BaseModel:
    """
    Run an ADK agent with the given input and parse the result.

    Uses an in-memory session and runner, then returns a validated
    instance of ``output_schema``.
    """
    runner = InMemoryRunner(agent=agent, app_name=agent.name)

    user_id = "pipeline_user"
    session_id = str(uuid.uuid4())
    await runner.session_service.create_session(
        app_name=agent.name, user_id=user_id, session_id=session_id
    )

    message = types.Content(role="user", parts=[types.Part(text=input_text)])

    final_text = ""
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text or ""

    if not final_text:
        raise RuntimeError(f"Agent '{agent.name}' returned no output")

    parsed = json.loads(final_text)
    return output_schema(**parsed)
