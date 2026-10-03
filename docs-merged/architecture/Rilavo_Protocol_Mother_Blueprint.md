# Rilavo Protocol — Mother Blueprint

**Document type:** Mother blueprint for `/RILAVO_PROTOCOL/` (45 documents)
**Status:** Seeds documents 00–45. Every entry below traces to the Mother Audit Question Bank (Parts I–II, and the protocol-relevant slices of Parts IV–IX) and to decisions already recorded in `Rilavo_Project_Audit_and_Specification.md`. Nothing here invents architecture the source material doesn't support — where the evidence isn't there yet, the entry says **Open**, not a confident guess.

**Governing rule for this entire tree, stated once so it doesn't need repeating 45 times:** the protocol is written as if for *any* operator. "Rilavo Product" is the first, reference operator — not a privileged one. Nothing in this document should read as if the protocol needs the company to function; that boundary is the whole point of the two-tree structure (Question Bank §1.3, §53, Appendix D).

**Confidence/status vocabulary used throughout** (from the Question Bank's own template, applied at blueprint grain rather than per-micro-question): Confidence — *Confirmed / Strong evidence / Working assumption / Unknown*. Status — *Decision / Open / Rejected / Deferred*. Priority — *P0 Existential → P4 Optimization* (Appendix B).

---

## Part I recap — What the protocol is (§1.1, §1.3)

**One technically precise sentence:** Rilavo is a stateless, cryptographically signed credential format that lets a receiving system verify, without a network call and without learning anything beyond what the credential discloses, that an agent holds a specific, time-boxed authorization from a specific principal.

**One executive sentence:** it's a way for software to prove it's allowed to do what it's doing, without a company in the middle holding onto who everyone is.

**Smallest atomic function:** issue a claim, sign it, let anyone with the issuer's public key check it. Everything else in this document is elaboration on that one function.

**The claim/sign/verify/receive chain:** a principal authorizes → an issuer signs a credential expressing that authorization → an agent presents it → a verifier checks the signature, expiry, and revocation status → a decision is made and receipted. **Decision, Confirmed:** this chain is identical in shape across every future claim class (agent, human, content, device, organization) — what differs between them is *what's being claimed*, not *how claims move*. That's the one unification worth committing to now; everything else about those future classes stays open until each is separately audited (§4 below).

---

## The 45 documents

### 00 — Protocol Master Specification
**Priority P0. Decision.** This blueprint *is* the working draft of 00. It will graduate to a standalone master spec once documents 06 (credential), 07 (authorization), 09 (revocation), and 22 (threat model) are frozen — those four are the load-bearing ones; everything else can be drafted in parallel. **Confidence: Strong evidence** this sequencing is right, based on which fields are hardest to change post-launch (§7's mechanics questions all resolve to these four).

### 01 — Protocol Mission and Scope
**Priority P0. Decision.** Why it exists: receiving systems currently have no portable, standard way to know whether an inbound AI-agent request is authorized — they either block all agent traffic (losing legitimate business) or accept it blind (taking on liability). v0 solves exactly this and nothing else. **Evidence, Strong:** independent 2026 measurements converge on roughly 38–40% of internet-exposed MCP servers running with no declared authentication at all — Wiz Research found 38% across 500+ servers, Bloomberry 38.7% across ~1,400, and Censys identified 12,520 exposed MCP services in April 2026, growing past 21,000 by May, with the great majority unauthenticated.<cite index="19-1">Roughly 38% to 40% of MCP servers run without authentication, based on three independent 2026 scans — Wiz Research (38%, 500+ servers), Bloomberry (38.7%, ~1,400 servers), and Censys (~40%, 12,520+ exposed services)</cite> A separate, more rigorous *dynamic* audit — actually testing whether auth is enforced, not just declared — found the real enforcement gap is far worse: <cite index="15-1">91.8% of dynamically audited servers lack OAuth authentication</cite>, and <cite index="15-1">the MCP specification treats OAuth 2.0 as optional, so many server implementations omit all authentication</cite>. This corrects the higher, unsourced "100%" figure that appeared in earlier project research — the real number is bad enough without rounding up, and the declared-vs-enforced gap is itself an argument for Rilavo's approach: a self-contained signed credential either verifies or it doesn't, which removes the "auth declared but not enforced" failure mode entirely. **What existing standards leave unsolved:** OAuth 2.1 solves human-session authorization well; it was never built for autonomous, long-running, non-interactive callers (see 18 below). Rilavo is a compatibility layer for that specific gap, not a replacement for identity or session management generally.

### 02 — Terminology and Semantics
**Priority P1. Decision — canonical glossary (v0 scope):**

| Term | Definition |
|---|---|
| Principal | The human or organization whose authority is being delegated |
| Agent | Software acting on a principal's behalf, holder of a credential |
| Issuer | The party that signs a credential attesting a principal's grant |
| Verifier | Any receiving system checking a credential before acting on it |
| Operator | An entity running issuer and/or verifier infrastructure — Rilavo Product is one instance of this, not a distinct role |
| Credential / proof | The signed object itself |
| Authorization | The specific scope (action-class, time, audience) a credential grants |
| Delegation / attenuation | A credential deriving from another, narrower or equal in scope, never broader (Horizon 2, §11, §34) |
| Revocation | An issuer or principal invalidating a credential before its natural expiry |
| Expiry | A credential's built-in, unextendable time limit |
| Nonce | A single-use value preventing replay |
| Audit receipt | A verifier's local record that a specific verification occurred |
| Root proof / sub-agent proof | A credential issued directly to a principal's primary agent, versus one derived from it |

**Open:** terms for Horizon 3+ claim classes (human, content, device, organization) are deliberately not defined yet — defining them before those horizons are reached would be exactly the "manufactured certainty" Appendix D warns against.

### 03 — Problem and Wedge
**Priority P0. Decision.** The wedge is agent authorization specifically because it's a greenfield problem with no entrenched incumbent to displace — unlike human KYC (Persona, Onfido, Jumio) or content provenance (C2PA), nobody yet owns "prove this agent is authorized." Alternative available today: OAuth 2.1 client-credentials flows, retrofitted. **Why a developer doesn't just keep using that:** OAuth's session model assumes a human behind the flow; service-account and client-credentials patches work but require stateful token orchestration (refresh rotation, per-tenant isolation) that's disproportionate for a single, short, scoped machine-to-machine call. **Excluded from v0, explicitly:** human verification, content provenance, device attestation, org verification, delegation chains beyond one hop. **Re-entry trigger for each:** stated per-horizon in documents 34–37.

### 04 — Protocol Principles
**Priority P1. Decision.** Five governing rules, carried forward from the audit's own usage instructions and restated as protocol-design principles: (1) no architecture decision gets marketing language instead of evidence; (2) no security claim rests on "the cryptography prevents it" without a threat-model entry; (3) no network-effect claim without a named mechanism; (4) no survivability claim rests on "the protocol is open" alone — openness is necessary, not sufficient; (5) the protocol never requires trusting Rilavo Product specifically, only trusting *an* issuer, which the principal or their tooling can choose.

### 05 — Actor and Trust Model
**Priority P0. Decision.** Roles as defined in 02. **Who holds the private key:** the issuer, at v0 (principal-held signing is a stated future direction, not v0 scope — flagged **Open**, since client-side key custody has real UX and recovery costs not yet designed). **Who can revoke:** issuer or principal, both — a principal must be able to kill their own agent's authority without waiting on the issuer. **Liability, per the audit's existing allocation:** issuer liable for wrongly issued credentials, verifier liable for accepting an invalid/expired one, operator liable only for protocol-level failure (e.g., signing-key compromise). **Status: Deferred to legal counsel** — this allocation is a sound working position, not yet enforceable contract language.

### 06 — Credential Specification
**Priority P0. Decision — mandatory fields:** issuer ID, principal ID, agent ID, action-class, audience (the specific verifier the credential is bound to), issued-at, expires-at, nonce, signature. **Optional:** delegation depth (0 at v0), context string. **Never encoded:** raw biometric data, precise device fingerprints, or anything that would let two verifiers correlate the same principal without the principal's action — this is a hard line from the privacy architecture (13), not a style preference. **What must be impossible to alter without invalidating the credential:** every field above the signature line, by construction. **Status: Decision, pending freeze after the first pilot integration's real traffic** — the exact field list is the single highest-cost-to-change artifact in the whole tree; it should not be treated as final until it has survived one production partner.

### 07 — Authorization Model
**Priority P0. Decision.** Authorization at v0 is action-class-level and audience-bound (not argument-level, not monetary, not geography-limited — those are Horizon 2 refinements). **The confused-deputy problem:** solved by mandatory audience binding — a credential issued for Verifier A is cryptographically invalid if presented to Verifier B, full stop, mirroring the discipline OAuth 2.1 adds via Resource Indicators (RFC 8707) for exactly this reason. **Proof-of-possession:** the agent must sign the specific request with a key bound to the credential, so a stolen credential alone (without the matching private key) isn't sufficient to impersonate the agent. **Confidence: Strong evidence** — this pattern is a direct, deliberate borrow from mature OAuth 2.1 practice, not a novel invention (see 18).

### 08 — Delegation and Attenuation
**Priority P1 (P0 once Horizon 2 opens). Decision.** Delegation is out of v0 scope but its target design is not invented from scratch — it adopts the shape already proven by Biscuit tokens and the IETF Agent Identity Protocol (AIP) draft: attenuation-only (a child credential can only narrow, never widen, scope across tools/budget/domain/time), a bounded maximum delegation depth declared in the root credential, mandatory non-empty context on every delegation hop for auditability, and ephemeral per-sub-agent keys with short TTLs so a compromised sub-agent's blast radius is small.<cite index="0-0">Each subsequent delegation block must be a strict subset of its parent's capabilities across four dimensions: Tools, Budget, Domains, and Time</cite>, and <cite index="0-0">the root token declares a max_depth value; delegation beyond this architectural depth is automatically rejected</cite>. **Confidence: Strong evidence**, adapted prior art, not yet Rilavo-tested. **Open:** exact chain-verification cost at depth, and whether verifiers should check the whole chain or only the final derived capability (both are used elsewhere; the tradeoff is verification cost versus auditability, and it isn't resolved).

### 09 — Revocation Specification
**Priority P0. Decision.** Revocation is via a public, append-only, hash-chained log — not a live database call, so it doesn't create a single point of failure a verifier depends on for every check. **Who can revoke:** issuer (any credential it issued) and principal (their own agent's authority) — both, independently. **Fail-open vs. fail-closed when the revocation log is unreachable:** fail-closed by default for v0, since the stakes of a wrongly-accepted authorization currently outweigh the stakes of a wrongly-rejected one — **Status: Open**, this default needs to be revisited per-verticals once verifiers with different risk tolerances exist. Short expiry (hours) is the primary defense, not revocation speed — a credential that expires in two hours doesn't need sub-second revocation propagation to be safe.

### 10 — Audit Receipts
**Priority P1. Decision.** A verifier logs, at minimum: which credential ID, which issuer, the outcome, and a timestamp — never the full credential contents, and never anything that would let the receipt log itself become a secondary identity database. **Non-repudiation:** the receipt is bound to the request via a hash of the verified credential, so a verifier can later prove what it checked without needing to have retained the credential itself. **Retention vs. deletion conflict (§13):** flagged **Open** — cryptographic auditability and legal right-to-erasure pull in opposite directions, and this needs a real answer (likely: retain the hash and outcome, never the underlying claim contents) before any Horizon 3 claim class involving personal data ships.

### 11 — Cryptographic Specification
**Priority P0. Decision.** Ed25519 for all v0 signing, no exceptions, no custom primitives. This isn't a default so much as a structural fit: a 256-bit Ed25519 key delivers roughly the security of a 3072-bit RSA key at a fraction of the size, with deterministic (not PRNG-dependent) nonce generation that removes an entire class of key-leak vulnerability RSA and ECDSA implementations have historically suffered from. Concretely, a public key is ~44 characters and a signature 64 bytes versus RSA's ~392–700 character keys and 256–512 byte signatures — the difference that keeps a Rilavo proof small enough to sit in an HTTP header without payload bloat, and fast enough (microsecond-scale verification) that checking a credential never becomes the bottleneck in a live transaction path. **Confidence: Confirmed** — this is settled, well-audited cryptography, not a novel choice requiring its own review.

### 12 — Key Management
**Priority P0. Decision.** Issuer keys generated and stored server-side at v0 (client-side principal custody is Horizon-2-adjacent, not v0). Rotation: scheduled, with a defined overlap window so in-flight credentials signed under the old key remain verifiable until their natural expiry. Compromise response: immediate key revocation via the same log as credential revocation, immediate rotation, and — because v0 has one issuer — this is the single highest-severity operational event the protocol can experience. **Status: Decision on mechanism, Open on incident playbook** — the mechanism is specified; the actual response runbook belongs in 23.

### 13 — Privacy Architecture
**Priority P0. Decision.** Minimum-disclosure by design: a credential reveals only the action-class and audience, never the principal's broader identity, unless the verifier's own business requires more (which is the verifier's choice to request, not the protocol's default). No two verifiers can correlate the same principal from credential contents alone, because credentials are audience-bound and don't repeat a static identifier across relationships. **What ZK unlocks later and why it's not in v0:** proving a claim (e.g., "this principal is over a threshold") without revealing the underlying attribute — genuinely valuable for Horizon 3, genuinely unnecessary for v0, where the verifier is *supposed* to know which principal it's dealing with (it's the agent's authorization being verified, not the principal's hidden attributes).

### 14 — Data Model
**Priority P1. Decision.** Ephemeral by default: the credential itself is never stored by the protocol after it expires; only the append-only revocation log and (locally, per-verifier) audit receipts persist. Nothing is globally replicated except issuer public keys and the revocation log — both of which are, by design, safe to replicate widely since neither contains personal data.

### 15 — Network Architecture
**Priority P0. Decision.** v0 topology: one issuer, N verifiers, no consensus mechanism, because there's nothing yet to reach consensus about — a single issuer's key is simply trusted directly, the way any TLS certificate authority is trusted directly. Consensus becomes a real question only once multiple mutually-distrusting issuers need to agree on shared state (revocation, primarily) without one operator controlling the log — that's a Horizon-2-or-later question, not answered here, **Status: Deferred**.

### 16 — Node and Operator Specification
**Priority P1. Decision.** A verifier "operates" nothing beyond a local library call against a cached public key — no node to run. An issuer operates a signing service and contributes to the shared revocation log. At v0, exactly one entity does the latter. **Open:** the exact technical requirements (uptime, key-security standard, audit-log format) an independent operator must meet to be admitted — this is gated by 24 (Governance) and doesn't have a concrete bar yet because there's no admission process to apply it to.

### 17 — Discovery and Key Directory
**Priority P1. Decision.** v0 uses a single, published, versioned key directory (not DNS-based, not blockchain-based) — simplest thing that works when there's one issuer. **Trigger to revisit:** the moment a second issuer exists, discovery needs to become federated or it silently recreates centralization at the directory layer even after issuance decentralizes — this is exactly the kind of second-order centralization risk §25 warns about, and it's flagged here explicitly so it isn't missed later.

### 18 — Interoperability Specification
**Priority P0. Decision.** Rilavo is deliberately positioned as complementary to OAuth 2.1, not a competitor to it — it reuses OAuth's hard-won security lessons (PKCE-equivalent binding, RFC 8707-style audience restriction) rather than reinventing them, while solving the specific stateless, non-interactive, machine-to-machine case OAuth wasn't built for. **Adjacent standards to track, not adopt wholesale at v0:** Client ID Metadata Documents (CIMD, domain-as-trust-anchor client identity), Identity Assertion Authorization Grant (ID-JAG), auth.md, and AAuth — all live 2026 attempts at the same gap from different angles. **Decision:** none of these are dependencies for v0; Rilavo should publish a compatibility note against each as they stabilize, rather than betting the credential format on any one becoming dominant before the field has consolidated. **MCP specifically:** a natural first integration surface, precisely because the current MCP spec treats authentication as optional and most implementations skip it — Rilavo slots in as the authorization layer MCP itself declines to mandate.

### 19 — API Specification
**Priority P1. Decision.** Two calls, minimum viable: `issue(principal, agent, action_class, audience, ttl)` → credential, and `verify(credential)` → accept/reject + reason. Everything else (dashboards, analytics) is product product, not protocol API surface — a deliberate, narrow API keeps the open surface small and stable, which is itself a defensibility property (a small, frozen API is hard to accidentally fragment).

### 20 — SDK Specification
**Priority P0. Decision.** Reference SDK ships in the language of the first pilot partner's stack — not decided in the abstract, decided by whoever the first real integration is with. A minimal integration should be answerable in single-digit lines of code for the `verify` call. **Testability without Rilavo servers:** a local test issuer and a fixed test keypair must ship with the SDK on day one, so integration testing never depends on live infrastructure. **Confidence: Working assumption** on line-count target — not yet tested against a real developer.

### 21 — Conformance Tests
**Priority P2. Decision.** A conformance suite is a Horizon-2 deliverable, not a v0 one — conformance testing exists to let independent implementations prove compatibility, and at v0 there is exactly one implementation. **Trigger:** the day a second party proposes an independent verifier or issuer implementation, this document becomes P0 overnight.

### 22 — Security Threat Model
**Priority P0. Decision.** Carries forward the attack-surface table from the existing audit specification in full (fake-identity creation deferred by scope; stolen/copied credentials bounded by short TTL; replay blocked by nonce + expiry; malicious-verifier tracking bounded by audience-binding and minimum disclosure; compromised-issuer risk bounded by a small vetted issuer set plus public audit logs; correlation risk bounded by non-reused identifiers; government/platform chokepoint abuse — the most serious item — bounded by minimal disclosure, appealable governance, and capped issuer concentration). **New evidence folded in here:** the real-world MCP authentication gap (01, above) is not just wedge-evidence, it's threat-model evidence — it's the exact failure pattern (auth declared but not enforced, or skipped entirely) Rilavo's stateless model is built to make structurally harder to fall into.

### 23 — Security Response Model
**Priority P0. Decision.** Severity and emergency-action authority sit with the operator running the compromised component at v0 (i.e., Rilavo, since there's one issuer) — **Status: Deferred**, this authority needs to move to a documented, appealable process the moment a second issuer exists, per 24. Disclosure: security incidents affecting live credentials get disclosed to affected verifiers immediately and publicly within a defined window — exact window **Open**, pending legal review.

### 24 — Governance Specification
**Priority P0. Decision.** v0 governance is Model A: the founder controls the reference implementation, sets initial issuer standards, and can patch security issues fast. **Powers the founder must never have, even now:** unilateral, undisclosed control over credential portability, and unilateral removal of a participant without a documented, appealable process. **Transition target:** Model C/D — infrastructure operator atop an independently governed protocol — triggered by 25.

### 25 — Decentralization Trigger
**Priority P0. Decision, interrogated per §25's own instruction rather than just restated.** The existing trigger — no single issuer, including Rilavo, holds a majority of proof-issuance volume — is kept, but it is explicitly **not sufficient on its own**, because issuance share doesn't capture every centralization risk. A single *verifier* implementation could still become the de facto gate even with many issuers (if everyone uses one verifier library uncritically). Discovery (17), key infrastructure (12), and software distribution (the SDK) can each recentralize independently of issuance share. **Decision:** issuance-share stays the primary, automatic trigger for governance transition, but discovery-concentration, verifier-implementation-concentration, and SDK-distribution-concentration are added as monitored secondary metrics that trigger a *review*, not an automatic transition — because those three are harder to define a clean numeric threshold for today. **Status: Open** on the exact secondary thresholds.

### 26 — Protocol Versioning
**Priority P2. Decision.** Semantic versioning at the wire-format level; v0's credential format is explicitly *not* frozen until it survives one production partner's real traffic (per 06). Once frozen, breaking changes require a new major version verifiers can opt into, never a silent change to an existing one.

### 27 — Backward Compatibility
**Priority P4. Deferred.** There is no prior version to be compatible with yet. This entry exists in the tree so the question isn't forgotten once v1 ships — it is honestly empty today.

### 28 — Upgrade and Migration
**Priority P1. Decision.** Cryptographic agility is designed in from day one even though only one algorithm is used: the credential format includes an explicit algorithm identifier field, so a future migration (post-quantum or otherwise) is a new supported value, not a format rewrite. **Post-quantum migration itself:** **Status: Deferred** — not needed at v0's stakes (short-lived, low-value credentials), worth a standing watch item rather than active work.

### 29 — Performance Requirements
**Priority P2. Decision — targets, not yet load-tested:** sub-10ms local verification (consistent with Ed25519's microsecond-scale signature checks plus network overhead), issuance latency low enough not to be the bottleneck in an agent's request path. **Where "near-zero marginal cost" stops being literally true:** at meaningful scale, revocation-log storage growth and issuer signing throughput become real, budgeted infrastructure costs — this is stated plainly in the existing audit spec and repeated here so it isn't lost: the phrase is a useful approximation, not a literal claim.

### 30 — Reliability Requirements
**Priority P1. Decision.** Verification must work with zero dependency on Rilavo's uptime once a public key is cached — that's the entire point of a stateless design. Issuance and revocation-log updates do depend on live infrastructure; **Open:** the specific uptime target and RTO/RPO for those, pending real operational data from the first pilot.

### 31 — Deployment Guide
**Priority P2. Decision.** Three paths at v0: hosted issuance (Rilavo runs it), embedded SDK verification (no deployment at all, just a library call), and self-hosted issuance (32) for anyone who doesn't want to depend on Rilavo's infrastructure even at this early stage.

### 32 — Self-Hosting Guide
**Priority P2. Decision.** Self-hosting an issuer must be possible from day one and documented, not added later — this is a direct, practical expression of the "protocol survives without the company" commitment, not a someday feature.

### 33 — Operator Requirements
**Priority P3. Open.** Pending 24 (Governance) defining an actual admission process — there's nothing to require of an operator yet because there's no second operator to admit.

### 34 — Horizon 2 Specification (Agent Delegation)
**Priority P1 (rises to P0 when triggered). Decision.** Content: the attenuation model from 08, formalized — scope-narrowing-only across tools/budget/domain/time, bounded depth, mandatory delegation context, ephemeral sub-agent keys. **Adds, from AIP's model specifically:** three escalating trust levels for delegated results — self-reported, counter-signed, and third-party attested — letting a verifier judge not just whether an agent was authorized, but how strongly the outcome it's reporting back can be trusted.<cite index="0-1">AIP defines three escalating trust levels for completion data—Self-Reported, Counter-Signed, and Third-Party Attested—allowing receiving systems to mathematically verify not just the agent's identity, but the provenance of the result it delivers</cite> **Entry trigger:** proof that v0's single-hop model is actually constraining real integrations, not speculative demand.

### 35 — Horizon 3: Human Verification
**Priority P2 (deferred by design). Decision on architecture direction, Open on timing.** Must be edge-computed and ZK-based from day one of this horizon — not retrofitted — specifically to avoid becoming the biometric data honeypot every existing KYC vendor already is. **Concrete case study grounding the design requirement, not just the principle:** Nigeria's 2026 identity/AML regime is a live example of exactly the tension this horizon has to resolve — CBN's tiered customer due diligence ties account risk tiers to BVN/NIN verification, the 2026 NIMC Act anchors financial transactions to a single verified national ID, and the accompanying Nigeria Data Protection Act imposes criminal penalties (a minimum five-year term) for unauthorized access to identity records. A regime with that liability profile is precisely the kind of environment where "prove eligibility without transmitting the underlying identifier" is a compliance asset, not just a privacy nicety — and it correlates with results: Nigerian digital payment fraud fell roughly 51% between 2024 and 2025 as database-backed identity verification tightened, which is suggestive evidence (not proof) that rigorous, standardized verification works at national scale when done right. **Status: genuinely Open** on whether Rilavo should target this or any specific jurisdiction first — that's a market decision belonging to the Product tree (see Product doc 10), not a protocol one.

### 36 — Horizon 3: Content Provenance
**Priority P2 (deferred by design, but with an external deadline attached — see below). Decision on direction.** What's proven: human-made vs. AI-generated vs. AI-assisted, signed at creation time, with provenance designed to survive re-encoding rather than rely on after-the-fact forensic detection. **External catalyst, concrete and dated:** the EU AI Act's Article 50 already requires generative-AI providers to mark synthetic audio, video, text, and image output as machine-readable and detectable, backstopped by fines reaching €15 million or 3% of global turnover, and the Act's Code of Practice sets a deadline for signatories to implement a unified, interoperable watermark-detection mechanism rather than forcing every platform to query every AI provider's proprietary detector separately. That interoperability requirement is the opening a neutral, cross-provider verification protocol is built for. **Status: Open** on whether Rilavo pursues this horizon on its own timeline or the regulatory deadline effectively sets it — flagged as a real external forcing function, not invented urgency.

### 37 — Horizon 4: Device and Software Attestation
**Priority P3. Decision, minimal.** Consume existing hardware attestation (TPM, Secure Enclave) rather than build competing infrastructure — this horizon is about integrating established signals, not inventing new ones. **Centralization risk flagged explicitly:** leaning on a small number of hardware vendors' attestation roots would quietly reintroduce the exact centralization the rest of the protocol is designed to avoid. **Status: Deferred**, no near-term trigger identified.

### 38 — Protocol Economics
**Priority P0. Decision.** The protocol — format, standard, revocation log, core API — is free, permanently, not as a promotional stance but structurally: metering the base layer would add friction at precisely the moment network effects need maximum velocity, and every commercial layer downstream (Product tree) depends on the base format being something nobody has to negotiate to use. **Can a future governance body introduce a protocol-level fee?** Technically yes, practically **Rejected** as a direction — nothing about the economics requires it, and it would hand a future governance body the exact taxing power this whole structure is designed to prevent any single party from holding.

### 39 — Protocol Licensing
**Priority P0. Decision — corrected from earlier project material.** Earlier research floated a copyleft (GPLv3) license as a deliberate "anti-fork trap." That reasoning doesn't hold: GPLv3's copyleft obligation triggers on *distribution* of a derivative work, so a competitor running a modified fork purely as an internal service never has to release anything — the AGPL exists specifically to close that gap, and even AGPL is slow and contested to enforce against a well-resourced opponent. Worse, copyleft licensing creates real adoption friction for the products this protocol most needs as verifiers, many of whom have blanket policies against GPL-family code in commercial products. **Decision:** license the reference implementation and SDKs permissively (Apache 2.0 or MIT) instead. **Rationale:** the moat was already correctly identified elsewhere in this tree (28/47 in the Product document, and the existing audit's Fork Test) as the trust graph — installed verifier base, issuer reputation, fraud-pattern intelligence, standards legitimacy — none of which a permissive license gives away, and all of which a restrictive license fails to protect anyway. **Status: Rejected (copyleft), Decision (permissive).**

### 40 — Protocol Ethics and Abuse
**Priority P0. Decision.** Unacceptable abuse cases, named explicitly rather than left implicit: using Rilavo to build a centralized blacklist of excluded people or agents; using it as a de facto mandatory "real human" certificate that gates participation in ordinary digital life; any use where a government or platform captures issuance to selectively deny service. **Enforcement:** boundary-setting sits with governance (24); appeal rights are a hard requirement on any removal or revocation process, not a nice-to-have.

### 41 — Protocol Regulatory Architecture
**Priority P0. Decision — the distinction this whole tree is built around, restated at the protocol layer specifically.** *Privacy* decentralization (edge compute, no central data store, minimum disclosure) protects against breaches and government data demands, and the protocol's architecture genuinely delivers this. *Market* decentralization (no single dominant issuer or verifier) protects against antitrust and gatekeeper exposure, and the protocol only has a *triggered intention* toward this (25), not yet the fact of it. **Decision:** the protocol's regulatory posture is to already do, voluntarily, what a future access-regulation regime would require — open format, portable credentials, no exclusivity — so a future designation, if it comes, changes nothing operationally.

### 42 — Protocol Disaster Recovery
**Priority P1. Decision.** For a stateless-verification design, "protocol availability" mostly means key-directory and revocation-log availability, not issuance availability — a verifier that already has a cached key can keep verifying through an issuance outage. **Open:** formal RTO/RPO targets, pending real operational history.

### 43 — Protocol Sunset and Succession
**Priority P0. Decision.** If the operating company disappears today: issuance halts, but exported, principal-held credentials remain valid until natural expiry — meaningfully better than total failure, because portability was a day-one requirement (06), not a later feature. Target end-state, once 25's trigger fires: the protocol, standard, and other operators continue; only the commercial layer built on top disappears with its operator. The gap between today and that target is exactly measured by whether the trigger has fired — a checkable fact, not an aspiration.

### 44 — Protocol Decision Log
**Priority P0. Decision.** Every entry above marked **Decision** or **Rejected** in this document is a first entry in this log. It should move to a standalone, append-only file the moment implementation starts, so agent-generated code always has a single, current source of truth to check against (Question Bank §69–70).

### 45 — Protocol Changelog
**Priority P4. Deferred.** Nothing has shipped yet. Opens on first release.

---

## Protocol Go/No-Go Gate (Question Bank §86), checked against the above

| Gate question | Cleared? |
|---|---|
| What exact problem is being solved? | Yes — 01, 03 |
| What is the exact proof, trust model, security model? | Yes — 06, 05, 22 |
| What happens if the issuer is compromised, or Rilavo disappears? | Yes — 12, 43 |
| How does revocation and portability work? | Yes — 09, 06 |
| What's free, what's open, what remains centralized, and why is that acceptable now? | Yes — 38, 39, 15 (single issuer, disclosed, low-stakes credentials only) |
| What triggers decentralization? | Yes, with an acknowledged gap — 25 (issuance-share trigger set; secondary metrics identified but not yet thresholded) |
| Is there a test proving the network effect exists, or is it assumed? | **Not yet.** This is the one gate item still open — the verification/developer/AI-agent loops are mechanically plausible (they mirror the existing audit's loop analysis) but unproven until a real pilot runs. **This is the single condition standing between v0 and full go.** |

## The Five Final Questions — protocol side (Q1–Q3 primarily; Q4–Q5 belong to the Product document)

**Q1 — Necessity:** the world increasingly lets autonomous software act on people's and organizations' behalf; that requires a way to check the software is allowed to do what it's doing, because the alternative — implicit trust or blanket blocking — doesn't scale with how fast agentic traffic is growing.

**Q2 — Protocol:** the smallest open mechanism is exactly v0 — a signed, short-lived, audience-bound authorization credential, verifiable with a public key and a revocation check, nothing more.

**Q3 — Network:** each legitimate verifier that accepts the format makes issuance more valuable to the next issuer, and each issuer expands what a verifier can trust — genuinely mechanical, not a marketing claim, though still unproven at real scale (see the Go/No-Go gap above).

*(Q4 and Q5 are answered in full in `Rilavo_Product_Mother_Blueprint.md`, since they turn on why a company — not the protocol — survives.)*

---

## Closure condition self-check (§90)

Every **Decision** and **Rejected** entry above traces to a named section of the Mother Audit Question Bank, the existing Audit & Specification, or the Research Plan — none were invented for this document. Every **Open** and **Deferred** entry is left that way deliberately, per Appendix D: the question list wasn't shrunk to make the tree easier to close. Documents 06, 07, 09, and 22 are the ones a downstream builder should treat as most load-bearing; document 39's licensing correction and document 25's trigger-interrogation are the two places this blueprint actively revises rather than just restates prior material.
