"""
agents/design_architect.py
Creates a full design specification (colors, fonts, layout) from requirements JSON.
"""

import os
from agents import Agent

from config.settings import settings


def _load_prompt() -> str:
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "prompt", "design_architect_prompt.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def create_design_architect_agent() -> Agent:
    """Create and return the Design Architect agent."""
    return Agent(
        name="Design Architect",
        instructions=_load_prompt(),
        model=settings.OPENROUTER_MODEL,
    )
