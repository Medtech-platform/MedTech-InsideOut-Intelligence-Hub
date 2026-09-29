"""
ThematicAgent
-------------
Groups prioritised signals into MECE business themes, validates structure,
defines themes in business-friendly language, scores each theme, and
produces opportunity-ready inputs for the bucket creation step.
"""
from __future__ import annotations

import json
import uuid
from typing import Any

from core.base_agent import BaseAgent
from schemas.opportunity import Theme, ThematicAnalysis


class ThematicAgent(BaseAgent):
    name = "thematic_agent"
    output_schema = ThematicAnalysis

    system_prompt = """
You are a strategy analyst performing thematic synthesis for a MedTech
market opportunity assessment.

Your task:
1. Review prioritised signals and identify recurring patterns.
2. Group patterns into MECE business themes (6–12 themes typical).
3. Name each theme in business-friendly language (not jargon).
4. Score evidence strength (0–10) and business relevance (0–10).
5. Write a 1-sentence opportunity direction for each theme.

Rules:
- Themes must be Mutually Exclusive (no overlap) and Collectively Exhaustive
  (all signals covered).
- Theme names should be actionable statements, not topic labels.
  Good: "After-sales service gap creates switching opportunity"
  Bad:  "Service"
- Return ONLY valid JSON — no prose, no markdown fences.
"""

    def run(self, context: dict[str, Any]) -> ThematicAnalysis:
        signal_data = self.get_prior_output("signal_agent") or {}
        signals = signal_data.get("signals", [])
        total = signal_data.get("total", len(signals))

        # Filter to high-relevance signals
        priority_signals = [
            s for s in signals if s.get("relevance_score", 0) >= 0.5
        ] or signals  # fallback: use all

        prompt = f"""
Total signals available: {total}
Priority signals selected for thematic analysis ({len(priority_signals)}):

{json.dumps(priority_signals, indent=2)[:9000]}

Group these signals into 6–12 MECE business themes.
For each theme provide:
- theme_id (short code, e.g. T01)
- name (actionable statement, ≤10 words)
- definition (1 sentence)
- explanation_bullets (2–3 bullets)
- supporting_signal_ids (list of signal_id values)
- evidence_strength_score (0–10)
- business_relevance_score (0–10)
- opportunity_direction (1 sentence: what opportunity this points to)
- relevant_segments (list of customer segments)
- confidence (high/medium/low)

Return a ThematicAnalysis JSON:
{{
  "themes": [...],
  "total_signals_processed": {len(priority_signals)}
}}
"""
        result = self.call_llm_structured(prompt, ThematicAnalysis)
        # Ensure IDs
        for i, t in enumerate(result.themes):
            if not t.theme_id:
                t.theme_id = f"T{i+1:02d}"
        return result
