from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SpanExporter, 
    SpanExportResult
)
import functools
import inspect
from typing import Any, Callable
from opentelemetry.trace import Status, StatusCode
import contextvars
import json

session_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("session_id", default="unknown")
turn_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("turn_id", default="unknown")

def _flatten(prefix, obj):

    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _flatten(f"{prefix}.{k}", v)
    else:
        yield prefix, obj

def _summarize_interaction(interaction) -> dict:
    steps = getattr(interaction, "steps", None) or []
    tool_calls = [
        {"name": s.name, "arguments": s.arguments}
        for s in steps
        if getattr(s, "type", None) == "function_call"
    ]
    text = getattr(interaction, "output_text", None)

    return {
        "status": getattr(interaction, "status", None),
        "output_text": text or None,
        "tool_calls": tool_calls,
    }        

def _set_input_attributes(span, kwargs: dict[str, Any]) -> None:
    """Best-effort: record simple kwargs as span attributes. Skip large/complex ones."""
    for key, value in _flatten("input", kwargs):
        if isinstance(value, (str, int, float, bool)):
            span.set_attribute(key, str(value))

def _set_output_attributes(span, result):

    if isinstance(result, (str, int, float, bool)):
        span.set_attribute("output", result)

    elif isinstance(result, (dict, list)):
        span.set_attribute(
            "output",
            json.dumps(result, default=str)
        )

    elif hasattr(result, "steps"):  # looks like an Interaction object
        span.set_attribute("output", json.dumps(_summarize_interaction(result)))    

    else:
        span.set_attribute(
            "output",
            repr(result)
        )

def traced(span_name: str | None = None):
    """Wraps a sync or async function in an OTel span, recording args/result/errors."""

    def decorator(fn: Callable) -> Callable:
        name = span_name or fn.__name__

        def _common_attrs(span):
            span.set_attribute("function", fn.__name__)
            span.set_attribute("session_id", session_id_var.get())
            span.set_attribute("turn_id", turn_id_var.get())

        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                # span.set_attribute("function", fn.__name__)
                _common_attrs(span)
                _set_input_attributes(span, kwargs)
                try:
                    result = await fn(*args, **kwargs)
                    _set_output_attributes(span, result)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                # span.set_attribute("function", fn.__name__)
                _common_attrs(span)
                _set_input_attributes(span, kwargs)
                try:
                    result = fn(*args, **kwargs)
                    _set_output_attributes(span, result)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        return async_wrapper if inspect.iscoroutinefunction(fn) else sync_wrapper

    return decorator


class JSONLFileExporter(SpanExporter):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def export(self, spans: Any) -> SpanExportResult:
        with open(self.filepath, "a") as f:
            for span in spans:
                context = getattr(span, "context", None)
                parent = getattr(span, "parent", None)
                start_time = getattr(span, "start_time", None)
                end_time = getattr(span, "end_time", None)

                status_code = getattr(getattr(span, "status", None), "status_code", None)
                status_name = status_code.name if status_code is not None else None

                record = {
                    "name": getattr(span, "name", None),
                    "trace_id": format(context.trace_id, "032x") if context is not None else None,
                    "span_id": format(context.span_id, "016x") if context is not None else None,
                    "parent_id": format(parent.span_id, "016x") if parent is not None else None,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration_ns": end_time - start_time if isinstance(start_time, int) and isinstance(end_time, int) else None,
                    "status": status_name,
                    "attributes": dict(getattr(span, "attributes", {}).items()),
                }
                f.write(json.dumps(record) + "\n")
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass        



provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(JSONLFileExporter("traces.jsonl")))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("agent") 