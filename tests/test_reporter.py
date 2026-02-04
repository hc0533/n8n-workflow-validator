"""Tests for the reporter module."""

from __future__ import annotations

import json

from n8n_validator.reporter import (
    DEFAULT_SUGGESTION,
    format_json,
    format_json_string,
    generate_report,
    get_suggestion,
)
from n8n_validator.validators import Severity, ValidationIssue, ValidationResult


class TestFormatJson:
    """Tests for format_json function."""

    def test_empty_result(self) -> None:
        """Format result with no issues."""
        result = ValidationResult(workflow_name="Test Workflow", issues=[])

        output = format_json(result)

        assert output["workflow_name"] == "Test Workflow"
        assert output["is_valid"] is True
        assert output["summary"]["total_issues"] == 0
        assert output["issues"] == []

    def test_result_with_issues(self) -> None:
        """Format result containing issues."""
        result = ValidationResult(
            workflow_name="Problem Workflow",
            issues=[
                ValidationIssue(
                    rule="error-handling",
                    message="No error handling",
                    severity=Severity.WARNING,
                ),
                ValidationIssue(
                    rule="webhook-timeout",
                    message="Missing timeout",
                    severity=Severity.WARNING,
                    node_name="My Webhook",
                ),
            ],
        )

        output = format_json(result)

        assert output["workflow_name"] == "Problem Workflow"
        assert output["summary"]["total_issues"] == 2
        assert output["summary"]["warnings"] == 2
        assert len(output["issues"]) == 2
        assert output["issues"][0]["rule"] == "error-handling"
        assert output["issues"][1]["node_name"] == "My Webhook"
        assert "suggestion" in output["issues"][0]

    def test_json_string_is_valid(self) -> None:
        """format_json_string should return valid JSON."""
        result = ValidationResult(workflow_name="Test", issues=[])

        json_str = format_json_string(result)
        parsed = json.loads(json_str)

        assert parsed["workflow_name"] == "Test"


class TestGenerateReport:
    """Tests for generate_report function."""

    def test_report_header(self) -> None:
        """Report should include workflow name."""
        result = ValidationResult(workflow_name="My Workflow", issues=[])

        report = generate_report(result)

        assert "My Workflow" in report
        assert "VALID" in report

    def test_report_with_issues(self) -> None:
        """Report should list issues with suggestions."""
        result = ValidationResult(
            workflow_name="Test",
            issues=[
                ValidationIssue(
                    rule="webhook-timeout",
                    message="Missing timeout",
                    severity=Severity.WARNING,
                    node_name="Webhook1",
                ),
            ],
        )

        report = generate_report(result)

        assert "WARNING" in report
        assert "webhook-timeout" in report
        assert "Webhook1" in report
        assert "Suggestion:" in report


class TestGetSuggestion:
    """Tests for get_suggestion function."""

    def test_known_rule(self) -> None:
        """Should return specific suggestion for known rules."""
        suggestion = get_suggestion("error-handling")
        assert "Error Trigger" in suggestion

    def test_unknown_rule(self) -> None:
        """Should return default suggestion for unknown rules."""
        suggestion = get_suggestion("unknown-rule")
        assert suggestion == DEFAULT_SUGGESTION
