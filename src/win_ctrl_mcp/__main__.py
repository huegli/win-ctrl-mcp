"""Entry point for the AeroSpace MCP Server.

Run with:
    uv run python -m win_ctrl_mcp
    or
    uv run win-ctrl-mcp
"""

import sys


def main() -> int:
    """Run the MCP server."""
    from win_ctrl_mcp.server import mcp

    mcp.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
