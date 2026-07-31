
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Any, Dict, List, Optional
import sys
import os

class MCPClient:
    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.servers: dict[str, ClientSession] = {}
        self.mcp_tools: dict[str, dict[str, Any]] = {}

    async def connect_to_server(
        self,
        server_name: str,
        command: str = sys.executable,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> None:
        """Establishes an async stdio session with an MCP server and updates tool index."""
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        server_params = StdioServerParameters(
            command=command, args=args or [], env=merged_env
        )

        # 1. Spawn sub-process and setup streams
        read, write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        # 2. Establish client session
        session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await session.initialize()

        # Save session handle
        self.servers[server_name] = session

        # 3. Discover and index tools for progressive disclosure
        tools_response = await session.list_tools()
        for tool in tools_response.tools:
            self.mcp_tools[f"{tool.name}"] = {
                "server_name": server_name,
                "schema": {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                    "output_schema": tool.output_schema
                },
            }

        print(
            f"Connected to server '{server_name}' ({len(tools_response.tools)} tools added)"
        )
   
    async def cleanup(self) -> None:
         """Safely tears down all connected MCP server sessions and stdio streams."""
         await self.exit_stack.aclose()
         self.servers.clear()
         self.mcp_tools.clear()


