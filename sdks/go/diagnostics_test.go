package rilavo

import (
	"strings"
	"testing"
)

func TestAllReasonCodesHaveExplanations(t *testing.T) {
	codes := []string{
		"audience_mismatch", "expired", "not_yet_valid",
		"unknown_issuer", "key_not_valid_at_issuance", "invalid_signature",
		"malformed_credential", "unrecognized_version", "missing_field",
		"replay_detected", "revoked", "revocation_state_unavailable",
		"proof_of_possession_failed", "scope_mismatch", "delegation_not_permitted",
	}
	for _, code := range codes {
		exp, ok := Explanations[code]
		if !ok {
			t.Errorf("missing explanation for %s", code)
			continue
		}
		if len(exp.Summary) < 10 {
			t.Errorf("%s: summary too short", code)
		}
		if len(exp.LikelyCauses) < 2 {
			t.Errorf("%s: expected >=2 likely causes", code)
		}
		if len(exp.Remediation) < 1 {
			t.Errorf("%s: expected >=1 remediation step", code)
		}
		if len(exp.DocPointer) < 5 {
			t.Errorf("%s: doc_pointer too short", code)
		}
	}
}

func TestUnknownCodeReturnsError(t *testing.T) {
	_, ok := Explanations["totally_bogus"]
	if ok {
		t.Error("unknown code should not have an explanation")
	}
}

func TestFormatExplanationContainsHeaders(t *testing.T) {
	exp := Explanations["expired"]
	text := FormatExplanation(exp)
	for _, header := range []string{"Summary:", "Likely causes:", "Remediation:", "Reference:"} {
		if !strings.Contains(text, header) {
			t.Errorf("missing header %q in formatted output", header)
		}
	}
}
