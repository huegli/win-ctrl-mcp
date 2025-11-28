"""Tests for display information tools."""

from unittest.mock import AsyncMock, patch

import pytest

from win_ctrl_mcp.tools.display import (
    _calculate_display_category,
    _get_size_category,
    get_display_by_id,
    get_display_category,
    get_display_info,
)


class TestCalculateDisplayCategory:
    """Tests for display category calculation."""

    def test_no_displays(self):
        """Test with no displays."""
        category, _ = _calculate_display_category([])
        assert category == "unknown"

    def test_single_small_display(self):
        """Test single small display categorization."""
        displays = [
            {
                "effective_resolution": {"width": 1366, "height": 768},
                "size_inches": 13,
            }
        ]
        category, _ = _calculate_display_category(displays)
        assert category == "small_single"

    def test_single_medium_display(self):
        """Test single medium display categorization."""
        displays = [
            {
                "effective_resolution": {"width": 1920, "height": 1080},
                "size_inches": 21,
            }
        ]
        category, _ = _calculate_display_category(displays)
        assert category == "medium_single"

    def test_single_large_display(self):
        """Test single large display categorization."""
        displays = [
            {
                "effective_resolution": {"width": 2560, "height": 1440},
                "size_inches": 27,
            }
        ]
        category, _ = _calculate_display_category(displays)
        assert category == "large_single"

    def test_dual_display(self):
        """Test dual display categorization."""
        displays = [
            {"effective_resolution": {"width": 1920, "height": 1080}},
            {"effective_resolution": {"width": 2560, "height": 1440}},
        ]
        category, _ = _calculate_display_category(displays)
        assert category == "dual_display"

    def test_triple_display(self):
        """Test triple+ display categorization."""
        displays = [
            {"effective_resolution": {"width": 1920, "height": 1080}},
            {"effective_resolution": {"width": 1920, "height": 1080}},
            {"effective_resolution": {"width": 1920, "height": 1080}},
        ]
        category, _ = _calculate_display_category(displays)
        assert category == "triple_plus"


class TestGetSizeCategory:
    """Tests for size category calculation."""

    def test_small_resolution(self):
        """Test small resolution categorization."""
        result = _get_size_category({"width": 1024, "height": 768})
        assert result == "small"

    def test_medium_resolution(self):
        """Test medium resolution categorization."""
        result = _get_size_category({"width": 1920, "height": 1080})
        assert result == "medium"

    def test_large_resolution(self):
        """Test large resolution categorization."""
        result = _get_size_category({"width": 2560, "height": 1440})
        assert result == "large"


class TestGetDisplayInfo:
    """Tests for get_display_info tool."""

    @pytest.mark.asyncio
    async def test_get_display_info(self, mock_monitor_list):
        """Test getting display information."""
        with patch("win_ctrl_mcp.tools.display.list_monitors", new_callable=AsyncMock) as mock_mon:
            mock_mon.return_value = mock_monitor_list

            with patch(
                "win_ctrl_mcp.tools.display._get_system_display_info", new_callable=AsyncMock
            ) as mock_sys:
                mock_sys.return_value = []

                result = await get_display_info()

                assert "displays" in result
                assert "arrangement" in result
                assert "category" in result
                assert len(result["displays"]) == 2


class TestGetDisplayCategory:
    """Tests for get_display_category tool."""

    @pytest.mark.asyncio
    async def test_get_display_category(self, mock_monitor_list):  # noqa: ARG002
        """Test getting display category."""
        with patch(
            "win_ctrl_mcp.tools.display.get_display_info", new_callable=AsyncMock
        ) as mock_info:
            mock_info.return_value = {
                "displays": [
                    {
                        "effective_resolution": {"width": 1920, "height": 1080},
                        "is_primary": True,
                    },
                    {
                        "effective_resolution": {"width": 2560, "height": 1440},
                        "is_primary": False,
                    },
                ],
            }

            result = await get_display_category()

            assert "category" in result
            assert result["category"] == "dual_display"
            assert "recommended_strategy" in result


class TestGetDisplayById:
    """Tests for get_display_by_id function."""

    @pytest.mark.asyncio
    async def test_get_existing_display(
        self,
        mock_monitor_list,  # noqa: ARG002
        mock_workspace_list,  # noqa: ARG002
    ):
        """Test getting an existing display by ID."""
        with patch(
            "win_ctrl_mcp.tools.display.get_display_info", new_callable=AsyncMock
        ) as mock_info:
            mock_info.return_value = {
                "displays": [
                    {"id": 1, "name": "Built-in Retina Display"},
                    {"id": 2, "name": "DELL U2720Q"},
                ]
            }

            with patch(
                "win_ctrl_mcp.tools.display.list_workspaces", new_callable=AsyncMock
            ) as mock_ws:
                mock_ws.return_value = mock_workspace_list

                with patch(
                    "win_ctrl_mcp.aerospace.list_windows", new_callable=AsyncMock
                ) as mock_win:
                    mock_win.return_value = []

                    result = await get_display_by_id(1)

                    assert result is not None
                    assert result["id"] == 1

    @pytest.mark.asyncio
    async def test_get_nonexistent_display(self):
        """Test getting a non-existent display."""
        with patch(
            "win_ctrl_mcp.tools.display.get_display_info", new_callable=AsyncMock
        ) as mock_info:
            mock_info.return_value = {"displays": [{"id": 1}]}

            result = await get_display_by_id(999)

            assert result is None
