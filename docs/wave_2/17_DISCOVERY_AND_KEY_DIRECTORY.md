# Rilavo Protocol — Discovery & Key Directory (P-17)

**Tree:** Protocol  
**Wave:** 2 — Engineering Core  
**Status:** Decided (v0)  
**Depends on:** P-15 (Key Management)  
**Closes when:** Reopens the day a second issuer exists — a single published directory silently recreates centralization at the discovery layer even after issuance itself decentralizes, so this document is explicitly flagged as a second-order risk, not just a convenience to revisit eventually.

---

## The Problem

Verifiers need to find an issuer's public key to verify credentials. How do they find it?

### v0 Mechanism: Single Published Key Directory

A single, published, versioned key directory — **not DNS-based, not blockchain-based**. The simplest thing that correctly works when there is one issuer.

### v0 Directory Entry Format

```json
{
  "issuer": "rilavo:iss:8f2a...c91",
  "public_key": "base64url(...)",
  "valid_from": 1754900000,
  "valid_until": null,
  "directory_version": 14
}
```

| Field | Description |
|-------|-------------|
| `issuer` | Issuer identifier (fingerprint of public key) |
| `public_key` | Issuer's Ed25519 public key, base64url |
| `valid_from` | Unix seconds — when this entry becomes valid |
| `valid_until` | Unix seconds — when this entry expires (null = no expiry) |
| `directory_version` | Monotonically increasing version number |

---

## How Verifiers Use the Directory

### At Startup (or periodically)
1. Fetch directory from known URL
2. Validate signature/integrity
3. Cache entries in memory
4. Refresh periodically (default: 5 minutes)

### At Verification Time
1. Extract `iss` from credential
2. Look up `iss` in local cache
3. If found and valid → use public key for signature verification
4. If not found → `unknown_issuer` reject

---

## Directory Entry Lifecycle

### Creation
When an issuer generates a new keypair:
1. Generate Ed25519 keypair
2. Compute issuer ID: `rilavo:iss:` + first 16 hex chars of SHA-256(raw public key)
3. Create directory entry with `valid_from` = now, `valid_until` = null
4. Publish to directory

### Rotation
When rotating keys:
1. Generate new keypair
2. Create new directory entry with `valid_from` = now
3. Update old entry's `valid_until` = rotation time
3. Publish updated directory
4. Wait for verifiers to refresh (max 5 min cache TTL)
5. Old credentials naturally expire (max 4h TTL)

### Compromise Response
If a key is compromised:
1. Set `valid_until` = compromise timestamp (or now)
2. Publish updated directory immediately
3. All verifiers will reject credentials signed after `valid_until` on next cache refresh

---

## Directory Publication

### v0: Single Static File (Simplest)

```
GET https://issuer.example.com/.well-known/rilavo-directory.json
```

**Response:**
```json
{
  "version": 14,
  "updated_at": 1755000000,
  "entries": [
    {
      "issuer": "rilavo:iss:8f2a...c91",
      "public_key": "base64url(...)",
      "valid_from": 1754900000,
      "valid_until": null,
      "directory_version": 14
    }
  ]
}
```

### Future: Multiple Issuers

When a second issuer exists, the directory becomes a **registry**. The current v0 design assumes a single issuer; multi-issuer support is explicitly deferred to post-v0.

---

## Verifier Implementation

```python
class KeyDirectory:
    def __init__(self, directory_url, refresh_interval=300):
        self.directory_url = directory_url
        self.refresh_interval = refresh_interval
        self._cache = {}
        self._last_refresh = 0

    def lookup(self, issuer_id):
        self._maybe_refresh()
        return self._cache.get(issuer_id)

    def _maybe_refresh(self):
        if time.time() - self._last_refresh > self.refresh_interval:
            self._refresh()

    def _refresh(self):
        response = httpx.get(self.directory_url)
        data = response.json()

        # Validate directory structure
        for entry in data["entries"]:
            # Verify public key format
            # Check valid_from/valid_until
            pass

        self._cache = {e["issuer"]: e for e in data["entries"]}
        self._last_refresh = time.time()
```

### Fail-Closed Behavior
- If directory fetch fails → cache stale → **reject** (`unknown_issuer`)
- If entry not found → **reject** (`unknown_issuer`)
- If entry expired (`valid_until` < now) → **reject** (`key_not_valid_at_issuance`)

---

## Security Considerations

| Threat | Mitigation |
|--------|------------|
| Directory tampering | Publish via HTTPS; verifiers can pin hash |
| Key compromise | `valid_until` cutoff + directory update |
| Directory poisoning | HTTPS + optional hash pinning |
| Directory unavailability | Fail-closed (cache stale → reject) |
| Stale cache | 5-minute TTL + fail-closed on stale |

---

## The Second-Order Risk (Why This Closes When a Second Issuer Exists)

> **A single published directory silently recreates centralization at the discovery layer even after issuance itself decentralizes.**

In v0, there's one issuer → one directory. When a second issuer exists:
- Who operates the directory?
- Who decides which issuers are listed?
- How do verifiers discover multiple issuers?

This is a **second-order risk** — it doesn't affect v0 security, but it's a structural risk that emerges at scale. The document explicitly flags this so it's not forgotten.

---

## Future: Multi-Issuer Discovery (Post-v0)

| Approach | Trade-offs |
|----------|------------|
| **Federated directories** | Each issuer publishes own; verifiers configure multiple sources |
| **DNS-based (DANE-like)** | DNSSEC + TLSA-like records |
| **Blockchain/DHT** | Decentralized but complex |
| **Central registry** | Simple but recreates centralization |

**Decision deferred** — will be revisited when a second issuer exists.

---

## Verifier Implementation Checklist

- [ ] Fetch directory over HTTPS
- [ ] Validate JSON structure
- [ ] Cache with TTL (default 5 min)
- [ ] Fail-closed on stale cache
- [ ] Validate entry structure (required fields)
- [ ] Check `valid_from` / `valid_until`
- [ ] Handle `valid_until = null` (no expiry)
- [ ] Log refresh failures
- [ ] Alert on refresh failures

---

> **Try it first:** [Interactive Playground](../playground/index.md) — issue and verify credentials in your browser without setting up infrastructure.