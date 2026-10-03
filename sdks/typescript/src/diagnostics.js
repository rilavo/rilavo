"use strict";
/**
 * Developer-UX diagnostics: human-readable explanations for every
 * verification rejection reason code. Parity with Python diagnostics.py.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.EXPLANATIONS = void 0;
exports.explainRejection = explainRejection;
exports.formatExplanation = formatExplanation;
exports.EXPLANATIONS = {
    audience_mismatch: {
        summary: "Credential audience does not match this verifier.",
        likely_causes: [
            "Credential issued for a different verifier.",
            "Verifier configuration audience mismatch.",
            "Wrong API endpoint for the credential held.",
        ],
        remediation: [
            "Request a new credential with the correct audience.",
            "Check your verifier_id configuration.",
        ],
        doc_pointer: "Core Spec section 6 step 1; P-07",
    },
    expired: {
        summary: "The credential has passed its expiration timestamp.",
        likely_causes: [
            "TTL has elapsed since issuance.",
            "Clock skew between issuer and verifier.",
            "Short-TTL credential was not used promptly.",
        ],
        remediation: [
            "Request a fresh credential from the issuer.",
            "Consider requesting longer TTLs if this happens frequently.",
            "Synchronize clocks using NTP.",
        ],
        doc_pointer: "Core Spec section 6 step 2; P-06 TTL ceiling",
    },
    not_yet_valid: {
        summary: "The credential issuance timestamp is in the future.",
        likely_causes: [
            "Issuer clock is ahead of verifier clock.",
            "Intentionally future-dated credential.",
            "NTP synchronization drift.",
        ],
        remediation: [
            "Wait until the credential becomes valid.",
            "Investigate clock synchronization between issuer and verifier.",
        ],
        doc_pointer: "Core Spec section 6 step 2; P-30",
    },
    unknown_issuer: {
        summary: "The credential references an issuer not found in the key directory.",
        likely_causes: [
            "Issuer has not registered its public key.",
            "Key directory unreachable or incomplete.",
            "Stale issuer identifier.",
        ],
        remediation: [
            "Verify the issuer public key is published in the key directory.",
            "Check network connectivity to the directory service.",
            "Confirm the iss field matches a known issuer fingerprint.",
        ],
        doc_pointer: "Core Spec section 6 step 3; P-17",
    },
    key_not_valid_at_issuance: {
        summary: "The credential iat falls after the signing key valid_until cutoff.",
        likely_causes: [
            "Issuer rotated its signing key but the agent cached the old one.",
            "Signing key was compromised and retroactively invalidated.",
            "Stale credential signed before rotation re-presented after cutoff.",
        ],
        remediation: [
            "Obtain a new credential signed under the current key.",
            "Clear cached old keys from local state.",
            "If you are the issuer, verify rotation completed successfully.",
        ],
        doc_pointer: "Core Spec section 6 step 4; P-12",
    },
    invalid_signature: {
        summary: "Ed25519 signature over canonicalized fields does not verify against the issuer public key.",
        likely_causes: [
            "One or more credential fields were modified after signing.",
            "The sig field was corrupted during transmission.",
            "A different key was used to sign than published in the directory.",
        ],
        remediation: [
            "Request a new credential without modifying any fields.",
            "Verify no proxy or middleware is altering the payload.",
            "Check for encoding issues (base64url padding).",
        ],
        doc_pointer: "Core Spec section 6 step 5; P-11 Ed25519",
    },
    malformed_credential: {
        summary: "The credential JSON could not be parsed or contains incorrect field types.",
        likely_causes: [
            "JSON is syntactically invalid (truncated, encoding error).",
            "Required field has wrong type (string vs integer).",
            "Base64url encoding of header is malformed.",
        ],
        remediation: [
            "Regenerate the credential from the issuer.",
            "Validate JSON structure against the v0 field list.",
            "Ensure no intermediate proxy stripped or modified the header.",
        ],
        doc_pointer: "Core Spec section 6 step 0; P-06 field contract",
    },
    unrecognized_version: {
        summary: "The credential carries a ver field not recognized by this verifier.",
        likely_causes: [
            "ver=2 or higher requires a newer verifier.",
            "Non-integer value placed in ver field.",
            "Credential created for future protocol version.",
        ],
        remediation: [
            "Remove ver field or set to 1 per P-26.",
            "Upgrade verifier if newer version is legitimate.",
        ],
        doc_pointer: "P-26 versioning; Core Spec step 0b",
    },
    missing_field: {
        summary: "One or more required fields are absent from the credential object.",
        likely_causes: [
            "Issuer omitted a mandatory field during creation.",
            "Serialization bug dropped a field during encoding.",
            "Credential was truncated in transit.",
        ],
        remediation: [
            "Request new credential ensuring all required fields are present.",
            "Check issuer implementation against v0 field list.",
            "Compare with known-good credential from test suite.",
        ],
        doc_pointer: "Core Spec section 6 step 0; P-06 field contract",
    },
    replay_detected: {
        summary: "The credential nonce has already been seen within the TTL window.",
        likely_causes: [
            "Same credential presented more than once to this verifier.",
            "Attacker captured and replayed a previously used credential.",
            "Load balancer routed same request to shared nonce cache.",
        ],
        remediation: [
            "Request fresh credential with new nonce from issuer.",
            "Ensure agent generates unique nonces per session.",
            "Use batch issuance with distinct nonces if multi-presentation needed.",
        ],
        doc_pointer: "Core Spec section 6 step 6; P-09",
    },
    revoked: {
        summary: "The credential has been explicitly revoked before its natural expiry.",
        likely_causes: [
            "Principal revoked via issuer revocation endpoint.",
            "Issuer detected compromise and revoked outstanding credentials.",
            "Automated fraud-detection flagged the credential.",
        ],
        remediation: [
            "Request new credential after resolving revocation cause.",
            "Contact issuer if revocation was in error.",
            "Review revocation reason in the issuer audit log.",
        ],
        doc_pointer: "Core Spec section 6 step 7; P-09",
    },
    revocation_state_unavailable: {
        summary: "Revocation status cannot be determined because source is unreachable. System fails closed.",
        likely_causes: [
            "Revocation service temporarily down.",
            "Network partition between verifier and revocation source.",
            "Cache expired and cannot refresh.",
        ],
        remediation: [
            "Retry after confirming connectivity.",
            "Check health of revocation service.",
            "Per fail-closed policy, request denied until status confirmed.",
        ],
        doc_pointer: "Core Spec section 6 step 7 fail-closed; P-09",
    },
    proof_of_possession_failed: {
        summary: "Ed25519 proof-of-possession signature does not verify against the agent public key.",
        likely_causes: [
            "Agent private key does not match apk in credential.",
            "PoP payload built with different method/path/action/nonce than signed.",
            "PoP signature corrupted during transport or encoding.",
        ],
        remediation: [
            "Ensure agent signs PopRequestPayload with exact values sent in request.",
            "Verify agent private key matches apk in credential.",
            "Check encoding mismatches (base64url vs standard base64).",
        ],
        doc_pointer: "Core Spec section 6 step 8; pop.py domain separation rilavo_pop_v0",
    },
    scope_mismatch: {
        summary: "Requested action class does not exactly match the action class in the credential. Exact-match only at v0.",
        likely_causes: [
            "Agent requested different operation than authorized.",
            "x-rilavo-action header does not match act field in credential.",
            "Wildcard or hierarchical scope matching attempted at v0.",
        ],
        remediation: [
            "Request credential with correct action_class for desired operation.",
            "Ensure x-rilavo-action header exactly matches credential act field.",
            "For multiple operations obtain separate credentials per action class.",
        ],
        doc_pointer: "Core Spec section 6 step 9; P-07 exact-match scope",
    },
    delegation_not_permitted: {
        summary: "Credential carries dlg (delegation depth) non-zero value rejected at v0.",
        likely_causes: [
            "Delegated sub-credential presented at v0 where delegation is Wave-6.",
            "dlg field accidentally included during credential creation.",
        ],
        remediation: [
            "Request top-level non-delegated credential from root issuer.",
            "Remove dlg field if added in error.",
            "Delegation becomes available when P-34 trigger condition met.",
        ],
        doc_pointer: "Core Spec step 0b delegation check; P-34 Wave-6 trigger",
    },
};
function explainRejection(code) {
    const exp = exports.EXPLANATIONS[code];
    if (!exp)
        throw new Error(`unknown reason code: ${code}`);
    return exp;
}
function formatExplanation(explanation) {
    const lines = [];
    lines.push(`Summary: ${explanation.summary}`);
    lines.push("");
    lines.push("Likely causes:");
    explanation.likely_causes.forEach((cause, i) => lines.push(`  ${i + 1}. ${cause}`));
    lines.push("");
    lines.push("Remediation:");
    explanation.remediation.forEach((step, i) => lines.push(`  ${i + 1}. ${step}`));
    lines.push("");
    lines.push(`Reference: ${explanation.doc_pointer}`);
    return lines.join("\n");
}
