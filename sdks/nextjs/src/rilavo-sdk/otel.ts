/**
 * OpenTelemetry instrumentation for Rilavo TypeScript SDK.
 * Provides tracing, metrics, and structured logging for verification operations.
 */

import { trace, metrics, Span, SpanOptions, Context } from '@opentelemetry/api';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { PrometheusExporter } from '@opentelemetry/exporter-prometheus';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';
import { NodeSDK } from '@opentelemetry/sdk-node';

// Semantic conventions for Rilavo
export const RILAVO_SERVICE_NAME = 'rilavo';
export const RILAVO_SERVICE_VERSION = '0.1.0';

// Metric names (following semantic conventions)
export const VERIFICATION_DURATION = 'rilavo.verification.duration';
export const VERIFICATION_RESULT = 'rilavo.verification.result';
export const CREDENTIAL_ISSUED = 'rilavo.credential.issued';
export const REPLAY_DETECTED = 'rilavo.replay.detected';
export const NONCE_CACHE_SIZE = 'rilavo.nonce_cache.size';
export const ISSUER_DIRECTORY_LOOKUPS = 'rilavo.issuer_directory.lookups';

// Attribute keys
export const VERIFICATION_REASON = 'rilavo.verification.reason';
export const VERIFICATION_ACCEPTED = 'rilavo.verification.accepted';
export const CREDENTIAL_ISSUER = 'rilavo.credential.issuer';
export const CREDENTIAL_AGENT = 'rilavo.credential.agent';

/**
 * Manages OpenTelemetry instrumentation for Rilavo TypeScript SDK.
 */
export class RilavoInstrumentation {
  private _sdk: any = null;
  private _tracer: any = null;
  private _meter: any = null;
  private _initialized = false;

  // Metric instruments (lazy initialization)
  private _verificationDuration: any = null;
  private _verificationResultCounter: any = null;
  private _credentialIssuedCounter: any = null;
  private _replayDetectedCounter: any = null;
  private _nonceCacheSizeGauge: any = null;
  private _issuerDirectoryLookupsCounter: any = null;

  constructor(
    private readonly serviceName: string = 'rilavo',
    private readonly serviceVersion: string = '0.1.0',
    private readonly otlpEndpoint?: string,
    private readonly enablePrometheus: boolean = true,
    private readonly enableOtlp: boolean = false,
  ) {}

