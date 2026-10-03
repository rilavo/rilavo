package rilavo

import (
	"context"
	"net/http"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/metric"
	"go.opentelemetry.io/otel/propagation"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.21.0"
	"go.opentelemetry.io/otel/trace"

	"github.com/prometheus/client_golang/prometheus/promhttp"
	)

const (
	serviceName    = "rilavo"
	serviceVersion = "0.1.0"

	VerificationDuration = "rilavo.verification.duration"
	VerificationResult   = "rilavo.verification.result"
	CredentialIssued     = "rilavo.credential.issued"
	ReplayDetected       = "rilavo.replay.detected"
	NonceCacheSize       = "rilavo.nonce_cache.size"
	IssuerDirectoryLookups = "rilavo.issuer_directory.lookups"

	VerificationReason   = "rilavo.verification.reason"
	VerificationAccepted = "rilavo.verification.accepted"
	CredentialIssuer     = "rilavo.credential.issuer"
	CredentialAgent      = "rilavo.credential.agent"
)

var (
	tracer trace.Tracer
	meter  metric.Meter
	initialized bool

	verificationDuration metric.Float64Histogram
	verificationResultCounter metric.Int64Counter
	credentialIssuedCounter metric.Int64Counter
	replayDetectedCounter metric.Int64Counter
	nonceCacheSizeGauge metric.Int64UpDownCounter
	issuerDirectoryLookupsCounter metric.Int64Counter
)

func init() {
	InitializeInstrumentation()
}

type instrumentationConfig struct {
	serviceName      string
	serviceVersion   string
	otlpEndpoint     string
	enablePrometheus bool
	enableOtlp       bool
}

func InitializeInstrumentation(opts ...func(*instrumentationConfig)) {
	if initialized {
		return
	}

	cfg := &instrumentationConfig{
		serviceName:      "rilavo",
		serviceVersion:   "0.1.0",
		enablePrometheus: true,
		enableOtlp:       false,
	}

	_ = cfg // suppress unused variable warning

	res, err := resource.New(context.Background(),
		resource.WithAttributes(
			semconv.ServiceName("rilavo"),
			semconv.ServiceVersion("0.1.0"),
		))
	if err != nil {
		panic(err)
	}

	traceProvider := sdktrace.NewTracerProvider(
		sdktrace.WithResource(res),
	)
	otel.SetTracerProvider(traceProvider)
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{},
		propagation.Baggage{},
	))
	tracer = otel.Tracer("rilavo")

	// Set up meter provider (no periodic reader needed for Prometheus)
	// Metrics will be exposed via Prometheus HTTP handler
	meterProvider := sdkmetric.NewMeterProvider(
		sdkmetric.WithResource(res),
	)

	// Start Prometheus metrics HTTP server
	// Note: OTel metrics are registered with global meter provider
	// Prometheus will scrape from the HTTP handler
	go func() {
		http.Handle("/metrics", promhttp.Handler())
		http.ListenAndServe(":9090", nil)
	}()
	otel.SetMeterProvider(meterProvider)
	meter = otel.Meter("rilavo")

	initialized = true
	initMetrics()
}

func initMetrics() {
	verificationDuration, _ = meter.Float64Histogram(
		"rilavo.verification.duration",
		metric.WithDescription("Duration of credential verification in milliseconds"),
		metric.WithUnit("ms"),
	)
	verificationResultCounter, _ = meter.Int64Counter(
		"rilavo.verification.result",
		metric.WithDescription("Total number of credential verifications by result"),
	)
	credentialIssuedCounter, _ = meter.Int64Counter(
		"rilavo.credential.issued",
		metric.WithDescription("Total number of credentials issued"),
	)
	replayDetectedCounter, _ = meter.Int64Counter(
		"rilavo.replay.detected",
		metric.WithDescription("Total number of replay attacks detected"),
	)
	nonceCacheSizeGauge, _ = meter.Int64UpDownCounter(
		"rilavo.nonce_cache.size",
		metric.WithDescription("Current size of nonce cache"),
	)
	issuerDirectoryLookupsCounter, _ = meter.Int64Counter(
		"rilavo.issuer_directory.lookups",
		metric.WithDescription("Total number of issuer directory lookups"),
	)
}

type VerificationMetrics struct {
	Accepted      bool
	ReasonCode    string
	DurationMs    float64
	CredentialIssuer string
}

func RecordVerification(m VerificationMetrics) {
	if !initialized {
		return
	}

	attrs := []attribute.KeyValue{
		attribute.Bool("rilavo.verification.accepted", m.Accepted),
	}
	if m.ReasonCode != "" {
		attrs = append(attrs, attribute.String("rilavo.verification.reason", m.ReasonCode))
	}
	if m.CredentialIssuer != "" {
		attrs = append(attrs, attribute.String("rilavo.credential.issuer", m.CredentialIssuer))
	}

	if verificationDuration != nil {
		verificationDuration.Record(context.Background(), m.DurationMs)
	}
	if verificationResultCounter != nil {
		verificationResultCounter.Add(context.Background(), 1, metric.WithAttributes(attrs...))
	}
}

func RecordCredentialIssued(issuer, agent string) {
	if !initialized {
		return
	}
	if credentialIssuedCounter != nil {
		credentialIssuedCounter.Add(context.Background(), 1,
			metric.WithAttributes(
				attribute.String("rilavo.credential.issuer", issuer),
				attribute.String("rilavo.credential.agent", agent),
			),
		)
	}
}

func RecordReplayDetected(issuer string) {
	if !initialized {
		return
	}
	if replayDetectedCounter != nil {
		replayDetectedCounter.Add(context.Background(), 1,
			metric.WithAttributes(
				attribute.String("rilavo.credential.issuer", issuer),
			),
		)
	}
}

func SetNonceCacheSize(size int64) {
	if !initialized {
		return
	}
	if nonceCacheSizeGauge != nil {
		nonceCacheSizeGauge.Add(context.Background(), size)
	}
}

func RecordIssuerDirectoryLookup(issuerId string, found bool) {
	if !initialized {
		return
	}
	if issuerDirectoryLookupsCounter != nil {
		issuerDirectoryLookupsCounter.Add(context.Background(), 1,
			metric.WithAttributes(
				attribute.String("issuer_id", issuerId),
				attribute.Bool("found", found),
			),
		)
	}
}

func Tracer() trace.Tracer {
	if !initialized {
		InitializeInstrumentation()
	}
	return tracer
}

func Meter() metric.Meter {
	if !initialized {
		InitializeInstrumentation()
	}
	return meter
}

func Shutdown() {
	initialized = false
}
