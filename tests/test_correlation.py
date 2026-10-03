"""P-13 correlation-gap instrumentation tests.

INSTRUMENTATION ONLY: these tests prove measurement works and the optional
mitigation mode behaves exactly as configured. None of them, nor the module,
claims P-13's Open status changed.
"""

from __future__ import annotations

import json

from rilavo.api import Issuer, do_issue
from rilavo.credential import IssueRequest, issue as raw_issue
from rilavo.correlation import (
    LABEL,
    CorrelationGapMonitor,
    CorrelationPolicy,
    relationship_subject_id,
    scoped_issue_args,
)
from datetime import datetime, timezone


T0 = 1_760_000_000


def test_detect_finds_known_collisions():
    m = CorrelationGapMonitor()
    # Same subject across two audiences -- the doc's exact worked example:
    m.record_issuance("acme-corp:runner-04", "agt_A", "verifier:a.example.com")
    m.record_issuance("acme-corp:runner-04", "agt_B", "verifier:b.example.com")
    collisions = {c.field_name: c for c in m.detect_reuse()}
    assert set(collisions) == {"sub"}
    sub = collisions["sub"]
    assert sub.distinct_audiences == 2
    assert set(sub.audiences) == {"verifier:a.example.com", "verifier:b.example.com"}
    # The instrument stores a hash, never the raw identifier:
    assert "acme-corp:runner-04" not in str(sub.value_hash)


def test_monitor_never_retains_raw_identifiers():
    """The instrument must not become a secondary identity database: raw
    sub/agt values are hashed at ingestion and never stored, even
    transiently. Detection still works because hashing is deterministic."""
    m = CorrelationGapMonitor()
    m.record_issuance("secret-principal-42", "secret-agent-99", "verifier:a")
    m.record_issuance("secret-principal-42", "another-agent-77", "verifier:b")
    internal_state = str([(r.subject, r.agent, r.audience) for r in m.records])
    assert "secret-principal-42" not in internal_state
    assert "secret-agent-99" not in internal_state
    assert "another-agent-77" not in internal_state
    # Collision detection is unaffected by hashing at ingestion:
    fields = {c.field_name for c in m.detect_reuse()}
    assert fields == {"sub"}
    assert next(c for c in m.detect_reuse()).distinct_audiences == 2


def test_agent_reuse_detected_independently():
    m = CorrelationGapMonitor()
    m.record_issuance("s1", "shared-agent-01", "verifier:a")
    m.record_issuance("s2", "shared-agent-01", "verifier:b")
    fields = {c.field_name for c in m.detect_reuse()}
    assert fields == {"agt"}          # subjects differ; only agt collides


def test_no_false_positives_on_clean_fixture():
    """Every identifier unique per relationship -> zero findings (misses none
    in the sense that genuinely clean issuance produces no collisions)."""
    m = CorrelationGapMonitor()
    for i in range(10):
        m.record_issuance(f"subject-{i}", f"agent-{i}", f"verifier:{i}.example.com")
        # same subject/agent REUSED at the SAME audience is not cross-verifier reuse:
        m.record_issuance(f"subject-{i}", f"agent-{i}", f"verifier:{i}.example.com")
    assert m.detect_reuse() == []
    summary = m.summary()
    assert summary["subjects_reused_across_audiences"] == 0
    assert summary["agents_reused_across_audiences"] == 0


def test_summary_carries_open_status_and_label():
    m = CorrelationGapMonitor()
    s = m.summary()
    assert s["label"] == LABEL
    assert "INSTRUMENTATION" in s["label"]
    assert "OPEN" in s["open_question_status"]


# ---------------------------------------------------------------------------
# Optional per-relationship mode
# ---------------------------------------------------------------------------

def _issue_with(harness_issuer, subject, audience, policy):
    scoped = scoped_issue_args(subject, audience, policy)
    return raw_issue(
        harness_issuer._private_key, harness_issuer.issuer_id,
        IssueRequest(principal=scoped, agent="agt_x",
                     agent_public_key_b64="k" * 43,
                     action_class="data.read", audience=audience),
        now=datetime.fromtimestamp(T0, tz=timezone.utc))


