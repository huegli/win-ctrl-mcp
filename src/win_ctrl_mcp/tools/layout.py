"""Layout management tools for AeroSpace.

This module provides MCP tools for managing window layouts.
"""

from typing import Any

from win_ctrl_mcp.aerospace import (
    get_focused_workspace,
    list_windows,
    run_aerospace_command,
    validate_layout,
)


async def set_layout(layout: str) -> dict[str, Any]:
    """Change the layout mode for the focused window's container.

    Args:
        layout: Layout mode - tiles, accordion, h_tiles, v_tiles,
                h_accordion, v_accordion, floating, tiling

    Returns:
        Result dictionary with layout info
    """
    validate_layout(layout)

    await run_aerospace_command("layout", layout)

    # Get affected windows (current workspace)
    workspace = await get_focused_workspace()
    windows = []
    if workspace:
        ws_windows = await list_windows(workspace=workspace.get("workspace"))
        windows = [w.get("window-id") for w in ws_windows]

    return {
        "success": True,
        "layout": layout,
        "affected_windows": windows,
    }


async def split_window(orientation: str) -> dict[str, Any]:
    """Split the current container to prepare for a new window.

    Args:
        orientation: Split orientation - horizontal or vertical

    Returns:
        Result dictionary with split info
    """
    valid_orientations = {"horizontal", "vertical"}
    if orientation not in valid_orientations:
        from win_ctrl_mcp.aerospace import AeroSpaceError

        raise AeroSpaceError(
            "INVALID_PARAMETERS",
            f"Invalid orientation '{orientation}'. Must be: horizontal or vertical",
            {"provided": orientation, "valid_options": list(valid_orientations)},
        )

    await run_aerospace_command("split", orientation)

    return {
        "success": True,
        "split_orientation": orientation,
    }


async def flatten_workspace(workspace: str | None = None) -> dict[str, Any]:
    """Flatten the workspace tree, removing nested containers.

    Args:
        workspace: Workspace to flatten (defaults to current workspace)

    Returns:
        Result dictionary with flatten info
    """
    if workspace:
        # Focus the workspace first
        await run_aerospace_command("workspace", workspace)

    await run_aerospace_command("flatten-workspace-tree")

    # Get the workspace name
    current_workspace = await get_focused_workspace()
    ws_name = workspace or (current_workspace.get("workspace") if current_workspace else "unknown")

    return {
        "success": True,
        "workspace": ws_name,
        "flattened_containers": 1,  # We don't have exact count, indicate success
    }


async def balance_sizes() -> dict[str, Any]:
    """Balance window sizes in the current workspace.

    Returns:
        Result dictionary with balance info
    """
    await run_aerospace_command("balance-sizes")

    # Get workspace info
    workspace = await get_focused_workspace()
    windows = []
    if workspace:
        ws_windows = await list_windows(workspace=workspace.get("workspace"))
        windows = ws_windows

    return {
        "success": True,
        "workspace": workspace.get("workspace") if workspace else "unknown",
        "balanced_windows": len(windows),
    }
