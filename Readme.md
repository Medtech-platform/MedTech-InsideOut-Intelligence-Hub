# MedTech Opportunity Assessment Platform

An agentic AI platform that automates the end-to-end market opportunity assessment workflow for MedTech engagements — from scope definition through GTM playbook generation.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Orchestrator                          │
│  (routes tasks, manages state, triggers agent chains)   │
└────────────┬────────────────────────────────────────────┘
             │
   ┌─────────┼──────────────────────────────────┐
   ▼         ▼         ▼          ▼             ▼
Market    Competitor  VoC      Opportunity    GTM
Landscape Landscape  Agents   Matrix         Playbook
Agents    Agents              Agents         Agent
```

## Modules

| Module | Agents | Purpose |
|--------|--------|---------|
| **Market Landscape** | `scope_agent`, `market_dynamics_agent`, `market_sizing_agent`, `forecast_agent` | Secondary research; market size, share, forecast |
| **Competitor Landscape** | `competitor_discovery_agent`, `product_strategy_agent`, `competitor_intelligence_agent` | 4Ps benchmarking; strategic intent; positioning |
| **Voice of Customers** | `screener_agent`, `discussion_guide_agent`, `transcript_agent`, `survey_agent` | Primary research design, fielding, synthesis |
| **Opportunity Matrix** | `signal_agent`, `thematic_agent`, `opportunity_bucket_agent`, `scoring_agent` | Signal → theme → scored opportunity buckets |
| **GTM Playbook** | `gtm_agent` | Entry model, commercial architecture, roadmap |

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/your-org/medtech-opportunity-platform.git
cd medtech-opportunity-platform
pip install -r requirements.txt

# 2. Set environment variables
cp config/.env.example config/.env
# Edit config/.env with your API keys

# 3. Run a full assessment
python scripts/run_assessment.py \
  --brief "path/to/client_brief.pdf" \
  --geography "Germany,France" \
  --module all

# 4. Run a single module
python scripts/run_assessment.py \
  --module market_landscape \
  --context path/to/scope.json
```

## Project Structure

```
medtech-opportunity-platform/
├── agents/                  # One file per agent
│   ├── scope_agent.py
│   ├── market_dynamics_agent.py
│   ├── market_sizing_agent.py
│   ├── forecast_agent.py
│   ├── competitor_discovery_agent.py
│   ├── product_strategy_agent.py
│   ├── competitor_intelligence_agent.py
│   ├── screener_agent.py
│   ├── discussion_guide_agent.py
│   ├── transcript_agent.py
│   ├── survey_agent.py
│   ├── signal_agent.py
│   ├── thematic_agent.py
│   ├── opportunity_bucket_agent.py
│   ├── scoring_agent.py
│   └── gtm_agent.py
├── core/
│   ├── orchestrator.py      # Main pipeline controller
│   ├── base_agent.py        # Abstract agent base class
│   ├── llm_client.py        # Anthropic Claude wrapper
│   ├── web_search.py        # Search tool wrapper
│   ├── document_parser.py   # PDF / DOCX / XLSX ingestion
│   └── state_manager.py     # Persistent state across runs
├── schemas/                 # Pydantic output schemas
│   ├── market.py
│   ├── competitor.py
│   ├── voc.py
│   ├── opportunity.py
│   └── gtm.py
├── config/
│   ├── settings.py          # App configuration
│   ├── .env.example
│   └── medtech_taxonomy.json
├── utils/
│   ├── exporters.py         # Word / Excel / PDF export
│   ├── validators.py        # Output quality checks
│   └── logger.py
├── tests/
│   ├── test_agents.py
│   ├── test_orchestrator.py
│   └── fixtures/
├── scripts/
│   └── run_assessment.py    # CLI entry point
└── .github/
    └── workflows/
        └── ci.yml
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Claude API key (required) |
| `SERP_API_KEY` | Web search API key |
| `OPENAI_API_KEY` | Optional fallback LLM |
| `OUTPUT_DIR` | Where to write output files (default: `./outputs`) |
| `LOG_LEVEL` | `DEBUG` / `INFO` / `WARNING` |

## Contributing

1. One agent per file; inherit from `BaseAgent`
2. Every output must be a validated Pydantic model
3. Add tests in `tests/test_agents.py`
4. Run `pytest` before opening a PR
