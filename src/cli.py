"""
CLI interface using typer.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root BEFORE importing anything that reads env vars
ROOT = Path(__file__).resolve().parents[1]   # src/ -> project root
load_dotenv(dotenv_path=ROOT / ".env", override=True)

# --- only AFTER load_dotenv, import the rest ---
import typer
import json
from typing import Optional

from src.llm_client import get_llm_client
from src.pipeline import run_pipeline

app = typer.Typer(help="Northwind Support Co-pilot CLI")


@app.command()
def run(
    ticket_id: Optional[str] = typer.Option(None, help="Specific ticket ID to process"),
    all: bool = typer.Option(False, help="Process all test tickets"),
    test_set: str = typer.Option("data/test_set.json", help="Path to test set"),
    output_dir: str = typer.Option("outputs", help="Output directory"),
):
    """
    Run the pipeline on a ticket or all test tickets.
    
    Examples:
        python -m src.cli run --ticket-id 1
        python -m src.cli run --all
    """
    llm_client = get_llm_client()

    if all:
        # Load all test tickets
        test_set_path = Path(test_set)
        if not test_set_path.exists():
            typer.secho(f"Test set not found: {test_set}", fg=typer.colors.RED)
            raise typer.Exit(1)

        test_data = json.loads(test_set_path.read_text())
        tickets = test_data.get("tickets", [])

        typer.secho(f"Processing {len(tickets)} tickets...", fg=typer.colors.BLUE)
        for ticket in tickets:
            try:
                run_pipeline(
                    str(ticket["id"]),
                    ticket["raw_ticket"],
                    llm_client,
                    save_output=True,
                    output_dir=output_dir,
                )
            except Exception as e:
                typer.secho(f"  Error on ticket {ticket['id']}: {e}", fg=typer.colors.RED)

    elif ticket_id:
        # Load and run specific ticket
        test_set_path = Path(test_set)
        test_data = json.loads(test_set_path.read_text())
        tickets = test_data.get("tickets", [])

        ticket = next((t for t in tickets if str(t["id"]) == ticket_id), None)
        if not ticket:
            typer.secho(f"Ticket {ticket_id} not found", fg=typer.colors.RED)
            raise typer.Exit(1)

        run_pipeline(
            ticket_id,
            ticket["raw_ticket"],
            llm_client,
            save_output=True,
            output_dir=output_dir,
        )

    else:
        typer.secho("Provide --ticket-id or --all", fg=typer.colors.YELLOW)


@app.command()
def eval(
    all: bool = typer.Option(False, help="Evaluate all tickets"),
    ticket_id: Optional[str] = typer.Option(None, help="Specific ticket ID to evaluate"),
):
    """
    Evaluate outputs against expected results.
    
    Examples:
        python -m src.cli eval --all
        python -m src.cli eval --ticket-id 1
    """
    from eval.evaluator import evaluate_all, evaluate_ticket

    if all:
        evaluate_all()
    elif ticket_id:
        evaluate_ticket(ticket_id)
    else:
        typer.secho("Provide --all or --ticket-id", fg=typer.colors.YELLOW)


@app.command()
def redteam():
    """Run red team tests (injection, edge cases, etc.)."""
    from eval.redteam import run_redteam_tests
    run_redteam_tests()


if __name__ == "__main__":
    app()
