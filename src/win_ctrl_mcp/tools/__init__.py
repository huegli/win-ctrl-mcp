"""AeroSpace MCP tools."""

from win_ctrl_mcp.tools.capture import (
    capture_window,
    capture_workspace,
)
from win_ctrl_mcp.tools.display import (
    get_display_category,
    get_display_info,
)
from win_ctrl_mcp.tools.focus import (
    apply_focus_preset,
    load_focus_preset,
    move_app_category_to_monitor,
    resize_window_optimal,
    save_focus_preset,
    set_window_zone,
)
from win_ctrl_mcp.tools.layout import (
    balance_sizes,
    flatten_workspace,
    set_layout,
    split_window,
)
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

__all__ = [
    # Window management
    "focus_window",
    "focus_monitor",
    "focus_workspace",
    "move_window",
    "resize_window",
    "close_window",
    "fullscreen_toggle",
    "minimize_window",
    # Layout management
    "set_layout",
    "split_window",
    "flatten_workspace",
    "balance_sizes",
    # Capture
    "capture_window",
    "capture_workspace",
    # Display info
    "get_display_info",
    "get_display_category",
    # Smart focus
    "apply_focus_preset",
    "save_focus_preset",
    "load_focus_preset",
    "resize_window_optimal",
    "set_window_zone",
    "move_app_category_to_monitor",
]
