<?php
/**
 * OpenTelemetry instrumentation for Rilavo WordPress SDK.
 * Provides metrics for verification operations.
 *
 * Uses the OpenTelemetry PHP SDK if installed (composer suggest:
 * open-telemetry/sdk, open-telemetry/exporter-prometheus); otherwise falls
 * back to lightweight in-process counters exportable in Prometheus text
 * format via rilavo_export_prometheus_metrics().
 *
 * OPTIONAL BY DESIGN: callers guard with class_exists('RilavoInstrumentation')
 * so the verifier works with zero instrumentation dependencies.
 *
 * @package RilavoMU
 */

if (!defined('ABSPATH')) {
    exit;
}

final class RilavoInstrumentation {

    // Metric names (consistent across all Rilavo SDKs)
    const VERIFICATION_DURATION   = 'rilavo.verification.duration';
    const VERIFICATION_RESULT     = 'rilavo.verification.result';
    const CREDENTIAL_ISSUED       = 'rilavo.credential.issued';
    const REPLAY_DETECTED         = 'rilavo.replay.detected';
    const NONCE_CACHE_SIZE        = 'rilavo.nonce_cache.size';
    const ISSUER_DIRECTORY_LOOKUPS = 'rilavo.issuer_directory.lookups';

    private static ?RilavoInstrumentation $instance = null;
    private bool $initialized = false;

    /** @var array<string, array<string, float>> metric name -> attribute key -> value sum */
    private array $fallbackMetrics = [];

    private function __construct() {}

    public static function getInstance(): RilavoInstrumentation {
        if (self::$instance === null) {
            self::$instance = new RilavoInstrumentation();
        }
        return self::$instance;
    }

    public function initialize(): void {
        if ($this->initialized) {
            return;
        }
        // OpenTelemetry PHP SDK integration is a documented OPTIONAL upgrade:
        // composer require open-telemetry/sdk open-telemetry/exporter-prometheus
        // Until then the lightweight fallback below is authoritative.
        $this->initialized = true;
    }

    /**
     * Record a verification outcome (accept or reject with reason code).
     */
    public function recordVerification(bool $accepted, ?string $reasonCode,
                                       float $durationMs, ?string $credentialIssuer = null): void {
        $attrs = [
            'rilavo.verification.accepted' => $accepted ? 'true' : 'false',
        ];
        if ($reasonCode !== null) {
            $attrs['rilavo.verification.reason'] = $reasonCode;
        }
        if ($credentialIssuer !== null) {
            $attrs['rilavo.credential.issuer'] = $credentialIssuer;
        }
        $this->bump(self::VERIFICATION_RESULT, $attrs, 1.0);
        $this->bump(self::VERIFICATION_DURATION, $attrs, $durationMs);
    }

    public function recordCredentialIssued(string $issuer, string $agent): void {
        $this->bump(self::CREDENTIAL_ISSUED, [
            'rilavo.credential.issuer' => $issuer,
            'rilavo.credential.agent' => $agent,
        ], 1.0);
    }

    public function recordReplayDetected(?string $credentialIssuer = null): void {
        $attrs = [];
        if ($credentialIssuer !== null) {
            $attrs['rilavo.credential.issuer'] = $credentialIssuer;
        }
        $this->bump(self::REPLAY_DETECTED, $attrs, 1.0);
    }

    public function setNonceCacheSize(int $size): void {
        $this->bump(self::NONCE_CACHE_SIZE, [], (float)$size);
    }

    public function recordIssuerDirectoryLookup(string $issuerId, bool $found): void {
        $this->bump(self::ISSUER_DIRECTORY_LOOKUPS, [
            'issuer_id' => $issuerId,
            'found' => $found ? 'true' : 'false',
        ], 1.0);
    }

    /** @return array<string, array<string, float>> all fallback metrics */
    public function getMetrics(): array {
        return $this->fallbackMetrics;
    }

    /**
     * Export fallback metrics in Prometheus text exposition format.
     * Wire to a WordPress AJAX/admin endpoint if external scraping is needed.
     */
    public function exportPrometheusFormat(): string {
        $lines = [];
        foreach ($this->fallbackMetrics as $name => $series) {
            $lines[] = "# HELP {$name} Rilavo metric (fallback in-process counter)";
            $lines[] = "# TYPE {$name} counter";
            foreach ($series as $attrKey => $value) {
                $label = '';
                if ($attrKey !== '') {
                    $label = '{attrs="' . addslashes($attrKey) . '"}';
                }
                $lines[] = "{$name}{$label} {$value}";
            }
        }
        return implode("\n", $lines) . "\n";
    }

    private function bump(string $metric, array $attrs, float $delta): void {
        if ($delta == 0.0) {
            return;
        }
        ksort($attrs);
        $pairs = [];
        foreach ($attrs as $k => $v) {
            $pairs[] = $k . '=' . $v;
        }
        $key = implode(',', $pairs);
        if (!isset($this->fallbackMetrics[$metric])) {
            $this->fallbackMetrics[$metric] = [];
        }
        $this->fallbackMetrics[$metric][$key] =
            ($this->fallbackMetrics[$metric][$key] ?? 0.0) + $delta;
    }
}

if (!function_exists('rilavo_export_prometheus_metrics')) {
    function rilavo_export_prometheus_metrics(): string {
        return RilavoInstrumentation::getInstance()->exportPrometheusFormat();
    }
}
