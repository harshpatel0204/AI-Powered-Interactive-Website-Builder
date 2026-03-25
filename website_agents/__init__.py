"""
website_agents/__init__.py
Initializes the shared OpenRouter client for all agents via the OpenAI Agents SDK.
"""

import os

from openai import AsyncOpenAI
from agents import set_default_openai_client  # from openai-agents SDK package
from agents.tracing import set_tracing_disabled  # disable OpenAI tracing endpoint

from config.settings import settings


def initialize_openrouter_client() -> AsyncOpenAI:
    """
    Create and register the OpenRouter-backed AsyncOpenAI client with the Agents SDK.

    Also disables the SDK's built-in tracing, which would otherwise try to POST
    traces to api.openai.com using the OpenRouter key (causing 401 errors).
    """
    # Disable tracing — we use OpenRouter, not OpenAI, so tracing POSTs fail.
    set_tracing_disabled(True)

    # Also set OPENAI_API_KEY in env so the SDK doesn't warn about a missing key.
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = settings.OPENROUTER_API_KEY or "not-used"

    client = AsyncOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
    )
    set_default_openai_client(client)
    return client
