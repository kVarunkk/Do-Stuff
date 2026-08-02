from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    SpanExporter, 
    SpanExportResult
)
import functools
import inspect
from typing import Any, Callable
from opentelemetry.trace import Status, StatusCode
import contextvars
import json
from typing import Sequence
from opentelemetry.sdk.trace import ReadableSpan
import os 

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


class SingleFileOTLPExporter(SpanExporter):
    def __init__(self, filepath: str = "trace.json"):
        self.filepath = filepath
        self._captured_spans = []
        
        # 1. Load existing spans from disk if trace.json already exists
        if os.path.exists(self.filepath) and os.path.getsize(self.filepath) > 0:
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    # Extract previous spans from the OTLP structure
                    self._captured_spans = (
                        existing_data.get("resourceSpans", [])[0]
                        .get("scopeSpans", [])[0]
                        .get("spans", [])
                    )
            except (json.JSONDecodeError, KeyError, IndexError):
                # If file is empty or corrupted, start fresh
                self._captured_spans = []

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        # 2. Append new spans to the existing list
        for span in spans:
            context = span.context
            parent = span.parent

            otlp_attributes = []
            if span.attributes:
                for k, v in span.attributes.items():
                    if isinstance(v, bool):
                        val_obj = {"boolValue": v}
                    elif isinstance(v, int):
                        val_obj = {"intValue": str(v)}
                    elif isinstance(v, float):
                        val_obj = {"doubleValue": v}
                    else:
                        val_obj = {"stringValue": str(v)}
                    otlp_attributes.append({"key": k, "value": val_obj})

            trace_id = format(context.trace_id, "032x") if context is not None else ""
            span_id = format(context.span_id, "016x") if context is not None else ""

            otlp_span = {
                "traceId": trace_id,
                "spanId": span_id,
                "parentSpanId": format(parent.span_id, "016x") if parent else "",
                "name": span.name,
                "kind": 1,
                "startTimeUnixNano": str(span.start_time),
                "endTimeUnixNano": str(span.end_time),
                "attributes": otlp_attributes,
                "status": {
                    "code": 1 if span.status.is_ok else (2 if span.status.status_code.name == "ERROR" else 0)
                }
            }
            self._captured_spans.append(otlp_span)

        # 3. Write back the complete accumulated history into trace.json
        payload = {
            "resourceSpans": [
                {
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": {"stringValue": "my-agent"}}
                        ]
                    },
                    "scopeSpans": [
                        {
                            "scope": {"name": "agent-tracer"},
                            "spans": self._captured_spans
                        }
                    ]
                }
            ]
        }

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass


provider = TracerProvider()
exporter = SingleFileOTLPExporter(filepath="trace.json")
provider.add_span_processor(SimpleSpanProcessor(exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("agent") 