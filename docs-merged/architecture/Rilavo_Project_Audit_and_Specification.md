# Rilavo — Project Discovery, Audit & Specification

**Status: v0 wedge validated by this audit. Horizons 2–3 remain in discovery, deliberately.**

This document runs your audit framework against Rilavo as it currently stands and records what survives it — decisions, not options. It carries forward the corrected model from the prior strategy audit in this conversation: verification-first, product-funded, consumer-distributed rather than consumer-monetized, and decentralization treated as an engineering destination to build toward, not a claim to make early.

Where a section reaches a real decision, it's marked **Decision**. Where something is genuinely unresolved, it's marked **Open** — this document doesn't manufacture certainty just to fill a template.

**Contents:** 1. Project Identity · 2. The Problem · 3. Smallest Possible Rilavo · 4. What Rilavo Verifies · 5. Trust Model · 6. Protocol vs Product · 7. First Users · 8. Distribution Loops · 9. Anti-Delusion · 10. The $1 Question · 11. Revenue · 12. Developer's Position · 13. Solo-Founder Feasibility · 14. AI Coding Agent Audit · 15. What Must Never Be Built First · 16. Attack Surfaces · 17. Regulation Audit · 18. Success Planning · 19. Fork Test · 20. Company-Dies-Tomorrow Test · 21. Master Decision Tree · The Core Rilavo Audit

---

## 1. Project Identity: What Is Rilavo?

**In one sentence:** Rilavo is a protocol that lets anyone prove — instantly, and without exposing the underlying data — that a person, an AI agent, or a piece of content is what it claims to be.

**Without technical language:** Rilavo lets you prove you're real, without handing a company permanent proof of who you are.

**Before Rilavo:** verification is fragmented and adversarial. Every company builds its own weak version — passwords, CAPTCHAs, document uploads, manual review — and each one becomes a fresh fraud target and a fresh point of failure. There is no standard way to know whether an incoming AI agent is authorized to act.

**After Rilavo:** a single proof travels with the person, agent, or content across any participating system, checkable in real time, without the verifier needing to store what it just checked and without the prover needing to trust the verifier not to misuse it.

**Who immediately gets it:** fraud and trust-and-safety teams, platforms already drowning in bot and deepfake traffic, compliance officers doing KYC, engineers building agent-to-agent commerce who currently have no way to authorize an agent at all.

**Who doesn't care:** anyone whose current trust needs are already met by something low-stakes and working. This is expected, not a flaw — it's exactly why the wedge (§3) has to be a specific acute pain point, not an appeal to everyone.

**What Rilavo is, decisively — not "a combination of everything":**
1. At the core, a **verification protocol** — a shared way to make and check cryptographic claims.
2. Structurally, therefore, also a **network** of issuers and verifiers.
3. Functionally, **security/identity infrastructure** for whoever builds on it.
4. Commercially, a **developer platform** (API/SDK) plus an **product product** (compliance, fraud, SLA).
5. Explicitly **not**, in its near-term form, a consumer product. Consumer-facing surfaces exist only as distribution for the protocol — see §10.

**The compression test:**
> Rilavo enables **an product, platform, or receiving system** to safely **verify that a human, AI agent, or piece of content is authentic** without having to **collect, store, or become liable for the underlying personal data.**

**Decision:** This passes the compression test cleanly. Rilavo is a protocol first, a network second, and a product (developer platform + product service) third — in that order of what it *is*, not what it earns money from.

---

## 2. What Exact Problem Does Rilavo Solve?

Three concrete, non-abstract instantiations, not "trust is hard":

- **A — Fraud cost.** Products absorb rising losses and manual-review cost from synthetic identities and AI-generated documents, and most existing identity-verification vendors rely on the very artifacts (photos, selfies, videos) generative AI can now forge convincingly.
- **B — Agent authorization gap.** As AI agents start taking real actions on people's and companies' behalf, receiving systems have no standard way to know if an inbound agent request is authorized, by whom, or within what limits. They either block all agent traffic (losing legitimate business) or accept it blind (taking on liability). This is actively throttling agent-commerce pilots today.
- **C — Content provenance gap.** Publishers and platforms have no fast way to prove a specific image, video, or statement is or isn't AI-generated at the moment it matters, because provenance wasn't attached at creation time.

