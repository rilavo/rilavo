# Rilavo Protocol — Audit Receipts (P-10)

**Tree:** Protocol
**Wave:** 2 — Engineering Core
**Status:** Decided (format); Open (retention vs. erasure conflict)
**Depends on:** P-06
**Closes when:** Legal review resolves the retention question below — the format itself doesn't need to change for that to happen.

## Format

```json
{
  "issuer": "rilavo:iss:8f2a...c91",
  "credential_hash": "sha256:71ac...409",
  "outcome": "accept",
  "reject_reason": null,
  "verified_at": 1755000012
}
```

`credential_hash` — never the credential itself. A verifier that stored full credential contents in its receipt log would be quietly rebuilding the exact kind of central data store the whole architecture exists to avoid, just one hop downstream.

## What a receipt proves, and to whom

A receipt lets a verifier later demonstrate what it checked and when, without needing to have retained the credential itself — non-repudiation without data retention. If a dispute arises about whether a specific action was authorized at the time it happened, the verifier can produce the receipt and, if the issuer's log is still available, confirm the hash corresponds to a real credential that existed with a specific outcome.

## Worked example

A disputed transaction six weeks after the fact. The verifier has `credential_hash: sha256:71ac...409`, `outcome: accept`, timestamped. It cannot reconstruct who the agent or principal were from this alone — by design. What it *can* do is confirm, against its own receipt log, that a credential matching that hash was checked and accepted at that time, which is sufficient to answer "did we have a basis for allowing this," even though it's not sufficient to answer "who exactly was behind it" without going back through the issuer, which has its own separate retention policy.

## The retention-vs-erasure conflict, stated plainly

Cryptographic auditability wants receipts kept indefinitely — they're valuable exactly because they can answer questions from the past. Privacy and right-to-erasure regimes want personal data deletable on request. These pull in opposite directions, and at v0 this is resolved narrowly rather than generally: **because a receipt never contains personal data — only a hash, an outcome, and a timestamp — it does not itself constitute erasable personal data under most privacy frameworks**, which is the whole reason the hash-only format was chosen instead of storing the credential. This reasoning has not been tested against real counsel, and it stops holding the moment Horizon 3 introduces claim classes that touch personal data more directly — at which point this document reopens, not just gets referenced.

## Edge case

**A rejected verification** still generates a receipt, with `outcome: "reject"` and a populated `reject_reason`. Rejected attempts are, if anything, more valuable to retain than accepted ones — they're the raw material fraud intelligence (Product, E-09) is built from.

## What would change this decision

Legal counsel confirming or denying the hash-only reasoning above; or a Horizon 3 claim class making it clear that even a hash of certain data types carries enough re-identification risk to require a different retention approach.
