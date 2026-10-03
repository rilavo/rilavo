"use strict";
/**
 * OpenTelemetry instrumentation for Rilavo TypeScript SDK.
 * Provides tracing, metrics, and structured logging for verification operations.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.RilavoInstrumentation = exports.CREDENTIAL_AGENT = exports.CREDENTIAL_ISSUER = exports.VERIFICATION_ACCEPTED = exports.VERIFICATION_REASON = exports.ISSUER_DIRECTORY_LOOKUPS = exports.NONCE_CACHE_SIZE = exports.REPLAY_DETECTED = exports.CREDENTIAL_ISSUED = exports.VERIFICATION_RESULT = exports.VERIFICATION_DURATION = exports.RILAVO_SERVICE_VERSION = exports.RILAVO_SERVICE_NAME = void 0;
exports.getInstrumentation = getInstrumentation;
exports.initializeInstrumentation = initializeInstrumentation;
exports.getTracer = getTracer;
exports.getMeter = getMeter;
exports.verificationSpan = verificationSpan;
exports.recordVerification = recordVerification;
exports.recordCredentialIssued = recordCredentialIssued;
exports.recordReplayDetected = recordReplayDetected;
exports.setNonceCacheSize = setNonceCacheSize;
exports.recordIssuerDirectoryLookup = recordIssuerDirectoryLookup;
exports.shutdownInstrumentation = shutdownInstrumentation;
const api_1 = require("@opentelemetry/api");
const resources_1 = require("@opentelemetry/resources");
const semantic_conventions_1 = require("@opentelemetry/semantic-conventions");
const instrumentation_1 = require("@opentelemetry/instrumentation");
const instrumentation_http_1 = require("@opentelemetry/instrumentation-http");
const sdk_node_1 = require("@opentelemetry/sdk-node");
// Semantic conventions for Rilavo
exports.RILAVO_SERVICE_NAME = 'rilavo';
exports.RILAVO_SERVICE_VERSION = '0.1.0';
// Metric names (following semantic conventions)
exports.VERIFICATION_DURATION = 'rilavo.verification.duration';
exports.VERIFICATION_RESULT = 'rilavo.verification.result';
exports.CREDENTIAL_ISSUED = 'rilavo.credential.issued';
exports.REPLAY_DETECTED = 'rilavo.replay.detected';
exports.NONCE_CACHE_SIZE = 'rilavo.nonce_cache.size';
exports.ISSUER_DIRECTORY_LOOKUPS = 'rilavo.issuer_directory.lookups';
// Attribute keys
exports.VERIFICATION_REASON = 'rilavo.verification.reason';
exports.VERIFICATION_ACCEPTED = 'rilavo.verification.accepted';
exports.CREDENTIAL_ISSUER = 'rilavo.credential.issuer';
exports.CREDENTIAL_AGENT = 'rilavo.credential.agent';
/**
 * Manages OpenTelemetry instrumentation for Rilavo TypeScript SDK.
 */
