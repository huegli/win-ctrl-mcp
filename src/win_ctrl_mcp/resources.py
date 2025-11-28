"""MCP Resources for AeroSpace.

This module provides read-only resources for querying AeroSpace state.
"""

from typing import Any

from win_ctrl_mcp.aerospace import (
    ERROR_WINDOW_NOT_FOUND,
    ERROR_WORKSPACE_NOT_FOUND,
    AeroSpaceError,
    get_focused_monitor,
    get_focused_window,
    get_focused_workspace,
    list_monitors,
    list_windows,
    list_workspaces,
    run_aerospace_command,
)
from win_ctrl_mcp.tools.display import get_display_by_id, get_display_info


async def get_windows_resource() -> dict[str, Any]:
    """Get list of all windows with metadata.

    Resource URI: aerospace://windows

    Returns:
        Dictionary with windows list and count
    """
    windows = await list_windows(all_windows=True)

    result = []
    for w in windows:
        # Get focused status
        focused_window = await get_focused_window()
        is_focused = focused_window and focused_window.get("window-id") == w.get("window-id")

        result.append(
            {
                "window_id": w.get("window-id"),
                "app_name": w.get("app-name"),
                "app_bundle_id": w.get("app-bundle-id", ""),
                "title": w.get("title", ""),
                "workspace": w.get("workspace"),
                "monitor": w.get("monitor", ""),
                "is_focused": is_focused,
                "is_fullscreen": w.get("is-fullscreen", False),
                "is_floating": w.get("is-floating", False),
            }
        )

    return {
        "windows": result,
        "total_count": len(result),
    }


async def get_window_resource(window_id: int) -> dict[str, Any]:
    """Get details for a specific window.

    Resource URI: aerospace://windows/{window_id}

    Args:
        window_id: The window ID

    Returns:
        Window details dictionary

    Raises:
        AeroSpaceError: If window not found
    """
    windows = await list_windows(all_windows=True)

    for w in windows:
        if w.get("window-id") == window_id:
            focused_window = await get_focused_window()
            is_focused = focused_window and focused_window.get("window-id") == window_id

            return {
                "window_id": window_id,
                "app_name": w.get("app-name"),
                "app_bundle_id": w.get("app-bundle-id", ""),
                "title": w.get("title", ""),
                "workspace": w.get("workspace"),
                "monitor": w.get("monitor", ""),
                "is_focused": is_focused,
                "is_fullscreen": w.get("is-fullscreen", False),
                "is_floating": w.get("is-floating", False),
                "parent_container": w.get("parent-container", ""),
            }

    available_ids = [w.get("window-id") for w in windows]
    raise AeroSpaceError(
        ERROR_WINDOW_NOT_FOUND,
        f"Window with ID {window_id} not found",
        {"requested_window_id": window_id, "available_windows": available_ids},
    )


async def get_workspaces_resource() -> dict[str, Any]:
    """Get list of all workspaces.

    Resource URI: aerospace://workspaces

    Returns:
        Dictionary with workspaces list and count
    """
    workspaces = await list_workspaces(all_workspaces=True)

    result = []
    for ws in workspaces:
        # Get window count for workspace
        windows = await list_windows(workspace=ws.get("workspace"))

        # Check if focused
        focused_ws = await get_focused_workspace()
        is_focused = focused_ws and focused_ws.get("workspace") == ws.get("workspace")

        # Check if visible
        visible_workspaces = await list_workspaces(visible=True)
        is_visible = any(v.get("workspace") == ws.get("workspace") for v in visible_workspaces)

        result.append(
            {
                "name": ws.get("workspace"),
                "monitor": ws.get("monitor"),
                "is_focused": is_focused,
                "is_visible": is_visible,
                "window_count": len(windows),
            }
        )

    return {
        "workspaces": result,
        "total_count": len(result),
    }


async def get_workspace_resource(workspace_name: str) -> dict[str, Any]:
    """Get details for a specific workspace.

    Resource URI: aerospace://workspaces/{workspace_name}

    Args:
        workspace_name: The workspace name

    Returns:
        Workspace details dictionary

    Raises:
        AeroSpaceError: If workspace not found
    """
    workspaces = await list_workspaces(all_workspaces=True)

    for ws in workspaces:
        if ws.get("workspace") == workspace_name:
            # Get windows in workspace
            windows = await list_windows(workspace=workspace_name)

            # Check if focused
            focused_ws = await get_focused_workspace()
            is_focused = focused_ws and focused_ws.get("workspace") == workspace_name

            # Check if visible
            visible_workspaces = await list_workspaces(visible=True)
            is_visible = any(v.get("workspace") == workspace_name for v in visible_workspaces)

            window_list = [
                {
                    "window_id": w.get("window-id"),
                    "app_name": w.get("app-name"),
                    "title": w.get("title", ""),
                }
                for w in windows
            ]

            return {
                "name": workspace_name,
                "monitor": ws.get("monitor"),
                "is_focused": is_focused,
                "is_visible": is_visible,
                "windows": window_list,
                "layout": ws.get("layout", ""),
            }

    available = [ws.get("workspace") for ws in workspaces]
    raise AeroSpaceError(
        ERROR_WORKSPACE_NOT_FOUND,
        f"Workspace '{workspace_name}' not found",
        {"requested_workspace": workspace_name, "available_workspaces": available},
    )


