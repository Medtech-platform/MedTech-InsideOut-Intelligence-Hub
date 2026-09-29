"""
MarketSizingAgent
-----------------
Triangulates current market size, installed base, penetration, and
competitor share using procedure-volume, installed-base, and
revenue-aggregation methods.
"""
from __future__ import annotations

import json
from typing import Any

from core.base_agent import BaseAgent
from schemas.market import MarketSize


class MarketSizingAgent(BaseAgent):
    name = "market_sizing_agent"
    output_schema = MarketSize

    system_prompt = """
You are a MedTech market-sizing specialist.
Your task is to estimate the current market size, serviceable market,
installed base, penetration, and competitor revenue shares for a defined
product category and geography.

Rules:
- Use at least two independent sizing methods and triangulate.
- Provide confidence levels (high/medium/low) for each key figure.
- Present competitor shares as percentages summing to ~100%.
- Return ONLY valid JSON conforming to the MarketSize schema.
"""

    def run(self, context: dict[str, Any]) -> MarketSize:
        scope = self.get_prior_output("scope_agent") or context.get("scope", {})
        geography_list = scope.get("geography", context.get("geography", ["Germany"]))
        geography = geography_list[0] if isinstance(geography_list, list) else geography_list
        technology = scope.get("technology_category", "orthopedic robotics")
        competitors = scope.get("key_competitors", [])

        # Search for sizing inputs
        queries = [
            f"{technology} market size {geography} USD million 2024",
            f"{technology} installed base procedures {geography} 2024",
            f"Stryker Zimmer {technology} revenue market share {geography}",
        ]
        search_data: dict = {}
        for q in queries:
            search_data[q] = self.search_web(q, 5)

        prompt = f"""
Geography: {geography}
Technology: {technology}
Key competitors: {competitors}

Search evidence:
{json.dumps(search_data, indent=2)[:7000]}

Estimate the current (base year ~2024) market for {technology} in {geography}.
Include:
- total_market_value_musd (all revenue lines)
- serviceable_market_musd (addressable by entrant)
- annual_procedures (if applicable)
- installed_base (active systems)
- penetration_pct (vs eligible procedures or sites)
- competitor_shares (list each major player with share %)
- methodology_notes explaining your triangulation
"""
        result = self.call_llm_structured(prompt, MarketSize)
        result.geography = geography
        return result
