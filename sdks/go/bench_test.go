//go:build bench

package rilavo

import (
    "testing"
    "time"
)

func BenchmarkIssue(b *testing.B) {
    issuer := NewIssuer(nil)
    agentPriv := issuer.PrivateKey
    agentPub := agentPriv.Public()
    b.ResetTimer()
    b.RunParallel(func(pb *testing.PB) {
        i := 0
        for pb.Next() {
            issuer.IssueCredential(IssueRequest{
                Principal:        "acme-corp",
                Agent:            "agent-bench",
                AgentPublicKey:   agentPub,
                ActionClass:      "data.read",
                Audience:         "verifier:bench.example.com",
            })
            i++
        }
        _ = i
    })
}

func BenchmarkVerify(b *testing.B) {
    issuer := NewIssuer(nil)
    directory := NewKeyDirectory()
    directory.Publish(issuer.DirectoryEntry())

    agentPriv := issuer.PrivateKey
    agentPub := agentPriv.Public()

    cred, _ := issuer.IssueCredential(IssueRequest{
        Principal:        "acme-corp",
        Agent:            "agent-bench",
        AgentPublicKey:   agentPub,
        ActionClass:      "data.read",
        Audience:         "verifier:bench.example.com",
    })

    verifier := NewVerifier(directory, &RevocationLog{{}}, NewNonceCache())

    b.ResetTimer()
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            popSig, nonce := SignRequest(agentPriv, "GET", "/data/1", "data.read")
            req := &Request{
                Method:           "GET",
                Path:             "/data/1",
                RequestedAction:  "data.read",
                Signature:        popSig,
                RequestNonce:     nonce,
            }
            verifier.Verify(cred, req)
        }
    })
}
