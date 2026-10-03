# Rilavo Protocol — Mission & Scope (P-01)

**Tree:** Protocol
**Wave:** 1 — System Foundation
**Status:** Decided
**Depends on:** None
**Closes when:** Confirmed by the first pilot's real behavior. This document should change rarely — if it starts changing often, that's a signal something upstream is wrong, not that the mission needs constant revision.

## What Rilavo is

**One technically precise sentence:** Rilavo is a stateless, cryptographically signed credential format that lets a receiving system verify, without a network call and without learning anything beyond what the credential discloses, that an agent holds a specific, time-boxed authorization from a specific principal.

**One executive sentence:** it's a way for software to prove it's allowed to do what it's doing, without a company in the middle holding onto who everyone is.

## Why it exists

Receiving systems currently have no portable, standard way to know whether an inbound AI-agent request is authorized. They either block all agent traffic — losing legitimate business — or accept it blind — taking on liability they can't price. This is not a hypothetical gap. Independent 2026 measurements converge on roughly 38–40% of internet-exposed MCP servers running with no declared authentication at all, and a more rigorous dynamic audit — actually testing whether authentication is enforced, not just declared — found the real enforcement gap is far worse: over 90% of dynamically audited servers lack working OAuth authentication, because the MCP specification itself treats authentication as optional. Rilavo exists to close exactly this gap, and no other.

## v0 boundary — what's in

A single claim class: **is this agent authorized, by this principal, for this action, at this receiving system, right now.** Nothing more.

## What's explicitly excluded from v0

Human identity verification, content provenance, device or software attestation, organization verification, and multi-hop delegation are all out of scope for v0. Each has a separate document (P-34 through P-37) defining what it will take to open — none are being built in parallel with v0 "for completeness." Building them now, before v0 has proven anything, would be exactly the kind of premature scope inflation this document exists to prevent.

## Success criteria for v0

Not adoption numbers. The test is narrower and harder: does a real receiving system, integrated against a real pilot partner, correctly accept legitimate authorized agent traffic and correctly reject unauthorized traffic, without requiring manual review in the verification path. If that works, v0 has done its job. Everything past that — scale, revenue, network effects — is downstream of this one fact being true first.

## Why the protocol must exist independently of any operator

Rilavo Product is an operator of this protocol, not a privileged component of it. Every claim in this document, and in every document that depends on it, is written as though for any operator — because the moment the protocol quietly requires trusting one specific company, the entire open-protocol premise becomes a disguised SaaS product wearing open-source language. That boundary is enforced structurally, not just stated: see the System Boundary Map and P-05.
