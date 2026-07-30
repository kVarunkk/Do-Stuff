import json
from lib.genai_client import get_client
import os
from dotenv import load_dotenv

load_dotenv()  
model = os.getenv("MODEL")

client = get_client()

async def resolve_memory_operation(user_id: str, new_fact: dict, memory_store) -> None:
    similar = await memory_store.query(user_id, new_fact["value"], top_k=3)

    if not similar:
        await memory_store.upsert_fact(user_id, new_fact)
        print(f"FACT SAVED IN LONG TERM MEMORY-> OPERATION: SIMILAR NOT FOUND, KEY: {new_fact["key"] or "unknown"}, VALUE: {new_fact["value"]}")
        return

    decision_prompt = f"""You manage a user's long-term memory. Given a NEW fact and
EXISTING related memories, decide ONE operation:
- ADD: new fact is genuinely new information, unrelated to existing ones
- UPDATE: new fact replaces/refines one of the existing ones (same topic, more/updated info)
- NOOP: new fact is already captured by an existing memory, no change needed

Return JSON: {{"operation": "ADD"|"UPDATE"|"NOOP", "replace_key": "<existing key or null>"}}

NEW FACT: {new_fact["value"]}

EXISTING MEMORIES:
{json.dumps(similar, indent=2)}
"""

    interaction = await client.interactions.create(model=model, input=decision_prompt)
    output_text = getattr(interaction, "output_text", "") or ""
    cleaned = output_text.strip().removeprefix("```json").removesuffix("```").strip()
    decision = json.loads(cleaned)

    if decision["operation"] == "NOOP":
        return
    elif decision["operation"] == "UPDATE":
        key_to_replace = decision.get("replace_key") or new_fact["key"]
        await memory_store.upsert_fact(user_id, {"key": key_to_replace, "value": new_fact["value"]})
        print(f"FACT SAVED IN LONG TERM MEMORY-> OPERATION: UPDATE, KEY: {key_to_replace}, VALUE: {new_fact["value"]}")
    else:  # ADD
        await memory_store.upsert_fact(user_id, new_fact)
        print(f"FACT SAVED IN LONG TERM MEMORY-> OPERATION: ADD, KEY: {new_fact["key"] or "unknown"}, VALUE: {new_fact["value"]}")