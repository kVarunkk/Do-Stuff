from lib.session_store import InMemorySessionStore
import asyncio
import uuid
import sys
from agent.run_agent import run_agent
from lib.genai_client import get_client

if __name__ == "__main__":
    store = InMemorySessionStore()
    session_id = sys.argv[1] if len(sys.argv) > 1 else str(uuid.uuid4())
    print(f"STARTING SESSION: {session_id}\n\n")
    async def main():
        client = get_client()
        try:
            await run_agent(session_id=session_id, store=store)
        finally:
            print("Client closed.")
            await client.aclose()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
