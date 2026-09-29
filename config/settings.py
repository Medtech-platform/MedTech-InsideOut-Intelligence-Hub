"""Application-wide configuration loaded from environment / .env file."""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the config directory or project root
load_dotenv(Path(__file__).parent / ".env")
load_dotenv()  # fallback: project root .env


class Settings:
    # LLM
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "8192"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.2"))

    # Search
    SERP_API_KEY: str = os.getenv("SERP_API_KEY", "")
    BRAVE_SEARCH_API_KEY: str = os.getenv("BRAVE_SEARCH_API_KEY", "")

    # Output
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "./outputs"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Agent behaviour
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "2.0"))

    def validate(self) -> None:
        if not self.ANTHROPIC_API_KEY:
            raise EnvironmentError("ANTHROPIC_API_KEY is not set.")
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
