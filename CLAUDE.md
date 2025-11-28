# Window Manager MCP for MacOSX / AeroSpace

This is a repository of an MCP server for the AeroSpace Window Manager running on MacOSX.

## Project Status

This repository is at the high level design state.

## Requirements

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) package manager
- [FastMCP SDK](https://github.com/jlowin/fastmcp)
- MacOSX with [AeroSpace](https://nikitabobko.github.io/AeroSpace/) window manager installed

## Installation

### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew
brew install uv
```

### 2. Clone and set up the project

```bash
git clone https://github.com/huegli/win-ctrl-mcp.git
cd win-ctrl-mcp

# Create virtual environment and install dependencies
uv sync
```

### 3. Install development dependencies

```bash
uv sync --dev
```

## Execution

### Running the MCP Server

```bash
# Run the server directly
uv run python -m win_ctrl_mcp

# Or if an entry point is defined
uv run win-ctrl-mcp
```

### Configuring with Claude Desktop

Add the server to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "win-ctrl": {
      "command": "uv",
      "args": ["--directory", "/path/to/win-ctrl-mcp", "run", "win-ctrl-mcp"]
    }
  }
}
```

## Debugging

### Enable Debug Logging

```bash
# Set environment variable for verbose logging
export MCP_DEBUG=1
uv run python -m win_ctrl_mcp
```

### Using MCP Inspector

The [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) is useful for debugging:

```bash
# Install and run the inspector
npx @modelcontextprotocol/inspector uv run python -m win_ctrl_mcp
```

### Common Debug Techniques

1. **Check server startup**: Ensure AeroSpace is running before starting the MCP server
2. **Verify AeroSpace CLI**: Test that `aerospace` commands work in your terminal
3. **Review logs**: Check stderr output for error messages
4. **Test tools individually**: Use the MCP Inspector to test each tool in isolation

## Linting

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

### Run Linter

```bash
# Check for linting issues
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .
```

### Run Formatter

```bash
# Check formatting
uv run ruff format --check .

# Auto-format code
uv run ruff format .
```

### Type Checking

```bash
# Run type checker (if mypy/pyright is configured)
uv run mypy .
# or
uv run pyright
```

## Testing

This project uses [pytest](https://pytest.org/) for testing.

### Run All Tests

```bash
uv run pytest
```

### Run Tests with Coverage

```bash
uv run pytest --cov=win_ctrl_mcp --cov-report=term-missing
```

### Run Specific Tests

```bash
# Run a specific test file
uv run pytest tests/test_tools.py

# Run a specific test function
uv run pytest tests/test_tools.py::test_list_windows

# Run tests matching a pattern
uv run pytest -k "window"
```

### Run Tests with Verbose Output

```bash
uv run pytest -v
```

## Project Structure

```
win-ctrl-mcp/
├── CLAUDE.md           # Development instructions (this file)
├── README.md           # Project overview
├── SPEC.md             # Specification and reference material
├── LICENSE             # License file
├── pyproject.toml      # Project configuration and dependencies
├── src/
│   └── win_ctrl_mcp/   # Main package
│       ├── __init__.py
│       ├── __main__.py # Entry point
│       ├── server.py   # MCP server implementation
│       └── tools/      # AeroSpace tool implementations
└── tests/              # Test files
    └── test_*.py
```

## Reference Material

- [AeroSpace Command Reference](https://nikitabobko.github.io/AeroSpace/commands)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Reference Implementation (Yabai)](https://github.com/huegli/capture-win-mcp)
