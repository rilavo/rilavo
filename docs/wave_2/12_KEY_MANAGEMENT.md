# Rilavo Protocol — Key Management (P-12)

**Tree:** Protocol
**Wave:** 2 — Engineering Core
**Status:** Decided (mechanism, and a first-cut incident runbook below); Open (production-grade custody at solo-founder stage)
**Depends on:** P-11
**Closes when:** The custody gap below is closed by real infrastructure, not just documented as a known risk.

## Generation

Ed25519 keypairs generated from an OS-level cryptographically secure random source. Never derived from passwords, seed phrases typed by a person, or any other low-entropy input.

## Storage — the honest gap

The private key must be encrypted at rest with access restricted so no single person can unilaterally use or export it in production. **True HSM- or cloud-KMS-backed custody is the correct target and is not guaranteed at v0 given solo-founder constraints.** This is named here as a real, currently-open risk, not a solved problem dressed up as one. A practical middle ground worth committing to now, short of dedicated hardware: a cloud KMS service (any major provider's managed key-management offering) that never exposes raw key material to the application layer at all, even to the operator — meaningfully better than an encrypted file on disk, meaningfully cheaper and faster to stand up than dedicated HSM hardware, and appropriate to this stage of the company.

## Rotation

Default 90-day cycle. Overlap window equals the maximum credential TTL (4 hours, per P-06) — once the old key's overlap window closes, nothing signed under it can still be unexpired, so there's no need for a longer grace period.

**Worked example:** key `K1` rotates to `K2` at time `T`. The key directory publishes `K2` as active and marks `K1`'s `valid_until` as `T`. Any credential with `iat` before `T` and signed under `K1` remains verifiable until its own `exp`, at most 4 hours later. Any credential claiming to be signed under `K1` with `iat` after `T` is rejected outright (see the compromise mechanic below — rotation and compromise-response share the same enforcement path).

## Compromise response — a first-cut runbook, not left abstract

1. **Detect or suspect compromise.** Trigger could be anomalous issuance volume, an infrastructure breach, or external report.
2. **Immediately publish a revocation of the suspected key** to the key directory, with `valid_until` set to the detection time — not a future time, the actual moment of suspicion, even before full confirmation. Erring toward an earlier cutoff costs some legitimate recently-issued credentials; erring toward a later one risks trusting attacker-issued ones. The former is the safer failure mode.
3. **Generate and publish a new key immediately.**
4. **Verifiers, per the reference verification algorithm, automatically reject anything with `iat` after the published cutoff** — this step requires no manual verifier action, because the check is already built into ordinary verification (core specification, step 4).
5. **Disclose the incident** to affected verifiers per the window defined in P-23 — still open there, not re-decided differently here.
6. **Post-incident:** review whether the 90-day rotation default should tighten, and whether the custody gap above contributed.

## Edge case

**A key compromise discovered retroactively, days after the fact:** every credential issued after the true compromise moment is, in principle, untrustworthy — but the cutoff published in step 2 can only be set to when compromise was *detected*, not when it *actually happened*, since the latter usually isn't known precisely. This is a real, acknowledged limitation: retroactive detection means some window of already-accepted, attacker-issued credentials cannot be un-accepted after the fact, only prevented from continuing.

## What would change this decision

Moving to real KMS-backed custody resolves the storage gap directly. Real incident history — if this runbook is ever exercised for real — is what actually validates or corrects it; a runbook that's never been tested is a draft, not a proven procedure.
