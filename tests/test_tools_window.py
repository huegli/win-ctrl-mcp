"""Tests for window management tools."""

from unittest.mock import AsyncMock, patch

import pytest

from win_ctrl_mcp.aerospace import AeroSpaceError
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


class TestFocusWindow:
    """Tests for focus_window tool."""

    @pytest.mark.asyncio
    async def test_focus_by_direction(self, mock_window_list):
        """Test focusing window by direction."""
        with patch(
            "win_ctrl_mcp.tools.window.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.tools.window.get_focused_window", new_callable=AsyncMock
            ) as mock_focused:
                mock_focused.return_value = mock_window_list[0]

                result = await focus_window(direction="left")

                assert result["success"] is True
                assert "focused_window" in result
                mock_cmd.assert_called_once_with("focus", "left")

    @pytest.mark.asyncio
    async def test_focus_by_window_id(self, mock_window_list):
        """Test focusing window by ID."""
        with patch(
            "win_ctrl_mcp.tools.window.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.tools.window.get_window_by_id", new_callable=AsyncMock
            ) as mock_get:
                mock_get.return_value = mock_window_list[0]

                with patch(
                    "win_ctrl_mcp.tools.window.get_focused_window", new_callable=AsyncMock
                ) as mock_focused:
                    mock_focused.return_value = mock_window_list[0]

                    result = await focus_window(window_id=1234)

                    assert result["success"] is True
                    assert result["focused_window"]["window_id"] == 1234

    @pytest.mark.asyncio
    async def test_focus_requires_parameter(self):
        """Test that focus_window requires either direction or window_id."""
        with pytest.raises(AeroSpaceError) as exc_info:
            await focus_window()

        assert "Either 'direction' or 'window_id' must be provided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_focus_rejects_both_parameters(self):
        """Test that focus_window rejects both direction and window_id."""
        with pytest.raises(AeroSpaceError) as exc_info:
            await focus_window(direction="left", window_id=1234)

        assert "Cannot specify both" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_focus_invalid_direction(self):
        """Test that invalid direction raises error."""
        with pytest.raises(AeroSpaceError) as exc_info:
            await focus_window(direction="diagonal")

        assert "INVALID_DIRECTION" in str(exc_info.value.code)


class TestFocusMonitor:
    """Tests for focus_monitor tool."""

    @pytest.mark.asyncio
    async def test_focus_monitor(self, mock_monitor_list):
        """Test focusing a monitor."""
        with patch(
            "win_ctrl_mcp.tools.window.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.aerospace.get_focused_workspace", new_callable=AsyncMock
            ) as mock_ws:
                mock_ws.return_value = {"workspace": "1", "monitor": "DELL U2720Q"}

                with patch(
                    "win_ctrl_mcp.aerospace.list_monitors", new_callable=AsyncMock
                ) as mock_mon:
                    mock_mon.return_value = mock_monitor_list

                    result = await focus_monitor(target="right")

                    assert result["success"] is True
                    mock_cmd.assert_called_once_with("focus-monitor", "right")


class TestFocusWorkspace:
    """Tests for focus_workspace tool."""

    @pytest.mark.asyncio
    async def test_focus_workspace(self, mock_workspace_list):
        """Test focusing a workspace."""
        with patch(
            "win_ctrl_mcp.tools.window.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch("win_ctrl_mcp.aerospace.list_workspaces", new_callable=AsyncMock) as mock_ws:
                mock_ws.return_value = mock_workspace_list

                with patch(
                    "win_ctrl_mcp.tools.window.list_windows", new_callable=AsyncMock
                ) as mock_win:
                    mock_win.return_value = []

                    result = await focus_workspace(workspace="dev")

                    assert result["success"] is True
                    assert result["workspace"]["name"] == "dev"


class TestMoveWindow:
    """Tests for move_window tool."""

    @pytest.mark.asyncio
    async def test_move_to_workspace(self, mock_window_list):
        """Test moving window to workspace."""
        with patch(
            "win_ctrl_mcp.tools.window.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.tools.window.get_focused_window", new_callable=AsyncMock
            ) as mock_focused:
                mock_focused.return_value = mock_window_list[0]

                result = await move_window(target_type="workspace", target="2")

                assert result["success"] is True
                assert result["moved_to"]["type"] == "workspace"
                assert result["moved_to"]["name"] == "2"

    @pytest.mark.asyncio
    async def test_move_invalid_target_type(self, mock_window_list):
        """Test that invalid target_type raises error."""
        with patch(
            "win_ctrl_mcp.tools.window.get_focused_window", new_callable=AsyncMock
        ) as mock_focused:
            mock_focused.return_value = mock_window_list[0]

            with pytest.raises(AeroSpaceError) as exc_info:
                await move_window(target_type="invalid", target="2")

            assert "Invalid target_type" in str(exc_info.value)


class TestResizeWindow:
    """Tests for resize_window tool."""

    @pytest.mark.asyncio
    async def test_resize_window(self, mock_window_list):
        """Test resizing a window."""
        with patch(
            "win_ctrl_mcp.tools.window.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.tools.window.get_focused_window", new_callable=AsyncMock
            ) as mock_focused:
                mock_focused.return_value = mock_window_list[0]

                result = await resize_window(dimension="width", amount="+50")

                assert result["success"] is True
                assert result["resize"]["dimension"] == "width"
                assert result["resize"]["amount"] == "+50"

    @pytest.mark.asyncio
    async def test_resize_invalid_dimension(self, mock_window_list):
        """Test that invalid dimension raises error."""
        with patch(
            "win_ctrl_mcp.tools.window.get_focused_window", new_callable=AsyncMock
        ) as mock_focused:
            mock_focused.return_value = mock_window_list[0]

            with pytest.raises(AeroSpaceError) as exc_info:
                await resize_window(dimension="invalid", amount="+50")

            assert "Invalid dimension" in str(exc_info.value)


class TestCloseWindow:
    """Tests for close_window tool."""

    @pytest.mark.asyncio
    async def test_close_focused_window(self, mock_window_list):
        """Test closing focused window."""
        with patch(
            "win_ctrl_mcp.tools.window.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.tools.window.get_focused_window", new_callable=AsyncMock
            ) as mock_focused:
                mock_focused.return_value = mock_window_list[0]

                result = await close_window()

                assert result["success"] is True
                assert result["closed_window"]["window_id"] == 1234


class TestFullscreenToggle:
    """Tests for fullscreen_toggle tool."""

    @pytest.mark.asyncio
    async def test_fullscreen_toggle(self, mock_window_list):
        """Test toggling fullscreen."""
        with patch(
            "win_ctrl_mcp.tools.window.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.tools.window.get_focused_window", new_callable=AsyncMock
            ) as mock_focused:
                mock_focused.return_value = mock_window_list[0]

                with patch(
                    "win_ctrl_mcp.tools.window.get_window_by_id", new_callable=AsyncMock
                ) as mock_get:
                    mock_get.return_value = mock_window_list[0]

                    result = await fullscreen_toggle()

                    assert result["success"] is True
                    assert "fullscreen" in result


class TestMinimizeWindow:
    """Tests for minimize_window tool."""

    @pytest.mark.asyncio
    async def test_minimize_window(self, mock_window_list):
        """Test minimizing a window."""
        with patch(
            "win_ctrl_mcp.tools.window.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.tools.window.get_focused_window", new_callable=AsyncMock
            ) as mock_focused:
                mock_focused.return_value = mock_window_list[0]

                result = await minimize_window()

                assert result["success"] is True
                assert result["minimized"] is True
