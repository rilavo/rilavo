# RILAVO — MOTHER AUDIT & BLUEPRINT QUESTION BANK

**Document Type:** Master / Mother Specification Question Bank  
**Project:** Rilavo  
**Purpose:** Generate, challenge, validate, and maintain the two primary Rilavo project trees:

1. **Rilavo Protocol Tree** — the open verification protocol, standards, network, technical architecture, governance, security, deployment, interoperability, and evolution.
2. **Rilavo Product Tree** — the commercial company, products, services, operations, distribution, revenue, customer value, proprietary capabilities, competitive strategy, governance, and survival model.

**Critical instruction:** This document is an **audit instrument, not an answer document**. It must ask questions before decisions are recorded. No question should be marked “answered” merely because an attractive assumption exists. Every material answer must be evidenced, tested, assigned an owner, and linked to the sectional document where the resulting decision belongs.

---

## 0. HOW THIS MOTHER DOCUMENT MUST BE USED

The Rilavo project already has a working strategic direction: verification-first, an agent-authorization wedge for v0, product-funded economics, a free/open protocol layer, and deliberate progression from initial centralization toward multi-operator governance. The existing specification explicitly separates the protocol from the commercial layer and identifies seven living artifacts required for disciplined AI-assisted development. fileciteturn3file0L121-L137 fileciteturn2file0L11-L20

This mother document does **not** replace those decisions. It asks what must be answered before each decision can become a durable blueprint, and what must be re-audited when conditions change.

### 0.1 Required answer record for every material question

For each question, the eventual project response should record:

- **Question ID**
- **Answer**
- **Evidence / source**
- **Confidence:** Confirmed / Strong evidence / Working assumption / Unknown
- **Decision:** Decision / Open / Rejected / Deferred
- **Owner**
- **Date answered**
- **Review date**
- **Affected Protocol documents**
- **Affected Product documents**
- **Dependencies**
- **Risks created or removed**
- **Test required**

### 0.2 Audit states

Every material question should eventually move through:

`UNASKED → ASKED → ANSWERED → EVIDENCED → TESTED → ACCEPTED / REJECTED / DEFERRED → SPECIFIED → IMPLEMENTED → MONITORED`

### 0.3 Five rules

1. Do not answer architecture questions with marketing language.
2. Do not answer product questions with technology enthusiasm.
3. Do not answer security questions with “the cryptography prevents it” without threat-model evidence.
4. Do not answer network-effect questions with “viral” unless there is a concrete mechanism by which usage creates the next usage.
5. Do not answer survivability questions with “the protocol is open” until the exact economic reason for the product's continued existence is demonstrated.

---

# PART I — RILAVO AS A TWO-SYSTEM CONCEPT

## 1. IDENTITY OF THE TWO THINGS

### 1.1 What is Rilavo the protocol?

- What is the protocol in one technically precise sentence?
- What is it in one sentence understandable by a non-technical executive?
- What does the protocol allow that was difficult, expensive, unsafe, or impossible before it existed?
- What is the smallest atomic function the protocol performs?
- What is the exact claim being created?
- Who creates the claim?
- Who signs the claim?
- Who receives the claim?
- Who verifies the claim?
- What is the minimum information a verifier needs?
- What information must the verifier never need?
- What does the protocol guarantee?
- What does it explicitly not guarantee?
- What does the protocol mean by “verification”?
- What does “authorization” mean within Rilavo?
- What does “identity” mean within Rilavo?
- What does “authenticity” mean within Rilavo?
- What does “provenance” mean within Rilavo?
- Are these distinct claim classes or one unified model?
- What is common between agent, human, content, device, and organizational verification?
- What must remain different between them?

### 1.2 What is Rilavo the product?

- What exactly does the company called Rilavo sell?
- Why must the company exist if the protocol can function without it?
- Which capabilities are commercial services rather than protocol functions?
- Which capabilities require operating a service at scale?
- Which capabilities require a legal entity?
- Which capabilities require insurance?
- Which capabilities require humans?
- Which capabilities can be automated?
- What would an product customer purchase from Rilavo that it cannot obtain simply by downloading the protocol?
- Why would a company pay Rilavo instead of operating the protocol itself?
- What is the product's strongest economic reason to exist?
- What is the product's weakest economic assumption?
- What would remain valuable if all commercial Rilavo APIs became commoditized?
- What would disappear if Rilavo Product disappeared tomorrow?
- What would continue if Rilavo Product disappeared tomorrow?

### 1.3 What must never be confused?

- Which responsibilities belong only to the protocol?
- Which responsibilities belong only to the product?
- Which responsibilities are shared?
- Which responsibilities must be independently governed?
- Which assets may be proprietary?
- Which assets must remain interoperable?
- Which data may the product hold?
- Which data must never become an product-controlled dependency?
- Which permissions can Rilavo Product grant?
- Which permissions can only the protocol governance layer grant?
- Can Rilavo Product change the protocol unilaterally?
- Can a protocol participant be excluded by the product?
- If yes, under what authority?
- If no, how is abuse handled?

---

# PART II — THE MOTHER QUESTION TREE FOR THE PROTOCOL

# 2. PROTOCOL PURPOSE AND EXISTENCE

- Why should this protocol exist at all?
- What concrete problem must exist before the protocol becomes necessary?
- What event in the world makes the protocol valuable?
- What happens if the protocol never exists?
- Who currently performs the protocol's function manually?
- Who performs it using fragmented software?
- Why are existing standards insufficient?
- Which parts of the problem are genuinely unsolved?
- Which parts are already solved by OAuth, API keys, C2PA, existing identity standards, platform-specific mechanisms, or capability systems?
- What does Rilavo unify?
- What does Rilavo deliberately leave to existing standards?
- Is Rilavo a replacement, an extension, a compatibility layer, or a new standard?
- What existing standard must Rilavo interoperate with on day one?
- What must Rilavo never attempt to replace?

## 3. PROTOCOL WEDGE AND SCOPE

- What is Rilavo v0 exactly?
- What is one user?
- What is one action?
- What is one proof?
- What is one verification outcome?
- Why is agent authorization the first wedge?
- What evidence confirms the wedge is actually painful?
- Which alternative solutions are available today?
- Why would a developer not simply continue using OAuth or an API key?
- What exact friction does Rilavo remove?
- How many integration steps does the first implementation require?
- What is the maximum acceptable integration time?
- What is explicitly excluded from v0?
- What would cause an excluded capability to re-enter scope?
- What is the minimum production-grade feature set?
- What feature would create unnecessary complexity without increasing initial value?
- What feature is tempting but strategically premature?
- What must be proven before Horizon 2 begins?
- What must be proven before Horizon 3 begins?
- What must be proven before federation begins?

The current research explicitly treats v0 as a narrow agent-authorization transaction and intentionally excludes blockchain, ZK, decentralized consensus, tokens, and custom cryptography at genesis. fileciteturn3file1L401-L428

## 4. PROTOCOL USERS, ACTORS, AND ROLES

Identify every role and ask:

- Who is the principal?
- Who is the agent?
- Who is the issuer?
- Who is the verifier?
- Who is the relying party?
- Who is the subject of the claim?
- Who controls the credential?
- Who holds the private key?
- Who can delegate authority?
- Who can attenuate authority?
- Who can revoke authority?
- Who can dispute a claim?
- Who can audit a claim?
- Who can observe the event?
- Who can correlate events?
- Who can appeal a decision?
- Who can remove an issuer?
- Who can change the standard?
- Who can upgrade software?
- Who can shut down an operator?
- Who can replace an operator?
- Who is liable when a false authorization is accepted?
- Who is liable when a valid authorization is rejected?
- Who is liable when a credential is stolen?
- Who is liable when an issuer is compromised?

## 5. PROTOCOL TERMINOLOGY AND SEMANTICS

Define every term before it appears in a specification.

- What exactly is an agent?
- What qualifies as an AI agent versus an ordinary service account?
- What exactly is a principal?
- What is an identity?
- What is a credential?
- What is a proof?
- What is an authorization?
- What is an authentication event?
- What is a delegation?
- What is an attenuation?
- What is an issuer?
- What is an operator?
- What is a verifier?
- What is a trust relationship?
- What is an issuer reputation?
- What is provenance?
- What is a revocation?
- What is an expiry?
- What is a nonce?
- What is an audit receipt?
- What is a verification event?
- What is an invalid proof?
- What is an unverifiable proof?
- What is a fraudulent proof?
- What is an expired proof?
- What is a revoked proof?
- What is an unknown issuer?
- What is an attenuated proof?
- What is a root proof?
- What is a sub-agent proof?

