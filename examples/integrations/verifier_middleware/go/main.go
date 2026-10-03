package main

import (
	"crypto/ed25519"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/rilavo/rilavo-go"
)

// Configuration
const (
	verifierAudience = "verifier:go-middleware-example.com"
	port             = ":8080"
)

// In-memory stores (use Redis/database in production)
var (
	nonceCache   = &memoryNonceCache{seen: make(map[string]int64)}
	revocationLog = &memoryRevocationLog{revoked: make(map[string]bool)}
	issuerDir    = rilavo.NewStaticDirectory(issuerPem, 0) // 0 = no cutoff
)

// issuerPem is the SPKI public key PEM for the demo issuer
// In production, fetch from issuer's /.well-known/rilavo
const issuerPem = `-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAKTZf8J3E5JzXq7Q2vZ8Y9pK1L6mN3R4tV7wX8yA2B1C==
-----END PUBLIC KEY-----`

// memoryNonceCache implements rilavo.NonceCache
type memoryNonceCache struct {
	seen map[string]int64
}

func (m *memoryNonceCache) SeenBefore(nonce string, windowSeconds int64, now int64) bool {
	// Clean expired entries
	for n, exp := range m.seen {
		if exp <= now {
			delete(m.seen, n)
		}
	}
	if m.seen[nonce] > now {
		return true
	}
	m.seen[nonce] = now + windowSeconds
	return false
}

// memoryRevocationLog implements rilavo.RevocationChecker
type memoryRevocationLog struct {
	revoked map[string]bool
}

func (m *memoryRevocationLog) IsRevoked(nonce string) bool {
	return m.revoked[nonce]
}

// CredentialResponse for JSON responses
type CredentialResponse struct {
	Credential map[string]interface{} `json:"credential"`
}

// PopResponse for JSON responses
type PopResponse struct {
	Method         string `json:"method"`
	Path           string `json:"path"`
	Action         string `json:"action"`
	Signature      string `json:"signature"`
	RequestNonce   string `json:"request_nonce"`
}

// Demo credentials (pre-issued for testing)
// In production, these would be issued by a Python/TypeScript service
var demoCredentials = map[string]map[string]interface{}{}

func main() {
	// Generate keys for demo
	agentPriv, agentPub := loadOrGenerateKeys()
	agentPubB64 := base64.RawURLEncoding.EncodeToString(agentPub)

	// Pre-issue a demo credential
	issuerSeed := []byte("demo-issuer-seed-32-bytes-long!!")
	demoCred := issueCredential(issuerSeed, "test-principal", "test-agent", agentPubB64, "data.read", verifierAudience)
	demoCredentials[demoCred["nonce"].(string)] = demoCred

	// HTTP routes
	mux := http.NewServeMux()

	// Public endpoints
	mux.HandleFunc("/health", healthHandler)
	mux.HandleFunc("/public/info", publicInfoHandler)

	// Admin endpoints (no auth required for demo)
	mux.HandleFunc("/admin/issue-test-credential", issueTestCredentialHandler(agentPubB64))
	mux.HandleFunc("/admin/sign-pop", signPopHandler(agentPriv))

	// Protected endpoints with Rilavo middleware
	rilavoMiddleware := rilavo.WithRilavo(rilavo.MiddlewareConfig{
		Audience:        verifierAudience,
		IssuerDirectory: issuerDir,
		RevocationLog:   revocationLog,
		NonceCache:      nonceCache,
		PublicPaths:     []string{"/health", "/public"},
	})

	mux.Handle("/protected/data", rilavoMiddleware(http.HandlerFunc(protectedDataHandler)))
	mux.Handle("/protected/dependency-style", rilavoMiddleware(http.HandlerFunc(protectedDependencyStyleHandler)))

	// Start server
	fmt.Printf("Server starting on %s\n", port)
	fmt.Printf("Audience: %s\n", verifierAudience)
	fmt.Println()
	fmt.Println("Test with:")
	fmt.Println("  1. POST /admin/issue-test-credential -> get credential")
	fmt.Println("  2. POST /admin/sign-pop -> get PoP signature")
	fmt.Println("  3. GET /protected/data with headers:")
	fmt.Println("     x-rilavo-credential: <credential>")
	fmt.Println("     x-rilavo-action: data.read")
	fmt.Println("     x-rilavo-pop-signature: <signature>")
	fmt.Println("     x-rilavo-request-nonce: <nonce>")

	log.Fatal(http.ListenAndServe(port, mux))
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "ok", "verifier": verifierAudience})
}

func publicInfoHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"public": true,
		"message": "No authentication required",
	})
}