Each of these costs money (fraud, chargebacks, review headcount), costs time (manual review cycles), creates security risk (account takeover), legal risk (AML/KYC exposure), reputational risk, and already blocks transactions that would otherwise happen (agent-commerce pilots stalling on exactly this gap).

**Who experiences / suffers / pays — deliberately not the same entity:**
- *Experiences* it: the platform or product, which has to build ad hoc defenses.
- *Suffers* from it: the end customer whose identity is stolen, or the legitimate agent wrongly blocked, or the defrauded counterparty.
- *Pays* to solve it: the product's risk, compliance, or trust-and-safety budget.

This three-way split is healthy, not a problem — it's the normal shape of B2B security spend.

**The pain test, honestly applied:** existing point solutions exist (Persona, Onfido, Jumio for KYC; C2PA for content provenance; OAuth/API keys for agent access) — the gap isn't "nothing exists," it's that nothing unifies human, agent, and content verification under one portable, privacy-preserving standard, and most of these were built before generative AI made their underlying signals (photos, documents) forgeable at scale. Manual solving is possible and currently common (human review teams) — that's precisely the cost Rilavo removes. The problem is not yet universally "existential" — I should resist over-claiming that, since it was exactly the overclaim the prior audit flagged in the source material. It is: recurring, growing, and moving from optional toward operationally necessary in specific verticals now (agent authorization, high-fraud KYC), with the broader case strengthening every year AI and automation scale.

**Decision:** The wedge problem is **B — the agent-authorization gap.** It is newest, least served by incumbents, and most concretely urgent right now, without requiring Rilavo to out-compete entrenched KYC vendors on day one.

---

## 3. What Is the Smallest Possible Rilavo?

**Rilavo v0, defined:**

| Element | Definition |
|---|---|
| One user | A developer or business that needs to verify an inbound AI-agent request is authorized |
| One action | An API call made by an AI agent on behalf of a named principal (person or org) |
| One proof | A short-lived, signed token: "agent X is authorized by principal Y for action-class Z, issued at T, expires at T+n" — standard asymmetric-key signature (Ed25519), no ZK, no blockchain |
| One outcome | Receiving API accepts and logs the action, or rejects with a clear, machine-readable reason |

No blockchain, no zero-knowledge proofs, no decentralization, no token, no million users — all deliberately excluded (see §15 for why). Who performs the action: the agent or its platform. What it's proving: that it's acting within scope actually granted, not a fabricated one. Who verifies: the receiving service. Success: request proceeds with an auditable receipt. Failure: rejection with a specific, self-correctable reason (expired, scope mismatch, revoked, unknown issuer).

**Decision:** v0 needs one issuer (Rilavo, centralized on purpose), one verifier library, and one willing developer partner. Nothing on the "probably not the starting point" list is required. This is buildable in 30 days by one person with AI-assisted coding (§13).

---

## 4. What Does Rilavo Actually Verify?

Sequenced, not assumed all-at-once:

| Order | Category | Status |
|---|---|---|
| v0 | Is an AI agent authorized? | Building now |
| v0+ | Has a credential been revoked / does it remain valid? | Ships with v0 — authorization is meaningless without it |
| Horizon 2 | Is an agent behaving within its permitted boundaries? | Natural extension once scope-based tokens exist |
| Horizon 3 | Is a human real? | Deferred — highest stakes, highest regulatory exposure; needs edge-compute privacy architecture in place first |
| Horizon 3 | Is content human-made or AI-generated? | Deferred — needs creation-time tooling partnerships, not just an API |
| Horizon 4 | Is a device authentic? Is software untampered? | Deferred — partly served already by TPM/Secure Enclave attestation; revisit only if a partner needs it |
| Horizon 4 | Is an organization legitimate? Did an event happen? | Deferred — needs multi-party corroboration; likely requires federation to already exist |

For the v0 category — claim / sign / verify / liable: the claim is created by the principal granting scope; it's signed by Rilavo's issuance service at v0 (moving to client-side principal signing later); it's verified statelessly by whichever system receives the agent's request. **Open:** liability allocation (issuer vs. principal vs. verifier when a proof is wrongly issued or wrongly accepted) is a real gap needing contractual terms of service and likely insurance — not yet solved, and flagged honestly rather than assumed away.

