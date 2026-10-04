"""P-20: day-one offline test kit (rilavo.testing).

Proves the fixed test issuer is deterministic across runs and that a full
issue -> proof-of-possession -> verify cycle runs with zero network and zero
external infrastructure, using only rilavo.testing helpers.
"""


from rilavo.api import Issuer
from rilavo.testing import (
    DEFAULT_TEST_VERIFIER_ID,
    TEST_ISSUER_FINGERPRINT,
    TEST_ISSUER_PUBLIC_KEY_PEM,
    local_test_agent,
    local_test_issuer,
    offline_test_kit,
)


def test_fixed_issuer_fingerprint_is_stable_across_runs():
    """Hardcoded expectation: the embedded keypair must never drift."""
    assert local_test_issuer().issuer_id == TEST_ISSUER_FINGERPRINT
    assert (
        TEST_ISSUER_FINGERPRINT == "rilavo:iss:38f93d4f0edb4f65"
    ), "fixed test issuer key changed — this breaks every offline integration test"


def test_local_test_issuer_is_deterministic_and_embedded_pem_matches():
    a, b = local_test_issuer(), local_test_issuer()
    assert isinstance(a, Issuer)
    assert a.issuer_id == b.issuer_id == TEST_ISSUER_FINGERPRINT
    assert a.public_key_pem().strip() == TEST_ISSUER_PUBLIC_KEY_PEM.strip()


def test_local_test_agent_is_fresh_and_random():
    k1, _ = local_test_agent()
    k2, _ = local_test_agent()
    from cryptography.hazmat.primitives import serialization

    raw1 = k1.private_bytes(
        serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption()
    )
    raw2 = k2.private_bytes(
        serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption()
    )
    assert raw1 != raw2  # agents are random; only the ISSUER must be fixed


def test_full_offline_issue_pop_verify_cycle_accepts():
    kit = offline_test_kit()
    agent_priv, agent_pub = local_test_agent()

    credential = kit.issue(
        principal="acme-corp",
        agent_public_key=agent_pub,
        action_class="payments.initiate",
        ttl_seconds=3600,
    )
    assert credential.fields["iss"] == TEST_ISSUER_FINGERPRINT
    assert credential.fields["aud"] == DEFAULT_TEST_VERIFIER_ID

    request = kit.sign_request(agent_priv, "POST", "/payments", "payments.initiate")
    result = kit.verify(credential, request)

    assert result.accepted is True
    assert result.reason_code == "accept"


def test_offline_reject_paths_without_any_infrastructure():
    kit = offline_test_kit()
    agent_priv, agent_pub = local_test_agent()

    # Wrong action class on the signed request -> scope mismatch.
    credential = kit.issue(
        principal="acme-corp",
        agent_public_key=agent_pub,
        action_class="payments.initiate",
    )
    request = kit.sign_request(agent_priv, "POST", "/payments", "payments.refund")
    result = kit.verify(credential, request)
    assert result.accepted is False
    assert result.reason_code == "scope_mismatch"

    # Proof-of-possession with the WRONG agent key.
    other_priv, _other_pub = local_test_agent()
    request = kit.sign_request(other_priv, "POST", "/payments", "payments.initiate")
    result = kit.verify(credential, request)
    assert result.accepted is False
    assert result.reason_code == "proof_of_possession_failed"

    # Unknown issuer: a credential signed by some OTHER random issuer cannot be
    # verified against the fixed offline directory.
    stranger = Issuer()  # random key, not in the offline directory
    stray_credential = stranger.issue_credential(
        principal="acme-corp",
        agent="agent:test-runner-01",
        agent_public_key=agent_pub,
        action_class="payments.initiate",
        audience=DEFAULT_TEST_VERIFIER_ID,
    )
    request = kit.sign_request(agent_priv, "POST", "/payments", "payments.initiate")
    result = kit.verify(stray_credential, request)
    assert result.accepted is False
    assert result.reason_code == "unknown_issuer"


def test_two_kits_share_the_same_fixed_issuer_trust_anchor():
    """Kits are independent objects but trust the SAME fixed issuer key."""
    kit_a, kit_b = offline_test_kit(), offline_test_kit(verifier_id="verifier:other.example")
    agent_priv, agent_pub = local_test_agent()

    credential = kit_a.issue(
        principal="acme-corp", agent_public_key=agent_pub, action_class="act.x",
        audience="verifier:other.example",
    )
    request = kit_b.sign_request(agent_priv, "GET", "/x", "act.x")
    result = kit_b.verify(credential, request)
    assert result.accepted is True
