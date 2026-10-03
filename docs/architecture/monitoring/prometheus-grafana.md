---
title: Monitoring Setup
description: Prometheus, Grafana, and Alerting for Rilavo
---

# Monitoring Setup

## Overview

Rilavo exposes metrics via Prometheus endpoint at `/metrics` (port 9090 by default). This guide covers setting up Prometheus, Grafana, and alerting.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Rilavo SDKs │────▶│ Rilavo Svc  │────▶│  Prometheus │
└─────────────┘     │  (port 9090)│     │  (scraping) │
                    └─────────────┘     └──────┬──────┘
                                               │
                    ┌─────────────┐            │
                    │   Grafana   │◀───────────┘
                    │ (dashboards)│
                    └─────────────┘
                                               │
                    ┌─────────────┐            │
                    │ Alertmanager│◀───────────┘
                    │  (alerts)   │
                    └─────────────┘
```

## Prometheus Configuration

### Basic Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 30s
  evaluation_interval: 30s
  external_labels:
    cluster: 'production'
    environment: 'prod'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'rules/*.yml'

scrape_configs:
  # Rilavo Service
  - job_name: 'rilavo-service'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - rilavo
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']

  # Node Exporter
  - job_name: 'node-exporter'
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
```

### Rilavo-Specific Scrape Config

```yaml
# Additional scrape config for Rilavo metrics
- job_name: 'rilavo-verification'
  kubernetes_sd_configs:
    - role: pod
      namespaces:
        names:
          - rilavo
  metrics_path: /metrics
  relabel_configs:
    - source_labels: [__meta_kubernetes_pod_label_app]
      action: keep
      regex: rilavo-service
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      regex: (\d+)
      target_label: __metrics_port__
    - source_labels: [__address__, __metrics_port__]
      action: replace
      regex: ([^:]+)(?::\d+)?;(\d+)
      replacement: $1:$2
      target_label: __address__
```

## Key Metrics

### Verification Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `rilavo_verification_total` | Counter | Total verifications |
| `rilavo_verification_accepted_total` | Counter | Accepted verifications |
| `rilavo_verification_rejected_total` | Counter | Rejected verifications (by reason) |
| `rilavo_verification_duration_seconds` | Histogram | Verification latency |
| `rilavo_verification_duration_seconds_bucket` | Histogram buckets | Latency percentiles |

### Credential Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `rilavo_credential_issued_total` | Counter | Credentials issued |
| `rilavo_credential_verify_total` | Counter | Credentials verified |

### Security Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `rilavo_replay_detected_total` | Counter | Replay attacks detected |
| `rilavo_revoked_total` | Counter | Revoked credentials |
| `rilavo_rate_limit_exceeded_total` | Counter | Rate limit hits |
| `rilavo_invalid_signature_total` | Counter | Invalid signatures |

### System Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `rilavo_nonce_cache_size` | Gauge | Nonce cache size |
| `rilavo_issuer_directory_lookups_total` | Counter | Issuer directory lookups |
| `rilavo_revocation_log_checks_total` | Counter | Revocation log checks |

### HTTP Metrics (Standard)

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | HTTP requests by method/path/status |
| `http_request_duration_seconds` | Histogram | Request latency |
| `http_request_size_bytes` | Histogram | Request size |
| `http_response_size_bytes` | Histogram | Response size |

## Grafana Dashboards

### Overview Dashboard

```json
{
  "title": "Rilavo Overview",
  "panels": [
    {
      "title": "Verification Rate",
      "type": "graph",
      "targets": [
        {
          "expr": "sum(rate(rilavo_verification_total[5m])) by (job)",
          "legendFormat": "{{job}}"
        }
      ]
    },
    {
      "title": "Acceptance Rate",
      "type": "stat",
      "targets": [
        {
          "expr": "sum(rate(rilavo_verification_accepted_total[5m])) / sum(rate(rilavo_verification_total[5m]))",
          "legendFormat": "Acceptance Rate"
        }
      ],
      "fieldConfig": {
        "defaults": {
          "unit": "percentunit"
        }
      }
    },
    {
      "title": "Rejection Reasons",
      "type": "piechart",
      "targets": [
        {
          "expr": "sum by (reason) (rate(rilavo_verification_rejected_total[5m]))",
          "legendFormat": "{{reason}}"
        }
      ]
    },
    {
      "title": "Verification Latency (p50, p95, p99)",
      "type": "graph",
      "targets": [
        {
          "expr": "histogram_quantile(0.50, sum(rate(rilavo_verification_duration_seconds_bucket[5m])) by (le))",
          "legendFormat": "p50"
        },
        {
          "expr": "histogram_quantile(0.95, sum(rate(rilavo_verification_duration_seconds_bucket[5m])) by (le))",
          "legendFormat": "p95"
        },
        {
          "expr": "histogram_quantile(0.99, sum(rate(rilavo_verification_duration_seconds_bucket[5m])) by (le))",
          "legendFormat": "p99"
        }
      ]
    }
  ]
}
```

