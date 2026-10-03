---
title: Security Hardening Guide
description: Production security hardening for Rilavo deployments
---

# Security Hardening Guide

## Overview

This guide covers security hardening for Rilavo production deployments, covering the service, SDKs, infrastructure, and operational practices.

## Service Hardening

### Network Security

#### TLS Configuration

```yaml
# Enforce TLS 1.2+
tls:
  minVersion: "1.2"
  cipherSuites:
    - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
    - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    - TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305
    - TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305
```

#### Security Headers

```go
// Go middleware
func securityHeaders(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")
        w.Header().Set("X-Content-Type-Options", "nosniff")
        w.Header().Set("X-Frame-Options", "DENY")
        w.Header().Set("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
        w.Header().Set("Referrer-Policy", "strict-origin-when-cross-origin")
        w.Header().Set("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        next.ServeHTTP(w, r)
    })
}
```

```python
# Python FastAPI middleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
```

### Network Policies

```yaml
# k8s/networkpolicy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: rilavo-service
  namespace: rilavo
spec:
  podSelector:
    matchLabels:
      app: rilavo-service
  policyTypes:
    - Ingress
    - Egress
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
  egress:
    - to:
      - podSelector:
          matchLabels:
            app: redis
      ports:
      - protocol: TCP
        port: 6379
    - to: []
      ports:
      - protocol: TCP
        port: 53
      - protocol: UDP
        port: 53
```

### Pod Security Standards

```yaml
# Restricted Pod Security Standard
apiVersion: v1
kind: Pod
metadata:
  name: rilavo-service
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: rilavo-service
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: cache
      mountPath: /app/cache
  volumes:
  - name: tmp
    emptyDir:
      medium: Memory
  - name: cache
    emptyDir: {}
```

### Secrets Management

```bash
# Never store secrets in images or config maps
# Use Kubernetes secrets or external secret managers

# Create issuer seed secret
kubectl create secret generic rilavo-issuer-seed   --namespace rilavo   --from-literal=seed=$(cat issuer.seed | base64 -w0)

# Use external secret operator for production
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: rilavo-issuer-seed
  namespace: rilavo
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: rilavo-issuer-seed
  data:
    - secretKey: seed
      remoteRef:
        key: rilavo/issuer-seed
        property: seed
```

### Certificate Management

```yaml
# cert-manager ClusterIssuer
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: security@rilavo.org
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
      - http01:
          ingress:
            class: nginx
```

```yaml
# Certificate for Rilavo service
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: rilavo-tls
  namespace: rilavo
spec:
  secretName: rilavo-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - rilavo.example.com
    - api.rilavo.example.com
  duration: 2160h # 90 days
  renewBefore: 360h # 15 days
```

## SDK Hardening

### Input Validation

All SDKs must validate inputs before processing:

```python
# Python example
def verify_credential(credential: dict, pop: dict, options: VerifyOptions) -> VerifyResult:
    # Validate credential structure
    required_fields = ["iss", "sub", "agt", "apk", "act", "aud", "nonce", "sig", "iat", "exp"]
    for field in required_fields:
        if field not in credential or not isinstance(credential[field], str):
            return VerifyResult(accepted=False, reason_code="missing_field")

    # Validate types
    for field in ["iat", "exp"]:
        if not isinstance(credential[field], int) or credential[field] <= 0:
            return VerifyResult(accepted=False, reason_code="malformed_credential")

    # ... rest of verification
```

### Constant-Time Operations

All cryptographic comparisons must use constant-time comparison:

```go
// Go - constant time comparison
func constantTimeCompare(a, b []byte) bool {
    if len(a) != len(b) {
        return false
    }
    var diff byte
    for i := range a {
        diff |= a[i] ^ b[i]
    }
    return diff == 0
}
```

```typescript
// TypeScript - constant time comparison
function constantTimeEqual(a: Uint8Array, b: Uint8Array): boolean {
    if (a.length !== b.length) return false;
    let diff = 0;
    for (let i = 0; i < a.length; i++) {
        diff |= a[i] ^ b[i];
    }
    return diff === 0;
}
```

### Dependency Scanning

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1' # Weekly

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Dependency Review
        uses: actions/dependency-review-action@v3
        with:
          config-file: '.github/dependency-review-config.yml'
```

```yaml
# .github/dependency-review-config.yml
fail-on-severity: high
allow-ghsas:
  - GHSA-xxxx-xxxx-xxxx # Known false positive
```

### Container Image Signing

```bash
# Sign images with cosign
cosign sign --yes ghcr.io/rilavo/rilavo-service:v0.1.0

# Verify signature
cosign verify ghcr.io/rilavo/rilavo-service:v0.1.0   --certificate-identity-regexp "https://github.com/rilavo/rilavo/.github/workflows/.*"   --certificate-oidc-issuer "https://token.actions.githubusercontent.com"
```

```yaml
# .github/workflows/publish.yml
- name: Sign image
  uses: sigstore/cosign-installer@v3
  with:
    cosign-release: 'v2.2.0'

