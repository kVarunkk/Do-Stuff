from helpers.agent.constants import KEEP_RECENT_STEPS
from lib.genai_client import get_client
import json
import os
from dotenv import load_dotenv

load_dotenv()  
model = os.getenv("MODEL")

async def compact_context(steps_history: list[dict]) -> list[dict]:
    client = get_client()

    if len(steps_history) <= KEEP_RECENT_STEPS:
        return steps_history

    old_steps, recent_steps = steps_history[:-KEEP_RECENT_STEPS], steps_history[-KEEP_RECENT_STEPS:]

    summary_prompt = (
        "Summarize the key facts, decisions, and outcomes from this conversation "
        "history in a compact paragraph. Preserve names, dates, and any commitments "
        "made. Do not include reasoning or tool call mechanics.\n\n"
        f"{json.dumps(old_steps, default=str)}"
    )

    summary_interaction = await client.interactions.create(
        model=model,
        input=summary_prompt,
    )
    summary_text = getattr(summary_interaction, "output_text", "")

    summary_step = {
        "type": "user_input",  # or a system-style note, depending on what the API accepts as a role
        "content": [{"type": "text", "text": f"[Earlier conversation summary]: {summary_text}"}],
    }

    return [summary_step, *recent_steps]