  /**
   * Initialize OpenTelemetry instrumentation.
   */
  async initialize(): Promise<void> {
    if (this._initialized) return;

    const resource = new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: 'rilavo',
      [SemanticResourceAttributes.SERVICE_VERSION]: '0.1.0',
    });

    // Configure SDK - Prometheus exporter starts its own HTTP server
    const { PrometheusExporter } = await import('@opentelemetry/exporter-prometheus');

    const prometheusExporter = new PrometheusExporter(
      { port: 9464, endpoint: '/metrics' },
      () => { console.log('Prometheus exporter started on :9464/metrics'); }
    );

    // Note: PrometheusExporter is a push exporter that starts its own HTTP server
    // We don't use a PeriodicExportingMetricReader with it
    const sdkConfig: any = {
      resource,
      traceExporter: undefined,
      metricReader: undefined,
    };

    // Create and start SDK
    const sdk = new NodeSDK(sdkConfig);
    this._sdk = sdk.start();

    // Register HTTP instrumentation for auto-instrumentation
    registerInstrumentations({
      instrumentations: [
        new HttpInstrumentation(),
      ],
    });

    // Initialize tracer and meter
    this._tracer = trace.getTracer('rilavo', '0.1.0');
    this._meter = metrics.getMeter('rilavo', '0.1.0');

    // Initialize metric instruments
    this._initMetrics();

    this._initialized = true;
  }

  private _initMetrics(): void {
    if (!this._meter) return;

    this._verificationDuration = this._meter.createHistogram(
      'rilavo.verification.duration',
      {
        description: 'Duration of credential verification in milliseconds',
        unit: 'ms',
      }
    );

    this._verificationResultCounter = this._meter.createCounter(
      'rilavo.verification.result',
      {
        description: 'Total number of credential verifications by result',
        unit: '1',
      }
    );

    this._credentialIssuedCounter = this._meter.createCounter(
      'rilavo.credential.issued',
      {
        description: 'Total number of credentials issued',
        unit: '1',
      }
    );

    this._replayDetectedCounter = this._meter.createCounter(
      'rilavo.replay.detected',
      {
        description: 'Total number of replay attacks detected',
        unit: '1',
      }
    );

    this._nonceCacheSizeGauge = this._meter.createUpDownCounter(
      'rilavo.nonce_cache.size',
      {
        description: 'Current size of nonce cache',
        unit: '1',
      }
    );

    this._issuerDirectoryLookupsCounter = this._meter.createCounter(
      'rilavo.issuer_directory.lookups',
      {
        description: 'Total number of issuer directory lookups',
        unit: '1',
      }
    );
  }

  get tracer() {
    if (!this._initialized) this.initialize();
    return this._tracer!;
  }

  get meter() {
    if (!this._initialized) this.initialize();
    return this._meter!;
  }

  /**
   * Create a span for credential verification.
   */
  verificationSpan(
    credentialIssuer?: string,
    credentialAgent?: string,
  ): any {
    if (!this._initialized) this.initialize();

    return this.tracer.startActiveSpan('verify_credential', {
      attributes: {
        'rilavo.credential.issuer': credentialIssuer || '',
        'rilavo.credential.agent': credentialAgent || '',
      },
    });
  }

  /**
   * Record verification result metrics.
   */
  recordVerification(
    accepted: boolean,
    reasonCode: string | null = null,
    durationMs: number = 0,
    credentialIssuer?: string,
  ): void {
    if (!this._initialized) this.initialize();

    const attributes: Record<string, string | boolean> = {
      'rilavo.verification.accepted': accepted,
    };
    if (reasonCode) {
      attributes['rilavo.verification.reason'] = reasonCode;
    }
    if (credentialIssuer) {
      attributes['rilavo.credential.issuer'] = credentialIssuer;
    }

    if (this._verificationDuration) {
      this._verificationDuration.record(durationMs, { attributes });
    }

    if (this._verificationResultCounter) {
      this._verificationResultCounter.add(1, { attributes });
    }
  }

  recordCredentialIssued(issuer: string, agent: string): void {
    if (!this._initialized) this.initialize();

    const attributes = {
      'rilavo.credential.issuer': issuer,
      'rilavo.credential.agent': agent,
    };

    this._credentialIssuedCounter?.add(1, { attributes });
  }

  recordReplayDetected(credentialIssuer?: string): void {
    if (!this._initialized) this.initialize();

    const attributes: Record<string, string> = {};
    if (credentialIssuer) {
      attributes['rilavo.credential.issuer'] = credentialIssuer;
    }

    this._replayDetectedCounter?.add(1, { attributes });
  }

  setNonceCacheSize(size: number): void {
    if (!this._initialized) this.initialize();
    this._nonceCacheSizeGauge?.add(size);
  }

  recordIssuerDirectoryLookup(issuerId: string, found: boolean): void {
    if (!this._initialized) this.initialize();

    const attributes = {
      issuer_id: issuerId,
      found,
    };

    this._issuerDirectoryLookupsCounter?.add(1, { attributes });
  }

  shutdown(): void {
    this._sdk?.shutdown();
    this._initialized = false;
  }
}

// Global instrumentation instance
let _instrumentation: RilavoInstrumentation | null = null;

/**
 * Get or create the global instrumentation instance.
 */
export function getInstrumentation(): any {
  if (!_instrumentation) {
    _instrumentation = new RilavoInstrumentation();
  }
  return _instrumentation;
}

/**
 * Initialize global instrumentation.
 */
export async function initializeInstrumentation(
  serviceName: string = 'rilavo',
  serviceVersion: string = '0.1.0',
  otlpEndpoint?: string,
  enablePrometheus: boolean = true,
  enableOtlp: boolean = false,
): Promise<any> {
  const inst = new RilavoInstrumentation(
    serviceName,
    serviceVersion,
    otlpEndpoint,
    true, // enablePrometheus
    !!otlpEndpoint,
  );
  await inst.initialize();
  return inst;
}

// Convenience functions
export function getTracer() {
  return getInstrumentation().tracer;
}

export function getMeter() {
  return getInstrumentation().meter;
}

export function verificationSpan(
  credentialIssuer?: string,
  credentialAgent?: string,
): any {
  return getInstrumentation().verificationSpan(credentialIssuer, credentialAgent);
}

export function recordVerification(
  accepted: boolean,
  reasonCode: string | null = null,
  durationMs: number = 0,
  credentialIssuer?: string,
): void {
  getInstrumentation().recordVerification(accepted, reasonCode, durationMs, credentialIssuer);
}

export function recordCredentialIssued(issuer: string, agent: string): void {
  getInstrumentation().recordCredentialIssued(issuer, agent);
}

export function recordReplayDetected(credentialIssuer?: string): void {
  getInstrumentation().recordReplayDetected(credentialIssuer);
}

export function setNonceCacheSize(size: number): void {
  getInstrumentation().setNonceCacheSize(size);
}

export function recordIssuerDirectoryLookup(issuerId: string, found: boolean): void {
  getInstrumentation().recordIssuerDirectoryLookup(issuerId, found);
}

export function shutdownInstrumentation(): void {
  // Implementation would go here
}
