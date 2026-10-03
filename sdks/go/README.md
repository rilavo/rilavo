# rilavo-go

Go SDK for Rilavo agent credential verification. Stdlib only.

## 10-line integration

```go
package main

import (
	"net/http"
	rilavo "github.com/rilavo/rilavo-go"
)

func main() {
	dir := rilavo.NewStaticDirectory(yourIssuerPEM, yourCutoff)
	mux := http.NewServeMux()
	mux.HandleFunc("/api", yourHandler)
	http.ListenAndServe(":8080",
		rilavo.WithRilavo(rilavo.MiddlewareConfig{
			Audience:        "verifier:yourdomain.example",
			IssuerDirectory: dir,
		})(mux))
}
```

## What is verified

Gate order mirrors the Python reference verifier exactly:
version → expiry → audience → issuer lookup → cutoff → signature →
replay → revocation → PoP → scope.

## Honest notes

- No TLS pinning, no mTLS — transport security is your reverse proxy's job.
- Replay cache is in-memory per process; use a shared store if you run
  multiple replicas behind a load balancer.
- The disclosure window and other Open decision numbers are not hardcoded.
