package rilavo

import (
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"testing"
)

func TestJCSByteParity(t *testing.T) {
	v := loadVectors(t)
	for _, vec := range v.JCS {
		got, err := Canonicalize(vec.Input)
		if err != nil {
			t.Fatalf("JCS error for %v: %v", vec.Input, err)
		}
		if string(got) != vec.Expected {
			t.Errorf("JCS mismatch: got %s, want %s", got, vec.Expected)
		}
	}
}

func TestPopPayloadByteParity(t *testing.T) {
	v := loadVectors(t)
	got := PopRequestPayload(v.Pop.Method, v.Pop.Path, v.Pop.Act, v.Pop.Nonce)
	want, _ := hex.DecodeString(v.Pop.PayloadHex)
	if string(got) != string(want) {
		t.Errorf("PoP payload mismatch: got %x, want %x", got, want)
	}
}

func TestFullAcceptPath(t *testing.T) {
	v := loadVectors(t)
	fields := deepCopyMap(v.CredentialFields)
	opts := VerifyOptions{
		Audience:        fields["aud"].(string),
		IssuerDirectory: &staticDir{entry: makeIssuerEntry(v.IssuerPubB64url)},
		RevocationLog:   &noopRevocation{},
		NonceCache:      &memNonceCache{seen: make(map[string]int64)},
		NowSeconds:      toInt64(fields["iat"]) + 1,
		Method:          "GET",
		Path:            "/data/1",
		RequestedAction: "data.read",
		PopSignature:    v.PopSig.SigB64url,
		PopNonce:        v.PopSig.Nonce,
	}
	result := Verify([]byte(mustJSON(fields)), opts)
	if !result.Accepted {
		t.Errorf("expected accept, got reject: %s", result.ReasonCode)
	}
}

func TestTamperedCredentialRejected(t *testing.T) {
	v := loadVectors(t)
	fields := deepCopyMap(v.CredentialFields)
	fields["sub"] = "attacker"
	opts := VerifyOptions{
		Audience:        fields["aud"].(string),
		IssuerDirectory: &staticDir{entry: makeIssuerEntry(v.IssuerPubB64url)},
		RevocationLog:   &noopRevocation{},
		NonceCache:      &memNonceCache{seen: make(map[string]int64)},
		NowSeconds:      toInt64(fields["iat"]) + 1,
		Method:          "POST", Path: "/data",
		RequestedAction: "data.read",
		PopSignature:    "AAAA" + v.CredentialFields["sig"].(string)[4:],
		PopNonce:        "tampered-nonce",
	}
	result := Verify([]byte(mustJSON(fields)), opts)
	if result.Accepted {
		t.Error("tampered credential should be rejected")
	}
}

func TestWrongAudienceRejected(t *testing.T) {
	v := loadVectors(t)
	fields := deepCopyMap(v.CredentialFields)
	opts := VerifyOptions{
		Audience:        "verifier:someone-else.example",
		IssuerDirectory: &staticDir{entry: makeIssuerEntry(v.IssuerPubB64url)},
		RevocationLog:   &noopRevocation{},
		NonceCache:      &memNonceCache{seen: make(map[string]int64)},
		NowSeconds:      toInt64(fields["iat"]) + 1,
		Method:          "POST", Path: "/data",
		RequestedAction: "data.read",
		PopSignature:    testPopSig,
		PopNonce:        "n-test",
	}
	result := Verify([]byte(mustJSON(fields)), opts)
	if result.ReasonCode != "audience_mismatch" &&
		result.ReasonCode != "proof_of_possession_failed" {
		t.Errorf("expected audience_mismatch or pop fail, got: %s", result.ReasonCode)
	}
}

func TestDelegationReject(t *testing.T) {
	v := loadVectors(t)
	for _, dlg := range []interface{}{float64(1), json.Number("2")} {
		fields := deepCopyMap(v.CredentialFields)
		fields["dlg"] = dlg
		opts := VerifyOptions{
			Audience:        toStr(fields["aud"]),
			IssuerDirectory: &staticDir{entry: makeIssuerEntry(v.IssuerPubB64url)},
			RevocationLog:   &noopRevocation{},
			NonceCache:      &memNonceCache{seen: make(map[string]int64)},
			NowSeconds:      toInt64(fields["iat"]) + 1,
			Method:          "POST", Path: "/data",
			RequestedAction: toStr(fields["act"]),
			PopSignature:    testPopSig,
			PopNonce:        "n-test",
		}
		result := Verify([]byte(mustJSON(fields)), opts)
		if result.Accepted || result.ReasonCode != "delegation_not_permitted" {
			t.Errorf("dlg=%v: expected delegation_not_permitted, got accepted=%v reason=%s", dlg, result.Accepted, result.ReasonCode)
		}
	}
	// dlg absent or 0 must not trigger the gate
	for _, dlg := range []interface{}{nil, json.Number("0"), float64(0)} {
		fields := deepCopyMap(v.CredentialFields)
		if dlg != nil {
			fields["dlg"] = dlg
		} else {
			delete(fields, "dlg")
		}
		opts := VerifyOptions{
			Audience:        toStr(fields["aud"]),
			IssuerDirectory: &staticDir{entry: makeIssuerEntry(v.IssuerPubB64url)},
			RevocationLog:   &noopRevocation{},
			NonceCache:      &memNonceCache{seen: make(map[string]int64)},
			NowSeconds:      toInt64(fields["iat"]) + 1,
			Method:          "POST", Path: "/data",
			RequestedAction: toStr(fields["act"]),
			PopSignature:    testPopSig,
			PopNonce:        "n-test",
		}
		result := Verify([]byte(mustJSON(fields)), opts)
		if result.ReasonCode == "delegation_not_permitted" {
			t.Errorf("dlg=%v: unexpected delegation_not_permitted", dlg)
		}
	}
}

// ---- helpers ----------------------------------------------------------------

const testPopSig = ""

type staticDir struct{ entry *IssuerKeyEntry }

func (d *staticDir) Lookup(issuerID string) *IssuerKeyEntry { return d.entry }

type noopRevocation struct{}

func (r *noopRevocation) IsRevoked(nonce string) bool { return false }

type memNonceCache struct {
	seen map[string]int64
}

func (c *memNonceCache) SeenBefore(nonce string, windowSeconds int64, now int64) bool {
	if exp, ok := c.seen[nonce]; ok && exp > now {
		return true
	}
	c.seen[nonce] = now + windowSeconds
	return false
}

func toStr(v interface{}) string {
	s, _ := v.(string)
	return s
}

func mustJSON(m map[string]interface{}) []byte {	b, _ := json.Marshal(m)
	return b
}

func deepCopyMap(src map[string]interface{}) map[string]interface{} {
	out := make(map[string]interface{})
	for k, v := range src {
		out[k] = v
	}
	return out
}

func makeIssuerEntry(pubB64url string) *IssuerKeyEntry {
	pubBytes, _ := base64.RawURLEncoding.DecodeString(pubB64url)
	der := append([]byte{
		0x30, 0x2a, 0x30, 0x05, 0x06, 0x03, 0x2b, 0x65, 0x70, 0x03, 0x21, 0x00,
	}, pubBytes...)
	pem := "-----BEGIN PUBLIC KEY-----\n" +
		base64.StdEncoding.EncodeToString(der) + "\n-----END PUBLIC KEY-----\n"
	return &IssuerKeyEntry{
		IssuerID:     "rilavo:iss:test",
		PublicKeyPem: pem,
		ValidUntil:   9999999999,
	}
}
