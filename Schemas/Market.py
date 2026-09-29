"""Pydantic schemas for Market Landscape agent outputs."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ProjectScope(BaseModel):
    """Output of ScopeAgent."""
    geography: list[str]
    therapeutic_area: str
    technology_category: str
    product_category: str
    customer_segments: list[str]
    key_competitors: list[str]
    business_questions: list[str]
    research_boundaries: str
    clarifying_questions: list[str] = Field(default_factory=list)
    confidence: str = "medium"


class MarketDynamics(BaseModel):
    """Output of MarketDynamicsAgent."""
    tailwinds: list[str]
    headwinds: list[str]
    reimbursement_summary: str
    regulatory_summary: str
    site_of_care_shifts: list[str] = Field(default_factory=list)
    key_trends: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class CompetitorShareEntry(BaseModel):
    company: str
    product: str
    estimated_share_pct: float
    confidence: str


class MarketSize(BaseModel):
    """Output of MarketSizingAgent."""
    geography: str
    base_year: int
    total_market_value_musd: float
    serviceable_market_musd: float
    annual_procedures: int | None = None
    installed_base: int | None = None
    penetration_pct: float | None = None
    competitor_shares: list[CompetitorShareEntry] = Field(default_factory=list)
    methodology_notes: str = ""
    confidence: str = "medium"
    sources: list[str] = Field(default_factory=list)


class ForecastScenario(BaseModel):
    label: str  # "base" | "upside" | "downside"
    cagr_pct: float
    year_5_market_value_musd: float
    key_assumptions: list[str]


class MarketForecast(BaseModel):
    """Output of ForecastAgent."""
    geography: str
    base_year: int
    forecast_horizon_years: int
    scenarios: list[ForecastScenario]
    annual_values: dict[str, Any] = Field(default_factory=dict)  # year → value
    sources: list[str] = Field(default_factory=list)
