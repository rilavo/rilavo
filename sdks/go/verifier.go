package rilavo

import (
	"crypto/ed25519"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"strings"
	"time"
)

// Reason codes - identical to Python errors.py
const (
	ReasonAudienceMismatch        = "audience_mismatch"
	ReasonExpired                 = "expired"
	ReasonNotYetValid             = "not_yet_valid"
	ReasonUnknownIssuer           = "unknown_issuer"
	ReasonKeyNotValidAtIssuance   = "key_not_valid_at_issuance"
	ReasonInvalidSignature        = "invalid_signature"
	ReasonMalformedCredential     = "malformed_credential"
	ReasonUnrecognizedVersion     = "unrecognized_version"
	ReasonMissingField            = "missing_field"
	ReasonReplayDetected          = "replay_detected"
	ReasonRevoked                 = "revoked"
	ReasonProofOfPossessionFailed = "proof_of_possession_failed"
	ReasonScopeMismatch           = "scope_mismatch"
)

// VerifyResult carries accept/reject outcome and reason code.
type VerifyResult struct {
	Accepted   bool
	ReasonCode string
}

// IssuerKeyEntry mirrors keys.IssuerKeyEntry.
type IssuerKeyEntry struct {
	IssuerID     string
	PublicKeyPem string
	ValidUntil   int64 // Unix seconds; far-future when active
}

// KeyDirectory is a pluggable issuer-key lookup interface (fail-closed).
type KeyDirectory interface {
	Lookup(issuerID string) *IssuerKeyEntry
}

// NonceCache is a pluggable replay-defense interface.
type NonceCache interface {
	SeenBefore(nonce string, windowSeconds int64, now int64) bool
}

// RevocationChecker is a pluggable revocation lookup.
type RevocationChecker interface {
	IsRevoked(nonce string) bool
}

// VerifyOptions bundles all dependencies for the verification pipeline.
type VerifyOptions struct {
	Audience        string
	IssuerDirectory KeyDirectory
	RevocationLog   RevocationChecker
	NonceCache      NonceCache
	NowSeconds      int64
	LeewaySeconds   int64
	Method          string
	Path            string
	RequestedAction string
	PopSignature    string
	PopNonce        string
}

// Verify implements the reference algorithm from Core Spec section 6,
// with gates in EXACTLY the same order as Python verifier.py.
func Verify(credentialJSON []byte, opts VerifyOptions) *VerifyResult {
	fields, err := ParseCredentialFields(credentialJSON)
	if err != nil {
		// OTel: record failure (no timing available at this early stage)
		RecordVerification(VerificationMetrics{
			Accepted:           false,
			ReasonCode:         "malformed_credential",
			DurationMs:         0,
			CredentialIssuer:   "",
		})
		return &VerifyResult{Accepted: false, ReasonCode: "malformed_credential"}
	}
	return verifyFields(fields, opts)
}

