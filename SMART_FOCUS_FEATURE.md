# Smart Focus Mode: Display-Aware Window Arrangement

This document explores enhancements to the `/focus_mode` prompt that would make it adaptive to different display configurations, from single small laptop screens to multi-monitor setups.

---

## The Problem

The current `focus_mode` implementation treats all setups equally, but user needs vary dramatically based on:

1. **Screen real estate** - A 13" laptop has ~2.3M pixels; a 32" 4K monitor has ~8.3M pixels
2. **Number of displays** - Single monitor users need different strategies than those with 2-3+ monitors
3. **Display arrangement** - Horizontal vs vertical stacking, primary monitor position
4. **Context switching cost** - On small screens, switching workspaces is cheap; on large multi-monitor setups, spatial arrangement matters more

---

## Display Configuration Categories

### Category 1: Small Single Display (≤15", ≤1920x1080)
**Examples:** MacBook Air 13", older laptops

**Constraints:**
- Limited pixels make side-by-side arrangements cramped
- Every pixel counts for the focused app
- Context switching via workspaces is preferable to splitting

**Ideal Focus Strategy:**
- Focused window goes fullscreen or near-fullscreen (95%+)
- Secondary windows move to adjacent workspace (not hidden, just out of view)
- Quick workspace switching becomes the primary navigation method
- Accordion layout for any remaining visible windows

### Category 2: Medium Single Display (15-24", 1920x1080 to 2560x1440)
**Examples:** MacBook Pro 16", standard external monitor

**Constraints:**
- Enough space for focused + one sidebar
- Side-by-side is viable but still limited

**Ideal Focus Strategy:**
- Focused window takes 70-80% of screen
- One secondary window in remaining 20-30% (vertical strip)
- Other windows in accordion behind the secondary
- Or: focused window fullscreen with floating mini-windows for quick reference

### Category 3: Large Single Display (≥27", ≥2560x1440)
**Examples:** 27" 4K, ultrawide monitors

**Constraints:**
- Abundant space, but too-wide windows become hard to read
- Sweet spot for main window is often 60-70% width, not 100%

**Ideal Focus Strategy:**
- Focused window centered at optimal reading width (80-120 characters for code)
- Secondary windows flanking on sides
- Consider "zones" - focus zone center, reference zone sides
- Ultrawide: could support three-column layout with focus in center

### Category 4: Dual Display
**Examples:** Laptop + external monitor, two matched monitors

**Constraints:**
- Primary/secondary monitor roles matter
- Cross-monitor window movement is expensive cognitively

**Ideal Focus Strategy:**
- Focused window fullscreen on primary monitor
- All secondary/reference windows on secondary monitor
- Secondary monitor uses tiled layout for quick scanning
- Never split focus window across monitors

### Category 5: Triple+ Display
**Examples:** Developer workstations, trading setups

**Constraints:**
- Too much space can be distracting
- Need clear purpose for each monitor

**Ideal Focus Strategy:**
- Primary: focused window only
- Secondary: directly related windows (terminal for code, docs for writing)
- Tertiary: monitoring/communication (Slack, email, dashboards)
- Consider dimming/reducing unfocused monitors

---

## Additional Tools Needed

### Display Information Tools

#### `get_display_info`
Returns detailed information about all connected displays.

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

**Why needed:** Focus mode must know screen sizes and arrangement to make intelligent decisions.

#### `get_display_category`
Simplified tool that returns the display configuration category.

```json
{
  "category": "dual_display",
  "primary_size": "medium",
  "secondary_sizes": ["large"],
  "recommended_strategy": "primary_focus_secondary_reference"
}
```

**Why needed:** Quick categorization for prompt decision-making without parsing raw display data.

### Layout Preset Tools

#### `apply_focus_preset`
Apply a predefined focus layout based on display category.

```python
await apply_focus_preset(
    preset="dual_monitor_focus",
    focus_window_id=1234,
    options={
        "reference_apps": ["Terminal", "Chrome"],
        "hide_communication": True
    }
)
```

**Why needed:** Encapsulates complex multi-step layouts into atomic operations.

#### `save_focus_preset` / `load_focus_preset`
Allow users to save their preferred focus arrangements.

```python
await save_focus_preset(
    name="coding_focus",
    description="VS Code focused, terminal on side"
)

await load_focus_preset(name="coding_focus")
```

**Why needed:** User preferences vary; learning their preferred arrangements improves UX.

### Window Sizing Tools

#### `resize_window_optimal`
Resize window to optimal dimensions for its content type.

```python
await resize_window_optimal(
    window_id=1234,
    content_type="code_editor",  # or "browser", "terminal", "document"
    constraints={
        "max_width_percent": 70,
        "min_width_percent": 50
    }
)
```

**Why needed:** Different apps have different optimal widths (code editors ~120 chars, documents ~80 chars).

#### `set_window_zone`
Position window in a named zone rather than explicit coordinates.

```python
await set_window_zone(
    window_id=1234,
    zone="center_focus",  # or "left_reference", "right_reference", "floating_pip"
    monitor="primary"
)
```

**Why needed:** Abstracts positioning to intent rather than pixels.

### Monitor-Aware Tools

#### `dim_unfocused_monitors`
Reduce brightness/saturation of non-primary monitors to reduce distraction.

