"""AeroSpace CLI interface.

This module provides functions to execute AeroSpace CLI commands
and parse their output.
"""

import asyncio
import json
import os
import subprocess
from typing import Any

# Error codes
ERROR_AEROSPACE_NOT_RUNNING = "AEROSPACE_NOT_RUNNING"
ERROR_WINDOW_NOT_FOUND = "WINDOW_NOT_FOUND"
ERROR_WORKSPACE_NOT_FOUND = "WORKSPACE_NOT_FOUND"
ERROR_INVALID_DIRECTION = "INVALID_DIRECTION"
ERROR_INVALID_LAYOUT = "INVALID_LAYOUT"
ERROR_NO_WINDOW_FOCUSED = "NO_WINDOW_FOCUSED"
ERROR_COMMAND_FAILED = "COMMAND_FAILED"

# Valid directions for focus/move commands
VALID_DIRECTIONS = {"left", "right", "up", "down"}

# Valid layout modes
VALID_LAYOUTS = {
    "tiles",
    "accordion",
    "h_tiles",
    "v_tiles",
    "h_accordion",
    "v_accordion",
    "floating",
    "tiling",
}


class AeroSpaceError(Exception):
    """Base exception for AeroSpace errors."""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            },
        }


async def run_aerospace_command(
    *args: str,
    json_output: bool = False,
    check: bool = True,
) -> tuple[str, str, int]:
    """Run an aerospace CLI command asynchronously.

    Args:
        *args: Command arguments to pass to aerospace CLI
        json_output: If True, add --json flag
        check: If True, raise exception on non-zero exit code

    Returns:
        Tuple of (stdout, stderr, return_code)

    Raises:
        AeroSpaceError: If command fails and check is True
    """
    cmd = ["aerospace", *args]
    if json_output:
        cmd.append("--json")

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        stdout_str = stdout.decode("utf-8").strip()
        stderr_str = stderr.decode("utf-8").strip()

        if check and proc.returncode != 0:
            # Check for common error conditions
            if "aerospace" not in os.environ.get("PATH", "") and proc.returncode == 127:
                raise AeroSpaceError(
                    ERROR_AEROSPACE_NOT_RUNNING,
                    "AeroSpace CLI not found. Please ensure AeroSpace is installed and in PATH.",
                    {
                        "suggestion": "Install AeroSpace from https://nikitabobko.github.io/AeroSpace/"
                    },
                )
            raise AeroSpaceError(
                ERROR_COMMAND_FAILED,
                f"AeroSpace command failed: {stderr_str or stdout_str}",
                {"command": cmd, "return_code": proc.returncode, "stderr": stderr_str},
            )

        return stdout_str, stderr_str, proc.returncode or 0

    except FileNotFoundError:
        raise AeroSpaceError(
            ERROR_AEROSPACE_NOT_RUNNING,
            "AeroSpace daemon is not running. Please start it first.",
            {"suggestion": "Run 'aerospace start' or launch AeroSpace from Applications"},
        )


def run_aerospace_command_sync(
    *args: str,
    json_output: bool = False,
    check: bool = True,
) -> tuple[str, str, int]:
    """Run an aerospace CLI command synchronously.

    Args:
        *args: Command arguments to pass to aerospace CLI
        json_output: If True, add --json flag
        check: If True, raise exception on non-zero exit code

    Returns:
        Tuple of (stdout, stderr, return_code)

    Raises:
        AeroSpaceError: If command fails and check is True
    """
    cmd = ["aerospace", *args]
    if json_output:
        cmd.append("--json")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        stdout_str = result.stdout.strip()
        stderr_str = result.stderr.strip()

        if check and result.returncode != 0:
            if result.returncode == 127:
                raise AeroSpaceError(
                    ERROR_AEROSPACE_NOT_RUNNING,
                    "AeroSpace CLI not found. Please ensure AeroSpace is installed and in PATH.",
                    {
                        "suggestion": "Install AeroSpace from https://nikitabobko.github.io/AeroSpace/"
                    },
                )
            raise AeroSpaceError(
                ERROR_COMMAND_FAILED,
                f"AeroSpace command failed: {stderr_str or stdout_str}",
                {"command": cmd, "return_code": result.returncode, "stderr": stderr_str},
            )

        return stdout_str, stderr_str, result.returncode

    except FileNotFoundError:
        raise AeroSpaceError(
            ERROR_AEROSPACE_NOT_RUNNING,
            "AeroSpace daemon is not running. Please start it first.",
            {"suggestion": "Run 'aerospace start' or launch AeroSpace from Applications"},
        )


