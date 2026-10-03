---
title: Rate Limiting Middleware
status: Proposed
date: 2024-03-20
deciders: [Rilavo Core Team]
consulted: [SRE Team, SDK Maintainers]
informed: [All Contributors]
---

# ADR-010: Rate Limiting Middleware

## Context and Problem Statement

Production Rilavo deployments need rate limiting to prevent abuse, ensure fair usage, and protect against DoS attacks. Rate limiting must be implemented at the middleware/verification layer and be configurable per deployment.

## Decision Drivers

- Prevent credential stuffing and brute force
- Fair usage across agents/tenants
- DoS protection for verification endpoints
- Configurable per deployment (multi-tenant)
- Minimal latency impact
- Distributed deployment support (Redis)

## Considered Options

### Option 1: Application-Level Rate Limiting (per SDK)

Each SDK implements its own rate limiting.

**Pros:**
- No additional infrastructure
- Simple for single-service deployments

**Cons:**
- Inconsistent limits across SDKs
- No shared state in distributed deployments
- Duplicated implementation effort
- Cannot enforce global limits

### Option 2: Middleware/Proxy Level Rate Limiting (Chosen)

Implement rate limiting at the HTTP middleware layer (Next.js, Go, FastAPI, Express) with shared Redis backend.

**Pros:**
- Consistent limits across all SDKs
- Shared state for distributed deployments
- Configurable algorithms (token bucket, sliding window)
- Per-credential, per-IP, per-tenant limits
- Integration with existing middleware

**Cons:**
- Requires Redis infrastructure
- Added latency (minimal with local cache)
- Additional operational dependency

### Option 3: API Gateway / Reverse Proxy

Use NGINX, Envoy, or cloud provider rate limiting.

**Pros:**
- Centralized, no code changes
- Advanced features (geo, bot detection)

**Cons:**
- Less flexible (limited to HTTP layer)
- Cannot access credential context (per-credential limits)
- Vendor-specific configuration
- Additional infrastructure layer

## Decision Outcome

Chosen option: **Option 2: Middleware/Proxy Level Rate Limiting** with shared Redis backend because it provides the best balance of flexibility, consistency, and integration with existing middleware.

### Rate Limiting Algorithms

1. **Token Bucket** - Smooth rate limiting, allows bursts
2. **Sliding Window Log** - Precise, memory intensive
3. **Sliding Window Counter** - Good balance, used for per-credential limits
4. **Fixed Window** - Simple, but allows bursts at boundaries

### Limit Dimensions

| Dimension | Use Case | Algorithm |
|-----------|----------|-----------|
| Per Credential | Prevent credential abuse | Sliding Window Counter |
| Per Agent DID | Fair usage per agent | Token Bucket |
| Per IP | Basic DoS protection | Fixed Window |
| Per Tenant | Multi-tenant fairness | Token Bucket |
| Global | Overall DoS protection | Fixed Window |

### Implementation

- **Go/Express/FastAPI/Next.js**: Middleware with Redis client
- **Configuration**: YAML/ENV for limits, windows, algorithms
- **Storage**: Redis sorted sets (sliding window) or keys (token bucket)
- **Fallback**: In-memory if Redis unavailable (degraded mode)
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- **Response**: 429 with `Retry-After` header

### Positive Consequences

- Consistent protection across all SDKs
- Shared state for distributed deployments
- Rich configuration per deployment
- Standard rate limit headers

### Negative Consequences

- Redis dependency
- Added latency (~1-2ms)
- Operational complexity (Redis management)

## Implementation Plan

1. Create rate limiting library per SDK (Go, TypeScript, Python, Next.js)
2. Redis-backed sliding window counter implementation
3. Configuration via ENV/YAML
4. Integration with existing middleware
5. Metrics for rate limit hits
6. Documentation and examples

## Links

- [Rate Limiting Algorithms](https://github.com/redis/redis-rate-limiter)
- [Token Bucket](https://en.wikipedia.org/wiki/Token_bucket)
