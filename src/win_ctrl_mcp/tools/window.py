"""Window management tools for AeroSpace.

This module provides MCP tools for window focus, movement, and control.
"""

from typing import Any

from win_ctrl_mcp.aerospace import (
    ERROR_NO_WINDOW_FOCUSED,
    ERROR_WINDOW_NOT_FOUND,
    AeroSpaceError,
    get_focused_window,
    get_window_by_id,
    list_windows,
    run_aerospace_command,
    validate_direction,
)


async def focus_window(
    direction: str | None = None,
    window_id: int | None = None,
) -> dict[str, Any]:
    """Focus a window by direction or window ID.

    Args:
        direction: Direction to focus: left, right, up, down
        window_id: Specific window ID to focus

    Returns:
        Result dictionary with focused window info

    Raises:
        AeroSpaceError: If parameters are invalid or command fails
    """
    if direction is None and window_id is None:
        raise AeroSpaceError(
            "INVALID_PARAMETERS",
            "Either 'direction' or 'window_id' must be provided",
            {"provided_direction": direction, "provided_window_id": window_id},
        )

    if direction is not None and window_id is not None:
        raise AeroSpaceError(
            "INVALID_PARAMETERS",
            "Cannot specify both 'direction' and 'window_id'",
            {"provided_direction": direction, "provided_window_id": window_id},
        )

    if direction is not None:
        validate_direction(direction)
        await run_aerospace_command("focus", direction)
    else:
        # Focus by window ID
        window = await get_window_by_id(window_id)  # type: ignore[arg-type]
        if window is None:
            available = await list_windows(all_windows=True)
            available_ids = [w.get("window-id") for w in available]
            raise AeroSpaceError(
                ERROR_WINDOW_NOT_FOUND,
                f"Window with ID {window_id} not found",
                {"requested_window_id": window_id, "available_windows": available_ids},
            )
        await run_aerospace_command("focus", "--window-id", str(window_id))

    # Get the newly focused window
    focused = await get_focused_window()
    if focused is None:
        return {"success": True, "focused_window": None}

    return {
        "success": True,
        "focused_window": {
            "window_id": focused.get("window-id"),
            "app_name": focused.get("app-name"),
            "title": focused.get("title", ""),
        },
    }


async def focus_monitor(target: str) -> dict[str, Any]:
    """Focus a specific monitor by name, pattern, or direction.

    Args:
        target: Monitor identifier - direction (left, right, up, down), name, or pattern

    Returns:
        Result dictionary with focused monitor info
    """
    await run_aerospace_command("focus-monitor", target)

    # Get updated focus info - note: aerospace doesn't have focused monitor in list-monitors
    # We'll get the focused workspace's monitor
    from win_ctrl_mcp.aerospace import get_focused_workspace, list_monitors

    workspace = await get_focused_workspace()
    monitors = await list_monitors()

    focused_monitor = None
    if workspace and monitors:
        monitor_name = workspace.get("monitor")
        for m in monitors:
            if m.get("name") == monitor_name:
                focused_monitor = m
                break

    return {
        "success": True,
        "focused_monitor": {
            "name": focused_monitor.get("name") if focused_monitor else target,
            "id": focused_monitor.get("monitor-id") if focused_monitor else None,
        },
    }


async def focus_workspace(workspace: str) -> dict[str, Any]:
    """Switch to a specific workspace by name or number.

    Args:
        workspace: Workspace name or number (e.g., "1", "dev", "mail")

    Returns:
        Result dictionary with workspace info
    """
    await run_aerospace_command("workspace", workspace)

    # Get workspace info
    from win_ctrl_mcp.aerospace import list_workspaces

    workspaces = await list_workspaces(all_workspaces=True)
    ws_info = None
    for ws in workspaces:
        if ws.get("workspace") == workspace:
            ws_info = ws
            break

    # Get window count for workspace
    windows = await list_windows(workspace=workspace)

    return {
        "success": True,
        "workspace": {
            "name": workspace,
            "window_count": len(windows),
            "monitor": ws_info.get("monitor") if ws_info else None,
        },
    }


async def move_window(
    target_type: str,
    target: str,
    window_id: int | None = None,
) -> dict[str, Any]:
    """Move the focused window to a different workspace, monitor, or position.

    Args:
        target_type: Type of move: workspace, monitor, or direction
        target: Target destination (workspace name, monitor name, or direction)
        window_id: Specific window ID to move (defaults to focused window)

    Returns:
        Result dictionary with move info
    """
    # Get the window to move
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
        # Focus the window first if specified
        await run_aerospace_command("focus", "--window-id", str(window_id))
        actual_window_id = window_id
    else:
        focused = await get_focused_window()
        if focused is None:
            raise AeroSpaceError(
                ERROR_NO_WINDOW_FOCUSED,
                "No window is currently focused",
                {"suggestion": "Focus a window first"},
            )
        actual_window_id = int(focused.get("window-id", 0))

    # Execute the move based on target_type
    if target_type == "workspace":
        await run_aerospace_command("move-node-to-workspace", target)
    elif target_type == "monitor":
        await run_aerospace_command("move-node-to-monitor", target)
    elif target_type == "direction":
        validate_direction(target)
        await run_aerospace_command("move", target)
    else:
        raise AeroSpaceError(
            "INVALID_PARAMETERS",
            f"Invalid target_type '{target_type}'. Must be: workspace, monitor, or direction",
            {"provided": target_type, "valid_options": ["workspace", "monitor", "direction"]},
        )

    return {
        "success": True,
        "window_id": actual_window_id,
        "moved_to": {
            "type": target_type,
            "name": target,
        },
    }


