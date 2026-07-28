from typing import Any
from lib.tracing import traced
from google.genai import types
from lib.genai_client import get_client
from tools.definitions import schedule_meeting_schema
from opentelemetry import trace as otel_trace
import os
from dotenv import load_dotenv

load_dotenv()  
model = os.getenv("MODEL")

@traced("model_call")
async def call_agent(steps_history: list[types.Step], system_instruction: str) -> Any:
    client = get_client()
    interaction = await client.interactions.create(
        model=model,
        input=steps_history,
        tools=[{"type": "function", **schedule_meeting_schema}],
        # opt out of server side state storage
        store=False,
        system_instruction=system_instruction,
    )

    usage = getattr(interaction, "usage", None)
    if usage is not None:
        span = otel_trace.get_current_span()
        span.set_attribute("usage.total_tokens", getattr(usage, "total_tokens", 0))
        span.set_attribute("usage.input_tokens", getattr(usage, "total_input_tokens", 0))
        span.set_attribute("usage.output_tokens", getattr(usage, "total_output_tokens", 0))


    return interaction