def test_policy_default_is_off():
    policy = CorrelationPolicy()
    assert policy.enabled is False
    # OFF: pass-through even without any key configured
    assert scoped_issue_args("global-sub", "aud", policy) == "global-sub"


def test_enabled_policy_requires_secret_key():
    import pytest
    with pytest.raises(ValueError):
        CorrelationPolicy(enabled=True)


def test_mode_off_produces_identical_credential_shape_to_before():
    """With the flag OFF, issued credentials are byte-for-byte what the old
    path produced: same field set, same global `sub`, everything equal except
    the inherently-random nonce and its signature."""
    issuer = Issuer()
    apub_b64 = "k" * 43
    before = raw_issue(issuer._private_key, issuer.issuer_id,
                       IssueRequest(principal="global-sub", agent="agt_x",
                                    agent_public_key_b64=apub_b64,
                                    action_class="data.read",
                                    audience="verifier:a"),
                       now=datetime.fromtimestamp(T0, tz=timezone.utc))
    off_policy = CorrelationPolicy()   # default OFF
    after = _issue_with(issuer, "global-sub", "verifier:a", off_policy)

    assert set(before.fields) == set(after.fields)          # same schema
    stable = ("iss", "sub", "agt", "apk", "act", "aud", "iat", "exp")
    assert all(before.fields[k] == after.fields[k] for k in stable)
    # canonical payload sans sig identical once nonce excluded:
    b_payload = {k: v for k, v in before.signing_payload().items() if k != "nonce"}
    a_payload = {k: v for k, v in after.signing_payload().items() if k != "nonce"}
    assert json.dumps(b_payload, sort_keys=True) == json.dumps(a_payload, sort_keys=True)


def test_mode_on_scopes_identifier_per_relationship():
    issuer = Issuer()
    policy = CorrelationPolicy(enabled=True, secret_key=b"k" * 32)

    c_a = _issue_with(issuer, "global-sub", "verifier:a", policy)
    c_b = _issue_with(issuer, "global-sub", "verifier:b", policy)
    c_a2 = _issue_with(issuer, "global-sub", "verifier:a", policy)

    # Different relationships -> unrelated identifiers:
    assert c_a.fields["sub"] != c_b.fields["sub"]
    assert c_a.fields["sub"] != "global-sub"
    # Same relationship -> STABLE identifier (deterministic):
    assert c_a.fields["sub"] == c_a2.fields["sub"]
    # Original global identifier leaks nowhere:
    for cred in (c_a, c_b):
        assert "global-sub" not in cred.to_json()


def test_mode_on_eliminates_collisions_the_monitor_would_flag():
    """End-to-end instrumentation loop: ON-mode issuance across many
    verifiers produces zero findings from the monitor itself."""
    issuer = Issuer()
    policy = CorrelationPolicy(enabled=True, secret_key=b"k" * 32)
    monitor = CorrelationGapMonitor()
    for i, aud in enumerate(f"verifier:{j}" for j in range(8)):
        scoped = scoped_issue_args("one-principal", aud, policy)
        monitor.record_issuance(scoped, "agt_shared", aud)
    subs = [c for c in monitor.detect_reuse() if c.field_name == "sub"]
    assert subs == []            # agt reuse may remain flagged -- it is a
                                 # separate lever, honestly still visible


def test_relationship_id_is_stable_and_unlinkable():
    k = b"k" * 32
    id1 = relationship_subject_id(k, "subject", "audience-a")
    id2 = relationship_subject_id(k, "subject", "audience-a")
    id3 = relationship_subject_id(k, "subject", "audience-b")
    other_key = relationship_subject_id(b"different", "subject", "audience-a")
    assert id1 == id2                      # stable within a relationship
    assert id1 != id3                      # unlinkable across relationships
    assert id1 != other_key                # keyed -- operator-secret domain separation
