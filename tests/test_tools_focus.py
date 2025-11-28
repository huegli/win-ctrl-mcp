"""Tests for smart focus tools."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from win_ctrl_mcp.aerospace import AeroSpaceError
from win_ctrl_mcp.tools.focus import (
    _get_app_category,
    apply_focus_preset,
    move_app_category_to_monitor,
    resize_window_optimal,
    save_focus_preset,
    set_window_zone,
)


class TestGetAppCategory:
    """Tests for app category detection."""

    def test_communication_app(self):
        """Test detecting communication apps."""
        assert _get_app_category("Slack") == "communication"
        assert _get_app_category("Discord") == "communication"
        assert _get_app_category("Microsoft Teams") == "communication"

    def test_development_app(self):
        """Test detecting development apps."""
        assert _get_app_category("Visual Studio Code") == "development"
        assert _get_app_category("Terminal") == "development"
        assert _get_app_category("Xcode") == "development"

    def test_reference_app(self):
        """Test detecting reference apps."""
        assert _get_app_category("Safari") == "reference"
        assert _get_app_category("Notes") == "reference"
        assert _get_app_category("Notion") == "reference"

    def test_media_app(self):
        """Test detecting media apps."""
        assert _get_app_category("Spotify") == "media"
        assert _get_app_category("VLC") == "media"

    def test_unknown_app(self):
        """Test that unknown apps return None."""
        assert _get_app_category("SomeRandomApp") is None

    def test_partial_match(self):
        """Test partial name matching."""
        # Should match "Chrome" in "Google Chrome"
        assert _get_app_category("Google Chrome") == "reference"


class TestApplyFocusPreset:
    """Tests for apply_focus_preset tool."""

    @pytest.mark.asyncio
    async def test_apply_auto_preset(self, mock_window_list, mock_monitor_list):
        """Test applying auto preset."""
        with patch(
            "win_ctrl_mcp.tools.focus.get_display_category", new_callable=AsyncMock
        ) as mock_cat:
            mock_cat.return_value = {"category": "medium_single"}

            with patch(
                "win_ctrl_mcp.tools.focus.get_focused_window", new_callable=AsyncMock
            ) as mock_focused:
                mock_focused.return_value = mock_window_list[0]

                with patch(
                    "win_ctrl_mcp.tools.focus.list_windows", new_callable=AsyncMock
                ) as mock_win:
                    mock_win.return_value = mock_window_list

                    with patch(
                        "win_ctrl_mcp.tools.focus.list_monitors", new_callable=AsyncMock
                    ) as mock_mon:
                        mock_mon.return_value = mock_monitor_list

                        with patch(
                            "win_ctrl_mcp.tools.focus.run_aerospace_command",
                            new_callable=AsyncMock,
                        ) as mock_cmd:
                            mock_cmd.return_value = ("", "", 0)

                            result = await apply_focus_preset(preset="auto")

                            assert result["success"] is True
                            assert result["display_category"] == "medium_single"

    @pytest.mark.asyncio
    async def test_apply_preset_no_focused_window(self):
        """Test error when no window is focused."""
        with patch(
            "win_ctrl_mcp.tools.focus.get_display_category", new_callable=AsyncMock
        ) as mock_cat:
            mock_cat.return_value = {"category": "medium_single"}

            with patch(
                "win_ctrl_mcp.tools.focus.get_focused_window", new_callable=AsyncMock
            ) as mock_focused:
                mock_focused.return_value = None

                with pytest.raises(AeroSpaceError) as exc_info:
                    await apply_focus_preset()

                assert "NO_WINDOW_FOCUSED" in exc_info.value.code


class TestSaveFocusPreset:
    """Tests for save_focus_preset tool."""

    @pytest.mark.asyncio
    async def test_save_preset(self, mock_window_list, mock_monitor_list):
        """Test saving a focus preset."""
        with tempfile.TemporaryDirectory() as tmpdir:
            preset_dir = Path(tmpdir)

            with (
                patch("win_ctrl_mcp.tools.focus.PRESET_DIR", preset_dir),
                patch(
                    "win_ctrl_mcp.tools.focus.get_display_category", new_callable=AsyncMock
                ) as mock_cat,
            ):
                mock_cat.return_value = {"category": "medium_single"}

                with patch(
                    "win_ctrl_mcp.tools.focus.list_windows", new_callable=AsyncMock
                ) as mock_win:
                    mock_win.return_value = mock_window_list

                    with patch(
                        "win_ctrl_mcp.tools.focus.list_monitors", new_callable=AsyncMock
                    ) as mock_mon:
                        mock_mon.return_value = mock_monitor_list

                        result = await save_focus_preset(
                            name="test_preset", description="Test description"
                        )

                        assert result["success"] is True
                        assert result["preset"]["name"] == "test_preset"

                        # Verify file was created
                        preset_file = preset_dir / "test_preset.json"
                        assert preset_file.exists()


class TestResizeWindowOptimal:
    """Tests for resize_window_optimal tool."""

    @pytest.mark.asyncio
    async def test_resize_code_editor(self, mock_window_list):
        """Test resizing for code editor."""
        with patch(
            "win_ctrl_mcp.tools.focus.get_focused_window", new_callable=AsyncMock
        ) as mock_focused:
            mock_focused.return_value = mock_window_list[2]  # VS Code

            with patch(
                "win_ctrl_mcp.tools.focus.get_display_info", new_callable=AsyncMock
            ) as mock_display:
                mock_display.return_value = {
                    "displays": [{"effective_resolution": {"width": 1920, "height": 1080}}]
                }

                with patch(
                    "win_ctrl_mcp.tools.focus.run_aerospace_command", new_callable=AsyncMock
                ) as mock_cmd:
                    mock_cmd.return_value = ("", "", 0)

                    result = await resize_window_optimal(content_type="code_editor")

                    assert result["success"] is True
                    assert result["content_type"] == "code_editor"
                    assert "new_dimensions" in result

    @pytest.mark.asyncio
    async def test_resize_invalid_content_type(self, mock_window_list):
        """Test error with invalid content type."""
        with patch(
            "win_ctrl_mcp.tools.focus.get_focused_window", new_callable=AsyncMock
        ) as mock_focused:
            mock_focused.return_value = mock_window_list[0]

            with pytest.raises(AeroSpaceError) as exc_info:
                await resize_window_optimal(content_type="invalid_type")

            assert "Invalid content_type" in str(exc_info.value)


class TestSetWindowZone:
    """Tests for set_window_zone tool."""

    @pytest.mark.asyncio
    async def test_set_center_focus_zone(self, mock_window_list):
        """Test setting center focus zone."""
        with patch(
            "win_ctrl_mcp.tools.focus.get_focused_window", new_callable=AsyncMock
        ) as mock_focused:
            mock_focused.return_value = mock_window_list[0]

            with patch(
                "win_ctrl_mcp.tools.focus.get_display_info", new_callable=AsyncMock
            ) as mock_display:
                mock_display.return_value = {
                    "displays": [{"effective_resolution": {"width": 1920, "height": 1080}}]
                }

                with patch(
                    "win_ctrl_mcp.tools.focus.run_aerospace_command", new_callable=AsyncMock
                ) as mock_cmd:
                    mock_cmd.return_value = ("", "", 0)

                    result = await set_window_zone(zone="center_focus")

                    assert result["success"] is True
                    assert result["zone"] == "center_focus"

    @pytest.mark.asyncio
    async def test_set_invalid_zone(self, mock_window_list):
        """Test error with invalid zone."""
        with patch(
            "win_ctrl_mcp.tools.focus.get_focused_window", new_callable=AsyncMock
        ) as mock_focused:
            mock_focused.return_value = mock_window_list[0]

            with pytest.raises(AeroSpaceError) as exc_info:
                await set_window_zone(zone="invalid_zone")

            assert "Invalid zone" in str(exc_info.value)


class TestMoveAppCategoryToMonitor:
    """Tests for move_app_category_to_monitor tool."""

    @pytest.mark.asyncio
    async def test_move_communication_apps(self, mock_window_list, mock_monitor_list):
        """Test moving communication apps to monitor."""
        # Add a communication app to the mock list
        comm_window = {
            "window-id": 9999,
            "app-name": "Slack",
            "workspace": "1",
        }
        test_windows = mock_window_list + [comm_window]

        with patch("win_ctrl_mcp.tools.focus.list_monitors", new_callable=AsyncMock) as mock_mon:
            mock_mon.return_value = mock_monitor_list

            with patch("win_ctrl_mcp.tools.focus.list_windows", new_callable=AsyncMock) as mock_win:
                mock_win.return_value = test_windows

                with patch(
                    "win_ctrl_mcp.tools.focus.run_aerospace_command", new_callable=AsyncMock
                ) as mock_cmd:
                    mock_cmd.return_value = ("", "", 0)

                    result = await move_app_category_to_monitor(
                        category="communication", monitor="secondary"
                    )

                    assert result["success"] is True
                    assert result["category"] == "communication"
                    assert len(result["windows_moved"]) == 1

    @pytest.mark.asyncio
    async def test_move_invalid_category(self, mock_monitor_list):  # noqa: ARG002
        """Test error with invalid category."""
        with pytest.raises(AeroSpaceError) as exc_info:
            await move_app_category_to_monitor(category="invalid_category", monitor="primary")

        assert "Invalid category" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_move_invalid_layout(self, mock_monitor_list):  # noqa: ARG002
        """Test error with invalid layout."""
        with pytest.raises(AeroSpaceError) as exc_info:
            await move_app_category_to_monitor(
                category="communication", monitor="primary", layout="invalid_layout"
            )

        assert "Invalid layout" in str(exc_info.value)
