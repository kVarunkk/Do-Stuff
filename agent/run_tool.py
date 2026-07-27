from helpers.agent.constants import TOOL_MAP
from typing import Any
from lib.tracing import traced
import inspect
import asyncio

@traced("tool_call")
async def run_tool(fn_name: str | None, fn_args: dict[str, Any]) -> Any:
    if not (isinstance(fn_name, str) and fn_name in TOOL_MAP):
        return f"Error: Tool {fn_name} not found."

    fn = TOOL_MAP[fn_name]

    try:
        if inspect.iscoroutinefunction(fn):
            return await fn(**fn_args)
        else:
            return await asyncio.to_thread(fn, **fn_args)
    except Exception as e:
        return e