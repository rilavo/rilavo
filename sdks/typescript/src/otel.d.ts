/**
 * OpenTelemetry instrumentation for Rilavo TypeScript SDK.
 * Provides tracing, metrics, and structured logging for verification operations.
 */
export declare const RILAVO_SERVICE_NAME = "rilavo";
export declare const RILAVO_SERVICE_VERSION = "0.1.0";
export declare const VERIFICATION_DURATION = "rilavo.verification.duration";
export declare const VERIFICATION_RESULT = "rilavo.verification.result";
export declare const CREDENTIAL_ISSUED = "rilavo.credential.issued";
export declare const REPLAY_DETECTED = "rilavo.replay.detected";
export declare const NONCE_CACHE_SIZE = "rilavo.nonce_cache.size";
export declare const ISSUER_DIRECTORY_LOOKUPS = "rilavo.issuer_directory.lookups";
export declare const VERIFICATION_REASON = "rilavo.verification.reason";
export declare const VERIFICATION_ACCEPTED = "rilavo.verification.accepted";
export declare const CREDENTIAL_ISSUER = "rilavo.credential.issuer";
export declare const CREDENTIAL_AGENT = "rilavo.credential.agent";
/**
 * Manages OpenTelemetry instrumentation for Rilavo TypeScript SDK.
 */
export declare class RilavoInstrumentation {
    private readonly serviceName;
    private readonly serviceVersion;
    private readonly otlpEndpoint?;
    private readonly enablePrometheus;
    private readonly enableOtlp;
    private _sdk;
    private _tracer;
    private _meter;
    private _initialized;
    private _verificationDuration;
    private _verificationResultCounter;
    private _credentialIssuedCounter;
    private _replayDetectedCounter;
    private _nonceCacheSizeGauge;
    private _issuerDirectoryLookupsCounter;
    constructor(serviceName?: string, serviceVersion?: string, otlpEndpoint?: string | undefined, enablePrometheus?: boolean, enableOtlp?: boolean);
    /**
     * Initialize OpenTelemetry instrumentation.
     */
    initialize(): Promise<void>;
    private _initMetrics;
    get tracer(): any;
    get meter(): any;
    /**
     * Create a span for credential verification.
     */
    verificationSpan(credentialIssuer?: string, credentialAgent?: string): any;
    /**
     * Record verification result metrics.
     */
    recordVerification(accepted: boolean, reasonCode?: string | null, durationMs?: number, credentialIssuer?: string): void;
    recordCredentialIssued(issuer: string, agent: string): void;
    recordReplayDetected(credentialIssuer?: string): void;
    setNonceCacheSize(size: number): void;
    recordIssuerDirectoryLookup(issuerId: string, found: boolean): void;
    shutdown(): void;
}
/**
 * Get or create the global instrumentation instance.
 */
export declare function getInstrumentation(): any;
/**
 * Initialize global instrumentation.
 */
export declare function initializeInstrumentation(serviceName?: string, serviceVersion?: string, otlpEndpoint?: string, enablePrometheus?: boolean, enableOtlp?: boolean): Promise<any>;
export declare function getTracer(): any;
export declare function getMeter(): any;
export declare function verificationSpan(credentialIssuer?: string, credentialAgent?: string): any;
export declare function recordVerification(accepted: boolean, reasonCode?: string | null, durationMs?: number, credentialIssuer?: string): void;
export declare function recordCredentialIssued(issuer: string, agent: string): void;
export declare function recordReplayDetected(credentialIssuer?: string): void;
export declare function setNonceCacheSize(size: number): void;
export declare function recordIssuerDirectoryLookup(issuerId: string, found: boolean): void;
export declare function shutdownInstrumentation(): void;
