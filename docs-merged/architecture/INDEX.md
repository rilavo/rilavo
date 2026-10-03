# Rilavo Docs Hub

Single entry page for everything a developer needs. Start at the top; each
link was verified to resolve inside this repository.

## Start here
- **What is Rilavo?** — [top-level README](../README.md) (compression test, architecture map, 5-minute quickstart)
- **Security & disclosure** — [SECURITY.md](../SECURITY.md) · [threat-model summary](threat_model_summary.md)

## Quickstart & tutorials
1. [T1 — Verify your first credential](tutorials/T1-verify-your-first-credential.md) (10 min, offline)
2. [T2 — Self-host an issuer](tutorials/T2-self-host-an-issuer.md)
3. [T3 — Integrate the SDK into a mock checkout](tutorials/T3-mock-checkout.md)
4. [T4 — Product metering walkthrough](tutorials/T4-product-metering.md)
- All tutorials: [docs/tutorials/](tutorials/index.md)

## Framework guides
| Stack | Integration | Scaffold it |
|---|---|---|
| Next.js | [`@rilavo/next` middleware](../packages/rilavo-next) | `rilavo init --framework nextjs` |
| FastAPI | [`rilavo.fastapi` dependency](../rilavo-protocol/src/rilavo/fastapi.py) | `rilavo init --framework fastapi` |
| Express | `@rilavo/sdk` gate adapter via scaffolder | `rilavo init --framework express` |
| Go net/http | [middleware + example](../packages/rilavo-go/README.md) | — |
| WSGI / ASGI (any Python) | [`rilavo.middleware`](../rilavo-protocol/src/rilavo/middleware.py) | — |
| WordPress | [must-use plugin zip](../packages/rilavo-wp/README.md) | build script |
| More examples | [examples gallery](../examples/) (middleware, MCP gating, multi-tenant onboarding) | — |

## Install
- One command: `./install.sh [--prefix DIR]` (repo root)
- Docker: `deploy/embedded`, `deploy/selfhosted`, `deploy/hosted` walkthroughs in [rilavo-protocol/deploy/](../rilavo-protocol/deploy/)
- Packaging status: [PACKAGING_PLAN.md](../PACKAGING_PLAN.md)

## Trust discovery (proposal)
- [`.well-known/rilavo` format proposal](p3a1_discovery_format.md) · [JSON schema](p3a1_discovery_schema.json)

## Governance
- Decision logs: [protocol](../rilavo-protocol/DECISION_LOG.md) · [product](../rilavo-product/DECISION_LOG.md) · compiled view (`scripts/compile_decision_log.py`)
