"""Tests for the loader module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from n8n_validator.loader import WorkflowLoadResult, load_workflow, load_workflows


@pytest.fixture
def valid_workflow(tmp_path: Path) -> Path:
    """Create a valid workflow JSON file."""
    workflow = {
        "name": "Test Workflow",
        "nodes": [],
        "connections": {},
    }
    file_path = tmp_path / "valid_workflow.json"
    file_path.write_text(json.dumps(workflow))
    return file_path


@pytest.fixture
def invalid_json_file(tmp_path: Path) -> Path:
    """Create a file with invalid JSON."""
    file_path = tmp_path / "invalid.json"
    file_path.write_text("{invalid json}")
    return file_path


@pytest.fixture
def non_object_json_file(tmp_path: Path) -> Path:
    """Create a JSON file that is not an object."""
    file_path = tmp_path / "array.json"
    file_path.write_text("[]")
    return file_path


class TestLoadWorkflow:
    """Tests for load_workflow function."""

    def test_load_valid_workflow(self, valid_workflow: Path) -> None:
        """Test loading a valid workflow file."""
        result = load_workflow(valid_workflow)

        assert result.success is True
        assert result.workflow is not None
        assert result.workflow["name"] == "Test Workflow"
        assert result.error is None
        assert result.file_path == valid_workflow

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test loading a non-existent file."""
        result = load_workflow(tmp_path / "nonexistent.json")

        assert result.success is False
        assert result.workflow is None
        assert "File not found" in result.error

    def test_invalid_extension(self, tmp_path: Path) -> None:
        """Test loading a file with wrong extension."""
        file_path = tmp_path / "workflow.txt"
        file_path.write_text("{}")

        result = load_workflow(file_path)

        assert result.success is False
        assert "Invalid file extension" in result.error

    def test_invalid_json(self, invalid_json_file: Path) -> None:
        """Test loading a file with invalid JSON."""
        result = load_workflow(invalid_json_file)

        assert result.success is False
        assert "Invalid JSON" in result.error

    def test_non_object_json(self, non_object_json_file: Path) -> None:
        """Test loading a JSON file that is not an object."""
        result = load_workflow(non_object_json_file)

        assert result.success is False
        assert "must be a JSON object" in result.error

    def test_directory_path(self, tmp_path: Path) -> None:
        """Test that directories are rejected."""
        result = load_workflow(tmp_path)

        assert result.success is False
        assert "Not a file" in result.error


class TestLoadWorkflows:
    """Tests for load_workflows function."""

    def test_load_multiple_workflows(
        self, valid_workflow: Path, invalid_json_file: Path
    ) -> None:
        """Test loading multiple workflow files."""
        results = load_workflows([valid_workflow, invalid_json_file])

        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is False

    def test_empty_list(self) -> None:
        """Test loading an empty list."""
        results = load_workflows([])
        assert results == []
