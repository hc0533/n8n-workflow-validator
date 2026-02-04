"""Validators module for validating n8n workflow structure and content."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(Enum):
    """Validation issue severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """A single validation issue found in a workflow."""

    rule: str
    message: str
    severity: Severity = Severity.WARNING
    node_name: str | None = None


@dataclass
class ValidationResult:
    """Result of validating a workflow."""

    workflow_name: str
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Return True if no errors were found."""
        return not any(issue.severity == Severity.ERROR for issue in self.issues)

    @property
    def error_count(self) -> int:
        """Return count of error-level issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        """Return count of warning-level issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.WARNING)


def get_nodes(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract nodes list from workflow."""
    return workflow.get("nodes", [])


def get_node_type(node: dict[str, Any]) -> str:
    """Get the type of a node."""
    return node.get("type", "")


def get_node_name(node: dict[str, Any]) -> str:
    """Get the name of a node."""
    return node.get("name", "Unknown")


def check_error_handling(workflow: dict[str, Any]) -> list[ValidationIssue]:
    """Check if workflow has error handling (Error Trigger node or errorWorkflow setting).

    Rule: Workflows should have error handling to catch and process failures.
    """
    issues: list[ValidationIssue] = []
    nodes = get_nodes(workflow)

    # Check for Error Trigger node
    has_error_trigger = any(
        "errortrigger" in get_node_type(node).lower() for node in nodes
    )

    # Check for errorWorkflow setting in workflow settings
    settings = workflow.get("settings", {})
    has_error_workflow = bool(settings.get("errorWorkflow"))

    if not has_error_trigger and not has_error_workflow:
        issues.append(
            ValidationIssue(
                rule="error-handling",
                message="Workflow has no error handling. Add an Error Trigger node or set errorWorkflow in settings.",
                severity=Severity.WARNING,
            )
        )

    return issues


def check_webhook_timeout(workflow: dict[str, Any]) -> list[ValidationIssue]:
    """Check if Webhook nodes have appropriate timeout settings.

    Rule: Webhook nodes should have explicit timeout configuration.
    """
    issues: list[ValidationIssue] = []
    nodes = get_nodes(workflow)

    for node in nodes:
        node_type = get_node_type(node)
        node_name = get_node_name(node)

        # Check if it's a Webhook node
        if "webhook" not in node_type.lower():
            continue

        # Check for timeout in options
        options = node.get("parameters", {}).get("options", {})
        response_mode = node.get("parameters", {}).get("responseMode", "")

        # If webhook waits for response, timeout is important
        if response_mode == "responseNode" or response_mode == "lastNode":
            if "timeout" not in options:
                issues.append(
                    ValidationIssue(
                        rule="webhook-timeout",
                        message=f"Webhook '{node_name}' waits for response but has no timeout configured.",
                        severity=Severity.WARNING,
                        node_name=node_name,
                    )
                )

    return issues


def validate_workflow(workflow: dict[str, Any]) -> ValidationResult:
    """Run all validation checks on a workflow.

    Args:
        workflow: Parsed n8n workflow dictionary.

    Returns:
        ValidationResult containing all issues found.
    """
    workflow_name = workflow.get("name", "Unnamed Workflow")
    all_issues: list[ValidationIssue] = []

    # Run all checks
    all_issues.extend(check_error_handling(workflow))
    all_issues.extend(check_webhook_timeout(workflow))

    return ValidationResult(workflow_name=workflow_name, issues=all_issues)
