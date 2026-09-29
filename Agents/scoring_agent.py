"""
ScoringAgent
------------
Ingests opportunity buckets, scores each on four dimensions
(attractiveness, ability-to-win, strategic fit, speed-to-revenue),
computes weighted scores, assigns decision calls, and outputs the
ranked Opportunity Matrix.
"""
from __future__ import annotations

import json
from typing import Any

from core.base_agent import BaseAgent
from schemas.opportunity import OpportunityMatrix, ScoredOpportunity

WEIGHTS = {
    "attractiveness": 0.30,
    "ability_to_win": 0.30,
    "strategic_fit": 0.20,
    "speed_to_revenue": 0.20,
}


def _decision_call(score: float) -> str:
    if score >= 7.5:
        return "Do now"
    if score >= 6.5:
        return "Winnable"
    if score >= 5.0:
        return "Plan"
    return "Low priority"


class ScoringAgent(BaseAgent):
    name = "scoring_agent"
    output_schema = OpportunityMatrix

    system_prompt = """
You are a MedTech strategy consultant scoring commercial opportunities.

For each opportunity bucket score these dimensions 0–10:
- attractiveness: market size, growth, unmet need, customer demand
- ability_to_win: competitive gaps, client capability, differentiation
- strategic_fit: alignment with client strengths and objectives
- speed_to_revenue: time to first revenue, sales cycle, complexity

Provide a 1-sentence rationale and a 1-sentence recommended_move.
Return ONLY valid JSON — no prose, no markdown fences.
"""

    def run(self, context: dict[str, Any]) -> OpportunityMatrix:
        bucket_data = self.get_prior_output("opportunity_bucket_agent") or {}
        buckets: list[dict] = bucket_data.get("buckets", [])

        market_data = self.get_prior_output("market_sizing_agent") or {}
        competitor_data = self.get_prior_output("competitor_intelligence_agent") or {}

        prompt = f"""
Opportunity buckets to score:
{json.dumps(buckets, indent=2)[:6000]}

Supporting context:
Market size: {market_data.get('total_market_value_musd', 'unknown')} M USD
Top competitors: {[c.get('company') for c in competitor_data.get('competitors', [])[:5]]}

Score each bucket on: attractiveness, ability_to_win, strategic_fit,
speed_to_revenue (all 0–10). Add rationale and recommended_move.

Return an OpportunityMatrix JSON:
{{
  "scored_opportunities": [
    {{
      "bucket_id": "...",
      "name": "...",
      "attractiveness": X,
      "ability_to_win": X,
      "strategic_fit": X,
      "speed_to_revenue": X,
      "weighted_score": 0,   // will be computed by code
      "decision_call": "",   // will be set by code
      "recommended_move": "...",
      "rationale": "...",
      "confidence": "medium"
    }},
    ...
  ],
  "scoring_weights": {json.dumps(WEIGHTS)}
}}
"""
        matrix = self.call_llm_structured(prompt, OpportunityMatrix)

        # Compute weighted scores and decision calls in Python
        for opp in matrix.scored_opportunities:
            opp.weighted_score = round(
                opp.attractiveness * WEIGHTS["attractiveness"]
                + opp.ability_to_win * WEIGHTS["ability_to_win"]
                + opp.strategic_fit * WEIGHTS["strategic_fit"]
                + opp.speed_to_revenue * WEIGHTS["speed_to_revenue"],
                2,
            )
            opp.decision_call = _decision_call(opp.weighted_score)

        # Sort descending
        matrix.scored_opportunities.sort(key=lambda x: x.weighted_score, reverse=True)
        return matrix
