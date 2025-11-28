"""Smart focus tools for AeroSpace.

This module provides MCP tools for intelligent window arrangement
based on display configuration.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from win_ctrl_mcp.aerospace import (
    ERROR_NO_WINDOW_FOCUSED,
    ERROR_WINDOW_NOT_FOUND,
    AeroSpaceError,
    get_focused_window,
    get_window_by_id,
    list_monitors,
    list_windows,
    run_aerospace_command,
)
from win_ctrl_mcp.tools.display import get_display_category, get_display_info

# Preset storage directory
PRESET_DIR = Path.home() / ".config" / "win-ctrl-mcp" / "presets"

# App categories for organization
APP_CATEGORIES: dict[str, list[str]] = {
    "communication": [
        "Slack",
        "Discord",
        "Mail",
        "Messages",
        "Microsoft Teams",
        "Zoom",
        "Telegram",
        "WhatsApp",
        "Signal",
    ],
    "development": [
        "Visual Studio Code",
        "Code",
        "Xcode",
        "Terminal",
        "iTerm",
        "iTerm2",
        "IntelliJ IDEA",
        "PyCharm",
        "WebStorm",
        "Android Studio",
        "Sublime Text",
        "Atom",
        "Vim",
        "Neovim",
        "Emacs",
    ],
    "reference": [
        "Google Chrome",
        "Chrome",
        "Safari",
        "Firefox",
        "Arc",
        "Notes",
        "Notion",
        "Obsidian",
        "Evernote",
        "Bear",
        "Preview",
        "Finder",
    ],
    "media": [
        "Spotify",
        "Music",
        "Apple Music",
        "YouTube",
        "VLC",
        "Photos",
        "QuickTime Player",
        "IINA",
    ],
}

# Optimal dimensions by content type (in characters or pixels)
OPTIMAL_DIMENSIONS: dict[str, dict[str, Any]] = {
    "code_editor": {
        "min_chars": 80,
        "optimal_chars": 120,
        "max_chars": 140,
        "char_width_px": 10,  # Approximate character width
    },
    "browser": {
        "min_width_px": 1024,
        "optimal_width_px": 1280,
        "max_width_px": 1400,
    },
    "terminal": {
        "min_chars": 80,
        "optimal_chars": 100,
        "max_chars": 120,
        "char_width_px": 9,
    },
    "document": {
        "min_chars": 50,
        "optimal_chars": 70,
        "max_chars": 80,
        "char_width_px": 10,
    },
    "communication": {
        "min_width_px": 350,
        "optimal_width_px": 450,
        "max_width_px": 600,
    },
}


def _get_app_category(app_name: str) -> str | None:
    """Get the category for an app.

    Args:
        app_name: Application name

    Returns:
        Category name or None if not categorized
    """
    for category, apps in APP_CATEGORIES.items():
        if app_name in apps or any(app.lower() in app_name.lower() for app in apps):
            return category
    return None


async def apply_focus_preset(
    preset: str = "auto",
    focus_window_id: int | None = None,
    reference_apps: list[str] | None = None,
    hide_communication: bool = False,
) -> dict[str, Any]:
    """Apply a predefined or saved focus layout based on display category.

    Args:
        preset: Preset name - auto, small_single_focus, medium_split,
                large_centered, dual_monitor_focus, triple_monitor_focus,
                or a saved preset name
        focus_window_id: Window to focus (defaults to currently focused)
        reference_apps: Apps to keep visible as reference
        hide_communication: Move communication apps to separate workspace

    Returns:
        Result dictionary with applied layout info
    """
    # Get display category for auto mode
    display_cat = await get_display_category()
    category = display_cat.get("category", "medium_single")

    # Determine which preset to use
    if preset == "auto":
        preset_map = {
            "small_single": "small_single_focus",
            "medium_single": "medium_split",
            "large_single": "large_centered",
            "dual_display": "dual_monitor_focus",
            "triple_plus": "triple_monitor_focus",
        }
        preset = preset_map.get(category, "medium_split")

    # Check if it's a saved preset
    saved_preset_path = PRESET_DIR / f"{preset}.json"
    if saved_preset_path.exists():
        return await load_focus_preset(name=preset)

    # Get the focus window
    if focus_window_id is not None:
        focus_win = await get_window_by_id(focus_window_id)
        if focus_win is None:
            available = await list_windows(all_windows=True)
            available_ids = [w.get("window-id") for w in available]
            raise AeroSpaceError(
                ERROR_WINDOW_NOT_FOUND,
                f"Window with ID {focus_window_id} not found",
                {"requested_window_id": focus_window_id, "available_windows": available_ids},
            )
    else:
        focus_win = await get_focused_window()
        if focus_win is None:
            raise AeroSpaceError(
                ERROR_NO_WINDOW_FOCUSED,
                "No window is currently focused",
                {"suggestion": "Focus a window first"},
            )
        focus_window_id = focus_win.get("window-id")

    # Get all windows
    all_windows = await list_windows(all_windows=True)
    monitors = await list_monitors()

    # Categorize windows
    reference_windows = []
    hidden_windows = []

    reference_apps = reference_apps or []

    for window in all_windows:
        if window.get("window-id") == focus_window_id:
            continue

        app_name = window.get("app-name", "")
        app_category = _get_app_category(app_name)

        # Check if this should be a reference window
        if app_name in reference_apps or app_category == "reference":
            reference_windows.append(window)
        elif hide_communication and app_category == "communication":
            hidden_windows.append(window)

    # Apply the preset layout
    layout_result: dict[str, Any] = {
        "focus_window": {
            "window_id": focus_window_id,
            "monitor": 1,
            "arrangement": "normal",
        },
        "reference_windows": [],
        "hidden_windows": [],
    }

    # Focus the main window
    await run_aerospace_command("focus", "--window-id", str(focus_window_id))

    # Apply layout based on preset
    if preset == "small_single_focus":
        # Make focus window fullscreen
        await run_aerospace_command("fullscreen")
        layout_result["focus_window"]["arrangement"] = "fullscreen"

    elif preset == "medium_split":
        # 70/30 split - focus window larger
        await run_aerospace_command("layout", "h_tiles")
        await run_aerospace_command("resize", "width", "+30%")
        layout_result["focus_window"]["arrangement"] = "tiled_70"

    elif preset == "large_centered":
        # Center focus window, reference on sides
        await run_aerospace_command("layout", "h_tiles")
        layout_result["focus_window"]["arrangement"] = "centered"

    elif preset == "dual_monitor_focus":
        # Fullscreen on primary, reference on secondary
        if len(monitors) >= 2:
            await run_aerospace_command("fullscreen")
            layout_result["focus_window"]["arrangement"] = "fullscreen"
            layout_result["focus_window"]["monitor"] = 1

            # Move reference windows to secondary monitor
            for ref_win in reference_windows:
                try:
                    await run_aerospace_command(
                        "focus",
                        "--window-id",
                        str(ref_win.get("window-id")),
                    )
                    await run_aerospace_command("move-node-to-monitor", "next")
                    layout_result["reference_windows"].append(
                        {
                            "window_id": ref_win.get("window-id"),
                            "monitor": 2,
                            "arrangement": "tiled",
                        }
                    )
                except AeroSpaceError:
                    pass  # Window might have closed

    elif preset == "triple_monitor_focus":
        # Primary for focus, secondary for reference, tertiary for communication
        if len(monitors) >= 3:
            await run_aerospace_command("fullscreen")
            layout_result["focus_window"]["arrangement"] = "fullscreen"
            layout_result["focus_window"]["monitor"] = 1

    # Hide communication windows if requested
    if hide_communication:
        for hidden_win in hidden_windows:
            try:
                await run_aerospace_command(
                    "focus",
                    "--window-id",
                    str(hidden_win.get("window-id")),
                )
                await run_aerospace_command("move-node-to-workspace", "communication")
                layout_result["hidden_windows"].append(
                    {
                        "window_id": hidden_win.get("window-id"),
                        "moved_to_workspace": "communication",
                    }
                )
            except AeroSpaceError:
                pass

    # Refocus the main window
    await run_aerospace_command("focus", "--window-id", str(focus_window_id))

    return {
        "success": True,
        "preset_applied": preset,
        "display_category": category,
        "layout": layout_result,
    }


async def save_focus_preset(
    name: str,
    description: str | None = None,
) -> dict[str, Any]:
    """Save the current window arrangement as a named focus preset.

    Args:
        name: Name for the preset
        description: Human-readable description

    Returns:
        Result dictionary with saved preset info
    """
    # Get current state
    display_cat = await get_display_category()
    all_windows = await list_windows(all_windows=True)
    monitors = await list_monitors()

    # Create preset data
    windows_list: list[dict[str, Any]] = []
    preset_data: dict[str, Any] = {
        "name": name,
        "description": description or f"Focus preset: {name}",
        "display_category": display_cat.get("category"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "windows": windows_list,
        "monitors": [m.get("name") for m in monitors],
    }

    for window in all_windows:
        windows_list.append(
            {
                "app_name": window.get("app-name"),
                "workspace": window.get("workspace"),
                "is_focused": window.get("is-focused", False),
            }
        )

    # Save to file
    PRESET_DIR.mkdir(parents=True, exist_ok=True)
    preset_path = PRESET_DIR / f"{name}.json"
    with open(preset_path, "w") as f:
        json.dump(preset_data, f, indent=2)

    return {
        "success": True,
        "preset": {
            "name": name,
            "description": preset_data["description"],
            "display_category": display_cat.get("category"),
            "created_at": preset_data["created_at"],
            "window_count": len(all_windows),
        },
    }


async def load_focus_preset(
    name: str,
    adapt_to_displays: bool = True,
) -> dict[str, Any]:
    """Load and apply a previously saved focus preset.

    Args:
        name: Name of the preset to load
        adapt_to_displays: Adapt preset if display config changed (default: True)

    Returns:
        Result dictionary with loaded preset info
    """
    preset_path = PRESET_DIR / f"{name}.json"

    if not preset_path.exists():
        # List available presets
        available = []
        if PRESET_DIR.exists():
            available = [f.stem for f in PRESET_DIR.glob("*.json")]

        raise AeroSpaceError(
            "PRESET_NOT_FOUND",
            f"Preset '{name}' not found",
            {"available_presets": available},
        )

    with open(preset_path) as f:
        preset_data = json.load(f)

    # Check display compatibility
    current_category = (await get_display_category()).get("category")
    saved_category = preset_data.get("display_category")
    adapted = False

    if current_category != saved_category and not adapt_to_displays:
        raise AeroSpaceError(
            "DISPLAY_MISMATCH",
            f"Display configuration changed from '{saved_category}' to '{current_category}'",
            {"suggestion": "Set adapt_to_displays=True to adapt the preset"},
        )

    if current_category != saved_category:
        adapted = True

    # Apply the preset
    # Get current windows
    all_windows = await list_windows(all_windows=True)
    windows_arranged = 0

    for preset_window in preset_data.get("windows", []):
        app_name = preset_window.get("app_name")
        workspace = preset_window.get("workspace")

        # Find matching window
        for window in all_windows:
            if window.get("app-name") == app_name:
                try:
                    await run_aerospace_command(
                        "focus",
                        "--window-id",
                        str(window.get("window-id")),
                    )
                    if workspace:
                        await run_aerospace_command(
                            "move-node-to-workspace",
                            workspace,
                        )
                    windows_arranged += 1
                except AeroSpaceError:
                    pass
                break

    return {
        "success": True,
        "preset_loaded": name,
        "adapted": adapted,
        "windows_arranged": windows_arranged,
    }


async def resize_window_optimal(
    window_id: int | None = None,
    content_type: str = "code_editor",
    max_width_percent: int = 80,
    min_width_percent: int = 40,
) -> dict[str, Any]:
    """Resize a window to optimal dimensions based on its content type.

    Args:
        window_id: Window to resize (defaults to focused)
        content_type: Content type - code_editor, browser, terminal, document, communication
        max_width_percent: Maximum width as percentage of screen (default: 80)
        min_width_percent: Minimum width as percentage of screen (default: 40)

    Returns:
        Result dictionary with new dimensions
    """
    valid_types = {"code_editor", "browser", "terminal", "document", "communication"}
    if content_type not in valid_types:
        raise AeroSpaceError(
            "INVALID_PARAMETERS",
            f"Invalid content_type '{content_type}'",
            {"valid_options": list(valid_types)},
        )

    # Get the window
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

    # Get display info for screen size
    display_info = await get_display_info()
    displays = display_info.get("displays", [])

    # Use first display's dimensions (simplification)
    screen_width = 1920  # Default
    if displays:
        res = displays[0].get("effective_resolution") or displays[0].get("resolution", {})
        screen_width = res.get("width", 1920)

    # Calculate optimal width
    dims = OPTIMAL_DIMENSIONS.get(content_type, OPTIMAL_DIMENSIONS["code_editor"])

    if "optimal_chars" in dims:
        # Character-based sizing
        char_width = dims.get("char_width_px", 10)
        optimal_px = dims["optimal_chars"] * char_width
        # Add padding for window chrome (~50px)
        optimal_px += 50
    else:
        optimal_px = dims.get("optimal_width_px", 1200)

    # Apply constraints
    max_px = int(screen_width * max_width_percent / 100)
    min_px = int(screen_width * min_width_percent / 100)

    final_width = max(min_px, min(optimal_px, max_px))

    # Focus and resize the window
    await run_aerospace_command("focus", "--window-id", str(window_id))

    # Calculate resize amount (this is approximate since we don't know current size)
    # We'll set to a percentage-based width
    target_percent = int(final_width / screen_width * 100)

    # Resize using layout and resize commands
    await run_aerospace_command("layout", "h_tiles")
    await run_aerospace_command("resize", "width", f"{target_percent}%")

    return {
        "success": True,
        "window_id": window_id,
        "content_type": content_type,
        "new_dimensions": {
            "width": final_width,
            "height": None,  # Not calculated
            "optimal_chars_per_line": dims.get("optimal_chars"),
        },
    }


async def set_window_zone(
    window_id: int | None = None,
    zone: str = "center_focus",
    monitor: str = "primary",
) -> dict[str, Any]:
    """Position a window in a named zone rather than explicit coordinates.

    Args:
        window_id: Window to position (defaults to focused)
        zone: Zone name - center_focus, left_reference, right_reference,
              top_reference, bottom_reference, floating_pip
        monitor: Monitor - primary, secondary, or monitor ID (default: primary)

    Returns:
        Result dictionary with position info
    """
    valid_zones = {
        "center_focus",
        "left_reference",
        "right_reference",
        "top_reference",
        "bottom_reference",
        "floating_pip",
    }
    if zone not in valid_zones:
        raise AeroSpaceError(
            "INVALID_PARAMETERS",
            f"Invalid zone '{zone}'",
            {"valid_options": list(valid_zones)},
        )

    # Get the window
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

    # Focus the window
    await run_aerospace_command("focus", "--window-id", str(window_id))

    # Move to correct monitor if needed
    if monitor == "secondary":
        await run_aerospace_command("move-node-to-monitor", "next")
    elif monitor != "primary" and monitor.isdigit():
        # Move to specific monitor by index
        monitors = await list_monitors()
        if int(monitor) <= len(monitors):
            target_name = monitors[int(monitor) - 1].get("name")
            if target_name:
                await run_aerospace_command("move-node-to-monitor", target_name)

    # Apply zone layout
    # Get display info for calculations
    display_info = await get_display_info()
    displays = display_info.get("displays", [])
    screen_width = 1920
    screen_height = 1080
    if displays:
        res = displays[0].get("effective_resolution") or displays[0].get("resolution", {})
        screen_width = res.get("width", 1920)
        screen_height = res.get("height", 1080)

    bounds = {"x": 0, "y": 0, "width": screen_width, "height": screen_height}

    if zone == "center_focus":
        # 60-70% width, centered
        width = int(screen_width * 0.65)
        x = int((screen_width - width) / 2)
        bounds = {"x": x, "y": 0, "width": width, "height": screen_height}
        await run_aerospace_command("layout", "tiling")
        await run_aerospace_command("resize", "width", "65%")

    elif zone == "left_reference":
        # 25-30% width on left
        width = int(screen_width * 0.28)
        bounds = {"x": 0, "y": 0, "width": width, "height": screen_height}
        await run_aerospace_command("layout", "h_tiles")
        await run_aerospace_command("move", "left")
        await run_aerospace_command("resize", "width", "-40%")

    elif zone == "right_reference":
        # 25-30% width on right
        width = int(screen_width * 0.28)
        x = screen_width - width
        bounds = {"x": x, "y": 0, "width": width, "height": screen_height}
        await run_aerospace_command("layout", "h_tiles")
        await run_aerospace_command("move", "right")
        await run_aerospace_command("resize", "width", "-40%")

    elif zone == "top_reference":
        # Top half
        height = int(screen_height / 2)
        bounds = {"x": 0, "y": 0, "width": screen_width, "height": height}
        await run_aerospace_command("layout", "v_tiles")
        await run_aerospace_command("move", "up")

    elif zone == "bottom_reference":
        # Bottom half
        height = int(screen_height / 2)
        bounds = {"x": 0, "y": height, "width": screen_width, "height": height}
        await run_aerospace_command("layout", "v_tiles")
        await run_aerospace_command("move", "down")

    elif zone == "floating_pip":
        # Small floating window in corner (picture-in-picture style)
        width = int(screen_width * 0.25)
        height = int(screen_height * 0.25)
        x = screen_width - width - 20
        y = screen_height - height - 20
        bounds = {"x": x, "y": y, "width": width, "height": height}
        await run_aerospace_command("layout", "floating")

    return {
        "success": True,
        "window_id": window_id,
        "zone": zone,
        "monitor": monitor,
        "bounds": bounds,
    }


async def move_app_category_to_monitor(
    category: str,
    monitor: str,
    layout: str = "tiled",
) -> dict[str, Any]:
    """Move all windows belonging to an application category to a specific monitor.

    Args:
        category: App category - communication, development, reference, media
        monitor: Target monitor - primary, secondary, tertiary, or monitor ID
        layout: Layout for moved windows - tiled, accordion, stacked (default: tiled)

    Returns:
        Result dictionary with moved windows info
    """
    if category not in APP_CATEGORIES:
        raise AeroSpaceError(
            "INVALID_PARAMETERS",
            f"Invalid category '{category}'",
            {"valid_options": list(APP_CATEGORIES.keys())},
        )

    valid_layouts = {"tiled", "accordion", "stacked"}
    if layout not in valid_layouts:
        raise AeroSpaceError(
            "INVALID_PARAMETERS",
            f"Invalid layout '{layout}'",
            {"valid_options": list(valid_layouts)},
        )

    # Get monitors
    monitors = await list_monitors()
    if not monitors:
        raise AeroSpaceError(
            "NO_MONITORS",
            "No monitors found",
            {},
        )

    # Determine target monitor name
    target_monitor = None
    if monitor == "primary":
        # Primary is first monitor or the one marked as main
        target_monitor = monitors[0].get("name")
    elif monitor == "secondary" and len(monitors) >= 2:
        target_monitor = monitors[1].get("name")
    elif monitor == "tertiary" and len(monitors) >= 3:
        target_monitor = monitors[2].get("name")
    elif monitor.isdigit():
        idx = int(monitor) - 1
        if 0 <= idx < len(monitors):
            target_monitor = monitors[idx].get("name")

    if not target_monitor:
        raise AeroSpaceError(
            "MONITOR_NOT_FOUND",
            f"Monitor '{monitor}' not found",
            {"available_monitors": [m.get("name") for m in monitors]},
        )

    # Get all windows
    all_windows = await list_windows(all_windows=True)

    # Find windows in the category
    category_apps = APP_CATEGORIES[category]
    windows_moved = []

    for window in all_windows:
        app_name = window.get("app-name", "")
        if app_name in category_apps or any(
            cat_app.lower() in app_name.lower() for cat_app in category_apps
        ):
            try:
                await run_aerospace_command(
                    "focus",
                    "--window-id",
                    str(window.get("window-id")),
                )
                await run_aerospace_command("move-node-to-monitor", target_monitor)
                windows_moved.append(
                    {
                        "window_id": window.get("window-id"),
                        "app_name": app_name,
                    }
                )
            except AeroSpaceError:
                pass  # Window might have closed

    # Apply layout to moved windows
    if windows_moved:
        layout_map = {
            "tiled": "h_tiles",
            "accordion": "h_accordion",
            "stacked": "v_accordion",
        }
        aerospace_layout = layout_map.get(layout, "h_tiles")

        # Focus first moved window and apply layout
        try:
            await run_aerospace_command(
                "focus",
                "--window-id",
                str(windows_moved[0]["window_id"]),
            )
            await run_aerospace_command("layout", aerospace_layout)
        except AeroSpaceError:
            pass

    return {
        "success": True,
        "category": category,
        "monitor": monitor,
        "windows_moved": windows_moved,
        "layout_applied": layout,
    }
