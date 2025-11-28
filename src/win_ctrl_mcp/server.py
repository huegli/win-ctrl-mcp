"""AeroSpace MCP Server implementation.

This module defines the FastMCP server with all tools, resources, and prompts.
"""

from typing import Annotated, Any

from fastmcp import FastMCP

from win_ctrl_mcp.aerospace import AeroSpaceError
from win_ctrl_mcp.prompts import PROMPTS
from win_ctrl_mcp.resources import (
    get_display_resource,
    get_displays_resource,
    get_focused_resource,
    get_monitors_resource,
    get_tree_resource,
    get_window_resource,
    get_windows_resource,
    get_workspace_resource,
    get_workspaces_resource,
)
from win_ctrl_mcp.tools.capture import capture_window, capture_workspace
from win_ctrl_mcp.tools.display import get_display_category, get_display_info
from win_ctrl_mcp.tools.focus import (
    apply_focus_preset,
    load_focus_preset,
    move_app_category_to_monitor,
    resize_window_optimal,
    save_focus_preset,
    set_window_zone,
)
from win_ctrl_mcp.tools.layout import balance_sizes, flatten_workspace, set_layout, split_window
from win_ctrl_mcp.tools.window import (
    close_window,
    focus_monitor,
    focus_window,
    focus_workspace,
    fullscreen_toggle,
    minimize_window,
    move_window,
    resize_window,
)

# Create the FastMCP server
mcp = FastMCP(
    "AeroSpace Window Manager",
    instructions="MCP server for controlling the AeroSpace tiling window manager on macOS",
)


def handle_error(e: Exception) -> dict[str, Any]:
    """Convert exception to error response dictionary.

    Args:
        e: The exception to handle

    Returns:
        Error response dictionary
    """
    if isinstance(e, AeroSpaceError):
        return e.to_dict()
    return {
        "success": False,
        "error": {
            "code": "UNKNOWN_ERROR",
            "message": str(e),
            "details": {},
        },
    }


# =============================================================================
# Window Management Tools
# =============================================================================


@mcp.tool()
async def tool_focus_window(
    direction: Annotated[str | None, "Direction to focus: left, right, up, down"] = None,
    window_id: Annotated[int | None, "Specific window ID to focus"] = None,
) -> dict[str, Any]:
    """Focus a window by direction or window ID.

    Either direction or window_id must be provided, but not both.
    """
    try:
        return await focus_window(direction=direction, window_id=window_id)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_focus_monitor(
    target: Annotated[str, "Monitor identifier: direction, name, or pattern"],
) -> dict[str, Any]:
    """Focus a specific monitor by name, pattern, or direction."""
    try:
        return await focus_monitor(target=target)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_focus_workspace(
    workspace: Annotated[str, "Workspace name or number (e.g., '1', 'dev', 'mail')"],
) -> dict[str, Any]:
    """Switch to a specific workspace by name or number."""
    try:
        return await focus_workspace(workspace=workspace)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_move_window(
    target_type: Annotated[str, "Type of move: workspace, monitor, or direction"],
    target: Annotated[str, "Target destination (workspace name, monitor name, or direction)"],
    window_id: Annotated[int | None, "Specific window ID to move (defaults to focused)"] = None,
) -> dict[str, Any]:
    """Move the focused window to a different workspace, monitor, or position."""
    try:
        return await move_window(target_type=target_type, target=target, window_id=window_id)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_resize_window(
    dimension: Annotated[str, "Dimension to resize: smart, width, height"],
    amount: Annotated[str, "Resize amount with sign: +50, -50, +10%, -10%"],
) -> dict[str, Any]:
    """Resize the focused window."""
    try:
        return await resize_window(dimension=dimension, amount=amount)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_close_window(
    window_id: Annotated[int | None, "Specific window ID to close (defaults to focused)"] = None,
) -> dict[str, Any]:
    """Close the focused window or a specific window by ID."""
    try:
        return await close_window(window_id=window_id)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_fullscreen_toggle(
    window_id: Annotated[int | None, "Specific window ID (defaults to focused)"] = None,
) -> dict[str, Any]:
    """Toggle fullscreen mode for the focused window.

    Uses AeroSpace's native fullscreen, not macOS native fullscreen.
    """
    try:
        return await fullscreen_toggle(window_id=window_id)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_minimize_window(
    window_id: Annotated[int | None, "Specific window ID (defaults to focused)"] = None,
) -> dict[str, Any]:
    """Minimize the focused window or a specific window."""
    try:
        return await minimize_window(window_id=window_id)
    except Exception as e:
        return handle_error(e)


# =============================================================================
# Layout Management Tools
# =============================================================================