## 6. PROTOCOL VALUE PROPOSITION

- What does a verifier gain?
- What does an issuer gain?
- What does an agent gain?
- What does a principal gain?
- What does a developer gain?
- What does an product gain?
- What does a regulator gain?
- What does the ecosystem gain?
- What does the protocol make cheaper?
- What does it make faster?
- What does it make safer?
- What does it make interoperable?
- What does it make possible that previously required bespoke integration?
- What does it remove from the receiving system's liability surface?
- What does it add to the receiving system's obligations?

## 7. PROTOCOL MECHANICS — END TO END

- What happens before an agent requests authorization?
- How does the principal grant authority?
- Where is authority recorded?
- How is authority represented?
- How is the agent bound to the authority?
- How is the action scope represented?
- How is time represented?
- How is audience represented?
- How is the request bound to a particular receiving service?
- How is replay prevented?
- How is duplication detected?
- How is expiry enforced?
- How is revocation discovered?
- How does a verifier obtain issuer keys?
- How does a verifier know it is using the correct key?
- What happens when the verifier is offline?
- What happens when the revocation system is unavailable?
- What is fail-open versus fail-closed behavior?
- When is each appropriate?
- What happens when clocks disagree?
- What happens when an issuer key rotates?
- What happens when the token format changes?
- What happens when the agent changes identity mid-session?
- What happens when a principal withdraws authority?
- What happens when an agent delegates?
- What happens when a sub-agent delegates again?
- What prevents authority expansion through delegation?

## 8. PROTOCOL CREDENTIAL DESIGN

- What is the canonical credential structure?
- Which fields are mandatory?
- Which fields are optional?
- Which fields are public?
- Which fields are confidential?
- Which fields are hashed?
- Which fields are signed?
- Which fields are derived?
- Which fields identify the issuer?
- Which fields identify the principal?
- Which fields identify the agent?
- Which fields identify the resource?
- Which fields identify the action?
- Which fields define time?
- Which fields define budget?
- Which fields define domain?
- Which fields define tools?
- Which fields define delegation depth?
- Which fields define context?
- Which fields define revocation status?
- Which fields define assurance level?
- What must be impossible to alter without invalidating the credential?
- What can be transformed while preserving validity?
- What information should never be encoded because it creates surveillance risk?

## 9. CRYPTOGRAPHIC QUESTIONS

- Which standard cryptographic primitives are used?
- Why is each primitive necessary?
- Why is it preferable to alternatives?
- What assumptions does it rely upon?
- What are the implementation risks?
- What is the key generation process?
- Where are private keys generated?
- Where are private keys stored?
- Who can access private keys?
- How are issuer keys rotated?
- How are keys revoked?
- How are keys backed up?
- How are compromised keys quarantined?
- What happens when a key is lost?
- What happens when an issuer loses all keys?
- Which algorithms are acceptable?
- Which algorithms are forbidden?
- How is cryptographic agility handled?
- What is the migration path if the chosen primitive is weakened?
- What is the post-quantum migration strategy?
- Is post-quantum support actually needed at each horizon?
- What evidence is required before introducing a new cryptographic primitive?

The current research proposes standard Ed25519 signatures for v0 and explicitly prohibits custom cryptography at genesis. fileciteturn3file1L430-L450

## 10. AUTHORIZATION MODEL

- What exactly is being authorized?
- Authorization for what action, against what target, by what agent, under whose authority?
- Is authorization endpoint-based?
- Is it argument-level?
- Is it resource-level?
- Is it monetary?
- Is it time-limited?
- Is it geography-limited?
- Is it domain-limited?
- Is it tool-limited?
- Can authorization be one-time?
- Can authorization be reusable?
- What makes a request materially different from the authority granted?
- How is the “confused deputy” problem addressed?
- How is audience binding performed?
- How is subject binding performed?
- How is proof-of-possession performed?
- How is the agent prevented from presenting another agent's credential?

## 11. DELEGATION AND HORIZON 2

- Can an authorized agent delegate authority?
- Under what circumstances?
- What is the maximum delegation depth?
- How is depth encoded?
- How is attenuation enforced?
- Can a child grant more authority than its parent?
- Can a child extend expiry?
- Can a child increase budget?
- Can a child broaden tools?
- Can a child broaden domains?
- Can a child change the reason for delegation?
- Must every delegation contain context?
- How is context interpreted?
- Is context human-readable, machine-readable, or both?
- How is a sub-agent identified?
- Must every sub-agent have a unique ephemeral key?
- How long should sub-agent credentials live?
- How are chained delegations audited?
- Can a delegated agent prove the origin of its authority?
- Can a verifier inspect the full chain?
- Can a verifier verify only the final capability?
- What happens when one delegation block is invalid?
- What happens when a parent credential is revoked?
- What happens to descendants after revocation?
- What is the computational cost of verifying a long chain?
- What is the maximum acceptable chain length?

The research points toward capability attenuation, bounded depth, contextual delegation, ephemeral sub-agent grants, and progressively stronger attestation levels as Horizon 2 concepts; these remain questions to formalize into Rilavo-specific requirements rather than automatic adoption. fileciteturn3file1L474-L494

## 12. REVOCATION

- Who can revoke?
- What can be revoked?
- Can a principal revoke authority directly?
- Can an issuer revoke credentials it issued?
- Can a verifier mark an issuer as untrusted?
- Is revocation global or relationship-specific?
- How quickly must revocation propagate?
- What is the maximum acceptable revocation delay?
- Can the protocol function without real-time revocation?
- What is the role of expiry compared with revocation?
- Is there an append-only revocation log?
- Who hosts it?
- Can multiple operators host copies?
- Can revocation logs be independently audited?
- What happens if a log is unavailable?
- What happens if an issuer falsely revokes a credential?
- What appeal exists?
- What is the difference between credential revocation and issuer suspension?

## 13. AUDIT RECEIPTS AND NON-REPUDIATION

- What exactly is logged when verification succeeds?
- What exactly is logged when verification fails?
- Who owns the log?
- Who can read it?
- Can the log expose personal data?
- How is a receipt cryptographically bound to the request?
- Can a verifier prove later that it verified a credential?
- Can a principal prove later what authority was granted?
- Can a verifier deny having accepted a proof?
- Can a malicious verifier fabricate an audit trail?
- Can two systems produce conflicting records?
- Is there a canonical timestamp source?
- How are logs retained?
- How are logs deleted where required by law?
- Can deletion coexist with cryptographic auditability?

## 14. PRIVACY ARCHITECTURE

- What personal data does the protocol require?
- What personal data does it avoid?
- What personal data can appear in a credential?
- What personal data can appear in logs?
- Can proofs be relationship-specific?
- Can proofs be unlinkable?
- Can two verifiers collude to identify the same principal?
- Can Rilavo correlate activity across verifiers?
- Can an issuer correlate all uses of its credentials?
- Can a verifier infer more than the claim requires?
- What is the minimum disclosure principle?
- Which claims can be proven without revealing raw attributes?
- What becomes possible once ZK proofs are introduced?
- What are the performance costs of ZK?
- What are the operational costs of ZK?
- What legal or product requirement would justify moving to ZK?
- What data residency requirements apply?
- What right-to-erasure obligations could conflict with immutable logs?

## 15. DATA ARCHITECTURE

- What data exists in the protocol?
- Where is each category stored?
- Is storage mandatory or optional?
- What can be computed at the edge?
- What can be computed locally by the principal?
- What can be computed locally by the agent?
- What can be computed locally by the verifier?
- Which data is ephemeral?
- Which data has a retention period?
- What data is globally replicated?
- What data is jurisdiction-specific?
- What data can be deleted?
- What data must survive for security?
- How are data minimization requirements expressed as protocol rules rather than policy statements?

## 16. NETWORK TOPOLOGY

- What is a node?
- What does a verifier operate?
- What does an issuer operate?
- What does an auditor operate?
- What is the minimum network topology at v0?
- What changes at v1?
- What changes when multiple issuers exist?
- Does the network require consensus?
- If not, why not?
- If yes, what exact problem requires it?
- How are public keys distributed?
- How are trust anchors distributed?
- How are issuer directories discovered?
- Is discovery centralized, federated, or distributed?
- What happens when two issuer directories disagree?
- Can a country run its own operator?
- Can a company run an independent operator?
- Can a competitor run an independent operator?
- Can the network function across operators without Rilavo Product infrastructure?

## 17. DEPLOYMENT MODEL

