"""
Orchestrator
------------
Controls the end-to-end assessment pipeline.

Pipeline order:
  1. ScopeAgent
  2. MarketDynamicsAgent
  3. MarketSizingAgent        ─┐
  4. CompetitorDiscoveryAgent ─┤ parallel (future)
  5. CompetitorIntelligenceAgent
  6. SignalAgent
  7. ThematicAgent
  8. OpportunityBucketAgent
  9. ScoringAgent
  10. GTMAgent

Each agent reads prior outputs from the shared StateManager.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from agents.competitor_discovery_agent import CompetitorDiscoveryAgent
from agents.competitor_intelligence_agent import CompetitorIntelligenceAgent
from agents.gtm_agent import GTMAgent
from agents.market_dynamics_agent import MarketDynamicsAgent
from agents.market_sizing_agent import MarketSizingAgent
from agents.opportunity_bucket_agent import OpportunityBucketAgent
from agents.scope_agent import ScopeAgent
from agents.scoring_agent import ScoringAgent
from agents.signal_agent import SignalAgent
from agents.thematic_agent import ThematicAgent
from core.llm_client import LLMClient
from core.state_manager import StateManager
from core.web_search import WebSearchTool

console = Console()

MODULE_CHAINS: dict[str, list[str]] = {
    "market_landscape": ["scope", "market_dynamics", "market_sizing"],
    "competitor_landscape": ["scope", "competitor_discovery", "competitor_intelligence"],
    "opportunity_matrix": [
        "scope", "market_dynamics", "market_sizing",
        "competitor_discovery", "competitor_intelligence",
        "signal", "thematic", "opportunity_bucket", "scoring",
    ],
    "gtm": [
        "scope", "market_dynamics", "market_sizing",
        "competitor_discovery", "competitor_intelligence",
        "signal", "thematic", "opportunity_bucket", "scoring", "gtm",
    ],
    "all": [
        "scope", "market_dynamics", "market_sizing",
        "competitor_discovery", "competitor_intelligence",
        "signal", "thematic", "opportunity_bucket", "scoring", "gtm",
    ],
}

AGENT_MAP = {
    "scope": ScopeAgent,
    "market_dynamics": MarketDynamicsAgent,
    "market_sizing": MarketSizingAgent,
    "competitor_discovery": CompetitorDiscoveryAgent,
    "competitor_intelligence": CompetitorIntelligenceAgent,
    "signal": SignalAgent,
    "thematic": ThematicAgent,
    "opportunity_bucket": OpportunityBucketAgent,
    "scoring": ScoringAgent,
    "gtm": GTMAgent,
}


@dataclass
class AssessmentConfig:
    brief_text: str = ""
    geography: list[str] = field(default_factory=lambda: ["Germany"])
    module: str = "all"
    run_id: str | None = None
    voc_summary: dict | None = None  # inject primary research if available


class Orchestrator:
    def __init__(self, config: AssessmentConfig) -> None:
        self.config = config
        self.state = StateManager(run_id=config.run_id)
        self.llm = LLMClient()
        self.search = WebSearchTool()

    def run(self) -> dict[str, Any]:
        """Execute the configured pipeline and return all agent outputs."""
        steps = MODULE_CHAINS.get(self.config.module, MODULE_CHAINS["all"])
        context = self._base_context()

        console.print(f"\n[bold magenta]MedTech Assessment Platform[/bold magenta]")
        console.print(f"Run ID: {self.state.run_id}  |  Module: {self.config.module}")
        console.print(f"Geography: {self.config.geography}\n")

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            for step in steps:
                agent_cls = AGENT_MAP.get(step)
                if not agent_cls:
                    logger.warning(f"Unknown step: {step} — skipping")
                    continue

                task = progress.add_task(f"[cyan]{step}[/cyan]", total=None)
                agent = agent_cls(llm=self.llm, search=self.search, state=self.state)
                try:
                    result = agent.execute(context)
                    progress.update(task, description=f"[green]✓ {step}[/green]")
                except Exception as exc:
                    progress.update(task, description=f"[red]✗ {step}: {exc}[/red]")
                    logger.exception(f"Agent {step} failed: {exc}")

        console.print("\n[bold green]Assessment complete.[/bold green]")
        console.print(f"State saved to: {self.state._path}\n")
        return self.state.all()

    def _base_context(self) -> dict[str, Any]:
        ctx: dict[str, Any] = {
            "brief_text": self.config.brief_text,
            "geography": self.config.geography,
        }
        if self.config.voc_summary:
            ctx["voc_summary"] = self.config.voc_summary
        return ctx
