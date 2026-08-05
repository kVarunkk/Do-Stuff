import json
from typing import Literal

def format_transcript(
    steps_history: list[dict],
    type: Literal["memory_update", "skill_update"],
    max_result_chars: int = 1000,
) -> str:
    """Extracts and formats text messages, tool calls, and tool results from steps history.

    - type='memory_update': Formats only conversational text (User / Model).
    - type='skill_update': Formats text, function calls, and function results.
    """
    lines = []

    role_map_memory = {
        "user_input": "User",
        "model_output": "Model",
    }

    role_map_skill = {
        "user_input": "User",
        "model_output": "Model",
        "function_call": "Function Call",
        "function_result": "Function Result",
    }

    active_role_map = (
        role_map_memory if type == "memory_update" else role_map_skill
    )

    for step in steps_history:
        step_type = step.get("type", "")

        # Skip step completely if its type isn't relevant to the current mode
        if step_type not in active_role_map:
            continue

        role = active_role_map[step_type]

        # -------------------------------------------------------------------------
        # Case A: Top-level Function Call Step
        # Schema: {"type": "function_call", "name": "...", "arguments": {...}, "id": "..."}
        # -------------------------------------------------------------------------
        if step_type == "function_call":
            fn_name = step.get("name", "unknown_function")
            args = step.get("arguments", {})
            args_str = json.dumps(args) if isinstance(args, dict) else str(args)
            lines.append(f"{role} ({fn_name}): {args_str}")
            continue

        # -------------------------------------------------------------------------
        # Case B: Top-level Function Result Step
        # Schema: {"type": "function_result", "name": "...", "result": ..., "id": "..."}
        # -------------------------------------------------------------------------
        if step_type == "function_result":
            fn_name = step.get("name", "unknown_function")
            raw_result = step.get("result", "")

            result_str = (
                json.dumps(raw_result)
                if isinstance(raw_result, (dict, list))
                else str(raw_result)
            )

            # Truncate long tool outputs to avoid exhausting context/token budget
            if len(result_str) > max_result_chars:
                result_str = (
                    result_str[:max_result_chars]
                    + f"... [Truncated {len(result_str) - max_result_chars} chars]"
                )

            lines.append(f"{role} ({fn_name}): {result_str}")
            continue

        # -------------------------------------------------------------------------
        # Case C: User Input / Model Output Steps with nested content array
        # Schema: {"type": "user_input"|"model_output", "content": [{"type": "text", "text": "..."}]}
        # -------------------------------------------------------------------------
        content_items = step.get("content", [])
        if not isinstance(content_items, list):
            continue

        text_parts = [
            item.get("text", "")
            for item in content_items
            if isinstance(item, dict)
            and item.get("type") == "text"
            and item.get("text")
        ]

        if text_parts:
            combined_text = "\n".join(text_parts).strip()
            if combined_text:
                lines.append(f"{role}: {combined_text}")

    return "\n".join(lines)