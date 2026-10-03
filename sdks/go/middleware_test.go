package rilavo

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

// TestMiddlewareNoCredentials verifies fail-closed behavior when no
// credential header is present.
func TestMiddlewareNoCredentials(t *testing.T) {
	v := loadVectors(t)
	dir := &staticDir{entry: makeIssuerEntry(v.IssuerPubB64url)}
	cache := &memNonceCache{seen: make(map[string]int64)}
	mw := WithRilavo(MiddlewareConfig{
		Audience:        "verifier:test",
		IssuerDirectory: dir,
		RevocationLog:   &noopRevocation{},
		NonceCache:      cache,
	})
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		t.Error("handler should not be called")
	})
	req := httptest.NewRequest("GET", "/data", nil)
	rec := httptest.NewRecorder()
	mw(handler).ServeHTTP(rec, req)

	if rec.Code != http.StatusUnauthorized {
		t.Errorf("expected 401, got %d", rec.Code)
	}
	var body map[string]string
	json.Unmarshal(rec.Body.Bytes(), &body)
	if body["error"] != "no_credentials" {
		t.Errorf("expected no_credentials, got %s", body["error"])
	}
}

// TestMiddlewarePublicPathBypass verifies that public paths skip auth.
func TestMiddlewarePublicPathBypass(t *testing.T) {
	v := loadVectors(t)
	dir := &staticDir{entry: makeIssuerEntry(v.IssuerPubB64url)}
	mw := WithRilavo(MiddlewareConfig{
		Audience:        "verifier:x",
		IssuerDirectory: dir,
		RevocationLog:   &noopRevocation{},
		NonceCache:      &memNonceCache{seen: make(map[string]int64)},
		PublicPaths:     []string{"/health"},
	})
	called := false
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		called = true
		w.WriteHeader(200)
	})
	req := httptest.NewRequest("GET", "/health", nil)
	rec := httptest.NewRecorder()
	mw(handler).ServeHTTP(rec, req)
	if !called {
		t.Error("public path handler was not called")
	}
}

// TestMiddlewareRejectReason verifies that a bad credential produces a
// JSON body with a reason code (not just a bare 401).
func TestMiddlewareRejectReason(t *testing.T) {
	v := loadVectors(t)
	dir := &staticDir{entry: makeIssuerEntry(v.IssuerPubB64url)}
	mw := WithRilavo(MiddlewareConfig{
		Audience:        "verifier:x",
		IssuerDirectory: dir,
		RevocationLog:   &noopRevocation{},
		NonceCache:      &memNonceCache{seen: make(map[string]int64)},
	})
	req := httptest.NewRequest("GET", "/data", nil)
	req.Header.Set(CredentialHeader, "{}") // empty cred -> missing_field
	rec := httptest.NewRecorder()
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {})
	mw(handler).ServeHTTP(rec, req)

	if rec.Code != 401 {
		t.Errorf("expected 401, got %d", rec.Code)
	}
	var body map[string]string
	json.Unmarshal(rec.Body.Bytes(), &body)
	if body["error"] == "" {
		t.Error("reject response should contain a reason code")
	}
}
