"""
agents/update_handler.py
Applies user-requested changes to an existing HTML website.
"""

import os
from agents import Agent

from config.settings import settings


def _load_prompt() -> str:
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "prompt", "update_handler_prompt.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def create_update_handler_agent() -> Agent:
    """Create and return the Update Handler agent."""
    return Agent(
        name="Update Handler",
        instructions=_load_prompt(),
        model=settings.OPENROUTER_MODEL,
    )
