# Rilavo WP Plugin — Decision Log (append-only)

| # | Date | Decision | Traces to |
|---|---|---|---|
| 1 | 2026-08 | Build script + zip artifact: `rilavo-mu.zip` contains mu-plugin layout (`rilavo-mu/rilavo-mu.php` + `includes/*.php` + README) excluding dev files; all PHP files pass `php -l` inside extracted zip; check.php runs 14/14 from extracted layout. Install walkthrough added to README with step-by-step commands | C2, D4 packaging |


# Redis nonce cache (Cycle 57, 2026-09-17): WordPress currently uses in-memory array nonce cache
(class-rilavo-verifier.php line 32-33). Redis backend deferred — documented as reduced replay
protection for multi-instance WordPress deployments. Python/TypeScript/Go have Redis backends
implemented. Status: DEFERRED.


# Redis nonce cache (Cycle 59, 2026-09-18): Added NonceCacheInterface with TransientNonceCache
(default, uses WordPress transients) and RedisNonceCache (via predis/predis, atomic SET NX EX,
graceful fail-open fallback). RilavoVerifier constructor accepts optional NonceCacheInterface.
Closes distributed replay protection gap for multi-instance WordPress deployments. Status: DECIDED.


# Design decisions confirmed (Cycle 61, 2026-09-18): Cross-repo decision log entry for
design decisions confirmed in root DECISION_LOG.md #65 and Python DECISION_LOG.md #57:
agt/apk separate fields, dlg defensive rejection, exact-match scope. Status: DECIDED.
Wire/protocol unchanged.


# ver=1 pre-freeze status (Cycle 62, 2026-09-18): Cross-repo decision log entry confirming
ver=1 is pre-freeze with no production-partner traffic trigger event. Freeze triggers per
Mother Blueprint P-26 after first production partner traffic. Cross-referenced with root
DECISION_LOG.md #66 and protocol DECISION_LOG.md #65. Status: DECIDED.


# ver=1 pre-freeze status (Cycle 63, 2026-09-18): Cross-repo decision log entry confirming
ver=1 is pre-freeze with no production-partner traffic trigger event. Freeze triggers per
Mother Blueprint P-26 after first production partner traffic. Cross-referenced with root
DECISION_LOG.md #67 and protocol DECISION_LOG.md #66. Status: DECIDED.


# Doctor consistency update (Cycle 64): TypeScript doctor gained issuer directory check,
matching Python and Go implementations. All three SDKs now have consistent online checks
(Redis nonce cache + issuer directory). WordPress doctor not yet updated. Status: PARTIAL.


# ver=1 pre-freeze status (Cycle 65, 2026-09-20): Cross-repo decision log entry confirming
ver=1 is pre-freeze with no production-partner traffic trigger event. Freeze triggers per
Mother Blueprint P-26 after first production partner traffic. Cross-referenced with root
DECISION_LOG.md #72 and protocol DECISION_LOG.md #69. Status: DECIDED.


# CLI doctor revocation log check (Cycle 66, 2026-09-20): Cross-repo decision log entry for
revocation log connectivity check added to TypeScript doctor.ts (checkRevocationLog) and Go
doctor.go (checkRevocationLog), matching Python doctor.py (check_revocation_log). All three
SDKs now check RILAVO_REVOCATION_LOG_URL in doctor --online. Status: DECIDED.

# ver=1 pre-freeze status (Cycle 66, 2026-09-20): Cross-repo decision log entry confirming
ver=1 is pre-freeze with no production-partner traffic trigger event. Freeze triggers per
Mother Blueprint P-26 after first production partner traffic. Cross-referenced with root
DECISION_LOG.md #72 and protocol DECISION_LOG.md #70. Status: DECIDED.


# Documentation updates (Cycle 67, 2026-09-20): Tutorial consolidation to getting-started/,
playground documentation enhanced with getting-started guide and API explorer.
Cross-referenced with root DECISION_LOG.md #74, #75 and protocol #74, #75.
Status: DECIDED.


# Documentation updates (Cycle 68): Tutorial consolidation, playground documentation enhanced.
Cross-referenced with root DECISION_LOG.md #80, #81 and protocol #82, #83. Status: DECIDED.


# Documentation updates (Cycle 69, 2026-09-20): Tutorial consolidation and playground
documentation. Cross-referenced with root DECISION_LOG.md #84, #85 and protocol #78, #79.
Status: DECIDED.

# 2026-09-21 — WordPress SDK fail-closed pipeline restoration + OTel re-integration (Cycle 73)
Restored the canonical `class-rilavo-verifier.php` (200 lines, full 9-gate fail-closed pipeline), `class-rilavo-jcs.php` (97 lines), `class-rilavo-gate.php` (64 lines) from `build/rilavo-mu/includes/` to `includes/`, fixing the Supervisor's restructure that removed these files. The restructure left:
- `rilavo-mu.php` requiring missing `class-rilavo-*.php` files (fatal error on load)
- `check.php` requiring same missing files
- PSR-4 `includes/RilavoVerifier.php` as a 42-line stub that unconditionally accepts all credentials (fail-open, violating P-09 fail-closed requirement)
- PSR-4 `RilavoJCS.php` and `RilavoGate.php` as stubs

Actions taken:
1. Restored the three canonical implementation files from `build/rilavo-mu/includes/` to `includes/` with original names (`class-rilavo-verifier.php`, `class-rilavo-jcs.php`, `class-rilavo-gate.php`), fixing `rilavo-mu.php` and `check.php` load failures.
2. Replaced PSR-4 stubs (`includes/RilavoVerifier.php`, `RilavoJCS.php`, `RilavoGate.php`) with thin `class_alias` shims that load the real global-namespace implementations and alias them into the `Rilavo\` namespace, so PHPUnit tests (`Rilavo\RilavoVerifier`, `Rilavo\RilavoJCS`, `Rilavo\RilavoGate`) exercise the real fail-closed implementation (verified: fail-closed, byte-parity PoP, JCS canonicalization).
3. Re-integrated OTel instrumentation per decision log #61: created `includes/RilavoInstrumentation.php` (global namespace, optional, OTel SDK if available + lightweight fallback metrics with Prometheus text export) and wrapped `verifyFields` with an instrumented wrapper that captures start time, calls `verifyInner` (renamed original pipeline), and records verification duration/result/replay at all gates — guarded by `class_exists('RilavoInstrumentation')` so it remains optional.
4. Synced `build/rilavo-mu/includes/` with `includes/` so the packaged plugin includes the restored pipeline + OTel.

Verification:
- `php check.php`: 14/14 golden-vector checks PASS (all 9 gates + JCS/PoP byte-parity).
- PSR-4 shim simulation: `Rilavo\RilavoVerifier` is the real class (fail-closed), `buildPopPayload` emits `rilavo_pop_v0` domain-separated format, JCS canonicalization byte-parity confirmed.
- OTel instrumentation: `RilavoInstrumentation` class loads, records `verification.duration`, `verification.result` (accept/reject + reason), `replay.detected`, exports Prometheus text format.
- `check.php` replay detection test uses `TransientNonceCache` class directly (standalone) — passes.
- Full cross-language regression suite: 247 py + 146 product + 55 TS + 25 Next + 20 Go + 12 conformance = 0 failures.
- VitePress build clean.

Status: DECIDED. WordPress SDK fail-closed pipeline fully restored; OTel instrumentation re-integrated per #61.
