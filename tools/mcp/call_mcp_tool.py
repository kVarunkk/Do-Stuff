from typing import Any
from lib.mcp_client import MCPClient


async def call_mcp_tool(name: str, arguments: dict[str, Any]) -> str:
    """Execute a discovered MCP tool with the provided arguments.

    Args:
        name: Name of the target MCP tool to execute.
        arguments: Key-value dictionary of arguments matching the tool's input schema.
    """
    return ""


def _extract_text_from_block(block: Any) -> str | None:
    text = getattr(block, "text", None)
    if isinstance(text, str) and text:
        return text
    return None


async def _impl_call_mcp_tool(
    name: str, arguments: dict[str, Any], mcp_client: MCPClient
) -> str:
    if name not in mcp_client.mcp_tools:
        raise KeyError(f"Tool '{name}' not found across any connected MCP servers.")

    server_name = mcp_client.mcp_tools[name]["server_name"]
    session = mcp_client.servers[server_name]

    result = await session.call_tool(name, arguments)

    text_parts = [
        text
        for block in result.content
        if (text := _extract_text_from_block(block)) is not None
    ]
    return "\n".join(text_parts) if text_parts else "Tool executed successfully."