"""Pytest fixtures for win_ctrl_mcp tests."""

import json
from typing import Any
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_aerospace_command():
    """Fixture to mock aerospace command execution."""

    async def _mock_run(
        *args: str,
        json_output: bool = False,  # noqa: ARG001
        check: bool = True,  # noqa: ARG001
    ):
        """Mock aerospace command runner."""
        cmd = args[0] if args else ""

        # Default responses for different commands
        if cmd == "list-windows":
            data = [
                {
                    "window-id": 1234,
                    "app-name": "Firefox",
                    "app-bundle-id": "org.mozilla.firefox",
                    "title": "GitHub - Mozilla Firefox",
                    "workspace": "1",
                    "monitor": "Built-in Retina Display",
                },
                {
                    "window-id": 5678,
                    "app-name": "Terminal",
                    "app-bundle-id": "com.apple.Terminal",
                    "title": "bash - 80x24",
                    "workspace": "1",
                    "monitor": "Built-in Retina Display",
                },
            ]
            return json.dumps(data), "", 0

        elif cmd == "list-workspaces":
            data = [
                {"workspace": "1", "monitor": "Built-in Retina Display"},
                {"workspace": "2", "monitor": "Built-in Retina Display"},
                {"workspace": "dev", "monitor": "DELL U2720Q"},
            ]
            return json.dumps(data), "", 0

        elif cmd == "list-monitors":
            data = [
                {"name": "Built-in Retina Display"},
                {"name": "DELL U2720Q"},
            ]
            return json.dumps(data), "", 0

        else:
            # Default success for action commands
            return "", "", 0

    with patch("win_ctrl_mcp.aerospace.run_aerospace_command", side_effect=_mock_run):
        yield _mock_run


@pytest.fixture
def mock_window_list() -> list[dict[str, Any]]:
    """Sample window list for testing."""
    return [
        {
            "window-id": 1234,
            "app-name": "Firefox",
            "app-bundle-id": "org.mozilla.firefox",
            "title": "GitHub - Mozilla Firefox",
            "workspace": "1",
            "monitor": "Built-in Retina Display",
        },
        {
            "window-id": 5678,
            "app-name": "Terminal",
            "app-bundle-id": "com.apple.Terminal",
            "title": "bash - 80x24",
            "workspace": "1",
            "monitor": "Built-in Retina Display",
        },
        {
            "window-id": 9012,
            "app-name": "Visual Studio Code",
            "app-bundle-id": "com.microsoft.VSCode",
            "title": "project - Visual Studio Code",
            "workspace": "dev",
            "monitor": "DELL U2720Q",
        },
    ]


@pytest.fixture
def mock_workspace_list() -> list[dict[str, Any]]:
    """Sample workspace list for testing."""
    return [
        {"workspace": "1", "monitor": "Built-in Retina Display"},
        {"workspace": "2", "monitor": "Built-in Retina Display"},
        {"workspace": "dev", "monitor": "DELL U2720Q"},
    ]


@pytest.fixture
def mock_monitor_list() -> list[dict[str, Any]]:
    """Sample monitor list for testing."""
    return [
        {"name": "Built-in Retina Display"},
        {"name": "DELL U2720Q"},
    ]
