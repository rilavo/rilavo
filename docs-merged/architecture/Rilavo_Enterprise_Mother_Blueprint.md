# Rilavo Product — Mother Blueprint

**Document type:** Mother blueprint for `/RILAVO_PRODUCT/` (45 documents)
**Status:** Seeds documents 00–45, plus the Connection-tree content (Question Bank Part IV, §53–58) that lives inside Product documents 39–43 rather than as a separate tree — that placement is itself a decision, explained at 39.

**Governing rule for this document, mirroring the Protocol blueprint's own:** Product is written as *one possible operator*, not the privileged one. Every claim below has to justify itself against an open, free, forkable protocol — nothing here gets to assume loyalty just because Rilavo built the reference implementation first. Where that justification is genuinely uncomfortable, this document says so rather than papering over it — see 25, 40, and 41–43 in particular.

Confidence/status/priority vocabulary is identical to the Protocol document's: Confidence — *Confirmed / Strong evidence / Working assumption / Unknown*. Status — *Decision / Open / Rejected / Deferred*. Priority — *P0 → P4*.

---

## Part I recap — What the product is (§1.2, §1.3)

**What the company sells:** not the protocol — the protocol is free and always will be (Protocol Blueprint, doc 38). It sells continuous operation, accumulated intelligence, and accountability: hosted infrastructure a customer doesn't have to run, fraud signal a customer can't generate alone from its own traffic, compliance packaging a customer would otherwise build in-house, and a support relationship with a real party to call when something breaks.

**Why it must exist if the protocol can function without it:** because "the protocol can function without it" and "a given product customer wants to run their own issuer, patch their own security, and build their own fraud-detection from zero" are different claims. Most won't want to. That gap is the entire commercial thesis — and it only holds if the gap is real, which is why 06 and 26 below are treated as the two hardest, most load-bearing entries in this document, not the easiest.

**Strongest economic reason to exist:** products already have a funded budget line for exactly this problem — fraud, compliance, and trust-and-safety spend that exists today, independent of Rilavo. **Weakest assumption, named plainly:** that being first confers durability by itself. It doesn't. It buys time to build the things that do (26).

---

## The 45 documents

### 00 — Product Master Specification
**Priority P0. Decision.** This blueprint is the working draft of 00, graduating once 01 (mission), 06 (product portfolio), 15 (pricing), 17 (revenue model), and 26 (moat) are frozen — the same "four or five load-bearing documents first" logic as the Protocol tree, applied here.

### 01 — Product Mission
**Priority P0. Decision.** Exists to remove operational burden (running production-grade issuance/verification with correct security hygiene), financial loss (fraud from unauthorized or wrongly-trusted agent actions), and engineering cost (building this internally, badly, slowly) that a business would otherwise absorb itself. **What it performs that an individual developer or internal team structurally cannot:** intelligence that only accrues from operating *across* many customers' traffic — no single customer, however skilled, can see the cross-customer fraud pattern Rilavo can (09, 26).

### 02 — Company Identity
**Priority P1. Decision.** Trust infrastructure, closer in kind to security infrastructure than to a KYC vendor or an "AI company." First commercial product: hosted agent-authorization issuance and verification for developers who don't want to run their own issuer. Known for, first: being correctly scoped and boring in the good sense — the layer that just works. **Never to become known for:** a data broker, or a mandatory arbiter of who counts as a "real human" — either would violate the ethics boundary already set in the Protocol tree (doc 40) and would be close to an extinction-level reputational risk, not a growth strategy.

### 03 — Customer Problem
**Priority P0. Decision.** The first paying customer is a platform or API provider currently either blocking all inbound AI-agent traffic (losing legitimate business) or accepting it blind (carrying the liability) — the same wedge evidence as the Protocol tree's doc 01, now read as a sales trigger rather than a design trigger. Economic buyer: whoever owns platform-risk or trust-and-safety budget. Technical buyer: the integrating engineering team. These are frequently different people, and the sales motion (22) has to speak to both.

### 04 — Customer Segments
**Priority P1. Decision, ranked by buying urgency, not by market size:** (1) API/platform providers with active, unmanaged agent traffic today; (2) MCP server operators specifically, given the well-documented authentication gap in that ecosystem (Protocol doc 01); (3) fintech and marketplace platforms with agent-initiated transactions; (4) compliance-heavy verticals, once Horizon 3 ships (10). Segment 1–2 are where v0 evidence already exists; 3–4 are informed projection, not yet demonstrated demand — **Confidence: Working assumption** for 3–4.

