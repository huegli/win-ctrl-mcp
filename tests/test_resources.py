"""Tests for MCP resources."""

from unittest.mock import AsyncMock, patch

import pytest

from win_ctrl_mcp.aerospace import AeroSpaceError
from win_ctrl_mcp.resources import (
    get_display_resource,
    get_displays_resource,
    get_focused_resource,
    get_monitors_resource,
    get_tree_resource,
    get_window_resource,
    get_windows_resource,
    get_workspace_resource,
    get_workspaces_resource,
)


class TestWindowsResource:
    """Tests for windows resource."""

    @pytest.mark.asyncio
    async def test_get_windows(self, mock_window_list):
        """Test getting all windows."""
        with patch("win_ctrl_mcp.resources.list_windows", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = mock_window_list

            with patch(
                "win_ctrl_mcp.resources.get_focused_window", new_callable=AsyncMock
            ) as mock_focused:
                mock_focused.return_value = mock_window_list[0]

                result = await get_windows_resource()

                assert "windows" in result
                assert "total_count" in result
                assert result["total_count"] == 3


class TestWindowResource:
    """Tests for single window resource."""

    @pytest.mark.asyncio
    async def test_get_existing_window(self, mock_window_list):
        """Test getting an existing window."""
        with patch("win_ctrl_mcp.resources.list_windows", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = mock_window_list

            with patch(
                "win_ctrl_mcp.resources.get_focused_window", new_callable=AsyncMock
            ) as mock_focused:
                mock_focused.return_value = mock_window_list[0]

                result = await get_window_resource(1234)

                assert result["window_id"] == 1234
                assert result["app_name"] == "Firefox"

    @pytest.mark.asyncio
    async def test_get_nonexistent_window(self, mock_window_list):
        """Test error for non-existent window."""
        with patch("win_ctrl_mcp.resources.list_windows", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = mock_window_list

            with pytest.raises(AeroSpaceError) as exc_info:
                await get_window_resource(9999)

            assert "WINDOW_NOT_FOUND" in exc_info.value.code


class TestWorkspacesResource:
    """Tests for workspaces resource."""

    @pytest.mark.asyncio
    async def test_get_workspaces(self, mock_workspace_list):
        """Test getting all workspaces."""
        with patch("win_ctrl_mcp.resources.list_workspaces", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = mock_workspace_list

            with patch("win_ctrl_mcp.resources.list_windows", new_callable=AsyncMock) as mock_win:
                mock_win.return_value = []

                with patch(
                    "win_ctrl_mcp.resources.get_focused_workspace", new_callable=AsyncMock
                ) as mock_focused:
                    mock_focused.return_value = mock_workspace_list[0]

                    result = await get_workspaces_resource()

                    assert "workspaces" in result
                    assert "total_count" in result
                    assert result["total_count"] == 3


class TestWorkspaceResource:
    """Tests for single workspace resource."""

    @pytest.mark.asyncio
    async def test_get_existing_workspace(self, mock_workspace_list, mock_window_list):
        """Test getting an existing workspace."""
        with patch("win_ctrl_mcp.resources.list_workspaces", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = mock_workspace_list

            with patch("win_ctrl_mcp.resources.list_windows", new_callable=AsyncMock) as mock_win:
                mock_win.return_value = mock_window_list[:2]

                with patch(
                    "win_ctrl_mcp.resources.get_focused_workspace", new_callable=AsyncMock
                ) as mock_focused:
                    mock_focused.return_value = mock_workspace_list[0]

                    result = await get_workspace_resource("1")

                    assert result["name"] == "1"
                    assert len(result["windows"]) == 2

    @pytest.mark.asyncio
    async def test_get_nonexistent_workspace(self, mock_workspace_list):
        """Test error for non-existent workspace."""
        with patch("win_ctrl_mcp.resources.list_workspaces", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = mock_workspace_list

            with pytest.raises(AeroSpaceError) as exc_info:
                await get_workspace_resource("nonexistent")

            assert "WORKSPACE_NOT_FOUND" in exc_info.value.code


class TestMonitorsResource:
    """Tests for monitors resource."""

    @pytest.mark.asyncio
    async def test_get_monitors(self, mock_monitor_list, mock_workspace_list):
        """Test getting all monitors."""
        with patch("win_ctrl_mcp.resources.list_monitors", new_callable=AsyncMock) as mock_mon:
            mock_mon.return_value = mock_monitor_list

            with patch("win_ctrl_mcp.resources.list_workspaces", new_callable=AsyncMock) as mock_ws:
                mock_ws.return_value = mock_workspace_list

                result = await get_monitors_resource()

                assert "monitors" in result
                assert "total_count" in result
                assert result["total_count"] == 2


class TestTreeResource:
    """Tests for tree resource."""

    @pytest.mark.asyncio
    async def test_get_tree(self, mock_workspace_list, mock_window_list):
        """Test getting window tree."""
        with patch(
            "win_ctrl_mcp.resources.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.resources.get_focused_workspace", new_callable=AsyncMock
            ) as mock_ws:
                mock_ws.return_value = mock_workspace_list[0]

                with patch(
                    "win_ctrl_mcp.resources.list_windows", new_callable=AsyncMock
                ) as mock_win:
                    mock_win.return_value = mock_window_list[:2]

                    result = await get_tree_resource()

                    assert "tree" in result
                    assert result["tree"]["type"] == "workspace"
                    assert "children" in result["tree"]


class TestFocusedResource:
    """Tests for focused resource."""

    @pytest.mark.asyncio
    async def test_get_focused(self, mock_window_list, mock_workspace_list, mock_monitor_list):
        """Test getting focused state."""
        with patch("win_ctrl_mcp.resources.get_focused_window", new_callable=AsyncMock) as mock_win:
            mock_win.return_value = mock_window_list[0]

            with patch(
                "win_ctrl_mcp.resources.get_focused_workspace", new_callable=AsyncMock
            ) as mock_ws:
                mock_ws.return_value = mock_workspace_list[0]

                with patch(
                    "win_ctrl_mcp.resources.get_focused_monitor", new_callable=AsyncMock
                ) as mock_mon:
                    mock_mon.return_value = mock_monitor_list[0]

                    with patch(
                        "win_ctrl_mcp.resources.list_windows", new_callable=AsyncMock
                    ) as mock_list_win:
                        mock_list_win.return_value = mock_window_list[:2]

                        result = await get_focused_resource()

                        assert "window" in result
                        assert "workspace" in result
                        assert "monitor" in result
                        assert result["window"]["window_id"] == 1234


class TestDisplaysResource:
    """Tests for displays resource."""

    @pytest.mark.asyncio
    async def test_get_displays(self, mock_workspace_list):
        """Test getting displays."""
        with patch("win_ctrl_mcp.resources.get_display_info", new_callable=AsyncMock) as mock_info:
            mock_info.return_value = {
                "displays": [
                    {"id": 1, "name": "Display 1"},
                    {"id": 2, "name": "Display 2"},
                ],
                "category": "dual_display",
            }

            with patch("win_ctrl_mcp.resources.list_workspaces", new_callable=AsyncMock) as mock_ws:
                mock_ws.return_value = mock_workspace_list

                result = await get_displays_resource()

                assert "displays" in result
                assert len(result["displays"]) == 2


class TestDisplayResource:
    """Tests for single display resource."""

    @pytest.mark.asyncio
    async def test_get_existing_display(self):
        """Test getting an existing display."""
        with patch("win_ctrl_mcp.resources.get_display_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"id": 1, "name": "Display 1"}

            result = await get_display_resource(1)

            assert result["id"] == 1

    @pytest.mark.asyncio
    async def test_get_nonexistent_display(self):
        """Test error for non-existent display."""
        with patch("win_ctrl_mcp.resources.get_display_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            with patch(
                "win_ctrl_mcp.resources.get_display_info", new_callable=AsyncMock
            ) as mock_info:
                mock_info.return_value = {"displays": [{"id": 1}]}

                with pytest.raises(AeroSpaceError) as exc_info:
                    await get_display_resource(999)

                assert "DISPLAY_NOT_FOUND" in exc_info.value.code
