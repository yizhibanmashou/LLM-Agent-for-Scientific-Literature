"""
Entry point for running paper2latex MCP server.
"""

from .server import mcp

if __name__ == "__main__":
    mcp.run(transport="streamable-http", json_response=True)
