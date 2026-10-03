# Rilavo Product — Managed Infrastructure (E-08)

**Tree:** Product
**Wave:** 3 — Commercial Core
**Status:** Decided
**Depends on:** E-07
**Closes when:** The migration-out path is tested before the first real customer signs — a promise about portability that's never been exercised isn't yet a proven one.

## Self-hosted vs. managed, compared honestly

| | Self-hosted (P-32) | Managed (Rilavo-hosted) |
|---|---|---|
| Effort | Generate keypair, run `/issue`, publish key-directory entry, maintain uptime | Point SDK at Rilavo's endpoint |
| Control | Full — customer holds the signing key | Rilavo holds the signing key on the customer's instruction |
| Ongoing burden | Security patching, key custody, uptime, all owned by the customer | Owned by Rilavo, priced into the SLA tier |
| Best fit | Teams with dedicated security engineering | Teams without it — the majority of E-04's segment 1 |

The pitch for managed is removing operational burden, not removing capability the customer couldn't otherwise have — everything managed infrastructure does, a sufficiently resourced team could do themselves by following P-32 directly.

## Worked example — onboarding

A new customer points their SDK at Rilavo's hosted `/issue` and `/verify` endpoints per the standard API contract (P-19). No infrastructure stood up on their side. Time to first production credential: however long it takes to write the integration itself, with zero additional operational setup.

## Worked example — migrating away

A customer decides to self-host. They export their principal/agent configuration and action-class conventions, stand up their own issuer following the P-32 checklist exactly, and repoint their verifiers at their own new key-directory entry. **Credentials already issued under Rilavo's key remain valid until their natural expiry** — the same mechanic that makes the protocol-level company-dies-tomorrow scenario (P-43) survivable applies identically here, because migrating away from managed infrastructure is, mechanically, the same event as Rilavo Product disappearing, just voluntary and gradual instead of sudden.

## Edge case — partial migration

A customer self-hosts issuance but still wants Rilavo's fraud intelligence feed. **Decided, consistent with E-06:** this is allowed. Managed infrastructure and the intelligence product are priced and sold independently — a customer isn't required to buy the operational convenience to access the data product, and isn't required to buy the data product to get the operational convenience.

## What this document must never allow, stated as a hard constraint on future decisions

Any managed-infrastructure feature that would make self-hosting meaningfully harder than the P-32 checklist describes — for instance, a proprietary extension to issuance that self-hosted issuers can't replicate — would quietly convert "managed for convenience" into "managed because there's no real alternative." That's the lock-in-with-a-friendlier-name failure mode named directly in the Mother Blueprint, and this document exists partly to keep it from happening by accretion.

## What would change this decision

A real customer attempting the migrate-away path and hitting a friction point the P-32 checklist doesn't account for — at which point either this document or P-32 gets corrected, immediately, not deferred.
