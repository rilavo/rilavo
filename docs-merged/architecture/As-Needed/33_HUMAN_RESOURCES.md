# Rilavo Product — Human Resources (E-33)

**Tree:** Product
**Wave:** Continuous / As-Needed
**Status:** Deferred
**Depends on:** None
**Closes when:** The first hire beyond the founder — there is no HR function to describe before there's a second person to apply it to.

## Why this document doesn't invent process the company doesn't have

Same discipline as E-32, applied here: a solo-founder company has no hiring process, compensation structure, or personnel policy worth documenting in detail, because none of it has been tested against a real second employee yet.

## What's flagged for later, not decided now

Who reviews access to production signing infrastructure once there's more than one person who could plausibly hold it (E-30's least-privilege principle, which will need real enforcement mechanics the moment a second person exists). Compensation and equity structure. Basic employment policy appropriate to wherever the company is actually incorporated and hiring.

## Why E-30's security principle is the one thing this document flags as urgent the moment it applies

Unlike most of this document's contents, the access-control discipline in E-30 isn't optional to defer — "no single employee able to unilaterally rotate a production issuer key" only means something once there's more than one employee, and the mechanics of enforcing it need to exist before the second hire touches production infrastructure, not sometime after.

## What would change this decision

An actual first hire — at which point this document's job shifts from "nothing to describe" to "describe what was actually decided when it mattered," informed by a real case rather than speculative policy.
