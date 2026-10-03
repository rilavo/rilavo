package rilavo

import (
	"fmt"
)

// Explanation carries human-readable diagnostic info for a rejection code.
type Explanation struct {
	Summary      string
	LikelyCauses []string
	Remediation   []string
	DocPointer   string
}

// Explanations maps reason codes to diagnostic explanations.
var Explanations = map[string]Explanation{
	"audience_mismatch": {
		Summary: "Credential audience does not match this verifier.",
		LikelyCauses: []string{
			"Credential issued for a different verifier.",
			"Verifier configuration audience mismatch.",
			"Wrong API endpoint for the credential held.",
		},
		Remediation: []string{
			"Request a new credential with the correct audience.",
			"Check your verifier_id configuration.",
		},
		DocPointer: "Core Spec section 6 step 1; P-07",
	},
	"expired": {
		Summary: "The credential has passed its expiration timestamp.",
		LikelyCauses: []string{
			"TTL has elapsed since issuance.",
			"Clock skew between issuer and verifier.",
			"Short-TTL credential was not used promptly.",
		},
		Remediation: []string{
			"Request a fresh credential from the issuer.",
			"Consider requesting longer TTLs if this happens frequently.",
			"Synchronize clocks using NTP.",
		},
		DocPointer: "Core Spec section 6 step 2; P-06 TTL ceiling",
	},
	"not_yet_valid": {
		Summary: "The credential issuance timestamp is in the future.",
		LikelyCauses: []string{
			"Issuer clock is ahead of verifier clock.",
			"Intentionally future-dated credential.",
			"NTP synchronization drift.",
		},
		Remediation: []string{
			"Wait until the credential becomes valid.",
			"Investigate clock synchronization between issuer and verifier.",
		},
		DocPointer: "Core Spec section 6 step 2; P-30",
	},
	"unknown_issuer": {
		Summary: "The credential references an issuer not found in the key directory.",
		LikelyCauses: []string{
			"Issuer has not registered its public key.",
			"Key directory unreachable or incomplete.",
			"Stale issuer identifier.",
		},
		Remediation: []string{
			"Verify the issuer public key is published in the key directory.",
			"Check network connectivity to the directory service.",
			"Confirm the iss field matches a known issuer fingerprint.",
		},
		DocPointer: "Core Spec section 6 step 3; P-17",
	},
	"key_not_valid_at_issuance": {
		Summary: "The credential iat falls after the signing key valid_until cutoff.",
		LikelyCauses: []string{
			"Issuer rotated its signing key but the agent cached the old one.",
			"Signing key was compromised and retroactively invalidated.",
			"Stale credential signed before rotation re-presented after cutoff.",
		},
		Remediation: []string{
			"Obtain a new credential signed under the current key.",
			"Clear cached old keys from local state.",
			"If you are the issuer, verify rotation completed successfully.",
		},
		DocPointer: "Core Spec section 6 step 4; P-12",
	},
	"invalid_signature": {
		Summary: "Ed25519 signature over canonicalized fields does not verify against the issuer public key.",
		LikelyCauses: []string{
			"One or more credential fields were modified after signing.",
			"The sig field was corrupted during transmission.",
			"A different key was used to sign than published in the directory.",
		},
		Remediation: []string{
			"Request a new credential without modifying any fields.",
			"Verify no proxy or middleware is altering the payload.",
			"Check for encoding issues (base64url padding).",
		},
		DocPointer: "Core Spec section 6 step 5; P-11 Ed25519",
	},
	"malformed_credential": {
		Summary: "The credential JSON could not be parsed or contains incorrect field types.",
		LikelyCauses: []string{
			"JSON is syntactically invalid (truncated, encoding error).",
			"Required field has wrong type (string vs integer).",
			"Base64url encoding of header is malformed.",
		},
		Remediation: []string{
			"Regenerate the credential from the issuer.",
			"Validate JSON structure against the v0 field list.",
			"Ensure no intermediate proxy stripped or modified the header.",
		},
		DocPointer: "Core Spec section 6 step 0; P-06 field contract",
	},
	"unrecognized_version": {
		Summary: "The credential carries a ver field not recognized by this verifier.",
		LikelyCauses: []string{
			"ver=2 or higher requires a newer verifier.",
			"Non-integer value placed in ver field.",
			"Credential created for future protocol version.",
		},
		Remediation: []string{
			"Remove ver field or set to 1 per P-26.",
			"Upgrade verifier if newer version is legitimate.",
		},
		DocPointer: "P-26 versioning; Core Spec step 0b",
	},
	"missing_field": {
		Summary: "One or more required fields are absent from the credential object.",
		LikelyCauses: []string{
			"Issuer omitted a mandatory field during creation.",
			"Serialization bug dropped a field during encoding.",
			"Credential was truncated in transit.",
		},
		Remediation: []string{
			"Request new credential ensuring all required fields are present.",
			"Check issuer implementation against v0 field list.",
			"Compare with known-good credential from test suite.",
		},
		DocPointer: "Core Spec section 6 step 0; P-06 field contract",
	},
	"replay_detected": {
		Summary: "The credential nonce has already been seen within the TTL window.",
		LikelyCauses: []string{
			"Same credential presented more than once to this verifier.",
			"Attacker captured and replayed a previously used credential.",
			"Load balancer routed same request to shared nonce cache.",
		},
		Remediation: []string{
			"Request fresh credential with new nonce from issuer.",
			"Ensure agent generates unique nonces per session.",
			"Use batch issuance with distinct nonces if multi-presentation needed.",
		},
		DocPointer: "Core Spec section 6 step 6; P-09",
	},
	"revoked": {
		Summary: "The credential has been explicitly revoked before its natural expiry.",
		LikelyCauses: []string{
			"Principal revoked via issuer revocation endpoint.",
			"Issuer detected compromise and revoked outstanding credentials.",
			"Automated fraud-detection flagged the credential.",
		},
		Remediation: []string{
			"Request new credential after resolving revocation cause.",
			"Contact issuer if revocation was in error.",
			"Review revocation reason in the issuer audit log.",
		},
		DocPointer: "Core Spec section 6 step 7; P-09",
	},
	"revocation_state_unavailable": {
		Summary: "Revocation status cannot be determined because source is unreachable. System fails closed.",
		LikelyCauses: []string{
			"Revocation service temporarily down.",
			"Network partition between verifier and revocation source.",
			"Cache expired and cannot refresh.",
		},
		Remediation: []string{
			"Retry after confirming connectivity.",
			"Check health of revocation service.",
			"Per fail-closed policy, request denied until status confirmed.",
		},
		DocPointer: "Core Spec section 6 step 7 fail-closed; P-09",
	},
	"proof_of_possession_failed": {
		Summary: "Ed25519 proof-of-possession signature does not verify against the agent public key.",
		LikelyCauses: []string{
			"Agent private key does not match apk in credential.",
			"PoP payload built with different method/path/action/nonce than signed.",
			"PoP signature corrupted during transport or encoding.",
		},
		Remediation: []string{
			"Ensure agent signs PopRequestPayload with exact values sent in request.",
			"Verify agent private key matches apk in credential.",
			"Check encoding mismatches (base64url vs standard base64).",
		},
		DocPointer: "Core Spec section 6 step 8; pop.py domain separation rilavo_pop_v0",
	},
	"scope_mismatch": {
		Summary: "Requested action class does not exactly match the action class in the credential. Exact-match only at v0.",
		LikelyCauses: []string{
			"Agent requested different operation than authorized.",
			"x-rilavo-action header does not match act field in credential.",
			"Wildcard or hierarchical scope matching attempted at v0.",
		},
		Remediation: []string{
			"Request credential with correct action_class for desired operation.",
			"Ensure x-rilavo-action header exactly matches credential act field.",
			"For multiple operations obtain separate credentials per action class.",
		},
		DocPointer: "Core Spec section 6 step 9; P-07 exact-match scope",
	},
	"delegation_not_permitted": {
		Summary: "Credential carries dlg (delegation depth) non-zero value rejected at v0.",
		LikelyCauses: []string{
			"Delegated sub-credential presented at v0 where delegation is Wave-6.",
			"dlg field accidentally included during credential creation.",
		},
		Remediation: []string{
			"Request top-level non-delegated credential from root issuer.",
			"Remove dlg field if added in error.",
			"Delegation becomes available when P-34 trigger condition met.",
		},
		DocPointer: "Core Spec step 0b delegation check; P-34 Wave-6 trigger",
	},
}

// ExplainRejection returns the Explanation for a given reason code.
// Returns an error on unknown codes (fail-closed).
func ExplainRejection(code string) (Explanation, error) {
	exp, ok := Explanations[code]
	if !ok {
		return Explanation{}, &UnknownCodeError{Code: code}
	}
	return exp, nil
}

// UnknownCodeError indicates a reason code not in the diagnostics registry.
type UnknownCodeError struct{ Code string }

func (e *UnknownCodeError) Error() string { return "unknown reason code: " + e.Code }

// FormatExplanation renders an Explanation into human-readable text.
func FormatExplanation(e Explanation) string {
	result := "Summary: " + e.Summary + "\n\n"
	result += "Likely causes:\n"
	for i, cause := range e.LikelyCauses {
		result += fmt.Sprintf("  %d. %s\n", i+1, cause)
	}
	result += "\nRemediation:\n"
	for i, step := range e.Remediation {
		result += fmt.Sprintf("  %d. %s\n", i+1, step)
	}
	result += "\nReference: " + e.DocPointer
	return result
}
