"""
CompetitorDiscoveryAgent
------------------------
Discovers, deduplicates, classifies, and profiles all relevant
competitors in the target market using web search.
"""
from __future__ import annotations

import json
from typing import Any

from core.base_agent import BaseAgent
from schemas.competitor import CompetitorLandscape, CompetitorProfile


class CompetitorDiscoveryAgent(BaseAgent):
    name = "competitor_discovery_agent"
    output_schema = CompetitorLandscape

    system_prompt = """
You are a competitive intelligence analyst specialising in MedTech.
Your task: discover, classify, and profile all relevant competitors
in a defined market.

Rules:
- Classify each competitor as: leader | challenger | niche | emerging | substitute
- Assign a relevance_score 0–10 based on product overlap, geography, and customer fit
- Remove duplicates (subsidiaries, acquired companies, aliases)
- Return ONLY valid JSON — no prose, no markdown fences
"""

    def run(self, context: dict[str, Any]) -> CompetitorLandscape:
        scope = self.get_prior_output("scope_agent") or context.get("scope", {})
        geography = scope.get("geography", ["Germany"])
        technology = scope.get("technology_category", "orthopedic robotics")
        geo_str = ", ".join(geography) if isinstance(geography, list) else geography

        queries = [
            f"{technology} companies competitors {geo_str} 2024",
            f"{technology} OEM vendors market participants global",
            f"emerging startups {technology} funding 2023 2024",
        ]
        results: dict = {}
        for q in queries:
            results[q] = self.search_web(q, 8)

        prompt = f"""
Market: {technology}
Geography: {geo_str}

Search results:
{json.dumps(results, indent=2)[:8000]}

Identify all relevant competitors. For each:
- company name
- main product name
- market_role (leader/challenger/niche/emerging/substitute)
- headquarters
- geographies served
- relevance_score (0–10)
- source URL

Return as a CompetitorLandscape JSON with the `competitors` list populated.
Set product_benchmarks, recent_activities, strategic_intents, channel_profiles
to empty lists for now.
"""
        landscape = self.call_llm_structured(prompt, CompetitorLandscape)
        return landscape