async def resize_window(
    dimension: str,
    amount: str,
) -> dict[str, Any]:
    """Resize the focused window.

    Args:
        dimension: Dimension to resize: smart, width, height
        amount: Resize amount with sign: +50, -50, +10%, -10%

    Returns:
        Result dictionary with resize info
    """
    valid_dimensions = {"smart", "width", "height"}
    if dimension not in valid_dimensions:
        raise AeroSpaceError(
            "INVALID_PARAMETERS",
            f"Invalid dimension '{dimension}'. Must be: smart, width, or height",
            {"provided": dimension, "valid_options": list(valid_dimensions)},
        )

    focused = await get_focused_window()
    if focused is None:
        raise AeroSpaceError(
            ERROR_NO_WINDOW_FOCUSED,
            "No window is currently focused",
            {"suggestion": "Focus a window first"},
        )

    await run_aerospace_command("resize", dimension, amount)

    return {
        "success": True,
        "window_id": focused.get("window-id"),
        "resize": {
            "dimension": dimension,
            "amount": amount,
        },
    }


async def close_window(window_id: int | None = None) -> dict[str, Any]:
    """Close the focused window or a specific window by ID.

    Args:
        window_id: Specific window ID to close (defaults to focused window)

    Returns:
        Result dictionary with closed window info
    """
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
        closed_window = {
            "window_id": window_id,
            "app_name": window.get("app-name"),
            "title": window.get("title", ""),
        }
        await run_aerospace_command("close", "--window-id", str(window_id))
    else:
        focused = await get_focused_window()
        if focused is None:
            raise AeroSpaceError(
                ERROR_NO_WINDOW_FOCUSED,
                "No window is currently focused",
                {"suggestion": "Focus a window first"},
            )
        closed_window = {
            "window_id": focused.get("window-id"),
            "app_name": focused.get("app-name"),
            "title": focused.get("title", ""),
        }
        await run_aerospace_command("close")

    return {
        "success": True,
        "closed_window": closed_window,
    }


async def fullscreen_toggle(window_id: int | None = None) -> dict[str, Any]:
    """Toggle fullscreen mode for the focused window.

    Note: This uses AeroSpace's native fullscreen, not macOS native fullscreen.

    Args:
        window_id: Specific window ID (defaults to focused window)

    Returns:
        Result dictionary with fullscreen state
    """
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
        # Focus the window first
        await run_aerospace_command("focus", "--window-id", str(window_id))
        actual_window_id = window_id
    else:
        focused = await get_focused_window()
        if focused is None:
            raise AeroSpaceError(
                ERROR_NO_WINDOW_FOCUSED,
                "No window is currently focused",
                {"suggestion": "Focus a window first"},
            )
        actual_window_id = int(focused.get("window-id", 0))

    await run_aerospace_command("fullscreen")

    # Check new state - the window should now be fullscreen or not
    updated_window = await get_window_by_id(actual_window_id)  # type: ignore[arg-type]
    is_fullscreen = False
    if updated_window:
        # AeroSpace doesn't directly expose fullscreen state in list-windows
        # We infer it from the command success
        is_fullscreen = True  # Toggle happened, we assume it's now fullscreen

    return {
        "success": True,
        "window_id": actual_window_id,
        "fullscreen": is_fullscreen,
    }


async def minimize_window(window_id: int | None = None) -> dict[str, Any]:
    """Minimize the focused window or a specific window.

    Args:
        window_id: Specific window ID (defaults to focused window)

    Returns:
        Result dictionary with minimized state
    """
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
        # Focus the window first
        await run_aerospace_command("focus", "--window-id", str(window_id))
        actual_window_id = window_id
    else:
        focused = await get_focused_window()
        if focused is None:
            raise AeroSpaceError(
                ERROR_NO_WINDOW_FOCUSED,
                "No window is currently focused",
                {"suggestion": "Focus a window first"},
            )
        actual_window_id = int(focused.get("window-id", 0))

    await run_aerospace_command("macos-native-minimize")

    return {
        "success": True,
        "window_id": actual_window_id,
        "minimized": True,
    }