- How is a verifier installed?
- How is an issuer installed?
- Is there a hosted deployment?
- Is there a self-hosted deployment?
- Is there an embedded SDK?
- Is there a sidecar?
- Is there a gateway?
- Is there a library?
- Is there an API service?
- What is the easiest deployment path?
- What is the most secure deployment path?
- What is the highest-scale deployment path?
- What is the smallest deployment a solo developer can run?
- Can verification happen offline?
- Can issuance happen offline?
- What requires a network connection?
- What happens during Rilavo infrastructure outage?
- What happens during DNS failure?
- What happens during key-directory failure?
- What happens during revocation-service failure?
- What does graceful degradation look like?

## 18. SDK AND DEVELOPER EXPERIENCE

- Which languages receive official SDKs first?
- Why those languages?
- Which SDK is the reference implementation?
- Can a developer integrate Rilavo without opening an account?
- Can verification be tested locally?
- Is there a simulator?
- Is there a sandbox?
- Is there a test issuer?
- How is a test credential generated?
- Can the verifier run without Rilavo servers?
- How many lines of code should a minimal integration require?
- Can an AI coding agent implement the SDK correctly from the documentation?
- What documentation must exist for agents as well as humans?
- How are backwards-incompatible changes handled?
- What is the versioning model?
- What is the compatibility guarantee?
- How are deprecated features handled?

## 19. INTEROPERABILITY

- What does it mean to be Rilavo-compatible?
- What tests certify compatibility?
- Can third parties implement the protocol from the specification alone?
- Is there a conformance suite?
- Is there an interoperability test network?
- What must be standardized?
- What can remain implementation-specific?
- How does Rilavo interoperate with OAuth?
- How does it interoperate with MCP?
- How does it interoperate with other agent protocols?
- How does it interoperate with existing identity providers?
- How does it interoperate with content-provenance standards?
- What happens when a receiving system supports multiple verification standards?
- Can Rilavo be one verification method among many?
- Can another protocol become the preferred interface without breaking Rilavo?

## 20. PERFORMANCE AND SCALE

- What is the target verification latency?
- What is the target issuance latency?
- What is the target throughput per verifier?
- What is the target throughput per issuer?
- What is the maximum token size?
- What is the maximum delegation chain size?
- What is the storage growth rate?
- What is the bandwidth cost per verification?
- What is the compute cost per verification?
- What is the cost at one million verifications?
- What is the cost at one billion?
- What is the cost at one trillion?
- Which component becomes the bottleneck first?
- What can be horizontally scaled?
- What cannot be horizontally scaled?
- Where does “near-zero marginal cost” stop being true?
- What is the maximum acceptable degradation during overload?

## 21. RELIABILITY AND AVAILABILITY

- What does protocol availability mean if verification is local?
- What services must be highly available?
- What is the target uptime?
- What is the recovery time objective?
- What is the recovery point objective?
- Which components can fail independently?
- What happens if Rilavo's hosted service disappears?
- What happens if an issuer disappears?
- What happens if an issuer becomes malicious?
- What happens if a verifier is compromised?
- What happens if a region is unavailable?
- What happens during a global outage?
- Can the network fail safely?

## 22. SECURITY AND THREAT MODEL

The source audit identifies replay, stolen credentials, malicious tracking, compromised issuers, correlation, and chokepoint abuse as distinct risks. fileciteturn2file0L43-L55

Audit every threat class:

- What is the attacker trying to accomplish?
- What capability must the attacker obtain?
- What is the cheapest attack?
- What is the most scalable attack?
- What is the least detectable attack?
- What is the most damaging attack?
- What evidence would show that the mitigation works?
- What is the residual risk?
- What is the blast radius?
- How is the blast radius bounded?
- How is compromise detected?
- How is compromise communicated?
- Who decides severity?
- Who decides emergency action?
- Who publishes security incidents?
- What secrets exist?
- How are secrets rotated?
- What insider threats exist?
- What supply-chain threats exist?
- What dependency risks exist?
- What malicious-SDK risks exist?
- Can a rogue verifier misuse Rilavo?
- Can a rogue issuer poison the trust graph?
- Can a state actor capture a major operator?
- Can a platform force Rilavo to reveal users?
- Can Rilavo become a surveillance layer?

## 23. FORMAL SECURITY TESTING

- What properties must be formally specified?
- Which properties require formal verification?
- Which require penetration testing?
- Which require fuzzing?
- Which require property-based testing?
- Which require independent cryptographic review?
- What are the replay tests?
- What are the expiry tests?
- What are the revocation tests?
- What are key-rotation tests?
- What are delegation tests?
- What are malformed-token tests?
- What are downgrade tests?
- What are algorithm-confusion tests?
- What are audience-binding tests?
- What are concurrency tests?
- What are clock-skew tests?
- What are incident-recovery tests?

## 24. GOVERNANCE

- Who governs the protocol at v0?
- Why is that governance model appropriate for v0?
- What powers does the founder have?
- What powers must the founder never have?
- What powers belong to a future foundation or standards body?
- Who controls the protocol specification?
- Who controls reference implementations?
- Who controls issuer admission?
- Who can suspend an issuer?
- Who can remove an issuer?
- Who hears appeals?
- Who controls emergency security upgrades?
- Who can change the credential format?
- What voting or approval mechanism applies?
- Who is eligible to participate?
- How are conflicts of interest managed?
- How is capture prevented?
- How is geographic representation handled?
- How is commercial representation balanced against public-interest representation?
- What happens if the governing body becomes inactive?

## 25. DECENTRALIZATION TRIGGERS

The existing research uses a quantitative trigger based on issuer concentration. fileciteturn3file0L110-L121

Do not merely preserve the trigger; interrogate it:

- Why is issuance share the correct metric?
- Could a single verifier still become dominant while issuers are decentralized?
- Could discovery become centralized?
- Could key infrastructure become centralized?
- Could software distribution become centralized?
- Could governance become centralized?
- Could fraud intelligence become centralized?
- What concentration metric should be monitored for each layer?
- What threshold triggers governance decentralization?
- What threshold triggers multiple operators?
- What threshold triggers independent audits?
- What threshold triggers mandatory portability checks?
- What threshold triggers competition review?
- What happens if the threshold is reached unexpectedly fast?
- Can the trigger be manipulated?
- Who verifies the trigger?
- Is the trigger automatic or discretionary?
- What if decentralization causes security to worsen?

## 26. ECONOMIC MODEL OF THE PROTOCOL

- Is the core protocol free?
- Why must it be free?
- What happens if it is not free?
- What adoption friction does pricing create?
- Who pays infrastructure costs?
- Is there a protocol-level fee?
- If not, why not?
- If yes, what exactly is being priced?
- Who can introduce a fee?
- Can a future governance body introduce one?
- What prevents an operator from charging for access to the format?
- Can Rilavo Product charge for hosted services while the protocol remains free?
- Can another provider charge less?
- Can another provider provide the same protocol for free?
- What part of the economy is actually open competition?
- What part of the economy can support commercial margin?

## 27. PROTOCOL DISTRIBUTION / NETWORK EFFECT

The current model identifies verification, developer, organization, and AI-agent loops. fileciteturn2file1L76-L94

Interrogate them rigorously:

### Verification loop

- Why does a verifier integrate?
- What does the verifier gain immediately?
- Can the verifier verify without creating an account?
- Does verification itself create a reason to issue credentials?
- When does the verifier become an issuer?
- What prevents it from using the protocol without becoming part of the network?

### Developer loop

- Why does a developer discover Rilavo?
- What is the first value moment?
- How many minutes to integration?
- What is the first successful verification?
- Does the developer invite another developer automatically?
- Does the application built by the developer expose Rilavo to another organization?
- Can documentation itself be distributed through code generators and AI agents?

### Organization loop

- Why does Company B accept Rilavo because Company A requires it?
- What causes B to require it from C?
- What happens if C refuses?
- Does Rilavo become a network necessity or a compliance burden?
- What prevents coercive adoption mechanisms from becoming anti-competitive?

### AI-agent loop

- How does an agent discover that a receiving system requires Rilavo?
- Can an agent discover the required authorization mechanism automatically?
- Can an agent obtain authorization without human support?
- Can agent frameworks ship Rilavo support by default?
- Can the protocol become part of agent infrastructure without becoming a mandatory proprietary dependency?

### Viral mechanism test

- What exact event causes one adoption to generate another?
- Is the next adoption voluntary?
- Does the next user gain immediate value?
- Is the loop independent of Rilavo marketing spend?
- Can the loop operate across countries?
- Can it operate across industries?
- Can it operate without a consumer token?
- Can it operate without a crypto market?
- Can it operate when Rilavo Product does nothing?

## 28. TRUST GRAPH AND DEFENSIBILITY