**Decision:** Build only the top two rows now. Every category below the line is explicitly out of scope until it independently passes the Core Rilavo Audit (see closing section).

---

## 5. What Is the Trust Model?

**Who can issue proofs:** at v0, only Rilavo — a disclosed, deliberate centralization, not hidden. **Can anyone become an issuer:** not initially; a malicious issuer can mint fake credentials that damage the whole graph's credibility, which argues for a vetted allow-list, not permissionless issuance, until reputation and removal mechanisms exist. **Who approves issuers:** Rilavo alone at v0, transitioning to a multi-stakeholder body once a concrete trigger fires (below). **Issuer reputation:** calculated from a track record — disputed/revoked proofs per issuer, verifier complaint rate — which is exactly the fraud-intelligence asset flagged as a durable moat in §9 and §19. **Can an issuer be removed, and can that be abused:** yes to both; abuse risk is exactly why removal power needs to leave a single company's hands as the network scales (§12).

**If Rilavo itself is compromised:** at v0, a signing-key compromise is catastrophic for everything issued under it — which is precisely why v0 is scoped to short-lived, revocable, low-stakes credentials (hours, not years) rather than something like a permanent identity claim. This is an architectural argument, not just a caution.

**Can the network survive without the company:** honestly, no, not yet. v0 is a centralized service using unusually disciplined hygiene (short-lived credentials, public audit logs, an open verification standard) as a stepping stone toward federation — not a decentralized network wearing decentralized vocabulary it hasn't earned.

**Decentralization trigger — stated once, reused everywhere in this document:**
> No single issuer, including Rilavo itself, holds a majority of proof-issuance volume.

**Decision:** v0 is centralized and says so plainly. The trigger above is the one and only condition that starts the governance transition described in §12.

---

## 6. Protocol vs Product

