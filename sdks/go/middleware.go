package rilavo

import (
	"context"
	"encoding/json"
	"net/http"
	"strings"
	"time"
)

// CredentialHeader is the header carrying the base64url credential JSON.
const CredentialHeader = "X-Rilavo-Credential"

// PopSignatureHeader carries the base64url PoP signature.
const PopSignatureHeader = "X-Rilavo-Pop-Signature"

// RequestNonceHeader carries the request-level nonce.
const RequestNonceHeader = "X-Rilavo-Request-Nonce"

// ActionHeader carries the requested action class.
const ActionHeader = "X-Rilavo-Action"

type contextKey string

// CtxVerifyResult is the context key for storing VerifyResult.
const CtxVerifyResult contextKey = "rilavo_verify_result"

// MiddlewareConfig configures the net/http middleware.
type MiddlewareConfig struct {
	Audience        string
	NowSeconds      int64 // 0 = use real wall-clock time
	IssuerDirectory KeyDirectory
	RevocationLog   RevocationChecker
	NonceCache      NonceCache
	PublicPaths     []string // exact paths that skip verification
}

// WithRilavo returns an http.Handler middleware that gates requests on
// Rilavo credential verification. On accept, the VerifyResult is stored in
// the request context under CtxVerifyResult. On reject, a 401 with a JSON
// reason-code body is returned (fail-closed).
func WithRilavo(opts MiddlewareConfig) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			for _, pp := range opts.PublicPaths {
				if r.URL.Path == pp || strings.HasPrefix(r.URL.Path, pp+"/") {
					next.ServeHTTP(w, r)
					return
				}
			}
			credJSON := r.Header.Get(CredentialHeader)
			if credJSON == "" {
				writeReject(w, "no_credentials")
				return
			}
			popSig := r.Header.Get(PopSignatureHeader)
			popNonce := r.Header.Get(RequestNonceHeader)
			action := r.Header.Get(ActionHeader)
			if action == "" {
				action = strings.TrimPrefix(r.URL.Path, "/")
			}
			now := opts.NowSeconds
			if now == 0 {
				now = timeNow()
			}

			result := Verify([]byte(credJSON), VerifyOptions{
				Audience:        opts.Audience,
				IssuerDirectory: opts.IssuerDirectory,
				RevocationLog:   opts.RevocationLog,
				NonceCache:      opts.NonceCache,
				NowSeconds:      now,
				Method:          r.Method,
				Path:            r.URL.Path,
				RequestedAction: action,
				PopSignature:    popSig,
				PopNonce:        popNonce,
			})
			if !result.Accepted {
				writeReject(w, result.ReasonCode)
				return
			}
			ctx := context.WithValue(r.Context(), CtxVerifyResult, result)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

var timeNow = time.Now().Unix

func writeReject(w http.ResponseWriter, reason string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusUnauthorized)
	json.NewEncoder(w).Encode(map[string]string{"error": reason})
}

// GetVerifyResult extracts the VerifyResult from a request context
// (populated by WithRilavo on accept).
func GetVerifyResult(ctx context.Context) *VerifyResult {
	v, ok := ctx.Value(CtxVerifyResult).(*VerifyResult)
	if !ok {
		return nil
	}
	return v
}

// NewStaticDirectory creates a KeyDirectory from a PEM string and cutoff.
func NewStaticDirectory(pem string, validUntil int64) KeyDirectory {
	return &staticDirFromPem{pem: pem, validUntil: validUntil}
}

type staticDirFromPem struct {
	pem         string
	validUntil  int64
}

func (d *staticDirFromPem) Lookup(issuerID string) *IssuerKeyEntry {
	return &IssuerKeyEntry{
		IssuerID:     issuerID,
		PublicKeyPem: d.pem,
		ValidUntil:   d.validUntil,
	}
}
