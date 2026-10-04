"""
OpenTelemetry Tracing for Rilavo (Cycle 55).

INSTRUMENTATION ONLY — adds zero protocol surface. Spans are internal
observability; no wire format, verifier semantics, or return values
are touched.

Configuration via environment variables:
  OTEL_EXPORTER_OTLP_ENDPOINT     OTLP HTTP endpoint (default: http://localhost:4318/v1/traces)
  OTEL_EXPORTER_OTLP_PROTOCOL     http/protobuf or http/json (default: http/protobuf)
  OTEL_SERVICE_NAME               service.name attribute (default: rilavo)
  OTEL_SAMPLING_RATE              trace sampling rate 0.0-1.0 (default: 0.01)
  OTEL_RESOURCE_ATTRIBUTES        additional resource attributes
"""

from __future__ import annotations

import os
import contextlib
from typing import Optional, TYPE_CHECKING
from contextvars import ContextVar

# Optional imports - OpenTelemetry is a soft dependency
OTEL_AVAILABLE = False
if TYPE_CHECKING:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.trace import SpanKind, Status, StatusCode
    from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
else:
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.sdk.resources import Resource, SERVICE_NAME
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.trace import SpanKind, Status, StatusCode
        from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
        OTEL_AVAILABLE = True
    except ImportError:
        trace = None  # type: ignore[assignment]
        TracerProvider = None  # type: ignore[assignment]
        BatchSpanProcessor = None  # type: ignore[assignment]
        ConsoleSpanExporter = None  # type: ignore[assignment]
        Resource = None  # type: ignore[assignment]
        SERVICE_NAME = None  # type: ignore[assignment]
        OTLPSpanExporter = None  # type: ignore[assignment]
        SpanKind = None  # type: ignore[assignment]
        Status = None  # type: ignore[assignment]
        StatusCode = None  # type: ignore[assignment]
        TraceIdRatioBased = None  # type: ignore[assignment]


# Current span context variable for manual span management
_current_span: ContextVar[Optional["trace.Span"]] = ContextVar("_current_span", default=None)

# Module-level tracer
_tracer: Optional["trace.Tracer"] = None
_provider_initialized = False


def init_tracing(
    service_name: str = "rilavo",
    endpoint: Optional[str] = None,
    sampling_rate: float = 0.01,
    resource_attributes: Optional[dict] = None,
) -> bool:
    """Initialize OpenTelemetry tracing.

    Returns True if initialized, False if OpenTelemetry not available.
    Safe to call multiple times; subsequent calls are no-ops.
    """
    global _tracer, _provider_initialized

    if not OTEL_AVAILABLE:
        return False

    if _provider_initialized:
        return True

    # Determine endpoint
    if endpoint is None:
        endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318/v1/traces")

    # Resource attributes
    attrs = {SERVICE_NAME: service_name}
    if resource_attributes:
        attrs.update(resource_attributes)
    # Add default attributes
    attrs.update({
        "service.version": os.environ.get("RILAVO_VERSION", "0.1.0"),
        "deployment.environment": os.environ.get("DEPLOYMENT_ENV", "development"),
    })

    resource = Resource.create(attrs)

    # Provider
    provider = TracerProvider(resource=resource)

    # Sampler
    provider.sampler = TraceIdRatioBased(sampling_rate)  # type: ignore[attr-defined]

    # Exporter
    if endpoint:
        otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    else:
        # Console exporter for development
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(__name__)
    _provider_initialized = True

    return True


def get_tracer() -> Optional["trace.Tracer"]:
    """Get the module tracer, initializing if needed."""
    global _tracer
    if _tracer is None and OTEL_AVAILABLE:
        init_tracing()
    return _tracer