@mcp.tool()
async def tool_set_layout(
    layout: Annotated[
        str,
        "Layout mode: tiles, accordion, h_tiles, v_tiles, h_accordion, v_accordion, floating, tiling",
    ],
) -> dict[str, Any]:
    """Change the layout mode for the focused window's container."""
    try:
        return await set_layout(layout=layout)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_split_window(
    orientation: Annotated[str, "Split orientation: horizontal or vertical"],
) -> dict[str, Any]:
    """Split the current container to prepare for a new window."""
    try:
        return await split_window(orientation=orientation)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_flatten_workspace(
    workspace: Annotated[str | None, "Workspace to flatten (defaults to current)"] = None,
) -> dict[str, Any]:
    """Flatten the workspace tree, removing nested containers."""
    try:
        return await flatten_workspace(workspace=workspace)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_balance_sizes() -> dict[str, Any]:
    """Balance window sizes in the current workspace."""
    try:
        return await balance_sizes()
    except Exception as e:
        return handle_error(e)


# =============================================================================
# Capture Tools
# =============================================================================


@mcp.tool()
async def tool_capture_window(
    window_id: Annotated[int | None, "Specific window ID to capture (defaults to focused)"] = None,
    output_path: Annotated[str | None, "Path to save the screenshot (defaults to temp)"] = None,
    format: Annotated[str, "Image format: png, jpg, pdf"] = "png",  # noqa: A002
) -> dict[str, Any]:
    """Capture a screenshot of the currently focused window."""
    try:
        return await capture_window(window_id=window_id, output_path=output_path, format=format)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_capture_workspace(
    workspace: Annotated[str | None, "Workspace name to capture (defaults to focused)"] = None,
    output_path: Annotated[str | None, "Path to save the screenshot (defaults to temp)"] = None,
    format: Annotated[str, "Image format: png, jpg, pdf"] = "png",  # noqa: A002
) -> dict[str, Any]:
    """Capture a screenshot of the currently focused workspace (and monitor)."""
    try:
        return await capture_workspace(workspace=workspace, output_path=output_path, format=format)
    except Exception as e:
        return handle_error(e)


# =============================================================================
# Display Information Tools
# =============================================================================


@mcp.tool()
async def tool_get_display_info() -> dict[str, Any]:
    """Get detailed information about all connected displays.

    Returns resolution, scale factor, size, position, and PPI for each display.
    """
    try:
        return await get_display_info()
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_get_display_category() -> dict[str, Any]:
    """Get simplified display configuration category with recommended strategy.

    Categories: small_single, medium_single, large_single, dual_display, triple_plus.
    """
    try:
        return await get_display_category()
    except Exception as e:
        return handle_error(e)


# =============================================================================
# Smart Focus Tools
# =============================================================================


@mcp.tool()
async def tool_apply_focus_preset(
    preset: Annotated[
        str,
        "Preset name: auto, small_single_focus, medium_split, large_centered, dual_monitor_focus, triple_monitor_focus, or saved preset name",
    ] = "auto",
    focus_window_id: Annotated[
        int | None, "Window to focus (defaults to currently focused)"
    ] = None,
    reference_apps: Annotated[list[str] | None, "Apps to keep visible as reference"] = None,
    hide_communication: Annotated[bool, "Move communication apps to separate workspace"] = False,
) -> dict[str, Any]:
    """Apply a predefined or saved focus layout based on display category."""
    try:
        return await apply_focus_preset(
            preset=preset,
            focus_window_id=focus_window_id,
            reference_apps=reference_apps,
            hide_communication=hide_communication,
        )
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_save_focus_preset(
    name: Annotated[str, "Name for the preset"],
    description: Annotated[str | None, "Human-readable description"] = None,
) -> dict[str, Any]:
    """Save the current window arrangement as a named focus preset."""
    try:
        return await save_focus_preset(name=name, description=description)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_load_focus_preset(
    name: Annotated[str, "Name of the preset to load"],
    adapt_to_displays: Annotated[bool, "Adapt preset if display config changed"] = True,
) -> dict[str, Any]:
    """Load and apply a previously saved focus preset."""
    try:
        return await load_focus_preset(name=name, adapt_to_displays=adapt_to_displays)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_resize_window_optimal(
    window_id: Annotated[int | None, "Window to resize (defaults to focused)"] = None,
    content_type: Annotated[
        str, "Content type: code_editor, browser, terminal, document, communication"
    ] = "code_editor",
    max_width_percent: Annotated[int, "Maximum width as percentage of screen"] = 80,
    min_width_percent: Annotated[int, "Minimum width as percentage of screen"] = 40,
) -> dict[str, Any]:
    """Resize a window to optimal dimensions based on its content type."""
    try:
        return await resize_window_optimal(
            window_id=window_id,
            content_type=content_type,
            max_width_percent=max_width_percent,
            min_width_percent=min_width_percent,
        )
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_set_window_zone(
    window_id: Annotated[int | None, "Window to position (defaults to focused)"] = None,
    zone: Annotated[
        str,
        "Zone name: center_focus, left_reference, right_reference, top_reference, bottom_reference, floating_pip",
    ] = "center_focus",
    monitor: Annotated[str, "Monitor: primary, secondary, or monitor ID"] = "primary",
) -> dict[str, Any]:
    """Position a window in a named zone rather than explicit coordinates."""
    try:
        return await set_window_zone(window_id=window_id, zone=zone, monitor=monitor)
    except Exception as e:
        return handle_error(e)


