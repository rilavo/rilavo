# Rilavo — Master Dependency Register & System Boundary Map

**What this is:** the third artifact, not a fourth document tree. It converts the two Mother Blueprints from a content taxonomy (00–45, organized to match future filenames) into a build-sequenced project plan (organized by what actually blocks what). Every row traces to a document already decided in `Rilavo_Protocol_Mother_Blueprint.md` or `Rilavo_Product_Mother_Blueprint.md` — nothing here re-argues those decisions, it sequences them.

**Governing status vocabulary, used everywhere below instead of prose:**
- **Decided** — safe to build against now.
- **Open** — a real question with no manufactured answer; needs evidence, a pilot, or real operation to close.
- **Deferred** — correctly not being solved yet; opens on a named trigger, not a schedule.

---

## System Boundary Map

**Protocol → Product, what may flow:** issue/verify calls, the revocation log, public keys, aggregated verification telemetry for fraud intelligence. **What must never flow:** exclusive issuance rights, secret governance powers, privileged access to any protocol data an independent operator couldn't also get, or unilateral protocol-modification authority.

**Product → Protocol, what may flow:** the reference implementation, SDKs, interoperability and security research, ecosystem funding, governance participation as one voice among others. **The one hard constraint governing all of it:** money does not buy governance power. Seats are never proportional to funding contributed — stated once here so it's a system-level rule, not a line buried in Product document 40.

---

## Standing Tests

Not documents — permanent checks, re-run at every wave, never marked closed.

1. **Protocol Independence** — can the protocol function without Rilavo Product? *Target: yes. Current: partially — issuance is centralized at v0, but credentials are portable, which is the honest, load-bearing distinction.*
2. **Product Independence** — can Rilavo Product survive without exclusive control of the protocol? *Target: yes. Current: not proven — this is the real business risk in the entire project.*
3. **Mutual Non-Capture** — can either side become powerful enough to capture the other's governance? *Current: guarded against by design (Boundary Map, above), not yet tested by a real capture attempt.*

**Product Survival Matrix** — the practical, scenario-level expression of Test 2:

| Scenario | What must be true for Rilavo to survive it |
|---|---|
| Protocol is free | Product sells operation, not access |
| Customer can self-host | Hosted still wins on convenience, not lock-in |
| Competitor forks the protocol | Trust graph (26) is real, not assumed |
| AWS / Microsoft / Google enters | Being first + right about the wedge outweighs their capital |
| Competitor underprices Rilavo | Retention comes from accuracy and intelligence, not price |
| Competitor has better uptime or fraud detection | Same as above |
| Protocol itself gets replaced by a rival standard | Operating skill (secure issuance, compliance packaging) transfers |
| Founder disappears | Portability (06) already holds without them |
| Product fails outright | Protocol survives regardless (Protocol Independence, above) |

Every row is currently **Open**. This table doesn't get filled in by more writing — only by real operation.

---

## Wave 1 — System Foundation

*Unlocks: everything. Nothing below should start before this wave is genuinely stable.*

| ID | Document | Priority | Depends on | Status | Closes when |
|---|---|---|---|---|---|
| — | System Boundary Map | P0 | None | Decided | Re-audited every time a new Product product is proposed |
| P-00 | Protocol Master Spec | P0 | P-01,02,04,05 | Open (draft) | Freezes once P-06,07,09,22 freeze |
| P-01 | Mission & Scope | P0 | None | Decided | Confirmed by first pilot's real behavior |
| P-02 | Terminology | P0 | None | Decided | New terms enter only via decision log |
| P-03 | Problem & Wedge | P0 | P-01 | Decided | Same as P-01 |
| P-04 | Principles | P1 | P-01 | Decided | Revisited only if a decision would violate one |
| P-05 | Actor & Trust Model | P0 | P-02 | Decided (v0); Open (principal-held keys) | v0 scope closes now; reopens at Horizon 2 |
| P-38 | Protocol Economics | P0 | None | Decided | Reopens only if governance proposes a protocol fee |
| P-39 | Protocol Licensing | P0 | None | Decided | Locked at first public code release |
| E-00 | Product Master Spec | P0 | E-01,03,06,15,17,26 | Open (draft) | Freezes once E-06,15,17,26 freeze |
| E-01 | Product Mission | P0 | P-01 | Decided | Same as P-01 |
| E-02 | Company Identity | P1 | E-01 | Decided | Revisited only on repositioning |
| E-03 | Customer Problem | P0 | P-01 | Decided | Confirmed by first paying customer |
| E-04 | Customer Segments | P0 | E-03 | Decided (1–2); Working assumption (3–4) | Closes per segment as pilots land |
| E-05 | Value Proposition | P0 | E-03,04 | Decided (direction); Open (numbers) | Closes when a customer runs the ROI math independently |
| E-39 | Protocol Relationship | P0 | Boundary Map, P-05 | Decided | Re-audited with every new Product product |

