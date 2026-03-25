"""
agents/qa_reviewer.py
Reviews generated HTML for quality, accessibility, and completeness.
"""

import os
from agents import Agent

from config.settings import settings


def _load_prompt() -> str:
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "prompt", "qa_reviewer_prompt.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def create_qa_reviewer_agent() -> Agent:
    """Create and return the QA Reviewer agent."""
    return Agent(
        name="QA Reviewer",
        instructions=_load_prompt(),
        model=settings.OPENROUTER_MODEL,
    )