@contextlib.contextmanager
def start_span(
    name: str,
    kind: Optional["SpanKind"] = None,
    attributes: Optional[dict] = None,
):
    """Context manager for creating a span.

    Usage:
        with start_span("verify_credential", attributes={"credential.issuer": iss}) as span:
            # do work
            span.set_attribute("result", "accepted")
    """
    if not OTEL_AVAILABLE or _tracer is None:
        yield None
        return

    if kind is None:
        kind = SpanKind.INTERNAL

    span = _tracer.start_span(name, kind=kind, attributes=attributes or {})
    token = _current_span.set(span)
    try:
        yield span
    except Exception as e:
        span.set_status(Status(StatusCode.ERROR, str(e)))
        span.record_exception(e)
        raise
    finally:
        span.end()
        _current_span.reset(token)


def get_current_span() -> Optional["trace.Span"]:
    """Get the current active span from context."""
    return _current_span.get()


def add_span_attributes(attributes: dict) -> None:
    """Add attributes to the current span."""
    span = get_current_span()
    if span:
        for k, v in attributes.items():
            span.set_attribute(k, v)


def record_span_event(name: str, attributes: Optional[dict] = None) -> None:
    """Record an event on the current span."""
    span = get_current_span()
    if span:
        span.add_event(name, attributes or {})


# Convenience functions for common Rilavo operations

@contextlib.contextmanager
def trace_verify_credential(credential_issuer: str, audience: str):
    """Trace a credential verification."""
    if not OTEL_AVAILABLE:
        yield None
        return

    with start_span(
        "rilavo.verify_credential",
        kind=SpanKind.SERVER,
        attributes={
            "rilavo.credential.issuer": credential_issuer,
            "rilavo.credential.audience": audience,
        },
    ) as span:
        yield span


@contextlib.contextmanager
def trace_issue_credential(principal: str, action_class: str, audience: str):
    """Trace a credential issuance."""
    if not OTEL_AVAILABLE:
        yield None
        return

    with start_span(
        "rilavo.issue_credential",
        kind=SpanKind.INTERNAL,
        attributes={
            "rilavo.credential.principal": principal,
            "rilavo.credential.action_class": action_class,
            "rilavo.credential.audience": audience,
        },
    ) as span:
        yield span


@contextlib.contextmanager
def trace_directory_lookup(issuer_id: str):
    """Trace a key directory lookup."""
    if not OTEL_AVAILABLE:
        yield None
        return

    with start_span(
        "rilavo.directory.lookup",
        kind=SpanKind.CLIENT,
        attributes={"rilavo.directory.issuer_id": issuer_id},
    ) as span:
        yield span


@contextlib.contextmanager
def trace_revocation_check(nonce: str):
    """Trace a revocation log check."""
    if not OTEL_AVAILABLE:
        yield None
        return

    with start_span(
        "rilavo.revocation.check",
        kind=SpanKind.CLIENT,
        attributes={"rilavo.revocation.nonce": nonce[:16]},  # Truncate for privacy
    ) as span:
        yield span


@contextlib.contextmanager
def trace_pop_verification(action_class: str):
    """Trace a proof-of-possession verification."""
    if not OTEL_AVAILABLE:
        yield None
        return

    with start_span(
        "rilavo.pop.verify",
        kind=SpanKind.SERVER,
        attributes={"rilavo.pop.action_class": action_class},
    ) as span:
        yield span


# Integration helpers for metrics

def trace_with_metrics(span_name: str, metrics_name: str, attributes: Optional[dict] = None):
    """Decorator combining span + metrics timing."""
    def decorator(func):
        import functools
        import time

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            with start_span(span_name, attributes=attributes) as span:
                try:
                    result = func(*args, **kwargs)
                    if span:
                        span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    if span:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                    raise
                finally:
                    duration = time.perf_counter() - start
                    # Record metric if metrics available
                    try:
                        from .observability import get_metrics
                        metrics = get_metrics()
                        if metrics:
                            metrics.observe_duration(metrics_name, duration, attributes)
                    except ImportError:
                        pass
        return wrapper
    return decorator
