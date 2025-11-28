# Integration Tests for AeroSpace MCP Server

This document provides a guide for manual integration testing of the AeroSpace MCP Server. These tests require a macOS system with AeroSpace window manager installed and running.

## Prerequisites

1. **macOS with AeroSpace installed**
   - Install AeroSpace: https://nikitabobko.github.io/AeroSpace/
   - Ensure AeroSpace is running (`aerospace` command available in terminal)

2. **MCP Server installed**
   ```bash
   cd win-ctrl-mcp
   uv sync
   ```

3. **Claude Desktop or Claude Code configured**
   - Add the MCP server to your configuration (see CLAUDE.md for details)

## Test Environment Setup

Before testing, open several applications to have multiple windows:
- A web browser (Firefox, Chrome, Safari)
- A code editor (VS Code, Sublime Text)
- Terminal
- A communication app (Slack, Discord, Messages)
- Any other apps you commonly use

Create at least 2-3 workspaces with different windows distributed across them.

---

## Phase 1 Integration Tests

### 1. Window Management Tools

#### 1.1 Focus Window (tool_focus_window)

**Test: Focus by direction**
- Prompt: "Focus the window to the left of my current window"
- Expected: Focus shifts to the window on the left
- Verify: The window that was to the left is now focused

**Test: Focus by window ID**
- First ask: "List all my windows"
- Then ask: "Focus window ID [pick an ID from the list]"
- Expected: That specific window receives focus

**Questions for feedback:**
- Did the focus move correctly?
- Was there any visible lag or jank?

#### 1.2 Focus Monitor (tool_focus_monitor)

**Test: Focus secondary monitor** (requires multiple displays)
- Prompt: "Focus my secondary monitor"
- Expected: Focus moves to a window on the secondary monitor

**Test: Focus by direction**
- Prompt: "Focus the monitor to the right"
- Expected: Focus moves to the monitor on the right

#### 1.3 Focus Workspace (tool_focus_workspace)

**Test: Switch workspace by number**
- Prompt: "Switch to workspace 2"
- Expected: Workspace 2 becomes active

**Test: Switch workspace by name**
- Prompt: "Switch to the dev workspace"
- Expected: The "dev" workspace becomes active (if it exists)

#### 1.4 Move Window (tool_move_window)

**Test: Move to workspace**
- Prompt: "Move this window to workspace 3"
- Expected: Current window moves to workspace 3

**Test: Move to monitor**
- Prompt: "Move this window to my external monitor"
- Expected: Window appears on the external monitor

**Test: Move by direction**
- Prompt: "Move this window to the right"
- Expected: Window position/order changes in the tiling layout

#### 1.5 Resize Window (tool_resize_window)

**Test: Resize width**
- Prompt: "Make this window 100 pixels wider"
- Expected: Window width increases

**Test: Resize by percentage**
- Prompt: "Reduce this window's height by 20%"
- Expected: Window height decreases by ~20%

#### 1.6 Close Window (tool_close_window)

**Test: Close focused window**
- Prompt: "Close this window"
- Expected: The currently focused window closes
- Warning: Test with a window you can afford to close!

#### 1.7 Fullscreen Toggle (tool_fullscreen_toggle)

**Test: Enter fullscreen**
- Prompt: "Make this window fullscreen"
- Expected: Window fills the workspace

**Test: Exit fullscreen**
- Prompt: "Exit fullscreen mode"
- Expected: Window returns to tiled state

#### 1.8 Minimize Window (tool_minimize_window)

**Test: Minimize window**
- Prompt: "Minimize this window"
- Expected: Window minimizes to the dock

---

### 2. Layout Management Tools

#### 2.1 Set Layout (tool_set_layout)

**Test: Switch to horizontal tiles**
- Prompt: "Change to horizontal tiles layout"
- Expected: Windows arrange horizontally

**Test: Switch to accordion**
- Prompt: "Change layout to accordion mode"
- Expected: Windows stack with tabs

#### 2.2 Split Window (tool_split_window)

**Test: Split horizontally**
- Prompt: "Split this container horizontally"
- Expected: New windows will appear horizontally next to this one

#### 2.3 Flatten Workspace (tool_flatten_workspace)

**Test: Flatten nested containers**
- Prompt: "Flatten my current workspace"
- Expected: Nested containers are removed, windows are direct children

#### 2.4 Balance Sizes (tool_balance_sizes)

**Test: Balance all windows**
- Prompt: "Balance the window sizes in this workspace"
- Expected: All windows become equal size

---

### 3. Capture Tools

#### 3.1 Capture Window (tool_capture_window)

**Test: Capture current window**
- Prompt: "Take a screenshot of this window"
- Expected: Screenshot is saved, path is returned
- Verify: Image file exists and shows the correct window

**Test: Capture with custom format**
- Prompt: "Capture this window as a JPEG"
- Expected: Screenshot saved in JPEG format

#### 3.2 Capture Workspace (tool_capture_workspace)

**Test: Capture entire workspace**
- Prompt: "Take a screenshot of my current workspace"
- Expected: Screenshot includes the entire workspace/monitor

---

### 4. Display Information Tools

#### 4.1 Get Display Info (tool_get_display_info)

**Test: Query displays**
- Prompt: "Tell me about my connected displays"
- Expected: Returns resolution, scale factor, size info for each display

#### 4.2 Get Display Category (tool_get_display_category)

**Test: Get display category**
- Prompt: "What's my display category?"
- Expected: Returns category (small_single, medium_single, large_single, dual_display, or triple_plus) with strategy recommendations

---

### 5. Smart Focus Tools

#### 5.1 Apply Focus Preset (tool_apply_focus_preset)

**Test: Auto focus preset**
- Prompt: "Apply the auto focus preset"
- Expected: Windows rearrange based on display category

