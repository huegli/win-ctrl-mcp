"""Tests for aerospace module."""

import pytest

from win_ctrl_mcp.aerospace import (
    ERROR_INVALID_DIRECTION,
    ERROR_INVALID_LAYOUT,
    VALID_DIRECTIONS,
    VALID_LAYOUTS,
    AeroSpaceError,
    validate_direction,
    validate_layout,
)


class TestAeroSpaceError:
    """Tests for AeroSpaceError class."""

    def test_error_creation(self):
        """Test creating an AeroSpaceError."""
        error = AeroSpaceError(
            code="TEST_ERROR",
            message="Test error message",
            details={"key": "value"},
        )
        assert error.code == "TEST_ERROR"
        assert error.message == "Test error message"
        assert error.details == {"key": "value"}

    def test_error_to_dict(self):
        """Test converting error to dictionary."""
        error = AeroSpaceError(
            code="TEST_ERROR",
            message="Test message",
            details={"foo": "bar"},
        )
        result = error.to_dict()

        assert result["success"] is False
        assert result["error"]["code"] == "TEST_ERROR"
        assert result["error"]["message"] == "Test message"
        assert result["error"]["details"] == {"foo": "bar"}

    def test_error_default_details(self):
        """Test error with default empty details."""
        error = AeroSpaceError(code="TEST", message="Test")
        assert error.details == {}


class TestValidateDirection:
    """Tests for direction validation."""

    def test_valid_directions(self):
        """Test that valid directions pass validation."""
        for direction in VALID_DIRECTIONS:
            # Should not raise
            validate_direction(direction)

    def test_invalid_direction(self):
        """Test that invalid direction raises error."""
        with pytest.raises(AeroSpaceError) as exc_info:
            validate_direction("diagonal")

        error = exc_info.value
        assert error.code == ERROR_INVALID_DIRECTION
        assert "diagonal" in error.message


class TestValidateLayout:
    """Tests for layout validation."""

    def test_valid_layouts(self):
        """Test that valid layouts pass validation."""
        for layout in VALID_LAYOUTS:
            # Should not raise
            validate_layout(layout)

    def test_invalid_layout(self):
        """Test that invalid layout raises error."""
        with pytest.raises(AeroSpaceError) as exc_info:
            validate_layout("invalid_layout")

        error = exc_info.value
        assert error.code == ERROR_INVALID_LAYOUT
        assert "invalid_layout" in error.message
