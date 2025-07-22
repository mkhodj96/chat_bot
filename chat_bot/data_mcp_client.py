from typing import Any

from mcp import ClientSession
from mcp.client.sse import sse_client


class MCPClient:
    """A client class for interacting with the MCP (Model Control Protocol) server."""

    def __init__(self, sse_url: str = "http://0.0.0.0:8000/sse"):
        """Initialize the MCP client with server parameters."""
        self.sse_url = sse_url

    async def get_available_tools(self) -> list[Any]:
        """Retrieve a list of available tools from the MCP server."""
        async with sse_client(self.sse_url) as (read, write):  # noqa: SIM117
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools = await session.list_tools()
                return tools.tools

    async def call_tool(self, tool_name: str, **kwargs) -> Any:  # noqa: ANN401
        """Create a callable function for a specific tool.

        This allows us to execute database operations through the MCP server.

        Args:
            tool_name: The name of the tool to create a callable for
            **kwargs: tool kwargs

        Returns:
            A callable async function that executes the specified tool

        """
        async with sse_client(self.sse_url) as (read, write):  # noqa: SIM117
            async with ClientSession(read, write) as session:
                await session.initialize()
                res = await session.call_tool(tool_name, arguments=kwargs)
                return res.content[0].text