@mcp.tool()
async def tool_move_app_category_to_monitor(
    category: Annotated[str, "App category: communication, development, reference, media"],
    monitor: Annotated[str, "Target monitor: primary, secondary, tertiary, or monitor ID"],
    layout: Annotated[str, "Layout for moved windows: tiled, accordion, stacked"] = "tiled",
) -> dict[str, Any]:
    """Move all windows belonging to an application category to a specific monitor."""
    try:
        return await move_app_category_to_monitor(category=category, monitor=monitor, layout=layout)
    except Exception as e:
        return handle_error(e)


# =============================================================================
# Resources
# =============================================================================


@mcp.resource("aerospace://windows")
async def resource_windows() -> str:
    """List of all windows with metadata."""
    import json

    result = await get_windows_resource()
    return json.dumps(result, indent=2)


@mcp.resource("aerospace://windows/{window_id}")
async def resource_window(window_id: int) -> str:
    """Details for a specific window."""
    import json

    try:
        result = await get_window_resource(window_id)
        return json.dumps(result, indent=2)
    except AeroSpaceError as e:
        return json.dumps(e.to_dict(), indent=2)


@mcp.resource("aerospace://workspaces")
async def resource_workspaces() -> str:
    """List of all workspaces."""
    import json

    result = await get_workspaces_resource()
    return json.dumps(result, indent=2)


@mcp.resource("aerospace://workspaces/{workspace_name}")
async def resource_workspace(workspace_name: str) -> str:
    """Details for a specific workspace."""
    import json

    try:
        result = await get_workspace_resource(workspace_name)
        return json.dumps(result, indent=2)
    except AeroSpaceError as e:
        return json.dumps(e.to_dict(), indent=2)


@mcp.resource("aerospace://monitors")
async def resource_monitors() -> str:
    """List of all monitors."""
    import json

    result = await get_monitors_resource()
    return json.dumps(result, indent=2)


@mcp.resource("aerospace://tree")
async def resource_tree() -> str:
    """Current window tree structure."""
    import json

    result = await get_tree_resource()
    return json.dumps(result, indent=2)


@mcp.resource("aerospace://focused")
async def resource_focused() -> str:
    """Currently focused window, workspace, and monitor info."""
    import json

    result = await get_focused_resource()
    return json.dumps(result, indent=2)


@mcp.resource("aerospace://displays")
async def resource_displays() -> str:
    """Complete display configuration."""
    import json

    result = await get_displays_resource()
    return json.dumps(result, indent=2)


@mcp.resource("aerospace://displays/{display_id}")
async def resource_display(display_id: int) -> str:
    """Individual display details."""
    import json

    try:
        result = await get_display_resource(display_id)
        return json.dumps(result, indent=2)
    except AeroSpaceError as e:
        return json.dumps(e.to_dict(), indent=2)


# =============================================================================
# Prompts
# =============================================================================


@mcp.prompt()
def prompt_organize_windows(strategy: str | None = None) -> str:
    """Help me organize my current windows efficiently based on the apps I have open."""
    template: str = str(PROMPTS["organize_windows"]["template"])
    if strategy:
        template = f"Strategy requested: {strategy}\n\n{template}"
    return template


@mcp.prompt()
def prompt_smart_focus(
    strategy: str | None = None,
    keep_visible: str | None = None,
    reference_monitor: str | None = None,
    save_as: str | None = None,
    undo: bool = False,
) -> str:
    """Display-aware focus mode that adapts window arrangement based on display configuration."""
    template: str = str(PROMPTS["smart_focus"]["template"])

    args: list[str] = []
    if strategy:
        args.append(f"Strategy: {strategy}")
    if keep_visible:
        args.append(f"Keep visible: {keep_visible}")
    if reference_monitor:
        args.append(f"Reference monitor: {reference_monitor}")
    if save_as:
        args.append(f"Save as: {save_as}")
    if undo:
        args.append("Undo: yes")

    if args:
        template = "Arguments:\n" + "\n".join(f"- {a}" for a in args) + "\n\n" + template

    return template


@mcp.prompt()
def prompt_presentation_layout(
    presenter_app: str | None = None,
    notes_app: str | None = None,
) -> str:
    """Arrange my windows for a presentation or screen sharing session."""
    template: str = str(PROMPTS["presentation_layout"]["template"])

    args: list[str] = []
    if presenter_app:
        args.append(f"Presenter app: {presenter_app}")
    if notes_app:
        args.append(f"Notes app: {notes_app}")

    if args:
        template = "Arguments:\n" + "\n".join(f"- {a}" for a in args) + "\n\n" + template

    return template


@mcp.prompt()
def prompt_debug_app_gui(
    app_name: str | None = None,
    baseline: str | None = None,
) -> str:
    """Debug the GUI of an app under development."""
    template: str = str(PROMPTS["debug_app_gui"]["template"])

    args: list[str] = []
    if app_name:
        args.append(f"App name: {app_name}")
    if baseline:
        args.append(f"Baseline image: {baseline}")

    if args:
        template = "Arguments:\n" + "\n".join(f"- {a}" for a in args) + "\n\n" + template

    return template
