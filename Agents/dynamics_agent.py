"""
MarketDynamicsAgent
-------------------
Assesses the external environment: tailwinds, headwinds, reimbursement
landscape, regulatory requirements, and key market trends — all via
secondary research (web search + LLM synthesis).
"""
from __future__ import annotations

import json
from typing import Any

from core.base_agent import BaseAgent
from schemas.market import MarketDynamics


class MarketDynamicsAgent(BaseAgent):
    name = "market_dynamics_agent"
    output_schema = MarketDynamics

    system_prompt = """
You are a senior MedTech market intelligence analyst.
Your task is to synthesise secondary research into a structured assessment
of market dynamics: tailwinds, headwinds, reimbursement, and regulatory
environment.

Rules:
- Ground every statement in evidence from the search results provided.
- Distinguish between confirmed facts and inferences.
- Return ONLY valid JSON — no prose, no markdown fences.
"""

    def run(self, context: dict[str, Any]) -> MarketDynamics:
        scope = self.get_prior_output("scope_agent") or context.get("scope", {})
        geography = scope.get("geography", context.get("geography", ["Germany"]))
        technology = scope.get("technology_category", context.get("technology", "orthopedic robotics"))

        geo_str = ", ".join(geography) if isinstance(geography, list) else geography

        # Multi-query web search
        queries = [
            f"{technology} market drivers trends {geo_str} 2024 2025",
            f"{technology} reimbursement coverage {geo_str}",
            f"{technology} regulatory requirements {geo_str} MDR CE mark",
            f"{technology} market headwinds barriers adoption {geo_str}",
        ]
        search_results = {}
        for q in queries:
            results = self.search_web(q, num_results=5)
            search_results[q] = results
            self.log(f"Searched: {q} — {len(results)} results")

        search_text = json.dumps(search_results, indent=2)[:8000]  # stay within context

        prompt = f"""
Geography: {geo_str}
Technology / Market: {technology}

Search results:
{search_text}

Based on the search results above, produce a MarketDynamics JSON object.
List at least 4 tailwinds, 4 headwinds, summarise reimbursement and regulatory
landscape, and identify notable site-of-care shifts and key trends.
Include source URLs where available.
"""
        return self.call_llm_structured(prompt, MarketDynamics)
