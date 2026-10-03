# Rilavo Examples Gallery

| Example | Traces to | What it shows |
|---|---|---|
| `verifier_middleware/` | P-18 | Framework-agnostic dual-acceptance middleware (WSGI/ASGI sketches): OAuth bearer OR Rilavo credential, reports which mechanism authenticated |
| `mcp_server/` | P-18 (MCP as first surface) | Sketch of an MCP server gating tool calls with exact-match credential checks; demonstrates single-use credentials per action |
| `multi_tenant_onboarding/` | E-08/E-07/E-14 | Onboard a platform customer: hashed API key minted once, tier limits, free allowance; fail-closed wrong-key demo |

Every example is executed by the test suites (`tests/test_examples_gallery.py`
in rilavo-protocol), so they cannot silently rot. Examples are presentation/
education artifacts — they add no protocol surface and no new source of truth.
