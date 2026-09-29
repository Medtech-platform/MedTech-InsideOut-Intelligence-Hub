"""Pydantic schemas for GTM Playbook output."""
from __future__ import annotations

from pydantic import BaseModel, Field


class RoadmapPhase(BaseModel):
    label: str          # e.g. "Q1–Q2"
    activities: list[str]
    milestones: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)


class GTMPlaybook(BaseModel):
    geography: str
    recommended_entry_model: str
    entry_model_rationale: str
    commercial_architecture: list[str]   # pricing, service model, etc.
    target_account_waves: list[dict]     # [{wave, segments, rationale}]
    launch_actions: list[str]
    retention_actions: list[str]
    executive_recommendations: list[str]
    roadmap: list[RoadmapPhase]
    evidence_links: list[str] = Field(default_factory=list)
