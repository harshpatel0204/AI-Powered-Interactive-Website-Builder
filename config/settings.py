import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # OpenRouter settings (used by the multi-agent pipeline)
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")


settings = Settings()
