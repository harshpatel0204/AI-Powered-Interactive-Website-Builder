"""
agents/requirements_analyst.py
Transforms raw Q&A answers into a structured requirements JSON using OpenAI Agents SDK.
"""

import os
from agents import Agent

from config.settings import settings


def _load_prompt() -> str:
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "prompt", "requirements_analyst_prompt.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def create_requirements_analyst_agent() -> Agent:
    """Create and return the Requirements Analyst agent."""
    return Agent(
        name="Requirements Analyst",
        instructions=_load_prompt(),
        model=settings.OPENROUTER_MODEL,
    )