### Verification Deep-Dive Dashboard

```json
{
  "title": "Rilavo Verification Deep-Dive",
  "panels": [
    {
      "title": "Verification Latency Heatmap",
      "type": "heatmap",
      "targets": [
        {
          "expr": "sum(rate(rilavo_verification_duration_seconds_bucket[5m])) by (le)",
          "format": "heatmap"
        }
      ]
    },
    {
      "title": "Rejection Reason Breakdown",
      "type": "bargauge",
      "targets": [
        {
          "expr": "sum by (reason) (rate(rilavo_verification_rejected_total[5m]))",
          "legendFormat": "{{reason}}"
        }
      ]
    },
    {
      "title": "Replay Detection Rate",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(rilavo_replay_detected_total[5m])",
          "legendFormat": "Replay Detected"
        }
      ]
    },
    {
      "title": "Rate Limit Exceeded",
      "type": "stat",
      "targets": [
        {
          "expr": "rate(rilavo_rate_limit_exceeded_total[5m])",
          "legendFormat": "Rate Limited"
        }
      ]
    }
  ]
}
```

## Alerting Rules

```yaml
# rules/rilavo.yml
groups:
  - name: rilavo-alerts
    interval: 30s
    rules:
      # High Error Rate
      - alert: RilavoHighErrorRate
        expr: |
          sum(rate(rilavo_verification_rejected_total[5m])) / 
          sum(rate(rilavo_verification_total[5m])) > 0.05
        for: 2m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "High Rilavo verification error rate ({{ $value | humanizePercentage }})"
          description: "More than 5% of verifications are failing. Check rejection reasons."
          runbook_url: "https://docs.rilavo.org/../troubleshooting/index.md#runbookshigh-error-rate"

      # High Latency
      - alert: RilavoHighLatency
        expr: |
          histogram_quantile(0.99, 
            sum(rate(rilavo_verification_duration_seconds_bucket[5m])) by (le)
          ) > 1
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "High Rilavo verification latency (p99 > 1s)"
          description: "P99 verification latency exceeds 1 second."
          runbook_url: "https://docs.rilavo.org/../troubleshooting/index.md#runbookshigh-latency"

      # Replay Attacks
      - alert: RilavoReplayAttackDetected
        expr: |
          rate(rilavo_replay_detected_total[5m]) > 0.1
        for: 1m
        labels:
          severity: critical
          team: security
        annotations:
          summary: "Replay attack detected on Rilavo service"
          description: "Replay detection rate exceeds 0.1/sec. Possible credential theft."
          runbook_url: "https://docs.rilavo.org/../troubleshooting/index.md#runbooksreplay-attack"

      # Rate Limiting
      - alert: RilavoHighRateLimitHits
        expr: |
          rate(rilavo_rate_limit_exceeded_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "High rate limit hits on Rilavo service"
          description: "Rate limit exceeded rate exceeds 10/sec. Possible abuse or misconfiguration."

      # High Memory
      - alert: RilavoHighMemoryUsage
        expr: |
          (container_memory_working_set_bytes{container="rilavo-service"} / 
           container_spec_memory_limit_bytes{container="rilavo-service"}) > 0.85
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "Rilavo service memory usage > 85%"
          description: "Memory usage exceeds 85% of limit."

      # High CPU
      - alert: RilavoHighCPUUsage
        expr: |
          (rate(container_cpu_usage_seconds_total{container="rilavo-service"}[5m]) / 
           container_spec_cpu_quota{container="rilavo-service"} / 
           container_spec_cpu_period{container="rilavo-service"}) > 0.85
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "Rilavo service CPU usage > 85%"
          description: "CPU usage exceeds 85% of limit."

      # Pod Restart
      - alert: RilavoPodRestarting
        expr: |
          increase(kube_pod_container_status_restarts_total{container="rilavo-service",namespace="rilavo"}[1h]) > 3
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "Rilavo pod restarting frequently"
          description: "Pod has restarted more than 3 times in the last hour."

      # Certificate Expiry
      - alert: RilavoTLSCertExpiring
        expr: |
          ssl_certificate_expiration_timestamp_seconds - time() < 86400 * 30
        for: 1h
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "Rilavo TLS certificate expiring within 30 days"
          description: "TLS certificate for Rilavo service expires soon."

      # Issuer Directory Unavailable
      - alert: RilavoIssuerDirectoryUnavailable
        expr: |
          rate(rilavo_issuer_directory_unavailable_total[5m]) > 0
        for: 1m
        labels:
          severity: critical
          team: platform
        annotations:
          summary: "Rilavo issuer directory unavailable"
          description: "Issuer directory is unreachable, verifications will fail closed."

      # Nonce Cache Full
      - alert: RilavoNonceCacheFull
        expr: |
          (rilavo_nonce_cache_size / 1000000) > 0.9
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "Rilavo nonce cache > 90% capacity"
          description: "Nonce cache is approaching capacity. Consider increasing cache size or TTL."
```

