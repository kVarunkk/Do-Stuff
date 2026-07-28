from lib.session_store import InMemorySessionStore
import asyncio
import uuid
import sys
from agent.run_agent import run_agent
from lib.genai_client import get_client
from lib.memory_store import ChromaMemoryStore
from helpers.agent.save_memories_and_exit import save_memories_and_exit

if __name__ == "__main__":
    store = InMemorySessionStore()
    memory_store = ChromaMemoryStore()

    session_id = sys.argv[1] if len(sys.argv) > 1 else input("Enter your session ID (leave blank to create new): ").strip()
    if not session_id:
            session_id = str(uuid.uuid4())
    user_id = sys.argv[2] if len(sys.argv) > 2 else input("Enter your user ID (leave blank to create new): ").strip()
    if not user_id:
        user_id = str(uuid.uuid4())
    print(f"USER ID: {user_id}\n\n")
    print(f"SESSION ID: {session_id}\n\n")
    async def main():
        client = get_client()
        try:
            await run_agent(session_id=session_id, user_id=user_id, store=store, memory_store=memory_store)
        finally:
            print("Client closed.")
            await client.aclose()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
        async def cleanup():
            recovered_history = await store.load(session_id)
            await save_memories_and_exit(recovered_history, user_id, memory_store)
    
        asyncio.run(cleanup())
