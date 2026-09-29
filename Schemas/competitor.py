"""Pydantic schemas for Competitive Landscape agent outputs."""
from __future__ import annotations

from pydantic import BaseModel, Field


class CompetitorProfile(BaseModel):
    company: str
    product: str
    market_role: str  # leader | challenger | niche | emerging
    headquarters: str = ""
    geographies: list[str] = Field(default_factory=list)
    relevance_score: float = 0.0
    source: str = ""


class ProductBenchmark(BaseModel):
    dimension: str
    scores: dict[str, float]  # company → score (0–5)


class CompetitorActivity(BaseModel):
    company: str
    date: str
    activity_type: str
    headline: str
    summary: str
    geography: str = ""
    source: str = ""


class StrategicIntent(BaseModel):
    company: str
    focus_areas: list[str]
    inferred_intent: str
    evidence: list[str]
    confidence: str = "medium"


class ChannelProfile(BaseModel):
    company: str
    go_to_market: str
    origin: str
    service_tat_hours: str = ""
    after_sales_score: float | None = None


class CompetitorLandscape(BaseModel):
    """Aggregated output of all Competitor Landscape sub-agents."""
    competitors: list[CompetitorProfile]
    product_benchmarks: list[ProductBenchmark] = Field(default_factory=list)
    recent_activities: list[CompetitorActivity] = Field(default_factory=list)
    strategic_intents: list[StrategicIntent] = Field(default_factory=list)
    channel_profiles: list[ChannelProfile] = Field(default_factory=list)
    differentiation_hypothesis: str = ""
