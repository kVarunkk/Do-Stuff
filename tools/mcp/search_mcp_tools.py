from lib.mcp_client import MCPClient
import json

def search_mcp_tools(query: str) -> list[dict[str, str]]:
    """Search available MCP tools by keyword across connected MCP servers.
    
    Args:
        query: Keywords or description to search for matching tools.
        
    Returns:
        List of matching tools with tool name and short description only.
    """
    return []

def _impl_search_mcp_tools(query: str, mcp_client: MCPClient) -> str:
    query_lower = query.lower()
    results = []
    for tool_name, tool_info in mcp_client.mcp_tools.items():
        desc = tool_info["schema"].get("description", "")
        if query_lower in tool_name.lower() or query_lower in desc.lower():
            results.append({
                "name": tool_name,
                "description": desc,
                "server": tool_info["server_name"]
            })
    if not results:
        return f"No MCP tools found matching query: '{query}'."

    return json.dumps(results, indent=2)   