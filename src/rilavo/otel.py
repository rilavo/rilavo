"""
OpenTelemetry instrumentation for Rilavo Python SDK.

Provides tracing, metrics, and structured logging for verification operations.
"""

from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Semantic conventions for Rilavo
RILAVO_SERVICE_NAME = "rilavo"
RILAVO_SERVICE_VERSION = "0.1.0"

# Metric names (following semantic conventions)
VERIFICATION_DURATION = "rilavo.verification.duration"
VERIFICATION_RESULT = "rilavo.verification.result"
CREDENTIAL_ISSUED = "rilavo.credential.issued"
REPLAY_DETECTED = "rilavo.replay.detected"
NONCE_CACHE_SIZE = "rilavo.nonce_cache.size"
ISSUER_DIRECTORY_LOOKUPS = "rilavo.issuer_directory.lookups"

# Attribute keys
VERIFICATION_REASON = "rilavo.verification.reason"
VERIFICATION_ACCEPTED = "rilavo.verification.accepted"
CREDENTIAL_ISSUER = "rilavo.credential.issuer"
CREDENTIAL_AGENT = "rilavo.credential.agent"


class RilavoInstrumentation:
    """Manages OpenTelemetry instrumentation for Rilavo."""

    def __init__(
        self,
        service_name: str = RILAVO_SERVICE_NAME,
        service_version: str = RILAVO_SERVICE_VERSION,
        otlp_endpoint: str | None = None,
        enable_prometheus: bool = True,
        enable_otlp: bool = False,
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        self.enable_prometheus = enable_prometheus
        self.enable_otlp = enable_otlp or bool(self.otlp_endpoint)

        self._tracer_provider: TracerProvider | None = None
        self._meter_provider: MeterProvider | None = None
        self._tracer: trace.Tracer | None = None
        self._meter: metrics.Meter | None = None
        self._initialized = False

        # Metric instruments (lazy initialization)
        self._verification_duration: Any | None = None
        self._verification_result_counter: Any | None = None
        self._credential_issued_counter: Any | None = None
        self._replay_detected_counter: Any | None = None
        self._nonce_cache_size_gauge: Any | None = None
        self._issuer_directory_lookups_counter: Any | None = None

    def initialize(self) -> None:
        """Initialize OpenTelemetry instrumentation."""
        if self._initialized:
            return

        # Create resource
        resource = Resource.create({
            SERVICE_NAME: self.service_name,
            SERVICE_VERSION: self.service_version,
        })

        # Initialize tracing
        self._tracer_provider = TracerProvider(resource=resource)

        if self.enable_otlp and self.otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
            self._tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

        trace.set_tracer_provider(self._tracer_provider)
        self._tracer = trace.get_tracer(self.service_name, self.service_version)

        # Initialize metrics
        from opentelemetry.sdk.metrics.export import MetricReader
        readers: list[MetricReader] = []
        if self.enable_prometheus:
            readers.append(PrometheusMetricReader())

        if self.enable_otlp and self.otlp_endpoint:
            metric_exporter = OTLPMetricExporter(endpoint=self.otlp_endpoint)
            from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
            readers.append(PeriodicExportingMetricReader(metric_exporter))

        self._meter_provider = MeterProvider(resource=resource, metric_readers=readers)
        metrics.set_meter_provider(self._meter_provider)
        self._meter = metrics.get_meter(self.service_name, self.service_version)

        # Initialize logging instrumentation
        LoggingInstrumentor().instrument(set_logging_format=True)

        # Initialize metric instruments
        self._init_metrics()

        self._initialized = True

    def _init_metrics(self) -> None:
        """Initialize metric instruments."""
        if not self._meter:
            return

        self._verification_duration = self._meter.create_histogram(
            name=VERIFICATION_DURATION,
            description="Duration of credential verification in milliseconds",
            unit="ms",
        )

        self._verification_result_counter = self._meter.create_counter(
            name=VERIFICATION_RESULT,
            description="Total number of credential verifications by result",
            unit="1",
        )

        self._credential_issued_counter = self._meter.create_counter(
            name=CREDENTIAL_ISSUED,
            description="Total number of credentials issued",
            unit="1",
        )

        self._replay_detected_counter = self._meter.create_counter(
            name=REPLAY_DETECTED,
            description="Total number of replay attacks detected",
            unit="1",
        )

        self._nonce_cache_size_gauge = self._meter.create_up_down_counter(
            name=NONCE_CACHE_SIZE,
            description="Current size of nonce cache",
            unit="1",
        )

        self._issuer_directory_lookups_counter = self._meter.create_counter(
            name=ISSUER_DIRECTORY_LOOKUPS,
            description="Total number of issuer directory lookups",
            unit="1",
        )

    @property
    def tracer(self) -> trace.Tracer:
        """Get the tracer instance."""
        if not self._initialized:
            self.initialize()
        assert self._tracer is not None
        return self._tracer

    @property
    def meter(self) -> metrics.Meter:
        """Get the meter instance."""
        if not self._initialized:
            self.initialize()
        assert self._meter is not None
        return self._meter

    @contextmanager
    def verification_span(
        self,
        credential_issuer: str | None = None,
        credential_agent: str | None = None,
    ) -> Generator[trace.Span, None, None]:
        """Create a span for credential verification."""
        if not self._initialized:
            self.initialize()

        with self.tracer.start_as_current_span("verify_credential") as span:
            if credential_issuer:
                span.set_attribute(CREDENTIAL_ISSUER, credential_issuer)
            if credential_agent:
                span.set_attribute(CREDENTIAL_AGENT, credential_agent)
            yield span

    def record_verification(
        self,
        accepted: bool,
        reason_code: str | None = None,
        duration_ms: float = 0.0,
        credential_issuer: str | None = None,
    ) -> None:
        """Record verification result metrics."""
        if not self._initialized:
            self.initialize()

        attributes: dict[str, str] = {
            VERIFICATION_ACCEPTED: str(accepted).lower(),
        }
        if reason_code:
            attributes[VERIFICATION_REASON] = reason_code
        if credential_issuer:
            attributes[CREDENTIAL_ISSUER] = credential_issuer

        if self._verification_duration:
            self._verification_duration.record(duration_ms, attributes=attributes)

        if self._verification_result_counter:
            self._verification_result_counter.add(1, attributes=attributes)

    def record_credential_issued(self, issuer: str, agent: str) -> None:
        """Record credential issuance."""
        if not self._initialized:
            self.initialize()

        attributes: dict[str, str] = {
            CREDENTIAL_ISSUER: issuer,
            CREDENTIAL_AGENT: agent,
        }

        if self._credential_issued_counter:
            self._credential_issued_counter.add(1, attributes=attributes)

    def record_replay_detected(self, credential_issuer: str | None = None) -> None:
        """Record replay detection."""
        if not self._initialized:
            self.initialize()

        attributes: dict[str, str] = {}
        if credential_issuer:
            attributes[CREDENTIAL_ISSUER] = credential_issuer

        if self._replay_detected_counter:
            self._replay_detected_counter.add(1, attributes=attributes)

    def set_nonce_cache_size(self, size: int) -> None:
        """Update nonce cache size gauge."""
        if not self._initialized:
            self.initialize()

        if self._nonce_cache_size_gauge:
            self._nonce_cache_size_gauge.add(size)

    def record_issuer_directory_lookup(self, issuer_id: str, found: bool) -> None:
        """Record issuer directory lookup."""
        if not self._initialized:
            self.initialize()

        attributes: dict[str, str] = {
            "issuer_id": issuer_id,
            "found": str(found).lower(),
        }

        if self._issuer_directory_lookups_counter:
            self._issuer_directory_lookups_counter.add(1, attributes=attributes)

    def shutdown(self) -> None:
        """Shutdown instrumentation."""
        if self._tracer_provider:
            self._tracer_provider.shutdown()
        if self._meter_provider:
            self._meter_provider.shutdown()
        self._initialized = False


# Global instrumentation instance
_instrumentation: RilavoInstrumentation | None = None


def get_instrumentation() -> RilavoInstrumentation:
    """Get or create the global instrumentation instance."""
    global _instrumentation
    if _instrumentation is None:
        _instrumentation = RilavoInstrumentation()
    return _instrumentation


def initialize_instrumentation(
    service_name: str = RILAVO_SERVICE_NAME,
    service_version: str = RILAVO_SERVICE_VERSION,
    otlp_endpoint: str | None = None,
    enable_prometheus: bool = True,
    enable_otlp: bool = False,
) -> RilavoInstrumentation:
    """Initialize global instrumentation."""
    global _instrumentation
    _instrumentation = RilavoInstrumentation(
        service_name=service_name,
        service_version=service_version,
        otlp_endpoint=otlp_endpoint,
        enable_prometheus=enable_prometheus,
        enable_otlp=enable_otlp,
    )
    _instrumentation.initialize()
    return _instrumentation


# Convenience functions
def get_tracer() -> trace.Tracer:
    """Get the global tracer."""
    return get_instrumentation().tracer


def get_meter() -> metrics.Meter:
    """Get the global meter."""
    return get_instrumentation().meter


@contextmanager
def verification_span(
    credential_issuer: str | None = None,
    credential_agent: str | None = None,
) -> Generator[trace.Span, None, None]:
    """Create a verification span."""
    with get_instrumentation().verification_span(credential_issuer, credential_agent) as span:
        yield span


def record_verification(
    accepted: bool,
    reason_code: str | None = None,
    duration_ms: float = 0.0,
    credential_issuer: str | None = None,
) -> None:
    """Record verification result."""
    get_instrumentation().record_verification(accepted, reason_code, duration_ms, credential_issuer)


def record_credential_issued(issuer: str, agent: str) -> None:
    """Record credential issuance."""
    get_instrumentation().record_credential_issued(issuer, agent)


def record_replay_detected(credential_issuer: str | None = None) -> None:
    """Record replay detection."""
    get_instrumentation().record_replay_detected(credential_issuer)


def set_nonce_cache_size(size: int) -> None:
    """Update nonce cache size."""
    get_instrumentation().set_nonce_cache_size(size)


def record_issuer_directory_lookup(issuer_id: str, found: bool) -> None:
    """Record issuer directory lookup."""
    get_instrumentation().record_issuer_directory_lookup(issuer_id, found)


def shutdown_instrumentation() -> None:
    """Shutdown global instrumentation."""
    global _instrumentation
    if _instrumentation:
        _instrumentation.shutdown()
        _instrumentation = None
