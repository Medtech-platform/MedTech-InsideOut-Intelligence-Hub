"""
Thin wrapper around the Anthropic Messages API.

Handles tool-use turns automatically so agents only need to
call `complete()` and get back a plain string.
"""
from __future__ import annotations

import json
from typing import Any

import anthropic
from loguru import logger

from config.settings import settings


class LLMClient:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.ANTHROPIC_MODEL
        self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def complete(
        self,
        user: str,
        system: str = "You are a helpful assistant.",
        tools: list[dict] | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Send a single user turn and return the assistant's text reply.
        Handles multi-turn tool-use loops transparently.
        """
        messages: list[dict] = [{"role": "user", "content": user}]
        kwargs: dict[str, Any] = {
            "model": self.model,
            "system": system,
            "max_tokens": max_tokens or settings.MAX_TOKENS,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        max_loops = 10
        for _ in range(max_loops):
            response = self._client.messages.create(**kwargs)
            logger.debug(f"LLM stop_reason={response.stop_reason}")

            if response.stop_reason == "end_turn":
                # Concatenate all text blocks
                return "".join(
                    block.text for block in response.content if hasattr(block, "text")
                )

            if response.stop_reason == "tool_use":
                # Append assistant turn
                messages.append({"role": "assistant", "content": response.content})
                # Process each tool call and append tool-result turn
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self._dispatch_tool(block.name, block.input)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(result),
                            }
                        )
                messages.append({"role": "user", "content": tool_results})
                kwargs["messages"] = messages
                continue

            # Unknown stop reason — return whatever text we have
            return "".join(
                block.text for block in response.content if hasattr(block, "text")
            )

        raise RuntimeError("LLM tool-use loop exceeded max iterations.")

    # ------------------------------------------------------------------ #
    #  Built-in tool dispatcher                                            #
    # ------------------------------------------------------------------ #

    def _dispatch_tool(self, name: str, tool_input: dict) -> Any:
        """Route tool calls to internal implementations."""
        from core.web_search import WebSearchTool

        if name == "web_search":
            return WebSearchTool().search(tool_input.get("query", ""))
        logger.warning(f"Unknown tool: {name}")
        return {"error": f"Tool '{name}' not found."}

    # ------------------------------------------------------------------ #
    #  Tool definitions for web search                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def web_search_tool_def() -> dict:
        return {
            "name": "web_search",
            "description": (
                "Search the web for up-to-date information. "
                "Returns a list of results with title, url, and snippet."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string.",
                    }
                },
                "required": ["query"],
            },
        }
