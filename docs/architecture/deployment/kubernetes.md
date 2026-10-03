---
title: Kubernetes Deployment Guide
description: Deploy Rilavo on Kubernetes with Helm and Kustomize
---

# Kubernetes Deployment Guide

## Prerequisites

- Kubernetes 1.24+
- Helm 3.10+
- kubectl configured
- Cert-manager for TLS
- Ingress controller (NGINX, Traefik, etc.)

## Quick Start with Helm

```bash
# Add Rilavo Helm repo
helm repo add rilavo https://charts.rilavo.io
helm repo update

# Install with default values
helm install rilavo rilavo/rilavo-platform   --namespace rilavo   --create-namespace   --set global.verifierId=verifier:myapp.example.com   --set global.issuerSeedSecret=rilavo-issuer-seed

# Verify deployment
kubectl get pods -n rilavo
kubectl logs -n rilavo -l app=rilavo-service
```

## Helm Chart Structure

```
rilavo-platform/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── serviceaccount.yaml
│   ├── rbac.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   ├── servicemonitor.yaml
│   └── networkpolicy.yaml
└── values.schema.json
```

## Configuration

### Global Values

```yaml
# values.yaml
global:
  # Verifier identity (used as audience in credentials)
  verifierId: "verifier:myapp.example.com"

  # Issuer seed secret (base64 encoded Ed25519 seed)
  issuerSeedSecret: "rilavo-issuer-seed"

  # Image registry
  imageRegistry: "ghcr.io/rilavo"
  imagePullSecrets: ["ghcr-secret"]

  # Resource defaults
  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
```

### Service Configuration

```yaml
service:
  # HTTP service
  type: ClusterIP
  port: 80
  targetPort: 8090

  # Metrics service
  metricsPort: 9090

  # Discovery service
  serveDiscovery: true

  # TLS
  tls:
    enabled: true
    secretName: rilavo-tls
```

### Issuer Directory

```yaml
issuerDirectory:
  # Static issuers (for development)
  static:
    - issuerId: "did:example:issuer1"
      publicKeyPem: |
        -----BEGIN PUBLIC KEY-----
        MCowBQYDK2VwAyEA...
        -----END PUBLIC KEY-----
      validUntil: 4102444800  # Year 2100

  # Dynamic issuer fetching (production)
  dynamic:
    enabled: true
    cacheTTL: 3600
    timeout: 10s
    # Issuers discovered via /.well-known/rilavo
```

### Revocation Log

```yaml
revocationLog:
  # Redis-backed (production)
  redis:
    enabled: true
    url: "redis://redis:6379/0"
    keyPrefix: "rilavo:revoked:"

  # In-memory (development)
  memory:
    enabled: false
```

### Nonce Cache

```yaml
nonceCache:
  # Redis-backed (production, distributed)
  redis:
    enabled: true
    url: "redis://redis:6379/1"
    keyPrefix: "rilavo:nonce:"

  # In-memory (development)
  memory:
    enabled: false
```

### Rate Limiting

```yaml
rateLimit:
  enabled: true
  redis:
    enabled: true
    url: "redis://redis:6379/2"

  limits:
    # Per-credential rate limit
    perCredential:
      requests: 100
      window: 60s
      algorithm: sliding-window-counter

    # Per IP
    perIP:
      requests: 1000
      window: 60s
      algorithm: fixed-window

    # Per tenant (for multi-tenant)
    perTenant:
      requests: 10000
      window: 60s
      algorithm: token-bucket
```

### Monitoring

```yaml
monitoring:
  # Prometheus ServiceMonitor
  serviceMonitor:
    enabled: true
    interval: 30s
    namespace: monitoring
    labels:
      release: prometheus

  # Grafana dashboards
  grafana:
    enabled: true
    dashboards:
      - name: rilavo-overview
        file: dashboards/overview.json
      - name: rilavo-verification
        file: dashboards/verification.json
      - name: rilavo-rate-limit
        file: dashboards/rate-limit.json

  # Alerting
  alerts:
    enabled: true
    rules:
      - name: rilavo-high-error-rate
        expr: |
          sum(rate(rilavo_verification_rejected_total[5m])) / 
          sum(rate(rilavo_verification_total[5m])) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High Rilavo verification error rate"

      - name: rilavo-high-latency
        expr: |
          histogram_quantile(0.99, 
            sum(rate(rilavo_verification_duration_bucket[5m])) by (le)
          ) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High Rilavo verification latency"
```