The current audit treats the installed verifier base, issuer reputation history, fraud-pattern intelligence, and standards legitimacy as potential durable assets. fileciteturn2file4L194-L210

Audit each:

- What exactly is the trust graph?
- Which edges exist in the graph?
- Who creates each edge?
- How is an edge verified?
- Can a competitor reproduce the graph?
- Can Rilavo sell the graph without compromising privacy?
- What information creates issuer reputation?
- How is reputation protected from gaming?
- How is reputation transferred between operators?
- What is portable?
- What is proprietary?
- What fraud signals can be aggregated legally and ethically?
- What makes fraud intelligence unique?
- How long does it take to accumulate?
- How easily could a competitor acquire equivalent data?
- What happens if a larger competitor enters with more data on day one?

## 29. FORK TEST FOR THE PROTOCOL

- If the entire protocol code is copied tomorrow, what remains unique?
- If the specification is copied, what remains unique?
- If the SDK is copied, what remains unique?
- If the entire hosted service is rebuilt, what remains unique?
- If a large competitor integrates first-class Rilavo support into its ecosystem, what advantage remains?
- If a competitor offers the protocol free and hosts it cheaper, what remains?
- If a competitor offers better tooling, what remains?
- If a competitor offers higher reliability, what happens?
- If a competitor offers better fraud intelligence, what happens?
- What part of Rilavo is protected by network effects?
- What part is protected by trust?
- What part is protected by operational excellence?
- What part is not defensible at all and should therefore remain commoditized?

## 30. COMPANY-DIES-TOMORROW TEST FOR THE PROTOCOL

- If Rilavo Product shuts down, can an existing verifier still verify?
- Can an issuer continue issuing?
- Can keys still be discovered?
- Can revocations still be checked?
- Can credentials still be exported?
- Can another operator take over infrastructure?
- Can developers migrate without rewriting applications?
- Can another company create a compatible service immediately?
- Can governance continue?
- Can the network continue without the founding company?
- What minimum pieces must be decentralized before that becomes true?

---

# PART III — THE MOTHER QUESTION TREE FOR THE RILAVO PRODUCT

# 31. WHY DOES RILAVO PRODUCT EXIST?

This is the central product question.

- If the protocol is open and free, why does Rilavo Product exist?
- What does the product provide that the protocol intentionally does not?
- Why would an product customer pay Rilavo rather than self-host?
- What operational burden does Rilavo remove?
- What financial loss does Rilavo prevent?
- What regulatory burden does Rilavo reduce?
- What engineering cost does Rilavo remove?
- What opportunity does Rilavo enable?
- What service does Rilavo perform better than an internal engineering team?
- What service does Rilavo perform that an individual developer cannot?
- What requires continuous operation rather than software ownership?
- What requires a trust relationship rather than code?
- What requires insurance or legal accountability?
- What requires global support?
- What requires intelligence derived from operating the network?

## 32. PRODUCT IDENTITY

- What kind of company is Rilavo Product?
- Is it cybersecurity?
- Identity infrastructure?
- Trust infrastructure?
- Developer infrastructure?
- Compliance infrastructure?
- AI security infrastructure?
- Managed infrastructure?
- Risk intelligence?
- Is it one company with several products or a platform with services?
- What is its first commercial product?
- What should the company be known for first?
- What should it never become known for?

## 33. PRODUCT CUSTOMER

- Who is the first paying customer?
- Who signs the contract?
- Who uses the API?
- Who owns the risk?
- Who owns the budget?
- Who approves procurement?
- Who evaluates security?
- Who evaluates legal terms?
- Who is the economic buyer?
- Who is the technical buyer?
- Who is the security buyer?
- Who is the daily user?
- Who can cancel the contract?
- What event causes a customer to buy?
- What event causes them not to buy?

## 34. PRODUCT VALUE

- What measurable outcome does the product deliver?
- Does it reduce fraud loss?
- Does it reduce engineering headcount?
- Does it reduce manual review?
- Does it reduce compliance cost?
- Does it reduce transaction abandonment?
- Does it increase successful agent transactions?
- Does it reduce incident response time?
- Does it increase availability?
- Does it reduce liability?
- Can the value be measured in currency?
- Can the customer calculate ROI without trusting Rilavo's marketing?

## 35. PRODUCT PRODUCT STACK

For every proposed product, ask:

- What is it?
- Who uses it?
- Who pays for it?
- Why does it need Rilavo protocol?
- Why cannot the customer build it themselves?
- Which protocol primitives does it consume?
- What proprietary components does it add?
- Is it an API?
- Dashboard?
- Managed infrastructure?
- Compliance service?
- Fraud intelligence service?
- Monitoring system?
- Incident response service?
- Identity orchestration service?
- Agent security gateway?
- Hosted issuer service?
- Hosted verifier service?
- Certification service?
- Audit service?
- Insurance/assurance service?
- Marketplace?

## 36. PRODUCT — DEVELOPER PLATFORM

- What does the free developer experience contain?
- What is paid?
- What must never be paywalled?
- What is the product upgrade moment?
- What usage level causes a customer to need paid infrastructure?
- What features justify product pricing?
- What happens if a developer never pays?
- Can a developer stay on the open protocol forever?
- If so, how does Rilavo still benefit?
- What portion of developers become issuers?
- What portion become verifiers?
- What portion become product customers?

## 37. PRODUCT — MANAGED INFRASTRUCTURE

- Why would a company use Rilavo-hosted infrastructure?
- What does Rilavo operate?
- What does the customer operate?
- What uptime does Rilavo guarantee?
- How does Rilavo recover from failure?
- What geographic regions can customers choose?
- What data residency options exist?
- Can a customer run a private deployment?
- Can Rilavo support hybrid deployments?
- How does a customer migrate away?
- How does Rilavo avoid becoming an operational lock-in point?

## 38. PRODUCT — FRAUD INTELLIGENCE

- What fraud signals can Rilavo legally and safely aggregate?
- What data is actually needed to generate them?
- What data must never be aggregated?
- Can signals be privacy-preserving?
- Can they be anonymized without destroying utility?
- How are false positives handled?
- How is intelligence validated?
- How does intelligence improve with network scale?
- Who owns derived intelligence?
- Can a customer opt out?
- Can a customer contribute data and still prohibit resale?
- How is competitive data separation handled?
- Can one customer infer another customer's activity?

## 39. PRODUCT — COMPLIANCE

- Which regulations create immediate customer demand?
- Which industries need auditability?
- Which jurisdictions matter first?
- What evidence can Rilavo produce?
- What cannot Rilavo certify?
- What does Rilavo's compliance product actually automate?
- Who is the legal decision-maker for compliance?
- Is Rilavo merely infrastructure or does it make regulated determinations?
- What happens if a customer relies on Rilavo and a regulator disagrees?
- What liability attaches to the service?
- Does the service require external certification?

## 40. PRODUCT — SLA AND ASSURANCE

- Why is uptime worth paying for if the protocol can run locally?
- Which services are genuinely mission-critical?
- What happens when Rilavo is down?
- Does the verifier continue operating locally?
- Which customers need centralized monitoring?
- What SLA tiers make sense?
- What support obligations exist?
- What incident-response obligations exist?
- What financial penalties apply to Rilavo failures?
- What insurance is required?

## 41. PRODUCT — INCIDENT RESPONSE

- Who contacts Rilavo during an incident?
- Who contacts the customer?
- Who contacts an issuer?
- Who has authority to revoke?
- Who has authority to suspend?
- How fast can Rilavo respond?
- What is the escalation ladder?
- How is evidence preserved?
- How is customer notification handled?
- How is public disclosure handled?
- What happens if disclosure creates additional security risk?
- How is post-incident intelligence fed back into the network?

## 42. PRODUCT REVENUE MODEL

The current audit identifies usage, product infrastructure, compliance, SLA, developer tooling, security, and privacy-preserving intelligence as candidate commercial layers, while rejecting the consumer $1 concept as the core revenue engine. fileciteturn3file0L179-L212

For each revenue stream ask:

- What exactly is charged?
- Who pays?
- Why do they pay?
- What budget pays for it?
- What existing expense does it replace?
- What measurable loss does it reduce?
- How frequently is the charge incurred?
- What is the gross margin?
- What are direct infrastructure costs?
- What are support costs?
- What are security costs?
- What are insurance costs?
- What are compliance costs?
- What happens at 1,000 customers?
- 10,000?
- 100,000?
- What causes revenue concentration risk?
- What prevents one customer from becoming dangerously dominant?

## 43. THE $1 AUDIT

