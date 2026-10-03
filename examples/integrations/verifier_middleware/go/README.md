# Go HTTP Middleware Example

Complete Go standard library integration using `rilavo-go` for credential verification.

## Quick Start

```bash
cd examples/verifier_middleware/go
go mod tidy
go run main.go
```

Server runs on `http://localhost:8080`.

## Usage

### 1. Install Dependencies

```bash
go get github.com/rilavo/rilavo-go
```

### 2. Create Middleware

```go
// middleware/rilavo.go
package middleware

import (
    "context"
    "encoding/json"
    "net/http"
    "strings"

    "github.com/rilavo/rilavo-go"
)

// Config holds the middleware configuration
type Config struct {
    Audience         string
    HeaderName       string
    PublicPaths      []string
    IssuerDirectory  rilavo.KeyDirectory
    RevocationLog    rilavo.RevocationLog
    NonceCache       rilavo.NonceCache
    NowSeconds       int64 // optional, for testing
}

// DefaultConfig returns a default configuration
func DefaultConfig() Config {
    return Config{
        HeaderName:  "x-rilavo-credential",
        PublicPaths: []string{"/health", "/public"},
    }
}

// Middleware returns an HTTP middleware that verifies Rilavo credentials
func Middleware(cfg Config) func(http.Handler) http.Handler {
    if cfg.HeaderName == "" {
        cfg.HeaderName = "x-rilavo-credential"
    }

    if cfg.NonceCache == nil {
        cfg.NonceCache = rilavo.NewNonceCache()
    }

    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            // Skip public paths
            path := r.URL.Path
            for _, p := range cfg.PublicPaths {
                if path == p || strings.HasPrefix(path, p+"/") {
                    next.ServeHTTP(w, r)
                    return
                }
            }

            // Get credential from header
            credentialB64url := r.Header.Get(cfg.HeaderName)
            if credentialB64url == "" {
                writeJSON(w, http.StatusUnauthorized, map[string]string{"error": "no_credentials"})
                return
            }

            // Parse credential
            var cred rilavo.CredentialFields
            if err := rilavo.DecodeCredential(credentialB64url, &cred); err != nil {
                writeJSON(w, http.StatusUnauthorized, map[string]string{"error": "malformed_credential"})
                return
            }

            // Build PoP request from headers
            pop := rilavo.PopRequest{
                Method:          r.Method,
                Path:            r.URL.Path,
                RequestedAction: r.Header.Get("x-rilavo-action"),
                Signature:       r.Header.Get("x-rilavo-pop-signature"),
                RequestNonce:    r.Header.Get("x-rilavo-request-nonce"),
            }

            // Verify credential
            opts := rilavo.VerifyOptions{
                IssuerDirectory:  cfg.IssuerDirectory,
                RevocationLog:    cfg.RevocationLog,
                NonceCache:       cfg.NonceCache,
                VerifierAudience: cfg.Audience,
                NowSeconds:       cfg.NowSeconds,
            }

            result := rilavo.VerifyCredential(cred, pop, opts)
            if !result.Accepted {
                writeJSON(w, http.StatusUnauthorized, map[string]string{"error": result.ReasonCode})
                return
            }

            // Credential verified, attach to request context
            ctx := context.WithValue(r.Context(), "rilavo_credential", cred)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}

func writeJSON(w http.ResponseWriter, status int, data interface{}) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}
```

### 3. Usage

