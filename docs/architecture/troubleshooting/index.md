---
title: Troubleshooting Guide
description: Common issues and solutions for Rilavo deployments
---

# Troubleshooting Guide

## Quick Reference

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| 401 Unauthorized on all requests | Issuer seed mismatch | Verify issuer seed matches issuer directory |
| 401 with `audience_mismatch` | Wrong audience in config | Check `verifierId` matches credential `aud` |
| 401 with `expired` | Credential expired or clock skew | Check server time, credential `exp` |
| 401 with `replay_detected` | Duplicate nonce | Check nonce cache, agent nonce generation |
| 500 Internal Server Error | Config/dependency issue | Check logs, verify dependencies |
| High latency | Slow issuer directory / Redis | Check Redis latency, issuer directory cache |
| High memory | Nonce cache growth | Check cache TTL, implement eviction |

---

## Common Issues

### 1. Credential Verification Failures

#### `audience_mismatch`

**Symptoms:**
- 401 response with `{"error": "audience_mismatch"}`
- Verification logs show `reason: audience_mismatch`

**Causes:**
- Verifier's `audience` config doesn't match credential's `aud` field
- Multiple verifiers with different audiences

**Fix:**
```bash
# Check credential audience
echo "<credential_b64url>" | base64 -d | jq .aud

# Check verifier config
kubectl get configmap rilavo-config -n rilavo -o yaml | grep verifierId

# Fix: Update verifierId to match credential aud
kubectl patch configmap rilavo-config -n rilavo   --patch '{"data":{"verifier-id":"verifier:correct-audience.example.com"}}'
```

#### `expired` / `not_yet_valid`

**Symptoms:**
- 401 with `expired` or `not_yet_valid`
- Credentials rejected immediately

**Causes:**
- Server clock skew (NTP not synced)
- Credential actually expired
- Wrong `nowSeconds` in test config

**Fix:**
```bash
# Check server time
date
ntpdate -q pool.ntp.org

# Check credential times
echo "<credential_b64url>" | base64 -d | jq '.iat, .exp'

# For testing: use nowSeconds in config
# In test: nowSeconds: Math.floor(Date.now()/1000) - 3600  # 1 hour ago
```

#### `invalid_signature`

**Symptoms:**
- 401 with `invalid_signature`
- High rejection rate

**Causes:**
- Issuer seed mismatch (verifier using different key than issuer)
- Credential tampered
- Wrong issuer public key in directory

**Fix:**
```bash
# Verify issuer seed matches
# Issuer side:
rilavo keygen --out issuer.key
cat issuer.pub | base64 -w0

# Verifier side - check directory entry
kubectl get configmap issuer-directory -n rilavo -o yaml

# Regenerate issuer keypair if needed
rilavo keygen --out new-issuer.key
# Update directory with new public key
```

#### `unknown_issuer`

**Symptoms:**
- 401 with `unknown_issuer`
- All credentials from specific issuer fail

**Causes:**
- Issuer not in directory
- Directory unreachable (`unreachable: true`)
- Issuer ID mismatch

**Fix:**
```bash
# Check issuer directory
kubectl get configmap issuer-directory -n rilavo -o yaml

# Check issuer ID in credential
echo "<credential_b64url>" | base64 -d | jq .iss

# Add issuer to directory
kubectl patch configmap issuer-directory -n rilavo   --patch '{"data":{"issuers.json":"[...]"}}'
```

#### `key_not_valid_at_issuance`

**Symptoms:**
- 401 with `key_not_valid_at_issuance`
- Credentials issued after key rotation fail

**Causes:**
- Issuer key rotated, but `validUntil` not updated
- Credential `iat` > issuer key `validUntil`

**Fix:**
```bash
# Check issuer directory entry
kubectl get configmap issuer-directory -n rilavo -o yaml | grep validUntil

# Update validUntil to far future
kubectl patch configmap issuer-directory -n rilavo   --patch '{"data":{"issuers.json":"[{"issuerId":"...","validUntil":4102444800}]"}}'
```

#### `replay_detected`

**Symptoms:**
- 401 with `replay_detected`
- Second request with same nonce fails

**Causes:**
- Agent reusing nonce
- Nonce cache not shared across replicas
- Agent not generating unique nonces

