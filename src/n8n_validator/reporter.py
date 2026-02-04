"""Reporter module for formatting and outputting validation results."""

from __future__ import annotations

import json
from typing import Any

from n8n_validator.validators import Severity, ValidationIssue, ValidationResult


# Improvement suggestions for each rule
SUGGESTIONS: dict[str, str] = {
    "error-handling": (
        "Add an Error Trigger node to handle failures, "
        "or set 'errorWorkflow' in workflow settings to delegate error handling."
    ),
    "webhook-timeout": (
        "Configure a timeout in the Webhook node's options to prevent "
        "hanging requests. Recommended: 30-60 seconds for typical API calls."
    ),
}

DEFAULT_SUGGESTION = "Review the workflow configuration for this issue."


def get_suggestion(rule: str) -> str:
    """Get improvement suggestion for a validation rule."""
    return SUGGESTIONS.get(rule, DEFAULT_SUGGESTION)


def format_json(result: ValidationResult) -> dict[str, Any]:
    """Convert ValidationResult to a JSON-serializable dictionary.

    Args:
        result: The validation result to format.

    Returns:
        Dictionary representation of the validation result.
    """
    return {
        "workflow_name": result.workflow_name,
        "is_valid": result.is_valid,
        "summary": {
            "total_issues": len(result.issues),
            "errors": result.error_count,
            "warnings": result.warning_count,
        },
        "issues": [
            {
                "rule": issue.rule,
                "severity": issue.severity.value,
                "message": issue.message,
                "node_name": issue.node_name,
                "suggestion": get_suggestion(issue.rule),
            }
            for issue in result.issues
        ],
    }


def format_json_string(result: ValidationResult, indent: int = 2) -> str:
    """Convert ValidationResult to a JSON string.

    Args:
        result: The validation result to format.
        indent: Indentation level for pretty printing.

    Returns:
        JSON string representation.
    """
    return json.dumps(format_json(result), indent=indent, ensure_ascii=False)


def generate_report(result: ValidationResult) -> str:
    """Generate a human-readable report with improvement suggestions.

    Args:
        result: The validation result to report on.

    Returns:
        Formatted text report.
    """
    lines: list[str] = []

    # Header
    lines.append(f"Validation Report: {result.workflow_name}")
    lines.append("=" * 50)

    # Summary
    if result.is_valid:
        lines.append("Status: VALID (no errors)")
    else:
        lines.append("Status: INVALID (errors found)")

    lines.append(f"Issues: {len(result.issues)} ({result.error_count} errors, {result.warning_count} warnings)")
    lines.append("")

    # Issues with suggestions
    if result.issues:
        lines.append("Issues Found:")
        lines.append("-" * 30)

        for i, issue in enumerate(result.issues, 1):
            severity_label = issue.severity.value.upper()
            node_info = f" (node: {issue.node_name})" if issue.node_name else ""

            lines.append(f"{i}. [{severity_label}] {issue.rule}{node_info}")
            lines.append(f"   {issue.message}")
            lines.append(f"   Suggestion: {get_suggestion(issue.rule)}")
            lines.append("")
    else:
        lines.append("No issues found.")

    return "\n".join(lines)
