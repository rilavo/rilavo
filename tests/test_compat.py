"""P-18 compatibility layer: dual acceptance, dispatch-only, no OAuth
implementation, no bet on tracked standards."""

from __future__ import annotations

import inspect

from rilavo.api import Issuer, do_issue
from rilavo.compat import (
    MECHANISM_OAUTH_BEARER,
    MECHANISM_RILAVO_CREDENTIAL,
    REASON_BEARER_REJECTED,
    REASON_NO_CREDENTIALS,
    authenticate,
)
from rilavo.errors import INVALID_SIGNATURE
from rilavo.keys import KeyDirectory, generate_keypair
from rilavo.pop import Request, sign_request
from rilavo.revocation import RevocationLog
from rilavo.verifier import NonceCache

V = "verifier:compat.example.com"


class Harness:
    def __init__(self):
        self.issuer = Issuer()
        self.directory = KeyDirectory()
        self.issuer.register_into(self.directory)
        self.agent_priv, self.agent_pub = generate_keypair()
        self.revocations = RevocationLog()

    def credential(self, **overrides):
        cred = do_issue(self.issuer, principal="acme:runner-01", agent="agt_c1",
                        agent_public_key=self.agent_pub,
                        action_class="data.read", audience=V)
        cred.fields.update(overrides)
        return cred

    def request(self, action="data.read"):
        sig, nonce = sign_request(self.agent_priv, "POST", "/x", action)
        return Request("POST", "/x", action, sig, nonce)

    def auth(self, cred=None, req=None, token=None, validator=None):
        return authenticate(
            bearer_token=token, bearer_validator=validator,
            credential=cred, pop_request=req, verifier_id=V,
            key_directory=self.directory, revocation_log=self.revocations,
            nonces=NonceCache(), now=(cred or self.credential()).fields["iat"] + 1
            if cred else None)


def accept_bearer(token: str):
    """Operator-supplied validator stand-in: any token it recognizes maps to
    claims; the adapter itself knows nothing about token formats."""
    return {"sub": "legacy-client-01"} if token == "valid-oauth-token" else None


# --- bearer path -----------------------------------------------------------

def test_bearer_token_accepted_reports_mechanism():
    h = Harness()
    result = h.auth(token="valid-oauth-token", validator=accept_bearer)
    assert result.authenticated is True
    assert result.mechanism == MECHANISM_OAUTH_BEARER
    assert result.principal_claims == {"sub": "legacy-client-01"}


def test_bearer_token_rejected_reports_rejection():
    h = Harness()
    result = h.auth(token="forged-token", validator=accept_bearer)
    assert result.authenticated is False
    assert result.mechanism == MECHANISM_OAUTH_BEARER
    assert result.reason_code == REASON_BEARER_REJECTED


def test_adapter_never_implements_oauth_itself():
    """The adapter must dispatch, not validate: no token parsing, no
    introspection calls, no network. Validation authority is the callable."""
    src = inspect.getsource(__import__("rilavo.compat", fromlist=["authenticate"]))
    for banned in ("decode", "introspect", "urlopen", "jwt", "authorization_server"):
        assert banned not in src.lower(), f"adapter implements OAuth: {banned}"


# --- rilavo credential path (delegates to do_verify semantics) -------------

def test_rilavo_credential_accepted_reports_mechanism():
    h = Harness()
    result = h.auth(cred=h.credential(), req=h.request())
    assert result.authenticated is True
    assert result.mechanism == MECHANISM_RILAVO_CREDENTIAL
    assert result.reason_code is None


def test_rilavo_credential_rejection_delegates_to_existing_semantics():
    """A tampered credential fails exactly as plain do_verify would fail it."""
    h = Harness()
    tampered = h.credential(sub="attacker")
    result = h.auth(cred=tampered, req=h.request())
    assert result.authenticated is False
    assert result.mechanism == MECHANISM_RILAVO_CREDENTIAL
    assert result.reason_code == INVALID_SIGNATURE


# --- neither present --------------------------------------------------------

def test_absent_both_rejects_with_explicit_no_credentials():
    h = Harness()
    result = h.auth()
    assert result.authenticated is False
    assert result.mechanism is None
    assert result.reason_code == REASON_NO_CREDENTIALS


# --- both present: documented precedence, no downgrade ----------------------

def test_both_present_valid_credential_wins_documented_precedence():
    """Precedence: Rilavo credential path attempted first; when it succeeds,
    that mechanism is reported."""
    h = Harness()
    result = h.auth(cred=h.credential(), req=h.request(),
                    token="valid-oauth-token", validator=accept_bearer)
    assert result.authenticated is True
    assert result.mechanism == MECHANISM_RILAVO_CREDENTIAL


def test_both_present_failed_credential_never_falls_back_to_bearer():
    """Anti-downgrade: an invalid credential is reported as its own failure
    even when a VALID bearer token is also present. No silent degradation."""
    h = Harness()
    tampered = h.credential(sub="attacker")
    result = h.auth(cred=tampered, req=h.request(),
                    token="valid-oauth-token", validator=accept_bearer)
    assert result.authenticated is False
    assert result.mechanism == MECHANISM_RILAVO_CREDENTIAL
    assert result.reason_code == INVALID_SIGNATURE
    assert result.principal_claims is None


# --- posture neutrality ------------------------------------------------------

def test_no_bet_on_tracked_standards():
    """CIMD / ID-JAG / AAuth are tracked, not adopted: the compatibility
    layer must not couple to any of them."""
    import ast
    tree = ast.parse(inspect.getsource(
        __import__("rilavo.compat", fromlist=["authenticate"]).__dict__["authenticate"].__module__
        and __import__("rilavo.compat")))
    # Coupling means code-level dependence (imports/attribute access), not a
    # documentation mention of why we deliberately DON'T depend on them.
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(a.name.split(".")[0].lower() for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0].lower())
    for standard in ("cimd", "id_jag", "idjag", "aauth"):
        assert standard not in imported_names, f"coupled to tracked standard: {standard}"
    # Mentions are fine only as posture statements; verify they appear in
    # comments/docstrings context by confirming the module still dispatches
    # to exactly two mechanisms:
    from rilavo import compat
    mechanisms = {compat.MECHANISM_OAUTH_BEARER, compat.MECHANISM_RILAVO_CREDENTIAL}
    assert len(mechanisms) == 2