func issueTestCredentialHandler(agentPubB64 string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var req struct {
			Principal   string `json:"principal"`
			Agent       string `json:"agent"`
			ActionClass string `json:"action_class"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			req.Principal = "test-principal"
			req.Agent = "test-agent"
			req.ActionClass = "data.read"
		}

		issuerSeed := []byte("demo-issuer-seed-32-bytes-long!!")
		cred := issueCredential(issuerSeed, req.Principal, req.Agent, agentPubB64, req.ActionClass, verifierAudience)
		demoCredentials[cred["nonce"].(string)] = cred

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(CredentialResponse{Credential: cred})
	}
}

func signPopHandler(agentPriv ed25519.PrivateKey) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var req struct {
			Method string `json:"method"`
			Path   string `json:"path"`
			Action string `json:"action"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			req.Method = "GET"
			req.Path = "/protected/data"
			req.Action = "data.read"
		}

		signature, nonce := signRequest(agentPriv, req.Method, req.Path, req.Action)

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(PopResponse{
			Method:       req.Method,
			Path:         req.Path,
			Action:       req.Action,
			Signature:    signature,
			RequestNonce: nonce,
		})
	}
}

func protectedDataHandler(w http.ResponseWriter, r *http.Request) {
	// Get verification result from context
	result := rilavo.GetVerifyResult(r.Context())
	if result == nil || !result.Accepted {
		http.Error(w, `{"error":"unauthorized"}`, http.StatusUnauthorized)
		return
	}

	// Extract credential fields from the request
	credHeader := r.Header.Get("X-Rilavo-Credential")
	var credFields map[string]interface{}
	if credHeader != "" {
		credJSON, _ := base64.RawURLEncoding.DecodeString(credHeader)
		json.Unmarshal(credJSON, &credFields)
	}

	auth := map[string]string{
		"principal":     credFields["sub"].(string),
		"agent":         credFields["agt"].(string),
		"action_class":  credFields["act"].(string),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"data": "Sensitive data accessed successfully",
		"authenticated_as": auth,
	})
}

func protectedDependencyStyleHandler(w http.ResponseWriter, r *http.Request) {
	result := rilavo.GetVerifyResult(r.Context())
	if result == nil || !result.Accepted {
		http.Error(w, `{"error":"unauthorized"}`, http.StatusUnauthorized)
		return
	}

	credHeader := r.Header.Get("X-Rilavo-Credential")
	var credFields map[string]interface{}
	if credHeader != "" {
		credJSON, _ := base64.RawURLEncoding.DecodeString(credHeader)
		json.Unmarshal(credJSON, &credFields)
	}

	auth := map[string]string{
		"principal":     credFields["sub"].(string),
		"agent":         credFields["agt"].(string),
		"action_class":  credFields["act"].(string),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"data": "Accessed via middleware chain",
		"authenticated_as": auth,
	})
}

func loadOrGenerateKeys() (ed25519.PrivateKey, ed25519.PublicKey) {
	// In production, load from secure storage
	// For demo, generate new keys each time
	pub, priv, _ := ed25519.GenerateKey(rand.Reader)
	return priv, pub
}

// ============================================================================
// Credential issuance and PoP signing (implemented locally since Go SDK is verify-only)
// In production, use Python/TypeScript SDK for issuance
// ============================================================================

func issueCredential(issuerSeed []byte, principal, agent, agentPubB64, actionClass, audience string) map[string]interface{} {
	// Generate keys from seed
	privKey := ed25519.NewKeyFromSeed(issuerSeed)
	pubKey := privKey.Public().(ed25519.PublicKey)

	now := time.Now().Unix()
	ttl := int64(14400) // 4 hours
	nonce := generateNonce()

	// Build credential fields
	fields := map[string]interface{}{
		"iss": issuerID(pubKey),
		"sub": principal,
		"agt": agent,
		"apk": agentPubB64,
		"act": actionClass,
		"aud": audience,
		"iat": now,
		"exp": now + ttl,
		"nonce": nonce,
	}

	// Sign the canonicalized fields (without sig)
	signingFields := make(map[string]interface{})
	for k, v := range fields {
		signingFields[k] = v
	}
	canonical, _ := rilavo.Canonicalize(signingFields)
	sig := ed25519.Sign(privKey, canonical)
	fields["sig"] = base64.RawURLEncoding.EncodeToString(sig)

	return fields
}

func signRequest(priv ed25519.PrivateKey, method, path, action string) (string, string) {
	nonce := generateNonce()
	payload := rilavo.PopRequestPayload(method, path, action, nonce)
	sig := ed25519.Sign(priv, payload)
	return base64.RawURLEncoding.EncodeToString(sig), nonce
}

func generateNonce() string {
	b := make([]byte, 16)
	rand.Read(b)
	return base64.RawURLEncoding.EncodeToString(b)
}

func issuerID(pub ed25519.PublicKey) string {
	hash := sha256.Sum256(pub)
	return "rilavo:iss:" + hex.EncodeToString(hash[:])[:16]
}

func base64URLDecode(s string) ([]byte, error) {
	padding := 4 - len(s)%4
	if padding != 4 {
		s += strings.Repeat("=", padding)
	}
	return base64.URLEncoding.DecodeString(s)
}
