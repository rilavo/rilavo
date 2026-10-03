# Rilavo Product — Unit Economics (E-16)

**Tree:** Product
**Wave:** 3 — Commercial Core (Economics block)
**Status:** Open — genuinely, not provisionally. No real cost data exists yet.
**Depends on:** E-14, E-15
**Closes when:** Real cost data exists past the first few thousand customers — not before, and not by more analysis in the meantime.

## What "deepening" this document honestly means

Every other Wave 3 document got more concrete by adding worked numbers. This one gets more concrete by building the real cost framework — what scales with what, and what data would be needed to fill it in — without inventing dollar figures the project doesn't have. Fabricating a specific margin number here would be a worse outcome than leaving this document open, because a fake number gets treated as real by anyone who reads it later.

## Cost components, by how they scale

| Cost | Scaling behavior | Scales with | What data fills this in |
|---|---|---|---|
| Issuance & verification compute | Variable | Call volume | Real infrastructure billing once production traffic exists |
| Revocation-log storage | Variable, cumulative | Revocation events (volume × revocation rate) over time | Same, plus real observed revocation rate |
| Key management / KMS | Mostly fixed | Number of issuers, not call volume | Cloud KMS provider pricing (already knowable in advance, unlike the others) |
| Support & incident response staffing | Step-function, not smooth | Customer count and tier mix | Real support-ticket volume per customer once a base exists |
| Fraud-intelligence model development | Largely fixed, front-loaded | Not usage — mostly R&D-shaped cost | Internal engineering time, estimable in advance |
| Payment processing overhead | Depends on E-15's resolution | Whether the $1 mechanic is billed discretely or batched/absorbed | Resolved by E-15, not independently open here |

## The margin formula, structurally, with the unknown left explicit rather than guessed

$$\text{Gross margin per verification} = \frac{\text{Price} - \text{Variable cost per verification}}{\text{Price}}$$

At the illustrative $0.001 price point from E-14: if variable cost per verification is a small fraction of a cent, margin is high, consistent with the "near-zero marginal cost" language used elsewhere. **This document does not assert that variable cost is in fact that small** — it states the formula so that whatever real number eventually fills it in has somewhere correct to go.

## Break-even framework, same discipline

$$\text{Break-even volume} = \frac{\text{Fixed costs}}{\text{Price} - \text{Variable cost per unit}}$$

Fixed costs — KMS, a baseline of support staffing, the up-front fraud-model work — are the numerator. Until real figures exist for each, this formula is structurally correct and numerically empty, which is the honest state of this document.

## Worked illustration of the *shape* of the risk, not a prediction

If support staffing turns out to scale less like a smooth variable cost and more like a step function — flat until a threshold, then a discrete jump when another support hire becomes necessary — then unit economics can look healthy right up until a customer-count threshold and then compress sharply right after it, before smoothing out again at the next plateau. This is a real, common pattern in support-heavy B2B infrastructure businesses, named here as a shape to watch for, not a claim about where Rilavo's specific threshold sits.

## What would change this document from Open to Decided

Real infrastructure and support cost data from operating past the first few thousand customers (Dependency Register, Wave 3 closure condition). Nothing else — not more modeling, not more reasoning about the formula above, only real numbers.
