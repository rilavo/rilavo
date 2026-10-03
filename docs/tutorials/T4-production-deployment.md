# T4 — Production Deployment & Cross-SDK Verification

**What you'll do:** deploy a Rilavo verifier to production and verify cross-SDK credential compatibility. ~15 minutes.

## Prerequisites

- A server or cloud VM with Docker
- A domain name pointed at the server (for TLS)
- Basic familiarity with Docker and reverse proxies

## Step 1 — Build the Docker image

```bash
git clone https://github.com/rilavo/rilavo.git
cd rilavo
docker build -t rilavo-service .
```

## Step 2 — Generate issuer keys

```bash
mkdir -p /etc/rilavo
docker run --rm -v /etc/rilavo:/keys rilavo-service   rilavo keygen --out /keys/issuer.pem > /etc/rilavo/directory_entry.json
```

## Step 3 — Configure the service

Create `/etc/rilavo/config.env`:

```env
RILAVO_ISSUER_KEY=/keys/issuer.pem
RILAVO_VERIFIER_ID=verifier:api.yourdomain.com
RILAVO_OTEL_ENDPOINT=https://otel.yourdomain.com:4318
RILAVO_OTEL_SAMPLING=0.1
```

## Step 4 — Run with systemd

Create `/etc/systemd/system/rilavo.service`:

```ini
[Unit]
Description=Rilavo Authorization Service
After=network.target

[Service]
Type=simple
EnvironmentFile=/etc/rilavo/config.env
ExecStart=/usr/bin/docker run --rm \
  --name rilavo \
  -p 8090:8090 \
  -p 9090:9090 \
  -v /etc/rilavo:/keys:ro \
  rilavo-service \
  rilavo service --port 8090 --metrics-port 9090 \
    --issuer-key /keys/issuer.pem \
    --verifier-id $RILAVO_VERIFIER_ID \
    --otel-endpoint $RILAVO_OTEL_ENDPOINT \
    --otel-sampling $RILAVO_OTEL_SAMPLING
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now rilavo
```

## Step 5 — Verify the deployment

```bash
# Health check
curl https://api.yourdomain.com/healthz

# Directory entry (publish this for verifiers)
curl https://api.yourdomain.com/directory

# Metrics (Prometheus)
curl https://api.yourdomain.com/metrics
```

## Step 6 — Cross-SDK verification test

Test that credentials issued by one SDK verify correctly with another:

```bash
# Using Python SDK to issue
uv run rilavo keygen --out issuer.pem > directory_entry.json

uv run python -c "
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import base64
k = Ed25519PrivateKey.generate()
open('agent.pem','wb').write(k.private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption()))
print(base64.urlsafe_b64encode(
    k.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode().rstrip('='))
" > agent_pub.txt

uv run rilavo issue --key issuer.pem \
  --principal myorg:worker-1 --agent agt_001 \
  --agent-key \$(cat agent_pub.txt) \
  --action-class data.read --audience verifier:api.yourdomain.com > credential.json
```

```typescript
// Using TypeScript SDK to verify
import { verifyCredential, NonceCache } from '@rilavo/sdk';

const result = verifyCredential(
  credential,
  popRequest,
  { issuerDirectory, revocationLog, nonceCache, verifierAudience: 'verifier:api.yourdomain.com' }
);

console.log(result.accepted ? '✅ Verified' : '❌ Rejected:', result.reasonCode);
```

```go
// Using Go SDK to verify
import "github.com/rilavo/rilavo-go"

result := rilavo.VerifyCredential(credential, popRequest, rilavo.VerifyOptions{
    IssuerDirectory: directory,
    RevocationLog:   revLog,
    NonceCache:      nonceCache,
    VerifierAudience: "verifier:api.yourdomain.com",
})

fmt.Println(result.Accepted, result.ReasonCode)
```

## Step 7 — Set up reverse proxy (nginx example)

```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Step 8 — Monitoring & alerting

The service exposes Prometheus metrics at `/metrics`. Key metrics to alert on:

- `rilavo_verify_total{result="rejected"}` — spike indicates attack
- `rilavo_verify_duration_seconds` — p99 > 10ms needs investigation
- `rilavo_revocation_cache_stale` — should be 0
- `rilavo_nonce_cache_size` — monitor for memory growth

## Next steps

- [ ] Configure log aggregation (Loki, Datadog, etc.)
- [ ] Set up certificate rotation for issuer keys (90-day default)
- [ ] Implement revocation log sync from upstream
- [ ] Load test with `rilavo conformance --target https://api.yourdomain.com`