func verifyFields(fields map[string]interface{}, opts VerifyOptions) *VerifyResult {
	now := opts.NowSeconds
	if now == 0 {
		now = time.Now().Unix()
	}
	startTime := time.Now()

	// Record issuer for metrics (extract early for use in defer)
	issuer := ""
	if v, ok := fields["iss"].(string); ok {
		issuer = v
	}

	// step 0: shape
	for _, f := range []string{"iss", "sub", "agt", "apk", "act", "aud", "nonce", "sig"} {
		v, ok := fields[f]
		if !ok || v == nil {
			return reject("missing_field", issuer, startTime)
		}
		s, isStr := v.(string)
		if !isStr || s == "" {
			return reject("malformed_credential", issuer, startTime)
		}
	}
	for _, f := range []string{"iat", "exp"} {
		v, ok := fields[f]
		if !ok {
			return reject("missing_field", issuer, startTime)
		}
		switch n := v.(type) {
		case json.Number:
			if _, err := n.Int64(); err != nil {
				return reject("malformed_credential", issuer, startTime)
			}
		case float64:
			if float64(int64(n)) != n {
				return reject("malformed_credential", issuer, startTime)
			}
		default:
			return reject("malformed_credential", issuer, startTime)
		}
	}

	// step 0a: delegation gate (v0: dlg must be absent or 0)
	if dlgVal, hasDlg := fields["dlg"]; hasDlg {
		dlgZero := false
		switch v := dlgVal.(type) {
		case json.Number:
			f, e := v.Float64()
			dlgZero = e == nil && f == 0
		case float64:
			dlgZero = v == 0
		}
		if !dlgZero {
			return reject("delegation_not_permitted", issuer, startTime)
		}
	}

	// step 0b: version gate (P-26)
	verVal, hasVer := fields["ver"]
	ver := int64(1)
	if hasVer {
		switch v := verVal.(type) {
		case json.Number:
			i, e := v.Int64()
			if e != nil || i != 1 {
				return reject("unrecognized_version", issuer, startTime)
			}
		case float64:
			if float64(int64(v)) != v || int64(v) != 1 {
				return reject("unrecognized_version", issuer, startTime)
			}
		default:
			return reject("unrecognized_version", issuer, startTime)
		}
	}
	_ = ver

	// step 1: audience binding
	aud, _ := fields["aud"].(string)
	if aud != opts.Audience {
		return reject("audience_mismatch", issuer, startTime)
	}

	// step 2: time window (with optional clock-skew leeway)
	// Default LeewaySeconds=0 preserves current behavior.
	// Nonzero values widen the acceptance window symmetrically.
	iat := toInt64(fields["iat"])
	exp := toInt64(fields["exp"])
	leeway := opts.LeewaySeconds
	if now-leeway >= exp {
		return reject("expired", issuer, startTime)
	}
	if now+leeway < iat {
		return reject("not_yet_valid", issuer, startTime)
	}

	// step 3: issuer lookup (fail-closed)
	iss, _ := fields["iss"].(string)
	entry := opts.IssuerDirectory.Lookup(iss)
	// OTel: record issuer directory lookup
	RecordIssuerDirectoryLookup(iss, entry != nil)
	if entry == nil {
		return reject("unknown_issuer", iss, startTime)
	}

	// step 4: retroactive compromise cutoff
	if iat > entry.ValidUntil {
		return reject("key_not_valid_at_issuance", iss, startTime)
	}

	// step 5: signature over JCS-canonicalized sans sig
	signingFields := make(map[string]interface{})
	for k, v := range fields {
		if k != "sig" {
			signingFields[k] = v
		}
	}
	canonical, err := Canonicalize(signingFields)
	if err != nil {
		return reject("invalid_signature", iss, startTime)
	}

	pubKeyRaw, err := pemToEd25519Raw(entry.PublicKeyPem)
	if err != nil {
		return reject("invalid_signature", iss, startTime)
	}
	sigStr, _ := fields["sig"].(string)
	sigBytes, err := base64.RawURLEncoding.DecodeString(sigStr)
	if err != nil {
		return reject("invalid_signature", iss, startTime)
	}
	if !ed25519.Verify(pubKeyRaw, canonical, sigBytes) {
		return reject("invalid_signature", iss, startTime)
	}

	// step 6: replay
	nonceVal, _ := fields["nonce"].(string)
	ttl := exp - iat
	if opts.NonceCache.SeenBefore(nonceVal, ttl, now) {
		// OTel: record replay detected
		RecordReplayDetected(iss)
		return reject("replay_detected", iss, startTime)
	}

	// step 7: revocation
	if opts.RevocationLog.IsRevoked(nonceVal) {
		return reject("revoked", iss, startTime)
	}

	// step 8: proof-of-possession
	apkStr, _ := fields["apk"].(string)
	apkBytes, err := base64.RawURLEncoding.DecodeString(apkStr)
	if err != nil || len(apkBytes) != ed25519.PublicKeySize {
		return reject("proof_of_possession_failed", iss, startTime)
	}
	popPayload := PopRequestPayload(opts.Method, opts.Path,
		opts.RequestedAction, opts.PopNonce)
	popSigBytes, err := base64.RawURLEncoding.DecodeString(opts.PopSignature)
	if err != nil || len(popSigBytes) != ed25519.SignatureSize {
		return reject("proof_of_possession_failed", iss, startTime)
	}
	if !ed25519.Verify(apkBytes, popPayload, popSigBytes) {
		return reject("proof_of_possession_failed", iss, startTime)
	}

	// step 9: exact-match scope
	reqAct := opts.RequestedAction
	credAct, _ := fields["act"].(string)
	if reqAct != credAct {
		return reject("scope_mismatch", iss, startTime)
	}

	// OTel: record successful verification
	RecordVerification(VerificationMetrics{
		Accepted:           true,
		ReasonCode:         "",
		DurationMs:         float64(time.Since(startTime).Milliseconds()),
		CredentialIssuer:   iss,
	})
	return &VerifyResult{Accepted: true, ReasonCode: "accept"}
}

func reject(code string, issuer string, startTime time.Time) *VerifyResult {
	// OTel: record verification failure
	RecordVerification(VerificationMetrics{
		Accepted:           false,
		ReasonCode:         code,
		DurationMs:         float64(time.Since(startTime).Milliseconds()),
		CredentialIssuer:   issuer,
	})
	return &VerifyResult{Accepted: false, ReasonCode: code}
}

func toInt64(v interface{}) int64 {
	switch val := v.(type) {
	case json.Number:
		i, _ := val.Int64()
		return i
	case float64:
		return int64(val)
	case int64:
		return val
	case int:
		return int64(val)
	}
	return 0
}

func pemToEd25519Raw(pem string) ([]byte, error) {
	// SPKI DER for Ed25519 = 12-byte prefix + raw 32 bytes.
	b64Body := strings.ReplaceAll(pem, "-----BEGIN PUBLIC KEY-----", "")
	b64Body = strings.ReplaceAll(b64Body, "-----END PUBLIC KEY-----", "")
	b64Body = strings.ReplaceAll(b64Body, "\n", "")
	der, err := base64.StdEncoding.DecodeString(b64Body)
	if err != nil {
		return nil, err
	}
	if len(der) < 12 {
		return nil, fmt.Errorf("PEM too short")
	}
	return der[12:], nil
}