- name: Sign image
  run: |
    cosign sign --yes       --annotation "git-sha=${{ github.sha }}"       --annotation "git-ref=${{ github.ref }}"       ghcr.io/rilavo/rilavo-service:${{ steps.meta.outputs.tags }}
```

## Infrastructure Security

### Kubernetes Security

```yaml
# Admission controller for security policies
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: rilavo-security-policy
spec:
  matchConstraints:
    resourceRules:
      - apiGroups: ["apps"]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["deployments", "statefulsets", "daemonsets"]
  validations:
    - expression: "object.spec.template.spec.securityContext.runAsNonRoot == true"
      message: "Containers must run as non-root"
    - expression: "object.spec.template.spec.containers.all(c, c.securityContext.runAsNonRoot == true)"
      message: "All containers must run as non-root"
    - expression: "object.spec.template.spec.containers.all(c, c.securityContext.readOnlyRootFilesystem == true)"
      message: "Containers must have read-only root filesystem"
    - expression: "object.spec.template.spec.containers.all(c, c.securityContext.capabilities.drop.exists(c, c == 'ALL'))"
      message: "All capabilities must be dropped"
```

### Runtime Security (Falco)

```yaml
# falco-rules.yaml
- rule: Rilavo Unexpected Process
  desc: Detect unexpected processes in Rilavo containers
  condition: >
    container.image.repository contains "rilavo" and
    proc.name not in (python, go, node, java) and
    proc.name not in (sh, bash, python3, go, node)
  output: >
    Unexpected process in Rilavo container (user=%user.name command=%proc.cmdline container=%container.name)
  priority: WARNING
  tags: [container, rilavo]

- rule: Rilavo Network Connection
  desc: Detect unexpected network connections
  condition: >
    container.image.repository contains "rilavo" and
    evt.type in (connect, accept) and
    fd.sport not in (8090, 9090, 6379)
  output: >
    Unexpected network connection from Rilavo (fd=%fd.name sport=%fd.sport)
  priority: WARNING
  tags: [network, rilavo]
```

## Supply Chain Security

### SBOM Generation

```yaml
# .github/workflows/sbom.yml
name: Generate SBOM

on:
  push:
    tags: ['v*']

jobs:
  sbom:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          path: .
          format: spdx-json
          output-file: sbom.spdx.json

      - name: Upload SBOM
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: sbom.spdx.json
          category: sbom
```

```bash
# Generate SBOM locally
syft packages dir:. -o spdx-json=sbom.spdx.json

# Scan SBOM for vulnerabilities
grype sbom:sbom.spdx.json
```

## Incident Response

### Security Incident Runbook

```markdown
# Security Incident Runbook: Credential Compromise

## Detection
- Alert: High rejection rate with `invalid_signature`
- Alert: Unusual verification patterns
- Report: External report of credential theft

## Triage
1. Identify compromised credential(s)
   - Check `rilavo_verification_rejected_total` by reason
   - Check `rilavo_replay_detected_total` spikes

2. Assess scope
   - Single credential vs. issuer compromise
   - Check issuer directory for compromised keys

## Containment
1. Revoke compromised credentials
   ```bash
   # Add to revocation log
   redis-cli SADD revoked:nonce <nonce>
   ```

2. Rotate issuer keys (if issuer compromised)
   ```bash
   # Generate new issuer key
   rilavo keygen --out new-issuer.key

   # Update issuer directory
   kubectl patch configmap issuer-directory -n rilavo      --patch '{"data":{"issuer1.pem":"<new-pem>"}}'
   ```

3. Rotate service TLS certificates
   ```bash
   cert-manager renew rilavo-tls -n rilavo
   ```

## Eradication
1. Audit all verifications in affected time window
2. Notify affected parties (if applicable)
3. Update detection rules

## Recovery
1. Monitor verification rates and error rates
2. Verify new issuer keys working
3. Confirm rate limits effective

## Lessons Learned
- Document root cause
- Update detection rules
- Improve monitoring
- Update runbook
```

---

## Compliance Checklist

- [ ] TLS 1.2+ enforced everywhere
- [ ] Security headers on all responses
- [ ] Network policies restricting traffic
- [ ] Pods run as non-root with dropped capabilities
- [ ] Secrets managed via external secret store
- [ ] TLS certificates auto-renewed (cert-manager)
- [ ] Dependency scanning in CI (Trivy, Dependabot)
- [ ] Container images signed (cosign)
- [ ] SBOM generated for each release
- [ ] Network policies restrict pod communication
- [ ] Pod Security Standards enforced (Restricted)
- [ ] Runtime security monitoring (Falco)
- [ ] SBOM generated for each release
- [ ] Supply chain security (SLSA Level 2+)
- [ ] Incident response runbook tested quarterly

---

## Next Steps

- [Troubleshooting Guide](../troubleshooting/index.md)
- [Runbooks](../troubleshooting/index.md#runbooks)
- [Compliance](../security/hardening.md#compliance)
