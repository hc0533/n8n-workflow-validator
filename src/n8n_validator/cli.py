"""Command-line interface for the n8n workflow validator."""

from __future__ import annotations

import argparse
import sys

from n8n_validator.loader import load_workflow
from n8n_validator.reporter import format_json_string, generate_report
from n8n_validator.validators import validate_workflow


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="n8n-validator",
        description="Validate n8n workflow JSON files",
    )
    parser.add_argument(
        "file",
        help="Path to the workflow JSON file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Load workflow
    load_result = load_workflow(args.file)
    if not load_result.success:
        print(f"Error: {load_result.error}", file=sys.stderr)
        return 1

    # Validate
    result = validate_workflow(load_result.workflow)

    # Output
    if args.json:
        print(format_json_string(result))
    else:
        print(generate_report(result))

    # Return 0 if valid, 1 if has errors
    return 0 if result.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
