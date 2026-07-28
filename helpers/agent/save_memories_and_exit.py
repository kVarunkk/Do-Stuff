from helpers.memory.extract_memories import extract_memories

async def save_memories_and_exit(steps_history, user_id, memory_store):
    print("WE ARE NOW SAVING YOUR LONG TERM MEMORY. THIS MIGHT TAKE SOME TIME. THE PROCESS WILL GRACEFULLY EXIT ON ITS OWN.")
    facts = await extract_memories(steps_history)
    if facts:
        await memory_store.add(user_id, facts)
        print(f"SAVED LONG TERM MEMORY. EXITING.")