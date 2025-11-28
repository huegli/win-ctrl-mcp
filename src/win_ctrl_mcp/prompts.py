"""MCP Prompts for AeroSpace.

This module provides pre-configured prompts for common window management tasks.
"""

# Prompt templates for MCP server

ORGANIZE_WINDOWS_PROMPT = """You have access to window management tools. Your task is to help organize the user's windows efficiently.

First, use the aerospace://windows resource to list all open windows. Then analyze the applications and suggest an efficient organization based on the user's workflow.

Consider grouping by:
- Development tools (editors, terminals, documentation)
- Communication (email, chat, video)
- Reference materials (browsers, notes)
- Media and entertainment

Strategy options:
- by_app: Group windows by application type
- by_task: Group windows by inferred task/project
- minimal: Minimize visible windows, focus on current task

After suggesting a reorganization plan, ask for confirmation before making changes.

When ready to execute, use the move_window and set_layout tools to reorganize windows.

Available tools:
- focus_window: Focus a specific window
- move_window: Move windows between workspaces/monitors
- set_layout: Change layout mode (tiles, accordion, etc.)
- focus_workspace: Switch to a workspace

Remember: Ask for confirmation before making changes, and explain your reasoning.
"""

SMART_FOCUS_PROMPT = """Display-aware focus mode that adapts to the user's monitor configuration.

Your task is to create a focused workspace arrangement that maximizes productivity based on the display setup.

Decision Flow:
1. Query aerospace://displays to determine display category
2. Query aerospace://focused to identify the focus target window
3. Query aerospace://windows to inventory all windows
4. Categorize windows: focus, reference, communication, other
5. Select and apply strategy based on display category:

   - small_single (≤15"): Focus fullscreen, others to adjacent workspace
   - medium_single (15-24"): 70/30 split, reference in sidebar accordion
   - large_single (≥27"): 60% centered focus, reference flanking both sides
   - dual_display: Focus fullscreen on primary, reference tiled on secondary
   - triple_plus: Focus=primary, reference=secondary, communication=tertiary

6. Use batch operations for smooth transitions
7. Capture final state for confirmation
8. Offer to save as preset

Arguments you might receive:
- strategy: auto, maximize, balanced, minimal (default: auto)
- keep_visible: Apps to keep visible (comma-separated)
- reference_monitor: Which monitor for reference windows
- save_as: Save this arrangement as a named preset
- undo: Restore previous arrangement

Available tools:
- get_display_category: Get display configuration
- apply_focus_preset: Apply a focus layout
- set_window_zone: Position window in named zone
- move_app_category_to_monitor: Move app category to monitor
- save_focus_preset: Save current arrangement
- capture_workspace: Capture screenshot of result

Always explain what display category was detected and what strategy is being applied.
Offer to save the arrangement as a preset for future use.
"""

PRESENTATION_LAYOUT_PROMPT = """Arrange windows for a presentation or screen sharing session.

Your task is to set up an optimal window arrangement for presenting.

Process:
1. Query aerospace://windows to see what's available
2. Identify presentation-ready apps (slides, demos, browsers)
3. Set up the layout:
   - Main presentation app fullscreen on primary monitor
   - Move distracting apps (chat, email) to secondary monitor or hide
   - Keep presenter notes accessible but not visible to audience
   - Minimize notification-heavy apps

Arguments you might receive:
- presenter_app: The main app to present (auto-detect if not specified)
- notes_app: App for presenter notes (optional)

Available tools:
- focus_window: Focus the presenter window
- fullscreen_toggle: Make presentation fullscreen
- move_window: Move windows to other workspaces/monitors
- minimize_window: Hide distracting windows

Considerations:
- Ask which app they want to present if multiple candidates exist
- Warn about apps that might show notifications
- Suggest keeping terminal accessible for demos
- Offer to restore previous layout after presentation

Always confirm the setup with the user before screen sharing begins.
"""

DEBUG_APP_GUI_PROMPT = """Debug the GUI of an application by capturing and comparing visual state.

Your task is to help debug GUI issues by:
1. Capturing the current state of the application
2. Comparing against expected appearance (if reference provided)
3. Identifying visual discrepancies
4. Suggesting possible causes

Process:
1. Use capture_window to capture the app's current appearance
2. If a reference image is provided, compare visually
3. If description is provided, analyze the capture for discrepancies
4. Suggest possible causes for visual differences
5. Offer to recapture after changes for comparison

Arguments you might receive:
- app_name: The app to debug (defaults to focused window's app)
- baseline: Path to baseline/expected image
- mode: Debug mode (visual, structural, interactive, full) - Phase 2

Available tools (Phase 1):
- capture_window: Capture screenshot of a window
- capture_workspace: Capture entire workspace

For visual debugging, help the user by:
- Describing what you observe in the capture
- Asking clarifying questions about expected appearance
- Suggesting common causes (disabled states, theme issues, style problems)
- Offering to capture again after they make changes

Remember: Be systematic in your analysis and offer to iterate on the debugging process.
"""

# Prompt metadata for registration
PROMPTS = {
    "organize_windows": {
        "description": "Help me organize my current windows efficiently based on the apps I have open",
        "template": ORGANIZE_WINDOWS_PROMPT,
        "arguments": [
            {
                "name": "strategy",
                "description": "Organization strategy: by_app, by_task, minimal",
                "required": False,
            }
        ],
    },
    "smart_focus": {
        "description": "Display-aware focus mode that adapts window arrangement based on display configuration",
        "template": SMART_FOCUS_PROMPT,
        "arguments": [
            {
                "name": "strategy",
                "description": "Strategy: auto, maximize, balanced, minimal (default: auto)",
                "required": False,
            },
            {
                "name": "keep_visible",
                "description": "Apps to keep visible (comma-separated)",
                "required": False,
            },
            {
                "name": "reference_monitor",
                "description": "Which monitor for reference windows",
                "required": False,
            },
            {
                "name": "save_as",
                "description": "Save this arrangement as a named preset",
                "required": False,
            },
            {
                "name": "undo",
                "description": "Restore previous arrangement",
                "required": False,
            },
        ],
    },
    "presentation_layout": {
        "description": "Arrange my windows for a presentation or screen sharing session",
        "template": PRESENTATION_LAYOUT_PROMPT,
        "arguments": [
            {
                "name": "presenter_app",
                "description": "The main app to present (defaults to auto-detect)",
                "required": False,
            },
            {
                "name": "notes_app",
                "description": "App for presenter notes (optional)",
                "required": False,
            },
        ],
    },
    "debug_app_gui": {
        "description": "Debug the GUI of an app under development",
        "template": DEBUG_APP_GUI_PROMPT,
        "arguments": [
            {
                "name": "app_name",
                "description": "The app to debug (defaults to focused window's app)",
                "required": False,
            },
            {
                "name": "baseline",
                "description": "Path to baseline/expected image",
                "required": False,
            },
        ],
    },
}
