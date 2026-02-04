"""Workflow loader module for loading and parsing n8n workflow JSON files."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class WorkflowLoadResult:
    """Result of loading a workflow file."""

    success: bool
    workflow: dict[str, Any] | None = None
    error: str | None = None
    file_path: Path | None = None


def load_workflow(file_path: str | Path) -> WorkflowLoadResult:
    """Load an n8n workflow from a JSON file.

    Args:
        file_path: Path to the workflow JSON file.

    Returns:
        WorkflowLoadResult containing the parsed workflow or error information.
    """
    path = Path(file_path)

    if not path.exists():
        return WorkflowLoadResult(
            success=False,
            error=f"File not found: {path}",
            file_path=path,
        )

    if not path.is_file():
        return WorkflowLoadResult(
            success=False,
            error=f"Not a file: {path}",
            file_path=path,
        )

    if path.suffix.lower() != ".json":
        return WorkflowLoadResult(
            success=False,
            error=f"Invalid file extension: {path.suffix} (expected .json)",
            file_path=path,
        )

    try:
        with open(path, encoding="utf-8") as f:
            workflow = json.load(f)
    except json.JSONDecodeError as e:
        return WorkflowLoadResult(
            success=False,
            error=f"Invalid JSON: {e}",
            file_path=path,
        )
    except OSError as e:
        return WorkflowLoadResult(
            success=False,
            error=f"Failed to read file: {e}",
            file_path=path,
        )

    if not isinstance(workflow, dict):
        return WorkflowLoadResult(
            success=False,
            error="Workflow must be a JSON object",
            file_path=path,
        )

    return WorkflowLoadResult(
        success=True,
        workflow=workflow,
        file_path=path,
    )


def load_workflows(file_paths: list[str | Path]) -> list[WorkflowLoadResult]:
    """Load multiple n8n workflows from JSON files.

    Args:
        file_paths: List of paths to workflow JSON files.

    Returns:
        List of WorkflowLoadResult for each file.
    """
    return [load_workflow(path) for path in file_paths]
