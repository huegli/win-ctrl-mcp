# Reference Material

- MCP Server for windows capture with Yabai Window Manager: https://github.com/huegli/capture-win-mcp
- Command Reference for Aerospace: https://nikitabobko.github.io/AeroSpace/commands

# Requirements

- Python > 3.10
- FastMCP SDK
- uv package manager

---

# Suggested Tools

## Window Management Tools
- `focus_window` - Focus a window by direction (left, right, up, down) or by window ID
- `move_window` - Move the focused window to a different workspace or position
- `resize_window` - Resize the focused window (smart, width, height adjustments)
- `close_window` - Close the focused window or a specific window by ID
- `fullscreen_toggle` - Toggle fullscreen mode for the focused window
- `minimize_window` - Minimize a window
- `list_windows` - List all windows with their properties (app name, title, workspace, position)

## Workspace Management Tools
- `switch_workspace` - Switch to a specific workspace by name or number
- `list_workspaces` - List all workspaces and their window counts
- `move_window_to_workspace` - Move the focused window to a specified workspace
- `create_workspace` - Create a new named workspace
- `rename_workspace` - Rename an existing workspace

## Layout Management Tools
- `set_layout` - Change the layout mode (tiles, accordion, horizontal, vertical, floating)
- `split_window` - Split the current container horizontally or vertically
- `flatten_workspace` - Flatten the workspace tree structure
- `balance_sizes` - Balance window sizes in the current workspace

## Monitor/Display Tools
- `list_monitors` - List all connected monitors and their properties
- `focus_monitor` - Focus a specific monitor by name or direction
- `move_workspace_to_monitor` - Move a workspace to a different monitor

## Query Tools
- `get_focused_window` - Get details about the currently focused window
- `get_workspace_info` - Get detailed info about a specific workspace
- `get_tree` - Get the full window tree structure (useful for debugging/visualization)

## Utility Tools
- `reload_config` - Reload the AeroSpace configuration file
- `execute_aerospace_command` - Execute a raw aerospace command (escape hatch)

---

# Suggested Resources

## Static Resources
- `aerospace://config` - Current AeroSpace configuration
- `aerospace://version` - AeroSpace version information

## Dynamic Resources (with URI templates)
- `aerospace://windows` - List of all windows with metadata
- `aerospace://windows/{window_id}` - Details for a specific window
- `aerospace://workspaces` - List of all workspaces
- `aerospace://workspaces/{workspace_name}` - Details for a specific workspace
- `aerospace://monitors` - List of all monitors
- `aerospace://tree` - Current window tree structure
- `aerospace://focused` - Currently focused window/workspace info

---

# Suggested Prompts

## Window Organization Prompts
- `organize_windows` - "Help me organize my current windows efficiently based on the apps I have open"
- `focus_mode` - "Set up a focus mode by moving distracting apps to a separate workspace"
- `presentation_layout` - "Arrange my windows for a presentation or screen sharing session"

## Workspace Setup Prompts
- `development_setup` - "Create a development-focused workspace layout with terminal, editor, and browser"
- `communication_setup` - "Organize communication apps (Slack, email, calendar) into a dedicated workspace"
- `cleanup_workspaces` - "Analyze my current workspaces and suggest consolidation or reorganization"

## Troubleshooting Prompts
- `debug_layout` - "Help me understand why my window layout isn't working as expected"
- `find_window` - "Help me find a specific window that I've lost track of"

---

# Suggested Advanced MCP Server Features

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