class RilavoInstrumentation {
    serviceName;
    serviceVersion;
    otlpEndpoint;
    enablePrometheus;
    enableOtlp;
    _sdk = null;
    _tracer = null;
    _meter = null;
    _initialized = false;
    // Metric instruments (lazy initialization)
    _verificationDuration = null;
    _verificationResultCounter = null;
    _credentialIssuedCounter = null;
    _replayDetectedCounter = null;
    _nonceCacheSizeGauge = null;
    _issuerDirectoryLookupsCounter = null;
    constructor(serviceName = 'rilavo', serviceVersion = '0.1.0', otlpEndpoint, enablePrometheus = true, enableOtlp = false) {
        this.serviceName = serviceName;
        this.serviceVersion = serviceVersion;
        this.otlpEndpoint = otlpEndpoint;
        this.enablePrometheus = enablePrometheus;
        this.enableOtlp = enableOtlp;
    }
    /**
     * Initialize OpenTelemetry instrumentation.
     */
    async initialize() {
        if (this._initialized)
            return;
        const resource = new resources_1.Resource({
            [semantic_conventions_1.SemanticResourceAttributes.SERVICE_NAME]: 'rilavo',
            [semantic_conventions_1.SemanticResourceAttributes.SERVICE_VERSION]: '0.1.0',
        });
        // Configure SDK - Prometheus exporter starts its own HTTP server
        const { PrometheusExporter } = await Promise.resolve().then(() => __importStar(require('@opentelemetry/exporter-prometheus')));
        const prometheusExporter = new PrometheusExporter({ port: 9464, endpoint: '/metrics' }, () => { console.log('Prometheus exporter started on :9464/metrics'); });
        // Note: PrometheusExporter is a push exporter that starts its own HTTP server
        // We don't use a PeriodicExportingMetricReader with it
        const sdkConfig = {
            resource,
            traceExporter: undefined,
            metricReader: undefined,
        };
        // Create and start SDK
        const sdk = new sdk_node_1.NodeSDK(sdkConfig);
        this._sdk = sdk.start();
        // Register HTTP instrumentation for auto-instrumentation
        (0, instrumentation_1.registerInstrumentations)({
            instrumentations: [
                new instrumentation_http_1.HttpInstrumentation(),
            ],
        });
        // Initialize tracer and meter
        this._tracer = api_1.trace.getTracer('rilavo', '0.1.0');
        this._meter = api_1.metrics.getMeter('rilavo', '0.1.0');
        // Initialize metric instruments
        this._initMetrics();
        this._initialized = true;
    }
    _initMetrics() {
        if (!this._meter)
            return;
        this._verificationDuration = this._meter.createHistogram('rilavo.verification.duration', {
            description: 'Duration of credential verification in milliseconds',
            unit: 'ms',
        });
        this._verificationResultCounter = this._meter.createCounter('rilavo.verification.result', {
            description: 'Total number of credential verifications by result',
            unit: '1',
        });
        this._credentialIssuedCounter = this._meter.createCounter('rilavo.credential.issued', {
            description: 'Total number of credentials issued',
            unit: '1',
        });
        this._replayDetectedCounter = this._meter.createCounter('rilavo.replay.detected', {
            description: 'Total number of replay attacks detected',
            unit: '1',
        });
        this._nonceCacheSizeGauge = this._meter.createUpDownCounter('rilavo.nonce_cache.size', {
            description: 'Current size of nonce cache',
            unit: '1',
        });
        this._issuerDirectoryLookupsCounter = this._meter.createCounter('rilavo.issuer_directory.lookups', {
            description: 'Total number of issuer directory lookups',
            unit: '1',
        });
    }
    get tracer() {
        if (!this._initialized)
            this.initialize();
        return this._tracer;
    }
    get meter() {
        if (!this._initialized)
            this.initialize();
        return this._meter;
    }
    /**
     * Create a span for credential verification.
     */
    verificationSpan(credentialIssuer, credentialAgent) {
        if (!this._initialized)
            this.initialize();
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
    recordVerification(accepted, reasonCode = null, durationMs = 0, credentialIssuer) {
        if (!this._initialized)
            this.initialize();
        const attributes = {
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
    recordCredentialIssued(issuer, agent) {
        if (!this._initialized)
            this.initialize();
        const attributes = {
            'rilavo.credential.issuer': issuer,
            'rilavo.credential.agent': agent,
        };
        this._credentialIssuedCounter?.add(1, { attributes });
    }
    recordReplayDetected(credentialIssuer) {
        if (!this._initialized)
            this.initialize();
        const attributes = {};
        if (credentialIssuer) {
            attributes['rilavo.credential.issuer'] = credentialIssuer;
        }
        this._replayDetectedCounter?.add(1, { attributes });
    }
    setNonceCacheSize(size) {
        if (!this._initialized)
            this.initialize();
        this._nonceCacheSizeGauge?.add(size);
    }
    recordIssuerDirectoryLookup(issuerId, found) {
        if (!this._initialized)
            this.initialize();
        const attributes = {
            issuer_id: issuerId,
            found,
        };
        this._issuerDirectoryLookupsCounter?.add(1, { attributes });
    }
    shutdown() {
        this._sdk?.shutdown();
        this._initialized = false;
    }
}
exports.RilavoInstrumentation = RilavoInstrumentation;
// Global instrumentation instance
let _instrumentation = null;
/**
 * Get or create the global instrumentation instance.
 */
function getInstrumentation() {
    if (!_instrumentation) {
        _instrumentation = new RilavoInstrumentation();
    }
    return _instrumentation;
}
/**
 * Initialize global instrumentation.
 */
async function initializeInstrumentation(serviceName = 'rilavo', serviceVersion = '0.1.0', otlpEndpoint, enablePrometheus = true, enableOtlp = false) {
    const inst = new RilavoInstrumentation(serviceName, serviceVersion, otlpEndpoint, true, // enablePrometheus
    !!otlpEndpoint);
    await inst.initialize();
    return inst;
}
// Convenience functions
function getTracer() {
    return getInstrumentation().tracer;
}
function getMeter() {
    return getInstrumentation().meter;
}
function verificationSpan(credentialIssuer, credentialAgent) {
    return getInstrumentation().verificationSpan(credentialIssuer, credentialAgent);
}
function recordVerification(accepted, reasonCode = null, durationMs = 0, credentialIssuer) {
    getInstrumentation().recordVerification(accepted, reasonCode, durationMs, credentialIssuer);
}
function recordCredentialIssued(issuer, agent) {
    getInstrumentation().recordCredentialIssued(issuer, agent);
}
function recordReplayDetected(credentialIssuer) {
    getInstrumentation().recordReplayDetected(credentialIssuer);
}
function setNonceCacheSize(size) {
    getInstrumentation().setNonceCacheSize(size);
}
function recordIssuerDirectoryLookup(issuerId, found) {
    getInstrumentation().recordIssuerDirectoryLookup(issuerId, found);
}
function shutdownInstrumentation() {
    // Implementation would go here
}
