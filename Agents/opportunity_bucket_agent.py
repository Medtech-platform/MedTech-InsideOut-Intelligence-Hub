"""
OpportunityBucketAgent
-----------------------
Converts validated themes into opportunity statements,
clusters them into MECE opportunity buckets, profiles each bucket
with market metrics and risks, and outputs a scored-ready repository.
"""
from __future__ import annotations

import json
import uuid
from typing import Any

from pydantic import BaseModel, Field

from core.base_agent import BaseAgent
from schemas.opportunity import OpportunityBucket


class OpportunityBucketRepository(BaseModel):
    buckets: list[OpportunityBucket] = Field(default_factory=list)
    total: int = 0


class OpportunityBucketAgent(BaseAgent):
    name = "opportunity_bucket_agent"
    output_schema = OpportunityBucketRepository

    system_prompt = """
You are a MedTech strategy analyst responsible for structuring commercial
opportunity buckets from thematic research.

Your task:
1. Convert each validated theme into 1–2 concrete opportunity statements.
2. Group related statements into 4–8 MECE opportunity buckets.
3. Profile each bucket: target segments, customer need, strategic relevance,
   market metrics (size, growth), and key risks.

Rules:
- Bucket names must be specific and commercially meaningful.
  Good: "Mid-tier knee accounts — service-led wedge"
  Bad:  "Market opportunity"
- Every bucket must trace back to at least one theme.
- Return ONLY valid JSON — no prose, no markdown fences.
"""

    def run(self, context: dict[str, Any]) -> OpportunityBucketRepository:
        thematic_data = self.get_prior_output("thematic_agent") or {}
        themes = thematic_data.get("themes", [])

        market_data = self.get_prior_output("market_sizing_agent") or {}
        competitor_data = self.get_prior_output("competitor_intelligence_agent") or {}

        prompt = f"""
Validated themes from thematic analysis:
{json.dumps(themes, indent=2)[:7000]}

Market sizing context:
- Total market: {market_data.get('total_market_value_musd', '?')} M USD
- Serviceable: {market_data.get('serviceable_market_musd', '?')} M USD
- Penetration: {market_data.get('penetration_pct', '?')}%

Competitor weaknesses / gaps:
{json.dumps([
    {'company': c.get('company'), 'intent': i.get('inferred_intent')}
    for c, i in zip(
        competitor_data.get('competitors', [])[:5],
        competitor_data.get('strategic_intents', [])[:5]
    )
], indent=2)[:2000]}

Create 4–8 opportunity buckets. For each:
- bucket_id (e.g., OB01)
- name (≤8 words, specific)
- description (2–3 sentences)
- target_segments (list)
- supporting_theme_ids (list of theme_id values from above)
- market_size_musd (estimate or null)
- market_growth_pct (estimate or null)
- risks (list of 2–3 key risks)

Return:
{{
  "buckets": [...],
  "total": <number>
}}
"""
        result = self.call_llm_structured(prompt, OpportunityBucketRepository)
        for i, b in enumerate(result.buckets):
            if not b.bucket_id:
                b.bucket_id = f"OB{i+1:02d}"
        result.total = len(result.buckets)
        return result
