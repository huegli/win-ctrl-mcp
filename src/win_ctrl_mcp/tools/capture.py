"""Capture tools for AeroSpace.

This module provides MCP tools for capturing window and workspace screenshots.
Uses the macOS screencapture utility.
"""

import asyncio
import os
import tempfile
from typing import Any

from win_ctrl_mcp.aerospace import (
    ERROR_NO_WINDOW_FOCUSED,
    ERROR_WINDOW_NOT_FOUND,
    AeroSpaceError,
    get_focused_monitor,
    get_focused_window,
    get_focused_workspace,
    get_window_by_id,
    list_monitors,
    list_windows,
)


async def _run_screencapture(
    *args: str,
    output_path: str,
) -> None:
    """Run the macOS screencapture command.

    Args:
        *args: Arguments to pass to screencapture
        output_path: Path to save the screenshot

    Raises:
        AeroSpaceError: If capture fails
    """
    cmd = ["screencapture", *args, output_path]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise AeroSpaceError(
            "CAPTURE_FAILED",
            "Failed to capture screenshot",
            {
                "reason": stderr.decode("utf-8").strip() or "Unknown error",
                "suggestion": "Grant screen recording permission in System Settings > Privacy & Security",
            },
        )


def _get_format_extension(format_type: str) -> str:
    """Get file extension for format type.

    Args:
        format_type: Image format (png, jpg, pdf)

    Returns:
        File extension including dot
    """
    return {
        "png": ".png",
        "jpg": ".jpg",
        "jpeg": ".jpg",
        "pdf": ".pdf",
    }.get(format_type.lower(), ".png")


def _get_format_flag(format_type: str) -> str:
    """Get screencapture format flag.

    Args:
        format_type: Image format

    Returns:
        Format flag for screencapture
    """
    return {
        "png": "png",
        "jpg": "jpg",
        "jpeg": "jpg",
        "pdf": "pdf",
    }.get(format_type.lower(), "png")


async def capture_window(
    window_id: int | None = None,
    output_path: str | None = None,
    format: str = "png",  # noqa: A002
) -> dict[str, Any]:
    """Capture a screenshot of the currently focused window.

    Args:
        window_id: Specific window ID to capture (defaults to focused window)
        output_path: Path to save the screenshot (defaults to temp file)
        format: Image format - png, jpg, pdf (defaults to png)

    Returns:
        Result dictionary with capture info
    """
    # Validate format
    valid_formats = {"png", "jpg", "jpeg", "pdf"}
    if format.lower() not in valid_formats:
        raise AeroSpaceError(
            "INVALID_PARAMETERS",
            f"Invalid format '{format}'. Must be: png, jpg, or pdf",
            {"provided": format, "valid_options": list(valid_formats)},
        )

    # Get the window to capture
    if window_id is not None:
        window = await get_window_by_id(window_id)
        if window is None:
            available = await list_windows(all_windows=True)
            available_ids = [w.get("window-id") for w in available]
            raise AeroSpaceError(
                ERROR_WINDOW_NOT_FOUND,
                f"Window with ID {window_id} not found",
                {"requested_window_id": window_id, "available_windows": available_ids},
            )
    else:
        window = await get_focused_window()
        if window is None:
            raise AeroSpaceError(
                ERROR_NO_WINDOW_FOCUSED,
                "No window is currently focused",
                {"suggestion": "Focus a window first"},
            )
        window_id = window.get("window-id")

    # Determine output path
    if output_path is None:
        ext = _get_format_extension(format)
        output_path = os.path.join(
            tempfile.gettempdir(),
            f"window_capture_{window_id}{ext}",
        )

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Capture the window
    # screencapture -l <window_id> captures a specific window by its CGWindowID
    # Note: AeroSpace window IDs should be CGWindowIDs
    format_flag = _get_format_flag(format)
    await _run_screencapture(
        "-l",
        str(window_id),
        "-t",
        format_flag,
        "-o",  # No shadow
        output_path=output_path,
    )

    # Try to get image dimensions (would need PIL, so we'll skip for now)
    # For a real implementation, you'd use PIL to get dimensions

    return {
        "success": True,
        "capture": {
            "window_id": window_id,
            "app_name": window.get("app-name"),
            "title": window.get("title", ""),
            "file_path": output_path,
            "format": format.lower(),
            "dimensions": {
                "width": None,  # Would require image analysis
                "height": None,
            },
        },
    }


async def capture_workspace(
    workspace: str | None = None,
    output_path: str | None = None,
    format: str = "png",  # noqa: A002
) -> dict[str, Any]:
    """Capture a screenshot of the currently focused workspace (and monitor).

    Args:
        workspace: Workspace name to capture (defaults to focused workspace)
        output_path: Path to save the screenshot (defaults to temp file)
        format: Image format - png, jpg, pdf (defaults to png)

    Returns:
        Result dictionary with capture info
    """
    # Validate format
    valid_formats = {"png", "jpg", "jpeg", "pdf"}
    if format.lower() not in valid_formats:
        raise AeroSpaceError(
            "INVALID_PARAMETERS",
            f"Invalid format '{format}'. Must be: png, jpg, or pdf",
            {"provided": format, "valid_options": list(valid_formats)},
        )

    # Get workspace info
    if workspace:
        # Focus the workspace to ensure we capture the right monitor
        from win_ctrl_mcp.aerospace import run_aerospace_command

        await run_aerospace_command("workspace", workspace)

    current_workspace = await get_focused_workspace()
    ws_name = workspace or (current_workspace.get("workspace") if current_workspace else "unknown")

    # Get monitor info
    monitor = await get_focused_monitor()
    monitors = await list_monitors()

    # Find the monitor ID (display index for screencapture)
    display_index = 1  # Default to main display
    if monitor and monitors:
        for i, m in enumerate(monitors, 1):
            if m.get("name") == monitor.get("name"):
                display_index = i
                break

    # Get windows in workspace
    windows = await list_windows(workspace=ws_name)
    window_info = [
        {"window_id": w.get("window-id"), "app_name": w.get("app-name")} for w in windows
    ]

    # Determine output path
    if output_path is None:
        ext = _get_format_extension(format)
        output_path = os.path.join(
            tempfile.gettempdir(),
            f"workspace_capture_{ws_name}{ext}",
        )

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Capture the display
    format_flag = _get_format_flag(format)
    await _run_screencapture(
        "-D",
        str(display_index),
        "-t",
        format_flag,
        output_path=output_path,
    )

    return {
        "success": True,
        "capture": {
            "workspace": ws_name,
            "monitor": monitor.get("name") if monitor else "Unknown",
            "file_path": output_path,
            "format": format.lower(),
            "dimensions": {
                "width": None,  # Would require image analysis
                "height": None,
            },
            "windows_captured": window_info,
        },
    }
