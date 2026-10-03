# Security Policy — Rilavo Protocol

## Threat model traceability matrix (P-22)

Source of truth: `docs/wave_2/22_SECURITY_THREAT_MODEL.md` (STRIDE). Every
threat row maps to named tests in this repository's suite — if a test is
deleted or renamed, `tests/test_security_matrix.py` fails and this document
must be updated in the same change. The authoritative mechanism descriptions
live in the Core Specification; this table is the verification index.

| STRIDE | Threat | Mechanism | Verifying test(s) |
|---|---|---|---|
| Spoofing | Credential presented without the agent's private key | Proof-of-possession (P-07) | `test_copied_credential_alone_is_inert`, `test_wrong_agent_key_fails_pop`, `test_pop_binds_to_method_path_and_action` |
| Spoofing | Fake credential claiming a real issuer | Signature verification against published key (P-11) | `test_unknown_issuer_rejected`, `test_signature_verifies_over_jcs_canonical_payload_via_published_key`, `test_post_compromise_credentials_invalidated_retroactively` |
| Tampering | Modifying any field of a signed credential | Any field change invalidates the signature (P-06/P-11) | `test_tampering_any_field_invalidates_signature[*]`, `test_present_ver_is_inside_the_signed_payload` |
| Tampering | Retroactive edits to revocation-log history | Hash-chained log (P-09) | `test_hash_chain_detects_history_rewrite`, `test_intact_chain_verifies` |
| Repudiation | Verifier denies having accepted a credential | Audit receipts, hash-bound (P-10) | `test_accept_records_audit_receipt_without_full_contents` |
| Info Disclosure | Learning more about a principal than necessary | Minimum-disclosure field design (P-13); receipts store hashes only (P-10) | `test_accept_records_audit_receipt_without_full_contents`, `test_credentials_for_different_audiences_do_not_share_correlatable_state` |
| Info Disclosure (residual, OPEN) | Cross-verifier correlation via reused `sub`/`agt` values | Named honestly in P-13 — recommendation, not yet enforcement | Measurement: `test_detect_finds_known_collisions`, `test_mode_on_scopes_identifier_per_relationship` (optional mitigation mode, OFF by default) |
| Denial of Service | Revocation-log unavailability exploited to force acceptance | Fail-closed default (P-09) | `test_unreachable_revocation_log_fails_closed`, `test_stale_revocation_cache_fails_closed` |
| Denial of Service | Issuer outage blocking verification | Stateless verification against cached keys (P-15) | `test_T1_blocks_run_in_sequence` (fully offline verify), `test_valid_credential_is_accepted` |
| Elevation of Privilege | One action-class used for another | Exact-match scope (P-07) | `test_scope_mismatch_rejected_exact_match_only`, `test_wildcard_never_matches` |
| Elevation of Privilege | Credential presented to a different verifier | Audience binding (P-07) | `test_credential_presented_to_wrong_verifier_rejected` |

Additional structural guards beyond the original P-22 table:

- Version confusion: `test_ver_2_rejected_with_unrecognized_version`,
  `test_delegation_depth_nonzero_rejected_at_v0` (P-26 / Wave 6 gate).
- TTL ceiling: `test_ttl_never_exceeds_four_hours` (P-06).
- Product boundary: enforced structurally by
  `rilavo-commercial/tests/test_boundary.py`.

## Explicitly out of scope (hard boundary, per P-22)

A malicious or compromised agent that is correctly authorized and behaving
badly is not defended against. Rilavo answers "was this agent allowed to try
this" — never "should this agent be trusted to behave well."

## How the protocol/product boundary limits impact

Product (`rilavo-commercial/`) reaches the protocol exclusively through
the published HTTP API — enforced structurally by its boundary test suite.
Consequences:

- A compromise of Product code cannot forge credentials: signing
  keys never exist inside Product process boundary.
- Platform authentication (API keys) gates Product's own door only;
  issued credentials remain plain v0 credentials any verifier accepts.
- Raw protocol telemetry is architecturally unreachable internally except
  through the time-boxed, logged incident exception measured by the E-27
  scorecard (see `enforcement_scorecard.py`).

## Reporting a vulnerability (responsible disclosure)

- Contact: **security@rilavo.example** *(placeholder format — no public
  inbox is operated yet; reserved for when one exists)*.
- Disclosure window: **OPEN** — deliberately unset pending legal review
  (P-23/E-13). No number is committed here because naming one carelessly is
  worse than leaving it open. Until legal sets the window, reports receive
  acknowledgment and status updates on a best-effort basis.

## Re-audit trigger

Any change to P-06, P-07, or P-09 requires re-passing every STRIDE category
above and re-running the full suite including the conformance and boundary
files. This is a required re-pass, not an optional review.