## Wave 2 — Protocol Engineering Core

*Unlocks: anything that can be sold or integrated. This is the block the audit correctly identifies as one iterative loop, not six linear documents.*

| ID | Document | Priority | Depends on | Status | Closes when |
|---|---|---|---|---|---|
| P-06 | Credential Specification | P0 | P-02,05 | Decided (draft, not frozen) | Survives one production partner's real traffic without a breaking field change |
| P-07 | Authorization Model | P0 | P-06 | Decided | Same freeze condition as P-06 |
| P-09 | Revocation Specification | P0 | P-06,07 | Decided (mechanism); Open (fail-open/closed default) | Default revisited once verifiers with differing risk tolerance exist |
| P-10 | Audit Receipts | P1 | P-06 | Decided (format); Open (retention vs. erasure) | Closes once legal resolves the retention conflict |
| P-11 | Cryptographic Specification | P0 | None | Decided, Confirmed | Reopens only at a post-quantum migration trigger (P-28) |
| P-12 | Key Management | P0 | P-11 | Decided (mechanism); Open (incident runbook) | Closes once P-23 exists |
| P-13 | Privacy Architecture | P0 | P-06 | Decided | Re-audited at every future horizon |
| P-14 | Data Model | P1 | P-06,13 | Decided | Stable barring a new claim class |
| P-15 | Network Architecture | P0 | P-05 | Decided (v0: one issuer) | Reopens at the decentralization trigger (P-25) |
| P-17 | Discovery & Key Directory | P1 | P-15 | Decided (v0) | Reopens the day a second issuer exists |
| P-18 | Interoperability Specification | P0 | P-07 | Decided (posture); Open (which adjacent standard wins) | Revisited as CIMD/ID-JAG/AAuth stabilize |
| P-19 | API Specification | P0 | P-06,07 | Decided | Stable barring a breaking credential change |
| P-20 | SDK Specification | P0 | P-19 | Decided (contract); Unknown (target language, ease-of-integration claim) | Closes after first real developer integration |
| P-22 | Security Threat Model | P0 | P-06,07,09 | Decided | Re-audited every time P-06/07/09 change |
| P-23 | Security Response Model | P0 | P-12,22 | Decided (ladder); Open (disclosure window) | Closes once legal sets the window |
| P-26 | Versioning | P1 | P-06 | Decided (policy) | Exercised, not closed, at first breaking change |
| P-32 | Self-Hosting Guide | **P0 (corrected — see note)** | P-06,19,20 | Decided | Must exist **before** v0 launch |

**Note on P-32:** the original blueprint's own prose said self-hosting "must be possible from day one, not added later," but its priority field read P2 — an internal contradiction the audit's launch-critical callout exposed correctly. Fixed here to P0, moved from a later, lower-urgency slot into this wave.

## Wave 3 — Product Commercial Core

*Unlocks: a sellable product. Answers "can someone actually buy Rilavo?"*

