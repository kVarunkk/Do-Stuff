from lib.genai_client import get_client
import json
import os
from dotenv import load_dotenv

load_dotenv()  
model = os.getenv("MODEL")

def estimate_tokens(step: dict) -> int:
    """Rough token estimate for a single step dict. Not exact — real tokenization
    isn't a fixed chars-per-token ratio — but good enough for deciding a trim boundary.
    """
    text = json.dumps(step, default=str)
    return len(text) // 4


def split_by_token_budget(
    steps_history: list[dict], keep_token_budget: int
) -> tuple[list[dict], list[dict]]:
    """Walks backward from the end of steps_history, accumulating steps until the
    token budget is used up. Always keeps at least one step, even if it alone
    exceeds the budget.

    Returns:
        (old_steps, recent_steps) — old_steps are candidates for summarization,
        recent_steps are kept verbatim.
    """
    recent_steps = []
    running_total = 0

    for i in range(len(steps_history) - 1, -1, -1):
        step = steps_history[i]
        step_tokens = estimate_tokens(step)

        if running_total + step_tokens > keep_token_budget and recent_steps:
            # don't cut here if it would leave an incomplete function-call sequence
            if recent_steps[0].get("type") in ("function_call", "function_result", "thought"):
                recent_steps.insert(0, step)
                running_total += step_tokens
                continue
            break

        recent_steps.insert(0, step)
        running_total += step_tokens

    split_index = len(steps_history) - len(recent_steps)
    return steps_history[:split_index], steps_history[split_index:]


async def compact_context(steps_history: list[dict], keep_token_budget: int) -> tuple[list[dict], str]:
    """Produces a compacted view of steps_history for sending to the model, without
    mutating the original list — callers should keep the full steps_history intact
    for the durable store/audit trail, and only use the returned recent_steps for
    the actual call_agent request.

    Args:
        steps_history: The full, uncompacted conversation history.

    Returns:
        (recent_steps, summary_text) — recent_steps is the trimmed step list to
        send to the model; summary_text is a compact summary of everything older,
        meant to be appended to the system instruction (empty string if no
        compaction was needed).
    """
    old_steps, recent_steps = split_by_token_budget(steps_history, keep_token_budget)

    if not old_steps:
        return steps_history, ""

    client = get_client()

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
    summary_text = getattr(summary_interaction, "output_text", "") or ""

    return recent_steps, summary_text