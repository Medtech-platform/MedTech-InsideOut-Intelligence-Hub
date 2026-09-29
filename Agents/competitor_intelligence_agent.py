"""
CompetitorIntelligenceAgent
----------------------------
Tracks recent competitor activities, classifies them, infers
strategic intent, and benchmarks channel / service strategies.
Enriches the CompetitorLandscape produced by CompetitorDiscoveryAgent.
"""
from __future__ import annotations

import json
from typing import Any

from core.base_agent import BaseAgent
from schemas.competitor import (
    ChannelProfile,
    CompetitorActivity,
    CompetitorLandscape,
    StrategicIntent,
)


class CompetitorIntelligenceAgent(BaseAgent):
    name = "competitor_intelligence_agent"
    output_schema = CompetitorLandscape

    system_prompt = """
You are a senior competitive intelligence analyst for a MedTech strategy firm.
Your tasks:
1. Identify recent (last 12–24 months) activities for each competitor.
2. Classify activities: Product Launch | Partnership | Acquisition | Expansion |
   Regulatory | Publication | Hiring | Investment | Conference.
3. Infer each competitor's strategic intent from the pattern of activities.
4. Profile channel strategy and after-sales service for each competitor.

Return ONLY valid JSON — no prose, no markdown fences.
"""

    def run(self, context: dict[str, Any]) -> CompetitorLandscape:
        landscape_data = self.get_prior_output("competitor_discovery_agent") or {}
        competitors: list[dict] = landscape_data.get("competitors", [])
        technology = context.get("technology", "orthopedic robotics")

        activities: list[CompetitorActivity] = []
        intents: list[StrategicIntent] = []
        channels: list[ChannelProfile] = []

        for comp in competitors[:8]:  # cap to avoid rate limits in CI
            company = comp.get("company", "")
            product = comp.get("product", "")
            self.log(f"Researching {company} …")

            # Activities
            act_results = self.search_web(
                f"{company} {product} news launch partnership 2024 2025", 5
            )
            ch_results = self.search_web(
                f"{company} {product} service after-sales distribution channel", 4
            )

            act_prompt = f"""
Company: {company}, Product: {product}
Market: {technology}

News search results:
{json.dumps(act_results, indent=2)[:3000]}

List up to 6 recent activities in the last 24 months.
Each activity: company, date (YYYY-MM or YYYY), activity_type,
headline (≤12 words), summary (1–2 sentences), geography, source URL.

Also infer the strategic intent: list focus_areas and a 1-sentence inferred_intent.

Also describe the channel profile: go_to_market model, origin (import/local),
typical service TAT, after_sales_score out of 10.

Return JSON with keys:
  activities: [list of CompetitorActivity]
  strategic_intent: {{company, focus_areas, inferred_intent, evidence, confidence}}
  channel_profile: {{company, go_to_market, origin, service_tat_hours, after_sales_score}}
"""
            raw = self.call_llm(act_prompt)
            # Parse incrementally — be tolerant of partial JSON
            try:
                import json as _json
                data = _json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip())
                for a in data.get("activities", []):
                    try:
                        activities.append(CompetitorActivity(**{k: a.get(k, "") for k in CompetitorActivity.model_fields}))
                    except Exception:
                        pass
                si = data.get("strategic_intent", {})
                if si:
                    try:
                        intents.append(StrategicIntent(**si))
                    except Exception:
                        pass
                cp = data.get("channel_profile", {})
                if cp:
                    try:
                        channels.append(ChannelProfile(**cp))
                    except Exception:
                        pass
            except Exception as exc:
                self.log(f"Parse error for {company}: {exc}", "warning")

        # Merge back into landscape
        prior = CompetitorLandscape(**landscape_data) if landscape_data else CompetitorLandscape(competitors=[])
        prior.recent_activities = activities
        prior.strategic_intents = intents
        prior.channel_profiles = channels
        return prior
