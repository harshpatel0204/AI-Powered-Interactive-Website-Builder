import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL")
    GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL")

settings = Settings()
