#!/usr/bin/env python3
"""
CLI entry point for the MedTech Opportunity Assessment Platform.

Usage examples:
  python scripts/run_assessment.py --brief brief.pdf --geography Germany France --module all
  python scripts/run_assessment.py --brief brief.txt --module market_landscape
"""
import json
import sys
from pathlib import Path

# Make the project root importable when running from scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import click
from loguru import logger

from config.settings import settings
from core.document_parser import DocumentParser
from core.orchestrator import AssessmentConfig, Orchestrator


@click.command()
@click.option("--brief", required=True, type=click.Path(exists=True),
              help="Path to client brief (PDF, DOCX, TXT, XLSX).")
@click.option("--geography", "-g", multiple=True, default=("Germany",),
              show_default=True, help="Target geographies (repeat for multiple).")
@click.option("--module", "-m",
              type=click.Choice(["all", "market_landscape", "competitor_landscape",
                                 "opportunity_matrix", "gtm"]),
              default="all", show_default=True, help="Pipeline module to run.")
@click.option("--run-id", default=None, help="Resume a prior run (state is reused).")
@click.option("--output", "-o", default=None, type=click.Path(),
              help="Path to write final JSON output (default: stdout).")
def main(brief: str, geography: tuple, module: str, run_id: str | None, output: str | None) -> None:
    """Run the MedTech Opportunity Assessment pipeline."""
    settings.validate()
    logger.remove()
    logger.add(sys.stderr, level=settings.LOG_LEVEL)

    # Parse brief document
    brief_text = DocumentParser().parse(brief)
    click.echo(f"Brief parsed: {len(brief_text)} characters.")

    config = AssessmentConfig(
        brief_text=brief_text,
        geography=list(geography),
        module=module,
        run_id=run_id,
    )

    results = Orchestrator(config).run()

    if output:
        Path(output).write_text(json.dumps(results, indent=2, default=str))
        click.echo(f"Output written to {output}")
    else:
        print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
