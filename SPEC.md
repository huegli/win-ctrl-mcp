# Implementation Phases

- **PHASE 1**: Core window management, layout, capture, display info, and smart focus tools
- **PHASE 2**: Enhanced GUI debugging with accessibility inspection, visual comparison, and interaction simulation

---

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

## Display Information Tools
- `get_display_info` - Returns detailed information about all connected displays (resolution, scale factor, size, position, PPI)
- `get_display_category` - Returns simplified display configuration category (small_single, medium_single, large_single, dual_display, triple_plus) with recommended strategy

## Smart Focus Tools
- `apply_focus_preset` - Apply a predefined focus layout based on display category
- `save_focus_preset` - Save current window arrangement as a named focus preset
- `load_focus_preset` - Load and apply a previously saved focus preset
- `resize_window_optimal` - Resize window to optimal dimensions based on content type (code_editor, browser, terminal, document)
- `set_window_zone` - Position window in a named zone (center_focus, left_reference, right_reference) rather than explicit coordinates
- `move_app_category_to_monitor` - Move all windows of an app category (communication, development, reference, media) to a specific monitor

---

# PHASE 2: Enhanced GUI Debugging Tools

## Capture Tools (Enhanced)
- `capture_region` - Capture a specific rectangular region of a window
- `capture_element` - Capture a specific UI element by accessibility identifier or label
- `capture_sequence` - Capture multiple frames at intervals for animations/transitions

## Inspection Tools
- `get_accessibility_tree` - Retrieve the accessibility tree for a window (macOS Accessibility API)
- `find_element` - Find UI elements matching a query (role, label, etc.)
- `get_element_properties` - Get detailed properties of a specific element (bounds, enabled, visible, actions)

## Comparison Tools
- `compare_screenshots` - Generate a visual diff between two screenshots with difference percentage and regions
- `compare_element_state` - Compare current element state against expected state (semantic comparison)
- `compare_layout` - Compare layout/positioning of elements against expected layout

## Interaction Tools
- `simulate_click` - Simulate a mouse click at coordinates or on an element
- `simulate_input` - Simulate keyboard input to a focused element
- `trigger_ui_state` - Force a specific UI state for testing (hover, pressed, focused, disabled)

## Debug Session Tools
- `start_debug_session` - Begin a debug session with automatic state tracking and baseline capture
- `capture_debug_snapshot` - Capture a labeled snapshot within a session
- `get_session_history` - Get all snapshots and comparisons from a debug session
- `end_debug_session` - End session and optionally generate summary report

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
- `aerospace://displays` - Complete display configuration (resolution, scale, size, arrangement, category)
- `aerospace://displays/{display_id}` - Individual display details including assigned workspaces

## PHASE 2: GUI Debugging Resources
- `aerospace://window/{window_id}/accessibility` - Full accessibility tree for a window
- `aerospace://window/{window_id}/elements` - Flat list of all accessible elements with bounds
- `aerospace://debug/sessions` - List of active and recent debug sessions
- `aerospace://debug/session/{session_id}` - Details of a specific debug session

---

#  Prompts to implement

## Window Organization Prompts
- `organize_windows` - "Help me organize my current windows efficiently based on the apps I have open"
- `smart_focus` - "Display-aware focus mode that adapts window arrangement based on display configuration (single small/medium/large display, dual display, triple+ displays). Makes the focused window prominent while keeping reference windows accessible, using different strategies per display category. Supports presets, undo, and batch operations."
- `presentation_layout` - "Arrange my windows for a presentation or screen sharing session"

## Development  Prompts
- `debug_app_gui` - "Debug the GUI of an app under development by comparing what is expected vs what is actually on screen, using the capture tool functionality" (PHASE 2: Enhanced with accessibility tree inspection, visual diff generation, element state comparison, interaction simulation, and debug session tracking)

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
