# Reference Material

- MCP Server for windows capture with Yabai Window Manager: https://github.com/huegli/capture-win-mcp
- Command Reference for Aerospace: https://nikitabobko.github.io/AeroSpace/commands

# Requirements

- Python > 3.10
- FastMCP SDK
- uv package manager
- Use the MacOSX 'screencapture' CLI utility for screenshoots

---

# Tools to implement

## Window Management Tools
- `focus_window` - Focus a window by direction (left, right, up, down) or by window ID
- `focus_monitor` - Focus a specific monitor by name or direction
- `focus_workspace` - Switch to a specific workspace by name or number
- `move_window` - Move the focused window to a different workspace, monitor or position
- `resize_window` - Resize the focused window (smart, width, height adjustments)
- `close_window` - Close the focused window or a specific window by ID
- `fullscreen_toggle` - Toggle fullscreen mode for the focused window. NOTE: do not use macosx-native-fullscreen
- `minimize_window` - Minimize a window

## Layout Management Tools
- `set_layout` - Change the layout mode (tiles, accordion, horizontal, vertical, floating)
- `split_window` - Split the current container horizontally or vertically
- `flatten_workspace` - Flatten the workspace tree structure
- `balance_sizes` - Balance window sizes in the current workspace

## Capture Tools
- `capture_window` - Capture the content of the window that currently has the focus as a screenshot
- `capture_workspace` - capture the content of the currently focussed workspace (and monitor, if more than one) as a screenshot

---

# Resources to implement

## Dynamic Resources (with URI templates)
- `aerospace://windows` - List of all windows with metadata
- `aerospace://windows/{window_id}` - Details for a specific window
- `aerospace://workspaces` - List of all workspaces
- `aerospace://workspaces/{workspace_name}` - Details for a specific workspace
- `aerospace://monitors` - List of all monitors
- `aerospace://tree` - Current window tree structure
- `aerospace://focused` - Currently focused window/workspace info

---

#  Prompts to implement

## Window Organization Prompts
- `organize_windows` - "Help me organize my current windows efficiently based on the apps I have open"
- `focus_mode` - "Rearrange the windows in the current workspace so that the window that currently has the focus is most prominent but other windows remain visible / accessible, making use of the capture tool functionality"
- `presentation_layout` - "Arrange my windows for a presentation or screen sharing session"

## Development  Prompts
- `debug_app_gui` - "Debug the GUI of an app under development by comparing what is expected vs what is actually on screen, using the capture tool functionality"

# Prompts to consider for the future (DO NOT IMPLEMENT)
## Workspace Setup Prompts
- `development_setup` - "Create a development-focused workspace layout with terminal, editor, and browser"
- `communication_setup` - "Organize communication apps (Slack, email, calendar) into a dedicated workspace"
- `cleanup_workspaces` - "Analyze my current workspaces and suggest consolidation or reorganization"


---

# Advanced MCP Server Features to consider (DO NOT IMPLEMENT)

## Event Subscriptions (SSE)
- Subscribe to window focus changes
- Subscribe to workspace switches
- Subscribe to window open/close events
- Subscribe to layout changes
- Enables real-time dashboard or logging capabilities

## Batch Operations
- Execute multiple aerospace commands atomically
- Support for transaction-like behavior (rollback on failure)
- Bulk window operations (e.g., move all windows matching a pattern)

## State Management
- Save/restore workspace layouts as named snapshots
- Export/import window arrangements
- Undo/redo support for recent operations

## Context-Aware Features
- App-specific layout recommendations based on detected applications
- Time-based workspace suggestions (e.g., morning routine, end-of-day cleanup)
- Smart window grouping based on usage patterns

## Integration Capabilities
- Integration with macOS Shortcuts for automation
- Webhook support for external triggers
- Optional persistence layer for layout presets

## Safety Features
- Confirmation prompts for destructive operations (close all windows)
- Dry-run mode for testing commands
- Operation logging with timestamps

## Performance Optimizations
- Caching of window/workspace state with configurable TTL
- Debounced refresh for rapid state queries
- Lazy loading of window details