- What exactly is the $1?
- Who pays it?
- Why $1 rather than $0.10 or $5?
- Is it revenue, identity issuance cost, distribution cost, acquisition cost, or something else?
- Does it have a genuine economic purpose?
- Would adoption remain strong if it were free?
- Does it create psychological commitment?
- Does it create unnecessary payment friction?
- Is it only relevant to consumer-facing credentials?
- Can product customers subsidize consumer use?
- Does the $1 mechanism remain useful if no crypto/token exists?
- Does the $1 mechanism remain useful if another company offers the same protocol for free?
- What is the legal and accounting treatment?
- What are payment-processing costs?
- What happens in countries where $1 is economically material?
- Is pricing local or global?

## 44. OPEN-PROTOCOL / PAID-PRODUCT EQUILIBRIUM

- What remains free forever?
- What can become paid later?
- Can the product place proprietary features around the open protocol without undermining openness?
- Which services benefit from scale?
- Which services can competitors reproduce?
- What prevents Rilavo from turning protocol access into a hidden tax?
- What prevents Rilavo from withholding interoperability to force product upgrades?
- Can a customer downgrade to the free protocol?
- Can a competitor implement the same API?
- Can a competitor provide managed infrastructure using the same protocol?
- Can a customer leave Rilavo Product while remaining in the protocol ecosystem?
- If yes, what makes Rilavo Product valuable enough that customers choose to stay?

## 45. THE “BETTER COMPANY BUILDS ON RILAVO” TEST

This is a mandatory product survival audit.

### Scenario

A much richer company downloads the open Rilavo protocol, launches a better hosted service, has more servers, more salespeople, more capital, better branding, lower prices, and faster global expansion.

Ask:

- Why does Rilavo Product survive?
- What can the competitor copy immediately?
- What cannot be copied immediately?
- What network position belongs to the protocol rather than Rilavo Product?
- Can Rilavo Product compete on price?
- Should it?
- Can it compete on reliability?
- Can it compete on trust?
- Can it compete on fraud intelligence?
- Can it compete on compliance expertise?
- Can it compete on customer support?
- Can it compete on reference implementation quality?
- Can it compete on standards leadership?
- Can it compete on ecosystem relationships?
- Can it compete on historical issuer reputation?
- What customer relationships are portable?
- What customer relationships are proprietary?
- What happens if the rival becomes the largest operator?
- What happens if the rival becomes the largest issuer?
- What happens if the rival controls developer distribution?
- What happens if the rival's service is technically superior?
- What prevents Rilavo from becoming a commodity operator?
- If nothing prevents it, is Rilavo Product still worth building?

## 46. THE “RILAVO PRODUCT IS NOT SPECIAL” TEST

- Could AWS build this?
- Could Microsoft build this?
- Could Google build this?
- Could Cloudflare build this?
- Could a major identity company build this?
- Could a major security company build this?
- Could an existing API gateway vendor add it?
- Could an AI agent platform bundle it?
- Could a bank consortium build it?
- Could a standards organization provide it?
- If every answer is yes, what does Rilavo uniquely know or operate?
- If the answer is “nothing,” should the product exist independently of the protocol?

## 47. PRODUCT MOAT

- What is the product moat separate from the protocol moat?
- What does Rilavo Product learn from operation?
- What gets better with more customers?
- What gets better with more issuers?
- What gets better with more verifiers?
- What gets better with more incidents observed?
- What gets better with more jurisdictions served?
- What gets better with more compliance integrations?
- What gets better with more developer integrations?
- What is difficult to copy because it takes time?
- What is difficult to copy because it requires trust?
- What is difficult to copy because it requires operations?
- What is difficult to copy because it requires relationships?
- What is easy to copy and should therefore not be treated as a moat?

## 48. PRODUCT DATA ADVANTAGE

- What information can the product learn from operating the service?
- Is that information generated by the product, customer, protocol, or network?
- Can it be used commercially?
- Can it be used for fraud prevention?
- Can it be shared with other customers?
- What privacy restrictions apply?
- What competitive restrictions apply?
- Can a customer demand deletion?
- Can the product aggregate signals without identifying the customer?
- How is this advantage prevented from becoming an invasive surveillance system?
- What governance prevents product intelligence from silently becoming protocol governance?

## 49. PRODUCT SALES MODEL

- Is the first motion developer-led, product-led, founder-led, partner-led, or product sales?
- What is the shortest sales cycle?
- What is the highest-value vertical?
- Which vertical has an immediate pain point?
- What proof of value can be demonstrated in 14 days?
- What proof of value can be demonstrated in 30 days?
- What procurement objections will occur?
- What security questionnaire must Rilavo satisfy?
- What legal objections will occur?
- What integration objections will occur?
- What makes the customer take the first production step?
- What makes them expand?
- What makes them renew?
- What makes them recommend Rilavo?

## 50. PRODUCT CUSTOMER RETENTION

- What makes Rilavo difficult to remove from a workflow without creating harmful lock-in?
- What makes the service useful after the protocol becomes commodity infrastructure?
- Does Rilavo continuously improve risk decisions?
- Does it continuously improve observability?
- Does it reduce incidents over time?
- Does the customer's value increase with usage history?
- Can the customer take its data and leave?
- Can it return later without losing interoperability?
- Why would it still choose Rilavo?

## 51. PRODUCT DISTRIBUTION

- How does the first customer discover Rilavo?
- How does the second customer discover Rilavo?
- Can the protocol itself create product leads?
- Can developer use create product demand?
- Can a verifier recommend Rilavo to its suppliers?
- Can an issuer recommend Rilavo to its customers?
- Can an agent platform distribute the protocol?
- Can cloud marketplaces distribute the product product?
- Can security platforms bundle the product?
- Can compliance consultants distribute it?
- Can banks or infrastructure partners distribute it?
- Does the product need paid advertising?
- What part of growth is organic?
- What part is sales-led?
- What part is network-led?

## 52. PRODUCT PARTNER ECOSYSTEM

- Which companies should integrate rather than compete?
- Which companies could become issuers?
- Which could become verifiers?
- Which could become product resellers?
- Which could become certification partners?
- Which could become auditors?
- Which could provide insurance?
- Which could provide hardware attestation?
- Which could provide identity evidence?
- Which could provide fraud intelligence?
- What incentives align each partner?
- What prevents a partner from becoming a competitor?
- What partner rights should be standardized?

---

# PART IV — THE PROTOCOL ↔ PRODUCT CONNECTION

# 53. EXACT INTERFACE BETWEEN THE TWO

- What protocol objects does Rilavo Product consume?
- What protocol objects does Rilavo Product produce?
- What APIs belong to the protocol?
- What APIs are only Rilavo Product APIs?
- What data flows from product to protocol?
- What data flows from protocol to product?
- Which data must never flow in either direction?
- What can Product cache?
- What can Product enrich?
- What can Product aggregate?
- What can Product monetize?
- What remains protocol-governed?
- Can the product operate without proprietary protocol privileges?
- Can another product operate on exactly the same protocol permissions?

## 54. VALUE FLOW

Map every value flow:

`Principal → Agent → Issuer → Credential → Verifier → Decision → Receipt → Intelligence → Product Service`

For each arrow ask:

- What is transferred?
- Why is it transferred?
- Who authorizes the transfer?
- Who benefits?
- Who pays?
- What risk is introduced?
- What trust assumption is introduced?
- Is the transfer necessary?
- Can the transfer be eliminated?

## 55. MONEY FLOW

Map:

`Customer payment → Rilavo Product → infrastructure → staff → security → compliance → insurance → protocol ecosystem`

Ask:

- Does any money need to enter the protocol?
- Should any money enter the protocol?
- Can the protocol remain commercially neutral?
- Does Product subsidize protocol development?
- Does Product fund ecosystem grants?
- Does Product fund independent audits?
- Does Product fund governance?
- Would that funding create capture risk?
- How can protocol governance remain independent if Product is its largest funder?

## 56. CONTROL FLOW

Map who controls:

- issuance;
- verification;
- key discovery;
- revocation;
- issuer admission;
- governance;
- software releases;
- product accounts;
- fraud intelligence;
- customer data;
- emergency response.

Then ask:

- Which controls belong to the protocol?
- Which belong to Product?
- Which must be independent?
- Which controls should become decentralized with scale?
- Which controls must remain centralized for operational safety?

## 57. FAILURE FLOW

For each major failure, ask what happens independently to protocol and product:

- Rilavo Product shuts down.
- Rilavo Product is hacked.
- Protocol governance is compromised.
- One issuer is compromised.
- One verifier is compromised.
- Revocation services fail.
- Key directories fail.
- A major cloud provider fails.
- A major country blocks Rilavo services.
- A major customer leaves.
- A major competitor forks the protocol.
- A major competitor offers a superior hosted service.
- A major regulator imposes interoperability requirements.
- A major vulnerability is found in the cryptographic primitive.