**Test: Named preset**
- Prompt: "Apply the dual_monitor_focus preset"
- Expected: Windows arrange for dual monitor workflow

#### 5.2 Save Focus Preset (tool_save_focus_preset)

**Test: Save current arrangement**
- Prompt: "Save my current window arrangement as 'coding_session'"
- Expected: Preset is saved with that name

#### 5.3 Load Focus Preset (tool_load_focus_preset)

**Test: Load saved preset**
- Prompt: "Load my 'coding_session' preset"
- Expected: Windows restore to saved arrangement

#### 5.4 Resize Window Optimal (tool_resize_window_optimal)

**Test: Optimal size for code editor**
- Prompt: "Resize this code editor to optimal size"
- Expected: Window resizes to recommended dimensions for code

#### 5.5 Set Window Zone (tool_set_window_zone)

**Test: Center focus zone**
- Prompt: "Put this window in the center focus zone"
- Expected: Window moves to center of screen with appropriate size

#### 5.6 Move App Category to Monitor (tool_move_app_category_to_monitor)

**Test: Move communication apps**
- Prompt: "Move all my communication apps to the secondary monitor"
- Expected: Slack, Discord, Messages, etc. move to secondary monitor

---

### 6. Resources

#### 6.1 Windows Resource (aerospace://windows)

**Test: List all windows**
- Prompt: "Show me all my open windows"
- Expected: Returns list with window IDs, app names, titles, workspaces

#### 6.2 Workspaces Resource (aerospace://workspaces)

**Test: List workspaces**
- Prompt: "What workspaces do I have?"
- Expected: Returns all workspaces with window counts

#### 6.3 Focused Resource (aerospace://focused)

**Test: Get focused info**
- Prompt: "What window/workspace am I focused on?"
- Expected: Returns current focus state

#### 6.4 Displays Resource (aerospace://displays)

**Test: Get display config**
- Prompt: "Show me my display configuration"
- Expected: Returns complete display information with workspace assignments

---

### 7. Prompts

#### 7.1 Organize Windows (prompt_organize_windows)

**Test: Organization assistance**
- Use prompt: "Help me organize my windows"
- Expected: AI analyzes open windows and suggests organization strategy
- Verify: AI asks for confirmation before making changes

#### 7.2 Smart Focus (prompt_smart_focus)

**Test: Focus mode setup**
- Use prompt: "Set up focus mode for coding"
- Expected: AI detects display config, suggests appropriate arrangement

#### 7.3 Presentation Layout (prompt_presentation_layout)

**Test: Presentation setup**
- Use prompt: "Set up for a presentation"
- Expected: AI identifies presentation-ready apps, suggests layout

#### 7.4 Debug App GUI (prompt_debug_app_gui)

**Test: GUI debugging assistance**
- Use prompt: "Help me debug the GUI of my app"
- Expected: AI captures window and offers to analyze visual state

---

## Feedback Questions

After completing the integration tests, please provide feedback on:

### Functionality
1. Did all tools execute successfully?
2. Were there any commands that failed or produced unexpected results?
3. Were error messages clear and helpful when things went wrong?

### User Experience
4. Was the response time acceptable for each operation?
5. Were the return values informative and useful?
6. Did the AI provide good context when using prompts?

### Display Configuration
7. What display setup did you test with?
   - Single display (what size?)
   - Dual displays
   - Triple+ displays
8. Did display detection work correctly?
9. Were the recommended strategies appropriate for your setup?

### Edge Cases
10. Did you encounter any crashes or hung operations?
11. Were there scenarios where AeroSpace reported an error?
12. Any windows/apps that didn't work well with the tools?

### Missing Features
13. What features would you want that aren't included in Phase 1?
14. Any improvements to existing tools you'd suggest?

---

## Reporting Issues

If you encounter issues during testing:

1. Note the exact prompt/command used
2. Capture any error messages returned
3. Check AeroSpace CLI directly: `aerospace list-windows --json`
4. Check server logs if running in debug mode: `MCP_DEBUG=1 uv run win-ctrl-mcp`

Report issues at: https://github.com/huegli/win-ctrl-mcp/issues

---

## Test Checklist

Use this checklist to track your testing progress:

### Window Management
- [ ] Focus window by direction
- [ ] Focus window by ID
- [ ] Focus monitor
- [ ] Focus workspace
- [ ] Move window to workspace
- [ ] Move window to monitor
- [ ] Move window by direction
- [ ] Resize window (pixels)
- [ ] Resize window (percentage)
- [ ] Close window
- [ ] Fullscreen toggle on
- [ ] Fullscreen toggle off
- [ ] Minimize window

### Layout Management
- [ ] Set layout (tiles)
- [ ] Set layout (accordion)
- [ ] Split window (horizontal)
- [ ] Split window (vertical)
- [ ] Flatten workspace
- [ ] Balance sizes

### Capture
- [ ] Capture window (PNG)
- [ ] Capture window (JPG)
- [ ] Capture workspace

### Display Info
- [ ] Get display info
- [ ] Get display category

### Smart Focus
- [ ] Apply focus preset (auto)
- [ ] Apply focus preset (specific)
- [ ] Save focus preset
- [ ] Load focus preset
- [ ] Resize window optimal
- [ ] Set window zone
- [ ] Move app category to monitor

### Resources
- [ ] aerospace://windows
- [ ] aerospace://windows/{id}
- [ ] aerospace://workspaces
- [ ] aerospace://workspaces/{name}
- [ ] aerospace://monitors
- [ ] aerospace://tree
- [ ] aerospace://focused
- [ ] aerospace://displays
- [ ] aerospace://displays/{id}

### Prompts
- [ ] organize_windows
- [ ] smart_focus
- [ ] presentation_layout
- [ ] debug_app_gui
