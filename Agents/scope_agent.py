"""
ScopeAgent
----------
Reads the client brief / SOW / email and extracts a structured
project definition: geography, therapeutic area, product category,
customer segments, business questions, and research boundaries.
"""
from __future__ import annotations

from typing import Any

from core.base_agent import BaseAgent
from core.llm_client import LLMClient
from schemas.market import ProjectScope


class ScopeAgent(BaseAgent):
    name = "scope_agent"
    output_schema = ProjectScope

    system_prompt = """
You are a senior MedTech strategy consultant at Evalueserve.
Your job is to read a client brief, proposal, SOW, or transcript and extract
a precise, structured project definition.

Rules:
- Identify geography, therapeutic area, technology category, product category,
  customer segments, key competitors, and core business questions.
- If the brief mentions a product name (e.g., "Mako"), use your knowledge to
  identify the OEM and correct market category.
- Label all information as [client-stated], [inferred], or [enriched from web].
- Generate clarifying questions for any missing critical information.
- Respond ONLY with the JSON schema requested — no prose, no markdown fences.
"""

    def run(self, context: dict[str, Any]) -> ProjectScope:
        brief_text: str = context.get("brief_text", "")
        geography: list[str] = context.get("geography", [])

        # Optionally search for product/brand context
        known_products = self._identify_products(brief_text)
        search_context = ""
        if known_products:
            for product in known_products[:3]:
                results = self.search_web(f"{product} MedTech OEM market category")
                search_context += f"\n### Web context for '{product}':\n"
                for r in results[:3]:
                    search_context += f"- {r['title']}: {r['snippet']}\n"

        prompt = f"""
Client Brief / SOW:
---
{brief_text}
---

Geographies mentioned or requested: {geography}

Web context gathered:
{search_context}

Extract the structured project definition as JSON.
"""
        return self.call_llm_structured(prompt, ProjectScope)

    def _identify_products(self, text: str) -> list[str]:
        """Quick heuristic: look for quoted or capitalised brand-like tokens."""
        import re
        # Match words starting with uppercase or surrounded by quotes
        matches = re.findall(r'\b[A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+)?\b', text)
        # Filter out common non-product words
        stop = {"The","This","For","With","Our","Your","We","You","They","In","Of"}
        return [m for m in set(matches) if m not in stop][:10]