async def list_windows(
    workspace: str | None = None,
    monitor: str | None = None,
    all_windows: bool = True,
) -> list[dict[str, Any]]:
    """List windows with optional filtering.

    Args:
        workspace: Filter by workspace name
        monitor: Filter by monitor name
        all_windows: If True, list all windows

    Returns:
        List of window dictionaries
    """
    args = ["list-windows"]
    if all_windows:
        args.append("--all")
    if workspace:
        args.extend(["--workspace", workspace])
    if monitor:
        args.extend(["--monitor", monitor])

    stdout, _, _ = await run_aerospace_command(*args, json_output=True)
    if not stdout:
        return []

    result: list[dict[str, Any]] = json.loads(stdout)
    return result


async def list_workspaces(
    all_workspaces: bool = True,
    monitor: str | None = None,
    visible: bool = False,
    focused: bool = False,
) -> list[dict[str, Any]]:
    """List workspaces with optional filtering.

    Args:
        all_workspaces: If True, list all workspaces
        monitor: Filter by monitor name
        visible: If True, only visible workspaces
        focused: If True, only focused workspace

    Returns:
        List of workspace dictionaries
    """
    args = ["list-workspaces"]
    if all_workspaces:
        args.append("--all")
    if monitor:
        args.extend(["--monitor", monitor])
    if visible:
        args.append("--visible")
    if focused:
        args.append("--focused")

    stdout, _, _ = await run_aerospace_command(*args, json_output=True)
    if not stdout:
        return []

    result: list[dict[str, Any]] = json.loads(stdout)
    return result


async def list_monitors() -> list[dict[str, Any]]:
    """List all monitors.

    Returns:
        List of monitor dictionaries
    """
    args = ["list-monitors"]
    stdout, _, _ = await run_aerospace_command(*args, json_output=True)
    if not stdout:
        return []

    result: list[dict[str, Any]] = json.loads(stdout)
    return result


async def get_focused_window() -> dict[str, Any] | None:
    """Get the currently focused window.

    Returns:
        Window dictionary or None if no window is focused
    """
    args = ["list-windows", "--focused"]
    stdout, _, code = await run_aerospace_command(*args, json_output=True, check=False)
    if code != 0 or not stdout:
        return None

    windows = json.loads(stdout)
    return windows[0] if windows else None


async def get_focused_workspace() -> dict[str, Any] | None:
    """Get the currently focused workspace.

    Returns:
        Workspace dictionary or None
    """
    args = ["list-workspaces", "--focused"]
    stdout, _, code = await run_aerospace_command(*args, json_output=True, check=False)
    if code != 0 or not stdout:
        return None

    workspaces = json.loads(stdout)
    return workspaces[0] if workspaces else None


async def get_focused_monitor() -> dict[str, Any] | None:
    """Get the currently focused monitor.

    Returns:
        Monitor dictionary or None
    """
    args = ["list-monitors", "--focused"]
    stdout, _, code = await run_aerospace_command(*args, json_output=True, check=False)
    if code != 0 or not stdout:
        return None

    monitors = json.loads(stdout)
    return monitors[0] if monitors else None


def validate_direction(direction: str) -> None:
    """Validate a direction parameter.

    Args:
        direction: Direction to validate

    Raises:
        AeroSpaceError: If direction is invalid
    """
    if direction not in VALID_DIRECTIONS:
        raise AeroSpaceError(
            ERROR_INVALID_DIRECTION,
            f"Invalid direction '{direction}'. Must be one of: {', '.join(sorted(VALID_DIRECTIONS))}",
            {"provided": direction, "valid_options": sorted(VALID_DIRECTIONS)},
        )


def validate_layout(layout: str) -> None:
    """Validate a layout parameter.

    Args:
        layout: Layout to validate

    Raises:
        AeroSpaceError: If layout is invalid
    """
    if layout not in VALID_LAYOUTS:
        raise AeroSpaceError(
            ERROR_INVALID_LAYOUT,
            f"Invalid layout '{layout}'. Must be one of: {', '.join(sorted(VALID_LAYOUTS))}",
            {"provided": layout, "valid_options": sorted(VALID_LAYOUTS)},
        )


async def get_window_by_id(window_id: int) -> dict[str, Any] | None:
    """Get a window by its ID.

    Args:
        window_id: Window ID to find

    Returns:
        Window dictionary or None if not found
    """
    windows = await list_windows(all_windows=True)
    for window in windows:
        if window.get("window-id") == window_id:
            return window
    return None
