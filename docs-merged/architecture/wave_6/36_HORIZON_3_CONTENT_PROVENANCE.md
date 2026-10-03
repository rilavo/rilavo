# Rilavo Protocol — Horizon 3: Content Provenance (P-36)

**Tree:** Protocol
**Wave:** 6 — Future Horizons
**Status:** Decided (architectural principle only); externally dated, not internally scheduled
**Depends on:** P-13
**Closes when:** Either shipped voluntarily, or effectively forced by the external deadline described below.

## The one architectural principle that is decided

Provenance signed at creation time, designed to survive re-encoding, rather than relying on after-the-fact forensic detection of AI-generated content — detection-after-the-fact is an arms race with generative models that keeps getting harder to win; attestation-at-creation is a different kind of claim entirely, one this document commits to rather than the alternative.

## The real, dated, external pressure — not manufactured urgency

The EU AI Act's Article 50 already requires generative-AI providers to mark synthetic audio, video, text, and image output as machine-detectable, backed by fines reaching €15 million or 3% of global turnover. Its Code of Practice pushes toward a unified, interoperable watermark-detection mechanism, rather than forcing every platform to query every AI provider's own proprietary detector separately — and that interoperability requirement is precisely the gap a neutral, cross-provider verification protocol is built to fill. This is worth restating plainly: this horizon's timeline is not being set by Rilavo's own roadmap ambition, it's being set by a regulator, whether or not Rilavo chooses to engage with it on that schedule.

## Why this stays at the principle level despite having a real deadline attached

A deadline doesn't make the technical design ready — it makes the case for *when* to start it. The actual mechanism (how provenance is cryptographically bound to content, what survives re-encoding and what doesn't, how a verifier checks a provenance claim years after creation) depends on partnerships with content-creation tooling that don't currently exist. This is a business-development precondition as much as a technical one, and designing the wire format before those partnerships exist risks designing around assumptions about tooling integration points that turn out wrong the moment a real partner is in the room.

## What is genuinely undecided here

Which content-creation tools integrate provenance signing at the source — a partnership question, not a cryptography question. The specific watermarking or attestation technique for each media type (audio, video, text, image each have different technical constraints for surviving re-encoding). Whether Rilavo pursues this horizon on its own initiative or waits for the regulatory deadline to make the case unavoidable.

## What would need to happen before this earns P-08's level of technical depth

At least one real content-creation tooling partnership committed to integrating provenance signing at creation time — without that, a detailed technical spec would be designed against a hypothetical integration point rather than a real one.

## What would change this decision

A committed creation-time partner, or the Code of Practice's interoperability deadline becoming close enough that voluntary timing is no longer really a choice — either one moves this from principle to real specification work.
