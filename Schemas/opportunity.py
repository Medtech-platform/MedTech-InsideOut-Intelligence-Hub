"""Pydantic schemas for Signal → Thematic → Opportunity → GTM pipeline."""
from __future__ import annotations

from pydantic import BaseModel, Field


# ── Signal layer ──────────────────────────────────────────────────────── #

class Signal(BaseModel):
    signal_id: str
    statement: str
    category: str  # market_driver | customer_need | competitor_gap | ...
    commercial_implication: str
    source_module: str
    geography: str = ""
    segment: str = ""
    stakeholder_type: str = ""
    confidence: str = "medium"
    relevance_score: float = 0.0


class SignalRepository(BaseModel):
    signals: list[Signal]
    total: int


# ── Theme layer ───────────────────────────────────────────────────────── #

class Theme(BaseModel):
    theme_id: str
    name: str
    definition: str
    explanation_bullets: list[str]
    supporting_signal_ids: list[str]
    evidence_strength_score: float = 0.0
    business_relevance_score: float = 0.0
    opportunity_direction: str = ""
    relevant_segments: list[str] = Field(default_factory=list)
    confidence: str = "medium"


class ThematicAnalysis(BaseModel):
    themes: list[Theme]
    total_signals_processed: int


# ── Opportunity bucket layer ──────────────────────────────────────────── #

class OpportunityBucket(BaseModel):
    bucket_id: str
    name: str
    description: str
    target_segments: list[str]
    supporting_theme_ids: list[str]
    market_size_musd: float | None = None
    market_growth_pct: float | None = None
    risks: list[str] = Field(default_factory=list)


# ── Scoring layer ─────────────────────────────────────────────────────── #

class ScoredOpportunity(BaseModel):
    bucket_id: str
    name: str
    attractiveness: float     # 0–10
    ability_to_win: float     # 0–10
    strategic_fit: float      # 0–10
    speed_to_revenue: float   # 0–10
    weighted_score: float     # computed
    decision_call: str        # Do now | Winnable | Plan | Low priority
    recommended_move: str
    rationale: str
    confidence: str = "medium"


class OpportunityMatrix(BaseModel):
    scored_opportunities: list[ScoredOpportunity]
    scoring_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "attractiveness": 0.30,
            "ability_to_win": 0.30,
            "strategic_fit": 0.20,
            "speed_to_revenue": 0.20,
        }
    )
