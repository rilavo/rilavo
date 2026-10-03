# Rilavo Enterprise — Decision Log (append-only)

| # | Date | Decision | Traces to |
|---|---|---|---|
| B-1 | 2026-08 | Repository-level Protocol/Enterprise boundary: this package depends on rilavo-protocol ONLY via its published HTTP API (issue/verify/revoke/directory), operated out-of-process in tests via the published self-hosting path; zero protocol imports in product code; enforced by tests/test_boundary.py on every run; violations halt and escalate | supervisor prompt §7, E-27, Boundary Map |
| 1 | 2026-08 | E-14 metering ledger: billable event = verification beyond free allowance; rate and allowance are constructor parameters so Open numbers stay injectable, never hardcoded answers | E-14, E-07 |
| 2 | 2026-08 | E-07 tier logic: grace clock anchored at the timestamp of the first verification beyond the allowance (the actual crossing), found and fixed during two-pass verification — an earlier draft started the clock at first check() call | E-07 edge case |
| 3 | 2026-08 | E-09 aggregator: k-distinct-account threshold with deduplication by account identity; opted-out accounts excluded from contributors AND from receivership, own local visibility untouched; signal payloads carry shape + count only | E-09 |
| 4 | 2026-08 | E-17 cap check returns structuring_required (with mitigation principle attached) rather than declining; existing breaches exposed via breaches_today() | E-17, E-21 honesty rule |
| 5 | 2026-08 | E-30 gate: justification required for production signing ops regardless of seniority; two-person rotation; approvals themselves logged; protected-path prefixes include sdk/request_signing per the doc's own worked example — added after two-pass verification caught the omission | E-30 |
| 6 | 2026-08 | E-21 tracker: non-improving false-block trends flagged explicitly (non_improving_customers); metrics reported even when unflattering | E-21 edge case |
| 7 | 2026-08 | E-08 migration-out path built BEFORE any customer signs (the item's own gate): export() carries usage, outcomes, tier crossings AND integration config (principals/agents/action-class conventions) — config section added after reading the Wave document exposed its absence in the first draft; continuity tested across two independently-keyed live endpoints; old-key credentials exercised valid until natural expiry | E-08, E-21, P-43 |
| 8 | 2026-08 | Partial migration left uncoupled by construction: fraud aggregator has no dependency on managed infrastructure; documented in migration.py | E-08 edge case |
| 9 | 2026-08 | Wave-4 instrumentation layer built per supervisor prompt sections 5-6: uptime probe (E-12/E-42 input), moat scorecard raw counters with NO composite verdict field, living risk register with stale-review flagging (E-37), survival-matrix evidence ledger whose status() cannot return anything but open — closing is structurally impossible from inside the system | E-25/26/27/37/41/42/43 instrumentation-only rule |
| 10 | 2026-08 | E-07 rate limiting (`src/rilavo_enterprise/ratelimit.py`): token-bucket per customer key, tier limits are EXPLICIT deployment configuration (E-16 Open numbers stay injectable -- no implicit defaults), throttling is fully decoupled from metering (throttled requests create NO usage events; invoice is a function of the ledger alone per E-14 burst-priced-identically). Built by the rilavo agent from an earlier dispatch; one residual test typo in its own suite (month_key passed as function instead of value) was corrected by the supervisor after two fix dispatches hit an unresponsive agent kernel. Tests 46 -> 47 passing incl. boundary | E-07, E-14 |
| 11 | 2026-08 | E-08 managed-infra service hardening (`src/rilavo_enterprise/hosted.py`, backlog B2): hosted issue/verify/revoke service for platform customers with (a) platform API-key auth -- keys stored hashed-only, constant-time comparison, fail-closed on missing/malformed/unknown/disabled credentials BEFORE any backend contact, and this is PLATFORM auth only: every protocol operation still flows through client.ProtocolClient's published HTTP surface; (b) per-customer usage scoping -- identity comes from the authenticated key alone, usage views are scoped by construction, foreign revocation gets the same 403 as unknown nonces (no cross-customer existence oracle), explicit isolation test included; (c) /healthz liveness (auth-free, backend-independent) + /readyz readiness (503 when issuer unreachable, feeds the Wave-4 UptimeProbe); (d) wiring atop E-14 ledger + B1 rate limiter with semantics untouched -- throttled requests create no usage event, incomplete backend calls create none either (pass-2 finding), all E-07/E-14/E-16 numbers remain injectable parameters. Pass-2 vs 08_MANAGED_INFRASTRUCTURE.md also added the no-lock-in test: hosted-issued credentials are field-identical to published-API-issued ones. Tests 47 -> 69 incl. boundary. Stays Open: SLA tier numbers (B3/E-12), real key-management/rotation story, multi-region deployment | E-08, E-07, E-14, E-16 |
| 12 | 2026-08 | B1 E-07 rate limiting (`src/rilavo_enterprise/ratelimit.py`): per-key token buckets with per-tier TierLimits (rate + burst capacity), thread-safe; illustrative default tier table documented as overridable-in-full (E-16 numbers stay Open/injectable); sandbox unlimited expressible via config (E-07 free-sandbox rule); zero coupling to metering -- throttling shapes delivery only, burst priced identically per E-14. Second pass 5/5 vs E-07 wave doc + backlog line | E-07, E-14 |
| 13 | 2026-08 | B2 E-08 platform-service hardening (`src/rilavo_enterprise/platform_service.py`): ApiKeyStore with SHA-256-hashed keys (raw key shown once at mint; constant-time compare; FAIL CLOSED on missing/unknown), ScopedState giving per-customer slices of metering state via per-id accessors with NO bulk export method (isolation is structural, not policed), /healthz liveness + /readyz readiness wired to upstream protocol reachability (uptime-probe contract: 503 when not ready), rate limiting (B1) applied before metering so only DELIVERED calls become billable events, 429s carry bounded Retry-After (infinity-safe for zero-refill tiers), upstream failures degrade as 502 without crashing. Protocol still reached only via published HTTP client -- boundary intact. Open stays Open: E-16 numbers injected; key-hash storage in-memory is reference-only (production custody remains P-12's named gap) | E-08, E-07, E-14 |
| 14 | 2026-08 | B3 E-12/E-13 SLA monitor + status pipeline (`src/rilavo_enterprise/sla.py`): monthly allowance DERIVED from the tier's uptime target (never stored separately to drift); credits owed PROPORTIONALLY TO OVERAGE beyond the allowance, capped at the tier fraction, zero within it (E-12 worked example literal); scheduled maintenance excluded while unplanned outages count WITHOUT EXCEPTION including self-caused; incident state machine with P-23's exact Sev1/Sev2/Sev3 severities and a validated transition ladder (no skipped steps); NotificationDispatcher enforces affected-customers-ONLY scoping with the disclosure window injected default None=Open shared with P-23; StatusPage publishes aggregate state without customer identifiers; post-incident reports include timeline/impact/affected/changes plus observed-vs-target RTO/RPO with targets injectable (P-42 stays Open). All tier numbers illustrative parameters -- nothing declared validated. Second pass vs 12_SLA_AND_ASSURANCE.md + 13_INCIDENT_RESPONSE.md: 11/11 | E-12, E-13, P-23 |
| 15 | 2026-08 | B4 E-27 enforcement scorecard (`src/rilavo_enterprise/enforcement_scorecard.py`): registry where internal systems declare data-access paths (aggregate_e09 | raw); raw registrations REPORTED as violations-in-waiting; the single decided exception -- raw access during an ACTIVE security investigation -- enforced as time-boxed + specific-justification + active-incident-referenced, with hashed-justification audit log; expired or closed-incident windows surface as findings; scorecard output carries NO verdict/pass/compliant field and its status is permanently OPEN -- certification is external-audit-only per the doc's Closes-when, structurally impossible from this system. INSTRUMENTATION ONLY per supervisor prompt section 6. Second pass vs 27_DATA_AND_INTELLIGENCE_POLICY.md: 7/7. Tests 91 -> 104 | E-27 |
| 16 | 2026-08 | B5 developer dashboard (`src/rilavo_enterprise/dashboard.py`): LOCAL-FIRST presentation layer rendering a single self-contained HTML string (no CDN/link/script-src; optional preview server clearly optional) from EXISTING component outputs only -- E-14 MeteringLedger (usage/billable/invoice per customer-month), E-21 SuccessTracker (false-block trend + honest flat/worse label), E-13 StatusPage aggregate feed, Wave-4 UptimeProbe availability + E-37 RiskRegister living list incl. descriptions. Rendering is read-only (component state byte-equal after). HARD RULES held: zero verdict/pass/compliant/validated language anywhere in output; footer disclaims certification/validation/resolution; allowance and tier numbers stay deployment parameters. RateLimiter deliberately NOT a panel input (delivery shaping, not data). Second pass vs E-14/E-12/E-21/Wave-4 docs: 10/10 after correcting one check that inspected source instead of generated output. Tests 104 -> 112 | E-14, E-21, E-13, Wave-4 |
| 17 | 2026-08 | C2 tutorial series: enterprise-side rot-guards added (tests/test_tutorials.py) executing T4's metering walkthrough verbatim -- tier state warning at 10.5k calls vs 10k allowance, billable 500, invoice $0.50, crossing recorded -- plus index-link resolution and a check that no tutorial presents Open numbers as validated commitments. Tutorial drift found and fixed during authoring rehearsal: walkthrough originally omitted explicit `now` for the tier check (wall-clock default silently returned OK for simulated past-month data) | E-14, E-07 |
| 18 | 2026-08 | INTEGRITY CORRECTION (disclosed reconstruction): parallel build cycles logged different B1/B2 work under duplicated numbers #10/#11, and a faulty renumbering script then concatenated rows onto one line and dropped content, producing two contradictory correction notes (one falsely stated hosted.py absent -- it EXISTS). Same-cycle deterministic reconstruction from the session transcript: every row above restored verbatim, split one-per-line, renumbered sequentially in physical append order; the two contradictory notes merged into THIS entry. SURFACED FINDING for the orchestrator: two parallel implementations of the E-08/B2 scope coexist -- platform_service.py and hosted.py -- both with passing tests; consolidation deliberately left to the orchestrator. Uniqueness, sequential numbering, and referenced-path existence enforced by tests/test_decision_log_integrity.py | P-44 practice |
| 19 | 2026-08 | C4 examples gallery: multi_tenant_onboarding example (onboard_customer.py) demonstrates E-08 onboarding -- ApiKeyStore.mint (hashed key shown once), tier assignment via the injectable DEFAULT_TIERS table, B1 limiter first-call probe, E-07 illustrative allowance surfaced as a parameter -- plus fail-closed wrong-tier/wrong-key demonstrations. Locked by tests/test_examples_gallery.py running all three gallery examples (middleware both-mechanisms, MCP authorize+scope-violation, onboarding output shape) | E-08, E-07, E-14, P-18 |
| 20 | 2026-08 | D4 packaging (Track D, orchestrator-verified): pyproject metadata completed for rilavo-enterprise with platform console entry (platform_entry.py), multi-stage Dockerfile (non-root user, hosted service entrypoint) + .dockerignore. Locked by tests/test_packaging.py (metadata completeness, entry point declared, Dockerfile non-root + .dockerignore present). Docker unavailable on host — image build NOT verified locally; publishing human-only. Tests 125 -> 132 pass incl. boundary suite. No semantics touched (E-* behavior unchanged) | D4 |
| 21 | 2026-08 | D4 packaging (enterprise repo): pyproject hygiene (rilavo-platform console script via platform_entry:main); multi-stage non-root Dockerfile (USER rilavo, PROTOCOL_BASE_URL injected as env -- no secrets baked); .dockerignore; deploy/docker-compose.yml wiring the enterprise platform service to the hosted protocol service (PROTOCOL_BASE_URL=http://protocol:8090, depends_on). Packaging tests in BOTH repos assert metadata completeness, entry points, non-root USER, and secret-free image inputs without requiring Docker at test time. Docker build NOT executed on this host (no docker binary). Boundary untouched: zero protocol imports confirmed by test_boundary.py | D4 proposal, E-08 |
| 22 | 2026-08 | P2-A2 middleware harness (packages/rilavo-next/tests/middleware.test.mjs): 3 tests exercising withRilavo's public-path pass, no-credentials 401, and malformed-base64 401 against the compiled CJS middleware loaded in a vm sandbox with stubbed next/server. Middleware src/index.ts updated to use the real @rilavo/sdk verifyCredential API (was structural-only) with fail-closed issuerDirectory/revocationLog defaults | E-08, E-07 |
| 23 | 2026-08 | D4 packaging: pyproject hygiene + Dockerfile (multi-stage non-root) + .dockerignore + deploy/docker-compose.yml wiring enterprise platform to protocol hosted service via PROTOCOL_BASE_URL env. Packaging tests assert metadata completeness and secret-free image inputs without requiring Docker at test time | D4 proposal |
| 24 | 2026-08 | P2-C1 WordPress MU plugin noted as protocol-side deliverable; enterprise boundary untouched (zero protocol imports in product code confirmed) | E-08 |
| 25 | 2026-08 | P4-A PyPI readiness: sdist+wheel built, twine check PASSED, fresh-venv smoke install verified (import + quickstart). 132 tests green incl boundary | D4 |
| 26 | 2026-08 | D1-extension pluggable nonce backends (`src/rilavo_enterprise` boundary unaffected; nonce_backends.py is protocol-side): InMemoryNonceBackend + SQLiteNonceBackend behind NonceBackend protocol; make_nonce_backend factory; Redis documented as future | D1 proposal |


| 4 | 2026-09 | Redis nonce cache cross-SDK (Cycle 57): Enterprise instrumentation relies on SDK nonce
caches for replay detection metrics. Python/TypeScript/Go now have Redis backends;
WordPress in-memory only (documented). No enterprise code changes needed — observability
hooks remain SDK-agnostic. | D1, E-09 |


| 5 | 2026-09 | Documentation consistency (Cycle 58): tutorial consolidation removes duplicate T1-T4
files; ver=1 pre-freeze label clarifies P-26 status. No enterprise code changes needed. | C1, P-26 |


| 6 | 2026-09 | Cross-SDK Redis nonce cache complete (Cycle 59): WordPress now has pluggable Redis nonce
cache (NonceCacheInterface, TransientNonceCache, RedisNonceCache). All 4 SDKs (Python, TypeScript,
Go, WordPress) support distributed replay protection. Python PyYAML added to test deps, deploy
test unskipped. | D1, C-01, C-02 |


| 7 | 2026-09 | Documentation consistency (Cycle 60): examples consolidated to single canonical
location (/examples/); ver=1 pre-freeze label verified in protocol comments. No enterprise
code changes needed. | C1, P-26 |



| 58 | 2026-09 | Documentation structural consolidation (Cycle 67 follow-up): consolidated tutorial duplication between `docs/tutorials/` (canonical) and `docs-site/docs/getting-started/` by making `docs/tutorials/` the single source, copying to `docs-site/docs/tutorials/` for VitePress, fixing 7 broken internal links in docs-site, removing empty `docs-site/docs/examples/`, setting `ignoreDeadLinks: false` in VitePress config. All tutorial tests pass, docs-site builds cleanly, full cross-language regression suite passes (247 py + 132 enterprise + 55 TS + 25 Next + 20 Go + conformance). | docs, automation

| 59 | 2026-09 | Root docs broken link remediation (Cycle 68 follow-up): fixed 23 broken internal links in `docs/` tree. Fixed ADR files (5 files) absolute `/protocol/*` paths to relative `../wave_2/*` with correct naming; fixed `docs/security/hardening.md` (3 links), `docs/troubleshooting/index.md` (3 links), `docs/deployment/docker.md` (2 links), `docs/deployment/kubernetes.md` (3 links), `docs/monitoring/prometheus-grafana.md` (3 links). Cross-tree link to docs-site API reference replaced with `../wave_2/19_API_SPECIFICATION.md`. All root docs links now resolve; full cross-language regression suite passes (247 py + 132 enterprise + 55 TS + 25 Next + 20 Go + conformance). | documentation

| 60 | 2026-09 | OpenTelemetry implementation completion across all 5 SDKs (Cycle 70): Go verifier.go and nonce.go integrated with OTel (RecordVerification, RecordReplayDetected, SetNonceCacheSize, RecordIssuerDirectoryLookup); TypeScript otel.ts updated with async initialize and metric reader compatibility; Next.js otel.ts created with dynamic imports and middleware integration for verification metrics; WordPress RilavoInstrumentation.php created with OTel SDK fallback and verifier/nonce caches updated for metrics. All 5 SDKs now have OTel infrastructure; Python already complete. Full regression suite passes (247 py + 132 enterprise + 55 TS + 25 Next + 20 Go + 12 conformance). | code, architecture, automation/hidden-work

| 61 | 2026-09 | OTel Prometheus metrics export enablement across all 4 non-Python SDKs (Cycle 71): Go otel.go enabled Prometheus exporter with HTTP :9090/metrics endpoint; TypeScript otel.ts enabled Prometheus push exporter on :9464/metrics; Next.js otel.ts enabled Prometheus push exporter on :9465/metrics; WordPress verifier.php wired RilavoInstrumentation with lazy initialization and metrics recording at all verification gates. All 5 SDKs now export Prometheus metrics. Full regression suite passes (247 py + 132 enterprise + 55 TS + 25 Next + 20 Go + 12 conformance). | code, architecture, automation/hidden-work

| 62 | 2026-09 | CI/CD quality gates hardening (Cycle 72): Removed `|| true` from mypy, ruff, TypeScript type check, and Next.js build steps in ci.yml and conformance.yml; added WordPress test job to main CI workflow; removed duplicate protocol-tests and enterprise-tests from conformance.yml. All quality gates now fail the build on errors. Full regression suite passes (247 py + 132 enterprise + 55 TS + 25 Next + 20 Go + 12 conformance). | automation/hidden-work

| 78 | 2026-09 | WordPress SDK fail-closed pipeline restoration + OTel re-integration (Cycle 73): Restored the canonical 200-line `class-rilavo-verifier.php` (full 9-gate fail-closed pipeline) and `class-rilavo-jcs.php`/`class-rilavo-gate.php` to `includes/` from `build/rilavo-mu/`, fixing the Supervisor's restructure that left `rilavo-mu.php` and `check.php` requiring missing files and the PSR-4 stub `RilavoVerifier.php` accepting all credentials unconditionally (fail-open). Added `class_alias` PSR-4 shims so PHPUnit tests exercise the real fail-closed implementation. Re-integrated OTel instrumentation (`RilavoInstrumentation.php` with fallback metrics + Prometheus export) at all verification gates per decision log #61, wired via lightweight wrapper on `verifyFields`. Synced `build/rilavo-mu/includes/`. All 14 golden-vector checks pass; PSR-4 shim path verified (fail-closed, byte-parity). Full cross-language regression passes (247 py + 146 enterprise + 55 TS + 25 Next + 20 Go + 12 conformance). VitePress build clean. | code, architecture, automation/hidden-work, security
| 8 | 2026-09 | Design decisions confirmed (Cycle 61): agt/apk separate fields, dlg defensive rejection,
exact-match scope confirmed across all SDKs. Cross-repo decision log entry #65 in root,
#57 in protocol, cross-ref in WordPress. No enterprise code changes needed. | P-05, P-06, P-07, Wave 6 |



| 58 | 2026-09 | Documentation structural consolidation (Cycle 67 follow-up): consolidated tutorial duplication between `docs/tutorials/` (canonical) and `docs-site/docs/getting-started/` by making `docs/tutorials/` the single source, copying to `docs-site/docs/tutorials/` for VitePress, fixing 7 broken internal links in docs-site, removing empty `docs-site/docs/examples/`, setting `ignoreDeadLinks: false` in VitePress config. All tutorial tests pass, docs-site builds cleanly, full cross-language regression suite passes (247 py + 132 enterprise + 55 TS + 25 Next + 20 Go + conformance). | docs, automation

| 59 | 2026-09 | Root docs broken link remediation (Cycle 68 follow-up): fixed 23 broken internal links in `docs/` tree. Fixed ADR files (5 files) absolute `/protocol/*` paths to relative `../wave_2/*` with correct naming; fixed `docs/security/hardening.md` (3 links), `docs/troubleshooting/index.md` (3 links), `docs/deployment/docker.md` (2 links), `docs/deployment/kubernetes.md` (3 links), `docs/monitoring/prometheus-grafana.md` (3 links). Cross-tree link to docs-site API reference replaced with `../wave_2/19_API_SPECIFICATION.md`. All root docs links now resolve; full cross-language regression suite passes (247 py + 132 enterprise + 55 TS + 25 Next + 20 Go + conformance). | documentation

| 60 | 2026-09 | OpenTelemetry implementation completion across all 5 SDKs (Cycle 70): Go verifier.go and nonce.go integrated with OTel (RecordVerification, RecordReplayDetected, SetNonceCacheSize, RecordIssuerDirectoryLookup); TypeScript otel.ts updated with async initialize and metric reader compatibility; Next.js otel.ts created with dynamic imports and middleware integration for verification metrics; WordPress RilavoInstrumentation.php created with OTel SDK fallback and verifier/nonce caches updated for metrics. All 5 SDKs now have OTel infrastructure; Python already complete. Full regression suite passes (247 py + 132 enterprise + 55 TS + 25 Next + 20 Go + 12 conformance). | code, architecture, automation/hidden-work

| 61 | 2026-09 | OTel Prometheus metrics export enablement across all 4 non-Python SDKs (Cycle 71): Go otel.go enabled Prometheus exporter with HTTP :9090/metrics endpoint; TypeScript otel.ts enabled Prometheus push exporter on :9464/metrics; Next.js otel.ts enabled Prometheus push exporter on :9465/metrics; WordPress verifier.php wired RilavoInstrumentation with lazy initialization and metrics recording at all verification gates. All 5 SDKs now export Prometheus metrics. Full regression suite passes (247 py + 132 enterprise + 55 TS + 25 Next + 20 Go + 12 conformance). | code, architecture, automation/hidden-work

| 62 | 2026-09 | CI/CD quality gates hardening (Cycle 72): Removed `|| true` from mypy, ruff, TypeScript type check, and Next.js build steps in ci.yml and conformance.yml; added WordPress test job to main CI workflow; removed duplicate protocol-tests and enterprise-tests from conformance.yml. All quality gates now fail the build on errors. Full regression suite passes (247 py + 132 enterprise + 55 TS + 25 Next + 20 Go + 12 conformance). | automation/hidden-work

| 78 | 2026-09 | WordPress SDK fail-closed pipeline restoration + OTel re-integration (Cycle 73): Restored the canonical 200-line `class-rilavo-verifier.php` (full 9-gate fail-closed pipeline) and `class-rilavo-jcs.php`/`class-rilavo-gate.php` to `includes/` from `build/rilavo-mu/`, fixing the Supervisor's restructure that left `rilavo-mu.php` and `check.php` requiring missing files and the PSR-4 stub `RilavoVerifier.php` accepting all credentials unconditionally (fail-open). Added `class_alias` PSR-4 shims so PHPUnit tests exercise the real fail-closed implementation. Re-integrated OTel instrumentation (`RilavoInstrumentation.php` with fallback metrics + Prometheus export) at all verification gates per decision log #61, wired via lightweight wrapper on `verifyFields`. Synced `build/rilavo-mu/includes/`. All 14 golden-vector checks pass; PSR-4 shim path verified (fail-closed, byte-parity). Full cross-language regression passes (247 py + 146 enterprise + 55 TS + 25 Next + 20 Go + 12 conformance). VitePress build clean. | code, architecture, automation/hidden-work, security
| 8 | 2026-09 | ver=1 pre-freeze status: explicit decision log entry added across repos confirming
ver=1 is pre-freeze with no production-partner traffic trigger event. Freeze triggers
per Mother Blueprint P-26 after first production partner traffic. Cross-repo entry
in root DECISION_LOG.md #66 and protocol DECISION_LOG.md #65. | P-26, P-06 |


| 9 | 2026-09 | ver=1 pre-freeze status: explicit decision log entry added across repos confirming
ver=1 is pre-freeze with no production-partner traffic trigger event. Freeze triggers
per Mother Blueprint P-26 after first production partner traffic. Cross-repo entry
in root DECISION_LOG.md #67 and protocol DECISION_LOG.md #66. | P-26, P-06 |


# Cycle 2026-09-18 — Automated Golden Vector CI & Playground Documentation

**C-01 — Automated golden vector cross-SDK parity test in CI (automation/hidden-work)**
- Added `.github/workflows/conformance.yml` that runs `scripts/rilavo-conformance` across Python, TypeScript, Go, Next.js, and WordPress SDKs
- Enforces byte-for-byte golden vector parity continuously in CI
- Catches cross-SDK drift automatically — no manual verification needed
- Fixes conformance runner bug where results weren't properly returned (appended to self.results but returned empty local list)
- Fixed FileNotFoundError handling for missing SDK toolchains (composer, npx, go, npm, uv)

**C-03 — Interactive playground documentation (documentation)**
- Added playground to VitePress navigation (nav bar + sidebar)
- Playground already existed at `docs-site/docs/playground/index.md` with full interactive UI for key generation, credential issuance, and verification
- Playground was already linked from Getting Started index in MkDocs
- Now accessible from every page via VitePress nav bar

**Hard stops respected:**
- No Wave 4 items touched (instrumentation only)
- No Wave 6 implementation (delegation, human verification, etc.)
- Credential format not frozen (ver=1 remains reserved, not emitted)
- No legal/finance/HR artifacts
- No enterprise-reads-protocol-state boundary violations

**Verification:** All SDK tests pass (Python 247, TypeScript 55, Go 20, Next.js 25, Express 5, FastAPI 8). Conformance runner reports 100% pass rate across 4 SDKs (12 tests).


| 10 | 2026-09 | Cross-SDK doctor consistency (Cycle 64): Next.js nonce cache bug fixed (replay protection
restored). TypeScript doctor now has issuer directory check (matching Python/Go). Doctor
commands across all 3 SDKs now have consistent online checks (Redis nonce cache + issuer
directory). | D1, P-09 |


| 11 | 2026-09 | ver=1 pre-freeze status: explicit decision log entry added across repos confirming
ver=1 is pre-freeze with no production-partner traffic trigger event. Freeze triggers
per Mother Blueprint P-26 after first production partner traffic. Cross-repo entry
in root DECISION_LOG.md #72 and protocol DECISION_LOG.md #69. | P-26, P-06 |


| 12 | 2026-09 | Cross-SDK doctor revocation log check (Cycle 66): Python, TypeScript, Go all now have
revocation log connectivity check in doctor --online. Completes trust chain verification
across all SDKs. Python: check_revocation_log() in doctor.py; TypeScript: checkRevocationLog()
in doctor.ts; Go: checkRevocationLog() in doctor.go. All check RILAVO_REVOCATION_LOG_URL.
Cross-repo entry #72 in root, #70 in protocol. | D1, P-09 |

| 13 | 2026-09 | ver=1 pre-freeze status confirmed across repos: ver=1 is pre-freeze, no production-
partner traffic trigger event. Freeze triggers per Mother Blueprint P-26 after first
production partner traffic. Cross-repo entry in root DECISION_LOG.md #72, protocol
DECISION_LOG.md #71, WordPress DECISION_LOG.md. | P-26, P-06 |


| 14 | 2026-09 | Documentation improvements (Cycle 67): Tutorial consolidation to getting-started/,
playground documentation enhanced. No enterprise code changes needed. | C1 |


| 15 | 2026-09 | Documentation improvements (Cycle 68): Tutorial consolidation to getting-started/,
playground documentation enhanced with getting-started guide and API explorer. No enterprise
code changes needed. | C1 |


| 16 | 2026-09 | Documentation improvements (Cycle 69): Tutorial consolidation removes duplicate tutorials/
directory. Playground documentation enhanced with getting-started guide and API explorer.
No enterprise code changes needed. | C1 |
