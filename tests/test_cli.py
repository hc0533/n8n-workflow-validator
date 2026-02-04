"""Tests for the CLI module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from n8n_validator.cli import main


@pytest.fixture
def valid_workflow_file(tmp_path: Path) -> Path:
    """Create a valid workflow with error handling."""
    workflow = {
        "name": "Valid Workflow",
        "nodes": [{"name": "Error", "type": "n8n-nodes-base.errorTrigger"}],
    }
    file_path = tmp_path / "valid.json"
    file_path.write_text(json.dumps(workflow))
    return file_path


@pytest.fixture
def invalid_workflow_file(tmp_path: Path) -> Path:
    """Create a workflow with issues."""
    workflow = {"name": "Problem Workflow", "nodes": []}
    file_path = tmp_path / "invalid.json"
    file_path.write_text(json.dumps(workflow))
    return file_path


class TestCli:
    """Tests for CLI main function."""

    def test_valid_workflow_returns_zero(self, valid_workflow_file: Path) -> None:
        """Valid workflow should return exit code 0."""
        exit_code = main([str(valid_workflow_file)])
        assert exit_code == 0

    def test_file_not_found_returns_one(self, tmp_path: Path) -> None:
        """Missing file should return exit code 1."""
        exit_code = main([str(tmp_path / "missing.json")])
        assert exit_code == 1

    def test_json_output(self, valid_workflow_file: Path, capsys) -> None:
        """--json flag should output JSON."""
        main([str(valid_workflow_file), "--json"])
        output = capsys.readouterr().out
        parsed = json.loads(output)
        assert parsed["workflow_name"] == "Valid Workflow"
