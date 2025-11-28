"""Tests for layout management tools."""

from unittest.mock import AsyncMock, patch

import pytest

from win_ctrl_mcp.aerospace import AeroSpaceError
from win_ctrl_mcp.tools.layout import (
    balance_sizes,
    flatten_workspace,
    set_layout,
    split_window,
)


class TestSetLayout:
    """Tests for set_layout tool."""

    @pytest.mark.asyncio
    async def test_set_layout_h_tiles(self, mock_workspace_list, mock_window_list):
        """Test setting horizontal tiles layout."""
        with patch(
            "win_ctrl_mcp.tools.layout.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.tools.layout.get_focused_workspace", new_callable=AsyncMock
            ) as mock_ws:
                mock_ws.return_value = mock_workspace_list[0]

                with patch(
                    "win_ctrl_mcp.tools.layout.list_windows", new_callable=AsyncMock
                ) as mock_win:
                    mock_win.return_value = mock_window_list[:2]

                    result = await set_layout(layout="h_tiles")

                    assert result["success"] is True
                    assert result["layout"] == "h_tiles"
                    mock_cmd.assert_called_once_with("layout", "h_tiles")

    @pytest.mark.asyncio
    async def test_set_layout_invalid(self):
        """Test that invalid layout raises error."""
        with pytest.raises(AeroSpaceError) as exc_info:
            await set_layout(layout="invalid_layout")

        assert "INVALID_LAYOUT" in exc_info.value.code


class TestSplitWindow:
    """Tests for split_window tool."""

    @pytest.mark.asyncio
    async def test_split_horizontal(self):
        """Test horizontal split."""
        with patch(
            "win_ctrl_mcp.tools.layout.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            result = await split_window(orientation="horizontal")

            assert result["success"] is True
            assert result["split_orientation"] == "horizontal"
            mock_cmd.assert_called_once_with("split", "horizontal")

    @pytest.mark.asyncio
    async def test_split_vertical(self):
        """Test vertical split."""
        with patch(
            "win_ctrl_mcp.tools.layout.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            result = await split_window(orientation="vertical")

            assert result["success"] is True
            assert result["split_orientation"] == "vertical"

    @pytest.mark.asyncio
    async def test_split_invalid_orientation(self):
        """Test that invalid orientation raises error."""
        with pytest.raises(AeroSpaceError) as exc_info:
            await split_window(orientation="diagonal")

        assert "Invalid orientation" in str(exc_info.value)


class TestFlattenWorkspace:
    """Tests for flatten_workspace tool."""

    @pytest.mark.asyncio
    async def test_flatten_current_workspace(self, mock_workspace_list):
        """Test flattening current workspace."""
        with patch(
            "win_ctrl_mcp.tools.layout.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.tools.layout.get_focused_workspace", new_callable=AsyncMock
            ) as mock_ws:
                mock_ws.return_value = mock_workspace_list[0]

                result = await flatten_workspace()

                assert result["success"] is True
                # Verify flatten-workspace-tree was called
                assert any(
                    "flatten-workspace-tree" in str(call) for call in mock_cmd.call_args_list
                )

    @pytest.mark.asyncio
    async def test_flatten_specific_workspace(self, mock_workspace_list):  # noqa: ARG002
        """Test flattening a specific workspace."""
        with patch(
            "win_ctrl_mcp.tools.layout.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.tools.layout.get_focused_workspace", new_callable=AsyncMock
            ) as mock_ws:
                mock_ws.return_value = {"workspace": "dev"}

                result = await flatten_workspace(workspace="dev")

                assert result["success"] is True
                assert result["workspace"] == "dev"


class TestBalanceSizes:
    """Tests for balance_sizes tool."""

    @pytest.mark.asyncio
    async def test_balance_sizes(self, mock_workspace_list, mock_window_list):
        """Test balancing window sizes."""
        with patch(
            "win_ctrl_mcp.tools.layout.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.tools.layout.get_focused_workspace", new_callable=AsyncMock
            ) as mock_ws:
                mock_ws.return_value = mock_workspace_list[0]

                with patch(
                    "win_ctrl_mcp.tools.layout.list_windows", new_callable=AsyncMock
                ) as mock_win:
                    mock_win.return_value = mock_window_list[:2]

                    result = await balance_sizes()

                    assert result["success"] is True
                    assert result["balanced_windows"] == 2
                    mock_cmd.assert_called_once_with("balance-sizes")