```python
await dim_unfocused_monitors(
    focus_monitor=1,
    dim_level=0.7  # 70% brightness
)
```

**Why needed:** On multi-monitor setups, peripheral displays can distract.

#### `move_app_category_to_monitor`
Move all windows of a category to a specific monitor.

```python
await move_app_category_to_monitor(
    category="communication",  # predefined: communication, development, reference, media
    monitor=3
)
```

**Why needed:** Bulk organization by app purpose rather than individual windows.

---

## Additional Resources Needed

### `aerospace://displays`
Complete display configuration information.

```json
{
  "displays": [...],
  "arrangement": "horizontal",
  "total_workspace_area": {...}
}
```

### `aerospace://displays/{display_id}`
Individual display details including assigned workspaces.

### `aerospace://optimal_layouts`
Suggested layouts based on current display configuration and window count.

```json
{
  "current_config": "dual_display",
  "window_count": 5,
  "suggested_layouts": [
    {
      "name": "focus_primary_reference_secondary",
      "description": "Main window on primary, others tiled on secondary",
      "preview_ascii": "[ FOCUS ]  [ref1][ref2]\n           [ref3][ref4]"
    },
    {
      "name": "split_focus_with_terminal",
      "description": "70/30 split on primary, communication on secondary",
      "preview_ascii": "[ FOCUS ][term] [slack][mail]"
    }
  ]
}
```

---

## Enhanced Focus Mode Prompt Design

### Input Parameters

```
/focus_mode [options]

Options:
  --strategy     auto|maximize|balanced|minimal
  --keep-visible <app_names>  Apps to keep visible (comma-separated)
  --reference-monitor <id>    Which monitor for reference windows
  --dim-others               Dim unfocused monitors
  --save-as <name>           Save this arrangement as preset
```

### Decision Flow

```
1. Query aerospace://displays to determine configuration category
2. Query aerospace://focused to identify focus target
3. Query aerospace://windows to inventory all windows

4. Categorize windows:
   - Focus: the target window
   - Reference: directly related (same project, documentation)
   - Communication: Slack, Mail, Messages
   - Other: everything else

5. Select strategy based on display category:

   IF small_single_display:
     - Focus window → fullscreen
     - Reference → next workspace (accordion)
     - Communication → workspace 3
     - Capture screenshot for user reference

   ELIF medium_single_display:
     - Focus window → 75% width
     - Top reference → 25% width sidebar
     - Others → accordion behind sidebar
     - Communication → separate workspace

   ELIF large_single_display:
     - Focus window → 60% centered
     - Reference → 20% each side
     - Communication → floating mini-windows or separate workspace

   ELIF dual_display:
     - Focus window → fullscreen on primary
     - Reference → tiled on secondary
     - Communication → corner of secondary or hidden
     - Optional: dim secondary

   ELIF triple_plus_display:
     - Focus window → primary monitor
     - Reference → secondary monitor
     - Communication → tertiary monitor
     - Dim tertiary unless communication is active

6. Execute layout changes
7. Capture final state for confirmation
8. Offer to save as preset
```

---

## User Experience Considerations

### Learning User Preferences

Over time, the system could learn:
- Which apps the user typically keeps visible during focus
- Preferred window sizes for specific applications
- Whether they prefer workspace switching or spatial arrangement
- Time-of-day patterns (morning: communication visible, afternoon: focus mode)

### Graceful Degradation

If display configuration changes (laptop undocked):
- Saved presets should adapt, not break
- "Dual monitor focus" preset on single monitor → maximize focus, move reference to adjacent workspace

### Quick Escape

Focus mode should be easily reversible:
- `/focus_mode --undo` restores previous arrangement
- Or: automatic snapshot before changes

### Preview Before Apply

For complex rearrangements:
- Show ASCII art preview of proposed layout
- Ask for confirmation before moving windows
- Capture before/after screenshots

---

## Implementation Phases

### Phase 1: Display Awareness
- Add `get_display_info` tool
- Add `aerospace://displays` resource
- Update focus_mode to detect and log display category

### Phase 2: Category-Specific Strategies
- Implement distinct strategies for each display category
- Test on various configurations

### Phase 3: User Customization
- Add preset save/load functionality
- Remember user preferences

### Phase 4: Advanced Features
- Monitor dimming
- App category bulk moves
- Learning/adaptation

---

## Open Questions

1. **How to handle ultrawide monitors?** They're a single display but behave more like dual. Should we detect aspect ratio and treat 21:9+ as "virtual dual"?

2. **What about virtual desktops/Spaces?** macOS Spaces add another dimension. Should focus mode consider moving windows to different Spaces?

3. **Performance during rearrangement** - Moving many windows can be visually jarring. Should we batch changes or use animation?

4. **Conflict with user's AeroSpace config** - User may have per-app rules in aerospace.toml. How do we respect those while implementing focus mode?

5. **Multi-user scenarios** - If the Mac is shared (unlikely but possible), should presets be per-user?

---

## Related Reading

- [AeroSpace Configuration Guide](https://nikitabobko.github.io/AeroSpace/config)
- Research on optimal code editor widths (80-120 characters)
- Studies on multi-monitor productivity (tl;dr: more monitors help for reference tasks, not focus tasks)