```go
// main.go
package main

import (
    "context"
    "net/http"

    "github.com/rilavo/rilavo-go"
    "myapp/middleware"
)

func main() {
    // Configure issuer directory
    issuerDir := &MyIssuerDirectory{}

    // Configure revocation log
    revLog := &MyRevocationLog{}

    // Create middleware
    cfg := middleware.Config{
        Audience:         "myapp.example.com",
        IssuerDirectory:  issuerDir,
        RevocationLog:    revLog,
    }
    rilavoMiddleware := middleware.Middleware(cfg)

    // Create HTTP handler
    mux := http.NewServeMux()

    // Public routes
    mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
    })

    // Protected routes
    protected := http.NewServeMux()
    protected.HandleFunc("/api/data", func(w http.ResponseWriter, r *http.Request) {
        // Access verified credential from context
        if cred, ok := r.Context().Value("rilavo_credential").(rilavo.CredentialFields); ok {
            json.NewEncoder(w).Encode(map[string]interface{}{
                "data": "sensitive data",
                "user": cred["sub"],
            })
        }
    })
    protected.HandleFunc("/api/action", func(w http.ResponseWriter, r *http.Request) {
        json.NewEncoder(w).Encode(map[string]string{"success": "true"})
    })

    // Apply middleware to protected routes
    mux.Handle("/api/", middleware.Middleware(middleware.Config{
        Audience:        "myapp.example.com",
        IssuerDirectory: &MyIssuerDirectory{},
        RevocationLog:   &MyRevocationLog{},
    })(protected))

    // Public routes (no middleware)
    mux.Handle("/health", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
    }))

    http.ListenAndServe(":8080", mux)
}
```

### 4. Issuer Directory Implementation

```go
type MyIssuerDirectory struct{}

func (d *MyIssuerDirectory) Lookup(issuerId string) (*rilavo.IssuerKeyEntry, error) {
    // In production, fetch from issuer's /directory endpoint
    // and cache the results

    // Example: known issuers
    known := map[string]*rilavo.IssuerKeyEntry{
        "did:example:issuer1": {
            IssuerId:     "did:example:issuer1",
            PublicKeyPEM: `-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEA...
-----END PUBLIC KEY-----`,
            ValidUntil:   time.Now().AddDate(1, 0, 0).Unix(),
        },
    }

    if entry, ok := known[issuerId]; ok {
        return entry, nil
    }
    return nil, nil
}

func (d *MyIssuerDirectory) Unreachable() bool {
    return false
}
```

### 5. Revocation Log Implementation

```go
type MyRevocationLog struct {
    redis *redis.Client
}

func (r *MyRevocationLog) IsRevoked(nonce string) bool {
    // Check Redis with TTL matching credential expiry
    exists, err := r.redis.SIsMember(context.Background(), "revoked_nonces", nonce).Result()
    return err == nil && exists
}
```

## Client-Side: Agent Making Requests

```go
// Agent code
package main

import (
    "crypto/ed25519"
    "encoding/base64"
    "net/http"
    "time"

    "github.com/rilavo/rilavo-go"
)

func main() {
    // Load agent private key
    agentPriv := loadPrivateKey()

    // Get credential from issuer
    credential := getCredentialFromIssuer()

    // Prepare PoP
    nonce := generateNonce()
    popPayload := rilavo.PopRequestPayload("POST", "/api/action", "data.write", nonce)
    signature := ed25519.Sign(agentPrivateKey, popPayload)

    // Make request
    req, _ := http.NewRequest("POST", "https://myapp.example.com/api/action", payload)
    req.Header.Set("x-rilavo-credential", credential)
    req.Header.Set("x-rilavo-method", "POST")
    req.Header.Set("x-rilavo-path", "/api/action")
    req.Header.Set("x-rilavo-action", "data.write")
    req.Header.Set("x-rilavo-pop-signature", base64.RawURLEncoding.EncodeToString(signature))
    req.Header.Set("x-rilavo-request-nonce", nonce)

    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()
}
```

## Production Considerations

1. **Issuer Directory**: Fetch from `https://{issuer}/.well-known/rilavo` and cache with TTL
2. **Revocation Log**: Use Redis with TTL matching credential expiry
3. **Nonce Cache**: Use Redis with sliding window expiration (use `rilavo.NewRedisNonceCache()`)
4. **Rate Limiting**: Add rate limiting per credential/agent
5. **Logging**: Log verification results for audit trails
6. **Error Handling**: Distinguish between auth errors and server errors

## Running Tests

```bash
cd examples/verifier_middleware/go
go test ./...
```