### 05 — Value Proposition
**Priority P0. Decision.** Measurable, not aspirational: reduced fraud loss from unauthorized agent action, reduced manual-review and allowlisting engineering hours, higher legitimate-agent success rate (fewer false blocks), reduced liability exposure. **ROI test:** a customer should be able to compare "cost of building this internally plus residual fraud rate without it" against "Rilavo's usage-based fee" using their own numbers, without needing to trust anything Rilavo says about itself. If that comparison can't be run independently, the value prop isn't real yet.

### 06 — Product Portfolio
**Priority P0. Decision.** Hosted issuer/verifier API, fraud-intelligence feed (09), compliance tooling (10), SLA-backed infrastructure (12), incident response (13), developer dashboard (07). Each is tested the same way: does it consume a protocol primitive and add something genuinely proprietary on top (uptime, aggregated pattern data, audit packaging), or is it just the free protocol with a markup? Every item on this list passes that test as designed; the discipline is making sure nothing gets added to it later that doesn't.

### 07 — Developer Platform
**Priority P0. Decision.** Free: SDK, docs, sandbox/test issuer, a generous base API tier. Paid: usage past that tier, dashboards, staging environments, priority support. **Never paywalled, as a hard line:** the ability to self-host and never touch Rilavo's infrastructure at all (Protocol doc 32). **What portion of developers convert to paying customers:** genuinely **Unknown** pre-pilot — stated as unknown rather than estimated, because a fabricated conversion number would be exactly the "manufactured certainty" this whole framework exists to prevent.

### 08 — Managed Infrastructure
**Priority P1. Decision.** The pitch for hosted over self-hosted is removing operational burden — key management, uptime, security patching — for teams without dedicated security engineering, not removing capability the customer couldn't otherwise have. **Migration away must stay straightforward** — export credentials and configuration, point at a self-hosted issuer — or "managed infrastructure" quietly becomes "lock-in with a friendlier name," which the question bank calls out by name (§37) as the exact failure mode to avoid.

### 09 — Fraud Intelligence
**Priority P0. Decision.** Aggregatable, safely: behavioral patterns — velocity anomalies, credential-reuse signatures, revocation-triggering behavior clusters. Never aggregated: anything letting one customer infer another's specific activity, or anything that re-identifies a principal from pattern data. This is the commercial expression of the trust-graph moat named in the Protocol tree's fork test (39) — it only stays defensible if it stays privacy-preserving, because the moment it requires raw data sharing, competitive-separation and privacy promises both break at once.

### 10 — Compliance Products
**Priority P1 now, rises to P0 once Horizon 3 ships. Decision — with real, dated external grounding, not manufactured urgency.** Two concrete anchors from the research already gathered: the EU AI Act's Article 50 imposes a hard, fined obligation (up to €15 million or 3% of global turnover) on marking synthetic media as machine-detectable, with the Act's own Code of Practice pushing toward a unified, interoperable watermark-verification mechanism rather than per-provider bespoke checks — that interoperability requirement is a sellable compliance product the moment Rilavo's content-provenance horizon (Protocol doc 36) ships. Separately, Nigeria's 2026 identity regime — CBN's tiered customer-due-diligence rules tying account risk tiers to BVN/NIN verification, the NIMC Act anchoring transactions to a verified national ID, and the Nigeria Data Protection Act's criminal penalties for mishandling identity records — is a concrete, well-documented first-market candidate for a Horizon-3 human-verification compliance product, precisely because "prove eligibility without transmitting the raw identifier" is worth real money in a jurisdiction with that liability profile. **Hard line, stated explicitly so it never gets blurred in a sales conversation:** Rilavo is infrastructure that produces a verifiable audit trail, not a certification that a customer's overall compliance program satisfies any regulator — what it can and cannot attest needs to be contract language, not marketing language.

### 11 — Security Services
**Priority P3. Decision, minimal.** Not a distinct product at v0 — proactive secure-integration review folds into developer platform support (07) until there's evidence of standalone demand. **Status: Deferred.**