**Fix:**
```bash
# Check nonce cache
redis-cli -h redis SMEMBERS "rilavo:nonce:*"

# Check agent nonce generation
# Agent must generate unique nonce per request

# For distributed: ensure Redis nonce cache shared
# Check Redis connection from all replicas
kubectl exec -n rilavo deploy/rilavo-service -- redis-cli -h redis ping
```

#### `revoked`

**Symptoms:**
- 401 with `revoked`
- Credential was working, now rejected

**Causes:**
- Credential explicitly revoked
- Nonce added to revocation log

**Fix:**
```bash
# Check revocation log
redis-cli -h redis SMEMBERS "revoked:nonce"

# Remove from revocation if error
redis-cli -h redis SREM "revoked:nonce" "<nonce>"
```

---

### 2. Service Issues

#### Service Won't Start

**Symptoms:**
- Pod stuck in `CrashLoopBackOff`
- Logs show panic or config error

**Debug:**
```bash
# Check pod status
kubectl describe pod -n rilavo -l app=rilavo-service

# Check logs
kubectl logs -n rilavo -l app=rilavo-service --previous

# Common causes:
# 1. Missing issuer seed secret
kubectl get secret rilavo-issuer-seed -n rilavo

# 2. Config validation error
kubectl logs -n rilavo -l app=rilavo-service | grep -i error

# 3. Redis connection failed
kubectl exec -n rilavo deploy/rilavo-service -- redis-cli -h redis ping
```

#### High Memory Usage

**Symptoms:**
- Pod OOM killed
- Memory usage growing

**Causes:**
- Nonce cache not evicting
- Memory leak in SDK
- Large request bodies

**Fix:**
```bash
# Check memory usage
kubectl top pods -n rilavo

# Check nonce cache size
redis-cli -h redis DBSIZE
redis-cli -h redis KEYS "rilavo:nonce:*" | wc -l

# Adjust cache TTL
# In config: nonceCacheTTL: 3600 (1 hour)

# Restart to clear cache
kubectl rollout restart deploy/rilavo-service -n rilavo
```

#### High Latency

**Symptoms:**
- Slow verification responses (> 500ms)
- Timeouts on verification

**Debug:**
```bash
# Check metrics
curl -s http://localhost:9090/metrics | grep rilavo_verification_duration

# Check Redis latency
redis-cli -h redis --latency-history -i 1

# Check issuer directory latency
# Add timing logs to verification code

# Check CPU/memory
kubectl top pods -n rilavo
```

#### High Error Rate

**Symptoms:**
- > 5% verification failures
- Alerts firing

**Debug:**
```bash
# Check rejection reasons
curl -s http://localhost:9090/metrics | grep rilavo_verification_rejected

# Check logs for patterns
kubectl logs -n rilavo -l app=rilavo-service | grep -i error | tail -20

# Check specific rejection reasons
curl -s http://localhost:9090/metrics | grep rilavo_verification_rejected_total
```

---

### 3. SDK-Specific Issues

#### TypeScript SDK

```typescript
// Issue: Module not found
// Fix: Ensure proper imports
import { verifyCredential } from '@rilavo/sdk'; // Correct
// import { verifyCredential } from '@rilavo/sdk/src'; // Wrong

// Issue: Type errors with verification options
// Fix: Use correct types
import type { VerifyOptions, VerifyResult } from '@rilavo/sdk';

const opts: VerifyOptions = {
  issuerDirectory: dir,
  revocationLog: revLog,
  nonceCache: new NonceCache(),
  verifierAudience: 'myapp.example.com',
};
```

#### Go SDK

```go
// Issue: Build tags
// Fix: Use correct build tags
//go:build ignore
// +build ignore

// Issue: Module path
// Fix: Use correct module path
import "github.com/rilavo/rilavo-go" // Correct
// import "rilavo-go" // Wrong
```

#### Go Middleware

```go
// Issue: Context values not accessible
// Fix: Use correct context key type
type contextKey string

const rilavoCredentialKey contextKey = "rilavo_credential"

func GetCredential(ctx context.Context) (rilavo.CredentialFields, bool) {
    cred, ok := ctx.Value(rilavoCredentialKey).(rilavo.CredentialFields)
    return cred, ok
}
```

