# Rilavo Product — Incident Response (E-13)

**Tree:** Product
**Wave:** 3 — Commercial Core
**Status:** Decided (escalation ladder mirrors P-23 exactly)
**Depends on:** P-23
**Closes when:** Same condition as P-23 — this is one decision viewed from the customer-facing side, not a second, independent decision.

## What a customer actually experiences during an incident — the part P-23 doesn't cover, because P-23 is written for the protocol layer, not the customer relationship

A public status page reflecting real-time incident state. Direct notification to affected customers — timing tied to the same disclosure window P-23 leaves genuinely open pending legal review, restated here rather than re-decided differently. A post-incident report once resolved, describing what happened, what was affected, and what changes as a result.

## Escalation ladder, restated at the commercial layer

Customer detects or is notified → Rilavo → the affected component's operator, if third-party (relevant once federation exists) → public disclosure. Identical in shape to P-23's ladder, because it is the same ladder — duplicating it here with different wording would risk the two documents silently drifting apart over time.

## Worked example — a customer's actual experience of a Sev1

A signing-key compromise is detected (per P-12's runbook). Within the disclosure window, the customer receives direct notification — not just a status-page update they have to notice themselves — describing what happened, what's already been done (key rotated, revocation published), and what, if anything, they need to check on their own side (whether any of their own recently-issued credentials should be treated with extra scrutiny during the transition window). A post-incident report follows once the rotation's overlap window (P-12) has fully closed.

## Edge case — an incident that doesn't affect the customer

Not every Sev1 or Sev2 touches every customer. **Decided:** notification scope is genuinely scoped to affected customers, not broadcast to the entire customer base regardless of relevance — an unaffected customer receiving unnecessary incident notifications erodes the signal value of the notifications that do matter to them.

## What Product adds on top of the protocol-level response that's genuinely commercial, not just protocol response wearing a different label

Staffing and accountability — a real team responsible for executing P-23's mechanism under real time pressure, and a contractual relationship (via the SLA, E-12) that gives the customer recourse if the response itself falls short, not just if the underlying incident occurred.

## What would change this decision

Legal counsel setting the disclosure window (shared with P-23); real incident history testing whether the notification-scoping edge case above actually works as intended once it's exercised for real, not just designed on paper.
