"""Observability hooks for the Rilavo verifier (Track D1 proposal).

INSTRUMENTATION ONLY -- adds zero protocol surface: no verifier semantics,
wire format, or return values are touched. The recorder is an OPTIONAL
wrapper (`timed_verify`) around the unchanged `do_verify` path; nothing in
the core modules imports this file.

Exports:
  - Prometheus text exposition format (counters + duration histogram)
  - JSON snapshot (counts by reason, latency percentiles)

All metric names are prefixed `rilavo_`. Labels: `reason` (the stable reject/
accept codes from rilavo.errors). No credential content, principal ids, or
nonces ever enter a metric label or value -- observability must not become a
secondary identity database (P-10 discipline applied to telemetry).
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

METRIC_PREFIX = "rilavo"

# Duration histogram bucket upper bounds, seconds (Prometheus `le` labels).
DEFAULT_BUCKETS = (0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25,
                   0.5, 1.0, 2.5, 5.0, 10.0)


@dataclass
class _DurationSeries:
    buckets: tuple = DEFAULT_BUCKETS
    counts: list = field(default_factory=list)     # per-bucket cumulative
    total_count: int = 0
    total_sum: float = 0.0

    def observe(self, value: float) -> None:
        if not self.counts:
            self.counts = [0] * len(self.buckets)
        for i, bound in enumerate(self.buckets):
            if value <= bound:
                self.counts[i] += 1
        self.total_count += 1
        self.total_sum += value

    def prometheus_text(self) -> str:
        """Export duration histogram in Prometheus text exposition format (v0.0.4)."""
        lines = []
        safe_name = "rilavo_verify_duration_seconds"
        lines.append(f"# HELP {safe_name} Verification latency.")
        lines.append(f"# TYPE {safe_name} histogram")
        if self.counts:
            cumulative = 0
            for bound, count in zip(self.buckets, self.counts):
                cumulative += count
                le = str(bound) if bound != float("inf") else "+Inf"
                lines.append(f'{safe_name}_bucket{{le="{le}"}} {cumulative}')
        else:
            for bound in self.buckets:
                le = str(bound) if bound != float("inf") else "+Inf"
                lines.append(f'{safe_name}_bucket{{le="{le}"}} 0')
        lines.append(f'{safe_name}_bucket{{le="+Inf"}} {self.total_count}')
        lines.append(f'{safe_name}_sum {self.total_sum:.6f}')
        lines.append(f'{safe_name}_count {self.total_count}')
        return "\n".join(lines) + "\n"



class Metrics:
    """Thread-safe in-process metrics store."""

    def __init__(self, buckets: tuple = DEFAULT_BUCKETS) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int))
        self.durations = _DurationSeries(buckets=buckets)

    # -- recording ----------------------------------------------------------
    def inc(self, name: str, labels: dict | None = None, value: int = 1) -> None:
        label_key = self._label_key(labels)
        with self._lock:
            self._counters[name][label_key] += value

    def observe_duration(self, name: str, seconds: float,
                         labels: dict | None = None) -> None:
        del labels  # duration series carries no labels at v0
        with self._lock:
            self.durations.observe(seconds)

    @staticmethod
    def _label_key(labels: dict | None) -> str:
        if not labels:
            return ""
        return ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))

    # -- sink interface (D1 extension) ----------------------------------------
    def record_count(self, name: str, labels: dict | None = None,
                     value: int = 1) -> None:
        self.inc(name, labels, value)

    def record_duration(self, name: str, seconds: float,
                        labels: dict | None = None) -> None:
        self.observe_duration(name, seconds)

    # -- exports -------------------------------------------------------------
    def json_export(self) -> dict:
        with self._lock:
            counters = {name: dict(labels) for name, labels in self._counters.items()}
            d = self.durations
            hist = ({str(b): c for b, c in zip(d.buckets, d.counts)}
                    if d.counts else {})
        return {
            "format": "rilavo-observability-v0",
            "counters": counters,
            "duration_histogram": {
                "buckets_le": hist,
                "count": d.total_count,
                "sum": round(d.total_sum, 6),
            },
        }

    def prometheus(self) -> str:
        """Prometheus text exposition format (v0.0.4)."""
        with self._lock:
            lines = []
            total_name = f"{METRIC_PREFIX}_verifications_total"
            lines += [f"# HELP {total_name} Verification outcomes by reason.",
                      f"# TYPE {total_name} counter"]
            for name, labels in sorted(self._counters.items()):
                for label_key, value in sorted(labels.items()):
                    metric = name.replace(f"{METRIC_PREFIX}_", "",
                                          1) if name.startswith(
                        METRIC_PREFIX) else name
                    lines.append(f"{total_name}{{{label_key}}} {value}"
                                 if label_key else f"{total_name} {value}")
            d = self.durations
            hist_name = f"{METRIC_PREFIX}_verify_duration_seconds"
            lines += [f"# HELP {hist_name} Verification latency.",
                      f"# TYPE {hist_name} histogram"]
            cumulative = 0
            if d.counts:
                for bound, c in zip(d.buckets, d.counts):
                    cumulative = c
                    lines.append(f'{hist_name}_bucket{{le="{bound}"}} {c}')
            else:
                for bound in d.buckets:
                    lines.append(f'{hist_name}_bucket{{le="{bound}"}} 0')
            lines.append(f'{hist_name}_bucket{{le="+Inf"}} {d.total_count}')
            lines.append(f"{hist_name}_sum {round(d.total_sum, 6)}")
            lines.append(f"{hist_name}_count {d.total_count}")
            return "\n".join(lines) + "\n"



    def prometheus_text(self) -> str:
        """Export metrics in Prometheus text exposition format (v0.0.4)."""
        lines = []
        with self._lock:
            # Counters
            for name, label_map in self._counters.items():
                safe_name = name.replace(".", "_").replace("-", "_")
                for label_key, value in label_map.items():
                    if label_key:
                        lines.append(f'{safe_name}{{{label_key}}} {value}')
                    else:
                        lines.append(f'{safe_name} {value}')

            # Duration histogram
            if self.durations.total_count > 0:
                safe_name = "rilavo_verify_duration_seconds"
                # Count per bucket
                cumulative = 0
                for i, bound in enumerate(self.durations.buckets):
                    cumulative += self.durations.counts[i]
                    le = str(bound) if bound != float("inf") else "+Inf"
                    lines.append(f'{safe_name}_bucket{{le="{le}"}} {cumulative}')
                lines.append(f'{safe_name}_bucket{{le="+Inf"}} {self.durations.total_count}')
                lines.append(f'{safe_name}_count {self.durations.total_count}')
                lines.append(f'{safe_name}_sum {self.durations.total_sum}')

        return "\n".join(lines) + "\n"

def timed_verify(metrics: Metrics, do_verify_callable, *,
                 credential, request, verifier_id: str,
                 key_directory, revocation_log, **kwargs):
    """OPTIONAL instrumentation wrapper. Calls do_verify unchanged, measures
    wall time, records outcome by reason code. Returns the VerifyResult
    object itself -- zero impact on caller-visible behavior."""
    t0 = time.perf_counter_ns()
    result = do_verify_callable(credential=credential, request=request,
                                verifier_id=verifier_id,
                                key_directory=key_directory,
                                revocation_log=revocation_log, **kwargs)
    dt = (time.perf_counter_ns() - t0) / 1e9
    metrics.inc("rilavo_verifications_total",
                {"reason": result.reason_code})
    metrics.observe_duration("rilavo_verify_duration_seconds", dt)
    return result


def timed_verify_raising(metrics: Metrics, verify_fn, **kwargs):
    """Variant for the raising `verify()` entry point: converts failures into
    counter increments with the exception's reason code, then re-raises."""
    t0 = time.perf_counter_ns()
    try:
        result = verify_fn(**kwargs)
    except __import__("rilavo.errors", fromlist=["VerificationError"]).VerificationError as exc:
        dt = (time.perf_counter_ns() - t0) / 1e9
        metrics.inc("rilavo_verifications_total", {"reason": exc.reason_code})
        metrics.observe_duration("rilavo_verify_duration_seconds", dt)
        raise
    dt = (time.perf_counter_ns() - t0) / 1e9
    metrics.inc("rilavo_verifications_total", {"reason": "accept"})
    metrics.observe_duration("rilavo_verify_duration_seconds", dt)
    return result



