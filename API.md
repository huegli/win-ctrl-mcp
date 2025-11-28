# AeroSpace Window Manager MCP Server API

This document describes the API for the AeroSpace Window Manager MCP Server, including all tools, resources, and prompts.

---

## Table of Contents

1. [Overview](#overview)
2. [Tools](#tools)
   - [Window Management](#window-management-tools)
   - [Layout Management](#layout-management-tools)
3. [Resources](#resources)
4. [Prompts](#prompts)
5. [Error Handling](#error-handling)

---

## Overview

The AeroSpace MCP Server provides programmatic control over the AeroSpace tiling window manager for macOS. It exposes functionality through the Model Context Protocol (MCP), enabling LLMs and other clients to manage windows, workspaces, monitors, and layouts.

### Base Requirements

- AeroSpace window manager must be installed and running
- Python >= 3.10
- FastMCP SDK
- The `aerospace` CLI must be available in PATH

### Command Execution

All tools execute AeroSpace commands via the `aerospace` CLI. Commands are executed synchronously and return structured JSON responses.

---

## Tools

### Window Management Tools

#### `focus_window`

Focus a window by direction or window ID.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `direction` | string | No | Direction to focus: `left`, `right`, `up`, `down` |
| `window_id` | integer | No | Specific window ID to focus |

*Note: Either `direction` or `window_id` must be provided, but not both.*

**Returns:**

```json
{
  "success": true,
  "focused_window": {
    "window_id": 1234,
    "app_name": "Firefox",
    "title": "GitHub - Mozilla Firefox"
  }
}
```

**Examples:**

```python
# Focus window to the right
await focus_window(direction="right")

# Focus specific window by ID
await focus_window(window_id=1234)
```

**AeroSpace CLI equivalent:**
```bash
aerospace focus left
aerospace focus --window-id 1234
```

---

#### `focus_monitor`

Focus a specific monitor by name, pattern, or direction.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `target` | string | Yes | Monitor identifier: direction (`left`, `right`, `up`, `down`), name, or pattern |

**Returns:**

```json
{
  "success": true,
  "focused_monitor": {
    "name": "Built-in Retina Display",
    "id": 1
  }
}
```

**Examples:**

```python
# Focus monitor to the right
await focus_monitor(target="right")

# Focus monitor by name
await focus_monitor(target="DELL U2720Q")
```

**AeroSpace CLI equivalent:**
```bash
aerospace focus-monitor right
aerospace focus-monitor "DELL U2720Q"
```

---

#### `focus_workspace`

Switch to a specific workspace by name or number.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `workspace` | string | Yes | Workspace name or number (e.g., "1", "dev", "mail") |

**Returns:**

```json
{
  "success": true,
  "workspace": {
    "name": "dev",
    "window_count": 3,
    "monitor": "Built-in Retina Display"
  }
}
```

**Examples:**

```python
# Switch to workspace 1
await focus_workspace(workspace="1")

# Switch to named workspace
await focus_workspace(workspace="dev")
```

**AeroSpace CLI equivalent:**
```bash
aerospace workspace 1
aerospace workspace dev
```

---

#### `move_window`

Move the focused window to a different workspace, monitor, or position.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `target_type` | string | Yes | Type of move: `workspace`, `monitor`, or `direction` |
| `target` | string | Yes | Target destination (workspace name, monitor name, or direction) |
| `window_id` | integer | No | Specific window ID to move (defaults to focused window) |

**Returns:**

```json
{
  "success": true,
  "window_id": 1234,
  "moved_to": {
    "type": "workspace",
    "name": "2"
  }
}
```

**Examples:**

```python
# Move focused window to workspace 2
await move_window(target_type="workspace", target="2")

# Move focused window to the left monitor
await move_window(target_type="monitor", target="left")

# Move window in a direction (swap with adjacent)
await move_window(target_type="direction", target="right")

# Move specific window to workspace
await move_window(target_type="workspace", target="dev", window_id=1234)
```

**AeroSpace CLI equivalent:**
```bash
aerospace move-node-to-workspace 2
aerospace move-node-to-monitor left
aerospace move right
```

---

#### `resize_window`

Resize the focused window.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `dimension` | string | Yes | Dimension to resize: `smart`, `width`, `height` |
| `amount` | string | Yes | Resize amount with sign: `+50`, `-50`, `+10%`, `-10%` |

**Returns:**

```json
{
  "success": true,
  "window_id": 1234,
  "resize": {
    "dimension": "width",
    "amount": "+50"
  }
}
```

**Examples:**

```python
# Smart resize (increases size in the "natural" direction)
await resize_window(dimension="smart", amount="+50")

# Increase width by 100 pixels
await resize_window(dimension="width", amount="+100")

# Decrease height by 10%
await resize_window(dimension="height", amount="-10%")
```

**AeroSpace CLI equivalent:**
```bash
aerospace resize smart +50
aerospace resize width +100
```

---

#### `close_window`

Close the focused window or a specific window by ID.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Specific window ID to close (defaults to focused window) |

**Returns:**

```json
{
  "success": true,
  "closed_window": {
    "window_id": 1234,
    "app_name": "TextEdit",
    "title": "Untitled"
  }
}
```

**Examples:**

```python
# Close the focused window
await close_window()

# Close specific window by ID
await close_window(window_id=1234)
```

**AeroSpace CLI equivalent:**
```bash
aerospace close
aerospace close --window-id 1234
```

---

#### `fullscreen_toggle`

Toggle fullscreen mode for the focused window.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Specific window ID (defaults to focused window) |

**Returns:**

```json
{
  "success": true,
  "window_id": 1234,
  "fullscreen": true
}
```

**Examples:**

```python
# Toggle fullscreen for focused window
await fullscreen_toggle()

# Toggle fullscreen for specific window
await fullscreen_toggle(window_id=1234)
```

**AeroSpace CLI equivalent:**
```bash
aerospace fullscreen
```

---

#### `minimize_window`

Minimize the focused window or a specific window.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Specific window ID (defaults to focused window) |

**Returns:**

```json
{
  "success": true,
  "window_id": 1234,
  "minimized": true
}
```

**Examples:**

```python
# Minimize the focused window
await minimize_window()
```

**AeroSpace CLI equivalent:**
```bash
aerospace macos-native-minimize
```

---

### Layout Management Tools

#### `set_layout`

Change the layout mode for the focused window's container.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `layout` | string | Yes | Layout mode: `tiles`, `accordion`, `h_tiles`, `v_tiles`, `h_accordion`, `v_accordion`, `floating`, `tiling` |

**Layout Modes:**

| Mode | Description |
|------|-------------|
| `tiles` | Toggle between horizontal and vertical tiling |
| `accordion` | Toggle between horizontal and vertical accordion |
| `h_tiles` | Horizontal tiling (windows side by side) |
| `v_tiles` | Vertical tiling (windows stacked) |
| `h_accordion` | Horizontal accordion (one visible, others stacked horizontally) |
| `v_accordion` | Vertical accordion (one visible, others stacked vertically) |
| `floating` | Make window floating |
| `tiling` | Make window tiling |

**Returns:**

```json
{
  "success": true,
  "layout": "h_tiles",
  "affected_windows": [1234, 5678]
}
```

**Examples:**

```python
# Set horizontal tiling layout
await set_layout(layout="h_tiles")

# Toggle to accordion mode
await set_layout(layout="accordion")

# Make current window floating
await set_layout(layout="floating")
```

**AeroSpace CLI equivalent:**
```bash
aerospace layout h_tiles
aerospace layout floating
```

---

#### `split_window`

Split the current container to prepare for a new window.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `orientation` | string | Yes | Split orientation: `horizontal` or `vertical` |

**Returns:**

```json
{
  "success": true,
  "split_orientation": "horizontal"
}
```

**Examples:**

```python
# Split horizontally (next window appears to the right)
await split_window(orientation="horizontal")

# Split vertically (next window appears below)
await split_window(orientation="vertical")
```

**AeroSpace CLI equivalent:**
```bash
aerospace split horizontal
aerospace split vertical
```

---

#### `flatten_workspace`

Flatten the workspace tree, removing nested containers.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `workspace` | string | No | Workspace to flatten (defaults to current workspace) |

**Returns:**

```json
{
  "success": true,
  "workspace": "1",
  "flattened_containers": 3
}
```

**Examples:**

```python
# Flatten current workspace
await flatten_workspace()

# Flatten specific workspace
await flatten_workspace(workspace="dev")
```

**AeroSpace CLI equivalent:**
```bash
aerospace flatten-workspace-tree
```

---

#### `balance_sizes`

Balance window sizes in the current workspace.

**Parameters:**

None.

**Returns:**

```json
{
  "success": true,
  "workspace": "1",
  "balanced_windows": 4
}
```

**Examples:**

```python
# Balance all window sizes
await balance_sizes()
```

**AeroSpace CLI equivalent:**
```bash
aerospace balance-sizes
```

---

## Resources

Resources provide read-only access to AeroSpace state information. They use URI templates and return JSON data.

### `aerospace://windows`

List all windows with metadata.

**URI:** `aerospace://windows`

**Response:**

```json
{
  "windows": [
    {
      "window_id": 1234,
      "app_name": "Firefox",
      "app_bundle_id": "org.mozilla.firefox",
      "title": "GitHub - Mozilla Firefox",
      "workspace": "1",
      "monitor": "Built-in Retina Display",
      "is_focused": true,
      "is_fullscreen": false,
      "is_floating": false
    },
    {
      "window_id": 5678,
      "app_name": "Terminal",
      "app_bundle_id": "com.apple.Terminal",
      "title": "bash - 80x24",
      "workspace": "1",
      "monitor": "Built-in Retina Display",
      "is_focused": false,
      "is_fullscreen": false,
      "is_floating": false
    }
  ],
  "total_count": 2
}
```

**AeroSpace CLI equivalent:**
```bash
aerospace list-windows --all --json
```

---

### `aerospace://windows/{window_id}`

Get details for a specific window.

**URI Template:** `aerospace://windows/{window_id}`

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `window_id` | integer | The window ID |

**Response:**

```json
{
  "window_id": 1234,
  "app_name": "Firefox",
  "app_bundle_id": "org.mozilla.firefox",
  "title": "GitHub - Mozilla Firefox",
  "workspace": "1",
  "monitor": "Built-in Retina Display",
  "is_focused": true,
  "is_fullscreen": false,
  "is_floating": false,
  "parent_container": "h_tiles"
}
```

---

### `aerospace://workspaces`

List all workspaces.

**URI:** `aerospace://workspaces`

**Response:**

```json
{
  "workspaces": [
    {
      "name": "1",
      "monitor": "Built-in Retina Display",
      "is_focused": true,
      "is_visible": true,
      "window_count": 3
    },
    {
      "name": "2",
      "monitor": "Built-in Retina Display",
      "is_focused": false,
      "is_visible": false,
      "window_count": 1
    },
    {
      "name": "dev",
      "monitor": "DELL U2720Q",
      "is_focused": false,
      "is_visible": true,
      "window_count": 2
    }
  ],
  "total_count": 3
}
```

**AeroSpace CLI equivalent:**
```bash
aerospace list-workspaces --all --json
```

---

### `aerospace://workspaces/{workspace_name}`

Get details for a specific workspace.

**URI Template:** `aerospace://workspaces/{workspace_name}`

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `workspace_name` | string | The workspace name |

**Response:**

```json
{
  "name": "dev",
  "monitor": "DELL U2720Q",
  "is_focused": false,
  "is_visible": true,
  "windows": [
    {
      "window_id": 1234,
      "app_name": "VS Code",
      "title": "project - Visual Studio Code"
    },
    {
      "window_id": 5678,
      "app_name": "Terminal",
      "title": "zsh"
    }
  ],
  "layout": "h_tiles"
}
```

---

### `aerospace://monitors`

List all monitors.

**URI:** `aerospace://monitors`

**Response:**

```json
{
  "monitors": [
    {
      "id": 1,
      "name": "Built-in Retina Display",
      "is_main": true,
      "workspaces": ["1", "2", "3"],
      "focused_workspace": "1"
    },
    {
      "id": 2,
      "name": "DELL U2720Q",
      "is_main": false,
      "workspaces": ["dev", "mail"],
      "focused_workspace": "dev"
    }
  ],
  "total_count": 2
}
```

**AeroSpace CLI equivalent:**
```bash
aerospace list-monitors --json
```

---

### `aerospace://tree`

Get the current window tree structure.

**URI:** `aerospace://tree`

**Response:**

```json
{
  "tree": {
    "type": "workspace",
    "name": "1",
    "layout": "h_tiles",
    "children": [
      {
        "type": "window",
        "window_id": 1234,
        "app_name": "Firefox",
        "title": "GitHub"
      },
      {
        "type": "container",
        "layout": "v_tiles",
        "children": [
          {
            "type": "window",
            "window_id": 5678,
            "app_name": "Terminal",
            "title": "zsh"
          },
          {
            "type": "window",
            "window_id": 9012,
            "app_name": "Notes",
            "title": "Meeting Notes"
          }
        ]
      }
    ]
  }
}
```

**AeroSpace CLI equivalent:**
```bash
aerospace debug-windows
```

---

### `aerospace://focused`

Get currently focused window, workspace, and monitor info.

**URI:** `aerospace://focused`

**Response:**

```json
{
  "window": {
    "window_id": 1234,
    "app_name": "Firefox",
    "title": "GitHub - Mozilla Firefox"
  },
  "workspace": {
    "name": "1",
    "window_count": 3
  },
  "monitor": {
    "id": 1,
    "name": "Built-in Retina Display"
  }
}
```

---

## Prompts

Prompts provide pre-configured interaction patterns for common window management tasks.

### `organize_windows`

Help organize current windows efficiently based on open applications.

**Description:** "Help me organize my current windows efficiently based on the apps I have open"

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `strategy` | string | No | Organization strategy: `by_app`, `by_task`, `minimal` |

**Example Interaction:**

```
User: /organize_windows
Assistant: I can see you have 8 windows open across 3 workspaces. Let me analyze them:

Current windows:
- Workspace 1: Firefox (GitHub), Terminal (2 windows), VS Code
- Workspace 2: Slack, Mail
- Workspace dev: Chrome (Documentation), Notes

Suggested organization:
1. Move VS Code to "dev" workspace with your documentation browser
2. Keep communication apps (Slack, Mail) together on workspace 2
3. Use workspace 1 for browsing and general terminal work

Shall I proceed with this reorganization?
```

**Prompt Template:**

```
You have access to window management tools. First, use the aerospace://windows
resource to list all open windows. Then analyze the applications and suggest
an efficient organization based on the user's workflow.

Consider grouping by:
- Development tools (editors, terminals, documentation)
- Communication (email, chat, video)
- Reference materials (browsers, notes)
- Media and entertainment

After suggesting, ask for confirmation before making changes.
```

---

### `focus_mode`

Update this section based on SPEC.md

---

### `presentation_layout`

Arrange windows for a presentation or screen sharing session.

**Description:** "Arrange my windows for a presentation or screen sharing session"

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `presenter_app` | string | No | The main app to present (defaults to auto-detect) |
| `notes_app` | string | No | App for presenter notes (optional) |

**Example Interaction:**

```
User: /presentation_layout
Assistant: I'll set up your windows for presenting. What will you be sharing?

Detected presentation-ready apps:
- Keynote: "Q4 Review.key"
- Google Chrome: "Slides - Product Demo"
- VS Code: "demo-project"

Which would you like as your main presentation? I'll:
1. Make it fullscreen on your primary monitor
2. Move other apps to secondary monitor or hide them
3. Keep any notes app accessible but hidden from screen share

User: VS Code for the demo
Assistant: Setting up VS Code for your demo:

1. Made VS Code fullscreen on primary monitor
2. Moved Slack and Mail to secondary monitor
3. Hidden notification-heavy apps

Your presentation layout is ready. Tip: I've kept Terminal accessible via
workspace 2 if you need to run commands during the demo.
```

---

### `debug_app_gui`

Update this section based on SPEC.md

---

## Error Handling

All tools return structured error responses when operations fail.

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description",
    "details": {}
  }
}
```

### Common Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `AEROSPACE_NOT_RUNNING` | AeroSpace daemon is not running | Start AeroSpace with `aerospace start` |
| `WINDOW_NOT_FOUND` | Specified window ID does not exist | Verify window ID with `aerospace://windows` |
| `WORKSPACE_NOT_FOUND` | Specified workspace does not exist | Check workspace names with `aerospace://workspaces` |
| `INVALID_DIRECTION` | Invalid direction parameter | Use: `left`, `right`, `up`, `down` |
| `INVALID_LAYOUT` | Invalid layout mode specified | See valid layouts in `set_layout` documentation |
| `NO_WINDOW_FOCUSED` | No window is currently focused | Focus a window first |
| `COMMAND_FAILED` | AeroSpace CLI command failed | Check the error details for CLI output |
| `PERMISSION_DENIED` | Accessibility permissions not granted | Grant accessibility permissions in System Settings |

### Example Error Responses

**Window Not Found:**
```json
{
  "success": false,
  "error": {
    "code": "WINDOW_NOT_FOUND",
    "message": "Window with ID 9999 not found",
    "details": {
      "requested_window_id": 9999,
      "available_windows": [1234, 5678, 9012]
    }
  }
}
```

**AeroSpace Not Running:**
```json
{
  "success": false,
  "error": {
    "code": "AEROSPACE_NOT_RUNNING",
    "message": "AeroSpace daemon is not running. Please start it first.",
    "details": {
      "suggestion": "Run 'aerospace start' or launch AeroSpace from Applications"
    }
  }
}
```

**Invalid Parameter:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_DIRECTION",
    "message": "Invalid direction 'diagonal'. Must be one of: left, right, up, down",
    "details": {
      "provided": "diagonal",
      "valid_options": ["left", "right", "up", "down"]
    }
  }
}
```
