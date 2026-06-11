"""
Stage prompt templates and execution logic.
"""

import json
import re
from pathlib import Path
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def load_prompt_template(stage_num: int, version: str = "v1") -> str:
    """Load a stage prompt template."""
    prompt_dir = Path(__file__).parent.parent / "prompts"
    prompt_file = prompt_dir / f"stage{stage_num}_*.{version}.md"
    
    # Find the file matching the pattern
    matching_files = list(prompt_dir.glob(f"stage{stage_num}_*.{version}.md"))
    if not matching_files:
        raise FileNotFoundError(f"Prompt file not found for stage {stage_num} v{version}")
    
    return matching_files[0].read_text()


def sanitize_ticket_input(raw_ticket: str) -> str:
    """
    Strip/neutralize injected instructions in ticket text.
    Ticket is DATA, not instructions.
    """
    # Remove common injection patterns
    injection_patterns = [
        r"ignore.*instructions",
        r"disregard.*policy",
        r"forget.*previous",
    ]
    sanitized = raw_ticket
    for pattern in injection_patterns:
        sanitized = re.sub(pattern, "[instruction attempt removed]", sanitized, flags=re.IGNORECASE)
    return sanitized


def extract_json_from_response(response: str) -> dict:
    """
    Extract JSON from response text, handling markdown code blocks.
    """
    # Try to extract from markdown code block first
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(1))
    
    # Try to find JSON object directly
    json_match = re.search(r"\{.*?\}", response, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))
    
    # If no JSON found, raise error
    raise ValueError(f"No JSON found in response: {response[:200]}")


def parse_stage_output(
    response: str,
    output_schema: Type[T],
    stage_num: int,
    llm_client=None,
) -> T:
    """
    Parse and validate stage output with robust error handling.
    
    Args:
        response: Raw LLM response
        output_schema: Pydantic model to validate against
        stage_num: Stage number for error reporting
        llm_client: Optional LLM client for retry
        
    Returns:
        Validated output object
    """
    try:
        json_data = extract_json_from_response(response)
        return output_schema(**json_data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Stage {stage_num}: JSON extraction failed: {e}")
        if llm_client:
            print(f"Retrying with repair instruction...")
            repair_prompt = (
                "The previous response was not valid JSON. "
                "Return ONLY a valid JSON object, no markdown, no explanation."
            )
            retry_response = llm_client.call(repair_prompt, response)
            try:
                json_data = extract_json_from_response(retry_response)
                return output_schema(**json_data)
            except Exception as retry_error:
                raise RuntimeError(
                    f"Stage {stage_num}: JSON parsing failed even after retry. "
                    f"Original error: {e}, Retry error: {retry_error}"
                )
        else:
            raise RuntimeError(f"Stage {stage_num}: JSON parsing failed: {e}")
    except ValidationError as e:
        raise RuntimeError(f"Stage {stage_num}: Validation error: {e}")


def run_stage(
    stage_num: int,
    input_text: str,
    output_schema: Type[T],
    llm_client,
    prompt_version: str = "v1",
) -> T:
    """
    Execute a single stage: load prompt, call LLM, parse output.
    """
    # Load prompt template
    prompt = load_prompt_template(stage_num, prompt_version)
    
    # Sanitize input for stage 1
    if stage_num == 1:
        input_text = sanitize_ticket_input(input_text)
    
    # Call LLM
    response = llm_client.call(prompt, input_text)
    
    # Parse and validate
    return parse_stage_output(response, output_schema, stage_num, llm_client)
