from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.trace import Status, StatusCode
import functools
import inspect
from typing import Any, Callable
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


# 1. Define Resource attributes (Service Name for Jaeger UI)
resource = Resource.create({
    SERVICE_NAME: "my-agent"
})

# 2. Initialize TracerProvider with Resource
provider = TracerProvider(resource=resource)

# 3. Configure the standard OTLP Exporter
otlp_exporter = OTLPSpanExporter(
    endpoint="localhost:4317", 
    insecure=True
)

# 4. Use BatchSpanProcessor for optimal async trace exporting
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

# 5. Set global tracer provider
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("agent")