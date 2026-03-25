"""
agents/code_generator.py
Generates complete, production-ready HTML/CSS website from design specification.
"""

import os
from agents import Agent

from config.settings import settings


def _load_prompt() -> str:
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "prompt", "code_generator_prompt.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def create_code_generator_agent() -> Agent:
    """Create and return the Code Generator agent."""
    return Agent(
        name="Code Generator",
        instructions=_load_prompt(),
        model=settings.OPENROUTER_MODEL,
    )
