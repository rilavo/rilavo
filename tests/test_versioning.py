"""P-26 versioning enforcement.

Derived from docs/wave_2/26_VERSIONING.md: ver is reserved in the schema's
design space; absent ver implicitly means 1; a verifier encountering any
other value rejects it as an unrecognized version -- an explicit failure,
never silent misinterpretation, and never conflated with shape failures.
"""

from __future__ import annotations

from rilavo.api import Issuer, do_issue, do_verify
from rilavo.credential import Credential
from rilavo.errors import INVALID_SIGNATURE, UNRECOGNIZED_VERSION
from rilavo.keys import KeyDirectory, generate_keypair
from rilavo.pop import Request, sign_request
from rilavo.revocation import RevocationLog
from rilavo.verifier import NonceCache

V = "verifier:versioning.example.com"


class Harness:
    def __init__(self):
        self.issuer = Issuer()
        self.directory = KeyDirectory()
        self.issuer.register_into(self.directory)
        self.agent_priv, self.agent_pub = generate_keypair()

    def credential(self, **overrides):
        cred = do_issue(self.issuer, principal="p", agent="a",
                        agent_public_key=self.agent_pub,
                        action_class="data.read", audience=V)
        cred.fields.update(overrides)
        return cred

    def request(self):
        sig, nonce = sign_request(self.agent_priv, "POST", "/x", "data.read")
        return Request("POST", "/x", "data.read", sig, nonce)

    def result_for(self, cred):
        return do_verify(V, cred, self.request(), self.directory,
                         RevocationLog(), nonces=NonceCache(),
                         now=cred.fields["iat"] + 1)


def test_absent_ver_accepted():
    """v0 wire format carries no ver; absence implicitly means version 1."""
    h = Harness()
    assert h.result_for(h.credential()).reason_code == "accept"


def test_explicit_ver_1_accepted():
    """A credential may make the version explicit without structural change."""
    h = Harness()
    # re-sign so the explicit field is covered by a valid signature:
    from rilavo.credential import issue as raw_issue, IssueRequest
    from rilavo.keys import b64url_encode, public_key_bytes
    from datetime import datetime, timezone
    cred = raw_issue(
        h.issuer._private_key, h.issuer.issuer_id,
        IssueRequest(principal="p", agent="a",
                     agent_public_key_b64=b64url_encode(public_key_bytes(h.agent_pub)),
                     action_class="data.read", audience=V),
        now=datetime.fromtimestamp(1_760_000_000, tz=timezone.utc))
    cred.fields["ver"] = 1
    # re-sign with ver included (a real ver:1 issuer would sign it):
    from rilavo.canonical import canonicalize
    from rilavo.keys import b64url_encode as b64e
    sig = h.issuer._private_key.sign(canonicalize(cred.signing_payload()))
    cred.fields["sig"] = b64e(sig)
    assert h.result_for(cred).reason_code == "accept"


def test_ver_2_rejected_with_unrecognized_version():
    """The doc's own worked example: a ver:1 verifier encountering ver:2
    rejects it as an unrecognized version."""
    h = Harness()
    result = h.result_for(h.credential(ver=2))
    assert result.accepted is False
    assert result.reason_code == UNRECOGNIZED_VERSION


def test_ver_garbage_string_rejected_with_unrecognized_version():
    h = Harness()
    result = h.result_for(h.credential(ver="garbage"))
    assert result.reason_code == UNRECOGNIZED_VERSION


def test_ver_beta_rejected_with_unrecognized_version():
    h = Harness()
    result = h.result_for(h.credential(ver="beta"))
    assert result.reason_code == UNRECOGNIZED_VERSION


def test_non_integer_ver_rejected_with_unrecognized_version():
    h = Harness()
    for value in (2.5, True, None, [1]):
        result = h.result_for(h.credential(ver=value))
        assert result.reason_code == UNRECOGNIZED_VERSION, f"ver={value!r}"


def test_version_gate_is_distinct_from_shape_failures():
    """A missing required field still reports MISSING_FIELD; only a wrong
    VERSION claim reports unrecognized_version (no conflation)."""
    from rilavo.errors import MISSING_FIELD
    h = Harness()
    cred = h.credential()
    del cred.fields["sub"]
    assert h.result_for(cred).reason_code == MISSING_FIELD


def _signed_ver1_credential(h):
    from rilavo.credential import issue as raw_issue, IssueRequest
    from rilavo.keys import b64url_encode, public_key_bytes
    from datetime import datetime, timezone
    from rilavo.canonical import canonicalize
    cred = raw_issue(
        h.issuer._private_key, h.issuer.issuer_id,
        IssueRequest(principal="p", agent="a",
                     agent_public_key_b64=b64url_encode(public_key_bytes(h.agent_pub)),
                     action_class="data.read", audience=V),
        now=datetime.fromtimestamp(1_760_000_000, tz=timezone.utc))
    cred.fields["ver"] = 1
    sig = h.issuer._private_key.sign(canonicalize(cred.signing_payload()))
    cred.fields["sig"] = b64url_encode(sig)
    return cred


def test_present_ver_is_inside_the_signed_payload():
    """ver, when present, sits inside the signing payload: removing it from a
    credential signed WITH it breaks the signature."""
    h = Harness()
    cred = _signed_ver1_credential(h)
    stripped = Credential(fields={k: v for k, v in cred.fields.items()
                                  if k != "ver"})
    assert h.result_for(stripped).reason_code == INVALID_SIGNATURE


def test_version_gate_runs_before_signature_verification():
    """Deliberate ordering: an unknown version is rejected fail-fast with the
    explicit version reason -- the doc's 'clear, explicit failure' -- without
    spending the Ed25519 verification first."""
    h = Harness()
    cred = _signed_ver1_credential(h)
    tampered = Credential(fields={**cred.fields, "ver": 2})
    assert h.result_for(tampered).reason_code == UNRECOGNIZED_VERSION