**Must stay open:** credential format, verification standard, revocation-check mechanism (ideally a public, append-only, hash-chained log — not dependent on Rilavo's servers being up), core API/SDK interfaces, and eventually node-to-node communication once more than one issuer exists.

**Can stay closed without violating the open promise:** the specific fraud-signal models used to flag suspicious issuance, and the operational infrastructure itself. Being closed here isn't a compromise — operational excellence isn't what draws regulatory fire; access-point control is.

**Can another company build a compatible verifier?** Yes — actively encouraged; a competing verifier speaking the same format is how a protocol becomes a standard. **Can another company run infrastructure?** Yes, in the target end-state, not at v0 (the format needs to survive contact with real production traffic before it's frozen for multi-operator use). **Can users leave without losing credentials?** This must be a day-one commitment even while centralized: credentials are exportable and principal-held, not something that only exists inside Rilavo's database — otherwise "can the protocol survive if Rilavo disappears" (§20) never gets a real answer.

**What the company sells:** managed infrastructure, product APIs, fraud intelligence, compliance tooling, SLA-backed uptime, incident response, developer tooling (see §11 for the full breakdown).

**The equilibrium answer:** the format being open is exactly what makes products willing to depend on Rilavo at all — nobody builds critical infrastructure on a black box they can be locked into. What's actually hard to reproduce, and therefore worth paying for, is uptime at scale, accumulated fraud-pattern intelligence, audit-ready compliance packaging, and integration convenience. This is not a tension to resolve later; it's the design.

**Decision:** Format, standard, revocation log, and core API contracts are open from day one, even while operated by one company. Infrastructure, intelligence, and compliance packaging are the paid product.

---

## 7. Who Uses Rilavo First?

**User zero:** teams building AI-agent products currently throttled or blocked by APIs that don't trust unauthenticated agent traffic — an early agent-commerce startup, an internal automation team wiring agents to vendor payments, a marketplace piloting agent-driven purchasing. Findable via agent-framework developer communities, hackathons, and direct outreach — no paid advertising required, because this is a technical, high-intent audience already discussing the exact pain in public. What they use now: nothing standardized — ad hoc API keys, IP allowlisting, manual vetting, or outright blocking. What flips the switch: a drop-in SDK that turns "we manually vet every agent integration" into "any agent with a valid Rilavo proof is automatically scoped and auditable."

**User one hundred:** this is a genuine two-sided loop, not referral marketing. Once one platform requires or accepts Rilavo proofs for inbound agent traffic, every developer whose agent wants to reach that platform now has a mechanical reason to integrate issuance. B's adoption creates A's reason to adopt.

**User one million:** onboarding must be self-serve (docs + SDK + sandbox, no sales call for the default tier); verification must be fully automatic (no manual review in the verification path — only, if anywhere, in issuer approval); integration must not require ever speaking to Rilavo for base usage. This is a concrete commitment, not an aspiration — it's the difference between a protocol and a sales-led product.

**Decision:** Bootstrap through Loop A/B (below) with agent-tooling developers; do not build a sales-led product motion until self-serve usage has already proven the model.

---

## 8. How Does Rilavo Distribute Itself?

**Loop A — Verification loop.** B verifies a proof without creating an account (any friction here kills the loop at the exact moment it would otherwise spread). Once B has verified enough incoming proofs to trust the model, B has a direct incentive to become an issuer itself for its own downstream partners — this is the actual network-effect engine, not marketing.

**Loop B — Developer loop.** SDK is free; integration takes minutes, not days — a hard requirement, not an aspiration. Every integration adds a verifier and expands where a proof is useful: a textbook multi-sided effect.

**Loop C — Organization loop.** Once Company A requires Rilavo verification from Company B, B has a reason to push the same requirement onto its own suppliers if it wants to pass verified status downstream. Real, but slower and more sales-dependent than A/B — not purely self-propagating.

**Loop D — AI-agent loop.** The sharpest loop, and it's the one the v0 wedge is built around: if a receiving system requires a Rilavo proof, every agent framework that wants its agents to actually work against that system must integrate issuance — entirely machine-to-machine, no human signup flow required beyond initial developer registration. This scales with agent adoption itself, which is growing independent of Rilavo.

**Decision:** Loops A and B bootstrap v0. Loop D is the primary long-run growth engine — fully automatable and riding a trend Rilavo doesn't have to create. Loop C is a secondary, slower channel for product expansion once A/B/D are proven.

---

## 9. Why Choose Rilavo Over an Existing System?

For the agent-authorization wedge specifically: alternatives are OAuth/API-key allowlisting (no fine-grained, auditable, revocable scope designed for autonomous non-human callers) and homegrown internal vetting (doesn't interoperate across companies — everyone rebuilds the same thing alone). The difference isn't purely technological — OAuth could theoretically be extended — it's that no one has built a cross-company, portable standard for this specific problem, and that requires coordination, not just code.

**Can a big company copy this in six months?** The code, easily. What they can't copy: an installed base of verifiers who already accept the format, an issuer-reputation track record, and the cold-start problem they'd have to re-run from zero.

**What becomes harder to reproduce after five years — to be demonstrated, not assumed:** issuer reputation history; accumulated fraud-pattern intelligence specific to agent-authorization abuse (a genuinely new attack surface no one else has years of data on yet); standing with standards bodies; integration density inside the agent frameworks developers already use. **Open, honestly:** Rilavo has zero of these on day one. Integration density and fraud intelligence compound fastest, because they accrue mechanically from usage. Standards legitimacy requires deliberate outside work and won't emerge from usage alone.

**Decision:** The moat is not the code, and it is not a license clause (see the GPLv3 correction in the prior audit) — it's the graph and the track record. Both take years and can't be shortcut.

---

## 10. The $1 Question

This section closes out — rather than reopens — the correction made in the prior strategy audit.

**$1 for what:** not a flat per-user annual fee. The product/developer layer is priced per verification event (small, usage-based, consistent with the original $0.001/query figure). The consumer-facing $1 is not the primary business model — it exists only as an optional, low-friction way for an individual principal to self-issue or maintain a personal credential, priced at roughly cost, not profit.

**Revenue or acquisition cost:** acquisition/distribution cost. Settled, not open.

**Cost to process the event:** near-zero at the margin once infrastructure exists, but not literally zero — server load, fraud monitoring, and support scale sub-linearly, not to nothing. The "zero marginal cost" framing from the original overview is a useful approximation, not a literal claim.

**Who absorbs fraud:** the issuer bears liability for a wrongly issued credential; the verifier bears the risk of accepting an invalid or expired proof it should have checked; Rilavo, as protocol operator, is contractually liable only for protocol-level failures such as its own key compromise. **Open:** this needs to become real terms-of-service language, not just a stated principle.

**At 1M vs. 1B transactions:** at 1M, unit economics are dominated by fixed engineering cost, which is normal. At 1B+, real infrastructure investment starts to matter in a way "zero marginal cost" language obscures — and the product tiers need to already be profitable by then, because a consumer-only $1 model could never fund this scale.

**Would the user notice if $1 disappeared?** Mostly no — which is the point: fine as a near-invisible acquisition mechanic, not meaningful as revenue. **Would Rilavo still get used if product paid and consumers paid nothing?** Yes.

**Decision:** The $1 consumer charge is not the business model. It never survives this audit as a revenue line — only as a distribution mechanic.

---

## 11. Where Does the Real Revenue Come From?

| Layer | Why it exists this way |
|---|---|
| Free protocol | Free because adoption is the asset a metered core protocol could never reach — the format being free earns the right to sell everything built on it |
| Developer tools | Base SDK free; paid tier covers dashboards, staging/sandbox environments, priority support |
| API | Billable event = a verification call beyond a generous free tier — small per-call fee |
| Product | Replaces the cost of an internal build-vs-buy fraud/trust engineering decision; reduces fraud loss and review headcount directly — a real, already-budgeted expense |
| Compliance | Genuine requirement in finance, hiring, and health-adjacent verticals needing audit trails of who verified what, and when |
| Security | Prevents specific, quantifiable loss: account takeover, synthetic-identity onboarding, unauthorized agent financial action |
| SLA | Products putting verification in a live transaction path need uptime guarantees, because a Rilavo outage becomes their outage |
| Intelligence | Aggregated, privacy-preserving fraud-pattern signal, sold without exposing any individual's underlying data — the moat asset from §9, monetized |

**Decision:** Every row answers "who pays, from what existing budget, replacing what existing cost" — none rely on users deciding, out of nowhere, to buy abstract security. That's the test this section demands, and it's the one the original consumer-stamp line failed.

---

## 12. Where Does the Developer Stand?

Not a single static model — a sequence. **Start as Model A** (founder owns code, infrastructure, direction, and customer relationships) because v0 needs speed and unambiguous ownership, and no team can run a standards process before there's a standard worth governing. **Model B describes the transition itself,** not a separate end-state. **Target Model C/D** — infrastructure operator on top of an increasingly independently governed protocol — once the decentralization trigger from §5 fires.

Pure Model D from day one would be premature-decentralization theater with nothing yet to coordinate. Staying in Model A forever would falsify the open-protocol commitment made in §6.

**Powers the founder should retain early:** control of the reference implementation, ability to set initial issuer standards, ability to move fast on security patches.

**Powers the founder should never have, even early:** unilateral, undisclosed control over credential portability (must remain exportable even while centralized — a hard line, not a someday feature), and unilateral removal of a participant without a documented, appealable process.

**If the founder disappears at v0:** the network mostly stops — matches §20's category 1. Acceptable now, specifically because v0's stakes are small (short-lived tokens, not permanent identity). Unacceptable once verification categories expand, which is exactly why decentralization work needs to be underway well before that expansion, not after.

**Is decentralization technically necessary, or ideological, right now?** Mostly not technically necessary at v0 scale. It becomes necessary once stakes outgrow what a single point of failure can respectably hold, or once regulatory exposure (§17) makes "no single entity controls this" a load-bearing legal position rather than a narrative. Preparing early is far cheaper than retrofitting under pressure.

**Decision:** Model A now, Model C/D as the explicit target, triggered by the same issuer-concentration threshold defined in §5 — not by a vague "eventually."

---

## 13. Can One Person Actually Build Rilavo?

**Yes, for v0 as scoped in §3** — landing page, SDK, API, proof prototype using standard signature schemes, database, auth, dashboard, one verification workflow, docs, a couple of pilot integrations. This is deliberately true *because* v0 excludes exotic cryptography, blockchain, and decentralization — that exclusion is what makes solo feasibility real rather than aspirational.

**What AI coding agents accelerate well:** boilerplate, frontend, backend scaffolding, tests, docs, infra config, SDK generation, debugging.

**What AI cannot safely replace:** security architecture, cryptographic design validation, threat modeling, production security review, legal strategy, business discovery, deciding what should exist. Even using standard signature schemes correctly has real failure modes — key management, expiry handling, replay protection — that deserve a qualified human security review before this touches any real liability-bearing transaction. **Decision:** that review is a required gate before v0 moves from pilot to a paying product customer, not an optional nice-to-have.

**Development principle, operationalized:** the irreversible decisions at v0 are the credential format and the initial trust/liability terms — changing either later breaks every integrator. Those get the most upfront rigor. Everything reversible (database choice, frontend framework) shouldn't block starting.

---

## 14. The AI Coding Agent Development Audit

**Architecture decisions:** stay with the human founder/technical lead, always. Agents implement against a spec a human already approved; they don't originate irreversible structural decisions. **Code generation:** any capable agent, scoped to an already-specified task. **Review:** the founder (or a designated reviewer once a team exists), with mandatory human eyes on anything touching issuance or verification. **Vulnerability detection:** automated scanning plus the mandatory human security review from §13 before anything liability-bearing ships. **Source of truth:** the artifacts below — this is exactly why they exist.

Rilavo needs, as living documents, not one-time deliverables:
1. **Product specification** — this document is an early version of it.
2. **Architecture specification** — the §3–§6 decisions, formalized.
3. **Threat model** — §16, formalized and kept current.
4. **API contracts** — the credential format frozen for v0, versioned thereafter.
5. **Test requirements** — especially replay, expiry, and revocation edge cases.
6. **Security rules** — no custom cryptography, mandatory review gate, key-management standards.
7. **Decision log** — every entry marked **Decision** in this document, appended to as new ones are made.

**Decision:** Without all seven maintained as living artifacts, coding agents will build fast and build an incoherent system. This document covers 1, 2, and part of 3 and 7. The rest need to exist before code-writing begins in earnest.

---

## 15. What Must Never Be Built First?

| Technology | Needed for v0? | The real trigger to revisit |
|---|---|---|
| Blockchain | No | Multiple mutually-distrusting issuers need consensus without a shared operator |
| Cryptocurrency / token | No — actively avoid | Nothing in this model requires one; adds securities/regulatory risk for no functional gain, and invites a crypto-scam narrative the trust pitch doesn't need |
| Custom cryptography | No — never | No problem here requires new primitives; use standard, audited signatures only |
| Zero-knowledge proofs | No | A verifier must confirm a claim without learning the underlying data (e.g., age without birthdate) — Horizon 3 |
| Decentralized consensus | No | Same trigger as blockchain |
| Mobile applications | No | A genuine consumer-facing product exists — not the near-term focus |
| Custom hardware | No — avoid indefinitely | Integrate existing secure-enclave standards if device attestation is ever needed |
| Global identity verification | No | This is the Horizon-3 "is a human real" ambition, deliberately sequenced later |
| DAO | No | Governance decentralization (§12) is achieved by a multi-stakeholder foundation, not a DAO specifically |
| International expansion | No | The v0 wedge isn't jurisdiction-bound the way consumer identity is |

**Decision:** everything in this table stays out until its specific trigger fires. None are needed to ship or sell v0.

---

## 16. What Are the Attack Surfaces?

| Attack | Exposure at v0 | Mitigation |
|---|---|---|
| Fake identity creation | Low — v0 asserts no open identity claim | Deferred to Horizon 3 by design |
| Stolen / copied credential | Real, but bounded | Short-lived, scoped tokens limit the damage window |
| AI impersonating a user | The central threat the project exists to prevent | First-class threat-model scenario, not an afterthought |
| Replay of a valid proof | Real | Expiry + single-use nonce, required in the format |
| Malicious verifier tracking users | Real once many verifiers exist | Proofs reveal scope only, not full principal identity, wherever possible |
| Compromised issuer | Serious | Small vetted issuer set, public audit logs, revocation authority |
| Correlating "private" activity | Real if credentials are reused | Support per-relationship / per-session credentials, not one static identifier |
| 51%-malicious equivalent (no blockchain) | Not yet applicable — one issuer | Becomes: no single issuer, including Rilavo, may hold majority proof-issuance share |
| Government or platform abuse as a chokepoint | The most serious item on this list | See below |

**The most damaging thing that could happen if Rilavo succeeds:** not a technical breach. If Rilavo becomes the de facto way agents — and eventually humans — prove who they are across the economy, the worst failure mode is Rilavo, or a captured/coerced version of it, becoming a chokepoint used to selectively deny participation or de-anonymize people after the fact. This has to shape architecture from day one: minimize what any single verification reveals, keep removal power subject to a documented, appealable process (§12), and keep the format open enough that no single operator — including a future, larger Rilavo — is ever a mandatory, permanent chokepoint.

---

## 17. The Regulation Audit

Not "how do we avoid regulators" — what could they reasonably object to, and how does the architecture legitimately reduce it.

**Does Rilavo need to know who the user is?** For v0, no — it needs to know a valid principal authorized a valid agent for a valid scope, without holding a persistent identity record of the underlying human. **Can it verify without storing identity?** Yes, by design, for v0. This gets harder but must remain a hard requirement once "is a human real" (Horizon 3) enters scope, given how much regulatory and reputational risk sits specifically in biometric data retention. **Can data stay local?** Yes — at Horizon 3, edge-computed proofs become the load-bearing design choice specifically to avoid becoming a biometric honeypot. **Can credentials be revoked, can users leave, can competitors interoperate?** Yes to all three — already decided in §6 and §12.

**Does Rilavo control access to an essential market? Could it become an unavoidable gatekeeper?** Honestly, yes — this is the real long-run risk, and it shouldn't be softened. If the agent-authorization standard succeeds as hoped, "does this agent have a valid Rilavo proof" could become as load-bearing as "does this site have a valid TLS certificate" — exactly the essential-access-point position that triggers gatekeeper-style regulation regardless of how open or privacy-preserving the underlying tech is. The response isn't to avoid succeeding. It's to already be doing, voluntarily, what a gatekeeper regime would eventually require — interoperable verifiers, portable credentials, no exclusivity — so that a future designation changes nothing operationally.

**Decision — the distinction this section explicitly demands:** *privacy decentralization* (edge compute, no central data store) protects against breaches and government data demands. *Market decentralization* (multiple independent operators, no single dominant issuer) protects against antitrust and gatekeeper exposure. Rilavo has a real, concrete plan for the first (§4, §17 above) and only a triggered intention for the second (§5, §12). Conflating the two was the central mistake identified across most of the comparison answers in the prior audit, and this document does not repeat it.

---

## 18. What Happens If Rilavo Becomes Successful?

- **10,000 users:** what breaks first — the manual, ad hoc parts of the pipeline: issuer review (if still human-gated), support, incident response processes that were fine informally across a handful of pilots.
- **1 million users:** what becomes expensive — infrastructure and on-call burden, and this is the first point where the fraud/cost answers from §10 get tested against real numbers. What becomes legally complicated — this is roughly the scale at which "are we now a critical vendor multiple products depend on for a compliance-relevant function" starts mattering, meaning liability, insurance, and SLA terms need real legal investment, not boilerplate.
- **100 million users:** does one company still control infrastructure — under the plan as decided, it shouldn't. If it still does at this scale, that's a signal the decentralization trigger (§5) was set too late or not honored, not a reason to redefine the trigger after the fact.
- **Global adoption:** governance sits with the multi-stakeholder body from §12, not the founding company alone. Countries and competitors can run compatible, interoperable infrastructure by the open-protocol commitments already made in §6. The founder cannot make unilateral changes at this stage — a hard "no," closing the loop from §12's "powers the founder should never have."

---

## 19. The "Fork Test"

If a trillion-dollar company copies every line of code tomorrow, what can't be copied: accumulated issuer reputation and fraud-pattern intelligence from real observed abuse, the installed base of verifiers who already trust and have integrated the format (a copy starts with zero verifiers, and a proof format only has value if someone accepts it), and any standing already earned with actual standards bodies.

**Decision:** the moat is explicitly not the code — reinforcing the GPLv3 correction from the prior audit. Even fully closed-source code wouldn't be the real moat; clean-room reimplementation of a known, public spec is straightforward for a well-resourced competitor. What's hard to copy is the trust graph, not the software, and that only accrues through years of real usage — which is why §7–§9's sequencing (bootstrap real usage before chasing scale) matters more than any code or license decision.

---

## 20. The "Company Dies Tomorrow" Test

Answered honestly by horizon, not as one static claim:

**Today, at v0:** closest to category 1/2 — issuance stops, since the issuer is centralized. But because credential export and portability were made a hard requirement in §6/§12, users retain their existing valid credentials until natural expiry — meaningfully better than pure category 1, even at this early stage.

**Target end-state,** once the §5 decentralization trigger has fired: category 4 — the protocol and other operators continue; only Rilavo's specific commercial layer (its fraud intelligence, SLAs, compliance tooling) disappears with the company. This is the explicit goal, not the current reality, and the gap between the two is measured exactly by whether the trigger has fired yet — a checkable fact, not a vibe.

**Decision:** Rilavo is trying to become category 4. It is currently category 1/2 with the portability groundwork already laid so the transition is additive engineering, not a rewrite.

---

## 21. The Rilavo Master Decision Tree

| Stage | Core question | Decision reached |
|---|---|---|
| 1 — Reality | Painful problem, who pays | Agents acting across company boundaries with no portable authorization proof; products absorb the cost (§2) |
| 2 — Wedge | Smallest useful product, first 10 users | Signed, short-lived agent-authorization token; reached via developer communities building agentic tooling, no paid ads (§3, §7) |
| 3 — Mechanics | What's created, issued, verified | A scoped authorization proof, issued by Rilavo (v0) on a principal's instruction, verified statelessly by the receiving system (§3, §4) |
| 4 — Network | Why usage compounds | Loop A (verification) + Loop D (AI-agent): every verifier that accepts the format makes issuance more valuable, and vice versa (§8) |
| 5 — Architecture | Protocol vs. product, centralization | Format, standard, and revocation open; infrastructure, intelligence, and compliance proprietary; centralized issuer at v0, disclosed (§5, §6) |
| 6 — Economics | Free, $1, real revenue | Core protocol and SDK free; usage-based product/API pricing is the real revenue line; $1 consumer layer is acquisition cost, not revenue (§10, §11) |
| 7 — Defensibility | Why it can't just be copied | Issuer reputation, fraud-pattern intelligence, verifier installed base, standards legitimacy — none exist on day one; all must be earned (§9, §19) |
| 8 — Founder feasibility | What one person can build | The full v0 scope, AI-assisted, with a mandatory human security review gate before production use (§13, §14) |
| 9 — Scale | What happens if it succeeds | Governance and issuer concentration must decentralize before Rilavo becomes either a single point of failure or an unavoidable access point (§12, §17, §18) |

---

## The Core Rilavo Audit

1. **What must the world do anyway?** Let increasingly agentic software act on people's and companies' behalf across organizational boundaries. This is happening regardless of Rilavo.
2. **Why is it currently difficult, expensive, insecure, or impossible?** No portable, standard way exists to prove an agent's authorization. Every company either rebuilds ad hoc trust or blocks agent traffic outright — both costly.
3. **What is the smallest piece of infrastructure that makes it easier?** The v0 signed, short-lived, scoped agent-authorization proof — verifiable via a public key and a revocation check. No blockchain, no ZK, no token.
4. **Why does every new use make Rilavo more valuable to the next user?** Every verifier that accepts the format makes issuance more valuable; every issuer expands what a verifier can trust. This compounds mechanically (§8), not through marketing.
5. **If copied, the founder leaves, competitors appear, and regulators investigate — what remains?** The accumulated issuer-reputation and fraud-pattern graph, the installed base of verifiers already depending on the format, and — once the decentralization trigger has fired — a protocol that structurally survives its founding company by design, not by promise.

**Verdict:** v0, as scoped throughout this document, has strong, specific answers to all five questions and is ready to leave discovery for development. Horizons 2–4 — human identity, content provenance, device/organization attestation, and full federation — do **not** yet have equally strong answers to all five, and stay in discovery, run through this same audit independently, rather than being built in parallel with v0 out of ambition.
