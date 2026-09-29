"""
GTMAgent
--------
Synthesises all prior outputs into a go-to-market playbook:
entry model, commercial architecture, target-account sequencing,
launch / retention strategy, executive recommendations, and roadmap.
"""
from __future__ import annotations

import json
from typing import Any

from core.base_agent import BaseAgent
from schemas.gtm import GTMPlaybook


class GTMAgent(BaseAgent):
    name = "gtm_agent"
    output_schema = GTMPlaybook

    system_prompt = """
You are a senior MedTech commercial strategy partner.
Your task is to produce a concrete, evidence-based GTM Playbook.

Rules:
- Every recommendation must link back to evidence from the opportunity matrix,
  competitor analysis, or voice-of-customer research.
- Be specific: name customer segments, account types, pricing models,
  and timelines — not generic advice.
- The roadmap should cover ~18 months in quarterly phases.
- Return ONLY valid JSON — no prose, no markdown fences.
"""

    def run(self, context: dict[str, Any]) -> GTMPlaybook:
        scope = self.get_prior_output("scope_agent") or {}
        geography_list = scope.get("geography", ["Germany"])
        geography = geography_list[0] if isinstance(geography_list, list) else geography_list

        opportunity_matrix = self.get_prior_output("scoring_agent") or {}
        top_opps = (opportunity_matrix.get("scored_opportunities") or [])[:4]

        competitor_data = self.get_prior_output("competitor_intelligence_agent") or {}
        market_data = self.get_prior_output("market_sizing_agent") or {}
        dynamics = self.get_prior_output("market_dynamics_agent") or {}

        prompt = f"""
Geography: {geography}
Technology: {scope.get('technology_category', 'MedTech solution')}

Top-ranked opportunities (from scoring):
{json.dumps(top_opps, indent=2)[:3000]}

Market context:
- Serviceable market: {market_data.get('serviceable_market_musd', '?')} M USD
- Key tailwinds: {dynamics.get('tailwinds', [])[:3]}
- Key headwinds: {dynamics.get('headwinds', [])[:3]}

Competitor channel profiles:
{json.dumps(competitor_data.get('channel_profiles', []), indent=2)[:2000]}

Generate a GTMPlaybook with:
1. recommended_entry_model (e.g., "Hybrid: direct mid-tier + distributor tail")
2. entry_model_rationale (2–3 sentences)
3. commercial_architecture (5–7 bullet points: pricing, service model, etc.)
4. target_account_waves: 3 waves — each with {{wave, segments, rationale, objective}}
5. launch_actions (5 bullet points)
6. retention_actions (4 bullet points)
7. executive_recommendations (3–5 bullet points)
8. roadmap: 3 phases (Q1-Q2, Q3-Q4, Q5-Q6) each with label, activities, milestones

Return a GTMPlaybook JSON.
"""
        playbook = self.call_llm_structured(prompt, GTMPlaybook)
        playbook.geography = geography
        return playbook