#### Next.js Middleware

```typescript
// Issue: "require is not defined"
// Fix: Use injection pattern (see middleware.test.mjs)

// Issue: Dynamic import fails in tests
// Fix: Use injectVerifyCredential for testing
import { injectVerifyCredential } from '@rilavo/next';
injectVerifyCredential(sdk.verifyCredential);
```

#### Python SDK

```python
# Issue: Import errors
# Fix: Install in development mode
pip install -e ./rilavo-protocol

# Issue: Async vs sync
# Fix: verify_credential is sync, issue_credential is async
from rilavo import verify_credential, issue_credential

# Sync
result = verify_credential(fields, pop, opts)

# Async
cred = await issue_credential(opts)
```

---

### 4. Infrastructure Issues

#### Redis Connection Issues

```bash
# Test Redis connectivity
kubectl exec -n rilavo deploy/rilavo-service -- redis-cli -h redis ping

# Check Redis logs
kubectl logs -n rilavo deploy/redis

# Check Redis memory
redis-cli -h redis INFO memory
```

#### DNS Issues

```bash
# Test service DNS
kubectl exec -n rilavo deploy/rilavo-service -- nslookup redis

# Check CoreDNS
kubectl logs -n kube-system -l k8s-app=kube-dns
```

#### Certificate Issues

```bash
# Check certificate
openssl x509 -in cert.pem -text -noout

# Check cert-manager
kubectl get certificate -n rilavo
kubectl describe certificate rilavo-tls -n rilavo

# Check cert-manager logs
kubectl logs -n cert-manager deploy/cert-manager
```

---

### 5. Performance Tuning

#### Redis Optimization

```redis
# Increase maxmemory
CONFIG SET maxmemory 512mb
CONFIG SET maxmemory-policy allkeys-lru

# Disable persistence if not needed
CONFIG SET save ""
CONFIG SET appendonly no
```

#### Go Service Tuning

```go
// Increase GOMAXPROCS for multi-core
runtime.GOMAXPROCS(runtime.NumCPU())

// Tune GC
debug.SetGCPercent(50) // Lower = more frequent GC, less memory
```

#### Python Service Tuning

```python
# Use uvloop for async performance
import uvloop
uvloop.install()

# Increase worker processes
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker
```

---

## Debugging Commands Cheat Sheet

```bash
# Service logs
kubectl logs -n rilavo -l app=rilavo-service -f

# Previous container logs
kubectl logs -n rilavo -l app=rilavo-service --previous

# Pod details
kubectl describe pod -n rilavo -l app=rilavo-service

# Exec into container
kubectl exec -n rilavo -it deploy/rilavo-service -- /bin/sh

# Redis CLI
kubectl exec -n rilavo deploy/redis -- redis-cli

# Check metrics
curl -s http://localhost:9090/metrics | grep rilavo

# Port forward
kubectl port-forward -n rilavo svc/rilavo-service 8090:80

# Health checks
curl http://localhost:8090/health
curl http://localhost:8090/ready
curl http://localhost:8090/metrics

# Decode credential
echo "<credential_b64url>" | base64 -d | jq .

# Verify JWT-like credential
echo "<credential_b64url>" | base64 -d | jq '.iat, .exp, .aud, .iss'

# Check certificate
openssl x509 -in cert.pem -text -noout

# Test Redis
redis-cli -h redis ping
redis-cli -h redis --latency-history -i 1

# Check config
kubectl get configmap rilavo-config -n rilavo -o yaml

# Check secrets
kubectl get secret -n rilavo
```

---

## Escalation Matrix

| Severity | Response Time | Escalation |
|----------|---------------|------------|
| Critical (service down) | 15 min | Page on-call |
| High (degraded) | 30 min | Notify team lead |
| Medium (degraded) | 2 hours | Assign to engineer |
| Low (minor) | Next business day | Add to backlog |

---

## Useful Links

- [Rilavo Protocol Spec](../wave_2/)
- [SDK Documentation](../wave_2/19_API_SPECIFICATION.md)
- [Monitoring Dashboards](https://grafana.rilavo.org/d/rilavo)
- [Alert Runbooks](./index.md#runbooks)
- [Security Contacts](mailto:security@rilavo.org)
