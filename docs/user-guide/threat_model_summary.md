# Rilavo Protocol — Threat Model Summary (P-22 traceability)

Derived mechanically from `docs/wave_2/22_SECURITY_THREAT_MODEL.md` (STRIDE
rows) cross-referenced against tests actually defined in
`rilavo-protocol/tests/`. The Status column reflects suite reality — nothing
is claimed covered without a named, existing test.

| Category | Threat | Mitigating module(s) | Verifying test(s) | Status |
|---|---|---|---|---|
| Spoofing | an attacker presents a credential without holding the matching agent private key. | pop middleware/verifier (P-07) | `test_copied_credential_alone_is_inert`, `test_pop_binds_to_method_path_and_action`, `test_wrong_agent_key_fails_pop` | COVERED by named tests |
| Spoofing | an attacker signs a fake credential claiming to be the issuer. | issuer signature verification (P-11) | `test_signature_verifies_over_jcs_canonical_payload_via_published_key`, `test_unknown_issuer_rejected` | COVERED by named tests |
| Tampering | modifying any field of a signed credential. | signature invalidation (P-06/P-11) | `test_present_ver_is_inside_the_signed_payload`, `test_tampering_any_field_invalidates_signature` | COVERED by named tests |
| Tampering | retroactively editing revocation-log history. | hash chaining (P-09) | `test_hash_chain_detects_history_rewrite`, `test_intact_chain_verifies` | COVERED by named tests |
| Repudiation | a verifier later denies having accepted a specific credential. | audit receipts (P-10) | `test_accept_records_audit_receipt_without_full_contents` | COVERED by named tests |
| Information Disclosure | a verifier or issuer learning more about a principal than necessary. | minimum disclosure (P-13) | `test_credentials_for_different_audiences_do_not_share_correlatable_state` | COVERED by named tests |
| Information Disclosure | correlating a principal across verifiers via reused `sub`/`agt` values. | correlation instrumentation (OPEN gap measurement) | `test_detect_finds_known_collisions`, `test_mode_on_scopes_identifier_per_relationship` | COVERED by named tests; RESIDUAL GAP -- OPEN per P-13 |
| Denial of Service | revocation-log unavailability exploited to force acceptance of a credential that should be rejected. | fail-closed default (P-09) | `test_stale_revocation_cache_fails_closed`, `test_unreachable_revocation_log_fails_closed` | COVERED by named tests |
| Denial of Service | issuer outage blocking new issuance. | stateless decoupling (P-15) | `test_T1_blocks_run_in_sequence`, `test_valid_credential_is_accepted` | COVERED by named tests |
| Elevation of Privilege | a credential scoped to one action-class used for another. | exact-match scope (P-07) | `test_scope_mismatch_rejected_exact_match_only`, `test_wildcard_never_matches` | COVERED by named tests |
| Elevation of Privilege | a credential presented to a different verifier than intended. | audience binding (P-07) | `test_credential_presented_to_wrong_verifier_rejected` | COVERED by named tests |
