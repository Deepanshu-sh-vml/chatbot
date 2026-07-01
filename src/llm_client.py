"""
LLM Client abstraction with ManualClient and OpenAIClient implementations.
"""

import os
from abc import ABC, abstractmethod
from typing import Optional
import json


class LLMClient(ABC):
    """Abstract base class for LLM interactions."""

    @abstractmethod
    def call(self, prompt: str, input_text: str) -> str:
        """
        Call the LLM with a prompt and input.
        
        Args:
            prompt: The system/template prompt
            input_text: The user input (e.g., ticket text)
            
        Returns:
            The LLM's response (should be valid JSON)
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify the client is ready."""
        pass


class ManualClient(LLMClient):
    """Tier 0: Manual client—prints prompt+input, waits for pasted response."""

    def call(self, prompt: str, input_text: str) -> str:
        """
        Display prompt and input, wait for manual response.
        """
        print("\n" + "=" * 80)
        print("MANUAL CLIENT MODE (No API Key)")
        print("=" * 80)
        print("\n--- PROMPT ---")
        print(prompt)
        print("\n--- INPUT ---")
        print(input_text)
        print("\n" + "=" * 80)
        print("Paste the JSON response from ChatGPT/LLM below and press ENTER twice:")
        print("=" * 80 + "\n")

        lines = []
        blank_count = 0
        while blank_count < 1:
            line = input()
            if line.strip() == "":
                blank_count += 1
            else:
                blank_count = 0
                lines.append(line)

        return "\n".join(lines)

    def health_check(self) -> bool:
        """Manual client is always ready."""
        return True


class GEMINIClient(LLMClient):
    """Tier 1: GEMINI API client (works with OpenAI, Gemini, or Ollama)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize a GEMINI-compatible client (works with OpenAI, Gemini, or Ollama).

        Args:
            api_key:  API key (reads from GEMINI_API_KEY env if None)
            model:    Model name (reads from GEMINI_MODEL env if None)
            base_url: API endpoint (reads from GEMINI_BASE_URL env if None)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.base_url = base_url or os.getenv(
            "GEMINI_BASE_URL", "https://api.gemini.com/v1"
        )

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or arguments")

    def call(self, prompt: str, input_text: str) -> str:
        """
        Call an GEMINI-compatible Chat Completions API (works with OpenAI, Gemini, or Ollama).
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed. Install via: pip install openai")

        # Build a client that can point to OpenAI OR Gemini OR Ollama via base_url
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": input_text},
                ],
                temperature=0.3,
                max_tokens=3000,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"API call failed: {e}")

    def health_check(self) -> bool:
        """Check if API key is valid."""
        return bool(self.api_key)


def get_llm_client() -> LLMClient:
    """
    Auto-select LLM client: GEMINI if key present, else Manual.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            return GEMINIClient(api_key=api_key)
        except Exception as e:
            print(f"Warning: Failed to initialize GEMINI client ({e}), falling back to ManualClient")
            return ManualClient()
    else:
        print("No GEMINI_API_KEY found. Using ManualClient.")
        return ManualClient()