## 58. SURVIVAL MATRIX

For each scenario ask:

- Does the protocol survive?
- Does the product survive?
- Does the customer survive?
- Does the network survive?
- What data remains portable?
- What service must be replaced?
- Who can replace it?
- How quickly?
- What does the customer lose?
- What does Rilavo lose?
- What remains Rilavo's advantage?

---

# PART V — FUTURE HORIZONS AUDIT

# 59. HORIZON 2 — AGENT DELEGATION

- What exact new problem does Horizon 2 solve?
- Why cannot v0 solve it?
- What new security guarantees are needed?
- What new fields must the protocol support?
- What happens to token size?
- What happens to verification cost?
- What happens to privacy?
- What happens to auditability?
- What happens to revocation?
- What happens to issuer liability?
- What happens to product pricing?
- What happens to adoption?

# 60. HORIZON 3 — HUMAN VERIFICATION

The current research deliberately defers human verification due to higher stakes, higher regulatory exposure, and the requirement for stronger privacy architecture. fileciteturn3file0L90-L106

Ask:

- What exactly does “real human” mean?
- What evidence establishes it?
- Who provides the evidence?
- How is liveness proven?
- Is biometric data required?
- Can biometric data remain on-device?
- Can ZK prove eligibility without revealing raw identity?
- Who is liable for a false positive?
- Who is liable for a false negative?
- How are minors handled?
- How are vulnerable populations handled?
- What accessibility problems arise?
- What jurisdictions recognize the credential?
- What jurisdictions reject it?
- Can users use alternative evidence?
- What happens when a user loses access to their device?

# 61. HORIZON 3 — CONTENT PROVENANCE

- What exactly is proven about content?
- Human-created?
- AI-generated?
- AI-assisted?
- Edited?
- Originated from a specific source?
- Who signs content at creation time?
- How is provenance preserved through re-encoding?
- How is metadata stripped?
- What happens when content passes through multiple generators?
- How is provenance inherited?
- Can a verifier determine uncertainty?
- What happens when content has no provenance?
- Does “no proof” mean “fake”?
- Who decides?
- How is Rilavo interoperable with existing provenance ecosystems?

# 62. HORIZON 4 — DEVICE AND SOFTWARE ATTESTATION

- What is an authentic device?
- What is trusted software?
- What evidence comes from secure hardware?
- How does Rilavo consume TPM/Secure Enclave/attestation signals?
- What can be verified without controlling the hardware manufacturer?
- What happens when manufacturers disagree?
- Does hardware attestation create centralization risk?
- Does Rilavo become dependent on platform vendors?

# 63. HORIZON 4 — ORGANIZATIONS AND EVENTS

- How does Rilavo prove an organization is legitimate?
- Who issues organizational claims?
- How are beneficial ownership claims handled?
- How are licenses verified?
- How are events corroborated?
- Can multiple independent attestations combine into one claim?
- What happens when attestations disagree?
- How is confidence represented?

---

# PART VI — LEGAL, REGULATORY, ETHICAL, AND SOCIAL AUDIT

# 64. LEGAL CHARACTERIZATION

- Is the protocol merely software?
- Does operating an issuer create regulated activity?
- Does hosting verification create regulated activity?
- Does human identity verification create regulated activity?
- Does fraud intelligence create data-controller obligations?
- Does Rilavo become an identity provider?
- Does it become a regulated compliance vendor?
- What jurisdictions matter first?
- What laws apply to data processing?
- What laws apply to AI?
- What laws apply to competition?
- What laws apply to cybersecurity?
- What laws apply to digital identity?
- What contractual allocation of liability is required?

## 65. PRIVACY AND DATA PROTECTION

- What is the minimum data collected?
- What is the lawful basis?
- Who is controller?
- Who is processor?
- Who is joint controller?
- What is the retention period?
- What are the deletion obligations?
- What rights must users have?
- What happens when deletion conflicts with audit evidence?
- How is consent handled?
- What happens when consent is withdrawn?
- What happens when a verifier legally must keep records?
- What happens when jurisdictions conflict?

## 66. COMPETITION AND GATEKEEPER RISK

- Can Rilavo become an essential access point?
- Can any single operator become dominant?
- Can Product discriminate between operators?
- Can Product withhold information from competitors?
- Can Product require exclusivity?
- Can Product offer preferential pricing to lock in customers?
- Can protocol governance favor Product?
- What interoperability obligations should be voluntarily adopted?
- What portability guarantees are mandatory?
- How would the business operate if a regulator imposed access requirements?
- Can the business remain profitable under those requirements?

The existing specification explicitly distinguishes privacy decentralization from market decentralization and treats gatekeeper risk as a long-term consequence of success rather than something to disguise. fileciteturn3file0L300-L308

## 67. ETHICAL ABUSE

- Can Rilavo be used to exclude legitimate users?
- Can it be used for surveillance?
- Can it be used for political suppression?
- Can it be used to create centralized blacklists?
- Can it become a de facto “real human” certificate?
- Can governments misuse it?
- Can corporations misuse it?
- Can criminals misuse it?
- What abuse cases are unacceptable?
- Who enforces those boundaries?
- How are appeals handled?
- Can a person challenge a verification decision?
- Can a person use an alternative verification provider?

---

# PART VII — DEVELOPMENT BY A SOLO FOUNDER + AI AGENTS

# 68. SOLO-FOUNDER FEASIBILITY

- What can one developer actually build?
- What cannot one developer safely build?
- What knowledge is mandatory?
- What knowledge can be delegated to AI coding agents?
- What knowledge must remain with the human?
- Which components require external security specialists?
- Which components require legal counsel?
- Which components require product research?
- Which components require customer interviews?
- Which components require standards participation?
- Which components require independent audit?

The current audit considers v0 solo-buildable precisely because it excludes exotic cryptography, blockchain, and premature decentralization, while requiring human review before liability-bearing production use. fileciteturn3file0L234-L242

## 69. AI CODING AGENT GOVERNANCE

- What may an AI coding agent decide?
- What may it never decide?
- Who approves architecture?
- Who approves cryptographic choices?
- Who approves protocol changes?
- Who approves security changes?
- Who approves migrations?
- What is the source of truth?
- How does the agent access the source of truth?
- How is context controlled?
- How are conflicting agent outputs resolved?
- How is generated code tested?
- How is generated code reviewed?
- How are hallucinated APIs detected?
- How are malicious dependencies detected?
- How are secrets protected from coding agents?
- Can agents commit directly to production?
- What is the mandatory human approval path?

## 70. THE SEVEN LIVING ARTIFACTS AUDIT

The current Rilavo specification identifies product specification, architecture specification, threat model, API contracts, test requirements, security rules, and decision log as living artifacts. fileciteturn3file0L246-L259

For each artifact ask:

- Who owns it?
- Who may edit it?
- Who approves changes?
- What is immutable?
- What is versioned?
- What triggers review?
- What other documents depend on it?
- Can an AI agent read it safely?
- Can an AI agent modify it?
- What evidence is required before modification?
- How are contradictory versions resolved?

## 71. DEVELOPMENT ROADMAP

- What must be specified first?
- What must be prototyped first?
- What must be tested first?
- What is reversible?
- What is irreversible?
- What must be frozen before developers are allowed to implement?
- What can be changed weekly?
- What can be changed monthly?
- What can only change through protocol governance?
- What is the minimum demo?
- What is the minimum pilot?
- What is the minimum production release?
- What is the minimum product-ready release?

---

# PART VIII — TESTING THE WHOLE CONCEPT

# 72. ANTI-DELUSION TESTS

- Is Rilavo solving a real problem or an impressive problem statement?
- Would users pay if AI disappeared?
- Would users pay if fraud disappeared?
- Would agents need it if OAuth improved substantially?
- Would platforms integrate it if they already had perfect internal authorization?
- Would protocol adoption happen without Rilavo Product?
- Would Product revenue exist without protocol network effects?
- Is the network effect real or merely an assumption?
- Is the moat real or merely a future possibility?
- Does decentralization solve the stated problem?
- Does openness create value or remove value?
- Does product defensibility depend on data that customers would refuse to share?

# 73. COUNTERFACTUAL TESTS

Ask what happens if:

- OAuth becomes agent-native and solves most of the wedge.
- A competing open protocol becomes more popular.
- A major cloud vendor bundles equivalent functionality.
- A major AI agent platform requires another standard.
- Governments mandate another credential system.
- C2PA or another provenance standard becomes dominant.
- ZK becomes too expensive for production.
- A new cryptographic primitive replaces Ed25519.
- The protocol gains no network effect after five years.
- Rilavo Product never becomes the largest operator.
- Another company becomes the largest operator.
- The protocol succeeds but the product fails.
- The product succeeds but the protocol is forked.
- Customers stop paying but continue using the protocol.

