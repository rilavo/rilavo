---
title: OpenTelemetry Observability Integration
status: Proposed
date: 2024-03-15
deciders: [Rilavo Core Team]
consulted: [SRE Team, SDK Maintainers]
informed: [All Contributors]
---

# ADR-009: OpenTelemetry Observability Integration

## Context and Problem Statement

Rilavo SDKs and services need production-grade observability for monitoring, debugging, and performance optimization. OpenTelemetry (OTel) is the industry standard for vendor-neutral observability.

## Decision Drivers

- Vendor-neutral instrumentation (OpenTelemetry)
- Distributed tracing across SDKs and services
- Metrics for verification latency, error rates, throughput
- Structured logging with correlation IDs
- Vendor-agnostic (supports Prometheus, Jaeger, Zipkin, DataDog, etc.)
- Auto-instrumentation where possible

## Considered Options

### Option 1: Custom Metrics/Logging per SDK

Each SDK implements its own metrics and logging.

**Pros:**
- Full control
- No external dependencies

**Cons:**
- Inconsistent metrics across SDKs
- Vendor lock-in for observability backends
- Duplicate effort
- Hard to correlate across services

### Option 2: OpenTelemetry SDKs (Chosen)

Use OpenTelemetry SDKs for each language with consistent semantic conventions.

**Pros:**
- Vendor-neutral
- Consistent semantic conventions (semconv)
- Rich ecosystem (collectors, exporters, operators)
- Auto-instrumentation for common frameworks
- Correlatable traces across SDKs and services
- CNCF graduated project

**Cons:**
- Adds dependencies
- Learning curve
- Configuration complexity

### Option 3: Prometheus Client Libraries Only

Use Prometheus client libraries directly for metrics.

**Pros:**
- Simpler than full OTel
- Native Prometheus integration

**Cons:**
- No distributed tracing
- Vendor lock-in to Prometheus
- No standard semantic conventions
- Manual instrumentation required

## Decision Outcome

Chosen option: **Option 2: OpenTelemetry SDKs** because it provides vendor-neutral, comprehensive observability with distributed tracing, metrics, and logging using industry-standard semantic conventions.

### Implementation Approach

1. **Python SDK**: `opentelemetry-sdk`, `opentelemetry-instrumentation-*`
2. **TypeScript SDK**: `@opentelemetry/sdk-node`, `@opentelemetry/instrumentation-*`
3. **Go SDK**: `go.opentelemetry.io/otel`, `go.opentelemetry.io/contrib/instrumentation`
4. **Next.js Middleware**: `@opentelemetry/instrumentation-http`, `@opentelemetry/instrumentation-nextjs`
5. **WordPress**: OpenTelemetry PHP SDK
6. **Service**: Full OTel with Prometheus exporter, Jaeger/OTLP exporter

### Semantic Conventions

- `rilavo.verification.duration` - Histogram (ms)
- `rilavo.verification.result` - Counter (accepted/rejected by reason)
- `rilavo.credential.issued` - Counter
- `rilavo.replay.detected` - Counter
- `rilavo.nonce_cache.size` - Gauge
- `rilavo.issuer_directory.lookups` - Counter
- `http.request.duration` - Standard HTTP semconv

### Trace Context Propagation

- W3C Trace Context headers (`traceparent`, `tracestate`)
- Propagate across SDK boundaries
- Correlation IDs in logs

### Positive Consequences

- Unified observability across all SDKs and services
- Vendor flexibility (switch backends without code changes)
- Rich ecosystem (collectors, operators, dashboards)
- Correlation of traces across SDK boundaries
- Standard semantic conventions

### Negative Consequences

- Added dependencies (OTel SDKs)
- Configuration complexity
- Performance overhead (minimal with sampling)
- Learning curve for team

## Implementation Plan

1. Add OTel dependencies to all SDKs
2. Implement verification tracing (span per verification)
3. Add metrics for verification latency, results, errors
4. Add structured logging with trace correlation
4. Configure OTel Collector for production
5. Add Grafana dashboards
6. Add alerting rules (PrometheusRule)

## Links

- [OpenTelemetry](https://opentelemetry.io/)
- [Semantic Conventions](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/semantic_conventions/README.md)
