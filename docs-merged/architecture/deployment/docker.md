---
title: Docker Best Practices
description: Production-ready Docker images for Rilavo services and SDKs
---

# Docker Best Practices for Rilavo

## Multi-Stage Builds

Use multi-stage builds to minimize final image size and attack surface.

### Python Service (rilavo-protocol)

```dockerfile
# syntax = docker/dockerfile:1.4

# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends     gcc     libffi-dev     && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv &&     uv pip install --system --no-cache .

# Runtime stage
FROM python:3.11-slim AS runtime

# Create non-root user
RUN groupadd -r rilavo && useradd -r -g rilavo rilavo

WORKDIR /app

# Copy only runtime dependencies
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=rilavo:rilavo src/ ./src/
COPY --chown=rilavo:rilavo scripts/ ./scripts/

# Security: Drop capabilities, read-only rootfs
USER rilavo
RUN mkdir -p /app/data && chown rilavo:rilavo /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3     CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8090/health')"

EXPOSE 8090
CMD ["python", "-m", "rilavo.service"]
```

### Go SDK Service

```dockerfile
# syntax = docker/dockerfile:1.4

# Build stage
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache git make

# Cache dependencies
COPY go.mod go.sum ./
RUN go mod download

# Build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build     -ldflags="-s -w"     -o /rilavo-service ./cmd/service

# Runtime stage
FROM gcr.io/distroless/static-debian12 AS runtime

# Non-root user (distroless has nonroot:nonroot)
USER nonroot:nonroot

COPY --from=builder /rilavo-service /rilavo-service

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3     CMD ["/rilavo-service", "health"]

EXPOSE 8090
ENTRYPOINT ["/rilavo-service"]
```

### Next.js Middleware

```dockerfile
# syntax = docker/dockerfile:1.4

# Base image with Node.js
FROM node:20-alpine AS base

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Build
COPY . .
RUN npm run build

# Runtime
FROM node:20-alpine AS runtime

WORKDIR /app

# Non-root user
RUN addgroup -g 1001 -S nodejs &&     adduser -S nextjs -u 1001 -G nodejs

COPY --from=base --chown=nextjs:nodejs /app/public ./public
COPY --from=base --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=base --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV NODE_ENV=production

CMD ["node", "server.js"]
```

## Security Hardening

### Image Scanning

```yaml
# .github/workflows/security.yml
- name: Scan Docker image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'rilavo/service:${{ github.sha }}'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

### Security Best Practices

1. **Use distroless/minimal base images** - Reduce attack surface
2. **Run as non-root user** - Drop privileges
3. **Read-only root filesystem** - Prevent tampering
4. **Drop all capabilities** - `docker run --cap-drop=ALL`
5. **Scan for vulnerabilities** - Trivy in CI
5. **Sign images** - cosign for supply chain security
6. **Pin base image digests** - Not just tags
6. **Multi-arch builds** - Support arm64/amd64

## Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  rilavo-service:
    build:
      context: ./rilavo-protocol
      dockerfile: Dockerfile
    ports:
      - "8090:8090"
    environment:
      - RILAVO_VERIFIER_ID=verifier:local
      - RILAVO_ISSUER_SEED=file:/seeds/issuer.seed
      - RILAVO_SERVE_DISCOVERY=true
      - RILAVO_METRICS_PORT=9090
    volumes:
      - ./seeds:/seeds:ro
      - rilavo-data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8090/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./grafana/datasources:/etc/grafana/provisioning/datasources:ro

volumes:
  rilavo-data:
  redis-data:
  prometheus-data:
  grafana-data:
```

## Production Deployment

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rilavo-service
  labels:
    app: rilavo-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rilavo-service
  template:
    metadata:
      labels:
        app: rilavo-service
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
      - name: rilavo-service
        image: ghcr.io/rilavo/rilavo-service:v0.1.0
        ports:
        - containerPort: 8090
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: RILAVO_VERIFIER_ID
          valueFrom:
            configMapKeyRef:
              name: rilavo-config
              key: verifier-id
        - name: RILAVO_ISSUER_SEED
          valueFrom:
            secretKeyRef:
              name: rilavo-secrets
              key: issuer-seed
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8090
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8090
          initialDelaySeconds: 5
          periodSeconds: 10
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop: ["ALL"]
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: data
          mountPath: /app/data
      volumes:
      - name: tmp
        emptyDir: {}
      - name: data
        persistentVolumeClaim:
          claimName: rilavo-data
---
apiVersion: v1
kind: Service
metadata:
  name: rilavo-service
spec:
  selector:
    app: rilavo-service
  ports:
  - name: http
    port: 80
    targetPort: 8090
  - name: metrics
    port: 9090
    targetPort: 9090
```

## Image Publishing

```yaml
# .github/workflows/publish.yml
name: Publish Images

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/rilavo/rilavo-service
          tags: |
            type=ref,event=tag
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./rilavo-protocol
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: true
          sbom: true
```

---

## Next Steps

- [Kubernetes Deployment Guide](kubernetes.md)
- [Monitoring Setup](../monitoring/prometheus-grafana.md)
- [Security Hardening](../security/hardening.md)
