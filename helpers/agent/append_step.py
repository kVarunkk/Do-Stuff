from lib.session_store import  SessionStore

async def append_step(step: dict, steps_history: list, working_history: list, session_id: str, store: SessionStore) -> None:
    steps_history.append(step)
    working_history.append(step)
    await store.append(session_id, step)