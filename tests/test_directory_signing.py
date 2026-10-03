"""D3 PROPOSAL tests: signed key-directory entries (opt-in, additive).

Nothing here changes KeyDirectory or the verification path -- this module is
a self-contained proposal artifact per the Track-D rules.
"""

from __future__ import annotations

import base64

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from rilavo.directory_signing import (
    PROPOSAL_STATUS,
    DirectoryPayload,
    DirectorySigner,
    verify_signed_entry,
)


def _payload(issuer="rilavo:iss:abc123", pem="-----BEGIN PUBLIC KEY-----\nX\n",
             valid_until=None, version=14):
    return DirectoryPayload(issuer_id=issuer, public_key_pem=pem,
                            valid_until=valid_until,
                            directory_version=version)


def test_proposal_status_is_labeled_not_decided():
    assert "PROPOSED" in PROPOSAL_STATUS
    assert "undecided" in PROPOSAL_STATUS.lower() or \
        "not a Decided register item" in PROPOSAL_STATUS


def test_sign_and_verify_roundtrip():
    signer = DirectorySigner()
    signed = signer.sign(_payload())
    pub = signer.public_key
    assert verify_signed_entry(signed, pub) is True


def test_tampered_payload_rejected():
    signer = DirectorySigner()
    signed = signer.sign(_payload(valid_until=None))
    from dataclasses import replace
    tampered = replace(signed.payload,
                       valid_until=1_999_999_999)   # extend lifetime illegally
    forged = replace(signed, payload=tampered)
    assert verify_signed_entry(forged, signer.public_key) is False


def test_wrong_signer_key_rejected():
    real_signer = DirectorySigner()
    attacker = DirectorySigner()
    signed_by_attacker = attacker.sign(_payload(issuer="rilavo:iss:real"))
    # verifier only trusts the REAL directory operator's key:
    assert verify_signed_entry(signed_by_attacker, real_signer.public_key) is False


def test_payload_serialization_deterministic_and_field_exact():
    p1 = _payload(version=14)
    p2 = _payload(version=14)
    assert p1.canonical_bytes() == p2.canonical_bytes()
    decoded = json.loads(p1.canonical_bytes())
    assert set(decoded) == {"directory_version", "issuer_id",
                            "public_key_pem", "valid_until"}
    assert decoded["valid_until"] == -1            # None serialized as -1


import json  # noqa: E402  (used above via json.loads after canonical_bytes)


def test_none_valid_until_serializes_as_minus_one():
    p = _payload(valid_until=None)
    assert b'"valid_until":-1' in p.canonical_bytes()
    p_active = _payload(valid_until=1_754_900_000)
    assert b"1754900000" in p_active.canonical_bytes()


def test_signer_id_distinct_from_any_issuer_fingerprint():
    """The directory operator's identity is its own -- never an issuer key."""
    signer = DirectorySigner()
    assert signer.signer_id.startswith("rilavo:dir:")
    assert "rilavo:iss:" not in signer.signer_id


def test_module_imports_nothing_from_verification_path():
    """Additive-only guarantee: the proposal module must not wire itself into
    KeyDirectory or verifier.py."""
    import ast
    from pathlib import Path
    src = Path(__file__).resolve().parents[1] / "src" / "rilavo" / "directory_signing.py"
    tree = ast.parse(src.read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            top = node.module.split(".")[0]
            if top == "rilavo":
                imported.add(node.module)
    allowed = {"rilavo.keys"}
    unexpected = imported - allowed
    assert not unexpected, f"proposal imports beyond keys util: {unexpected}"
