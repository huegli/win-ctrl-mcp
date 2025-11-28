"""Display information tools for AeroSpace.

This module provides MCP tools for querying display configuration.
Uses system_profiler and AeroSpace monitor info.
"""

import asyncio
import json
import re
from typing import Any

from win_ctrl_mcp.aerospace import list_monitors, list_workspaces


async def _get_system_display_info() -> list[dict[str, Any]]:
    """Get display information from system_profiler.

    Returns:
        List of display information dictionaries
    """
    proc = await asyncio.create_subprocess_exec(
        "system_profiler",
        "SPDisplaysDataType",
        "-json",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()

    if proc.returncode != 0:
        return []

    try:
        data = json.loads(stdout.decode("utf-8"))
        displays = []

        # Navigate the system_profiler JSON structure
        for item in data.get("SPDisplaysDataType", []):
            for display in item.get("spdisplays_ndrvs", []):
                display_info = {
                    "name": display.get("_name", "Unknown"),
                    "resolution_str": display.get("_spdisplays_resolution", ""),
                    "is_builtin": display.get("spdisplays_builtin") == "spdisplays_yes",
                    "is_main": display.get("spdisplays_main") == "spdisplays_yes",
                }

                # Parse resolution string like "2560 x 1600 @ 60 Hz"
                res_match = re.match(
                    r"(\d+)\s*x\s*(\d+)",
                    display_info["resolution_str"],
                )
                if res_match:
                    display_info["resolution"] = {
                        "width": int(res_match.group(1)),
                        "height": int(res_match.group(2)),
                    }
                else:
                    display_info["resolution"] = {"width": 0, "height": 0}

                # Get pixels info for scale factor calculation
                pixels = display.get("_spdisplays_pixels", "")
                pixels_match = re.match(r"(\d+)\s*x\s*(\d+)", pixels)
                if pixels_match:
                    display_info["native_resolution"] = {
                        "width": int(pixels_match.group(1)),
                        "height": int(pixels_match.group(2)),
                    }

                displays.append(display_info)

        return displays

    except (json.JSONDecodeError, KeyError):
        return []


def _calculate_display_category(
    displays: list[dict[str, Any]],
) -> tuple[str, str]:
    """Calculate display configuration category.

    Args:
        displays: List of display info dictionaries

    Returns:
        Tuple of (category, description)
    """
    num_displays = len(displays)

    if num_displays == 0:
        return "unknown", "No displays detected"

    if num_displays >= 3:
        return (
            "triple_plus",
            "Three or more monitors: focus=primary, reference=secondary, communication=tertiary",
        )

    if num_displays == 2:
        return "dual_display", "Two monitors: focus on primary, reference on secondary"

    # Single display - categorize by size
    display = displays[0]
    resolution = display.get("effective_resolution") or display.get("resolution", {})
    width = resolution.get("width", 0)
    height = resolution.get("height", 0)
    total_pixels = width * height

    # Calculate diagonal in inches if we have size info
    size_inches = display.get("size_inches", 0)

    # Heuristics for display size category
    if size_inches > 0:
        if size_inches >= 27:
            return (
                "large_single",
                'Large single display (27"+): centered focus with flanking reference',
            )
        elif size_inches >= 15:
            return "medium_single", 'Medium single display (15-24"): 70/30 split with sidebar'
        else:
            return (
                "small_single",
                'Small single display (<15"): fullscreen focus, workspaces for others',
            )
    else:
        # Fallback to resolution-based detection
        if total_pixels >= 3686400:  # >= 2560x1440
            return "large_single", "Large single display: centered focus with flanking reference"
        elif total_pixels >= 1036800:  # >= 1280x810
            return "medium_single", "Medium single display: 70/30 split with sidebar"
        else:
            return "small_single", "Small single display: fullscreen focus, workspaces for others"


def _get_size_category(resolution: dict[str, int]) -> str:
    """Get size category based on resolution.

    Args:
        resolution: Resolution dictionary with width and height

    Returns:
        Size category: small, medium, or large
    """
    width = resolution.get("width", 0)
    height = resolution.get("height", 0)
    total_pixels = width * height

    if total_pixels >= 3686400:  # >= 2560x1440
        return "large"
    elif total_pixels >= 1036800:  # >= 1280x810
        return "medium"
    else:
        return "small"


async def get_display_info() -> dict[str, Any]:
    """Get detailed information about all connected displays.

    Returns:
        Dictionary with display information
    """
    # Get AeroSpace monitor info
    monitors = await list_monitors()

    # Get system display info
    system_displays = await _get_system_display_info()

    # Merge the information
    displays = []
    for i, monitor in enumerate(monitors):
        display = {
            "id": i + 1,
            "name": monitor.get("name", f"Display {i + 1}"),
        }

        # Try to match with system display info
        system_display = None
        for sd in system_displays:
            if sd.get("name") in display["name"] or display["name"] in sd.get("name", ""):
                system_display = sd
                break
            # Also check for built-in matching
            if sd.get("is_builtin") and "built-in" in display["name"].lower():
                system_display = sd
                break

        if system_display:
            display["resolution"] = system_display.get("resolution", {"width": 0, "height": 0})
            display["is_builtin"] = system_display.get("is_builtin", False)
            display["is_primary"] = system_display.get("is_main", i == 0)

            # Calculate scale factor
            native = system_display.get("native_resolution")
            effective = system_display.get("resolution")
            if native and effective and effective.get("width"):
                scale = native.get("width", 0) / effective.get("width", 1)
                display["scale_factor"] = round(scale, 1)
                display["effective_resolution"] = effective
            else:
                display["scale_factor"] = 1.0
                display["effective_resolution"] = display["resolution"]

            # Estimate size in inches (rough calculation)
            # Assume 110 PPI for external, 220 for retina laptop
            ppi = 220 if display.get("is_builtin") else 110
            if display["scale_factor"] > 1:
                ppi = 220  # Retina display
            width_px = display["resolution"].get("width", 0)
            if ppi > 0 and width_px > 0:
                width_inches = width_px / ppi
                # Assume 16:10 aspect ratio for height estimate
                height_inches = width_inches * 0.625
                diagonal = (width_inches**2 + height_inches**2) ** 0.5
                display["size_inches"] = round(diagonal, 1)
                display["ppi"] = ppi
            else:
                display["size_inches"] = 0
                display["ppi"] = 0
        else:
            # Defaults when we can't get system info
            display["resolution"] = {"width": 0, "height": 0}
            display["scale_factor"] = 1.0
            display["effective_resolution"] = {"width": 0, "height": 0}
            display["size_inches"] = 0
            display["is_primary"] = i == 0
            display["is_builtin"] = False
            display["ppi"] = 0

        # Position (not available from aerospace, would need AppKit)
        display["position"] = {"x": 0, "y": 0}

        displays.append(display)

    # Calculate arrangement
    if len(displays) == 1:
        arrangement = "single"
    elif len(displays) == 2:
        arrangement = "horizontal"  # Most common
    else:
        arrangement = "multiple"

    # Calculate total effective pixels
    total_pixels = sum(
        d.get("effective_resolution", {}).get("width", 0)
        * d.get("effective_resolution", {}).get("height", 0)
        for d in displays
    )

    # Get category
    category, _ = _calculate_display_category(displays)

    return {
        "displays": displays,
        "arrangement": arrangement,
        "total_effective_pixels": total_pixels,
        "category": category,
    }


async def get_display_category() -> dict[str, Any]:
    """Get simplified display configuration category with recommended strategy.

    Returns:
        Dictionary with category and strategy info
    """
    display_info = await get_display_info()
    displays = display_info.get("displays", [])

    category, description = _calculate_display_category(displays)

    # Determine primary and secondary sizes
    primary_size = "medium"
    secondary_sizes = []

    if displays:
        primary_display = next((d for d in displays if d.get("is_primary")), displays[0])
        primary_size = _get_size_category(
            primary_display.get("effective_resolution") or primary_display.get("resolution", {})
        )

        for d in displays:
            if not d.get("is_primary"):
                size = _get_size_category(d.get("effective_resolution") or d.get("resolution", {}))
                secondary_sizes.append(size)

    # Recommended strategy based on category
    strategies = {
        "small_single": "fullscreen_focus",
        "medium_single": "split_sidebar",
        "large_single": "centered_focus",
        "dual_display": "primary_focus_secondary_reference",
        "triple_plus": "dedicated_monitors",
    }

    return {
        "category": category,
        "primary_size": primary_size,
        "secondary_sizes": secondary_sizes,
        "recommended_strategy": strategies.get(category, "fullscreen_focus"),
        "description": description,
    }


async def get_display_by_id(display_id: int) -> dict[str, Any] | None:
    """Get individual display details by ID.

    Args:
        display_id: The display ID

    Returns:
        Display dictionary or None if not found
    """
    display_info = await get_display_info()
    displays: list[dict[str, Any]] = display_info.get("displays", [])

    for display in displays:
        if display.get("id") == display_id:
            # Add workspace information
            workspaces = await list_workspaces(all_workspaces=True)
            display_workspaces = [
                w.get("workspace") for w in workspaces if w.get("monitor") == display.get("name")
            ]

            # Find focused workspace on this display
            focused_workspaces = await list_workspaces(focused=True)
            focused_ws = None
            for fw in focused_workspaces:
                if fw.get("monitor") == display.get("name"):
                    focused_ws = fw.get("workspace")
                    break

            display["workspaces"] = display_workspaces
            display["focused_workspace"] = focused_ws
            display["size_category"] = _get_size_category(
                display.get("effective_resolution") or display.get("resolution", {})
            )

            # Count windows on this display
            from win_ctrl_mcp.aerospace import list_windows

            windows = await list_windows(monitor=display.get("name"))
            display["window_count"] = len(windows)

            return display

    return None
