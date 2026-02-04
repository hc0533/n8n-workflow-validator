"""Tests for the validators module."""

from __future__ import annotations

import pytest

from n8n_validator.validators import (
    Severity,
    ValidationIssue,
    ValidationResult,
    check_error_handling,
    check_webhook_timeout,
    validate_workflow,
)


class TestCheckErrorHandling:
    """Tests for error handling validation."""

    def test_no_error_handling_warns(self) -> None:
        """Workflow without error handling should produce warning."""
        workflow = {
            "name": "Test Workflow",
            "nodes": [
                {"name": "Start", "type": "n8n-nodes-base.start"},
            ],
        }

        issues = check_error_handling(workflow)

        assert len(issues) == 1
        assert issues[0].rule == "error-handling"
        assert issues[0].severity == Severity.WARNING

    def test_error_trigger_node_passes(self) -> None:
        """Workflow with Error Trigger node should pass."""
        workflow = {
            "name": "Test Workflow",
            "nodes": [
                {"name": "Start", "type": "n8n-nodes-base.start"},
                {"name": "Error Handler", "type": "n8n-nodes-base.errorTrigger"},
            ],
        }

        issues = check_error_handling(workflow)

        assert len(issues) == 0

    def test_error_workflow_setting_passes(self) -> None:
        """Workflow with errorWorkflow setting should pass."""
        workflow = {
            "name": "Test Workflow",
            "nodes": [
                {"name": "Start", "type": "n8n-nodes-base.start"},
            ],
            "settings": {
                "errorWorkflow": "error-handler-workflow-id",
            },
        }

        issues = check_error_handling(workflow)

        assert len(issues) == 0

    def test_empty_workflow(self) -> None:
        """Empty workflow should produce warning."""
        workflow = {"name": "Empty"}

        issues = check_error_handling(workflow)

        assert len(issues) == 1


class TestCheckWebhookTimeout:
    """Tests for webhook timeout validation."""

    def test_webhook_without_response_mode_passes(self) -> None:
        """Webhook that responds immediately doesn't need timeout."""
        workflow = {
            "name": "Test Workflow",
            "nodes": [
                {
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {
                        "responseMode": "onReceived",
                    },
                },
            ],
        }

        issues = check_webhook_timeout(workflow)

        assert len(issues) == 0

    def test_webhook_response_node_without_timeout_warns(self) -> None:
        """Webhook waiting for response without timeout should warn."""
        workflow = {
            "name": "Test Workflow",
            "nodes": [
                {
                    "name": "My Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {
                        "responseMode": "responseNode",
                    },
                },
            ],
        }

        issues = check_webhook_timeout(workflow)

        assert len(issues) == 1
        assert issues[0].rule == "webhook-timeout"
        assert issues[0].node_name == "My Webhook"
        assert "timeout" in issues[0].message.lower()

    def test_webhook_last_node_without_timeout_warns(self) -> None:
        """Webhook waiting for lastNode without timeout should warn."""
        workflow = {
            "name": "Test Workflow",
            "nodes": [
                {
                    "name": "API Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {
                        "responseMode": "lastNode",
                    },
                },
            ],
        }

        issues = check_webhook_timeout(workflow)

        assert len(issues) == 1
        assert issues[0].node_name == "API Webhook"

    def test_webhook_with_timeout_passes(self) -> None:
        """Webhook with timeout configured should pass."""
        workflow = {
            "name": "Test Workflow",
            "nodes": [
                {
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {
                        "responseMode": "responseNode",
                        "options": {
                            "timeout": 30000,
                        },
                    },
                },
            ],
        }

        issues = check_webhook_timeout(workflow)

        assert len(issues) == 0

    def test_non_webhook_nodes_ignored(self) -> None:
        """Non-webhook nodes should be ignored."""
        workflow = {
            "name": "Test Workflow",
            "nodes": [
                {
                    "name": "HTTP Request",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {},
                },
            ],
        }

        issues = check_webhook_timeout(workflow)

        assert len(issues) == 0


class TestValidateWorkflow:
    """Tests for the main validate_workflow function."""

    def test_returns_validation_result(self) -> None:
        """Should return ValidationResult with workflow name."""
        workflow = {"name": "My Workflow", "nodes": []}

        result = validate_workflow(workflow)

        assert isinstance(result, ValidationResult)
        assert result.workflow_name == "My Workflow"

    def test_collects_all_issues(self) -> None:
        """Should collect issues from all validators."""
        workflow = {
            "name": "Problem Workflow",
            "nodes": [
                {
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {"responseMode": "lastNode"},
                },
            ],
        }

        result = validate_workflow(workflow)

        # Should have both error-handling and webhook-timeout issues
        rules = [issue.rule for issue in result.issues]
        assert "error-handling" in rules
        assert "webhook-timeout" in rules

    def test_unnamed_workflow(self) -> None:
        """Workflow without name should use default."""
        result = validate_workflow({})

        assert result.workflow_name == "Unnamed Workflow"


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_is_valid_with_no_issues(self) -> None:
        """Should be valid when no issues."""
        result = ValidationResult(workflow_name="Test", issues=[])

        assert result.is_valid is True

    def test_is_valid_with_warnings_only(self) -> None:
        """Should be valid when only warnings."""
        result = ValidationResult(
            workflow_name="Test",
            issues=[
                ValidationIssue(rule="test", message="warning", severity=Severity.WARNING)
            ],
        )

        assert result.is_valid is True

    def test_is_invalid_with_errors(self) -> None:
        """Should be invalid when has errors."""
        result = ValidationResult(
            workflow_name="Test",
            issues=[
                ValidationIssue(rule="test", message="error", severity=Severity.ERROR)
            ],
        )

        assert result.is_valid is False

    def test_error_count(self) -> None:
        """Should count errors correctly."""
        result = ValidationResult(
            workflow_name="Test",
            issues=[
                ValidationIssue(rule="a", message="", severity=Severity.ERROR),
                ValidationIssue(rule="b", message="", severity=Severity.WARNING),
                ValidationIssue(rule="c", message="", severity=Severity.ERROR),
            ],
        )

        assert result.error_count == 2
        assert result.warning_count == 1