# 74. “NO RILAVO” TEST

- Can the problem be solved without Rilavo?
- How?
- At what cost?
- With what limitations?
- Why would anyone change?
- Is the proposed advantage strong enough to overcome switching costs?

# 75. “NO PRODUCT” TEST

- Can the protocol succeed with no Rilavo company?
- Who maintains infrastructure?
- Who answers developers?
- Who handles security incidents?
- Who creates trust intelligence?
- Who builds integrations?
- Who maintains certification?
- Who supports product users?
- Does a foundation perform these functions instead?
- If so, what exactly is the commercial role of Rilavo Product?

# 76. “NO PROTOCOL” TEST

- Could the product simply build a proprietary closed network?
- If yes, why open a protocol?
- What value does interoperability add?
- What value does portability add?
- Does openness increase adoption enough to offset the loss of protocol exclusivity?

# 77. “BETTER PROTOCOL” TEST

- What if another open protocol is technically better?
- Can Rilavo Product support it?
- Should Rilavo become protocol-agnostic?
- Does the company sell trust infrastructure rather than one particular protocol?
- What parts of Rilavo remain useful?
- Could Rilavo migrate its network?

# 78. “BETTER PRODUCT” TEST

- What if another product operator is better?
- Can Rilavo customers switch operators without changing the protocol?
- What keeps Rilavo Product commercially relevant?
- Is the answer network trust, intelligence, operations, standards, or something else?
- Has that advantage been demonstrated or assumed?

---

# PART IX — SCALE AND LONG-TERM FAILURE TESTS

# 79. 10,000-SCALE QUESTIONS

- What breaks first?
- Which manual processes become bottlenecks?
- Which security controls need automation?
- Which support processes need automation?
- What operational metrics become mandatory?
- Which product assumptions are tested for the first time?

# 80. 1-MILLION-SCALE QUESTIONS

- What infrastructure becomes expensive?
- What customer support becomes expensive?
- What security operations become expensive?
- What compliance obligations emerge?
- What liability changes?
- What insurance changes?
- What governance changes?
- What concentration risk appears?

# 81. 100-MILLION-SCALE QUESTIONS

- Who controls issuance?
- Who controls discovery?
- Who controls revocation?
- Who controls product access?
- Does Rilavo become an essential infrastructure provider?
- Does a single operator dominate?
- Has the decentralization trigger fired?
- Has governance moved?
- Can users still migrate?
- Can competitors still participate?

# 82. GLOBAL-SCALE QUESTIONS

- What happens across jurisdictions?
- What happens when governments disagree?
- What happens when governments require local control?
- Can countries run local operators?
- Can products run private operators?
- Can public-interest operators participate?
- Can the network tolerate political fragmentation?
- What is the international governance structure?
- Can one nation control the protocol?
- Can one company control the protocol?

The current strategic blueprint treats global adoption as a state in which the protocol and compatible operators must survive independently of the founding company. fileciteturn2file4L202-L210

---

# PART X — DOCUMENT TREE GENERATION QUESTIONS

The answers to this mother document must generate the following two project trees.

# 83. PROTOCOL TREE — REQUIRED DOCUMENTS

For each document below, the mother document must provide enough answered questions to create it without inventing missing architecture.

### `/RILAVO_PROTOCOL/`

- `00_PROTOCOL_MASTER_SPECIFICATION.md`
- `01_PROTOCOL_MISSION_AND_SCOPE.md`
- `02_TERMINOLOGY_AND_SEMANTICS.md`
- `03_PROBLEM_AND_WEDGE.md`
- `04_PROTOCOL_PRINCIPLES.md`
- `05_ACTOR_AND_TRUST_MODEL.md`
- `06_CREDENTIAL_SPECIFICATION.md`
- `07_AUTHORIZATION_MODEL.md`
- `08_DELEGATION_AND_ATTENUATION.md`
- `09_REVOCATION_SPECIFICATION.md`
- `10_AUDIT_RECEIPTS.md`
- `11_CRYPTOGRAPHIC_SPECIFICATION.md`
- `12_KEY_MANAGEMENT.md`
- `13_PRIVACY_ARCHITECTURE.md`
- `14_DATA_MODEL.md`
- `15_NETWORK_ARCHITECTURE.md`
- `16_NODE_AND_OPERATOR_SPECIFICATION.md`
- `17_DISCOVERY_AND_KEY_DIRECTORY.md`
- `18_INTEROPERABILITY_SPECIFICATION.md`
- `19_API_SPECIFICATION.md`
- `20_SDK_SPECIFICATION.md`
- `21_CONFORMANCE_TESTS.md`
- `22_SECURITY_THREAT_MODEL.md`
- `23_SECURITY_RESPONSE_MODEL.md`
- `24_GOVERNANCE_SPECIFICATION.md`
- `25_DECENTRALIZATION_TRIGGER.md`
- `26_PROTOCOL_VERSIONING.md`
- `27_BACKWARD_COMPATIBILITY.md`
- `28_UPGRADE_AND_MIGRATION.md`
- `29_PERFORMANCE_REQUIREMENTS.md`
- `30_RELIABILITY_REQUIREMENTS.md`
- `31_DEPLOYMENT_GUIDE.md`
- `32_SELF_HOSTING_GUIDE.md`
- `33_OPERATOR_REQUIREMENTS.md`
- `34_HORIZON_2_SPECIFICATION.md`
- `35_HORIZON_3_HUMAN_VERIFICATION.md`
- `36_HORIZON_3_CONTENT_PROVENANCE.md`
- `37_HORIZON_4_ATTESTATION.md`
- `38_PROTOCOL_ECONOMICS.md`
- `39_PROTOCOL_LICENSING.md`
- `40_PROTOCOL_ETHICS_AND_ABUSE.md`
- `41_PROTOCOL_REGULATORY_ARCHITECTURE.md`
- `42_PROTOCOL_DISASTER_RECOVERY.md`
- `43_PROTOCOL_SUNSET_AND_SUCCESSION.md`
- `44_PROTOCOL_DECISION_LOG.md`
- `45_PROTOCOL_CHANGELOG.md`

### Generation questions for every protocol document

- Which mother questions feed this document?
- Which answers are prerequisites?
- Which unanswered questions block it?
- Which answers are protocol decisions versus product decisions?
- What tests prove its claims?
- Who approves it?
- What other documents depend on it?

# 84. PRODUCT TREE — REQUIRED DOCUMENTS

### `/RILAVO_PRODUCT/`

- `00_PRODUCT_MASTER_SPECIFICATION.md`
- `01_PRODUCT_MISSION.md`
- `02_COMPANY_IDENTITY.md`
- `03_CUSTOMER_PROBLEM.md`
- `04_CUSTOMER_SEGMENTS.md`
- `05_VALUE_PROPOSITION.md`
- `06_PRODUCT_PORTFOLIO.md`
- `07_DEVELOPER_PLATFORM.md`
- `08_MANAGED_INFRASTRUCTURE.md`
- `09_FRAUD_INTELLIGENCE.md`
- `10_COMPLIANCE_PRODUCTS.md`
- `11_SECURITY_SERVICES.md`
- `12_SLA_AND_ASSURANCE.md`
- `13_INCIDENT_RESPONSE.md`
- `14_API_BUSINESS_MODEL.md`
- `15_PRICING.md`
- `16_UNIT_ECONOMICS.md`
- `17_REVENUE_MODEL.md`
- `18_GO_TO_MARKET.md`
- `19_NETWORK_DISTRIBUTION.md`
- `20_PARTNER_ECOSYSTEM.md`
- `21_CUSTOMER_SUCCESS.md`
- `22_SALES_PROCESS.md`
- `23_MARKETING.md`
- `24_DEVELOPER_RELATIONS.md`
- `25_COMPETITIVE_STRATEGY.md`
- `26_PRODUCT_MOAT.md`
- `27_DATA_AND_INTELLIGENCE_POLICY.md`
- `28_LEGAL_AND_REGULATORY.md`
- `29_PRIVACY_AND_DATA_GOVERNANCE.md`
- `30_PRODUCT_SECURITY.md`
- `31_INSURANCE_AND_LIABILITY.md`
- `32_FINANCE_AND_OPERATIONS.md`
- `33_HUMAN_RESOURCES.md`
- `34_VENDOR_MANAGEMENT.md`
- `35_CORPORATE_GOVERNANCE.md`
- `36_FUNDING_AND_CAPITAL.md`
- `37_PRODUCT_RISK_REGISTER.md`
- `38_COMPETITOR_RESPONSE_PLAYBOOK.md`
- `39_PROTOCOL_RELATIONSHIP.md`
- `40_PROTOCOL_FUNDING_AND_STEWARDSHIP.md`
- `41_SURVIVAL_IF_PROTOCOL_FORKED.md`
- `42_SURVIVAL_IF_COMPETITOR_OPERATES_BETTER.md`
- `43_SURVIVAL_IF_RILAVO_PROTOCOL_DECLINES.md`
- `44_SUCCESSION_AND_CONTINUITY.md`
- `45_PRODUCT_DECISION_LOG.md`

