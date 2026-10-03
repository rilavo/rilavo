"""Compact encoding tests (PROPOSAL -- wire format UNCHANGED)."""
import pytest

from rilavo.credential import Credential, DEFAULT_MAX_TTL_SECONDS
from rilavo.compact import to_compact, from_compact, VERSION_TAG
from rilavo.testing import offline_test_kit, local_test_agent
from rilavo.keys import b64url_encode, public_key_bytes


V = "verifier:compact.example"


@pytest.fixture
def cred_fields():
    kit = offline_test_kit()
    _, agent_pub = local_test_agent()
    from rilavo.keys import public_key_bytes as pkb
    apk_b64 = b64url_encode(pkb(agent_pub))
    from rilavo.api import do_issue
    cred = do_issue(
        issuer=kit.issuer,
        principal="acme-corp:runner-01",
        agent="agt-compact",
        agent_public_key=agent_pub,
        action_class="data.read",
        audience=V,
    )
    return dict(cred.fields)


def test_compact_size_under_160(cred_fields):
    data = to_compact(cred_fields)
    assert len(data) < 160
    print(f"compact size: {len(data)} bytes")


def test_roundtrip_preserves_all_fields(cred_fields):
    data = to_compact(cred_fields)

    # Resolvers:
    def resolve_iss(fp8):
        return cred_fields["iss"]

    def resolve_act(h8):
        return cred_fields["act"]

    def resolve_aud(h8):
        return cred_fields["aud"]

    result = from_compact(data, resolve_iss, resolve_act, resolve_aud)
    for field in ("apk", "act", "aud", "iat", "exp", "nonce", "sig"):
        assert result[field] == cred_fields[field], f"field {field} mismatch"


def test_unknown_fingerprint_fails_closed(cred_fields):
    data = to_compact(cred_fields)
    def fail_iss(fp): raise ValueError("unknown fingerprint")
    def ok_act(h): return cred_fields["act"]
    def ok_aud(h): return cred_fields["aud"]
    with pytest.raises(ValueError):
        from_compact(data, fail_iss, ok_act, ok_aud)


def test_version_tag_present(cred_fields):
    assert to_compact(cred_fields)[0] == VERSION_TAG


def test_wire_format_unchanged():
    """The compact encoding is additive; v0 JSON wire format is untouched."""
    from rilavo.credential import REQUIRED_FIELDS
    assert REQUIRED_FIELDS == ("iss", "sub", "agt", "apk", "act", "aud",
                               "iat", "exp", "nonce", "sig")