### 12 — SLA and Assurance
**Priority P1. Decision.** Worth paying for specifically because issuance and revocation-log freshness genuinely depend on live infrastructure, even though verification itself doesn't (Protocol doc 30) — any customer putting Rilavo in a live transaction path needs bounded, compensated outage risk. **Open:** actual tier numbers, pending real operational history from the first customers rather than invented targets.

### 13 — Incident Response
**Priority P0. Decision.** Escalation: customer → Rilavo → affected third-party issuer if applicable → public disclosure, on the same disclosure-window logic flagged as still open in the Protocol tree's doc 23 — deliberately not re-decided differently here, since it's one decision viewed from two documents, not two decisions. Authority to revoke or suspend during a live incident sits with whoever operates the compromised component.

### 14 — API Business Model
**Priority P0. Decision.** Billable event: a verification call beyond a generous free tier, priced small and usage-based — consistent with the original $0.001/query figure in the founding project material, treated here as a starting anchor to be tested against real infrastructure cost, not a fixed commitment.

### 15 — Pricing (including the $1 Audit, §43)
**Priority P0. Decision — this is the single most re-litigated question across the whole project, settled here plainly.** $1 is not a per-user annual revenue line. It is an optional, near-cost mechanic for an individual principal to self-issue or maintain a personal credential — nothing more. **Would adoption survive if it were free?** Yes, mostly — and that's exactly the test that disqualifies it as revenue: if removing the charge wouldn't be noticed, it was never doing revenue work. **Payment-processing reality:** card-processing minimums routinely exceed the margin on a standalone $1 transaction, which is itself an argument against treating $1 as a billable event at all, not just a stylistic preference. **Legal and accounting treatment of the $1 mechanic:** genuinely **Open**, deferred to counsel. **Real pricing:** usage-based API fees plus product infrastructure, compliance, SLA, and intelligence tiers (16–17) — all mapped to budgets that already exist, which is the actual discipline (§11's own test: value already being purchased somewhere, not hoped-for new demand).

### 16 — Unit Economics
**Priority P0. Decision.** Marginal cost per verification is low but not zero — signature verification is computationally cheap; revocation-log storage growth, support, and fraud-monitoring are not (Protocol doc 29, repeated here because it's the exact assumption pricing depends on). **Open:** the actual cost curve, pending real infrastructure spend data past the first few thousand customers.

### 17 — Revenue Model
**Priority P0. Decision, per layer:**

| Layer | Why it holds |
|---|---|
| Free protocol/SDK | Adoption is the asset; a metered core would never reach network-effect density |
| API usage | Small per-verification fee past a free tier — billable, measurable, usage-linked |
| Managed infrastructure | Replaces an internal ops/security build a customer would otherwise fund themselves |
| Compliance | Genuine, dated, regulator-driven demand (10) — not manufactured |
| SLA | Worth paying to bound outage risk in a live transaction path |
| Fraud intelligence | Sellable because it only exists at network scale — no single customer can replicate it alone |

**Revenue concentration risk (§42):** no single product customer should be allowed to become large enough that losing them threatens survival. **Status: Open** — no numeric cap decided yet, flagged as a real design constraint for 22 (sales process) rather than resolved here.

### 18 — Go To Market
**Priority P0. Decision.** Developer-led and product-led first, not product-sales-led — the wedge audience is technical and reachable through documentation and direct outreach, without paid advertising (consistent with the original audit's own §7). Shortest sales cycle: MCP server operators and agent-platform builders already exposed by the documented authentication gap — a felt, current pain, not a hypothetical future one. 14-day proof of value: a pilot integration demonstrably blocking unauthorized traffic in the customer's own sandbox.

### 19 — Network Distribution
**Priority P0. Decision.** Inherits the Protocol tree's own verification and developer loops directly (Protocol doc §8 in the underlying audit) rather than inventing a separate product distribution mechanism — Product's distribution is mostly a byproduct of protocol adoption working, not a parallel effort.

### 20 — Partner Ecosystem
**Priority P1. Decision.** Integrate-not-compete candidates: agent-framework vendors (natural issuers), API gateway vendors (natural verifiers), cloud marketplaces (distribution surface). Certification/reseller candidates: compliance consultants, once 10 has real product to sell. **What stops a partner becoming a competitor:** nothing structurally does, on purpose — the protocol being open means any partner *can* become an operator (Protocol doc's governing rule). Product's job is to be the best operator, not the only permitted one.

### 21 — Customer Success
**Priority P1. Decision.** Retention has to come from compounding value — fraud-detection accuracy and false-block rates improving with more observed traffic — not from withheld interoperability. A customer must be able to export their data and leave, and return later without losing compatibility with the network. Anything less would directly contradict the anti-lock-in commitments made throughout this document (08, 20) and the Protocol tree's own portability requirements.

### 22 — Sales Process
**Priority P2. Decision.** Standard objections to prepare for: a security questionnaire (target certification level **Open**, not yet decided), data-handling questions (answered cleanly by the minimum-disclosure architecture itself), and the honest one — "why trust a young company with this." **Decision:** answered by contractual SLA and incident-response commitments plus guaranteed exportability, not by claims about size or funding the company doesn't yet have.

### 23 — Marketing
**Priority P3. Decision.** Minimal and technical: documentation quality, integration guides, and transparent public incident writeups do more work for this audience than campaign spend, consistent with a growth thesis that rests on mechanical loops rather than advertising (Protocol doc §27 loops, inherited). **Status: Deferred** as a dedicated function until product-led data suggests otherwise.

### 24 — Developer Relations
**Priority P2. Decision.** A trust-building function, not a marketing channel: responding fast in public developer venues, publishing real postmortems after incidents (13), keeping the SDK experience genuinely good. Distinct from the free tier itself (07) — this is about relationship, not pricing.

### 25 — Competitive Strategy (§45, §46 — the two hardest tests in the bank, answered directly)
**Priority P0. Decision, stated without softening.** **Scenario:** a much richer company forks the open protocol and launches a better-funded, cheaper, faster-growing hosted service. **What they copy immediately:** all of it — code, API surface, credential format — because it's open by design (Protocol doc 39). **What they cannot copy immediately:** issuer reputation history, fraud-pattern intelligence from real accumulated traffic, and an installed verifier base that already trusts the *original* format — a well-funded rival still starts with zero verifiers on day one, because trust doesn't transfer with capital. **Can Rilavo Product compete on price against AWS, Microsoft, Google, or Cloudflare?** No, and it shouldn't try — that's a fight against infrastructure economics no early-stage company wins. **Could any of those companies build this?** Yes, easily, faster than Rilavo can. **The honest answer this forces:** if technical capability alone were the defense, Rilavo Product should not exist independently. The actual defense is that none of them have an obvious reason to move first on a narrow, unglamorous B2B security primitive before it's proven — so being early and being right about the wedge is the entire game, not a footnote to it. **Status: genuinely Open, not resolved** — this is the single most important unresolved risk in this document, and Appendix D's instruction not to manufacture certainty applies here more than anywhere else in the tree.

### 26 — Product Moat
**Priority P0. Decision.** What compounds with scale, specifically at the product/operational layer (distinct from the protocol's own moat in its Fork Test): operational track record (fewer incidents, better-tuned fraud signals over time), hard-won jurisdictional compliance integrations (each new regulatory regime supported takes real work, not a checkbox), and relationships — partners who've operated alongside Rilavo through an actual incident trust it differently than a new entrant they've never tested. **Not a moat, and shouldn't be treated as one:** the hosted infrastructure itself, the dashboard UI, the pricing page — all trivially replicable and explicitly excluded from this list on purpose.

### 27 — Data and Intelligence Policy
**Priority P0. Decision.** The same guardrail flagged in the Protocol tree (doc 41) restated at the product layer, because it's the same risk from the other side: what Product learns from operating the network must never silently become protocol governance power. If it does, the claim that the protocol is neutral becomes false in substance even while staying true on paper — and that gap is exactly what a future antitrust or gatekeeper review (Protocol doc's governing distinction between privacy- and market-decentralization) would go looking for. Customers can demand deletion of their own data; aggregate fraud signals must be architected to survive that deletion, not just promise to honor it.

### 28 — Legal and Regulatory
**Priority P1. Decision.** At v0, Product is not a data controller of anything sensitive by design — no biometric data, no long-lived personal identifiers (Protocol doc 13). That changes the moment Horizon 3 ships (human verification, content provenance), at which point operating an issuer plausibly becomes a regulated activity in specific jurisdictions. **Status: Deferred to real counsel per claim-type, before Horizon 3 launches — not before.**

### 29 — Privacy and Data Governance
**Priority P1. Decision.** Controller/processor/joint-controller roles are genuinely **Open** and jurisdiction-dependent, and shouldn't be pre-answered generically — this gets resolved per Horizon and per market as each one is actually entered, not speculatively now.

### 30 — Product Security
**Priority P0. Decision.** Least-privilege internal access to signing infrastructure; no single employee able to unilaterally rotate a production issuer key; a mandatory human security review gate before any liability-bearing release — directly inheriting the solo-founder development gate from the original audit specification rather than inventing a separate product-security standard.

### 31 — Insurance and Liability
**Priority P0. Decision.** Builds directly on the allocation already set in the Protocol tree (doc 05): issuer liable for wrongly issued credentials, verifier liable for accepting an invalid one, Product liable — as protocol-level operator — only for provable protocol-level failure such as key compromise. **Status: Deferred** to real contractual terms of service and, once volume justifies the cost, an actual insurance product — not yet in place, and shouldn't be described to a customer as though it already were.

### 32 — Finance and Operations
**Priority P4. Deferred.** Not a blueprint-stage decision for a solo-founder-plus-AI-agents company. Flagged here only so it isn't silently assumed later without ever having been asked.

### 33 — Human Resources
**Priority P4. Deferred.** Same treatment as 32, for the same reason.

### 34 — Vendor Management
**Priority P4. Deferred.** Same treatment as 32–33.

### 35 — Corporate Governance
**Priority P2. Decision, one line, but important.** The legal entity's own governance (board, decision rights) must stay institutionally separate from protocol governance (Protocol doc 24) — conflating the two is exactly the capture risk named in 27. Beyond that separation, entity-level governance detail is **Deferred**, appropriate to current stage.

### 36 — Funding and Capital
**Priority P4. Deferred.** Not decided here; flagged so it isn't assumed silently.

### 37 — Product Risk Register
**Priority P0. Decision — a register, not a new analysis: consolidates risks already named elsewhere so none quietly drop out of view.** Revenue concentration (17), replication by a hyperscale competitor (25), governance capture of protocol neutrality by product data (27), regulatory characterization risk at Horizon 3 (28), and single-issuer key compromise (inherited from Protocol doc 12). Each has an owning document above; this entry's only job is to make sure the list stays visible as one list.

### 38 — Competitor Response Playbook
**Priority P1. Decision.** The practical version of 25: if a well-funded competitor forks and undercuts on price, the response is not a price war — it's accelerating the assets that don't fork (fraud-intelligence accumulation, standards-body engagement, deepening the earliest integrations) rather than competing on the one axis (capital-funded infrastructure economics) where Rilavo structurally cannot win.

### 39 — Protocol Relationship
**Priority P0. Decision — this is where the Connection-tree content (Question Bank §53) lives, by design, rather than in a separate document tree.** Product consumes protocol primitives (issue/verify calls, the revocation log) and produces protocol-compatible credentials with no more privilege than any other operator could have. What flows from protocol to Product: verification events, in aggregate, for fraud intelligence (09). What must never flow: anything letting Product reconstruct an individual principal's identity from protocol-level data alone. **The test of whether this separation is real, not just claimed:** Product must be able to operate without any proprietary protocol privilege. If a future audit found a privilege that only Rilavo Product held at the protocol layer, that would falsify the entire two-tree structure — this is stated as a standing test, not a one-time check.

### 40 — Protocol Funding and Stewardship (§55)
**Priority P1. Decision on principle, Open on mechanism.** No money needs to enter the protocol layer (Protocol doc 38). As Product matures, it will plausibly become the largest funder of governance activity, audits, or ecosystem grants around the protocol — and that creates a real capture risk worth naming now rather than discovering later. **Decision:** any future funding relationship must be structured so governance seats are never proportional to money contributed. **Status: Open** on the actual mechanism — resolving this in more detail today would be exactly the unearned certainty Appendix D warns against.

### 41 — Survival If Protocol Forked
**Priority P0. Decision, honestly stated.** Product survives a fork if its trust graph and operational record are real and demonstrated (26); it does not survive on the strength of having built the reference implementation first. This is a direct consequence of 25, not a new claim.

### 42 — Survival If Competitor Operates Better Infrastructure
**Priority P0. Decision, honestly stated.** Because customers can leave Product without leaving the protocol (07, 08, 21 — all by design), Product has to actually earn retention through service quality and accumulated intelligence. It cannot assume it, and nothing in this document's structure lets it.

### 43 — Survival If Rilavo Protocol Declines
**Priority P0. Open — this is the least comfortable entry in the entire tree, and it stays uncomfortable rather than being resolved artificially.** If a different standard becomes dominant instead of Rilavo's, Product's honest fallback position is that it operates trust-and-verification infrastructure — secure issuance, fraud intelligence, compliance packaging — skills that are largely protocol-agnostic even though the current product is built on one specific protocol. Whether that fallback is commercially real or just a comforting story is **genuinely untested**, and this document does not pretend otherwise.

### 44 — Succession and Continuity
**Priority P0. Decision.** Product-side company-dies-tomorrow is the same fact as Protocol doc 43, viewed from this document instead: today, issuance halts but exported credentials remain valid until natural expiry; the target end-state (protocol and other operators continue, only Product's commercial layer disappears) is reached exactly when the decentralization trigger fires (Protocol doc 25) — not before.

### 45 — Product Decision Log
**Priority P0. Decision.** Every entry above marked **Decision** or **Rejected** becomes a first entry here, on the same append-only discipline as the Protocol tree's doc 44.

---

## Product Go/No-Go Gate (§87)

| Gate question | Cleared? |
|---|---|
| Why does the company exist independently of the protocol? | Yes — 01, 06 |
| What does it sell, who pays, why, from what budget? | Yes — 03–06, 17 |
| Gross-margin logic? | Directional yes, numeric **Open** — 16 |
| What if a richer competitor provides better infrastructure? | Honestly answered, **not resolved** — 25, 42 |
| Can Product survive a protocol fork, or losing exclusive access to anything? | Honestly answered, **not resolved** — 41, 43 |
| Is the business genuinely competitive without artificial lock-in? | Yes by design (07, 08, 21) — but **untested** against a real competitor |

**Reading of this gate:** every mechanical question (what's sold, to whom, from what budget) clears cleanly. Every survival-under-real-competition question stays honestly open. That split is itself the finding — v0 is ready to build and sell; the moat is a thesis to be proven by operating, not a fact already established.

## Protocol–Product Joint Gate (§88)

Drawing on both documents: the protocol can function without Rilavo Product (Protocol doc 43 — degraded but not destroyed, even today). Product cannot yet demonstrate it can survive losing every privileged position (39, 41–43 above are Open, not resolved). Customers can leave Product without leaving the protocol (by design). Product cannot yet tax protocol access even if it wanted to (Protocol doc 38 forecloses this structurally). **Net reading:** the structure passes the *design* test — nothing here requires unilateral control by either side — but has not yet passed the *operating* test, which only real customers, real incidents, and real time can supply.

## The Five Final Questions — full synthesis, weighted toward Q4–Q5

**Q4 — Product:** a rational customer pays because protocol-level correctness (a valid signature checks out) is necessary but not sufficient — uptime, cross-customer fraud intelligence, compliance packaging, and a real party accountable when something breaks are not things the free protocol provides on its own, and building all of them in-house costs more than buying them from an operator who already has.

**Q5 — Survival:** this is the question this document refuses to answer with false confidence. If the protocol is copied, Product outcompeted, the founder gone, regulators active, and a better-funded rival runs a superior service on the same open protocol — what remains is the trust graph (issuer reputation, fraud intelligence, installed verifier base) *if and only if* it was genuinely built during the time Product had a head start. Nothing in this document proves that will happen. It states, as clearly as the rest of the tree states its decisions, that this is the one thing time and real operation have to prove — not architecture, and not this blueprint.

---

## Closure condition self-check (§90)

Every **Decision** and **Rejected** entry traces to the Mother Audit Question Bank (Part III primarily, Part IV for 39–43, and the relevant slices of Parts VI–VII), the existing Audit & Specification, or the Research Plan. The Connection tree (§85) was not built as a fourteenth-through-nineteenth separate document set — its content lives inside Product 39–43, which is itself a decision (stated at 39), not an omission. The two documents in this pair — Protocol and Product — are the complete required deliverable; nothing here assumes a third document exists to catch what these two don't cover.