async def get_monitors_resource() -> dict[str, Any]:
    """Get list of all monitors.

    Resource URI: aerospace://monitors

    Returns:
        Dictionary with monitors list and count
    """
    monitors = await list_monitors()
    workspaces = await list_workspaces(all_workspaces=True)

    result = []
    for i, m in enumerate(monitors):
        # Get workspaces for this monitor
        monitor_workspaces = [
            ws.get("workspace") for ws in workspaces if ws.get("monitor") == m.get("name")
        ]

        # Get focused workspace for this monitor
        focused_ws = None
        visible_workspaces = await list_workspaces(visible=True)
        for vws in visible_workspaces:
            if vws.get("monitor") == m.get("name"):
                focused_ws = vws.get("workspace")
                break

        result.append(
            {
                "id": i + 1,
                "name": m.get("name"),
                "is_main": i == 0,  # First monitor is typically main
                "workspaces": monitor_workspaces,
                "focused_workspace": focused_ws,
            }
        )

    return {
        "monitors": result,
        "total_count": len(result),
    }


async def get_tree_resource() -> dict[str, Any]:
    """Get the current window tree structure.

    Resource URI: aerospace://tree

    Returns:
        Dictionary with tree structure
    """
    # Use debug-windows to get tree structure
    stdout, _, _ = await run_aerospace_command("debug-windows", check=False)

    # Parse the tree output
    # The debug-windows command outputs a text representation
    # For simplicity, we'll return the focused workspace tree

    focused_ws = await get_focused_workspace()
    ws_name = focused_ws.get("workspace") if focused_ws else "1"

    windows = await list_windows(workspace=ws_name)

    # Build a simple tree structure
    children = []
    for w in windows:
        children.append(
            {
                "type": "window",
                "window_id": w.get("window-id"),
                "app_name": w.get("app-name"),
                "title": w.get("title", ""),
            }
        )

    tree = {
        "type": "workspace",
        "name": ws_name,
        "layout": focused_ws.get("layout", "h_tiles") if focused_ws else "h_tiles",
        "children": children,
    }

    return {"tree": tree}


async def get_focused_resource() -> dict[str, Any]:
    """Get currently focused window, workspace, and monitor info.

    Resource URI: aerospace://focused

    Returns:
        Dictionary with focused state
    """
    window = await get_focused_window()
    workspace = await get_focused_workspace()
    monitor = await get_focused_monitor()

    return {
        "window": {
            "window_id": window.get("window-id") if window else None,
            "app_name": window.get("app-name") if window else None,
            "title": window.get("title", "") if window else None,
        }
        if window
        else None,
        "workspace": {
            "name": workspace.get("workspace") if workspace else None,
            "window_count": len(await list_windows(workspace=workspace.get("workspace")))
            if workspace
            else 0,
        }
        if workspace
        else None,
        "monitor": {
            "id": 1,  # Would need more info to get actual ID
            "name": monitor.get("name") if monitor else None,
        }
        if monitor
        else None,
    }


async def get_displays_resource() -> dict[str, Any]:
    """Get complete display configuration information.

    Resource URI: aerospace://displays

    Returns:
        Dictionary with display configuration
    """
    display_info = await get_display_info()

    # Add workspace information to each display
    workspaces = await list_workspaces(all_workspaces=True)

    for display in display_info.get("displays", []):
        display_name = display.get("name")
        display["workspaces"] = [
            ws.get("workspace") for ws in workspaces if ws.get("monitor") == display_name
        ]

    # Add category description
    from win_ctrl_mcp.tools.display import _calculate_display_category

    category, description = _calculate_display_category(display_info.get("displays", []))
    display_info["category_description"] = description

    return display_info


async def get_display_resource(display_id: int) -> dict[str, Any]:
    """Get individual display details.

    Resource URI: aerospace://displays/{display_id}

    Args:
        display_id: The display ID

    Returns:
        Display details dictionary

    Raises:
        AeroSpaceError: If display not found
    """
    display = await get_display_by_id(display_id)

    if display is None:
        display_info = await get_display_info()
        available_ids = [d.get("id") for d in display_info.get("displays", [])]
        raise AeroSpaceError(
            "DISPLAY_NOT_FOUND",
            f"Display with ID {display_id} not found",
            {"requested_display_id": display_id, "available_displays": available_ids},
        )

    return display