### Generation questions for every product document

- What protocol assumptions does this depend on?
- Can the product feature exist without Rilavo protocol?
- Should it exist if a competitor runs the protocol?
- Can another company replicate it?
- What customer value makes it worth paying for?
- What evidence supports the market claim?
- What is the failure condition?
- What is the unit-economic test?
- What regulatory review is required?

# 85. CONNECTION TREE — REQUIRED CROSS-LAYER DOCUMENTS

### `/RILAVO_CONNECTION/`

- `01_PROTOCOL_PRODUCT_BOUNDARY.md`
- `02_DATA_FLOW_BETWEEN_LAYERS.md`
- `03_VALUE_FLOW_BETWEEN_LAYERS.md`
- `04_MONEY_FLOW_BETWEEN_LAYERS.md`
- `05_CONTROL_AND_GOVERNANCE_BOUNDARY.md`
- `06_API_AND_INTERFACE_CONTRACTS.md`
- `07_PORTABILITY_AND_EXIT.md`
- `08_COMPETITOR_OPERATOR_MODEL.md`
- `09_PRODUCT_ON_AN_OPEN_PROTOCOL.md`
- `10_PROTOCOL_WITHOUT_PRODUCT.md`
- `11_PRODUCT_WITHOUT_PROTOCOL.md`
- `12_PROTOCOL_FORK_SURVIVAL.md`
- `13_PRODUCT_COMPETITOR_SURVIVAL.md`
- `14_DECENTRALIZATION_TRANSITION.md`
- `15_PROTOCOL_FUNDING_AND_INDEPENDENCE.md`
- `16_SHARED_SECURITY_MODEL.md`
- `17_SHARED_INCIDENT_MODEL.md`
- `18_SHARED_RISK_REGISTER.md`
- `19_SHARED_ROADMAP.md`

---

# PART XI — FINAL BLUEPRINT GATES

# 86. PROTOCOL GO / NO-GO GATE

Do not approve protocol development beyond v0 until every question below has an evidenced answer:

- What exact problem is being solved?
- Who needs the solution?
- Why do existing mechanisms fail?
- What is the minimum transaction?
- What is the exact proof?
- What is the exact trust model?
- What is the exact security model?
- What happens if the issuer is compromised?
- What happens if Rilavo disappears?
- How does revocation work?
- How does portability work?
- What is free?
- What is open?
- What remains centralized?
- Why is centralization acceptable at this stage?
- What triggers decentralization?
- How is interoperability guaranteed?
- How is abuse handled?
- What is the test that proves the network effect exists?

# 87. PRODUCT GO / NO-GO GATE

- Why does the company exist independently of the protocol?
- What exactly does it sell?
- Who pays?
- Why do they pay?
- What existing budget pays?
- What is the first product?
- What is the first customer?
- What is the gross-margin logic?
- What happens if protocol usage grows but Product revenue does not?
- What happens if Product revenue grows but protocol adoption does not?
- What if a richer competitor provides better infrastructure?
- What if a competitor offers the same services cheaper?
- What if customers self-host?
- What remains uniquely valuable?
- Can Product survive a protocol fork?
- Can Product survive losing protocol governance?
- Can Product survive losing exclusive access to anything?
- Is the business genuinely competitive without artificial lock-in?

# 88. PROTOCOL–PRODUCT GO / NO-GO GATE

- Can the protocol function without Rilavo Product?
- Can Product function without privileged protocol ownership?
- Can customers leave Product without leaving the protocol?
- Can competitors operate on the same protocol?
- Can the protocol survive Product failure?
- Can Product survive protocol competition?
- Can protocol governance remain independent from Product?
- Can Product earn money without taxing protocol access?
- Can Product create value without controlling identity data?
- Can a future regulator require interoperability without destroying Product economics?
- Can the system remain useful if a better competitor exists?

---

# 89. THE FIVE FINAL RILAVO QUESTIONS

These are the final questions that the complete mother blueprint must eventually answer with evidence — but this document deliberately does not answer them:

### Q1 — Necessity

> **What must the world increasingly do anyway, and why does that action require a new trust mechanism?**

### Q2 — Protocol

> **What is the smallest open mechanism that makes that action safer, more interoperable, more private, or more economically viable?**

### Q3 — Network

> **Why does each legitimate use of the protocol increase its usefulness to another independent participant without requiring a centralized marketing campaign?**

### Q4 — Product

> **Why does a rational customer pay Rilavo Product when the protocol itself is free, open, portable, and independently operable?**

### Q5 — Survival

> **If the protocol is copied, the product is outcompeted, the founder disappears, regulators intervene, and another company operates a better commercial service on the same protocol, what remains valuable and why?**

---

# 90. MOTHER-DOCUMENT CLOSURE CONDITION

This document is complete only when it can serve as the upstream source from which the Protocol and Product trees can be generated without inventing material assumptions.

The closure condition is therefore:

> **Every material claim required by the Protocol tree, Product tree, and Connection tree must trace back to one or more answered, evidenced, tested questions in this mother document.**

If a downstream document introduces a major decision for which no mother question exists, the mother document must be reopened and the missing question added before the downstream decision is treated as authoritative.

The existing Rilavo specification already uses this philosophy: decisions are separated from genuinely open questions, and the project explicitly warns against manufacturing certainty merely to fill a template. fileciteturn3file0L10-L18

---

# APPENDIX A — REQUIRED ANSWER TEMPLATE

Use this template for every material question:

```text
QUESTION ID:

QUESTION:

ANSWER:

EVIDENCE / SOURCE:

CONFIDENCE:
[ ] Confirmed
[ ] Strong evidence
[ ] Working assumption
[ ] Unknown

STATUS:
[ ] Decision
[ ] Open
[ ] Rejected
[ ] Deferred

RATIONALE:

COUNTERARGUMENT:

TEST / VALIDATION:

OWNER:

DATE ANSWERED:

NEXT REVIEW DATE:

PROTOCOL DOCUMENTS AFFECTED:

PRODUCT DOCUMENTS AFFECTED:

CONNECTION DOCUMENTS AFFECTED:

DEPENDENCIES:

RISKS CREATED:

RISKS REDUCED:

FOLLOW-UP QUESTIONS:
```

# APPENDIX B — QUESTION PRIORITY

Every question should be marked:

- **P0 — Existential:** wrong answer can invalidate Rilavo.
- **P1 — Foundational:** wrong answer can invalidate a major architecture or business model.
- **P2 — Structural:** required to create a downstream specification.
- **P3 — Operational:** required for implementation or scaling.
- **P4 — Optimization:** improves an already-valid system.

# APPENDIX C — EVIDENCE STANDARD

Prefer, in descending order:

1. Production evidence.
2. Independent user/customer evidence.
3. Security testing or formal analysis.
4. Independent expert review.
5. Standards or authoritative regulatory sources.
6. Controlled experiments.
7. Market research.
8. Well-defined technical reasoning.
9. Founder hypothesis.
10. Intuition.

A lower-level evidence source may support discovery but should not silently become a permanent architectural truth.

# APPENDIX D — MOTHER DOCUMENT PRINCIPLE

**Do not make the question list smaller merely to make the project easier.**

The purpose of the mother document is to expose assumptions before they become code, contracts, governance structures, pricing commitments, or irreversible protocol decisions.

The protocol and product are intentionally close but not identical:

- The **protocol** must eventually be capable of surviving Rilavo Product.
- The **product** must be capable of competing without owning the protocol.
- The **connection layer** must make the two economically complementary without making either one existentially dependent on unilateral control by the other.

The research and current project specification support this separation: the protocol is envisioned as open and free, while the commercial layer monetizes managed infrastructure, APIs, SLAs, compliance tooling, and privacy-preserving intelligence; the long-run target is for the protocol to survive independently of the founding company. fileciteturn3file1L496-L528 fileciteturn3file1L534-L543

**End of Mother Audit & Blueprint Question Bank.**