| ID | Document | Priority | Depends on | Status | Closes when |
|---|---|---|---|---|---|
| E-06 | Product Portfolio | P0 | E-05, Wave 2 complete | Decided | Re-tested against "why not just the free protocol" per item |
| E-07 | Developer Platform | P0 | E-06, P-20 | Decided (split); Unknown (conversion rate) | Closes numerically after 90 days of real usage |
| E-08 | Managed Infrastructure | P1 | E-07 | Decided | Migration-out path tested before first customer signs |
| E-09 | Fraud Intelligence | P0 | E-06, P-10 | Decided (what's aggregable) | Closes once privacy counsel confirms the method |
| E-12 | SLA & Assurance | P1 | E-08, P-30 | Open (tier numbers) | Closes after real uptime history exists |
| E-13 | Incident Response | P0 | P-23 | Decided (mirrors P-23) | Same as P-23 |
| E-14 | API Business Model | P0 | E-06 | Decided (mechanism); Open (exact fee) | Closes against real infrastructure cost data |
| E-15 | Pricing (incl. $1 audit) | P0 | E-14 | Decided — $1 is acquisition cost, not revenue | Re-litigated only by formal amendment |
| E-16 | Unit Economics | P0 | E-14,15 | Open | Closes only with real cost data past first few thousand customers |
| E-17 | Revenue Model | P0 | E-14,15,16 | Decided (layers); Open (concentration cap) | Cap set before first large customer signs |
| E-18 | Go-to-Market | P0 | E-04,05 | Decided | Revisited if segments 1–2 don't convert as expected |
| E-19 | Network Distribution | P0 | Protocol's Wave-2 loops | Decided | Inherited, not separately closed |
| E-20 | Partner Ecosystem | P1 | E-18 | Decided (integrate-not-compete) | Tested at first real partner conversation |
| E-21 | Customer Success | P1 | E-07 | Decided (earned retention, not lock-in) | Closes at first renewal |

## Wave 4 — Survival & Defensibility

*Unlocks: nothing by writing. This wave's entire finding is that these documents cannot close themselves — they name what has to be proven by operating, not drafting.*

| ID | Document | Priority | Depends on | Status | Closes when |
|---|---|---|---|---|---|
| E-25 | Competitive Strategy | P0 | E-06,26 | **Open, by design** | Rilavo survives a real, well-funded competitor — not before |
| E-26 | Product Moat | P0 | E-09,25 | **Open, by design** | Accumulates through operation; never gets "decided" on paper |
| E-27 | Data & Intelligence Policy | P0 | E-09, P-13 | Decided (guardrail); Open (enforcement mechanism) | Closes once architecture, not just policy, prevents governance capture |
| E-37 | Product Risk Register | P0 | All of Wave 4 | Decided, as a living list | Never fully closes — reviewed every wave |
| E-38 | Competitor Response Playbook | P1 | E-25 | Decided (don't price-war) | Tested at first real competitive threat |
| E-41 | Survival If Protocol Forked | P0 | E-26, P-25 | Open | Closes only through real operation |
| E-42 | Survival If Better Infra Appears | P0 | E-26 | Open | Same |
| E-43 | Survival If Protocol Declines | P0 | E-26 | **Open — least resolved item in the whole project** | Same, and hardest of the three |

## Wave 5 — Governance & Institutionalization

*Unlocks: a second operator, real regulatory exposure, and the transition from prototype to institution. Correctly sequenced after Wave 4, not before — there's nothing to govern at scale until something worth operating exists.*

| ID | Document | Priority | Depends on | Status | Closes when |
|---|---|---|---|---|---|
| P-16 | Node & Operator Specification | P1 | P-15,24 | Deferred | Opens when a second operator applies |
| P-21 | Conformance Tests | P2 | P-06,07,09 | Deferred | Opens the day a second implementation is proposed |
| P-24 | Governance | P0 | P-05 | Decided (Model A now) | Transition begins at P-25's trigger |
| P-25 | Decentralization Trigger | P0 | P-24 | Decided (primary trigger); Open (secondary concentration thresholds) | Closes once thresholds are numerically set |
| P-33 | Operator Requirements | P1 | P-24 | Deferred | Same as P-16 |
| P-40 | Ethics & Abuse | P0 | P-24 | Decided | Re-audited at every future horizon |
| P-41 | Regulatory Architecture | P0 | P-13,25 | Decided (posture) | Re-tested if any jurisdiction actually designates Rilavo |
| P-42 | Disaster Recovery | P1 | P-15,23 | Open (RTO/RPO numbers) | Closes with real operational history |
| P-43 | Sunset & Succession | P0 | P-06,24 | Decided (today's state + target state) | Closes exactly when P-25's trigger fires |
| P-44 | Decision Log | P0 | Everything | Decided (practice) | Never closes — it is the record itself |
| E-28 | Legal & Regulatory | P1 | P-41 | Deferred beyond v0 | Opens before Horizon 3 |
| E-29 | Privacy & Data Governance | P1 | E-27 | Open | Resolved per-jurisdiction as each is entered |
| E-30 | Product Security | P0 | P-12 | Decided | Same gate as the original solo-founder review |
| E-31 | Insurance & Liability | P0 | P-05's allocation | Decided (allocation); Deferred (actual policy/ToS) | Closes when real ToS and an insurance product exist |
| E-35 | Corporate Governance | P2 | E-27 | Deferred | Only fixed point: stays separate from protocol governance |
| E-40 | Protocol Funding & Stewardship | P1 | P-38,24 | Decided (no governance-by-funding); Open (mechanism) | Closes once Product actually funds something at scale |
| E-44 | Succession & Continuity | P0 | P-43 | Decided, mirrors P-43 | Same as P-43 |
| P-45 / E-45 | Changelogs / Decision Logs | P4 / P0 | P-44 | Deferred / Decided (practice) | Changelog opens at first release; decision logs never close |

## Wave 6 — Future Horizons

*Gated, not scheduled. Nothing here starts until its own named trigger fires — that discipline is the point.*

| ID | Document | Priority | Depends on | Status | Opens when |
|---|---|---|---|---|---|
| P-08 | Delegation & Attenuation | P1→P0 at trigger | P-07 | Decided (direction, adapted from Biscuit/AIP) | v0 proves single-hop authorization is actually constraining real integrations |
| P-34 | Horizon 2 Specification | Same | P-08 | Same | Same |
| P-35 | Human Verification | P2 | P-13 | Decided (edge-compute/ZK direction); Open (first market) | An Product market decision is made — not a protocol one |
| P-36 | Content Provenance | P2, externally dated | P-13 | Decided (direction) | Effectively dated by the EU AI Act's own interoperability deadline |
| P-37 | Device/Software Attestation | P3 | None yet | Deferred | Only if a partner requires it |
| E-10 | Compliance Products | P1→P0 at trigger | P-35,36 | Decided (infrastructure, not certification); Open (first market) | The day either P-35 or P-36 ships |

## Continuous / As-Needed

*Deliberately not wave-gated — forcing these into a numbered wave would manufacture urgency none of them have. They open on a practical trigger, not a milestone.*

| ID | Document | Priority | Depends on | Status | Opens when |
|---|---|---|---|---|---|
| P-27 | Backward Compatibility | P4 | P-26 | Deferred, honestly empty | First v1 release |
| P-28 | Upgrade & Migration | P1 | P-11 | Decided (agility mechanism); Deferred (PQC work) | Standing watch item |
| P-29 | Performance Requirements | P2 | P-11 | Decided (targets); Open (load-tested reality) | First load test |
| P-30 | Reliability Requirements | P1 | P-15 | Open | Real operational data exists |
| P-31 | Deployment Guide | P2 | P-19,20 | Decided | Updated as paths are added |
| E-11 | Security Services | P3 | E-07 | Deferred | Standalone demand appears |
| E-22 | Sales Process | P2 | E-18 | Decided (objections); Open (certification target) | First real deal closes |
| E-23 | Marketing | P3 | E-19 | Deferred | Product-led data says otherwise |
| E-24 | Developer Relations | P2 | E-07 | Decided (function, not channel) | Ongoing, never closed |
| E-32/33/34/36 | Finance, HR, Vendors, Funding | P4 | — | Deferred | Each opens at its own concrete trigger (revenue, first hire, first vendor contract, first raise) — none assumed now |

---

## What this unlocks

Wave 1 is the only thing that should be worked on right now — specifically the Boundary Map and P-39/E-39, since everything else in Wave 1 was already effectively decided across the two blueprints and mostly needs confirming, not drafting. Wave 2 is where real engineering starts, and P-06/07/09/22 are still the four documents nothing else can safely build past.

The one thing this register cannot do is close Wave 4. That's the honest finding underneath all the reorganizing: the project's hardest questions were never a documentation problem, and no amount of restructuring the other 84 documents changes that.
