package rilavo

import (
	"encoding/json"
	"os"
	"testing"
)

type TestVectors struct {
	JCS []struct {
		Input    map[string]interface{} `json:"input"`
		Expected string                 `json:"expected"`
	} `json:"jcs"`
	Pop struct {
		Method      string `json:"method"`
		Path        string `json:"path"`
		Act         string `json:"act"`
		Nonce       string `json:"nonce"`
		PayloadHex  string `json:"payload_hex"`
	} `json:"pop"`
	PopSig struct {
		SigB64url string `json:"sig_b64url"`
		Nonce     string `json:"nonce"`
	} `json:"pop_sig"`
	IssuerPubB64url     string                 `json:"issuer_pub_b64url"`
	AgentPubB64url      string                 `json:"agent_pub_b64url"`
	CredentialFields    map[string]interface{} `json:"credential_fields"`
}

func loadVectors(t *testing.T) TestVectors {
	t.Helper()
	data, err := os.ReadFile("testdata/golden.json")
	if err != nil {
		// fallback for dev environments that generate vectors at /tmp
		data, err = os.ReadFile("/tmp/go_vectors.json")
	}
	if err != nil {
		t.Skipf("golden vectors not found: %v", err)
	}
	var v TestVectors
	if err := json.Unmarshal(data, &v); err != nil {
		t.Fatalf("failed to parse vectors: %v", err)
	}
	return v
}
