# Rilavo Protocol — Security Response Model (P-23)

**Tree:** Protocol
**Wave:** 2 — Engineering Core
**Status:** Decided (severity ladder, escalation, and authority); Open (exact disclosure window)
**Depends on:** P-12, P-22
**Closes when:** Legal review sets the disclosure window — everything else here is already actionable.

## Severity classification

| Level | Definition | Example |
|---|---|---|
| **Sev1** | Active exploitation, or a compromise affecting live, unexpired credentials | Issuer signing-key compromise |
| **Sev2** | A confirmed vulnerability with no evidence of exploitation yet | A discovered flaw in a specific SDK version's proof-of-possession check |
| **Sev3** | A theoretical or low-impact weakness, no immediate exposure | A documentation gap that could lead to developer misconfiguration |

## Authority

Emergency action authority sits with whoever operates the compromised component. At v0, that's Rilavo, since there's one issuer. **Status: Deferred** — this authority needs to move to a documented, appealable process the moment a second issuer exists, per the governance transition in P-24. Concentrating emergency authority in one operator is acceptable only because, at v0, that operator's failure modes are already fully disclosed rather than hidden behind a claim of full decentralization.

## Worked example — walking a Sev1 through, start to finish

1. **Detection:** anomalous issuance pattern flagged, or an external report received.
2. **Classification:** confirmed as Sev1 — signing key suspected compromised.
3. **Immediate action:** the compromise-response runbook in P-12 executes — revocation published, new key generated, verifiers automatically enforce the cutoff via the reference verification algorithm's existing `key_not_valid_at_issuance` check. No new mechanism is invented at incident time; this is exactly why that check exists in the reference algorithm in the first place.
4. **Disclosure:** affected verifiers notified. Exact timing **Open**, pending legal review — but the commitment that disclosure happens publicly, not just privately to large customers, is already decided, even though the clock isn't.
5. **Post-incident:** a review of whether rotation cadence (P-12) or custody arrangements should change as a result.

## Escalation ladder, restated at the protocol level

Whoever detects an issue → operator of the affected component → affected verifiers → public disclosure. This exact ladder is reused, not reinvented, at the Product layer (E-13) — the two are one decision described from two documents, not two separate decisions that happen to look similar.

## What deliberately isn't specified here

A fixed disclosure-window number. **Naming a number without legal review would be worse than leaving it open** — a commitment made carelessly here could become a contractual liability later if it turns out to be unrealistic once real incident response is actually exercised.

## What would change this decision

Legal counsel setting the disclosure window; or a second operator existing, which triggers the authority-transfer already flagged above.
