"""
BaseAgent — abstract class every domain agent inherits.

Each agent:
  1. Receives a typed input context (Pydantic model or dict)
  2. Calls the LLM (optionally with web-search tool use)
  3. Returns a typed, validated Pydantic output model
  4. Writes its output to the shared state store
"""
from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from loguru import logger
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_fixed

from config.settings import settings
from core.llm_client import LLMClient
from core.state_manager import StateManager
from core.web_search import WebSearchTool

T = TypeVar("T", bound=BaseModel)


class BaseAgent(ABC):
    """
    Abstract base for all MedTech assessment agents.

    Subclasses must implement:
      - name: str                         — unique agent identifier
      - system_prompt: str                — role & behaviour instructions
      - output_schema: type[BaseModel]    — Pydantic model for validated output
      - run(context) -> BaseModel         — core agent logic
    """

    name: str = "base_agent"
    system_prompt: str = "You are a helpful research assistant."
    output_schema: type[BaseModel] | None = None

    def __init__(
        self,
        llm: LLMClient | None = None,
        search: WebSearchTool | None = None,
        state: StateManager | None = None,
    ) -> None:
        self.llm = llm or LLMClient()
        self.search = search or WebSearchTool()
        self.state = state or StateManager()

    # ------------------------------------------------------------------ #
    #  Public entry point                                                  #
    # ------------------------------------------------------------------ #

    def execute(self, context: dict[str, Any]) -> BaseModel:
        """
        Top-level method called by the orchestrator.

        Runs the agent, validates output, persists to state, and returns.
        """
        logger.info(f"[{self.name}] Starting …")
        start = time.time()

        result = self.run(context)

        elapsed = time.time() - start
        logger.info(f"[{self.name}] Completed in {elapsed:.1f}s")

        # Persist output so downstream agents can access it
        self.state.set(self.name, result.model_dump())

        return result

    # ------------------------------------------------------------------ #
    #  Subclass contract                                                   #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def run(self, context: dict[str, Any]) -> BaseModel:
        """Core agent logic. Must return a validated Pydantic model."""

    # ------------------------------------------------------------------ #
    #  Helpers available to all agents                                     #
    # ------------------------------------------------------------------ #

    @retry(stop=stop_after_attempt(settings.MAX_RETRIES), wait=wait_fixed(settings.RETRY_DELAY))
    def call_llm(
        self,
        user_message: str,
        system_override: str | None = None,
        tools: list[dict] | None = None,
    ) -> str:
        """Call Claude and return the text content of the first message."""
        return self.llm.complete(
            system=system_override or self.system_prompt,
            user=user_message,
            tools=tools,
        )

    def call_llm_structured(self, user_message: str, schema: type[T]) -> T:
        """
        Ask Claude to respond as JSON conforming to `schema`, then validate.
        Returns a populated Pydantic model instance.
        """
        json_instruction = (
            f"\n\nRespond ONLY with a valid JSON object that conforms to this schema:\n"
            f"{json.dumps(schema.model_json_schema(), indent=2)}\n"
            "No markdown fences, no prose — raw JSON only."
        )
        raw = self.call_llm(user_message + json_instruction)
        # Strip accidental fences
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)
        return schema.model_validate(data)

    def search_web(self, query: str, num_results: int | None = None) -> list[dict]:
        """Run a web search and return structured results."""
        return self.search.search(query, num_results or settings.MAX_SEARCH_RESULTS)

    def get_prior_output(self, agent_name: str) -> dict | None:
        """Retrieve a prior agent's output from the shared state store."""
        return self.state.get(agent_name)

    def log(self, message: str, level: str = "info") -> None:
        getattr(logger, level)(f"[{self.name}] {message}")
