---
layout: home

hero:
  name: Rilavo
  text: Stateless Credential Verification
  tagline: Verify AI agent authorizations offline — no network call, no database, no liability.
  actions:
    - theme: brand
      text: Get Started
      link: /tutorials/verify-first-credential
    - theme: alt
      text: View on GitHub
      link: https://github.com/rilavo/rilavo

features:
  - title: Offline Verification
    details: Credentials verify with zero network calls. Only a cached issuer directory entry is needed.
  - title: Proof-of-Possession
    details: Every request is signed by the agent's private key, binding the credential to the caller.
  - title: Fail-Closed Security
    details: Every failure path (revocation, replay, clock skew) fails closed by default.
  - title: Multi-Language SDKs
    details: TypeScript, Python, Go, and framework integrations (Next.js, Express, FastAPI).
  - title: Product Ready
    details: Rate limiting, tiered metering, SLA monitoring, and developer dashboard.
  - title: Open Protocol
    details: Specification-first development with public decision logs and versioned spec.