### Security

```yaml
security:
  # Network policies
  networkPolicy:
    enabled: true
    ingress:
      - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
        ports:
        - protocol: TCP
          port: 8090
      - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
        ports:
        - protocol: TCP
          port: 9090

  # Pod security
  podSecurity:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    readOnlyRootFilesystem: true
    capabilities:
      drop: ["ALL"]
    allowPrivilegeEscalation: false

  # Network encryption
  tls:
    enabled: true
    certManager:
      enabled: true
      issuer: letsencrypt-prod
      dnsNames:
        - rilavo.example.com
```

### Scaling

```yaml
autoscaling:
  hpa:
    enabled: true
    minReplicas: 3
    maxReplicas: 50
    metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 70
      - type: Pods
        pods:
          metric:
            name: rilavo_verification_duration_seconds
          target:
            type: AverageValue
            averageValue: "500ms"
    behavior:
      scaleDown:
        stabilizationWindowSeconds: 300
        policies:
          - type: Percent
            value: 10
            periodSeconds: 60
      scaleUp:
        stabilizationWindowSeconds: 0
        policies:
          - type: Percent
            value: 100
            periodSeconds: 15
            - type: Pods
              value: 4
              periodSeconds: 15
        selectPolicy: Max

  # Pod Disruption Budget
  pdb:
    enabled: true
    minAvailable: 2
```

## Installation

```bash
# Create namespace
kubectl create namespace rilavo

# Create secrets
kubectl create secret generic rilavo-issuer-seed   --namespace rilavo   --from-literal=seed=$(cat issuer.seed | base64 -w0)

kubectl create secret generic rilavo-tls   --namespace rilavo   --from-file=tls.crt=cert.pem   --from-file=tls.key=key.pem

# Create Redis (if not using external)
helm install redis bitnami/redis -n rilavo   --set auth.enabled=false   --set architecture=standalone

# Install Rilavo
helm install rilavo rilavo/rilavo-platform -n rilavo -f values-prod.yaml

# Verify
kubectl get pods -n rilavo -w
kubectl logs -n rilavo -l app=rilavo-service -f
```

## Upgrades

```bash
# Upgrade to new version
helm upgrade rilavo rilavo/rilavo-platform -n rilavo -f values-prod.yaml

# Rollback if needed
helm rollback rilavo -n rilavo

# Check status
helm status rilavo -n rilavo
```

## Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod -n rilavo -l app=rilavo-service
   kubectl logs -n rilavo -l app=rilavo-service --previous
   ```

2. **Issuer seed not found**
   ```bash
   kubectl get secret rilavo-issuer-seed -n rilavo -o yaml
   ```

3. **Redis connection failed**
   ```bash
   kubectl exec -n rilavo deploy/rilavo-service -- redis-cli -h redis ping
   ```

4. **High memory usage**
   ```bash
   kubectl top pods -n rilavo
   kubectl describe pod -n rilavo -l app=rilavo-service
   ```

### Debug Commands

```bash
# Port forward for local debugging
kubectl port-forward -n rilavo svc/rilavo-service 8090:80

# Check metrics
curl http://localhost:9090/metrics | grep rilavo

# Check health
curl http://localhost:8090/health
curl http://localhost:8090/ready

# Verify certificate
kubectl get secret rilavo-tls -n rilavo -o yaml
```

---

## Next Steps

- [Monitoring Setup](../monitoring/prometheus-grafana.md)
- [Security Hardening](../security/hardening.md)
- [Troubleshooting](../troubleshooting/index.md)