## Alertmanager Configuration

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alerts@rilavo.org'
  smtp_auth_username: 'alerts@rilavo.org'
  smtp_auth_password: '${SMTP_PASSWORD}'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
      continue: true
    - match:
        team: security
      receiver: 'security-alerts'

receivers:
  - name: 'default'
    email_configs:
      - to: 'platform-alerts@rilavo.org'
        send_resolved: true
    slack_configs:
      - api_url: '${SLACK_WEBHOOK}'
        channel: '#platform-alerts'
        send_resolved: true
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}
{{ .Annotations.description }}{{ end }}'

  - name: 'critical-alerts'
    email_configs:
      - to: 'oncall@rilavo.org'
        send_resolved: true
    pagerduty_configs:
      - service_key: '${PAGERDUTY_KEY}'
        severity: critical

  - name: 'security-alerts'
    email_configs:
      - to: 'security@rilavo.org'
        send_resolved: true
    slack_configs:
      - api_url: '${SLACK_WEBHOOK}'
        channel: '#security-alerts'
        send_resolved: true

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'cluster', 'service']
```

## Deployment

### Prometheus Operator (Recommended)

```bash
# Install Prometheus Operator
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack   --namespace monitoring   --create-namespace   --values prometheus-values.yaml
```

### Prometheus Values

```yaml
# prometheus-values.yaml
prometheus:
  prometheusSpec:
    retention: 30d
    retentionSize: 50GB
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: fast-storage
          resources:
            requests:
              storage: 100Gi
    serviceMonitorSelector:
      matchLabels:
        release: rilavo
    ruleSelector:
      matchLabels:
        release: rilavo
    additionalScrapeConfigs:
      - job_name: 'rilavo-service'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names:
                - rilavo
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            action: keep
            regex: rilavo-service

grafana:
  enabled: true
  adminPassword: ${GRAFANA_PASSWORD}
  dashboards:
    default:
      rilavo-overview:
        json: |
          ${file("dashboards/overview.json")}
      rilavo-verification:
        json: |
          ${file("dashboards/verification.json")}
    dashboardProviders:
      dashboardproviders.yaml:
        apiVersion: 1
        providers:
          - name: 'Rilavo'
            orgId: 1
            folder: 'Rilavo'
            type: file
            disableDeletion: false
            updateIntervalSeconds: 10
            allowUiUpdates: true
            options:
              path: /var/lib/grafana/dashboards/rilavo

alertmanager:
  enabled: true
  alertmanagerSpec:
    storage:
      volumeClaimTemplate:
        spec:
          storageClassName: fast-storage
          resources:
            requests:
              storage: 10Gi
    config:
      global:
        resolve_timeout: 5m
      route:
        group_by: ['alertname', 'cluster', 'service']
        group_wait: 30s
        group_interval: 5m
        repeat_interval: 4h
        receiver: 'default'
      receivers:
        - name: 'default'
          email_configs:
            - to: 'platform-alerts@rilavo.org'
              send_resolved: true
          slack_configs:
            - api_url: '${SLACK_WEBHOOK}'
              channel: '#platform-alerts'
              send_resolved: true
```

---

## Next Steps

- [Security Hardening](../security/hardening.md)
- [Troubleshooting](../troubleshooting/index.md)
- [Runbooks](../troubleshooting/index.md#runbooks)
