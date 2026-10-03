# Rilavo Protocol — Horizon 4: Device & Software Attestation (P-37)

**Tree:** Protocol
**Wave:** 6 — Future Horizons
**Status:** Deferred
**Depends on:** None yet
**Closes when:** Only if a specific partner requires it — the least determined trigger of any document in this project, and treated that way rather than dressed up as more developed than it is.

## Why this stays short

Every other Wave 6 document had something real to say now — a settled design (P-08), a decided architectural principle with real stakes (P-35), a real external deadline (P-36). This one has neither a settled direction nor a forcing event. Writing more here than the project actually knows would be padding, not depth.

## What's decided, minimally

Consume existing hardware attestation standards — TPM, Secure Enclave — rather than build competing infrastructure. This horizon is about integrating established signals, not inventing new ones.

## The one risk worth naming even at this level of undevelopment

Leaning on a small number of hardware vendors' attestation roots would quietly reintroduce the exact centralization the rest of this protocol is architected to avoid. Worth flagging now, before any real design work begins, so it's not discovered as a surprise later.

## What would change this decision

A specific partner — a device manufacturer, an product customer with a hardware-attestation requirement — actually asking for this. Nothing about internal roadmap ambition changes this document's status; only external, concrete demand does.
