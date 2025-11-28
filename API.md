# AeroSpace Window Manager MCP Server API

This document describes the API for the AeroSpace Window Manager MCP Server, including all tools, resources, and prompts.

---

## Table of Contents

1. [Overview](#overview)
2. [Tools - Phase 1](#tools)
   - [Window Management](#window-management-tools)
   - [Layout Management](#layout-management-tools)
   - [Capture Tools](#capture-tools)
   - [Display Information Tools](#display-information-tools)
   - [Smart Focus Tools](#smart-focus-tools)
3. [Tools - Phase 2](#phase-2-enhanced-gui-debugging-tools)
   - [Capture Tools (Enhanced)](#capture-tools-enhanced)
   - [Inspection Tools](#inspection-tools)
   - [Comparison Tools](#comparison-tools)
   - [Interaction Tools](#interaction-tools)
   - [Debug Session Tools](#debug-session-tools)
4. [Resources](#resources)
5. [Prompts](#prompts)
6. [Error Handling](#error-handling)

---

## Overview

The AeroSpace MCP Server provides programmatic control over the AeroSpace tiling window manager for macOS. It exposes functionality through the Model Context Protocol (MCP), enabling LLMs and other clients to manage windows, workspaces, monitors, and layouts.

### Base Requirements

- AeroSpace window manager must be installed and running
- Python >= 3.10
- FastMCP SDK
- The `aerospace` CLI must be available in PATH
- The macOS `screencapture` CLI utility (for capture tools)

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

> **Note:** This uses AeroSpace's native fullscreen, not macOS native fullscreen (`macos-native-fullscreen`).

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

### Capture Tools

#### `capture_window`

Capture a screenshot of the currently focused window.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Specific window ID to capture (defaults to focused window) |
| `output_path` | string | No | Path to save the screenshot (defaults to temp file) |
| `format` | string | No | Image format: `png`, `jpg`, `pdf` (defaults to `png`) |

**Returns:**

```json
{
  "success": true,
  "capture": {
    "window_id": 1234,
    "app_name": "Firefox",
    "title": "GitHub - Mozilla Firefox",
    "file_path": "/tmp/window_capture_1234.png",
    "format": "png",
    "dimensions": {
      "width": 1920,
      "height": 1080
    }
  }
}
```

**Examples:**

```python
# Capture the focused window
await capture_window()

# Capture specific window to a custom path
await capture_window(window_id=1234, output_path="/Users/me/screenshots/app.png")

# Capture as JPEG
await capture_window(format="jpg")
```

**macOS CLI equivalent:**
```bash
# Capture specific window (interactive selection)
screencapture -w /path/to/output.png

# Capture window by ID (requires window bounds)
screencapture -R x,y,w,h /path/to/output.png
```

---

#### `capture_workspace`

Capture a screenshot of the currently focused workspace (and monitor).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `workspace` | string | No | Workspace name to capture (defaults to focused workspace) |
| `output_path` | string | No | Path to save the screenshot (defaults to temp file) |
| `format` | string | No | Image format: `png`, `jpg`, `pdf` (defaults to `png`) |

**Returns:**

```json
{
  "success": true,
  "capture": {
    "workspace": "dev",
    "monitor": "Built-in Retina Display",
    "file_path": "/tmp/workspace_capture_dev.png",
    "format": "png",
    "dimensions": {
      "width": 2560,
      "height": 1440
    },
    "windows_captured": [
      {"window_id": 1234, "app_name": "VS Code"},
      {"window_id": 5678, "app_name": "Terminal"}
    ]
  }
}
```

**Examples:**

```python
# Capture the current workspace
await capture_workspace()

# Capture specific workspace
await capture_workspace(workspace="dev")

# Capture to custom path as PDF
await capture_workspace(output_path="/Users/me/workspace.pdf", format="pdf")
```

**macOS CLI equivalent:**
```bash
# Capture entire screen (monitor)
screencapture /path/to/output.png

# Capture specific display
screencapture -D 1 /path/to/output.png
```

---

### Display Information Tools

#### `get_display_info`

Returns detailed information about all connected displays.

**Parameters:**

None.

**Returns:**

```json
{
  "displays": [
    {
      "id": 1,
      "name": "Built-in Retina Display",
      "resolution": {"width": 2560, "height": 1600},
      "scale_factor": 2.0,
      "effective_resolution": {"width": 1280, "height": 800},
      "size_inches": 14.2,
      "is_primary": true,
      "is_builtin": true,
      "position": {"x": 0, "y": 0},
      "ppi": 218
    },
    {
      "id": 2,
      "name": "DELL U2720Q",
      "resolution": {"width": 3840, "height": 2160},
      "scale_factor": 1.5,
      "effective_resolution": {"width": 2560, "height": 1440},
      "size_inches": 27,
      "is_primary": false,
      "is_builtin": false,
      "position": {"x": 1280, "y": -320},
      "ppi": 163
    }
  ],
  "arrangement": "horizontal",
  "total_effective_pixels": 5765120,
  "category": "dual_display"
}
```

**Examples:**

```python
# Get all display information
info = await get_display_info()
print(f"Display category: {info['category']}")
print(f"Number of displays: {len(info['displays'])}")
```

---

#### `get_display_category`

Returns simplified display configuration category with recommended focus strategy.

**Parameters:**

None.

**Returns:**

```json
{
  "category": "dual_display",
  "primary_size": "medium",
  "secondary_sizes": ["large"],
  "recommended_strategy": "primary_focus_secondary_reference",
  "description": "Focus window fullscreen on primary, reference windows tiled on secondary"
}
```

**Display Categories:**

| Category | Description | Recommended Strategy |
|----------|-------------|---------------------|
| `small_single` | ≤15", ≤1920x1080 | Fullscreen focus, workspaces for others |
| `medium_single` | 15-24", up to 2560x1440 | 70/30 split with sidebar |
| `large_single` | ≥27", ≥2560x1440 | Centered focus with flanking reference |
| `dual_display` | Two monitors | Focus on primary, reference on secondary |
| `triple_plus` | Three or more monitors | Dedicated monitors per purpose |

**Examples:**

```python
# Quick category check for focus mode decisions
category = await get_display_category()
if category['category'] == 'small_single':
    # Use fullscreen strategy
    await fullscreen_toggle()
elif category['category'] == 'dual_display':
    # Use multi-monitor strategy
    await apply_focus_preset(preset="dual_monitor_focus")
```

---

### Smart Focus Tools

#### `apply_focus_preset`

Apply a predefined or saved focus layout based on display category.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `preset` | string | Yes | Preset name: `auto`, `small_single_focus`, `medium_split`, `large_centered`, `dual_monitor_focus`, `triple_monitor_focus`, or a saved preset name |
| `focus_window_id` | integer | No | Window to focus (defaults to currently focused) |
| `reference_apps` | string[] | No | Apps to keep visible as reference |
| `hide_communication` | boolean | No | Move communication apps to separate workspace |

**Returns:**

```json
{
  "success": true,
  "preset_applied": "dual_monitor_focus",
  "display_category": "dual_display",
  "layout": {
    "focus_window": {
      "window_id": 1234,
      "monitor": 1,
      "arrangement": "fullscreen"
    },
    "reference_windows": [
      {"window_id": 5678, "monitor": 2, "arrangement": "tiled"},
      {"window_id": 9012, "monitor": 2, "arrangement": "tiled"}
    ],
    "hidden_windows": [
      {"window_id": 3456, "moved_to_workspace": "communication"}
    ]
  }
}
```

**Examples:**

```python
# Auto-detect best preset based on display configuration
await apply_focus_preset(preset="auto")

# Apply specific preset with options
await apply_focus_preset(
    preset="dual_monitor_focus",
    reference_apps=["Terminal", "Chrome"],
    hide_communication=True
)
```

---

#### `save_focus_preset`

Save the current window arrangement as a named focus preset.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | string | Yes | Name for the preset |
| `description` | string | No | Human-readable description |

**Returns:**

```json
{
  "success": true,
  "preset": {
    "name": "coding_focus",
    "description": "VS Code focused, terminal on side",
    "display_category": "medium_single",
    "created_at": "2025-01-15T10:30:00Z",
    "window_count": 4
  }
}
```

**Examples:**

```python
# Save current arrangement
await save_focus_preset(
    name="coding_focus",
    description="VS Code focused, terminal on side"
)
```

---

#### `load_focus_preset`

Load and apply a previously saved focus preset.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | string | Yes | Name of the preset to load |
| `adapt_to_displays` | boolean | No | Adapt preset if display config changed (default: true) |

**Returns:**

```json
{
  "success": true,
  "preset_loaded": "coding_focus",
  "adapted": false,
  "windows_arranged": 4
}
```

**Examples:**

```python
# Load a saved preset
await load_focus_preset(name="coding_focus")

# Load with adaptation disabled (fail if displays don't match)
await load_focus_preset(name="coding_focus", adapt_to_displays=False)
```

---

#### `resize_window_optimal`

Resize a window to optimal dimensions based on its content type.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Window to resize (defaults to focused) |
| `content_type` | string | Yes | Content type: `code_editor`, `browser`, `terminal`, `document`, `communication` |
| `max_width_percent` | integer | No | Maximum width as percentage of screen (default: 80) |
| `min_width_percent` | integer | No | Minimum width as percentage of screen (default: 40) |

**Returns:**

```json
{
  "success": true,
  "window_id": 1234,
  "content_type": "code_editor",
  "new_dimensions": {
    "width": 1400,
    "height": 900,
    "optimal_chars_per_line": 120
  }
}
```

**Optimal Widths by Content Type:**

| Content Type | Optimal Width | Rationale |
|--------------|---------------|-----------|
| `code_editor` | 100-140 chars | Standard code line length |
| `browser` | 1200-1400px | Responsive breakpoint |
| `terminal` | 80-120 chars | Traditional terminal width |
| `document` | 60-80 chars | Readable prose line length |
| `communication` | 400-600px | Chat/sidebar width |

**Examples:**

```python
# Resize VS Code to optimal coding width
await resize_window_optimal(content_type="code_editor")

# Resize with constraints
await resize_window_optimal(
    content_type="browser",
    max_width_percent=70,
    min_width_percent=50
)
```

---

#### `set_window_zone`

Position a window in a named zone rather than using explicit coordinates.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Window to position (defaults to focused) |
| `zone` | string | Yes | Zone name: `center_focus`, `left_reference`, `right_reference`, `top_reference`, `bottom_reference`, `floating_pip` |
| `monitor` | string | No | Monitor: `primary`, `secondary`, or monitor ID (default: `primary`) |

**Returns:**

```json
{
  "success": true,
  "window_id": 1234,
  "zone": "center_focus",
  "monitor": "primary",
  "bounds": {
    "x": 320,
    "y": 0,
    "width": 1920,
    "height": 1080
  }
}
```

**Available Zones:**

| Zone | Description |
|------|-------------|
| `center_focus` | Center of screen, 60-70% width |
| `left_reference` | Left side, 20-30% width |
| `right_reference` | Right side, 20-30% width |
| `top_reference` | Top half of screen |
| `bottom_reference` | Bottom half of screen |
| `floating_pip` | Small floating window in corner |

**Examples:**

```python
# Position main editor in center focus zone
await set_window_zone(zone="center_focus")

# Position terminal on right side of secondary monitor
await set_window_zone(
    window_id=5678,
    zone="right_reference",
    monitor="secondary"
)
```

---

#### `move_app_category_to_monitor`

Move all windows belonging to an application category to a specific monitor.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `category` | string | Yes | App category: `communication`, `development`, `reference`, `media` |
| `monitor` | string | Yes | Target monitor: `primary`, `secondary`, `tertiary`, or monitor ID |
| `layout` | string | No | Layout for moved windows: `tiled`, `accordion`, `stacked` (default: `tiled`) |

**Returns:**

```json
{
  "success": true,
  "category": "communication",
  "monitor": "secondary",
  "windows_moved": [
    {"window_id": 1234, "app_name": "Slack"},
    {"window_id": 5678, "app_name": "Mail"},
    {"window_id": 9012, "app_name": "Messages"}
  ],
  "layout_applied": "tiled"
}
```

**App Categories:**

| Category | Included Apps |
|----------|---------------|
| `communication` | Slack, Discord, Mail, Messages, Teams, Zoom |
| `development` | VS Code, Xcode, Terminal, iTerm, IntelliJ |
| `reference` | Chrome, Safari, Firefox, Notes, Notion, Obsidian |
| `media` | Spotify, Music, YouTube, VLC, Photos |

**Examples:**

```python
# Move all communication apps to secondary monitor
await move_app_category_to_monitor(
    category="communication",
    monitor="secondary"
)

# Move reference apps to tertiary monitor in accordion layout
await move_app_category_to_monitor(
    category="reference",
    monitor="tertiary",
    layout="accordion"
)
```

---

## Phase 2: Enhanced GUI Debugging Tools

These tools enable AI agents to debug GUI applications by inspecting accessibility trees, comparing visual states, and simulating user interactions.

### Requirements (Phase 2)

- macOS Accessibility permissions must be granted (System Preferences > Privacy & Security > Accessibility)
- `pyobjc-framework-ApplicationServices` for accessibility APIs
- `pyobjc-framework-Quartz` for advanced screen capture

---

### Capture Tools (Enhanced)

#### `capture_region`

Capture a specific rectangular region of a window.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Window ID (defaults to focused window) |
| `region` | object | Yes | Region to capture: `{x, y, width, height}` |
| `output_path` | string | No | Path to save screenshot (defaults to temp file) |
| `format` | string | No | Image format: `png`, `jpg` (defaults to `png`) |

**Returns:**

```json
{
  "success": true,
  "file_path": "/tmp/region_capture.png",
  "region": {"x": 100, "y": 50, "width": 200, "height": 100},
  "window_id": 1234
}
```

**Examples:**

```python
# Capture a specific region of the focused window
await capture_region(
    region={"x": 100, "y": 50, "width": 200, "height": 100}
)

# Capture region from specific window
await capture_region(
    window_id=1234,
    region={"x": 0, "y": 0, "width": 400, "height": 300},
    output_path="/tmp/header_region.png"
)
```

---

#### `capture_element`

Capture a specific UI element by accessibility identifier or label.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Window ID (defaults to focused window) |
| `element_query` | object | Yes | Query to find element: `{role, label, identifier}` |
| `padding` | integer | No | Pixels of padding around element (default: 0) |
| `output_path` | string | No | Path to save screenshot |

**Returns:**

```json
{
  "success": true,
  "file_path": "/tmp/element_capture.png",
  "element": {
    "role": "button",
    "label": "Submit",
    "bounds": {"x": 150, "y": 200, "width": 80, "height": 32}
  }
}
```

**Examples:**

```python
# Capture a button by label
await capture_element(
    element_query={"role": "button", "label": "Submit"},
    padding=10
)

# Capture a text field by identifier
await capture_element(
    window_id=1234,
    element_query={"identifier": "usernameField"}
)
```

---

#### `capture_sequence`

Capture multiple frames at intervals for animations/transitions.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Window ID (defaults to focused window) |
| `frames` | integer | Yes | Number of frames to capture |
| `interval_ms` | integer | Yes | Milliseconds between frames |
| `output_dir` | string | No | Directory for frame files |
| `region` | object | No | Optional region to capture |

**Returns:**

```json
{
  "success": true,
  "frames": [
    {"index": 0, "timestamp": 0, "file_path": "/tmp/seq/frame_000.png"},
    {"index": 1, "timestamp": 100, "file_path": "/tmp/seq/frame_001.png"},
    {"index": 2, "timestamp": 200, "file_path": "/tmp/seq/frame_002.png"}
  ],
  "total_duration_ms": 200
}
```

**Examples:**

```python
# Capture 10 frames at 100ms intervals
await capture_sequence(
    frames=10,
    interval_ms=100,
    output_dir="/tmp/animation_debug/"
)

# Capture animation in specific region
await capture_sequence(
    window_id=1234,
    frames=20,
    interval_ms=50,
    region={"x": 100, "y": 100, "width": 200, "height": 200}
)
```

---

### Inspection Tools

#### `get_accessibility_tree`

Retrieve the accessibility tree for a window using macOS Accessibility API.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Window ID (defaults to focused window) |
| `depth` | integer | No | Maximum depth to traverse (default: unlimited) |
| `include_hidden` | boolean | No | Include hidden elements (default: false) |

**Returns:**

```json
{
  "window_id": 1234,
  "app_name": "MyApp",
  "root": {
    "role": "window",
    "title": "Main Window",
    "bounds": {"x": 0, "y": 0, "width": 800, "height": 600},
    "children": [
      {
        "role": "toolbar",
        "bounds": {"x": 0, "y": 0, "width": 800, "height": 44},
        "children": [
          {
            "role": "button",
            "label": "New",
            "enabled": true,
            "bounds": {"x": 10, "y": 8, "width": 60, "height": 28}
          }
        ]
      },
      {
        "role": "scrollarea",
        "bounds": {"x": 0, "y": 44, "width": 800, "height": 556},
        "children": []
      }
    ]
  }
}
```

**Examples:**

```python
# Get full accessibility tree
tree = await get_accessibility_tree()

# Get shallow tree (depth 2)
tree = await get_accessibility_tree(depth=2)

# Include hidden elements
tree = await get_accessibility_tree(include_hidden=True)
```

---

#### `find_element`

Find UI elements matching a query.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Window ID (defaults to focused window) |
| `query` | object | Yes | Query object with match criteria |

**Query Options:**

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | Element role (button, textfield, etc.) |
| `label` | string | Exact label match |
| `label_contains` | string | Partial label match |
| `identifier` | string | Accessibility identifier |
| `enabled` | boolean | Filter by enabled state |
| `visible` | boolean | Filter by visibility |

**Returns:**

```json
{
  "matches": [
    {
      "role": "button",
      "label": "Submit Form",
      "bounds": {"x": 300, "y": 500, "width": 100, "height": 40},
      "enabled": true,
      "path": "window/dialog/form/button[2]"
    }
  ]
}
```

**Examples:**

```python
# Find all buttons
buttons = await find_element(query={"role": "button"})

# Find element by partial label
elements = await find_element(query={"label_contains": "Submit"})

# Find enabled text fields
fields = await find_element(query={
    "role": "textfield",
    "enabled": True
})
```

---

#### `get_element_properties`

Get detailed properties of a specific element.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Window ID (defaults to focused window) |
| `element_path` | string | Yes | Path to element (e.g., "window/toolbar/button[0]") |

**Returns:**

```json
{
  "role": "button",
  "subrole": "none",
  "label": "New Document",
  "title": "New",
  "description": "Create a new document",
  "enabled": true,
  "focused": false,
  "visible": true,
  "bounds": {"x": 10, "y": 8, "width": 60, "height": 28},
  "actions": ["press"],
  "value": null,
  "attributes": {
    "accessibilityIdentifier": "newDocButton"
  }
}
```

**Examples:**

```python
# Get properties of first toolbar button
props = await get_element_properties(
    element_path="window/toolbar/button[0]"
)

# Check if element is enabled
props = await get_element_properties(
    window_id=1234,
    element_path="window/form/submitButton"
)
print(f"Button enabled: {props['enabled']}")
```

---

### Comparison Tools

#### `compare_screenshots`

Generate a visual diff between two screenshots.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `baseline` | string | Yes | Path to baseline/expected image |
| `actual` | string | Yes | Path to actual/current image |
| `output_diff` | string | No | Path to save diff image |
| `threshold` | float | No | Difference tolerance (0.0-1.0, default: 0.01) |

**Returns:**

```json
{
  "match": false,
  "difference_percentage": 3.2,
  "diff_image": "/tmp/diff.png",
  "diff_regions": [
    {
      "bounds": {"x": 150, "y": 200, "width": 80, "height": 32},
      "difference_percentage": 45.2,
      "description": "Significant difference in button region"
    }
  ],
  "dimensions_match": true,
  "baseline_dimensions": {"width": 800, "height": 600},
  "actual_dimensions": {"width": 800, "height": 600}
}
```

**Examples:**

```python
# Compare two screenshots
result = await compare_screenshots(
    baseline="/tmp/expected.png",
    actual="/tmp/actual.png",
    output_diff="/tmp/diff.png"
)

if not result["match"]:
    print(f"Difference: {result['difference_percentage']}%")
    for region in result["diff_regions"]:
        print(f"  Region at {region['bounds']}: {region['difference_percentage']}%")
```

---

#### `compare_element_state`

Compare current element state against expected state.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Window ID (defaults to focused window) |
| `element_path` | string | Yes | Path to element |
| `expected` | object | Yes | Expected property values |

**Expected Object Options:**

| Field | Type | Description |
|-------|------|-------------|
| `label` | string | Expected label |
| `enabled` | boolean | Expected enabled state |
| `visible` | boolean | Expected visibility |
| `value` | any | Expected value |
| `bounds.width` | object | Width constraints: `{min, max}` |
| `bounds.height` | object | Height constraints: `{min, max}` |

**Returns:**

```json
{
  "match": false,
  "mismatches": [
    {
      "property": "enabled",
      "expected": true,
      "actual": false,
      "message": "Button is disabled but expected to be enabled"
    }
  ],
  "matches": [
    {"property": "label", "value": "Submit"},
    {"property": "visible", "value": true}
  ]
}
```

**Examples:**

```python
# Check button state
result = await compare_element_state(
    element_path="window/form/button[0]",
    expected={
        "label": "Submit",
        "enabled": True,
        "bounds.width": {"min": 80, "max": 120}
    }
)

if not result["match"]:
    for mismatch in result["mismatches"]:
        print(f"Mismatch: {mismatch['message']}")
```

---

#### `compare_layout`

Compare layout/positioning of elements against expected layout.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Window ID (defaults to focused window) |
| `expected_layout` | object | Yes | Expected layout specification |

**Layout Specification:**

```json
{
  "element_name": {
    "role": "string",
    "position": "top|bottom|left|right|center|fill",
    "width": number,
    "height": number,
    "margin": number
  }
}
```

**Returns:**

```json
{
  "match": false,
  "layout_issues": [
    {
      "element": "sidebar",
      "expected": "position: left, width: 200",
      "actual": "position: left, width: 150",
      "issue": "Width mismatch: expected 200px, got 150px"
    }
  ],
  "verified": [
    {"element": "header", "status": "OK"},
    {"element": "content", "status": "OK"}
  ]
}
```

**Examples:**

```python
# Verify layout structure
result = await compare_layout(
    expected_layout={
        "header": {"role": "toolbar", "position": "top", "height": 44},
        "sidebar": {"role": "list", "position": "left", "width": 200},
        "content": {"role": "scrollarea", "position": "fill"}
    }
)
```

---

### Interaction Tools

#### `simulate_click`

Simulate a mouse click at coordinates or on an element.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Window ID (defaults to focused window) |
| `target` | object | Yes | Click target (coordinates or element query) |
| `click_type` | string | No | Type: `single`, `double`, `right` (default: single) |

**Target Options:**

- `{"coordinates": {"x": 100, "y": 200}}` - Click at specific coordinates
- `{"element_query": {"role": "button", "label": "Submit"}}` - Click on element

**Returns:**

```json
{
  "success": true,
  "clicked_at": {"x": 350, "y": 520},
  "element_clicked": {
    "role": "button",
    "label": "Submit"
  }
}
```

**Examples:**

```python
# Click on element by query
await simulate_click(
    target={"element_query": {"role": "button", "label": "Submit"}}
)

# Click at specific coordinates
await simulate_click(
    target={"coordinates": {"x": 100, "y": 200}}
)

# Double-click
await simulate_click(
    target={"element_query": {"role": "listitem", "label": "File.txt"}},
    click_type="double"
)
```

---

#### `simulate_input`

Simulate keyboard input to a focused element.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Window ID (defaults to focused window) |
| `text` | string | Yes | Text to input |
| `element_query` | object | No | Element to focus before typing |
| `clear_first` | boolean | No | Clear existing content first (default: false) |

**Returns:**

```json
{
  "success": true,
  "text_entered": "Hello World",
  "target_element": {
    "role": "textfield",
    "label": "Name"
  }
}
```

**Examples:**

```python
# Type into focused element
await simulate_input(text="Hello World")

# Type into specific field
await simulate_input(
    text="user@example.com",
    element_query={"role": "textfield", "label": "Email"},
    clear_first=True
)
```

---

#### `trigger_ui_state`

Force a specific UI state for testing appearance.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `window_id` | integer | No | Window ID (defaults to focused window) |
| `element_path` | string | Yes | Path to element |
| `state` | string | Yes | State to trigger: `hover`, `pressed`, `focused`, `disabled` |
| `duration_ms` | integer | No | How long to hold state (default: 1000) |

**Returns:**

```json
{
  "success": true,
  "element": "window/form/button[0]",
  "state_triggered": "hover",
  "duration_ms": 1000
}
```

**Examples:**

```python
# Trigger hover state for screenshot
await trigger_ui_state(
    element_path="window/form/button[0]",
    state="hover",
    duration_ms=2000
)

# Check focused appearance
await trigger_ui_state(
    element_path="window/form/textfield[0]",
    state="focused"
)
```

---

### Debug Session Tools

#### `start_debug_session`

Begin a debug session with automatic state tracking.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `app_name` | string | No | App to debug (defaults to focused window's app) |
| `session_name` | string | No | Name for the session |
| `baseline_capture` | boolean | No | Capture baseline screenshot (default: true) |
| `capture_accessibility` | boolean | No | Capture accessibility tree (default: true) |

**Returns:**

```json
{
  "session_id": "debug_abc123",
  "session_name": "button_color_debug",
  "app_name": "MyApp",
  "window_id": 1234,
  "baseline_capture": "/tmp/debug_sessions/debug_abc123/baseline.png",
  "baseline_accessibility": "/tmp/debug_sessions/debug_abc123/baseline_tree.json",
  "started_at": "2025-01-15T10:30:00Z"
}
```

**Examples:**

```python
# Start debug session
session = await start_debug_session(
    app_name="MyApp",
    session_name="button_color_debug"
)
print(f"Session ID: {session['session_id']}")
```

---

#### `capture_debug_snapshot`

Capture a labeled snapshot within a session.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `session_id` | string | Yes | Debug session ID |
| `label` | string | Yes | Label for this snapshot |
| `note` | string | No | Optional note about changes made |
| `compare_to_baseline` | boolean | No | Auto-compare to baseline (default: true) |

**Returns:**

```json
{
  "snapshot_id": "snap_001",
  "label": "after_css_fix",
  "file_path": "/tmp/debug_sessions/debug_abc123/snap_001_after_css_fix.png",
  "note": "Changed button color from gray to blue",
  "timestamp": "2025-01-15T10:35:00Z",
  "comparison": {
    "match": false,
    "difference_percentage": 1.2,
    "diff_image": "/tmp/debug_sessions/debug_abc123/diff_snap_001.png"
  }
}
```

**Examples:**

```python
# Capture snapshot after making changes
snapshot = await capture_debug_snapshot(
    session_id="debug_abc123",
    label="after_css_fix",
    note="Changed button color from gray to blue"
)
print(f"Difference: {snapshot['comparison']['difference_percentage']}%")
```

---

#### `get_session_history`

Get all snapshots and comparisons from a debug session.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `session_id` | string | Yes | Debug session ID |

**Returns:**

```json
{
  "session_id": "debug_abc123",
  "session_name": "button_color_debug",
  "app_name": "MyApp",
  "started_at": "2025-01-15T10:30:00Z",
  "snapshots": [
    {
      "id": "baseline",
      "timestamp": "2025-01-15T10:30:00Z",
      "file_path": "/tmp/debug_sessions/debug_abc123/baseline.png"
    },
    {
      "id": "snap_001",
      "label": "after_css_fix",
      "timestamp": "2025-01-15T10:35:00Z",
      "file_path": "/tmp/debug_sessions/debug_abc123/snap_001_after_css_fix.png",
      "note": "Changed button color from gray to blue"
    }
  ],
  "comparisons": [
    {
      "baseline": "baseline",
      "snapshot": "snap_001",
      "difference_percentage": 1.2,
      "diff_image": "/tmp/debug_sessions/debug_abc123/diff_snap_001.png"
    }
  ]
}
```

---

#### `end_debug_session`

End a debug session and optionally generate a summary report.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `session_id` | string | Yes | Debug session ID |
| `generate_report` | boolean | No | Generate HTML summary report (default: false) |
| `cleanup` | boolean | No | Delete temporary files (default: false) |

**Returns:**

```json
{
  "success": true,
  "session_id": "debug_abc123",
  "duration_seconds": 300,
  "total_snapshots": 5,
  "report_path": "/tmp/debug_sessions/debug_abc123/report.html",
  "issues_found": [
    "Button hover state not implemented",
    "Toolbar alignment off by 2px"
  ]
}
```

**Examples:**

```python
# End session with report
result = await end_debug_session(
    session_id="debug_abc123",
    generate_report=True
)
print(f"Report: {result['report_path']}")
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

### `aerospace://displays`

Complete display configuration information.

**URI:** `aerospace://displays`

**Response:**

```json
{
  "displays": [
    {
      "id": 1,
      "name": "Built-in Retina Display",
      "resolution": {"width": 2560, "height": 1600},
      "scale_factor": 2.0,
      "effective_resolution": {"width": 1280, "height": 800},
      "size_inches": 14.2,
      "is_primary": true,
      "is_builtin": true,
      "position": {"x": 0, "y": 0},
      "ppi": 218,
      "workspaces": ["1", "2", "3"]
    },
    {
      "id": 2,
      "name": "DELL U2720Q",
      "resolution": {"width": 3840, "height": 2160},
      "scale_factor": 1.5,
      "effective_resolution": {"width": 2560, "height": 1440},
      "size_inches": 27,
      "is_primary": false,
      "is_builtin": false,
      "position": {"x": 1280, "y": -320},
      "ppi": 163,
      "workspaces": ["dev", "mail"]
    }
  ],
  "arrangement": "horizontal",
  "total_effective_pixels": 5765120,
  "category": "dual_display",
  "category_description": "Two monitors: focus on primary, reference on secondary"
}
```

---

### `aerospace://displays/{display_id}`

Individual display details including assigned workspaces.

**URI Template:** `aerospace://displays/{display_id}`

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `display_id` | integer | The display ID |

**Response:**

```json
{
  "id": 2,
  "name": "DELL U2720Q",
  "resolution": {"width": 3840, "height": 2160},
  "scale_factor": 1.5,
  "effective_resolution": {"width": 2560, "height": 1440},
  "size_inches": 27,
  "is_primary": false,
  "is_builtin": false,
  "position": {"x": 1280, "y": -320},
  "ppi": 163,
  "workspaces": ["dev", "mail"],
  "focused_workspace": "dev",
  "window_count": 4,
  "size_category": "large"
}
```

---

### Phase 2: GUI Debugging Resources

#### `aerospace://window/{window_id}/accessibility`

Full accessibility tree for a window.

**URI Template:** `aerospace://window/{window_id}/accessibility`

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `window_id` | integer | The window ID |

**Response:**

```json
{
  "window_id": 1234,
  "app_name": "MyApp",
  "accessibility_tree": {
    "role": "window",
    "title": "Main Window",
    "bounds": {"x": 0, "y": 0, "width": 800, "height": 600},
    "children": [
      {
        "role": "toolbar",
        "bounds": {"x": 0, "y": 0, "width": 800, "height": 44},
        "children": [
          {"role": "button", "label": "New", "enabled": true},
          {"role": "button", "label": "Open", "enabled": true}
        ]
      }
    ]
  },
  "element_count": 47,
  "captured_at": "2025-01-15T10:30:00Z"
}
```

---

#### `aerospace://window/{window_id}/elements`

Flat list of all accessible elements with bounds.

**URI Template:** `aerospace://window/{window_id}/elements`

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `window_id` | integer | The window ID |

**Response:**

```json
{
  "window_id": 1234,
  "app_name": "MyApp",
  "elements": [
    {
      "path": "window",
      "role": "window",
      "title": "Main Window",
      "bounds": {"x": 0, "y": 0, "width": 800, "height": 600}
    },
    {
      "path": "window/toolbar",
      "role": "toolbar",
      "bounds": {"x": 0, "y": 0, "width": 800, "height": 44}
    },
    {
      "path": "window/toolbar/button[0]",
      "role": "button",
      "label": "New",
      "enabled": true,
      "bounds": {"x": 10, "y": 8, "width": 60, "height": 28}
    },
    {
      "path": "window/toolbar/button[1]",
      "role": "button",
      "label": "Open",
      "enabled": true,
      "bounds": {"x": 80, "y": 8, "width": 60, "height": 28}
    }
  ],
  "total_elements": 47
}
```

---

#### `aerospace://debug/sessions`

List of active and recent debug sessions.

**URI:** `aerospace://debug/sessions`

**Response:**

```json
{
  "active_sessions": [
    {
      "session_id": "debug_abc123",
      "session_name": "button_color_debug",
      "app_name": "MyApp",
      "window_id": 1234,
      "started_at": "2025-01-15T10:30:00Z",
      "snapshot_count": 3
    }
  ],
  "recent_sessions": [
    {
      "session_id": "debug_xyz789",
      "session_name": "layout_fix",
      "app_name": "OtherApp",
      "started_at": "2025-01-14T15:00:00Z",
      "ended_at": "2025-01-14T16:30:00Z",
      "snapshot_count": 8,
      "report_path": "/tmp/debug_sessions/debug_xyz789/report.html"
    }
  ]
}
```

---

#### `aerospace://debug/session/{session_id}`

Details of a specific debug session.

**URI Template:** `aerospace://debug/session/{session_id}`

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `session_id` | string | The debug session ID |

**Response:**

```json
{
  "session_id": "debug_abc123",
  "session_name": "button_color_debug",
  "app_name": "MyApp",
  "window_id": 1234,
  "started_at": "2025-01-15T10:30:00Z",
  "status": "active",
  "baseline": {
    "screenshot": "/tmp/debug_sessions/debug_abc123/baseline.png",
    "accessibility_tree": "/tmp/debug_sessions/debug_abc123/baseline_tree.json"
  },
  "snapshots": [
    {
      "id": "snap_001",
      "label": "after_css_fix",
      "timestamp": "2025-01-15T10:35:00Z",
      "file_path": "/tmp/debug_sessions/debug_abc123/snap_001.png",
      "note": "Changed button color",
      "difference_percentage": 1.2
    }
  ],
  "issues_identified": [
    "Button hover state missing",
    "Alignment issue in toolbar"
  ]
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

### `smart_focus`

Display-aware focus mode that adapts window arrangement based on display configuration.

**Description:** "Display-aware focus mode that adapts window arrangement based on display configuration (single small/medium/large display, dual display, triple+ displays). Makes the focused window prominent while keeping reference windows accessible, using different strategies per display category. Supports presets, undo, and batch operations."

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `strategy` | string | No | Strategy: `auto`, `maximize`, `balanced`, `minimal` (default: `auto`) |
| `keep_visible` | string[] | No | Apps to keep visible (comma-separated) |
| `reference_monitor` | string | No | Which monitor for reference windows |
| `save_as` | string | No | Save this arrangement as a named preset |
| `undo` | boolean | No | Restore previous arrangement |

**Display Category Strategies:**

| Category | Strategy |
|----------|----------|
| `small_single` (≤15") | Focus fullscreen, others to adjacent workspace |
| `medium_single` (15-24") | 70/30 split with sidebar |
| `large_single` (≥27") | 60% centered focus, flanking reference |
| `dual_display` | Focus fullscreen on primary, reference tiled on secondary |
| `triple_plus` | Dedicated monitors: primary=focus, secondary=reference, tertiary=communication |

**Example Interaction:**

```
User: /smart_focus

Assistant: I'll help you focus. First, let me analyze your display configuration...

**Display Configuration Detected:**
- Category: `dual_display`
- Primary: Built-in Retina Display (14", 1280x800 effective)
- Secondary: DELL U2720Q (27", 2560x1440 effective)
- Recommended strategy: Focus on primary, reference on secondary

**Current Windows:**
- VS Code: "project - Visual Studio Code" [FOCUSED] - Primary monitor
- Terminal: "zsh" - Primary monitor
- Chrome: "Documentation" - Secondary monitor
- Slack: "General" - Secondary monitor
- Notes: "Meeting Notes" - Secondary monitor

**Applying dual_display focus strategy:**

Actions taken:
1. Captured current layout (saved for undo)
2. VS Code → fullscreen on primary monitor
3. Terminal, Chrome, Notes → tiled on secondary monitor
4. Slack → moved to "communication" workspace

Your smart focus is ready:
- Primary monitor: VS Code (fullscreen focus)
- Secondary monitor: Reference windows (Terminal, Chrome, Notes)
- Communication apps isolated on separate workspace

Use `/smart_focus --undo` to restore previous layout.
Would you like to save this as a preset? Use `--save-as "coding"`
```

**Prompt Template:**

```
Display-aware focus mode that adapts to the user's monitor configuration.

Decision Flow:
1. Query aerospace://displays to determine display category
2. Query aerospace://focused to identify the focus target window
3. Query aerospace://windows to inventory all windows
4. Categorize windows: focus, reference, communication, other
5. Select and apply strategy based on display category:

   - small_single: Focus fullscreen, others to adjacent workspace
   - medium_single: 70/30 split, reference in sidebar accordion
   - large_single: 60% centered, reference flanking both sides
   - dual_display: Focus fullscreen on primary, reference tiled on secondary
   - triple_plus: Focus=primary, reference=secondary, communication=tertiary

6. Use batch operations for smooth transitions
7. Capture final state for confirmation
8. Offer to save as preset

Tools used: get_display_category, apply_focus_preset, set_window_zone,
move_app_category_to_monitor, capture_workspace
```

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

Debug the GUI of an application by comparing expected vs actual screen appearance. (Phase 2: Enhanced with accessibility inspection, visual diff, element state comparison, and debug sessions)

**Description:** "Debug the GUI of an app under development by comparing what is expected vs what is actually on screen, using the capture tool functionality"

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `app_name` | string | No | The app to debug (defaults to focused window's app) |
| `mode` | string | No | Debug mode: `visual`, `structural`, `interactive`, `full` (Phase 2) |
| `baseline` | string | No | Path to baseline image OR session ID to compare against (Phase 2) |
| `element_focus` | string | No | Specific element to focus debugging on (Phase 2) |
| `auto_capture` | boolean | No | Automatically capture after each code change (Phase 2) |

**Example Interaction (Phase 1 - Basic):**

```
User: /debug_app_gui app_name="MyApp"
Assistant: I'll help you debug the GUI of MyApp. Let me capture the current state...

Captured MyApp window (window_id: 4521):
- Title: "MyApp - Main Window"
- Dimensions: 1200x800
- Screenshot saved to: /tmp/myapp_capture.png

What would you like to compare against?

1. Provide a reference screenshot path
2. Describe what you expect to see
3. I can analyze the current UI for common issues

User: The button in the top-right should be blue, not gray
Assistant: Let me analyze the captured screenshot...

Analysis of MyApp GUI:
- Found button in top-right region at coordinates (1150, 50)
- Current color appears to be #808080 (gray)
- You expected: blue

Possible causes:
1. Button state might be "disabled" - check if it's enabled in code
2. CSS/style not being applied - verify stylesheet is loaded
3. Theme override - check if dark mode or system theme is affecting it

Would you like me to capture again after you make changes to compare?
```

**Example Interaction (Phase 2 - Full Debug):**

```
User: /debug_app_gui app_name="MyApp" mode="full"
Assistant: I'll help you debug MyApp's GUI. Starting a full debug session...

[Starting debug session: debug_myapp_001]

**1. Baseline Capture**
- Window: "MyApp - Main Window" (ID: 4521)
- Dimensions: 1200x800
- Screenshot: /tmp/debug_sessions/debug_myapp_001/baseline.png

**2. Accessibility Tree Analysis**
Found 47 UI elements:
- 1 window
- 2 toolbars (24 buttons)
- 1 sidebar (list with 8 items)
- 1 main content area (scroll view)
- 12 labels, 6 text fields

**3. Visual Analysis**
Scanning for common issues...
- [✓] Color contrast: PASS
- [✓] Element overlap: PASS
- [!] Alignment issue: Toolbar button "Export" appears 2px lower than siblings
- [✓] Text truncation: PASS

**4. Interactive Element Audit**
Testing hover/click states on all 30 buttons...
- [!] Button "Submit" (window/form/button[0]): Shows no visual feedback on hover
- [✓] All other buttons: Visual feedback OK

**Summary of Issues Found:**
1. Toolbar alignment: "Export" button misaligned by 2px
2. Missing hover state: "Submit" button has no hover effect

Would you like me to:
1. Capture detailed screenshots of these issues?
2. Show the accessibility properties for the problematic elements?
3. Generate a diff after you make changes?

User: Show me the Submit button issue
Assistant: Let me capture and analyze the Submit button...

**Element Details: Submit Button**
- Path: window/form/button[0]
- Bounds: x=300, y=500, width=100, height=40
- Label: "Submit"
- Enabled: true
- Focused: false

**State Captures:**
1. Normal state: /tmp/debug_sessions/debug_myapp_001/submit_normal.png
2. Hover state: /tmp/debug_sessions/debug_myapp_001/submit_hover.png

**Visual Comparison:**
Comparing normal vs hover states...
- Difference: 0.0% (identical)
- Issue confirmed: No visual change on hover

The button has no hover style defined. Make your changes and say "check again" to recapture.
```

**Prompt Template:**

```
Help debug GUI issues by capturing and analyzing window screenshots.

Phase 1 Steps:
1. Use capture_window to capture the app's current appearance
2. If a reference image is provided, compare visually
3. If description is provided, analyze the capture for discrepancies
4. Suggest possible causes for visual differences
5. Offer to recapture after changes for comparison

Phase 2 Steps (Enhanced):
1. Start a debug session with start_debug_session
2. Capture baseline screenshot and accessibility tree
3. Based on mode:
   - visual: Use compare_screenshots to generate visual diffs
   - structural: Use get_accessibility_tree and compare_element_state
   - interactive: Use trigger_ui_state to test hover/click/focus states
   - full: Run all analyses
4. Use find_element and get_element_properties for element inspection
5. Use capture_element for focused element screenshots
6. Use capture_debug_snapshot to track changes during iteration
7. Generate report with end_debug_session

Tools used: capture_window, capture_element, capture_sequence, get_accessibility_tree,
find_element, get_element_properties, compare_screenshots, compare_element_state,
simulate_click, trigger_ui_state, start_debug_session, capture_debug_snapshot
```

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
| `CAPTURE_FAILED` | Screenshot capture failed | Check screencapture permissions in System Settings |

### Phase 2 Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `ACCESSIBILITY_NOT_ENABLED` | Accessibility API access denied | Grant accessibility permissions in System Settings > Privacy & Security |
| `ELEMENT_NOT_FOUND` | UI element matching query not found | Verify element exists with `get_accessibility_tree` |
| `INVALID_ELEMENT_PATH` | Element path is malformed or invalid | Use format: `window/container/element[index]` |
| `SESSION_NOT_FOUND` | Debug session ID not found | Check active sessions with `aerospace://debug/sessions` |
| `SESSION_EXPIRED` | Debug session has expired or ended | Start a new session with `start_debug_session` |
| `COMPARISON_FAILED` | Screenshot comparison failed | Verify both images exist and have valid formats |
| `DIMENSIONS_MISMATCH` | Images have different dimensions | Ensure baseline and actual images are same size |
| `INTERACTION_FAILED` | Click/input simulation failed | Verify element is visible, enabled, and accessible |
| `INVALID_REGION` | Capture region is invalid or out of bounds | Check region coordinates against window bounds |
| `SEQUENCE_CAPTURE_TIMEOUT` | Animation capture exceeded timeout | Reduce frame count or increase interval |

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

**Capture Failed:**
```json
{
  "success": false,
  "error": {
    "code": "CAPTURE_FAILED",
    "message": "Failed to capture window screenshot",
    "details": {
      "window_id": 1234,
      "reason": "Screen recording permission not granted",
      "suggestion": "Grant screen recording permission in System Settings > Privacy & Security"
    }
  }
}
```
