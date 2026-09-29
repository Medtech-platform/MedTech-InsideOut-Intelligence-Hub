"""
SignalAgent
-----------
Consolidates all module outputs, breaks findings into discrete signals,
categorises each by business meaning, interprets commercial implication,
assesses evidence strength, and selects commercially relevant signals
for thematic analysis.
"""
from __future__ import annotations

import json
import uuid
from typing import Any

from core.base_agent import BaseAgent
from schemas.opportunity import Signal, SignalRepository


SIGNAL_CATEGORIES = [
    "market_driver",
    "market_restraint",
    "customer_need",
    "purchase_criterion",
    "adoption_barrier",
    "competitor_strength",
    "competitor_weakness",
    "reimbursement_factor",
    "regulatory_factor",
    "workflow_challenge",
    "pricing_value_concern",
    "gtm_implication",
]


class SignalAgent(BaseAgent):
    name = "signal_agent"
    output_schema = SignalRepository

    system_prompt = f"""
You are a research synthesis analyst at a MedTech strategy firm.
Your task is to convert long-form research findings into discrete, standalone
signals — each representing a single commercial observation.

For every signal provide:
- signal_id (UUID-like short code)
- statement (1 sentence, standalone, specific)
- category (one of: {', '.join(SIGNAL_CATEGORIES)})
- commercial_implication ("so what?" in 1–2 sentences)
- source_module (which module the finding came from)
- geography, segment, stakeholder_type (where applicable)
- confidence (high/medium/low)
- relevance_score (0.0–1.0)

Rules:
- One signal = one idea. Split compound statements.
- Merge genuinely identical observations from multiple sources.
- Do not invent findings not present in the input.
- Return ONLY valid JSON — no prose, no markdown fences.
"""

    def run(self, context: dict[str, Any]) -> SignalRepository:
        # Gather all prior module outputs
        modules = {
            "market_dynamics": self.get_prior_output("market_dynamics_agent"),
            "market_sizing": self.get_prior_output("market_sizing_agent"),
            "competitor_landscape": self.get_prior_output("competitor_intelligence_agent")
                                    or self.get_prior_output("competitor_discovery_agent"),
            "voc_summary": context.get("voc_summary"),  # injected if primary research done
        }
        modules = {k: v for k, v in modules.items() if v}

        prompt = f"""
Consolidated research evidence from all modules:

{json.dumps(modules, indent=2)[:10000]}

Break this evidence into discrete signals. Aim for 20–40 signals.
Return a SignalRepository JSON:
{{
  "signals": [ ... ],
  "total": <number>
}}
"""
        result = self.call_llm_structured(prompt, SignalRepository)
        # Ensure every signal has an ID
        for s in result.signals:
            if not s.signal_id:
                s.signal_id = f"S{str(uuid.uuid4())[:6].upper()}"
        result.total = len(result.signals)
        return result
