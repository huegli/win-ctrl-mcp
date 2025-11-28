"""Tests for capture tools."""

import os
import tempfile
from unittest.mock import AsyncMock, patch

import pytest

from win_ctrl_mcp.aerospace import AeroSpaceError
from win_ctrl_mcp.tools.capture import capture_window, capture_workspace


class TestCaptureWindow:
    """Tests for capture_window tool."""

    @pytest.mark.asyncio
    async def test_capture_focused_window(self, mock_window_list):
        """Test capturing the focused window."""
        with patch(
            "win_ctrl_mcp.tools.capture.get_focused_window", new_callable=AsyncMock
        ) as mock_focused:
            mock_focused.return_value = mock_window_list[0]

            with patch("win_ctrl_mcp.tools.capture._run_screencapture", new_callable=AsyncMock):
                result = await capture_window()

                assert result["success"] is True
                assert result["capture"]["window_id"] == 1234
                assert result["capture"]["app_name"] == "Firefox"
                assert result["capture"]["format"] == "png"

    @pytest.mark.asyncio
    async def test_capture_specific_window(self, mock_window_list):
        """Test capturing a specific window by ID."""
        with patch(
            "win_ctrl_mcp.tools.capture.get_window_by_id", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_window_list[1]

            with patch("win_ctrl_mcp.tools.capture._run_screencapture", new_callable=AsyncMock):
                result = await capture_window(window_id=5678)

                assert result["success"] is True
                assert result["capture"]["window_id"] == 5678
                assert result["capture"]["app_name"] == "Terminal"

    @pytest.mark.asyncio
    async def test_capture_with_custom_path(self, mock_window_list):
        """Test capturing to a custom output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.png")

            with patch(
                "win_ctrl_mcp.tools.capture.get_focused_window", new_callable=AsyncMock
            ) as mock_focused:
                mock_focused.return_value = mock_window_list[0]

                with patch("win_ctrl_mcp.tools.capture._run_screencapture", new_callable=AsyncMock):
                    result = await capture_window(output_path=output_path)

                    assert result["success"] is True
                    assert result["capture"]["file_path"] == output_path

    @pytest.mark.asyncio
    async def test_capture_jpg_format(self, mock_window_list):
        """Test capturing in JPG format."""
        with patch(
            "win_ctrl_mcp.tools.capture.get_focused_window", new_callable=AsyncMock
        ) as mock_focused:
            mock_focused.return_value = mock_window_list[0]

            with patch("win_ctrl_mcp.tools.capture._run_screencapture", new_callable=AsyncMock):
                result = await capture_window(format="jpg")

                assert result["success"] is True
                assert result["capture"]["format"] == "jpg"

    @pytest.mark.asyncio
    async def test_capture_invalid_format(self, mock_window_list):
        """Test that invalid format raises error."""
        with patch(
            "win_ctrl_mcp.tools.capture.get_focused_window", new_callable=AsyncMock
        ) as mock_focused:
            mock_focused.return_value = mock_window_list[0]

            with pytest.raises(AeroSpaceError) as exc_info:
                await capture_window(format="bmp")

            assert "Invalid format" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_capture_no_focused_window(self):
        """Test error when no window is focused."""
        with patch(
            "win_ctrl_mcp.tools.capture.get_focused_window", new_callable=AsyncMock
        ) as mock_focused:
            mock_focused.return_value = None

            with pytest.raises(AeroSpaceError) as exc_info:
                await capture_window()

            assert "NO_WINDOW_FOCUSED" in exc_info.value.code


class TestCaptureWorkspace:
    """Tests for capture_workspace tool."""

    @pytest.mark.asyncio
    async def test_capture_focused_workspace(self, mock_workspace_list, mock_monitor_list):
        """Test capturing the focused workspace."""
        with patch(
            "win_ctrl_mcp.tools.capture.get_focused_workspace", new_callable=AsyncMock
        ) as mock_ws:
            mock_ws.return_value = mock_workspace_list[0]

            with patch(
                "win_ctrl_mcp.tools.capture.get_focused_monitor", new_callable=AsyncMock
            ) as mock_mon:
                mock_mon.return_value = mock_monitor_list[0]

                with patch(
                    "win_ctrl_mcp.tools.capture.list_monitors", new_callable=AsyncMock
                ) as mock_mons:
                    mock_mons.return_value = mock_monitor_list

                    with patch(
                        "win_ctrl_mcp.tools.capture.list_windows", new_callable=AsyncMock
                    ) as mock_win:
                        mock_win.return_value = []

                        with patch(
                            "win_ctrl_mcp.tools.capture._run_screencapture",
                            new_callable=AsyncMock,
                        ):
                            result = await capture_workspace()

                            assert result["success"] is True
                            assert result["capture"]["workspace"] == "1"

    @pytest.mark.asyncio
    async def test_capture_specific_workspace(
        self,
        mock_workspace_list,  # noqa: ARG002
        mock_monitor_list,
        mock_window_list,  # noqa: ARG002
    ):
        """Test capturing a specific workspace."""
        with patch(
            "win_ctrl_mcp.aerospace.run_aerospace_command", new_callable=AsyncMock
        ) as mock_cmd:
            mock_cmd.return_value = ("", "", 0)

            with patch(
                "win_ctrl_mcp.tools.capture.get_focused_workspace", new_callable=AsyncMock
            ) as mock_ws:
                mock_ws.return_value = {"workspace": "dev"}

                with patch(
                    "win_ctrl_mcp.tools.capture.get_focused_monitor", new_callable=AsyncMock
                ) as mock_mon:
                    mock_mon.return_value = mock_monitor_list[1]

                    with patch(
                        "win_ctrl_mcp.tools.capture.list_monitors", new_callable=AsyncMock
                    ) as mock_mons:
                        mock_mons.return_value = mock_monitor_list

                        with patch(
                            "win_ctrl_mcp.tools.capture.list_windows", new_callable=AsyncMock
                        ) as mock_win:
                            mock_win.return_value = [mock_window_list[2]]

                            with patch(
                                "win_ctrl_mcp.tools.capture._run_screencapture",
                                new_callable=AsyncMock,
                            ):
                                result = await capture_workspace(workspace="dev")

                                assert result["success"] is True
                                assert result["capture"]["workspace"] == "dev"
                                assert len(result["capture"]["windows_captured"]) == 1
