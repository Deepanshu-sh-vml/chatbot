"""CLI interface using argparse."""
import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=ROOT / ".env", override=True)

from src.llm_client import get_llm_client
from src.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m src.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the pipeline on a ticket or all test tickets")
    run_parser.add_argument("--ticket-id", dest="ticket_id")
    run_parser.add_argument("--all", action="store_true", help="Process all test tickets")
    run_parser.add_argument("--test-set", default="data/test_set.json")
    run_parser.add_argument("--output-dir", default="outputs")

    eval_parser = subparsers.add_parser("eval", help="Evaluate outputs")
    eval_parser.add_argument("--all", action="store_true", help="Evaluate all tickets")
    eval_parser.add_argument("--ticket-id", dest="ticket_id")

    subparsers.add_parser("redteam", help="Run red team tests")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        llm_client = get_llm_client()
        if args.all:
            test_set_path = Path(args.test_set)
            if not test_set_path.exists():
                parser.error(f"Test set not found: {args.test_set}")

            test_data = json.loads(test_set_path.read_text(encoding="utf-8"))
            tickets = test_data.get("tickets", [])
            print(f"Processing {len(tickets)} tickets...")
            for ticket in tickets:
                try:
                    run_pipeline(
                        str(ticket["id"]),
                        ticket["raw_ticket"],
                        llm_client,
                        save_output=True,
                        output_dir=args.output_dir,
                    )
                except Exception as exc:
                    print(f"  Error on ticket {ticket['id']}: {exc}")
            return 0

        if args.ticket_id:
            test_set_path = Path(args.test_set)
            test_data = json.loads(test_set_path.read_text(encoding="utf-8"))
            tickets = test_data.get("tickets", [])
            ticket = next((t for t in tickets if str(t["id"]) == args.ticket_id), None)
            if not ticket:
                parser.error(f"Ticket {args.ticket_id} not found")

            run_pipeline(
                args.ticket_id,
                ticket["raw_ticket"],
                llm_client,
                save_output=True,
                output_dir=args.output_dir,
            )
            return 0

        parser.error("Provide --ticket-id or --all")

    if args.command == "eval":
        from eval.evaluator import evaluate_all, evaluate_ticket

        if args.all:
            evaluate_all()
        elif args.ticket_id:
            evaluate_ticket(args.ticket_id)
        else:
            parser.error("Provide --all or --ticket-id")
        return 0

    if args.command == "redteam":
        from eval.redteam import run_redteam_tests
        run_redteam_tests()
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