# --------------------------------------------------------------------------
# Pluggable sink interface (extended D1): anything implementing record_count /
# record_duration can receive telemetry. NullSink is the DEFAULT: calling it
# is a no-op, so unconfigured deployments behave byte-identically to before
# this module existed.
# --------------------------------------------------------------------------

class NullSink:
    """Default sink: accepts every record and does nothing. Zero overhead by
    design -- this is what makes OFF-mode identical to pre-instrumentation."""

    def record_count(self, name: str, labels: dict | None = None,
                     value: int = 1) -> None:
        return None

    def record_duration(self, name: str, seconds: float,
                        labels: dict | None = None) -> None:
        return None


class Sink(NullSink):
    """Interface documentation subclass: implement record_count and/or
    record_duration to receive telemetry."""

    def record(self, kind: str, name: str, value: float,
               labels: dict | None = None) -> None:
        if kind == "count":
            self.record_count(name, labels, int(value))
        else:
            self.record_duration(name, value, labels)


def json_log_line(event: str, fields: dict | None = None,
                  at: float | None = None) -> str:
    """Structured-log line formatter (JSON single-line). Pure function."""
    import json as _json
    payload = {"event": event,
               "ts": at if at is not None else time.time()}
    if fields:
        payload.update(fields)
    return _json.dumps(payload, separators=(",", ":"), sort_keys=True)


