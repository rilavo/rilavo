package rilavo

import (
	"encoding/hex"
	"testing"
)

func TestGoldenVectorsJCS(t *testing.T) {
	v := loadVectors(t)
	for i, vec := range v.JCS {
		got, err := Canonicalize(vec.Input)
		if err != nil {
			t.Fatalf("JCS error for vector %d: %v", i, err)
		}
		if string(got) != vec.Expected {
			t.Errorf("JCS[%d] mismatch: got %s, want %s", i, got, vec.Expected)
		}
	}
}

func TestGoldenVectorsPoP(t *testing.T) {
	v := loadVectors(t)
	got := PopRequestPayload(v.Pop.Method, v.Pop.Path, v.Pop.Act, v.Pop.Nonce)
	want, _ := hex.DecodeString(v.Pop.PayloadHex)
	if string(got) != string(want) {
		t.Errorf("PoP payload mismatch: got %x, want %x", got, want)
	}
}
