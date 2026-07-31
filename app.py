from lib.session_store import InMemorySessionStore
import asyncio
import uuid
import sys
from agent.run_agent import run_agent
from lib.genai_client import get_client
from lib.memory_store import ChromaMemoryStore
from helpers.agent.save_memories_and_exit import save_memories_and_exit
from helpers.skills.discover_skills import discover_skills
from helpers.agent.constants import SYSTEM_INSTRUCTIONS
from lib.mcp_client import MCPClient
from helpers.mcp.load_mcp_config import load_mcp_config

async def main(session_id: str, user_id: str, system_instructions: str):
    client = get_client()
    store = InMemorySessionStore()
    memory_store = ChromaMemoryStore()
    mcp_client = MCPClient()

    mcp_servers = load_mcp_config("mcp_config.json")

    try:

        if mcp_servers:
             print("\nConnecting to MCP servers from mcp_config.json...")
             for server_name, server_cfg in mcp_servers.items():
                 command = server_cfg.get("command")
                 args = server_cfg.get("args", [])
 
                 if not command:
                     print(f"⚠️ Skipping '{server_name}': Missing 'command' field.")
                     continue
 
                 try:
                     await mcp_client.connect_to_server(
                         server_name=server_name,
                         command=command,
                         args=args
                     )
                     print(f" Connected to server '{server_name}'")
                 except Exception as e:
                     print(f"❌ Failed to connect to MCP server '{server_name}': {e}")
 
             print(f"Initialized {len(mcp_client.servers)} MCP server(s).\n")
        else:
             print("No active MCP servers loaded. Running with local tools only.\n")


        await run_agent(
            session_id=session_id,
            user_id=user_id,
            store=store,
            memory_store=memory_store,
            system_instructions=system_instructions,
            mcp_client=mcp_client,
        )
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nInterrupted. Saving memories before exit...")
        # Save memories WHILE client is still active
        recovered_history = await store.load(session_id)
        if recovered_history:
            await save_memories_and_exit(recovered_history, user_id, memory_store)
    finally:
        print("Cleaning up MCP server processes...")
        await mcp_client.cleanup()
        print("Closing API client...")
        await client.aclose()
        print("Client closed. Done.")


if __name__ == "__main__":
    skills = discover_skills()
    skills_summary = "\n\n".join(
        f"- name: {s['name']}\n  description: {s['description']}\n  location: {s['location']}"
        for s in skills
    )

    system_instructions = SYSTEM_INSTRUCTIONS.format(
        skills_summary=skills_summary or "(none available)"
    )

    session_id = (
        sys.argv[1]
        if len(sys.argv) > 1
        else input("Enter your session ID (leave blank to create new): ").strip()
    )
    if not session_id:
        session_id = str(uuid.uuid4())

    user_id = (
        sys.argv[2]
        if len(sys.argv) > 2
        else input("Enter your user ID (leave blank to create new): ").strip()
    )
    if not user_id:
        user_id = str(uuid.uuid4())

    print(f"USER ID: {user_id}\n")
    print(f"SESSION ID: {session_id}\n")

    try:
        asyncio.run(main(session_id, user_id, system_instructions))
    except KeyboardInterrupt:
        # Handles Ctrl+C if triggered outside main() execution loop
        print("\nExited.")