class LoggingSink(NullSink):
    """Sink that emits one structured JSON line per record through a
    caller-supplied emit callable (default: collect into a list)."""

    def __init__(self, emit=None) -> None:
        self._emit = emit or (lambda line: None)
        self.lines: list[str] = []

    def record_count(self, name: str, labels: dict | None = None,
                     value: int = 1) -> None:
        line = json_log_line("counter", {"name": name, "value": value,
                                         **(labels or {})})
        self.lines.append(line)
        self._emit(line)

    def record_duration(self, name: str, seconds: float,
                        labels: dict | None = None) -> None:
        line = json_log_line("duration", {"name": name,
                                          "seconds": round(seconds, 6),
                                          **(labels or {})})
        self.lines.append(line)
        self._emit(line)


def instrumented_do_verify(metrics_sink, do_verify_callable, *,
                           credential, request, verifier_id: str,
                           key_directory, revocation_log, **kwargs):
    """Pure-observation wrapper around do_verify: measures latency and counts
    the outcome by reason code, feeding ANY sink (Metrics, LoggingSink,
    NullSink). Returns do_verify's VerifyResult object UNCHANGED -- acceptance
    semantics are untouched by construction because the call itself is not
    wrapped in any try/except that could alter outcomes."""
    t0 = time.perf_counter_ns()
    result = do_verify_callable(
        credential=credential, request=request, verifier_id=verifier_id,
        key_directory=key_directory, revocation_log=revocation_log,
        **({"nonces": kwargs["nonces"]} if "nonces" in kwargs else {}),
        **({"receipts": kwargs["receipts"]} if "receipts" in kwargs else {}),
        **({"now": kwargs["now"]} if "now" in kwargs else {}))
    dt = (time.perf_counter_ns() - t0) / 1e9
    metrics_sink.record_count("rilavo_verifications_total",
                              {"reason": result.reason_code})
    metrics_sink.record_duration("rilavo_verify_duration_seconds", dt)
    return result


# =============================================================================
# Prometheus Metrics Export (Cycle 55)
# =============================================================================

class MetricsServer:
    """Threaded HTTP server exposing Prometheus metrics on /metrics endpoint.

    Binds to localhost by default for security. Use network policy to control
    external access in Kubernetes.
    """

    def __init__(self, metrics: Metrics, host: str = "127.0.0.1", port: int = 9090):
        self.metrics = metrics
        self.host = host
        self.port = port
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def start(self) -> None:
        """Start the metrics server in a background thread."""
        if self._running:
            return

        from http.server import HTTPServer, BaseHTTPRequestHandler
        import threading
        import socket

        class MetricsHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/metrics":
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
                    self.end_headers()
                    output = self.server.metrics_collector.prometheus_text()
                    self.wfile.write(output.encode("utf-8"))
                elif self.path == "/healthz":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"status":"ok"}')
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                # Suppress default log messages
                pass

        class ReuseAddrHTTPServer(HTTPServer):
            def server_bind(self):
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                super().server_bind()

        self._server = ReuseAddrHTTPServer((self.host, self.port), MetricsHandler)
        self._server.metrics_collector = self.metrics  # type: ignore[attr-defined]

        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        self._running = True

    def stop(self) -> None:
        """Stop the metrics server."""
        if self._running and self._server:
            self._server.shutdown()
            self._server.server_close()
            self._running = False


def start_metrics_server(metrics: Metrics, host: str = "127.0.0.1", port: int = 9090) -> MetricsServer:
    """Convenience function to start a metrics server."""
    server = MetricsServer(metrics, host, port)
    server.start()
    return server


# Global metrics instance for convenience
_global_metrics: Metrics | None = None

def get_metrics() -> Metrics:
    """Get the global metrics instance (singleton)."""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = Metrics()
    return _global_metrics
