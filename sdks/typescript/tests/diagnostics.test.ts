import { test } from "node:test";
import assert from "node:assert/strict";
import { EXPLANATIONS, formatExplanation } from "../src/diagnostics";

const CODES = Object.keys(EXPLANATIONS);

test("all 14 reason codes have explanations", () => {
  const expected = [
    "audience_mismatch", "expired", "not_yet_valid",
    "unknown_issuer", "key_not_valid_at_issuance", "invalid_signature",
    "malformed_credential", "unrecognized_version", "missing_field",
    "replay_detected", "revoked", "revocation_state_unavailable",
    "proof_of_possession_failed", "scope_mismatch",
    "delegation_not_permitted",
  ];
  for (const code of expected) {
    assert.ok(EXPLANATIONS[code], `missing: ${code}`);
  }
});

test("all explanations have non-empty fields", () => {
  for (const [code, exp] of Object.entries(EXPLANATIONS)) {
    assert.ok(exp.summary.length > 10, code);
    assert.ok(exp.likely_causes.length >= 2, code);
    assert.ok(exp.remediation.length >= 1, code);
    assert.ok(exp.doc_pointer.length > 5, code);
  }
});
