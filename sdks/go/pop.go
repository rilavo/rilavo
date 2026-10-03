package rilavo

import (
	"crypto/sha256"
	"encoding/hex"
)

// PopRequestPayload builds the domain-separated PoP payload bytes,
// matching rilavo.pop.request_payload byte-for-byte.
func PopRequestPayload(method, path, act, nonce string) []byte {
	body := `{"act":` + canonString(act) +
		`,"method":` + canonString(method) +
		`,"nonce":` + canonString(nonce) +
		`,"path":` + canonString(path) + `}`
	digest := sha256.Sum256([]byte(body))
	hexDigest := hex.EncodeToString(digest[:])
	payload := `{"rilavo_pop_v0":` + canonString(hexDigest) + `}`
	return []byte(payload)
}
