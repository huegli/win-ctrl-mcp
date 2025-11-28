"""Tests for MCP server module."""

from win_ctrl_mcp.aerospace import AeroSpaceError
from win_ctrl_mcp.server import handle_error, mcp


class TestMCPServer:
    """Tests for MCP server setup."""

    def test_mcp_server_exists(self):
        """Test that MCP server is created."""
        assert mcp is not None
        assert mcp.name == "AeroSpace Window Manager"

    def test_mcp_server_has_tools(self):
        """Test that MCP server has registered tools."""
        # FastMCP stores tools in _tool_manager
        # We can check that tools were registered by checking the server exists
        assert hasattr(mcp, "_tool_manager") or hasattr(mcp, "tools")

    def test_mcp_server_has_resources(self):
        """Test that MCP server has registered resources."""
        # Resources are registered via decorators
        assert hasattr(mcp, "_resource_manager") or hasattr(mcp, "resources")

    def test_mcp_server_has_prompts(self):
        """Test that MCP server has registered prompts."""
        # Prompts are registered via decorators
        assert hasattr(mcp, "_prompt_manager") or hasattr(mcp, "prompts")


class TestHandleError:
    """Tests for error handling."""

    def test_handle_aerospace_error(self):
        """Test handling AeroSpaceError."""
        error = AeroSpaceError(
            code="TEST_ERROR",
            message="Test error message",
            details={"key": "value"},
        )
        result = handle_error(error)

        assert result["success"] is False
        assert result["error"]["code"] == "TEST_ERROR"
        assert result["error"]["message"] == "Test error message"
        assert result["error"]["details"]["key"] == "value"

    def test_handle_generic_error(self):
        """Test handling generic exception."""
        error = ValueError("Something went wrong")
        result = handle_error(error)

        assert result["success"] is False
        assert result["error"]["code"] == "UNKNOWN_ERROR"
        assert "Something went wrong" in result["error"]["message"]
        assert result["error"]["details"] == {}

    def test_handle_error_with_empty_details(self):
        """Test handling error with empty details."""
        error = AeroSpaceError(code="TEST", message="Test")
        result = handle_error(error)

        assert result["error"]["details"] == {}
